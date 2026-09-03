#!/usr/bin/env wolframscript

packageDirectory = DirectoryName[$InputFileName];
Get[FileNameJoin[{packageDirectory, "BASSNumBoostCertificate.wl"}]];

result = BASSNumBoostCertificate`RunExactSelfChecks[];
Print[InputForm[result]];

Exit[
  If[
    TrueQ[result["AllPassed"]] &&
    result["Passed"] === 17 &&
    result["Total"] === 17,
    0,
    1
  ]
];
