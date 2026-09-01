$ALG01R1Specs = BASS`Bianchi`CanonicalTypeSpecRegistry[];
$ALG01R1Witnesses = BASS`Bianchi`CanonicalWitnessRegistry[];
$ALG01R1ExceptionalSpec = $ALG01R1Specs["VI_-1/9"];
$ALG01R1ExceptionalWitness = $ALG01R1Witnesses["VI_-1/9"];
$ALG01R1ShearDeletedWitness = ReplacePart[
 $ALG01R1ExceptionalWitness,
 "shear" -> ConstantArray[0, {3, 3}]
];
$ALG01R1ShearDeletedReport = BASS`Bianchi`BranchPredicateReport[
 $ALG01R1ExceptionalSpec,
 $ALG01R1ShearDeletedWitness
];

VerificationTest[
 Lookup[
  $ALG01R1ExceptionalSpec,
  "counted_public_algebra_type",
  Missing["KeyAbsent"]
 ],
 False,
 TestID -> "BASS-ALG-01R1-exceptional-not-twelfth-type"
]
VerificationTest[
 MemberQ[
  Lookup[$ALG01R1ExceptionalSpec, "witness_obligations", {}],
  "non_diagonal_shear_survival"
 ],
 True,
 TestID -> "BASS-ALG-01R1-exceptional-shear-obligation-declared"
]
VerificationTest[
 TrueQ[$ALG01R1ShearDeletedReport["pass"]],
 False,
 TestID -> "BASS-ALG-01R1-shear-deletion-rejected"
]
VerificationTest[
 MemberQ[
  Lookup[$ALG01R1ShearDeletedReport, "failed_checks", {}],
  "witness_obligations"
 ],
 True,
 TestID -> "BASS-ALG-01R1-shear-deletion-fails-obligation"
]

$ALG01R1ProperRotation = {{0, 1, 0}, {0, 0, 1}, {1, 0, 0}};
$ALG01R1ImproperRotation = DiagonalMatrix[{-1, 1, 1}];
$ALG01R1IIVector = $ALG01R1Witnesses["II"]["a"];
$ALG01R1IIMatrix = $ALG01R1Witnesses["II"]["n"];
$ALG01R1ExceptionalVector = $ALG01R1ExceptionalWitness["a"];
$ALG01R1ExceptionalMatrix = $ALG01R1ExceptionalWitness["n"];

VerificationTest[
 NameQ["BASS`Geometry`StructureCovarianceQ"],
 True,
 TestID -> "BASS-ALG-01R1-covariance-api-exists"
]
VerificationTest[
 If[
  NameQ["BASS`Geometry`StructureCovarianceQ"],
  BASS`Geometry`StructureCovarianceQ[
   $ALG01R1ProperRotation,
   $ALG01R1IIVector,
   $ALG01R1IIMatrix
  ],
  False
 ],
 True,
 TestID -> "BASS-ALG-01R1-II-proper-covariance"
]
VerificationTest[
 If[
  NameQ["BASS`Geometry`StructureCovarianceQ"],
  BASS`Geometry`StructureCovarianceQ[
   $ALG01R1ImproperRotation,
   $ALG01R1IIVector,
   $ALG01R1IIMatrix
  ],
  False
 ],
 True,
 TestID -> "BASS-ALG-01R1-II-improper-covariance"
]
VerificationTest[
 If[
  NameQ["BASS`Geometry`StructureCovarianceQ"],
  BASS`Geometry`StructureCovarianceQ[
   $ALG01R1ProperRotation,
   $ALG01R1ExceptionalVector,
   $ALG01R1ExceptionalMatrix
  ],
  False
 ],
 True,
 TestID -> "BASS-ALG-01R1-exceptional-proper-covariance"
]
VerificationTest[
 If[
  NameQ["BASS`Geometry`StructureCovarianceQ"],
  BASS`Geometry`StructureCovarianceQ[
   $ALG01R1ImproperRotation,
   $ALG01R1ExceptionalVector,
   $ALG01R1ExceptionalMatrix
  ],
  False
 ],
 True,
 TestID -> "BASS-ALG-01R1-exceptional-improper-covariance"
]

$ALG01R1WrongImproperDetected = If[
 And[
  NameQ["BASS`Geometry`TransformStructureConstants"],
  NameQ["BASS`Geometry`BianchiStructureConstants"]
 ],
 Module[{original, expected, wrongVector, wrongMatrix, wrongStructure},
  original = BASS`Geometry`BianchiStructureConstants[
   $ALG01R1IIVector,
   $ALG01R1IIMatrix
  ];
  expected = BASS`Geometry`TransformStructureConstants[
   $ALG01R1ImproperRotation,
   original
  ];
  wrongVector = Simplify[
   $ALG01R1ImproperRotation . $ALG01R1IIVector
  ];
  wrongMatrix = Simplify[
   $ALG01R1ImproperRotation . $ALG01R1IIMatrix .
    Transpose[$ALG01R1ImproperRotation]
  ];
  wrongStructure = BASS`Geometry`BianchiStructureConstants[
   wrongVector,
   wrongMatrix
  ];
  Not @ AllTrue[
    Flatten[Simplify[wrongStructure - expected]],
    TrueQ[PossibleZeroQ[#]] &
   ]
 ],
 False
];
VerificationTest[
 $ALG01R1WrongImproperDetected,
 True,
 TestID -> "BASS-ALG-01R1-improper-pseudotensor-sign-mutation-detected"
]
VerificationTest[
 If[
  NameQ["BASS`Geometry`TransformBianchiAlgebraData"],
  FailureQ[
   BASS`Geometry`TransformBianchiAlgebraData[
    DiagonalMatrix[{2, 1, 1}],
    $ALG01R1IIVector,
    $ALG01R1IIMatrix
   ]
  ],
  False
 ],
 True,
 TestID -> "BASS-ALG-01R1-nonorthogonal-frame-fails-closed"
]
