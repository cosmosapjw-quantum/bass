(* ::Package:: *)

BeginPackage["BASS`IR`"];

ClearAll[SharedFramePhotonHardeningR1ExactResiduals];
SharedFramePhotonHardeningR1ExactResiduals[] := Module[
  {
    b2, mu, gam, chi, dop, coeff, unitResidual,
    beta, x, sourceX, targetD, temp, fullGenerator, dopplerOnly,
    hp, nu, kb, temperature, d, planck,
    hgeom, see, accelerationDotDirection,
    s11, s12, s13, s22, s23,
    n11, n12, n13, n22, n23, n33,
    a1, a2, a3, om1, om2, om3,
    e1, e2, e3, sMat, nMat, aVec, omVec, eVec, directionFlow
  },

  gam = 1/Sqrt[1 - b2];
  chi = gam^2/(gam + 1);
  dop = gam (1 + mu);
  coeff = gam + chi mu;
  unitResidual = FullSimplify[
    (1 + 2 coeff mu + coeff^2 b2)/dop^2 - 1,
    Assumptions -> 0 <= b2 < 1 && -Sqrt[b2] <= mu <= Sqrt[b2]
  ];

  sourceX = (x - beta)/(1 - beta x);
  targetD = 1/((1/Sqrt[1 - beta^2]) (1 - beta x));
  fullGenerator = FullSimplify[
    D[targetD temp[sourceX], beta] /. beta -> 0
  ];
  dopplerOnly = FullSimplify[(D[targetD, beta] /. beta -> 0) temp[x]];

  planck[frequency_, absoluteTemperature_] :=
    2 hp frequency^3/(Exp[hp frequency/(kb absoluteTemperature)] - 1);

  sMat = {
    {s11, s12, s13},
    {s12, s22, s23},
    {s13, s23, -s11 - s22}
  };
  nMat = {
    {n11, n12, n13},
    {n12, n22, n23},
    {n13, n23, n33}
  };
  aVec = {a1, a2, a3};
  omVec = {om1, om2, om3};
  eVec = {e1, e2, e3};
  see = Expand[eVec . sMat . eVec];
  directionFlow = Expand[
    (see + aVec . eVec) eVec - sMat . eVec - aVec +
    Cross[omVec, eVec] - Cross[eVec, nMat . eVec]
  ];

  <|
    "regular_coefficient" -> FullSimplify[
      (gam - 1)/b2 - chi,
      Assumptions -> 0 < b2 < 1
    ],
    "zero_boost_coefficient" -> FullSimplify[Limit[chi, b2 -> 0]],
    "aberrated_direction_unit_norm" -> unitResidual,
    "blackbody_weighted_pullback_generator" -> FullSimplify[
      fullGenerator - (x temp[x] - (1 - x^2) Derivative[1][temp][x])
    ],
    "doppler_only_omission_witness" -> FullSimplify[
      ((fullGenerator - dopplerOnly) /. temp -> Function[{z}, z^2]) /. x -> 1/2
    ],
    "planck_covariance" -> FullSimplify[
      d^3 planck[nu/d, temperature] - planck[nu, d temperature],
      Assumptions ->
        hp > 0 && nu > 0 && kb > 0 && temperature > 0 && d > 0
    ],
    "general_energy_drift_specialization" -> FullSimplify[
      (-hgeom - accelerationDotDirection - see) - (-hgeom - see) +
      accelerationDotDirection
    ],
    "omitted_normal_acceleration_coefficient" -> Coefficient[
      -hgeom - accelerationDotDirection - see,
      accelerationDotDirection
    ],
    "direction_flow_tangency" -> FullSimplify[
      eVec . directionFlow,
      Assumptions -> e1^2 + e2^2 + e3^2 == 1
    ]
  |>
];

ClearAll[SharedFramePhotonHardeningR1PatchContractQ];
SharedFramePhotonHardeningR1PatchContractQ[data_Association] := Module[
  {hardening, blackbody, photon, local, formulaIDs},
  hardening = Lookup[data, "required_hardening", <||>];
  blackbody = Lookup[hardening, "blackbody_weighted_pullback", <||>];
  photon = Lookup[hardening, "photon_characteristics", <||>];
  local = Lookup[data, "local_replay_contract", <||>];
  formulaIDs = Lookup[data, "formula_ids", {}];
  And[
    Lookup[data, "repository_scope", None] === "BASS_ONLY",
    Lookup[data, "owner", None] === "bass",
    formulaIDs === SharedFramePhotonHardeningR1FormulaIDs[],
    Lookup[Lookup[hardening, "aberration", <||>], "regular_coefficient", None] ===
      "gamma^2/(gamma+1)",
    Lookup[blackbody, "mathematical_kind", None] ===
      "WEIGHTED_SECTION_PUSHFORWARD",
    Lookup[Lookup[blackbody, "base_map_dependency", <||>], "role", None] ===
      "BASE_MAP_REQUIRED",
    Lookup[Lookup[blackbody, "fiber_weight_dependency", <||>], "role", None] ===
      "FIBER_WEIGHT_REQUIRED",
    Lookup[blackbody, "spin_weight", None] === 0,
    Lookup[blackbody, "doppler_weight", None] === 1,
    Lookup[photon, "ray_parameter", None] === "s=c*t",
    Lookup[photon, "screen_basis_transport_status", None] ===
      "EXCLUDED_NEXT_BASS_NODE",
    Lookup[local, "expected_top_level_munit_tests", None] === 11
  ]
];
SharedFramePhotonHardeningR1PatchContractQ[_] := False;

EndPackage[];
