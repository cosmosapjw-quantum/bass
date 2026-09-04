#!/usr/bin/env wolframscript

ClearAll[fileSHA256, jsonSafe, jsonSafeProbeSymbol];
fileSHA256[path_String] := IntegerString[FileHash[path, "SHA256"], 16, 64];

jsonSafe[value_Association] := AssociationThread[Keys[value], jsonSafe /@ Values[value]];
jsonSafe[value_List] := jsonSafe /@ value;
jsonSafe[value_String] := value;
jsonSafe[value_Integer] := value;
jsonSafe[value_Real] := value;
jsonSafe[True] := True;
jsonSafe[False] := False;
jsonSafe[Null] := Null;
jsonSafe[value_] := ToString[InputForm[value]];

jsonSafeProbe = Quiet@Check[
  jsonSafe[<|
    "outer" -> <|
      "integer" -> 1,
      "list" -> {True, Null, 1/2},
      "symbolic" -> 2 jsonSafeProbeSymbol
    |>
  |>],
  $Failed
];
jsonSafeProbeOuter = If[
  AssociationQ[jsonSafeProbe],
  Lookup[jsonSafeProbe, "outer", Missing["OuterAssociationAbsent"]],
  Missing["ProbeNotAssociation"]
];
jsonSafeProbeList = If[
  AssociationQ[jsonSafeProbeOuter],
  Lookup[jsonSafeProbeOuter, "list", Missing["ListAbsent"]],
  Missing["OuterAssociationInvalid"]
];
jsonSafeProbeValid = And[
  AssociationQ[jsonSafeProbe],
  AssociationQ[jsonSafeProbeOuter],
  Lookup[jsonSafeProbeOuter, "integer", None] === 1,
  ListQ[jsonSafeProbeList],
  Length[jsonSafeProbeList] === 3,
  jsonSafeProbeList[[1]] === True,
  jsonSafeProbeList[[2]] === Null,
  StringQ[jsonSafeProbeList[[3]]],
  StringQ[Lookup[jsonSafeProbeOuter, "symbolic", None]]
];
If[!TrueQ[jsonSafeProbeValid],
  Print[InputForm[<|
    "status" -> "FAIL_JSON_SAFE_ASSOCIATION_RECURSION",
    "probe_head" -> Head[jsonSafeProbe],
    "outer_head" -> Head[jsonSafeProbeOuter],
    "list_head" -> Head[jsonSafeProbeList]
  |>]];
  Exit[3]
];

scriptDirectory = DirectoryName[$InputFileName];
repositoryRoot = DirectoryName[DirectoryName[scriptDirectory]];
arguments = Rest[$ScriptCommandLine];
outputDirectory = If[
  Length[arguments] >= 1,
  ExpandFileName[First[arguments]],
  FileNameJoin[{repositoryRoot, "artifacts", "sync_map02f_r3_consumer_bindings"}]
];
If[!DirectoryQ[outputDirectory],
  CreateDirectory[outputDirectory, CreateIntermediateDirectories -> True]
];

modulePath = FileNameJoin[{
  repositoryRoot, "wolfram", "BASS", "Kernel", "IR",
  "ConsumerBindingContractsR3.wl"
}];
testPath = FileNameJoin[{
  repositoryRoot, "wolfram", "BASS", "Tests",
  "ConsumerBindingContractsR3.wlt"
}];
graphPath = FileNameJoin[{
  repositoryRoot, "docs", "bass_master_ssot_v2", "SYNC_MAP_02F_R3",
  "CONSUMER_BINDING_CONTRACTS.json"
}];
receiptPath = FileNameJoin[{
  outputDirectory, "SYNC_MAP_02F_R3_CONSUMER_BINDING_WOLFRAM_RECEIPT.json"
}];
receiptTemporaryPath = receiptPath <> ".tmp";

missing = Select[{modulePath, testPath, graphPath}, !FileExistsQ[#] &];
If[missing =!= {},
  Print[InputForm[<|"status" -> "FAIL_MISSING_INPUT", "missing" -> missing|>]];
  Exit[2]
];

Get[modulePath];
contract = Import[graphPath, "RawJSON"];
validatorPass = TrueQ[
  BASS`IR`ConsumerBindingContractsR3`BASSConsumerBindingContractsR3Q[contract]
];
residuals =
  BASS`IR`ConsumerBindingContractsR3`BASSConsumerBindingContractsR3Residuals[contract];

report = Block[
  {Global`$BASSConsumerBindingContractsR3TestData = contract},
  TestReport[testPath]
];
succeeded = Quiet@Check[report["TestsSucceededCount"], Missing["Unavailable"]];
failed = Quiet@Check[report["TestsFailedCount"], Missing["Unavailable"]];
notEvaluated = Quiet@Check[report["TestsNotEvaluatedCount"], Missing["Unavailable"]];
expected = 18;

gitHead = Quiet@Check[
  StringTrim@RunProcess[
    {"git", "-C", repositoryRoot, "rev-parse", "HEAD"},
    "StandardOutput"
  ],
  Missing["GitUnavailable"]
];

allPassed = And[
  validatorPass,
  succeeded === expected,
  failed === 0,
  notEvaluated === 0,
  Lookup[residuals, "consumer_count_residual", None] === 0,
  Lookup[residuals, "binding_request_count_residual", None] === 0,
  Lookup[residuals, "source_role_pin_count_residual", None] === 0,
  Lookup[residuals, "named_source_symbol_count_residual", None] === 0,
  Lookup[residuals, "absent_slot_count_residual", None] === 0,
  Lookup[residuals, "formula_count_residual", None] === 0,
  Lookup[residuals, "state_surface_count_residual", None] === 0,
  Lookup[residuals, "certificate_family_count_residual", None] === 0,
  Lookup[residuals, "blocked_promotion_count_residual", None] === 0,
  TrueQ[Lookup[residuals, "pair_coverage_exact", False]],
  TrueQ[Lookup[residuals, "formula_authority_exact", False]],
  TrueQ[Lookup[residuals, "source_role_pins_exact", False]],
  TrueQ[Lookup[residuals, "rei_absent_slot_intact", False]],
  TrueQ[Lookup[residuals, "htt_blackbody_roles_distinct", False]],
  TrueQ[Lookup[residuals, "state_surface_firewall_intact", False]],
  TrueQ[Lookup[residuals, "authorization_firewall_intact", False]],
  TrueQ[Lookup[residuals, "stage_dag_acyclic", False]],
  TrueQ[Lookup[residuals, "literature_authority_none", False]],
  TrueQ[Lookup[residuals, "parallel_r6c_nonpromotional", False]]
];

receipt = <|
  "schema_version" -> "1.0.0",
  "stage_id" -> "SYNC_MAP_02F_R3_CONSUMER_BINDING_CONTRACTS_WOLFRAM_REPLAY",
  "repository_scope" -> "BASS_ONLY",
  "git_head" -> gitHead,
  "wolfram_version" -> $Version,
  "graph_sha256" -> fileSHA256[graphPath],
  "module_sha256" -> fileSHA256[modulePath],
  "wlt_sha256" -> fileSHA256[testPath],
  "validator_pass" -> validatorPass,
  "exact_residuals" -> residuals,
  "json_safe_association_mode" -> "ASSOCIATION_THREAD_KEYS_RECURSIVE_VALUES",
  "json_safe_probe_pass" -> True,
  "expected_top_level_munit_tests" -> expected,
  "tests_succeeded" -> succeeded,
  "tests_failed" -> failed,
  "tests_not_evaluated" -> notEvaluated,
  "receipt_write_policy" -> "TEMPORARY_FILE_STRICT_JSON_ROUND_TRIP_THEN_RENAME",
  "runtime_parity_status" -> "ALL_WITHHELD",
  "parallel_r6c_evidence_effect" -> "NONE_FOR_BINDING_ADMISSION",
  "status" -> If[allPassed, "PASS_LOCAL_EXACT_REPLAY", "FAIL_LOCAL_EXACT_REPLAY"]
|>;
receipt = jsonSafe[receipt];

If[FileExistsQ[receiptTemporaryPath], DeleteFile[receiptTemporaryPath]];
receiptJSON = Quiet@Check[ExportString[receipt, "RawJSON"], $Failed];
receiptWrite = If[
  StringQ[receiptJSON],
  Quiet@Check[Export[receiptTemporaryPath, receiptJSON, "String"], $Failed],
  $Failed
];
receiptRoundTrip = If[
  StringQ[receiptWrite] && FileExistsQ[receiptTemporaryPath] &&
  FileByteCount[receiptTemporaryPath] > 0,
  Quiet@Check[Import[receiptTemporaryPath, "RawJSON"], $Failed],
  $Failed
];
receiptRoundTripValid = And[
  AssociationQ[receiptRoundTrip],
  Lookup[receiptRoundTrip, "stage_id", None] === Lookup[receipt, "stage_id", None],
  Lookup[receiptRoundTrip, "status", None] === Lookup[receipt, "status", None],
  Lookup[receiptRoundTrip, "validator_pass", None] === True,
  Lookup[receiptRoundTrip, "json_safe_probe_pass", None] === True,
  Lookup[receiptRoundTrip, "runtime_parity_status", None] === "ALL_WITHHELD",
  Lookup[
    Lookup[receiptRoundTrip, "exact_residuals", <||>],
    "binding_request_count_residual",
    None
  ] === 0
];

If[!receiptRoundTripValid,
  Print[InputForm[<|
    "status" -> "FAIL_RECEIPT_JSON_EXPORT",
    "serialization_succeeded" -> StringQ[receiptJSON],
    "temporary_write_succeeded" -> StringQ[receiptWrite],
    "temporary_file_exists" -> FileExistsQ[receiptTemporaryPath],
    "temporary_file_bytes" -> If[
      FileExistsQ[receiptTemporaryPath], FileByteCount[receiptTemporaryPath], 0
    ],
    "round_trip_association" -> AssociationQ[receiptRoundTrip]
  |>]];
  If[FileExistsQ[receiptTemporaryPath], DeleteFile[receiptTemporaryPath]];
  Exit[3]
];

If[FileExistsQ[receiptPath], DeleteFile[receiptPath]];
RenameFile[receiptTemporaryPath, receiptPath];
If[!FileExistsQ[receiptPath] || FileByteCount[receiptPath] <= 0,
  Print[InputForm[<|
    "status" -> "FAIL_RECEIPT_JSON_EXPORT",
    "detail" -> "validated temporary receipt was not published"
  |>]];
  Exit[3]
];

Print[InputForm[receipt]];
Exit[If[allPassed, 0, 1]];
