(* Source-independent analytic check of kinetic susceptibility and LRS GR tensor work.
   Wolfram 15 and local xAct xTensor. Metric signature (-,+,+,+).
   Output does not overwrite any original BASS or REI source evidence. *)
Needs["xAct`xTensor`"];
xAct`xTensor`$DefInfoQ=False;
DefManifold[MassStressNCP,4,{aa,bb,cc,dd}];
DefMetric[-1,mm[-aa,-bb],CovDer,{";","D"}];
DefTensor[normal[aa],MassStressNCP];
DefTensor[axis[aa],MassStressNCP];
DefConstantSymbol[ss];DefConstantSymbol[del];
rules=Join@@(MakeRule[#,MetricOn->All,ContractMetrics->True]&/@{
 {normal[aa]normal[-aa],-1},
 {axis[aa]axis[-aa],1},
 {normal[aa]axis[-aa],0}});
canon[v_]:=FullSimplify[FixedPoint[ToCanonical[ContractMetric[Expand[#/.rules]]]&,v,12]];
space[aa_,bb_]:=mm[aa,bb]+normal[aa]normal[bb];
shear[aa_,bb_]:=ss(3axis[aa]axis[bb]-space[aa,bb]);
pi[aa_,bb_]:=(del/3)(3axis[aa]axis[bb]-space[aa,bb]);
tensor=<|
 "shear_trace"->canon[shear[aa,bb]space[-aa,-bb]],
 "stress_trace"->canon[pi[aa,bb]space[-aa,-bb]],
 "shear_half_norm"->canon[shear[aa,bb]shear[-aa,-bb]/2-3ss^2],
 "stress_shear_work"->canon[shear[aa,bb]pi[-aa,-bb]-2ss del]|>;
Clear[mass,q,r,beta,mu];
k=r^2 q^2;
f=Exp[2beta](1-mu^2)+Exp[-4beta]mu^2;
ee=Sqrt[mass^2+k f];
ls=Exp[-4beta]mu^2-Exp[2beta](1-mu^2)/2;
dpe=k ls/ee;
pebar=k f/(3ee);
susp=k*(-4Exp[-4beta]mu^2-Exp[2beta](1-mu^2))/ee+2(k ls)^2/ee^3;
condition={mass>0,q>0,r>0,-1<=mu<=1,beta\[Element]Reals};
physics=<|
 "DeltaP_minus_half_energy_b"->FullSimplify[dpe+D[ee,beta]/2,Assumptions->condition],
 "analytic_susceptibility"->FullSimplify[D[dpe,beta]-susp,Assumptions->condition],
 "canonical_expansion_energy_work"->FullSimplify[
    -r D[r^3 ee,r]+3r^3(ee+pebar),Assumptions->condition],
 "mass_shell_LRS_positive_energy"->FullSimplify[
    ee^2-mass^2-k f,Assumptions->condition]|>;
checks=Join[tensor,physics];
receipt=<|"schema"->"bass.rei.native_stress.xact_susceptibility.v1",
 "wolfram_version"->System`$Version,"xTensor"->ToString[xAct`xTensor`$Version,InputForm],
 "checks"->Map[ToString[#,InputForm]&,checks],
 "zero_count"->Count[Values[checks],0],
 "all_zero"->And@@Map[TrueQ[#===0]&,Values[checks]],
 "scope"->"LRS massive collisionless FD matter, source-independent local tensor and distribution stress identities"|>;
out=FileNameJoin[{DirectoryName[$InputFileName],"evidence","XACT_JACOBIAN.json"}];
Export[out,receipt,"RawJSON"];
Print[ExportString[receipt,"RawJSON"]];
If[TrueQ[receipt["all_zero"]],Exit[0],Exit[1]];
