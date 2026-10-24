ClearAll["Global\`*"];
cpu0 = TimeUsed[];
timed = AbsoluteTiming[
 ass = g > 0 && k > 0 && nAtoms > 0 && f >= 0 && v >= 0 && 0 <= x0 < g/(g + 1);
 bb = g + 1; ff = 1 + bb f; xe = g f/ff; de = g/ff;
 eta = k ff/de; yy = x0 - xe; zz = -bb yy/de;
 aa = 1 - Exp[-v]; rr = v - aa;
 xx = xe + yy Exp[-v]; dx = -yy aa;
 dt = (v + zz aa)/eta;
 down = nAtoms (1 + f)/ff (x0 aa + xe rr);
 up = nAtoms g f/ff ((1 - x0) aa + (1 - xe) rr);
 axes = Join[IdentityMatrix[3], -IdentityMatrix[3]];
 dirs = Join[axes, Tuples[{-1, 1}, 3]/Sqrt[3]];
 weights = Join[ConstantArray[1/15, 6], ConstantArray[3/40, 8]];
 ss = {{sxx,sxy,sxz},{sxy,syy,syz},{sxz,syz,-sxx-syy}};
 qq = (1 + #.ss.#)& /@ dirs;
 second = Sum[weights[[j]] Outer[Times, dirs[[j]], dirs[[j]]],{j,14}];
 fourth = Table[Sum[weights[[j]] dirs[[j,i]] dirs[[j,l]] dirs[[j,m]] dirs[[j,n]],{j,14}] -
  (KroneckerDelta[i,l] KroneckerDelta[m,n] + KroneckerDelta[i,m] KroneckerDelta[l,n] +
   KroneckerDelta[i,n] KroneckerDelta[l,m])/15,{i,3},{l,3},{m,3},{n,3}];
 qsecond = Sum[weights[[j]] qq[[j]] Outer[Times,dirs[[j]],dirs[[j]]],{j,14}];
 raw = <|
 "down_direct" -> (down - nAtoms (1+f) (k f dt - dx)),
 "up_direct" -> (up - nAtoms f (k (1+f) dt - dx)),
 "net_owner_increment" -> (down-up+nAtoms dx),
 "population_ODE" -> (D[xx,v]/D[dt,v] + k ff (xx-xe)/(g-bb xx)),
 "down_rate" -> (D[down,v]/D[dt,v] - nAtoms k (1+f) xx/(g-bb xx)),
 "up_rate" -> (D[up,v]/D[dt,v] - nAtoms k g f (1-xx)/(g-bb xx)),
 "LTE_down" -> ((down /. x0 -> xe) - nAtoms g f(1+f)v/ff^2),
 "LTE_up" -> ((up /. x0 -> xe) - nAtoms g f(1+f)v/ff^2),
 "zero_f_up" -> (up /. f->0),
 "zero_duration" -> ({down,up,dx,dt}/.v->0),
 "cubature_sum" -> (Total[weights]-1),
 "cubature_odd" -> Sum[weights[[j]] dirs[[j]],{j,14}],
 "cubature_second" -> (second-IdentityMatrix[3]/3),
 "cubature_fourth" -> fourth,
 "q_number" -> (weights.qq-1),
 "q_odd" -> Sum[weights[[j]] qq[[j]] dirs[[j]],{j,14}],
 "q_pressure" -> (qsecond-IdentityMatrix[3]/3-2 ss/15),
 "q_trace" -> Tr[qsecond-IdentityMatrix[3]/3],
 "state_rate_units" -> (kap len^3 en dn/(cc duration) (cc duration/len) - kap len^2 en dn)
 |>;
 reduced = Map[FullSimplify[#, Assumptions->ass]&,raw];
 residualSummary = Map[DeleteDuplicates[Flatten[{#}]]&, reduced];
 allZero = And @@ (TrueQ[# === {0}]& /@ Values[residualSummary]);
 <|"groups"->Length[raw],"all_zero"->allZero,"residuals"->residualSummary,
 "LTE_rule"->"Use v=omega at y0=0 even though upstream u=0 is a net-only shortcut",
 "scope"->"Frozen thick model; canonical rest; 14-node N/T only; no finite-opacity gross admission"|>
];
<|"elapsed_wall_seconds"->timed[[1]],"kernel_cpu_seconds"->(TimeUsed[]-cpu0),"result"->timed[[2]]|>
