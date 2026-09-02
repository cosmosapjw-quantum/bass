ClearAll[
  SYNCMap01R1Verify, nonEmptyListQ, gitPathIdentityQ,
  familyRecordQ, sourceClassCounts
];

nonEmptyListQ[value_] := ListQ[value] && Length[value] > 0;

gitPathIdentityQ[path_Association] := And[
  StringQ[Lookup[path, "path", None]],
  StringLength[Lookup[path, "path", ""]] > 0,
  MatchQ[
    Lookup[path, "blob_sha", None],
    _String?(StringMatchQ[#, RegularExpression["[0-9a-f]{40}"]] &)
  ]
];
gitPathIdentityQ[___] := False;

familyRecordQ[record_Association] := And[
  StringQ[Lookup[record, "family_id", None]],
  Lookup[record, "owner", None] === "bass",
  StringQ[Lookup[record, "source_class", None]],
  StringQ[Lookup[record, "authority_effect", None]],
  StringQ[Lookup[record, "source_status", None]],
  ListQ[Lookup[record, "prerequisites", None]],
  ListQ[Lookup[record, "consumers", None]],
  AssociationQ[Lookup[record, "physical_contract", None]],
  KeyExistsQ[record, "implemented"],
  BooleanQ[Lookup[record, "implemented"]],
  MemberQ[
    {"PENDING_SYNC_MAP_02", "HELD_SIBLING_COMPOSITION", "NOT_APPLICABLE_NOT_IMPLEMENTED"},
    Lookup[record, "semantic_status", None]
  ]
];
familyRecordQ[___] := False;

sourceClassCounts[records_List] := Counts[(Lookup[#, "source_class", Missing["source_class"]] &) /@ records];

SYNCMap01R1Verify[sourceMap_Association] := Module[
  {
    records, ids, owners, byId, expectedIds, expectedCounts, actualCounts,
    gitBound, canonicalGitBound, evidenceBearing, externalRecords,
    redRecords, absentRecords, siblingRecords, checks, canonicalPayload
  },

  expectedIds = {
    "CONV.CORE",
    "FRAME.LORENTZ_SCREEN",
    "GEOM.BIANCHI_ALGEBRA",
    "GEOM.LEVI_CIVITA_CONNECTION",
    "GEOM.SPATIAL_CURVATURE",
    "GEOM.GR_EINSTEIN_PROJECTIONS",
    "GEOM.STRUCTURE_EVOLUTION",
    "KIN.HOMOGENEOUS_PHOTON_CORE",
    "COLL.THOMSON_REST",
    "COLL.THOMSON_FINITE_TILT",
    "NUM.ARBITRARY_L_COMPILER",
    "OBS.LOCAL_BOOST",
    "INT.REC_REI_HISTORY_SPLICE",
    "INT.BASS_COUPLED_HISTORY",
    "INT.HTT_BACKGROUND_EXPORT"
  };

  expectedCounts = <|
    "GIT_DURABLE" -> 3,
    "GIT_FORMULA_ONLY" -> 2,
    "GIT_SIBLING_HELD" -> 1,
    "EXTERNAL_SNAPSHOT_ONLY" -> 2,
    "RED_ONLY" -> 1,
    "NOT_STARTED_OR_BLOCKED" -> 6
  |>;

  records = Lookup[sourceMap, "families", {}];
  If[!ListQ[records], Return[<|"status" -> "FAIL", "reason" -> "FAMILIES_NOT_A_LIST"|>]];
  ids = (Lookup[#, "family_id", Missing["family_id"]] &) /@ records;
  owners = (Lookup[#, "owner", Missing["owner"]] &) /@ records;
  byId = If[records =!= {} && DuplicateFreeQ[ids], AssociationThread[ids, records], <||>];
  actualCounts = sourceClassCounts[records];

  gitBound = Select[records,
    MemberQ[{"GIT_DURABLE", "GIT_FORMULA_ONLY", "GIT_SIBLING_HELD"}, Lookup[#, "source_class", None]] &];
  canonicalGitBound = Select[records,
    MemberQ[{"GIT_DURABLE", "GIT_FORMULA_ONLY"}, Lookup[#, "source_class", None]] &];
  evidenceBearing = Select[records,
    MemberQ[{"GIT_DURABLE", "GIT_FORMULA_ONLY", "GIT_SIBLING_HELD", "EXTERNAL_SNAPSHOT_ONLY", "RED_ONLY"},
      Lookup[#, "source_class", None]] &];
  externalRecords = Select[records, Lookup[#, "source_class", None] === "EXTERNAL_SNAPSHOT_ONLY" &];
  redRecords = Select[records, Lookup[#, "source_class", None] === "RED_ONLY" &];
  absentRecords = Select[records, Lookup[#, "source_class", None] === "NOT_STARTED_OR_BLOCKED" &];
  siblingRecords = Select[records, Lookup[#, "source_class", None] === "GIT_SIBLING_HELD" &];

  checks = <|
    "association_input" -> AssociationQ[sourceMap],
    "stage_id" -> Lookup[sourceMap, "stage_id", None] === "SYNC-MAP-01R1",
    "proposal_parent_pinned" -> And[
      Lookup[Lookup[sourceMap, "control_parent", <||>], "commit", None] ===
        "336a91ad22a5489b270043a12663375ff4158558",
      Lookup[Lookup[sourceMap, "control_parent", <||>], "pull_request", None] === 90
    ],
    "fifteen_records" -> Length[records] === 15,
    "all_expected_ids_once" -> Sort[ids] === Sort[expectedIds] && DuplicateFreeQ[ids],
    "all_records_well_formed" -> And @@ (familyRecordQ /@ records),
    "all_owned_by_bass" -> Sort[DeleteDuplicates[owners]] === {"bass"},
    "source_class_counts" -> KeySort[actualCounts] === KeySort[expectedCounts],
    "six_git_bound" -> Length[gitBound] === 6,
    "five_canonical_git_bound" -> Length[canonicalGitBound] === 5,
    "nine_evidence_bearing" -> Length[evidenceBearing] === 9,
    "git_lineages_present" -> And @@ (nonEmptyListQ[Lookup[#, "source_lineages", {}]] & /@ gitBound),
    "git_paths_exact_pinned" -> And @@ Flatten[(gitPathIdentityQ /@ Lookup[#, "source_paths", {}]) & /@ gitBound],
    "external_snapshots_not_mislabelled_git" -> And @@ (
      (nonEmptyListQ[Lookup[#, "external_snapshots", {}]] &&
       Lookup[#, "source_paths", {}] === {} &&
       Lookup[#, "implemented", True] === False) & /@ externalRecords),
    "red_only_not_implemented" -> And @@ (
      (nonEmptyListQ[Lookup[#, "evidence_paths", {}]] &&
       Lookup[#, "implemented", True] === False) & /@ redRecords),
    "absent_nodes_fail_closed" -> And @@ (
      (Lookup[#, "source_paths", {}] === {} &&
       Lookup[#, "source_lineages", {}] === {} &&
       Lookup[#, "implemented", True] === False) & /@ absentRecords),
    "sibling_lineage_held" -> And @@ (
      (StringQ[Lookup[#, "blocking_condition", None]] &&
       Lookup[#, "semantic_status", None] === "HELD_SIBLING_COMPOSITION") & /@ siblingRecords),
    "connection_curvature_split" -> And[
      KeyExistsQ[byId, "GEOM.LEVI_CIVITA_CONNECTION"],
      KeyExistsQ[byId, "GEOM.SPATIAL_CURVATURE"],
      Lookup[byId["GEOM.LEVI_CIVITA_CONNECTION"], "source_class"] === "GIT_DURABLE",
      Lookup[byId["GEOM.SPATIAL_CURVATURE"], "source_class"] === "GIT_SIBLING_HELD"
    ],
    "photon_snapshot_scope_firewall" -> And @@ (
      SubsetQ[
        Lookup[#, "scope_exclusions", {}],
        {"finite electron tilt", "recombination and reionization", "hierarchy truncation", "solver construction", "numerical evolution", "inference"}
      ] & /@ Select[records,
        MemberQ[{"KIN.HOMOGENEOUS_PHOTON_CORE", "COLL.THOMSON_REST"}, Lookup[#, "family_id"]] &]),
    "finite_tilt_and_local_boost_separate" -> And[
      KeyExistsQ[byId, "COLL.THOMSON_FINITE_TILT"],
      KeyExistsQ[byId, "OBS.LOCAL_BOOST"],
      Lookup[byId["COLL.THOMSON_FINITE_TILT"], "source_status"] === "FORMULA_LEVEL_DURABLE_RUNTIME_UNBOUND",
      Lookup[byId["OBS.LOCAL_BOOST"], "source_status"] === "NOT_STARTED_OUTPUT_NODE",
      Lookup[byId["OBS.LOCAL_BOOST"], "execution_owner", None] === "htt_base"
    ],
    "no_semantic_winner" -> Lookup[sourceMap, "semantic_winner_selected", True] === False,
    "official_dag_unchanged" -> Lookup[sourceMap, "official_dag_mutated", True] === False,
    "science_not_promoted" -> Lookup[sourceMap, "science_claim_promoted", True] === False,
    "next_node_limited" -> Lookup[sourceMap, "next_node", None] === "SYNC-MAP-01C_GEOMETRY_LINEAGE_COMPOSITION"
  |>;

  canonicalPayload = <|
    "map_id" -> Lookup[sourceMap, "map_id", None],
    "ids" -> Sort[ids],
    "source_class_counts" -> KeySort[actualCounts],
    "checks" -> checks
  |>;

  <|
    "status" -> If[And @@ Values[checks], "PASS", "FAIL"],
    "map_id" -> Lookup[sourceMap, "map_id", None],
    "family_count" -> Length[records],
    "source_class_counts" -> KeySort[actualCounts],
    "canonical_git_bound_count" -> Length[canonicalGitBound],
    "git_bound_count" -> Length[gitBound],
    "evidence_bearing_count" -> Length[evidenceBearing],
    "checks" -> checks,
    "failed_checks" -> Keys@Select[checks, Not@TrueQ[#] &],
    "canonical_sha256" -> Hash[
      ExportString[canonicalPayload, "RawJSON", "Compact" -> True],
      "SHA256", "HexString"
    ],
    "wolfram_version" -> $Version,
    "system_id" -> $SystemID,
    "xact_required" -> False,
    "claim_boundary" -> "BASS_SOURCE_LINEAGE_MAP_ONLY_NO_SEMANTIC_EQUIVALENCE_OR_SCIENCE_PROMOTION"
  |>
];
SYNCMap01R1Verify[___] := <|"status" -> "FAIL", "reason" -> "INVALID_SOURCE_MAP_INPUT"|>;

If[
  ValueQ[$SYNCMap01R1SourceMapURL],
  Module[{sourceMap = Quiet@Check[Import[$SYNCMap01R1SourceMapURL, "RawJSON"], $Failed]},
    If[AssociationQ[sourceMap], SYNCMap01R1Verify[sourceMap], <|"status" -> "FAIL", "reason" -> "SOURCE_MAP_IMPORT_FAILED"|>]
  ],
  <|"status" -> "NOT_RUN", "reason" -> "SET_$SYNCMap01R1SourceMapURL_BEFORE_GET"|>
]
