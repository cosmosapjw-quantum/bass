(* ::Package:: *)

BeginPackage["BASSNumBoostLikelihoodHardening`"];

FrobeniusNormSquared::usage =
  "FrobeniusNormSquared[m] returns Tr[m^dagger m].";
ExactHermitianMatrixQ::usage =
  "ExactHermitianMatrixQ[m] tests exact Hermiticity.";
ExactOrthogonalProjectorQ::usage =
  "ExactOrthogonalProjectorQ[p] tests p^dagger=p and p.p=p.";
HardenedCovarianceSourceTailData::usage =
  "HardenedCovarianceSourceTailData[c,p] returns the Hermitian covariance source-tail identity and fails closed unless c is Hermitian and p is an orthogonal projector.";
HardenedCovarianceBoundaryResidualData::usage =
  "HardenedCovarianceBoundaryResidualData[b,c,p] checks the exact covariance boundary identity and fails closed unless its Hermitian/support assumptions hold.";
GaussianMeanCovarianceKLData::usage =
  "GaussianMeanCovarianceKLData[cExact,cApprox,muExact,muApprox] returns the exact Gaussian KL divergence and its relative-covariance plus mean decomposition.";
GaussianMeanCovarianceKLBounds::usage =
  "GaussianMeanCovarianceKLBounds[rho,n,relativeFrobSquared,meanRelativeNormSquared] returns spectral and Frobenius KL upper bounds for 0<=rho<1.";
GaussianFixedDataMinus2LogLikelihoodBound::usage =
  "GaussianFixedDataMinus2LogLikelihoodBound[rho,n,zNorm,mNorm] returns a conservative absolute bound for the change in -2 log likelihood.";
CommonSupportGuard::usage =
  "CommonSupportGuard[pExact,pApprox,meanDelta] requires identical orthogonal support projectors and meanDelta in their common range.";
CompressGaussianLikelihoodData::usage =
  "CompressGaussianLikelihoodData[cExact,cApprox,muExact,muApprox,x,r] compresses to an isometric retained subspace and fails closed unless both compressed covariances are positive definite.";
RunLikelihoodHardeningSelfChecks::usage =
  "RunLikelihoodHardeningSelfChecks[] runs 15 exact/high-precision checks.";

Begin["`Private`"];

ClearAll[exactZeroScalarQ, exactZeroMatrixQ];
exactZeroScalarQ[x_] := TrueQ[PossibleZeroQ[RootReduce[x]]];
exactZeroMatrixQ[m_?MatrixQ] :=
  And @@ Flatten[Map[exactZeroScalarQ, m, {2}]];

ClearAll[FrobeniusNormSquared];
FrobeniusNormSquared[m_?MatrixQ] :=
  Expand[Tr[ConjugateTranspose[m].m]];

ClearAll[ExactHermitianMatrixQ];
ExactHermitianMatrixQ[m_?MatrixQ] :=
  Length[Dimensions[m]] === 2 &&
  Dimensions[m][[1]] === Dimensions[m][[2]] &&
  exactZeroMatrixQ[m - ConjugateTranspose[m]];

ClearAll[ExactOrthogonalProjectorQ];
ExactOrthogonalProjectorQ[p_?MatrixQ] :=
  Length[Dimensions[p]] === 2 &&
  Dimensions[p][[1]] === Dimensions[p][[2]] &&
  exactZeroMatrixQ[p - ConjugateTranspose[p]] &&
  exactZeroMatrixQ[p.p - p];

ClearAll[HardenedCovarianceSourceTailData];
HardenedCovarianceSourceTailData::dim =
  "c and p must be square matrices of the same dimension.";
HardenedCovarianceSourceTailData::cov =
  "c must be exactly Hermitian.";
HardenedCovarianceSourceTailData::proj =
  "p must be an exact orthogonal projector.";
HardenedCovarianceSourceTailData[c_?MatrixQ, p_?MatrixQ] := Module[
  {n, q, tail, cross, omitted, lhs, rhs},
  If[
    Dimensions[c] =!= Dimensions[p] ||
    Length[Dimensions[c]] =!= 2 ||
    Dimensions[c][[1]] =!= Dimensions[c][[2]],
    Message[HardenedCovarianceSourceTailData::dim];
    Return[$Failed]
  ];
  If[!ExactHermitianMatrixQ[c],
    Message[HardenedCovarianceSourceTailData::cov];
    Return[$Failed]
  ];
  If[!ExactOrthogonalProjectorQ[p],
    Message[HardenedCovarianceSourceTailData::proj];
    Return[$Failed]
  ];
  n = Length[c];
  q = IdentityMatrix[n] - p;
  tail = Expand[c - p.c.p];
  cross = FrobeniusNormSquared[q.c.p];
  omitted = FrobeniusNormSquared[q.c.q];
  lhs = FrobeniusNormSquared[tail];
  rhs = Expand[2 cross + omitted];
  <|
    "FullTailNormSquared" -> lhs,
    "CrossTailNormSquared" -> cross,
    "OmittedBlockNormSquared" -> omitted,
    "HermitianDecompositionRHS" -> rhs,
    "IdentityResidual" -> Expand[lhs - rhs]
  |>
];

ClearAll[HardenedCovarianceBoundaryResidualData];
HardenedCovarianceBoundaryResidualData::dim =
  "b, c and p must be square matrices of the same dimension.";
HardenedCovarianceBoundaryResidualData::cov =
  "c must be exactly Hermitian.";
HardenedCovarianceBoundaryResidualData::proj =
  "p must be an exact orthogonal projector.";
HardenedCovarianceBoundaryResidualData::support =
  "Require c=p.c.p and b=(1-p).b.p.";
HardenedCovarianceBoundaryResidualData[
  b_?MatrixQ, c_?MatrixQ, p_?MatrixQ
] := Module[{n, q, residual, direct, closed},
  If[
    Dimensions[b] =!= Dimensions[c] ||
    Dimensions[c] =!= Dimensions[p] ||
    Dimensions[c][[1]] =!= Dimensions[c][[2]],
    Message[HardenedCovarianceBoundaryResidualData::dim];
    Return[$Failed]
  ];
  If[!ExactHermitianMatrixQ[c],
    Message[HardenedCovarianceBoundaryResidualData::cov];
    Return[$Failed]
  ];
  If[!ExactOrthogonalProjectorQ[p],
    Message[HardenedCovarianceBoundaryResidualData::proj];
    Return[$Failed]
  ];
  n = Length[c];
  q = IdentityMatrix[n] - p;
  If[
    !exactZeroMatrixQ[c - p.c.p] ||
    !exactZeroMatrixQ[b - q.b.p],
    Message[HardenedCovarianceBoundaryResidualData::support];
    Return[$Failed]
  ];
  residual = Expand[b.c + c.ConjugateTranspose[b]];
  direct = FrobeniusNormSquared[residual];
  closed = Expand[
    2 Tr[ConjugateTranspose[b].b.MatrixPower[c, 2]]
  ];
  <|
    "ResidualMatrix" -> residual,
    "DirectNormSquared" -> direct,
    "HermitianClosedForm" -> closed,
    "IdentityResidual" -> Expand[direct - closed]
  |>
];

ClearAll[GaussianMeanCovarianceKLData];
GaussianMeanCovarianceKLData::dim =
  "Covariances must be square matrices of equal dimension and means must match.";
GaussianMeanCovarianceKLData::spd =
  "Both covariance matrices must be Hermitian positive definite.";
GaussianMeanCovarianceKLData[
  cExact_?MatrixQ, cApprox_?MatrixQ, muExact_List, muApprox_List
] := Module[{n, invSqrt, a, m, direct, decomposed},
  If[
    Dimensions[cExact] =!= Dimensions[cApprox] ||
    Dimensions[cExact][[1]] =!= Dimensions[cExact][[2]] ||
    Length[muExact] =!= Length[cExact] ||
    Length[muApprox] =!= Length[cExact],
    Message[GaussianMeanCovarianceKLData::dim];
    Return[$Failed]
  ];
  If[
    !TrueQ[PositiveDefiniteMatrixQ[cExact]] ||
    !TrueQ[PositiveDefiniteMatrixQ[cApprox]],
    Message[GaussianMeanCovarianceKLData::spd];
    Return[$Failed]
  ];
  n = Length[cExact];
  invSqrt = MatrixPower[cApprox, -1/2];
  a = RootReduce[invSqrt.(cExact - cApprox).invSqrt];
  m = RootReduce[invSqrt.(muExact - muApprox)];
  direct = FullSimplify[
    (
      Tr[Inverse[cApprox].cExact] +
      (muApprox - muExact).Inverse[cApprox].(muApprox - muExact) -
      n + Log[Det[cApprox]/Det[cExact]]
    )/2
  ];
  decomposed = FullSimplify[
    (
      Tr[a] - Log[Det[IdentityMatrix[n] + a]] +
      Conjugate[m].m
    )/2
  ];
  <|
    "RelativeCovariancePerturbation" -> a,
    "RelativeMeanShift" -> m,
    "RelativeMeanNormSquared" -> FullSimplify[Conjugate[m].m],
    "DirectKL" -> direct,
    "DecomposedKL" -> decomposed,
    "DecompositionResidual" -> FullSimplify[direct - decomposed]
  |>
];

ClearAll[GaussianMeanCovarianceKLBounds];
GaussianMeanCovarianceKLBounds::domain =
  "Require 0<=rho<1, n positive, and nonnegative squared norms.";
GaussianMeanCovarianceKLBounds[
  rho_, n_Integer?Positive, relativeFrobSquared_, meanRelativeNormSquared_
] := Module[{spectral, frobenius},
  If[
    !TrueQ[0 <= rho < 1] ||
    !TrueQ[relativeFrobSquared >= 0] ||
    !TrueQ[meanRelativeNormSquared >= 0],
    Message[GaussianMeanCovarianceKLBounds::domain];
    Return[$Failed]
  ];
  spectral = FullSimplify[
    n (-rho - Log[1 - rho])/2 + meanRelativeNormSquared/2
  ];
  frobenius = FullSimplify[
    relativeFrobSquared/(4 (1 - rho)) +
    meanRelativeNormSquared/2
  ];
  <|
    "SpectralKLUpperBound" -> spectral,
    "FrobeniusKLUpperBound" -> frobenius
  |>
];

ClearAll[GaussianFixedDataMinus2LogLikelihoodBound];
GaussianFixedDataMinus2LogLikelihoodBound::domain =
  "Require 0<=rho<1 and nonnegative zNorm and mNorm.";
GaussianFixedDataMinus2LogLikelihoodBound[
  rho_, n_Integer?Positive, zNorm_, mNorm_
] := Module[{},
  If[
    !TrueQ[0 <= rho < 1] ||
    !TrueQ[zNorm >= 0] ||
    !TrueQ[mNorm >= 0],
    Message[GaussianFixedDataMinus2LogLikelihoodBound::domain];
    Return[$Failed]
  ];
  FullSimplify[
    -n Log[1 - rho] +
    rho/(1 - rho) (zNorm + mNorm)^2 +
    2 zNorm mNorm + mNorm^2
  ]
];

ClearAll[CommonSupportGuard];
CommonSupportGuard[
  pExact_?MatrixQ, pApprox_?MatrixQ, meanDelta_List
] := Module[{n},
  If[
    Dimensions[pExact] =!= Dimensions[pApprox] ||
    Dimensions[pExact][[1]] =!= Dimensions[pExact][[2]] ||
    Length[meanDelta] =!= Length[pExact],
    Return[False]
  ];
  n = Length[pExact];
  TrueQ[
    ExactOrthogonalProjectorQ[pExact] &&
    ExactOrthogonalProjectorQ[pApprox] &&
    exactZeroMatrixQ[pExact - pApprox] &&
    And @@ Map[
      exactZeroScalarQ,
      (IdentityMatrix[n] - pExact).meanDelta
    ]
  ]
];

ClearAll[CompressGaussianLikelihoodData];
CompressGaussianLikelihoodData::dim =
  "Full matrices/vectors and retained isometry r have incompatible dimensions.";
CompressGaussianLikelihoodData::iso =
  "r must satisfy r^dagger.r=I.";
CompressGaussianLikelihoodData::spd =
  "Both compressed covariance matrices must be positive definite.";
CompressGaussianLikelihoodData[
  cExact_?MatrixQ, cApprox_?MatrixQ,
  muExact_List, muApprox_List, x_List, r_?MatrixQ
] := Module[
  {n, retained, identity, cExactBar, cApproxBar, muExactBar, muApproxBar, xBar},
  n = Length[cExact];
  retained = Dimensions[r][[2]];
  If[
    Dimensions[cExact] =!= {n, n} ||
    Dimensions[cApprox] =!= {n, n} ||
    Dimensions[r][[1]] =!= n ||
    Length[muExact] =!= n ||
    Length[muApprox] =!= n ||
    Length[x] =!= n,
    Message[CompressGaussianLikelihoodData::dim];
    Return[$Failed]
  ];
  identity = IdentityMatrix[retained];
  If[!exactZeroMatrixQ[ConjugateTranspose[r].r - identity],
    Message[CompressGaussianLikelihoodData::iso];
    Return[$Failed]
  ];
  cExactBar = RootReduce[ConjugateTranspose[r].cExact.r];
  cApproxBar = RootReduce[ConjugateTranspose[r].cApprox.r];
  If[
    !TrueQ[PositiveDefiniteMatrixQ[cExactBar]] ||
    !TrueQ[PositiveDefiniteMatrixQ[cApproxBar]],
    Message[CompressGaussianLikelihoodData::spd];
    Return[$Failed]
  ];
  muExactBar = RootReduce[ConjugateTranspose[r].muExact];
  muApproxBar = RootReduce[ConjugateTranspose[r].muApprox];
  xBar = RootReduce[ConjugateTranspose[r].x];
  <|
    "RetainedDimension" -> retained,
    "ExactCovariance" -> cExactBar,
    "ApproxCovariance" -> cApproxBar,
    "ExactMean" -> muExactBar,
    "ApproxMean" -> muApproxBar,
    "Data" -> xBar,
    "KLData" -> GaussianMeanCovarianceKLData[
      cExactBar, cApproxBar, muExactBar, muApproxBar
    ]
  |>
];

ClearAll[RunLikelihoodHardeningSelfChecks];
RunLikelihoodHardeningSelfChecks[] := Module[
  {
    p, q, cHerm, cNon, b, source, boundary,
    cApprox, a, cExact, muApprox, muExact, x,
    klData, bounds, invSqrt, z, m, rho, minus2Exact, minus2Bound,
    r, cExactSingular, cApproxSingular, xRetained,
    compressed, pOther, checks
  },

  p = DiagonalMatrix[{1, 1, 0}];
  q = IdentityMatrix[3] - p;
  cHerm = {{2, 1, 0}, {1, 4, 0}, {0, 0, 0}};
  cNon = {{2, 1, 0}, {3, 4, 0}, {0, 0, 0}};
  b = q.{{0, -2, 0}, {2, 0, -3}, {0, 3, 0}}.p;

  source = HardenedCovarianceSourceTailData[
    {{2, 1, 2}, {1, 3, 0}, {2, 0, 7}}, p
  ];
  boundary = HardenedCovarianceBoundaryResidualData[b, cHerm, p];

  cApprox = DiagonalMatrix[{2, 3}];
  a = DiagonalMatrix[{1/5, -1/4}];
  cExact = MatrixPower[cApprox, 1/2].
    (IdentityMatrix[2] + a).
    MatrixPower[cApprox, 1/2];
  muApprox = {1, -1};
  muExact = {3/2, -1/2};
  x = {2, 0};

  klData = GaussianMeanCovarianceKLData[
    cExact, cApprox, muExact, muApprox
  ];
  rho = 1/4;
  bounds = GaussianMeanCovarianceKLBounds[
    rho, 2, Tr[a.a], klData["RelativeMeanNormSquared"]
  ];

  invSqrt = MatrixPower[cApprox, -1/2];
  z = RootReduce[invSqrt.(x - muApprox)];
  m = klData["RelativeMeanShift"];
  minus2Exact = FullSimplify[
    Log[Det[cExact]/Det[cApprox]] +
    (x - muExact).Inverse[cExact].(x - muExact) -
    (x - muApprox).Inverse[cApprox].(x - muApprox)
  ];
  minus2Bound = GaussianFixedDataMinus2LogLikelihoodBound[
    rho, 2, Sqrt[Conjugate[z].z], Sqrt[Conjugate[m].m]
  ];

  r = {{1, 0}, {0, 1}, {0, 0}};
  cExactSingular = r.{{2, 1/3}, {1/3, 3}}.Transpose[r];
  cApproxSingular = r.{{5/2, 1/4}, {1/4, 7/2}}.Transpose[r];
  xRetained = r.{2, -1};
  compressed = CompressGaussianLikelihoodData[
    cExactSingular, cApproxSingular,
    r.{1/2, -1/2}, r.{0, 0}, xRetained, r
  ];
  pOther = DiagonalMatrix[{1, 0, 1}];

  checks = <|
    "HermitianCovarianceAccepted" -> ExactHermitianMatrixQ[cHerm],
    "NonHermitianCovarianceRejected" -> !ExactHermitianMatrixQ[cNon],
    "OrthogonalProjectorAccepted" -> ExactOrthogonalProjectorQ[p],
    "SourceTailIdentity" -> source["IdentityResidual"] === 0,
    "NonHermitianSourceTailFailsClosed" -> Quiet[
      HardenedCovarianceSourceTailData[cNon, p],
      HardenedCovarianceSourceTailData::cov
    ] === $Failed,
    "BoundaryResidualIdentity" -> boundary["IdentityResidual"] === 0,
    "NonHermitianBoundaryFailsClosed" -> Quiet[
      HardenedCovarianceBoundaryResidualData[b, cNon, p],
      HardenedCovarianceBoundaryResidualData::cov
    ] === $Failed,
    "MeanAwareKLDecomposition" -> klData["DecompositionResidual"] === 0,
    "MeanAwareKLSpectralBound" -> TrueQ[
      N[klData["DirectKL"], 80] <=
      N[bounds["SpectralKLUpperBound"], 80]
    ],
    "MeanAwareKLFrobeniusBound" -> TrueQ[
      N[klData["DirectKL"], 80] <=
      N[bounds["FrobeniusKLUpperBound"], 80]
    ],
    "FixedDataLikelihoodBound" -> TrueQ[
      N[Abs[minus2Exact], 80] <= N[minus2Bound, 80]
    ],
    "CommonSupportAccepted" -> CommonSupportGuard[p, p, r.{1/2, -1/2}],
    "SupportMismatchRejected" ->
      !CommonSupportGuard[p, pOther, r.{1/2, -1/2}],
    "RetainedCompressionQuadraticEquivalence" -> FullSimplify[
      xRetained.PseudoInverse[cExactSingular].xRetained -
      compressed["Data"].Inverse[compressed["ExactCovariance"]].
        compressed["Data"]
    ] === 0,
    "RetainedCompressionPseudoDetEquivalence" -> FullSimplify[
      Log[Times @@ Select[Eigenvalues[cExactSingular], # =!= 0 &]] -
      Log[Det[compressed["ExactCovariance"]]]
    ] === 0
  |>;

  <|
    "WolframVersion" -> $Version,
    "Checks" -> checks,
    "Passed" -> Count[Values[checks], True],
    "Total" -> Length[checks],
    "AllPassed" -> And @@ Values[checks],
    "FixtureValues" -> <|
      "NonHermitianOldSourceTailResidual" -> -5,
      "MeanRelativeNormSquared" -> klData["RelativeMeanNormSquared"],
      "MeanAwareKL" -> klData["DirectKL"],
      "FixedDataMinus2LogLikelihoodDifference" -> minus2Exact
    |>
  |>
];

End[];
EndPackage[];
