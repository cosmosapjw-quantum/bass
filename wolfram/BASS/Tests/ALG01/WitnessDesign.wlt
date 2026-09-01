$BASSALG01Labels = {"I", "II", "V", "IX", "VI_-1/9"};

VerificationTest[
 BASS`Bianchi`BianchiWitnessLabels[],
 $BASSALG01Labels,
 TestID -> "BASS-ALG01-SPEC-001-supported-witness-labels"]

VerificationTest[
 AllTrue[$BASSALG01Labels,
  BASS`Bianchi`BianchiTypeSpecQ[BASS`Bianchi`BianchiTypeSpec[#]] &],
 True,
 TestID -> "BASS-ALG01-SPEC-002-type-spec-schema"]

VerificationTest[
 AllTrue[$BASSALG01Labels,
  BASS`Bianchi`BianchiWitnessQ[#, BASS`Bianchi`BianchiWitness[#]] &],
 True,
 TestID -> "BASS-ALG01-WITNESS-001-canonical-witnesses"]

$BASSALG01Witnesses = BASS`Bianchi`WitnessRegistry[];
$BASSALG01Structures = AssociationMap[
 BASS`Geometry`BianchiStructureConstants[
   Lookup[$BASSALG01Witnesses[#], "a"],
   Lookup[$BASSALG01Witnesses[#], "n"]] &,
 $BASSALG01Labels];

VerificationTest[
 AllTrue[Values[$BASSALG01Structures],
  BASS`Geometry`StructureConstantsQ[#] &&
    BASS`Geometry`JacobiIdentityQ[#] &],
 True,
 TestID -> "BASS-ALG01-CARTAN-001-structure-and-jacobi"]

VerificationTest[
 $BASSALG01Structures["I"],
 ConstantArray[0, {3, 3, 3}],
 TestID -> "BASS-ALG01-WITNESS-I-001-zero-structure"]

VerificationTest[
 $BASSALG01Structures["IX"],
 Normal[LeviCivitaTensor[3]],
 TestID -> "BASS-ALG01-WITNESS-IX-001-su2-structure"]

$BASSALG01Connections = AssociationMap[
 BASS`Geometry`LeviCivitaConnection[$BASSALG01Structures[#]] &,
 $BASSALG01Labels];

VerificationTest[
 AllTrue[$BASSALG01Labels,
  BASS`Geometry`MetricCompatibilityQ[$BASSALG01Connections[#]] &&
    BASS`Geometry`TorsionFreeQ[
      $BASSALG01Connections[#], $BASSALG01Structures[#]] &],
 True,
 TestID -> "BASS-ALG01-CARTAN-002-metric-and-torsion"]

$BASSALG01Riemann = AssociationMap[
 BASS`Geometry`SpatialRiemann[
   $BASSALG01Structures[#], $BASSALG01Connections[#]] &,
 $BASSALG01Labels];

VerificationTest[
 BASS`Geometry`SpatialRicci[$BASSALG01Riemann["II"]],
 DiagonalMatrix[{1/2, -1/2, -1/2}],
 TestID -> "BASS-ALG01-WITNESS-II-001-ricci"]

VerificationTest[
 {BASS`Geometry`SpatialRicci[$BASSALG01Riemann["V"]],
  BASS`Geometry`SpatialRicciScalar[$BASSALG01Riemann["V"]]},
 {-2 IdentityMatrix[3], -6},
 TestID -> "BASS-ALG01-WITNESS-V-001-negative-curvature"]

VerificationTest[
 {BASS`Geometry`SpatialRicci[$BASSALG01Riemann["IX"]],
  BASS`Geometry`SpatialRicciScalar[$BASSALG01Riemann["IX"]]},
 {IdentityMatrix[3]/2, 3/2},
 TestID -> "BASS-ALG01-WITNESS-IX-002-positive-curvature"]

VerificationTest[
 BASS`Bianchi`ExceptionalVIm1over9ConstraintResidual[
   $BASSALG01Witnesses["VI_-1/9"]],
 {0, 0},
 TestID -> "BASS-ALG01-WITNESS-VIM1OVER9-001-constraints"]

VerificationTest[
 BASS`Bianchi`ExceptionalShearSurvivalQ[
   $BASSALG01Witnesses["VI_-1/9"]],
 True,
 TestID -> "BASS-ALG01-WITNESS-VIM1OVER9-002-shear-survival"]

VerificationTest[
 With[{adapter = BASS`Geometry`XActRiemannConventionAdapter[]},
  BASS`Geometry`RiemannConventionAdapterQ[adapter] &&
   Lookup[adapter, "project_from_xact_factor"] === -1],
 True,
 TestID -> "BASS-ALG01-RIEMANN-001-xact-project-adapter"]
