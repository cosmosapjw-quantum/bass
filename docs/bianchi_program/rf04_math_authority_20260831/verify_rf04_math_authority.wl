(* BASS RF04 exact formula replay. No production or RF04 promotion claim. *)
ClearAll["Global`*"];
zeroM[m_] := And @@ Flatten[Map[# === 0 &, m, {2}]];
zeroV[v_] := And @@ Map[# === 0 &, v];

e={e1,e2,e3}; a={a1,a2,a3}; om={o1,o2,o3};
sig={{s11,s12,s13},{s12,s22,s23},{s13,s23,-s11-s22}};
n={{n11,n12,n13},{n12,n22,n23},{n13,n23,n33}};
qs=e.sig.e; ss=-sig.e+qs e;
w=om+Cross[a,e]+n.e-(Tr[n]/2)e+Cross[e,ss];
codeV=Cross[w,e];
authV=Cross[om,e]+e(a.e)-a-Cross[e,n.e]-sig.e+qs e;
ass1=Element[Flatten[{e,a,om,sig,n}],Reals]&&e.e==1;
dirResidual=FullSimplify[codeV-authV,ass1];
tangentResidual=FullSimplify[e.codeV,ass1];
screenResidual=FullSimplify[e.w-(e.om+e.n.e-Tr[n]/2),ass1];

f=1/2{{i0+q0,u0-I v0},{u0+I v0,i0-q0}}; j2={{0,1},{-1,0}};
df=Expand[j2.f-f.j2];
dI=FullSimplify[df[[1,1]]+df[[2,2]]];
dQ=FullSimplify[df[[1,1]]-df[[2,2]]];
dU=FullSimplify[df[[1,2]]+df[[2,1]]];
dV=FullSimplify[I(df[[1,2]]-df[[2,1]])];
helicityResidual=FullSimplify[(dQ+I dU)+2I(q0+I u0)];

ee={x,y,z}; dop=g(1-v x); p=IdentityMatrix[3]-Outer[Times,ee,ee];
ep={g(x-v)/dop,y/dop,z/dop}; lor=DiagonalMatrix[{g,1,1}];
screen=Table[lor[[i]].p[[All,k]]+g v p[[1,k]]ep[[i]],{i,1,3},{k,1,3}];
pp=IdentityMatrix[3]-Outer[Times,ep,ep];
ass2=Element[{x,y,z,v,g},Reals]&&x^2+y^2+z^2==1&&g^2(1-v^2)==1&&g>0&&-1<v<1;
sourceIso=FullSimplify[Transpose[screen].screen-p,ass2];
targetIso=FullSimplify[screen.Transpose[screen]-pp,ass2];
nullResidual=FullSimplify[screen.ee,ass2];
muPrime=(x-v)/(1-v x);
jacResidual=FullSimplify[D[muPrime,x]-1/dop^2,ass2];

u={Cos[t],Sin[t]}; proj=Outer[Times,u,u]; pd=D[proj,t];
kato=pd.proj-proj.pd;
projResidual=FullSimplify[proj.proj-proj];
katoResidual=FullSimplify[pd-(kato.proj-proj.kato)];

aa={{aa11,aa12},{aa21,aa22}}; cc={{cc11,cc12},{cc21,cc22}}; id=IdentityMatrix[2];
ea=id+h aa/2+h^2 aa.aa/8+h^3 aa.aa.aa/48;
ec=id+h cc+h^2 cc.cc/2+h^3 cc.cc.cc/6;
m=Map[Normal@Series[#,{h,0,3}]&,ea.ec.ea,{2}]; xx=m-id;
lg=Map[Normal@Series[#,{h,0,3}]&,xx-xx.xx/2+xx.xx.xx/3,{2}];
cubic=Map[Expand@Coefficient[#,h,3]&,lg,{2}];
comm[x_,y_]:=x.y-y.x;
expected=-comm[aa,comm[aa,cc]]/24-comm[cc,comm[aa,cc]]/12;
bchResidual=FullSimplify[cubic-expected];

r={{1,0},{1/2,1/2}}; wc={1,1}; mix={{3/4,1/4},{1/4,3/4}};
uRound=2^-53; gamma3=FullSimplify[3uRound/(1-3uRound)];

checks=<|
 "direction_flow"->zeroV[dirResidual],
 "direction_tangency"->tangentResidual===0,
 "screen_rate"->screenResidual===0,
 "stokes"->And[dI===0,FullSimplify[dQ-2u0]===0,FullSimplify[dU+2q0]===0,dV===0,helicityResidual===0],
 "screen_source_isometry"->zeroM[sourceIso],
 "screen_target_isometry"->zeroM[targetIso],
 "screen_null"->zeroV[nullResidual],
 "solid_angle_jacobian"->jacResidual===0,
 "projector_idempotence"->zeroM[projResidual],
 "kato_transport"->zeroM[katoResidual],
 "strang_bch"->zeroM[bchResidual],
 "row_constant"->r.{1,1}==={1,1},
 "row_not_weighted_conservative"->wc.r-wc==={1/2,-1/2},
 "positive_mix_inverse_has_negative_entries"->Min[Flatten[Inverse[mix]]]<0,
 "gamma3_exact"->gamma3===3/(2^53-3)
|>;
If[!And@@Values[checks],Print["FAIL ",checks];Exit[1]];
receipt=<|"schema"->"bass.rf04.wolfram-replay.v1","status"->"PASS_EXACT_SYMBOLIC_FORMULA_CHECKS_ONLY","checks"->checks,"gamma3"->ToString[InputForm[gamma3]],"claimBoundary"->{"NO_PRODUCTION_CODE_EXECUTION","NO_NATIVE_OPERATOR_PARITY","NO_XACT_TENSOR_PROMOTION","NO_PASS_RF04"}|>;
Print[receipt];
If[Length[$ScriptCommandLine]>1,Export[$ScriptCommandLine[[2]],receipt,"RawJSON"]];
Exit[0];
