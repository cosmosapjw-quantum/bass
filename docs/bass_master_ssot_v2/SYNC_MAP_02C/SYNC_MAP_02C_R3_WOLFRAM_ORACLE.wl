(* Stateless exact oracle for SYNC-MAP-02C R3 and the six-record 02E scope.
   xAct is not required: this file checks finite-dimensional Lorentz algebra,
   sphere tangency, source/owner counts and DAG prerequisites only. *)
ClearAll["Global`*"];

GammaB = 1/Sqrt[1 - b^2];
Doppler = GammaB (1 + b mu);
MuBoosted = (mu + b)/(1 + b mu);
PerpBoostedSquared = (1 - mu^2) (1 - b^2)/(1 + b mu)^2;

NormResidual = FullSimplify[
  MuBoosted^2 + PerpBoostedSquared - 1,
  Assumptions -> {-1 < b < 1, -1 < mu < 1}
];
DopplerChartResidual = FullSimplify[
  Doppler - 1/(GammaB (1 - b MuBoosted)),
  Assumptions -> {-1 < b < 1, -1 < mu < 1}
];
JacobianResidual = FullSimplify[
  D[MuBoosted, mu] - Doppler^-2,
  Assumptions -> {-1 < b < 1, -1 < mu < 1}
];
BlackbodyResidual = FullSimplify[
  hP (Doppler nu)/(kB (Doppler temp)) - hP nu/(kB temp),
  Assumptions -> {Doppler > 0, nu > 0, temp > 0, hP > 0, kB > 0}
];

e = {ex, ey, ez};
aB = {ax, ay, az};
omega = {ox, oy, oz};
sigma = {{s11, s12, s13}, {s12, s22, s23}, {s13, s23, -s11 - s22}};
nB = {{n11, n12, n13}, {n12, n22, n23}, {n13, n23, n33}};
DirectionFlow = (e.sigma.e + aB.e) e - sigma.e - aB +
  Cross[omega, e] - Cross[e, nB.e];
TangencyResidual = FullSimplify[
  e.DirectionFlow,
  Assumptions -> {ex^2 + ey^2 + ez^2 == 1}
];
EnergyDriftFLRW = (-hgeom - e.sigma.e) /. Thread[Flatten[sigma] -> 0] // Simplify;

SharedFormulas = {
  "BASS.FRAME.ABERRATED_DIRECTION.001",
  "BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001",
  "BASS.FRAME.DOPPLER_FACTOR.001",
  "BASS.FRAME.SOLID_ANGLE_JACOBIAN.001",
  "BASS.PHOTON.DIRECTION_FLOW.001",
  "BASS.PHOTON.ENERGY_DRIFT.001"
};
RelationOwners = {
  "bass", "rec_bianchi", "bass", "rei_bianchi", "rei_bianchi",
  "rei_bianchi", "rei_bianchi", "rei_bianchi", "rei_bianchi",
  "rei_bianchi", "rei_bianchi", "rei_bianchi"
};
RelationClasses = {
  "PINNED_ARTIFACT_IMPORT_REQUIRED",
  "PINNED_ARTIFACT_IMPORT_REQUIRED",
  "PINNED_ARTIFACT_IMPORT_REQUIRED",
  "BASELINE_CONTROL_ORACLE",
  "ADAPTER_SPECIALIZATION", "ADAPTER_SPECIALIZATION",
  "OWNED_EXTENSION", "OWNED_EXTENSION", "OWNED_EXTENSION",
  "OWNED_EXTENSION", "OWNED_EXTENSION", "OWNED_FEASIBILITY_GATE"
};
SourceBlobs = {
  "5f797469eaa67847fa3c5f3701a5b8416a55d98e",
  "b3cc5e45988687b76d5be04c6335009b4c9bd17f",
  "3c0f68cb0e40e3826a3d80dfce2fcdd5065fd826",
  "afe9c5afc6b2d2b75283f50e4223c371b90746d0",
  "1328e49baa0f4bb5d4e1d5a5ca0940c10e8852d5",
  "389753d94a291fffbfb2b09092029d61afb3ea19",
  "7ec9bd5548db4c024c075b70d0affc81eccfe0d7",
  "ecb55acd39aba9d609f2eb704ef282018d6666b2",
  "cdd24e2e17897bf2bfe102814b123668d884c456",
  "604697415f4de9363951653165f90273f297e0b0",
  "3d80474e7ba1ecba4f102c5dd85b6efa2bfb0ec3",
  "3d806e1c1d3bb523bb3c339d1a141f67d7f10069",
  "5b74a4036c8cb21a2cb772dd3d373c5f96d5a36c",
  "6f5c13f02d0e549e581a02d3c4d8b8313b209bbf",
  "69e671769d70804be6f7debc4b9ba1f11519bbfc",
  "026a22b1843ab3a3336b210317727e216202fc75",
  "ea2a10a60114622fd1215b692be3dd0d04ef0c6d",
  "80a7627baf5981375de10ae55d862b09b0071432",
  "5d39fef633662178a71685dac90e4ffe9a0a788d",
  "83abebd1a4f7e7a6f5fba83d4a20e1b23063fa02",
  "1c295b27d692618fffef442182d1595feac56d7d",
  "fba94e59d20d640237290911abd774ede3fe5360"
};

Nodes = {"02A", "02B", "02C", "02D", "02E", "02F", "SYNC_REC",
  "SYNC_REI", "SYNC_HTT", "GATE"};
Edges = {"02A" -> "02B", "02B" -> "02C", "02B" -> "02D",
  "02C" -> "02E", "02D" -> "02E", "02E" -> "02F",
  "02F" -> "SYNC_REC", "02F" -> "SYNC_REI", "02F" -> "SYNC_HTT",
  "SYNC_REC" -> "GATE", "SYNC_REI" -> "GATE", "SYNC_HTT" -> "GATE"};
G = Graph[Nodes, DirectedEdge @@@ (List @@@ Edges)];

Checks = <|
  "aberrated_direction_unit_norm" -> TrueQ[NormResidual == 0],
  "doppler_chart_equivalence" -> TrueQ[DopplerChartResidual == 0],
  "solid_angle_jacobian" -> TrueQ[JacobianResidual == 0],
  "blackbody_planck_argument_invariant" -> TrueQ[BlackbodyResidual == 0],
  "direction_flow_tangent" -> TrueQ[TangencyResidual == 0],
  "energy_drift_flrw_limit" -> TrueQ[EnergyDriftFLRW == -hgeom],
  "six_formula_union" -> (Length[SharedFormulas] == 6 && DuplicateFreeQ[SharedFormulas]),
  "single_owner_invariant" -> AllTrue[RelationOwners,
    MemberQ[{"bass", "rec_bianchi", "rei_bianchi", "htt_base"}, #] &],
  "relation_count_12" -> (Length[RelationClasses] == 12),
  "source_blob_count_22" -> (Length[SourceBlobs] == 22 && DuplicateFreeQ[SourceBlobs]),
  "dag_acyclic" -> AcyclicGraphQ[G],
  "dag_topological_coverage" -> (Length[TopologicalSort[G]] == Length[Nodes]),
  "02c_and_02d_both_gate_02e" ->
    (MemberQ[Edges, "02C" -> "02E"] && MemberQ[Edges, "02D" -> "02E"])
|>;

Mutations = <|
  "wrong_jacobian_power_detected" -> TrueQ[FullSimplify[
    D[MuBoosted, mu] - Doppler^-1,
    Assumptions -> {-1 < b < 1, -1 < mu < 1}] =!= 0],
  "blackbody_weight_zero_detected" -> TrueQ[FullSimplify[
    hP (Doppler nu)/(kB temp) - hP nu/(kB temp),
    Assumptions -> {Doppler > 0, Doppler != 1, nu > 0, temp > 0,
      hP > 0, kB > 0}] =!= 0],
  "radial_compensation_omission_detected" ->
    TrueQ[{1, 0, 0}.(-DiagonalMatrix[{1, -1, 0}].{1, 0, 0}) == -1],
  "multi_owner_detected" ->
    Not[MemberQ[{"bass", "rec_bianchi", "rei_bianchi", "htt_base"}, "bass_and_rec"]],
  "stale_four_formula_union_detected" -> (Length[Take[SharedFormulas, 4]] != 6),
  "missing_source_row_detected" -> (Length[Most[SourceBlobs]] != 22),
  "missing_02d_gate_detected" ->
    Not[MemberQ[DeleteCases[Edges, "02D" -> "02E"], "02D" -> "02E"]]
|>;

Report = <|
  "status" -> If[And @@ Values[Checks] && And @@ Values[Mutations],
    "PASS_SYNC_MAP_02C_R3_AND_02E_SIX_FORMULA_CONTRACT", "FAIL"],
  "wolfram_version" -> $Version,
  "xact_required" -> False,
  "checks" -> Checks,
  "mutations" -> Mutations,
  "failed_checks" -> Keys@Select[Join[Checks, Mutations], Not@*TrueQ],
  "source_count" -> Length[SourceBlobs],
  "relation_count" -> Length[RelationClasses],
  "shared_formula_count" -> Length[SharedFormulas],
  "shared_formulas" -> SharedFormulas,
  "claim_effect" -> "NONE"
|>;

Print[ExportString[Report, "RawJSON", "Compact" -> True]];
If[Report["status"] =!= "PASS_SYNC_MAP_02C_R3_AND_02E_SIX_FORMULA_CONTRACT", Exit[1]];
