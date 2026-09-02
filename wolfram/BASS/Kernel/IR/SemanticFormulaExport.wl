(* ::Package:: *)

BeginPackage["BASS`IR`"];

BASSFormulaGlobalIDMap::usage =
 "BASSFormulaGlobalIDMap[] maps legacy BASS formula identifiers onto globally stable BASS.GEO identifiers.";
BASSFormulaEquationIRRegistry::usage =
 "BASSFormulaEquationIRRegistry[] returns the fourteen canonical BASS geometry formulas as valid EquationIR records.";
FormulaSemanticProjection::usage =
 "FormulaSemanticProjection[ir] removes identifier, human-label and provenance fields from a valid EquationIR before semantic hashing.";
FormulaSemanticSHA256::usage =
 "FormulaSemanticSHA256[ir] returns the canonical SHA-256 of FormulaSemanticProjection[ir].";
BASSFormulaDependencyEdges::usage =
 "BASSFormulaDependencyEdges[] returns closed depends_on edges among the canonical BASS geometry formula IDs.";
BASSFormulaSemanticExport::usage =
 "BASSFormulaSemanticExport[] returns the machine-readable owned-formula export for SYNC-MAP-02A.";
BASSFormulaSemanticExportQ::usage =
 "BASSFormulaSemanticExportQ[export] validates IDs, EquationIR records, semantic hashes, dependency closure and ownership.";

Begin["`Private`"];

ClearAll[
 BASSFormulaGlobalIDMap, BASSFormulaEquationIRRegistry,
 FormulaSemanticProjection, FormulaSemanticSHA256,
 BASSFormulaDependencyEdges, BASSFormulaSemanticExport,
 BASSFormulaSemanticExportQ, semanticStructureEquation,
 globalizeEquationIR, w3EquationIR, sourcePathMap,
 dependenciesFor, legacyIDsFor, exportFormulaRecord,
 semanticRegistryProjection, semanticHashStringQ,
 semanticFormulaIDs
];

BASSFormulaGlobalIDMap[] := <|
 "ALG01-STRUCTURE-001" -> "BASS.GEO.STRUCTURE_CONSTANTS.001",
 "W2-GEO-001" -> "BASS.GEO.SPATIAL_PROJECTOR.001",
 "W2-GEO-002" -> "BASS.GEO.SPATIAL_VOLUME_FORM.001",
 "W2-KIN-001" -> "BASS.GEO.NORMAL_ACCELERATION.001",
 "W2-KIN-002" -> "BASS.GEO.EXTRINSIC_CURVATURE.001",
 "W2-KIN-003" -> "BASS.GEO.NORMAL_DERIVATIVE_DECOMPOSITION.001",
 "W2-KIN-004" -> "BASS.GEO.EXTRINSIC_CURVATURE_SHEAR_SPLIT.001",
 "W2-CURV-001" -> "BASS.GEO.GAUSS.001",
 "W2-CURV-002" -> "BASS.GEO.CODAZZI.001",
 "W2-CURV-003" -> "BASS.GEO.CONTRACTED_GAUSS.001",
 "W3-CONN-001" -> "BASS.GEO.LEVI_CIVITA_CONNECTION.001",
 "W3-RIEM-001" -> "BASS.GEO.SPATIAL_RIEMANN.001",
 "W3-RICCI-001" -> "BASS.GEO.SPATIAL_RICCI.001",
 "W3-SCALAR-001" -> "BASS.GEO.SPATIAL_SCALAR.001"
|>;

semanticFormulaIDs[] := Values[BASSFormulaGlobalIDMap[]];

sourcePathMap[] := <|
 "BASS.GEO.STRUCTURE_CONSTANTS.001" ->
  "wolfram/BASS/Kernel/Geometry/StructureConstants.wl",
 "BASS.GEO.SPATIAL_PROJECTOR.001" ->
  "wolfram/BASS/Kernel/Geometry/Abstract1Plus3.wl",
 "BASS.GEO.SPATIAL_VOLUME_FORM.001" ->
  "wolfram/BASS/Kernel/Geometry/Abstract1Plus3.wl",
 "BASS.GEO.NORMAL_ACCELERATION.001" ->
  "wolfram/BASS/Kernel/Geometry/Abstract1Plus3.wl",
 "BASS.GEO.EXTRINSIC_CURVATURE.001" ->
  "wolfram/BASS/Kernel/Geometry/Abstract1Plus3.wl",
 "BASS.GEO.NORMAL_DERIVATIVE_DECOMPOSITION.001" ->
  "wolfram/BASS/Kernel/Geometry/Abstract1Plus3.wl",
 "BASS.GEO.EXTRINSIC_CURVATURE_SHEAR_SPLIT.001" ->
  "wolfram/BASS/Kernel/Geometry/Abstract1Plus3.wl",
 "BASS.GEO.GAUSS.001" ->
  "wolfram/BASS/Kernel/Geometry/Abstract1Plus3.wl",
 "BASS.GEO.CODAZZI.001" ->
  "wolfram/BASS/Kernel/Geometry/Abstract1Plus3.wl",
 "BASS.GEO.CONTRACTED_GAUSS.001" ->
  "wolfram/BASS/Kernel/Geometry/Abstract1Plus3.wl",
 "BASS.GEO.LEVI_CIVITA_CONNECTION.001" ->
  "wolfram/BASS/Kernel/Geometry/LeviCivitaConnection.wl",
 "BASS.GEO.SPATIAL_RIEMANN.001" ->
  "wolfram/BASS/Kernel/Geometry/ONFConnectionCurvature.wl",
 "BASS.GEO.SPATIAL_RICCI.001" ->
  "wolfram/BASS/Kernel/Geometry/ONFConnectionCurvature.wl",
 "BASS.GEO.SPATIAL_SCALAR.001" ->
  "wolfram/BASS/Kernel/Geometry/ONFConnectionCurvature.wl"
|>;

semanticStructureEquation[] := BASS`IR`MakeEquationIR[<|
 "formula_id" -> "BASS.GEO.STRUCTURE_CONSTANTS.001",
 "authority_theorem" -> "Bianchi orthonormal-frame structure decomposition",
 "target" -> "C^gamma_{alpha beta}",
 "free_indices" -> {"gamma", "alpha", "beta"},
 "representation" -> "homogeneous-orthonormal-frame",
 "assumptions" -> {
   "epsilon_123 = +1",
   "n^{alpha beta} = n^{beta alpha}",
   "n^{alpha beta} a_beta = 0"
  },
 "domain" -> <|
   "spatial_dimension" -> 3,
   "metric" -> "positive orthonormal spatial metric"
  |>,
 "dimensions" -> <|"target" -> "L^-1"|>,
 "terms" -> {
   <|"input" -> "epsilon_{alpha beta delta} n^{delta gamma}",
     "coefficient" -> BASS`IR`ExactScalarAST[1]|>,
   <|"input" -> "a_alpha delta^gamma_beta",
     "coefficient" -> BASS`IR`ExactScalarAST[1]|>,
   <|"input" -> "a_beta delta^gamma_alpha",
     "coefficient" -> BASS`IR`ExactScalarAST[-1]|>
  },
 "structural_zero_rules" -> {
   "C^gamma_{alpha beta} = -C^gamma_{beta alpha}"
  },
 "branch_predicates" -> {
   "BianchiTypeSpec supplies algebraic rank, inertia and signed-h domain"
  },
 "known_limits" -> {
   "Bianchi I: a_alpha = 0 and n^{alpha beta} = 0 implies C = 0"
  },
 "provenance" -> <|
   "stage" -> "ALG-01R2",
   "owner" -> "bass",
   "legacy_formula_id" -> "ALG01-STRUCTURE-001",
   "source_path" ->
    "wolfram/BASS/Kernel/Geometry/StructureConstants.wl"
  |>
|>];

globalizeEquationIR[ir_Association] := Module[
 {legacyID, globalID, provenance},
 legacyID = Lookup[ir, "formula_id", Missing["FormulaID"]];
 globalID = Lookup[BASSFormulaGlobalIDMap[], legacyID,
   Missing["GlobalFormulaID"]];
 If[MissingQ[globalID],
  Return[Failure["UnmappedLegacyFormulaID", <|"legacy_id" -> legacyID|>]]
 ];
 provenance = Join[
   Lookup[ir, "provenance", <||>],
   <|
    "owner" -> "bass",
    "legacy_formula_id" -> legacyID,
    "source_path" -> Lookup[sourcePathMap[], globalID,
      Missing["SourcePath"]]
   |>
  ];
 BASS`IR`CanonicalizeData @ Join[
   ir,
   <|"formula_id" -> globalID, "provenance" -> provenance|>
  ]
];

w3EquationIR[record_Association] := Module[
 {legacyID, globalID, target, dimension, freeIndices, structuralZeros,
  limits, terms},
 legacyID = Lookup[record, "formula_id", Missing["FormulaID"]];
 globalID = Lookup[BASSFormulaGlobalIDMap[], legacyID,
   Missing["GlobalFormulaID"]];
 If[MissingQ[globalID],
  Return[Failure["UnmappedW3FormulaID", <|"legacy_id" -> legacyID|>]]
 ];
 target = Lookup[record, "target", Missing["Target"]];
 dimension = Lookup[record, "dimension", Missing["Dimension"]];
 freeIndices = Switch[legacyID,
   "W3-CONN-001", {"alpha", "beta", "gamma"},
   "W3-RIEM-001", {"alpha", "beta", "gamma", "delta"},
   "W3-RICCI-001", {"gamma", "beta"},
   "W3-SCALAR-001", {},
   _, {}
  ];
 structuralZeros = Switch[legacyID,
   "W3-CONN-001", {
     "Gamma_{alpha beta gamma} + Gamma_{alpha gamma beta} = 0"
    },
   "W3-RIEM-001", {
     "R3_{alpha beta gamma delta} = -R3_{beta alpha gamma delta}",
     "R3_{alpha beta gamma delta} = -R3_{alpha beta delta gamma}",
     "R3_{alpha beta gamma delta} = R3_{gamma delta alpha beta}"
    },
   "W3-RICCI-001", {
     "R3_{alpha beta} = R3_{beta alpha}"
    },
   _, {}
  ];
 limits = Switch[legacyID,
   "W3-CONN-001", {"Bianchi I gives Gamma = 0"},
   "W3-RIEM-001", {"Bianchi I gives R3_{alpha beta gamma delta} = 0"},
   "W3-RICCI-001", {
     "Bianchi V normalized witness gives Ricci = -2 I_3",
     "Bianchi IX normalized witness gives Ricci = I_3/2"
    },
   "W3-SCALAR-001", {
     "Bianchi I: R3 = 0",
     "Bianchi V normalized witness: R3 = -6",
     "Bianchi IX normalized witness: R3 = 3/2"
    },
   _, {}
  ];
 terms = Map[
   Function[term,
    <|
     "input" -> Lookup[term, "input", Missing["Input"]],
     "coefficient" ->
      BASS`IR`ExactScalarAST[Lookup[term, "coefficient", Missing["Coefficient"]]]
    |>
   ],
   Lookup[record, "terms", {}]
  ];
 BASS`IR`MakeEquationIR[<|
   "formula_id" -> globalID,
   "authority_theorem" -> Switch[legacyID,
     "W3-CONN-001", "Homogeneous ONF Levi-Civita connection",
     "W3-RIEM-001", "Homogeneous ONF spatial Riemann tensor",
     "W3-RICCI-001", "Spatial Ricci contraction",
     "W3-SCALAR-001", "Spatial scalar-curvature contraction",
     _, "W3 geometry formula"
    ],
   "target" -> target,
   "free_indices" -> freeIndices,
   "representation" -> "homogeneous-orthonormal-frame",
   "assumptions" -> {
     "torsion-free metric-compatible spatial connection",
     "homogeneous frame coefficients",
     "Bianchi Jacobi identity"
    },
   "domain" -> <|
     "spatial_dimension" -> 3,
     "metric" -> "positive orthonormal spatial metric",
     "riemann_convention" ->
      "[nabla_alpha,nabla_beta] v^delta = R_{alpha beta gamma}^delta v^gamma"
    |>,
   "dimensions" -> <|"target" -> dimension|>,
   "terms" -> terms,
   "structural_zero_rules" -> structuralZeros,
   "branch_predicates" -> {
     "BianchiTypeSpec and JacobiIdentityQ select the algebra branch"
    },
   "known_limits" -> limits,
   "provenance" -> <|
     "stage" -> "SYNC-MAP-01C/W3",
     "owner" -> "bass",
     "legacy_formula_id" -> legacyID,
     "source_path" -> Lookup[sourcePathMap[], globalID,
       Missing["SourcePath"]]
    |>
  |>]
];

BASSFormulaEquationIRRegistry[] := Module[
 {w2, w3, records},
 w2 = globalizeEquationIR /@
   BASS`Geometry`Abstract1Plus3EquationRegistry[];
 w3 = w3EquationIR /@ BASS`Geometry`W3FormulaRegistry[];
 records = Join[{semanticStructureEquation[]}, w2, w3];
 SortBy[records, Lookup[#, "formula_id", ""] &]
];

FormulaSemanticProjection[ir_Association] /; BASS`IR`EquationIRQ[ir] :=
 BASS`IR`CanonicalizeData @
  KeyDrop[ir, {"schema_version", "formula_id", "authority_theorem",
    "provenance"}];
FormulaSemanticProjection[other_] := Failure[
 "InvalidEquationIRForSemanticProjection",
 <|"input_head" -> ToString[Head[Unevaluated[other]], InputForm]|>
];

FormulaSemanticSHA256[ir_Association] := Module[{projection},
 projection = FormulaSemanticProjection[ir];
 If[FailureQ[projection], Return[projection]];
 BASS`IR`CanonicalSHA256[projection]
];
FormulaSemanticSHA256[other_] := Failure[
 "InvalidEquationIRForSemanticHash",
 <|"input_head" -> ToString[Head[Unevaluated[other]], InputForm]|>
];

BASSFormulaDependencyEdges[] := SortBy[
 {
  <|"from" -> "BASS.GEO.EXTRINSIC_CURVATURE.001",
    "to" -> "BASS.GEO.SPATIAL_PROJECTOR.001",
    "relation" -> "depends_on"|>,
  <|"from" -> "BASS.GEO.NORMAL_DERIVATIVE_DECOMPOSITION.001",
    "to" -> "BASS.GEO.NORMAL_ACCELERATION.001",
    "relation" -> "depends_on"|>,
  <|"from" -> "BASS.GEO.NORMAL_DERIVATIVE_DECOMPOSITION.001",
    "to" -> "BASS.GEO.EXTRINSIC_CURVATURE.001",
    "relation" -> "depends_on"|>,
  <|"from" -> "BASS.GEO.EXTRINSIC_CURVATURE_SHEAR_SPLIT.001",
    "to" -> "BASS.GEO.EXTRINSIC_CURVATURE.001",
    "relation" -> "depends_on"|>,
  <|"from" -> "BASS.GEO.EXTRINSIC_CURVATURE_SHEAR_SPLIT.001",
    "to" -> "BASS.GEO.SPATIAL_PROJECTOR.001",
    "relation" -> "depends_on"|>,
  <|"from" -> "BASS.GEO.GAUSS.001",
    "to" -> "BASS.GEO.EXTRINSIC_CURVATURE.001",
    "relation" -> "depends_on"|>,
  <|"from" -> "BASS.GEO.GAUSS.001",
    "to" -> "BASS.GEO.SPATIAL_RIEMANN.001",
    "relation" -> "depends_on"|>,
  <|"from" -> "BASS.GEO.CODAZZI.001",
    "to" -> "BASS.GEO.EXTRINSIC_CURVATURE.001",
    "relation" -> "depends_on"|>,
  <|"from" -> "BASS.GEO.CONTRACTED_GAUSS.001",
    "to" -> "BASS.GEO.EXTRINSIC_CURVATURE.001",
    "relation" -> "depends_on"|>,
  <|"from" -> "BASS.GEO.CONTRACTED_GAUSS.001",
    "to" -> "BASS.GEO.SPATIAL_SCALAR.001",
    "relation" -> "depends_on"|>,
  <|"from" -> "BASS.GEO.LEVI_CIVITA_CONNECTION.001",
    "to" -> "BASS.GEO.STRUCTURE_CONSTANTS.001",
    "relation" -> "depends_on"|>,
  <|"from" -> "BASS.GEO.SPATIAL_RIEMANN.001",
    "to" -> "BASS.GEO.LEVI_CIVITA_CONNECTION.001",
    "relation" -> "depends_on"|>,
  <|"from" -> "BASS.GEO.SPATIAL_RIEMANN.001",
    "to" -> "BASS.GEO.STRUCTURE_CONSTANTS.001",
    "relation" -> "depends_on"|>,
  <|"from" -> "BASS.GEO.SPATIAL_RICCI.001",
    "to" -> "BASS.GEO.SPATIAL_RIEMANN.001",
    "relation" -> "depends_on"|>,
  <|"from" -> "BASS.GEO.SPATIAL_SCALAR.001",
    "to" -> "BASS.GEO.SPATIAL_RICCI.001",
    "relation" -> "depends_on"|>
 },
 {Lookup[#, "from", ""], Lookup[#, "to", ""]} &
];

dependenciesFor[formulaID_String] := Sort @ Lookup[
 Select[BASSFormulaDependencyEdges[],
  Lookup[#, "from", None] === formulaID &],
 "to", {}
];

legacyIDsFor[globalID_String] := Sort @ Keys @ Select[
 BASSFormulaGlobalIDMap[], SameQ[#, globalID] &
];

exportFormulaRecord[ir_Association] := Module[
 {formulaID, semanticHash},
 formulaID = Lookup[ir, "formula_id", Missing["FormulaID"]];
 semanticHash = FormulaSemanticSHA256[ir];
 <|
  "formula_id" -> formulaID,
  "owner" -> "bass",
  "authority_effect" -> "AUTHORITATIVE_DERIVATION",
  "status" -> "SYMBOLIC_VERIFIED",
  "legacy_formula_ids" -> legacyIDsFor[formulaID],
  "source_path" -> Lookup[sourcePathMap[], formulaID,
    Missing["SourcePath"]],
  "semantic_hash" -> semanticHash,
  "semantic_projection" -> FormulaSemanticProjection[ir],
  "equation_ir" -> ir,
  "dependencies" -> dependenciesFor[formulaID],
  "allowed_consumer_modes" -> {
    "PINNED_IMPORT", "INDEPENDENT_ORACLE", "ADAPTER_SPECIALIZATION"
   }
 |>
];

semanticRegistryProjection[records_List, edges_List] := <|
 "formulas" -> Map[
   KeyTake[#, {"formula_id", "semantic_hash", "dependencies"}] &,
   records
  ],
 "dependency_edges" -> edges
|>;

BASSFormulaSemanticExport[] := Module[
 {registry, records, edges, registryHash},
 registry = BASSFormulaEquationIRRegistry[];
 records = exportFormulaRecord /@ registry;
 edges = BASSFormulaDependencyEdges[];
 registryHash = BASS`IR`CanonicalSHA256[
   semanticRegistryProjection[records, edges]
  ];
 BASS`IR`CanonicalizeData @ <|
  "schema_version" -> "1.0.0",
  "program_id" -> "BIANCHI-WOLFRAM-TRIREPO-20260830",
  "stage_id" -> "SYNC_MAP_02A_BASS_EQUATIONIR_AND_SEMANTIC_HASH_EXPORT",
  "owner" -> "bass",
  "source_repository" -> "cosmosapjw-quantum/bass",
  "source_parent_commit" ->
   "80d271cc528e1a0ffa813ecd3e3fb7610f3fa755",
  "formula_source_commit" ->
   "fd022fdb43ac73ae8977494f7b61959f4ea600ac",
  "formula_source_tree" ->
   "ce560f825c692cfbc835ca01ff1292cee291f656",
  "convention_hash" ->
   BASS`IR`CanonicalSHA256[BASS`Authority`ConventionLock[]],
  "type_registry_semantic_hash" ->
   BASS`Bianchi`CanonicalTypeSpecRegistrySemanticSHA256[],
  "formula_count" -> Length[records],
  "formulas" -> records,
  "dependency_edges" -> edges,
  "registry_semantic_hash" -> registryHash,
  "coverage" -> <|
    "included" -> {
      "ALG-01 Bianchi structure decomposition",
      "W2 abstract 1+3 and Gauss-Codazzi registry",
      "W3 canonical connection and I/V/IX spatial-curvature formulas"
     },
    "excluded" -> {
      "all-type curvature specialization",
      "Einstein-matter background evolution",
      "REC and REI semantic relation mapping"
     }
   |>,
  "claim_boundary" ->
   "BASS_FORMULA_SEMANTIC_EXPORT_ONLY_NO_CROSS_REPO_EQUIVALENCE_BACKGROUND_OR_SCIENCE_PROMOTION"
 |>
];

semanticHashStringQ[value_] :=
 StringQ[value] && StringLength[value] === 64 &&
  StringMatchQ[value, HexadecimalCharacter ..];

BASSFormulaSemanticExportQ[export_Association] := Module[
 {formulas, edges, ids, expectedIDs, records, recalculatedRegistryHash,
  dependencyClosed},
 formulas = Lookup[export, "formulas", Missing["Formulas"]];
 edges = Lookup[export, "dependency_edges", Missing["Edges"]];
 If[!ListQ[formulas] || !ListQ[edges], Return[False]];
 ids = Lookup[formulas, "formula_id", Missing["FormulaID"]];
 expectedIDs = Sort[semanticFormulaIDs[]];
 records = Lookup[formulas, "equation_ir", Missing["EquationIR"]];
 dependencyClosed = AllTrue[edges,
   MemberQ[expectedIDs, Lookup[#, "from", None]] &&
    MemberQ[expectedIDs, Lookup[#, "to", None]] &&
    Lookup[#, "relation", None] === "depends_on" &
  ];
 recalculatedRegistryHash = BASS`IR`CanonicalSHA256[
   semanticRegistryProjection[formulas, edges]
  ];
 And[
  Lookup[export, "schema_version", None] === "1.0.0",
  Lookup[export, "stage_id", None] ===
   "SYNC_MAP_02A_BASS_EQUATIONIR_AND_SEMANTIC_HASH_EXPORT",
  Lookup[export, "owner", None] === "bass",
  Lookup[export, "formula_count", None] === 14,
  Length[formulas] === 14,
  Sort[ids] === expectedIDs,
  DuplicateFreeQ[ids],
  AllTrue[records, BASS`IR`EquationIRQ],
  AllTrue[formulas,
   semanticHashStringQ[Lookup[#, "semantic_hash", None]] &&
    Lookup[#, "semantic_hash", None] ===
     FormulaSemanticSHA256[Lookup[#, "equation_ir", <||>]] &&
    Lookup[#, "owner", None] === "bass" &&
    Lookup[#, "authority_effect", None] ===
     "AUTHORITATIVE_DERIVATION" &
  ],
  dependencyClosed,
  FreeQ[export, _Real],
  Lookup[export, "convention_hash", None] ===
   "e12258405c1c2ec296839524f5169e03441715b3acaaff1cef9de28bfa490a70",
  Lookup[export, "type_registry_semantic_hash", None] ===
   "e0e5fbba464a839fcb5b11d41c7772c666224ec69f806910aab3bfab5a2f1762",
  semanticHashStringQ[Lookup[export, "registry_semantic_hash", None]],
  Lookup[export, "registry_semantic_hash", None] ===
   recalculatedRegistryHash,
  Lookup[export, "claim_boundary", None] ===
   "BASS_FORMULA_SEMANTIC_EXPORT_ONLY_NO_CROSS_REPO_EQUIVALENCE_BACKGROUND_OR_SCIENCE_PROMOTION"
 ]
];
BASSFormulaSemanticExportQ[_] := False;

End[];
EndPackage[];
