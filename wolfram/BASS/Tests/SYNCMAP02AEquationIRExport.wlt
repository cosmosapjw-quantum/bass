If[!ValueQ[$BASSXActSource],
 $BASSXActSource = "https://xact.es/download/xAct_1.3.0.tgz"
];
If[!ValueQ[$BASSXActExpectedSHA256],
 $BASSXActExpectedSHA256 =
  "7a6c5f600868a3922668b020a15c0692f76574ff2a559808c62d460cef1b07be"
];

$BASSSyncMap02AExpectedIDs = {
 "BASS.GEO.STRUCTURE_CONSTANTS.001",
 "BASS.GEO.SPATIAL_PROJECTOR.001",
 "BASS.GEO.SPATIAL_VOLUME_FORM.001",
 "BASS.GEO.NORMAL_ACCELERATION.001",
 "BASS.GEO.EXTRINSIC_CURVATURE.001",
 "BASS.GEO.NORMAL_DERIVATIVE_DECOMPOSITION.001",
 "BASS.GEO.EXTRINSIC_CURVATURE_SHEAR_SPLIT.001",
 "BASS.GEO.GAUSS.001",
 "BASS.GEO.CODAZZI.001",
 "BASS.GEO.CONTRACTED_GAUSS.001",
 "BASS.GEO.LEVI_CIVITA_CONNECTION.001",
 "BASS.GEO.SPATIAL_RIEMANN.001",
 "BASS.GEO.SPATIAL_RICCI.001",
 "BASS.GEO.SPATIAL_SCALAR.001"
};

VerificationTest[
 And @@ (NameQ /@ {
   "BASS`IR`BASSFormulaGlobalIDMap",
   "BASS`IR`BASSFormulaEquationIRRegistry",
   "BASS`IR`FormulaSemanticProjection",
   "BASS`IR`FormulaSemanticSHA256",
   "BASS`IR`BASSFormulaDependencyEdges",
   "BASS`IR`BASSFormulaSemanticExport",
   "BASS`IR`BASSFormulaSemanticExportQ"
  }),
 True,
 TestID -> "BASS-SYNC-MAP-02A-001-public-apis"
]

$BASSSyncMap02AIDMap = BASS`IR`BASSFormulaGlobalIDMap[];
$BASSSyncMap02ARegistry = BASS`IR`BASSFormulaEquationIRRegistry[];
$BASSSyncMap02AEdges = BASS`IR`BASSFormulaDependencyEdges[];
$BASSSyncMap02AExport = BASS`IR`BASSFormulaSemanticExport[];

VerificationTest[
 Sort[Lookup[$BASSSyncMap02ARegistry, "formula_id", Missing[]]],
 Sort[$BASSSyncMap02AExpectedIDs],
 TestID -> "BASS-SYNC-MAP-02A-001-global-formula-ids"
]

VerificationTest[
 Length[$BASSSyncMap02ARegistry],
 14,
 TestID -> "BASS-SYNC-MAP-02A-001-formula-count"
]

VerificationTest[
 AllTrue[$BASSSyncMap02ARegistry, BASS`IR`EquationIRQ],
 True,
 TestID -> "BASS-SYNC-MAP-02A-001-equation-ir-valid"
]

VerificationTest[
 DuplicateFreeQ[Lookup[$BASSSyncMap02ARegistry, "formula_id", Missing[]]],
 True,
 TestID -> "BASS-SYNC-MAP-02A-001-formula-ids-unique"
]

VerificationTest[
 FreeQ[$BASSSyncMap02ARegistry, _Real],
 True,
 TestID -> "BASS-SYNC-MAP-02A-001-no-machine-real"
]

VerificationTest[
 AllTrue[
  BASS`IR`FormulaSemanticSHA256 /@ $BASSSyncMap02ARegistry,
  StringQ[#] && StringLength[#] === 64 &
 ],
 True,
 TestID -> "BASS-SYNC-MAP-02A-001-semantic-hashes"
]

$BASSSyncMap02AProbe = First[$BASSSyncMap02ARegistry];
VerificationTest[
 BASS`IR`FormulaSemanticSHA256[$BASSSyncMap02AProbe],
 BASS`IR`FormulaSemanticSHA256[
  Join[$BASSSyncMap02AProbe,
   <|"formula_id" -> "OTHER.OWNER.ALIAS.999",
     "provenance" -> <|"stage" -> "independent-oracle"|>|>]
 ],
 TestID -> "BASS-SYNC-MAP-02A-001-hash-excludes-id-and-provenance"
]

VerificationTest[
 Sort[Keys[$BASSSyncMap02AIDMap]],
 Sort@Join[
  Lookup[BASS`Geometry`Abstract1Plus3EquationRegistry[],
   "formula_id", Missing[]],
  Lookup[BASS`Geometry`W3FormulaRegistry[],
   "formula_id", Missing[]],
  {"ALG01-STRUCTURE-001"}
 ],
 TestID -> "BASS-SYNC-MAP-02A-001-legacy-id-coverage"
]

VerificationTest[
 AllTrue[
  $BASSSyncMap02AEdges,
  MemberQ[$BASSSyncMap02AExpectedIDs, Lookup[#, "from", None]] &&
   MemberQ[$BASSSyncMap02AExpectedIDs, Lookup[#, "to", None]] &&
   Lookup[#, "relation", None] === "depends_on" &
 ],
 True,
 TestID -> "BASS-SYNC-MAP-02A-001-dependency-closure"
]

VerificationTest[
 MemberQ[
  $BASSSyncMap02AEdges,
  <|"from" -> "BASS.GEO.SPATIAL_RIEMANN.001",
    "to" -> "BASS.GEO.LEVI_CIVITA_CONNECTION.001",
    "relation" -> "depends_on"|>
 ],
 True,
 TestID -> "BASS-SYNC-MAP-02A-001-curvature-connection-edge"
]

VerificationTest[
 BASS`IR`BASSFormulaSemanticExportQ[$BASSSyncMap02AExport],
 True,
 TestID -> "BASS-SYNC-MAP-02A-001-export-valid"
]

VerificationTest[
 Lookup[$BASSSyncMap02AExport, "formula_count", None],
 14,
 TestID -> "BASS-SYNC-MAP-02A-001-export-count"
]

VerificationTest[
 Lookup[$BASSSyncMap02AExport, "owner", None],
 "bass",
 TestID -> "BASS-SYNC-MAP-02A-001-single-owner"
]

VerificationTest[
 Lookup[$BASSSyncMap02AExport, "convention_hash", None],
 "e12258405c1c2ec296839524f5169e03441715b3acaaff1cef9de28bfa490a70",
 TestID -> "BASS-SYNC-MAP-02A-001-convention-hash"
]

VerificationTest[
 Lookup[$BASSSyncMap02AExport, "type_registry_semantic_hash", None],
 "e0e5fbba464a839fcb5b11d41c7772c666224ec69f806910aab3bfab5a2f1762",
 TestID -> "BASS-SYNC-MAP-02A-001-type-registry-hash"
]

VerificationTest[
 Lookup[$BASSSyncMap02AExport, "claim_boundary", None],
 "BASS_FORMULA_SEMANTIC_EXPORT_ONLY_NO_CROSS_REPO_EQUIVALENCE_BACKGROUND_OR_SCIENCE_PROMOTION",
 TestID -> "BASS-SYNC-MAP-02A-001-claim-boundary"
]
