(* Top-level tests. Do not wrap in one Module. *)

Get[FileNameJoin[{
  DirectoryName[$InputFileName],
  "BASSNumBoostLikelihoodHardening.wl"
}]];

VerificationTest[
  RunLikelihoodHardeningSelfChecks[]["Total"],
  15,
  TestID -> "NUMBOOST-R2-EXACT-TEST-COUNT"
]

VerificationTest[
  RunLikelihoodHardeningSelfChecks[]["Passed"],
  15,
  TestID -> "NUMBOOST-R2-EXACT-PASS-COUNT"
]

VerificationTest[
  TrueQ[RunLikelihoodHardeningSelfChecks[]["AllPassed"]],
  True,
  TestID -> "NUMBOOST-R2-ALL-CHECKS"
]

VerificationTest[
  Quiet[
    HardenedCovarianceSourceTailData[
      {{1, 2}, {3, 4}},
      DiagonalMatrix[{1, 0}]
    ],
    HardenedCovarianceSourceTailData::cov
  ],
  $Failed,
  TestID -> "NUMBOOST-R2-NONHERMITIAN-TAIL-FAIL-CLOSED"
]

VerificationTest[
  CommonSupportGuard[
    DiagonalMatrix[{1, 1, 0}],
    DiagonalMatrix[{1, 0, 1}],
    {0, 0, 0}
  ],
  False,
  TestID -> "NUMBOOST-R2-SUPPORT-MISMATCH-FAIL-CLOSED"
]
