Needs["xAct`xTensor`"];
xAct`xTensor`$DefInfoQ=False;
DefManifold[ST,4,{a,b,d,e,f,j}];
DefMetric[-1,g[-a,-b],CD,{";","D"}];
DefTensor[u[a],ST];DefTensor[n[a],ST];DefTensor[z[a],ST];
DefConstantSymbol[cphys];DefConstantSymbol[ene];DefConstantSymbol[sh];
DefConstantSymbol[bc];DefConstantSymbol[bs];DefConstantSymbol[mu];
rules=Join@@(MakeRule[#,MetricOn->All,ContractMetrics->True]&/@{{u[a]u[-a],-1},{n[a]n[-a],1},{z[a]z[-a],1},{u[a]n[-a],0},{u[a]z[-a],0},{n[a]z[-a],mu}});
can[expr_]:=FullSimplify[FixedPoint[ToCanonical[ContractMetric[Expand[#/.rules]]]&,expr,12],bc^2-bs^2==1];
hh[a_,b_]:=g[a,b]+u[a]u[b];
ss[a_,b_]:=sh(3z[a]z[b]-hh[a,b]);
screen[a_,b_]:=hh[a,b]-n[a]n[b];
pp[a_]:=(ene/cphys)(u[a]+n[a]);
ww[a_]:=bc u[a]+bs z[a];
checks=<|
 "NullPhoton"->can[pp[a]pp[-a]],
 "PhysicalEnergy"->can[-cphys u[-a]pp[a]-ene],
 "BoostEnergy"->can[-cphys ww[-a]pp[a]-ene(bc-bs mu)],
 "ScreenTraceTwo"->can[screen[a,-a]-2],
 "ScreenIdempotent"->can[screen[a,-d]screen[d,b]-screen[a,b]],
 "ScreenKillsPhoton"->can[screen[a,-b]pp[b]],
 "ShearTraceZero"->can[ss[a,-a]],
 "ShearSquaredHalf"->can[ss[a,b]ss[-a,-b]/2-3sh^2],
 "ShearCubic"->can[ss[a,-b]ss[b,-d]ss[d,-a]-6sh^3],
 "IsotropicLinearScalarZero"->can[ss[a,b]hh[-a,-b]/3]
|>;
result=<|"WolframVersion"->System`$Version,"xTensorVersion"->xAct`xTensor`$Version,"Checks"->Map[ToString[#,InputForm]&,checks],"AllCheckedZero"->And@@Map[#===0&,Values[checks]]|>;
Export["/home/cosmosapjw/archives/BASS_FA03_REI_THEORY_20261014/xact_result.json",result,"RawJSON"];
Print[ExportString[result,"RawJSON"]];
If[TrueQ[result["AllCheckedZero"]],Exit[0],Exit[1]];
