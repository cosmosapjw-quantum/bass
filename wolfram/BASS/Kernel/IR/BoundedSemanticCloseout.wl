BeginPackage["BASS`IR`BoundedSemanticCloseout`"];

BASSBoundedSemanticCloseoutQ::usage =
  "BASSBoundedSemanticCloseoutQ[data] validates the BASS-only bounded SYNC-MAP-02F closeout contract.";
BASSBoundedSemanticCloseoutResiduals::usage =
  "BASSBoundedSemanticCloseoutResiduals[data] returns exact count residuals and semantic firewall checks.";

Begin["`Private`"];

ClearAll[graphAcyclicQ];
graphAcyclicQ[dag_Association] := Module[{nodes, edges},
  nodes = Lookup[dag, "nodes", {}];
  edges = Lookup[dag, "edges", {}];
  If[
    !ListQ[nodes] || !ListQ[edges] ||
    !And @@ (MatchQ[#, {_String, _String}] & /@ edges),
    Return[False]
  ];
  TrueQ[AcyclicGraphQ[Graph[nodes, DirectedEdge @@@ edges]]]
];

ClearAll[expectedStages, expectedCounts, expectedNodes, expectedEdges,
  expectedClaims, expectedFirewall];

expectedStages[] := {
  <|
    "stage" -> "SYNC_MAP_02E_R1_OWNER_FORMULA_HARDENING",
    "pr" -> 110,
    "closeout_commit" -> "8b73919e0e2a2326c338c796ac80b0684fe49db1",
    "native_replay_source_head" -> "65be780c06b014e8b699a8af4835b2290f39b252",
    "primary_identity_kind" -> "REGISTRY_SEMANTIC_HASH",
    "primary_identity" -> "5951f566d911c81848743055c1573f6d11b0b00937d36747b71e6bc12dd96416",
    "secondary_identity_kind" -> "GENERATED_EXPORT_SHA256",
    "secondary_identity" -> "d3398cc283f1d88301496aff3014a9dbc57de4bceaa89de997e687c1f8c44723",
    "native_gate" -> "PYTHON_6_OF_6_AND_WOLFRAM_11_OF_11_PASS"
  |>,
  <|
    "stage" -> "SYNC_MAP_02F_R2B_STATE_SURFACE_REGISTRY",
    "pr" -> 114,
    "closeout_commit" -> "6bb65476a87d1ac8daa9f7239d884c369c51ce33",
    "native_replay_source_head" -> "bf7b7056fd0b61e4c4a188f30d5b4fc136f6e9c5",
    "primary_identity_kind" -> "STATE_SURFACE_REGISTRY_SHA256",
    "primary_identity" -> "5a5042d4b4cd653b3455dda45f9cd5aa67314cb03416b532ff34dbc9695f621c",
    "secondary_identity_kind" -> "NATIVE_WOLFRAM_RECEIPT_SHA256",
    "secondary_identity" -> "d96ddb95ecb2979ae5919837ad8a1de30b0468c3a3d34ab28885f31c9be99bf2",
    "native_gate" -> "PYTHON_7_OF_7_AND_WOLFRAM_7_OF_7_PASS"
  |>,
  <|
    "stage" -> "SYNC_MAP_02F_R2A_FORMULA_CONSUMER_ROLE_GRAPH",
    "pr" -> 116,
    "closeout_commit" -> "0967a801d7baa9c4845cbcf07d9f967ae48f37c5",
    "native_replay_source_head" -> "bc7ea693bd8ac4f14376aaac51d4007467702803",
    "primary_identity_kind" -> "ROLE_GRAPH_SHA256",
    "primary_identity" -> "23e4f1a01cbb7f5844cb151148a8ef359c17a27d4317e9dd4c6227e5c0f1bfe6",
    "secondary_identity_kind" -> "NATIVE_WOLFRAM_RECEIPT_SHA256",
    "secondary_identity" -> "3e675324b1abe8673df3d7111d811cfffe9cea4edaeb9a72732dea039daec59d",
    "native_gate" -> "PYTHON_9_OF_9_AND_WOLFRAM_11_OF_11_PASS"
  |>,
  <|
    "stage" -> "SYNC_MAP_02F_R2C_PROJECTION_CLOSURE_CERTIFICATE_GRAPH",
    "pr" -> 118,
    "closeout_commit" -> "e0e4d703bb160128135a97cc384f8533fced743b",
    "native_replay_source_head" -> "4694fc0f9c66b26c96acb6d21bee0a58c8606373",
    "primary_identity_kind" -> "CERTIFICATE_GRAPH_SHA256",
    "primary_identity" -> "876c13d37181e5565bacd8d27ccecfeb835268c21520fa936d6736f74b0cc3ae",
    "secondary_identity_kind" -> "NATIVE_WOLFRAM_RECEIPT_SHA256",
    "secondary_identity" -> "8bd3ee213b9fbb3ad3a8b28bd561e8de5e8896c16534c7c4894691b71b542b00",
    "native_gate" -> "PYTHON_9_OF_9_AND_WOLFRAM_17_OF_17_PASS"
  |>
};

expectedCounts[] := <|
  "upstream_stage_rows" -> 4,
  "authority_formulas" -> 6,
  "state_surfaces" -> 6,
  "formula_consumer_pairs" -> 10,
  "implementation_role_rows" -> 11,
  "named_source_symbols" -> 12,
  "explicit_absent_implementation_slots" -> 1,
  "certificate_families" -> 4,
  "relation_certificate_rows" -> 6,
  "exact_witnesses" -> 6,
  "blocked_promotions" -> 13
|>;

expectedNodes[] := {
  "OWNER_FORMULA_HARDENING",
  "STATE_SURFACE_REGISTRY",
  "FORMULA_CONSUMER_ROLE_GRAPH",
  "PROJECTION_CLOSURE_CERTIFICATE_GRAPH",
  "BOUNDED_SEMANTIC_CLOSEOUT"
};

expectedEdges[] := {
  {"OWNER_FORMULA_HARDENING", "STATE_SURFACE_REGISTRY"},
  {"STATE_SURFACE_REGISTRY", "FORMULA_CONSUMER_ROLE_GRAPH"},
  {"FORMULA_CONSUMER_ROLE_GRAPH", "PROJECTION_CLOSURE_CERTIFICATE_GRAPH"},
  {"PROJECTION_CLOSURE_CERTIFICATE_GRAPH", "BOUNDED_SEMANTIC_CLOSEOUT"}
};

expectedClaims[] := <|
  "owner_formula_semantics" -> "PASS_BOUNDED",
  "state_surface_typing" -> "PASS_BOUNDED",
  "formula_consumer_role_semantics" -> "PASS_BOUNDED",
  "projection_closure_certificate_schema" -> "PASS_BOUNDED",
  "normal_ancestry" -> "PASS_EXACT_PINNED",
  "native_replay_evidence" -> "PASS_ALL_FOUR_STAGES"
|>;

expectedFirewall[] := {
  "CROSS_REPOSITORY_CONSUMER_RUNTIME_PARITY",
  "GRID_PSTF_NUMERICAL_PARITY",
  "J_SPECTRAL_CLOSURE_ADMISSION",
  "G_SPECTRAL_CLOSURE_ADMISSION",
  "FLUID_EXCHANGE_RUNTIME_PASS",
  "SCREEN_BASIS_TRANSPORT_IMPLEMENTED",
  "POLARIZED_COLLISION_RUNTIME",
  "POLARIZED_ARBITRARY_ELL_COMPILER",
  "BASS_BACKGROUND_PROVIDER",
  "GLOBAL_MATTER_TILT",
  "LIKELIHOOD_READY",
  "SCIENCE_PROMOTION",
  "PASS_RF04"
};

ClearAll[BASSBoundedSemanticCloseoutQ];
BASSBoundedSemanticCloseoutQ[data_Association] := Module[
  {ancestry, stages, counts, dag, binding, literature},
  ancestry = Lookup[data, "normal_ancestry", <||>];
  stages = Lookup[ancestry, "stages", {}];
  counts = Lookup[data, "count_contract", <||>];
  dag = Lookup[data, "stage_dag", <||>];
  binding = Lookup[data, "consumer_binding_policy", <||>];
  literature = Lookup[data, "literature_regression", <||>];

  And[
    Lookup[data, "schema_version", None] === "1.0.0",
    Lookup[data, "stage_id", None] === "SYNC_MAP_02F_BOUNDED_SEMANTIC_CLOSEOUT",
    Lookup[data, "repository_scope", None] === "BASS_ONLY",
    Lookup[data, "owner", None] === "bass",
    !KeyExistsQ[data, "consumer_bindings"],

    Lookup[ancestry, "parent_commit", None] ===
      "e0e4d703bb160128135a97cc384f8533fced743b",
    stages === expectedStages[],
    counts === expectedCounts[],

    Lookup[dag, "nodes", {}] === expectedNodes[],
    Lookup[dag, "edges", {}] === expectedEdges[],
    graphAcyclicQ[dag],

    Lookup[data, "bounded_claims", <||>] === expectedClaims[],
    Lookup[data, "promotion_firewall", {}] === expectedFirewall[],
    DuplicateFreeQ[Lookup[data, "promotion_firewall", {}]],
    Lookup[data, "promotion_status", None] === "ALL_WITHHELD",

    Lookup[binding, "binding_rows_present", None] === False,
    Lookup[binding, "consumer_source_mutation_authorized", None] === False,
    Lookup[binding, "runtime_parity_inferred_from_formula_occurrence", None] === False,
    Lookup[binding, "next_stage", None] === "BASS_CONSUMER_BINDING_CONTRACTS",

    Lookup[literature, "authority_effect", None] === "NONE",
    Lookup[data, "status", None] === "IMPLEMENTED_CONTRACT_LOCAL_REPLAY_REQUIRED"
  ]
];

ClearAll[BASSBoundedSemanticCloseoutResiduals];
BASSBoundedSemanticCloseoutResiduals[data_Association] := Module[
  {ancestry, stages, counts, dag, binding, firewall},
  ancestry = Lookup[data, "normal_ancestry", <||>];
  stages = Lookup[ancestry, "stages", {}];
  counts = Lookup[data, "count_contract", <||>];
  dag = Lookup[data, "stage_dag", <||>];
  binding = Lookup[data, "consumer_binding_policy", <||>];
  firewall = Lookup[data, "promotion_firewall", {}];

  <|
    "upstream_stage_count_residual" -> Length[stages] - 4,
    "formula_count_residual" -> Lookup[counts, "authority_formulas", -999] - 6,
    "state_surface_count_residual" -> Lookup[counts, "state_surfaces", -999] - 6,
    "formula_consumer_pair_count_residual" ->
      Lookup[counts, "formula_consumer_pairs", -999] - 10,
    "implementation_role_count_residual" ->
      Lookup[counts, "implementation_role_rows", -999] - 11,
    "named_source_symbol_count_residual" ->
      Lookup[counts, "named_source_symbols", -999] - 12,
    "absent_slot_count_residual" ->
      Lookup[counts, "explicit_absent_implementation_slots", -999] - 1,
    "certificate_family_count_residual" ->
      Lookup[counts, "certificate_families", -999] - 4,
    "relation_certificate_count_residual" ->
      Lookup[counts, "relation_certificate_rows", -999] - 6,
    "exact_witness_count_residual" -> Lookup[counts, "exact_witnesses", -999] - 6,
    "blocked_promotion_count_residual" -> Length[firewall] - 13,
    "stage_dag_acyclic" -> graphAcyclicQ[dag],
    "upstream_identity_exact" -> TrueQ[stages === expectedStages[]],
    "bounded_claims_exact" ->
      TrueQ[Lookup[data, "bounded_claims", <||>] === expectedClaims[]],
    "promotion_firewall_exact" -> TrueQ[
      firewall === expectedFirewall[] &&
      DuplicateFreeQ[firewall] &&
      Lookup[data, "promotion_status", None] === "ALL_WITHHELD"
    ],
    "consumer_binding_firewall_intact" -> TrueQ[
      !KeyExistsQ[data, "consumer_bindings"] &&
      Lookup[binding, "binding_rows_present", None] === False &&
      Lookup[binding, "consumer_source_mutation_authorized", None] === False &&
      Lookup[binding, "runtime_parity_inferred_from_formula_occurrence", None] === False
    ]
  |>
];

End[];
EndPackage[];
