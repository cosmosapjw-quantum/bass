ClearAll["Global\`*"]; 
axes=Join[IdentityMatrix[3],-IdentityMatrix[3]];
corners=Tuples[{-1,1},3]/Sqrt[3];
boost[v_]:=Module[{g=1/Sqrt[1-v.v]},ArrayFlatten[{{{{g}},{g v}},{Transpose[{g v}],IdentityMatrix[3]+g^2/(g+1) Outer[Times,v,v]}}]];
packet[d_,v_]:=(boost[v].Prepend[#,1]& /@ d);
moment[d_,v_]:=Module[{p=packet[d,v],q,k,pi},q=Total[p]/Length[d];k=Total[(Outer[Times,#,#]/First[#]& /@ p)]/Length[d];pi=k[[2;;4,2;;4]]-IdentityMatrix[3] Tr[k[[2;;4,2;;4]]]/3;{q,k,pi}];
aa=Simplify[moment[axes,{3/5,0,0}]];
bb=Simplify[moment[corners,{3/5,0,0}]];
wrong=Simplify[boost[{3/5,0,0}].DiagonalMatrix[{1,1/3,1/3,1/3}].Transpose[boost[{3/5,0,0}]]];
diff=FullSimplify[moment[axes,{b,0,0}][[3,1,1]]-moment[corners,{b,0,0}][[3,1,1]]-2 b^2 Sqrt[1-b^2]/(3 (3-b^2)),Assumptions->Element[b,Reals]&&-1<b<1];
oblique=FullSimplify[moment[axes,{1/5,2/5,2/5}][[3,1,1]]-moment[corners,{1/5,2/5,2/5}][[3,1,1]]];
<|"kernel"->$Version,"Q_A"->aa[[1]],"Q_B"->bb[[1]],"Pi_A"->aa[[3]],"Pi_B"->bb[[3]],"delta"->Simplify[aa[[3]]-bb[[3]]],"axis_formula_residual"->diff,"oblique_delta_xx"->oblique,"wrong_state_weight_Q"->wrong[[1]],"null_trace_A"->Simplify[-aa[[2,1,1]]+Tr[aa[[2,2;;4,2;;4]]]],"sqrt_validation"->{NumberQ[1/Sqrt[3]],NumericQ[1/Sqrt[3]],TrueQ[Element[1/Sqrt[3],Reals]]}|>

