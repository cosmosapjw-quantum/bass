(* ::Package:: *)

BeginPackage["BASS`Geometry`"];

RunXCobaCurvatureWitness::usage =
 "RunXCobaCurvatureWitness[label] runs the independent xCoba coordinate-chart curvature witness for I, V or IX.";
RunXCobaCurvatureWitnesses::usage =
 "RunXCobaCurvatureWitnesses[] runs and caches all independent xCoba coordinate-chart curvature witnesses.";
XCobaCurvatureWitnessReceiptPayload::usage =
 "XCobaCurvatureWitnessReceiptPayload[] returns a JSON-safe W3 component-witness payload.";

Begin["`Private`"];

ClearAll[
 ensureW3XCoba, transformCovariantRiemann, makeWitnessResult,
 runXCobaI, runXCobaV, runXCobaIX,
 RunXCobaCurvatureWitness, RunXCobaCurvatureWitnesses,
 XCobaCurvatureWitnessReceiptPayload, $w3XCobaWitnessCache
];

$w3XCobaWitnessCache = Missing["NotRun"];

ensureW3XCoba[] := Module[{loaded, backend},
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
 backend = SelectW2CanonicalBackend[];
 <|
  "status" -> If[Lookup[backend, "status", "FAIL"] === "PASS", "PASS", "BLOCKED"],
  "xTensor_version" -> ToString[InputForm[xAct`xTensor`$Version]],
  "xCoba_version" -> ToString[InputForm[xAct`xCoba`$Version]],
  "xPerm_mathlink" -> False,
  "symbol_namespace" -> "Global`BASSW3*",
  "canonical_backend" -> backend
 |>
];

transformCovariantRiemann[raw_List, frame_List, assumptions_] :=
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

makeWitnessResult[
 label_String,
 metric_List,
 frame_List,
 raw_List,
 direct_List,
 assumptions_
] := Module[{frameMetric, transformed, checks},
 frameMetric = FullSimplify[frame . metric . Transpose[frame], assumptions];
 transformed = transformCovariantRiemann[raw, frame, assumptions];
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
   "COORDINATE_XCOBA_TO_ONF_CURVATURE_WITNESS_ONLY_NO_BACKGROUND_EVOLUTION"
 |>
];

runXCobaI[] := Module[
 {environment, metric, frame, raw, direct},
 environment = ensureW3XCoba[];
 If[Lookup[environment, "status", "BLOCKED"] =!= "PASS", Return[environment]];
 If[!TrueQ[xAct`xTensor`ManifoldQ[Global`BASSW3IM3]],
  xAct`xTensor`DefManifold[
   Global`BASSW3IM3, 3,
   {Global`BASSW3Ia, Global`BASSW3Ib, Global`BASSW3Ic, Global`BASSW3Id}
  ]
 ];
 If[!TrueQ[xAct`xTensor`MetricQ[Global`BASSW3Ig]],
  xAct`xTensor`DefMetric[
   1,
   Global`BASSW3Ig[-Global`BASSW3Ia, -Global`BASSW3Ib],
   Global`BASSW3ICD,
   {";", "D"}
  ]
 ];
 If[!TrueQ[xAct`xCoba`ChartQ[Global`BASSW3Ich]],
  xAct`xCoba`DefChart[
   Global`BASSW3Ich, Global`BASSW3IM3, {1, 2, 3},
   {Global`BASSW3Ix[], Global`BASSW3Iy[], Global`BASSW3Iz[]}
  ]
 ];
 metric = IdentityMatrix[3];
 frame = IdentityMatrix[3];
 xAct`xCoba`MetricInBasis[Global`BASSW3Ig, -Global`BASSW3Ich, metric];
 xAct`xCoba`MetricCompute[
  Global`BASSW3Ig, Global`BASSW3Ich, All,
  xAct`xCoba`CVSimplify -> FullSimplify,
  xAct`xCore`Verbose -> False
 ];
 raw = xAct`xCoba`ToValues[
   xAct`xCoba`ComponentArray[
    Global`RiemannBASSW3ICD[
     {-Global`BASSW3Ia, -Global`BASSW3Ich},
     {-Global`BASSW3Ib, -Global`BASSW3Ich},
     {-Global`BASSW3Ic, -Global`BASSW3Ich},
     {-Global`BASSW3Id, -Global`BASSW3Ich}
    ]
   ]
  ];
 direct = ONFRiemannTensor[{0, 0, 0}, ConstantArray[0, {3, 3}]];
 Join[
  makeWitnessResult["I", metric, frame, raw, direct, True],
  <|"environment" -> environment, "chart_domain" -> "R^3"|>
 ]
];

runXCobaV[] := Module[
 {environment, metric, frame, raw, direct},
 environment = ensureW3XCoba[];
 If[Lookup[environment, "status", "BLOCKED"] =!= "PASS", Return[environment]];
 If[!TrueQ[xAct`xTensor`ManifoldQ[Global`BASSW3VM3]],
  xAct`xTensor`DefManifold[
   Global`BASSW3VM3, 3,
   {Global`BASSW3Va, Global`BASSW3Vb, Global`BASSW3Vc, Global`BASSW3Vd}
  ]
 ];
 If[!TrueQ[xAct`xTensor`MetricQ[Global`BASSW3Vg]],
  xAct`xTensor`DefMetric[
   1,
   Global`BASSW3Vg[-Global`BASSW3Va, -Global`BASSW3Vb],
   Global`BASSW3VCD,
   {";", "D"}
  ]
 ];
 If[!TrueQ[xAct`xCoba`ChartQ[Global`BASSW3Vch]],
  xAct`xCoba`DefChart[
   Global`BASSW3Vch, Global`BASSW3VM3, {1, 2, 3},
   {Global`BASSW3Vx[], Global`BASSW3Vy[], Global`BASSW3Vz[]}
  ]
 ];
 metric = {
   {1, 0, 0},
   {0, Exp[-2 Global`BASSW3Vx[]], 0},
   {0, 0, Exp[-2 Global`BASSW3Vx[]]}
  };
 frame = DiagonalMatrix[
   {1, Exp[Global`BASSW3Vx[]], Exp[Global`BASSW3Vx[]]}
  ];
 xAct`xCoba`MetricInBasis[Global`BASSW3Vg, -Global`BASSW3Vch, metric];
 xAct`xCoba`MetricCompute[
  Global`BASSW3Vg, Global`BASSW3Vch, All,
  xAct`xCoba`CVSimplify -> FullSimplify,
  xAct`xCore`Verbose -> False
 ];
 raw = xAct`xCoba`ToValues[
   xAct`xCoba`ComponentArray[
    Global`RiemannBASSW3VCD[
     {-Global`BASSW3Va, -Global`BASSW3Vch},
     {-Global`BASSW3Vb, -Global`BASSW3Vch},
     {-Global`BASSW3Vc, -Global`BASSW3Vch},
     {-Global`BASSW3Vd, -Global`BASSW3Vch}
    ]
   ]
  ];
 direct = ONFRiemannTensor[{1, 0, 0}, ConstantArray[0, {3, 3}]];
 Join[
  makeWitnessResult["V", metric, frame, raw, direct, True],
  <|
   "environment" -> environment,
   "chart_domain" -> "x,y,z in R",
   "coordinate_metric" -> "dx^2 + exp(-2x)(dy^2+dz^2)"
  |>
 ]
];

runXCobaIX[] := Module[
 {environment, metric, frame, raw, direct, assumptions},
 environment = ensureW3XCoba[];
 If[Lookup[environment, "status", "BLOCKED"] =!= "PASS", Return[environment]];
 If[!TrueQ[xAct`xTensor`ManifoldQ[Global`BASSW3IXM3]],
  xAct`xTensor`DefManifold[
   Global`BASSW3IXM3, 3,
   {Global`BASSW3IXa, Global`BASSW3IXb,
    Global`BASSW3IXc, Global`BASSW3IXd}
  ]
 ];
 If[!TrueQ[xAct`xTensor`MetricQ[Global`BASSW3IXg]],
  xAct`xTensor`DefMetric[
   1,
   Global`BASSW3IXg[-Global`BASSW3IXa, -Global`BASSW3IXb],
   Global`BASSW3IXCD,
   {";", "D"}
  ]
 ];
 If[!TrueQ[xAct`xCoba`ChartQ[Global`BASSW3IXch]],
  xAct`xCoba`DefChart[
   Global`BASSW3IXch, Global`BASSW3IXM3, {1, 2, 3},
   {Global`BASSW3IXtheta[],
    Global`BASSW3IXphi[],
    Global`BASSW3IXpsi[]}
  ]
 ];
 metric = {
   {1, 0, 0},
   {0, 1, Cos[Global`BASSW3IXtheta[]]},
   {0, Cos[Global`BASSW3IXtheta[]], 1}
  };
 frame = {
   {1, 0, 0},
   {0, Csc[Global`BASSW3IXtheta[]], -Cot[Global`BASSW3IXtheta[]]},
   {0, 0, 1}
  };
 assumptions = 0 < Global`BASSW3IXtheta[] < Pi;
 xAct`xCoba`MetricInBasis[Global`BASSW3IXg, -Global`BASSW3IXch, metric];
 xAct`xCoba`MetricCompute[
  Global`BASSW3IXg, Global`BASSW3IXch, All,
  xAct`xCoba`CVSimplify -> FullSimplify,
  xAct`xCore`Verbose -> False
 ];
 raw = xAct`xCoba`ToValues[
   xAct`xCoba`ComponentArray[
    Global`RiemannBASSW3IXCD[
     {-Global`BASSW3IXa, -Global`BASSW3IXch},
     {-Global`BASSW3IXb, -Global`BASSW3IXch},
     {-Global`BASSW3IXc, -Global`BASSW3IXch},
     {-Global`BASSW3IXd, -Global`BASSW3IXch}
    ]
   ]
  ];
 direct = ONFRiemannTensor[{0, 0, 0}, IdentityMatrix[3]];
 Join[
  makeWitnessResult["IX", metric, frame, raw, direct, assumptions],
  <|
   "environment" -> environment,
   "chart_domain" -> "0 < theta < pi",
   "coordinate_metric" ->
    "dtheta^2+dphi^2+dpsi^2+2 cos(theta) dphi dpsi"
  |>
 ]
];

RunXCobaCurvatureWitnesses[] :=
 If[AssociationQ[$w3XCobaWitnessCache],
  $w3XCobaWitnessCache,
  $w3XCobaWitnessCache = <|
    "I" -> runXCobaI[],
    "V" -> runXCobaV[],
    "IX" -> runXCobaIX[]
   |>
 ];

RunXCobaCurvatureWitness[label_String] :=
 Lookup[
  RunXCobaCurvatureWitnesses[],
  label,
  Failure["UnknownWitness", <|"label" -> label|>]
 ];

XCobaCurvatureWitnessReceiptPayload[] := Module[
 {witnesses, summary},
 witnesses = RunXCobaCurvatureWitnesses[];
 summary = <|
   "labels" -> Keys[witnesses],
   "all_pass" ->
    AllTrue[Values[witnesses], Lookup[#, "status", "FAIL"] === "PASS" &],
   "all_full_riemann_match" ->
    AllTrue[
     Values[witnesses],
     TrueQ[Lookup[Lookup[#, "checks", <||>], "dual_full_riemann_match", False]] &
    ],
   "all_orthonormal_frames" ->
    AllTrue[
     Values[witnesses],
     TrueQ[Lookup[Lookup[#, "checks", <||>], "orthonormal_frame", False]] &
    ],
   "component_shapes" -> Map[
     Lookup[#, "component_shape", {}] &,
     witnesses
    ]
  |>;
 <|
  "schema_version" -> "1.0.0",
  "stage_id" -> "W3",
  "summary" -> summary,
  "witnesses" -> Map[
    KeyTake[#, {"schema_version", "label", "status", "checks",
      "component_shape", "chart_domain", "coordinate_metric",
      "claim_boundary"}] &,
    witnesses
   ],
  "claim_boundary" -> {
   "W3_I_V_IX_XCOBA_FULL_RIEMANN_WITNESSES_VERIFIED",
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
