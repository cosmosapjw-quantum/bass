Needs["xAct`xTensor`"];
xAct`xTensor`$DefInfoQ=False;
DefManifold[C7M,4,{a,b,d,e,f,h}];
DefMetric[-1,g[-a,-b],CD,{";","D"}];
DefTensor[uc[a],C7M];DefTensor[nc[a],C7M];
DefConstantSymbol[Eph];DefConstantSymbol[Clight];
rules=Join@@(MakeRule[#,MetricOn->All,ContractMetrics->True]&/@{
 {uc[a]uc[-a],-1},{nc[a]nc[-a],1},{uc[a]nc[-a],0}});
cn[x_]:=FullSimplify[FixedPoint[ToCanonical[ContractMetric[Expand[#/.rules]]]&,x,12]];
qq[a_,b_]:=g[a,b]+uc[a]uc[b]-nc[a]nc[b];
kk[a_]:=(Eph/Clight)(uc[a]+nc[a]);
res=<|"ScreenTrace"->cn[qq[a,-a]-2],
"ScreenObserverTransverse"->cn[qq[a,-b]uc[b]],
"ScreenRayTransverse"->cn[qq[a,-b]nc[b]],
"ScreenIdempotent"->cn[qq[a,-b]qq[b,-d]-qq[a,-d]],
"PhotonNull"->cn[kk[a]kk[-a]],
"ObserverPhotonRestEnergy"->cn[-Clight uc[-a]kk[a]-Eph],
"ScreenPhotonZero"->cn[qq[a,-b]kk[b]]|>;
o=<|"kernel"->System`$Version,
"xTensorVersion"->xAct`xTensor`$Version,
"checks"->Map[ToString[#,InputForm]&,res],
"all_zero"->And@@Map[#===0&,Values[res]],
"scope"->"C7 local geometric tetrad screen and photon sign convention; no chemical solver"|>;
Export["/home/cosmosapjw/worktrees/bass-fa03-c7-polarized-batch-20261015/research/fa03_c7_polarized_batch_20261015/evidence/XACT_C7.json",o,"RawJSON"];
Print[ExportString[o,"RawJSON"]];
If[TrueQ[o["all_zero"]],Exit[0],Exit[1]];