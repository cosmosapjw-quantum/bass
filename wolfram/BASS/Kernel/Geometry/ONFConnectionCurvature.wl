(* ::Package:: *)

BeginPackage["BASS`Geometry`"];

ONFLeviCivitaConnection::usage =
 "ONFLeviCivitaConnection[a,n] returns Gamma_{alpha beta gamma}=<e_gamma,nabla_{e_alpha}e_beta> for the locked Bianchi structure constants.";
ONFConnectionEquationSolve::usage =
 "ONFConnectionEquationSolve[a,n] independently solves torsion-free and metric-compatibility equations for Gamma_{alpha beta gamma}.";
ONFTorsionResidual::usage =
 "ONFTorsionResidual[a,n] returns Gamma_{alpha beta gamma}-Gamma_{beta alpha gamma}-C_{gamma alpha beta}.";
ONFMetricCompatibilityResidual::usage =
 "ONFMetricCompatibilityResidual[a,n] returns Gamma_{alpha beta gamma}+Gamma_{alpha gamma beta}.";
ONFRiemannTensor::usage =
 "ONFRiemannTensor[a,n] returns the all-lower homogeneous spatial Riemann tensor in the BASS convention.";
ONFRicciTensor::usage =
 "ONFRicciTensor[a,n] contracts ONFRiemannTensor as R_{gamma beta}=sum_alpha R_{alpha beta gamma alpha}.";
ONFScalarCurvature::usage =
 "ONFScalarCurvature[a,n] returns the orthonormal-frame scalar curvature.";
ONFRiemannSymmetryReport::usage =
 "ONFRiemannSymmetryReport[a,n] checks the Riemann pair symmetries exactly.";
ONFCurvatureWitnessRegistry::usage =
 "ONFCurvatureWitnessRegistry[] returns the exact I, V and IX witness data.";
ValidateONFCurvatureWitness::usage =
 "ValidateONFCurvatureWitness[label] validates one direct ONF witness.";
ValidateONFCurvatureWitnesses::usage =
 "ValidateONFCurvatureWitnesses[] validates all direct ONF witnesses.";
W3FormulaRegistry::usage =
 "W3FormulaRegistry[] returns the semantic connection and curvature formula registry.";
W3FormulaRegistryQ::usage =
 "W3FormulaRegistryQ[registry] validates the W3 semantic formula registry.";

Begin["`Private`"];

ClearAll[
 vector3Q, symmetric3Q, zeroArrayQ, exactCoefficientQ,
 ONFLeviCivitaConnection, ONFConnectionEquationSolve,
 ONFTorsionResidual, ONFMetricCompatibilityResidual,
 ONFRiemannTensor, ONFRicciTensor, ONFScalarCurvature,
 ONFRiemannSymmetryReport, ONFCurvatureWitnessRegistry,
 ValidateONFCurvatureWitness, ValidateONFCurvatureWitnesses,
 W3FormulaRegistry, W3FormulaRegistryQ
];

vector3Q[x_] := ListQ[x] && Length[x] === 3;
symmetric3Q[x_] := MatrixQ[x] && Dimensions[x] === {3, 3} &&
 TrueQ[Simplify[x == Transpose[x]]];
zeroArrayQ[x_] := AllTrue[Flatten[x], TrueQ[PossibleZeroQ[#]] &];
exactCoefficientQ[x_] := IntegerQ[x] || MatchQ[x, _Rational];

ONFLeviCivitaConnection[a_List, n_List] /;
  vector3Q[a] && symmetric3Q[n] := Module[{c},
 c = BianchiStructureConstants[a, n];
 If[FailureQ[c], Return[c]];
 Array[
  Function[{alpha, beta, gamma},
   Simplify[
    (c[[gamma, alpha, beta]]
      - c[[alpha, beta, gamma]]
      + c[[beta, gamma, alpha]])/2
   ]
  ],
  {3, 3, 3}
 ]
];
ONFLeviCivitaConnection[___] :=
 Failure["InvalidBianchiAlgebraInput", <||>];

ONFConnectionEquationSolve[a_List, n_List] /;
  vector3Q[a] && symmetric3Q[n] := Module[
 {c, gammaVariables, equations, solutions},
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
 gamma = ONFLeviCivitaConnection[a, n];
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
 gamma = ONFLeviCivitaConnection[a, n];
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

ONFRiemannTensor[a_List, n_List] /;
  vector3Q[a] && symmetric3Q[n] := Module[{c, gamma},
 c = BianchiStructureConstants[a, n];
 gamma = ONFLeviCivitaConnection[a, n];
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
 {spec, a, n, gamma, solvedGamma, torsion, metric, riemann, ricci,
  scalar, symmetry, checks},
 spec = Lookup[ONFCurvatureWitnessRegistry[], label, Missing["Unknown"]];
 If[MissingQ[spec],
  Return[Failure["UnknownWitness", <|"label" -> label|>]]
 ];
 a = spec["a"];
 n = spec["n"];
 gamma = ONFLeviCivitaConnection[a, n];
 solvedGamma = ONFConnectionEquationSolve[a, n];
 torsion = ONFTorsionResidual[a, n];
 metric = ONFMetricCompatibilityResidual[a, n];
 riemann = ONFRiemannTensor[a, n];
 ricci = ONFRicciTensor[a, n];
 scalar = ONFScalarCurvature[a, n];
 symmetry = ONFRiemannSymmetryReport[a, n];
 checks = <|
   "connection_linear_solve" ->
    TrueQ[Simplify[gamma == solvedGamma]],
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
  "connection" -> gamma,
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
  "target" -> "Gamma_{alpha beta gamma}",
  "dimension" -> "L^-1",
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

End[];
EndPackage[];
