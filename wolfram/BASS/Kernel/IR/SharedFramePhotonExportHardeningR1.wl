(* ::Package:: *)

BeginPackage["BASS`IR`"];

SharedFramePhotonHardeningR1FormulaIDs::usage =
  "SharedFramePhotonHardeningR1FormulaIDs[] returns the six BASS-owned formula IDs.";
SharedFramePhotonHardeningR1ExactResiduals::usage =
  "SharedFramePhotonHardeningR1ExactResiduals[] returns exact hardening residuals and hostile witnesses.";
SharedFramePhotonHardeningR1PatchContractQ::usage =
  "SharedFramePhotonHardeningR1PatchContractQ[data] validates the machine patch contract.";
SharedFramePhotonHardeningR1ExportQ::usage =
  "SharedFramePhotonHardeningR1ExportQ[data] fail-closed validates a generated hardened export.";

Begin["`Private`"];

ClearAll[
  SharedFramePhotonHardeningR1FormulaIDs,
  SharedFramePhotonHardeningR1ExactResiduals,
  SharedFramePhotonHardeningR1PatchContractQ,
  SharedFramePhotonHardeningR1ExportQ,
  formulaMap,
  dependencyRoleMap,
  allLowercaseHex64Q,
  exactZeroScalarQ,
  exactZeroVectorQ
];

SharedFramePhotonHardeningR1FormulaIDs[] := {
  "BASS.FRAME.ABERRATED_DIRECTION.001",
  "BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001",
  "BASS.FRAME.DOPPLER_FACTOR.001",
  "BASS.FRAME.SOLID_ANGLE_JACOBIAN.001",
  "BASS.PHOTON.DIRECTION_FLOW.001",
  "BASS.PHOTON.ENERGY_DRIFT.001"
};

exactZeroScalarQ[value_] := TrueQ[PossibleZeroQ[RootReduce[value]]];
exactZeroVectorQ[value_List] := And @@ Map[exactZeroScalarQ, value];

formulaMap[data_Association] := Association @ Map[
  Lookup[#, "formula_id", Missing["FormulaID"]] -> # &,
  Lookup[data, "formulas", {}]
];

dependencyRoleMap[record_Association] := Association @ Map[
  Lookup[#, "formula_id", Missing["FormulaID"]] ->
    Lookup[#, "role", Missing["Role"]] &,
  Lookup[record, "dependency_roles", {}]
];

allLowercaseHex64Q[value_] :=
  StringQ[value] && StringMatchQ[value, RegularExpression["[0-9a-f]{64}"]];

SharedFramePhotonHardeningR1ExactResiduals[] := Module[
  {
    b2, mu, gam, chi, dop, coeff, unitResidual,
    beta, x, sourceX, targetD, fullGenerator, dopplerOnly,
    hp, nu, kb, temp, d, planck,
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

  planck[frequency_, temperature_] :=
    2 hp frequency^3/(1 - Exp[-hp frequency/(kb temperature)]);

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
      (fullGenerator - dopplerOnly) /. {
        temp[x] -> x^2,
        Derivative[1][temp][x] -> 2 x,
        x -> 1/2
      }
    ],
    "planck_covariance" -> FullSimplify[
      d^3 planck[nu/d, temp] - planck[nu, d temp],
      Assumptions -> hp > 0 && nu > 0 && kb > 0 && temp > 0 && d > 0
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
    Lookup[local, "expected_top_level_munit_tests", None] === 10
  ]
];
SharedFramePhotonHardeningR1PatchContractQ[_] := False;

SharedFramePhotonHardeningR1ExportQ[data_Association] := Module[
  {
    ids, rows, byID, aberration, blackbody, direction, energy,
    blackbodyRoles, hashes, claims, targets, internalEdges, expectedEdges
  },
  rows = Lookup[data, "formulas", {}];
  ids = Lookup[rows, "formula_id", {}];
  byID = formulaMap[data];
  aberration = Lookup[byID, "BASS.FRAME.ABERRATED_DIRECTION.001", <||>];
  blackbody = Lookup[byID, "BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001", <||>];
  direction = Lookup[byID, "BASS.PHOTON.DIRECTION_FLOW.001", <||>];
  energy = Lookup[byID, "BASS.PHOTON.ENERGY_DRIFT.001", <||>];
  blackbodyRoles = dependencyRoleMap[blackbody];
  hashes = Lookup[rows, "semantic_hash", {}];
  claims = Lookup[data, "claim_boundary", {}];
  targets = Lookup[data, "declared_consumer_targets", <||>];
  internalEdges = Sort @ Map[
    {Lookup[#, "from", None], Lookup[#, "to", None]} &,
    Lookup[data, "internal_dependency_edges", {}]
  ];
  expectedEdges = Sort @ {
    {"BASS.FRAME.ABERRATED_DIRECTION.001", "BASS.FRAME.DOPPLER_FACTOR.001"},
    {"BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001", "BASS.FRAME.ABERRATED_DIRECTION.001"},
    {"BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001", "BASS.FRAME.DOPPLER_FACTOR.001"},
    {"BASS.FRAME.SOLID_ANGLE_JACOBIAN.001", "BASS.FRAME.ABERRATED_DIRECTION.001"},
    {"BASS.FRAME.SOLID_ANGLE_JACOBIAN.001", "BASS.FRAME.DOPPLER_FACTOR.001"}
  };
  And[
    Lookup[data, "schema_version", None] === "1.1.0",
    Lookup[data, "stage_id", None] ===
      "SYNC_MAP_02E_R1_SEMANTIC_HARDENING",
    Lookup[data, "repository_scope", None] === "BASS_ONLY",
    Lookup[data, "owner", None] === "bass",
    Lookup[data, "formula_count", None] === 6,
    ids === SharedFramePhotonHardeningR1FormulaIDs[],
    DuplicateFreeQ[ids],
    AllTrue[hashes, allLowercaseHex64Q],
    allLowercaseHex64Q[Lookup[data, "registry_semantic_hash", None]],
    !KeyExistsQ[data, "consumer_bindings"],
    Sort[Keys[targets]] === Sort[SharedFramePhotonHardeningR1FormulaIDs[]],
    StringContainsQ[
      ToString[Lookup[Lookup[aberration, "equation_ir", <||>], "terms", {}]],
      "gamma^2/(gamma+1)"
    ],
    StringFreeQ[
      ToString[Lookup[Lookup[aberration, "equation_ir", <||>], "terms", {}]],
      "(gamma-1)/beta_squared"
    ],
    Lookup[blackbody, "dependencies", {}] === {
      "BASS.FRAME.ABERRATED_DIRECTION.001",
      "BASS.FRAME.DOPPLER_FACTOR.001"
    },
    blackbodyRoles === <|
      "BASS.FRAME.ABERRATED_DIRECTION.001" -> "BASE_MAP_REQUIRED",
      "BASS.FRAME.DOPPLER_FACTOR.001" -> "FIBER_WEIGHT_REQUIRED"
    |>,
    Lookup[
      Lookup[Lookup[blackbody, "equation_ir", <||>], "operator_ir", <||>],
      "base_map",
      <||>
    ]["target_evaluation_uses"] === "INVERSE_MAP",
    StringContainsQ[
      Lookup[Lookup[direction, "equation_ir", <||>], "target", ""],
      "/ds"
    ],
    StringContainsQ[
      Lookup[Lookup[energy, "equation_ir", <||>], "target", ""],
      "/ds"
    ],
    Lookup[
      Lookup[direction, "equation_ir", <||>],
      "screen_basis_transport_status",
      None
    ] === "EXCLUDED_NEXT_BASS_NODE",
    internalEdges === expectedEdges,
    claims === {
      "BASS_OWNER_FORMULA_HARDENING_ONLY",
      "NO_CROSS_REPOSITORY_SOURCE_MUTATION",
      "NO_CONSUMER_PARITY",
      "NO_BACKGROUND_PROVIDER",
      "NO_GLOBAL_TILT",
      "NO_SCREEN_TRANSPORT",
      "NO_NUMERICAL_OR_SCIENCE_PROMOTION"
    }
  ]
];
SharedFramePhotonHardeningR1ExportQ[_] := False;

End[];
EndPackage[];
