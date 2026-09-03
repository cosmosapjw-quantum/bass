#!/usr/bin/env wolframscript

ClearAll[fileSHA256, processExitCode, processStandardOutput];

fileSHA256[path_String] := IntegerString[FileHash[path, "SHA256"], 16, 64];
processExitCode[result_Association] := Lookup[result, "ExitCode", Missing["ExitCode"]];
processStandardOutput[result_Association] := Lookup[result, "StandardOutput", ""];

scriptDirectory = DirectoryName[$InputFileName];
repositoryRoot = DirectoryName[DirectoryName[scriptDirectory]];
arguments = Rest[$ScriptCommandLine];
outputDirectory = If[
  Length[arguments] >= 1,
  ExpandFileName[First[arguments]],
  FileNameJoin[{
    repositoryRoot,
    "artifacts",
    "sync_map02e_r1_local_replay"
  }]
];

If[!DirectoryQ[outputDirectory],
  CreateDirectory[outputDirectory, CreateIntermediateDirectories -> True]
];

parentPath = FileNameJoin[{
  repositoryRoot,
  "docs",
  "bass_master_ssot_v2",
  "SYNC_MAP_02E",
  "BASS_SHARED_FRAME_PHOTON_EXPORT.json"
}];
outputPath = FileNameJoin[{
  outputDirectory,
  "BASS_SHARED_FRAME_PHOTON_EXPORT_R1.json"
}];
buildReceiptPath = FileNameJoin[{
  outputDirectory,
  "SYNC_MAP_02E_R1_LOCAL_BUILD_RECEIPT.json"
}];
replayReceiptPath = FileNameJoin[{
  outputDirectory,
  "SYNC_MAP_02E_R1_LOCAL_WOLFRAM_REPLAY_RECEIPT.json"
}];

generatorPath = FileNameJoin[{
  repositoryRoot,
  "scripts",
  "build_sync_map02e_r1_hardening.py"
}];
verifierPath = FileNameJoin[{
  repositoryRoot,
  "scripts",
  "verify_sync_map02e_r1_hardening.py"
}];
modulePath = FileNameJoin[{
  repositoryRoot,
  "wolfram",
  "BASS",
  "Kernel",
  "IR",
  "SharedFramePhotonExportHardeningR1.wl"
}];
fixPath = FileNameJoin[{
  repositoryRoot,
  "wolfram",
  "BASS",
  "Kernel",
  "IR",
  "SharedFramePhotonExportHardeningR1Fix1.wl"
}];
testPath = FileNameJoin[{
  repositoryRoot,
  "wolfram",
  "BASS",
  "Tests",
  "SYNCMAP02ER1SharedFramePhotonHardening.wlt"
}];
patchContractPath = FileNameJoin[{
  repositoryRoot,
  "docs",
  "bass_master_ssot_v2",
  "SYNC_MAP_02E_R1",
  "SEMANTIC_HARDENING_PATCH_CONTRACT.json"
}];

requiredPaths = {
  parentPath,
  generatorPath,
  verifierPath,
  modulePath,
  fixPath,
  testPath,
  patchContractPath
};
missingPaths = Select[requiredPaths, !FileExistsQ[#] &];
If[missingPaths =!= {},
  Print[InputForm[<|
    "status" -> "FAIL_MISSING_LOCAL_REPLAY_INPUT",
    "missing_paths" -> missingPaths
  |>]];
  Exit[2]
];

(* The canonical shell entry point resolves python3 before launching Wolfram and
   passes the absolute executable path as the second user argument.  Wolfram
   Language 15.0.1 has no System`FindExecutable symbol, so executable discovery
   must not be attempted through an unevaluated Global`FindExecutable call. *)
python = If[
  Length[arguments] >= 2,
  ExpandFileName[arguments[[2]]],
  Missing["PythonArgument"]
];
If[!StringQ[python] || !FileExistsQ[python],
  Print[InputForm[<|
    "status" -> "FAIL_PYTHON3_ARGUMENT_MISSING",
    "received_argument" -> python
  |>]];
  Exit[3]
];

pythonProbe = Quiet @ Check[RunProcess[{python, "--version"}], $Failed];
If[
  !AssociationQ[pythonProbe] || processExitCode[pythonProbe] =!= 0,
  Print[InputForm[<|
    "status" -> "FAIL_PYTHON3_UNUSABLE",
    "python_path" -> python,
    "exit_code" -> If[
      AssociationQ[pythonProbe],
      processExitCode[pythonProbe],
      Missing["RunProcessFailed"]
    ],
    "stdout" -> If[
      AssociationQ[pythonProbe],
      processStandardOutput[pythonProbe],
      ""
    ],
    "stderr" -> If[
      AssociationQ[pythonProbe],
      Lookup[pythonProbe, "StandardError", ""],
      ""
    ]
  |>]];
  Exit[3]
];

buildProcess = RunProcess[{
  python,
  generatorPath,
  "--input", parentPath,
  "--output", outputPath,
  "--receipt", buildReceiptPath
}];
If[processExitCode[buildProcess] =!= 0,
  Print[InputForm[<|
    "status" -> "FAIL_GENERATOR",
    "exit_code" -> processExitCode[buildProcess],
    "stdout" -> processStandardOutput[buildProcess],
    "stderr" -> Lookup[buildProcess, "StandardError", ""]
  |>]];
  Exit[4]
];

verifyProcess = RunProcess[{
  python,
  verifierPath,
  "--input", outputPath,
  "--receipt", buildReceiptPath
}];
If[processExitCode[verifyProcess] =!= 0,
  Print[InputForm[<|
    "status" -> "FAIL_PYTHON_VERIFIER",
    "exit_code" -> processExitCode[verifyProcess],
    "stdout" -> processStandardOutput[verifyProcess],
    "stderr" -> Lookup[verifyProcess, "StandardError", ""]
  |>]];
  Exit[5]
];

(* Load the exact, hash-recorded BASS modules and patch contract once in the
   canonical runner.  The WLT receives this absolute context dynamically and
   performs no $InputFileName-based path inference of its own. *)
Get[modulePath];
Get[fixPath];
hardenedExport = Import[outputPath, "RawJSON"];
patchContract = Import[patchContractPath, "RawJSON"];
residuals = BASS`IR`SharedFramePhotonHardeningR1ExactResiduals[];
exportValid = TrueQ[
  BASS`IR`SharedFramePhotonHardeningR1ExportQ[hardenedExport]
];
patchValid = TrueQ[
  BASS`IR`SharedFramePhotonHardeningR1PatchContractQ[patchContract]
];

testContextPayload = <|
  "repository_scope" -> "BASS_ONLY",
  "repository_root" -> repositoryRoot,
  "module_path" -> modulePath,
  "fix_path" -> fixPath,
  "patch_contract_path" -> patchContractPath,
  "patch_contract" -> patchContract
|>;
injectedTestContext = testContextPayload;
report = Block[
  {Global`$BASSSyncMap02ER1TestContext = injectedTestContext},
  TestReport[testPath]
];
succeeded = Quiet @ Check[report["TestsSucceededCount"], Missing["Unavailable"]];
failed = Quiet @ Check[report["TestsFailedCount"], Missing["Unavailable"]];
notEvaluated = Quiet @ Check[
  report["TestsNotEvaluatedCount"],
  Missing["Unavailable"]
];
expectedTestCount = 11;

gitHead = Quiet @ Check[
  StringTrim @ RunProcess[
    {"git", "-C", repositoryRoot, "rev-parse", "HEAD"},
    "StandardOutput"
  ],
  Missing["GitUnavailable"]
];

receipt = <|
  "schema_version" -> "1.0.0",
  "stage_id" -> "SYNC_MAP_02E_R1_LOCAL_WOLFRAM_REPLAY",
  "repository_scope" -> "BASS_ONLY",
  "git_head" -> gitHead,
  "wolfram_version" -> $Version,
  "python_executable" -> python,
  "python_probe_exit_code" -> processExitCode[pythonProbe],
  "python_version_stdout" -> StringTrim[processStandardOutput[pythonProbe]],
  "python_version_stderr" -> StringTrim[Lookup[pythonProbe, "StandardError", ""]],
  "parent_sha256" -> fileSHA256[parentPath],
  "generated_export_sha256" -> fileSHA256[outputPath],
  "build_receipt_sha256" -> fileSHA256[buildReceiptPath],
  "module_sha256" -> fileSHA256[modulePath],
  "fix_sha256" -> fileSHA256[fixPath],
  "wlt_sha256" -> fileSHA256[testPath],
  "patch_contract_sha256" -> fileSHA256[patchContractPath],
  "python_generator_exit_code" -> processExitCode[buildProcess],
  "python_verifier_exit_code" -> processExitCode[verifyProcess],
  "python_verifier_stdout" -> StringTrim[processStandardOutput[verifyProcess]],
  "export_valid" -> exportValid,
  "patch_contract_valid" -> patchValid,
  "exact_residuals" -> residuals,
  "test_context_mode" -> "RUNNER_INJECTED_ABSOLUTE_CONTEXT",
  "expected_top_level_munit_tests" -> expectedTestCount,
  "tests_succeeded" -> succeeded,
  "tests_failed" -> failed,
  "tests_not_evaluated" -> notEvaluated
|>;

allPassed = And[
  processExitCode[pythonProbe] === 0,
  processExitCode[buildProcess] === 0,
  processExitCode[verifyProcess] === 0,
  exportValid,
  patchValid,
  succeeded === expectedTestCount,
  failed === 0,
  notEvaluated === 0,
  Lookup[residuals, "regular_coefficient", None] === 0,
  Lookup[residuals, "zero_boost_coefficient", None] === 1/2,
  Lookup[residuals, "aberrated_direction_unit_norm", None] === 0,
  Lookup[residuals, "blackbody_weighted_pullback_generator", None] === 0,
  Lookup[residuals, "doppler_only_omission_witness", None] === -3/4,
  Lookup[residuals, "planck_covariance", None] === 0,
  Lookup[residuals, "general_energy_drift_specialization", None] === 0,
  Lookup[residuals, "omitted_normal_acceleration_coefficient", None] === -1,
  Lookup[residuals, "direction_flow_tangency", None] === 0
];

receipt = Append[
  receipt,
  "status" -> If[
    allPassed,
    "PASS_LOCAL_EXACT_REPLAY",
    "FAIL_LOCAL_EXACT_REPLAY"
  ]
];
Export[replayReceiptPath, receipt, "RawJSON"];
Print[InputForm[receipt]];
Exit[If[allPassed, 0, 1]];
