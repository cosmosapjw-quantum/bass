(* ::Package:: *)

BeginPackage["BASS`Geometry`"];

LeviCivitaConnection::usage =
 "LeviCivitaConnection[a,n] returns Gamma^gamma_{alpha beta} for the locked orthonormal-frame Bianchi structure constants.";
ConnectionTorsionResidual::usage =
 "ConnectionTorsionResidual[a,n] returns Gamma^gamma_{alpha beta}-Gamma^gamma_{beta alpha}-C^gamma_{alpha beta}.";
ConnectionMetricCompatibilityResidual::usage =
 "ConnectionMetricCompatibilityResidual[a,n] returns Gamma^gamma_{alpha beta}+Gamma^beta_{alpha gamma}.";
ConnectionOneFormTerms::usage =
 "ConnectionOneFormTerms[a,n] returns the nonzero terms of omega^gamma_beta=Gamma^gamma_{alpha beta} omega^alpha.";
ConnectionCovarianceQ::usage =
 "ConnectionCovarianceQ[R,a,n] checks exact constant-O(3) covariance of the generated connection.";

Begin["`Private`"];

ClearAll[
 LeviCivitaConnection, ConnectionTorsionResidual,
 ConnectionMetricCompatibilityResidual, ConnectionOneFormTerms,
 ConnectionCovarianceQ, connectionVector3Q, connectionMatrix3Q,
 connectionSymmetric3Q, connectionTensor333Q, connectionZeroQ,
 transformConnectionCoefficients
];

connectionVector3Q[vector_] := ListQ[vector] && Length[vector] === 3;
connectionMatrix3Q[matrix_] :=
 MatrixQ[matrix] && Dimensions[matrix] === {3, 3};
connectionSymmetric3Q[matrix_] :=
 connectionMatrix3Q[matrix]
  && TrueQ[Simplify[matrix == Transpose[matrix]]];
connectionTensor333Q[tensor_] :=
 ListQ[tensor] && Dimensions[tensor] === {3, 3, 3};
connectionZeroQ[expression_] :=
 AllTrue[Flatten[{expression}], TrueQ[PossibleZeroQ[#]] &];

LeviCivitaConnection[a_List, n_List] /;
  connectionVector3Q[a] && connectionSymmetric3Q[n] := Module[
 {structure},
 structure = BianchiStructureConstants[a, n];
 If[FailureQ[structure], Return[structure]];
 Array[
   Function[{gamma, alpha, beta},
    Simplify[
     (
       structure[[gamma, alpha, beta]]
        - structure[[alpha, beta, gamma]]
        + structure[[beta, gamma, alpha]]
      )/2
    ]
   ],
   {3, 3, 3}
  ]
];
LeviCivitaConnection[___] := Failure[
 "InvalidBianchiConnectionInput",
 <|"reason" -> "a must be length three and n symmetric 3 by 3"|>
];

ConnectionTorsionResidual[a_List, n_List] := Module[
 {structure, connection},
 structure = BianchiStructureConstants[a, n];
 connection = LeviCivitaConnection[a, n];
 If[FailureQ[structure], Return[structure]];
 If[FailureQ[connection], Return[connection]];
 Array[
   Function[{gamma, alpha, beta},
    Simplify[
     connection[[gamma, alpha, beta]]
      - connection[[gamma, beta, alpha]]
      - structure[[gamma, alpha, beta]]
    ]
   ],
   {3, 3, 3}
  ]
];
ConnectionTorsionResidual[___] := Failure[
 "InvalidBianchiConnectionInput", <||>
];

ConnectionMetricCompatibilityResidual[a_List, n_List] := Module[
 {connection},
 connection = LeviCivitaConnection[a, n];
 If[FailureQ[connection], Return[connection]];
 Array[
   Function[{gamma, alpha, beta},
    Simplify[
     connection[[gamma, alpha, beta]]
      + connection[[beta, alpha, gamma]]
    ]
   ],
   {3, 3, 3}
  ]
];
ConnectionMetricCompatibilityResidual[___] := Failure[
 "InvalidBianchiConnectionInput", <||>
];

ConnectionOneFormTerms[a_List, n_List] := Module[
 {connection},
 connection = LeviCivitaConnection[a, n];
 If[FailureQ[connection], Return[connection]];
 Flatten @ Table[
   If[
    ! TrueQ[PossibleZeroQ[connection[[gamma, alpha, beta]]]],
    <|
     "upper" -> gamma,
     "lower" -> beta,
     "basis" -> alpha,
     "coefficient" -> Simplify[connection[[gamma, alpha, beta]]]
    |>,
    Nothing
   ],
   {gamma, 3}, {beta, 3}, {alpha, 3}
  ]
];
ConnectionOneFormTerms[___] := Failure[
 "InvalidBianchiConnectionInput", <||>
];

transformConnectionCoefficients[
 rotation_List,
 connection_List
] /; OrthogonalMatrix3Q[rotation] && connectionTensor333Q[connection] :=
 Array[
  Function[{gamma, alpha, beta},
   Sum[
    rotation[[gamma, rho]]
     rotation[[alpha, mu]]
     rotation[[beta, nu]]
     connection[[rho, mu, nu]],
    {rho, 3}, {mu, 3}, {nu, 3}
   ]
  ],
  {3, 3, 3}
 ] // Simplify;
transformConnectionCoefficients[___] := Failure[
 "InvalidConnectionFrameTransform", <||>
];

ConnectionCovarianceQ[
 rotation_List,
 a_List,
 n_List
] := Module[
 {transformedData, originalConnection, expectedConnection,
  generatedConnection},
 transformedData = TransformBianchiAlgebraData[rotation, a, n];
 If[FailureQ[transformedData], Return[False]];
 originalConnection = LeviCivitaConnection[a, n];
 If[FailureQ[originalConnection], Return[False]];
 expectedConnection = transformConnectionCoefficients[
   rotation, originalConnection
  ];
 If[FailureQ[expectedConnection], Return[False]];
 generatedConnection = LeviCivitaConnection[
   transformedData["a"], transformedData["n"]
  ];
 If[FailureQ[generatedConnection], Return[False]];
 connectionZeroQ[Simplify[generatedConnection - expectedConnection]]
];
ConnectionCovarianceQ[___] := False;

End[];
EndPackage[];
