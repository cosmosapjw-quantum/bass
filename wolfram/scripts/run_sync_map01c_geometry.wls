#!/usr/bin/env wolframscript

Block[{$HistoryLength = 0},
 Module[{scriptDir, repositoryRoot, initFile, tests, report, summary},
  scriptDir = DirectoryName[$InputFileName];
  repositoryRoot = ExpandFileName[FileNameJoin[{scriptDir, "..", ".."}]];
  initFile = FileNameJoin[{repositoryRoot, "wolfram", "BASS", "Kernel", "init.wl"}];
  If[!FileExistsQ[initFile],
   Print["BLOCKED: missing init file: " <> initFile]; Exit[2]
  ];
  Get[initFile];
  tests = FileNameJoin[{repositoryRoot, "wolfram", "BASS", "Tests", #}] & /@ {
    "W0Environment.wlt",
    "W1Conventions.wlt",
    "ALG01BianchiAlgebra.wlt",
    "ALG01R1ExceptionalAndCovariance.wlt",
    "ALG01R2ExactIdentityAndCarriers.wlt",
    "GEO02CartanConnection.wlt",
    "GEO02R2ConnectionComposition.wlt",
    "W2AbstractGeometry.wlt",
    "W3ONFCurvature.wlt",
    "SYNCMAP01CGeometryComposition.wlt"
   };
  If[!AllTrue[tests, FileExistsQ],
   Print["BLOCKED: one or more composition test files are missing."]; Exit[2]
  ];
  report = TestReport[tests];
  summary = <|
    "stage_id" -> "SYNC_MAP_01C_GEOMETRY_LINEAGE_COMPOSITION",
    "status" -> If[TrueQ[report["ReportSucceeded"]], "PASS", "FAIL"],
    "tests_succeeded" -> report["TestsSucceededCount"],
    "tests_failed" -> report["TestsFailedCount"],
    "tests_not_evaluated" -> report["TestsNotEvaluatedCount"],
    "canonical_parent_commit" -> "c787e6c51608568fcb60d52f010235f8cb2c1076",
    "tested_donor_commit" -> "5d3e8ecce2a40a1bc2b43af7daa985e042d9815f",
    "claim_boundary" ->
     "W2_AND_SPATIAL_CURVATURE_COMPOSITION_ONLY_NO_BACKGROUND_OR_SCIENCE_PROMOTION"
   |>;
  Print[ExportString[summary, "RawJSON"]];
  Exit[If[TrueQ[report["ReportSucceeded"]], 0, 1]]
 ]
]
