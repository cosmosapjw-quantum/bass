(* Top-level MUnit tests. Do not wrap VerificationTest expressions in Module. *)

Get[FileNameJoin[{
  DirectoryName[DirectoryName[$InputFileName]],
  "Kernel",
  "IR",
  "SharedFramePhotonExportHardeningR1.wl"
}]];

VerificationTest[
  SharedFramePhotonHardeningR1FormulaIDs[],
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
  SharedFramePhotonHardeningR1ExactResiduals[]["regular_coefficient"],
  0,
  TestID -> "SYNCMAP02E-R1-REGULAR-COEFFICIENT"
]

VerificationTest[
  SharedFramePhotonHardeningR1ExactResiduals[]["zero_boost_coefficient"],
  1/2,
  TestID -> "SYNCMAP02E-R1-ZERO-BOOST-DIRECT"
]

VerificationTest[
  SharedFramePhotonHardeningR1ExactResiduals[]["aberrated_direction_unit_norm"],
  0,
  TestID -> "SYNCMAP02E-R1-ABERRATION-UNIT-NORM"
]

VerificationTest[
  SharedFramePhotonHardeningR1ExactResiduals[]["blackbody_weighted_pullback_generator"],
  0,
  TestID -> "SYNCMAP02E-R1-BLACKBODY-WEIGHTED-PULLBACK"
]

VerificationTest[
  SharedFramePhotonHardeningR1ExactResiduals[]["doppler_only_omission_witness"],
  -3/4,
  TestID -> "SYNCMAP02E-R1-ABERRATION-DEPENDENCY-WITNESS"
]

VerificationTest[
  SharedFramePhotonHardeningR1ExactResiduals[]["planck_covariance"],
  0,
  TestID -> "SYNCMAP02E-R1-PLANCK-COVARIANCE"
]

VerificationTest[
  SharedFramePhotonHardeningR1ExactResiduals[]["general_energy_drift_specialization"],
  0,
  TestID -> "SYNCMAP02E-R1-GEODESIC-NORMAL-SPECIALIZATION"
]

VerificationTest[
  SharedFramePhotonHardeningR1ExactResiduals[]["omitted_normal_acceleration_coefficient"],
  -1,
  TestID -> "SYNCMAP02E-R1-NORMAL-ACCELERATION-COEFFICIENT"
]

VerificationTest[
  SharedFramePhotonHardeningR1ExactResiduals[]["direction_flow_tangency"],
  0,
  TestID -> "SYNCMAP02E-R1-DIRECTION-FLOW-TANGENCY"
]

VerificationTest[
  SharedFramePhotonHardeningR1PatchContractQ[
    Import[
      FileNameJoin[{
        DirectoryName[
          DirectoryName[
            DirectoryName[
              DirectoryName[$InputFileName]
            ]
          ]
        ],
        "docs",
        "bass_master_ssot_v2",
        "SYNC_MAP_02E_R1",
        "SEMANTIC_HARDENING_PATCH_CONTRACT.json"
      }],
      "RawJSON"
    ]
  ],
  True,
  TestID -> "SYNCMAP02E-R1-PATCH-CONTRACT"
]
