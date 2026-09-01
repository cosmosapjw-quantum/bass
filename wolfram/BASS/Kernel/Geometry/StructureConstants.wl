(* ::Package:: *)

BeginPackage["BASS`Geometry`"];

LeviCivita3::usage =
 "LeviCivita3[i,j,k] is the locked spatial alternating symbol with epsilon_123=+1.";
BianchiStructureConstants::usage =
 "BianchiStructureConstants[a,n] returns C^gamma_{alpha beta} from the locked Bianchi decomposition.";
JacobiVectorResidual::usage =
 "JacobiVectorResidual[a,n] returns the three-component residual n^{alpha beta} a_beta.";
JacobiTensorResidual::usage =
 "JacobiTensorResidual[a,n] returns the full four-index Lie-algebra Jacobi residual.";
JacobiIdentityQ::usage =
 "JacobiIdentityQ[a,n] requires both the vector and full-tensor Jacobi residuals to vanish exactly.";
StructureAntisymmetryQ::usage =
 "StructureAntisymmetryQ[a,n] checks C^gamma_{alpha beta}=-C^gamma_{beta alpha}.";
CartanCoframeTerms::usage =
 "CartanCoframeTerms[a,n] returns coefficients in d omega^gamma for the alpha<beta wedge basis.";
CartanReconstructionQ::usage =
 "CartanReconstructionQ[a,n] reconstructs the structure constants from CartanCoframeTerms.";

Begin["`Private`"];

ClearAll[
 vector3Q, matrix3Q, symmetric3Q, zeroArrayQ,
 LeviCivita3, BianchiStructureConstants, JacobiVectorResidual,
 JacobiTensorResidual, JacobiIdentityQ, StructureAntisymmetryQ,
 CartanCoframeTerms, CartanReconstructionQ
];

vector3Q[vector_] := ListQ[vector] && Length[vector] === 3;
matrix3Q[matrix_] := MatrixQ[matrix] && Dimensions[matrix] === {3, 3};
symmetric3Q[matrix_] :=
 matrix3Q[matrix] && TrueQ[Simplify[matrix == Transpose[matrix]]];
zeroArrayQ[expression_] :=
 AllTrue[Flatten[expression], TrueQ[PossibleZeroQ[#]] &];

LeviCivita3[i_Integer, j_Integer, k_Integer] /;
  AllTrue[{i, j, k}, 1 <= # <= 3 &] := Signature[{i, j, k}];

BianchiStructureConstants[a_List, n_List] /;
  vector3Q[a] && symmetric3Q[n] :=
 Array[
  Function[{gamma, alpha, beta},
   Sum[LeviCivita3[alpha, beta, delta] n[[delta, gamma]],
     {delta, 3}]
    + a[[alpha]] KroneckerDelta[gamma, beta]
    - a[[beta]] KroneckerDelta[gamma, alpha]],
  {3, 3, 3}
 ];
BianchiStructureConstants[___] :=
 Failure["InvalidBianchiAlgebraInput", <|
   "reason" -> "a must be length three and n must be symmetric 3 by 3"
 |>];

JacobiVectorResidual[a_List, n_List] /;
  vector3Q[a] && symmetric3Q[n] := Simplify[n . a];
JacobiVectorResidual[___] :=
 Failure["InvalidBianchiAlgebraInput", <||>];

JacobiTensorResidual[a_List, n_List] /;
  vector3Q[a] && symmetric3Q[n] := Module[{structure},
 structure = BianchiStructureConstants[a, n];
 Array[
   Function[{delta, alpha, beta, gamma},
    Sum[
      structure[[mu, beta, gamma]] structure[[delta, alpha, mu]]
       + structure[[mu, gamma, alpha]] structure[[delta, beta, mu]]
       + structure[[mu, alpha, beta]] structure[[delta, gamma, mu]],
      {mu, 3}]],
   {3, 3, 3, 3}
  ] // Simplify
];
JacobiTensorResidual[___] :=
 Failure["InvalidBianchiAlgebraInput", <||>];

JacobiIdentityQ[a_List, n_List] := Module[{vectorResidual, tensorResidual},
 vectorResidual = JacobiVectorResidual[a, n];
 tensorResidual = JacobiTensorResidual[a, n];
 ! FailureQ[vectorResidual]
  && ! FailureQ[tensorResidual]
  && zeroArrayQ[vectorResidual]
  && zeroArrayQ[tensorResidual]
];

StructureAntisymmetryQ[a_List, n_List] := Module[{structure},
 structure = BianchiStructureConstants[a, n];
 ! FailureQ[structure]
  && zeroArrayQ[structure + Transpose[structure, {1, 3, 2}]]
];

CartanCoframeTerms[a_List, n_List] := Module[{structure},
 structure = BianchiStructureConstants[a, n];
 If[FailureQ[structure], Return[structure]];
 Association @ Table[
   gamma -> Flatten @ Table[
     If[
      alpha < beta
       && ! TrueQ[PossibleZeroQ[structure[[gamma, alpha, beta]]]],
      <|
       "coefficient" -> Simplify[-structure[[gamma, alpha, beta]]],
       "wedge" -> {alpha, beta}
      |>,
      Nothing
     ],
     {alpha, 3}, {beta, 3}
    ],
   {gamma, 3}
  ]
];

CartanReconstructionQ[a_List, n_List] := Module[
 {structure, terms, reconstructed},
 structure = BianchiStructureConstants[a, n];
 If[FailureQ[structure], Return[False]];
 terms = CartanCoframeTerms[a, n];
 reconstructed = ConstantArray[0, {3, 3, 3}];
 KeyValueMap[
  Function[{gamma, termList},
   Scan[
    Function[term,
     With[
      {alpha = term["wedge"][[1]],
       beta = term["wedge"][[2]],
       coefficient = term["coefficient"]},
      reconstructed[[gamma, alpha, beta]] = -coefficient;
      reconstructed[[gamma, beta, alpha]] = coefficient
     ]
    ],
    termList
   ]
  ],
  terms
 ];
 zeroArrayQ[Simplify[reconstructed - structure]]
];

End[];
EndPackage[];
