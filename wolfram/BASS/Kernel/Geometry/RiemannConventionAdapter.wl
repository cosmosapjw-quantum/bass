(* ::Package:: *)

BeginPackage["BASS`Geometry`"];

XActRiemannConventionAdapter::usage =
 "XActRiemannConventionAdapter[] returns the exact sign/index adapter from the loaded xTensor convention to the BASS project convention.";
RiemannConventionAdapterQ::usage =
 "RiemannConventionAdapterQ[adapter] validates the ALG-01 xAct/project convention receipt.";

Begin["`Private`"];

ClearAll[xActValue, XActRiemannConventionAdapter,
 RiemannConventionAdapterQ];

xActValue[name_String] :=
 If[NameQ[name], ToExpression[name], Missing["NotLoaded", name]];

XActRiemannConventionAdapter[] := Module[
 {loaded, version, riemannSign, ricciSign, torsionSign, epsilonSign, factor},
 loaded = MemberQ[$Packages, "xAct`xTensor`"];
 version = xActValue["xAct`xTensor`$Version"];
 riemannSign = xActValue["xAct`xTensor`$RiemannSign"];
 ricciSign = xActValue["xAct`xTensor`$RicciSign"];
 torsionSign = xActValue["xAct`xTensor`$TorsionSign"];
 epsilonSign = xActValue["xAct`xTensor`$epsilonSign"];
 factor = If[IntegerQ[riemannSign], -riemannSign, Missing["NotLoaded"]];
 <|
  "schema_version" -> "1.0.0",
  "stage_id" -> "ALG_01",
  "status" -> If[loaded && IntegerQ[factor], "PASS", "BLOCKED"],
  "xact_xtensor_loaded" -> loaded,
  "xact_xtensor_version" -> version,
  "xact_riemann_sign" -> riemannSign,
  "xact_ricci_sign" -> ricciSign,
  "xact_torsion_sign" -> torsionSign,
  "xact_epsilon_sign" -> epsilonSign,
  "xact_commute_rule" ->
   "D_b D_a v^c = D_a D_b v^c + s_R R^c{}_{d a b} v^d",
  "project_commutator" ->
   "[D_a,D_b] v^c = R_project{}_{ab d}{}^c v^d",
  "project_from_xact_factor" -> factor,
  "project_index_map" ->
   "R_project{}_{ab d}{}^c = factor * R_xAct[-a,-b,-d,c]",
  "source" ->
   "xTensor 1.3.0 CommuteCovDs implementation and sign globals",
  "claim_boundary" ->
   "SIGN_AND_INDEX_ADAPTER_ONLY_NO_BACKGROUND_CURVATURE_PROMOTION"
 |>
];

RiemannConventionAdapterQ[adapter_Association] := And[
 Lookup[adapter, "schema_version", None] === "1.0.0",
 Lookup[adapter, "stage_id", None] === "ALG_01",
 Lookup[adapter, "status", None] === "PASS",
 TrueQ[Lookup[adapter, "xact_xtensor_loaded", False]],
 Lookup[adapter, "xact_riemann_sign", None] === 1,
 Lookup[adapter, "xact_ricci_sign", None] === 1,
 Lookup[adapter, "xact_torsion_sign", None] === 1,
 Lookup[adapter, "xact_epsilon_sign", None] === 1,
 Lookup[adapter, "project_from_xact_factor", None] === -1,
 Lookup[adapter, "claim_boundary", None] ===
  "SIGN_AND_INDEX_ADAPTER_ONLY_NO_BACKGROUND_CURVATURE_PROMOTION"
];
RiemannConventionAdapterQ[_] := False;

End[];
EndPackage[];
