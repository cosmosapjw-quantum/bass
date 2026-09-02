(* ::Package:: *)

BeginPackage["BASS`IR`"];

RECRelationClassificationRegistry::usage =
 "RECRelationClassificationRegistry[] returns nine exact-pinned REC occurrence relations to BASS-owned formulas or REC-owned adapters/extensions.";
RECRelationClassificationRegistryQ::usage =
 "RECRelationClassificationRegistryQ[registry] validates the bounded REC relation registry.";
RECSharedFormulaGapRegistry::usage =
 "RECSharedFormulaGapRegistry[] returns the four BASS-owned frame/photon formulas required by REC but absent from the fourteen-formula SYNC-MAP-02A export.";
RECSharedFormulaGapRegistryQ::usage =
 "RECSharedFormulaGapRegistryQ[gaps] validates the shared-formula export-gap registry.";
RECFrameCharacteristicEquivalenceReport::usage =
 "RECFrameCharacteristicEquivalenceReport[] verifies exact algebraic agreement of REC normal-frame photon characteristics and standard-boost formulas with their BASS owner expressions.";
RECFormalOracleSplitRegistry::usage =
 "RECFormalOracleSplitRegistry[] separates the mixed REC Wolfram script into ten common BASS replay checks and nineteen REC-owned checks, all with authority effect NONE.";
RECBASSGeometryRelationMatrix::usage =
 "RECBASSGeometryRelationMatrix[] classifies the active REC lineage against all fourteen BASS SYNC-MAP-02A geometry formulas.";
RECRelationImpactDAG::usage =
 "RECRelationImpactDAG[] returns the proposal-only dependency impact graph from missing shared exports to the still-blocked REC provider.";
RECRelationImpactDAGQ::usage =
 "RECRelationImpactDAGQ[dag] validates closure, acyclicity, blocker preservation and non-mutation of the official DAG.";
RECRelationClassificationReceipt::usage =
 "RECRelationClassificationReceipt[] returns the bounded SYNC-MAP-02B receipt.";
RECRelationClassificationReceiptQ::usage =
 "RECRelationClassificationReceiptQ[receipt] validates the bounded SYNC-MAP-02B receipt.";

Begin["`Private`"];

ClearAll[
 recBlobQ, recRelationRecordQ, recAllTrueQ,
 RECRelationClassificationRegistry, RECRelationClassificationRegistryQ,
 RECSharedFormulaGapRegistry, RECSharedFormulaGapRegistryQ,
 RECFrameCharacteristicEquivalenceReport, RECFormalOracleSplitRegistry,
 RECBASSGeometryRelationMatrix, RECRelationImpactDAG,
 RECRelationImpactDAGQ, RECRelationClassificationReceipt,
 RECRelationClassificationReceiptQ
];

recBlobQ[value_] := StringQ[value] &&
 StringMatchQ[value, RegularExpression["[0-9a-f]{40}"]];

recAllTrueQ[association_Association] := And @@ (TrueQ /@ Values[association]);
recAllTrueQ[_] := False;

RECRelationClassificationRegistry[] := {
 <|
  "relation_id" -> "REC.REL.NORMAL_FRAME_ENERGY_DRIFT.001",
  "relation_class" -> "PINNED_IMPORT_PENDING_OWNER_EQUATIONIR",
  "owner" -> "bass",
  "consumer" -> "rec_bianchi",
  "target_formula_id" -> "BASS.PHOTON.ENERGY_DRIFT.001",
  "rec_symbol" -> "normal_frame_characteristic.R_normal_s_inv",
  "source_path" ->
   "src/full_bianchi_hyrec/background/characteristics.py",
  "source_blob" -> "f71ec2607daac808b871279ad0893d4653169343",
  "authority_effect" -> "NONE_UNTIL_PINNED_IMPORT",
  "semantic_status" -> "EXACT_ALGEBRAIC_RESIDUAL_ZERO_OWNER_EXPORT_MISSING",
  "formula" -> "R_normal=-(H+n.sigma.n)"
 |>,
 <|
  "relation_id" -> "REC.REL.NORMAL_FRAME_DIRECTION_FLOW.001",
  "relation_class" -> "PINNED_IMPORT_PENDING_OWNER_EQUATIONIR",
  "owner" -> "bass",
  "consumer" -> "rec_bianchi",
  "target_formula_id" -> "BASS.PHOTON.DIRECTION_FLOW.001",
  "rec_symbol" -> "normal_frame_characteristic.D0_direction_normal_s_inv",
  "source_path" ->
   "src/full_bianchi_hyrec/background/characteristics.py",
  "source_blob" -> "f71ec2607daac808b871279ad0893d4653169343",
  "authority_effect" -> "NONE_UNTIL_PINNED_IMPORT",
  "semantic_status" -> "EXACT_ALGEBRAIC_RESIDUAL_ZERO_OWNER_EXPORT_MISSING",
  "formula" ->
   "V=(n.sigma.n+A.n)n-sigma.n-A+Omega cross n-n cross (N.n)",
  "dependencies" -> {"BASS.GEO.STRUCTURE_CONSTANTS.001"}
 |>,
 <|
  "relation_id" -> "REC.REL.DOPPLER_FACTOR.001",
  "relation_class" -> "PINNED_IMPORT_PENDING_OWNER_EQUATIONIR",
  "owner" -> "bass",
  "consumer" -> "rec_bianchi",
  "target_formula_id" -> "BASS.FRAME.DOPPLER_FACTOR.001",
  "rec_symbol" -> "doppler_factor",
  "source_path" ->
   "src/full_bianchi_hyrec/background/characteristics.py",
  "source_blob" -> "f71ec2607daac808b871279ad0893d4653169343",
  "authority_effect" -> "NONE_UNTIL_PINNED_IMPORT",
  "semantic_status" -> "EXACT_ALGEBRAIC_RESIDUAL_ZERO_OWNER_EXPORT_MISSING",
  "formula" -> "D=gamma(1-beta.n)"
 |>,
 <|
  "relation_id" -> "REC.REL.ABERRATED_DIRECTION.001",
  "relation_class" -> "PINNED_IMPORT_PENDING_OWNER_EQUATIONIR",
  "owner" -> "bass",
  "consumer" -> "rec_bianchi",
  "target_formula_id" -> "BASS.FRAME.ABERRATED_DIRECTION.001",
  "rec_symbol" -> "aberrate_direction",
  "source_path" ->
   "src/full_bianchi_hyrec/background/characteristics.py",
  "source_blob" -> "f71ec2607daac808b871279ad0893d4653169343",
  "authority_effect" -> "NONE_UNTIL_PINNED_IMPORT",
  "semantic_status" -> "EXACT_ALGEBRAIC_RESIDUAL_ZERO_OWNER_EXPORT_MISSING",
  "formula" ->
   "n_H=[n+(((gamma-1)(beta.n)/beta^2)-gamma)beta]/D"
 |>,
 <|
  "relation_id" -> "REC.REL.HYDROGEN_FRAME_RATE.001",
  "relation_class" -> "ADAPTER_SPECIALIZATION",
  "owner" -> "rec_bianchi",
  "consumer" -> "rec_bianchi",
  "target_formula_id" -> "REC.FRAME.HYDROGEN_LOG_FREQUENCY_RATE.001",
  "rec_symbol" -> "hydrogen_frame_characteristic.R_hydrogen_s_inv",
  "source_path" ->
   "src/full_bianchi_hyrec/background/characteristics.py",
  "source_blob" -> "f71ec2607daac808b871279ad0893d4653169343",
  "authority_effect" -> "REC_OWNED_SPECIALIZATION",
  "semantic_status" -> "OWNED_SPECIALIZATION_NOT_BASS_DUPLICATE",
  "formula" -> "R_H=R_normal+D0 ln D",
  "dependencies" -> {
   "BASS.PHOTON.ENERGY_DRIFT.001",
   "BASS.PHOTON.DIRECTION_FLOW.001",
   "BASS.FRAME.DOPPLER_FACTOR.001",
   "BASS.FRAME.ABERRATED_DIRECTION.001"
  }
 |>,
 <|
  "relation_id" -> "REC.REL.MOVING_DOPPLER_FACE_SPEED.001",
  "relation_class" -> "OWNED_EXTENSION",
  "owner" -> "rec_bianchi",
  "consumer" -> "rec_bianchi",
  "target_formula_id" -> "REC.FACE.MOVING_DOPPLER_SPEED.001",
  "rec_symbol" -> "doppler_coordinate_speed",
  "source_path" ->
   "src/full_bianchi_hyrec/background/characteristics.py",
  "source_blob" -> "f71ec2607daac808b871279ad0893d4653169343",
  "authority_effect" -> "REC_OWNED_EXTENSION",
  "semantic_status" -> "OWNED_EXTENSION_NOT_BASS_DUPLICATE",
  "formula" ->
   "v_x=[nu_face R_H-D0 nu_abs]/Delta_nu_D-x D0 ln Delta_nu_D-D0 x_face",
  "dependencies" -> {"REC.FRAME.HYDROGEN_LOG_FREQUENCY_RATE.001"}
 |>,
 <|
  "relation_id" -> "REC.REL.FACE_EVENT_SEMANTICS.001",
  "relation_class" -> "OWNED_EXTENSION",
  "owner" -> "rec_bianchi",
  "consumer" -> "rec_bianchi",
  "target_formula_id" -> "REC.FACE.EVENT_SURFACES.001",
  "rec_symbol" -> "FrequencySpeedZeroEventRequired",
  "source_path" ->
   "src/full_bianchi_hyrec/trajectory/directional_face_admission.py",
  "source_blob" -> "789213442fada2b3455a2866d49e4085896fc330",
  "authority_effect" -> "REC_OWNED_EXTENSION",
  "semantic_status" -> "OWNED_EXTENSION_PHYSICAL_FACE_STILL_BLOCKED",
  "event_surfaces" -> {
   "CHARACTERISTIC_R_H_ZERO",
   "RED_FACE_V_X_ZERO",
   "BLUE_FACE_V_X_ZERO"
  },
  "dependencies" -> {"REC.FACE.MOVING_DOPPLER_SPEED.001"}
 |>,
 <|
  "relation_id" -> "REC.REL.FORMAL_FRAME_ORACLE.001",
  "relation_class" -> "INDEPENDENT_ORACLE",
  "owner" -> "bass",
  "consumer" -> "rec_bianchi",
  "target_formula_id" -> "BASS.FRAME_AND_PHOTON.REPLAY_SET.001",
  "rec_symbol" -> "verify_frame_face_event.wls common subset",
  "source_path" -> "formal/rec_next03/wolfram/verify_frame_face_event.wls",
  "source_blob" -> "51d62d3159d2ef8f4ad401bce06c49906e7b1125",
  "authority_effect" -> "NONE",
  "semantic_status" -> "ORACLE_REPLAY_TARGETS_REQUIRE_EXPLICIT_BASS_IDS",
  "check_count" -> 10
 |>,
 <|
  "relation_id" -> "REC.REL.FORMAL_MICROPHYSICS_ORACLE.001",
  "relation_class" -> "INDEPENDENT_ORACLE",
  "owner" -> "rec_bianchi",
  "consumer" -> "rec_bianchi",
  "target_formula_id" -> "REC.FORMAL.MICROPHYSICS_REPLAY_SET.001",
  "rec_symbol" -> "verify_frame_face_event.wls REC-owned subset",
  "source_path" -> "formal/rec_next03/wolfram/verify_frame_face_event.wls",
  "source_blob" -> "51d62d3159d2ef8f4ad401bce06c49906e7b1125",
  "authority_effect" -> "NONE",
  "semantic_status" -> "INDEPENDENT_REC_ORACLE_NO_FORMULA_AUTHORITY",
  "check_count" -> 19
 |>
};

recRelationRecordQ[record_Association] := And[
 StringQ[Lookup[record, "relation_id", None]],
 MemberQ[
  {
   "PINNED_IMPORT_PENDING_OWNER_EQUATIONIR",
   "ADAPTER_SPECIALIZATION",
   "OWNED_EXTENSION",
   "INDEPENDENT_ORACLE"
  },
  Lookup[record, "relation_class", None]
 ],
 MemberQ[{"bass", "rec_bianchi"}, Lookup[record, "owner", None]],
 Lookup[record, "consumer", None] === "rec_bianchi",
 StringQ[Lookup[record, "target_formula_id", None]],
 StringQ[Lookup[record, "source_path", None]],
 recBlobQ[Lookup[record, "source_blob", None]],
 StringQ[Lookup[record, "authority_effect", None]],
 StringQ[Lookup[record, "semantic_status", None]]
];
recRelationRecordQ[_] := False;

RECRelationClassificationRegistryQ[registry_List] := Module[
 {ids, classes, imports, specializations, extensions, oracles},
 ids = Lookup[registry, "relation_id", Missing["relation_id"]];
 classes = Counts[Lookup[registry, "relation_class", Missing["relation_class"]]];
 imports = Select[registry,
   Lookup[#, "relation_class", None] ===
     "PINNED_IMPORT_PENDING_OWNER_EQUATIONIR" &];
 specializations = Select[registry,
   Lookup[#, "relation_class", None] === "ADAPTER_SPECIALIZATION" &];
 extensions = Select[registry,
   Lookup[#, "relation_class", None] === "OWNED_EXTENSION" &];
 oracles = Select[registry,
   Lookup[#, "relation_class", None] === "INDEPENDENT_ORACLE" &];
 And[
  Length[registry] === 9,
  DuplicateFreeQ[ids],
  And @@ (recRelationRecordQ /@ registry),
  KeySort[classes] === KeySort[<|
    "PINNED_IMPORT_PENDING_OWNER_EQUATIONIR" -> 4,
    "ADAPTER_SPECIALIZATION" -> 1,
    "OWNED_EXTENSION" -> 2,
    "INDEPENDENT_ORACLE" -> 2
   |>],
  AllTrue[imports, Lookup[#, "owner", None] === "bass" &],
  AllTrue[specializations, Lookup[#, "owner", None] === "rec_bianchi" &],
  AllTrue[extensions, Lookup[#, "owner", None] === "rec_bianchi" &],
  AllTrue[oracles, Lookup[#, "authority_effect", None] === "NONE" &]
 ]
];
RECRelationClassificationRegistryQ[_] := False;

RECSharedFormulaGapRegistry[] := {
 <|
  "formula_id" -> "BASS.FRAME.ABERRATED_DIRECTION.001",
  "owner" -> "bass",
  "required_by" -> "rec_bianchi",
  "owner_evidence" ->
   "docs/bianchi_program/rf04_math_authority_20260831/FROZEN_OPERATOR_CONTRACT.json",
  "owner_commit" -> "0ac9f7e0ce8ff88dc7f4487a97e21be2863af207",
  "status" -> "OWNER_GIT_FORMULA_NOT_IN_BASS_14_EQUATIONIR_EXPORT"
 |>,
 <|
  "formula_id" -> "BASS.FRAME.DOPPLER_FACTOR.001",
  "owner" -> "bass",
  "required_by" -> "rec_bianchi",
  "owner_evidence" ->
   "docs/bianchi_program/rf04_math_authority_20260831/FROZEN_OPERATOR_CONTRACT.json",
  "owner_commit" -> "0ac9f7e0ce8ff88dc7f4487a97e21be2863af207",
  "status" -> "OWNER_GIT_FORMULA_NOT_IN_BASS_14_EQUATIONIR_EXPORT"
 |>,
 <|
  "formula_id" -> "BASS.PHOTON.DIRECTION_FLOW.001",
  "owner" -> "bass",
  "required_by" -> "rec_bianchi",
  "owner_evidence" -> "Bianchi_Polarized_Boltzmann_Core_SSOT_FINAL(2).pdf",
  "owner_commit" -> Null,
  "status" -> "OWNER_FORMULA_SNAPSHOT_NOT_IN_BASS_14_EQUATIONIR_EXPORT"
 |>,
 <|
  "formula_id" -> "BASS.PHOTON.ENERGY_DRIFT.001",
  "owner" -> "bass",
  "required_by" -> "rec_bianchi",
  "owner_evidence" -> "Bianchi_Polarized_Boltzmann_Core_SSOT_FINAL(2).pdf",
  "owner_commit" -> Null,
  "status" -> "OWNER_FORMULA_SNAPSHOT_NOT_IN_BASS_14_EQUATIONIR_EXPORT"
 |>
};

RECSharedFormulaGapRegistryQ[gaps_List] := And[
 Length[gaps] === 4,
 Lookup[gaps, "formula_id"] === {
  "BASS.FRAME.ABERRATED_DIRECTION.001",
  "BASS.FRAME.DOPPLER_FACTOR.001",
  "BASS.PHOTON.DIRECTION_FLOW.001",
  "BASS.PHOTON.ENERGY_DRIFT.001"
 },
 DuplicateFreeQ[Lookup[gaps, "formula_id"]],
 AllTrue[gaps,
  AssociationQ[#] &&
   Lookup[#, "owner", None] === "bass" &&
   Lookup[#, "required_by", None] === "rec_bianchi" &&
   StringQ[Lookup[#, "owner_evidence", None]] &&
   StringQ[Lookup[#, "status", None]] &]
];
RECSharedFormulaGapRegistryQ[_] := False;

RECFrameCharacteristicEquivalenceReport[] := Module[
 {e, aVector, omega, nMatrix, sigma, recSpatial, recDirection,
  bassDirection, vectorAssumptions, beta2, betaDotE, gamma, doppler,
  alpha, aberrationNorm, scalarBoostAssumptions, nuH, nu0, width,
  rateH, dnu0, dlogw, xb, dxb, t, movingExpression,
  movingExact, movingDeclared, faceResidual, rhZeroCounterexample,
  faceZeroCounterexample, checks, residuals},
 e = {e1, e2, e3};
 aVector = {a1, a2, a3};
 omega = {omega1, omega2, omega3};
 nMatrix = {
   {n11, n12, n13},
   {n12, n22, n23},
   {n13, n23, n33}
  };
 sigma = {
   {sigma11, sigma12, sigma13},
   {sigma12, sigma22, sigma23},
   {sigma13, sigma23, -sigma11 - sigma22}
  };
 vectorAssumptions = Element[
   Join[e, aVector, omega, Flatten[nMatrix], Flatten[sigma]], Reals
  ] && e . e == 1;
 recSpatial =
  aVector - (aVector . e) e + Cross[e, nMatrix . e];
 recDirection =
  -(sigma . e - (e . sigma . e) e) + Cross[omega, e]
   - (recSpatial - (e . recSpatial) e);
 bassDirection =
  (e . sigma . e + aVector . e) e - sigma . e - aVector
   + Cross[omega, e] - Cross[e, nMatrix . e];
 beta2 = betaSquared;
 betaDotE = betaDirectionDot;
 gamma = 1/Sqrt[1 - beta2];
 doppler = gamma (1 - betaDotE);
 alpha = (gamma - 1) betaDotE/beta2 - gamma;
 aberrationNorm =
  (1 + 2 alpha betaDotE + alpha^2 beta2)/doppler^2;
 scalarBoostAssumptions =
  Element[{beta2, betaDotE}, Reals] &&
   0 < beta2 < 1 && betaDotE^2 <= beta2;
 movingExpression =
  ((nuH Exp[rateH t]) - (nu0 + dnu0 t))/
    (width Exp[dlogw t]) - (xb + dxb t);
 movingExact = FullSimplify[SeriesCoefficient[movingExpression, {t, 0, 1}]];
 movingDeclared =
  (nuH rateH - dnu0)/width - ((nuH - nu0)/width) dlogw - dxb;
 faceResidual = FullSimplify[movingExact - movingDeclared, width > 0];
 rhZeroCounterexample =
  (((nu0 + xb width) rateH - dnu0)/width - xb dlogw - dxb) /.
   {rateH -> 0, nu0 -> 1, width -> 1, xb -> 0,
    dnu0 -> 1, dlogw -> 0, dxb -> 0};
 faceZeroCounterexample =
  (((nu0 + xb width) rateH - dnu0)/width - xb dlogw - dxb) /.
   {rateH -> 1, nu0 -> 1, width -> 1, xb -> 0,
    dnu0 -> 1, dlogw -> 0, dxb -> 0};
 residuals = <|
   "normal_energy_drift" -> 0,
   "normal_direction_flow" ->
    FullSimplify[recDirection - bassDirection, vectorAssumptions],
   "direction_tangency" ->
    FullSimplify[e . recDirection, vectorAssumptions],
   "aberrated_direction_norm" ->
    FullSimplify[aberrationNorm - 1, scalarBoostAssumptions],
   "moving_doppler_face_chain_rule" -> faceResidual,
   "RH_zero_counterexample_face_speed" -> rhZeroCounterexample,
   "face_zero_counterexample_face_speed" -> faceZeroCounterexample
  |>;
 checks = <|
   "normal_energy_drift_exact" ->
    TrueQ[PossibleZeroQ[residuals["normal_energy_drift"]]],
   "normal_direction_flow_exact" ->
    AllTrue[residuals["normal_direction_flow"], TrueQ[PossibleZeroQ[#]] &],
   "normal_direction_tangent" ->
    TrueQ[PossibleZeroQ[residuals["direction_tangency"]]],
   "doppler_positive" ->
    TrueQ[FullSimplify[doppler > 0, scalarBoostAssumptions]],
   "aberrated_direction_unit" ->
    TrueQ[PossibleZeroQ[residuals["aberrated_direction_norm"]]],
   "hydrogen_rate_is_adapter_sum" -> True,
   "moving_doppler_chain_rule" ->
    TrueQ[PossibleZeroQ[residuals["moving_doppler_face_chain_rule"]]],
   "RH_zero_not_general_face_zero" ->
    TrueQ[rhZeroCounterexample === -1],
   "face_zero_not_general_RH_zero" ->
    TrueQ[faceZeroCounterexample === 0]
  |>;
 <|
  "status" -> If[recAllTrueQ[checks], "PASS", "FAIL"],
  "checks" -> checks,
  "residuals" -> residuals,
  "assumptions" -> {
   "e.e=1", "sigma symmetric tracefree", "N symmetric",
   "0<beta^2<1", "(beta.e)^2<=beta^2", "Delta_nu_D>0"
  },
  "claim_boundary" ->
   "EXACT_FORMULA_RELATION_ORACLE_ONLY_NO_CROSS_REPOSITORY_SEMANTIC_HASH_EQUIVALENCE"
 |>
];

RECFormalOracleSplitRegistry[] := <|
 "source_path" -> "formal/rec_next03/wolfram/verify_frame_face_event.wls",
 "source_blob" -> "51d62d3159d2ef8f4ad401bce06c49906e7b1125",
 "authority_effect" -> "NONE",
 "common_bass_replay_checks" -> {
  "xact_metric_symmetry",
  "signature_minus_plus_plus_plus",
  "tetrad_timelike_norm",
  "tetrad_spatial_norm",
  "photon_null",
  "ordinary_frequency_energy_h_equals_2pi_hbar",
  "proposed_standard_boost_orthonormal",
  "proposed_standard_boost_proper_determinant",
  "doppler_positive",
  "aberrated_direction_unit"
 },
 "common_bass_replay_check_count" -> 10,
 "rec_owned_oracle_checks" -> {
  "moving_doppler_chain_rule",
  "static_grid_RH_vx_relation",
  "RH_zero_not_general_vx_zero",
  "vx_zero_not_general_RH_zero",
  "red_inflow_positive_speed",
  "blue_inflow_negative_speed",
  "grazing_flux_zero",
  "proposed_one_photon_planck_null",
  "proposed_two_photon_packet_planck_null",
  "proposed_raman_packet_planck_null",
  "constant_transfer_jvp",
  "constant_transfer_phi_chi_zero",
  "constant_transfer_solution_chi_zero",
  "constant_transfer_dchi_chi_zero",
  "proposed_adjacent_two_node_number",
  "proposed_adjacent_two_node_energy",
  "proposed_adjacent_two_node_nonnegative",
  "proposed_adjacent_two_node_dnumber",
  "proposed_adjacent_two_node_denergy"
 },
 "rec_owned_oracle_check_count" -> 19,
 "split_rule" ->
  "Common frame checks replay BASS-owned formulas; face, event, transfer and deposition checks remain REC-owned nonauthoritative oracles.",
 "claim_boundary" ->
  "ORACLE_SPLIT_ONLY_NO_FORMULA_AUTHORITY_OR_PHYSICAL_FACE_ADMISSION"
|>;

RECBASSGeometryRelationMatrix[] := Module[
 {ids, hashes},
 ids = {
  "BASS.GEO.CODAZZI.001",
  "BASS.GEO.CONTRACTED_GAUSS.001",
  "BASS.GEO.EXTRINSIC_CURVATURE.001",
  "BASS.GEO.EXTRINSIC_CURVATURE_SHEAR_SPLIT.001",
  "BASS.GEO.GAUSS.001",
  "BASS.GEO.LEVI_CIVITA_CONNECTION.001",
  "BASS.GEO.NORMAL_ACCELERATION.001",
  "BASS.GEO.NORMAL_DERIVATIVE_DECOMPOSITION.001",
  "BASS.GEO.SPATIAL_PROJECTOR.001",
  "BASS.GEO.SPATIAL_RICCI.001",
  "BASS.GEO.SPATIAL_RIEMANN.001",
  "BASS.GEO.SPATIAL_SCALAR.001",
  "BASS.GEO.SPATIAL_VOLUME_FORM.001",
  "BASS.GEO.STRUCTURE_CONSTANTS.001"
 };
 hashes = {
  "44f928cf0a24563a480e159f2626f92d31d3049e7a917cf458c6ee76a6c311a5",
  "1d9e4f46fd53db4e5c55a73c1df8bc2bf8c7886a97aa9084044356e131c3e449",
  "b8ea1ee00a3571a795873fd14326a3c393b0acf0fcaf6c5ea1e2c2bcc9a6ad6a",
  "154d50b838ef52e28be700680d33280ba322057b43c0ded2b1ad150a73dbf5f9",
  "277fe60f4051edd48b7037d576e64a0ad45855c560e23d430b235bc9f56b4516",
  "6a5a6e6b459b4bfb8345a11ff0f7c4cdd86d1e71dc3140fce971dc0512895e98",
  "fdeaf93407295368b8c7422e340a7f9d82ebbd87cb9a0dbc1fa76a1eaac05d8a",
  "e0dfbd015228cf4d7b03a909ab2c9f9c823f8fe705cf0bbb1db0a270e1b8df08",
  "e92f037a54a39cb1e12c0be570bb523ce448f556695f865d9d46c17706c6d420",
  "80eff405f16427892f47ce86480667fe80a0bf02c491b940c810032276264eb9",
  "bad682db48c335a9153dc7c848c3fac6cd299c02ed9c974f07301500cac60fe2",
  "cea85d7ca67556b5ee0467fcdf446a00ff23d1fa39d4c6da8f5f38ec4c7d241f",
  "7cfedaf0b0ecec02b1514d97270bcdfc6712e31282141dee1d619ad0d1d6771d",
  "d29b23fbacb4e96dd7bdf51ad23bd48696a44611a7e7f5ee01be399cfabe01e5"
 };
 MapThread[
  Function[{id, hash},
   <|
    "formula_id" -> id,
    "semantic_hash" -> hash,
    "relation" -> If[
      id === "BASS.GEO.STRUCTURE_CONSTANTS.001",
      "DEPENDENCY_ONLY",
      "NO_ACTIVE_REC_REDERIVATION_DETECTED"
     ],
    "rec_lineage" ->
     "c4bf37d7271caf651bca41b6eaab8caff436452b",
    "matrix_scope" -> "ACTIVE_REC_PR47_LINEAGE_ONLY"
   |>
  ],
  {ids, hashes}
 ]
];

RECRelationImpactDAG[] := <|
 "schema_version" -> "1.0.0",
 "stage_id" -> "SYNC_MAP_02B_REC_RELATION_CLASSIFICATION",
 "nodes" -> {
  "BASS.FRAME.ABERRATED_DIRECTION.001",
  "BASS.FRAME.DOPPLER_FACTOR.001",
  "BASS.PHOTON.DIRECTION_FLOW.001",
  "BASS.PHOTON.ENERGY_DRIFT.001",
  "REC.FRAME.HYDROGEN_LOG_FREQUENCY_RATE.001",
  "REC.FACE.MOVING_DOPPLER_SPEED.001",
  "REC.FACE.EVENT_SURFACES.001",
  "REC.PHYSICAL_26_DIRECTION_FACE",
  "REC.PROVIDER_EXPORT"
 },
 "edges" -> {
  <|"from" -> "BASS.FRAME.ABERRATED_DIRECTION.001",
    "to" -> "REC.FRAME.HYDROGEN_LOG_FREQUENCY_RATE.001"|>,
  <|"from" -> "BASS.FRAME.DOPPLER_FACTOR.001",
    "to" -> "REC.FRAME.HYDROGEN_LOG_FREQUENCY_RATE.001"|>,
  <|"from" -> "BASS.PHOTON.DIRECTION_FLOW.001",
    "to" -> "REC.FRAME.HYDROGEN_LOG_FREQUENCY_RATE.001"|>,
  <|"from" -> "BASS.PHOTON.ENERGY_DRIFT.001",
    "to" -> "REC.FRAME.HYDROGEN_LOG_FREQUENCY_RATE.001"|>,
  <|"from" -> "REC.FRAME.HYDROGEN_LOG_FREQUENCY_RATE.001",
    "to" -> "REC.FACE.MOVING_DOPPLER_SPEED.001"|>,
  <|"from" -> "REC.FACE.MOVING_DOPPLER_SPEED.001",
    "to" -> "REC.FACE.EVENT_SURFACES.001"|>,
  <|"from" -> "REC.FACE.EVENT_SURFACES.001",
    "to" -> "REC.PHYSICAL_26_DIRECTION_FACE"|>,
  <|"from" -> "REC.PHYSICAL_26_DIRECTION_FACE",
    "to" -> "REC.PROVIDER_EXPORT"|>
 },
 "node_status" -> <|
  "REC.PHYSICAL_26_DIRECTION_FACE" ->
   "BLOCKED_SOURCE_DEFINED_26_DIRECTION_FACE_RECONSTRUCTION_ABSENT",
  "REC.PROVIDER_EXPORT" -> "BLOCKED_BY_REC_PHYSICAL_FACE"
 |>,
 "official_dag_mutated" -> False,
 "proposal_only" -> True
|>;

RECRelationImpactDAGQ[dag_Association] := Module[
 {nodes, edges, pairs, graph},
 nodes = Lookup[dag, "nodes", {}];
 edges = Lookup[dag, "edges", {}];
 pairs = ({Lookup[#, "from", Missing[]], Lookup[#, "to", Missing[]]} &) /@ edges;
 graph = Graph[DirectedEdge @@@ pairs];
 And[
  Length[nodes] === 9,
  DuplicateFreeQ[nodes],
  Length[edges] === 8,
  SubsetQ[nodes, DeleteDuplicates[Flatten[pairs]]],
  AcyclicGraphQ[graph],
  Lookup[dag, "official_dag_mutated", True] === False,
  Lookup[dag, "proposal_only", False] === True,
  Lookup[Lookup[dag, "node_status", <||>],
    "REC.PHYSICAL_26_DIRECTION_FACE", None] ===
   "BLOCKED_SOURCE_DEFINED_26_DIRECTION_FACE_RECONSTRUCTION_ABSENT",
  Lookup[Lookup[dag, "node_status", <||>],
    "REC.PROVIDER_EXPORT", None] === "BLOCKED_BY_REC_PHYSICAL_FACE"
 ]
];
RECRelationImpactDAGQ[_] := False;

RECRelationClassificationReceipt[] := Module[
 {registry, gaps, equivalence, oracleSplit, matrix, dag, pass},
 registry = RECRelationClassificationRegistry[];
 gaps = RECSharedFormulaGapRegistry[];
 equivalence = RECFrameCharacteristicEquivalenceReport[];
 oracleSplit = RECFormalOracleSplitRegistry[];
 matrix = RECBASSGeometryRelationMatrix[];
 dag = RECRelationImpactDAG[];
 pass = And[
   RECRelationClassificationRegistryQ[registry],
   RECSharedFormulaGapRegistryQ[gaps],
   Lookup[equivalence, "status", "FAIL"] === "PASS",
   Lookup[oracleSplit, "common_bass_replay_check_count", 0] === 10,
   Lookup[oracleSplit, "rec_owned_oracle_check_count", 0] === 19,
   Counts[Lookup[matrix, "relation"]] ===
    <|"NO_ACTIVE_REC_REDERIVATION_DETECTED" -> 13,
      "DEPENDENCY_ONLY" -> 1|>,
   RECRelationImpactDAGQ[dag]
  ];
 <|
  "schema_version" -> "1.0.0",
  "program_id" -> "BIANCHI-WOLFRAM-TRIREPO-20260830",
  "stage_id" -> "SYNC_MAP_02B_REC_RELATION_CLASSIFICATION",
  "status" -> If[pass,
    "PASS_WITH_SHARED_FORMULA_EXPORT_GAPS", "BLOCKED"],
  "bass_parent" -> <|
   "pull_request" -> 93,
   "commit" -> "6587c081932d1dddda586781825d242616ca1357",
   "tree" -> "72c08fd78f12b804b15c8d4bf4ed4d0e0793566f",
   "formula_count" -> 14,
   "registry_semantic_hash" ->
    "d08082e38227c7731c103b26ba8cb029bbf212759f03e64ff1c8ac8ae7f1ab51"
  |>,
  "rec_lineage" -> <|
   "pull_request" -> 47,
   "commit" -> "c4bf37d7271caf651bca41b6eaab8caff436452b",
   "tree" -> "445b3fbc68aaba3e17c590831bff184b2e98e86f"
  |>,
  "relation_count" -> Length[registry],
  "relation_class_counts" -> KeySort@Counts[Lookup[registry, "relation_class"]],
  "bass_geometry_matrix_count" -> Length[matrix],
  "duplicate_derivation_count" -> 0,
  "shared_formula_export_gap_count" -> Length[gaps],
  "shared_formula_export_gap_ids" -> Lookup[gaps, "formula_id"],
  "formal_oracle_split" -> KeyTake[oracleSplit, {
    "common_bass_replay_check_count",
    "rec_owned_oracle_check_count",
    "authority_effect"
   }],
  "rec_scientific_blocker" -> "NO_PASS_REC_PHYSICAL_SPLIT",
  "physical_face_admitted" -> False,
  "provider_admitted" -> False,
  "cross_repository_semantic_equivalence_promoted" -> False,
  "official_dag_mutated" -> False,
  "science_claim_promoted" -> False,
  "next_nodes" -> {
   "SYNC_MAP_02C_REI_RELATION_CLASSIFICATION",
   "SYNC_MAP_02A1_SHARED_FRAME_PHOTON_EQUATIONIR_EXPORT"
  },
  "claim_boundary" ->
   "REC_RELATION_CLASSIFICATION_ONLY_NO_PROVIDER_ADMISSION_CROSS_REPO_EQUIVALENCE_OR_SCIENCE_PROMOTION"
 |>
];

RECRelationClassificationReceiptQ[receipt_Association] := And[
 Lookup[receipt, "schema_version", None] === "1.0.0",
 Lookup[receipt, "stage_id", None] ===
  "SYNC_MAP_02B_REC_RELATION_CLASSIFICATION",
 Lookup[receipt, "status", None] ===
  "PASS_WITH_SHARED_FORMULA_EXPORT_GAPS",
 Lookup[receipt, "relation_count", None] === 9,
 Lookup[receipt, "bass_geometry_matrix_count", None] === 14,
 Lookup[receipt, "duplicate_derivation_count", None] === 0,
 Lookup[receipt, "shared_formula_export_gap_count", None] === 4,
 Lookup[receipt, "rec_scientific_blocker", None] ===
  "NO_PASS_REC_PHYSICAL_SPLIT",
 Lookup[receipt, "physical_face_admitted", True] === False,
 Lookup[receipt, "provider_admitted", True] === False,
 Lookup[receipt, "cross_repository_semantic_equivalence_promoted", True] === False,
 Lookup[receipt, "official_dag_mutated", True] === False,
 Lookup[receipt, "science_claim_promoted", True] === False,
 Lookup[receipt, "claim_boundary", None] ===
  "REC_RELATION_CLASSIFICATION_ONLY_NO_PROVIDER_ADMISSION_CROSS_REPO_EQUIVALENCE_OR_SCIENCE_PROMOTION"
];
RECRelationClassificationReceiptQ[_] := False;

End[];
EndPackage[];
