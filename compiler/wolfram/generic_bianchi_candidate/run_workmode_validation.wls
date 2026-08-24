#!/usr/bin/env wolframscript
(* Work-mode-only driver.  This file is authored but never executed locally. *)

ClearAll[BASSDriverFail];
BASSDriverFail[code_String, detail_: <||>] := (Print[ExportString[<|"code" -> code, "detail" -> detail, "status" -> "FAIL"|>, "RawJSON"]]; Exit[1]);

ClearAll[BASSArgument];
BASSArgument[name_String] := Module[{position = FirstPosition[$ScriptCommandLine, name]},
  If[MissingQ[position] || First[position] >= Length[$ScriptCommandLine], BASSDriverFail["MISSING_ARGUMENT", <|"argument" -> name|>]];
  $ScriptCommandLine[[First[position] + 1]]
];

packetRoot = ExpandFileName[BASSArgument["--packet-root"]];
outputDir = ExpandFileName[BASSArgument["--output-dir"]];
xactRoot = ExpandFileName[BASSArgument["--xact-root"]];
If[! DirectoryQ[packetRoot] || ! DirectoryQ[xactRoot], BASSDriverFail["INPUT_DIRECTORY_ABSENT"]];
If[FileExistsQ[outputDir], BASSDriverFail["OUTPUT_MUST_BE_FRESH"]];

ClearAll[BASSFileSHA256];
BASSFileSHA256[path_String] := IntegerString[FileHash[path, "SHA256"], 16, 64];

ClearAll[BASSVerifyPacketManifest];
BASSVerifyPacketManifest[root_String] := Module[{manifest, lines, records, actual},
  manifest = FileNameJoin[{root, "MANIFEST.sha256"}];
  If[! FileExistsQ[manifest], BASSDriverFail["PACKET_MANIFEST_ABSENT"]];
  lines = Import[manifest, "Lines"];
  records = Map[
    Function[line, With[{parts = StringSplit[line, "  ", 2]},
      If[Length[parts] =!= 2 || ! StringMatchQ[parts[[1]], RegularExpression["[0-9a-f]{64}"]], BASSDriverFail["MALFORMED_PACKET_MANIFEST"]];
      <|"hash" -> parts[[1]], "path" -> parts[[2]]|>
    ]], lines];
  If[Lookup[records, "path"] =!= Sort[Lookup[records, "path"]] || DuplicateFreeQ[Lookup[records, "path"]] =!= True,
     BASSDriverFail["NONCANONICAL_PACKET_MANIFEST"]];
  actual = Sort[FileNameDrop[#, FileNameDepth[root]] & /@ Select[FileNames["*", root, Infinity], FileType[#] === File && FileNameTake[#] =!= "MANIFEST.sha256" &]];
  If[Lookup[records, "path"] =!= actual, BASSDriverFail["PACKET_MANIFEST_COVERAGE_MISMATCH"]];
  Scan[If[BASSFileSHA256[FileNameJoin[{root, #["path"]}]] =!= #["hash"], BASSDriverFail["PACKET_FILE_HASH_MISMATCH", <|"path" -> #["path"]|>]] &, records];
  True
];

BASSVerifyPacketManifest[packetRoot];
sourceNames = {"BianchiSpec.wl", "GenericFrameDerivation.wl", "GenericAdapters.wl", "SymIRV2Export.wl"};
Scan[Get[FileNameJoin[{packetRoot, #}]] &, sourceNames];

PrependTo[$Path, xactRoot];
Quiet[Needs["xAct`xTensor`"], {FrontEndObject::notavail, StringJoin::string, MessageName::messg}];
If[! MemberQ[$Packages, "xAct`xTensor`"] || ! NameQ["xAct`xTensor`DefTensor"], BASSDriverFail["XACT_XTENSOR_NOT_LOADED"]];
abstractBlocks = BASSInitializeXActCandidate[];
If[FailureQ[abstractBlocks], BASSDriverFail["XACT_GENERIC_INITIALIZATION_FAILED"]];

sourceHashes = Association @ Map[# -> BASSFileSHA256[FileNameJoin[{packetRoot, #}]] &, sourceNames];
xactVersion = ToString[InputForm[xAct`xTensor`$Version]];

ClearAll[BASSWriteUTF8];
BASSWriteUTF8[path_String, text_String] := Module[{stream},
  CreateDirectory[DirectoryName[path], CreateIntermediateDirectories -> True];
  stream = OpenWrite[path, CharacterEncoding -> "UTF8"];
  WriteString[stream, text];
  Close[stream];
];

ClearAll[BASSFailureExpected];
BASSFailureExpected[spec_Association] := FailureQ[BASSCanonicalizeSpec[spec]];

iiRaw = Import[FileNameJoin[{packetRoot, "fixtures", "II_equivalent.json"}], "RawJSON"];
iiCOnly = KeyDrop[iiRaw, {"na_decomposition", "matrix_generators", "generator_representation"}];
iiNAOnly = KeyDrop[iiRaw, {"structure_constants", "matrix_generators", "generator_representation"}];
iiGOnly = KeyDrop[iiRaw, {"structure_constants", "na_decomposition"}];
equivalentHashes = BASSSHA256UTF8[BASSCanonicalJSON[BASSCanonicalizeSpec[#]]] & /@ {iiCOnly, iiNAOnly, iiGOnly};
equivalentRepresentationsEqual = SameQ @@ equivalentHashes;

invalidAntisymmetry = Join[KeyDrop[iiCOnly, {"structure_constants"}], <|
  "structure_constants" -> <|"entries" -> {<|"indices" -> {0, 1, 2}, "value" -> <|"kind" -> "integer", "value" -> 1|>|>}, "shape" -> {3, 3, 3}|>
|>];
invalidJacobi = Join[KeyDrop[iiCOnly, {"structure_constants"}], <|
  "structure_constants" -> <|"entries" -> {
    <|"indices" -> {0, 0, 1}, "value" -> <|"kind" -> "integer", "value" -> 1|>|>,
    <|"indices" -> {0, 1, 0}, "value" -> <|"kind" -> "integer", "value" -> -1|>|>,
    <|"indices" -> {1, 1, 2}, "value" -> <|"kind" -> "integer", "value" -> 1|>|>,
    <|"indices" -> {1, 2, 1}, "value" -> <|"kind" -> "integer", "value" -> -1|>|>
  }, "shape" -> {3, 3, 3}|>
|>];
iiCanonical = BASSCanonicalizeSpec[iiRaw];
iiC = BASSDecodeSparse[iiCanonical["structure_constants"], {3, 3, 3}];
invalidGenerators = Normal[BASSGeneratorsFromC[iiC]];
invalidGenerators[[1, 1, 1]] = 1;

acceptanceChecks = <|
  "antisymmetry_failure_fail_closed" -> BASSFailureExpected[invalidAntisymmetry],
  "closure_failure_fail_closed" -> Not[BASSValidateGenerators[invalidGenerators, iiC]],
  "equivalent_representations_equal" -> equivalentRepresentationsEqual,
  "jacobi_failure_fail_closed" -> BASSFailureExpected[invalidJacobi]
|>;

CreateDirectory[outputDir, CreateIntermediateDirectories -> True];
CreateDirectory[FileNameJoin[{outputDir, "cold"}]];
CreateDirectory[FileNameJoin[{outputDir, "warm"}]];
CreateDirectory[FileNameJoin[{outputDir, "cache"}]];

fixtureFiles = Sort[FileNames["*.json", FileNameJoin[{packetRoot, "fixtures"}]]];
fixtureRegistry = Import[FileNameJoin[{packetRoot, "FIXTURE_REGISTRY.json"}], "RawJSON"];
registryById = Association @ Map[Lookup[#, "spec_id"] -> # &, Lookup[fixtureRegistry, "fixtures", {}]];
fixtureResults = Reap[
  Do[
    rawSpec = Import[fixturePath, "RawJSON"];
    canonicalSpec = BASSCanonicalizeSpec[rawSpec];
    If[FailureQ[canonicalSpec], BASSDriverFail["SPEC_VALIDATION_FAILED", <|"fixture" -> FileNameTake[fixturePath]|>]];
    specHash = BASSSHA256UTF8[BASSCanonicalJSON[canonicalSpec]];
    If[! KeyExistsQ[registryById, canonicalSpec["spec_id"]] || registryById[canonicalSpec["spec_id"]]["canonical_sha256"] =!= specHash,
       BASSDriverFail["FIXTURE_REGISTRY_SPEC_HASH_MISMATCH", <|"fixture" -> canonicalSpec["spec_id"]|>]];
    derived = BASSDeriveGenericFrame[canonicalSpec];
    adapters = Catch[BASSApplyExactAdapters[canonicalSpec, derived, specHash], "BASSValidation"];
    If[FailureQ[adapters], BASSDriverFail["ADAPTER_PRECONDITION_FAILED", <|"fixture" -> canonicalSpec["spec_id"]|>]];
    If[Lookup[adapters, "adapter_id"] =!= registryById[canonicalSpec["spec_id"]]["adapters"],
       BASSDriverFail["FIXTURE_REGISTRY_ADAPTER_MISMATCH", <|"fixture" -> canonicalSpec["spec_id"]|>]];
    symir = BASSBuildSymIRV2[canonicalSpec, derived, adapters, sourceHashes];
    If[symir["selected_oracle"] =!= registryById[canonicalSpec["spec_id"]]["oracle"],
       BASSDriverFail["FIXTURE_REGISTRY_ORACLE_MISMATCH", <|"fixture" -> canonicalSpec["spec_id"]|>]];
    coldText = BASSCanonicalJSON[symir];
    cacheKey = BASSSHA256UTF8[BASSCanonicalJSON[<|
      "convention_hash" -> canonicalSpec["convention_hash"],
      "pass_version" -> "generic-bianchi-candidate-1",
      "source_hashes" -> sourceHashes,
      "spec_hash" -> specHash,
      "xact_version" -> xactVersion
    |>]];
    cachePath = FileNameJoin[{outputDir, "cache", cacheKey <> ".json"}];
    BASSWriteUTF8[cachePath, coldText];
    warmText = BASSCanonicalJSON[Import[cachePath, "RawJSON"]];
    If[coldText =!= warmText, BASSDriverFail["COLD_WARM_CANONICAL_DRIFT", <|"fixture" -> canonicalSpec["spec_id"]|>]];
    coldPath = FileNameJoin[{outputDir, "cold", canonicalSpec["spec_id"] <> ".symir-v2.json"}];
    warmPath = FileNameJoin[{outputDir, "warm", canonicalSpec["spec_id"] <> ".symir-v2.json"}];
    BASSWriteUTF8[coldPath, coldText];
    BASSWriteUTF8[warmPath, warmText];
    Sow[<|
      "cold_sha256" -> BASSFileSHA256[coldPath],
      "fixture_id" -> canonicalSpec["spec_id"],
      "result_path" -> FileNameJoin[{"cold", FileNameTake[coldPath]}],
      "warm_sha256" -> BASSFileSHA256[warmPath]
    |>],
    {fixturePath, fixtureFiles}
  ]
][[2, 1]];

adapterByFixture = Association @ Map[
  Function[result, With[{obj = Import[FileNameJoin[{outputDir, result["result_path"]}], "RawJSON"]}, result["fixture_id"] -> Lookup[Lookup[obj, "adapters"], "adapter_id"]]],
  fixtureResults
];
AssociateTo[acceptanceChecks,
  "canonical_output_deterministic" -> And @@ Map[#["cold_sha256"] === #["warm_sha256"] &, fixtureResults],
  "exceptional_adapter_exact" -> MemberQ[adapterByFixture["VIstar_minus_1_9"], "exceptional_codazzi_rank_loss"],
  "selected_oracle_emitted" -> And @@ Map[KeyExistsQ[Import[FileNameJoin[{outputDir, #["result_path"]}], "RawJSON"], "selected_oracle"] &, fixtureResults],
  "typeii_specialization_no_leak" -> And @@ Map[! MemberQ[adapterByFixture[#], "rank_one_axis_projector"] &, {"VI_0", "VII_0", "VIII"}]
];
If[! And @@ Values[acceptanceChecks], BASSDriverFail["FOCUSED_ACCEPTANCE_FAILED", acceptanceChecks]];

aggregate = <|
  "acceptance_checks" -> KeySort[acceptanceChecks],
  "aggregate_status" -> "VALIDATED_NEW_CANDIDATE",
  "authority_status" -> "CANDIDATE_UNPROMOTED_FORMULA_BYTES_ABSENT",
  "cold_warm_equal" -> True,
  "fixtures" -> SortBy[fixtureResults, Lookup[#, "fixture_id"] &],
  "packet_manifest_sha256" -> BASSFileSHA256[FileNameJoin[{packetRoot, "MANIFEST.sha256"}]],
  "schema_version" -> "workmode-result-v1",
  "wolfram_environment" -> <|"kernel_version" -> $Version, "system_id" -> $SystemID, "xact_version" -> xactVersion|>
|>;
BASSWriteUTF8[FileNameJoin[{outputDir, "aggregate_result.json"}], BASSCanonicalJSON[aggregate]];

resultFiles = Sort[Select[FileNames["*", outputDir, Infinity], FileType[#] === File && FileNameTake[#] =!= "RESULT_MANIFEST.sha256" &]];
resultManifest = StringJoin @ Map[
  BASSFileSHA256[#] <> "  " <> FileNameDrop[#, FileNameDepth[outputDir]] <> "\n" &,
  resultFiles
];
BASSWriteUTF8[FileNameJoin[{outputDir, "RESULT_MANIFEST.sha256"}], resultManifest];
Print[ExportString[<|"fixture_count" -> Length[fixtureResults], "result_manifest_sha256" -> BASSFileSHA256[FileNameJoin[{outputDir, "RESULT_MANIFEST.sha256"}]], "status" -> "VALIDATED_NEW_CANDIDATE"|>, "RawJSON", "Compact" -> True]];
Exit[0];
