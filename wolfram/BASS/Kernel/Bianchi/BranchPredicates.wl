(* ::Package:: *)

BeginPackage["BASS`Bianchi`"];

StructureClass::usage =
 "StructureClass[a] returns \"A\" when the Bianchi structure vector vanishes and \"B\" otherwise.";
SymmetricInertia::usage =
 "SymmetricInertia[n] returns {positive, negative, zero} eigenvalue counts for an exact real symmetric 3x3 matrix.";
TransverseDeterminant::usage =
 "TransverseDeterminant[n] returns Det[n[[{2,3},{2,3}]]] in the A-aligned chart.";
SignedH::usage =
 "SignedH[a,n] returns a[[1]]^2/Det[n_perp] in the A-aligned Class-B chart.";

Begin["`Private`"];

ClearAll[zeroQ, positiveQ, negativeQ, vector3Q, matrix3Q,
 StructureClass, SymmetricInertia, TransverseDeterminant, SignedH];

zeroQ[x_] := TrueQ[PossibleZeroQ[Together[x]]];
positiveQ[x_] := TrueQ[FullSimplify[x > 0]];
negativeQ[x_] := TrueQ[FullSimplify[x < 0]];
vector3Q[x_] := ListQ[x] && Dimensions[x] === {3};
matrix3Q[x_] := MatrixQ[x] && Dimensions[x] === {3, 3};

StructureClass[a_?vector3Q] :=
 If[AllTrue[a, zeroQ], "A", "B"];
StructureClass[_] := Failure["InvalidStructureVector", <||>];

SymmetricInertia[n_?matrix3Q] := Module[{eigenvalues},
 If[! TrueQ[FullSimplify[n == Transpose[n]]],
  Return[Failure["NonSymmetricStructureMatrix", <||>]]];
 eigenvalues = Eigenvalues[n];
 {Count[eigenvalues, _?positiveQ], Count[eigenvalues, _?negativeQ],
  Count[eigenvalues, _?zeroQ]}
];
SymmetricInertia[_] := Failure["InvalidStructureMatrix", <||>];

TransverseDeterminant[n_?matrix3Q] :=
 Together[Det[n[[{2, 3}, {2, 3}]]]];
TransverseDeterminant[_] := Failure["InvalidStructureMatrix", <||>];

SignedH[a_?vector3Q, n_?matrix3Q] := Module[{det},
 det = TransverseDeterminant[n];
 If[FailureQ[det] || zeroQ[det],
  Failure["DegenerateTransverseBlock", <|"determinant" -> det|>],
  Together[a[[1]]^2/det]]
];
SignedH[___] := Failure["InvalidSignedHInput", <||>];

End[];
EndPackage[];
