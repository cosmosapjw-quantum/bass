$BASSBG02Assumptions = BASS`Background`GRBackgroundAssumptions[];

VerificationTest[
 BASS`Background`GRBackgroundAssumptionsQ[$BASSBG02Assumptions],
 True,
 TestID -> "BASS-BG02-SPEC-001-assumptions"]

$BASSBG02EquationSet = BASS`Background`GRBackgroundEquationSet[];
VerificationTest[
 BASS`Background`GRBackgroundEquationSetQ[$BASSBG02EquationSet],
 True,
 TestID -> "BASS-BG02-SPEC-002-equation-set"]

$BASSBG02Zero = ConstantArray[0, {3, 3}];
$BASSBG02Hamiltonian = BASS`Background`HamiltonianConstraintResidual[
 H, sigma, R3, rho, lambda, kappaE];
VerificationTest[
 $BASSBG02Hamiltonian,
 R3 + 6 H^2 - Tr[sigma . sigma] - 2 lambda - 2 kappaE rho,
 TestID -> "BASS-BG02-CONSTRAINT-001-hamiltonian"]

$BASSBG02TypeVGamma = BASS`Geometry`LeviCivitaConnection[
 BASS`Geometry`BianchiStructureConstants[{A, 0, 0}, $BASSBG02Zero]];
$BASSBG02TypeVSigma = DiagonalMatrix[{s1, s2, -s1 - s2}];
VerificationTest[
 BASS`Background`HomogeneousMomentumGeometry[
  $BASSBG02TypeVGamma, $BASSBG02TypeVSigma],
 {3 A s1, 0, 0},
 TestID -> "BASS-BG02-CONSTRAINT-002-type-v-momentum-sign"]

VerificationTest[
 BASS`Background`MomentumConstraintResidual[
  $BASSBG02TypeVGamma, $BASSBG02TypeVSigma, {q1, 0, 0}, kappaE],
 {3 A s1 - kappaE q1, 0, 0},
 TestID -> "BASS-BG02-CONSTRAINT-003-momentum-matter"]

$BASSBG02KasnerH = 1/(3 s);
$BASSBG02KasnerSigma = DiagonalMatrix[{2/3, -1/3, -1/3}]/s;
VerificationTest[
 FullSimplify[BASS`Background`HamiltonianConstraintResidual[
   $BASSBG02KasnerH, $BASSBG02KasnerSigma, 0, 0, 0, kappaE]],
 0,
 TestID -> "BASS-BG02-LIMIT-001-kasner-hamiltonian"]

VerificationTest[
 FullSimplify[D[$BASSBG02KasnerH, s] -
   BASS`Background`RaychaudhuriRHS[
    $BASSBG02KasnerH, $BASSBG02KasnerSigma, 0, 0, 0, kappaE]],
 0,
 TestID -> "BASS-BG02-LIMIT-002-kasner-raychaudhuri"]

VerificationTest[
 FullSimplify[D[$BASSBG02KasnerSigma, s] -
   BASS`Background`ShearEvolutionRHS[
    $BASSBG02KasnerH, $BASSBG02KasnerSigma,
    $BASSBG02Zero, $BASSBG02Zero, kappaE]],
 $BASSBG02Zero,
 TestID -> "BASS-BG02-LIMIT-003-kasner-shear"]

VerificationTest[
 FullSimplify[BASS`Background`RaychaudhuriRHS[
   Sqrt[lambda/3], $BASSBG02Zero, 0, 0, lambda, kappaE]],
 0,
 TestID -> "BASS-BG02-LIMIT-004-de-sitter"]

$BASSBG02MilneA = {1/s, 0, 0};
$BASSBG02MilneC = BASS`Geometry`BianchiStructureConstants[
 $BASSBG02MilneA, $BASSBG02Zero];
$BASSBG02MilneGamma = BASS`Geometry`LeviCivitaConnection[$BASSBG02MilneC];
$BASSBG02MilneRiemann = BASS`Geometry`SpatialRiemann[
 $BASSBG02MilneC, $BASSBG02MilneGamma];
$BASSBG02MilneR3 = BASS`Geometry`SpatialRicciScalar[$BASSBG02MilneRiemann];
VerificationTest[
 FullSimplify[BASS`Background`HamiltonianConstraintResidual[
   1/s, $BASSBG02Zero, $BASSBG02MilneR3, 0, 0, kappaE]],
 0,
 TestID -> "BASS-BG02-LIMIT-005-milne-hamiltonian"]

$BASSBG02MilneStructureRHS = BASS`Background`StructureEvolutionRHS[
 1/s, $BASSBG02Zero, $BASSBG02MilneA, $BASSBG02Zero];
VerificationTest[
 FullSimplify[D[$BASSBG02MilneA, s] -
   Lookup[$BASSBG02MilneStructureRHS, "a_dot"]],
 {0, 0, 0},
 TestID -> "BASS-BG02-LIMIT-006-milne-structure"]

$BASSBG02JacobiResidual = BASS`Background`JacobiConstraintPropagationResidual[
 H, {{x11, x12, x13}, {x12, x22, x23}, {x13, x23, -x11-x22}},
 {{n11, n12, n13}, {n12, n22, n23}, {n13, n23, n33}},
 {a1, a2, a3}];
VerificationTest[
 FullSimplify[$BASSBG02JacobiResidual],
 {0, 0, 0},
 TestID -> "BASS-BG02-PROP-001-jacobi-constraint"]

VerificationTest[
 BASS`Background`EvolutionPolicySpecQ[
  BASS`Background`EvolutionPolicySpec["spatial_einstein_unadjusted"]],
 True,
 TestID -> "BASS-BG02-POLICY-001-unadjusted"]

VerificationTest[
 BASS`Background`EvolutionPolicySpecQ[
  BASS`Background`EvolutionPolicySpec["raychaudhuri_adjusted"]],
 True,
 TestID -> "BASS-BG02-POLICY-002-adjusted"]

$BASSBG02TraceDifference = BASS`Background`SpatialEinsteinTraceRHS[
 H, $BASSBG02TypeVSigma, R3, rho, p, lambda, kappaE] -
 BASS`Background`RaychaudhuriRHS[
 H, $BASSBG02TypeVSigma, rho, p, lambda, kappaE];
VerificationTest[
 FullSimplify[$BASSBG02TraceDifference +
   BASS`Background`HamiltonianConstraintResidual[
    H, $BASSBG02TypeVSigma, R3, rho, lambda, kappaE]/12],
 0,
 TestID -> "BASS-BG02-POLICY-003-trace-adjustment"]

$BASSBG02UnadjustedPropagation =
 BASS`Background`EinsteinConstraintPropagationRHS[
  "spatial_einstein_unadjusted", H, $BASSBG02TypeVSigma,
  CH, {CM, 0, 0}, $BASSBG02TypeVGamma];
VerificationTest[
 FullSimplify[{
   Lookup[$BASSBG02UnadjustedPropagation, "hamiltonian_dot"],
   Lookup[$BASSBG02UnadjustedPropagation, "momentum_dot"]}],
 {-3 H CH + 4 A CM, {-(4 H + s1) CM, 0, 0}},
 TestID -> "BASS-BG02-PROP-002-type-v-unadjusted"]

$BASSBG02AdjustedPropagation =
 BASS`Background`EinsteinConstraintPropagationRHS[
  "raychaudhuri_adjusted", H, $BASSBG02TypeVSigma,
  CH, {CM, 0, 0}, $BASSBG02TypeVGamma];
VerificationTest[
 FullSimplify[Lookup[$BASSBG02AdjustedPropagation, "hamiltonian_dot"]],
 -2 H CH + 4 A CM,
 TestID -> "BASS-BG02-PROP-003-type-v-adjusted"]

VerificationTest[
 FullSimplify[Coefficient[
   Lookup[$BASSBG02UnadjustedPropagation, "momentum_dot"][[1]], CH]],
 0,
 TestID -> "BASS-BG02-PROP-004-no-hamiltonian-feedback"]

VerificationTest[
 FullSimplify[BASS`Background`EnergyConservationResidual[
   -3 H (rho + p), H, rho, p, 0, 0,
   $BASSBG02Zero, $BASSBG02Zero, 0]],
 0,
 TestID -> "BASS-BG02-MATTER-001-perfect-fluid-energy"]
