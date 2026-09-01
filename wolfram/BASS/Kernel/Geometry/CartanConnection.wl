(* ::Package:: *)

BeginPackage["BASS`Geometry`"];

LeviCivitaConnection::usage =
 "LeviCivitaConnection[C] returns the orthonormal-frame coefficients Gamma_{ijk}=(C_{ijk}-C_{jki}+C_{kij})/2.";
MetricCompatibilityResidual::usage =
 "MetricCompatibilityResidual[Gamma] returns Gamma_{ijk}+Gamma_{ikj}.";
MetricCompatibilityQ::usage =
 "MetricCompatibilityQ[Gamma] verifies metric compatibility in the Euclidean spatial ONF.";
TorsionResidual::usage =
 "TorsionResidual[Gamma,C] returns Gamma_{ijk}-Gamma_{jik}-C_{ijk}.";
TorsionFreeQ::usage =
 "TorsionFreeQ[Gamma,C] verifies the torsion-free Cartan relation.";
SpatialRiemann::usage =
 "SpatialRiemann[C,Gamma] returns R_{ijk}{}^l for a spatially homogeneous orthonormal frame.";
SpatialRicci::usage =
 "SpatialRicci[R] returns Ricci_{jk}=R_{ijk}{}^i.";
SpatialRicciScalar::usage =
 "SpatialRicciScalar[R] returns the Euclidean spatial trace of SpatialRicci[R].";
RiemannFirstPairAntisymmetryQ::usage =
 "RiemannFirstPairAntisymmetryQ[R] checks antisymmetry in the first two derivative slots.";

Begin["`Private`"];

ClearAll[zeroQ, tensor333Q, tensor3333Q, LeviCivitaConnection,
 MetricCompatibilityResidual, MetricCompatibilityQ, TorsionResidual,
 TorsionFreeQ, SpatialRiemann, SpatialRicci, SpatialRicciScalar,
 RiemannFirstPairAntisymmetryQ];

zeroQ[x_] := TrueQ[PossibleZeroQ[Together[x]]];
tensor333Q[x_] := ListQ[x] && Dimensions[x] === {3, 3, 3};
tensor3333Q[x_] := ListQ[x] && Dimensions[x] === {3, 3, 3, 3};

LeviCivitaConnection[c_?tensor333Q] :=
 Table[
  Together[(c[[i, j, k]] - c[[j, k, i]] + c[[k, i, j]])/2],
  {i, 3}, {j, 3}, {k, 3}];
LeviCivitaConnection[_] := Failure["InvalidStructureConstants", <||>];

MetricCompatibilityResidual[gamma_?tensor333Q] :=
 Table[Together[gamma[[i, j, k]] + gamma[[i, k, j]]],
  {i, 3}, {j, 3}, {k, 3}];
MetricCompatibilityResidual[_] := Failure["InvalidConnection", <||>];

MetricCompatibilityQ[gamma_?tensor333Q] :=
 AllTrue[Flatten[MetricCompatibilityResidual[gamma]], zeroQ];
MetricCompatibilityQ[_] := False;

TorsionResidual[gamma_?tensor333Q, c_?tensor333Q] :=
 Table[Together[gamma[[i, j, k]] - gamma[[j, i, k]] - c[[i, j, k]]],
  {i, 3}, {j, 3}, {k, 3}];
TorsionResidual[___] := Failure["InvalidCartanInput", <||>];

TorsionFreeQ[gamma_?tensor333Q, c_?tensor333Q] :=
 AllTrue[Flatten[TorsionResidual[gamma, c]], zeroQ];
TorsionFreeQ[___] := False;

SpatialRiemann[c_?tensor333Q, gamma_?tensor333Q] :=
 Table[
  Together[Sum[
    gamma[[j, k, m]] gamma[[i, m, l]] -
    gamma[[i, k, m]] gamma[[j, m, l]] -
    c[[i, j, m]] gamma[[m, k, l]],
    {m, 3}]],
  {i, 3}, {j, 3}, {k, 3}, {l, 3}];
SpatialRiemann[___] := Failure["InvalidCurvatureInput", <||>];

SpatialRicci[riemann_?tensor3333Q] :=
 Table[Together[Sum[riemann[[i, j, k, i]], {i, 3}]],
  {j, 3}, {k, 3}];
SpatialRicci[_] := Failure["InvalidRiemannTensor", <||>];

SpatialRicciScalar[riemann_?tensor3333Q] :=
 Together[Tr[SpatialRicci[riemann]]];
SpatialRicciScalar[_] := Failure["InvalidRiemannTensor", <||>];

RiemannFirstPairAntisymmetryQ[riemann_?tensor3333Q] :=
 AllTrue[Flatten[Table[
   riemann[[i, j, k, l]] + riemann[[j, i, k, l]],
   {i, 3}, {j, 3}, {k, 3}, {l, 3}]], zeroQ];
RiemannFirstPairAntisymmetryQ[_] := False;

End[];
EndPackage[];
