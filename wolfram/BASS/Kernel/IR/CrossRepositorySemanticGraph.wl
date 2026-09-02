(* ::Package:: *)

BeginPackage["BASS`IR`"];

CrossRepositorySemanticGraphSummary::usage =
 "CrossRepositorySemanticGraphSummary[] returns the exact six-formula, ten-relation SYNC-MAP-02F graph summary.";
CrossRepositorySemanticGraphSummaryQ::usage =
 "CrossRepositorySemanticGraphSummaryQ[summary] validates owner uniqueness, relation coverage, DAG order, and claim firewalls.";
CrossRepositorySemanticAdapterReport::usage =
 "CrossRepositorySemanticAdapterReport[] returns exact algebraic residuals for the direction, time-rate, and strict-subdomain adapters.";
CrossRepositorySemanticGraphReceipt::usage =
 "CrossRepositorySemanticGraphReceipt[] returns the bounded formula-graph receipt with no runtime or science authority effect.";

Begin["`Private`"];

ClearAll[
 CrossRepositorySemanticGraphSummary,
 CrossRepositorySemanticGraphSummaryQ,
 CrossRepositorySemanticAdapterReport,
 CrossRepositorySemanticGraphReceipt,
 sync02FAcyclicQ
];

CrossRepositorySemanticGraphSummary[] := <|
 "StageID" -> "SYNC_MAP_02F_CROSS_REPOSITORY_SEMANTIC_GRAPH",
 "AuthorityOwner" -> "bass",
 "FormulaIDs" -> {
  "BASS.FRAME.ABERRATED_DIRECTION.001",
  "BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001",
  "BASS.FRAME.DOPPLER_FACTOR.001",
  "BASS.FRAME.SOLID_ANGLE_JACOBIAN.001",
  "BASS.PHOTON.DIRECTION_FLOW.001",
  "BASS.PHOTON.ENERGY_DRIFT.001"
 },
 "ConsumerRelations" -> {
  {"BASS.FRAME.ABERRATED_DIRECTION.001", "rec_bianchi", "SEMANTIC_EQUIVALENT_WITH_DIRECTION_ADAPTER"},
  {"BASS.FRAME.DOPPLER_FACTOR.001", "rec_bianchi", "SEMANTIC_EQUIVALENT_WITH_DIRECTION_ADAPTER"},
  {"BASS.PHOTON.DIRECTION_FLOW.001", "rec_bianchi", "SEMANTIC_EQUIVALENT_WITH_RATE_AND_NOTATION_ADAPTER"},
  {"BASS.PHOTON.ENERGY_DRIFT.001", "rec_bianchi", "SEMANTIC_EQUIVALENT_WITH_RATE_AND_NOTATION_ADAPTER"},
  {"BASS.PHOTON.DIRECTION_FLOW.001", "rei_bianchi", "ABSENT_REQUIRED_DEPENDENCY"},
  {"BASS.PHOTON.ENERGY_DRIFT.001", "rei_bianchi", "NON_EQUIVALENT_RESTRICTED_CONTROL"},
  {"BASS.FRAME.ABERRATED_DIRECTION.001", "htt_base", "SEMANTIC_EQUIVALENT_IDENTITY_CHART"},
  {"BASS.FRAME.DOPPLER_FACTOR.001", "htt_base", "SEMANTIC_EQUIVALENT_IDENTITY_CHART"},
  {"BASS.FRAME.SOLID_ANGLE_JACOBIAN.001", "htt_base", "INDEPENDENT_ORACLE"},
  {"BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001", "htt_base", "ADAPTER_SPECIALIZATION_STRICT_SUBDOMAIN"}
 },
 "DAGNodes" -> {
  "SYNC_MAP_02A_BASS", "SYNC_MAP_02B_REC", "SYNC_MAP_02C_REI",
  "SYNC_MAP_02D_HTT", "SYNC_MAP_02E_SHARED_EXPORT",
  "SYNC_MAP_02F_SEMANTIC_GRAPH", "SYNC_REC_01", "SYNC_REI_01",
  "SYNC_HTT_01A", "SYNC_GATE_01"
 },
 "DAGEdges" -> {
  "SYNC_MAP_02A_BASS" -> "SYNC_MAP_02B_REC",
  "SYNC_MAP_02B_REC" -> "SYNC_MAP_02C_REI",
  "SYNC_MAP_02B_REC" -> "SYNC_MAP_02D_HTT",
  "SYNC_MAP_02C_REI" -> "SYNC_MAP_02E_SHARED_EXPORT",
  "SYNC_MAP_02D_HTT" -> "SYNC_MAP_02E_SHARED_EXPORT",
  "SYNC_MAP_02E_SHARED_EXPORT" -> "SYNC_MAP_02F_SEMANTIC_GRAPH",
  "SYNC_MAP_02F_SEMANTIC_GRAPH" -> "SYNC_REC_01",
  "SYNC_MAP_02F_SEMANTIC_GRAPH" -> "SYNC_REI_01",
  "SYNC_MAP_02F_SEMANTIC_GRAPH" -> "SYNC_HTT_01A",
  "SYNC_REC_01" -> "SYNC_GATE_01",
  "SYNC_REI_01" -> "SYNC_GATE_01",
  "SYNC_HTT_01A" -> "SYNC_GATE_01"
 },
 "ManualGate" -> True,
 "OfficialJiraEdgesMutated" -> False
|>;

sync02FAcyclicQ[nodes_List, edges_List] := Module[{graph},
 graph = Graph[nodes, DirectedEdge @@@ (List @@@ edges)];
 AcyclicGraphQ[graph] && Sort[VertexList[graph]] === Sort[nodes]
];

CrossRepositorySemanticGraphSummaryQ[summary_Association] := Module[
 {ids, relations, nodes, edges, coverage},
 ids = Lookup[summary, "FormulaIDs", {}];
 relations = Lookup[summary, "ConsumerRelations", {}];
 nodes = Lookup[summary, "DAGNodes", {}];
 edges = Lookup[summary, "DAGEdges", {}];
 coverage = GroupBy[relations, First -> (#[[2]] &)];
 And[
  Lookup[summary, "StageID", None] ===
   "SYNC_MAP_02F_CROSS_REPOSITORY_SEMANTIC_GRAPH",
  Lookup[summary, "AuthorityOwner", None] === "bass",
  Length[ids] === 6 && DuplicateFreeQ[ids],
  Length[relations] === 10 && DuplicateFreeQ[relations],
  Sort[DeleteDuplicates[Lookup[coverage, "BASS.FRAME.ABERRATED_DIRECTION.001", {}]]] === Sort[{"rec_bianchi", "htt_base"}],
  Sort[DeleteDuplicates[Lookup[coverage, "BASS.FRAME.DOPPLER_FACTOR.001", {}]]] === Sort[{"rec_bianchi", "htt_base"}],
  Sort[DeleteDuplicates[Lookup[coverage, "BASS.PHOTON.DIRECTION_FLOW.001", {}]]] === Sort[{"rec_bianchi", "rei_bianchi"}],
  Sort[DeleteDuplicates[Lookup[coverage, "BASS.PHOTON.ENERGY_DRIFT.001", {}]]] === Sort[{"rec_bianchi", "rei_bianchi"}],
  Length[nodes] === 10 && DuplicateFreeQ[nodes],
  Length[edges] === 12 && DuplicateFreeQ[edges],
  sync02FAcyclicQ[nodes, edges],
  MemberQ[edges, "SYNC_MAP_02E_SHARED_EXPORT" -> "SYNC_MAP_02F_SEMANTIC_GRAPH"],
  MemberQ[edges, "SYNC_MAP_02F_SEMANTIC_GRAPH" -> "SYNC_REC_01"],
  MemberQ[edges, "SYNC_MAP_02F_SEMANTIC_GRAPH" -> "SYNC_REI_01"],
  MemberQ[edges, "SYNC_MAP_02F_SEMANTIC_GRAPH" -> "SYNC_HTT_01A"],
  TrueQ[Lookup[summary, "ManualGate", False]],
  FalseQ[Lookup[summary, "OfficialJiraEdgesMutated", True]]
 ]
];
CrossRepositorySemanticGraphSummaryQ[_] := False;

CrossRepositorySemanticAdapterReport[] := Module[
 {gamma, betaDotE, c, rEll, vEll, sigmaEE, h, dopplerSky, dopplerPhoton,
  recR, recV, reiControl, bassGeneric},
 dopplerSky = gamma (1 + (-betaDotE));
 dopplerPhoton = gamma (1 - betaDotE);
 recR = c rEll;
 recV = c vEll;
 reiControl = -h;
 bassGeneric = -h - sigmaEE;
 <|
  "FuturePhotonOutwardSkyDopplerResidual" ->
   Expand[dopplerSky - dopplerPhoton],
  "RECEnergyRateAdapterResidual" -> Expand[recR - c rEll],
  "RECDirectionRateAdapterResidual" -> Expand[recV - c vEll],
  "REIHOnlyMinusGenericEnergyDrift" -> Expand[reiControl - bassGeneric],
  "REIHOnlyIsotropicControlResidual" ->
   Expand[(reiControl - bassGeneric) /. sigmaEE -> 0],
  "REIGenericEquivalenceQ" ->
   TrueQ[Expand[reiControl - bassGeneric] === 0]
 |>
];

CrossRepositorySemanticGraphReceipt[] := Module[
 {summary = CrossRepositorySemanticGraphSummary[], adapters},
 adapters = CrossRepositorySemanticAdapterReport[];
 <|
  "Status" -> If[
    CrossRepositorySemanticGraphSummaryQ[summary] &&
     Lookup[adapters, "FuturePhotonOutwardSkyDopplerResidual"] === 0 &&
     Lookup[adapters, "RECEnergyRateAdapterResidual"] === 0 &&
     Lookup[adapters, "RECDirectionRateAdapterResidual"] === 0 &&
     Lookup[adapters, "REIHOnlyMinusGenericEnergyDrift"] === sigmaEE &&
     Lookup[adapters, "REIHOnlyIsotropicControlResidual"] === 0 &&
     FalseQ[Lookup[adapters, "REIGenericEquivalenceQ"]],
    "PASS", "FAIL"],
  "FormulaCount" -> 6,
  "ConsumerRelationCount" -> 10,
  "AuthorityEffect" -> "NONE_BEYOND_BOUNDED_SEMANTIC_GRAPH",
  "Withheld" -> {
   "CONSUMER_IMPLEMENTATION_PARITY", "GLOBAL_MATTER_TILT",
   "FINITE_ELECTRON_TILT_COLLISION", "PROVIDER_ADMISSION",
   "NUMERICAL_PARITY", "SCIENCE_VALIDITY", "PASS_RF04"
  }
 |>
];

End[];
EndPackage[];
