(* ::Package:: *)

BeginPackage["BASS`IR`"];

RECFrameCharacteristicAdversarialReport::usage =
 "RECFrameCharacteristicAdversarialReport[] checks that wrong energy-drift sign and wrong hydrogen-adapter coefficient mutations are detected.";

Begin["`Private`"];

ClearAll[
 RECFrameCharacteristicEquivalenceReport,
 RECFrameCharacteristicAdversarialReport,
 RECRelationImpactDAGQ
];

RECFrameCharacteristicEquivalenceReport[] := Module[
 {e, aVector, omega, nMatrix, sigma, recSpatial, recDirection,
  bassDirection, vectorAssumptions, recEnergy, bassEnergy,
  dlogD, recHydrogen, ownerHydrogen, beta2, betaDotE, gamma,
  doppler, alpha, aberrationNorm, scalarBoostAssumptions,
  nuH, nu0, width, rateH, dnu0, dlogw, xb, dxb, t,
  movingExpression, movingExact, movingDeclared, faceResidual,
  rhZeroCounterexample, faceZeroCounterexample, checks, residuals},
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
   Join[e, aVector, omega, Flatten[nMatrix], Flatten[sigma], {H, dlogD}],
   Reals
  ] && e . e == 1;
 recSpatial = aVector - (aVector . e) e + Cross[e, nMatrix . e];
 recDirection =
  -(sigma . e - (e . sigma . e) e) + Cross[omega, e]
   - (recSpatial - (e . recSpatial) e);
 bassDirection =
  (e . sigma . e + aVector . e) e - sigma . e - aVector
   + Cross[omega, e] - Cross[e, nMatrix . e];
 recEnergy = -(H + e . sigma . e);
 bassEnergy = -H - e . sigma . e;
 recHydrogen = recEnergy + dlogD;
 ownerHydrogen = bassEnergy + dlogD;
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
   "normal_energy_drift" ->
    FullSimplify[recEnergy - bassEnergy, vectorAssumptions],
   "normal_direction_flow" ->
    FullSimplify[recDirection - bassDirection, vectorAssumptions],
   "direction_tangency" ->
    FullSimplify[e . recDirection, vectorAssumptions],
   "aberrated_direction_norm" ->
    FullSimplify[aberrationNorm - 1, scalarBoostAssumptions],
   "hydrogen_adapter" ->
    FullSimplify[recHydrogen - ownerHydrogen, vectorAssumptions],
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
   "hydrogen_rate_is_adapter_sum" ->
    TrueQ[PossibleZeroQ[residuals["hydrogen_adapter"]]],
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

RECFrameCharacteristicAdversarialReport[] := Module[
 {e, sigma, correctEnergy, wrongEnergy, dlogD,
  correctHydrogen, wrongHydrogen, witnessRules,
  wrongEnergyResidual, wrongHydrogenResidual},
 e = {e1, e2, e3};
 sigma = {
   {sigma11, sigma12, sigma13},
   {sigma12, sigma22, sigma23},
   {sigma13, sigma23, -sigma11 - sigma22}
  };
 correctEnergy = -H - e . sigma . e;
 wrongEnergy = H + e . sigma . e;
 correctHydrogen = correctEnergy + dlogD;
 wrongHydrogen = correctEnergy + 2 dlogD;
 witnessRules = {
  H -> 2, e1 -> 1, e2 -> 0, e3 -> 0,
  sigma11 -> 1, sigma22 -> -1, sigma12 -> 0,
  sigma13 -> 0, sigma23 -> 0, dlogD -> 1
 };
 wrongEnergyResidual = Simplify[(wrongEnergy - correctEnergy) /. witnessRules];
 wrongHydrogenResidual =
  Simplify[(wrongHydrogen - correctHydrogen) /. witnessRules];
 <|
  "wrong_energy_sign_residual" -> wrongEnergyResidual,
  "wrong_energy_sign_detected" -> Not@TrueQ[PossibleZeroQ[wrongEnergyResidual]],
  "wrong_hydrogen_adapter_coefficient_residual" -> wrongHydrogenResidual,
  "wrong_hydrogen_adapter_coefficient_detected" ->
   Not@TrueQ[PossibleZeroQ[wrongHydrogenResidual]],
  "claim_boundary" -> "ADVERSARIAL_ORACLE_ONLY"
 |>
];

RECRelationImpactDAGQ[dag_Association] := Module[
 {nodes, edges, pairs, endpoints, graph},
 nodes = Lookup[dag, "nodes", {}];
 edges = Lookup[dag, "edges", {}];
 If[!ListQ[nodes] || !ListQ[edges], Return[False]];
 pairs = ({Lookup[#, "from", Missing[]], Lookup[#, "to", Missing[]]} &) /@ edges;
 endpoints = DeleteDuplicates[Flatten[pairs]];
 graph = Graph[DirectedEdge @@@ pairs];
 And[
  Length[nodes] === 9,
  DuplicateFreeQ[nodes],
  Length[edges] === 8,
  Sort[endpoints] === Sort[nodes],
  AllTrue[pairs, MatchQ[#, {_String, _String}] &],
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

End[];
EndPackage[];
