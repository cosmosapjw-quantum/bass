#!/usr/bin/env wolframscript

scriptDirectory = DirectoryName[$InputFileName];
repositoryRoot = DirectoryName[DirectoryName[scriptDirectory]];
arguments = Rest[$ScriptCommandLine];
outputDirectory = If[
  Length[arguments] >= 1,
  ExpandFileName[First[arguments]],
  FileNameJoin[{repositoryRoot, "artifacts", "sync_map02f_r2_state_surface_registry"}]
];
If[!DirectoryQ[outputDirectory],
  CreateDirectory[outputDirectory, CreateIntermediateDirectories -> True]
];

modulePath = FileNameJoin[{
  repositoryRoot, "wolfram", "BASS", "Kernel", "IR", "BASSStateSurfaceRegistry.wl"
}];
testPath = FileNameJoin[{
  repositoryRoot, "wolfram", "BASS", "Tests", "BASSStateSurfaceRegistry.wlt"
}];
registryPath = FileNameJoin[{
  repositoryRoot, "docs", "bass_master_ssot_v2", "SYNC_MAP_02F_R2",
  "BASS_STATE_SURFACE_REGISTRY.json"
}];
receiptPath = FileNameJoin[{
  outputDirectory, "SYNC_MAP_02F_R2_STATE_SURFACE_WOLFRAM_RECEIPT.json"
}];

missing = Select[{modulePath, testPath, registryPath}, !FileExistsQ[#] &];
If[missing =!= {},
  Print[InputForm[<|"status" -> "FAIL_MISSING_INPUT", "missing" -> missing|>]];
  Exit[2]
];

Get[modulePath];
registry = Import[registryPath, "RawJSON"];
validatorPass = TrueQ[BASS`IR`BASSStateSurfaceRegistryQ[registry]];
residuals = BASS`IR`BASSStateSurfaceRegistryExactResiduals[];

report = Block[
  {Global`$BASSStateSurfaceRegistryTestData = registry},
  TestReport[testPath]
];
succeeded = Quiet@Check[report["TestsSucceededCount"], Missing["Unavailable"]];
failed = Quiet@Check[report["TestsFailedCount"], Missing["Unavailable"]];
notEvaluated = Quiet@Check[report["TestsNotEvaluatedCount"], Missing["Unavailable"]];
expected = 7;

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
  Lookup[residuals, "band_limited_grid_pstf_reconstruction", None] === 0,
  Lookup[residuals, "same_integrated_G_state", None] === 0,
  Lookup[residuals, "different_frequency_loss", None] === chi1 - chi2,
  Lookup[residuals, "scalar_to_polarized_implicit_promotion_defined", None] === False
];

receipt = <|
  "schema_version" -> "1.0.0",
  "stage_id" -> "SYNC_MAP_02F_R2_BASS_STATE_SURFACE_WOLFRAM_REPLAY",
  "repository_scope" -> "BASS_ONLY",
  "git_head" -> gitHead,
  "wolfram_version" -> $Version,
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
