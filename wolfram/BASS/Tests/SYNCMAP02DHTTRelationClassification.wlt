$SYNCMAP02DRequiredAPIs = {
 "BASS`IR`HTTRelationClassification`HTTLorentzRelationChecks",
 "BASS`IR`HTTRelationClassification`HTTFederationDAGChecks",
 "BASS`IR`HTTRelationClassification`HTTRelationClassificationReport"
};

$SYNCMAP02DAPIsPresent = And @@ (NameQ /@ $SYNCMAP02DRequiredAPIs);

VerificationTest[
 $SYNCMAP02DAPIsPresent,
 True,
 TestID -> "BASS-SYNC-MAP-02D-API-CONTRACT-001"
]

If[$SYNCMAP02DAPIsPresent,
 $SYNCMAP02DLorentz =
  BASS`IR`HTTRelationClassification`HTTLorentzRelationChecks[];
 $SYNCMAP02DDAG =
  BASS`IR`HTTRelationClassification`HTTFederationDAGChecks[];
 $SYNCMAP02DReport =
  BASS`IR`HTTRelationClassification`HTTRelationClassificationReport[];

 VerificationTest[
  Lookup[$SYNCMAP02DLorentz, "status"],
  "PASS",
  TestID -> "BASS-SYNC-MAP-02D-LORENTZ-STATUS-001"
 ];

 VerificationTest[
  And @@ (TrueQ[# == 0] & /@
    Values[Lookup[$SYNCMAP02DLorentz, "residuals", <||>]]),
  True,
  TestID -> "BASS-SYNC-MAP-02D-EXACT-RESIDUALS-001"
 ];

 VerificationTest[
  And @@ Values[Lookup[$SYNCMAP02DLorentz, "mutations", <||>]],
  True,
  TestID -> "BASS-SYNC-MAP-02D-LORENTZ-MUTATIONS-001"
 ];

 VerificationTest[
  Lookup[$SYNCMAP02DDAG, "status"],
  "PASS",
  TestID -> "BASS-SYNC-MAP-02D-DAG-STATUS-001"
 ];

 VerificationTest[
  Lookup[$SYNCMAP02DDAG, "node_count"],
  10,
  TestID -> "BASS-SYNC-MAP-02D-DAG-NODE-COUNT-001"
 ];

 VerificationTest[
  Lookup[$SYNCMAP02DDAG, "edge_count"],
  12,
  TestID -> "BASS-SYNC-MAP-02D-DAG-EDGE-COUNT-001"
 ];

 VerificationTest[
  And @@ Values[Lookup[$SYNCMAP02DDAG, "checks", <||>]],
  True,
  TestID -> "BASS-SYNC-MAP-02D-DAG-CHECKS-001"
 ];

 VerificationTest[
  MemberQ[
   Lookup[$SYNCMAP02DDAG, "edges", {}],
   {"02D_HTT", "02E_SHARED_EXPORT"}
  ],
  True,
  TestID -> "BASS-SYNC-MAP-02D-SHARED-EXPORT-DEPENDENCY-001"
 ];

 VerificationTest[
  MemberQ[
   Lookup[$SYNCMAP02DDAG, "edges", {}],
   {"02E_SHARED_EXPORT", "02F_SEMANTIC_GRAPH"}
  ],
  True,
  TestID -> "BASS-SYNC-MAP-02D-SEMANTIC-GRAPH-ORDER-001"
 ];

 VerificationTest[
  Lookup[$SYNCMAP02DReport, "status"],
  "PASS",
  TestID -> "BASS-SYNC-MAP-02D-COMBINED-STATUS-001"
 ];

 VerificationTest[
  Lookup[$SYNCMAP02DReport, "claim_boundary"],
  "RELATION_CLASSIFICATION_ONLY_NO_SHARED_EXPORT_GLOBAL_TILT_DATA_FIT_PROVIDER_OR_SCIENCE_PROMOTION",
  TestID -> "BASS-SYNC-MAP-02D-CLAIM-BOUNDARY-001"
 ];
]
