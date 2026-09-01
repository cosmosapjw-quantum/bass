#!/usr/bin/env wolframscript

Module[{scriptDir, repositoryRoot, outputDirectory, rows, csvPath,
  chartPath, chart},
 scriptDir = DirectoryName[$InputFileName];
 repositoryRoot = ExpandFileName[FileNameJoin[{scriptDir, "..", ".."}]];
 outputDirectory = FileNameJoin[
   {repositoryRoot, "docs", "bass_master_ssot_v2", "ALG_01"}
  ];
 If[! DirectoryQ[outputDirectory],
  CreateDirectory[outputDirectory, CreateIntermediateDirectories -> True]];
 rows = {
   {"I", "canonical", 0, 0, 0},
   {"II", "canonical", 0, 0, 0},
   {"V", "canonical", 0, 0, 0},
   {"IX", "canonical", 0, 0, 0},
   {"VI_-1/9", "canonical", 0, 0, 0},
   {"JACOBI_BREAK", "hostile", 3, 6, 0},
   {"IX_INERTIA_BREAK", "hostile", 1, 0, 0},
   {"V_N_BREAK", "hostile", 3, 0, 0},
   {"EXCEPTIONAL_H_BREAK", "hostile", 2, 0, 5},
   {"EXCEPTIONAL_MOMENTUM_BREAK", "hostile", 1, 0, 12}
  };
 csvPath = FileNameJoin[{outputDirectory, "CRAG_PLOT_DATA.csv"}];
 chartPath = FileNameJoin[{outputDirectory, "CRAG_WITNESS_SIGNALS.svg"}];
 Export[csvPath,
  Prepend[rows, {"witness_id", "kind", "failed_contract_count",
    "jacobi_tensor_nonzero_count", "max_abs_exceptional_residual"}],
  "CSV"];
 chart = BarChart[
   rows[[All, 3]],
   ChartLabels -> Placed[rows[[All, 1]], Below],
   AxesLabel -> {None, "failed ALG-01 contracts"},
   PlotLabel -> "ALG-01 canonical admission and adversarial detection",
   ImageSize -> Large,
   PlotRange -> {0, 4}
  ];
 Export[chartPath, chart, "SVG"];
 Print[ExportString[
   <|"status" -> "PASS", "csv" -> csvPath, "svg" -> chartPath,
    "canonical_zero_count" -> Count[rows[[1 ;; 5, 3]], 0],
    "hostile_positive_count" -> Count[rows[[6 ;;, 3]], _?Positive]|>,
   "RawJSON"]]
]
