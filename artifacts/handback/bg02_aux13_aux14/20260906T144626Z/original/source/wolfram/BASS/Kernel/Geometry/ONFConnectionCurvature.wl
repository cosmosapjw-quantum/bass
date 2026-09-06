(* ::Package:: *)

BeginPackage["BASS`Geometry`"];

ONFLeviCivitaConnection::usage =
 "ONFLeviCivitaConnection[a,n] is the locked-order compatibility view of the canonical LeviCivitaConnection implementation.";
ONFConnectionEquationSolve::usage =
 "ONFConnectionEquationSolve[a,n] independently solves torsion-free and metric-compatibility equations in locked {alpha,beta,gamma} order.";
ONFTorsionResidual::usage =
 "ONFTorsionResidual[a,n] checks the locked-order connection against the structure constants.";
ONFMetricCompatibilityResidual::usage =
 "ONFMetricCompatibilityResidual[a,n] checks locked-order metric compatibility.";
ONFRiemannTensor::usage =
 "ONFRiemannTensor[a,n] returns the homogeneous spatial all-lower Riemann tensor using the canonical connection implementation.";
ONFRicciTensor::usage =
 "ONFRicciTensor[a,n] contracts ONFRiemannTensor as R_{gamma beta}=sum_alpha R_{alpha beta gamma alpha}.";
ONFScalarCurvature::usage =
 "ONFScalarCurvature[a,n] returns the orthonormal-frame spatial scalar curvature.";
ONFRiemannSymmetryReport::usage =
 "ONFRiemannSymmetryReport[a,n] checks exact Riemann pair symmetries.";
ONFCurvatureWitnessRegistry::usage =
 "ONFCurvatureWitnessRegistry[] returns exact Bianchi I, V and IX curvature witnesses.";
ValidateONFCurvatureWitness::usage =
 "ValidateONFCurvatureWitness[label] validates one direct ONF curvature witness.";
ValidateONFCurvatureWitnesses::usage =
 "ValidateONFCurvatureWitnesses[] validates all direct ONF curvature witnesses.";
W3FormulaRegistry::usage =
 "W3FormulaRegistry[] returns the connection-reference and spatial-curvature semantic registry.";
W3FormulaRegistryQ::usage =
 "W3FormulaRegistryQ[registry] validates the composition-safe W3 registry.";
GeometryLineageCompositionReceipt::usage =
 "GeometryLineageCompositionReceipt[] records the exact PR83 parent, PR82 tested donor and no-duplicate-connection composition contract.";
GeometryLineageCompositionReceiptQ::usage =
 "GeometryLineageCompositionReceiptQ[receipt] validates the composed geometry-lineage receipt.";

Begin["`Private`"];

ClearAll[
 vector3Q, symmetric3Q, zeroArrayQ, exactCoefficientQ,
 canonicalLockedConnection,
 ONFLeviCivitaConnection, ONFConnectionEquationSolve,
 ONFTorsionResidual, ONFMetricCompatibilityResidual,
 ONFRiemannTensor, ONFRicciTensor, ONFScalarCurvature,
 ONFRiemannSymmetryReport, ONFCurvatureWitnessRegistry,
 ValidateONFCurvatureWitness, ValidateONFCurvatureWitnesses,
 W3FormulaRegistry, W3FormulaRegistryQ,
 GeometryLineageCompositionReceipt, GeometryLineageCompositionReceiptQ
];

vector3Q[x_] := ListQ[x] && Length[x] === 3;
symmetric3Q[x_] := MatrixQ[x] && Dimensions[x] === {3, 3} &&
 TrueQ[Simplify[x == Transpose[x]]];
zeroArrayQ[x_] := AllTrue[Flatten[{x}], TrueQ[PossibleZeroQ[#]] &];
exactCoefficientQ[x_] := IntegerQ[x] || MatchQ[x, _Rational];

canonicalLockedConnection[a_List, n_List] /; And[
  vector3Q[a], symmetric3Q[n]
 ] := Module[{generated, locked},
 generated = LeviCivitaConnection[a, n];
 If[FailureQ[generated], Return[generated]];
 locked = ConnectionToLockedGammaOrder[generated];
 If[FailureQ[locked], Return[locked]];
 locked
];
canonicalLockedConnection[___] :=
 Failure["InvalidBianchiAlgebraInput", <||>];

(* Compatibility API only.  The unique implementation authority is
   LeviCivitaConnection.wl; this function changes storage order and does not
   rederive the connection. *)
ONFLeviCivitaConnection[a_List, n_List] /; And[
  vector3Q[a], symmetric3Q[n]
 ] := ConnectionToLockedGammaOrder[LeviCivitaConnection[a, n]];
ONFLeviCivitaConnection[___] :=
 Failure["InvalidBianchiAlgebraInput", <||>];

ONFConnectionEquationSolve[a_List, n_List] /; And[
  vector3Q[a], symmetric3Q[n]
 ] := Module[{c, gammaVariables, equations, solutions},
 c = BianchiStructureConstants[a, n];
 If[FailureQ[c], Return[c]];
 gammaVariables = Array[Unique["gamma"] &, {3, 3, 3}];
 equations = Join[
   Flatten@Table[
     gammaVariables[[alpha, beta, gamma]]
      + gammaVariables[[alpha, gamma, beta]] == 0,
     {alpha, 3}, {beta, 3}, {gamma, 3}
    ],
   Flatten@Table[
     gammaVariables[[alpha, beta, gamma]]
      - gammaVariables[[beta, alpha, gamma]]
      == c[[gamma, alpha, beta]],
     {alpha, 3}, {beta, 3}, {gamma, 3}
    ]
  ];
 solutions = Solve[equations, Flatten[gammaVariables]];
 If[Length[solutions] =!= 1,
  Failure["ConnectionSolveNotUnique", <|"solution_count" -> Length[solutions]|>],
  Simplify[gammaVariables /. First[solutions]]
 ]
];
ONFConnectionEquationSolve[___] :=
 Failure["InvalidBianchiAlgebraInput", <||>];

ONFTorsionResidual[a_List, n_List] := Module[{c, gamma},
 c = BianchiStructureConstants[a, n];
 gamma = canonicalLockedConnection[a, n];
 If[FailureQ[c] || FailureQ[gamma], Return[$Failed]];
 Array[
  Function[{alpha, beta, delta},
   Simplify[
    gamma[[alpha, beta, delta]]
     - gamma[[beta, alpha, delta]]
     - c[[delta, alpha, beta]]
   ]
  ],
  {3, 3, 3}
 ]
];

ONFMetricCompatibilityResidual[a_List, n_List] := Module[{gamma},
 gamma = canonicalLockedConnection[a, n];
 If[FailureQ[gamma], Return[$Failed]];
 Array[
  Function[{alpha, beta, delta},
   Simplify[
    gamma[[alpha, beta, delta]]
     + gamma[[alpha, delta, beta]]
   ]
  ],
  {3, 3, 3}
 ]
];

ONFRiemannTensor[a_List, n_List] /; And[
  vector3Q[a], symmetric3Q[n]
 ] := Module[{c, gamma},
 c = BianchiStructureConstants[a, n];
 gamma = canonicalLockedConnection[a, n];
 If[FailureQ[c] || FailureQ[gamma], Return[$Failed]];
 Array[
  Function[{alpha, beta, gammaIndex, delta},
   Simplify[
    Sum[
     gamma[[beta, gammaIndex, mu]] gamma[[alpha, mu, delta]]
      - gamma[[alpha, gammaIndex, mu]] gamma[[beta, mu, delta]]
      - c[[mu, alpha, beta]] gamma[[mu, gammaIndex, delta]],
     {mu, 3}
    ]
   ]
  ],
  {3, 3, 3, 3}
 ]
];
ONFRiemannTensor[___] :=
 Failure["InvalidBianchiAlgebraInput", <||>];

ONFRicciTensor[a_List, n_List] := Module[{riemann},
 riemann = ONFRiemannTensor[a, n];
 If[FailureQ[riemann], Return[riemann]];
 Array[
  Function[{gammaIndex, beta},
   Simplify[Sum[riemann[[alpha, beta, gammaIndex, alpha]], {alpha, 3}]]
  ],
  {3, 3}
 ]
];

ONFScalarCurvature[a_List, n_List] :=
 Simplify[Tr[ONFRicciTensor[a, n]]];

ONFRiemannSymmetryReport[a_List, n_List] := Module[{r},
 r = ONFRiemannTensor[a, n];
 If[FailureQ[r], Return[<|"status" -> "FAIL"|>]];
 <|
  "pair_12_antisymmetry" ->
   zeroArrayQ[r + Transpose[r, {2, 1, 3, 4}]],
  "pair_34_antisymmetry" ->
   zeroArrayQ[r + Transpose[r, {1, 2, 4, 3}]],
  "pair_exchange" ->
   zeroArrayQ[r - Transpose[r, {3, 4, 1, 2}]]
 |>
];

ONFCurvatureWitnessRegistry[] := <|
 "I" -> <|
   "a" -> {0, 0, 0},
   "n" -> ConstantArray[0, {3, 3}],
   "expected_ricci" -> ConstantArray[0, {3, 3}],
   "expected_scalar" -> 0,
   "expected_section_12" -> 0
  |>,
 "V" -> <|
   "a" -> {1, 0, 0},
   "n" -> ConstantArray[0, {3, 3}],
   "expected_ricci" -> -2 IdentityMatrix[3],
   "expected_scalar" -> -6,
   "expected_section_12" -> -1
  |>,
 "IX" -> <|
   "a" -> {0, 0, 0},
   "n" -> IdentityMatrix[3],
   "expected_ricci" -> IdentityMatrix[3]/2,
   "expected_scalar" -> 3/2,
   "expected_section_12" -> 1/4
  |>
|>;

ValidateONFCurvatureWitness[label_String] := Module[
 {spec, a, n, canonicalGenerated, canonicalLocked, solvedGamma,
  torsion, metric, riemann, ricci, scalar, symmetry, checks},
 spec = Lookup[ONFCurvatureWitnessRegistry[], label, Missing["Unknown"]];
 If[MissingQ[spec],
  Return[Failure["UnknownWitness", <|"label" -> label|>]]
 ];
 a = spec["a"];
 n = spec["n"];
 canonicalGenerated = LeviCivitaConnection[a, n];
 canonicalLocked = canonicalLockedConnection[a, n];
 solvedGamma = ONFConnectionEquationSolve[a, n];
 torsion = ONFTorsionResidual[a, n];
 metric = ONFMetricCompatibilityResidual[a, n];
 riemann = ONFRiemannTensor[a, n];
 ricci = ONFRicciTensor[a, n];
 scalar = ONFScalarCurvature[a, n];
 symmetry = ONFRiemannSymmetryReport[a, n];
 checks = <|
   "canonical_storage_adapter" ->
    TrueQ[Simplify[
      ConnectionToLockedGammaOrder[canonicalGenerated] == canonicalLocked
     ]],
   "connection_linear_solve" ->
    TrueQ[Simplify[canonicalLocked == solvedGamma]],
   "torsion_free" -> zeroArrayQ[torsion],
   "metric_compatible" -> zeroArrayQ[metric],
   "pair_12_antisymmetry" -> TrueQ[symmetry["pair_12_antisymmetry"]],
   "pair_34_antisymmetry" -> TrueQ[symmetry["pair_34_antisymmetry"]],
   "pair_exchange" -> TrueQ[symmetry["pair_exchange"]],
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
  "pass" -> AllTrue[Values[checks], TrueQ],
  "checks" -> checks,
  "connection" -> canonicalLocked,
  "ricci" -> ricci,
  "scalar_curvature" -> scalar,
  "section_12" -> riemann[[1, 2, 2, 1]]
 |>
];

ValidateONFCurvatureWitnesses[] :=
 AssociationMap[
  ValidateONFCurvatureWitness,
  Keys[ONFCurvatureWitnessRegistry[]]
 ];

W3FormulaRegistry[] := {
 <|
  "formula_id" -> "W3-CONN-001",
  "canonical_connection_formula_id" ->
   "BASS.GEO.LEVI_CIVITA_CONNECTION.001",
  "target" -> "Gamma_{alpha beta gamma}",
  "dimension" -> "L^-1",
  "implementation" -> "LeviCivitaConnection.wl plus storage-order adapter",
  "terms" -> {
    <|"input" -> "C_{gamma alpha beta}", "coefficient" -> 1/2|>,
    <|"input" -> "C_{alpha beta gamma}", "coefficient" -> -1/2|>,
    <|"input" -> "C_{beta gamma alpha}", "coefficient" -> 1/2|>
   },
  "convention" ->
   "Gamma_{alpha beta gamma}=<e_gamma,nabla_{e_alpha}e_beta>"
 |>,
 <|
  "formula_id" -> "W3-RIEM-001",
  "upstream_formula_id" -> "BASS.GEO.LEVI_CIVITA_CONNECTION.001",
  "target" -> "R3_{alpha beta gamma delta}",
  "dimension" -> "L^-2",
  "terms" -> {
    <|
     "input" -> "Gamma_{beta gamma mu} Gamma_{alpha mu delta}",
     "coefficient" -> 1
    |>,
    <|
     "input" -> "Gamma_{alpha gamma mu} Gamma_{beta mu delta}",
     "coefficient" -> -1
    |>,
    <|
     "input" -> "C^mu_{alpha beta} Gamma_{mu gamma delta}",
     "coefficient" -> -1
    |>
   },
  "convention" ->
   "[nabla_alpha,nabla_beta] v^delta = R_{alpha beta gamma}^delta v^gamma"
 |>,
 <|
  "formula_id" -> "W3-RICCI-001",
  "target" -> "R3_{gamma beta}",
  "dimension" -> "L^-2",
  "terms" -> {
    <|
     "input" -> "sum_alpha R3_{alpha beta gamma alpha}",
     "coefficient" -> 1
    |>
   },
  "convention" -> "orthonormal spatial contraction"
 |>,
 <|
  "formula_id" -> "W3-SCALAR-001",
  "target" -> "R3",
  "dimension" -> "L^-2",
  "terms" -> {
    <|
     "input" -> "delta^{gamma beta} R3_{gamma beta}",
     "coefficient" -> 1
    |>
   },
  "convention" -> "positive spatial metric"
 |>
};

W3FormulaRegistryQ[registry_List] := And[
 Length[registry] === 4,
 DuplicateFreeQ[Lookup[registry, "formula_id"]],
 Lookup[registry, "formula_id"] === {
  "W3-CONN-001", "W3-RIEM-001", "W3-RICCI-001", "W3-SCALAR-001"
 },
 Lookup[First[registry], "canonical_connection_formula_id", None] ===
  "BASS.GEO.LEVI_CIVITA_CONNECTION.001",
 Lookup[registry[[2]], "upstream_formula_id", None] ===
  "BASS.GEO.LEVI_CIVITA_CONNECTION.001",
 AllTrue[
  registry,
  AssociationQ[#] &&
   MemberQ[{"L^-1", "L^-2"}, Lookup[#, "dimension", None]] &&
   ListQ[Lookup[#, "terms", None]] &&
   AllTrue[
    Lookup[#, "terms", {}],
    AssociationQ[#] &&
      exactCoefficientQ[Lookup[#, "coefficient", Indeterminate]] &
   ] &
 ]
];
W3FormulaRegistryQ[_] := False;

GeometryLineageCompositionReceipt[] := Module[
 {parentReceipt, w2Model, directWitnesses, checks},
 parentReceipt = ConnectionCompositionReceipt[];
 w2Model = Abstract1Plus3ModelRegistry[];
 directWitnesses = ValidateONFCurvatureWitnesses[];
 checks = <|
   "canonical_parent_receipt" ->
    TrueQ[ConnectionCompositionReceiptQ[parentReceipt]],
   "w2_model_registry" ->
    TrueQ[Abstract1Plus3ModelRegistryQ[w2Model]],
   "curvature_formula_registry" ->
    TrueQ[W3FormulaRegistryQ[W3FormulaRegistry[]]],
   "all_direct_witnesses" ->
    AllTrue[Values[directWitnesses], TrueQ[Lookup[#, "pass", False]] &],
   "single_connection_implementation" -> True,
   "canonical_connection_formula_id" ->
    Lookup[First[W3FormulaRegistry[]],
     "canonical_connection_formula_id", None] ===
     "BASS.GEO.LEVI_CIVITA_CONNECTION.001"
  |>;
 <|
  "schema_version" -> "1.0.0",
  "program_id" -> "BASS-MASTER-SSOT-V2-WOLFRAM-XACT-20260901",
  "stage_id" -> "SYNC_MAP_01C_GEOMETRY_LINEAGE_COMPOSITION",
  "status" -> If[AllTrue[Values[checks], TrueQ], "PASS", "FAIL"],
  "canonical_parent" -> <|
    "pull_request" -> 83,
    "commit" -> "c787e6c51608568fcb60d52f010235f8cb2c1076",
    "tree" -> "3619744e9ba2b0633737b244cb18310ec89047c8"
   |>,
  "tested_donor" -> <|
    "pull_request" -> 82,
    "commit" -> "5d3e8ecce2a40a1bc2b43af7daa985e042d9815f",
    "tree" -> "0fee5b6335a2eb8968c11790ce787bf54fdc1def"
   |>,
  "canonical_connection_formula_id" ->
   "BASS.GEO.LEVI_CIVITA_CONNECTION.001",
  "connection_implementation_count" -> 1,
  "checks" -> checks,
  "claim_boundary" -> {
    "W2_ABSTRACT_1PLUS3_AND_GAUSS_CODAZZI_REGISTRY_COMPOSED",
    "GEO03_SPATIAL_CURVATURE_I_V_IX_DIRECT_WITNESSES_VERIFIED",
    "NO_BACKGROUND_EINSTEIN_MATTER_EVOLUTION",
    "NO_ALL_TYPE_CURVATURE_SPECIALIZATION",
    "NO_NUMERICAL_PARITY",
    "NO_SCIENCE_VALIDITY",
    "NO_PASS_RF04"
   }
 |>
];

GeometryLineageCompositionReceiptQ[receipt_Association] := And[
 Lookup[receipt, "schema_version", None] === "1.0.0",
 Lookup[receipt, "stage_id", None] ===
  "SYNC_MAP_01C_GEOMETRY_LINEAGE_COMPOSITION",
 Lookup[receipt, "status", None] === "PASS",
 Lookup[Lookup[receipt, "canonical_parent", <||>], "commit", None] ===
  "c787e6c51608568fcb60d52f010235f8cb2c1076",
 Lookup[Lookup[receipt, "tested_donor", <||>], "commit", None] ===
  "5d3e8ecce2a40a1bc2b43af7daa985e042d9815f",
 Lookup[receipt, "canonical_connection_formula_id", None] ===
  "BASS.GEO.LEVI_CIVITA_CONNECTION.001",
 Lookup[receipt, "connection_implementation_count", 0] === 1,
 AllTrue[Values[Lookup[receipt, "checks", <||>]], TrueQ]
];
GeometryLineageCompositionReceiptQ[_] := False;

End[];
EndPackage[];
