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
     report["TestsFailedCount"] === 0 &&
      report["TestsNotEvaluatedCount"] === 0,
     "PASS",
     "FAIL"
    ],
   "tests_succeeded" -> report["TestsSucceededCount"],
   "tests_failed" -> report["TestsFailedCount"],
   "tests_not_evaluated" -> report["TestsNotEvaluatedCount"],
   "wolfram_version" -> $Version,
   "system_id" -> $SystemID,
   "claim_effect" -> "NONE"
  |>;
 Print[ExportString[result, "RawJSON", "Compact" -> True]];
 If[result["status"] === "PASS", result, Exit[1]]
]
