BeginPackage["BASS`IR`ConsumerBindingContractsR3`"];

BASSConsumerBindingContractsR3Q::usage =
  "BASSConsumerBindingContractsR3Q[data] validates the BASS-only consumer-binding contract.";
BASSConsumerBindingContractsR3Residuals::usage =
  "BASSConsumerBindingContractsR3Residuals[data] returns exact count residuals and semantic firewall checks.";

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

ClearAll[
  expectedCounts, expectedConsumerCoreRows, expectedPairIDs,
  expectedBindingCoreRows, expectedFormulaCoreRows, expectedRoleCoreRows,
  expectedNamedSymbols, expectedStateSurfaces, expectedCertificateFamilies,
  expectedBlockedPromotions, expectedAuthorizationFirewall,
  expectedDAGNodes, expectedDAGEdges
];

expectedCounts[] := <|
  "consumers" -> 3,
  "binding_requests" -> 10,
  "source_role_pins" -> 11,
  "named_source_symbols" -> 12,
  "absent_implementation_slots" -> 1,
  "owner_formulas" -> 6,
  "state_surfaces" -> 6,
  "certificate_families" -> 4,
  "blocked_promotions" -> 13
|>;

expectedConsumerCoreRows[] := {
  {"rec_bianchi", 4, "REC_BINDING_RUNTIME_VALIDATION", False, False},
  {"rei_bianchi", 2, "REI_BINDING_RUNTIME_VALIDATION", False, False},
  {"htt_base", 4, "HTT_BINDING_RUNTIME_VALIDATION", False, False}
};

expectedPairIDs[] := {
  "02F-R2A-REC-ABERRATION",
  "02F-R2A-REC-DOPPLER",
  "02F-R2A-REC-DIRECTION-FLOW",
  "02F-R2A-REC-ENERGY-DRIFT",
  "02F-R2A-REI-DIRECTION-FLOW",
  "02F-R2A-REI-ENERGY-DRIFT",
  "02F-R2A-HTT-ABERRATION",
  "02F-R2A-HTT-DOPPLER",
  "02F-R2A-HTT-SOLID-ANGLE",
  "02F-R2A-HTT-BLACKBODY-T"
};

expectedBindingCoreRows[] := {
  {"BINDING-REC-ABERRATION", "02F-R2A-REC-ABERRATION", "rec_bianchi",
    "BASS.FRAME.ABERRATED_DIRECTION.001", {"ROLE-REC-ABERRATION"},
    {"ANGULAR_REPRESENTATION_CERTIFICATE"}, "REC_BINDING_RUNTIME_VALIDATION", False, False},
  {"BINDING-REC-DOPPLER", "02F-R2A-REC-DOPPLER", "rec_bianchi",
    "BASS.FRAME.DOPPLER_FACTOR.001", {"ROLE-REC-DOPPLER"},
    {"ANGULAR_REPRESENTATION_CERTIFICATE"}, "REC_BINDING_RUNTIME_VALIDATION", False, False},
  {"BINDING-REC-DIRECTION-FLOW", "02F-R2A-REC-DIRECTION-FLOW", "rec_bianchi",
    "BASS.PHOTON.DIRECTION_FLOW.001", {"ROLE-REC-DIRECTION-FLOW"},
    {"ANGULAR_REPRESENTATION_CERTIFICATE"}, "REC_BINDING_RUNTIME_VALIDATION", False, False},
  {"BINDING-REC-ENERGY-DRIFT", "02F-R2A-REC-ENERGY-DRIFT", "rec_bianchi",
    "BASS.PHOTON.ENERGY_DRIFT.001", {"ROLE-REC-ENERGY-DRIFT"},
    {"ANGULAR_REPRESENTATION_CERTIFICATE"}, "REC_BINDING_RUNTIME_VALIDATION", False, False},
  {"BINDING-REI-DIRECTION-FLOW", "02F-R2A-REI-DIRECTION-FLOW", "rei_bianchi",
    "BASS.PHOTON.DIRECTION_FLOW.001", {"ROLE-REI-DIRECTION-FLOW-ABSENT"},
    {}, "REI_BINDING_RUNTIME_VALIDATION", False, False},
  {"BINDING-REI-ENERGY-DRIFT", "02F-R2A-REI-ENERGY-DRIFT", "rei_bianchi",
    "BASS.PHOTON.ENERGY_DRIFT.001", {"ROLE-REI-ENERGY-DRIFT-CONTROL"},
    {}, "REI_BINDING_RUNTIME_VALIDATION", False, False},
  {"BINDING-HTT-ABERRATION", "02F-R2A-HTT-ABERRATION", "htt_base",
    "BASS.FRAME.ABERRATED_DIRECTION.001", {"ROLE-HTT-ABERRATION-BIDIRECTIONAL"},
    {}, "HTT_BINDING_RUNTIME_VALIDATION", False, False},
  {"BINDING-HTT-DOPPLER", "02F-R2A-HTT-DOPPLER", "htt_base",
    "BASS.FRAME.DOPPLER_FACTOR.001", {"ROLE-HTT-DOPPLER-BIDIRECTIONAL"},
    {}, "HTT_BINDING_RUNTIME_VALIDATION", False, False},
  {"BINDING-HTT-SOLID-ANGLE", "02F-R2A-HTT-SOLID-ANGLE", "htt_base",
    "BASS.FRAME.SOLID_ANGLE_JACOBIAN.001", {"ROLE-HTT-SOLID-ANGLE-ORACLE"},
    {}, "HTT_BINDING_RUNTIME_VALIDATION", False, False},
  {"BINDING-HTT-BLACKBODY-T", "02F-R2A-HTT-BLACKBODY-T", "htt_base",
    "BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001",
    {"ROLE-HTT-BLACKBODY-FULL", "ROLE-HTT-BLACKBODY-PREPULLED"},
    {}, "HTT_BINDING_RUNTIME_VALIDATION", False, False}
};

expectedFormulaCoreRows[] := {
  {"BASS.FRAME.ABERRATED_DIRECTION.001", "b20aa445f5e2890674480a6e8e71fd919aa9efd13a1a8c4780e98b67b9974eec", "1"},
  {"BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001", "99ededbaa9c04ab51f2ffda4c19a55236b243021271445d3dad916e2e660c143", "K"},
  {"BASS.FRAME.DOPPLER_FACTOR.001", "fb56218a0256edde59a1d89eb4e3ce69ce82800d852908ee84ce8aec83f2fb47", "1"},
  {"BASS.FRAME.SOLID_ANGLE_JACOBIAN.001", "0436b513724b09fe826aa486c5dd3def19d0dc5e6daf9fabdd8d899fd1618dc4", "1"},
  {"BASS.PHOTON.DIRECTION_FLOW.001", "1eb20b3b46b596139d781d529a1511df983c2b6c00fbe85208ef03e7888f08ce", "L^-1"},
  {"BASS.PHOTON.ENERGY_DRIFT.001", "840fe1d68d87b78bb5b5d831fb3d8025b26c29fda1f9da49b0f387e1a8d7bcfd", "L^-1"}
};

expectedRoleCoreRows[] := {
  {"ROLE-REC-ABERRATION", "02F-R2A-REC-ABERRATION", "CONSUMER_IMPLEMENTATION",
    "c4bf37d7271caf651bca41b6eaab8caff436452b", "src/full_bianchi_hyrec/background/characteristics.py",
    "f71ec2607daac808b871279ad0893d4653169343", {"aberrate_direction"}, True},
  {"ROLE-REC-DOPPLER", "02F-R2A-REC-DOPPLER", "CONSUMER_IMPLEMENTATION",
    "c4bf37d7271caf651bca41b6eaab8caff436452b", "src/full_bianchi_hyrec/background/characteristics.py",
    "f71ec2607daac808b871279ad0893d4653169343", {"doppler_factor"}, True},
  {"ROLE-REC-DIRECTION-FLOW", "02F-R2A-REC-DIRECTION-FLOW", "CONSUMER_IMPLEMENTATION",
    "c4bf37d7271caf651bca41b6eaab8caff436452b", "src/full_bianchi_hyrec/background/characteristics.py",
    "f71ec2607daac808b871279ad0893d4653169343", {"normal_frame_characteristic.D0_direction_normal_s_inv"}, True},
  {"ROLE-REC-ENERGY-DRIFT", "02F-R2A-REC-ENERGY-DRIFT", "CONSUMER_IMPLEMENTATION",
    "c4bf37d7271caf651bca41b6eaab8caff436452b", "src/full_bianchi_hyrec/background/characteristics.py",
    "f71ec2607daac808b871279ad0893d4653169343", {"normal_frame_characteristic.R_normal_s_inv"}, True},
  {"ROLE-REI-DIRECTION-FLOW-ABSENT", "02F-R2A-REI-DIRECTION-FLOW", "ABSENT_IMPLEMENTATION_SLOT",
    "f4eb2c893ce6449f8899ab6f02c83421fc7c7019", "src/rei_bianchi/b2b_physical_model.py",
    "b3cc5e45988687b76d5be04c6335009b4c9bd17f", {}, False},
  {"ROLE-REI-ENERGY-DRIFT-CONTROL", "02F-R2A-REI-ENERGY-DRIFT", "RESTRICTED_SUBSPACE_IMPLEMENTATION",
    "f4eb2c893ce6449f8899ab6f02c83421fc7c7019", "src/rei_bianchi/b2b_physical_model.py",
    "b3cc5e45988687b76d5be04c6335009b4c9bd17f", {"SpectrumLane.redshift_coeff"}, False},
  {"ROLE-HTT-ABERRATION-BIDIRECTIONAL", "02F-R2A-HTT-ABERRATION", "BIDIRECTIONAL_DIRECTION_MAP",
    "29427a1f7f2c5d46e43ffe03053c4ac13e969228", "htt/obsstat/lorentz_sky_pullback.py",
    "c518cdd0dcdd3ca628c71f6dd9e6a75e174ba805", {"aberrate_sky_direction", "deaberrate_sky_direction"}, True},
  {"ROLE-HTT-DOPPLER-BIDIRECTIONAL", "02F-R2A-HTT-DOPPLER", "BIDIRECTIONAL_CHART_FACTOR",
    "29427a1f7f2c5d46e43ffe03053c4ac13e969228", "htt/obsstat/lorentz_sky_pullback.py",
    "c518cdd0dcdd3ca628c71f6dd9e6a75e174ba805", {"doppler_factor_unboosted", "doppler_factor_boosted"}, True},
  {"ROLE-HTT-SOLID-ANGLE-ORACLE", "02F-R2A-HTT-SOLID-ANGLE", "INDEPENDENT_ORACLE",
    "29427a1f7f2c5d46e43ffe03053c4ac13e969228", "htt/obsstat/lorentz_sky_pullback.py",
    "c518cdd0dcdd3ca628c71f6dd9e6a75e174ba805", {"solid_angle_jacobian"}, False},
  {"ROLE-HTT-BLACKBODY-FULL", "02F-R2A-HTT-BLACKBODY-T", "FULL_FIELD_PULLBACK",
    "29427a1f7f2c5d46e43ffe03053c4ac13e969228", "htt/obsstat/lorentz_sky_pullback.py",
    "c518cdd0dcdd3ca628c71f6dd9e6a75e174ba805", {"pullback_thermodynamic_temperature_field"}, True},
  {"ROLE-HTT-BLACKBODY-PREPULLED", "02F-R2A-HTT-BLACKBODY-T", "PREPULLED_VALUE_PRIMITIVE",
    "29427a1f7f2c5d46e43ffe03053c4ac13e969228", "htt/obsstat/lorentz_sky_pullback.py",
    "c518cdd0dcdd3ca628c71f6dd9e6a75e174ba805", {"thermodynamic_temperature_pullback"}, False}
};

expectedNamedSymbols[] := {
  "aberrate_direction", "doppler_factor",
  "normal_frame_characteristic.D0_direction_normal_s_inv",
  "normal_frame_characteristic.R_normal_s_inv",
  "SpectrumLane.redshift_coeff", "aberrate_sky_direction",
  "deaberrate_sky_direction", "doppler_factor_unboosted",
  "doppler_factor_boosted", "solid_angle_jacobian",
  "pullback_thermodynamic_temperature_field", "thermodynamic_temperature_pullback"
};

expectedStateSurfaces[] := {
  "GRID_F_Q_E", "PSTF_F_AELL_Q", "J_I_AELL", "G_ANGULAR_ENERGY",
  "FLUID_COMPONENT_SUMMARY", "POLARIZED_COHERENCY"
};

expectedCertificateFamilies[] := {
  "ANGULAR_REPRESENTATION_CERTIFICATE",
  "SPECTRAL_PROJECTION_CLOSURE_CERTIFICATE",
  "MOMENT_EXCHANGE_CERTIFICATE",
  "POLARIZED_SCREEN_CERTIFICATE"
};

expectedBlockedPromotions[] := {
  "CROSS_REPOSITORY_CONSUMER_RUNTIME_PARITY", "GRID_PSTF_NUMERICAL_PARITY",
  "J_SPECTRAL_CLOSURE_ADMISSION", "G_SPECTRAL_CLOSURE_ADMISSION",
  "FLUID_EXCHANGE_RUNTIME_PASS", "SCREEN_BASIS_TRANSPORT_IMPLEMENTED",
  "POLARIZED_COLLISION_RUNTIME", "POLARIZED_ARBITRARY_ELL_COMPILER",
  "BASS_BACKGROUND_PROVIDER", "GLOBAL_MATTER_TILT", "LIKELIHOOD_READY",
  "SCIENCE_PROMOTION", "PASS_RF04"
};

expectedAuthorizationFirewall[] := <|
  "consumer_source_mutation_authorized" -> False,
  "runtime_parity_admitted" -> False,
  "provider_promotion_authorized" -> False,
  "science_promotion_authorized" -> False,
  "merge_or_ready_transition_authorized" -> False,
  "formula_occurrence_implies_runtime_parity" -> False,
  "source_role_pin_implies_runtime_parity" -> False,
  "certificate_schema_implies_runtime_certificate" -> False
|>;

expectedDAGNodes[] := {
  "BOUNDED_SEMANTIC_CLOSEOUT", "CONSUMER_BINDING_CONTRACTS",
  "REC_RUNTIME_VALIDATION", "REI_RUNTIME_VALIDATION", "HTT_RUNTIME_VALIDATION",
  "CROSS_REPOSITORY_PARITY_FEDERATION"
};

expectedDAGEdges[] := {
  {"BOUNDED_SEMANTIC_CLOSEOUT", "CONSUMER_BINDING_CONTRACTS"},
  {"CONSUMER_BINDING_CONTRACTS", "REC_RUNTIME_VALIDATION"},
  {"CONSUMER_BINDING_CONTRACTS", "REI_RUNTIME_VALIDATION"},
  {"CONSUMER_BINDING_CONTRACTS", "HTT_RUNTIME_VALIDATION"},
  {"REC_RUNTIME_VALIDATION", "CROSS_REPOSITORY_PARITY_FEDERATION"},
  {"REI_RUNTIME_VALIDATION", "CROSS_REPOSITORY_PARITY_FEDERATION"},
  {"HTT_RUNTIME_VALIDATION", "CROSS_REPOSITORY_PARITY_FEDERATION"}
};

ClearAll[consumerCoreRows, bindingCoreRows, formulaCoreRows, roleCoreRows];
consumerCoreRows[rows_List] := ({
  Lookup[#, "repository", None], Lookup[#, "binding_request_count", None],
  Lookup[#, "runtime_validation_stage", None],
  Lookup[#, "source_mutation_authorized", None],
  Lookup[#, "runtime_parity_admitted", None]
} & /@ rows);

bindingCoreRows[rows_List] := ({
  Lookup[#, "binding_id", None], Lookup[#, "pair_id", None],
  Lookup[#, "consumer_repository", None], Lookup[#, "formula_id", None],
  Lookup[#, "source_role_ids", {}], Lookup[#, "conditional_certificate_families", {}],
  Lookup[#, "next_owner_stage", None], Lookup[#, "runtime_parity_admitted", None],
  Lookup[#, "consumer_source_mutation_authorized", None]
} & /@ rows);

formulaCoreRows[rows_List] := ({
  Lookup[#, "formula_id", None], Lookup[#, "semantic_hash", None],
  Lookup[#, "dimension", None]
} & /@ rows);

roleCoreRows[rows_List] := ({
  Lookup[#, "role_id", None], Lookup[#, "pair_id", None],
  Lookup[#, "role_type", None], Lookup[#, "source_commit", None],
  Lookup[#, "source_path", None], Lookup[#, "source_blob", None],
  Lookup[#, "source_symbols", {}], Lookup[#, "implements_full_formula", None]
} & /@ rows);

ClearAll[BASSConsumerBindingContractsR3Q];
BASSConsumerBindingContractsR3Q[data_Association] := Module[
  {ancestry, counts, consumers, bindings, authority, formulas, roles,
   roleMap, statePolicy, certificates, blocked, firewall, dag, literature,
   gateIDs, parallel, flattenedSymbols},
  ancestry = Lookup[data, "normal_ancestry", <||>];
  counts = Lookup[data, "count_contract", <||>];
  consumers = Lookup[data, "consumer_repositories", {}];
  bindings = Lookup[data, "binding_requests", {}];
  authority = Lookup[data, "formula_authority", <||>];
  formulas = Lookup[authority, "formulas", {}];
  roles = Lookup[data, "source_role_pins", {}];
  roleMap = Association[(Lookup[#, "role_id", ""] -> #) & /@ roles];
  statePolicy = Lookup[data, "state_surface_policy", <||>];
  certificates = Lookup[data, "certificate_families", {}];
  blocked = Lookup[data, "blocked_promotions", {}];
  firewall = Lookup[data, "authorization_firewall", <||>];
  dag = Lookup[data, "stage_dag", <||>];
  literature = Lookup[data, "literature_regression", {}];
  gateIDs = Lookup[#, "gate_id", None] & /@ Lookup[data, "gate_templates", {}];
  parallel = Lookup[data, "parallel_bass_runtime_evidence", {}];
  flattenedSymbols = Flatten[Lookup[#, "source_symbols", {}] & /@ roles];

  And[
    Lookup[data, "schema_version", None] === "1.0.0",
    Lookup[data, "stage_id", None] === "SYNC_MAP_02F_R3_CONSUMER_BINDING_CONTRACTS",
    Lookup[data, "repository_scope", None] === "BASS_ONLY",
    Lookup[data, "owner", None] === "bass",
    Lookup[data, "status", None] === "IMPLEMENTED_CONTRACT_LOCAL_REPLAY_REQUIRED",
    Lookup[ancestry, "parent_commit", None] === "4a78ea05310126f720719e369a782466fdd1111e",
    Lookup[ancestry, "validated_closeout_source_head", None] ===
      "25dc6a75fc781d329dbe9a2b6d68eeb5f8a6607e",
    Lookup[ancestry, "expected_red_source_head", None] ===
      "21f5b08b704a90af19e617a372c994239e9046a2",
    Lookup[ancestry, "expected_red_gate", None] ===
      "PASS_EXPECTED_RED_12_FAILURES_0_ERRORS",
    counts === expectedCounts[],
    consumerCoreRows[consumers] === expectedConsumerCoreRows[],
    bindingCoreRows[bindings] === expectedBindingCoreRows[],
    DuplicateFreeQ[Lookup[#, "binding_id", None] & /@ bindings],
    DuplicateFreeQ[Lookup[#, "pair_id", None] & /@ bindings],
    Lookup[authority, "registry_semantic_hash", None] ===
      "5951f566d911c81848743055c1573f6d11b0b00937d36747b71e6bc12dd96416",
    formulaCoreRows[formulas] === expectedFormulaCoreRows[],
    roleCoreRows[roles] === expectedRoleCoreRows[],
    flattenedSymbols === expectedNamedSymbols[],
    Lookup[data, "named_source_symbols", {}] === expectedNamedSymbols[],
    DuplicateFreeQ[flattenedSymbols],
    KeyExistsQ[roleMap, "ROLE-REI-DIRECTION-FLOW-ABSENT"],
    Lookup[roleMap["ROLE-REI-DIRECTION-FLOW-ABSENT"], "role_type", None] ===
      "ABSENT_IMPLEMENTATION_SLOT",
    Lookup[roleMap["ROLE-REI-DIRECTION-FLOW-ABSENT"], "source_symbols", None] === {},
    Lookup[roleMap["ROLE-REI-DIRECTION-FLOW-ABSENT"], "implements_full_formula", None] === False,
    Lookup[roleMap["ROLE-HTT-BLACKBODY-FULL"], "role_type", None] === "FULL_FIELD_PULLBACK",
    Lookup[roleMap["ROLE-HTT-BLACKBODY-FULL"], "implements_full_formula", None] === True,
    Lookup[roleMap["ROLE-HTT-BLACKBODY-PREPULLED"], "role_type", None] ===
      "PREPULLED_VALUE_PRIMITIVE",
    Lookup[roleMap["ROLE-HTT-BLACKBODY-PREPULLED"], "implements_full_formula", None] === False,
    Lookup[statePolicy, "state_surfaces", {}] === expectedStateSurfaces[],
    Lookup[statePolicy, "primary_frequency_resolved_pair", {}] ===
      {"GRID_F_Q_E", "PSTF_F_AELL_Q"},
    Lookup[statePolicy, "j_and_g_generic_binding", None] ===
      "WITHHELD_REQUIRES_SPECTRAL_PROJECTION_CLOSURE_CERTIFICATE",
    Lookup[statePolicy, "scalar_to_polarized_binding", None] ===
      "FORBIDDEN_REQUIRES_POLARIZED_SCREEN_CERTIFICATE",
    Lookup[statePolicy, "certificate_schema_is_certificate_instance", None] === False,
    Lookup[statePolicy, "hardcoded_numeric_ell_cutoff_forbidden", None] === True,
    certificates === expectedCertificateFamilies[],
    ContainsAll[gateIDs, {
      "FORMULA_IDENTITY_GATE", "CONVENTION_DOMAIN_UNIT_GATE",
      "ANGULAR_REPRESENTATION_GATE", "SPECTRAL_PROJECTION_GATE",
      "MOMENT_EXCHANGE_GATE", "POLARIZED_SCREEN_GATE",
      "RESTRICTED_SUBSPACE_GATE", "ABSENT_IMPLEMENTATION_GATE"
    }],
    blocked === expectedBlockedPromotions[],
    DuplicateFreeQ[blocked],
    firewall === expectedAuthorizationFirewall[],
    Lookup[dag, "nodes", {}] === expectedDAGNodes[],
    Lookup[dag, "edges", {}] === expectedDAGEdges[],
    graphAcyclicQ[dag],
    Lookup[dag, "future_nodes_are_routing_declarations_not_pass_claims", None] === True,
    ListQ[literature] && Length[literature] >= 3 &&
      And @@ (Lookup[#, "authority_effect", None] === "NONE" & /@ literature),
    ListQ[parallel] && Length[parallel] === 1,
    Lookup[First[parallel], "classification", None] ===
      "PASS_BASS_REC_SOURCE_R6C_CLEAN_BACKEND_NONREGRESSION",
    Lookup[First[parallel], "runtime_parity_effect", None] === "NONE",
    Lookup[First[parallel], "remaining_trusted_gate", None] ===
      "PASS_R5D_TRUSTED_RF00_PAYLOAD_PROVENANCE_AND_BACKEND_GATE"
  ]
];

ClearAll[BASSConsumerBindingContractsR3Residuals];
BASSConsumerBindingContractsR3Residuals[data_Association] := Module[
  {counts, consumers, bindings, authority, formulas, roles, roleMap,
   statePolicy, certificates, blocked, firewall, dag, literature,
   parallel, flattenedSymbols},
  counts = Lookup[data, "count_contract", <||>];
  consumers = Lookup[data, "consumer_repositories", {}];
  bindings = Lookup[data, "binding_requests", {}];
  authority = Lookup[data, "formula_authority", <||>];
  formulas = Lookup[authority, "formulas", {}];
  roles = Lookup[data, "source_role_pins", {}];
  roleMap = Association[(Lookup[#, "role_id", ""] -> #) & /@ roles];
  statePolicy = Lookup[data, "state_surface_policy", <||>];
  certificates = Lookup[data, "certificate_families", {}];
  blocked = Lookup[data, "blocked_promotions", {}];
  firewall = Lookup[data, "authorization_firewall", <||>];
  dag = Lookup[data, "stage_dag", <||>];
  literature = Lookup[data, "literature_regression", {}];
  parallel = Lookup[data, "parallel_bass_runtime_evidence", {}];
  flattenedSymbols = Flatten[Lookup[#, "source_symbols", {}] & /@ roles];

  <|
    "consumer_count_residual" -> Length[consumers] - 3,
    "binding_request_count_residual" -> Length[bindings] - 10,
    "source_role_pin_count_residual" -> Length[roles] - 11,
    "named_source_symbol_count_residual" -> Length[flattenedSymbols] - 12,
    "absent_slot_count_residual" ->
      Count[Lookup[#, "role_type", None] & /@ roles, "ABSENT_IMPLEMENTATION_SLOT"] - 1,
    "formula_count_residual" -> Length[formulas] - 6,
    "state_surface_count_residual" ->
      Length[Lookup[statePolicy, "state_surfaces", {}]] - 6,
    "certificate_family_count_residual" -> Length[certificates] - 4,
    "blocked_promotion_count_residual" -> Length[blocked] - 13,
    "pair_coverage_exact" -> TrueQ[
      Lookup[#, "pair_id", None] & /@ bindings === expectedPairIDs[] &&
      bindingCoreRows[bindings] === expectedBindingCoreRows[]
    ],
    "formula_authority_exact" -> TrueQ[
      Lookup[authority, "registry_semantic_hash", None] ===
        "5951f566d911c81848743055c1573f6d11b0b00937d36747b71e6bc12dd96416" &&
      formulaCoreRows[formulas] === expectedFormulaCoreRows[]
    ],
    "source_role_pins_exact" -> TrueQ[
      roleCoreRows[roles] === expectedRoleCoreRows[] &&
      flattenedSymbols === expectedNamedSymbols[] &&
      Lookup[data, "named_source_symbols", {}] === expectedNamedSymbols[]
    ],
    "rei_absent_slot_intact" -> TrueQ[
      KeyExistsQ[roleMap, "ROLE-REI-DIRECTION-FLOW-ABSENT"] &&
      Lookup[roleMap["ROLE-REI-DIRECTION-FLOW-ABSENT"], "role_type", None] ===
        "ABSENT_IMPLEMENTATION_SLOT" &&
      Lookup[roleMap["ROLE-REI-DIRECTION-FLOW-ABSENT"], "source_symbols", None] === {} &&
      Lookup[roleMap["ROLE-REI-DIRECTION-FLOW-ABSENT"], "implements_full_formula", None] === False
    ],
    "htt_blackbody_roles_distinct" -> TrueQ[
      Lookup[roleMap["ROLE-HTT-BLACKBODY-FULL"], "role_type", None] ===
        "FULL_FIELD_PULLBACK" &&
      Lookup[roleMap["ROLE-HTT-BLACKBODY-FULL"], "implements_full_formula", None] === True &&
      Lookup[roleMap["ROLE-HTT-BLACKBODY-PREPULLED"], "role_type", None] ===
        "PREPULLED_VALUE_PRIMITIVE" &&
      Lookup[roleMap["ROLE-HTT-BLACKBODY-PREPULLED"], "implements_full_formula", None] === False
    ],
    "state_surface_firewall_intact" -> TrueQ[
      Lookup[statePolicy, "state_surfaces", {}] === expectedStateSurfaces[] &&
      Lookup[statePolicy, "primary_frequency_resolved_pair", {}] ===
        {"GRID_F_Q_E", "PSTF_F_AELL_Q"} &&
      Lookup[statePolicy, "j_and_g_generic_binding", None] ===
        "WITHHELD_REQUIRES_SPECTRAL_PROJECTION_CLOSURE_CERTIFICATE" &&
      Lookup[statePolicy, "scalar_to_polarized_binding", None] ===
        "FORBIDDEN_REQUIRES_POLARIZED_SCREEN_CERTIFICATE" &&
      Lookup[statePolicy, "certificate_schema_is_certificate_instance", None] === False
    ],
    "authorization_firewall_intact" -> TrueQ[
      firewall === expectedAuthorizationFirewall[] &&
      blocked === expectedBlockedPromotions[] && DuplicateFreeQ[blocked]
    ],
    "stage_dag_acyclic" -> TrueQ[
      Lookup[dag, "nodes", {}] === expectedDAGNodes[] &&
      Lookup[dag, "edges", {}] === expectedDAGEdges[] && graphAcyclicQ[dag]
    ],
    "literature_authority_none" -> TrueQ[
      ListQ[literature] && Length[literature] >= 3 &&
      And @@ (Lookup[#, "authority_effect", None] === "NONE" & /@ literature)
    ],
    "parallel_r6c_nonpromotional" -> TrueQ[
      ListQ[parallel] && Length[parallel] === 1 &&
      Lookup[First[parallel], "classification", None] ===
        "PASS_BASS_REC_SOURCE_R6C_CLEAN_BACKEND_NONREGRESSION" &&
      Lookup[First[parallel], "runtime_parity_effect", None] === "NONE" &&
      Lookup[First[parallel], "remaining_trusted_gate", None] ===
        "PASS_R5D_TRUSTED_RF00_PAYLOAD_PROVENANCE_AND_BACKEND_GATE"
    ]
  |>
];

End[];
EndPackage[];
