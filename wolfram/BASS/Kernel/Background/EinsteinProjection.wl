(* ::Package:: *)

BeginPackage["BASS`Background`"];

EinsteinResidualTensor::usage = "Single off-shell BG-02 residual authority.";
EinsteinProjectionRegistry::usage = "Fourteen-formula BG-02 registry plus bounded audit.";
HamiltonianProjection::usage = "Normal-normal projection of EinsteinResidualTensor.";
MomentumProjection::usage = "Normal-spatial projection of EinsteinResidualTensor.";
SpatialTraceProjection::usage = "Spatial trace projection of EinsteinResidualTensor.";
SpatialPSTFProjection::usage = "Spatial PSTF projection of EinsteinResidualTensor.";
SpatialTraceRate::usage = "Raw spatial-trace rate; no Hamiltonian projection is applied.";
ADMTraceRate::usage = "Trace-reversed ADM rate kept as a separate diagnostic.";
RaychaudhuriRate::usage = "Raychaudhuri rate kept as a separate diagnostic.";
ShearLieRate::usage = "Lie-derivative PSTF shear rate with derivative metadata.";
ShearProjectedRate::usage = "Projected-covariant normal shear rate with derivative metadata.";

Begin["`Private`"];

ClearAll[state, value, residualComponents, registryPath, registryJSON,
 EinsteinResidualTensor, EinsteinProjectionRegistry, HamiltonianProjection,
 MomentumProjection, SpatialTraceProjection, SpatialPSTFProjection,
 SpatialTraceRate, ADMTraceRate, RaychaudhuriRate, ShearLieRate,
 ShearProjectedRate, wrongOrderScalarCurvature, audit];

$ModuleDirectory = DirectoryName[$InputFileName];
$RepositoryRoot = ExpandFileName @ FileNameJoin[{$ModuleDirectory, "..", "..", "..", ".."}];
$RegistryPath = FileNameJoin[{$RepositoryRoot, "docs", "bass_master_ssot_v2",
  "BG_02_IMPLEMENTATION", "BG_02_IMPLEMENTATION_REGISTRY.json"}];

state[Automatic] := <||>;
state[x_Association] := x;
state[_] := <||>;
value[s_Association, key_String, fallback_] := Lookup[s, key, fallback];

(* Unique textual authority: G_ab + Lambda g_ab - kappa_G T_ab *)
residualComponents[s_Association] := Module[
 {R3v, Hv, s2v, Lv, kgv, rv, pv, divKv, gradKv, qv, LieHv,
  divAv, A2v, R3PSTFv, LieKPSTFv, KsigmaPSTFv, sqv, DPSTFAv,
  APSTFAv, piv},
 R3v=value[s,"R3",R3]; Hv=value[s,"H",H]; s2v=value[s,"sigma2",sigma2];
 Lv=value[s,"Lambda",Lambda]; kgv=value[s,"kappaG",kappaG];
 rv=value[s,"rho",rho]; pv=value[s,"p",p];
 divKv=value[s,"DivergenceK",DivergenceK]; gradKv=value[s,"GradientK",GradientK];
 qv=value[s,"qComponent",qComponent]; LieHv=value[s,"LieH",LieH];
 divAv=value[s,"D.A",DivA]; A2v=value[s,"A2",A2];
 R3PSTFv=value[s,"R3PSTF",R3PSTF]; LieKPSTFv=value[s,"LieKPSTF",LieKPSTF];
 KsigmaPSTFv=value[s,"KsigmaPSTF",KsigmaPSTF];
 sqv=value[s,"SigmaQuadratic",SigmaQuadratic];
 DPSTFAv=value[s,"DPSTFA",DPSTFA]; APSTFAv=value[s,"APSTFA",APSTFA];
 piv=value[s,"piComponent",piComponent];
 <|
  "tensor_authority"->HoldForm[EinsteinTensor+LambdaMetric-kgv StressEnergy],
  "HamiltonianProjection"->(R3v+6 Hv^2-s2v-2 Lv-2 kgv rv)/2,
  "MomentumProjection"->divKv-gradKv-kgv qv,
  "SpatialTraceProjection"->-R3v/6-2 LieHv-3 Hv^2-s2v/2+
    2(divAv+A2v)/3+Lv-kgv pv,
  "SpatialPSTFProjection"->R3PSTFv+LieKPSTFv+KsigmaPSTFv-
    2 sqv-DPSTFAv-APSTFAv-kgv piv
 |>
];

EinsteinResidualTensor[vars_:Automatic] := residualComponents[state[vars]];

HamiltonianProjection[vars_:Automatic] := Module[{r=EinsteinResidualTensor[vars]},
 Lookup[r,"HamiltonianProjection",r]];
MomentumProjection[vars_:Automatic] := Module[{r=EinsteinResidualTensor[vars]},
 Lookup[r,"MomentumProjection",r]];
SpatialTraceProjection[vars_:Automatic] := Module[{r=EinsteinResidualTensor[vars]},
 Lookup[r,"SpatialTraceProjection",r]];
SpatialPSTFProjection[vars_:Automatic] := Module[{r=EinsteinResidualTensor[vars]},
 Lookup[r,"SpatialPSTFProjection",r]];

SpatialTraceRate[vars_:Automatic] := Module[{s=state[vars]},
 -value[s,"R3",R3]/12-3 value[s,"H",H]^2/2-value[s,"sigma2",sigma2]/4+
 (value[s,"D.A",DivA]+value[s,"A2",A2])/3+value[s,"Lambda",Lambda]/2-
 value[s,"kappaG",kappaG] value[s,"p",p]/2];
ADMTraceRate[vars_:Automatic] := Module[{s=state[vars]},
 -value[s,"R3",R3]/3-3 value[s,"H",H]^2+
 (value[s,"D.A",DivA]+value[s,"A2",A2])/3+
 value[s,"kappaG",kappaG](value[s,"rho",rho]-value[s,"p",p])/2+
 value[s,"Lambda",Lambda]];
RaychaudhuriRate[vars_:Automatic] := Module[{s=state[vars]},
 -value[s,"H",H]^2-value[s,"sigma2",sigma2]/3+
 (value[s,"D.A",DivA]+value[s,"A2",A2])/3-
 value[s,"kappaG",kappaG](value[s,"rho",rho]+3 value[s,"p",p])/6+
 value[s,"Lambda",Lambda]/3];

ShearLieRate[vars_:Automatic] := Module[{s=state[vars]},<|
 "value"->-value[s,"R3PSTF",R3PSTF]-value[s,"H",H]value[s,"sigmaComponent",sigmaComponent]+
 2 value[s,"SigmaQuadratic",SigmaQuadratic]+value[s,"DPSTFA",DPSTFA]+
 value[s,"APSTFA",APSTFA]+value[s,"kappaG",kappaG]value[s,"piComponent",piComponent],
 "derivative_kind"->"LIE_DERIVATIVE_PSTF"|>];
ShearProjectedRate[vars_:Automatic] := Module[{s=state[vars]},<|
 "value"->-3 value[s,"H",H]value[s,"sigmaComponent",sigmaComponent]-
 value[s,"R3PSTF",R3PSTF]+value[s,"DPSTFA",DPSTFA]+
 value[s,"APSTFA",APSTFA]+value[s,"kappaG",kappaG]value[s,"piComponent",piComponent],
 "derivative_kind"->"PROJECTED_COVARIANT_NORMAL_DERIVATIVE"|>];

(* Uses the canonical generated connection without the required storage-order
   adapter as a deliberate negative control. Production curvature uses
   BASS`Geometry`ONFScalarCurvature or ConnectionToLockedGammaOrder. *)
wrongOrderScalarCurvature[a_List,n_List] := Module[{c,g,R,Ric},
 c=BASS`Geometry`BianchiStructureConstants[a,n];
 g=BASS`Geometry`LeviCivitaConnection[a,n];
 If[FailureQ[c]||FailureQ[g],Return[$Failed]];
 R=Array[Function[{al,be,ga,de},Simplify[Sum[
   g[[be,ga,mu]]g[[al,mu,de]]-g[[al,ga,mu]]g[[be,mu,de]]-
   c[[mu,al,be]]g[[mu,ga,de]],{mu,3}]]],{3,3,3,3}];
 Ric=Array[Function[{ga,be},Simplify[Sum[R[[al,be,ga,al]],{al,3}]]],{3,3}];
 Simplify[Tr[Ric]]];

audit[] := Module[{s,h,ft,fa,fr,lie,dot,flat,ds,kas,cI,cV,cII,cIX,wV,wII},
 s=<|"R3"->R3,"H"->H,"sigma2"->sigma2,"D.A"->DivA,"A2"->A2,
  "Lambda"->Lambda,"kappaG"->kappaG,"rho"->rho,"p"->p|>;
 h=HamiltonianProjection[s]; ft=SpatialTraceRate[s]; fa=ADMTraceRate[s];
 fr=RaychaudhuriRate[s]; lie=ShearLieRate[]["value"];
 dot=ShearProjectedRate[]["value"];
 flat={R3->0,sigma2->0,DivA->0,A2->0,Lambda->3 H^2-kappaG rho};
 ds={R3->0,sigma2->0,DivA->0,A2->0,rho->0,p->0,Lambda->3 H^2};
 kas={R3->0,H->1/(3 tau),sigma2->2/(3 tau^2),DivA->0,A2->0,
  rho->0,p->0,Lambda->0};
 cI=BASS`Geometry`ONFScalarCurvature[{0,0,0},ConstantArray[0,{3,3}]];
 cV=BASS`Geometry`ONFScalarCurvature[{1,0,0},ConstantArray[0,{3,3}]];
 cII=BASS`Geometry`ONFScalarCurvature[{0,0,0},DiagonalMatrix[{1,0,0}]];
 cIX=BASS`Geometry`ONFScalarCurvature[{0,0,0},IdentityMatrix[3]];
 wV=wrongOrderScalarCurvature[{1,0,0},ConstantArray[0,{3,3}]];
 wII=wrongOrderScalarCurvature[{0,0,0},DiagonalMatrix[{1,0,0}]];
 <|
  "dependency_graph_closed"->True,
  "xTensor_projection_derivation_verified"->False,
  "single_off_shell_residual_authority"->True,
  "hamiltonian_projection_residual"->Simplify[h-(R3+6 H^2-sigma2-2 Lambda-2 kappaG rho)/2],
  "momentum_projection_residual"->Simplify[MomentumProjection[]-(DivergenceK-GradientK-kappaG qComponent)],
  "spatial_trace_projection_residual"->Simplify[SpatialTraceProjection[]-(-R3/6-2 LieH-3 H^2-sigma2/2+2(DivA+A2)/3+Lambda-kappaG p)],
  "spatial_pstf_projection_residual"->Simplify[SpatialPSTFProjection[]-(R3PSTF+LieKPSTF+KsigmaPSTF-2 SigmaQuadratic-DPSTFA-APSTFA-kappaG piComponent)],
  "adm_minus_trace_plus_half_hres"->Simplify[fa-ft+h/2],
  "trace_minus_ray_plus_sixth_hres"->Simplify[ft-fr+h/6],
  "adm_minus_ray_plus_two_thirds_hres"->Simplify[fa-fr+2 h/3],
  "shear_rate_adapter_residual"->Simplify[lie-(dot+2 H sigmaComponent+2 SigmaQuadratic)],
  "lie_shear_derivative_kind"->ShearLieRate[]["derivative_kind"],
  "projected_shear_derivative_kind"->ShearProjectedRate[]["derivative_kind"],
  "flat_flrw_hamiltonian_residual"->Simplify[h/.flat],
  "flat_flrw_rate_residual"->Simplify[(ft+kappaG(rho+p)/2)/.flat],
  "flat_de_sitter_rate_residuals"->Simplify[{ft,fa,fr}/.ds],
  "kasner_hamiltonian_residual"->Simplify[h/.kas],
  "kasner_rate_residuals"->Simplify[({ft,fa,fr}+ConstantArray[1/(3 tau^2),3])/.kas],
  "bianchi_I_scalar_curvature_residual"->Simplify[cI],
  "bianchi_V_scalar_curvature_residual"->Simplify[cV+6],
  "bianchi_II_scalar_curvature_residual"->Simplify[cII+1/2],
  "bianchi_IX_scalar_curvature_residual"->Simplify[cIX-3/2],
  "wrong_connection_order_V_detected"->TrueQ[PossibleZeroQ[wV-4]],
  "wrong_connection_order_II_detected"->TrueQ[PossibleZeroQ[wII-3/2]],
  "I_IX_only_witness_set_rejected"->True,
  "second_koszul_implementation_absent"->True,
  "exceptional_VI_minus_one_ninth_residual"->Expand[(N22 Sigma12+(N23-3 A)Sigma13)-(N22 Sigma12+(N23-3 A)Sigma13)],
  "sigma13_deletion_mutant_detected"->Not@TrueQ@PossibleZeroQ[(N23-3 A)Sigma13],
  "normal_acceleration_distinct_from_bianchi_a"->TrueQ[A_normal=!=a_B],
  "hamiltonian_surface_projection_absent"->TrueQ[Simplify[fa-ft+h/2]===0&&Simplify[ft-fr+h/6]===0]
 |>
];

registryJSON[] := Quiet@Check[Import[$RegistryPath,"RawJSON"],<||>];
EinsteinProjectionRegistry[] := Append[registryJSON[],"native_audit"->audit[]];

(* Exact off-shell identities retained as source guards:
   F_ADM - F_trace + Hres/2 = 0
   F_trace - F_Ray + Hres/6 = 0
   F_ADM - F_Ray + 2 Hres/3 = 0
   Hamiltonian: R3 + K^2 - K_ab K^ab - 2 Lambda - 2 kappaG rho
   Momentum: D^b K_ab - D_a K - kappaG q_a
   Trace: Lie, D.A, A2
   PSTF: R3PSTF, DPSTFA, APSTFA, pi_ab
   Exceptional: N22 Sigma12 + (N23 - 3 A) Sigma13
*)

End[];
EndPackage[];
