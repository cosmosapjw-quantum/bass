Needs["xAct`xTensor`"];
xAct`xTensor`$DefInfoQ=False;
DefManifold[EVAXM,4,{a,b,c,d,e,f}];
DefMetric[-1,g[-a,-b],CD,{";","D"}];
DefTensor[u[a],EVAXM];
DefTensor[n[a],EVAXM];
DefTensor[ray[a],EVAXM];
DefConstantSymbol[Ssh];
DefConstantSymbol[Pps];
DefConstantSymbol[mu];
DefConstantSymbol[Ef];
DefConstantSymbol[Cc];
rules=Join@@(MakeRule[#,MetricOn->All,ContractMetrics->True]&/@{
{u[a]u[-a],-1},{n[a]n[-a],1},{ray[a]ray[-a],1},
{u[a]n[-a],0},{u[a]ray[-a],0},{n[a]ray[-a],mu}});
cn[ex_]:=FullSimplify[FixedPoint[ToCanonical[ContractMetric[Expand[#/.rules]]]&,ex,12]];
h[a_,b_]:=g[a,b]+u[a]u[b];
sh[a_,b_]:=Ssh(3n[a]n[b]-h[a,b]);
pi[a_,b_]:=Pps(3n[a]n[b]-h[a,b]);
screen[a_,b_]:=h[a,b]-ray[a]ray[b];
p[a_]:=(Ef/Cc)(u[a]+ray[a]);
checks=<|
 "ShearPSTFTrace"->cn[sh[a,b]h[-a,-b]],
 "AnisotropicStressPSTFTrace"->cn[pi[a,b]h[-a,-b]],
 "ShearNorm"->cn[sh[a,b]sh[-a,-b]/2-3Ssh^2],
 "ShearAnisStressContraction"->cn[sh[a,b]pi[-a,-b]-6Ssh Pps],
 "RadiationAngularPi"->cn[pi[a,b]ray[-a]ray[-b]-Pps(3mu^2-1)],
 "ScreenRank2"->cn[screen[a,-a]-2],
 "PhotonNull"->cn[p[a]p[-a]],
 "ObserverPhotonEnergy"->cn[-Cc u[-a]p[a]-Ef]
 |>;
out=<|"kernel"->System`$Version,"xTensor"->xAct`xTensor`$Version,
 "checks"->Map[ToString[#,InputForm]&,checks],
 "all_zero"->And@@Map[#===0&,Values[checks]],
 "scope"->"REI AX03 signature(-+++) LRS shear and independent π_ab; no collision/source closure proof"|>;
Export["/home/cosmosapjw/worktrees/bass-axbi-pi-stress-20261015/research/rei_axbi_initial_stress_20261015/evidence/XACT_INITIAL_STRESS.json",out,"RawJSON"];
Print[ExportString[out,"RawJSON"]];
If[TrueQ[out["all_zero"]],Exit[0],Exit[1]];