#!/usr/bin/env wolframscript

packageDirectory = DirectoryName[$InputFileName];
Get[FileNameJoin[{
  packageDirectory,
  "BASSNumBoostLikelihoodHardening.wl"
}]];

result =
  BASSNumBoostLikelihoodHardening`RunLikelihoodHardeningSelfChecks[];

Print[InputForm[result]];

Exit[
  If[
    TrueQ[result["AllPassed"]] &&
    result["Passed"] === 15 &&
    result["Total"] === 15,
    0,
    1
  ]
];
