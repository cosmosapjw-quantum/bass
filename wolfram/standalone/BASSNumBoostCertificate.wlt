(* Top-level MUnit tests: do not wrap VerificationTest expressions in Module. *)

Get[FileNameJoin[{DirectoryName[$InputFileName], "BASSNumBoostCertificate.wl"}]];

VerificationTest[
  RunExactSelfChecks[]["Total"],
  17,
  TestID -> "NUMBOOST01-EXACT-TEST-COUNT"
]

VerificationTest[
  RunExactSelfChecks[]["Passed"],
  17,
  TestID -> "NUMBOOST01-EXACT-PASS-COUNT"
]

VerificationTest[
  TrueQ[RunExactSelfChecks[]["AllPassed"]],
  True,
  TestID -> "NUMBOOST01-ALL-EXACT-CHECKS"
]

VerificationTest[
  FiniteBufferTheoremData[0, 0, 2, 4]["FirstFullStateLeakageOrder"],
  3,
  TestID -> "NUMBOOST01-BUFFER-LEAKAGE-ORDER"
]

VerificationTest[
  FiniteBufferTheoremData[0, 0, 2, 4]["FirstRetainedContaminationOrder"],
  6,
  TestID -> "NUMBOOST01-BUFFER-RETAINED-ORDER"
]

VerificationTest[
  FullSimplify[
    FiniteBufferTheoremData[0, 0, 2, 4]["ShortestPathCoefficientSquared"]
  ],
  32000/539,
  TestID -> "NUMBOOST01-SCALAR-SHORTEST-PATH-COEFFICIENT"
]

VerificationTest[
  D1FixedMGenerator[2, 1, 7],
  D1FixedMGenerator[-2, 1, 7],
  TestID -> "NUMBOOST01-SPIN-PLUS-MINUS-TWO-EQUALITY"
]

VerificationTest[
  RootReduce[
    D1FixedMGenerator[2, 1, 7] +
    Transpose[D1FixedMGenerator[2, 1, 7]]
  ],
  ConstantArray[0, Dimensions[D1FixedMGenerator[2, 1, 7]]],
  TestID -> "NUMBOOST01-D1-FINITE-BLOCK-SKEW"
]

VerificationTest[
  BipoSHUnitarityChecks[1, 1],
  <|"LeftUnitary" -> True, "RightUnitary" -> True|>,
  TestID -> "NUMBOOST01-BIPOSH-BLOCK-UNITARITY"
]

VerificationTest[
  BipolarPowerErrorBound[kappaApprox, epsilon],
  2 epsilon Sqrt[kappaApprox] + epsilon^2,
  TestID -> "NUMBOOST01-BIPOLAR-POWER-BOUND"
]

VerificationTest[
  GaussianRelativeLikelihoodBounds[1/4, 3, 61/30, 9/80][
    "KLFrobeniusBound"
  ],
  3/80,
  TestID -> "NUMBOOST01-GAUSSIAN-KL-FROBENIUS-BOUND"
]

VerificationTest[
  GaussianLikelihoodBoundsFromFrobenius[1/5, 2, 3, 1][
    "SPDGuaranteed"
  ],
  True,
  TestID -> "NUMBOOST01-GAUSSIAN-SPD-GUARD"
]

VerificationTest[
  GaussianLikelihoodBoundsFromFrobenius[3, 2, 3, 1][
    "SPDGuaranteed"
  ],
  False,
  TestID -> "NUMBOOST01-GAUSSIAN-SPD-FAIL-CLOSED"
]
