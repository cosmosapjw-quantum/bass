(* ::Package:: *)

BeginPackage["BASS`Geometry`"];

BianchiStructureConstants::usage =
 "BianchiStructureConstants[a,n] returns C^gamma_{alpha beta}=epsilon_{alpha beta delta} n^{delta gamma}+a_alpha delta^gamma_beta-a_beta delta^gamma_alpha.";
StructureConstantsQ::usage =
 "StructureConstantsQ[C] validates a real exact 3x3x3 tensor antisymmetric in its first two slots.";
JacobiResidual::usage =
 "JacobiResidual[C] returns J^l_{ijk}=C^m_{jk}C^l_{im}+cyclic permutations.";
JacobiIdentityQ::usage =
 "JacobiIdentityQ[C] is True when every exact Jacobi residual vanishes.";

Begin["`Private`"];

ClearAll[zeroQ, vector3Q, matrix3Q, tensor333Q,
 BianchiStructureConstants, StructureConstantsQ, JacobiResidual,
 JacobiIdentityQ];

zeroQ[x_] := TrueQ[PossibleZeroQ[Together[x]]];
vector3Q[x_] := ListQ[x] && Dimensions[x] === {3};
matrix3Q[x_] := MatrixQ[x] && Dimensions[x] === {3, 3};
tensor333Q[x_] := ArrayDepth[x] === 3 && Dimensions[x] === {3, 3, 3};

BianchiStructureConstants[a_?vector3Q, n_?matrix3Q] :=
 Module[{epsilon},
  If[! TrueQ[FullSimplify[n == Transpose[n]]],
   Return[Failure["NonSymmetricStructureMatrix", <||>]]];
  epsilon = Normal[LeviCivitaTensor[3]];
  Table[
   Together[
    Sum[epsilon[[alpha, beta, delta]] n[[delta, gamma]], {delta, 3}] +
     a[[alpha]] KroneckerDelta[gamma, beta] -
     a[[beta]] KroneckerDelta[gamma, alpha]],
   {alpha, 3}, {beta, 3}, {gamma, 3}]
 ];
BianchiStructureConstants[___] :=
 Failure["InvalidBianchiStructureInput", <||>];

StructureConstantsQ[c_?tensor333Q] :=
 AllTrue[Flatten[Table[c[[i, j, k]] + c[[j, i, k]],
    {i, 3}, {j, 3}, {k, 3}]], zeroQ];
StructureConstantsQ[_] := False;

JacobiResidual[c_?tensor333Q] :=
 Table[
  Together[Sum[
    c[[j, k, m]] c[[i, m, l]] +
    c[[k, i, m]] c[[j, m, l]] +
    c[[i, j, m]] c[[k, m, l]],
    {m, 3}]],
  {i, 3}, {j, 3}, {k, 3}, {l, 3}];
JacobiResidual[_] := Failure["InvalidStructureConstants", <||>];

JacobiIdentityQ[c_?tensor333Q] := Module[{residual},
 residual = JacobiResidual[c];
 StructureConstantsQ[c] && AllTrue[Flatten[residual], zeroQ]
];
JacobiIdentityQ[_] := False;

End[];
EndPackage[];
