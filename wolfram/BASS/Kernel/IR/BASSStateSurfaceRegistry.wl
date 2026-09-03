(* ::Package:: *)

BeginPackage["BASS`IR`"];

BASSStateSurfaceRegistryExactResiduals::usage =
  "BASSStateSurfaceRegistryExactResiduals[] returns exact representation and closure witnesses.";
BASSStateSurfaceRegistryQ::usage =
  "BASSStateSurfaceRegistryQ[data] validates the BASS-only state-surface registry.";

Begin["`Private`"];

ClearAll[exactZeroQ];
exactZeroQ[value_] := TrueQ[PossibleZeroQ[RootReduce[value]]];

ClearAll[BASSStateSurfaceRegistryExactResiduals];
BASSStateSurfaceRegistryExactResiduals[] := Module[
  {
    x, a0, a1, a2, distribution, coefficients, reconstruction,
    f1, f2, chi1, chi2, chiEff, sourceDefect,
    q1, q2, jWeight1, jWeight2
  },

  distribution =
    a0 LegendreP[0, x] + a1 LegendreP[1, x] + a2 LegendreP[2, x];
  coefficients = Table[
    FullSimplify[
      (2 ell + 1)/2 Integrate[
        distribution LegendreP[ell, x],
        {x, -1, 1}
      ]
    ],
    {ell, 0, 2}
  ];
  reconstruction = Sum[
    coefficients[[ell + 1]] LegendreP[ell, x],
    {ell, 0, 2}
  ];

  sourceDefect = Expand[
    chi1 f1 + chi2 f2 - chiEff (f1 + f2)
  ];

  <|
    "band_limited_grid_pstf_reconstruction" ->
      FullSimplify[reconstruction - distribution],
    "same_integrated_G_state" -> ((1 + 0) - (0 + 1)),
    "different_frequency_loss" ->
      Expand[(chi1 1 + chi2 0) - (chi1 0 + chi2 1)],
    "universal_scalar_closure_coefficients" -> {
      Coefficient[sourceDefect, f1],
      Coefficient[sourceDefect, f2]
    },
    "J_projection_noninvertibility_witness" ->
      Expand[(jWeight1 q1 + jWeight2 q2) - (jWeight1 q2 + jWeight2 q1)],
    "scalar_to_polarized_implicit_promotion_defined" -> False
  |>
];

ClearAll[BASSStateSurfaceRegistryQ];
BASSStateSurfaceRegistryQ[data_Association] := Module[
  {
    expectedStates, expectedRelations, states, relations, stateMap,
    relationMap, ancestry, relationContract, ellPolicy, jRelation,
    gRelation, polarizedRelation, noGo, claims
  },

  expectedStates = {
    "GRID_F_Q_E",
    "PSTF_F_AELL_Q",
    "J_I_AELL",
    "G_ANGULAR_ENERGY",
    "FLUID_COMPONENT_SUMMARY",
    "POLARIZED_COHERENCY"
  };
  expectedRelations = {
    "GRID_TO_PSTF",
    "PSTF_TO_GRID",
    "PSTF_TO_J",
    "GRID_TO_G",
    "KINETIC_TO_FLUID_SUMMARY",
    "SCALAR_TO_POLARIZED_PROHIBITED"
  };

  states = Lookup[data, "states", {}];
  relations = Lookup[data, "relations", {}];
  stateMap = Association @ Map[Lookup[#, "state_id", None] -> # &, states];
  relationMap = Association @ Map[Lookup[#, "relation_id", None] -> # &, relations];
  ancestry = Lookup[data, "normal_ancestry", <||>];
  relationContract = Lookup[data, "relation_graph_contract", <||>];
  ellPolicy = Lookup[data, "ell_policy", <||>];
  jRelation = Lookup[relationMap, "PSTF_TO_J", <||>];
  gRelation = Lookup[relationMap, "GRID_TO_G", <||>];
  polarizedRelation = Lookup[
    relationMap,
    "SCALAR_TO_POLARIZED_PROHIBITED",
    <||>
  ];
  noGo = Lookup[data, "closure_no_go", <||>];
  claims = Lookup[data, "claim_boundary", {}];

  And[
    Lookup[data, "schema_version", None] === "1.0.0",
    Lookup[data, "stage_id", None] ===
      "SYNC_MAP_02F_R2_BASS_STATE_SURFACE_REGISTRY",
    Lookup[data, "repository_scope", None] === "BASS_ONLY",
    Lookup[data, "owner", None] === "bass",
    Sort[Keys[stateMap]] === Sort[expectedStates],
    Sort[Keys[relationMap]] === Sort[expectedRelations],
    Length[stateMap] === Length[states],
    Length[relationMap] === Length[relations],
    Lookup[ancestry, "parent_commit", None] ===
      "8b73919e0e2a2326c338c796ac80b0684fe49db1",
    Lookup[ancestry, "hardened_formula_registry_semantic_hash", None] ===
      "5951f566d911c81848743055c1573f6d11b0b00937d36747b71e6bc12dd96416",
    Lookup[relationContract, "required_formula_consumer_pairs", None] === 10,
    Lookup[relationContract, "required_implementation_role_rows", None] === 11,
    Lookup[relationContract, "required_named_source_symbols", None] === 12,
    Lookup[relationContract, "required_absent_implementation_slots", None] === 1,
    TrueQ[Lookup[ellPolicy, "hardcoded_numeric_cutoff_forbidden", False]],
    Lookup[Lookup[stateMap, "GRID_F_Q_E", <||>], "spectral_variable_retained", None] === True,
    Lookup[Lookup[stateMap, "PSTF_F_AELL_Q", <||>], "spectral_variable_retained", None] === True,
    Lookup[Lookup[stateMap, "J_I_AELL", <||>], "spectral_variable_retained", None] === False,
    Lookup[Lookup[stateMap, "G_ANGULAR_ENERGY", <||>], "spectral_variable_retained", None] === False,
    Lookup[jRelation, "invertibility", None] === "NONINVERTIBLE_IN_GENERAL",
    MemberQ[
      Lookup[jRelation, "required_certificates", {}],
      "SOURCE_GRID_QUADRATURE_OR_SPECTRAL_CLOSURE"
    ],
    Lookup[gRelation, "invertibility", None] === "NONINVERTIBLE_IN_GENERAL",
    MemberQ[
      Lookup[gRelation, "required_certificates", {}],
      "SOURCE_GRID_QUADRATURE_OR_SPECTRAL_CLOSURE"
    ],
    Lookup[polarizedRelation, "runtime_parity", None] === "FORBIDDEN",
    MemberQ[
      Lookup[polarizedRelation, "required_certificates", {}],
      "SCREEN_BASIS_TRANSPORT"
    ],
    Lookup[
      Lookup[noGo, "two_bin_witness", <||>],
      "loss_difference",
      None
    ] === "chi_1-chi_2",
    MemberQ[claims, "NO_J_OR_G_EXACT_STATE_EQUIVALENCE"],
    MemberQ[claims, "NO_CROSS_REPOSITORY_SOURCE_MUTATION"]
  ]
];
BASSStateSurfaceRegistryQ[_] := False;

End[];
EndPackage[];
