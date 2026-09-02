(* ::Package:: *)

BeginPackage["BASS`Geometry`"];

SpatialRiemannTensor::usage =
 "SpatialRiemannTensor[a,n] returns the all-lower homogeneous spatial Riemann tensor R_{alpha beta gamma delta}, consuming the canonical LeviCivitaConnection and rejecting non-Jacobi inputs.";
SpatialRicciTensor::usage =
 "SpatialRicciTensor[a,n] returns R_{gamma beta}=Sum_alpha R_{alpha beta gamma alpha}.";
SpatialScalarCurvature::usage =
 "SpatialScalarCurvature[a,n] returns the spatial Ricci scalar.";
SpatialRiemannSymmetryReport::usage =
 "SpatialRiemannSymmetryReport[a,n] checks pair antisymmetries, pair exchange, first Bianchi, and Ricci symmetry.";
SpatialCurvatureCovarianceQ::usage =
 "SpatialCurvatureCovarianceQ[R,a,n] checks exact O(3) covariance of the all-lower spatial Riemann tensor.";
SpatialCurvatureWitnessRegistry::usage =
 "SpatialCurvatureWitnessRegistry[] returns exact I, II, V, IX, and exceptional VI_-1/9 direct ONF witnesses.";
ValidateSpatialCurvatureWitness::usage =
 "ValidateSpatialCurvatureWitness[label] validates one direct spatial-curvature witness.";
ValidateSpatialCurvatureWitnesses::usage =
 "ValidateSpatialCurvatureWitnesses[] validates all direct spatial-curvature witnesses.";
SpatialCurvatureFormulaRegistry::usage =
 "SpatialCurvatureFormulaRegistry[] returns only the curvature-owned formulas; the connection formula remains owned by LeviCivitaConnection.wl.";
SpatialCurvatureFormulaRegistryQ::usage =
 "SpatialCurvatureFormulaRegistryQ[registry] validates the curvature-only formula registry.";
GeometryLineageCompositionReceipt::usage =
 "GeometryLineageCompositionReceipt[] reports the PR83 canonical-connection to PR82 curvature-donor composition without selecting a second connection authority.";
GeometryLineageCompositionReceiptQ::usage =
 "GeometryLineageCompositionReceiptQ[receipt] validates the bounded geometry-lineage composition receipt.";

Begin["`Private`"];

ClearAll[
 curvatureVector3Q, curvatureSymmetric3Q, curvatureZeroQ,
 curvatureTensor3333Q, curvatureExactCoefficientQ,
 curvatureInputFailure, transformCovariantRiemann,
 SpatialRiemannTensor, SpatialRicciTensor, SpatialScalarCurvature,
 SpatialRiemannSymmetryReport, SpatialCurvatureCovarianceQ,
 SpatialCurvatureWitnessRegistry, ValidateSpatialCurvatureWitness,
 ValidateSpatialCurvatureWitnesses, SpatialCurvatureFormulaRegistry,
 SpatialCurvatureFormulaRegistryQ, GeometryLineageCompositionReceipt,
 GeometryLineageCompositionReceiptQ
];

curvatureVector3Q[vector_] := ListQ[vector] && Length[vector] === 3;
curvatureSymmetric3Q[matrix_] := MatrixQ[matrix] &&
 Dimensions[matrix] === {3, 3} &&
 TrueQ[Simplify[matrix == Transpose[matrix]]];
curvatureZeroQ[expression_] :=
 AllTrue[Flatten[{expression}], TrueQ[PossibleZeroQ[#]] &];
curvatureTensor3333Q[tensor_] :=
 ListQ[tensor] && Dimensions[tensor] === {3, 3, 3, 3};
curvatureExactCoefficientQ[value_] :=
 IntegerQ[value] || MatchQ[value, _Rational];

curvatureInputFailure[a_, n_] := Which[
 !curvatureVector3Q[a] || !curvatureSymmetric3Q[n],
 Failure[
  "InvalidBianchiCurvatureInput",
  <|"reason" -> "a must be length three and n symmetric 3 by 3"|>
 ],
 !TrueQ[JacobiIdentityQ[a, n]],
 Failure[
  "NonLieBianchiCurvatureInput",
  <|
   "reason" -> "n^{alpha beta} a_beta and the full Jacobi tensor must vanish",
   "jacobi_vector_residual" -> JacobiVectorResidual[a, n]
  |>
 ],
 True,
 None
];

SpatialRiemannTensor[a_, n_] := Module[
 {failure, structure, connection},
 failure = curvatureInputFailure[a, n];
 If[FailureQ[failure], Return[failure]];
 structure = BianchiStructureConstants[a, n];
 connection = LeviCivitaConnection[a, n];
 If[FailureQ[structure], Return[structure]];
 If[FailureQ[connection], Return[connection]];
 Array[
  Function[{alpha, beta, gamma, delta},
   Simplify[
    Sum[
     connection[[mu, beta, gamma]] connection[[delta, alpha, mu]]
      - connection[[mu, alpha, gamma]] connection[[delta, beta, mu]]
      - structure[[mu, alpha, beta]] connection[[delta, mu, gamma]],
     {mu, 3}
    ]
   ]
  ],
  {3, 3, 3, 3}
 ]
];

SpatialRicciTensor[a_, n_] := Module[{riemann},
 riemann = SpatialRiemannTensor[a, n];
 If[FailureQ[riemann], Return[riemann]];
 Array[
  Function[{gamma, beta},
   Simplify[Sum[riemann[[alpha, beta, gamma, alpha]], {alpha, 3}]]
  ],
  {3, 3}
 ]
];

SpatialScalarCurvature[a_, n_] := Module[{ricci},
 ricci = SpatialRicciTensor[a, n];
 If[FailureQ[ricci], Return[ricci]];
 Simplify[Tr[ricci]]
];

SpatialRiemannSymmetryReport[a_, n_] := Module[
 {riemann, ricci, pair12, pair34, pairExchange, firstBianchi},
 riemann = SpatialRiemannTensor[a, n];
 If[FailureQ[riemann],
  Return[<|"status" -> "FAIL", "failure" -> riemann|>]
 ];
 ricci = SpatialRicciTensor[a, n];
 pair12 = Array[
   Function[{alpha, beta, gamma, delta},
    Simplify[
     riemann[[alpha, beta, gamma, delta]]
      + riemann[[beta, alpha, gamma, delta]]
    ]],
   {3, 3, 3, 3}
  ];
 pair34 = Array[
   Function[{alpha, beta, gamma, delta},
    Simplify[
     riemann[[alpha, beta, gamma, delta]]
      + riemann[[alpha, beta, delta, gamma]]
    ]],
   {3, 3, 3, 3}
  ];
 pairExchange = Array[
   Function[{alpha, beta, gamma, delta},
    Simplify[
     riemann[[alpha, beta, gamma, delta]]
      - riemann[[gamma, delta, alpha, beta]]
    ]],
   {3, 3, 3, 3}
  ];
 firstBianchi = Array[
   Function[{alpha, beta, gamma, delta},
    Simplify[
     riemann[[alpha, beta, gamma, delta]]
      + riemann[[beta, gamma, alpha, delta]]
      + riemann[[gamma, alpha, beta, delta]]
    ]],
   {3, 3, 3, 3}
  ];
 <|
  "status" -> "PASS",
  "pair_12_antisymmetry" -> curvatureZeroQ[pair12],
  "pair_34_antisymmetry" -> curvatureZeroQ[pair34],
  "pair_exchange" -> curvatureZeroQ[pairExchange],
  "first_bianchi" -> curvatureZeroQ[firstBianchi],
  "ricci_symmetric" -> curvatureZeroQ[ricci - Transpose[ricci]]
 |>
];

transformCovariantRiemann[rotation_, riemann_] /; And[
 OrthogonalMatrix3Q[rotation],
 curvatureTensor3333Q[riemann]
] := Array[
 Function[{alpha, beta, gamma, delta},
  Simplify[
   Sum[
    rotation[[alpha, mu]] rotation[[beta, nu]]
     rotation[[gamma, rho]] rotation[[delta, sigma]]
     riemann[[mu, nu, rho, sigma]],
    {mu, 3}, {nu, 3}, {rho, 3}, {sigma, 3}
   ]
  ]
 ],
 {3, 3, 3, 3}
];
transformCovariantRiemann[___] :=
 Failure["InvalidSpatialCurvatureFrameTransform", <||>];

SpatialCurvatureCovarianceQ[rotation_, a_, n_] := Module[
 {transformedData, original, expected, generated},
 transformedData = TransformBianchiAlgebraData[rotation, a, n];
 If[FailureQ[transformedData], Return[False]];
 original = SpatialRiemannTensor[a, n];
 If[FailureQ[original], Return[False]];
 expected = transformCovariantRiemann[rotation, original];
 If[FailureQ[expected], Return[False]];
 generated = SpatialRiemannTensor[
   transformedData["a"], transformedData["n"]
  ];
 !FailureQ[generated] && curvatureZeroQ[Simplify[generated - expected]]
];
SpatialCurvatureCovarianceQ[___] := False;

SpatialCurvatureWitnessRegistry[] := Module[{base},
 base = BASS`Bianchi`CanonicalWitnessRegistry[];
 <|
  "I" -> Join[
    KeyTake[base["I"], {"a", "n"}],
    <|
     "expected_ricci" -> ConstantArray[0, {3, 3}],
     "expected_scalar" -> 0,
     "expected_section_12" -> 0
    |>
   ],
  "II" -> Join[
    KeyTake[base["II"], {"a", "n"}],
    <|
     "expected_ricci" -> DiagonalMatrix[{1/2, -1/2, -1/2}],
     "expected_scalar" -> -1/2,
     "expected_section_12" -> 1/4
    |>
   ],
  "V" -> Join[
    KeyTake[base["V"], {"a", "n"}],
    <|
     "expected_ricci" -> -2 IdentityMatrix[3],
     "expected_scalar" -> -6,
     "expected_section_12" -> -1
    |>
   ],
  "IX" -> Join[
    KeyTake[base["IX"], {"a", "n"}],
    <|
     "expected_ricci" -> IdentityMatrix[3]/2,
     "expected_scalar" -> 3/2,
     "expected_section_12" -> 1/4
    |>
   ],
  "VI_-1/9" -> Join[
    KeyTake[base["VI_-1/9"], {"a", "n"}],
    <|
     "expected_ricci" -> {{-22, 0, 0}, {0, -6, 8}, {0, 8, 2}},
     "expected_scalar" -> -26,
     "expected_section_12" -> -15
    |>
   ]
 |>
];

ValidateSpatialCurvatureWitness[label_String] := Module[
 {spec, a, n, connection, torsion, metricResidual, riemann, ricci,
  scalar, symmetry, checks},
 spec = Lookup[
   SpatialCurvatureWitnessRegistry[], label, Missing["UnknownWitness"]
  ];
 If[MissingQ[spec],
  Return[Failure["UnknownSpatialCurvatureWitness", <|"label" -> label|>]]
 ];
 a = spec["a"];
 n = spec["n"];
 connection = LeviCivitaConnection[a, n];
 torsion = ConnectionTorsionResidual[a, n];
 metricResidual = ConnectionMetricCompatibilityResidual[a, n];
 riemann = SpatialRiemannTensor[a, n];
 ricci = SpatialRicciTensor[a, n];
 scalar = SpatialScalarCurvature[a, n];
 symmetry = SpatialRiemannSymmetryReport[a, n];
 checks = <|
   "jacobi_admitted" -> TrueQ[JacobiIdentityQ[a, n]],
   "canonical_connection_available" -> !FailureQ[connection],
   "torsion_free" -> curvatureZeroQ[torsion],
   "metric_compatible" -> curvatureZeroQ[metricResidual],
   "pair_12_antisymmetry" -> TrueQ[symmetry["pair_12_antisymmetry"]],
   "pair_34_antisymmetry" -> TrueQ[symmetry["pair_34_antisymmetry"]],
   "pair_exchange" -> TrueQ[symmetry["pair_exchange"]],
   "first_bianchi" -> TrueQ[symmetry["first_bianchi"]],
   "ricci_symmetric" -> TrueQ[symmetry["ricci_symmetric"]],
   "ricci_expected" -> TrueQ[Simplify[ricci == spec["expected_ricci"]]],
   "scalar_expected" ->
    TrueQ[PossibleZeroQ[scalar - spec["expected_scalar"]]],
   "section_12_expected" ->
    TrueQ[PossibleZeroQ[
      riemann[[1, 2, 2, 1]] - spec["expected_section_12"]
     ]]
  |>;
 <|
  "schema_version" -> "1.0.0",
  "label" -> label,
  "pass" -> And @@ Values[checks],
  "checks" -> checks,
  "ricci" -> ricci,
  "scalar_curvature" -> scalar,
  "section_12" -> riemann[[1, 2, 2, 1]],
  "claim_boundary" ->
   "DIMENSIONLESS_DIRECT_ONF_CURVATURE_WITNESS_ONLY_NO_PHYSICAL_SCALE_OR_BACKGROUND_EVOLUTION"
 |>
];
ValidateSpatialCurvatureWitness[___] :=
 Failure["InvalidSpatialCurvatureWitnessLabel", <||>];

ValidateSpatialCurvatureWitnesses[] :=
 AssociationMap[
  ValidateSpatialCurvatureWitness,
  Keys[SpatialCurvatureWitnessRegistry[]]
 ];

SpatialCurvatureFormulaRegistry[] := {
 <|
  "formula_id" -> "GEO03-RIEMANN-001",
  "owner" -> "SpatialCurvature.wl",
  "target" -> "R3_{alpha beta gamma delta}",
  "dimension" -> "L^-2",
  "terms" -> {
    <|
     "input" -> "Gamma^mu_{beta gamma} Gamma^delta_{alpha mu}",
     "coefficient" -> 1
    |>,
    <|
     "input" -> "Gamma^mu_{alpha gamma} Gamma^delta_{beta mu}",
     "coefficient" -> -1
    |>,
    <|
     "input" -> "C^mu_{alpha beta} Gamma^delta_{mu gamma}",
     "coefficient" -> -1
    |>
   },
  "connection_owner" -> "LeviCivitaConnection.wl",
  "convention" ->
   "[nabla_alpha,nabla_beta]v^delta=R_{alpha beta gamma}^delta v^gamma"
 |>,
 <|
  "formula_id" -> "GEO03-RICCI-001",
  "owner" -> "SpatialCurvature.wl",
  "target" -> "R3_{gamma beta}",
  "dimension" -> "L^-2",
  "terms" -> {
    <|
     "input" -> "sum_alpha R3_{alpha beta gamma alpha}",
     "coefficient" -> 1
    |>
   },
  "connection_owner" -> "LeviCivitaConnection.wl",
  "convention" -> "orthonormal spatial contraction"
 |>,
 <|
  "formula_id" -> "GEO03-SCALAR-001",
  "owner" -> "SpatialCurvature.wl",
  "target" -> "R3",
  "dimension" -> "L^-2",
  "terms" -> {
    <|
     "input" -> "delta^{gamma beta} R3_{gamma beta}",
     "coefficient" -> 1
    |>
   },
  "connection_owner" -> "LeviCivitaConnection.wl",
  "convention" -> "positive spatial metric"
 |>
};

SpatialCurvatureFormulaRegistryQ[registry_List] := And[
 Length[registry] === 3,
 Lookup[registry, "formula_id"] === {
  "GEO03-RIEMANN-001", "GEO03-RICCI-001", "GEO03-SCALAR-001"
 },
 DuplicateFreeQ[Lookup[registry, "formula_id"]],
 AllTrue[
  registry,
  AssociationQ[#] &&
   Lookup[#, "owner", None] === "SpatialCurvature.wl" &&
   Lookup[#, "connection_owner", None] === "LeviCivitaConnection.wl" &&
   Lookup[#, "dimension", None] === "L^-2" &&
   ListQ[Lookup[#, "terms", None]] &&
   AllTrue[
    Lookup[#, "terms", {}],
    AssociationQ[#] &&
      curvatureExactCoefficientQ[
       Lookup[#, "coefficient", Indeterminate]
      ] &
   ] &
 ]
];
SpatialCurvatureFormulaRegistryQ[_] := False;

GeometryLineageCompositionReceipt[] := Module[
 {direct, parentReceipt, nonJacobiFailure, pass},
 direct = ValidateSpatialCurvatureWitnesses[];
 parentReceipt = ConnectionCompositionReceipt[];
 nonJacobiFailure = SpatialRiemannTensor[
   {1, 0, 0}, IdentityMatrix[3]
  ];
 pass = And[
   SpatialCurvatureFormulaRegistryQ[SpatialCurvatureFormulaRegistry[]],
   AllTrue[Values[direct], TrueQ[Lookup[#, "pass", False]] &],
   ConnectionCompositionReceiptQ[parentReceipt],
   FailureQ[nonJacobiFailure]
  ];
 <|
  "schema_version" -> "1.0.0",
  "program_id" -> "BIANCHI-WOLFRAM-TRIREPO-20260830",
  "stage_id" -> "SYNC-MAP-01C",
  "status" -> If[pass, "PASS", "BLOCKED"],
  "canonical_connection_parent" -> <|
    "pull_request" -> 83,
    "publication_commit" ->
     "c787e6c51608568fcb60d52f010235f8cb2c1076",
    "publication_tree" ->
     "3619744e9ba2b0633737b244cb18310ec89047c8",
    "source_path" ->
     "wolfram/BASS/Kernel/Geometry/LeviCivitaConnection.wl",
    "source_blob" -> "c8e4be28b00956b1fe2009a7d5bc8222a45585e0"
   |>,
  "curvature_donor" -> <|
    "pull_request" -> 82,
    "publication_commit" ->
     "394cb32784aa9dff15b5196db35f0fa065289fc6",
    "publication_tree" ->
     "49db2af672800115976bd94f8773c6b71b081305",
    "source_paths" -> {
     "wolfram/BASS/Kernel/Geometry/ONFConnectionCurvature.wl",
     "wolfram/BASS/Kernel/Geometry/XCobaCurvatureWitnesses.wl"
    },
    "role" -> "CURVATURE_AND_INDEPENDENT_XCOBA_ORACLE_DONOR_ONLY"
   |>,
  "connection_reimplemented" -> False,
  "curvature_input_jacobi_gate" -> True,
  "direct_witnesses" -> Keys[direct],
  "independent_xcoba_witnesses_required" -> {"I", "V", "IX"},
  "spatial_curvature_dimension" -> "L^-2",
  "official_dag_mutated" -> False,
  "science_claim_promoted" -> False,
  "claim_boundary" ->
   "CANONICAL_CONNECTION_TO_SPATIAL_CURVATURE_COMPOSITION_ONLY_NO_EINSTEIN_BACKGROUND_OR_SCIENCE_PROMOTION"
 |>
];

GeometryLineageCompositionReceiptQ[receipt_Association] := And[
 Lookup[receipt, "schema_version", None] === "1.0.0",
 Lookup[receipt, "stage_id", None] === "SYNC-MAP-01C",
 Lookup[receipt, "status", None] === "PASS",
 Lookup[
  Lookup[receipt, "canonical_connection_parent", <||>],
  "pull_request", None
 ] === 83,
 Lookup[
  Lookup[receipt, "curvature_donor", <||>],
  "pull_request", None
 ] === 82,
 Lookup[receipt, "connection_reimplemented", True] === False,
 Lookup[receipt, "curvature_input_jacobi_gate", False] === True,
 Lookup[receipt, "direct_witnesses", {}] ===
  {"I", "II", "V", "IX", "VI_-1/9"},
 Lookup[receipt, "independent_xcoba_witnesses_required", {}] ===
  {"I", "V", "IX"},
 Lookup[receipt, "spatial_curvature_dimension", None] === "L^-2",
 Lookup[receipt, "official_dag_mutated", True] === False,
 Lookup[receipt, "science_claim_promoted", True] === False,
 Lookup[receipt, "claim_boundary", None] ===
  "CANONICAL_CONNECTION_TO_SPATIAL_CURVATURE_COMPOSITION_ONLY_NO_EINSTEIN_BACKGROUND_OR_SCIENCE_PROMOTION"
];
GeometryLineageCompositionReceiptQ[_] := False;

End[];
EndPackage[];
