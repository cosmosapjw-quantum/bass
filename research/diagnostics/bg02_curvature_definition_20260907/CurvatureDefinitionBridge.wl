(* ::Package:: *)
(* PREPARED_UNEXECUTED.
   Native xTensor derivation of Gauss/Codazzi/normal-Ricci blocks from the
   ambient curvature definition and the induced hypersurface derivative.
   This is a research proof, not a production BASS API. *)
BeginPackage["BASS`Research`CB1`", {"xAct`xTensor`"}];
BuildCurvatureDefinitionBridge::usage =
 "BuildCurvatureDefinitionBridge[] derives the three hypersurface curvature blocks using xTensor's induced-metric machinery, SortCovDs and the positive-K BASS convention.";
Begin["`Private`"];
ClearAll[BuildCurvatureDefinitionBridge];
BuildCurvatureDefinitionBridge[] := Module[
 {oldKSign,oldASign,simp,signResidual,
  g1raw,g1curv,g1expanded,d1raw,d1curv,d1expanded,gaussOperator,gaussTensor,
  c1raw,c1curv,c1expanded,c2raw,c2expanded,codazziOperator,codazziTensor,
  q1raw,q1curv,q1expanded,q2raw,q2expanded,normalOperator,
  lieNormal,lieResidual,normalTensor,inducedRiemann,fullReconstruction,
  kh2,residuals},
 If[TrueQ[ManifoldQ[CBM]],Return[Failure["FreshProofKernelRequired",<||>]]];
 oldKSign=$ExtrinsicKSign; oldASign=$AccelerationSign;
 (* BASS convention: K_ab=+h_a^c h_b^d nabla_c n_d and
    A_a=n^b nabla_b n_a for n.n=-1. xTensor's acceleration definition
    divides by the normal norm, hence $AccelerationSign=-1. *)
 $ExtrinsicKSign=1; $AccelerationSign=-1;
 DefManifold[CBM,4,{a,b,c,d,e,f,g,h,i,j,k,l,m,p,q,r,s,t,u,v}];
 DefMetric[-1,cbg[-a,-b],CBD,{";","∇"}];
 DefTensor[cbn[a],CBM];
 AutomaticRules[cbn,MakeRule[{cbn[a]cbn[-a],-1}]];
 AutomaticRules[cbn,MakeRule[{cbg[-a,-b]cbn[a]cbn[b],-1}]];
 DefMetric[1,cbh[-a,-b],cbd,{"|","D"},InducedFrom->{cbg,cbn}];
 DefTensor[cbW[-a],CBM,OrthogonalTo->{cbn[a]},ProjectedWith->{cbh[a,-b]}];
 simp[x_] := ToCanonical[ContractMetric[Expand[x]]];
 signResidual=simp[
   GradNormalToExtrinsicK[CBD[-a][cbn[-b]]]
    -(ExtrinsicKcbh[-a,-b]-cbn[-a]Accelerationcbn[-b])];
 (* First Gauss-Codazzi identity: ambient projected commutator versus the
    induced-derivative commutator on an arbitrary spatial covector. *)
 g1raw=Projectorcbh[CBD[-d][CBD[-c][cbW[-b]]]-CBD[-c][CBD[-d][cbW[-b]]]];
 g1curv=SortCovDs[g1raw];
 g1expanded=simp[
   g1raw/.Projectorcbh->ProjectWith[cbh]//ProjectorToMetric//Expand//
    GradNormalToExtrinsicK//ContractMetric//GradNormalToExtrinsicK];
 d1raw=cbd[-d][cbd[-c][cbW[-b]]]-cbd[-c][cbd[-d][cbW[-b]]];
 d1curv=SortCovDs[d1raw];
 d1expanded=simp[
   d1raw//ProjectDerivative//ProjectDerivative/.
    Projectorcbh->ProjectWith[cbh]//ProjectorToMetric//Expand//
    GradNormalToExtrinsicK//ContractMetric];
 gaussOperator=simp[(g1curv-g1expanded)-(d1curv-d1expanded)];
 gaussTensor=simp[
   Projectorcbh[RiemannCBD[-a,-b,-c,-d]]-Riemanncbd[-a,-b,-c,-d]
    -ExtrinsicKcbh[-a,-c]ExtrinsicKcbh[-b,-d]
    +ExtrinsicKcbh[-a,-d]ExtrinsicKcbh[-b,-c]];
 (* Codazzi identity from the ambient commutator acting on the normal. *)
 c1raw=Projectorcbh[CBD[-d][CBD[-c][cbn[-b]]]-CBD[-c][CBD[-d][cbn[-b]]]];
 c1curv=SortCovDs[c1raw];
 c1expanded=simp[
   c1raw/.Projectorcbh->ProjectWith[cbh]//ProjectorToMetric//Expand//
    GradNormalToExtrinsicK//ContractMetric//GradNormalToExtrinsicK];
 c2raw=cbd[-c][ExtrinsicKcbh[-b,-d]]-cbd[-d][ExtrinsicKcbh[-b,-c]];
 c2expanded=simp[
   c2raw//ProjectDerivative/.Projectorcbh->ProjectWith[cbh]//
    ProjectorToMetric//Expand//GradNormalToExtrinsicK//ContractMetric];
 codazziOperator=simp[(c1curv-c1expanded)-(c2raw-c2expanded)];
 codazziTensor=simp[
   Projectorcbh[cbn[a]RiemannCBD[-a,-b,-c,-d]]
    -cbd[-d][ExtrinsicKcbh[-b,-c]]+cbd[-c][ExtrinsicKcbh[-b,-d]]];
 (* Third block: one normal derivative contracts the commutator on n. *)
 q1raw=Projectorcbh[cbn[d](CBD[-d][CBD[-c][cbn[-b]]]-CBD[-c][CBD[-d][cbn[-b]]])];
 q1curv=SortCovDs[q1raw];
 q1expanded=simp[
   q1raw/.Projectorcbh->ProjectWith[cbh]//ProjectorToMetric//Expand//
    GradNormalToExtrinsicK//ContractMetric//GradNormalToExtrinsicK];
 q2raw=-cbd[-c][Accelerationcbn[-b]]-
   Projectorcbh[cbn[d]CBD[-d][ExtrinsicKcbh[-b,-c]]];
 q2expanded=simp[
   q2raw//ProjectDerivative/.Projectorcbh->ProjectWith[cbh]//
    ProjectorToMetric//Expand//GradNormalToExtrinsicK//ContractMetric];
 normalOperator=simp[(q1curv-q1expanded)-(q2raw-q2expanded)];
 (* For positive K, Lie_n K - projected(nabla_n K)=+2 K.K. *)
 lieNormal=simp[
   ProjectWith[cbh][LieD[cbn[a],CBD][ExtrinsicKcbh[-b,-c]]
     -cbn[a]CBD[-a][ExtrinsicKcbh[-b,-c]]]//ContractMetric];
 kh2=simp[ExtrinsicKcbh[-b,a]ExtrinsicKcbh[-a,-c]];
 lieResidual=simp[lieNormal-2 kh2];
 (* xTensor documentation's third Gauss-Codazzi slot ordering is
    P[n^a n^d R_{b d c a}]. With positive K this equals
    -Lie_n K_bc + (K.K)_bc + D_c A_b + A_b A_c. *)
 normalTensor=simp[
   Projectorcbh[cbn[a]cbn[d]RiemannCBD[-b,-d,-c,-a]]
    +Projectorcbh[LieD[cbn[a],CBD][ExtrinsicKcbh[-b,-c]]]
    -kh2-cbd[-c][Accelerationcbn[-b]]
    -Accelerationcbn[-b]Accelerationcbn[-c]];
 (* Independent full-tensor decomposition supplied by xTensor after the three
    commutator derivations. This is not used as an input to the prior residuals. *)
 inducedRiemann=InducedDecomposition[RiemannCBD[-a,-b,-c,-d],{cbh,cbn}]//ToCanonical;
 fullReconstruction=simp[inducedRiemann-RiemannCBD[-a,-b,-c,-d]];
 residuals=<|
  "CB00_POSITIVE_K_ACCELERATION_SIGN_LOCK"->signResidual,
  "CB01_GAUSS_OPERATOR_COMMUTATOR"->gaussOperator,
  "CB02_GAUSS_TENSOR"->gaussTensor,
  "CB03_CODAZZI_OPERATOR_COMMUTATOR"->codazziOperator,
  "CB04_CODAZZI_TENSOR"->codazziTensor,
  "CB05_NORMAL_RICCI_OPERATOR_COMMUTATOR"->normalOperator,
  "CB06_LIE_VS_PROJECTED_NORMAL_K"->lieResidual,
  "CB07_NORMAL_RICCI_TENSOR"->normalTensor,
  "CB08_XTENSOR_INDUCED_DECOMPOSITION_RECONSTRUCTION"->fullReconstruction|>;
 $ExtrinsicKSign=oldKSign; $AccelerationSign=oldASign;
 <|"scope"->"NATIVE_CURVATURE_DEFINITION_TO_HYPERSURFACE_BLOCKS_ONLY",
   "residuals"->residuals,
   "conventions"-><|"metric_signature"->"(-,+,+,+)",
     "extrinsic_curvature"->"K_ab=+h_a^c h_b^d nabla_c n_d",
     "acceleration"->"A_a=n^b nabla_b n_a"|>,
   "curvature_definition_to_blocks_verified"->Missing["PENDING_NATIVE_EXECUTION"],
   "uses_component_arrays"->False,"uses_xCoba"->False,
   "production_admitted"->False|>
];
End[];
EndPackage[];
