#!/usr/bin/env wolframscript

Module[{scriptDir, repositoryRoot, dataPath, outputPath, rows,
  shearRows, covarianceRows, figure},
 scriptDir = DirectoryName[$InputFileName];
 repositoryRoot = ExpandFileName[FileNameJoin[{scriptDir, "..", ".."}]];
 dataPath = FileNameJoin[{repositoryRoot, "docs", "bass_master_ssot_v2",
    "ALG_01", "ALG_01R1_CRAG_PLOT_DATA.csv"}];
 outputPath = FileNameJoin[{repositoryRoot, "docs", "bass_master_ssot_v2",
    "ALG_01", "ALG_01R1_CRAG_PLOT.png"}];
 If[! FileExistsQ[dataPath],
  Print["BLOCKED: missing plot data: " <> dataPath]; Exit[2]];
 rows = Rest @ Import[dataPath, "CSV"];
 shearRows = Select[rows, First[#] === "exceptional_shear_obligation" &];
 covarianceRows = Select[rows, First[#] === "O3_covariance_residual_L1" &];
 figure = GraphicsRow[{
    BarChart[
     ToExpression /@ shearRows[[All, 3]],
     ChartLabels -> shearRows[[All, 2]],
     PlotLabel -> "Exceptional VI(-1/9) shear witness",
     AxesLabel -> {None, "obligation pass"},
     PlotRange -> {0, 1.1}
    ],
    BarChart[
     ToExpression /@ covarianceRows[[All, 3]],
     ChartLabels -> covarianceRows[[All, 2]],
     PlotLabel -> "O(3) covariance residual L1",
     AxesLabel -> {None, "residual"}
    ]
   }, ImageSize -> 1000];
 Export[outputPath, figure, "PNG"];
 Print[ExportString[<|"status" -> "PASS", "data" -> dataPath,
    "output" -> outputPath|>, "RawJSON"]]
]
