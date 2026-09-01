$GEO02Witnesses = BASS`Bianchi`CanonicalWitnessRegistry[];
$GEO02Labels = {"I", "II", "V", "IX", "VI_-1/9"};

$GEO02ZeroQ[expression_] :=
 AllTrue[Flatten[{expression}], TrueQ[PossibleZeroQ[#]] &];

$GEO02Connection[label_String] := With[
 {witness = $GEO02Witnesses[label]},
 BASS`Geometry`LeviCivitaConnection[witness["a"], witness["n"]]
];

$GEO02TensorTransform[rotation_, tensor_] := Array[
 Function[{gamma, alpha, beta},
  Sum[
   rotation[[gamma, rho]] rotation[[alpha, mu]] rotation[[beta, nu]]
    tensor[[rho, mu, nu]],
   {rho, 3}, {mu, 3}, {nu, 3}
  ]
 ],
 {3, 3, 3}
] // Simplify;

VerificationTest[
 NameQ["BASS`Geometry`LeviCivitaConnection"], True,
 TestID -> "BASS-GEO-02-API-connection"]
VerificationTest[
 NameQ["BASS`Geometry`ConnectionTorsionResidual"], True,
 TestID -> "BASS-GEO-02-API-torsion"]
VerificationTest[
 NameQ["BASS`Geometry`ConnectionMetricCompatibilityResidual"], True,
 TestID -> "BASS-GEO-02-API-metric-compatibility"]
VerificationTest[
 NameQ["BASS`Geometry`ConnectionOneFormTerms"], True,
 TestID -> "BASS-GEO-02-API-one-form-terms"]
VerificationTest[
 NameQ["BASS`Geometry`ConnectionCovarianceQ"], True,
 TestID -> "BASS-GEO-02-API-frame-covariance"]

VerificationTest[
 FailureQ[BASS`Geometry`LeviCivitaConnection[{0, 0}, IdentityMatrix[3]]],
 True,
 TestID -> "BASS-GEO-02-invalid-input-fails-closed"]

$GEO02TorsionReports = AssociationMap[
 With[{witness = $GEO02Witnesses[#]},
   BASS`Geometry`ConnectionTorsionResidual[witness["a"], witness["n"]]
 ] &,
 $GEO02Labels
];
VerificationTest[
 AllTrue[Values[$GEO02TorsionReports], $GEO02ZeroQ], True,
 TestID -> "BASS-GEO-02-torsion-free-all-witnesses"]

$GEO02MetricReports = AssociationMap[
 With[{witness = $GEO02Witnesses[#]},
   BASS`Geometry`ConnectionMetricCompatibilityResidual[
    witness["a"], witness["n"]
   ]
 ] &,
 $GEO02Labels
];
VerificationTest[
 AllTrue[Values[$GEO02MetricReports], $GEO02ZeroQ], True,
 TestID -> "BASS-GEO-02-metric-compatible-all-witnesses"]

$GEO02ConnectionCounts = AssociationMap[
 Count[Flatten[$GEO02Connection[#]],
   entry_ /; ! TrueQ[PossibleZeroQ[entry]]
 ] &,
 $GEO02Labels
];
VerificationTest[
 Lookup[$GEO02ConnectionCounts, $GEO02Labels], {0, 6, 4, 6, 10},
 TestID -> "BASS-GEO-02-connection-component-counts"]

VerificationTest[
 Cases[
  Flatten[
   Table[
    If[
     ! TrueQ[PossibleZeroQ[$GEO02Connection["II"][[gamma, alpha, beta]]]],
     {gamma, alpha, beta,
      $GEO02Connection["II"][[gamma, alpha, beta]]},
     Nothing
    ],
    {gamma, 3}, {alpha, 3}, {beta, 3}
   ],
   2
  ],
  {_Integer, _Integer, _Integer, _}
 ],
 {
  {1, 2, 3, 1/2}, {1, 3, 2, -1/2},
  {2, 1, 3, 1/2}, {2, 3, 1, 1/2},
  {3, 1, 2, -1/2}, {3, 2, 1, -1/2}
 },
 TestID -> "BASS-GEO-02-type-II-exact-connection"]

VerificationTest[
 Cases[
  Flatten[
   Table[
    If[
     ! TrueQ[PossibleZeroQ[$GEO02Connection["V"][[gamma, alpha, beta]]]],
     {gamma, alpha, beta,
      $GEO02Connection["V"][[gamma, alpha, beta]]},
     Nothing
    ],
    {gamma, 3}, {alpha, 3}, {beta, 3}
   ],
   2
  ],
  {_Integer, _Integer, _Integer, _}
 ],
 {
  {1, 2, 2, 1}, {1, 3, 3, 1},
  {2, 2, 1, -1}, {3, 3, 1, -1}
 },
 TestID -> "BASS-GEO-02-type-V-exact-connection"]

VerificationTest[
 With[{witness = $GEO02Witnesses["IX"]},
  $GEO02ZeroQ[
   $GEO02Connection["IX"]
    - BASS`Geometry`BianchiStructureConstants[
       witness["a"], witness["n"]
      ]/2
  ]
 ],
 True,
 TestID -> "BASS-GEO-02-type-IX-half-structure"]

$GEO02OneFormCounts = AssociationMap[
 Length @ With[{witness = $GEO02Witnesses[#]},
   BASS`Geometry`ConnectionOneFormTerms[witness["a"], witness["n"]]
 ] &,
 $GEO02Labels
];
VerificationTest[
 Lookup[$GEO02OneFormCounts, $GEO02Labels], {0, 6, 4, 6, 10},
 TestID -> "BASS-GEO-02-one-form-term-counts"]

$GEO02ProperRotation = {{0, 1, 0}, {0, 0, 1}, {1, 0, 0}};
$GEO02ImproperRotation = DiagonalMatrix[{-1, 1, 1}];
VerificationTest[
 And @@ Flatten @ Table[
   With[{witness = $GEO02Witnesses[label]},
    BASS`Geometry`ConnectionCovarianceQ[
     rotation, witness["a"], witness["n"]
    ]
   ],
   {label, {"II", "VI_-1/9"}},
   {rotation, {$GEO02ProperRotation, $GEO02ImproperRotation}}
 ],
 True,
 TestID -> "BASS-GEO-02-proper-improper-O3-covariance"]

$GEO02WrongParityWitness = $GEO02Witnesses["II"];
$GEO02WrongParityGenerated = BASS`Geometry`LeviCivitaConnection[
 $GEO02ImproperRotation . $GEO02WrongParityWitness["a"],
 $GEO02ImproperRotation . $GEO02WrongParityWitness["n"] .
  Transpose[$GEO02ImproperRotation]
];
$GEO02CorrectlyTransformed = $GEO02TensorTransform[
 $GEO02ImproperRotation,
 $GEO02Connection["II"]
];
VerificationTest[
 $GEO02ZeroQ[
  $GEO02WrongParityGenerated - $GEO02CorrectlyTransformed
 ],
 False,
 TestID -> "BASS-GEO-02-missing-detR-mutation-detected"]
