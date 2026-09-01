$GEO02R2Labels = {"I", "II", "V", "IX", "VI_-1/9"};
$GEO02R2Witnesses = BASS`Bianchi`CanonicalWitnessRegistry[];
$GEO02R2ParentSemanticHash =
 "e0e5fbba464a839fcb5b11d41c7772c666224ec69f806910aab3bfab5a2f1762";

$GEO02R2ZeroQ[expression_] :=
 AllTrue[Flatten[{expression}], TrueQ[PossibleZeroQ[#]] &];

$GEO02R2Connection[label_String] := With[
 {witness = $GEO02R2Witnesses[label]},
 BASS`Geometry`LeviCivitaConnection[witness["a"], witness["n"]]
];

$GEO02R2GeneratedTransform[rotation_, tensor_] := Array[
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
 And @@ (NameQ /@ {
   "BASS`Geometry`LeviCivitaConnection",
   "BASS`Geometry`ConnectionTorsionResidual",
   "BASS`Geometry`ConnectionMetricCompatibilityResidual",
   "BASS`Geometry`ConnectionOneFormTerms",
   "BASS`Geometry`ConnectionCovarianceQ",
   "BASS`Geometry`ConnectionToLockedGammaOrder",
   "BASS`Geometry`ConnectionFromLockedGammaOrder",
   "BASS`Geometry`ConnectionCompositionReceipt",
   "BASS`Geometry`ConnectionCompositionReceiptQ"
  }),
 True,
 TestID -> "BASS-GEO-02R2-API-composed-connection-surface"]

VerificationTest[
 FailureQ[BASS`Geometry`LeviCivitaConnection[{0, 0}, IdentityMatrix[3]]],
 True,
 TestID -> "BASS-GEO-02R2-invalid-input-fails-closed"]

VerificationTest[
 AllTrue[$GEO02R2Labels,
  With[{witness = $GEO02R2Witnesses[#]},
    $GEO02R2ZeroQ @ BASS`Geometry`ConnectionTorsionResidual[
      witness["a"], witness["n"]
    ]
  ] &
 ],
 True,
 TestID -> "BASS-GEO-02R2-torsion-free-all-witnesses"]

VerificationTest[
 AllTrue[$GEO02R2Labels,
  With[{witness = $GEO02R2Witnesses[#]},
    $GEO02R2ZeroQ @
     BASS`Geometry`ConnectionMetricCompatibilityResidual[
      witness["a"], witness["n"]
     ]
  ] &
 ],
 True,
 TestID -> "BASS-GEO-02R2-metric-compatible-all-witnesses"]

$GEO02R2ConnectionCounts = AssociationMap[
 Count[Flatten[$GEO02R2Connection[#]],
   entry_ /; ! TrueQ[PossibleZeroQ[entry]]
 ] &,
 $GEO02R2Labels
];
VerificationTest[
 Lookup[$GEO02R2ConnectionCounts, $GEO02R2Labels],
 {0, 6, 4, 6, 10},
 TestID -> "BASS-GEO-02R2-connection-component-counts"]

VerificationTest[
 Cases[
  Flatten[
   Table[
    If[! TrueQ[PossibleZeroQ[$GEO02R2Connection["II"][[g, a, b]]]],
     {g, a, b, $GEO02R2Connection["II"][[g, a, b]]}, Nothing],
    {g, 3}, {a, 3}, {b, 3}], 2],
  {_Integer, _Integer, _Integer, _}],
 {{1, 2, 3, 1/2}, {1, 3, 2, -1/2},
  {2, 1, 3, 1/2}, {2, 3, 1, 1/2},
  {3, 1, 2, -1/2}, {3, 2, 1, -1/2}},
 TestID -> "BASS-GEO-02R2-type-II-exact-connection"]

VerificationTest[
 Cases[
  Flatten[
   Table[
    If[! TrueQ[PossibleZeroQ[$GEO02R2Connection["V"][[g, a, b]]]],
     {g, a, b, $GEO02R2Connection["V"][[g, a, b]]}, Nothing],
    {g, 3}, {a, 3}, {b, 3}], 2],
  {_Integer, _Integer, _Integer, _}],
 {{1, 2, 2, 1}, {1, 3, 3, 1},
  {2, 2, 1, -1}, {3, 3, 1, -1}},
 TestID -> "BASS-GEO-02R2-type-V-exact-connection"]

VerificationTest[
 With[{witness = $GEO02R2Witnesses["IX"]},
  $GEO02R2ZeroQ[
   $GEO02R2Connection["IX"] -
    BASS`Geometry`BianchiStructureConstants[
      witness["a"], witness["n"]]/2
  ]
 ],
 True,
 TestID -> "BASS-GEO-02R2-type-IX-half-structure"]

$GEO02R2OneFormCounts = AssociationMap[
 Length @ With[{witness = $GEO02R2Witnesses[#]},
   BASS`Geometry`ConnectionOneFormTerms[witness["a"], witness["n"]]
 ] &,
 $GEO02R2Labels
];
VerificationTest[
 Lookup[$GEO02R2OneFormCounts, $GEO02R2Labels],
 {0, 6, 4, 6, 10},
 TestID -> "BASS-GEO-02R2-one-form-counts"]

$GEO02R2Proper = {{0, 1, 0}, {0, 0, 1}, {1, 0, 0}};
$GEO02R2Improper = DiagonalMatrix[{-1, 1, 1}];
VerificationTest[
 And @@ Flatten @ Table[
   With[{witness = $GEO02R2Witnesses[label]},
    BASS`Geometry`ConnectionCovarianceQ[
     rotation, witness["a"], witness["n"]]
   ],
   {label, {"II", "VI_-1/9"}},
   {rotation, {$GEO02R2Proper, $GEO02R2Improper}}
 ],
 True,
 TestID -> "BASS-GEO-02R2-proper-improper-O3-covariance"]

$GEO02R2WrongWitness = $GEO02R2Witnesses["II"];
$GEO02R2WrongParity = BASS`Geometry`LeviCivitaConnection[
 $GEO02R2Improper . $GEO02R2WrongWitness["a"],
 $GEO02R2Improper . $GEO02R2WrongWitness["n"] .
  Transpose[$GEO02R2Improper]
];
VerificationTest[
 $GEO02R2ZeroQ[
  $GEO02R2WrongParity -
   $GEO02R2GeneratedTransform[
    $GEO02R2Improper, $GEO02R2Connection["II"]]
 ],
 False,
 TestID -> "BASS-GEO-02R2-missing-detR-mutation-detected"]

$GEO02R2Probe = Array[Unique["gamma"] &, {3, 3, 3}];
$GEO02R2Locked =
 BASS`Geometry`ConnectionToLockedGammaOrder[$GEO02R2Probe];
VerificationTest[
 $GEO02R2Locked,
 Transpose[$GEO02R2Probe, {2, 3, 1}],
 TestID -> "BASS-GEO-02R2-generated-to-locked-index-order"]
VerificationTest[
 BASS`Geometry`ConnectionFromLockedGammaOrder[$GEO02R2Locked],
 $GEO02R2Probe,
 TestID -> "BASS-GEO-02R2-index-order-roundtrip"]
VerificationTest[
 Table[
  $GEO02R2Locked[[alpha, beta, gamma]] ===
   $GEO02R2Probe[[gamma, alpha, beta]],
  {alpha, 3}, {beta, 3}, {gamma, 3}],
 ConstantArray[True, {3, 3, 3}],
 TestID -> "BASS-GEO-02R2-locked-Gamma-definition-componentwise"]

$GEO02R2Receipt = BASS`Geometry`ConnectionCompositionReceipt[];
VerificationTest[
 BASS`Geometry`ConnectionCompositionReceiptQ[$GEO02R2Receipt],
 True,
 TestID -> "BASS-GEO-02R2-composition-receipt-valid"]
VerificationTest[
 Lookup[$GEO02R2Receipt, "parent_semantic_registry_sha256", None],
 $GEO02R2ParentSemanticHash,
 TestID -> "BASS-GEO-02R2-parent-semantic-identity-preserved"]
VerificationTest[
 Lookup[
  Lookup[$GEO02R2Receipt, "exceptional_carrier_report", <||>],
  "independent_carriers_present", False],
 True,
 TestID -> "BASS-GEO-02R2-exceptional-carriers-preserved"]
VerificationTest[
 Lookup[$GEO02R2Receipt, "curvature_generated", True],
 False,
 TestID -> "BASS-GEO-02R2-no-curvature-promotion"]
