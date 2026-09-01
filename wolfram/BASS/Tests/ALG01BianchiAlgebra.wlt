$ALG01ExpectedLabels = {"I", "II", "V", "IX", "VI_-1/9"};
$ALG01Specs = BASS`Bianchi`CanonicalTypeSpecRegistry[];
$ALG01Witnesses = BASS`Bianchi`CanonicalWitnessRegistry[];
$ALG01Canonical = BASS`Bianchi`ValidateWitnessRegistry[];
$ALG01Hostile = BASS`Bianchi`ValidateHostileWitnesses[];

VerificationTest[
 Sort[Keys[$ALG01Specs]], Sort[$ALG01ExpectedLabels],
 TestID -> "BASS-ALG-01-spec-registry-labels"]
VerificationTest[
 AllTrue[Values[$ALG01Specs], BASS`Bianchi`BianchiTypeSpecQ], True,
 TestID -> "BASS-ALG-01-spec-registry-valid"]
VerificationTest[
 Sort[Keys[$ALG01Witnesses]], Sort[$ALG01ExpectedLabels],
 TestID -> "BASS-ALG-01-witness-registry-labels"]
VerificationTest[
 AllTrue[Values[$ALG01Canonical], TrueQ[Lookup[#, "pass", False]] &], True,
 TestID -> "BASS-ALG-01-canonical-registry-pass"]

VerificationTest[$ALG01Canonical["I"]["pass"], True,
 TestID -> "BASS-ALG-01-I-pass"]
VerificationTest[$ALG01Canonical["II"]["pass"], True,
 TestID -> "BASS-ALG-01-II-pass"]
VerificationTest[$ALG01Canonical["V"]["pass"], True,
 TestID -> "BASS-ALG-01-V-pass"]
VerificationTest[$ALG01Canonical["IX"]["pass"], True,
 TestID -> "BASS-ALG-01-IX-pass"]
VerificationTest[$ALG01Canonical["VI_-1/9"]["pass"], True,
 TestID -> "BASS-ALG-01-exceptional-pass"]

VerificationTest[
 FailureQ[BASS`Bianchi`ValidateCanonicalWitness["UNKNOWN"]], True,
 TestID -> "BASS-ALG-01-unknown-witness-fails-closed"]
VerificationTest[$ALG01Canonical["I"]["actual"]["n_rank"], 0,
 TestID -> "BASS-ALG-01-I-rank-zero"]
VerificationTest[$ALG01Canonical["II"]["actual"]["n_rank"], 1,
 TestID -> "BASS-ALG-01-II-rank-one"]
VerificationTest[$ALG01Canonical["V"]["actual"]["transverse_det_sign"], 0,
 TestID -> "BASS-ALG-01-V-zero-transverse-block"]
VerificationTest[$ALG01Canonical["IX"]["actual"]["n_inertia"], {3, 0, 0},
 TestID -> "BASS-ALG-01-IX-same-sign-inertia"]
VerificationTest[
 $ALG01Canonical["VI_-1/9"]["actual"]["signed_h"],
 BASS`IR`ExactScalarAST[-1/9],
 TestID -> "BASS-ALG-01-exceptional-signed-h"]
VerificationTest[
 Values[$ALG01Canonical["VI_-1/9"]["actual"]["exceptional_residuals"]],
 {0, 0}, TestID -> "BASS-ALG-01-exceptional-constraints"]

VerificationTest[
 AllTrue[Values[$ALG01Canonical],
  TrueQ[Lookup[Lookup[#, "checks", <||>], "jacobi_vector", False]] &],
 True, TestID -> "BASS-ALG-01-jacobi-vector-all"]
VerificationTest[
 AllTrue[Values[$ALG01Canonical],
  TrueQ[Lookup[Lookup[#, "checks", <||>], "jacobi_tensor", False]] &],
 True, TestID -> "BASS-ALG-01-jacobi-tensor-all"]
VerificationTest[
 AllTrue[Values[$ALG01Canonical],
  TrueQ[Lookup[Lookup[#, "checks", <||>], "structure_antisymmetry", False]] &],
 True, TestID -> "BASS-ALG-01-antisymmetry-all"]
VerificationTest[
 AllTrue[Values[$ALG01Canonical],
  TrueQ[Lookup[Lookup[#, "checks", <||>], "cartan_reconstruction", False]] &],
 True, TestID -> "BASS-ALG-01-cartan-reconstruction-all"]

$ALG01CartanCounts = AssociationMap[
 Total[Length /@ Values[BASS`Geometry`CartanCoframeTerms[
     $ALG01Witnesses[#]["a"], $ALG01Witnesses[#]["n"]]]] &,
 $ALG01ExpectedLabels];
VerificationTest[
 Lookup[$ALG01CartanCounts, $ALG01ExpectedLabels], {0, 1, 2, 3, 3},
 TestID -> "BASS-ALG-01-cartan-term-counts"]
VerificationTest[
 BASS`Geometry`CartanCoframeTerms[
  $ALG01Witnesses["II"]["a"], $ALG01Witnesses["II"]["n"]][1],
 {<|"coefficient" -> -1, "wedge" -> {2, 3}|>},
 TestID -> "BASS-ALG-01-II-cartan-term"]
VerificationTest[
 BASS`Geometry`CartanCoframeTerms[
  $ALG01Witnesses["V"]["a"], $ALG01Witnesses["V"]["n"]],
 <|1 -> {},
   2 -> {<|"coefficient" -> -1, "wedge" -> {1, 2}|>},
   3 -> {<|"coefficient" -> -1, "wedge" -> {1, 3}|>}|>,
 TestID -> "BASS-ALG-01-V-cartan-terms"]
VerificationTest[
 BASS`Geometry`CartanCoframeTerms[
  $ALG01Witnesses["IX"]["a"], $ALG01Witnesses["IX"]["n"]],
 <|1 -> {<|"coefficient" -> -1, "wedge" -> {2, 3}|>},
   2 -> {<|"coefficient" -> 1, "wedge" -> {1, 3}|>},
   3 -> {<|"coefficient" -> -1, "wedge" -> {1, 2}|>}|>,
 TestID -> "BASS-ALG-01-IX-cartan-terms"]
VerificationTest[
 BASS`Geometry`CartanCoframeTerms[
  $ALG01Witnesses["VI_-1/9"]["a"],
  $ALG01Witnesses["VI_-1/9"]["n"]],
 <|1 -> {},
   2 -> {<|"coefficient" -> -4, "wedge" -> {1, 2}|>,
         <|"coefficient" -> 2, "wedge" -> {1, 3}|>},
   3 -> {<|"coefficient" -> 2, "wedge" -> {1, 3}|>}|>,
 TestID -> "BASS-ALG-01-exceptional-cartan-terms"]

VerificationTest[
 AllTrue[Values[$ALG01Hostile], TrueQ[Lookup[#, "detected", False]] &],
 True, TestID -> "BASS-ALG-01-hostile-all-detected"]
VerificationTest[
 SubsetQ[$ALG01Hostile["JACOBI_BREAK"]["failed_checks"],
  {"a_zero", "jacobi_vector", "jacobi_tensor"}], True,
 TestID -> "BASS-ALG-01-hostile-jacobi-break"]
VerificationTest[
 MemberQ[$ALG01Hostile["IX_INERTIA_BREAK"]["failed_checks"], "n_inertia"],
 True, TestID -> "BASS-ALG-01-hostile-IX-inertia"]
VerificationTest[
 SubsetQ[$ALG01Hostile["V_N_BREAK"]["failed_checks"],
  {"n_zero", "n_rank", "n_inertia"}], True,
 TestID -> "BASS-ALG-01-hostile-V-nonzero-n"]
VerificationTest[
 SubsetQ[$ALG01Hostile["EXCEPTIONAL_H_BREAK"]["failed_checks"],
  {"signed_h", "exceptional_constraints"}], True,
 TestID -> "BASS-ALG-01-hostile-exceptional-h"]
VerificationTest[
 MemberQ[$ALG01Hostile["EXCEPTIONAL_MOMENTUM_BREAK"]["failed_checks"],
  "exceptional_constraints"], True,
 TestID -> "BASS-ALG-01-hostile-exceptional-momentum"]

$ALG01RoleMutation = ReplacePart[$ALG01Witnesses["II"],
 "role" -> "physical magnitude"];
VerificationTest[
 FailureQ[BASS`Bianchi`BranchPredicateReport[
   $ALG01Specs["II"], $ALG01RoleMutation]], True,
 TestID -> "BASS-ALG-01-canonical-role-firewall"]
VerificationTest[
 FailureQ[BASS`Geometry`BianchiStructureConstants[
   {0, 0}, IdentityMatrix[3]]], True,
 TestID -> "BASS-ALG-01-invalid-input-fails-closed"]
