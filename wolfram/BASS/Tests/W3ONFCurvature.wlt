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

$BASSW3FormulaRegistry = BASS`Geometry`W3FormulaRegistry[];
$BASSW3Direct = BASS`Geometry`ValidateONFCurvatureWitnesses[];
$BASSW3XCoba = BASS`Geometry`RunXCobaCurvatureWitnesses[];
$BASSW3Payload = BASS`Geometry`XCobaCurvatureWitnessReceiptPayload[];

VerificationTest[
 BASS`Geometry`W3FormulaRegistryQ[$BASSW3FormulaRegistry],
 True,
 TestID -> "BASS-W3-FORMULA-REGISTRY-001-valid"
]

VerificationTest[
 Lookup[$BASSW3FormulaRegistry, "formula_id"],
 {"W3-CONN-001", "W3-RIEM-001", "W3-RICCI-001", "W3-SCALAR-001"},
 TestID -> "BASS-W3-FORMULA-REGISTRY-001-order"
]

VerificationTest[
 AllTrue[Values[$BASSW3Direct], TrueQ[Lookup[#, "pass", False]] &],
 True,
 TestID -> "BASS-W3-DIRECT-ONF-001-all-witnesses"
]

VerificationTest[
 AssociationMap[
  Lookup[Lookup[#, "checks", <||>], "connection_linear_solve", False] &,
  $BASSW3Direct
 ],
 <|"I" -> True, "V" -> True, "IX" -> True|>,
 TestID -> "BASS-W3-CONNECTION-001-independent-linear-solve"
]

VerificationTest[
 AssociationMap[Lookup[#, "scalar_curvature", Missing[]] &, $BASSW3Direct],
 <|"I" -> 0, "V" -> -6, "IX" -> 3/2|>,
 TestID -> "BASS-W3-CURVATURE-001-scalar-witnesses"
]

VerificationTest[
 AssociationMap[Lookup[#, "section_12", Missing[]] &, $BASSW3Direct],
 <|"I" -> 0, "V" -> -1, "IX" -> 1/4|>,
 TestID -> "BASS-W3-CURVATURE-001-section-witnesses"
]

VerificationTest[
 AssociationMap[Lookup[#, "status", "FAIL"] &, $BASSW3XCoba],
 <|"I" -> "PASS", "V" -> "PASS", "IX" -> "PASS"|>,
 TestID -> "BASS-W3-XCOBA-001-status"
]

VerificationTest[
 AssociationMap[
  Lookup[Lookup[#, "checks", <||>], "component_shape_3333", False] &,
  $BASSW3XCoba
 ],
 <|"I" -> True, "V" -> True, "IX" -> True|>,
 TestID -> "BASS-W3-XCOBA-001-component-shapes"
]

VerificationTest[
 AssociationMap[
  Lookup[Lookup[#, "checks", <||>], "orthonormal_frame", False] &,
  $BASSW3XCoba
 ],
 <|"I" -> True, "V" -> True, "IX" -> True|>,
 TestID -> "BASS-W3-XCOBA-001-frame-metric"
]

VerificationTest[
 AssociationMap[
  Lookup[Lookup[#, "checks", <||>], "xact_to_bass_sign_adapter", 0] &,
  $BASSW3XCoba
 ],
 <|"I" -> -1, "V" -> -1, "IX" -> -1|>,
 TestID -> "BASS-W3-XCOBA-001-riemann-sign-adapter"
]

VerificationTest[
 AssociationMap[
  Lookup[Lookup[#, "checks", <||>], "dual_full_riemann_match", False] &,
  $BASSW3XCoba
 ],
 <|"I" -> True, "V" -> True, "IX" -> True|>,
 TestID -> "BASS-W3-XCOBA-001-full-riemann-dual"
]

VerificationTest[
 Lookup[Lookup[$BASSW3Payload, "summary", <||>], "all_pass", False],
 True,
 TestID -> "BASS-W3-RECEIPT-001-all-pass"
]

VerificationTest[
 Lookup[Lookup[$BASSW3Payload, "summary", <||>],
  "all_full_riemann_match", False],
 True,
 TestID -> "BASS-W3-RECEIPT-001-full-riemann"
]

VerificationTest[
 BASS`IR`RawJSONRoundTripQ[$BASSW3Payload],
 True,
 TestID -> "BASS-W3-RECEIPT-001-json-roundtrip"
]

VerificationTest[
 Lookup[$BASSW3Payload, "claim_boundary", {}],
 {"W3_I_V_IX_XCOBA_FULL_RIEMANN_WITNESSES_VERIFIED",
  "NO_ALL_TYPE_CURVATURE_SPECIALIZATION",
  "NO_BACKGROUND_EINSTEIN_MATTER_EVOLUTION",
  "NO_NUMERICAL_PARITY",
  "NO_SCIENCE_VALIDITY",
  "NO_PASS_RF04"},
 TestID -> "BASS-W3-RECEIPT-001-claim-boundary"
]
