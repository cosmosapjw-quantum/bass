$BASSConventionLock = BASS`Authority`ConventionLock[];
$BASSDimensionRegistry = BASS`Authority`DimensionRegistry[];

VerificationTest[BASS`Authority`ConventionLockQ[$BASSConventionLock], True,
 TestID -> "BASS-CONVENTION-LOCK-001-valid"]
VerificationTest[Lookup[$BASSConventionLock, "metric_signature"], {-1, 1, 1, 1},
 TestID -> "BASS-CONVENTION-LOCK-001-signature"]
VerificationTest[BASS`Authority`ConventionLockQ[
 KeyDrop[$BASSConventionLock, "observed_direction"]], False,
 TestID -> "BASS-CONVENTION-LOCK-001-missing-key-rejected"]
VerificationTest[BASS`Authority`DimensionRegistryQ[$BASSDimensionRegistry], True,
 TestID -> "BASS-DIMENSION-REGISTRY-001-valid"]
VerificationTest[Lookup[Lookup[$BASSDimensionRegistry, "quantities"], "H_geom"],
 <|"L" -> -1, "M" -> 0, "T" -> 0, "Theta" -> 0|>,
 TestID -> "BASS-DIMENSION-REGISTRY-001-H-dimension"]
VerificationTest[BASS`IR`CanonicalSHA256[<|"b" -> 2, "a" -> 1|>],
 BASS`IR`CanonicalSHA256[<|"a" -> 1, "b" -> 2|>],
 TestID -> "BASS-IR-ROUNDTRIP-001-key-order-invariant"]
VerificationTest[StringLength[BASS`IR`CanonicalSHA256[$BASSConventionLock]], 64,
 TestID -> "BASS-IR-ROUNDTRIP-001-sha-length"]
VerificationTest[BASS`IR`RawJSONRoundTripQ[$BASSConventionLock], True,
 TestID -> "BASS-IR-ROUNDTRIP-001-raw-json"]

$BASSExactCoefficient = BASS`IR`ExactScalarAST[-3 Sqrt[2/7]/5 + ell (ell + 1)];
VerificationTest[BASS`IR`ExactScalarASTQ[$BASSExactCoefficient], True,
 TestID -> "BASS-EQUATION-IR-001-exact-coefficient"]

$BASSEquationIR = BASS`IR`MakeEquationIR[<|
 "formula_id" -> "W1-PROBE-001",
 "authority_theorem" -> "W1 exact semantic IR probe",
 "target" -> "probe_lm", "free_indices" -> {"ell", "m"},
 "representation" -> "wigner",
 "assumptions" -> {"ell is a nonnegative integer"},
 "domain" -> <|"ell_min" -> 0|>,
 "dimensions" -> <|"target" -> "dimensionless"|>,
 "terms" -> {<|"input" -> "probe_lm", "coefficient" -> $BASSExactCoefficient|>},
 "structural_zero_rules" -> {"outside declared ell domain"},
 "branch_predicates" -> {}, "known_limits" -> {"ell = 0 remains finite"},
 "provenance" -> <|"stage" -> "W0_W1"|>|>];
VerificationTest[BASS`IR`EquationIRQ[$BASSEquationIR], True,
 TestID -> "BASS-EQUATION-IR-001-valid"]

$BASSProvenance = BASS`Authority`MakeProvenanceEnvelope[
 "BASS-MASTER-SSOT-V2-WOLFRAM-XACT-20260901", "W0_W1",
 <|"repository" -> "cosmosapjw-quantum/bass",
  "base_commit" -> "0ac9f7e0ce8ff88dc7f4487a97e21be2863af207"|>,
 <|"convention_hash" -> BASS`IR`CanonicalSHA256[$BASSConventionLock]|>];
VerificationTest[BASS`Authority`ProvenanceEnvelopeQ[$BASSProvenance], True,
 TestID -> "BASS-STAGE-RECEIPT-IR-001-provenance"]

$BASSStageReceipt = BASS`IR`MakeStageReceipt["W0_W1", "PASS",
 <|"succeeded" -> 12, "failed" -> 0|>, $BASSProvenance,
 <|"authorized" -> {"W0_W1_SYMBOLIC_INFRASTRUCTURE_VERIFIED"},
  "withheld" -> {"BACKGROUND_TENSOR_DERIVATION"}|>];
VerificationTest[BASS`IR`StageReceiptQ[$BASSStageReceipt], True,
 TestID -> "BASS-STAGE-RECEIPT-IR-001-valid"]
VerificationTest[BASS`IR`StageReceiptQ[
 ReplacePart[$BASSStageReceipt, "status" -> "GREEN"]], False,
 TestID -> "BASS-STAGE-RECEIPT-IR-001-illegal-status-rejected"]
