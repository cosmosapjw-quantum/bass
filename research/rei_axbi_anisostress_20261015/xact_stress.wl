Needs["xAct`xTensor`"];
xAct`xTensor`$DefInfoQ=False;
DefManifold[PiBIM,4,{a,b,c,d,e,f}];
DefMetric[-1,g[-a,-b],CD,{";","D"}];
DefTensor[u[a],PiBIM];DefTensor[zz[a],PiBIM];DefTensor[nn[a],PiBIM];
DefConstantSymbol[ss];DefConstantSymbol[dd];DefConstantSymbol[muu];DefConstantSymbol[Eph];DefConstantSymbol[Cc];
cons=Join@@(MakeRule[#,MetricOn->All,ContractMetrics->True]&/@{
{u[a]u[-a],-1},{zz[a]zz[-a],1},{nn[a]nn[-a],1},
{u[a]zz[-a],0},{u[a]nn[-a],0},{zz[a]nn[-a],muu}});
cn[exp_]:=FullSimplify[FixedPoint[ToCanonical[ContractMetric[Expand[#/.cons]]]&,exp,10]];
h[a_,b_]:=g[a,b]+u[a]u[b];
basis[a_,b_]:=3zz[a]zz[b]-h[a,b];
sig[a_,b_]:=ss basis[a,b];
pi[a_,b_]:=(dd/3)basis[a,b];
p[a_]:=(Eph/Cc)(u[a]+nn[a]);
checks=<|
"shear_traceless"->cn[sig[a,b]h[-a,-b]],
"pi_traceless"->cn[pi[a,b]h[-a,-b]],
"sigma_norm_half_minus_3s2"->cn[sig[a,b]sig[-a,-b]/2-3ss^2],
"shear_pi_contraction_minus_2s_deltaP"->cn[sig[a,b]pi[-a,-b]-2ss dd],
"ray_shear_projection_minus_s_3mu2minus1"->cn[sig[a,b]nn[-a]nn[-b]-ss(3muu^2-1)],
"ray_pi_projection_minus_deltaP_over3_3mu2minus1"->cn[pi[a,b]nn[-a]nn[-b]-(dd/3)(3muu^2-1)],
"photon_null"->cn[p[a]p[-a]],
"observer_photon_energy"->cn[-Cc u[-a]p[a]-Eph]|>;
res=<|"WolframVersion"->System`$Version,"xTensorVersion"->xAct`xTensor`$Version,
"residuals"->Map[ToString[#,InputForm]&,checks],
"all_exact_zero"->And@@Map[#===0&,Values[checks]],
"scope"->"non-tilted LRS Bianchi I signature -+++ initial stress tensor geometry; no full matter Boltzmann source"|>;
Export["/home/cosmosapjw/worktrees/bass-axbi-anisostress-20261015/research/rei_axbi_anisostress_20261015/evidence/XACT_STRESS.json",res,"RawJSON"];
Print[ExportString[res,"RawJSON"]];
If[TrueQ[res["all_exact_zero"]],Exit[0],Exit[1]];