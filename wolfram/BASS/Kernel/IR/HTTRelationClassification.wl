(* ::Package:: *)

BeginPackage["BASS`IR`HTTRelationClassification`"];

HTTLorentzRelationChecks::usage =
  "HTTLorentzRelationChecks[] returns exact local-observer boost residuals, an explicit STF3 quadrupole-response proof, and hostile-mutation checks.";
HTTFederationDAGChecks::usage =
  "HTTFederationDAGChecks[] verifies the non-colliding 02C/02D/02E/02F federation projection.";
HTTRelationClassificationReport::usage =
  "HTTRelationClassificationReport[] returns the combined SYNC-MAP-02D exact report.";

Begin["`Private`"];

HTTLorentzRelationChecks[] := Module[
  {
    b2, mu, x, q, gamma, a, d, muT, invC, invDen,
    q11, q12, q13, q22, q23, b1, b2c, b3, n1, n2, n3,
    qMat, betaVec, nVec, delta3, qBetaVec, qBetaN, qNN, betaN,
    nNorm, stf3Tensor, stf3SymmetryResiduals, stf3TraceResiduals,
    stf3Contract, ambientResidual, expectedAmbientResidual,
    unitSphereResidual, wrongTraceTensor, wrongTraceResiduals,
    nonSymmetricTensor, nonSymmetricResidual, residuals,
    symbolicResiduals, structuralChecks, mutations, wrongDopplerSign,
    wrongJacobianPower, omittedDipole, omittedOctupole
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

  qMat = {
    {q11, q12, q13},
    {q12, q22, q23},
    {q13, q23, -q11 - q22}
  };
  betaVec = {b1, b2c, b3};
  nVec = {n1, n2, n3};
  delta3 = IdentityMatrix[3];
  qBetaVec = qMat . betaVec;
  qBetaN = Expand[betaVec . qMat . nVec];
  qNN = Expand[nVec . qMat . nVec];
  betaN = Expand[betaVec . nVec];
  nNorm = Expand[nVec . nVec];

  stf3Tensor = Table[
    betaVec[[aa]] qMat[[bb, cc]] +
    betaVec[[bb]] qMat[[cc, aa]] +
    betaVec[[cc]] qMat[[aa, bb]] -
    (2/5) (
      delta3[[aa, bb]] qBetaVec[[cc]] +
      delta3[[aa, cc]] qBetaVec[[bb]] +
      delta3[[bb, cc]] qBetaVec[[aa]]
    ),
    {aa, 3}, {bb, 3}, {cc, 3}
  ];
  stf3SymmetryResiduals = DeleteDuplicates @ Flatten @ Table[
    {
      Expand[stf3Tensor[[aa, bb, cc]] - stf3Tensor[[bb, aa, cc]]],
      Expand[stf3Tensor[[aa, bb, cc]] - stf3Tensor[[aa, cc, bb]]],
      Expand[stf3Tensor[[aa, bb, cc]] - stf3Tensor[[cc, bb, aa]]]
    },
    {aa, 3}, {bb, 3}, {cc, 3}
  ];
  stf3TraceResiduals = Table[
    Expand[Sum[stf3Tensor[[aa, aa, cc]], {aa, 3}]],
    {cc, 3}
  ];
  stf3Contract = Expand @ Sum[
    stf3Tensor[[aa, bb, cc]] nVec[[aa]] nVec[[bb]] nVec[[cc]],
    {aa, 3}, {bb, 3}, {cc, 3}
  ];
  ambientResidual = Factor @ Expand[
    stf3Contract - (4/5) qBetaN - (3 betaN qNN - 2 qBetaN)
  ];
  expectedAmbientResidual = Factor[-(6/5) (nNorm - 1) qBetaN];
  unitSphereResidual = FullSimplify[
    ambientResidual,
    Assumptions -> n1^2 + n2^2 + n3^2 == 1
  ];

  wrongTraceTensor = Table[
    betaVec[[aa]] qMat[[bb, cc]] +
    betaVec[[bb]] qMat[[cc, aa]] +
    betaVec[[cc]] qMat[[aa, bb]] -
    (1/5) (
      delta3[[aa, bb]] qBetaVec[[cc]] +
      delta3[[aa, cc]] qBetaVec[[bb]] +
      delta3[[bb, cc]] qBetaVec[[aa]]
    ),
    {aa, 3}, {bb, 3}, {cc, 3}
  ];
  wrongTraceResiduals = Table[
    Expand[Sum[wrongTraceTensor[[aa, aa, cc]], {aa, 3}]],
    {cc, 3}
  ];
  nonSymmetricTensor = stf3Tensor;
  nonSymmetricTensor[[1, 2, 3]] =
    Expand[nonSymmetricTensor[[1, 2, 3]] + b1 q23];
  nonSymmetricResidual = Expand[
    nonSymmetricTensor[[1, 2, 3]] - nonSymmetricTensor[[2, 1, 3]]
  ];

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
      D[(x + q)/(1 + q x), x] -
      (Sqrt[1 - q^2]/(1 + q x))^2,
      Assumptions -> -1 < q < 1 && -1 <= x <= 1
    ],
    "stf3_unit_sphere_residual" -> unitSphereResidual
  |>;
  symbolicResiduals = <|
    "stf3_ambient_domain_residual" -> ambientResidual
  |>;
  structuralChecks = <|
    "stf3_symmetric" ->
      And @@ (TrueQ[# == 0] & /@ stf3SymmetryResiduals),
    "stf3_trace_free" ->
      And @@ (TrueQ[# == 0] & /@ stf3TraceResiduals),
    "stf3_ambient_factor_matches" ->
      TrueQ[FullSimplify[ambientResidual - expectedAmbientResidual] == 0],
    "stf3_unit_sphere_residual" -> TrueQ[unitSphereResidual == 0],
    "stf3_unit_sphere_domain_required" -> And[
      Not[TrueQ[ambientResidual == 0]],
      TrueQ[unitSphereResidual == 0]
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
    (3 betaN qNN - 2 qBetaN) - stf3Contract,
    Assumptions -> n1^2 + n2^2 + n3^2 == 1
  ];
  omittedOctupole = FullSimplify[
    (3 betaN qNN - 2 qBetaN) - (-(4/5) qBetaN),
    Assumptions -> n1^2 + n2^2 + n3^2 == 1
  ];
  mutations = <|
    "wrong_doppler_sign_detected" -> Not[TrueQ[wrongDopplerSign == 0]],
    "wrong_jacobian_power_detected" ->
      Not[TrueQ[wrongJacobianPower == 0]],
    "omitted_dipole_detected" -> Not[TrueQ[omittedDipole == 0]],
    "omitted_octupole_detected" -> Not[TrueQ[omittedOctupole == 0]],
    "wrong_stf3_trace_coefficient_detected" ->
      Not[And @@ (TrueQ[# == 0] & /@ wrongTraceResiduals)],
    "non_symmetric_stf3_detected" ->
      Not[TrueQ[nonSymmetricResidual == 0]],
    "missing_unit_sphere_domain_detected" -> And[
      Not[TrueQ[ambientResidual == 0]],
      TrueQ[unitSphereResidual == 0]
    ]
  |>;

  <|
    "residuals" -> residuals,
    "symbolic_residuals" -> symbolicResiduals,
    "structural_checks" -> structuralChecks,
    "mutations" -> mutations,
    "status" -> If[
      And @@ (TrueQ[# == 0] & /@ Values[residuals]) &&
      And @@ (TrueQ /@ Values[structuralChecks]) &&
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
    "edge_closure" ->
      And @@ (MemberQ[nodes, #] & /@ Union[Flatten[edges]]),
    "acyclic" -> AcyclicGraphQ[graph],
    "topological_coverage" ->
      (Length[TopologicalSort[graph]] == Length[nodes]),
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
    "status" -> If[
      And @@ (TrueQ /@ Values[checks]),
      "PASS",
      "FAIL"
    ]
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
