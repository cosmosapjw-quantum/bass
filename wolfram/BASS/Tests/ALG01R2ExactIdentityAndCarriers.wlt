$ALG01R2Specs = BASS`Bianchi`CanonicalTypeSpecRegistry[];
$ALG01R2Witnesses = BASS`Bianchi`CanonicalWitnessRegistry[];
$ALG01R2Spec = $ALG01R2Specs["VI_-1/9"];
$ALG01R2Witness = $ALG01R2Witnesses["VI_-1/9"];

$ALG01R2Sigma13Deleted = ReplacePart[
 $ALG01R2Witness,
 "shear" -> ReplacePart[
   $ALG01R2Witness["shear"],
   {{1, 3} -> 0, {3, 1} -> 0}
  ]
];
$ALG01R2Sigma23Deleted = ReplacePart[
 $ALG01R2Witness,
 "shear" -> ReplacePart[
   $ALG01R2Witness["shear"],
   {{2, 3} -> 0, {3, 2} -> 0}
  ]
];
$ALG01R2AllDeleted = ReplacePart[
 $ALG01R2Witness,
 "shear" -> ConstantArray[0, {3, 3}]
];
$ALG01R2RealSpec = ReplacePart[
 $ALG01R2Spec,
 "expected" -> ReplacePart[
   $ALG01R2Spec["expected"],
   "signed_h" -> N[-1/9]
  ]
];

VerificationTest[
 NameQ["BASS`Bianchi`ExceptionalShearCarrierReport"],
 True,
 TestID -> "BASS-ALG-01R2-carrier-report-api-exists"
]
VerificationTest[
 Sort[Lookup[$ALG01R2Spec, "witness_obligations", {}]],
 Sort[{"sigma13_carrier_present", "sigma23_carrier_present"}],
 TestID -> "BASS-ALG-01R2-two-independent-carrier-obligations"
]
VerificationTest[
 Lookup[$ALG01R2Spec["expected"], "signed_h"],
 BASS`IR`ExactScalarAST[-1/9],
 TestID -> "BASS-ALG-01R2-exact-signed-h-AST"
]
VerificationTest[
 BASS`Bianchi`BianchiTypeSpecQ[$ALG01R2RealSpec],
 False,
 TestID -> "BASS-ALG-01R2-machine-real-signed-h-rejected"
]
VerificationTest[
 BASS`Bianchi`ExceptionalShearSurvivalQ[$ALG01R2Witness],
 True,
 TestID -> "BASS-ALG-01R2-canonical-two-carrier-witness"
]
VerificationTest[
 BASS`Bianchi`ExceptionalShearSurvivalQ[$ALG01R2Sigma13Deleted],
 False,
 TestID -> "BASS-ALG-01R2-sigma13-deletion-rejected"
]
VerificationTest[
 BASS`Bianchi`ExceptionalShearSurvivalQ[$ALG01R2Sigma23Deleted],
 False,
 TestID -> "BASS-ALG-01R2-sigma23-deletion-rejected"
]
VerificationTest[
 BASS`Bianchi`ExceptionalShearSurvivalQ[$ALG01R2AllDeleted],
 False,
 TestID -> "BASS-ALG-01R2-all-offdiagonal-deletion-rejected"
]

$ALG01R2CanonicalReport = BASS`Bianchi`BranchPredicateReport[
 $ALG01R2Spec,
 $ALG01R2Witness
];
VerificationTest[
 $ALG01R2CanonicalReport["actual"]["signed_h"],
 BASS`IR`ExactScalarAST[-1/9],
 TestID -> "BASS-ALG-01R2-report-preserves-exact-h"
]

$ALG01R2Hostile = BASS`Bianchi`ValidateHostileWitnesses[];
VerificationTest[
 SubsetQ[
  Keys[$ALG01R2Hostile],
  {
   "EXCEPTIONAL_SIGMA13_DELETE",
   "EXCEPTIONAL_SIGMA23_DELETE"
  }
 ],
 True,
 TestID -> "BASS-ALG-01R2-single-carrier-hostile-ids-present"
]
VerificationTest[
 And @@ Lookup[
   Lookup[
    $ALG01R2Hostile,
    {
     "EXCEPTIONAL_SHEAR_DELETE",
     "EXCEPTIONAL_SIGMA13_DELETE",
     "EXCEPTIONAL_SIGMA23_DELETE"
    },
    <||>
   ],
   "detected",
   False
  ],
 True,
 TestID -> "BASS-ALG-01R2-all-three-shear-deletions-detected"
]

VerificationTest[
 AnyTrue[
  Lookup[$ALG01R2Spec, "physical_predicates", {}],
  Function[predicate,
   StringContainsQ[predicate, "Sigma13"] ||
    StringContainsQ[predicate, "Sigma23"]
  ]
 ],
 False,
 TestID -> "BASS-ALG-01R2-obligations-do-not-strengthen-physical-branch"
]
VerificationTest[
 BASS`IR`CanonicalSHA256[$ALG01R2Spec] =!=
  BASS`IR`CanonicalSHA256[$ALG01R2RealSpec],
 True,
 TestID -> "BASS-ALG-01R2-exact-vs-real-identity-separated"
]
VerificationTest[
 BASS`IR`RawJSONRoundTripQ[$ALG01R2Spec],
 True,
 TestID -> "BASS-ALG-01R2-type-spec-raw-json-roundtrip"
]
