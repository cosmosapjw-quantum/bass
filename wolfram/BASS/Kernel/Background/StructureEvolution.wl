(* ::Package:: *)

BeginPackage["BASS`Background`"];

StructureEvolutionRHS::usage =
 "StructureEvolutionRHS[H,sigma,a,n] returns the Fermi-frame D0 evolution of the Bianchi structure vector and symmetric structure matrix.";
JacobiConstraintResidual::usage =
 "JacobiConstraintResidual[n,a] returns n_ab a^b.";
JacobiConstraintPropagationResidual::usage =
 "JacobiConstraintPropagationResidual[H,sigma,n,a] verifies D0(n.a)=(-2H I+sigma).(n.a) under the structure evolution.";

Begin["`Private`"];

ClearAll[matrix3Q, vector3Q, StructureEvolutionRHS,
 JacobiConstraintResidual, JacobiConstraintPropagationResidual];

matrix3Q[x_] := MatrixQ[x] && Dimensions[x] === {3, 3};
vector3Q[x_] := ListQ[x] && Dimensions[x] === {3};

StructureEvolutionRHS[
 H_, sigma_?matrix3Q, a_?vector3Q, n_?matrix3Q] := <|
 "a_dot" -> Together[-H a - sigma . a],
 "n_dot" -> Together[-H n + sigma . n + n . sigma],
 "frame" -> "Fermi-propagated spatial ONF",
 "claim_boundary" ->
  "GENERIC_STRUCTURE_EVOLUTION_ONLY_NO_BRANCH_RUNTIME_LOWERING"|>;
StructureEvolutionRHS[___] :=
 Failure["InvalidStructureEvolutionInput", <||>];

JacobiConstraintResidual[n_?matrix3Q, a_?vector3Q] := Together[n . a];
JacobiConstraintResidual[___] := Failure["InvalidJacobiConstraintInput", <||>];

JacobiConstraintPropagationResidual[
 H_, sigma_?matrix3Q, n_?matrix3Q, a_?vector3Q] :=
 Module[{rhs, direct, predicted, jacobi},
  rhs = StructureEvolutionRHS[H, sigma, a, n];
  If[FailureQ[rhs], Return[rhs]];
  jacobi = JacobiConstraintResidual[n, a];
  direct = Lookup[rhs, "n_dot"] . a + n . Lookup[rhs, "a_dot"];
  predicted = (-2 H IdentityMatrix[3] + sigma) . jacobi;
  Together[direct - predicted]
 ];
JacobiConstraintPropagationResidual[___] :=
 Failure["InvalidJacobiPropagationInput", <||>];

End[];
EndPackage[];
