(* ::Package:: *)

BeginPackage["BASS`Bianchi`", {"BASS`Geometry`"}];

CanonicalWitnessRegistry::usage =
 "CanonicalWitnessRegistry[] returns the five exact dimensionless ALG-01 witnesses.";
ExceptionalVIminusOneNinthResiduals::usage =
 "ExceptionalVIminusOneNinthResiduals[witness] returns the group and momentum residuals.";
BranchPredicateReport::usage =
 "BranchPredicateReport[spec,witness] checks branch, Jacobi and Cartan contracts.";
ValidateCanonicalWitness::usage =
 "ValidateCanonicalWitness[label] validates one named exact witness.";
ValidateWitnessRegistry::usage =
 "ValidateWitnessRegistry[] validates all bounded ALG-01 witnesses.";
HostileWitnessRegistry::usage =
 "HostileWitnessRegistry[] returns targeted adversarial witness mutations.";
ValidateHostileWitnesses::usage =
 "ValidateHostileWitnesses[] requires every targeted mutation to be rejected.";

Begin["`Private`"];

ClearAll[
 CanonicalWitnessRegistry, ExceptionalVIminusOneNinthResiduals,
 BranchPredicateReport, ValidateCanonicalWitness, ValidateWitnessRegistry,
 HostileWitnessRegistry, ValidateHostileWitnesses,
 witnessVector3Q, witnessMatrix3Q, witnessSymmetric3Q, witnessZeroQ,
 witnessQ, aAlignedQ, signedH, nullableMatchQ, failedCheckKeys,
 requiredWitnessKeys
];

witnessVector3Q[vector_] := ListQ[vector] && Length[vector] === 3;
witnessMatrix3Q[matrix_] := MatrixQ[matrix] && Dimensions[matrix] === {3, 3};
witnessSymmetric3Q[matrix_] :=
 witnessMatrix3Q[matrix] && TrueQ[Simplify[matrix == Transpose[matrix]]];
witnessZeroQ[expression_] :=
 AllTrue[Flatten[{expression}], TrueQ[PossibleZeroQ[#]] &];

requiredWitnessKeys = {"label", "role", "a", "n", "shear"};

witnessQ[witness_Association] := And[
 SubsetQ[Keys[witness], requiredWitnessKeys],
 StringQ[Lookup[witness, "label", None]],
 Lookup[witness, "role", None] ===
  "dimensionless canonical algebra witness only",
 witnessVector3Q[Lookup[witness, "a", None]],
 witnessSymmetric3Q[Lookup[witness, "n", None]],
 witnessSymmetric3Q[Lookup[witness, "shear", None]],
 TrueQ[PossibleZeroQ[Tr[Lookup[witness, "shear", IdentityMatrix[3]]]]]
];
witnessQ[_] := False;

aAlignedQ[a_] := witnessVector3Q[a] && witnessZeroQ[a[[2 ;; 3]]];

signedH[a_, n_] := Module[{transverseDeterminant},
 If[
  ! aAlignedQ[a] || ! witnessSymmetric3Q[n],
  Return[Failure["NotAAligned", <||>]]
 ];
 transverseDeterminant = Simplify[Det[n[[{2, 3}, {2, 3}]]]];
 If[
  TrueQ[PossibleZeroQ[transverseDeterminant]],
  Null,
  Simplify[Dot[a, a]/transverseDeterminant]
 ]
];

nullableMatchQ[expected_, actual_] :=
 If[expected === Null, True, SameQ[expected, actual]];

failedCheckKeys[checks_Association] :=
 Keys @ Select[checks, Not @* TrueQ];

CanonicalWitnessRegistry[] := <|
 "I" -> <|
   "label" -> "I",
   "role" -> "dimensionless canonical algebra witness only",
   "a" -> {0, 0, 0},
   "n" -> ConstantArray[0, {3, 3}],
   "shear" -> ConstantArray[0, {3, 3}]
  |>,
 "II" -> <|
   "label" -> "II",
   "role" -> "dimensionless canonical algebra witness only",
   "a" -> {0, 0, 0},
   "n" -> DiagonalMatrix[{1, 0, 0}],
   "shear" -> ConstantArray[0, {3, 3}]
  |>,
 "V" -> <|
   "label" -> "V",
   "role" -> "dimensionless canonical algebra witness only",
   "a" -> {1, 0, 0},
   "n" -> ConstantArray[0, {3, 3}],
   "shear" -> ConstantArray[0, {3, 3}]
  |>,
 "IX" -> <|
   "label" -> "IX",
   "role" -> "dimensionless canonical algebra witness only",
   "a" -> {0, 0, 0},
   "n" -> IdentityMatrix[3],
   "shear" -> ConstantArray[0, {3, 3}]
  |>,
 "VI_-1/9" -> <|
   "label" -> "VI_-1/9",
   "role" -> "dimensionless canonical algebra witness only",
   "a" -> {1, 0, 0},
   "n" -> {{0, 0, 0}, {0, 2, 3}, {0, 3, 0}},
   "shear" -> {{0, 0, 2}, {0, 0, 3}, {2, 3, 0}}
  |>
|>;

ExceptionalVIminusOneNinthResiduals[witness_Association] /;
  witnessQ[witness] := Module[{a, n, shear},
 a = witness["a"];
 n = witness["n"];
 shear = witness["shear"];
 <|
  "group" -> Simplify[
    9 a[[1]]^2 + Det[n[[{2, 3}, {2, 3}]]]
   ],
  "momentum" -> Simplify[
    n[[2, 2]] shear[[1, 2]]
     + (n[[2, 3]] - 3 a[[1]]) shear[[1, 3]]
   ]
 |>
];
ExceptionalVIminusOneNinthResiduals[___] :=
 Failure["InvalidWitness", <||>];

BranchPredicateReport[spec_Association, witness_Association] /;
  BianchiTypeSpecQ[spec] && witnessQ[witness] := Module[
 {a, n, expected, inertia, rank, transverseDetSign, h,
  exceptionalResiduals, jacobiVector, jacobiTensor,
  jacobiTensorNonzeroCount, checks},
 a = witness["a"];
 n = witness["n"];
 expected = spec["expected"];
 inertia = MatrixInertia3[n];
 rank = MatrixRank[n];
 transverseDetSign = If[
   spec["algebra_class"] === "B",
   Sign[Simplify[Det[n[[{2, 3}, {2, 3}]]]]],
   Null
  ];
 h = If[spec["algebra_class"] === "B", signedH[a, n], Null];
 exceptionalResiduals = If[
   TrueQ[spec["exceptional_sector"]],
   ExceptionalVIminusOneNinthResiduals[witness],
   Null
  ];
 jacobiVector = BASS`Geometry`JacobiVectorResidual[a, n];
 jacobiTensor = BASS`Geometry`JacobiTensorResidual[a, n];
 jacobiTensorNonzeroCount = Count[
   Flatten[jacobiTensor],
   entry_ /; ! TrueQ[PossibleZeroQ[entry]]
  ];
 checks = <|
   "label_match" -> SameQ[spec["public_label"], witness["label"]],
   "canonical_role_firewall" -> SameQ[
     witness["role"],
     "dimensionless canonical algebra witness only"
    ],
   "a_zero" -> SameQ[witnessZeroQ[a], expected["a_zero"]],
   "n_zero" -> SameQ[witnessZeroQ[n], expected["n_zero"]],
   "n_rank" -> SameQ[rank, expected["n_rank"]],
   "n_inertia" -> MemberQ[expected["n_inertia_options"], inertia],
   "transverse_det_sign" -> nullableMatchQ[
     expected["transverse_det_sign"], transverseDetSign
    ],
   "signed_h" -> nullableMatchQ[expected["signed_h"], h],
   "jacobi_vector" -> witnessZeroQ[jacobiVector],
   "jacobi_tensor" -> SameQ[jacobiTensorNonzeroCount, 0],
   "structure_antisymmetry" ->
    BASS`Geometry`StructureAntisymmetryQ[a, n],
   "cartan_reconstruction" ->
    BASS`Geometry`CartanReconstructionQ[a, n],
   "exceptional_constraints" -> If[
     expected["exceptional_constraints"] === Null,
     True,
     witnessZeroQ[Values[exceptionalResiduals]]
    ]
  |>;
 <|
  "schema_version" -> "1.0.0",
  "stage_id" -> "ALG_01",
  "label" -> witness["label"],
  "pass" -> And @@ Values[checks],
  "checks" -> checks,
  "failed_checks" -> failedCheckKeys[checks],
  "actual" -> <|
    "n_rank" -> rank,
    "n_inertia" -> inertia,
    "transverse_det_sign" -> transverseDetSign,
    "signed_h" -> h,
    "jacobi_vector_residual" -> jacobiVector,
    "jacobi_tensor_nonzero_count" -> jacobiTensorNonzeroCount,
    "exceptional_residuals" -> exceptionalResiduals,
    "cartan_terms" -> BASS`Geometry`CartanCoframeTerms[a, n]
   |>,
  "claim_boundary" ->
   "ALGEBRA_WITNESS_ONLY_NO_BACKGROUND_OR_SOLVER_PROMOTION"
 |>
];
BranchPredicateReport[___] :=
 Failure["InvalidSpecOrWitness", <||>];

ValidateCanonicalWitness[label_String] := Module[{specs, witnesses},
 specs = CanonicalTypeSpecRegistry[];
 witnesses = CanonicalWitnessRegistry[];
 If[
  ! KeyExistsQ[specs, label] || ! KeyExistsQ[witnesses, label],
  Return[Failure["UnknownWitness", <|"label" -> label|>]]
 ];
 BranchPredicateReport[specs[label], witnesses[label]]
];

ValidateWitnessRegistry[] := AssociationMap[
 ValidateCanonicalWitness,
 Keys[CanonicalWitnessRegistry[]]
];

HostileWitnessRegistry[] := Module[{base},
 base = CanonicalWitnessRegistry[];
 <|
  "JACOBI_BREAK" -> <|
    "target_label" -> "IX",
    "witness" -> ReplacePart[base["IX"], "a" -> {1, 0, 0}]
   |>,
  "IX_INERTIA_BREAK" -> <|
    "target_label" -> "IX",
    "witness" -> ReplacePart[
      base["IX"], "n" -> DiagonalMatrix[{1, 1, -1}]
     ]
   |>,
  "V_N_BREAK" -> <|
    "target_label" -> "V",
    "witness" -> ReplacePart[
      base["V"], "n" -> DiagonalMatrix[{0, 1, 0}]
     ]
   |>,
  "EXCEPTIONAL_H_BREAK" -> <|
    "target_label" -> "VI_-1/9",
    "witness" -> ReplacePart[
      base["VI_-1/9"],
      "n" -> {{0, 0, 0}, {0, 2, 2}, {0, 2, 0}}
     ]
   |>,
  "EXCEPTIONAL_MOMENTUM_BREAK" -> <|
    "target_label" -> "VI_-1/9",
    "witness" -> ReplacePart[
      base["VI_-1/9"],
      "n" -> {{0, 0, 0}, {0, 2, -3}, {0, -3, 0}}
     ]
   |>
 |>
];

ValidateHostileWitnesses[] := Module[{specs, hostileWitnesses},
 specs = CanonicalTypeSpecRegistry[];
 hostileWitnesses = HostileWitnessRegistry[];
 Association @ KeyValueMap[
   Function[{name, item},
    name -> Module[{report},
      report = BranchPredicateReport[
        specs[item["target_label"]],
        item["witness"]
       ];
      <|
       "detected" -> ! TrueQ[report["pass"]],
       "failed_checks" -> report["failed_checks"],
       "report" -> report
      |>
     ]
   ],
   hostileWitnesses
  ]
];

End[];
EndPackage[];
