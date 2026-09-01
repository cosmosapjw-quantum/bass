#!/usr/bin/env wolframscript

Block[{$HistoryLength = 0},
 Module[
  {scriptDir, repositoryRoot, initFile, args, argumentValue,
   xactSource, expectedSHA256, testFiles, report, testsSummary,
   specs, witnesses, hostile, exactSpec, realMutation,
   provenance, claims, receipt, receiptDirectory, receiptPath, status},

  scriptDir = DirectoryName[$InputFileName];
  repositoryRoot = ExpandFileName[
    FileNameJoin[{scriptDir, "..", ".."}]
   ];
  initFile = FileNameJoin[
    {repositoryRoot, "wolfram", "BASS", "Kernel", "init.wl"}
   ];
  If[! FileExistsQ[initFile],
   Print["BLOCKED: missing init file: " <> initFile]; Exit[2]];
  Get[initFile];

  args = Rest[$ScriptCommandLine];
  argumentValue[name_String, default_] := Module[{position},
    position = FirstPosition[args, name, Missing["NotFound"]];
    If[MissingQ[position] || First[position] >= Length[args],
     default, args[[First[position] + 1]]]
   ];
  xactSource = argumentValue[
    "--xact-source",
    Replace[Environment["BASS_XACT_SOURCE"],
     $Failed | "" -> "https://xact.es/download/xAct_1.3.0.tgz"]
   ];
  expectedSHA256 =
   "7a6c5f600868a3922668b020a15c0692f76574ff2a559808c62d460cef1b07be";
  $BASSXActSource = xactSource;
  $BASSXActExpectedSHA256 = expectedSHA256;

  testFiles = {
    FileNameJoin[{repositoryRoot, "wolfram", "BASS", "Tests",
      "W0Environment.wlt"}],
    FileNameJoin[{repositoryRoot, "wolfram", "BASS", "Tests",
      "W1Conventions.wlt"}],
    FileNameJoin[{repositoryRoot, "wolfram", "BASS", "Tests",
      "ALG01BianchiAlgebra.wlt"}],
    FileNameJoin[{repositoryRoot, "wolfram", "BASS", "Tests",
      "ALG01R1ExceptionalAndCovariance.wlt"}],
    FileNameJoin[{repositoryRoot, "wolfram", "BASS", "Tests",
      "ALG01R2ExactIdentityAndCarriers.wlt"}]
   };
  If[! AllTrue[testFiles, FileExistsQ],
   Print["BLOCKED: one or more test files are missing."]; Exit[2]];

  report = TestReport[testFiles];
  specs = BASS`Bianchi`CanonicalTypeSpecRegistry[];
  witnesses = BASS`Bianchi`ValidateWitnessRegistry[];
  hostile = BASS`Bianchi`ValidateHostileWitnesses[];
  exactSpec = specs["VI_-1/9"];
  realMutation = ReplacePart[
    exactSpec,
    "expected" -> ReplacePart[
      exactSpec["expected"], "signed_h" -> N[-1/9]]
   ];

  testsSummary = <|
    "succeeded" -> report["TestsSucceededCount"],
    "failed" -> report["TestsFailedCount"],
    "not_evaluated" -> report["TestsNotEvaluatedCount"],
    "report_succeeded" -> report["ReportSucceeded"],
    "test_files" -> testFiles,
    "canonical_pass" -> AllTrue[Values[witnesses],
      TrueQ[Lookup[#, "pass", False]] &],
    "hostile_detection_pass" -> AllTrue[Values[hostile],
      TrueQ[Lookup[#, "detected", False]] &],
    "hostile_ids" -> Keys[hostile],
    "exceptional_carrier_report" ->
     BASS`Bianchi`ExceptionalShearCarrierReport[
      BASS`Bianchi`CanonicalWitnessRegistry[]["VI_-1/9"]],
    "exact_signed_h" -> exactSpec["expected"]["signed_h"],
    "machine_real_spec_rejected" ->
     Not[BASS`Bianchi`BianchiTypeSpecQ[realMutation]],
    "exact_real_hash_separated" ->
     BASS`IR`CanonicalSHA256[exactSpec] =!=
      BASS`IR`CanonicalSHA256[realMutation]
   |>;
  status = If[TrueQ[report["ReportSucceeded"]] &&
    TrueQ[testsSummary["canonical_pass"]] &&
    TrueQ[testsSummary["hostile_detection_pass"]] &&
    TrueQ[testsSummary["machine_real_spec_rejected"]] &&
    TrueQ[testsSummary["exact_real_hash_separated"]],
   "PASS", "FAIL"];

  provenance = BASS`Authority`MakeProvenanceEnvelope[
    "BASS-MASTER-SSOT-V2-WOLFRAM-XACT-20260901",
    "ALG_01R2",
    <|
     "repository" -> "cosmosapjw-quantum/bass",
     "exact_parent_commit" ->
      "24e8d5ae3b7e929e34ca62d7070ce00e0960fb46",
     "exact_parent_tree" ->
      "a0f8cab48cdb32c18282d512f2b2ecb45083b62d"
    |>,
    <|
     "convention_hash" -> BASS`IR`CanonicalSHA256[
       BASS`Authority`ConventionLock[]],
     "xact_archive_sha256" -> expectedSHA256,
     "exact_type_spec_hash" -> BASS`IR`CanonicalSHA256[exactSpec]
    |>
   ];
  claims = <|
    "authorized" -> If[status === "PASS",
      {"ALG_01R2_EXACT_IDENTITY_AND_TWO_CARRIER_WITNESS_VERIFIED"}, {}],
    "withheld" -> {
      "CARTAN_CONNECTION_OR_CURVATURE_DERIVATION",
      "BACKGROUND_EINSTEIN_MATTER_EQUATIONS",
      "ALL_FAMILY_SOLVER_SUPPORT",
      "GENERIC_ELL_COMPILER_CORRECTNESS",
      "NUMERICAL_PARITY",
      "CROSS_REPOSITORY_COMPATIBILITY",
      "SCIENCE_VALIDITY",
      "BASS_RF04_PROMOTION"
     }
   |>;
  receipt = BASS`IR`MakeStageReceipt[
    "ALG_01R2", status, testsSummary, provenance, claims];
  receiptDirectory = FileNameJoin[
    {repositoryRoot, "docs", "bass_master_ssot_v2", "ALG_01R2"}];
  If[! DirectoryQ[receiptDirectory],
   CreateDirectory[receiptDirectory, CreateIntermediateDirectories -> True]];
  receiptPath = FileNameJoin[
    {receiptDirectory, "ALG_01R2_RECEIPT.json"}];
  Export[receiptPath, receipt, "RawJSON"];
  Print[ExportString[<|
     "stage" -> "ALG_01R2", "status" -> status,
     "tests" -> testsSummary, "receipt" -> receiptPath|>, "RawJSON"]];
  Exit[If[status === "PASS", 0, 1]]
 ]
]
