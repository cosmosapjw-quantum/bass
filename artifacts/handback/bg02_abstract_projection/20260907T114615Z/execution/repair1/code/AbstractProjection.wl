(* ::Package:: *)
(* PREPARED_UNEXECUTED. Conditional abstract-index contraction proof.
   Input premises are the Gauss/Codazzi/Ricci curvature blocks. This file does
   NOT derive those differential identities from an arbitrary metric, replace
   BASS geometry, or modify the old native/capture suites. No chart/components. *)
BeginPackage["BASS`Research`AP1`", {"xAct`xTensor`"}];
BuildAbstractProjectionProof::usage =
 "BuildAbstractProjectionProof[] contracts independently assembled curvature blocks with xTensor, compares all four Einstein projections and the existing BASS component consumer. Fresh kernel required.";
Begin["`Private`"];
ClearAll[BuildAbstractProjectionProof];
BuildAbstractProjectionProof[] := Module[
 {vb, dummy, rules, dNormalRules, step, reduce, projector, trace, norm2,
  kSquared, sigmaSquared, aaSquared, stf, intrinsic, gauss, mixed, electric,
  curvature, ricci, scalarR, stress, einstein, divK, gradK,
  hActual, mActual, pActual, sActual, eActual, hExpected, mExpected,
  pExpected, sExpected, projectedGauss, projectedMixed, projectedElectric,
  mTensor, sTensor, reconstructed, lieMetric, scalarTraceCheck,
  kRules, lGoodRules, lBadRules, toShear, sourceInput, sourceValues,
  shearValues, traceMutation, mutationWitness, ricHead, riemHead,
  residuals, owner},
 If[TrueQ[ManifoldQ[APM]],Return[Failure["FreshProofKernelRequired",<||>]]];
 If[Length[DownValues[BASS`Authority`BG02ConventionRegistry]]===0 ||
    Length[DownValues[BASS`Background`EinsteinResidualTensor]]===0,
   Return[Failure["MissingPinnedBG02Consumers",<||>]]];
 owner=BASS`Authority`BG02ConventionRegistry[];
 If[!AssociationQ[owner] || Lookup[owner,"contract_id",None]=!="BASS_BG02_OWNER_CONVENTION_V2",
   Return[Failure["UnexpectedBG02Owner",<||>]]];
 DefManifold[APM,4,{ia,ib,ic,id,ie,iff,ig,ih,ii,ij,ik,il,im,in,ip,ir,is,it}];
 DefMetric[-1,met[-ia,-ib],APCD,{";","D"}];
 DefTensor[nu[ia],APM];
 (* StressPi avoids the protected System`Pi constant. *)
 Scan[(DefTensor[#[-ia,-ib],APM,Symmetric[{-ia,-ib}]])&,
   {KK,LL,ZZ,DA,StressPi,Sigma,LSigma}];
 DefTensor[DK[-ia,-ib,-ic],APM,Symmetric[{-ib,-ic}]];
 DefTensor[acc[-ia],APM]; DefTensor[flux[-ia],APM];
 Scan[(DefTensor[#[],APM])&, {HH,HD,rho,press}];
 DefConstantSymbol[kappaG]; DefConstantSymbol[lambda];
 vb=TangentBundleOfManifold[APM]; dummy[]:=DummyIn[vb];
 rules=Join[
   MakeRule[{nu[ia]nu[-ia],-1},MetricOn->All,ContractMetrics->True],
   Flatten[Table[MakeRule[{nu[ia]t[-ia,-ib],0},
     MetricOn->All,ContractMetrics->True],{t,{KK,LL,ZZ,DA,StressPi,Sigma,LSigma}}],1],
   Flatten[Table[MakeRule[{nu[ia]v[-ia],0},
     MetricOn->All,ContractMetrics->True],{v,{acc,flux}}],1],
   MakeRule[{nu[ia]DK[-ia,-ib,-ic],0},MetricOn->All,ContractMetrics->True],
   MakeRule[{nu[ib]DK[-ia,-ib,-ic],0},MetricOn->All,ContractMetrics->True],
   Flatten[Table[MakeRule[{t[ia,-ia],0},MetricOn->All,
     ContractMetrics->True],{t,{StressPi,Sigma,LSigma}}],1]];
 dNormalRules=MakeRule[{APCD[-ia][nu[-ib]],KK[-ia,-ib]-nu[-ia]acc[-ib]},
   MetricOn->All,ContractMetrics->True];
 step[x_] := ToCanonical[Expand[ContractMetric[Expand[x]] /. dNormalRules /. rules]];
 reduce[x_] := FixedPoint[step,x,16];
 projector[x_,y_] := met[x,y]+nu[x]nu[y];
 trace[t_] := Module[{u=dummy[],v=dummy[]},met[u,v]t[-u,-v]];
 norm2[v_] := Module[{u=dummy[]},v[u]v[-u]];
 kSquared[x_,y_] := Module[{u=dummy[]},KK[x,u]KK[-u,y]];
 sigmaSquared[x_,y_] := Module[{u=dummy[]},Sigma[x,u]Sigma[-u,y]];
 aaSquared[x_,y_] := acc[x]acc[y];
 stf[t_,x_,y_] := t[x,y]-projector[x,y]trace[t]/3;
 (* ZZ is arbitrary spatial Ricci. In spatial dimension 3 this reconstructs
    the algebraic intrinsic Riemann tensor, without a coordinate metric. *)
 intrinsic[x_,y_,z_,w_] := projector[x,z]ZZ[y,w]-projector[x,w]ZZ[y,z]
   -projector[y,z]ZZ[x,w]+projector[y,w]ZZ[x,z]
   -trace[ZZ](projector[x,z]projector[y,w]-projector[x,w]projector[y,z])/2;
 gauss[x_,y_,z_,w_] := intrinsic[x,y,z,w]+KK[x,z]KK[y,w]-KK[x,w]KK[y,z];
 (* DK_abc means D_a K_bc. No homogeneity or zero GradientK is imposed. *)
 mixed[x_,y_,z_] := DK[z,x,y]-DK[y,x,z];
 (* LL_ab means the spatial (covariant-index) Lie derivative L_n K_ab. *)
 electric[x_,y_] := -LL[x,y]+kSquared[x,y]+DA[x,y]+aaSquared[x,y];
 curvature[x_,y_,z_,w_] := gauss[x,y,z,w]
   -nu[x]mixed[y,z,w]+nu[y]mixed[x,z,w]
   -nu[z]mixed[w,x,y]+nu[w]mixed[z,x,y]
   +nu[x]nu[z]electric[y,w]-nu[x]nu[w]electric[y,z]
   -nu[y]nu[z]electric[x,w]+nu[y]nu[w]electric[x,z];
 ricci[x_,y_] := Module[{u=dummy[],v=dummy[]},
   reduce[met[u,v]curvature[x,-u,y,-v]]];
 scalarR=reduce[trace[ricci]];
 stress[x_,y_] := rho[]nu[x]nu[y]+nu[x]flux[y]+nu[y]flux[x]
   +press[]projector[x,y]+StressPi[x,y];
 (* Refresh contracted indices of stored scalars before multiplying them by
    tensors with new free indices. *)
 einstein[x_,y_] := ricci[x,y]-met[x,y]ReplaceDummies[scalarR]/2
   +lambda met[x,y]-kappaG stress[x,y];
 divK[x_] := Module[{u=dummy[],v=dummy[]},met[u,v]DK[-u,x,-v]];
 gradK[x_] := Module[{u=dummy[],v=dummy[]},met[u,v]DK[x,-u,-v]];
 eActual=reduce[einstein[-ia,-ib]];
 hActual=reduce[nu[ia]nu[ib]ReplaceDummies[eActual]];
 mActual=reduce[-projector[-ia,ib]nu[ic]einstein[-ib,-ic]];
 pActual=reduce[projector[ia,ib]ReplaceDummies[eActual]/3];
 sActual=reduce[(projector[-ia,ic]projector[-ib,id]
   -projector[-ia,-ib]projector[ic,id]/3)einstein[-ic,-id]];
 hExpected=(trace[ZZ]+trace[KK]trace[KK]-trace[kSquared])/2-lambda-kappaG rho[];
 mExpected=-divK[-ia]+gradK[-ia]-kappaG flux[-ia];
 pExpected=-trace[ZZ]/6-2 trace[LL]/3-trace[KK]trace[KK]/6
   +5 trace[kSquared]/6+2(trace[DA]+norm2[acc])/3+lambda-kappaG press[];
 sExpected=stf[ZZ,-ia,-ib]+stf[LL,-ia,-ib]+trace[KK]stf[KK,-ia,-ib]
   -2 stf[kSquared,-ia,-ib]-stf[DA,-ia,-ib]-stf[aaSquared,-ia,-ib]-kappaG StressPi[-ia,-ib];
 projectedGauss=reduce[projector[-ia,ie]projector[-ib,iff]
   projector[-ic,ig]projector[-id,ih]curvature[-ie,-iff,-ig,-ih]];
 projectedMixed=reduce[nu[ie]projector[-ia,iff]projector[-ib,ig]
   projector[-ic,ih]curvature[-ie,-iff,-ig,-ih]];
 projectedElectric=reduce[nu[ic]nu[id]projector[-ia,ie]
   projector[-ib,iff]curvature[-ic,-ie,-id,-iff]];
 (* Reindex computed projections only; no expected expression feeds this path. *)
 mTensor[x_] := ReplaceIndex[ReplaceDummies[mActual],{ia->-x}];
 sTensor[x_,y_] := ReplaceIndex[ReplaceDummies[sActual],{ia->-x,ib->-y}];
 reconstructed=ReplaceDummies[hActual]nu[-ia]nu[-ib]
   +nu[-ia]mTensor[-ib]+nu[-ib]mTensor[-ia]
   +ReplaceDummies[pActual]projector[-ia,-ib]+sTensor[-ia,-ib];
 (* The derivative-of-inverse-metric identity is evaluated, not entered as a
    final-projection rewrite. Its contraction yields the +2 K_ab K^ab term. *)
 lieMetric=LieDToCovD[LieD[nu[ic]][projector[ia,ib]],APCD];
 scalarTraceCheck=reduce[KK[-ia,-ib]ReplaceDummies[lieMetric]+2 trace[kSquared]];
 (* MakeRule holds its first argument. Expand helper-defined tensor RHSs
    before xTensor validates their free indices. *)
 kRules=MakeRule[Evaluate[{KK[-ia,-ib],HH[]projector[-ia,-ib]+Sigma[-ia,-ib]}],
   MetricOn->All,ContractMetrics->True];
 (* LSigma is PSTF(L_n sigma), NOT the full Lie derivative or the projected
    covariant normal derivative. LL trace includes 2 sigma^2. *)
 lGoodRules=MakeRule[Evaluate[{LL[-ia,-ib],LSigma[-ia,-ib]+2 HH[]Sigma[-ia,-ib]
     +projector[-ia,-ib](HD[]+2 HH[]^2+2 trace[sigmaSquared]/3)}],
   MetricOn->All,ContractMetrics->True];
 lBadRules=MakeRule[Evaluate[{LL[-ia,-ib],LSigma[-ia,-ib]+2 HH[]Sigma[-ia,-ib]
     +projector[-ia,-ib]HD[]}],MetricOn->All,ContractMetrics->True];
 toShear[x_,lr_] := reduce[reduce[x] /. lr /. kRules];
 sourceInput=<|"R3"->trace[ZZ],"H"->HH[],"sigma2"->trace[sigmaSquared],
   "Lambda"->lambda,"kappaG"->kappaG,"rho"->rho[],"p"->press[],
   "DivergenceK"->divK[-ia],"GradientK"->gradK[-ia],"qComponent"->flux[-ia],
   "LieH"->HD[],"D.A"->trace[DA],"A2"->norm2[acc],
   "R3PSTF"->stf[ZZ,-ia,-ib],
   "LieKPSTF"->LSigma[-ia,-ib]+2 HH[]Sigma[-ia,-ib],
   "KsigmaPSTF"->3 HH[]Sigma[-ia,-ib],
   (* Legacy name: this residual slot carries (K.K)_PSTF, not (sigma.sigma)_PSTF.
      The latter is the distinct meaning in ShearLieRate, which is not called. *)
   "SigmaQuadratic"->2 HH[]Sigma[-ia,-ib]+stf[sigmaSquared,-ia,-ib],
   "DPSTFA"->stf[DA,-ia,-ib],"APSTFA"->stf[aaSquared,-ia,-ib],
   "piComponent"->StressPi[-ia,-ib]|>;
 sourceValues={BASS`Background`HamiltonianProjection[sourceInput],
   BASS`Background`MomentumProjection[sourceInput],
   BASS`Background`SpatialTraceProjection[sourceInput],
   BASS`Background`SpatialPSTFProjection[sourceInput]};
 If[!FreeQ[sourceValues,_Failure],Return[Failure["PinnedConsumerFailure",<|"values"->sourceValues|>]]];
 shearValues=toShear[#,lGoodRules]& /@ {hActual,mActual,pActual,sActual};
 traceMutation=reduce[toShear[pActual,lBadRules]-toShear[pActual,lGoodRules]];
 mutationWitness=traceMutation /. Sigma[___]->0 /. HH[]->1;
 riemHead=GiveSymbol[Riemann,APCD]; ricHead=GiveSymbol[Ricci,APCD];
 residuals=<|
  "AP00_XTENSOR_RICCI_CONTRACTION"->reduce[met[ic,id]riemHead[-ia,-ic,-ib,-id]-ricHead[-ia,-ib]],
  "AP01_CURVATURE_SYMMETRIES"->(reduce /@ {
    curvature[-ia,-ib,-ic,-id]+curvature[-ib,-ia,-ic,-id],
    curvature[-ia,-ib,-ic,-id]+curvature[-ia,-ib,-id,-ic],
    curvature[-ia,-ib,-ic,-id]-curvature[-ic,-id,-ia,-ib],
    curvature[-ia,-ib,-ic,-id]+curvature[-ia,-ic,-id,-ib]+curvature[-ia,-id,-ib,-ic]}),
  "AP02_GAUSS_BLOCK"->reduce[projectedGauss-gauss[-ia,-ib,-ic,-id]],
  "AP03_CODAZZI_BLOCK"->reduce[projectedMixed-mixed[-ia,-ib,-ic]],
  "AP04_NORMAL_RICCI_BLOCK"->reduce[projectedElectric-electric[-ia,-ib]],
  "AP05_HAMILTONIAN_PROJECTION"->reduce[hActual-hExpected],
  "AP06_MOMENTUM_PROJECTION"->reduce[mActual-mExpected],
  "AP07_SPATIAL_TRACE_PROJECTION"->reduce[pActual-pExpected],
  "AP08_SPATIAL_PSTF_PROJECTION"->reduce[sActual-sExpected],
  "AP09_FULL_RESIDUAL_RECONSTRUCTION"->reduce[eActual-reconstructed],
  "AP10_EXISTING_CONSUMER_ADAPTER"->MapThread[reduce[#1-#2]&,{shearValues,sourceValues}],
  "AP11_LIE_METRIC_TRACE_ADAPTER"->{reduce[lieMetric-nu[ia]acc[ib]-nu[ib]acc[ia]+2 KK[ia,ib]],scalarTraceCheck},
  "AP12_TRACE_MUTATION_NONZERO_WITNESS"->{reduce[traceMutation-4(3 HH[]^2+trace[sigmaSquared])/3],reduce[mutationWitness-4]}|>;
 <|"scope"->"CONDITIONAL_ABSTRACT_CURVATURE_BLOCK_CONTRACTION_ONLY",
   "residuals"->residuals,
   "computed_projections"->AssociationThread[{"Hamiltonian","Momentum","SpatialTrace","SpatialPSTF"},
     ToString[#,InputForm]& /@ {hActual,mActual,pActual,sActual}],
   "computed_shear_chart"->(ToString[#,InputForm]& /@ shearValues),
   "raw_trace_mutation"->ToString[traceMutation,InputForm],
   "trace_mutation_fixed_reference_witness"->ToString[mutationWitness,InputForm],
   "premises"->{"unit timelike hypersurface-orthogonal normal", "positive K",
     "3D intrinsic curvature reconstruction", "Gauss/Codazzi/Ricci block identities",
     "spatial symmetric K and covariant-index LieK", "D_a A_b symmetric", "spatial STF matter anisotropic stress"},
   "curvature_definition_to_blocks_verified"->False,
   "general_native_bridge_admitted"->False,"production_admitted"->False|>
];
End[];
EndPackage[];
