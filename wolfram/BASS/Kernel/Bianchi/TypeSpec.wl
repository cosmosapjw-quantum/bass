(* ::Package:: *)

BeginPackage["BASS`Bianchi`"];

MakeBianchiTypeSpec::usage =
 "MakeBianchiTypeSpec[spec] fills defaults and canonicalizes a Bianchi type specification.";
BianchiTypeSpecRequiredKeys::usage =
 "BianchiTypeSpecRequiredKeys[] returns the required top-level keys.";
BianchiTypeSpecQ::usage =
 "BianchiTypeSpecQ[spec] validates the fail-closed Bianchi type specification.";
BianchiTypeSpecSemanticProjection::usage =
 "BianchiTypeSpecSemanticProjection[spec] replaces the human-readable signed-h scalar with its exact semantic AST before hashing or export.";
BianchiTypeSpecSemanticSHA256::usage =
 "BianchiTypeSpecSemanticSHA256[spec] returns the canonical SHA-256 of the exact semantic type-spec projection.";
CanonicalTypeSpecRegistrySemanticSHA256::usage =
 "CanonicalTypeSpecRegistrySemanticSHA256[] hashes the exact semantic projection of the bounded canonical type registry.";
MatrixInertia3::usage =
 "MatrixInertia3[n] returns {positive,negative,zero} for an exact symmetric 3 by 3 matrix.";
CanonicalTypeSpecRegistry::usage =
 "CanonicalTypeSpecRegistry[] returns the five bounded ALG-01 type specifications.";

Begin["`Private`"];

ClearAll[
 MakeBianchiTypeSpec, BianchiTypeSpecRequiredKeys, BianchiTypeSpecQ,
 BianchiTypeSpecSemanticProjection, BianchiTypeSpecSemanticSHA256,
 CanonicalTypeSpecRegistrySemanticSHA256,
 MatrixInertia3, CanonicalTypeSpecRegistry,
 matrix3Q, symmetric3Q, expectedRequiredKeys,
 allowedWitnessObligations, exactSignedHConsistencyQ
];

matrix3Q[matrix_] := MatrixQ[matrix] && Dimensions[matrix] === {3, 3};
symmetric3Q[matrix_] :=
 matrix3Q[matrix] && TrueQ[Simplify[matrix == Transpose[matrix]]];

BianchiTypeSpecRequiredKeys[] := {
 "schema_version", "program_id", "public_label", "computational_key",
 "algebra_class", "exceptional_sector", "counted_public_algebra_type",
 "physical_predicates", "witness_obligations", "expected",
 "gauge_contract", "authority_formula_ids", "claim_boundary"
};

expectedRequiredKeys = {
 "a_zero", "n_zero", "n_rank", "n_inertia_options",
 "transverse_det_sign", "signed_h", "signed_h_ast",
 "exceptional_constraints"
};

allowedWitnessObligations = {
 "non_diagonal_shear_survival",
 "sigma13_carrier_present",
 "sigma23_carrier_present"
};

exactSignedHConsistencyQ[expected_Association] := Module[
 {signedH, signedHAST},
 signedH = Lookup[expected, "signed_h", Missing["KeyAbsent"]];
 signedHAST = Lookup[expected, "signed_h_ast", Missing["KeyAbsent"]];
 Which[
  signedH === Null,
  SameQ[signedHAST, Null],
  MissingQ[signedH] || MissingQ[signedHAST],
  False,
  ! FreeQ[signedH, _Real],
  False,
  ! BASS`IR`ExactScalarASTQ[signedHAST],
  False,
  True,
  SameQ[signedHAST, BASS`IR`ExactScalarAST[signedH]]
 ]
];
exactSignedHConsistencyQ[_] := False;

MakeBianchiTypeSpec[spec_Association] := BASS`IR`CanonicalizeData @ Join[
 <|
  "schema_version" -> "1.0.0",
  "program_id" -> "BASS-MASTER-SSOT-V2-WOLFRAM-XACT-20260901",
  "public_label" -> Missing["Required"],
  "computational_key" -> Missing["Required"],
  "algebra_class" -> Missing["Required"],
  "exceptional_sector" -> False,
  "counted_public_algebra_type" -> True,
  "physical_predicates" -> {},
  "witness_obligations" -> {},
  "expected" -> <||>,
  "gauge_contract" -> <|
    "canonical_witness_role" ->
     "dimensionless fingerprint only; never a physical magnitude",
    "physical_rate_dimension" -> "L^-1",
    "temporal_triad_rotation_retained" -> True
   |>,
  "authority_formula_ids" -> {"SSOT-T3.1", "SSOT-T11.1", "SSOT-T12.1"},
  "claim_boundary" ->
   "ALGEBRA_WITNESS_ONLY_NO_BACKGROUND_OR_SOLVER_PROMOTION"
 |>,
 spec
];

BianchiTypeSpecQ[spec_Association] := Module[{expected},
 expected = Lookup[spec, "expected", Missing["KeyAbsent"]];
 And[
  SubsetQ[Keys[spec], BianchiTypeSpecRequiredKeys[]],
  Lookup[spec, "schema_version", None] === "1.0.0",
  Lookup[spec, "program_id", None] ===
   "BASS-MASTER-SSOT-V2-WOLFRAM-XACT-20260901",
  StringQ[Lookup[spec, "public_label", None]],
  StringQ[Lookup[spec, "computational_key", None]],
  MemberQ[{"A", "B"}, Lookup[spec, "algebra_class", None]],
  BooleanQ[Lookup[spec, "exceptional_sector", None]],
  BooleanQ[Lookup[spec, "counted_public_algebra_type", None]],
  ListQ[Lookup[spec, "physical_predicates", None]],
  ListQ[Lookup[spec, "witness_obligations", None]],
  AllTrue[
   Lookup[spec, "witness_obligations", {}],
   MemberQ[allowedWitnessObligations, #] &
  ],
  AssociationQ[expected],
  SubsetQ[Keys[expected], expectedRequiredKeys],
  exactSignedHConsistencyQ[expected],
  AssociationQ[Lookup[spec, "gauge_contract", None]],
  Lookup[
    Lookup[spec, "gauge_contract", <||>],
    "canonical_witness_role", None
   ] === "dimensionless fingerprint only; never a physical magnitude",
  Lookup[
    Lookup[spec, "gauge_contract", <||>],
    "physical_rate_dimension", None
   ] === "L^-1",
  ListQ[Lookup[spec, "authority_formula_ids", None]],
  StringQ[Lookup[spec, "claim_boundary", None]]
 ]
];
BianchiTypeSpecQ[_] := False;

BianchiTypeSpecSemanticProjection[spec_Association] /;
  BianchiTypeSpecQ[spec] := Module[{expected, semanticExpected},
 expected = spec["expected"];
 semanticExpected = Join[
   KeyDrop[expected, {"signed_h", "signed_h_ast"}],
   <|"signed_h" -> expected["signed_h_ast"]|>
  ];
 BASS`IR`CanonicalizeData @ ReplacePart[
   spec,
   "expected" -> semanticExpected
  ]
];
BianchiTypeSpecSemanticProjection[___] := Failure[
 "InvalidBianchiTypeSpec",
 <|"reason" -> "semantic projection requires a valid exact type spec"|>
];

BianchiTypeSpecSemanticSHA256[spec_Association] := Module[{projection},
 projection = BianchiTypeSpecSemanticProjection[spec];
 If[FailureQ[projection], Return[projection]];
 BASS`IR`CanonicalSHA256[projection]
];
BianchiTypeSpecSemanticSHA256[___] := Failure[
 "InvalidBianchiTypeSpec",
 <|"reason" -> "semantic hash requires a valid exact type spec"|>
];

CanonicalTypeSpecRegistrySemanticSHA256[] := Module[
 {registry, projection},
 registry = CanonicalTypeSpecRegistry[];
 projection = Association @ KeyValueMap[
    Function[{label, typeSpec},
     label -> BianchiTypeSpecSemanticProjection[typeSpec]
    ],
    registry
   ];
 If[AnyTrue[Values[projection], FailureQ],
  Return[Failure["InvalidCanonicalRegistry", <||>]]
 ];
 BASS`IR`CanonicalSHA256[projection]
];

MatrixInertia3[n_List] /; symmetric3Q[n] := Module[{signs},
 signs = Sign[Simplify[Eigenvalues[n]]];
 If[
  ! AllTrue[signs, MemberQ[{-1, 0, 1}, #] &],
  Return[Failure["UndecidableInertia", <|"eigenvalue_signs" -> signs|>]]
 ];
 {Count[signs, 1], Count[signs, -1], Count[signs, 0]}
];
MatrixInertia3[___] := Failure["InvalidSymmetricMatrix", <||>];

CanonicalTypeSpecRegistry[] := <|
 "I" -> MakeBianchiTypeSpec[<|
   "public_label" -> "I",
   "computational_key" -> "I",
   "algebra_class" -> "A",
   "physical_predicates" -> {"a=0", "n=0"},
   "expected" -> <|
     "a_zero" -> True,
     "n_zero" -> True,
     "n_rank" -> 0,
     "n_inertia_options" -> {{0, 0, 3}},
     "transverse_det_sign" -> Null,
     "signed_h" -> Null,
     "signed_h_ast" -> Null,
     "exceptional_constraints" -> Null
    |>
  |>],
 "II" -> MakeBianchiTypeSpec[<|
   "public_label" -> "II",
   "computational_key" -> "II",
   "algebra_class" -> "A",
   "physical_predicates" -> {"a=0", "rank(n)=1"},
   "expected" -> <|
     "a_zero" -> True,
     "n_zero" -> False,
     "n_rank" -> 1,
     "n_inertia_options" -> {{1, 0, 2}, {0, 1, 2}},
     "transverse_det_sign" -> Null,
     "signed_h" -> Null,
     "signed_h_ast" -> Null,
     "exceptional_constraints" -> Null
    |>
  |>],
 "V" -> MakeBianchiTypeSpec[<|
   "public_label" -> "V",
   "computational_key" -> "V",
   "algebra_class" -> "B",
   "physical_predicates" -> {"a!=0", "n=0"},
   "expected" -> <|
     "a_zero" -> False,
     "n_zero" -> True,
     "n_rank" -> 0,
     "n_inertia_options" -> {{0, 0, 3}},
     "transverse_det_sign" -> 0,
     "signed_h" -> Null,
     "signed_h_ast" -> Null,
     "exceptional_constraints" -> Null
    |>
  |>],
 "IX" -> MakeBianchiTypeSpec[<|
   "public_label" -> "IX",
   "computational_key" -> "IX",
   "algebra_class" -> "A",
   "physical_predicates" -> {
     "a=0", "rank(n)=3", "all eigenvalues have the same sign"
    },
   "expected" -> <|
     "a_zero" -> True,
     "n_zero" -> False,
     "n_rank" -> 3,
     "n_inertia_options" -> {{3, 0, 0}, {0, 3, 0}},
     "transverse_det_sign" -> Null,
     "signed_h" -> Null,
     "signed_h_ast" -> Null,
     "exceptional_constraints" -> Null
    |>
  |>],
 "VI_-1/9" -> MakeBianchiTypeSpec[<|
   "public_label" -> "VI_-1/9",
   "computational_key" -> "VI_h(h=-1/9)",
   "algebra_class" -> "B",
   "exceptional_sector" -> True,
   "counted_public_algebra_type" -> False,
   "physical_predicates" -> {
     "a!=0", "det(n_perp)<0", "h=-1/9",
     "exceptional momentum constraint"
    },
   "witness_obligations" -> {
     "non_diagonal_shear_survival",
     "sigma13_carrier_present",
     "sigma23_carrier_present"
    },
   "expected" -> <|
     "a_zero" -> False,
     "n_zero" -> False,
     "n_rank" -> 2,
     "n_inertia_options" -> {{1, 1, 1}},
     "transverse_det_sign" -> -1,
     "signed_h" -> -1/9,
     "signed_h_ast" -> BASS`IR`ExactScalarAST[-1/9],
     "exceptional_constraints" -> True
    |>
  |>]
|>;

End[];
EndPackage[];
