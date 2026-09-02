(* ::Package:: *)

BeginPackage["BASS`Geometry`"];

RunSpatialXCobaCurvatureWitness::usage =
 "RunSpatialXCobaCurvatureWitness[label] runs the independent xCoba coordinate-chart curvature witness for I, V, or IX.";
RunSpatialXCobaCurvatureWitnesses::usage =
 "RunSpatialXCobaCurvatureWitnesses[] runs and caches the independent I, V, and IX xCoba witnesses.";
SpatialXCobaCurvatureReceiptPayload::usage =
 "SpatialXCobaCurvatureReceiptPayload[] returns a JSON-safe SYNC-MAP-01C xCoba witness payload.";

Begin["`Private`"];

ClearAll[
 ensureSpatialXCoba, transformXCobaCovariantRiemann,
 makeSpatialXCobaWitnessResult, runSpatialXCobaI,
 runSpatialXCobaV, runSpatialXCobaIX,
 RunSpatialXCobaCurvatureWitness, RunSpatialXCobaCurvatureWitnesses,
 SpatialXCobaCurvatureReceiptPayload, $spatialXCobaWitnessCache
];

$spatialXCobaWitnessCache = Missing["NotRun"];

ensureSpatialXCoba[] := Module[{loaded},
 If[!MemberQ[$Packages, "xAct`xTensor`"],
  Return[<|"status" -> "BLOCKED", "reason" -> "XTENSOR_NOT_LOADED"|>]
 ];
 loaded = If[
   MemberQ[$Packages, "xAct`xCoba`"],
   True,
   Quiet@Check[Needs["xAct`xCoba`"] ; True, False]
  ];
 If[!TrueQ[loaded],
  Return[<|"status" -> "BLOCKED", "reason" -> "XCOBA_LOAD_FAILED"|>]
 ];
 If[MemberQ[$Packages, "xAct`xPerm`"], xAct`xPerm`$xpermQ = False];
 <|
  "status" -> "PASS",
  "xTensor_version" -> ToString[InputForm[xAct`xTensor`$Version]],
  "xCoba_version" -> ToString[InputForm[xAct`xCoba`$Version]],
  "xPerm_mathlink" -> False,
  "canonical_backend" -> "pure-wolfram",
  "symbol_namespace" -> "Global`BASSSYNCMap01C*",
  "claim_boundary" ->
   "XCOBA_ENVIRONMENT_ONLY_NO_CURVATURE_AUTHORITY"
 |>
];

transformXCobaCovariantRiemann[raw_List, frame_List, assumptions_] :=
 Array[
  Function[{alpha, beta, gamma, delta},
   FullSimplify[
    -Sum[
      frame[[alpha, i]] frame[[beta, j]]
       frame[[gamma, k]] frame[[delta, l]] raw[[i, j, k, l]],
      {i, 3}, {j, 3}, {k, 3}, {l, 3}
     ],
    assumptions
   ]
  ],
  {3, 3, 3, 3}
 ];

makeSpatialXCobaWitnessResult[
 label_String,
 metric_List,
 frame_List,
 raw_List,
 direct_List,
 assumptions_
] := Module[{frameMetric, transformed, checks},
 frameMetric = FullSimplify[frame . metric . Transpose[frame], assumptions];
 transformed = transformXCobaCovariantRiemann[raw, frame, assumptions];
 checks = <|
   "component_shape_3333" -> SameQ[Dimensions[raw], {3, 3, 3, 3}],
   "orthonormal_frame" ->
    TrueQ[FullSimplify[frameMetric == IdentityMatrix[3], assumptions]],
   "xact_to_bass_sign_adapter" -> -1,
   "dual_full_riemann_match" ->
    TrueQ[FullSimplify[transformed == direct, assumptions]]
  |>;
 <|
  "schema_version" -> "1.0.0",
  "label" -> label,
  "status" -> If[
    TrueQ[checks["component_shape_3333"]] &&
     TrueQ[checks["orthonormal_frame"]] &&
     TrueQ[checks["dual_full_riemann_match"]],
    "PASS", "FAIL"
   ],
  "checks" -> checks,
  "component_shape" -> Dimensions[raw],
  "frame_metric" -> frameMetric,
  "claim_boundary" ->
   "INDEPENDENT_COORDINATE_XCOBA_ORACLE_ONLY_AUTHORITY_EFFECT_NONE"
 |>
];

runSpatialXCobaI[] := Module[
 {environment, metric, frame, raw, direct},
 environment = ensureSpatialXCoba[];
 If[Lookup[environment, "status", "BLOCKED"] =!= "PASS", Return[environment]];
 If[!TrueQ[xAct`xTensor`ManifoldQ[Global`BASSSYNCMap01CIM3]],
  xAct`xTensor`DefManifold[
   Global`BASSSYNCMap01CIM3, 3,
   {Global`BASSSYNCMap01CIa, Global`BASSSYNCMap01CIb,
    Global`BASSSYNCMap01CIc, Global`BASSSYNCMap01CId}
  ]
 ];
 If[!TrueQ[xAct`xTensor`MetricQ[Global`BASSSYNCMap01CIg]],
  xAct`xTensor`DefMetric[
   1,
   Global`BASSSYNCMap01CIg[
    -Global`BASSSYNCMap01CIa, -Global`BASSSYNCMap01CIb],
   Global`BASSSYNCMap01CICD,
   {";", "D"}
  ]
 ];
 If[!TrueQ[xAct`xCoba`ChartQ[Global`BASSSYNCMap01CIch]],
  xAct`xCoba`DefChart[
   Global`BASSSYNCMap01CIch, Global`BASSSYNCMap01CIM3, {1, 2, 3},
   {Global`BASSSYNCMap01CIx[], Global`BASSSYNCMap01CIy[],
    Global`BASSSYNCMap01CIz[]}
  ]
 ];
 metric = IdentityMatrix[3];
 frame = IdentityMatrix[3];
 xAct`xCoba`MetricInBasis[
  Global`BASSSYNCMap01CIg, -Global`BASSSYNCMap01CIch, metric];
 xAct`xCoba`MetricCompute[
  Global`BASSSYNCMap01CIg, Global`BASSSYNCMap01CIch, All,
  xAct`xCoba`CVSimplify -> FullSimplify,
  xAct`xCore`Verbose -> False
 ];
 raw = xAct`xCoba`ToValues[
   xAct`xCoba`ComponentArray[
    Global`RiemannBASSSYNCMap01CICD[
     {-Global`BASSSYNCMap01CIa, -Global`BASSSYNCMap01CIch},
     {-Global`BASSSYNCMap01CIb, -Global`BASSSYNCMap01CIch},
     {-Global`BASSSYNCMap01CIc, -Global`BASSSYNCMap01CIch},
     {-Global`BASSSYNCMap01CId, -Global`BASSSYNCMap01CIch}
    ]
   ]
  ];
 direct = SpatialRiemannTensor[
   {0, 0, 0}, ConstantArray[0, {3, 3}]
  ];
 Join[
  makeSpatialXCobaWitnessResult[
   "I", metric, frame, raw, direct, True],
  <|"environment" -> environment, "chart_domain" -> "R^3"|>
 ]
];

runSpatialXCobaV[] := Module[
 {environment, metric, frame, raw, direct},
 environment = ensureSpatialXCoba[];
 If[Lookup[environment, "status", "BLOCKED"] =!= "PASS", Return[environment]];
 If[!TrueQ[xAct`xTensor`ManifoldQ[Global`BASSSYNCMap01CVM3]],
  xAct`xTensor`DefManifold[
   Global`BASSSYNCMap01CVM3, 3,
   {Global`BASSSYNCMap01CVa, Global`BASSSYNCMap01CVb,
    Global`BASSSYNCMap01CVc, Global`BASSSYNCMap01CVd}
  ]
 ];
 If[!TrueQ[xAct`xTensor`MetricQ[Global`BASSSYNCMap01CVg]],
  xAct`xTensor`DefMetric[
   1,
   Global`BASSSYNCMap01CVg[
    -Global`BASSSYNCMap01CVa, -Global`BASSSYNCMap01CVb],
   Global`BASSSYNCMap01CVCD,
   {";", "D"}
  ]
 ];
 If[!TrueQ[xAct`xCoba`ChartQ[Global`BASSSYNCMap01CVch]],
  xAct`xCoba`DefChart[
   Global`BASSSYNCMap01CVch, Global`BASSSYNCMap01CVM3, {1, 2, 3},
   {Global`BASSSYNCMap01CVx[], Global`BASSSYNCMap01CVy[],
    Global`BASSSYNCMap01CVz[]}
  ]
 ];
 metric = {
   {1, 0, 0},
   {0, Exp[-2 Global`BASSSYNCMap01CVx[]], 0},
   {0, 0, Exp[-2 Global`BASSSYNCMap01CVx[]]}
  };
 frame = DiagonalMatrix[
   {1, Exp[Global`BASSSYNCMap01CVx[]],
    Exp[Global`BASSSYNCMap01CVx[]]}
  ];
 xAct`xCoba`MetricInBasis[
  Global`BASSSYNCMap01CVg, -Global`BASSSYNCMap01CVch, metric];
 xAct`xCoba`MetricCompute[
  Global`BASSSYNCMap01CVg, Global`BASSSYNCMap01CVch, All,
  xAct`xCoba`CVSimplify -> FullSimplify,
  xAct`xCore`Verbose -> False
 ];
 raw = xAct`xCoba`ToValues[
   xAct`xCoba`ComponentArray[
    Global`RiemannBASSSYNCMap01CVCD[
     {-Global`BASSSYNCMap01CVa, -Global`BASSSYNCMap01CVch},
     {-Global`BASSSYNCMap01CVb, -Global`BASSSYNCMap01CVch},
     {-Global`BASSSYNCMap01CVc, -Global`BASSSYNCMap01CVch},
     {-Global`BASSSYNCMap01CVd, -Global`BASSSYNCMap01CVch}
    ]
   ]
  ];
 direct = SpatialRiemannTensor[
   {1, 0, 0}, ConstantArray[0, {3, 3}]
  ];
 Join[
  makeSpatialXCobaWitnessResult[
   "V", metric, frame, raw, direct, True],
  <|
   "environment" -> environment,
   "chart_domain" -> "x,y,z in R",
   "coordinate_metric" -> "dx^2 + exp(-2x)(dy^2+dz^2)"
  |>
 ]
];

runSpatialXCobaIX[] := Module[
 {environment, metric, frame, raw, direct, assumptions},
 environment = ensureSpatialXCoba[];
 If[Lookup[environment, "status", "BLOCKED"] =!= "PASS", Return[environment]];
 If[!TrueQ[xAct`xTensor`ManifoldQ[Global`BASSSYNCMap01CIXM3]],
  xAct`xTensor`DefManifold[
   Global`BASSSYNCMap01CIXM3, 3,
   {Global`BASSSYNCMap01CIXa, Global`BASSSYNCMap01CIXb,
    Global`BASSSYNCMap01CIXc, Global`BASSSYNCMap01CIXd}
  ]
 ];
 If[!TrueQ[xAct`xTensor`MetricQ[Global`BASSSYNCMap01CIXg]],
  xAct`xTensor`DefMetric[
   1,
   Global`BASSSYNCMap01CIXg[
    -Global`BASSSYNCMap01CIXa, -Global`BASSSYNCMap01CIXb],
   Global`BASSSYNCMap01CIXCD,
   {";", "D"}
  ]
 ];
 If[!TrueQ[xAct`xCoba`ChartQ[Global`BASSSYNCMap01CIXch]],
  xAct`xCoba`DefChart[
   Global`BASSSYNCMap01CIXch, Global`BASSSYNCMap01CIXM3, {1, 2, 3},
   {Global`BASSSYNCMap01CIXtheta[],
    Global`BASSSYNCMap01CIXphi[],
    Global`BASSSYNCMap01CIXpsi[]}
  ]
 ];
 metric = {
   {1, 0, 0},
   {0, 1, Cos[Global`BASSSYNCMap01CIXtheta[]]},
   {0, Cos[Global`BASSSYNCMap01CIXtheta[]], 1}
  };
 frame = {
   {1, 0, 0},
   {0, Csc[Global`BASSSYNCMap01CIXtheta[]],
    -Cot[Global`BASSSYNCMap01CIXtheta[]]},
   {0, 0, 1}
  };
 assumptions = 0 < Global`BASSSYNCMap01CIXtheta[] < Pi;
 xAct`xCoba`MetricInBasis[
  Global`BASSSYNCMap01CIXg, -Global`BASSSYNCMap01CIXch, metric];
 xAct`xCoba`MetricCompute[
  Global`BASSSYNCMap01CIXg, Global`BASSSYNCMap01CIXch, All,
  xAct`xCoba`CVSimplify -> FullSimplify,
  xAct`xCore`Verbose -> False
 ];
 raw = xAct`xCoba`ToValues[
   xAct`xCoba`ComponentArray[
    Global`RiemannBASSSYNCMap01CIXCD[
     {-Global`BASSSYNCMap01CIXa, -Global`BASSSYNCMap01CIXch},
     {-Global`BASSSYNCMap01CIXb, -Global`BASSSYNCMap01CIXch},
     {-Global`BASSSYNCMap01CIXc, -Global`BASSSYNCMap01CIXch},
     {-Global`BASSSYNCMap01CIXd, -Global`BASSSYNCMap01CIXch}
    ]
   ]
  ];
 direct = SpatialRiemannTensor[
   {0, 0, 0}, IdentityMatrix[3]
  ];
 Join[
  makeSpatialXCobaWitnessResult[
   "IX", metric, frame, raw, direct, assumptions],
  <|
   "environment" -> environment,
   "chart_domain" -> "0 < theta < pi",
   "coordinate_metric" ->
    "dtheta^2+dphi^2+dpsi^2+2 cos(theta) dphi dpsi"
  |>
 ]
];

RunSpatialXCobaCurvatureWitnesses[] :=
 If[AssociationQ[$spatialXCobaWitnessCache],
  $spatialXCobaWitnessCache,
  $spatialXCobaWitnessCache = <|
    "I" -> runSpatialXCobaI[],
    "V" -> runSpatialXCobaV[],
    "IX" -> runSpatialXCobaIX[]
   |>
 ];

RunSpatialXCobaCurvatureWitness[label_String] :=
 Lookup[
  RunSpatialXCobaCurvatureWitnesses[], label,
  Failure["UnknownSpatialXCobaWitness", <|"label" -> label|>]
 ];

SpatialXCobaCurvatureReceiptPayload[] := Module[
 {witnesses, summary},
 witnesses = RunSpatialXCobaCurvatureWitnesses[];
 summary = <|
   "labels" -> Keys[witnesses],
   "all_pass" ->
    AllTrue[Values[witnesses], Lookup[#, "status", "FAIL"] === "PASS" &],
   "all_full_riemann_match" ->
    AllTrue[
     Values[witnesses],
     TrueQ[
       Lookup[Lookup[#, "checks", <||>],
        "dual_full_riemann_match", False]
      ] &
    ],
   "all_orthonormal_frames" ->
    AllTrue[
     Values[witnesses],
     TrueQ[
       Lookup[Lookup[#, "checks", <||>],
        "orthonormal_frame", False]
      ] &
    ],
   "component_shapes" ->
    Map[Lookup[#, "component_shape", {}] &, witnesses]
  |>;
 <|
  "schema_version" -> "1.0.0",
  "stage_id" -> "SYNC-MAP-01C",
  "authority_effect" -> "NONE",
  "replay_of" -> {
   "GEO03-RIEMANN-001", "GEO03-RICCI-001", "GEO03-SCALAR-001"
  },
  "summary" -> summary,
  "witnesses" -> Map[
    KeyTake[#, {
      "schema_version", "label", "status", "checks",
      "component_shape", "chart_domain", "coordinate_metric",
      "claim_boundary"
     }] &,
    witnesses
   ],
  "claim_boundary" -> {
   "SYNC_MAP_01C_I_V_IX_XCOBA_FULL_RIEMANN_ORACLE_PASS",
   "AUTHORITY_EFFECT_NONE",
   "NO_ALL_TYPE_CURVATURE_SPECIALIZATION",
   "NO_BACKGROUND_EINSTEIN_MATTER_EVOLUTION",
   "NO_NUMERICAL_PARITY",
   "NO_SCIENCE_VALIDITY",
   "NO_PASS_RF04"
  }
 |>
];

End[];
EndPackage[];
