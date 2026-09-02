ClearAll[FED00R1Verify, fedDagSummary, fedAssociationRules];

fedAssociationRules[associations_List, key_String] :=
  Lookup[associations, key, Missing["KeyAbsent", key]];

fedDagSummary[vertices_List, edges_List] := Module[
  {graph, order, distances = <||>, predecessors, roots, sinks},
  graph = Graph[vertices, DirectedEdge @@@ edges];
  order = TopologicalSort[graph];
  predecessors[vertex_] :=
    Cases[edges, {source_, target_} /; target === vertex :> source];
  Do[
    AssociateTo[
      distances,
      vertex -> If[
        predecessors[vertex] === {},
        0,
        1 + Max[Lookup[distances, predecessors[vertex]]]
      ]
    ],
    {vertex, order}
  ];
  roots = Select[vertices, VertexInDegree[graph, #] == 0 &];
  sinks = Select[vertices, VertexOutDegree[graph, #] == 0 &];
  <|
    "family_count" -> Length[vertices],
    "edge_count" -> Length[edges],
    "unique_family_ids" -> DuplicateFreeQ[vertices],
    "edges_closed_over_families" ->
      SubsetQ[vertices, Union[Flatten[edges]]],
    "acyclic" -> AcyclicGraphQ[graph],
    "topological_order_count" -> Length[order],
    "roots" -> Sort[roots],
    "sinks" -> Sort[sinks],
    "longest_path_edges" -> Max[Values[distances]]
  |>
];

FED00R1Verify[proposal_Association] := Module[
  {
    families, ids, explicitEdges, prerequisiteEdges, owners,
    expected, summary, familyById, checks, canonicalPayload
  },
  families = Lookup[proposal, "families", {}];
  ids = Lookup[families, "id", Missing["NoId"]];
  explicitEdges =
    ({Lookup[#, "from"], Lookup[#, "to"]} &) /@
      Lookup[proposal, "edges", {}];
  prerequisiteEdges = Sort@Flatten[
    Table[
      ({#, Lookup[family, "id"]} &) /@
        Lookup[family, "prerequisites", {}],
      {family, families}
    ],
    1
  ];
  owners = Counts[Lookup[families, "owner", Missing["NoOwner"]]];
  expected = Lookup[proposal, "wolfram_expected", <||>];
  summary = fedDagSummary[ids, explicitEdges];
  familyById = AssociationThread[ids, families];

  checks = <|
    "association_input" -> AssociationQ[proposal],
    "proposal_status" ->
      Lookup[proposal, "status", None] ===
        "PROPOSAL_ONLY_WOLFRAM_ACYCLIC_VERIFIED",
    "family_count" ->
      summary["family_count"] === Lookup[expected, "family_count"],
    "edge_count" ->
      summary["edge_count"] === Lookup[expected, "edge_count"],
    "unique_family_ids" -> TrueQ[summary["unique_family_ids"]],
    "edges_closed" -> TrueQ[summary["edges_closed_over_families"]],
    "acyclic" -> TrueQ[summary["acyclic"]],
    "topological_coverage" ->
      summary["topological_order_count"] === Length[ids],
    "single_root" ->
      summary["roots"] === {Lookup[expected, "root"]},
    "single_sink" ->
      summary["sinks"] === {Lookup[expected, "sink"]},
    "longest_path" ->
      summary["longest_path_edges"] ===
        Lookup[expected, "longest_path_edges"],
    "owner_counts" ->
      owners === Lookup[expected, "owner_counts"],
    "allowed_owners" ->
      SubsetQ[
        {"bass", "rec_bianchi", "rei_bianchi"},
        Keys[owners]
      ],
    "prerequisite_edge_equivalence" ->
      Sort[explicitEdges] === prerequisiteEdges,
    "connection_curvature_split" ->
      KeyExistsQ[familyById, "GEOM.LEVI_CIVITA_CONNECTION"] &&
      KeyExistsQ[familyById, "GEOM.SPATIAL_CURVATURE"],
    "finite_tilt_not_bg_blocked" ->
      FreeQ[
        Lookup[
          familyById["COLL.THOMSON_FINITE_TILT"],
          "prerequisites",
          {}
        ],
        "GEOM.GR_EINSTEIN_PROJECTIONS" | "GEOM.GR_BACKGROUND"
      ],
    "local_boost_output_owner_split" ->
      Lookup[familyById["OBS.LOCAL_BOOST"], "owner"] === "bass" &&
      Lookup[familyById["OBS.LOCAL_BOOST"], "execution_owner"] ===
        "htt_base",
    "rec_kernel_adapter_split" ->
      KeyExistsQ[familyById, "REC.DIRECTIONAL_SOURCE_KERNEL"] &&
      KeyExistsQ[familyById, "REC.BIANCHI_FACE_ADAPTER"],
    "rei_provider_adapter_split" ->
      KeyExistsQ[familyById, "REI.PROVIDER_EXPORT"] &&
      KeyExistsQ[familyById, "REI.BIANCHI_BACKGROUND_ADAPTER"],
    "splice_coupling_split" ->
      KeyExistsQ[familyById, "INT.REC_REI_HISTORY_SPLICE"] &&
      KeyExistsQ[familyById, "INT.BASS_COUPLED_HISTORY"],
    "manual_claim_boundary" ->
      StringContainsQ[
        Lookup[proposal, "claim_boundary", ""],
        "NO_OFFICIAL_DAG_MUTATION"
      ] &&
      StringContainsQ[
        Lookup[proposal, "claim_boundary", ""],
        "NO_SCIENCE_PROMOTION"
      ]
  |>;

  canonicalPayload = <|
    "proposal_id" -> Lookup[proposal, "proposal_id"],
    "summary" -> summary,
    "owner_counts" -> owners,
    "checks" -> checks
  |>;

  <|
    "status" -> If[And @@ Values[checks], "PASS", "FAIL"],
    "proposal_id" -> Lookup[proposal, "proposal_id"],
    "summary" -> summary,
    "owner_counts" -> owners,
    "checks" -> checks,
    "failed_checks" -> Keys@Select[checks, Not@TrueQ[#] &],
    "canonical_sha256" ->
      Hash[
        ExportString[canonicalPayload, "RawJSON", "Compact" -> True],
        "SHA256",
        "HexString"
      ],
    "wolfram_version" -> $Version,
    "system_id" -> $SystemID,
    "xact_required" -> False,
    "claim_boundary" ->
      "GRAPH_AND_OWNERSHIP_PROPOSAL_ONLY_NO_FORMULA_OR_SCIENCE_PROMOTION"
  |>
];

FED00R1Verify[url_String] := Module[{proposal},
  proposal = Quiet@Check[Import[url, "RawJSON"], $Failed];
  If[
    AssociationQ[proposal],
    FED00R1Verify[proposal],
    <|
      "status" -> "FAIL",
      "reason" -> "PROPOSAL_IMPORT_FAILED",
      "url" -> url
    |>
  ]
];

If[
  ValueQ[$FED00R1ProposalURL],
  FED00R1Verify[$FED00R1ProposalURL],
  <|
    "status" -> "NOT_RUN",
    "reason" -> "SET_$FED00R1ProposalURL_BEFORE_GET"
  |>
]
