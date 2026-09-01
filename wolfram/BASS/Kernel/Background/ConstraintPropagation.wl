(* ::Package:: *)

BeginPackage["BASS`Background`"];

EvolutionPolicySpec::usage =
 "EvolutionPolicySpec[key] returns the exact BG-02 off-shell background-evolution policy.";
EvolutionPolicySpecQ::usage =
 "EvolutionPolicySpecQ[spec] validates a BG-02 off-shell policy.";
HomogeneousVectorDivergence::usage =
 "HomogeneousVectorDivergence[Gamma,v] returns D_a v^a for constant spatial ONF components.";
EinsteinConstraintPropagationRHS::usage =
 "EinsteinConstraintPropagationRHS[policy,H,sigma,CH,CM,Gamma] returns D0 of the Hamiltonian and momentum residuals in the homogeneous geodesic Fermi frame.";

Begin["`Private`"];

ClearAll[matrix3Q, vector3Q, tensor333Q, policyRegistry,
 EvolutionPolicySpec, EvolutionPolicySpecQ,
 HomogeneousVectorDivergence, EinsteinConstraintPropagationRHS];

matrix3Q[x_] := MatrixQ[x] && Dimensions[x] === {3, 3};
vector3Q[x_] := ListQ[x] && Dimensions[x] === {3};
tensor333Q[x_] := ArrayDepth[x] === 3 && Dimensions[x] === {3, 3, 3};

policyRegistry[] := <|
 "spatial_einstein_unadjusted" -> <|
   "schema_version" -> "1.0.0",
   "stage_id" -> "BG_02",
   "policy_id" -> "spatial_einstein_unadjusted",
   "evolution_owner" -> "spatial Einstein residual S_ab=0",
   "H_rhs" -> "RaychaudhuriRHS - C_H/12",
   "hamiltonian_propagation_coefficient" -> -3,
   "momentum_propagation" ->
    "D0 C_Ma = -(4H delta_a^b + sigma_a^b) C_Mb",
   "runtime_relation" ->
    "matches the existing metric-derived Type-V residual audit",
   "claim_boundary" ->
    "OFF_SHELL_FORMULATION_POLICY_ONLY_NO_NUMERICAL_SOLVER"|>,
 "raychaudhuri_adjusted" -> <|
   "schema_version" -> "1.0.0",
   "stage_id" -> "BG_02",
   "policy_id" -> "raychaudhuri_adjusted",
   "evolution_owner" -> "Raychaudhuri normal-normal combination",
   "H_rhs" -> "RaychaudhuriRHS",
   "hamiltonian_propagation_coefficient" -> -2,
   "momentum_propagation" ->
    "D0 C_Ma = -(4H delta_a^b + sigma_a^b) C_Mb in the homogeneous scope",
   "runtime_relation" ->
    "constraint-adjusted alternative; not the current Type-V audit policy",
   "claim_boundary" ->
    "OFF_SHELL_FORMULATION_POLICY_ONLY_NO_NUMERICAL_SOLVER"|>
|>;

EvolutionPolicySpec[key_String] :=
 Lookup[policyRegistry[], key,
  Failure["UnsupportedEvolutionPolicy", <|"key" -> key|>]];
EvolutionPolicySpec[_] := Failure["InvalidEvolutionPolicyKey", <||>];

EvolutionPolicySpecQ[spec_Association] := And[
 Lookup[spec, "schema_version", None] === "1.0.0",
 Lookup[spec, "stage_id", None] === "BG_02",
 MemberQ[{"spatial_einstein_unadjusted", "raychaudhuri_adjusted"},
  Lookup[spec, "policy_id", None]],
 MemberQ[{-3, -2},
  Lookup[spec, "hamiltonian_propagation_coefficient", None]],
 Lookup[spec, "claim_boundary", None] ===
  "OFF_SHELL_FORMULATION_POLICY_ONLY_NO_NUMERICAL_SOLVER"
];
EvolutionPolicySpecQ[_] := False;

HomogeneousVectorDivergence[gamma_?tensor333Q, v_?vector3Q] :=
 Together[Sum[gamma[[a, b, a]] v[[b]], {a, 3}, {b, 3}]];
HomogeneousVectorDivergence[___] :=
 Failure["InvalidHomogeneousVectorDivergenceInput", <||>];

EinsteinConstraintPropagationRHS[
 policy_String, H_, sigma_?matrix3Q, cH_, cM_?vector3Q,
 gamma_?tensor333Q] :=
 Module[{spec, coefficient, divCM},
  spec = EvolutionPolicySpec[policy];
  If[FailureQ[spec], Return[spec]];
  coefficient = Lookup[spec, "hamiltonian_propagation_coefficient"];
  divCM = HomogeneousVectorDivergence[gamma, cM];
  <|
   "policy_id" -> policy,
   "hamiltonian_dot" -> Together[coefficient H cH - 2 divCM],
   "momentum_dot" -> Together[-(4 H IdentityMatrix[3] + sigma) . cM],
   "divergence_momentum" -> divCM,
   "no_hamiltonian_to_momentum_feedback" -> True,
   "claim_boundary" ->
    "HOMOGENEOUS_CONSTRAINT_PROPAGATION_ONLY_NO_INHOMOGENEOUS_ADM_CLAIM"|>
 ];
EinsteinConstraintPropagationRHS[___] :=
 Failure["InvalidEinsteinConstraintPropagationInput", <||>];

End[];
EndPackage[];
