#!/usr/bin/env wolframscript

packageDirectory = DirectoryName[$InputFileName];

Get[FileNameJoin[{
  packageDirectory,
  "BASSNumBoostLikelihoodHardening.wl"
}]];

Get[FileNameJoin[{
  packageDirectory,
  "BASSNumBoostLikelihoodRealGaussianGuard.wl"
}]];

result =
  BASSNumBoostLikelihoodHardening`RunLikelihoodHardeningSelfChecks[];

complexGuard = Quiet[
  BASSNumBoostLikelihoodHardening`GaussianMeanCovarianceKLData[
    IdentityMatrix[2],
    IdentityMatrix[2],
    {I, 0},
    {0, 0}
  ],
  BASSNumBoostLikelihoodHardening`GaussianMeanCovarianceKLData::real
] === $Failed;

Print[InputForm[<|
  "SelfChecks" -> result,
  "ComplexMeanGuard" -> complexGuard
|>]];

Exit[
  If[
    TrueQ[result["AllPassed"]] &&
    result["Passed"] === 15 &&
    result["Total"] === 15 &&
    TrueQ[complexGuard],
    0,
    1
  ]
];
