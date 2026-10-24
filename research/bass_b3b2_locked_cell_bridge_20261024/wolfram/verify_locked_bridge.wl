ClearAll["Global`*"];
cpu0=TimeUsed[];
run=AbsoluteTiming[
 dirs=Join[IdentityMatrix[3],-IdentityMatrix[3]];
 a=ConstantArray[1/6,6]; gs={3,7}; ps={2,5};
 fs=Table[(1+i/3)(1+dirs[[j,1]]/5+(dirs[[j,2]]^2-dirs[[j,3]]^2)/7),{i,2},{j,6}];
 ns=Flatten[Table[gs[[i]]a[[j]]fs[[i,j]],{i,2},{j,6}]];
 ell=Flatten[Table[Prepend[dirs[[j]],1],{i,2},{j,6}],1];
 pp=Flatten[Table[ps[[i]],{i,2},{j,6}]];
 alpha=11; cc=7; pstar=13; p4=MapThread[(#1/pstar)#2&,{pp,ell}]; ww=alpha cc pstar ns;
 nref=cc Total[MapThread[#1 #2&,{ns,ell}]];
 tref=Total[MapThread[cc #1 #2 Outer[Times,#3,#3]&,{pp,ns,ell}]];
 nfun[q_,w_]:=Total[MapThread[#1 #2/#2[[1]]&,{w,q}]]/(alpha pstar);
 tfun[q_,w_]:=Total[MapThread[(#1/#2[[1]])Outer[Times,#2,#2]&,{w,q}]];
 boost[b_]:=Module[{g=1/Sqrt[1-b.b],bb=IdentityMatrix[4]},
 bb[[1,1]]=g;bb[[1,2;;4]]=g b;bb[[2;;4,1]]=g b;
 bb[[2;;4,2;;4]]+=g^2/(g+1)Outer[Times,b,b];bb];
 res=<|"number_map"->FullSimplify[nfun[p4,ww]-nref],
 "tensor_map"->FullSimplify[tfun[p4,ww]-alpha tref],
 "massless_trace"->Tr[DiagonalMatrix[{-1,1,1,1}].tref],
 "fixed_grid_inverse"->Flatten[Table[ww[[(i-1)6+j]]/(alpha cc pstar gs[[i]]a[[j]])-fs[[i,j]],{i,2},{j,6}]],
 "vacuum_number"->nfun[p4,0 ww],"vacuum_tensor"->tfun[p4,0 ww],
 "unit_cancellation"->{Together[(kap len^2 c0 p0 G0 A0 f0)(pRad/p0)-kap len^2 c0 pRad G0 A0 f0],Together[(kap len^2 c0 p0 G0 A0 f0)/(kap len^2 c0 p0 G0 A0)-f0]}|>;
 Do[bb=boost[betas[[q]]]; qb=FullSimplify[(bb.#)&/@p4]; wb=FullSimplify[MapThread[#1 #2[[1]]/#3[[1]]&,{ww,qb,p4}]];
 AssociateTo[res,"number_covariance_"<>ToString[q]->FullSimplify[nfun[qb,wb]-bb.nref]];
 AssociateTo[res,"tensor_covariance_"<>ToString[q]->FullSimplify[tfun[qb,wb]-alpha bb.tref.Transpose[bb]]];
 back=FullSimplify[(boost[-betas[[q]]].#)&/@qb];
 wback=FullSimplify[MapThread[#1 #2[[1]]/#3[[1]]&,{wb,back,qb}]];
 AssociateTo[res,"packet_roundtrip_"<>ToString[q]->FullSimplify[back-p4]];
 AssociateTo[res,"weight_roundtrip_"<>ToString[q]->FullSimplify[wback-ww]],
 {q,Length[betas={{3/5,0,0},{1/5,2/5,0}}]}];
 bb=boost[{3/5,0,0}]; qb=(bb.#)&/@p4;
 mutantN=FullSimplify[nfun[qb,ww]-bb.nref];
 mutantT=FullSimplify[tfun[qb,ww]-alpha bb.tref.Transpose[bb]];
 <|"group_count"->Length[res],"all_zero"->And@@(TrueQ[FullSimplify[#==0]]&/@Flatten[Values[res]]),
 "residuals"->res,"wrong_state_weight_number_residual"->mutantN,
 "wrong_state_weight_T00_residual"->mutantT[[1,1]],"positive_input"->And@@Thread[ns>0]|>
];
<|"kernel_wall_seconds"->run[[1]],"kernel_cpu_seconds"->(TimeUsed[]-cpu0),"result"->run[[2]]|>
