$SYNCMAP02BRequiredAPIs = {
 "BASS`IR`RECRelationClassificationRegistry",
 "BASS`IR`RECRelationClassificationRegistryQ",
 "BASS`IR`RECSharedFormulaGapRegistry",
 "BASS`IR`RECSharedFormulaGapRegistryQ",
 "BASS`IR`RECFrameCharacteristicEquivalenceReport",
 "BASS`IR`RECFormalOracleSplitRegistry",
 "BASS`IR`RECBASSGeometryRelationMatrix",
 "BASS`IR`RECRelationImpactDAG",
 "BASS`IR`RECRelationImpactDAGQ",
 "BASS`IR`RECRelationClassificationReceipt",
 "BASS`IR`RECRelationClassificationReceiptQ"
};

$SYNCMAP02BAPIsPresent = And @@ (NameQ /@ $SYNCMAP02BRequiredAPIs);

VerificationTest[
 $SYNCMAP02BAPIsPresent,
 True,
 TestID -> "BASS-SYNC-MAP-02B-API-CONTRACT-001"
]

If[$SYNCMAP02BAPIsPresent,
 $SYNCMAP02BRegistry = BASS`IR`RECRelationClassificationRegistry[];
 $SYNCMAP02BGaps = BASS`IR`RECSharedFormulaGapRegistry[];
 $SYNCMAP02BEquivalence = BASS`IR`RECFrameCharacteristicEquivalenceReport[];
 $SYNCMAP02BOracleSplit = BASS`IR`RECFormalOracleSplitRegistry[];
 $SYNCMAP02BMatrix = BASS`IR`RECBASSGeometryRelationMatrix[];
 $SYNCMAP02BDAG = BASS`IR`RECRelationImpactDAG[];
 $SYNCMAP02BReceipt = BASS`IR`RECRelationClassificationReceipt[];

 VerificationTest[
  BASS`IR`RECRelationClassificationRegistryQ[$SYNCMAP02BRegistry],
  True,
  TestID -> "BASS-SYNC-MAP-02B-REGISTRY-VALID-001"
 ];

 VerificationTest[
  Length[$SYNCMAP02BRegistry],
  9,
  TestID -> "BASS-SYNC-MAP-02B-RELATION-COUNT-001"
 ];

 VerificationTest[
  KeySort@Counts[Lookup[$SYNCMAP02BRegistry, "relation_class"]],
  KeySort@<|
    "PINNED_IMPORT_PENDING_OWNER_EQUATIONIR" -> 4,
    "ADAPTER_SPECIALIZATION" -> 1,
    "OWNED_EXTENSION" -> 2,
    "INDEPENDENT_ORACLE" -> 2
   |>,
  TestID -> "BASS-SYNC-MAP-02B-RELATION-CLASS-COUNTS-001"
 ];

 VerificationTest[
  And @@ Map[
    StringMatchQ[Lookup[#, "source_blob", ""],
      RegularExpression["[0-9a-f]{40}"]] &,
    $SYNCMAP02BRegistry
   ],
  True,
  TestID -> "BASS-SYNC-MAP-02B-EXACT-REC-SOURCE-BLOBS-001"
 ];

 VerificationTest[
  BASS`IR`RECSharedFormulaGapRegistryQ[$SYNCMAP02BGaps],
  True,
  TestID -> "BASS-SYNC-MAP-02B-SHARED-GAPS-VALID-001"
 ];

 VerificationTest[
  Lookup[$SYNCMAP02BGaps, "formula_id"],
  {
   "BASS.FRAME.ABERRATED_DIRECTION.001",
   "BASS.FRAME.DOPPLER_FACTOR.001",
   "BASS.PHOTON.DIRECTION_FLOW.001",
   "BASS.PHOTON.ENERGY_DRIFT.001"
  },
  TestID -> "BASS-SYNC-MAP-02B-SHARED-GAP-IDS-001"
 ];

 VerificationTest[
  And @@ Values[Lookup[$SYNCMAP02BEquivalence, "checks", <||>]],
  True,
  TestID -> "BASS-SYNC-MAP-02B-FRAME-CHARACTERISTIC-EQUIVALENCE-001"
 ];

 VerificationTest[
  Lookup[$SYNCMAP02BOracleSplit, "common_bass_replay_check_count"],
  10,
  TestID -> "BASS-SYNC-MAP-02B-FORMAL-COMMON-CHECK-COUNT-001"
 ];

 VerificationTest[
  Lookup[$SYNCMAP02BOracleSplit, "rec_owned_oracle_check_count"],
  19,
  TestID -> "BASS-SYNC-MAP-02B-FORMAL-REC-CHECK-COUNT-001"
 ];

 VerificationTest[
  Lookup[$SYNCMAP02BOracleSplit, "authority_effect"],
  "NONE",
  TestID -> "BASS-SYNC-MAP-02B-FORMAL-ORACLE-NONAUTHORITY-001"
 ];

 VerificationTest[
  Length[$SYNCMAP02BMatrix],
  14,
  TestID -> "BASS-SYNC-MAP-02B-BASS-MATRIX-COUNT-001"
 ];

 VerificationTest[
  Counts[Lookup[$SYNCMAP02BMatrix, "relation"]],
  <|"NO_ACTIVE_REC_REDERIVATION_DETECTED" -> 13,
    "DEPENDENCY_ONLY" -> 1|>,
  TestID -> "BASS-SYNC-MAP-02B-NO-DUPLICATE-BASS14-001"
 ];

 VerificationTest[
  Lookup[
   SelectFirst[$SYNCMAP02BMatrix,
    Lookup[#, "relation", None] === "DEPENDENCY_ONLY" &],
   "formula_id"
  ],
  "BASS.GEO.STRUCTURE_CONSTANTS.001",
  TestID -> "BASS-SYNC-MAP-02B-STRUCTURE-DEPENDENCY-001"
 ];

 VerificationTest[
  BASS`IR`RECRelationImpactDAGQ[$SYNCMAP02BDAG],
  True,
  TestID -> "BASS-SYNC-MAP-02B-IMPACT-DAG-VALID-001"
 ];

 VerificationTest[
  Lookup[$SYNCMAP02BDAG, "official_dag_mutated"],
  False,
  TestID -> "BASS-SYNC-MAP-02B-OFFICIAL-DAG-UNCHANGED-001"
 ];

 VerificationTest[
  BASS`IR`RECRelationClassificationReceiptQ[$SYNCMAP02BReceipt],
  True,
  TestID -> "BASS-SYNC-MAP-02B-RECEIPT-VALID-001"
 ];

 VerificationTest[
  Lookup[$SYNCMAP02BReceipt, "status"],
  "PASS_WITH_SHARED_FORMULA_EXPORT_GAPS",
  TestID -> "BASS-SYNC-MAP-02B-STATUS-001"
 ];

 VerificationTest[
  Lookup[$SYNCMAP02BReceipt, "rec_scientific_blocker"],
  "NO_PASS_REC_PHYSICAL_SPLIT",
  TestID -> "BASS-SYNC-MAP-02B-REC-BLOCKER-PRESERVED-001"
 ];

 VerificationTest[
  Lookup[$SYNCMAP02BReceipt, "duplicate_derivation_count"],
  0,
  TestID -> "BASS-SYNC-MAP-02B-DUPLICATE-COUNT-001"
 ];

 VerificationTest[
  Lookup[$SYNCMAP02BReceipt, "claim_boundary"],
  "REC_RELATION_CLASSIFICATION_ONLY_NO_PROVIDER_ADMISSION_CROSS_REPO_EQUIVALENCE_OR_SCIENCE_PROMOTION",
  TestID -> "BASS-SYNC-MAP-02B-CLAIM-BOUNDARY-001"
 ];
]
