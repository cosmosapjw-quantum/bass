(* ::Package:: *)

(* Load only after BASSNumBoostLikelihoodHardening.wl. *)

BeginPackage["BASSNumBoostLikelihoodHardening`"];

GaussianMeanCovarianceKLData::real =
  "This 1/2-normalized likelihood contract is for a real multivariate Gaussian. Covariances and means must be exactly real; use a declared real stored-harmonic/map basis before calling it.";

CompressGaussianLikelihoodData::real =
  "This likelihood compression contract is for a real multivariate Gaussian. Covariances, means, data, and retained isometry must be exactly real.";

Begin["`Private`"];

ClearAll[
  exactRealScalarQ,
  exactRealVectorQ,
  exactRealMatrixQ,
  realGaussianKLInputQ,
  realGaussianCompressionInputQ
];

exactRealScalarQ[x_] :=
  TrueQ[PossibleZeroQ[RootReduce[Im[x]]]];

exactRealVectorQ[v_List] :=
  And @@ Map[exactRealScalarQ, v];

exactRealMatrixQ[m_?MatrixQ] :=
  And @@ Flatten[Map[exactRealScalarQ, m, {2}]];

realGaussianKLInputQ[
  cExact_?MatrixQ,
  cApprox_?MatrixQ,
  muExact_List,
  muApprox_List
] :=
  exactRealMatrixQ[cExact] &&
  exactRealMatrixQ[cApprox] &&
  exactRealVectorQ[muExact] &&
  exactRealVectorQ[muApprox];

realGaussianCompressionInputQ[
  cExact_?MatrixQ,
  cApprox_?MatrixQ,
  muExact_List,
  muApprox_List,
  x_List,
  r_?MatrixQ
] :=
  exactRealMatrixQ[cExact] &&
  exactRealMatrixQ[cApprox] &&
  exactRealVectorQ[muExact] &&
  exactRealVectorQ[muApprox] &&
  exactRealVectorQ[x] &&
  exactRealMatrixQ[r];

End[];

GaussianMeanCovarianceKLData[
  cExact_?MatrixQ,
  cApprox_?MatrixQ,
  muExact_List,
  muApprox_List
] /; !BASSNumBoostLikelihoodHardening`Private`realGaussianKLInputQ[
  cExact, cApprox, muExact, muApprox
] := (
  Message[GaussianMeanCovarianceKLData::real];
  $Failed
);

CompressGaussianLikelihoodData[
  cExact_?MatrixQ,
  cApprox_?MatrixQ,
  muExact_List,
  muApprox_List,
  x_List,
  r_?MatrixQ
] /; !BASSNumBoostLikelihoodHardening`Private`realGaussianCompressionInputQ[
  cExact, cApprox, muExact, muApprox, x, r
] := (
  Message[CompressGaussianLikelihoodData::real];
  $Failed
);

EndPackage[];
