#!/usr/bin/env wolframscript

ClearAll[fileSHA256];
fileSHA256[path_String] := IntegerString[FileHash[path, "SHA256"], 16, 64];

scriptDirectory = DirectoryName[$InputFileName];
repositoryRoot = DirectoryName[DirectoryName[scriptDirectory]];
arguments = Rest[$ScriptCommandLine];
outputDirectory = If[
  Length[arguments] >= 1,
  ExpandFileName[First[arguments]],
  FileNameJoin[{repositoryRoot, "artifacts", "sync_map02f_r2a_role_graph"}]
];
If[!DirectoryQ[outputDirectory],
  CreateDirectory[outputDirectory, CreateIntermediateDirectories -> True]
];

modulePath = FileNameJoin[{
  repositoryRoot, "wolfram", "BASS", "Kernel", "IR",
  "FormulaConsumerRoleGraphR2A.wl"
}];
testPath = FileNameJoin[{
  repositoryRoot, "wolfram", "BASS", "Tests",
  "FormulaConsumerRoleGraphR2A.wlt"
}];
graphPath = FileNameJoin[{
  repositoryRoot, "docs", "bass_master_ssot_v2", "SYNC_MAP_02F_R2A",
  "FORMULA_CONSUMER_ROLE_GRAPH.json"
}];
receiptPath = FileNameJoin[{
  outputDirectory, "SYNC_MAP_02F_R2A_WOLFRAM_REPLAY_RECEIPT.json"
}];

missing = Select[{modulePath, testPath, graphPath}, !FileExistsQ[#] &];
If[missing =!= {},
  Print[InputForm[<|"status" -> "FAIL_MISSING_INPUT", "missing" -> missing|>]];
  Exit[2]
];

Get[modulePath];
graph = Import[graphPath, "RawJSON"];
validatorPass = TrueQ[
  BASS`IR`FormulaConsumerRoleGraphR2A`BASSFormulaConsumerRoleGraphR2AQ[graph]
];
residuals =
  BASS`IR`FormulaConsumerRoleGraphR2A`BASSFormulaConsumerRoleGraphR2AResiduals[graph];

report = Block[
  {Global`$BASSFormulaConsumerRoleGraphR2ATestData = graph},
  TestReport[testPath]
];
succeeded = Quiet@Check[report["TestsSucceededCount"], Missing["Unavailable"]];
failed = Quiet@Check[report["TestsFailedCount"], Missing["Unavailable"]];
notEvaluated = Quiet@Check[report["TestsNotEvaluatedCount"], Missing["Unavailable"]];
expected = 11;

gitHead = Quiet@Check[
  StringTrim@RunProcess[
    {"git", "-C", repositoryRoot, "rev-parse", "HEAD"},
    "StandardOutput"
  ],
  Missing["GitUnavailable"]
];

allPassed = And[
  validatorPass,
  succeeded === expected,
  failed === 0,
  notEvaluated === 0,
  Lookup[residuals, "pair_count_residual", None] === 0,
  Lookup[residuals, "pair_uniqueness_residual", None] === 0,
  Lookup[residuals, "role_count_residual", None] === 0,
  Lookup[residuals, "named_symbol_count_residual", None] === 0,
  Lookup[residuals, "absent_slot_count_residual", None] === 0,
  Lookup[residuals, "htt_blackbody_role_count_residual", None] === 0,
  Lookup[residuals, "rei_energy_exact_residual", None] === 0,
  !TrueQ[PossibleZeroQ[Lookup[residuals, "rei_wrong_sign_mutant_residual", 0]]],
  TrueQ[Lookup[residuals, "stage_dag_acyclic", False]]
];

receipt = <|
  "schema_version" -> "1.0.0",
  "stage_id" -> "SYNC_MAP_02F_R2A_FORMULA_CONSUMER_ROLE_GRAPH_WOLFRAM_REPLAY",
  "repository_scope" -> "BASS_ONLY",
  "git_head" -> gitHead,
  "wolfram_version" -> $Version,
  "graph_sha256" -> fileSHA256[graphPath],
  "module_sha256" -> fileSHA256[modulePath],
  "wlt_sha256" -> fileSHA256[testPath],
  "validator_pass" -> validatorPass,
  "exact_residuals" -> residuals,
  "expected_top_level_munit_tests" -> expected,
  "tests_succeeded" -> succeeded,
  "tests_failed" -> failed,
  "tests_not_evaluated" -> notEvaluated,
  "status" -> If[allPassed, "PASS_LOCAL_EXACT_REPLAY", "FAIL_LOCAL_EXACT_REPLAY"]
|>;
Export[receiptPath, receipt, "RawJSON"];
Print[InputForm[receipt]];
Exit[If[allPassed, 0, 1]];
