#!/usr/bin/env wolframscript

Block[{$HistoryLength = 0},
 Module[{scriptDir, repositoryRoot, initFile, args, argumentValue,
   stage, xactSource, expectedSHA256, sourceCommit, sourceTree,
   testFiles, report, testsSummary, conventionLock, provenance, claims,
   receipt, receiptDirectory, receiptPath, status, stagePayload},

  scriptDir = DirectoryName[$InputFileName];
  repositoryRoot = ExpandFileName[FileNameJoin[{scriptDir, "..", ".."}]];
  initFile = FileNameJoin[{repositoryRoot, "wolfram", "BASS", "Kernel", "init.wl"}];
  If[!FileExistsQ[initFile],
   Print["BLOCKED: missing init file: " <> initFile]; Exit[2]];
  Get[initFile];

  args = Rest[$ScriptCommandLine];
  argumentValue[name_String, default_] := Module[{position},
    position = FirstPosition[args, name, Missing["NotFound"]];
    If[MissingQ[position] || First[position] >= Length[args], default,
     args[[First[position] + 1]]]
   ];

  stage = argumentValue["--stage", "W0_W1"];
  xactSource = argumentValue["--xact-source",
    Replace[Environment["BASS_XACT_SOURCE"], $Failed | "" ->
      "https://xact.es/download/xAct_1.3.0.tgz"]];
  sourceCommit = argumentValue["--source-commit", "UNSET"];
  sourceTree = argumentValue["--source-tree", "UNSET"];
  expectedSHA256 =
   "7a6c5f600868a3922668b020a15c0692f76574ff2a559808c62d460cef1b07be";

  testFiles = Switch[stage,
    "W0_W1",
    {FileNameJoin[{repositoryRoot, "wolfram", "BASS", "Tests", "W0Environment.wlt"}],
     FileNameJoin[{repositoryRoot, "wolfram", "BASS", "Tests", "W1Conventions.wlt"}]},
    "W2",
    {FileNameJoin[{repositoryRoot, "wolfram", "BASS", "Tests", "W0Environment.wlt"}],
     FileNameJoin[{repositoryRoot, "wolfram", "BASS", "Tests", "W1Conventions.wlt"}],
     FileNameJoin[{repositoryRoot, "wolfram", "BASS", "Tests", "W2AbstractGeometry.wlt"}]},
    _, Print["BLOCKED: unsupported stage: " <> ToString[stage]]; Exit[2]
   ];

  If[!AllTrue[testFiles, FileExistsQ],
   Print["BLOCKED: one or more test files are missing."]; Exit[2]];

  $BASSXActSource = xactSource;
  $BASSXActExpectedSHA256 = expectedSHA256;
  report = TestReport[testFiles];
  testsSummary = <|
    "succeeded" -> report["TestsSucceededCount"],
    "failed" -> report["TestsFailedCount"],
    "not_evaluated" -> report["TestsNotEvaluatedCount"],
    "report_succeeded" -> report["ReportSucceeded"],
    "test_files" -> testFiles|>;
  status = If[TrueQ[report["ReportSucceeded"]], "PASS", "FAIL"];
  conventionLock = BASS`Authority`ConventionLock[];
  stagePayload = If[stage === "W2",
    BASS`Geometry`Abstract1Plus3ReceiptPayload[], <||>];

  provenance = BASS`Authority`MakeProvenanceEnvelope[
    "BASS-MASTER-SSOT-V2-WOLFRAM-XACT-20260901", stage,
    <|"repository" -> "cosmosapjw-quantum/bass",
      "formula_parent_commit" -> "82776f50869d5c76e1cab4b28734c85f136c1e6f",
      "formula_parent_tree" -> "ffe65b1c48f332acdc5a7497b77a75ef64fd7500",
      "source_commit" -> sourceCommit, "source_tree" -> sourceTree|>,
    <|"convention_hash" -> BASS`IR`CanonicalSHA256[conventionLock],
      "xact_archive_sha256" -> expectedSHA256,
      "stage_payload_hash" -> BASS`IR`CanonicalSHA256[stagePayload]|>];

  claims = Switch[stage,
    "W2", <|"authorized" -> If[status === "PASS",
       {"W2_ABSTRACT_1PLUS3_PROJECTOR_AND_KINEMATIC_INFRASTRUCTURE_VERIFIED",
        "GAUSS_CODAZZI_SIGN_REGISTRY_VERIFIED"}, {}],
      "withheld" -> {"XCOBA_COMPONENT_DUAL_PROOF",
       "BACKGROUND_EINSTEIN_EQUATIONS", "BIANCHI_BRANCH_SPECIALIZATION",
       "GENERIC_ELL_COMPILER_CORRECTNESS", "NUMERICAL_PARITY",
       "CROSS_REPOSITORY_COMPATIBILITY", "SCIENCE_VALIDITY",
       "BASS_RF04_PROMOTION"}|>,
    _, <|"authorized" -> If[status === "PASS",
       {"W0_W1_SYMBOLIC_INFRASTRUCTURE_VERIFIED"}, {}],
      "withheld" -> {"BACKGROUND_TENSOR_DERIVATION",
       "BIANCHI_BRANCH_SPECIALIZATION", "GENERIC_ELL_COMPILER_CORRECTNESS",
       "NUMERICAL_PARITY", "CROSS_REPOSITORY_COMPATIBILITY",
       "SCIENCE_VALIDITY", "BASS_RF04_PROMOTION"}|>
   ];

  receipt = BASS`IR`MakeStageReceipt[stage, status,
    Join[testsSummary, <|"xact_activation" -> $BASSXActReceipt,
      "convention_hash" -> BASS`IR`CanonicalSHA256[conventionLock],
      "stage_payload" -> stagePayload|>], provenance, claims];
  receiptDirectory = FileNameJoin[{repositoryRoot, "docs",
     "bass_master_ssot_v2", stage}];
  If[!DirectoryQ[receiptDirectory],
   CreateDirectory[receiptDirectory, CreateIntermediateDirectories -> True]];
  receiptPath = FileNameJoin[{receiptDirectory, stage <> "_RECEIPT.json"}];
  Export[receiptPath, receipt, "RawJSON"];
  Print[ExportString[<|"stage" -> stage, "status" -> status,
      "tests" -> testsSummary, "receipt" -> receiptPath|>, "RawJSON"]];
  Exit[If[status === "PASS", 0, 1]]
 ]]
