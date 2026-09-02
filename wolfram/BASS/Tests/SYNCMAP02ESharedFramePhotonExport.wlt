VerificationTest[
 Module[{root, setup, setupResult},
  root = If[
    ValueQ[$SyncMap02ESourceRoot] && StringQ[$SyncMap02ESourceRoot] &&
     DirectoryQ[$SyncMap02ESourceRoot],
    $SyncMap02ESourceRoot,
    Directory[]
   ];
  setup = FileNameJoin[{
     root, "wolfram", "BASS", "Tests", "SYNCMAP02ETestSetup.wl"
    }];
  setupResult = Get[setup];
  If[
   AssociationQ[setupResult] && Lookup[setupResult, "status", None] === "PASS",
   BASS`IR`SharedFramePhotonFormulaIDs[],
   setupResult
  ]
 ],
 {
  "BASS.FRAME.ABERRATED_DIRECTION.001",
  "BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001",
  "BASS.FRAME.DOPPLER_FACTOR.001",
  "BASS.FRAME.SOLID_ANGLE_JACOBIAN.001",
  "BASS.PHOTON.DIRECTION_FLOW.001",
  "BASS.PHOTON.ENERGY_DRIFT.001"
 }, TestID -> "SYNC-MAP-02E-six-formula-identity"]

VerificationTest[
 Length[BASS`IR`SharedFramePhotonExactResiduals[]],
 10, TestID -> "SYNC-MAP-02E-ten-exact-residuals"]

VerificationTest[
 And @@ (TrueQ[# == 0] & /@ Values[BASS`IR`SharedFramePhotonExactResiduals[]]),
 True, TestID -> "SYNC-MAP-02E-exact-residuals-zero"]

VerificationTest[
 BASS`IR`SharedFramePhotonDependencyGraphQ[$SyncMap02EData],
 True, TestID -> "SYNC-MAP-02E-dependency-graph"]

VerificationTest[
 BASS`IR`SharedFramePhotonExportQ[$SyncMap02EData],
 True, TestID -> "SYNC-MAP-02E-canonical-export"]

VerificationTest[
 Module[{bad},
  bad = ReplacePart[$SyncMap02EData,
    {Key["predecessors"], Key["sync_map_02d"], Key["commit"]} ->
     "06aa29f78c26bcafeb60d85b719a4d3aa5c4c2e8"];
  BASS`IR`SharedFramePhotonExportQ[bad]
 ],
 False, TestID -> "SYNC-MAP-02E-reject-stale-02D-pin"]

VerificationTest[
 Module[{bad, terms},
  terms = {
    <|
     "input" -> "gamma*(1-beta_dot_n_sky)",
     "coefficient" -> <|"type" -> "integer", "value" -> 1|>
    |>
   };
  bad = mutateFormulaTerms[
    $SyncMap02EData,
    "BASS.FRAME.DOPPLER_FACTOR.001",
    terms
   ];
  BASS`IR`SharedFramePhotonExportQ[bad]
 ],
 False, TestID -> "SYNC-MAP-02E-reject-Doppler-sign-mutation"]

VerificationTest[
 Module[{bad, terms},
  terms = {
    <|
     "input" -> "H_geom",
     "coefficient" -> <|"type" -> "integer", "value" -> -1|>
    |>,
    <|
     "input" -> "sigma_ab*e^a*e^b",
     "coefficient" -> <|"type" -> "integer", "value" -> 1|>
    |>
   };
  bad = mutateFormulaTerms[
    $SyncMap02EData,
    "BASS.PHOTON.ENERGY_DRIFT.001",
    terms
   ];
  BASS`IR`SharedFramePhotonExportQ[bad]
 ],
 False, TestID -> "SYNC-MAP-02E-reject-energy-sign-mutation"]

VerificationTest[
 Module[{bad, edge},
  edge = <|
    "from" -> "BASS.FRAME.DOPPLER_FACTOR.001",
    "to" -> "BASS.FRAME.ABERRATED_DIRECTION.001",
    "relation" -> "depends_on"
   |>;
  bad = Join[
    KeyDrop[$SyncMap02EData, {"internal_dependency_edges"}],
    <|
     "internal_dependency_edges" ->
      Append[$SyncMap02EData["internal_dependency_edges"], edge]
    |>
   ];
  BASS`IR`SharedFramePhotonDependencyGraphQ[bad]
 ],
 False, TestID -> "SYNC-MAP-02E-reject-dependency-cycle"]

VerificationTest[
 Module[{bad, coverage},
  coverage = Join[
    KeyDrop[$SyncMap02EData["coverage"], {"included"}],
    <|
     "included" ->
      Append[$SyncMap02EData["coverage"]["included"],
       "finite electron tilt collision"]
    |>
   ];
  bad = Join[
    KeyDrop[$SyncMap02EData, {"coverage"}],
    <|"coverage" -> coverage|>
   ];
  BASS`IR`SharedFramePhotonExportQ[bad]
 ],
 False, TestID -> "SYNC-MAP-02E-reject-scope-injection"]

VerificationTest[
 Module[{bad},
  bad = Join[
    KeyDrop[$SyncMap02EData, {"formulas", "formula_count"}],
    <|
     "formulas" -> Take[$SyncMap02EData["formulas"], 4],
     "formula_count" -> 4
    |>
   ];
  BASS`IR`SharedFramePhotonExportQ[bad]
 ],
 False, TestID -> "SYNC-MAP-02E-reject-four-formula-union"]

VerificationTest[
 Module[{bad, record},
  record = First[$SyncMap02EData["formulas"]];
  bad = mutateFormulaHash[
    $SyncMap02EData,
    record["formula_id"],
    StringRepeat["0", 64]
   ];
  BASS`IR`SharedFramePhotonExportQ[bad]
 ],
 False, TestID -> "SYNC-MAP-02E-reject-semantic-hash-drift"]

VerificationTest[
 Module[{bad},
  bad = Join[
    KeyDrop[$SyncMap02EData, {"claim_boundary"}],
    <|"claim_boundary" -> "SYNC_MAP_02E_ONLY"|>
   ];
  BASS`IR`SharedFramePhotonExportQ[bad]
 ],
 False, TestID -> "SYNC-MAP-02E-reject-incomplete-claim-boundary"]
