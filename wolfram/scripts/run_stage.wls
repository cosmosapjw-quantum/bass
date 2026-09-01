#!/usr/bin/env wolframscript

Block[{$HistoryLength = 0},
 Module[{scriptDir, repositoryRoot, initFile, args, argumentValue, stage,
   xactSource, expectedSHA256, testFiles, report, testsSummary,
   conventionLock, provenance, claims, receipt, receiptPath, status,
   stageDirectory, predecessorCommit, predecessorTree},
  scriptDir = DirectoryName[$InputFileName];
  repositoryRoot = ExpandFileName[FileNameJoin[{scriptDir, "..", ".."}]];
  initFile = FileNameJoin[{repositoryRoot, "wolfram", "BASS", "Kernel", "init.wl"}];
  If[! FileExistsQ[initFile], Print["BLOCKED: missing init file: " <> initFile]; Exit[2]];
  Get[initFile];
  args = Rest[$ScriptCommandLine];
  argumentValue[name_String, default_] := Module[{position},
    position = FirstPosition[args, name, Missing["NotFound"]];
    If[MissingQ[position] || First[position] >= Length[args], default,
     args[[First[position] + 1]]]];
  stage = argumentValue["--stage", "W0_W1"];
  xactSource = argumentValue["--xact-source",
    Replace[Environment["BASS_XACT_SOURCE"], $Failed | "" ->
      "https://xact.es/download/xAct_1.3.0.tgz"]];
  expectedSHA256 = "7a6c5f600868a3922668b020a15c0692f76574ff2a559808c62d460cef1b07be";
  {testFiles, stageDirectory, predecessorCommit, predecessorTree} = Switch[stage,
    "W0_W1",
     {{
       FileNameJoin[{repositoryRoot, "wolfram", "BASS", "Tests", "W0Environment.wlt"}],
       FileNameJoin[{repositoryRoot, "wolfram", "BASS", "Tests", "W1Conventions.wlt"]
      }, "W0_W1",
      "0ac9f7e0ce8ff88dc7f4487a97e21be2863af207",
      "8775d24f8ddc607be20879873d845e8568acfe15"},
    "ALG_01",
     {{
       FileNameJoin[{repositoryRoot, "wolfram", "BASS", "Tests", "W0Environment.wlt"}],
       FileNameJoin[{repositoryRoot, "wolfram", "BASS", "Tests", "W1Conventions.wlt"}],
       FileNameJoin[{repositoryRoot, "wolfram", "BASS", "Tests", "ALG01", "WitnessDesign.wlt"]
      }, "ALG_01",
      "82776f50869d5c76e1cab4b28734c85f136c1e6f",
      "ffe65b1c48f332acdc5a7497b77a75ef64fd7500"},
    "BG_02",
     {{
       FileNameJoin[{repositoryRoot, "wolfram", "BASS", "Tests", "W0Environment.wlt"}],
       FileNameJoin[{repositoryRoot, "wolfram", "BASS", "Tests", "W1Conventions.wlt"}],
       FileNameJoin[{repositoryRoot, "wolfram", "BASS", "Tests", "ALG01", "WitnessDesign.wlt"]],
       FileNameJoin[{repositoryRoot, "wolfram", "BASS", "Tests", "BG02", "GRBackgroundConstraints.wlt"]],
       FileNameJoin[{repositoryRoot, "wolfram", "BASS", "Tests", "BG02", "TypeVMetricPropagation.wlt"]
      }, "BG_02",
      "c35177409909b7eef0f5c99c0c61a456b5e55117",
      "c2fa8cd3f34b46b9522479501a502d1ecd5ded6a"},
    _, Print["BLOCKED: unsupported stage: " <> ToString[stage]]; Exit[2]
   ];
  If[! AllTrue[testFiles, FileExistsQ],
   Print["BLOCKED: one or more test files are missing."]; Exit[2]];
  $BASSXActSource = xactSource;
  $BASSXActExpectedSHA256 = expectedSHA256;
  report = TestReport[testFiles];
  testsSummary = <|"succeeded" -> report["TestsSucceededCount"],
    "failed" -> report["TestsFailedCount"],
    "not_evaluated" -> report["TestsNotEvaluatedCount"],
    "report_succeeded" -> report["ReportSucceeded"], "test_files" -> testFiles|>;
  status = If[TrueQ[report["ReportSucceeded"]], "PASS", "FAIL"];
  conventionLock = BASS`Authority`ConventionLock[];
  provenance = BASS`Authority`MakeProvenanceEnvelope[
    "BASS-MASTER-SSOT-V2-WOLFRAM-XACT-20260901", stage,
    <|"repository" -> "cosmosapjw-quantum/bass",
     "predecessor_commit" -> predecessorCommit,
     "predecessor_tree" -> predecessorTree|>,
    <|"convention_hash" -> BASS`IR`CanonicalSHA256[conventionLock],
     "xact_archive_sha256" -> expectedSHA256|>];
  claims = Switch[stage,
    "W0_W1",
     <|"authorized" -> If[status === "PASS",
       {"W0_W1_SYMBOLIC_INFRASTRUCTURE_VERIFIED"}, {}],
      "withheld" -> {"BACKGROUND_TENSOR_DERIVATION",
       "BIANCHI_BRANCH_SPECIALIZATION", "GENERIC_ELL_COMPILER_CORRECTNESS",
       "NUMERICAL_PARITY", "CROSS_REPOSITORY_COMPATIBILITY",
       "SCIENCE_VALIDITY", "BASS_RF04_PROMOTION"}|>,
    "ALG_01",
     <|"authorized" -> If[status === "PASS",
       {"PASS_ALG01_WITNESS_GENERATOR"}, {}],
      "withheld" -> {"SPACETIME_BACKGROUND_EINSTEIN_DERIVATION",
       "ALL_ELEVEN_BRANCH_BACKGROUND_SUPPORT", "MATTER_EVOLUTION",
       "GENERIC_ELL_COMPILER_CORRECTNESS", "NUMERICAL_PARITY",
       "CROSS_REPOSITORY_COMPATIBILITY", "SCIENCE_VALIDITY",
       "BASS_RF04_PROMOTION"}|>,
    "BG_02",
     <|"authorized" -> If[status === "PASS",
       {"PASS_BG02_GR_PROJECTION_DESIGN",
        "PASS_BG02_CONSTRAINT_PROPAGATION_DESIGN",
        "PASS_BG02_TYPE_V_METRIC_AUDIT"}, {}],
      "withheld" -> {"ALL_ELEVEN_BRANCH_BACKGROUND_SUPPORT",
       "MATTER_MODEL_CLOSURE", "TILTED_MATTER_EVOLUTION",
       "CHART_EVENT_IMPLEMENTATION", "NUMERICAL_PARITY",
       "GENERIC_ELL_COMPILER_CORRECTNESS",
       "CROSS_REPOSITORY_COMPATIBILITY", "SCIENCE_VALIDITY",
       "BASS_RF04_PROMOTION"}|>
   ];
  receipt = BASS`IR`MakeStageReceipt[stage, status,
    Join[testsSummary, <|"xact_activation" -> $BASSXActReceipt,
      "convention_hash" -> BASS`IR`CanonicalSHA256[conventionLock]|>],
    provenance, claims];
  receiptPath = FileNameJoin[{repositoryRoot, "docs", "bass_master_ssot_v2",
     stageDirectory, stageDirectory <> "_RECEIPT.json"}];
  Export[receiptPath, receipt, "RawJSON"];
  Print[ExportString[<|"stage" -> stage, "status" -> status,
     "tests" -> testsSummary, "receipt" -> receiptPath|>, "RawJSON"]];
  Exit[If[status === "PASS", 0, 1]]
 ]]
