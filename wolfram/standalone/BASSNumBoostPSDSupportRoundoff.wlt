(* Top-level tests. Do not wrap VerificationTest expressions in Module. *)

Get[FileNameJoin[{
  DirectoryName[$InputFileName],
  "BASSNumBoostPSDSupportRoundoff.wl"
}]];

VerificationTest[
  RunPSDSupportRoundoffSelfChecks[]["Total"],
  16,
  TestID -> "NUMBOOST-R3-EXACT-TEST-COUNT"
]

VerificationTest[
  RunPSDSupportRoundoffSelfChecks[]["Passed"],
  16,
  TestID -> "NUMBOOST-R3-EXACT-PASS-COUNT"
]

VerificationTest[
  TrueQ[RunPSDSupportRoundoffSelfChecks[]["AllPassed"]],
  True,
  TestID -> "NUMBOOST-R3-ALL-CHECKS"
]

VerificationTest[
  SPDWeylGuard[1/10, 1/20]["CertifiedSPD"],
  True,
  TestID -> "NUMBOOST-R3-WEYL-SPD-PASS"
]

VerificationTest[
  SPDWeylGuard[1/10, 1/10]["CertifiedSPD"],
  False,
  TestID -> "NUMBOOST-R3-WEYL-SPD-STRICT-FAIL"
]

VerificationTest[
  SPDFloorPolicyData[-1/5, 1/10, False]["Status"],
  "REJECT_UNAUTHORIZED_MODEL_CHANGE",
  TestID -> "NUMBOOST-R3-NEGATIVE-EIGENVALUE-FLOOR-REJECT"
]

VerificationTest[
  Quiet[
    CommonSupportCompressionGuard[
      DiagonalMatrix[{2, 3, 5}],
      DiagonalMatrix[{5/2, 7/2, 4}],
      {0, 0, 0},
      {0, 0, 0},
      {1, -1, 2},
      {{1, 0}, {0, 1}, {0, 0}}
    ],
    CommonSupportCompressionGuard::cov
  ],
  $Failed,
  TestID -> "NUMBOOST-R3-OUTSIDE-SUPPORT-COVARIANCE-REJECT"
]

VerificationTest[
  ProjectorDriftBounds[
    DiagonalMatrix[{1, 0, 0}],
    Outer[Times, {4/5, 3/5, 0}, {4/5, 3/5, 0}],
    {{3, 1, 0}, {1, 2, 1/2}, {0, 1/2, 1}},
    {2, -1, 3}
  ]["AllBoundsPass"],
  True,
  TestID -> "NUMBOOST-R3-PROJECTOR-DRIFT-BOUND"
]
