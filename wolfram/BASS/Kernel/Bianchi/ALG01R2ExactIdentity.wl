(* ::Package:: *)

BeginPackage[
 "BASS`Bianchi`",
 {"BASS`Geometry`", "BASS`IR`"}
];

ExceptionalShearCarrierReport::usage =
 "ExceptionalShearCarrierReport[witness] reports independent Sigma13 and Sigma23 canonical-witness carrier obligations.";

Begin["`Private`"];

ClearAll[
 alg01r2BaseTypeRegistry, alg01r2BaseHostileRegistry,
 alg01r2SignedHExpectedQ
];

alg01r2BaseTypeRegistry = CanonicalTypeSpecRegistry[];
alg01r2BaseHostileRegistry = HostileWitnessRegistry[];

allowedWitnessObligations = {
 "sigma13_carrier_present",
 "sigma23_carrier_present"
};

alg01r2SignedHExpectedQ[value_] := Or[
 value === Null,
 And[AssociationQ[value], BASS`IR`ExactScalarASTQ[value]]
];

Clear[BianchiTypeSpecQ];
BianchiTypeSpecQ[spec_Association] := And[
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
 AssociationQ[Lookup[spec, "expected", None]],
 SubsetQ[Keys[Lookup[spec, "expected", <||>]], expectedRequiredKeys],
 alg01r2SignedHExpectedQ[
  Lookup[Lookup[spec, "expected", <||>],
   "signed_h", Missing["KeyAbsent"]]
 ],
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
];
BianchiTypeSpecQ[_] := False;

Clear[CanonicalTypeSpecRegistry];
CanonicalTypeSpecRegistry[] := Module[{registry, spec, expected},
 registry = alg01r2BaseTypeRegistry;
 spec = registry["VI_-1/9"];
 expected = ReplacePart[
   spec["expected"],
   "signed_h" -> BASS`IR`ExactScalarAST[-1/9]
  ];
 spec = ReplacePart[
   spec,
   {
    "witness_obligations" -> {
      "sigma13_carrier_present",
      "sigma23_carrier_present"
     },
    "expected" -> expected
   }
  ];
 ReplacePart[
  registry,
  "VI_-1/9" -> BASS`IR`CanonicalizeData[spec]
 ]
];

Clear[nullableMatchQ];
nullableMatchQ[Null, _] := True;
nullableMatchQ[expected_Association, actual_] /;
  BASS`IR`ExactScalarASTQ[expected] :=
 SameQ[expected, BASS`IR`ExactScalarAST[actual]];
nullableMatchQ[expected_, actual_] := SameQ[expected, actual];

Clear[ExceptionalShearCarrierReport, ExceptionalShearSurvivalQ];
ExceptionalShearCarrierReport[witness_Association] /;
  witnessQ[witness] := Module[{shear},
 shear = witness["shear"];
 <|
  "sigma13_carrier_present" ->
   Not[TrueQ[PossibleZeroQ[shear[[1, 3]]]]],
  "sigma23_carrier_present" ->
   Not[TrueQ[PossibleZeroQ[shear[[2, 3]]]]]
 |>
];
ExceptionalShearCarrierReport[___] :=
 Failure["InvalidWitness", <||>];

ExceptionalShearSurvivalQ[witness_Association] /;
  witnessQ[witness] := Module[{carrierReport},
 carrierReport = ExceptionalShearCarrierReport[witness];
 AssociationQ[carrierReport] && And @@ Values[carrierReport]
];
ExceptionalShearSurvivalQ[___] := False;

Clear[WitnessObligationReport];
WitnessObligationReport[
 spec_Association,
 witness_Association
] /; BianchiTypeSpecQ[spec] && witnessQ[witness] := Module[
 {obligations, carrierReport, checks},
 obligations = Lookup[spec, "witness_obligations", {}];
 carrierReport = ExceptionalShearCarrierReport[witness];
 checks = AssociationMap[
   Switch[
     #,
     "sigma13_carrier_present",
     TrueQ[Lookup[carrierReport, "sigma13_carrier_present", False]],
     "sigma23_carrier_present",
     TrueQ[Lookup[carrierReport, "sigma23_carrier_present", False]],
     _,
     False
    ] &,
   obligations
  ];
 <|
  "pass" -> And @@ Values[checks],
  "checks" -> checks,
  "failed_obligations" -> failedCheckKeys[checks],
  "scope_firewall" ->
   "witness-only obligation; not a physical branch predicate"
 |>
];
WitnessObligationReport[___] :=
 Failure["InvalidSpecOrWitness", <||>];

Clear[BranchPredicateReport];
BranchPredicateReport[spec_Association, witness_Association] /;
  BianchiTypeSpecQ[spec] && witnessQ[witness] := Module[
 {a, n, expected, inertia, rank, transverseDetSign, h,
  exceptionalResiduals, obligationReport, jacobiVector, jacobiTensor,
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
 obligationReport = WitnessObligationReport[spec, witness];
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
   "public_algebra_type_counting" -> SameQ[
     spec["counted_public_algebra_type"],
     Not[TrueQ[spec["exceptional_sector"]]]
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
    ],
   "witness_obligations" -> TrueQ[obligationReport["pass"]]
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
    "signed_h" -> If[
      h === Null,
      Null,
      BASS`IR`ExactScalarAST[h]
     ],
    "jacobi_vector_residual" -> jacobiVector,
    "jacobi_tensor_nonzero_count" -> jacobiTensorNonzeroCount,
    "exceptional_residuals" -> exceptionalResiduals,
    "witness_obligation_report" -> obligationReport,
    "cartan_terms" -> BASS`Geometry`CartanCoframeTerms[a, n]
   |>,
  "claim_boundary" ->
   "ALGEBRA_WITNESS_ONLY_NO_BACKGROUND_OR_SOLVER_PROMOTION"
 |>
];
BranchPredicateReport[___] :=
 Failure["InvalidSpecOrWitness", <||>];

Clear[HostileWitnessRegistry];
HostileWitnessRegistry[] := Module[{witness},
 witness = CanonicalWitnessRegistry[]["VI_-1/9"];
 Join[
  alg01r2BaseHostileRegistry,
  <|
   "EXCEPTIONAL_SIGMA13_DELETE" -> <|
     "target_label" -> "VI_-1/9",
     "witness" -> ReplacePart[
       witness,
       "shear" -> ReplacePart[
         witness["shear"],
         {{1, 3} -> 0, {3, 1} -> 0}
        ]
      ]
    |>,
   "EXCEPTIONAL_SIGMA23_DELETE" -> <|
     "target_label" -> "VI_-1/9",
     "witness" -> ReplacePart[
       witness,
       "shear" -> ReplacePart[
         witness["shear"],
         {{2, 3} -> 0, {3, 2} -> 0}
        ]
      ]
    |>
  |>
 ]
];

End[];
EndPackage[];
