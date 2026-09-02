Module[{root, summary, adapters, receipt},
 root = DirectoryName[DirectoryName[$InputFileName]];
 Get[FileNameJoin[{root, "Kernel", "IR", "CrossRepositorySemanticGraph.wl"}]];
 Get[FileNameJoin[{root, "Kernel", "IR", "CrossRepositorySemanticGraphReceiptFix1.wl"}]];
 summary = BASS`IR`CrossRepositorySemanticGraphSummary[];
 adapters = BASS`IR`CrossRepositorySemanticAdapterReport[];
 receipt = BASS`IR`CrossRepositorySemanticGraphReceipt[];

 VerificationTest[
  BASS`IR`CrossRepositorySemanticGraphSummaryQ[summary],
  True,
  TestID -> "SYNC02F-summary-valid"
 ],
 VerificationTest[
  Length[Lookup[summary, "FormulaIDs"]],
  6,
  TestID -> "SYNC02F-six-authority-formulas"
 ],
 VerificationTest[
  Length[Lookup[summary, "ConsumerRelations"]],
  10,
  TestID -> "SYNC02F-ten-consumer-relations"
 ],
 VerificationTest[
  Length[Lookup[summary, "DAGEdges"]],
  12,
  TestID -> "SYNC02F-twelve-dag-edges"
 ],
 VerificationTest[
  Lookup[adapters, "FuturePhotonOutwardSkyDopplerResidual"],
  0,
  TestID -> "SYNC02F-direction-sign-adapter"
 ],
 VerificationTest[
  Lookup[adapters, "RECEnergyRateAdapterResidual"],
  0,
  TestID -> "SYNC02F-rec-energy-rate-adapter"
 ],
 VerificationTest[
  Lookup[adapters, "RECDirectionRateAdapterResidual"],
  0,
  TestID -> "SYNC02F-rec-direction-rate-adapter"
 ],
 VerificationTest[
  Lookup[adapters, "REIHOnlyIsotropicControlResidual"],
  0,
  TestID -> "SYNC02F-rei-isotropic-control"
 ],
 VerificationTest[
  Lookup[adapters, "REIGenericEquivalenceQ"],
  False,
  TestID -> "SYNC02F-rei-not-generic-equivalence"
 ],
 VerificationTest[
  Lookup[receipt, "Status"],
  "PASS",
  TestID -> "SYNC02F-receipt-pass"
 ],
 VerificationTest[
  Lookup[receipt, "AuthorityEffect"],
  "NONE_BEYOND_BOUNDED_SEMANTIC_GRAPH",
  TestID -> "SYNC02F-authority-effect-firewall"
 ],
 VerificationTest[
  MemberQ[Lookup[receipt, "Withheld"], "FINITE_ELECTRON_TILT_COLLISION"],
  True,
  TestID -> "SYNC02F-finite-electron-collision-withheld"
 ]
]
