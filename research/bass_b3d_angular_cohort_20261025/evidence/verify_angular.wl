tStart=AbsoluteTime[]; cpuStart=TimeUsed[];
nn={x,y,z};
axes=Join[IdentityMatrix[3],-IdentityMatrix[3]];
corners=Tuples[{-1,1},3]/Sqrt[3];
edges=DeleteDuplicates[Flatten[Table[Permutations[{sx,sy,0}],{sx,{-1,1}},{sy,{-1,1}}],2]]/Sqrt[2];
points14=Join[axes,corners]; weights14=Join[ConstantArray[1/15,6],ConstantArray[3/40,8]];
points26=Join[axes,edges,corners]; weights26=Join[ConstantArray[1/21,6],ConstantArray[4/105,12],ConstantArray[9/280,8]];
moment[e_List]:=If[AnyTrue[e,OddQ],0,Times@@(Factorial2[#-1]&/@e)/Factorial2[Total[e]+1]];
average[pol_]:=Total[(#[[2]]*moment[#[[1]]])&/@CoefficientRules[Expand[pol],nn]];
rule[pol_,points_,weights_]:=Expand[Total[MapThread[#1*(pol/.Thread[nn->#2])&,{weights,points}]]];
d14[pol_]:=Simplify[rule[pol,points14,weights14]-average[pol]];
d26[pol_]:=Simplify[rule[pol,points26,weights26]-average[pol]];
powers5=Select[Tuples[Range[0,5],3],Total[#]<=5&];
powers7=Select[Tuples[Range[0,7],3],Total[#]<=7&];
exact5=DeleteDuplicates[d14[Times@@(nn^#)]&/@powers5];
exact7=DeleteDuplicates[d26[Times@@(nn^#)]&/@powers7];
bb={3/10,-1/10,-1/5}; ss=bb/2;
qA=1+Total[ss*nn^2];
zser=Normal[Series[Total[nn^2*(Exp[-2*eta*bb]-1)],{eta,0,4}]];
sq=Normal[Series[Sqrt[1+zser],{eta,0,4}]];
isq=Normal[Series[(1+zser)^(-1/2),{eta,0,3}]];
pser[q_,i_]:=Normal[Series[Exp[-2*eta*bb[[i]]]*q*nn[[i]]^2*isq,{eta,0,3}]];
e14A=d14[Coefficient[Expand[qA*sq],eta,2]];
p14A=Table[d14[Coefficient[Expand[pser[qA,i]],eta,1]],{i,3}];
e140=d14[Coefficient[Expand[sq],eta,3]];
p140=Table[d14[Coefficient[Expand[pser[1,i]],eta,2]],{i,3}];
e26A=d26[Coefficient[Expand[qA*sq],eta,3]];
p26A=Table[d26[Coefficient[Expand[pser[qA,i]],eta,2]],{i,3}];
e260=d26[Coefficient[Expand[sq],eta,4]];
p260=Table[d26[Coefficient[Expand[pser[1,i]],eta,3]],{i,3}];
groups={
 Total[weights14]-1, Total[weights26]-1, exact5, exact7,
 {d14[x^6],d14[x^4*y^2],d14[x^2*y^2*z^2]}-{4/315,-2/315,4/315},
 {d26[x^8],d26[x^6*y^2],d26[x^4*y^4],d26[x^4*y^2*z^2]}-{2/315,-1/315,1/315,0},
 e14A+9/35000,p14A-{13,-11,-2}/10500,
 e140+9/17500,p140-{13,-11,-2}/3500,
 e26A+7/100000,p26A-{9,-3,-6}/20000,
 e260+7/40000,p260-{3,-1,-2}/2000,
 Total[p14A],Total[p140],Total[p26A],Total[p260]};
delta=Tanh[1/2]; a0=(Exp[2/5]+Exp[-3/5])/2; kk=40;
tailS=Abs[Binomial[1/2,kk+1]]*delta^(kk+1)/(1-delta);
tailI=Abs[Binomial[-1/2,kk+1]]*delta^(kk+1)/(1-delta);
ExportString[<|"kernel_version"->$Version,"group_count"->Length[groups],
"residual_groups"->groups,"all_zero"->AllTrue[Flatten[groups],#===0&],
"positive_weights"->And@@Thread[Join[weights14,weights26]>0],
"monomials_checked_14"->Length[powers5],"monomials_checked_26"->Length[powers7],
"main_coefficients"-><|"Q14_ANISO_energy"->ToString[e14A,InputForm],"Q14_ANISO_pressure"->ToString[p14A,InputForm],
"Q14_ISO_energy"->ToString[e140,InputForm],"Q14_ISO_pressure"->ToString[p140,InputForm],
"Q26_ANISO_energy"->ToString[e26A,InputForm],"Q26_ANISO_pressure"->ToString[p26A,InputForm],
"Q26_ISO_energy"->ToString[e260,InputForm],"Q26_ISO_pressure"->ToString[p260,InputForm]|>,
"K40_ideal_energy_bound"->N[2*Sqrt[a0]*tailS,20],
"K40_ideal_pressure_bound"->N[2*Exp[2/5]/Sqrt[a0]*tailI,20],
"minimum_q"->9/10,"largest_final_redshift_factor"->N[Exp[-1/5],20],
"wall_seconds"->N[AbsoluteTime[]-tStart],"cpu_seconds"->N[TimeUsed[]-cpuStart]|>,"RawJSON"]
