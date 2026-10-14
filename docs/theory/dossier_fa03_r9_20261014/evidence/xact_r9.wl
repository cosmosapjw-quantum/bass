Needs["xAct`xTensor`"];
xAct`xTensor`$DefInfoQ = False;
DefManifold[R9M, 4, {a,b,d,e,f,j}];
DefMetric[-1, g[-a,-b], CD, {";","D"}];
DefTensor[uu[a], R9M]; DefTensor[zz[a], R9M]; DefTensor[nn[a], R9M];
DefConstantSymbol[s]; DefConstantSymbol[v]; DefConstantSymbol[ga];
DefConstantSymbol[mu]; DefConstantSymbol[en]; DefConstantSymbol[cc]; DefConstantSymbol[deltaP];
rules = Join @@ (MakeRule[#, MetricOn->All, ContractMetrics->True]& /@
  {{uu[a]uu[-a], -1}, {zz[a]zz[-a], 1}, {nn[a]nn[-a], 1},
   {uu[a]zz[-a], 0}, {uu[a]nn[-a], 0}, {nn[a]zz[-a], mu}});
can[expr_] := FullSimplify[FixedPoint[ToCanonical[ContractMetric[Expand[#/.rules]]]&,expr,12],ga^2(1-v^2)==1];
hh[a_,b_] := g[a,b] + uu[a]uu[b];
sig[a_,b_] := s(3zz[a]zz[b]-hh[a,b]);
pa[a_,b_] := deltaP(zz[a]zz[b]-hh[a,b]/3);
screen[a_,b_] := hh[a,b]-nn[a]nn[b];
ph[a_] := (en/cc)(uu[a]+nn[a]);
obs[a_] := ga(uu[a]+v zz[a]);
tests = <|
 "CovariantTracefreeShear"->can[sig[a,b]hh[-a,-b]],
 "ProperHalfShearSquare"->can[sig[a,b]sig[-a,-b]/2-3s^2],
 "NonzeroCubicShear"->can[sig[a,-b]sig[b,-d]sig[d,-a]-6s^3],
 "RadiationShearWork"->can[sig[a,b]pa[-a,-b]-2s deltaP],
 "ScreenRank"->can[screen[a,-a]-2],
 "ScreenIdempotence"->can[screen[a,-b]screen[b,-d]-screen[a,-d]],
 "PhotonNullVector"->can[ph[a]ph[-a]],
 "ObserverRestEnergy"->can[-cc obs[-a]ph[a]-en ga(1-v mu)]
|>;
result = <|"kernel"->System`$Version,"xTensorVersion"->xAct`xTensor`$Version,
  "residuals"->Map[ToString[#,InputForm]&,tests],"all_zero"->And@@Map[#===0&,Values[tests]],
  "scope"->"xTensor symbolic LRS kinematics/screen photon and anisotropic shear-work; no reaction or numerical solver"|>;
Export["/home/cosmosapjw/archives/BASS_FA03_R9_CAS_20261014/xact_r9_result.json",result,"RawJSON"];
Print[ExportString[result,"RawJSON"]];
If[TrueQ[result["all_zero"]],Exit[0],Exit[1]];
