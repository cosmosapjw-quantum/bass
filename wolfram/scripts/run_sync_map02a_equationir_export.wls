#!/usr/bin/env wolframscript

Block[{$HistoryLength = 0},
 Module[
  {scriptDir, repositoryRoot, initFile, testNames, tests, report,
   exportPayload, exportValid, outputDir, outputPath, summary, status},

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
  $BASSXActSource = Replace[
    Environment["BASS_XACT_SOURCE"],
    $Failed | "" -> "https://xact.es/download/xAct_1.3.0.tgz"
   ];
  $BASSXActExpectedSHA256 =
   "7a6c5f600868a3922668b020a15c0692f76574ff2a559808c62d460cef1b07be";

  testNames = {
    "W0Environment.wlt",
    "W1Conventions.wlt",
    "ALG01BianchiAlgebra.wlt",
    "ALG01R1ExceptionalAndCovariance.wlt",
    "ALG01R2ExactIdentityAndCarriers.wlt",
    "GEO02CartanConnection.wlt",
    "GEO02R2ConnectionComposition.wlt",
    "W2AbstractGeometry.wlt",
    "W3ONFCurvature.wlt",
    "SYNCMAP01CGeometryComposition.wlt",
    "SYNCMAP02AEquationIRExport.wlt"
   };
  tests = FileNameJoin[
     {repositoryRoot, "wolfram", "BASS", "Tests", #}
    ] & /@ testNames;

  If[!AllTrue[tests, FileExistsQ],
   Print["BLOCKED: one or more semantic-export test files are missing."];
   Exit[2]
  ];

  report = TestReport[tests];
  exportPayload = BASS`IR`BASSFormulaSemanticExport[];
  exportValid = BASS`IR`BASSFormulaSemanticExportQ[exportPayload];
  status = If[TrueQ[report["ReportSucceeded"]] && TrueQ[exportValid],
    "PASS", "FAIL"];

  outputDir = FileNameJoin[
    {repositoryRoot, "docs", "bass_master_ssot_v2", "SYNC_MAP_02A"}
   ];
  If[!DirectoryQ[outputDir],
   CreateDirectory[outputDir, CreateIntermediateDirectories -> True]
  ];
  outputPath = FileNameJoin[
    {outputDir, "BASS_FORMULA_SEMANTIC_EXPORT.json"}
   ];
  Export[outputPath, exportPayload, "RawJSON"];

  summary = <|
    "stage_id" ->
     "SYNC_MAP_02A_BASS_EQUATIONIR_AND_SEMANTIC_HASH_EXPORT",
    "status" -> status,
    "tests_succeeded" -> report["TestsSucceededCount"],
    "tests_failed" -> report["TestsFailedCount"],
    "tests_not_evaluated" -> report["TestsNotEvaluatedCount"],
    "formula_count" -> Lookup[exportPayload, "formula_count", Missing[]],
    "registry_semantic_hash" ->
     Lookup[exportPayload, "registry_semantic_hash", Missing[]],
    "export_valid" -> exportValid,
    "output_path" -> outputPath,
    "claim_boundary" ->
     "BASS_FORMULA_SEMANTIC_EXPORT_ONLY_NO_CROSS_REPO_EQUIVALENCE_BACKGROUND_OR_SCIENCE_PROMOTION"
   |>;

  Print[ExportString[summary, "RawJSON"]];
  Exit[If[status === "PASS", 0, 1]]
 ]
]
