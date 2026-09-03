#!/usr/bin/env wolframscript

packageDirectory = DirectoryName[$InputFileName];
Get[FileNameJoin[{
  packageDirectory,
  "BASSNumBoostPSDSupportRoundoff.wl"
}]];

result =
  BASSNumBoostPSDSupportRoundoff`RunPSDSupportRoundoffSelfChecks[];

Print[InputForm[result]];

Exit[
  If[
    TrueQ[result["AllPassed"]] &&
    result["Passed"] === 16 &&
    result["Total"] === 16,
    0,
    1
  ]
];
