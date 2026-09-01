(* ::Package:: *)

BeginPackage["BASS`Geometry`"];

OrthogonalMatrix3Q::usage =
 "OrthogonalMatrix3Q[R] validates an exact real 3 by 3 O(3) frame matrix.";
TransformBianchiAlgebraData::usage =
 "TransformBianchiAlgebraData[R,a,n] returns a'=R.a and n'=det(R) R.n.Transpose[R].";
TransformStructureConstants::usage =
 "TransformStructureConstants[R,C] transforms C^gamma_{alpha beta} as a (1,2) tensor under R.";
StructureCovarianceResidual::usage =
 "StructureCovarianceResidual[R,a,n] compares generated and transformed structure constants.";
StructureCovarianceQ::usage =
 "StructureCovarianceQ[R,a,n] requires the exact O(3) covariance residual to vanish.";

Begin["`Private`"];

ClearAll[
 OrthogonalMatrix3Q, TransformBianchiAlgebraData,
 TransformStructureConstants, StructureCovarianceResidual,
 StructureCovarianceQ, frameVector3Q, frameMatrix3Q,
 frameSymmetric3Q, frameTensor333Q, frameZeroQ
];

frameVector3Q[vector_] := ListQ[vector] && Length[vector] === 3;
frameMatrix3Q[matrix_] :=
 MatrixQ[matrix] && Dimensions[matrix] === {3, 3};
frameSymmetric3Q[matrix_] :=
 frameMatrix3Q[matrix] && TrueQ[Simplify[matrix == Transpose[matrix]]];
frameTensor333Q[tensor_] :=
 ListQ[tensor] && Dimensions[tensor] === {3, 3, 3};
frameZeroQ[expression_] :=
 AllTrue[Flatten[{expression}], TrueQ[PossibleZeroQ[#]] &];

OrthogonalMatrix3Q[rotation_] := And[
 frameMatrix3Q[rotation],
 TrueQ[Simplify[Transpose[rotation] . rotation == IdentityMatrix[3]]],
 MemberQ[{-1, 1}, Simplify[Det[rotation]]]
];

TransformBianchiAlgebraData[
 rotation_List,
 a_List,
 n_List
] /; (
 OrthogonalMatrix3Q[rotation] &&
 frameVector3Q[a] &&
 frameSymmetric3Q[n]
) := <|
 "a" -> Simplify[rotation . a],
 "n" -> Simplify[
   Det[rotation] rotation . n . Transpose[rotation]
  ]
|>;
TransformBianchiAlgebraData[___] := Failure[
 "InvalidBianchiFrameTransform",
 <|
  "reason" ->
   "R must be exact O(3), a length three, and n symmetric 3 by 3"
 |>
];

TransformStructureConstants[
 rotation_List,
 structure_List
] /; (
 OrthogonalMatrix3Q[rotation] &&
 frameTensor333Q[structure]
) := Array[
 Function[{gamma, alpha, beta},
  Sum[
   rotation[[gamma, rho]]
    rotation[[alpha, mu]]
    rotation[[beta, nu]]
    structure[[rho, mu, nu]],
   {rho, 3}, {mu, 3}, {nu, 3}
  ]
 ],
 {3, 3, 3}
] // Simplify;
TransformStructureConstants[___] := Failure[
 "InvalidStructureFrameTransform",
 <|
  "reason" -> "R must be exact O(3) and C must have dimensions 3 by 3 by 3"
 |>
];

StructureCovarianceResidual[
 rotation_List,
 a_List,
 n_List
] := Module[
 {transformedData, originalStructure, expectedStructure,
  generatedStructure},
 transformedData = TransformBianchiAlgebraData[rotation, a, n];
 If[FailureQ[transformedData], Return[transformedData]];
 originalStructure = BianchiStructureConstants[a, n];
 If[FailureQ[originalStructure], Return[originalStructure]];
 expectedStructure = TransformStructureConstants[
   rotation,
   originalStructure
  ];
 If[FailureQ[expectedStructure], Return[expectedStructure]];
 generatedStructure = BianchiStructureConstants[
   transformedData["a"],
   transformedData["n"]
  ];
 If[FailureQ[generatedStructure], Return[generatedStructure]];
 Simplify[generatedStructure - expectedStructure]
];

StructureCovarianceQ[
 rotation_List,
 a_List,
 n_List
] := Module[{residual},
 residual = StructureCovarianceResidual[rotation, a, n];
 ! FailureQ[residual] && frameZeroQ[residual]
];

End[];
EndPackage[];
