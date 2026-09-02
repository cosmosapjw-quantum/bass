(* ::Package:: *)

$SYNCMap02ERegistry = BASS`IR`SharedFramePhotonEquationIRRegistry[];
$SYNCMap02EExport = BASS`IR`SharedFramePhotonSemanticExport[];
$SYNCMap02EChecks = BASS`IR`SharedFramePhotonAlgebraChecks[];
$SYNCMap02EIDs = BASS`IR`SharedFramePhotonFormulaIDs[];
$SYNCMap02EInternal = BASS`IR`SharedFramePhotonInternalDependencyEdges[];
$SYNCMap02EExternal = BASS`IR`SharedFramePhotonExternalDependencyEdges[];

VerificationTest[
 Length[$SYNCMap02ERegistry],
 6,
 TestID -> "BASS-SYNC-MAP-02E-six-formula-registry"
]

VerificationTest[
 Sort[Lookup[$SYNCMap02ERegistry, "formula_id"]],
 Sort[$SYNCMap02EIDs],
 TestID -> "BASS-SYNC-MAP-02E-exact-six-formula-union"
]

VerificationTest[
 DuplicateFreeQ[Lookup[$SYNCMap02ERegistry, "formula_id"]],
 True,
 TestID -> "BASS-SYNC-MAP-02E-formula-ids-unique"
]

VerificationTest[
 And @@ (BASS`IR`EquationIRQ /@ $SYNCMap02ERegistry),
 True,
 TestID -> "BASS-SYNC-MAP-02E-equation-ir-valid"
]

VerificationTest[
 BASS`IR`SharedFramePhotonSemanticExportQ[$SYNCMap02EExport],
 True,
 TestID -> "BASS-SYNC-MAP-02E-export-valid"
]

VerificationTest[
 Lookup[$SYNCMap02EExport, "formula_count"],
 6,
 TestID -> "BASS-SYNC-MAP-02E-formula-count"
]

VerificationTest[
 Length[$SYNCMap02EInternal],
 4,
 TestID -> "BASS-SYNC-MAP-02E-four-internal-dependencies"
]

VerificationTest[
 Length[$SYNCMap02EExternal],
 3,
 TestID -> "BASS-SYNC-MAP-02E-three-external-dependencies"
]

VerificationTest[
 AcyclicGraphQ@Graph[
   $SYNCMap02EIDs,
   DirectedEdge @@@ ({Lookup[#, "from"], Lookup[#, "to"]} & /@
      $SYNCMap02EInternal)
  ],
 True,
 TestID -> "BASS-SYNC-MAP-02E-internal-dag-acyclic"
]

VerificationTest[
 And @@ (TrueQ /@ Values[$SYNCMap02EChecks]),
 True,
 TestID -> "BASS-SYNC-MAP-02E-all-exact-algebra-checks"
]

VerificationTest[
 Lookup[$SYNCMap02EChecks, "aberrated_direction_unit_norm"],
 True,
 TestID -> "BASS-SYNC-MAP-02E-aberrated-direction-unit-norm"
]

VerificationTest[
 Lookup[$SYNCMap02EChecks, "parallel_axis_fixed"],
 True,
 TestID -> "BASS-SYNC-MAP-02E-parallel-axis-fixed"
]

VerificationTest[
 Lookup[$SYNCMap02EChecks, "antiparallel_axis_fixed"],
 True,
 TestID -> "BASS-SYNC-MAP-02E-antiparallel-axis-fixed"
]

VerificationTest[
 Lookup[$SYNCMap02EChecks,
  "future_photon_and_outward_sky_doppler_charts"],
 True,
 TestID -> "BASS-SYNC-MAP-02E-sky-photon-chart-sign-adapter"
]

VerificationTest[
 Lookup[$SYNCMap02EChecks, "solid_angle_power_minus_two"],
 True,
 TestID -> "BASS-SYNC-MAP-02E-solid-angle-jacobian"
]

VerificationTest[
 Lookup[$SYNCMap02EChecks, "blackbody_planck_argument_invariant"],
 True,
 TestID -> "BASS-SYNC-MAP-02E-blackbody-planck-invariance"
]

VerificationTest[
 Lookup[$SYNCMap02EChecks, "direction_flow_tangent"],
 True,
 TestID -> "BASS-SYNC-MAP-02E-direction-flow-tangent"
]

VerificationTest[
 Lookup[$SYNCMap02EChecks, "energy_drift_FLRW_limit"],
 True,
 TestID -> "BASS-SYNC-MAP-02E-energy-drift-flrw-limit"
]

VerificationTest[
 Lookup[$SYNCMap02EChecks, "frame_and_background_exports_disjoint"],
 True,
 TestID -> "BASS-SYNC-MAP-02E-frame-background-export-firewall"
]

$SYNCMap02EHashByID = AssociationThread[
 Lookup[$SYNCMap02EExport["formulas"], "formula_id"],
 Lookup[$SYNCMap02EExport["formulas"], "semantic_hash"]
];

VerificationTest[
 Lookup[$SYNCMap02EHashByID, "BASS.FRAME.ABERRATED_DIRECTION.001"],
 "b781f0b5aa4a7239867cf4868aa56feced4ca932f7b3697eb09063317fffbad3",
 TestID -> "BASS-SYNC-MAP-02E-aberration-semantic-hash"
]

VerificationTest[
 Lookup[$SYNCMap02EHashByID,
  "BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001"],
 "f9cd508f65bdfdccafd90d0fb64f94821d29a3dc3e9bd956463e9ed28a4063cc",
 TestID -> "BASS-SYNC-MAP-02E-temperature-semantic-hash"
]

VerificationTest[
 Lookup[$SYNCMap02EHashByID, "BASS.FRAME.DOPPLER_FACTOR.001"],
 "bf2b4d41eb7b0b837be778e1debb15efec50a1b0bacd36e08b0d8098243aed16",
 TestID -> "BASS-SYNC-MAP-02E-doppler-semantic-hash"
]

VerificationTest[
 Lookup[$SYNCMap02EHashByID, "BASS.FRAME.SOLID_ANGLE_JACOBIAN.001"],
 "916650d0349ad00760f0dee0b96da9adc2013d63fb2352dabe4581d521b482fd",
 TestID -> "BASS-SYNC-MAP-02E-solid-angle-semantic-hash"
]

VerificationTest[
 Lookup[$SYNCMap02EHashByID, "BASS.PHOTON.DIRECTION_FLOW.001"],
 "cc374ce0e278e0683d7744c97896dcb1a2061e92c795a338cfea6d24e8f862b8",
 TestID -> "BASS-SYNC-MAP-02E-direction-flow-semantic-hash"
]

VerificationTest[
 Lookup[$SYNCMap02EHashByID, "BASS.PHOTON.ENERGY_DRIFT.001"],
 "d84e8d3ad0c926975069239817d1374d1e8921e07f8dd63b7ad3619b1cfcc42c",
 TestID -> "BASS-SYNC-MAP-02E-energy-drift-semantic-hash"
]

VerificationTest[
 FreeQ[$SYNCMap02EExport, _Real],
 True,
 TestID -> "BASS-SYNC-MAP-02E-no-inexact-formula-values"
]

VerificationTest[
 Lookup[$SYNCMap02EExport["predecessors", "sync_map_02d"], "commit"],
 "7006aaab27834af37d5034f8f1e50943fe85c0f3",
 TestID -> "BASS-SYNC-MAP-02E-final-htt-predecessor"
]

VerificationTest[
 Lookup[$SYNCMap02EExport, "claim_boundary"],
 "SIX_FORMULA_EQUATIONIR_EXPORT_ONLY_NO_CONSUMER_EQUIVALENCE_FINITE_TILT_GLOBAL_TILT_BACKGROUND_PROVIDER_OR_SCIENCE_PROMOTION",
 TestID -> "BASS-SYNC-MAP-02E-claim-boundary"
]
