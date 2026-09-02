(* ::Package:: *)

BeginPackage["BASS`IR`"];

SharedFramePhotonFormulaIDs::usage =
 "SharedFramePhotonFormulaIDs[] returns the six canonical SYNC-MAP-02E formula identifiers.";
SharedFramePhotonExpectedSemanticHashes::usage =
 "SharedFramePhotonExpectedSemanticHashes[] returns the exact six formula semantic hashes.";
SharedFramePhotonExactResiduals::usage =
 "SharedFramePhotonExactResiduals[] returns exact Lorentz and homogeneous-photon residuals.";
SharedFramePhotonDependencyGraphQ::usage =
 "SharedFramePhotonDependencyGraphQ[data] checks exact dependency closure and acyclicity.";
SharedFramePhotonExportQ::usage =
 "SharedFramePhotonExportQ[data] fail-closed validates a SYNC-MAP-02E machine export.";

Begin["`Private`"];

ClearAll[
 SharedFramePhotonFormulaIDs, SharedFramePhotonExpectedSemanticHashes,
 SharedFramePhotonExactResiduals, SharedFramePhotonDependencyGraphQ,
 SharedFramePhotonExportQ, semanticProjection, termSignature, formulaMap,
 expectedInternalEdges, expectedExternalEdges, expectedTerms, expectedDimensions,
 expectedConsumers, expectedDependencies, expectedExternalDependencies,
 exactIntegerValue, scopeFirewallQ, claimBoundaryQ
];

SharedFramePhotonFormulaIDs[] := {
 "BASS.FRAME.ABERRATED_DIRECTION.001",
 "BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001",
 "BASS.FRAME.DOPPLER_FACTOR.001",
 "BASS.FRAME.SOLID_ANGLE_JACOBIAN.001",
 "BASS.PHOTON.DIRECTION_FLOW.001",
 "BASS.PHOTON.ENERGY_DRIFT.001"
};

SharedFramePhotonExpectedSemanticHashes[] := <|
 "BASS.FRAME.ABERRATED_DIRECTION.001" ->
  "7d212853f2f5aead7bc338605112d510d2793ebc9fc1192de61fea9d757536e5",
 "BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001" ->
  "5ef8a90ff34b6df1f6075e8208faeca76e53921addc47441d0d877ee66bcc67f",
 "BASS.FRAME.DOPPLER_FACTOR.001" ->
  "6932f72745ed092dd2c356a9db984de4dc6197b77f2bcf881ad1699f87010fc8",
 "BASS.FRAME.SOLID_ANGLE_JACOBIAN.001" ->
  "937a9b46dece8df45590bfa895ede33c027cefd211a48a0f4b8ca49f4bcb94c4",
 "BASS.PHOTON.DIRECTION_FLOW.001" ->
  "a76d3e1ea11488b9e4269e169bf1f95d2d6f4a1ccd63715be36f76b85975df4e",
 "BASS.PHOTON.ENERGY_DRIFT.001" ->
  "d296e7686dce3feb4a932b81427f918df06d4690e57a4ba2b998cf96897e7b2d"
|>;

expectedInternalEdges[] := Sort[{
 {"BASS.FRAME.ABERRATED_DIRECTION.001", "BASS.FRAME.DOPPLER_FACTOR.001"},
 {"BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001", "BASS.FRAME.DOPPLER_FACTOR.001"},
 {"BASS.FRAME.SOLID_ANGLE_JACOBIAN.001", "BASS.FRAME.ABERRATED_DIRECTION.001"},
 {"BASS.FRAME.SOLID_ANGLE_JACOBIAN.001", "BASS.FRAME.DOPPLER_FACTOR.001"}
}];

expectedExternalEdges[] := Sort[{
 {"BASS.PHOTON.DIRECTION_FLOW.001", "BASS.GEO.EXTRINSIC_CURVATURE_SHEAR_SPLIT.001"},
 {"BASS.PHOTON.DIRECTION_FLOW.001", "BASS.GEO.STRUCTURE_CONSTANTS.001"},
 {"BASS.PHOTON.ENERGY_DRIFT.001", "BASS.GEO.EXTRINSIC_CURVATURE_SHEAR_SPLIT.001"}
}];

expectedTerms[] := <|
 "BASS.FRAME.ABERRATED_DIRECTION.001" -> {
  {"[n_sky^a+(gamma+((gamma-1)/beta_squared)*beta_dot_n_sky)*beta^a]/doppler_factor", 1}},
 "BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001" -> {
  {"doppler_factor*temperature(n_sky)", 1}},
 "BASS.FRAME.DOPPLER_FACTOR.001" -> {
  {"gamma*(1+beta_dot_n_sky)", 1}},
 "BASS.FRAME.SOLID_ANGLE_JACOBIAN.001" -> {
  {"doppler_factor^(-2)*dOmega", 1}},
 "BASS.PHOTON.DIRECTION_FLOW.001" -> {
  {"(sigma_bc*e^b*e^c+aB_b*e^b)*e^a", 1},
  {"sigma^a_b*e^b", -1},
  {"aB^a", -1},
  {"epsilon^a_bc*Omega_triad^b*e^c", 1},
  {"epsilon^a_bc*e^b*nB^c_d*e^d", -1}},
 "BASS.PHOTON.ENERGY_DRIFT.001" -> {
  {"H_geom", -1}, {"sigma_ab*e^a*e^b", -1}}
|>;

expectedDimensions[] := <|
 "BASS.FRAME.ABERRATED_DIRECTION.001" -> "1",
 "BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001" -> "K",
 "BASS.FRAME.DOPPLER_FACTOR.001" -> "1",
 "BASS.FRAME.SOLID_ANGLE_JACOBIAN.001" -> "1",
 "BASS.PHOTON.DIRECTION_FLOW.001" -> "L^-1",
 "BASS.PHOTON.ENERGY_DRIFT.001" -> "L^-1"
|>;

expectedConsumers[] := <|
 "BASS.FRAME.ABERRATED_DIRECTION.001" -> {"rec_bianchi", "htt_base"},
 "BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001" -> {"htt_base"},
 "BASS.FRAME.DOPPLER_FACTOR.001" -> {"rec_bianchi", "htt_base"},
 "BASS.FRAME.SOLID_ANGLE_JACOBIAN.001" -> {"htt_base"},
 "BASS.PHOTON.DIRECTION_FLOW.001" -> {"rec_bianchi", "rei_bianchi"},
 "BASS.PHOTON.ENERGY_DRIFT.001" -> {"rec_bianchi", "rei_bianchi"}
|>;

expectedDependencies[] := <|
 "BASS.FRAME.ABERRATED_DIRECTION.001" -> {"BASS.FRAME.DOPPLER_FACTOR.001"},
 "BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001" -> {"BASS.FRAME.DOPPLER_FACTOR.001"},
 "BASS.FRAME.DOPPLER_FACTOR.001" -> {},
 "BASS.FRAME.SOLID_ANGLE_JACOBIAN.001" -> {
  "BASS.FRAME.ABERRATED_DIRECTION.001", "BASS.FRAME.DOPPLER_FACTOR.001"},
 "BASS.PHOTON.DIRECTION_FLOW.001" -> {},
 "BASS.PHOTON.ENERGY_DRIFT.001" -> {}
|>;

expectedExternalDependencies[] := <|
 "BASS.FRAME.ABERRATED_DIRECTION.001" -> {},
 "BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001" -> {},
 "BASS.FRAME.DOPPLER_FACTOR.001" -> {},
 "BASS.FRAME.SOLID_ANGLE_JACOBIAN.001" -> {},
 "BASS.PHOTON.DIRECTION_FLOW.001" -> {
  "BASS.GEO.EXTRINSIC_CURVATURE_SHEAR_SPLIT.001",
  "BASS.GEO.STRUCTURE_CONSTANTS.001"},
 "BASS.PHOTON.ENERGY_DRIFT.001" -> {
  "BASS.GEO.EXTRINSIC_CURVATURE_SHEAR_SPLIT.001"}
|>;

semanticProjection[ir_Association] :=
 KeyDrop[ir, {"schema_version", "formula_id", "authority_theorem", "provenance"}];

exactIntegerValue[ast_Association] := If[
 Sort[Keys[ast]] === {"type", "value"} && Lookup[ast, "type", None] === "integer" &&
  IntegerQ[Lookup[ast, "value", None]], Lookup[ast, "value"], Missing["InvalidIntegerAST"]];
exactIntegerValue[_] := Missing["InvalidIntegerAST"];

termSignature[ir_Association] := Map[
 {Lookup[#, "input", Missing["Input"]], exactIntegerValue[Lookup[#, "coefficient", <||>]]} &,
 Lookup[ir, "terms", {}]];

formulaMap[data_Association] := Association @ Map[
 Lookup[#, "formula_id", Missing["ID"]] -> # &,
 Lookup[data, "formulas", {}]];

scopeFirewallQ[data_Association] := Module[{text},
 text = ToLowerCase @ StringRiffle[
   ToString /@ Lookup[Lookup[data, "coverage", <||>], "included", {}], " "];
 And @@ (StringFreeQ[text, #] & /@ {
   "background provider", "global matter", "electron tilt", "recombination",
   "reionization", "mask", "estimator", "likelihood", "statistics"})
];

claimBoundaryQ[data_Association] := Module[{boundary},
 boundary = Lookup[data, "claim_boundary", ""];
 StringQ[boundary] && And @@ (StringContainsQ[boundary, #] & /@ {
   "NO_BACKGROUND_PROVIDER", "NO_GLOBAL_TILT",
   "NO_FINITE_ELECTRON_COLLISION", "NO_CROSS_REPO_EQUIVALENCE",
   "NO_STATISTICS_OR_SCIENCE_PROMOTION"})
];

SharedFramePhotonDependencyGraphQ[data_Association] := Module[
 {ids, internal, external, graph},
 ids = SharedFramePhotonFormulaIDs[];
 internal = Sort @ ({Lookup[#, "from"], Lookup[#, "to"]} & /@
    Lookup[data, "internal_dependency_edges", {}]);
 external = Sort @ ({Lookup[#, "from"], Lookup[#, "to"]} & /@
    Lookup[data, "external_dependency_edges", {}]);
 graph = Graph[ids, DirectedEdge @@@ internal];
 internal === expectedInternalEdges[] && external === expectedExternalEdges[] &&
  AcyclicGraphQ[graph] && Length[TopologicalSort[graph]] === Length[ids]
];
SharedFramePhotonDependencyGraphQ[_] := False;

SharedFramePhotonExactResiduals[] := Module[
 {bSq, mu, x, bet, gam, coeff, dop, muT, invCoeff, invDen,
  hp, kb, nu, temp, hgeom, see, be, axialGam, axialDop, axialMuT,
  s11, s12, s13, s22, s23, n11, n12, n13, n22, n23, n33,
  a1, a2, a3, om1, om2, om3, ee1, ee2, ee3,
  sMat, nMat, aVec, omVec, eVec, dirFlow, zeroShearRules},
 gam = 1/Sqrt[1 - bSq];
 coeff = gam + (gam - 1) mu/bSq;
 dop = gam (1 + mu);
 muT = FullSimplify[(mu + coeff bSq)/dop,
   Assumptions -> 0 < bSq < 1 && -Sqrt[bSq] <= mu <= Sqrt[bSq]];
 invCoeff = (gam - 1) muT/bSq - gam;
 invDen = gam (1 - muT);
 axialGam = 1/Sqrt[1 - bet^2]; axialDop = axialGam (1 + bet x);
 axialMuT = (x + bet)/(1 + bet x);
 sMat = {{s11, s12, s13}, {s12, s22, s23}, {s13, s23, -s11 - s22}};
 nMat = {{n11, n12, n13}, {n12, n22, n23}, {n13, n23, n33}};
 aVec = {a1, a2, a3}; omVec = {om1, om2, om3}; eVec = {ee1, ee2, ee3};
 see = Expand[eVec . sMat . eVec];
 dirFlow = Expand[(see + aVec . eVec) eVec - sMat . eVec - aVec +
   Cross[omVec, eVec] - Cross[eVec, nMat . eVec]];
 zeroShearRules = {s11 -> 0, s12 -> 0, s13 -> 0, s22 -> 0, s23 -> 0};
 <|
  "aberrated_direction_unit_norm" -> FullSimplify[
   (1 + 2 coeff mu + coeff^2 bSq)/dop^2 - 1,
   Assumptions -> 0 < bSq < 1 && -Sqrt[bSq] <= mu <= Sqrt[bSq]],
  "doppler_inverse_chart" -> FullSimplify[1/(gam (1 - muT)) - dop,
   Assumptions -> 0 < bSq < 1 && -Sqrt[bSq] <= mu <= Sqrt[bSq]],
  "deaberration_n_coefficient" -> FullSimplify[(1/dop)/invDen - 1,
   Assumptions -> 0 < bSq < 1 && -Sqrt[bSq] <= mu <= Sqrt[bSq]],
  "deaberration_beta_coefficient" -> FullSimplify[(coeff/dop + invCoeff)/invDen,
   Assumptions -> 0 < bSq < 1 && -Sqrt[bSq] <= mu <= Sqrt[bSq]],
  "solid_angle_jacobian" -> FullSimplify[D[axialMuT, x] - axialDop^-2,
   Assumptions -> -1 < bet < 1 && -1 <= x <= 1],
  "blackbody_planck_argument" -> FullSimplify[
   hp (dop nu)/(kb (dop temp)) - hp nu/(kb temp),
   Assumptions -> hp > 0 && kb > 0 && nu > 0 && temp > 0 && dop > 0],
  "outward_sky_adapter" -> Expand[gam (1 + (-be)) - gam (1 - be)],
  "direction_flow_tangency" -> FullSimplify[eVec . dirFlow,
   Assumptions -> ee1^2 + ee2^2 + ee3^2 == 1],
  "energy_drift_flrw" -> FullSimplify[((-hgeom - see) /. zeroShearRules) + hgeom],
  "energy_drift_minkowski" -> FullSimplify[
   (-hgeom - see) /. Join[{hgeom -> 0}, zeroShearRules]]
 |>
];

SharedFramePhotonExportQ[data_Association] := Module[
 {forms, ids, byID, hashes, predecessor, formulaChecks, registryProjection},
 forms = Lookup[data, "formulas", {}];
 ids = Lookup[forms, "formula_id", {}];
 byID = formulaMap[data];
 hashes = SharedFramePhotonExpectedSemanticHashes[];
 predecessor = Lookup[Lookup[data, "predecessors", <||>], "sync_map_02d", <||>];
 registryProjection = Lookup[data, "registry_semantic_projection", <||>];
 formulaChecks = And @@ Map[
   Function[id,
    With[{record = Lookup[byID, id, <||>],
      ir = Lookup[Lookup[byID, id, <||>], "equation_ir", <||>]},
     BASS`IR`EquationIRQ[ir] &&
     termSignature[ir] === Lookup[expectedTerms[], id] &&
     Lookup[Lookup[ir, "dimensions", <||>], "target", None] ===
      Lookup[expectedDimensions[], id] &&
     Lookup[record, "owner", None] === "bass" &&
     Lookup[record, "authority_effect", None] === "AUTHORITATIVE_DERIVATION" &&
     Lookup[record, "consumer_repositories", None] === Lookup[expectedConsumers[], id] &&
     Lookup[record, "dependencies", None] === Lookup[expectedDependencies[], id] &&
     Lookup[record, "external_dependencies", None] ===
      Lookup[expectedExternalDependencies[], id] &&
     Lookup[record, "allowed_consumer_modes", None] === {
      "PINNED_IMPORT", "INDEPENDENT_ORACLE", "ADAPTER_SPECIALIZATION"} &&
     Lookup[record, "semantic_projection", None] === semanticProjection[ir] &&
     Lookup[record, "semantic_hash", None] === Lookup[hashes, id] &&
     Lookup[record, "semantic_hash", None] ===
      BASS`IR`CanonicalSHA256[semanticProjection[ir]]
    ]], SharedFramePhotonFormulaIDs[]];
 And[
  Lookup[data, "schema_version", None] === "1.0.0",
  Lookup[data, "program_id", None] === "BIANCHI-WOLFRAM-FOUR-REPO-20260902",
  Lookup[data, "stage_id", None] === "SYNC_MAP_02E_SHARED_FRAME_PHOTON_EXPORT",
  Lookup[data, "owner", None] === "bass",
  Lookup[data, "source_repository", None] === "cosmosapjw-quantum/bass",
  Lookup[Lookup[data, "source_parent", <||>], "commit", None] ===
   "9e39e2468b9efec05f33b9945de02fe2c8c6a66d",
  Lookup[Lookup[data, "source_parent", <||>], "workflow_conclusion", None] === "success",
  Lookup[Lookup[Lookup[data, "predecessors", <||>], "sync_map_02c", <||>],
   "commit", None] === "9e39e2468b9efec05f33b9945de02fe2c8c6a66d",
  Lookup[Lookup[Lookup[data, "predecessors", <||>], "sync_map_02c", <||>],
   "workflow_conclusion", None] === "success",
  Lookup[data, "formula_count", None] === 6,
  Sort[ids] === SharedFramePhotonFormulaIDs[], DuplicateFreeQ[ids],
  Lookup[predecessor, "pre_repair_commit_superseded", None] ===
   "06aa29f78c26bcafeb60d85b719a4d3aa5c4c2e8",
  Lookup[predecessor, "commit", None] ===
   "6203b1343a6adb0f53d7abd0667e6d76b80fec53",
  Lookup[predecessor, "tree", None] ===
   "db49005f8dc77431dc4b76d67d8b7a242877fa46",
  Lookup[predecessor, "final_receipt_head", None] ===
   "7006aaab27834af37d5034f8f1e50943fe85c0f3",
  Lookup[Lookup[data, "wolfram_oracle", <||>], "inputform_sha256", None] ===
   "60ea9b894f955c2599628ae3ebf51b0e6d3a9ab2c512551fdef86e8c022f254b",
  Lookup[data, "registry_semantic_hash", None] ===
   "16f699043a7420c6e62abdad02434a216075ce55f69583b5051965ea53db5612",
  Lookup[data, "registry_semantic_hash", None] === BASS`IR`CanonicalSHA256[registryProjection],
  Lookup[data, "consumer_bindings", None] === expectedConsumers[],
  SharedFramePhotonDependencyGraphQ[data], scopeFirewallQ[data], claimBoundaryQ[data],
  formulaChecks,
  And @@ (TrueQ[# == 0] & /@ Values[SharedFramePhotonExactResiduals[]])
 ]
];
SharedFramePhotonExportQ[_] := False;

End[];
EndPackage[];
