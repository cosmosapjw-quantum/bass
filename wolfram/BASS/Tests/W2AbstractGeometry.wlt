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

$BASSW2Creation = BASS`Geometry`CreateAbstract1Plus3Geometry[];
$BASSW2Backend = BASS`Geometry`W2CanonicalBackendReceipt[];
$BASSW2Model = BASS`Geometry`Abstract1Plus3ModelRegistry[];
$BASSW2Residuals = BASS`Geometry`Abstract1Plus3Residuals[];
$BASSW2Equations = BASS`Geometry`Abstract1Plus3EquationRegistry[];
$BASSW2Payload = BASS`Geometry`Abstract1Plus3ReceiptPayload[];
$BASSW2Dimensions = BASS`Authority`DimensionRegistry[];

VerificationTest[
 Lookup[$BASSW2Creation, "status", "FAIL"],
 "PASS",
 TestID -> "BASS-XTENSOR-1P3-001-model-registration"
]

VerificationTest[
 Lookup[$BASSW2Backend, "selected_backend", "none"],
 "pure-wolfram",
 TestID -> "BASS-XTENSOR-1P3-001-pure-canonical-backend"
]

VerificationTest[
 {Lookup[$BASSW2Backend, "external_accelerator_selected", True],
  Lookup[$BASSW2Backend, "selection_is_explicit", False]},
 {False, True},
 TestID -> "BASS-XTENSOR-1P3-001-backend-not-silent"
]

VerificationTest[
 BASS`Geometry`Abstract1Plus3ModelRegistryQ[$BASSW2Model],
 True,
 TestID -> "BASS-XTENSOR-1P3-001-model-registry"
]

VerificationTest[
 Lookup[$BASSW2Residuals, "status", "FAIL"],
 "PASS",
 TestID -> "BASS-XTENSOR-1P3-001-residual-status"
]

VerificationTest[
 Values[Lookup[$BASSW2Residuals, "exact_residuals", <||>]],
 ConstantArray[0, 7],
 TestID -> "BASS-XTENSOR-1P3-001-exact-zero-residuals"
]

VerificationTest[
 AllTrue[Values[Lookup[$BASSW2Residuals, "structural_checks", <||>]],
  TrueQ],
 True,
 TestID -> "BASS-XTENSOR-1P3-001-structural-symmetries"
]

VerificationTest[
 BASS`Geometry`Abstract1Plus3RegistryQ[$BASSW2Equations],
 True,
 TestID -> "BASS-XTENSOR-1P3-001-equation-registry"
]

VerificationTest[
 Lookup[$BASSW2Equations, "formula_id"],
 {"W2-GEO-001", "W2-GEO-002", "W2-KIN-001", "W2-KIN-002",
  "W2-KIN-003", "W2-KIN-004", "W2-CURV-001", "W2-CURV-002",
  "W2-CURV-003"},
 TestID -> "BASS-XTENSOR-1P3-001-formula-id-order"
]

VerificationTest[
 BASS`Geometry`GaussCodazziSignRegistryQ[$BASSW2Equations],
 True,
 TestID -> "BASS-XTENSOR-1P3-001-gauss-codazzi-signs"
]

VerificationTest[
 Lookup[Lookup[$BASSW2Dimensions, "quantities"], "A_a"],
 <|"L" -> -1, "M" -> 0, "T" -> 0, "Theta" -> 0|>,
 TestID -> "BASS-XTENSOR-1P3-001-acceleration-dimension"
]

VerificationTest[
 Lookup[Lookup[$BASSW2Dimensions, "quantities"], "K_ab"],
 <|"L" -> -1, "M" -> 0, "T" -> 0, "Theta" -> 0|>,
 TestID -> "BASS-XTENSOR-1P3-001-extrinsic-curvature-dimension"
]

VerificationTest[
 Lookup[Lookup[$BASSW2Dimensions, "quantities"], "R3_scalar"],
 <|"L" -> -2, "M" -> 0, "T" -> 0, "Theta" -> 0|>,
 TestID -> "BASS-XTENSOR-1P3-001-spatial-curvature-dimension"
]

VerificationTest[
 BASS`IR`RawJSONRoundTripQ[$BASSW2Payload],
 True,
 TestID -> "BASS-XTENSOR-1P3-001-json-safe-receipt"
]

VerificationTest[
 Lookup[$BASSW2Payload, "claim_boundary", {}],
 {"W2_ABSTRACT_1PLUS3_PROJECTOR_AND_KINEMATIC_INFRASTRUCTURE_VERIFIED",
  "GAUSS_CODAZZI_SIGN_REGISTRY_VERIFIED",
  "NO_XCOBA_COMPONENT_DUAL_PROOF",
  "NO_BACKGROUND_EINSTEIN_EQUATIONS",
  "NO_IMPLEMENTATION_PARITY",
  "NO_SCIENCE_VALIDITY",
  "NO_PASS_RF04"},
 TestID -> "BASS-XTENSOR-1P3-001-claim-boundary"
]
