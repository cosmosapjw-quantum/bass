(* ::Package:: *)

BeginPackage["BASSNumBoostCertificate`"];

SpinBoostCoefficient::usage =
  "SpinBoostCoefficient[s, ell, m] returns the exact d=1 nearest-neighbour boost coefficient.";
D1FixedMGenerator::usage =
  "D1FixedMGenerator[s,m,ellMax] returns the exact fixed-m d=1 Galerkin generator.";
FiniteBufferTheoremData::usage =
  "FiniteBufferTheoremData[s,m,ellTarget,ellWork] returns exact leakage/contamination orders and the shortest-path coefficient.";
BoundaryCouplingOperator::usage =
  "BoundaryCouplingOperator[s,m,ellWork] returns Q_W G P_W embedded through ellWork+1.";
StateBoundaryResidual::usage =
  "StateBoundaryResidual[s,m,ellWork,yWork] returns Q_W G P_W yWork.";
StateBoundaryResidualNormSquared::usage =
  "StateBoundaryResidualNormSquared[...] returns the exact squared Euclidean norm.";
CovarianceBoundaryResidual::usage =
  "CovarianceBoundaryResidual[s,m,ellWork,cWork] returns B_W C_W + C_W B_W^dagger.";
CovarianceBoundaryResidualNormSquared::usage =
  "CovarianceBoundaryResidualNormSquared[...] returns the exact Frobenius norm squared.";
CovarianceBoundaryResidualClosedForm::usage =
  "CovarianceBoundaryResidualClosedForm[...] evaluates the complete top-shell-row formula.";
FrobeniusNormSquared::usage =
  "FrobeniusNormSquared[m] returns Tr[m^dagger m].";
CovarianceSourceTailData::usage =
  "CovarianceSourceTailData[c,p] returns the full covariance-tail norm and its cross-tail decomposition.";
BipoSHTransformData::usage =
  "BipoSHTransformData[l1,l2] returns the ordered-block Clebsch-Gordan transform.";
BipoSHUnitarityChecks::usage =
  "BipoSHUnitarityChecks[l1,l2] checks both unitarity products exactly.";
BipolarPowerErrorBound::usage =
  "BipolarPowerErrorBound[kappaApprox,epsilon] returns (2 Sqrt[kappaApprox]+epsilon) epsilon.";
GaussianRelativeLikelihoodBounds::usage =
  "GaussianRelativeLikelihoodBounds[rho,n,chi2Approx,relativeFrobSquared] returns logdet, quadratic, likelihood and KL bounds for 0<=rho<1.";
GaussianLikelihoodBoundsFromFrobenius::usage =
  "GaussianLikelihoodBoundsFromFrobenius[epsilonF,lambdaMinApprox,n,chi2Approx] uses rho<=epsilonF/lambdaMinApprox.";
ProcessedCovarianceFrobeniusBound::usage =
  "ProcessedCovarianceFrobeniusBound[epsilonF,operatorGain] returns operatorGain^2 epsilonF.";
RunExactSelfChecks::usage =
  "RunExactSelfChecks[] executes 17 exact or high-precision fixture checks.";

Begin["`Private`"];

ClearAll[SpinBoostCoefficient];
SpinBoostCoefficient[s_Integer, ell_Integer, m_Integer] :=
  If[
    ell < Max[Abs[s], Abs[m]],
    0,
    Sqrt[((ell^2 - m^2) (ell^2 - s^2))/(4 ell^2 - 1)]
  ];

ClearAll[D1FixedMGenerator];
D1FixedMGenerator::range =
  "ellMax=`1` is below ellMin=Max[Abs[s],Abs[m]]=`2`.";
D1FixedMGenerator[s_Integer, m_Integer, ellMax_Integer] := Module[
  {ellMin = Max[Abs[s], Abs[m]], ells, n, rules = {}},
  If[ellMax < ellMin,
    Message[D1FixedMGenerator::range, ellMax, ellMin];
    Return[$Failed]
  ];
  ells = Range[ellMin, ellMax];
  n = Length[ells];
  Do[
    If[i < n,
      AppendTo[rules, {i + 1, i} -> SpinBoostCoefficient[s, ells[[i]] + 1, m]]
    ];
    If[i > 1,
      AppendTo[rules, {i - 1, i} -> -SpinBoostCoefficient[s, ells[[i]], m]]
    ],
    {i, n}
  ];
  Normal @ SparseArray[rules, {n, n}]
];

ClearAll[FiniteBufferTheoremData];
FiniteBufferTheoremData::range =
  "Require ellWork>=ellTarget>=Max[Abs[s],Abs[m]].";
FiniteBufferTheoremData[
  s_Integer, m_Integer, ellTarget_Integer, ellWork_Integer
] := Module[{ellMin, order, product},
  ellMin = Max[Abs[s], Abs[m]];
  If[ellWork < ellTarget || ellTarget < ellMin,
    Message[FiniteBufferTheoremData::range];
    Return[$Failed]
  ];
  order = ellWork - ellTarget + 1;
  product = Product[
    SpinBoostCoefficient[s, ell, m],
    {ell, ellTarget + 1, ellWork + 1}
  ];
  <|
    "BufferShells" -> (ellWork - ellTarget),
    "FirstFullStateLeakageOrder" -> order,
    "FirstRetainedContaminationOrder" -> 2 order,
    "ShortestPathCoefficient" -> product,
    "ShortestPathCoefficientSquared" -> FullSimplify[product^2]
  |>
];

ClearAll[BoundaryCouplingOperator];
BoundaryCouplingOperator::range =
  "ellWork=`1` is below ellMin=Max[Abs[s],Abs[m]]=`2`.";
BoundaryCouplingOperator[
  s_Integer, m_Integer, ellWork_Integer
] := Module[{ellMin, g, n, p, q},
  ellMin = Max[Abs[s], Abs[m]];
  If[ellWork < ellMin,
    Message[BoundaryCouplingOperator::range, ellWork, ellMin];
    Return[$Failed]
  ];
  g = D1FixedMGenerator[s, m, ellWork + 1];
  n = Length[g];
  p = DiagonalMatrix[Join[ConstantArray[1, n - 1], {0}]];
  q = IdentityMatrix[n] - p;
  q . g . p
];

ClearAll[StateBoundaryResidual];
StateBoundaryResidual::dim =
  "yWork has length `1`; expected `2` for s=`3`, m=`4`, ellWork=`5`.";
StateBoundaryResidual[
  s_Integer, m_Integer, ellWork_Integer, yWork_List
] := Module[{ellMin, expected, b, yEmbedded},
  ellMin = Max[Abs[s], Abs[m]];
  expected = ellWork - ellMin + 1;
  If[Length[yWork] =!= expected,
    Message[StateBoundaryResidual::dim, Length[yWork], expected, s, m, ellWork];
    Return[$Failed]
  ];
  b = BoundaryCouplingOperator[s, m, ellWork];
  yEmbedded = Join[yWork, {0}];
  Expand[b . yEmbedded]
];

ClearAll[FrobeniusNormSquared];
FrobeniusNormSquared[m_?MatrixQ] :=
  Expand[Tr[ConjugateTranspose[m] . m]];

ClearAll[StateBoundaryResidualNormSquared];
StateBoundaryResidualNormSquared[
  s_Integer, m_Integer, ellWork_Integer, yWork_List
] := Module[{residual = StateBoundaryResidual[s, m, ellWork, yWork]},
  If[residual === $Failed, Return[$Failed]];
  Expand[Conjugate[residual] . residual]
];

ClearAll[CovarianceBoundaryResidual];
CovarianceBoundaryResidual::dim =
  "cWork must be a square matrix of dimension `1` for s=`2`, m=`3`, ellWork=`4`.";
CovarianceBoundaryResidual[
  s_Integer, m_Integer, ellWork_Integer, cWork_?MatrixQ
] := Module[{ellMin, expected, b, cEmbedded},
  ellMin = Max[Abs[s], Abs[m]];
  expected = ellWork - ellMin + 1;
  If[Dimensions[cWork] =!= {expected, expected},
    Message[CovarianceBoundaryResidual::dim, expected, s, m, ellWork];
    Return[$Failed]
  ];
  b = BoundaryCouplingOperator[s, m, ellWork];
  cEmbedded = ArrayPad[cWork, {{0, 1}, {0, 1}}];
  Expand[b . cEmbedded + cEmbedded . ConjugateTranspose[b]]
];

ClearAll[CovarianceBoundaryResidualNormSquared];
CovarianceBoundaryResidualNormSquared[
  s_Integer, m_Integer, ellWork_Integer, cWork_?MatrixQ
] := Module[{residual = CovarianceBoundaryResidual[s, m, ellWork, cWork]},
  If[residual === $Failed, Return[$Failed]];
  FrobeniusNormSquared[residual]
];

ClearAll[CovarianceBoundaryResidualClosedForm];
CovarianceBoundaryResidualClosedForm[
  s_Integer, m_Integer, ellWork_Integer, cWork_?MatrixQ
] := Module[{b, row},
  b = SpinBoostCoefficient[s, ellWork + 1, m];
  row = Last[cWork];
  Expand[2 Conjugate[b] b (Conjugate[row] . row)]
];

ClearAll[CovarianceSourceTailData];
CovarianceSourceTailData::dim =
  "c and p must be square matrices of the same dimension.";
CovarianceSourceTailData[c_?MatrixQ, p_?MatrixQ] := Module[
  {n, q, tail, cross, omitted},
  If[
    Dimensions[c] =!= Dimensions[p] ||
    Dimensions[c][[1]] =!= Dimensions[c][[2]],
    Message[CovarianceSourceTailData::dim];
    Return[$Failed]
  ];
  n = Length[c];
  q = IdentityMatrix[n] - p;
  tail = Expand[c - p . c . p];
  cross = FrobeniusNormSquared[q . c . p];
  omitted = FrobeniusNormSquared[q . c . q];
  <|
    "FullTailNormSquared" -> FrobeniusNormSquared[tail],
    "CrossTailNormSquared" -> cross,
    "OmittedBlockNormSquared" -> omitted,
    "HermitianDecompositionRHS" -> Expand[2 cross + omitted]
  |>
];

ClearAll[BipoSHTransformData];
BipoSHTransformData[l1_Integer?NonNegative, l2_Integer?NonNegative] := Module[
  {productBasis, coupledBasis, transform},
  productBasis = Flatten[
    Table[{m1, m2}, {m1, -l1, l1}, {m2, -l2, l2}],
    1
  ];
  coupledBasis = Flatten[
    Table[{ellB, mB}, {ellB, Abs[l1 - l2], l1 + l2}, {mB, -ellB, ellB}],
    1
  ];
  transform = Table[
    With[
      {
        ellB = row[[1]], mB = row[[2]],
        m1 = col[[1]], m2 = col[[2]]
      },
      If[
        m1 - m2 === mB,
        (-1)^m2 ClebschGordan[{l1, m1}, {l2, -m2}, {ellB, mB}],
        0
      ]
    ],
    {row, coupledBasis},
    {col, productBasis}
  ];
  <|
    "Matrix" -> transform,
    "ProductBasis" -> productBasis,
    "CoupledBasis" -> coupledBasis
  |>
];

ClearAll[BipoSHUnitarityChecks];
BipoSHUnitarityChecks[l1_Integer?NonNegative, l2_Integer?NonNegative] := Module[
  {data, u, left, right},
  data = BipoSHTransformData[l1, l2];
  u = data["Matrix"];
  left = RootReduce[u . ConjugateTranspose[u] - IdentityMatrix[Length[u]]];
  right = RootReduce[
    ConjugateTranspose[u] . u - IdentityMatrix[Length[First[u]]]
  ];
  <|
    "LeftUnitary" -> And @@ Flatten[Map[PossibleZeroQ, left, {2}]],
    "RightUnitary" -> And @@ Flatten[Map[PossibleZeroQ, right, {2}]]
  |>
];

ClearAll[BipolarPowerErrorBound];
BipolarPowerErrorBound[kappaApprox_, epsilon_] :=
  Expand[(2 Sqrt[kappaApprox] + epsilon) epsilon];

ClearAll[GaussianRelativeLikelihoodBounds];
GaussianRelativeLikelihoodBounds::domain =
  "Require 0<=rho<1, positive integer n, chi2Approx>=0 and relativeFrobSquared>=0.";
GaussianRelativeLikelihoodBounds[
  rho_, n_Integer?Positive, chi2Approx_, relativeFrobSquared_
] := Module[{logDet, quadratic, klSpectral, klFrobenius},
  If[
    ! TrueQ[0 <= rho < 1] ||
    ! TrueQ[chi2Approx >= 0] ||
    ! TrueQ[relativeFrobSquared >= 0],
    Message[GaussianRelativeLikelihoodBounds::domain];
    Return[$Failed]
  ];
  logDet = -n Log[1 - rho];
  quadratic = rho chi2Approx/(1 - rho);
  klSpectral = n (-rho - Log[1 - rho])/2;
  klFrobenius = relativeFrobSquared/(4 (1 - rho));
  <|
    "LogDetAbsBound" -> logDet,
    "QuadraticFormAbsBound" -> quadratic,
    "Minus2LogLikelihoodAbsBound" -> Expand[logDet + quadratic],
    "LogLikelihoodAbsBound" -> Expand[(logDet + quadratic)/2],
    "KLSpectralBound" -> klSpectral,
    "KLFrobeniusBound" -> klFrobenius
  |>
];

ClearAll[GaussianLikelihoodBoundsFromFrobenius];
GaussianLikelihoodBoundsFromFrobenius::domain =
  "Require epsilonF>=0 and lambdaMinApprox>0.";
GaussianLikelihoodBoundsFromFrobenius[
  epsilonF_, lambdaMinApprox_, n_Integer?Positive, chi2Approx_
] := Module[{rho},
  If[
    ! TrueQ[epsilonF >= 0] || ! TrueQ[lambdaMinApprox > 0],
    Message[GaussianLikelihoodBoundsFromFrobenius::domain];
    Return[$Failed]
  ];
  rho = epsilonF/lambdaMinApprox;
  If[! TrueQ[rho < 1],
    Return[<|
      "SPDGuaranteed" -> False,
      "RelativeSpectralUpperBound" -> rho,
      "Reason" -> "epsilonF/lambdaMinApprox must be below one"
    |>]
  ];
  Join[
    <|
      "SPDGuaranteed" -> True,
      "RelativeSpectralUpperBound" -> rho,
      "RelativeFrobeniusSquaredUpperBound" -> rho^2
    |>,
    GaussianRelativeLikelihoodBounds[rho, n, chi2Approx, rho^2]
  ]
];

ClearAll[ProcessedCovarianceFrobeniusBound];
ProcessedCovarianceFrobeniusBound[epsilonF_, operatorGain_] :=
  Expand[operatorGain^2 epsilonF];

ClearAll[RunExactSelfChecks];
RunExactSelfChecks[] := Module[
  {
    w1, w2, w3, w4, w5, c0, c1, c2, c3, c4,
    g, pT, pW, qW, gW, powersG, powersGW, expectedDefect,
    c, bOp, rCov, covLHS, covRHS, topRowRHS,
    cSource, sourceTail, sourceCrossRHS,
    bipoData, u, vec, gPlus, gMinus, g0, cDiag, comm,
    cTilde, cExact, x, relativeA, rho, nDim,
    logDetError, logDetBound, quadError, quadBound,
    kl, klSpectral, klFrob, checks
  },

  g = {
    {0, -w1, 0, 0, 0, 0},
    {w1, 0, -w2, 0, 0, 0},
    {0, w2, 0, -w3, 0, 0},
    {0, 0, w3, 0, -w4, 0},
    {0, 0, 0, w4, 0, -w5},
    {0, 0, 0, 0, w5, 0}
  };
  pT = DiagonalMatrix[{1, 1, 1, 0, 0, 0}];
  pW = DiagonalMatrix[{1, 1, 1, 1, 1, 0}];
  qW = IdentityMatrix[6] - pW;
  gW = pW . g . pW;
  powersG = NestList[Expand[g . #] &, IdentityMatrix[6], 6];
  powersGW = NestList[Expand[gW . #] &, IdentityMatrix[6], 6];
  expectedDefect = -(w3 w4 w5)^2
    (Normal @ SparseArray[{{3, 3} -> 1}, {6, 6}]);

  c = {
    {2, 1, 0, 1, 0, 0},
    {1, 3, 1, 0, 1, 0},
    {0, 1, 4, 1, 0, 0},
    {1, 0, 1, 5, 1, 0},
    {0, 1, 0, 1, 6, 0},
    {0, 0, 0, 0, 0, 0}
  };
  bOp = qW . g . pW;
  rCov = Expand[bOp . c + c . Transpose[bOp]];
  covLHS = Expand[Tr[Transpose[rCov] . rCov]];
  covRHS = Expand[2 Tr[Transpose[bOp] . bOp . MatrixPower[c, 2]]];
  topRowRHS = Expand[2 w5^2 Total[c[[5, All]]^2]];

  cSource = {
    {2, 1, 0, 1, 0, 2},
    {1, 3, 1, 0, 1, 0},
    {0, 1, 4, 1, 0, 1},
    {1, 0, 1, 5, 1, 0},
    {0, 1, 0, 1, 6, 1},
    {2, 0, 1, 0, 1, 7}
  };
  sourceTail = Expand[cSource - pW . cSource . pW];
  sourceCrossRHS = Expand[
    2 FrobeniusNormSquared[qW . cSource . pW] +
    FrobeniusNormSquared[qW . cSource . qW]
  ];

  bipoData = BipoSHTransformData[1, 1];
  u = bipoData["Matrix"];
  vec = Range[Length[First[u]]];

  gPlus = D1FixedMGenerator[2, 1, 7];
  gMinus = D1FixedMGenerator[-2, 1, 7];
  g0 = D1FixedMGenerator[0, 0, 4];
  cDiag = DiagonalMatrix[{c0, c1, c2, c3, c4}];
  comm = Expand[g0 . cDiag - cDiag . g0];

  cTilde = DiagonalMatrix[{2, 3, 5}];
  relativeA = DiagonalMatrix[{1/5, -1/4, 1/10}];
  cExact = DiagonalMatrix[{12/5, 9/4, 11/2}];
  x = {1, 2, -1};
  rho = 1/4;
  nDim = 3;
  logDetError = FullSimplify[Abs[Log[Det[cExact]] - Log[Det[cTilde]]]];
  logDetBound = FullSimplify[-nDim Log[1 - rho]];
  quadError = FullSimplify[Abs[x . (Inverse[cExact] - Inverse[cTilde]) . x]];
  quadBound = FullSimplify[rho x . Inverse[cTilde] . x/(1 - rho)];
  kl = FullSimplify[(
    Tr[Inverse[cTilde] . cExact] - nDim -
    Log[Det[Inverse[cTilde] . cExact]]
  )/2];
  klSpectral = FullSimplify[nDim (-rho - Log[1 - rho])/2];
  klFrob = FullSimplify[Tr[relativeA . relativeA]/(4 (1 - rho))];

  checks = <|
    "FiniteBufferRetainedOrders" -> And @@ Table[
      Expand[pT . powersG[[k + 1]] . pT - pT . powersGW[[k + 1]] . pT] ===
        ConstantArray[0, {6, 6}],
      {k, 0, 5}
    ],
    "FiniteBufferLeakageOrders" -> And @@ Table[
      Expand[qW . powersG[[k + 1]] . pT] === ConstantArray[0, {6, 6}],
      {k, 0, 2}
    ],
    "FiniteBufferFirstRankOneDefect" ->
      Expand[pT . (powersG[[7]] - powersGW[[7]]) . pT - expectedDefect] ===
        ConstantArray[0, {6, 6}],
    "CovarianceResidualTraceIdentity" -> Expand[covLHS - covRHS] === 0,
    "CovarianceResidualTopRowIdentity" -> Expand[covLHS - topRowRHS] === 0,
    "CovarianceSourceCrossTailIdentity" ->
      Expand[FrobeniusNormSquared[sourceTail] - sourceCrossRHS] === 0,
    "BipoSHLeftUnitarity" -> And @@ Flatten[Map[
      PossibleZeroQ,
      RootReduce[u . ConjugateTranspose[u] - IdentityMatrix[Length[u]]],
      {2}
    ]],
    "BipoSHRightUnitarity" -> And @@ Flatten[Map[
      PossibleZeroQ,
      RootReduce[ConjugateTranspose[u] . u - IdentityMatrix[Length[First[u]]]],
      {2}
    ]],
    "BipoSHParseval" -> PossibleZeroQ @ RootReduce[
      Conjugate[u . vec] . (u . vec) - vec . vec
    ],
    "SpinPlusMinusTwoGeneratorEquality" -> gPlus === gMinus,
    "SpinTwoFiniteBlockSkew" ->
      RootReduce[gPlus + Transpose[gPlus]] === ConstantArray[0, Dimensions[gPlus]],
    "AdjacentEllCovarianceResponse" -> PossibleZeroQ @ RootReduce[
      comm[[4, 3]] - SpinBoostCoefficient[0, 3, 0] (c2 - c3)
    ],
    "GaussianLogDetBoundFixture" -> TrueQ[N[logDetError, 80] <= N[logDetBound, 80]],
    "GaussianQuadraticBoundFixture" -> TrueQ[N[quadError, 80] <= N[quadBound, 80]],
    "GaussianKLNonnegativeFixture" -> TrueQ[N[kl, 80] >= 0],
    "GaussianKLSpectralBoundFixture" -> TrueQ[N[kl, 80] <= N[klSpectral, 80]],
    "GaussianKLFrobeniusBoundFixture" -> TrueQ[N[kl, 80] <= N[klFrob, 80]]
  |>;

  <|
    "WolframVersion" -> $Version,
    "Checks" -> checks,
    "Passed" -> Count[Values[checks], True],
    "Total" -> Length[checks],
    "AllPassed" -> And @@ Values[checks],
    "FixtureValues" -> <|
      "CovarianceResidualNormSquared" -> covLHS,
      "LikelihoodLogDetError" -> logDetError,
      "LikelihoodQuadraticError" -> quadError,
      "LikelihoodKL" -> kl
    |>
  |>
];

End[];
EndPackage[];
