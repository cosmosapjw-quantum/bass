BeginPackage["BASS`IR`ProjectionClosureCertificateGraphR2C`"];

BASSProjectionClosureCertificateGraphR2CQ::usage =
  "BASSProjectionClosureCertificateGraphR2CQ[data] validates the BASS-only R2C certificate graph.";
BASSProjectionClosureCertificateR2CResiduals::usage =
  "BASSProjectionClosureCertificateR2CResiduals[] returns exact control and hostile-witness residuals.";

Begin["`Private`"];

ClearAll[graphAcyclicQ, rowsByKey];

graphAcyclicQ[dag_Association] := Module[{nodes, edges},
  nodes = Lookup[dag, "nodes", {}];
  edges = Lookup[dag, "edges", {}];
  If[
    !ListQ[nodes] || !ListQ[edges] ||
    Length[DeleteDuplicates[nodes]] =!= Length[nodes] ||
    !And @@ (MatchQ[#, {_String, _String}] & /@ edges),
    Return[False]
  ];
  TrueQ[AcyclicGraphQ[Graph[nodes, DirectedEdge @@@ edges]]]
];

rowsByKey[rows_List, key_String] := Association @ Map[
  Lookup[#, key, Missing["KeyAbsent"]] -> # &,
  rows
];

ClearAll[BASSProjectionClosureCertificateGraphR2CQ];
BASSProjectionClosureCertificateGraphR2CQ[data_Association] := Module[
  {
    ancestry, counts, families, relations, rankPolicy, witnesses, blocked,
    dag, literature, familyMap, relationMap, witnessMap, blockedMap,
    expectedFamilies, expectedRelations, expectedWitnesses, expectedBlocked
  },
  ancestry = Lookup[data, "normal_ancestry", <||>];
  counts = Lookup[data, "count_contract", <||>];
  families = Lookup[data, "certificate_families", {}];
  relations = Lookup[data, "relation_certificates", {}];
  rankPolicy = Lookup[data, "rank_and_aliasing_policy", <||>];
  witnesses = Lookup[data, "exact_witnesses", {}];
  blocked = Lookup[data, "explicit_blocked_promotions", {}];
  dag = Lookup[data, "stage_dag", <||>];
  literature = Lookup[data, "literature_regression", {}];

  familyMap = rowsByKey[families, "certificate_family_id"];
  relationMap = rowsByKey[relations, "relation_id"];
  witnessMap = rowsByKey[witnesses, "witness_id"];
  blockedMap = rowsByKey[blocked, "promotion"];

  expectedFamilies = Sort[{
    "ANGULAR_REPRESENTATION_CERTIFICATE",
    "SPECTRAL_PROJECTION_CLOSURE_CERTIFICATE",
    "MOMENT_EXCHANGE_CERTIFICATE",
    "POLARIZED_SCREEN_CERTIFICATE"
  }];
  expectedRelations = Sort[{
    "GRID_TO_PSTF",
    "PSTF_TO_GRID",
    "PSTF_TO_J",
    "GRID_TO_G",
    "KINETIC_TO_FLUID_SUMMARY",
    "SCALAR_TO_POLARIZED_PROHIBITED"
  }];
  expectedWitnesses = Sort[{
    "GAUSS_LEGENDRE_L2_ROUNDTRIP",
    "RADIAL_MULTIPLICATION_WORK_ORDER",
    "G_TWO_BIN_FREQUENCY_CLOSURE_NOGO",
    "RADIATION_MATTER_FOUR_FORCE_CANCELLATION",
    "SCREEN_PROJECTOR_RATIONAL_DIRECTION",
    "SCALAR_INTENSITY_DOES_NOT_FIX_POLARIZATION"
  }];
  expectedBlocked = Sort[{
    "PSTF_TO_J_AS_STATE_EQUIVALENCE",
    "GRID_TO_G_GENERIC_SCALAR_SOURCE_CLOSURE",
    "SCALAR_TO_POLARIZED_STATE"
  }];

  And[
    Lookup[data, "repository_scope", None] === "BASS_ONLY",
    Lookup[data, "owner", None] === "bass",
    !KeyExistsQ[data, "consumer_runtime_bindings"],

    Lookup[ancestry, "parent_commit", None] ===
      "0967a801d7baa9c4845cbcf07d9f967ae48f37c5",
    Lookup[ancestry, "native_role_graph_source_head", None] ===
      "bc7ea693bd8ac4f14376aaac51d4007467702803",
    Lookup[ancestry, "role_graph_sha256", None] ===
      "23e4f1a01cbb7f5844cb151148a8ef359c17a27d4317e9dd4c6227e5c0f1bfe6",
    Lookup[ancestry, "role_graph_wolfram_receipt_sha256", None] ===
      "3e675324b1abe8673df3d7111d811cfffe9cea4edaeb9a72732dea039daec59d",
    Lookup[ancestry, "state_surface_registry_sha256", None] ===
      "5a5042d4b4cd653b3455dda45f9cd5aa67314cb03416b532ff34dbc9695f621c",
    Lookup[ancestry, "hardened_formula_registry_semantic_hash", None] ===
      "5951f566d911c81848743055c1573f6d11b0b00937d36747b71e6bc12dd96416",

    counts === <|
      "certificate_families" -> 4,
      "relation_certificate_rows" -> 6,
      "exact_hostile_or_control_witnesses" -> 6,
      "explicit_blocked_promotions" -> 3
    |>,

    Length[families] === 4,
    Length[DeleteDuplicates[Keys[familyMap]]] === 4,
    Sort[Keys[familyMap]] === expectedFamilies,
    And @@ (
      ListQ[Lookup[#, "required_fields", None]] &&
      Length[Lookup[#, "required_fields", {}]] > 0 &&
      Lookup[#, "runtime_status", None] === "CERTIFICATE_SCHEMA_ONLY" &
      /@ families
    ),

    Length[relations] === 6,
    Length[DeleteDuplicates[Keys[relationMap]]] === 6,
    Sort[Keys[relationMap]] === expectedRelations,
    Lookup[Lookup[relationMap, "PSTF_TO_J", <||>], "invertibility_claim", None] ===
      "FORBIDDEN",
    Lookup[Lookup[relationMap, "GRID_TO_G", <||>], "invertibility_claim", None] ===
      "FORBIDDEN",
    Lookup[
      Lookup[relationMap, "SCALAR_TO_POLARIZED_PROHIBITED", <||>],
      "direction",
      None
    ] === "NO_IMPLICIT_PROMOTION",

    Lookup[rankPolicy, "hardcoded_numeric_ell_cutoff_forbidden", None] === True,
    Lookup[rankPolicy, "ell_target", None] === "RUNTIME_PARAMETER",
    Lookup[rankPolicy, "ell_work", None] ===
      "ADAPTIVE_OR_EXPLICIT_RUNTIME_PARAMETER",
    Lookup[rankPolicy, "radial_polynomial_product_sufficient_condition", None] ===
      "radial_work_order >= radial_output_order + radial_source_order",
    Lookup[rankPolicy, "angular_harmonic_product_sufficient_condition", None] ===
      "angular_work_rank >= angular_output_rank + angular_source_rank",

    Length[witnesses] === 6,
    Length[DeleteDuplicates[Keys[witnessMap]]] === 6,
    Sort[Keys[witnessMap]] === expectedWitnesses,
    Lookup[
      Lookup[witnessMap, "GAUSS_LEGENDRE_L2_ROUNDTRIP", <||>],
      "expected_analysis_residuals",
      None
    ] === {0, 0, 0},
    Lookup[
      Lookup[witnessMap, "RADIAL_MULTIPLICATION_WORK_ORDER", <||>],
      "dropped_high_order_coefficient_if_truncated_at_output_order",
      None
    ] === 8,
    Lookup[
      Lookup[witnessMap, "G_TWO_BIN_FREQUENCY_CLOSURE_NOGO", <||>],
      "generic_scalar_closure",
      None
    ] === False,
    Lookup[
      Lookup[witnessMap, "RADIATION_MATTER_FOUR_FORCE_CANCELLATION", <||>],
      "expected_total_residual",
      None
    ] === {0, 0, 0, 0},
    Lookup[
      Lookup[witnessMap, "SCREEN_PROJECTOR_RATIONAL_DIRECTION", <||>],
      "expected_trace",
      None
    ] === 2,
    Lookup[
      Lookup[witnessMap, "SCALAR_INTENSITY_DOES_NOT_FIX_POLARIZATION", <||>],
      "frobenius_difference_squared",
      None
    ] === 8,

    Length[blocked] === 3,
    Sort[Keys[blockedMap]] === expectedBlocked,

    graphAcyclicQ[dag],
    MemberQ[
      Lookup[dag, "edges", {}],
      {"FORMULA_CONSUMER_ROLE_GRAPH", "PROJECTION_CLOSURE_CERTIFICATE_GRAPH"}
    ],
    MemberQ[
      Lookup[dag, "edges", {}],
      {"PROJECTION_CLOSURE_CERTIFICATE_GRAPH", "CONSUMER_BINDING_CONTRACTS"}
    ],

    Length[literature] > 0,
    And @@ (Lookup[#, "authority_effect", None] === "NONE" & /@ literature),
    Lookup[data, "status", None] === "IMPLEMENTED_CONTRACT_LOCAL_REPLAY_REQUIRED"
  ]
];

ClearAll[BASSProjectionClosureCertificateR2CResiduals];
BASSProjectionClosureCertificateR2CResiduals[] := Module[
  {
    nodes, weights, coefficients, distribution, analyzed, reconstructed,
    q, radialProduct, direction, screen, coherencyA, coherencyB,
    radiationFourForce, matterFourForce
  },
  nodes = {-Sqrt[3/5], 0, Sqrt[3/5]};
  weights = {5/9, 8/9, 5/9};
  coefficients = {2, -3, 5};
  distribution[z_] := Sum[
    coefficients[[ell + 1]] LegendreP[ell, z],
    {ell, 0, 2}
  ];
  analyzed = RootReduce @ Table[
    (2 ell + 1)/2 Sum[
      weights[[k]] distribution[nodes[[k]]] LegendreP[ell, nodes[[k]]],
      {k, 1, 3}
    ],
    {ell, 0, 2}
  ];
  reconstructed[z_] := Sum[
    analyzed[[ell + 1]] LegendreP[ell, z],
    {ell, 0, 2}
  ];

  radialProduct = Expand[(1 + 2 q) (3 + 4 q)];

  direction = {3/5, 4/5, 0};
  screen = IdentityMatrix[3] - Outer[Times, direction, direction];

  coherencyA = {{3, 0}, {0, 1}};
  coherencyB = {{1, 0}, {0, 3}};

  radiationFourForce = {2, -3, 5, 7};
  matterFourForce = {-2, 3, -5, -7};

  <|
    "legendre_analysis_residuals" -> RootReduce[analyzed - coefficients],
    "legendre_grid_roundtrip_residuals" -> RootReduce @ Table[
      reconstructed[nodes[[k]]] - distribution[nodes[[k]]],
      {k, 1, 3}
    ],
    "radial_product_degree_residual" -> Exponent[radialProduct, q] - 2,
    "radial_dropped_coefficient_residual" -> Coefficient[radialProduct, q, 2] - 8,
    "radial_alias_witness_coefficient" -> Coefficient[radialProduct, q, 2],
    "g_integrated_state_residual" -> Total[{1, 0}] - Total[{0, 1}],
    "g_frequency_loss_difference" -> Dot[{2, 5}, {1, 0}] - Dot[{2, 5}, {0, 1}],
    "four_force_total_residual" -> radiationFourForce + matterFourForce,
    "screen_idempotence_residual" -> RootReduce[screen.screen - screen],
    "screen_direction_residual" -> RootReduce[screen.direction],
    "screen_trace_residual" -> RootReduce[Tr[screen] - 2],
    "scalar_intensity_trace_residual" -> Tr[coherencyA] - Tr[coherencyB],
    "polarization_state_frobenius_difference_squared" ->
      Tr[Transpose[coherencyA - coherencyB].(coherencyA - coherencyB)] - 8,
    "polarization_state_nonuniqueness_witness" ->
      Tr[Transpose[coherencyA - coherencyB].(coherencyA - coherencyB)],
    "radial_work_order_residual" -> 2 - (1 + 1),
    "angular_work_rank_residual" -> 4 - (2 + 2)
  |>
];

End[];
EndPackage[];
