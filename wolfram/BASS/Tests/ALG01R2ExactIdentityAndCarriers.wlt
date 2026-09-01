$ALG01R2Specs = BASS`Bianchi`CanonicalTypeSpecRegistry[];
$ALG01R2Witnesses = BASS`Bianchi`CanonicalWitnessRegistry[];
$ALG01R2ExceptionalSpec = $ALG01R2Specs["VI_-1/9"];
$ALG01R2ExceptionalWitness = $ALG01R2Witnesses["VI_-1/9"];

VerificationTest[
 NameQ["BASS`Bianchi`BianchiTypeSpecSemanticProjection"],
 True,
 TestID -> "BASS-ALG-01R2-API-semantic-projection"
]
VerificationTest[
 NameQ["BASS`Bianchi`BianchiTypeSpecSemanticSHA256"],
 True,
 TestID -> "BASS-ALG-01R2-API-semantic-sha256"
]
VerificationTest[
 NameQ["BASS`Bianchi`ExceptionalShearCarrierReport"],
 True,
 TestID -> "BASS-ALG-01R2-API-carrier-report"
]

$ALG01R2SignedHAST = Lookup[
 Lookup[$ALG01R2ExceptionalSpec, "expected", <||>],
 "signed_h_ast",
 Missing["KeyAbsent"]
];
VerificationTest[
 BASS`IR`ExactScalarASTQ[$ALG01R2SignedHAST],
 True,
 TestID -> "BASS-ALG-01R2-signed-h-exact-AST-valid"
]
VerificationTest[
 $ALG01R2SignedHAST,
 <|"type" -> "rational", "numerator" -> -1, "denominator" -> 9|>,
 TestID -> "BASS-ALG-01R2-signed-h-exact-rational"
]
VerificationTest[
 FreeQ[
  BASS`Bianchi`BianchiTypeSpecSemanticProjection[
   $ALG01R2ExceptionalSpec
  ],
  _Real
 ],
 True,
 TestID -> "BASS-ALG-01R2-semantic-projection-no-machine-real"
]
VerificationTest[
 StringLength[
  BASS`Bianchi`BianchiTypeSpecSemanticSHA256[
   $ALG01R2ExceptionalSpec
  ]
 ],
 64,
 TestID -> "BASS-ALG-01R2-semantic-hash-length"
]

$ALG01R2RealMutation = ReplacePart[
 $ALG01R2ExceptionalSpec,
 {"expected", "signed_h"} -> N[-1/9]
];
VerificationTest[
 BASS`Bianchi`BianchiTypeSpecQ[$ALG01R2RealMutation],
 False,
 TestID -> "BASS-ALG-01R2-machine-real-signed-h-rejected"
]
VerificationTest[
 FailureQ[
  BASS`Bianchi`BianchiTypeSpecSemanticProjection[$ALG01R2RealMutation]
 ],
 True,
 TestID -> "BASS-ALG-01R2-invalid-spec-semantic-projection-fails-closed"
]

$ALG01R2CanonicalCarrierReport =
 BASS`Bianchi`ExceptionalShearCarrierReport[
  $ALG01R2ExceptionalWitness
 ];
VerificationTest[
 Lookup[$ALG01R2CanonicalCarrierReport, "sigma13_carrier_present", False],
 True,
 TestID -> "BASS-ALG-01R2-canonical-sigma13-carrier"
]
VerificationTest[
 Lookup[$ALG01R2CanonicalCarrierReport, "sigma23_carrier_present", False],
 True,
 TestID -> "BASS-ALG-01R2-canonical-sigma23-carrier"
]

$ALG01R2Sigma13Deleted = ReplacePart[
 $ALG01R2ExceptionalWitness,
 {
  {"shear", 1, 3} -> 0,
  {"shear", 3, 1} -> 0
 }
];
$ALG01R2Sigma23Deleted = ReplacePart[
 $ALG01R2ExceptionalWitness,
 {
  {"shear", 2, 3} -> 0,
  {"shear", 3, 2} -> 0
 }
];
$ALG01R2Sigma13Report = BASS`Bianchi`BranchPredicateReport[
 $ALG01R2ExceptionalSpec,
 $ALG01R2Sigma13Deleted
];
$ALG01R2Sigma23Report = BASS`Bianchi`BranchPredicateReport[
 $ALG01R2ExceptionalSpec,
 $ALG01R2Sigma23Deleted
];
VerificationTest[
 TrueQ[$ALG01R2Sigma13Report["pass"]],
 False,
 TestID -> "BASS-ALG-01R2-sigma13-deletion-rejected"
]
VerificationTest[
 TrueQ[$ALG01R2Sigma23Report["pass"]],
 False,
 TestID -> "BASS-ALG-01R2-sigma23-deletion-rejected"
]
VerificationTest[
 MemberQ[
  $ALG01R2Sigma13Report["actual"]["witness_obligation_report"]
   ["failed_obligations"],
  "sigma13_carrier_present"
 ],
 True,
 TestID -> "BASS-ALG-01R2-sigma13-fails-specific-obligation"
]
VerificationTest[
 MemberQ[
  $ALG01R2Sigma23Report["actual"]["witness_obligation_report"]
   ["failed_obligations"],
  "sigma23_carrier_present"
 ],
 True,
 TestID -> "BASS-ALG-01R2-sigma23-fails-specific-obligation"
]

$ALG01R2Hostile = BASS`Bianchi`ValidateHostileWitnesses[];
VerificationTest[
 SubsetQ[
  Keys[$ALG01R2Hostile],
  {
   "EXCEPTIONAL_SIGMA13_DELETE",
   "EXCEPTIONAL_SIGMA23_DELETE",
   "EXCEPTIONAL_SHEAR_DELETE"
  }
 ],
 True,
 TestID -> "BASS-ALG-01R2-hostile-carrier-mutations-registered"
]
VerificationTest[
 And @@ Lookup[
  $ALG01R2Hostile,
  {
   "EXCEPTIONAL_SIGMA13_DELETE",
   "EXCEPTIONAL_SIGMA23_DELETE",
   "EXCEPTIONAL_SHEAR_DELETE"
  },
  <||>
 ][[All, "detected"]],
 True,
 TestID -> "BASS-ALG-01R2-hostile-carrier-mutations-detected"
]

VerificationTest[
 FreeQ[
  Lookup[$ALG01R2ExceptionalSpec, "physical_predicates", {}],
  _String?(StringContainsQ[#, "Sigma13!=0" | "Sigma23!=0"] &)
 ],
 True,
 TestID -> "BASS-ALG-01R2-witness-obligations-not-physical-predicates"
]
