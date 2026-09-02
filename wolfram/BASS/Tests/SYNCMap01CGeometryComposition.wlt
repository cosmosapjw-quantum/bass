If[!ValueQ[$BASSXActSource],
 $BASSXActSource = "https://xact.es/download/xAct_1.3.0.tgz"
];
If[!ValueQ[$BASSXActExpectedSHA256],
 $BASSXActExpectedSHA256 =
  "7a6c5f600868a3922668b020a15c0692f76574ff2a559808c62d460cef1b07be"
];
If[!MemberQ[$Packages, "xAct`xTensor`"],
 $BASSSYNCMap01CXActReceipt = BASS`Authority`ActivatePinnedXAct[
   $BASSXActSource, $BASSXActExpectedSHA256]
];

$BASSSYNCMap01CRequiredAPIs = {
 "BASS`Geometry`SpatialRiemannTensor",
 "BASS`Geometry`SpatialRicciTensor",
 "BASS`Geometry`SpatialScalarCurvature",
 "BASS`Geometry`SpatialRiemannSymmetryReport",
 "BASS`Geometry`SpatialCurvatureCovarianceQ",
 "BASS`Geometry`SpatialCurvatureWitnessRegistry",
 "BASS`Geometry`ValidateSpatialCurvatureWitnesses",
 "BASS`Geometry`SpatialCurvatureFormulaRegistry",
 "BASS`Geometry`GeometryLineageCompositionReceipt",
 "BASS`Geometry`RunSpatialXCobaCurvatureWitnesses"
};

VerificationTest[
 And @@ (NameQ /@ $BASSSYNCMap01CRequiredAPIs),
 True,
 TestID -> "BASS-SYNC-MAP-01C-API-RED-001"
]

$BASSSYNCMap01CRegistry = BASS`Geometry`SpatialCurvatureFormulaRegistry[];
$BASSSYNCMap01CDirect = BASS`Geometry`ValidateSpatialCurvatureWitnesses[];
$BASSSYNCMap01CXCoba = BASS`Geometry`RunSpatialXCobaCurvatureWitnesses[];
$BASSSYNCMap01CReceipt = BASS`Geometry`GeometryLineageCompositionReceipt[];

VerificationTest[
 BASS`Geometry`SpatialCurvatureFormulaRegistryQ[$BASSSYNCMap01CRegistry],
 True,
 TestID -> "BASS-SYNC-MAP-01C-FORMULA-REGISTRY-001"
]

VerificationTest[
 Lookup[$BASSSYNCMap01CRegistry, "formula_id"],
 {"GEO03-RIEMANN-001", "GEO03-RICCI-001", "GEO03-SCALAR-001"},
 TestID -> "BASS-SYNC-MAP-01C-FORMULA-OWNER-SPLIT-001"
]

VerificationTest[
 AllTrue[Values[$BASSSYNCMap01CDirect], TrueQ[Lookup[#, "pass", False]] &],
 True,
 TestID -> "BASS-SYNC-MAP-01C-DIRECT-WITNESSES-001"
]

VerificationTest[
 Map[Lookup[#, "scalar_curvature", Missing[]] &, $BASSSYNCMap01CDirect],
 <|"I" -> 0, "II" -> -1/2, "V" -> -6, "IX" -> 3/2,
   "VI_-1/9" -> -26|>,
 TestID -> "BASS-SYNC-MAP-01C-SCALAR-WITNESSES-001"
]

VerificationTest[
 Map[Lookup[#, "section_12", Missing[]] &, $BASSSYNCMap01CDirect],
 <|"I" -> 0, "II" -> 1/4, "V" -> -1, "IX" -> 1/4,
   "VI_-1/9" -> -15|>,
 TestID -> "BASS-SYNC-MAP-01C-SECTION-WITNESSES-001"
]

VerificationTest[
 FailureQ[BASS`Geometry`SpatialRiemannTensor[
   {1, 0, 0}, IdentityMatrix[3]]],
 True,
 TestID -> "BASS-SYNC-MAP-01C-NONJACOBI-REJECTED-001"
]

$BASSSYNCMap01CProperR = {{0, -1, 0}, {1, 0, 0}, {0, 0, 1}};
$BASSSYNCMap01CImproperR = DiagonalMatrix[{-1, 1, 1}];
$BASSSYNCMap01CWitnesses = BASS`Bianchi`CanonicalWitnessRegistry[];

VerificationTest[
 And[
  BASS`Geometry`SpatialCurvatureCovarianceQ[
   $BASSSYNCMap01CProperR,
   $BASSSYNCMap01CWitnesses["II"]["a"],
   $BASSSYNCMap01CWitnesses["II"]["n"]],
  BASS`Geometry`SpatialCurvatureCovarianceQ[
   $BASSSYNCMap01CImproperR,
   $BASSSYNCMap01CWitnesses["VI_-1/9"]["a"],
   $BASSSYNCMap01CWitnesses["VI_-1/9"]["n"]]
 ],
 True,
 TestID -> "BASS-SYNC-MAP-01C-O3-COVARIANCE-001"
]

VerificationTest[
 Map[Lookup[#, "status", "FAIL"] &, $BASSSYNCMap01CXCoba],
 <|"I" -> "PASS", "V" -> "PASS", "IX" -> "PASS"|>,
 TestID -> "BASS-SYNC-MAP-01C-XCOBA-STATUS-001"
]

VerificationTest[
 Map[
  Lookup[Lookup[#, "checks", <||>], "dual_full_riemann_match", False] &,
  $BASSSYNCMap01CXCoba
 ],
 <|"I" -> True, "V" -> True, "IX" -> True|>,
 TestID -> "BASS-SYNC-MAP-01C-XCOBA-FULL-RIEMANN-001"
]

VerificationTest[
 BASS`Geometry`GeometryLineageCompositionReceiptQ[$BASSSYNCMap01CReceipt],
 True,
 TestID -> "BASS-SYNC-MAP-01C-LINEAGE-RECEIPT-001"
]

VerificationTest[
 BASS`IR`RawJSONRoundTripQ[$BASSSYNCMap01CReceipt],
 True,
 TestID -> "BASS-SYNC-MAP-01C-RECEIPT-JSON-001"
]

VerificationTest[
 Lookup[$BASSSYNCMap01CReceipt, "claim_boundary", None],
 "CANONICAL_CONNECTION_TO_SPATIAL_CURVATURE_COMPOSITION_ONLY_NO_EINSTEIN_BACKGROUND_OR_SCIENCE_PROMOTION",
 TestID -> "BASS-SYNC-MAP-01C-CLAIM-BOUNDARY-001"
]
