(* ::Package:: *)

ClearAll[BG02CRAGPlots];

BG02CRAGPlots[] := Module[{ratePlot, indexPlot},
 ratePlot = Plot[
   {-x/2, -x/6, -2 x/3},
   {x, -1/5, 1/5},
   PlotLegends -> {
     "(F_ADM-F_trace)/H^2",
     "(F_trace-F_Ray)/H^2",
     "(F_ADM-F_Ray)/H^2"
   },
   AxesLabel -> {"Hres/H^2", "rate difference/H^2"},
   PlotLabel -> "Exact off-shell rate separation",
   ImageSize -> 500
 ];

 indexPlot = BarChart[
   {{0, -6, -1/2, 3/2}, {0, 4, 3/2, 3/2}},
   ChartLegends -> {"locked order", "wrong direct storage"},
   ChartLabels -> {None, {"I", "V", "II", "IX"}},
   AxesLabel -> {None, "normalized R3 witness"},
   PlotLabel -> "Connection-order adversarial witnesses",
   ImageSize -> 500
 ];

 GraphicsRow[{ratePlot, indexPlot}, ImageSize -> 1000]
];

BG02CRAGPlots[]
