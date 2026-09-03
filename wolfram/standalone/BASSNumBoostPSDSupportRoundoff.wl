(* ::Package:: *)

BeginPackage["BASSNumBoostPSDSupportRoundoff`"];

HermitianProjectionData::usage =
  "HermitianProjectionData[m] splits a square matrix into Hermitian and skew-Hermitian parts and records exact residuals.";

SPDWeylGuard::usage =
  "SPDWeylGuard[lambdaMinApprox,errorBound] certifies an unknown exact covariance as strictly positive definite only when lambdaMinApprox>errorBound>=0.";

SPDFloorPolicyData::usage =
  "SPDFloorPolicyData[lambdaMinRaw,floor,targetFloorAuthorized] distinguishes numerical cone projection from an unauthorized covariance-model floor.";

NearestHermitianEigenFloorData::usage =
  "NearestHermitianEigenFloorData[h,floor] clips exact decidable eigenvalues of a Hermitian matrix to a declared floor and returns an explicit repair ledger.";

PolarIsometryRepairData::usage =
  "PolarIsometryRepairData[rRaw] replaces a full-column-rank basis by its polar isometry and records the Gram and correction bounds.";

ProjectorDriftBounds::usage =
  "ProjectorDriftBounds[p,pApprox,c,mu] evaluates exact/spectral upper bounds for covariance and mean compression drift.";

CommonSupportCompressionGuard::usage =
  "CommonSupportCompressionGuard[cExact,cApprox,muExact,muApprox,x,r] compresses a degenerate Gaussian likelihood only when both covariances and both affine data residuals lie in the same retained support.";

RunPSDSupportRoundoffSelfChecks::usage =
  "RunPSDSupportRoundoffSelfChecks[] runs 16 exact or high-precision contract checks.";

Begin["`Private`"];

ClearAll[exactZeroScalarQ, exactZeroVectorQ, exactZeroMatrixQ, frobeniusNormSquared];

exactZeroScalarQ[x_] := TrueQ[PossibleZeroQ[RootReduce[x]]];
exactZeroVectorQ[v_List] := And @@ Map[exactZeroScalarQ, v];
exactZeroMatrixQ[m_?MatrixQ] := And @@ Flatten[Map[exactZeroScalarQ, m, {2}]];
frobeniusNormSquared[m_?MatrixQ] := Expand[Tr[ConjugateTranspose[m].m]];

ClearAll[exactHermitianQ, exactOrthogonalProjectorQ];
exactHermitianQ[m_?MatrixQ] :=
  Length[Dimensions[m]] === 2 &&
  Dimensions[m][[1]] === Dimensions[m][[2]] &&
  exactZeroMatrixQ[m - ConjugateTranspose[m]];

exactOrthogonalProjectorQ[p_?MatrixQ] :=
  Length[Dimensions[p]] === 2 &&
  Dimensions[p][[1]] === Dimensions[p][[2]] &&
  exactZeroMatrixQ[p - ConjugateTranspose[p]] &&
  exactZeroMatrixQ[p.p - p];

ClearAll[HermitianProjectionData];
HermitianProjectionData::dim = "m must be square.";
HermitianProjectionData[m_?MatrixQ] := Module[{h, k},
  If[
    Length[Dimensions[m]] =!= 2 || Dimensions[m][[1]] =!= Dimensions[m][[2]],
    Message[HermitianProjectionData::dim];
    Return[$Failed]
  ];
  h = Expand[(m + ConjugateTranspose[m])/2];
  k = Expand[(m - ConjugateTranspose[m])/2];
  <|
    "HermitianPart" -> h,
    "SkewHermitianPart" -> k,
    "DecompositionResidual" -> Expand[m - h - k],
    "HermitianResidual" -> Expand[h - ConjugateTranspose[h]],
    "SkewHermitianResidual" -> Expand[k + ConjugateTranspose[k]],
    "AntiHermitianNormSquared" -> frobeniusNormSquared[k]
  |>
];

ClearAll[SPDWeylGuard];
SPDWeylGuard::domain =
  "Require real lambdaMinApprox and errorBound with errorBound>=0.";
SPDWeylGuard[lambdaMinApprox_, errorBound_] := Module[{certified},
  If[
    !TrueQ[Element[{lambdaMinApprox, errorBound}, Reals]] ||
    !TrueQ[errorBound >= 0],
    Message[SPDWeylGuard::domain];
    Return[$Failed]
  ];
  certified = TrueQ[lambdaMinApprox > errorBound];
  <|
    "CertifiedSPD" -> certified,
    "WeylMargin" -> FullSimplify[lambdaMinApprox - errorBound],
    "StrictInequalityRequired" -> True
  |>
];

ClearAll[SPDFloorPolicyData];
SPDFloorPolicyData::domain =
  "Require real lambdaMinRaw, positive floor, and Boolean targetFloorAuthorized.";
SPDFloorPolicyData[
  lambdaMinRaw_, floor_, targetFloorAuthorized : (True | False)
] := Module[{status, repairLower, ratio},
  If[
    !TrueQ[Element[{lambdaMinRaw, floor}, Reals]] || !TrueQ[floor > 0],
    Message[SPDFloorPolicyData::domain];
    Return[$Failed]
  ];
  repairLower = Max[0, floor - lambdaMinRaw];
  ratio = FullSimplify[repairLower/floor];
  status = Which[
    TrueQ[lambdaMinRaw >= floor],
      "NO_FLOOR_ACTION_REQUIRED",
    TrueQ[targetFloorAuthorized],
      "AUTHORIZED_SAME_CONE_PROJECTION_OR_MODEL_REGULARIZATION",
    True,
      "REJECT_UNAUTHORIZED_MODEL_CHANGE"
  ];
  <|
    "Status" -> status,
    "DeclaredFloor" -> floor,
    "RawMinimumEigenvalue" -> lambdaMinRaw,
    "SpectralRepairLowerBound" -> repairLower,
    "RepairToFloorRatioLowerBound" -> ratio,
    "NegativeEigenvalueCannotSelfCertifyAgainstFloor" ->
      TrueQ[lambdaMinRaw < 0 && ratio > 1],
    "TargetFloorAuthorityRequired" -> TrueQ[lambdaMinRaw < floor]
  |>
];

ClearAll[NearestHermitianEigenFloorData];
NearestHermitianEigenFloorData::cov = "h must be exactly Hermitian.";
NearestHermitianEigenFloorData::floor = "floor must be a positive real scalar.";
NearestHermitianEigenFloorData::order =
  "Every exact eigenvalue must be decidably above or below the floor.";
NearestHermitianEigenFloorData[h_?MatrixQ, floor_] := Module[
  {values, vectors, clipped, undecidable, repaired, delta},
  If[!exactHermitianQ[h],
    Message[NearestHermitianEigenFloorData::cov];
    Return[$Failed]
  ];
  If[!TrueQ[Element[floor, Reals]] || !TrueQ[floor > 0],
    Message[NearestHermitianEigenFloorData::floor];
    Return[$Failed]
  ];
  {values, vectors} = Eigensystem[h];
  undecidable = Select[
    values,
    !TrueQ[# < floor] && !TrueQ[# >= floor] &
  ];
  If[undecidable =!= {},
    Message[NearestHermitianEigenFloorData::order];
    Return[$Failed]
  ];
  clipped = Map[If[TrueQ[# < floor], floor, #] &, values];
  repaired = RootReduce[
    ConjugateTranspose[vectors].DiagonalMatrix[clipped].vectors
  ];
  delta = RootReduce[repaired - h];
  <|
    "OriginalEigenvalues" -> values,
    "ClippedEigenvalues" -> clipped,
    "RepairedMatrix" -> repaired,
    "RepairFrobeniusNormSquared" -> frobeniusNormSquared[delta],
    "RepairSpectralNorm" -> Norm[delta, 2],
    "MinimumRepairedEigenvalue" -> Min[clipped]
  |>
];

ClearAll[PolarIsometryRepairData];
PolarIsometryRepairData::rank =
  "rRaw must have full column rank, equivalently rRaw^dagger.rRaw must be positive definite.";
PolarIsometryRepairData[rRaw_?MatrixQ] := Module[
  {gram, retained, repaired, epsGram, correction, bound, projector},
  retained = Dimensions[rRaw][[2]];
  gram = RootReduce[ConjugateTranspose[rRaw].rRaw];
  If[!TrueQ[PositiveDefiniteMatrixQ[gram]],
    Message[PolarIsometryRepairData::rank];
    Return[$Failed]
  ];
  repaired = RootReduce[rRaw.MatrixPower[gram, -1/2]];
  epsGram = Norm[gram - IdentityMatrix[retained], 2];
  correction = Norm[rRaw - repaired, 2];
  bound = If[
    TrueQ[epsGram < 1],
    FullSimplify[1 - Sqrt[1 - epsGram]],
    Missing["GramDefectNotBelowOne"]
  ];
  projector = RootReduce[repaired.ConjugateTranspose[repaired]];
  <|
    "RawGram" -> gram,
    "RepairedIsometry" -> repaired,
    "RepairedGramResidual" ->
      RootReduce[ConjugateTranspose[repaired].repaired - IdentityMatrix[retained]],
    "RepairedProjector" -> projector,
    "ProjectorIdempotenceResidual" -> RootReduce[projector.projector - projector],
    "GramDefectSpectralNorm" -> epsGram,
    "BasisCorrectionSpectralNorm" -> correction,
    "BasisCorrectionUpperBound" -> bound,
    "BoundPass" -> If[
      MissingQ[bound],
      False,
      TrueQ[N[correction, 80] <= N[bound, 80]]
    ]
  |>
];

ClearAll[ProjectorDriftBounds];
ProjectorDriftBounds::dim =
  "p, pApprox and c must be square matrices of one dimension, and mu must match.";
ProjectorDriftBounds::proj =
  "p and pApprox must be exact orthogonal projectors.";
ProjectorDriftBounds[p_?MatrixQ, pApprox_?MatrixQ, c_?MatrixQ, mu_List] := Module[
  {n, gap, covActual, covBound, meanActual, meanBound},
  n = Length[p];
  If[
    Dimensions[p] =!= {n, n} ||
    Dimensions[pApprox] =!= {n, n} ||
    Dimensions[c] =!= {n, n} || Length[mu] =!= n,
    Message[ProjectorDriftBounds::dim];
    Return[$Failed]
  ];
  If[!exactOrthogonalProjectorQ[p] || !exactOrthogonalProjectorQ[pApprox],
    Message[ProjectorDriftBounds::proj];
    Return[$Failed]
  ];
  gap = Norm[p - pApprox, 2];
  covActual = Norm[p.c.p - pApprox.c.pApprox, 2];
  covBound = 2 Norm[c, 2] gap;
  meanActual = Norm[p.mu - pApprox.mu, 2];
  meanBound = Norm[mu, 2] gap;
  <|
    "ProjectorGapSpectralNorm" -> gap,
    "CovarianceCompressionDifference" -> covActual,
    "CovarianceCompressionUpperBound" -> covBound,
    "MeanCompressionDifference" -> meanActual,
    "MeanCompressionUpperBound" -> meanBound,
    "CovarianceBoundPass" -> TrueQ[N[covActual, 80] <= N[covBound, 80]],
    "MeanBoundPass" -> TrueQ[N[meanActual, 80] <= N[meanBound, 80]],
    "AllBoundsPass" -> TrueQ[
      N[covActual, 80] <= N[covBound, 80] &&
      N[meanActual, 80] <= N[meanBound, 80]
    ]
  |>
];

ClearAll[CommonSupportCompressionGuard];
CommonSupportCompressionGuard::dim =
  "Full matrices/vectors and retained isometry r have incompatible dimensions.";
CommonSupportCompressionGuard::iso = "r must satisfy r^dagger.r=I.";
CommonSupportCompressionGuard::cov =
  "Both covariances must be Hermitian and exactly supported on p=r.r^dagger.";
CommonSupportCompressionGuard::affine =
  "The mean difference and both data-minus-mean residuals must lie in the common support.";
CommonSupportCompressionGuard::spd =
  "Both compressed covariances must be positive definite.";
CommonSupportCompressionGuard[
  cExact_?MatrixQ, cApprox_?MatrixQ,
  muExact_List, muApprox_List, x_List, r_?MatrixQ
] := Module[
  {n, retained, p, q, cExactBar, cApproxBar, muExactBar, muApproxBar, xBar,
   pseudoQuadExact, compressedQuadExact, pseudoDetExact, compressedDetExact},
  n = Length[cExact];
  retained = Dimensions[r][[2]];
  If[
    Dimensions[cExact] =!= {n, n} || Dimensions[cApprox] =!= {n, n} ||
    Dimensions[r][[1]] =!= n || Length[muExact] =!= n ||
    Length[muApprox] =!= n || Length[x] =!= n,
    Message[CommonSupportCompressionGuard::dim];
    Return[$Failed]
  ];
  If[!exactZeroMatrixQ[ConjugateTranspose[r].r - IdentityMatrix[retained]],
    Message[CommonSupportCompressionGuard::iso];
    Return[$Failed]
  ];
  p = RootReduce[r.ConjugateTranspose[r]];
  q = IdentityMatrix[n] - p;
  If[
    !exactHermitianQ[cExact] || !exactHermitianQ[cApprox] ||
    !exactZeroMatrixQ[cExact - p.cExact.p] ||
    !exactZeroMatrixQ[cApprox - p.cApprox.p],
    Message[CommonSupportCompressionGuard::cov];
    Return[$Failed]
  ];
  If[
    !exactZeroVectorQ[q.(muExact - muApprox)] ||
    !exactZeroVectorQ[q.(x - muExact)] ||
    !exactZeroVectorQ[q.(x - muApprox)],
    Message[CommonSupportCompressionGuard::affine];
    Return[$Failed]
  ];
  cExactBar = RootReduce[ConjugateTranspose[r].cExact.r];
  cApproxBar = RootReduce[ConjugateTranspose[r].cApprox.r];
  If[
    !TrueQ[PositiveDefiniteMatrixQ[cExactBar]] ||
    !TrueQ[PositiveDefiniteMatrixQ[cApproxBar]],
    Message[CommonSupportCompressionGuard::spd];
    Return[$Failed]
  ];
  muExactBar = RootReduce[ConjugateTranspose[r].muExact];
  muApproxBar = RootReduce[ConjugateTranspose[r].muApprox];
  xBar = RootReduce[ConjugateTranspose[r].x];
  pseudoQuadExact = FullSimplify[
    (x - muExact).PseudoInverse[cExact].(x - muExact)
  ];
  compressedQuadExact = FullSimplify[
    (xBar - muExactBar).Inverse[cExactBar].(xBar - muExactBar)
  ];
  pseudoDetExact = FullSimplify[
    Times @@ Select[Eigenvalues[cExact], !PossibleZeroQ[#] &]
  ];
  compressedDetExact = FullSimplify[Det[cExactBar]];
  <|
    "SupportProjector" -> p,
    "RetainedDimension" -> retained,
    "ExactCovariance" -> cExactBar,
    "ApproxCovariance" -> cApproxBar,
    "ExactMean" -> muExactBar,
    "ApproxMean" -> muApproxBar,
    "Data" -> xBar,
    "PseudoinverseQuadraticResidual" ->
      FullSimplify[pseudoQuadExact - compressedQuadExact],
    "PseudodeterminantResidual" ->
      FullSimplify[pseudoDetExact - compressedDetExact]
  |>
];

ClearAll[RunPSDSupportRoundoffSelfChecks];
RunPSDSupportRoundoffSelfChecks[] := Module[
  {h, k, raw, target, projection, floorData, polar, p, pApprox, c, mu,
   drift, r, cExactSingular, cApproxSingular, validSupport, invalidCov,
   invalidData, checks},
  h = DiagonalMatrix[{-1/5, 2, 3}];
  k = {{0, 1/20, 0}, {-1/20, 0, 0}, {0, 0, 0}};
  raw = h + k;
  target = DiagonalMatrix[{1, 5/2, 7/2}];
  projection = HermitianProjectionData[raw];
  floorData = NearestHermitianEigenFloorData[h, 1/10];
  polar = PolarIsometryRepairData[{{1, 0}, {0, 1}, {1/5, 0}}];
  p = DiagonalMatrix[{1, 0, 0}];
  pApprox = Outer[Times, {4/5, 3/5, 0}, {4/5, 3/5, 0}];
  c = {{3, 1, 0}, {1, 2, 1/2}, {0, 1/2, 1}};
  mu = {2, -1, 3};
  drift = ProjectorDriftBounds[p, pApprox, c, mu];
  r = {{1, 0}, {0, 1}, {0, 0}};
  cExactSingular = r.{{2, 1/3}, {1/3, 3}}.Transpose[r];
  cApproxSingular = r.{{5/2, 1/4}, {1/4, 7/2}}.Transpose[r];
  validSupport = CommonSupportCompressionGuard[
    cExactSingular, cApproxSingular,
    r.{1/2, -1/2}, r.{0, 0}, r.{2, -1}, r
  ];
  invalidCov = Quiet[
    CommonSupportCompressionGuard[
      DiagonalMatrix[{2, 3, 5}], DiagonalMatrix[{5/2, 7/2, 4}],
      {0, 0, 0}, {0, 0, 0}, {1, -1, 2}, r
    ],
    CommonSupportCompressionGuard::cov
  ];
  invalidData = Quiet[
    CommonSupportCompressionGuard[
      cExactSingular, cApproxSingular,
      r.{1/2, -1/2}, r.{0, 0}, {2, -1, 1}, r
    ],
    CommonSupportCompressionGuard::affine
  ];
  checks = <|
    "HermitianDecomposition" -> exactZeroMatrixQ[projection["DecompositionResidual"]],
    "HermitianPart" -> exactZeroMatrixQ[projection["HermitianResidual"]],
    "SkewHermitianPart" -> exactZeroMatrixQ[projection["SkewHermitianResidual"]],
    "SymmetrizationOrthogonalErrorSplit" ->
      Expand[
        frobeniusNormSquared[raw - target] -
        frobeniusNormSquared[projection["HermitianPart"] - target] -
        frobeniusNormSquared[projection["SkewHermitianPart"]]
      ] === 0,
    "WeylStrictPass" -> TrueQ[SPDWeylGuard[1/10, 1/20]["CertifiedSPD"]],
    "WeylEqualityFails" -> !TrueQ[SPDWeylGuard[1/10, 1/10]["CertifiedSPD"]],
    "UnauthorizedFloorRejected" ->
      SPDFloorPolicyData[-1/5, 1/10, False]["Status"] ===
        "REJECT_UNAUTHORIZED_MODEL_CHANGE",
    "NegativeFloorCannotSelfCertify" ->
      TrueQ[SPDFloorPolicyData[-1/5, 1/10, False][
        "NegativeEigenvalueCannotSelfCertifyAgainstFloor"
      ]],
    "AuthorizedFloorTyped" ->
      SPDFloorPolicyData[-1/5, 1/10, True]["Status"] ===
        "AUTHORIZED_SAME_CONE_PROJECTION_OR_MODEL_REGULARIZATION",
    "EigenFloorFixture" ->
      floorData["RepairedMatrix"] === DiagonalMatrix[{1/10, 2, 3}],
    "PolarIsometry" -> exactZeroMatrixQ[polar["RepairedGramResidual"]],
    "PolarCorrectionBound" -> TrueQ[polar["BoundPass"]],
    "ProjectorDriftBounds" -> TrueQ[drift["AllBoundsPass"]],
    "CommonSupportCompression" ->
      validSupport =!= $Failed &&
      validSupport["PseudoinverseQuadraticResidual"] === 0 &&
      validSupport["PseudodeterminantResidual"] === 0,
    "OutsideSupportCovarianceRejected" -> invalidCov === $Failed,
    "OutsideAffineSupportRejected" -> invalidData === $Failed
  |>;
  <|
    "WolframVersion" -> $Version,
    "Checks" -> checks,
    "Passed" -> Count[Values[checks], True],
    "Total" -> Length[checks],
    "AllPassed" -> And @@ Values[checks],
    "FixtureValues" -> <|
      "AntiHermitianNormSquared" -> projection["AntiHermitianNormSquared"],
      "FloorRepairFrobeniusNormSquared" -> floorData["RepairFrobeniusNormSquared"],
      "NegativeFloorRatioLowerBound" ->
        SPDFloorPolicyData[-1/5, 1/10, False]["RepairToFloorRatioLowerBound"],
      "PolarBasisCorrectionSpectralNorm" -> polar["BasisCorrectionSpectralNorm"],
      "ProjectorGapSpectralNorm" -> drift["ProjectorGapSpectralNorm"]
    |>
  |>
];

End[];
EndPackage[];
