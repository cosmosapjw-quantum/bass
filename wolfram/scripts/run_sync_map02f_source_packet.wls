#!/usr/bin/env wolframscript

root = DirectoryName[DirectoryName[$InputFileName]];
testFile = FileNameJoin[{root, "BASS", "Tests", "SYNCMAP02FCrossRepositorySemanticGraph.wlt"}];

If[!FileExistsQ[testFile],
 Print[ExportString[<|"status" -> "FAIL", "reason" -> "missing_test_file"|>, "RawJSON"]];
 Exit[2]
];

report = TestReport[testFile];
result = <|
 "status" -> If[report["TestsFailedCount"] === 0 && report["TestsNotEvaluatedCount"] === 0, "PASS", "FAIL"],
 "tests_succeeded" -> report["TestsSucceededCount"],
 "tests_failed" -> report["TestsFailedCount"],
 "tests_not_evaluated" -> report["TestsNotEvaluatedCount"],
 "expected_test_count" -> 12,
 "wolfram_version" -> $Version,
 "system_id" -> $SystemID,
 "authority_effect" -> "NONE_BEYOND_BOUNDED_SEMANTIC_GRAPH"
|>;
Print[ExportString[result, "RawJSON"]];
Exit[If[result["status"] === "PASS" && result["tests_succeeded"] === 12, 0, 1]];
