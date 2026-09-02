(* ::Package:: *)

BeginPackage["BASS`IR`HTTRelationClassification`"];

HTTLorentzRelationChecks::usage =
  "HTTLorentzRelationChecks[] returns exact local-observer boost residuals and hostile-mutation checks.";
HTTFederationDAGChecks::usage =
  "HTTFederationDAGChecks[] verifies the non-colliding 02C/02D/02E/02F federation projection.";
HTTRelationClassificationReport::usage =
  "HTTRelationClassificationReport[] returns the combined SYNC-MAP-02D exact report.";

Begin["`Private`"];

HTTLorentzRelationChecks[] := Module[
  {
    b2, mu, x, q, gamma, a, d, muT, invC, invDen,
    betaN, qnn, qbetaN, residuals, mutations,
    wrongDopplerSign, wrongJacobianPower, omittedDipole, omittedOctupole
  },
  gamma = 1/Sqrt[1 - b2];
  a = gamma + (gamma - 1) mu/b2;
  d = gamma (1 + mu);
  muT = FullSimplify[
    (mu + a b2)/d,
    Assumptions -> 0 < b2 < 1 && -Sqrt[b2] <= mu <= Sqrt[b2]
  ];
  invC = (gamma - 1) muT/b2 - gamma;
  invDen = gamma (1 - muT);

  residuals = <|
    "aberrated_direction_unit_norm" -> FullSimplify[
      (1 + 2 a mu + a^2 b2)/d^2 - 1,
      Assumptions -> 0 < b2 < 1 && -Sqrt[b2] <= mu <= Sqrt[b2]
    ],
    "doppler_chart_equivalence" -> FullSimplify[
      1/(gamma (1 - muT)) - d,
      Assumptions -> 0 < b2 < 1 && -Sqrt[b2] <= mu <= Sqrt[b2]
    ],
    "deaberration_inverse_n_coefficient" -> FullSimplify[
      (1/d)/invDen - 1,
      Assumptions -> 0 < b2 < 1 && -Sqrt[b2] <= mu <= Sqrt[b2]
    ],
    "deaberration_inverse_beta_coefficient" -> FullSimplify[
      (a/d + invC)/invDen,
      Assumptions -> 0 < b2 < 1 && -Sqrt[b2] <= mu <= Sqrt[b2]
    ],
    "solid_angle_jacobian" -> FullSimplify[
      D[(x + q)/(1 + q x), x] - (Sqrt[1 - q^2]/(1 + q x))^2,
      Assumptions -> -1 < q < 1 && -1 <= x <= 1
    ],
    "quadrupole_l1_l3_decomposition" -> FullSimplify[
      (3 betaN qnn - 2 qbetaN) -
        ((3 betaN qnn - (6/5) qbetaN) - (4/5) qbetaN)
    ]
  |>;

  wrongDopplerSign = FullSimplify[
    1/(gamma (1 + muT)) - d,
    Assumptions -> 0 < b2 < 1 && -Sqrt[b2] < mu < Sqrt[b2]
  ];
  wrongJacobianPower = FullSimplify[
    D[(x + q)/(1 + q x), x] - Sqrt[1 - q^2]/(1 + q x),
    Assumptions -> -1 < q < 1 && -1 < x < 1
  ];
  omittedDipole = FullSimplify[
    (3 betaN qnn - 2 qbetaN) - (3 betaN qnn - (6/5) qbetaN)
  ];
  omittedOctupole = FullSimplify[
    (3 betaN qnn - 2 qbetaN) - (-(4/5) qbetaN)
  ];
  mutations = <|
    "wrong_doppler_sign_detected" -> Not[TrueQ[wrongDopplerSign == 0]],
    "wrong_jacobian_power_detected" -> Not[TrueQ[wrongJacobianPower == 0]],
    "omitted_dipole_detected" -> Not[TrueQ[omittedDipole == 0]],
    "omitted_octupole_detected" -> Not[TrueQ[omittedOctupole == 0]]
  |>;

  <|
    "residuals" -> residuals,
    "mutations" -> mutations,
    "status" -> If[
      And @@ (TrueQ[# == 0] & /@ Values[residuals]) &&
      And @@ (TrueQ /@ Values[mutations]),
      "PASS",
      "FAIL"
    ]
  |>
];

HTTFederationDAGChecks[] := Module[
  {nodes, edges, graph, checks, badEdges},
  nodes = {
    "02A_BASS", "02B_REC", "02C_REI", "02D_HTT",
    "02E_SHARED_EXPORT", "02F_SEMANTIC_GRAPH",
    "SYNC_REC", "SYNC_REI", "SYNC_HTT_01A", "SYNC_GATE_01"
  };
  edges = {
    {"02A_BASS", "02B_REC"},
    {"02B_REC", "02C_REI"},
    {"02B_REC", "02D_HTT"},
    {"02C_REI", "02E_SHARED_EXPORT"},
    {"02D_HTT", "02E_SHARED_EXPORT"},
    {"02E_SHARED_EXPORT", "02F_SEMANTIC_GRAPH"},
    {"02F_SEMANTIC_GRAPH", "SYNC_REC"},
    {"02F_SEMANTIC_GRAPH", "SYNC_REI"},
    {"02F_SEMANTIC_GRAPH", "SYNC_HTT_01A"},
    {"SYNC_REC", "SYNC_GATE_01"},
    {"SYNC_REI", "SYNC_GATE_01"},
    {"SYNC_HTT_01A", "SYNC_GATE_01"}
  };
  graph = Graph[nodes, DirectedEdge @@@ edges];
  badEdges = DeleteCases[edges, {"02D_HTT", "02E_SHARED_EXPORT"}];
  checks = <|
    "unique_nodes" -> DuplicateFreeQ[nodes],
    "edge_closure" -> And @@ (MemberQ[nodes, #] & /@ Union[Flatten[edges]]),
    "acyclic" -> AcyclicGraphQ[graph],
    "topological_coverage" -> (Length[TopologicalSort[graph]] == Length[nodes]),
    "shared_export_has_rei_and_htt_prerequisites" -> And[
      MemberQ[edges, {"02C_REI", "02E_SHARED_EXPORT"}],
      MemberQ[edges, {"02D_HTT", "02E_SHARED_EXPORT"}]
    ],
    "semantic_graph_follows_shared_export" ->
      MemberQ[edges, {"02E_SHARED_EXPORT", "02F_SEMANTIC_GRAPH"}],
    "manual_gate_has_three_sync_inputs" ->
      (Count[edges, {_, "SYNC_GATE_01"}] == 3),
    "missing_02d_dependency_mutation_detected" ->
      Not[MemberQ[badEdges, {"02D_HTT", "02E_SHARED_EXPORT"}]],
    "missing_dependency_mutant_remains_acyclic" ->
      AcyclicGraphQ[Graph[nodes, DirectedEdge @@@ badEdges]]
  |>;
  <|
    "nodes" -> nodes,
    "edges" -> edges,
    "node_count" -> Length[nodes],
    "edge_count" -> Length[edges],
    "topological_order" -> TopologicalSort[graph],
    "checks" -> checks,
    "status" -> If[And @@ (TrueQ /@ Values[checks]), "PASS", "FAIL"]
  |>
];

HTTRelationClassificationReport[] := Module[{lorentz, dag},
  lorentz = HTTLorentzRelationChecks[];
  dag = HTTFederationDAGChecks[];
  <|
    "stage_id" -> "SYNC_MAP_02D_HTT_RELATION_CLASSIFICATION",
    "lorentz" -> lorentz,
    "dag" -> dag,
    "status" -> If[
      lorentz["status"] === "PASS" && dag["status"] === "PASS",
      "PASS",
      "FAIL"
    ],
    "claim_boundary" ->
      "RELATION_CLASSIFICATION_ONLY_NO_SHARED_EXPORT_GLOBAL_TILT_DATA_FIT_PROVIDER_OR_SCIENCE_PROMOTION"
  |>
];

End[];
EndPackage[];
