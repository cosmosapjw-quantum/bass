BeginPackage["BASS`IR`FormulaConsumerRoleGraphR2A`"];

BASSFormulaConsumerRoleGraphR2AQ::usage =
  "BASSFormulaConsumerRoleGraphR2AQ[data] validates the BASS-only 02F-R2A role graph.";
BASSFormulaConsumerRoleGraphR2AResiduals::usage =
  "BASSFormulaConsumerRoleGraphR2AResiduals[data] returns exact count and relation residuals.";

Begin["`Private`"];

ClearAll[pairKey, graphAcyclicQ];

pairKey[row_Association] := {
  Lookup[row, "formula_id", Missing["Formula"]],
  Lookup[row, "consumer_repository", Missing["Consumer"]]
};

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

ClearAll[BASSFormulaConsumerRoleGraphR2AQ];
BASSFormulaConsumerRoleGraphR2AQ[data_Association] := Module[
  {
    ancestry, convention, counts, formulas, pairs, roles, requiredFields,
    expectedFormulaHashes, expectedPairs, expectedSymbols, formulaIDs,
    pairIDs, roleIDs, observedPairs, namedSymbols, absent, blackbodyRoles,
    blackbodyTypes, primitive, reiEnergy, dag
  },

  ancestry = Lookup[data, "normal_ancestry", <||>];
  convention = Lookup[data, "convention_contract", <||>];
  counts = Lookup[data, "count_contract", <||>];
  formulas = Lookup[data, "authority_formulas", {}];
  pairs = Lookup[data, "formula_consumer_pairs", {}];
  roles = Lookup[data, "implementation_roles", {}];
  requiredFields = Lookup[data, "required_relation_fields", {}];
  dag = Lookup[data, "stage_dag", <||>];

  expectedFormulaHashes = <|
    "BASS.FRAME.ABERRATED_DIRECTION.001" ->
      "b20aa445f5e2890674480a6e8e71fd919aa9efd13a1a8c4780e98b67b9974eec",
    "BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001" ->
      "99ededbaa9c04ab51f2ffda4c19a55236b243021271445d3dad916e2e660c143",
    "BASS.FRAME.DOPPLER_FACTOR.001" ->
      "fb56218a0256edde59a1d89eb4e3ce69ce82800d852908ee84ce8aec83f2fb47",
    "BASS.FRAME.SOLID_ANGLE_JACOBIAN.001" ->
      "0436b513724b09fe826aa486c5dd3def19d0dc5e6daf9fabdd8d899fd1618dc4",
    "BASS.PHOTON.DIRECTION_FLOW.001" ->
      "1eb20b3b46b596139d781d529a1511df983c2b6c00fbe85208ef03e7888f08ce",
    "BASS.PHOTON.ENERGY_DRIFT.001" ->
      "840fe1d68d87b78bb5b5d831fb3d8025b26c29fda1f9da49b0f387e1a8d7bcfd"
  |>;

  expectedPairs = Sort[{
    {"BASS.FRAME.ABERRATED_DIRECTION.001", "rec_bianchi"},
    {"BASS.FRAME.DOPPLER_FACTOR.001", "rec_bianchi"},
    {"BASS.PHOTON.DIRECTION_FLOW.001", "rec_bianchi"},
    {"BASS.PHOTON.ENERGY_DRIFT.001", "rec_bianchi"},
    {"BASS.PHOTON.DIRECTION_FLOW.001", "rei_bianchi"},
    {"BASS.PHOTON.ENERGY_DRIFT.001", "rei_bianchi"},
    {"BASS.FRAME.ABERRATED_DIRECTION.001", "htt_base"},
    {"BASS.FRAME.DOPPLER_FACTOR.001", "htt_base"},
    {"BASS.FRAME.SOLID_ANGLE_JACOBIAN.001", "htt_base"},
    {"BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001", "htt_base"}
  }];

  expectedSymbols = Sort[{
    "aberrate_direction",
    "doppler_factor",
    "normal_frame_characteristic.D0_direction_normal_s_inv",
    "normal_frame_characteristic.R_normal_s_inv",
    "SpectrumLane.redshift_coeff",
    "aberrate_sky_direction",
    "deaberrate_sky_direction",
    "doppler_factor_unboosted",
    "doppler_factor_boosted",
    "solid_angle_jacobian",
    "pullback_thermodynamic_temperature_field",
    "thermodynamic_temperature_pullback"
  }];

  formulaIDs = Lookup[#, "formula_id", Missing["ID"]] & /@ formulas;
  pairIDs = Lookup[#, "pair_id", Missing["ID"]] & /@ pairs;
  roleIDs = Lookup[#, "role_id", Missing["ID"]] & /@ roles;
  observedPairs = Sort[pairKey /@ pairs];
  namedSymbols = Flatten[Lookup[#, "source_symbols", {}] & /@ roles];
  absent = Select[roles,
    Lookup[#, "role_type", ""] === "ABSENT_IMPLEMENTATION_SLOT" &
  ];
  blackbodyRoles = Select[roles,
    Lookup[#, "pair_id", ""] === "02F-R2A-HTT-BLACKBODY-T" &
  ];
  blackbodyTypes = Sort[Lookup[#, "role_type", ""] & /@ blackbodyRoles];
  primitive = SelectFirst[blackbodyRoles,
    Lookup[#, "role_type", ""] === "PREPULLED_VALUE_PRIMITIVE" &,
    <||>
  ];
  reiEnergy = SelectFirst[pairs,
    Lookup[#, "pair_id", ""] === "02F-R2A-REI-ENERGY-DRIFT" &,
    <||>
  ];

  And[
    Lookup[data, "repository_scope", None] === "BASS_ONLY",
    Lookup[data, "owner", None] === "bass",
    !KeyExistsQ[data, "consumer_bindings"],
    !KeyExistsQ[data, "relation_class_vocabulary"],

    Lookup[ancestry, "parent_commit", None] ===
      "6bb65476a87d1ac8daa9f7239d884c369c51ce33",
    Lookup[ancestry, "state_surface_registry_sha256", None] ===
      "5a5042d4b4cd653b3455dda45f9cd5aa67314cb03416b532ff34dbc9695f621c",
    Lookup[ancestry, "hardened_formula_registry_semantic_hash", None] ===
      "5951f566d911c81848743055c1573f6d11b0b00937d36747b71e6bc12dd96416",

    Lookup[convention, "ray_length_parameter", None] === "s=c*t with dimension L",
    Lookup[convention, "angular_multipole_rank", None] === "ell",

    Lookup[counts, "formula_consumer_pairs", None] === 10,
    Lookup[counts, "implementation_role_rows", None] === 11,
    Lookup[counts, "named_source_symbols", None] === 12,
    Lookup[counts, "explicit_absent_implementation_slots", None] === 1,

    Length[formulas] === 6,
    Length[DeleteDuplicates[formulaIDs]] === 6,
    Sort[formulaIDs] === Sort[Keys[expectedFormulaHashes]],
    And @@ (
      Lookup[#, "semantic_hash", None] ===
        Lookup[expectedFormulaHashes, Lookup[#, "formula_id", ""], None] &
      /@ formulas
    ),

    Length[pairs] === 10,
    Length[DeleteDuplicates[pairIDs]] === 10,
    observedPairs === expectedPairs,
    And @@ (
      And @@ (KeyExistsQ[#, #2] & @@@ Thread[{ConstantArray[#, Length[requiredFields]], requiredFields}]) &
      /@ pairs
    ),
    And @@ (!KeyExistsQ[#, "relation_class"] & /@ pairs),

    Length[roles] === 11,
    Length[DeleteDuplicates[roleIDs]] === 11,
    And @@ (MemberQ[pairIDs, Lookup[#, "pair_id", None]] & /@ roles),
    Length[namedSymbols] === 12,
    Sort[namedSymbols] === expectedSymbols,
    Length[DeleteDuplicates[namedSymbols]] === 12,

    Length[absent] === 1,
    Lookup[First[absent], "pair_id", None] === "02F-R2A-REI-DIRECTION-FLOW",
    Lookup[First[absent], "source_symbols", None] === {},
    Lookup[First[absent], "implements_full_formula", None] === False,

    Length[blackbodyRoles] === 2,
    blackbodyTypes === Sort[{"FULL_FIELD_PULLBACK", "PREPULLED_VALUE_PRIMITIVE"}],
    Lookup[primitive, "implements_full_formula", None] === False,
    AnyTrue[
      Lookup[primitive, "preconditions", {}],
      StringContainsQ[#, "inverse-aberrated"] &
    ],

    Lookup[reiEnergy, "exact_relation_residual", None] ===
      "Expand(((-H)-(-H-sigmaEE))-sigmaEE)=0",
    Lookup[reiEnergy, "parity_status", None] ===
      "GENERIC_PARITY_FORBIDDEN_CONTROL_SUBSPACE_ONLY",

    graphAcyclicQ[dag],
    MemberQ[
      Lookup[dag, "edges", {}],
      {"BASS_STATE_SURFACE_REGISTRY", "FORMULA_CONSUMER_ROLE_GRAPH"}
    ]
  ]
];

ClearAll[BASSFormulaConsumerRoleGraphR2AResiduals];
BASSFormulaConsumerRoleGraphR2AResiduals[data_Association] := Module[
  {pairs, roles, symbols, absent, blackbody, dag, h, sigmaEE, reiDelta},
  pairs = Lookup[data, "formula_consumer_pairs", {}];
  roles = Lookup[data, "implementation_roles", {}];
  symbols = Flatten[Lookup[#, "source_symbols", {}] & /@ roles];
  absent = Count[
    Lookup[#, "role_type", ""] & /@ roles,
    "ABSENT_IMPLEMENTATION_SLOT"
  ];
  blackbody = Count[
    Lookup[#, "pair_id", ""] & /@ roles,
    "02F-R2A-HTT-BLACKBODY-T"
  ];
  dag = Lookup[data, "stage_dag", <||>];
  reiDelta = Expand[(-h) - (-h - sigmaEE)];
  <|
    "pair_count_residual" -> Length[pairs] - 10,
    "pair_uniqueness_residual" -> Length[pairs] - Length[DeleteDuplicates[pairKey /@ pairs]],
    "role_count_residual" -> Length[roles] - 11,
    "named_symbol_count_residual" -> Length[symbols] - 12,
    "absent_slot_count_residual" -> absent - 1,
    "htt_blackbody_role_count_residual" -> blackbody - 2,
    "rei_energy_exact_residual" -> Expand[reiDelta - sigmaEE],
    "rei_wrong_sign_mutant_residual" -> Expand[(-h) - (-h + sigmaEE) - sigmaEE],
    "stage_dag_acyclic" -> graphAcyclicQ[dag]
  |>
];

End[];
EndPackage[];
