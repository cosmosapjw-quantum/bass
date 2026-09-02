$SYNCMAP02BFixRequired = And[
 NameQ["BASS`IR`RECFrameCharacteristicAdversarialReport"],
 NameQ["BASS`IR`RECFrameCharacteristicEquivalenceReport"],
 NameQ["BASS`IR`RECRelationImpactDAGQ"]
];

VerificationTest[
 $SYNCMAP02BFixRequired,
 True,
 TestID -> "BASS-SYNC-MAP-02B-VALIDATION-FIX-API-001"
]

If[$SYNCMAP02BFixRequired,
 $SYNCMAP02BHardenedEquivalence =
  BASS`IR`RECFrameCharacteristicEquivalenceReport[];
 $SYNCMAP02BAdversarial =
  BASS`IR`RECFrameCharacteristicAdversarialReport[];
 $SYNCMAP02BForeignEdgeDAG = Append[
  BASS`IR`RECRelationImpactDAG[],
  "edges" -> Append[
    BASS`IR`RECRelationImpactDAG[]["edges"],
    <|"from" -> "FOREIGN.UNREGISTERED.NODE", "to" -> "REC.PROVIDER_EXPORT"|>
   ]
 ];

 VerificationTest[
  And @@ Values[Lookup[$SYNCMAP02BHardenedEquivalence, "checks", <||>]],
  True,
  TestID -> "BASS-SYNC-MAP-02B-COMPUTED-RESIDUALS-001"
 ];

 VerificationTest[
  And[
   TrueQ[Lookup[$SYNCMAP02BAdversarial, "wrong_energy_sign_detected", False]],
   TrueQ[Lookup[$SYNCMAP02BAdversarial,
     "wrong_hydrogen_adapter_coefficient_detected", False]]
  ],
  True,
  TestID -> "BASS-SYNC-MAP-02B-SIGN-COEFFICIENT-MUTATIONS-001"
 ];

 VerificationTest[
  BASS`IR`RECRelationImpactDAGQ[$SYNCMAP02BForeignEdgeDAG],
  False,
  TestID -> "BASS-SYNC-MAP-02B-FOREIGN-DAG-ENDPOINT-REJECTED-001"
 ];
]
