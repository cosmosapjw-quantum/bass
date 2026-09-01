#!/usr/bin/env wolframscript

Block[{$HistoryLength = 0},
 Module[
  {scriptDir, repositoryRoot, initFile, args, argumentValue, stage,
   xactSource, expectedSHA256, sourceCommit, sourceTree, testFiles,
   report, testsSummary, conventionLock, provenance, claims, receipt,
   receiptDirectory, receiptPath, status, authorizedClaims,
   withheldClaims, stageEvidence, canonicalWitnesses, hostileWitnesses,
   w2Payload},

  scriptDir = DirectoryName[$InputFileName];
  repositoryRoot = ExpandFileName[FileNameJoin[{scriptDir, "..", ".."}]];
  initFile = FileNameJoin[
    {repositoryRoot, "wolfram", "BASS", "Kernel", "init.wl"}
   ];
  If[!FileExistsQ[initFile],
   Print["BLOCKED: missing init file: " <> initFile];
   Exit[2]
  ];
  Get[initFile];

  args = Rest[$ScriptCommandLine];
  argumentValue[name_String, default_] := Module[{position},
    position = FirstPosition[args, name, Missing["NotFound"]];
    If[MissingQ[position] || First[position] >= Length[args],
     default, args[[First[position] + 1]]]
   ];

  stage = argumentValue["--stage", "W0_W1"];
  xactSource = argumentValue[
    "--xact-source",
    Replace[Environment["BASS_XACT_SOURCE"],
     $Failed | "" -> "https://xact.es/download/xAct_1.3.0.tgz"]
   ];
  sourceCommit = argumentValue["--source-commit", "UNSET"];
  sourceTree = argumentValue["--source-tree", "UNSET"];
  expectedSHA256 =
   "7a6c5f600868a3922668b020a15c0692f76574ff2a559808c62d460cef1b07be";

  Switch[stage,
   "W0_W1",
   testFiles = {
     FileNameJoin[{repositoryRoot, "wolfram", "BASS", "Tests",
       "W0Environment.wlt"}],
     FileNameJoin[{repositoryRoot, "wolfram", "BASS", "Tests",
       "W1Conventions.wlt"}]
    };
   authorizedClaims = {"W0_W1_SYMBOLIC_INFRASTRUCTURE_VERIFIED"};
   withheldClaims = {
     "BACKGROUND_TENSOR_DERIVATION", "BIANCHI_BRANCH_SPECIALIZATION",
     "GENERIC_ELL_COMPILER_CORRECTNESS", "NUMERICAL_PARITY",
     "CROSS_REPOSITORY_COMPATIBILITY", "SCIENCE_VALIDITY",
     "BASS_RF04_PROMOTION"},

   "ALG_01",
   testFiles = {
     FileNameJoin[{repositoryRoot, "wolfram", "BASS", "Tests",
       "W0Environment.wlt"}],
     FileNameJoin[{repositoryRoot, "wolfram", "BASS", "Tests",
       "W1Conventions.wlt"}],
     FileNameJoin[{repositoryRoot, "wolfram", "BASS", "Tests",
       "ALG01BianchiAlgebra.wlt"}],
     FileNameJoin[{repositoryRoot, "wolfram", "BASS", "Tests",
       "ALG01R1ExceptionalAndCovariance.wlt"}]
    };
   authorizedClaims = {
     "ALG_01_BIANCHI_ALGEBRA_WITNESSES_VERIFIED",
     "ALG_01_EXCEPTIONAL_SHEAR_AND_O3_COVARIANCE_VERIFIED"};
   withheldClaims = {
     "CARTAN_CONNECTION_OR_CURVATURE_DERIVATION",
     "BACKGROUND_EINSTEIN_MATTER_EQUATIONS",
     "ALL_FAMILY_SOLVER_SUPPORT", "GENERIC_ELL_COMPILER_CORRECTNESS",
     "NUMERICAL_PARITY", "CROSS_REPOSITORY_COMPATIBILITY",
     "SCIENCE_VALIDITY", "BASS_RF04_PROMOTION"},

   "W2",
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
       "W2AbstractGeometry.wlt"}]
    };
   authorizedClaims = {
     "ALG_01_BIANCHI_ALGEBRA_WITNESSES_VERIFIED",
     "ALG_01_EXCEPTIONAL_SHEAR_AND_O3_COVARIANCE_VERIFIED",
     "W2_ABSTRACT_1PLUS3_PROJECTOR_AND_KINEMATIC_INFRASTRUCTURE_VERIFIED",
     "GAUSS_CODAZZI_SIGN_REGISTRY_VERIFIED"};
   withheldClaims = {
     "XCOBA_COMPONENT_DUAL_PROOF", "ONF_CONNECTION_CURVATURE_PROOF",
     "BACKGROUND_EINSTEIN_EQUATIONS", "ALL_FAMILY_SOLVER_SUPPORT",
     "GENERIC_ELL_COMPILER_CORRECTNESS", "NUMERICAL_PARITY",
     "CROSS_REPOSITORY_COMPATIBILITY", "SCIENCE_VALIDITY",
     "BASS_RF04_PROMOTION"},

   _,
   Print["BLOCKED: unsupported stage: " <> ToString[stage]];
   Exit[2]
  ];

  $BASSXActSource = xactSource;
  $BASSXActExpectedSHA256 = expectedSHA256;
  If[!AllTrue[testFiles, FileExistsQ],
   Print["BLOCKED: one or more test files are missing."];
   Exit[2]
  ];

  report = TestReport[testFiles];
  status = If[TrueQ[report["ReportSucceeded"]], "PASS", "FAIL"];

  stageEvidence = Switch[stage,
    "W0_W1", <||>,
    "ALG_01",
    canonicalWitnesses = BASS`Bianchi`ValidateWitnessRegistry[];
    hostileWitnesses = BASS`Bianchi`ValidateHostileWitnesses[];
    <|
     "canonical_labels" -> Keys[canonicalWitnesses],
     "canonical_pass" -> AllTrue[Values[canonicalWitnesses],
       TrueQ[Lookup[#, "pass", False]] &],
     "hostile_ids" -> Keys[hostileWitnesses],
     "hostile_detection_pass" -> AllTrue[Values[hostileWitnesses],
       TrueQ[Lookup[#, "detected", False]] &],
     "exceptional_not_twelfth_type" -> SameQ[
       BASS`Bianchi`CanonicalTypeSpecRegistry[]["VI_-1/9"]
        ["counted_public_algebra_type"], False],
     "exceptional_shear_survival" -> TrueQ[
       BASS`Bianchi`ValidateCanonicalWitness["VI_-1/9"]
        ["checks"]["witness_obligations"]],
     "exceptional_shear_delete_detected" -> TrueQ[
       hostileWitnesses["EXCEPTIONAL_SHEAR_DELETE"]["detected"]]
    |>,
    "W2",
    canonicalWitnesses = BASS`Bianchi`ValidateWitnessRegistry[];
    hostileWitnesses = BASS`Bianchi`ValidateHostileWitnesses[];
    w2Payload = BASS`Geometry`Abstract1Plus3ReceiptPayload[];
    <|
     "alg_01" -> <|
       "canonical_labels" -> Keys[canonicalWitnesses],
       "canonical_pass" -> AllTrue[Values[canonicalWitnesses],
         TrueQ[Lookup[#, "pass", False]] &],
       "hostile_ids" -> Keys[hostileWitnesses],
       "hostile_detection_pass" -> AllTrue[Values[hostileWitnesses],
         TrueQ[Lookup[#, "detected", False]] &]
      |>,
     "w2" -> w2Payload,
     "dag_parent_commit" ->
      "24e8d5ae3b7e929e34ca62d7070ce00e0960fb46",
     "dag_parent_tree" ->
      "a0f8cab48cdb32c18282d512f2b2ecb45083b62d"
    |>
   ];

  testsSummary = <|
    "succeeded" -> report["TestsSucceededCount"],
    "failed" -> report["TestsFailedCount"],
    "not_evaluated" -> report["TestsNotEvaluatedCount"],
    "report_succeeded" -> report["ReportSucceeded"],
    "test_files" -> testFiles,
    "stage_evidence" -> stageEvidence
   |>;
  conventionLock = BASS`Authority`ConventionLock[];
  provenance = BASS`Authority`MakeProvenanceEnvelope[
    "BASS-MASTER-SSOT-V2-WOLFRAM-XACT-20260901", stage,
    <|
     "repository" -> "cosmosapjw-quantum/bass",
     "formula_base_commit" ->
      "0ac9f7e0ce8ff88dc7f4487a97e21be2863af207",
     "formula_base_tree" ->
      "8775d24f8ddc607be20879873d845e8568acfe15",
     "w0_w1_commit" ->
      "82776f50869d5c76e1cab4b28734c85f136c1e6f",
     "w0_w1_tree" ->
      "ffe65b1c48f332acdc5a7497b77a75ef64fd7500",
     "alg_01_commit" ->
      "24e8d5ae3b7e929e34ca62d7070ce00e0960fb46",
     "alg_01_tree" ->
      "a0f8cab48cdb32c18282d512f2b2ecb45083b62d",
     "source_commit" -> sourceCommit,
     "source_tree" -> sourceTree
    |>,
    <|
     "convention_hash" -> BASS`IR`CanonicalSHA256[conventionLock],
     "xact_archive_sha256" -> expectedSHA256,
     "stage_evidence_hash" -> BASS`IR`CanonicalSHA256[stageEvidence]
    |>
   ];

  claims = <|
    "authorized" -> If[status === "PASS", authorizedClaims, {}],
    "withheld" -> withheldClaims
   |>;
  receipt = BASS`IR`MakeStageReceipt[stage, status,
    Join[testsSummary, <|
      "xact_activation" -> $BASSXActReceipt,
      "convention_hash" -> BASS`IR`CanonicalSHA256[conventionLock]
     |>], provenance, claims];

  receiptDirectory = FileNameJoin[
    {repositoryRoot, "docs", "bass_master_ssot_v2", stage}];
  If[!DirectoryQ[receiptDirectory],
   CreateDirectory[receiptDirectory, CreateIntermediateDirectories -> True]];
  receiptPath = FileNameJoin[{receiptDirectory, stage <> "_RECEIPT.json"}];
  Export[receiptPath, receipt, "RawJSON"];
  Print[ExportString[<|
     "stage" -> stage, "status" -> status,
     "tests" -> testsSummary, "receipt" -> receiptPath|>, "RawJSON"]];
  Exit[If[status === "PASS", 0, 1]]
 ]
]
