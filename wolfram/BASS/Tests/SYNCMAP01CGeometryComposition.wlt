If[!ValueQ[$BASSXActSource],
 $BASSXActSource = "https://xact.es/download/xAct_1.3.0.tgz"
];
If[!ValueQ[$BASSXActExpectedSHA256],
 $BASSXActExpectedSHA256 =
  "7a6c5f600868a3922668b020a15c0692f76574ff2a559808c62d460cef1b07be"
];
If[!MemberQ[$Packages, "xAct`xTensor`"],
 $BASSXActReceipt = BASS`Authority`ActivatePinnedXAct[
   $BASSXActSource, $BASSXActExpectedSHA256]
];

$BASSSyncMap01CParent =
 "c787e6c51608568fcb60d52f010235f8cb2c1076";
$BASSSyncMap01CDonor =
 "5d3e8ecce2a40a1bc2b43af7daa985e042d9815f";
$BASSSyncMap01CReceipt =
 BASS`Geometry`GeometryLineageCompositionReceipt[];
$BASSSyncMap01CW2Registry =
 BASS`Geometry`Abstract1Plus3EquationRegistry[];
$BASSSyncMap01CDirect =
 BASS`Geometry`ValidateONFCurvatureWitnesses[];
$BASSSyncMap01CXCoba =
 BASS`Geometry`RunXCobaCurvatureWitnesses[];

VerificationTest[
 BASS`Geometry`GeometryLineageCompositionReceiptQ[
  $BASSSyncMap01CReceipt],
 True,
 TestID -> "BASS-SYNC-MAP-01C-001-composition-receipt"
]

VerificationTest[
 Lookup[Lookup[$BASSSyncMap01CReceipt, "canonical_parent", <||>],
  "commit", None],
 $BASSSyncMap01CParent,
 TestID -> "BASS-SYNC-MAP-01C-001-parent-identity"
]

VerificationTest[
 Lookup[Lookup[$BASSSyncMap01CReceipt, "tested_donor", <||>],
  "commit", None],
 $BASSSyncMap01CDonor,
 TestID -> "BASS-SYNC-MAP-01C-001-donor-identity"
]

VerificationTest[
 BASS`Geometry`ConnectionCompositionReceiptQ[
  BASS`Geometry`ConnectionCompositionReceipt[]],
 True,
 TestID -> "BASS-SYNC-MAP-01C-001-canonical-connection-parent"
]

VerificationTest[
 BASS`Geometry`Abstract1Plus3RegistryQ[$BASSSyncMap01CW2Registry],
 True,
 TestID -> "BASS-SYNC-MAP-01C-001-w2-equation-registry"
]

VerificationTest[
 BASS`Geometry`GaussCodazziSignRegistryQ[$BASSSyncMap01CW2Registry],
 True,
 TestID -> "BASS-SYNC-MAP-01C-001-gauss-codazzi-signs"
]

VerificationTest[
 BASS`Geometry`ONFLeviCivitaConnection[
   {1, 0, 0}, ConstantArray[0, {3, 3}]] ===
  BASS`Geometry`ConnectionToLockedGammaOrder[
   BASS`Geometry`LeviCivitaConnection[
    {1, 0, 0}, ConstantArray[0, {3, 3}]]],
 True,
 TestID -> "BASS-SYNC-MAP-01C-001-single-connection-implementation"
]

VerificationTest[
 Map[Lookup[#, "scalar_curvature", Missing[]] &,
  $BASSSyncMap01CDirect],
 <|"I" -> 0, "V" -> -6, "IX" -> 3/2|>,
 TestID -> "BASS-SYNC-MAP-01C-001-direct-curvature"
]

VerificationTest[
 Map[
  Lookup[Lookup[#, "checks", <||>], "canonical_storage_adapter", False] &,
  $BASSSyncMap01CDirect],
 <|"I" -> True, "V" -> True, "IX" -> True|>,
 TestID -> "BASS-SYNC-MAP-01C-001-storage-adapter"
]

VerificationTest[
 Map[
  Lookup[Lookup[#, "checks", <||>], "dual_full_riemann_match", False] &,
  $BASSSyncMap01CXCoba],
 <|"I" -> True, "V" -> True, "IX" -> True|>,
 TestID -> "BASS-SYNC-MAP-01C-001-xcoba-dual-full-riemann"
]

VerificationTest[
 Lookup[First[BASS`Geometry`W3FormulaRegistry[]],
  "canonical_connection_formula_id", None],
 "BASS.GEO.LEVI_CIVITA_CONNECTION.001",
 TestID -> "BASS-SYNC-MAP-01C-001-formula-owner"
]

VerificationTest[
 Lookup[BASS`Authority`DimensionRegistry[], "schema_version", None],
 "1.1.0",
 TestID -> "BASS-SYNC-MAP-01C-001-dimension-registry"
]

VerificationTest[
 Lookup[$BASSSyncMap01CReceipt, "connection_implementation_count", 0],
 1,
 TestID -> "BASS-SYNC-MAP-01C-001-no-duplicate-connection"
]

VerificationTest[
 Lookup[$BASSSyncMap01CReceipt, "claim_boundary", {}],
 {"W2_ABSTRACT_1PLUS3_AND_GAUSS_CODAZZI_REGISTRY_COMPOSED",
  "GEO03_SPATIAL_CURVATURE_I_V_IX_DIRECT_WITNESSES_VERIFIED",
  "NO_BACKGROUND_EINSTEIN_MATTER_EVOLUTION",
  "NO_ALL_TYPE_CURVATURE_SPECIALIZATION",
  "NO_NUMERICAL_PARITY",
  "NO_SCIENCE_VALIDITY",
  "NO_PASS_RF04"},
 TestID -> "BASS-SYNC-MAP-01C-001-claim-boundary"
]
