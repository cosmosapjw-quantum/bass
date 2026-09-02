#!/usr/bin/env wolframscript

Module[{root, testPath, report, result},
 root = Nest[DirectoryName, $InputFileName, 3];
 $SyncMap02ESourceRoot = root;
 Needs["MUnit`"];
 testPath = FileNameJoin[{
    root, "wolfram", "BASS", "Tests",
    "SYNCMAP02ESharedFramePhotonExport.wlt"
   }];
 report = TestReport[testPath];
 result = <|
   "status" -> If[
     report["TestsSucceededCount"] === 13 &&
      report["TestsFailedCount"] === 0 &&
      report["TestsNotEvaluatedCount"] === 0,
     "PASS",
     "FAIL"
    ],
   "tests_succeeded" -> report["TestsSucceededCount"],
   "tests_failed" -> report["TestsFailedCount"],
   "tests_not_evaluated" -> report["TestsNotEvaluatedCount"],
   "expected_test_count" -> 13,
   "wolfram_version" -> $Version,
   "system_id" -> $SystemID,
   "claim_effect" -> "NONE"
  |>;
 Print[ExportString[result, "RawJSON", "Compact" -> True]];
 If[result["status"] === "PASS", result, Exit[1]]
]
