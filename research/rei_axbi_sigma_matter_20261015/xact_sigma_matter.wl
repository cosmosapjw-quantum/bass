Needs["xAct`xTensor`"];
xAct`xTensor`$DefInfoQ=False;
DefManifold[MbSigmaM,4,{a,b,c,d,e,f}];
DefMetric[-1,g[-a,-b],CD,{";","D"}];
DefTensor[uc[a],MbSigmaM];DefTensor[zz[a],MbSigmaM];DefTensor[nn[a],MbSigmaM];
DefConstantSymbol[s0];DefConstantSymbol[piR];DefConstantSymbol[piM];
DefConstantSymbol[mu];DefConstantSymbol[Eph];DefConstantSymbol[Cc];
rules=Join@@(MakeRule[#,MetricOn->All,ContractMetrics->True]&/@{
{uc[a]uc[-a],-1},{zz[a]zz[-a],1},{nn[a]nn[-a],1},
{uc[a]zz[-a],0},{uc[a]nn[-a],0},{zz[a]nn[-a],mu}});
cn[y_]:=FullSimplify[FixedPoint[ToCanonical[ContractMetric[Expand[#/.rules]]]&,y,12]];
h[a_,b_]:=g[a,b]+uc[a]uc[b];
B[a_,b_]:=3zz[a]zz[b]-h[a,b];
S[a_,b_]:=s0 B[a,b];
Pr[a_,b_]:=piR B[a,b];
Pm[a_,b_]:=piM B[a,b];
Pt[a_,b_]:=(piR+piM) B[a,b];
v[a_]:=(Eph/Cc)(uc[a]+nn[a]);
checks=<|
"TraceFreeShear"->cn[S[a,b]h[-a,-b]],
"ShearMagnitudeMinus3s2"->cn[S[a,b]S[-a,-b]/2-3s0^2],
"RadiationPiTrace"->cn[Pr[a,b]h[-a,-b]],
"MassiveMatterPiTrace"->cn[Pm[a,b]h[-a,-b]],
"TotalPiTrace"->cn[Pt[a,b]h[-a,-b]],
"RadiationShearPiContraction"->cn[S[a,b]Pr[-a,-b]-6s0*piR],
"MatterShearPiContraction"->cn[S[a,b]Pm[-a,-b]-6s0*piM],
"TotalShearPiContraction"->cn[S[a,b]Pt[-a,-b]-6s0(piR+piM)],
"PhotonNull"->cn[v[a]v[-a]],
"ObserverEnergySign"->cn[-Cc uc[-a]v[a]-Eph]|>;
r=<|"WolframVersion"->System`$Version,"xTensor"->xAct`xTensor`$Version,
"checks"->Map[ToString[#,InputForm]&,checks],
"all_zero"->And@@Map[#===0&,Values[checks]],
"scope"->"Source-locked SIGMA scalar, separate radiation and collisionless massive matter LRS tensor stress, no full REI chemistry source"|>;
Export["/home/cosmosapjw/worktrees/bass-axbi-sigma-massive-20261015/research/rei_axbi_sigma_matter_20261015/evidence/XACT_SIGMA_MATTER.json",r,"RawJSON"];
Print[ExportString[r,"RawJSON"]];
If[TrueQ[r["all_zero"]],Exit[0],Exit[1]];