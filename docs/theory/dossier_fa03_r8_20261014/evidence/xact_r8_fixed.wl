Needs["xAct`xTensor`"];
xAct`xTensor`$DefInfoQ = False;
DefManifold[FA8,4,{a,b,d,e,f,j}];
DefMetric[-1, g[-a,-b], CD, {";","D"}];
DefTensor[uu[a],FA8]; DefTensor[zz[a],FA8]; DefTensor[nn[a],FA8];
DefConstantSymbol[s];DefConstantSymbol[v];DefConstantSymbol[gg];DefConstantSymbol[mu];
DefConstantSymbol[en];DefConstantSymbol[cc];
rules=Join@@(MakeRule[#,MetricOn->All,ContractMetrics->True]&/@{{uu[a]uu[-a],-1},{zz[a]zz[-a],1},{nn[a]nn[-a],1},{uu[a]zz[-a],0},{uu[a]nn[-a],0},{nn[a]zz[-a],mu}});
can[expr_]:=FullSimplify[FixedPoint[ToCanonical[ContractMetric[Expand[#/.rules]]]&,expr,12],gg^2(1-v^2)==1];
hh[a_,b_]:=g[a,b]+uu[a]uu[b];
ss[a_,b_]:=s(3zz[a]zz[b]-hh[a,b]);
scre[a_,b_]:=hh[a,b]-nn[a]nn[b];
pp[a_]:=(en/cc)(uu[a]+nn[a]);
ww[a_]:=gg(uu[a]+v zz[a]);
tests=<|
"HalfShearSquare"->can[ss[a,b]ss[-a,-b]/2-3s^2],
"OddCubicShear"->can[ss[a,-b]ss[b,-d]ss[d,-a]-6s^3],
"LinearIsotropicScalarNull"->can[ss[a,b]hh[-a,-b]],
"ScreenRankTwo"->can[scre[a,-a]-2],
"ScreenTransverse"->can[scre[a,-b]pp[b]],
"EnergyDefinition"->can[-cc uu[-a] pp[a]-en],
"BoostRestEnergy"->can[-cc ww[-a]pp[a]-en gg(1-v mu)]
|>;
o=<|"kernel"->System`$Version,"xTensorVersion"->xAct`xTensor`$Version,"residuals"->Map[ToString[#,InputForm]&,tests],"all_zero"->And@@Map[#===0&,Values[tests]],"scope"->"REI LRS Bianchi I kinematic signature and finite photon observer boost; no physical chemistry simulation"|>;
Export["/home/cosmosapjw/archives/BASS_FA03_R8_RESULT_20261014/xact_r8_fixed.json",o,"RawJSON"];Print[ExportString[o,"RawJSON"]];
If[TrueQ[o["all_zero"]],Exit[0],Exit[1]];
