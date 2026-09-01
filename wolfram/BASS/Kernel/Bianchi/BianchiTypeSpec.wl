(* ::Package:: *)

BeginPackage["BASS`Bianchi`"];

BianchiTypeSpec::usage =
 "BianchiTypeSpec[key] returns the exact ALG-01 branch-predicate specification for a supported witness key.";
BianchiTypeSpecQ::usage =
 "BianchiTypeSpecQ[spec] validates the ALG-01 type-specification schema and claim boundary.";

Begin["`Private`"];

ClearAll[requiredSpecKeys, typeSpecRegistry, BianchiTypeSpec, BianchiTypeSpecQ];

requiredSpecKeys[] := {
 "schema_version", "stage_id", "registry_key", "public_label",
 "computational_key", "class", "exceptional_sector", "predicate_id",
 "a_condition", "n_condition", "authority_chart", "flrw_locus",
 "known_limits", "claim_boundary"
};

typeSpecRegistry[] := <|
 "I" -> <|
   "schema_version" -> "1.0.0", "stage_id" -> "ALG_01",
   "registry_key" -> "I", "public_label" -> "I",
   "computational_key" -> "I", "class" -> "A",
   "exceptional_sector" -> False,
   "predicate_id" -> "A_ZERO_N_RANK_0",
   "a_condition" -> "a_alpha = 0",
   "n_condition" -> "rank(n)=0",
   "authority_chart" -> "dimensionful_orthonormal_frame",
   "flrw_locus" -> "flat FLRW at zero shear",
   "known_limits" -> {"zero-structure baseline"},
   "claim_boundary" -> "WITNESS_PREDICATE_ONLY_NO_BACKGROUND_SOLVER"|>,
 "II" -> <|
   "schema_version" -> "1.0.0", "stage_id" -> "ALG_01",
   "registry_key" -> "II", "public_label" -> "II",
   "computational_key" -> "II", "class" -> "A",
   "exceptional_sector" -> False,
   "predicate_id" -> "A_ZERO_N_RANK_1",
   "a_condition" -> "a_alpha = 0",
   "n_condition" -> "rank(n)=1",
   "authority_chart" -> "dimensionful_orthonormal_frame",
   "flrw_locus" -> None,
   "known_limits" -> {"minimal non-flat Class-A witness"},
   "claim_boundary" -> "WITNESS_PREDICATE_ONLY_NO_BACKGROUND_SOLVER"|>,
 "V" -> <|
   "schema_version" -> "1.0.0", "stage_id" -> "ALG_01",
   "registry_key" -> "V", "public_label" -> "V",
   "computational_key" -> "V", "class" -> "B",
   "exceptional_sector" -> False,
   "predicate_id" -> "A_NONZERO_N_RANK_0",
   "a_condition" -> "a_alpha != 0",
   "n_condition" -> "rank(n)=0",
   "authority_chart" -> "A_aligned_dimensionful_orthonormal_frame",
   "flrw_locus" -> "open FLRW at isotropic expansion",
   "known_limits" -> {"pure Class-B vector channel"},
   "claim_boundary" -> "WITNESS_PREDICATE_ONLY_NO_BACKGROUND_SOLVER"|>,
 "IX" -> <|
   "schema_version" -> "1.0.0", "stage_id" -> "ALG_01",
   "registry_key" -> "IX", "public_label" -> "IX",
   "computational_key" -> "IX", "class" -> "A",
   "exceptional_sector" -> False,
   "predicate_id" -> "A_ZERO_N_DEFINITE_RANK_3",
   "a_condition" -> "a_alpha = 0",
   "n_condition" -> "rank(n)=3 with definite inertia",
   "authority_chart" -> "dimensionful_orthonormal_frame",
   "flrw_locus" -> "closed FLRW at isotropic n and zero shear",
   "known_limits" -> {"H=0 recollapse requires a non-Hubble chart later"},
   "claim_boundary" -> "WITNESS_PREDICATE_ONLY_NO_BACKGROUND_SOLVER"|>,
 "VI_-1/9" -> <|
   "schema_version" -> "1.0.0", "stage_id" -> "ALG_01",
   "registry_key" -> "VI_-1/9", "public_label" -> "VI_h",
   "computational_key" -> "VI_h(h=-1/9)", "class" -> "B",
   "exceptional_sector" -> True,
   "predicate_id" -> "CLASS_B_TRANSVERSE_INDEFINITE_H_MINUS_ONE_NINTH",
   "a_condition" -> "A-aligned a=(A,0,0), A!=0",
   "n_condition" ->
    "n has zero first row/column and det(n_perp)=-9 A^2",
   "authority_chart" -> "exceptional_VI_minus_1_over_9_full_shear",
   "flrw_locus" -> None,
   "known_limits" -> {
    "exceptional sector of VI_h, not a twelfth public type",
    "Sigma_13 and Sigma_23 are not removed by the generic VI_h reduction"},
   "claim_boundary" -> "WITNESS_PREDICATE_ONLY_NO_BACKGROUND_SOLVER"|>
|>;

BianchiTypeSpec[key_String] :=
 Lookup[typeSpecRegistry[], key,
  Failure["UnsupportedBianchiWitness", <|"key" -> key|>]];
BianchiTypeSpec[_] := Failure["InvalidBianchiWitnessKey", <||>];

BianchiTypeSpecQ[spec_Association] := And[
 SubsetQ[Keys[spec], requiredSpecKeys[]],
 Lookup[spec, "schema_version", None] === "1.0.0",
 Lookup[spec, "stage_id", None] === "ALG_01",
 MemberQ[{"A", "B"}, Lookup[spec, "class", None]],
 BooleanQ[Lookup[spec, "exceptional_sector", None]],
 StringQ[Lookup[spec, "registry_key", None]],
 StringQ[Lookup[spec, "public_label", None]],
 StringQ[Lookup[spec, "computational_key", None]],
 Lookup[spec, "claim_boundary", None] ===
  "WITNESS_PREDICATE_ONLY_NO_BACKGROUND_SOLVER"
];
BianchiTypeSpecQ[_] := False;

End[];
EndPackage[];
