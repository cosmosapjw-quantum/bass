(* Independent energy-derivative and xAct LRS shear-stress check.
   Run: wolframscript -file xact_stable_pi.wl.  No shared evidence overwritten. *)
Needs["xAct`xTensor`"];
xAct`xTensor`$DefInfoQ=False;
DefManifold[StablePiSpacetime,4,{aa,bb,cc,dd}];
DefMetric[-1,ssmetric[-aa,-bb],SSCOV,{";","D"}];
DefTensor[timelike[aa],StablePiSpacetime];
DefTensor[axis[aa],StablePiSpacetime];
DefConstantSymbol[sh];DefConstantSymbol[ps];
rules=Join@@(MakeRule[#,MetricOn->All,ContractMetrics->True]&/@{
 {timelike[aa]timelike[-aa],-1},
 {axis[aa]axis[-aa],1},
 {timelike[aa]axis[-aa],0}});
canon[v_]:=FullSimplify[FixedPoint[ToCanonical[ContractMetric[Expand[#/.rules]]]&,v,12]];
spatial[aa_,bb_]:=ssmetric[aa,bb]+timelike[aa]timelike[bb];
shear[aa_,bb_]:=sh(3axis[aa]axis[bb]-spatial[aa,bb]);
stress[aa_,bb_]:=ps(3axis[aa]axis[bb]-spatial[aa,bb]);
tensor=<|
"shear_trace"->canon[shear[aa,bb]spatial[-aa,-bb]],
"stress_trace"->canon[stress[aa,bb]spatial[-aa,-bb]],
"shear_half_norm"->canon[shear[aa,bb]shear[-aa,-bb]/2-3sh^2],
"stress_shear_work"->canon[stress[aa,bb]shear[-aa,-bb]-6sh ps]
|>;
Clear[mass,qr,rad,beta,mu,amp];
k=rad^2 qr^2;
energy=Sqrt[mass^2+k(Exp[2beta](1-mu^2)+Exp[-4beta]mu^2)];
dp=k(Exp[-4beta]mu^2-Exp[2beta](1-mu^2)/2)/energy;
assumptions={mass>0,qr>0,rad>0,-1<=mu<=1,beta\[Element]Reals};
energyid=FullSimplify[dp+D[energy,beta]/2,Assumptions->assumptions];
sus=FullSimplify[
 Integrate[(D[dp,beta]/.beta->0),{mu,-1,1}]/2
 -k(-2/Sqrt[mass^2+k]+2k/(5(mass^2+k)^(3/2))),
 Assumptions->{mass>0,qr>0,rad>0}];
leg=(3mu^2-1)/2;
poly=FullSimplify[
 Integrate[(1+amp leg)*(leg+(Exp[-4beta]-1)mu^2-
     (Exp[2beta]-1)(1-mu^2)/2),{mu,-1,1}]/2
 -(amp/5+(Exp[-4beta]-1)(1/3+2amp/15)-
 (Exp[2beta]-1)(1/3-amp/15))
];
checks=Join[tensor,<|
"pressure_energy_derivative"->energyid,
"linear_susceptibility"->sus,
"angular_polynomial_exact"->poly|>];
result=<|
"schema"->"bass.rei.stable_pi.xact.v1",
"wolfram"->System`$Version,
"xTensor"->ToString[xAct`xTensor`$Version,InputForm],
"checks"->Map[ToString[#,InputForm]&,checks],
"all_zero"->And@@Map[TrueQ[#===0]&,Values[checks]],
"scope"->"LRS Bianchi I orthonormal shear/stress and exact massive kinetic angular identities"
|>;
out=FileNameJoin[{DirectoryName[$InputFileName],"evidence","XACT_STABLE_PI.json"}];
Export[out,result,"RawJSON"];
Print[ExportString[result,"RawJSON"]];
If[TrueQ[result["all_zero"]],Exit[0],Exit[1]];
