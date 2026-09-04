#!/usr/bin/env wolframscript

(* Native local replay for the future BG-02 production implementation.
   This runner is intentionally present in RED but exits before evaluation
   until the production module and implementation registry exist. *)

ClearAll[fileSHA256, jsonSafe];

fileSHA256[path_String] :=
  IntegerString[FileHash[path, "SHA256"], 16, 64];

jsonSafe[value_Association] :=
  AssociationThread[Keys[value], jsonSafe /@ Values[value]];
jsonSafe[value_List] := jsonSafe /@ value;
jsonSafe[value_String] := value;
jsonSafe[value_Integer] := value;
jsonSafe[value_Real] := value;
jsonSafe[True] := True;
jsonSafe[False] := False;
jsonSafe[Null] := Null;
jsonSafe[value_Rational] := ToString[InputForm[value]];
jsonSafe[value_] := ToString[InputForm[value]];

scriptDirectory = DirectoryName[$InputFileName];
repositoryRoot = DirectoryName[DirectoryName[scriptDirectory]];
arguments = Rest[$ScriptCommandLine];

outputDirectory = If[
  Length[arguments] >= 1,
  ExpandFileName[First[arguments]],
  FileNameJoin[{
    repositoryRoot,
    "artifacts",
    "bg02_einstein_projection"
  }]
];

If[!DirectoryQ[outputDirectory],
  CreateDirectory[outputDirectory, CreateIntermediateDirectories -> True]
];

initPath = FileNameJoin[{
  repositoryRoot, "wolfram", "BASS", "Kernel", "init.wl"
}];
modulePath = FileNameJoin[{
  repositoryRoot,
  "wolfram",
  "BASS",
  "Kernel",
  "Background",
  "EinsteinProjection.wl"
}];
registryPath = FileNameJoin[{
  repositoryRoot,
  "docs",
  "bass_master_ssot_v2",
  "BG_02_IMPLEMENTATION",
  "BG_02_IMPLEMENTATION_REGISTRY.json"
}];
testPath = FileNameJoin[{
  repositoryRoot,
  "wolfram",
  "BASS",
  "Tests",
  "BG02EinsteinProjectionImplementation.wlt"
}];
receiptPath = FileNameJoin[{
  outputDirectory,
  "BG_02_EINSTEIN_PROJECTION_WOLFRAM_RECEIPT.json"
}];
temporaryReceiptPath = receiptPath <> ".tmp";

requiredPaths = {initPath, modulePath, registryPath, testPath};
missingPaths = Select[requiredPaths, !FileExistsQ[#] &];

If[missingPaths =!= {},
  Print[InputForm[<|
    "status" -> "FAIL_MISSING_BG02_GREEN_INPUT",
    "missing_paths" -> missingPaths
  |>]];
  Exit[2]
];

Get[initPath];

packageLoaded = TrueQ[
  NameQ["BASS`Background`EinsteinProjectionRegistry"] &&
  NameQ["BASS`Background`EinsteinResidualTensor"] &&
  NameQ["BASS`Background`HamiltonianProjection"] &&
  NameQ["BASS`Background`MomentumProjection"] &&
  NameQ["BASS`Background`SpatialTraceProjection"] &&
  NameQ["BASS`Background`SpatialPSTFProjection"]
];

xTensorLoaded = TrueQ[
  NameQ["xAct`xTensor`DefTensor"] ||
  NameQ["DefTensor"]
];
xCobaLoaded = TrueQ[
  NameQ["xAct`xCoba`DefChart"] ||
  NameQ["DefChart"]
];

If[!packageLoaded || !xTensorLoaded || !xCobaLoaded,
  Print[InputForm[<|
    "status" -> "FAIL_NATIVE_PACKAGE_REGISTRATION",
    "package_loaded" -> packageLoaded,
    "xTensor_loaded" -> xTensorLoaded,
    "xCoba_loaded" -> xCobaLoaded
  |>]];
  Exit[3]
];

registryJSON = Import[registryPath, "RawJSON"];
registry =
  BASS`Background`EinsteinProjectionRegistry[];
audit = Lookup[registry, "native_audit", <||>];

registryValid = TrueQ[
  AssociationQ[registry] &&
  Lookup[registry, "formula_count", Missing["FormulaCount"]] === 14 &&
  DuplicateFreeQ[
    Lookup[Lookup[registry, "formulas", {}], "formula_id", {}]
  ] &&
  DeleteDuplicates[
    Lookup[Lookup[registry, "formulas", {}], "dimension", {}]
  ] === {"L^-2"} &&
  Lookup[registry, "scientific_parent_commit", ""] ===
    "80d271cc528e1a0ffa813ecd3e3fb7610f3fa755" &&
  Lookup[registryJSON, "scientific_parent_commit", ""] ===
    "80d271cc528e1a0ffa813ecd3e3fb7610f3fa755"
];

testContextPayload = <|
  "repository_scope" -> "BASS_ONLY",
  "repository_root" -> repositoryRoot,
  "registry" -> registry,
  "registry_json" -> registryJSON,
  "registry_valid" -> registryValid,
  "audit" -> audit,
  "package_loaded" -> packageLoaded,
  "xTensor_loaded" -> xTensorLoaded,
  "xCoba_loaded" -> xCobaLoaded
|>;

report = Block[
  {Global`$BASSBG02EinsteinProjectionTestContext = testContextPayload},
  TestReport[testPath]
];

succeeded = Quiet @ Check[
  report["TestsSucceededCount"],
  Missing["Unavailable"]
];
failed = Quiet @ Check[
  report["TestsFailedCount"],
  Missing["Unavailable"]
];
notEvaluated = Quiet @ Check[
  report["TestsNotEvaluatedCount"],
  Missing["Unavailable"]
];
expectedTestCount = 26;

gitHead = Quiet @ Check[
  StringTrim @ RunProcess[
    {"git", "-C", repositoryRoot, "rev-parse", "HEAD"},
    "StandardOutput"
  ],
  Missing["GitUnavailable"]
];
gitTree = Quiet @ Check[
  StringTrim @ RunProcess[
    {"git", "-C", repositoryRoot, "show", "-s", "--format=%T", "HEAD"},
    "StandardOutput"
  ],
  Missing["GitUnavailable"]
];

jsonSafeProbe = jsonSafe[<|
  "nested" -> <|
    "integer" -> 1,
    "list" -> {True, False, Null, 1/2},
    "symbolic" -> (probeX + probeY)
  |>
|>];
nestedProbe = Lookup[jsonSafeProbe, "nested", Missing["Nested"]];
jsonSafeProbePass = TrueQ[
  AssociationQ[jsonSafeProbe] &&
  AssociationQ[nestedProbe] &&
  Lookup[nestedProbe, "integer", Missing["Integer"]] === 1 &&
  Lookup[nestedProbe, "list", Missing["List"]] ===
    {True, False, Null, "1/2"} &&
  StringQ[Lookup[nestedProbe, "symbolic", Missing["Symbolic"]]]
];

allPassed = TrueQ[
  packageLoaded &&
  xTensorLoaded &&
  xCobaLoaded &&
  registryValid &&
  succeeded === expectedTestCount &&
  failed === 0 &&
  notEvaluated === 0 &&
  jsonSafeProbePass
];

receipt = <|
  "schema_version" -> "1.0.0",
  "stage_id" -> "BG_02_EINSTEIN_PROJECTION_NATIVE_XACT_REPLAY",
  "repository_scope" -> "BASS_ONLY",
  "git_head" -> gitHead,
  "git_tree" -> gitTree,
  "wolfram_version" -> $Version,
  "xTensor_loaded" -> xTensorLoaded,
  "xCoba_loaded" -> xCobaLoaded,
  "package_loaded" -> packageLoaded,
  "registry_valid" -> registryValid,
  "module_sha256" -> fileSHA256[modulePath],
  "registry_sha256" -> fileSHA256[registryPath],
  "wlt_sha256" -> fileSHA256[testPath],
  "exact_audit" -> audit,
  "expected_top_level_munit_tests" -> expectedTestCount,
  "tests_succeeded" -> succeeded,
  "tests_failed" -> failed,
  "tests_not_evaluated" -> notEvaluated,
  "json_safe_association_mode" ->
    "ASSOCIATION_THREAD_KEYS_RECURSIVE_VALUES",
  "json_safe_probe_pass" -> jsonSafeProbePass,
  "receipt_write_policy" ->
    "TEMPORARY_FILE_STRICT_JSON_ROUND_TRIP_THEN_RENAME",
  "claim_boundary" -> {
    "NO_CONSTRAINT_PROPAGATION_CLAIM",
    "NO_BACKGROUND_NUMERICAL_EVOLUTION",
    "NO_PROVIDER_ADMISSION",
    "NO_SCIENCE_PROMOTION",
    "NO_PASS_RF04"
  },
  "status" -> If[
    allPassed,
    "PASS_NATIVE_XACT_BG02_PROJECTION",
    "FAIL_NATIVE_XACT_BG02_PROJECTION"
  ]
|>;

safeReceipt = jsonSafe[receipt];
serialized = Quiet @ Check[
  ExportString[safeReceipt, "RawJSON"],
  $Failed
];

If[!StringQ[serialized] || StringLength[serialized] === 0,
  Print[InputForm[<|"status" -> "FAIL_RECEIPT_JSON_EXPORT"|>]];
  Exit[4]
];

If[FileExistsQ[temporaryReceiptPath], DeleteFile[temporaryReceiptPath]];
If[FileExistsQ[receiptPath], DeleteFile[receiptPath]];

stream = Quiet @ Check[
  OpenWrite[temporaryReceiptPath, CharacterEncoding -> "UTF-8"],
  $Failed
];
If[Head[stream] =!= OutputStream,
  Print[InputForm[<|"status" -> "FAIL_RECEIPT_TEMPORARY_OPEN"|>]];
  Exit[4]
];

WriteString[stream, serialized];
Close[stream];

roundTrip = Quiet @ Check[
  Import[temporaryReceiptPath, "RawJSON"],
  $Failed
];
roundTripValid = TrueQ[
  AssociationQ[roundTrip] &&
  Lookup[roundTrip, "stage_id", ""] ===
    "BG_02_EINSTEIN_PROJECTION_NATIVE_XACT_REPLAY" &&
  Lookup[roundTrip, "status", ""] === Lookup[safeReceipt, "status", ""] &&
  Lookup[roundTrip, "tests_succeeded", -1] === expectedTestCount &&
  Lookup[roundTrip, "tests_failed", -1] === 0 &&
  Lookup[roundTrip, "tests_not_evaluated", -1] === 0
];

If[!roundTripValid,
  If[FileExistsQ[temporaryReceiptPath], DeleteFile[temporaryReceiptPath]];
  Print[InputForm[<|"status" -> "FAIL_RECEIPT_JSON_ROUND_TRIP"|>]];
  Exit[4]
];

renameResult = Quiet @ Check[
  RenameFile[temporaryReceiptPath, receiptPath],
  $Failed
];

If[
  renameResult === $Failed ||
  !FileExistsQ[receiptPath] ||
  FileByteCount[receiptPath] <= 0 ||
  FileExistsQ[temporaryReceiptPath],
  Print[InputForm[<|"status" -> "FAIL_RECEIPT_ATOMIC_RENAME"|>]];
  Exit[4]
];

Print[InputForm[safeReceipt]];
Exit[If[allPassed, 0, 1]];
