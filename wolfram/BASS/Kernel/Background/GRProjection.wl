(* ::Package:: *)

BeginPackage["BASS`Background`"];

GRBackgroundAssumptions::usage =
 "GRBackgroundAssumptions[] returns the exact BG-02 geometric, frame, matter-decomposition and unit assumptions.";
GRBackgroundAssumptionsQ::usage =
 "GRBackgroundAssumptionsQ[spec] validates the BG-02 assumption contract.";
GRBackgroundEquationSet::usage =
 "GRBackgroundEquationSet[] returns the machine-readable BG-02 equation and off-shell-policy registry.";
GRBackgroundEquationSetQ::usage =
 "GRBackgroundEquationSetQ[spec] validates the BG-02 equation-set registry.";
STF3::usage =
 "STF3[m] returns the symmetric trace-free part of an exact 3x3 spatial matrix.";
HamiltonianConstraintResidual::usage =
 "HamiltonianConstraintResidual[H,sigma,R3,rho,Lambda,kappaE] returns R3+6H^2-sigma_ab sigma^ab-2Lambda-2kappaE rho.";
NormalEinsteinProjectionResidual::usage =
 "NormalEinsteinProjectionResidual[...] returns one half of the Hamiltonian residual, equal to the normal-normal Einstein residual.";
HomogeneousMomentumGeometry::usage =
 "HomogeneousMomentumGeometry[Gamma,sigma] returns D_a K-D_b K^b_a=-D_b sigma^b_a for constant ONF components.";
MomentumConstraintResidual::usage =
 "MomentumConstraintResidual[Gamma,sigma,q,kappaE] returns the homogeneous momentum residual M_a-kappaE q_a.";
RaychaudhuriRHS::usage =
 "RaychaudhuriRHS[H,sigma,rho,p,Lambda,kappaE] gives D0 H in the geodesic hypersurface-normal Raychaudhuri formulation.";
SpatialEinsteinTraceRHS::usage =
 "SpatialEinsteinTraceRHS[H,sigma,R3,rho,p,Lambda,kappaE] gives the unadjusted spatial-Einstein trace evolution for H.";
ShearEvolutionRHS::usage =
 "ShearEvolutionRHS[H,sigma,Ricci3,pi,kappaE] gives D0 sigma_ab in a Fermi-propagated spatial ONF.";
EnergyConservationResidual::usage =
 "EnergyConservationResidual[rhoDot,H,rho,p,divq,Aq,sigma,pi,source] returns the normal-frame energy-balance residual, where source=-n_a Q^a.";

Begin["`Private`"];

ClearAll[matrix3Q, vector3Q, symmetric3Q, requiredAssumptionKeys,
 requiredEquationKeys, GRBackgroundAssumptions, GRBackgroundAssumptionsQ,
 GRBackgroundEquationSet, GRBackgroundEquationSetQ, STF3,
 HamiltonianConstraintResidual, NormalEinsteinProjectionResidual,
 HomogeneousMomentumGeometry, MomentumConstraintResidual,
 RaychaudhuriRHS, SpatialEinsteinTraceRHS, ShearEvolutionRHS,
 EnergyConservationResidual];

matrix3Q[x_] := MatrixQ[x] && Dimensions[x] === {3, 3};
vector3Q[x_] := ListQ[x] && Dimensions[x] === {3};
symmetric3Q[x_] := matrix3Q[x] && TrueQ[FullSimplify[x == Transpose[x]]];

requiredAssumptionKeys[] := {
 "schema_version", "stage_id", "metric_signature", "normal_congruence",
 "spatial_frame", "extrinsic_curvature", "stress_energy",
 "einstein_equation", "derivative", "units", "scope",
 "claim_boundary"
};

GRBackgroundAssumptions[] := <|
 "schema_version" -> "1.0.0",
 "stage_id" -> "BG_02",
 "metric_signature" -> {-1, 1, 1, 1},
 "normal_congruence" -> <|
   "norm" -> -1,
   "hypersurface_orthogonal" -> True,
   "vorticity" -> 0,
   "acceleration" -> 0,
   "lapse" -> "homogeneous",
   "shift" -> 0|>,
 "spatial_frame" -> <|
   "kind" -> "orthonormal",
   "component_transport" -> "Fermi-propagated authority frame",
   "triad_rotation" -> 0|>,
 "extrinsic_curvature" -> <|
   "definition" -> "K_ab = H_geom h_ab + sigma_ab",
   "trace" -> "K = 3 H_geom",
   "shear_trace" -> 0|>,
 "stress_energy" -> <|
   "definition" ->
    "T_ab = rho n_a n_b + 2 n_(a q_b) + p h_ab + pi_ab",
   "q_spatial" -> True,
   "pi_spatial_symmetric_tracefree" -> True|>,
 "einstein_equation" ->
  "G_ab + Lambda g_ab = kappa_E T_ab; kappa_E = 8 Pi G/c^4",
 "derivative" -> <|
   "operator" -> "D0",
   "definition" -> "D0=(1/c) partial_t=d/ds",
   "length_parameter" -> "s=c t"|>,
 "units" -> <|
   "natural_units" -> False,
   "H_sigma_a_n" -> "L^-1",
   "R3_Lambda_kappaT" -> "L^-2",
   "constraint_derivative" -> "L^-3"|>,
 "scope" -> <|
   "included" -> {
    "generic homogeneous GR projection identities",
    "geodesic hypersurface-normal background evolution",
    "off-shell evolution-policy distinction",
    "Einstein and Jacobi constraint propagation design"},
   "excluded" -> {
    "inhomogeneous perturbations", "nongeodesic lapse",
    "rotating-component frame adapters", "matter-model closure",
    "all-eleven-branch runtime lowering"}|>,
 "claim_boundary" ->
  "BG02_GENERIC_PROJECTION_AND_CONSTRAINT_DESIGN_NO_RUNTIME_OR_SCIENCE_PROMOTION"|>;

GRBackgroundAssumptionsQ[spec_Association] := And[
 SubsetQ[Keys[spec], requiredAssumptionKeys[]],
 Lookup[spec, "schema_version", None] === "1.0.0",
 Lookup[spec, "stage_id", None] === "BG_02",
 Lookup[spec, "metric_signature", None] === {-1, 1, 1, 1},
 TrueQ[Lookup[Lookup[spec, "normal_congruence", <||>],
   "hypersurface_orthogonal", False]],
 Lookup[Lookup[spec, "normal_congruence", <||>], "acceleration", None] === 0,
 Lookup[Lookup[spec, "spatial_frame", <||>], "triad_rotation", None] === 0,
 Lookup[spec, "claim_boundary", None] ===
  "BG02_GENERIC_PROJECTION_AND_CONSTRAINT_DESIGN_NO_RUNTIME_OR_SCIENCE_PROMOTION"
];
GRBackgroundAssumptionsQ[_] := False;

requiredEquationKeys[] := {
 "schema_version", "stage_id", "state", "constraints", "evolution",
 "matter_balance", "off_shell_policies", "dimensions", "known_limits",
 "claim_boundary"
};

GRBackgroundEquationSet[] := <|
 "schema_version" -> "1.0.0",
 "stage_id" -> "BG_02",
 "state" -> {
  "H_geom", "sigma_ab", "aB_a", "nB_ab", "rho", "p", "q_a", "pi_ab"},
 "constraints" -> <|
  "hamiltonian" ->
   "C_H = R3 + 6 H^2 - sigma_ab sigma^ab - 2 Lambda - 2 kappa_E rho",
  "momentum" ->
   "C_Ma = D_a K - D_b K^b_a - kappa_E q_a",
  "jacobi" -> "C_Ja = n_ab a^b"|>,
 "evolution" -> <|
  "raychaudhuri" ->
   "D0 H = -H^2 - sigma_ab sigma^ab/3 - kappa_E(rho+3p)/6 + Lambda/3",
  "spatial_einstein_trace" ->
   "D0 H|S=0 = D0 H|Raychaudhuri - C_H/12",
  "shear" ->
   "D0 sigma_ab = -3 H sigma_ab - R3_<ab> + kappa_E pi_ab",
  "structure_vector" -> "D0 a_a = -H a_a - sigma_a^b a_b",
  "structure_matrix" ->
   "D0 n_ab = -H n_ab + sigma_a^c n_cb + sigma_b^c n_ac"|>,
 "matter_balance" ->
  "D0 rho + 3H(rho+p) + D_a q^a + 2 A_a q^a + sigma_ab pi^ab = -n_a Q^a",
 "off_shell_policies" -> {
  "spatial_einstein_unadjusted", "raychaudhuri_adjusted"},
 "dimensions" -> <|
  "H_sigma_a_n" -> "L^-1",
  "R3_Lambda_kappaT_constraints" -> "L^-2",
  "D0_constraints" -> "L^-3"|>,
 "known_limits" -> {"Kasner", "de Sitter", "Milne/open-FLRW"},
 "claim_boundary" ->
  "BG02_EQUATION_REGISTRY_ONLY_NO_MATTER_PLUGIN_OR_NUMERICAL_SOLVER"|>;

GRBackgroundEquationSetQ[spec_Association] := And[
 SubsetQ[Keys[spec], requiredEquationKeys[]],
 Lookup[spec, "schema_version", None] === "1.0.0",
 Lookup[spec, "stage_id", None] === "BG_02",
 AssociationQ[Lookup[spec, "constraints", None]],
 AssociationQ[Lookup[spec, "evolution", None]],
 Sort[Lookup[spec, "off_shell_policies", {}]] ===
  Sort[{"spatial_einstein_unadjusted", "raychaudhuri_adjusted"}],
 Lookup[spec, "claim_boundary", None] ===
  "BG02_EQUATION_REGISTRY_ONLY_NO_MATTER_PLUGIN_OR_NUMERICAL_SOLVER"
];
GRBackgroundEquationSetQ[_] := False;

STF3[m_?matrix3Q] :=
 Together[(m + Transpose[m])/2 - IdentityMatrix[3] Tr[m]/3];
STF3[_] := Failure["InvalidSpatialMatrix", <||>];

HamiltonianConstraintResidual[H_, sigma_, r3_, rho_, lambda_, kappaE_] :=
 Together[r3 + 6 H^2 - Tr[sigma . sigma] - 2 lambda - 2 kappaE rho];

NormalEinsteinProjectionResidual[H_, sigma_, r3_, rho_, lambda_, kappaE_] :=
 Together[HamiltonianConstraintResidual[
   H, sigma, r3, rho, lambda, kappaE]/2];

HomogeneousMomentumGeometry[gamma_, sigma_] /;
  ArrayDepth[gamma] === 3 && Dimensions[gamma] === {3, 3, 3} &&
   matrix3Q[sigma] :=
 Table[Together[-Sum[
    gamma[[b, d, b]] sigma[[d, a]] -
     gamma[[b, a, d]] sigma[[b, d]],
    {b, 3}, {d, 3}]], {a, 3}];
HomogeneousMomentumGeometry[___] :=
 Failure["InvalidHomogeneousMomentumInput", <||>];

MomentumConstraintResidual[gamma_, sigma_, q_?vector3Q, kappaE_] :=
 Module[{geometry = HomogeneousMomentumGeometry[gamma, sigma]},
  If[FailureQ[geometry], geometry, Together[geometry - kappaE q]]
 ];
MomentumConstraintResidual[___] :=
 Failure["InvalidMomentumConstraintInput", <||>];

RaychaudhuriRHS[H_, sigma_?matrix3Q, rho_, p_, lambda_, kappaE_] :=
 Together[-H^2 - Tr[sigma . sigma]/3 -
   kappaE (rho + 3 p)/6 + lambda/3];
RaychaudhuriRHS[___] := Failure["InvalidRaychaudhuriInput", <||>];

SpatialEinsteinTraceRHS[
 H_, sigma_?matrix3Q, r3_, rho_, p_, lambda_, kappaE_] :=
 Together[RaychaudhuriRHS[H, sigma, rho, p, lambda, kappaE] -
   HamiltonianConstraintResidual[
    H, sigma, r3, rho, lambda, kappaE]/12];
SpatialEinsteinTraceRHS[___] :=
 Failure["InvalidSpatialEinsteinTraceInput", <||>];

ShearEvolutionRHS[
 H_, sigma_?matrix3Q, ricci3_?matrix3Q, pi_?matrix3Q, kappaE_] :=
 Together[-3 H sigma - STF3[ricci3] + kappaE STF3[pi]];
ShearEvolutionRHS[___] := Failure["InvalidShearEvolutionInput", <||>];

EnergyConservationResidual[
 rhoDot_, H_, rho_, p_, divq_, Aq_, sigma_?matrix3Q, pi_?matrix3Q,
 source_] :=
 Together[rhoDot + 3 H (rho + p) + divq + 2 Aq +
   Tr[sigma . pi] - source];
EnergyConservationResidual[___] :=
 Failure["InvalidEnergyConservationInput", <||>];

End[];
EndPackage[];
