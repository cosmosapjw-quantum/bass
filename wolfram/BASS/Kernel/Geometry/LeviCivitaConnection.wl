(* ::Package:: *)

BeginPackage["BASS`Geometry`"];

LeviCivitaConnection::usage =
 "LeviCivitaConnection[a,n] returns Gamma^gamma_{alpha beta}=<e_gamma,nabla_{e_alpha}e_beta> for the locked orthonormal-frame Bianchi structure constants.";
ConnectionTorsionResidual::usage =
 "ConnectionTorsionResidual[a,n] returns Gamma^gamma_{alpha beta}-Gamma^gamma_{beta alpha}-C^gamma_{alpha beta}.";
ConnectionMetricCompatibilityResidual::usage =
 "ConnectionMetricCompatibilityResidual[a,n] returns Gamma^gamma_{alpha beta}+Gamma^beta_{alpha gamma}.";
ConnectionOneFormTerms::usage =
 "ConnectionOneFormTerms[a,n] returns the nonzero terms of omega^gamma_beta=Gamma^gamma_{alpha beta} omega^alpha.";
ConnectionCovarianceQ::usage =
 "ConnectionCovarianceQ[R,a,n] checks exact constant-O(3) covariance of the generated connection.";
ConnectionToLockedGammaOrder::usage =
 "ConnectionToLockedGammaOrder[gammaGenerated] maps generated array order {gamma,alpha,beta} to the project-locked storage order {alpha,beta,gamma}.";
ConnectionFromLockedGammaOrder::usage =
 "ConnectionFromLockedGammaOrder[gammaLocked] maps project-locked storage order {alpha,beta,gamma} back to generated order {gamma,alpha,beta}.";
ConnectionCompositionReceipt::usage =
 "ConnectionCompositionReceipt[] returns the exact ALG-01R2 to GEO-02 composition receipt without promoting curvature.";
ConnectionCompositionReceiptQ::usage =
 "ConnectionCompositionReceiptQ[receipt] validates the exact parent identity, exceptional carriers and connection-only claim boundary.";

Begin["`Private`"];

ClearAll[
 LeviCivitaConnection, ConnectionTorsionResidual,
 ConnectionMetricCompatibilityResidual, ConnectionOneFormTerms,
 ConnectionCovarianceQ, ConnectionToLockedGammaOrder,
 ConnectionFromLockedGammaOrder, ConnectionCompositionReceipt,
 ConnectionCompositionReceiptQ, connectionVector3Q, connectionMatrix3Q,
 connectionSymmetric3Q, connectionTensor333Q, connectionZeroQ,
 transformConnectionCoefficients
];

connectionVector3Q[vector_] := ListQ[vector] && Length[vector] === 3;
connectionMatrix3Q[matrix_] :=
 MatrixQ[matrix] && Dimensions[matrix] === {3, 3};
connectionSymmetric3Q[matrix_] := And[
 connectionMatrix3Q[matrix],
 TrueQ[Simplify[matrix == Transpose[matrix]]]
];
connectionTensor333Q[tensor_] :=
 ListQ[tensor] && Dimensions[tensor] === {3, 3, 3};
connectionZeroQ[expression_] :=
 AllTrue[Flatten[{expression}], TrueQ[PossibleZeroQ[#]] &];

LeviCivitaConnection[a_List, n_List] /; And[
  connectionVector3Q[a],
  connectionSymmetric3Q[n]
 ] := Module[{structure},
 structure = BianchiStructureConstants[a, n];
 If[FailureQ[structure], Return[structure]];
 Array[
   Function[{gamma, alpha, beta},
    Simplify[
     (structure[[gamma, alpha, beta]]
       - structure[[alpha, beta, gamma]]
       + structure[[beta, gamma, alpha]])/2
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

ConnectionOneFormTerms[a_List, n_List] := Module[{connection},
 connection = LeviCivitaConnection[a, n];
 If[FailureQ[connection], Return[connection]];
 Flatten @ Table[
   If[! TrueQ[PossibleZeroQ[connection[[gamma, alpha, beta]]]],
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
] /; And[
  OrthogonalMatrix3Q[rotation],
  connectionTensor333Q[connection]
 ] := Array[
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

ConnectionToLockedGammaOrder[tensor_List] /;
  connectionTensor333Q[tensor] := Transpose[tensor, {2, 3, 1}];
ConnectionToLockedGammaOrder[___] := Failure[
 "InvalidGeneratedConnectionTensor",
 <|"expected_order" -> {"gamma", "alpha", "beta"}|>
];

ConnectionFromLockedGammaOrder[tensor_List] /;
  connectionTensor333Q[tensor] := Transpose[tensor, {3, 1, 2}];
ConnectionFromLockedGammaOrder[___] := Failure[
 "InvalidLockedConnectionTensor",
 <|"expected_order" -> {"alpha", "beta", "gamma"}|>
];

ConnectionCompositionReceipt[] := Module[
 {semanticHash, expectedHash, exceptionalWitness, carrierReport, pass},
 expectedHash =
  "e0e5fbba464a839fcb5b11d41c7772c666224ec69f806910aab3bfab5a2f1762";
 semanticHash = BASS`Bianchi`CanonicalTypeSpecRegistrySemanticSHA256[];
 exceptionalWitness =
  BASS`Bianchi`CanonicalWitnessRegistry[]["VI_-1/9"];
 carrierReport =
  BASS`Bianchi`ExceptionalShearCarrierReport[exceptionalWitness];
 pass = And[
   StringQ[semanticHash],
   semanticHash === expectedHash,
   AssociationQ[carrierReport],
   TrueQ[Lookup[carrierReport, "independent_carriers_present", False]]
  ];
 <|
  "schema_version" -> "1.0.0",
  "program_id" -> "BASS-MASTER-SSOT-V2-WOLFRAM-XACT-20260901",
  "stage_id" -> "GEO_02R2",
  "status" -> If[pass, "PASS", "BLOCKED"],
  "parent_alg01r2_commit" ->
   "b0a2c8da9e74ce960394ae9c67c9744fb8e497ad",
  "parent_semantic_registry_sha256" -> semanticHash,
  "expected_parent_semantic_registry_sha256" -> expectedHash,
  "exceptional_carrier_report" -> carrierReport,
  "generated_array_order" -> {"gamma", "alpha", "beta"},
  "locked_project_array_order" -> {"alpha", "beta", "gamma"},
  "generated_to_locked_permutation" -> {2, 3, 1},
  "locked_to_generated_permutation" -> {3, 1, 2},
  "connection_dimension" -> "L^-1",
  "curvature_generated" -> False,
  "claim_boundary" ->
   "ALG01R2_TO_SPATIAL_LEVI_CIVITA_CONNECTION_ONLY_NO_CURVATURE_BACKGROUND_OR_SCIENCE_PROMOTION"
 |>
];

ConnectionCompositionReceiptQ[receipt_Association] := And[
 Lookup[receipt, "schema_version", None] === "1.0.0",
 Lookup[receipt, "stage_id", None] === "GEO_02R2",
 Lookup[receipt, "status", None] === "PASS",
 Lookup[receipt, "parent_alg01r2_commit", None] ===
  "b0a2c8da9e74ce960394ae9c67c9744fb8e497ad",
 Lookup[receipt, "parent_semantic_registry_sha256", None] ===
  "e0e5fbba464a839fcb5b11d41c7772c666224ec69f806910aab3bfab5a2f1762",
 Lookup[receipt, "generated_array_order", None] ===
  {"gamma", "alpha", "beta"},
 Lookup[receipt, "locked_project_array_order", None] ===
  {"alpha", "beta", "gamma"},
 TrueQ[
  Lookup[
   Lookup[receipt, "exceptional_carrier_report", <||>],
   "independent_carriers_present", False
  ]
 ],
 Lookup[receipt, "curvature_generated", True] === False,
 Lookup[receipt, "claim_boundary", None] ===
  "ALG01R2_TO_SPATIAL_LEVI_CIVITA_CONNECTION_ONLY_NO_CURVATURE_BACKGROUND_OR_SCIENCE_PROMOTION"
];
ConnectionCompositionReceiptQ[_] := False;

End[];
EndPackage[];
