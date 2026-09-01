If[! ValueQ[$BASSXActSource],
 $BASSXActSource = "https://xact.es/download/xAct_1.3.0.tgz"];
If[! ValueQ[$BASSXActExpectedSHA256],
 $BASSXActExpectedSHA256 =
  "7a6c5f600868a3922668b020a15c0692f76574ff2a559808c62d460cef1b07be"];

$BASSXActReceipt = BASS`Authority`ActivatePinnedXAct[
 $BASSXActSource, $BASSXActExpectedSHA256];
$BASSW0DefinitionsMade = False;
If[Lookup[$BASSXActReceipt, "status", "BLOCKED"] === "PASS",
 Quiet[ToExpression["DefManifold[BASSW0M4,4,{ba,bb,bc,bd}]"]];
 Quiet[ToExpression["DefCovD[BASSW0CD[-ba],{\";\",\"D\"}]"]];
 $BASSW0DefinitionsMade = True];

VerificationTest[BASS`Authority`XActActivationReceiptQ[$BASSXActReceipt], True,
 TestID -> "BASS-WOLFRAM-ENV-001-activation-receipt"]
VerificationTest[Lookup[$BASSXActReceipt, "archive_sha256", ""],
 $BASSXActExpectedSHA256, TestID -> "BASS-WOLFRAM-ENV-001-archive-hash"]
VerificationTest[$BASSW0DefinitionsMade, True,
 TestID -> "BASS-WOLFRAM-ENV-001-definitions-made"]
VerificationTest[ToExpression["ManifoldQ[BASSW0M4]"], True,
 TestID -> "BASS-WOLFRAM-ENV-001-manifold"]
VerificationTest[ToExpression["CovDQ[BASSW0CD]"], True,
 TestID -> "BASS-WOLFRAM-ENV-001-covd"]
VerificationTest[ToExpression["xTensorQ[RiemannBASSW0CD]"], True,
 TestID -> "BASS-WOLFRAM-ENV-001-riemann"]
