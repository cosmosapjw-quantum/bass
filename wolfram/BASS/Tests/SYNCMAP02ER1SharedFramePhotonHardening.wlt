(* Top-level MUnit tests. Do not wrap VerificationTest expressions in Module. *)

(*
  The observed local Wolfram 15.0.0 TestReport retains the outer runner's
  input-file binding instead of exposing this WLT path.  The canonical replay
  script therefore preloads the exact modules and injects an absolute,
  hash-bound test context dynamically.  This WLT performs no repository-path
  inference and no file loading.
*)
injectedTestContext = If[
  AssociationQ[Global`$BASSSyncMap02ER1TestContext],
  Global`$BASSSyncMap02ER1TestContext,
  <||>
];
injectedPatchContract = Lookup[
  injectedTestContext,
  "patch_contract",
  <||>
];
injectedRepositoryScope = Lookup[
  injectedTestContext,
  "repository_scope",
  None
];
injectedModulePath = Lookup[
  injectedTestContext,
  "module_path",
  None
];
injectedFixPath = Lookup[
  injectedTestContext,
  "fix_path",
  None
];
injectedPatchContractPath = Lookup[
  injectedTestContext,
  "patch_contract_path",
  None
];

VerificationTest[
  BASS`IR`SharedFramePhotonHardeningR1FormulaIDs[],
  {
    "BASS.FRAME.ABERRATED_DIRECTION.001",
    "BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001",
    "BASS.FRAME.DOPPLER_FACTOR.001",
    "BASS.FRAME.SOLID_ANGLE_JACOBIAN.001",
    "BASS.PHOTON.DIRECTION_FLOW.001",
    "BASS.PHOTON.ENERGY_DRIFT.001"
  },
  TestID -> "SYNCMAP02E-R1-FORMULA-IDS"
]

VerificationTest[
  BASS`IR`SharedFramePhotonHardeningR1ExactResiduals[]["regular_coefficient"],
  0,
  TestID -> "SYNCMAP02E-R1-REGULAR-COEFFICIENT"
]

VerificationTest[
  BASS`IR`SharedFramePhotonHardeningR1ExactResiduals[]["zero_boost_coefficient"],
  1/2,
  TestID -> "SYNCMAP02E-R1-ZERO-BOOST-DIRECT"
]

VerificationTest[
  BASS`IR`SharedFramePhotonHardeningR1ExactResiduals[]["aberrated_direction_unit_norm"],
  0,
  TestID -> "SYNCMAP02E-R1-ABERRATION-UNIT-NORM"
]

VerificationTest[
  BASS`IR`SharedFramePhotonHardeningR1ExactResiduals[]["blackbody_weighted_pullback_generator"],
  0,
  TestID -> "SYNCMAP02E-R1-BLACKBODY-WEIGHTED-PULLBACK"
]

VerificationTest[
  BASS`IR`SharedFramePhotonHardeningR1ExactResiduals[]["doppler_only_omission_witness"],
  -3/4,
  TestID -> "SYNCMAP02E-R1-ABERRATION-DEPENDENCY-WITNESS"
]

VerificationTest[
  BASS`IR`SharedFramePhotonHardeningR1ExactResiduals[]["planck_covariance"],
  0,
  TestID -> "SYNCMAP02E-R1-PLANCK-COVARIANCE"
]

VerificationTest[
  BASS`IR`SharedFramePhotonHardeningR1ExactResiduals[]["general_energy_drift_specialization"],
  0,
  TestID -> "SYNCMAP02E-R1-GEODESIC-NORMAL-SPECIALIZATION"
]

VerificationTest[
  BASS`IR`SharedFramePhotonHardeningR1ExactResiduals[]["omitted_normal_acceleration_coefficient"],
  -1,
  TestID -> "SYNCMAP02E-R1-NORMAL-ACCELERATION-COEFFICIENT"
]

VerificationTest[
  BASS`IR`SharedFramePhotonHardeningR1ExactResiduals[]["direction_flow_tangency"],
  0,
  TestID -> "SYNCMAP02E-R1-DIRECTION-FLOW-TANGENCY"
]

VerificationTest[
  And[
    injectedRepositoryScope === "BASS_ONLY",
    StringQ[injectedModulePath],
    FileExistsQ[injectedModulePath],
    StringQ[injectedFixPath],
    FileExistsQ[injectedFixPath],
    StringQ[injectedPatchContractPath],
    FileExistsQ[injectedPatchContractPath],
    BASS`IR`SharedFramePhotonHardeningR1PatchContractQ[
      injectedPatchContract
    ]
  ],
  True,
  TestID -> "SYNCMAP02E-R1-INJECTED-PATCH-CONTRACT"
]
