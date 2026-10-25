Module[{cpu0=TimeUsed[], wall, groups, avg, mon, vars={x,y,z}, sv, uv, cv, rr, ee, oo, ob, of, hh, rot, cofact, sat, res},
wall=AbsoluteTiming[
mon[p_]:=If[AnyTrue[p,OddQ],0,Times@@(Factorial2[#-1]& /@ p)/Factorial2[Total[p]+1]];
avg[p_]:=Total[(Last[#] mon[First[#]])& /@ CoefficientRules[Expand[p],vars]];
sv={{s1,s3,s4},{s3,s2,s5},{s4,s5,-s1-s2}};
uv={{u1,u3,u4},{u3,u2,u5},{u4,u5,-u1-u2}};
cv={{c1,c4,c5},{c4,c2,c6},{c5,c6,c3}};
rr={{3/5,-4/5,0},{4/5,3/5,0},{0,0,1}}.DiagonalMatrix[{1/2,3/4,9/10}].Transpose[{{1,0,0},{0,5/13,-12/13},{0,12/13,5/13}}];
ee={{e1,e2,e3},{e4,e5,e6},{e7,e8,e9}};
ob={{3/5,0,4/5},{0,1,0},{-4/5,0,3/5}};
of={{1,0,0},{0,5/13,-12/13},{0,12/13,5/13}};
hh=IdentityMatrix[3]/3+2 sv/15;
cofact[m_]:=Table[(-1)^(i+j) Det[Map[Delete[#,j]&,Delete[m,i]]],{i,3},{j,3}];
sat=d (a b+a c+b c)+d^2 (a+b+c)+d^3;
groups=<|
"normalized_source"->Simplify[avg[1+vars.sv.vars]-1],
"weighted_second_moment"->Simplify[Table[avg[(1+vars.sv.vars)vars[[i]]vars[[j]]],{i,3},{j,3}]-hh],
"sixth_moment_general_STF"->Simplify[avg[(vars.uv.vars)^2(vars.cv.vars)]-(2Tr[uv.uv]Tr[cv]+8Tr[uv.uv.cv])/105],
"fourth_moment_source_norm"->Simplify[avg[(vars.uv.vars)^2]-2Tr[uv.uv]/15],
"kernel_Frobenius_identity"->Expand[2r^2+2t^2-2r t(1+cc^2)-(2(r-t)^2+2r t(1-cc^2))],
"kernel_Lipschitz_residual"->Expand[2(r^2+t^2-2r t cc)-(2(r-t)^2+2r t(1-cc^2))-2r t(1-cc)^2],
"isotropic_source_STF"->Simplify[Table[avg[(vars.uv.vars)vars[[i]]vars[[j]]],{i,3},{j,3}]-2uv/15],
"determinant_exact_difference"->Expand[Det[rr+ee]-Det[rr]-Tr[Transpose[cofact[rr]].ee]-Tr[Transpose[cofact[ee]].rr]-Det[ee]],
"determinant_radius_saturation"->Expand[(a+d)(b+d)(c+d)-a b c-sat],
"physical_R_scaling_fourth_power"->Simplify[(1-h)Det[(1-h)rr]-(1-h)^4Det[rr]],
"stable_physical_prefactor_difference"->Expand[nn1 dd1-nn0 dd0-(nn0(dd1-dd0)+(nn1-nn0)dd1)],
"map_bound_two_frame_invariance"->Simplify[Tr[(of.ee.Transpose[ob]).(IdentityMatrix[3]/3+2ob.sv.Transpose[ob]/15).Transpose[of.ee.Transpose[ob]]]-Tr[ee.hh.Transpose[ee]]],
"source_bound_two_frame_invariance"->Simplify[With[{uu=ob.uv.Transpose[ob],ccm=Transpose[of.rr.Transpose[ob]].(of.rr.Transpose[ob])},2Tr[uu.uu]Tr[ccm]+8Tr[uu.uu.ccm]-(2Tr[uv.uv]Tr[Transpose[rr].rr]+8Tr[uv.uv.Transpose[rr].rr])]],
"determinant_two_frame_invariance"->Simplify[Det[of.rr.Transpose[ob]]-Det[rr]],
"input_budget_boundary"->Simplify[(aa+Sqrt[2]uu+ep bb)-tt(ll-uu)/.uu->(tt ll-aa-ep bb)/(Sqrt[2]+tt)],
"mixture_absolute_reserve"->Expand[(aa1+aa2+Sqrt[2](uu1+uu2)+ep(bb1+bb2))-((aa1+Sqrt[2]uu1+ep bb1)+(aa2+Sqrt[2]uu2+ep bb2))]
|>;
res=AssociationMap[If[AllTrue[Flatten[{groups[#]}],(#===0)&],0,groups[#]]&,Keys[groups]];
][[1]];
<|"kernel_version"->$Version,"groups"->res,"group_count"->Length[res],"all_exact_zero"->AllTrue[Values[res],(#===0)&],"wall_seconds"->wall,"cpu_seconds"->(TimeUsed[]-cpu0)|>
]
