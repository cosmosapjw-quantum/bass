Clear["Global`*"];
startCpu=TimeUsed[];
{wall,out}=AbsoluteTiming[
vars={nx,ny,nz};
sphereMoment[ex_List]:=If[AnyTrue[ex,OddQ],0,
 Times@@(Factorial2[#-1]&/@ex)/Factorial2[Total[ex]+1]];
sphereAverage[poly_]:=Total[(Last[#]*sphereMoment[First[#]]&)/@CoefficientRules[Expand[poly],vars]];
sMat={{sx,sxy,sxz},{sxy,sy,syz},{sxz,syz,-sx-sy}};
qPoly=1+vars.sMat.vars;
hMat=IdentityMatrix[3]/3+2sMat/15;
oz={{3/5,-4/5,0},{4/5,3/5,0},{0,0,1}};
ox={{1,0,0},{0,5/13,-12/13},{0,12/13,5/13}};
oy={{3/5,0,4/5},{0,1,0},{-4/5,0,3/5}};
rMat=oz.DiagonalMatrix[{9/20,3/5,9/10}].Transpose[ox];
vVec=rMat.vars;
mMat=rMat.hMat.Transpose[rMat];
sRot=oy.sMat.Transpose[oy];
rRot=ox.rMat.Transpose[oy];
mRot=rRot.(IdentityMatrix[3]/3+2sRot/15).Transpose[rRot];
qZero=DiagonalMatrix[{-1,2/5,3/5}];
rBoundary=DiagonalMatrix[{9/20,3/5,9/10}];
mBoundary=rBoundary.(IdentityMatrix[3]/3+2qZero/15).rBoundary;
groups=<|
"q_normalization"->FullSimplify[sphereAverage[qPoly]-1],
"H_general_STF"->Table[FullSimplify[sphereAverage[qPoly vars[[i]] vars[[j]]]-hMat[[i,j]]],{i,3},{j,3}],
"M_noncommuting"->Table[FullSimplify[sphereAverage[qPoly vVec[[i]] vVec[[j]]]-mMat[[i,j]]],{i,3},{j,3}],
"m2_trace"->FullSimplify[sphereAverage[qPoly vVec.vVec]-Tr[mMat]],
"proper_rotations"->Flatten[Table[{rot.Transpose[rot]-IdentityMatrix[3],Det[rot]-1},{rot,{ox,oy,oz}}]],
"two_frame_covariance"->Map[FullSimplify,mRot-ox.mMat.Transpose[ox],{2}],
"chord_factorization"->FullSimplify[((y^2+a*b)/(a+b)-y)-(y-a)*(y-b)/(a+b)],
"isotropic_denominator"->FullSimplify[(Tr[t^2 hMat]+t^2)/(2t)-t],
"binomial_ratio_K0_K64"->Table[Abs[Binomial[1/2,k+1]]-Abs[Binomial[-1/2,k+1]]/(2k+1),{k,0,64}],
"coefficient_recurrence"->Table[Abs[Binomial[-1/2,j]]-Abs[Binomial[-1/2,j-1]]*(2j-1)/(2j),{j,1,65}],
"zero_source_directions"->Table[n.(IdentityMatrix[3]+qZero).n,{n,{{1,0,0},{-1,0,0}}}],
"boundary_H_eigenvalues"->Sort[Eigenvalues[IdentityMatrix[3]/3+2qZero/15]]-{1/5,29/75,31/75},
"boundary_M_direct"->Table[sphereAverage[(1+vars.qZero.vars)*(rBoundary.vars)[[i]]*(rBoundary.vars)[[j]]]-mBoundary[[i,j]],{i,3},{j,3}],
"tensor_STF_trace"->FullSimplify[Tr[{{p11,p12,p13},{p12,p22,p23},{p13,p23,p33}}-(p11+p22+p33)IdentityMatrix[3]/3]],
"mixture_lower_bound_accounting"->Expand[Sum[cc[j] eps flo[j],{j,1,4}]-eps Sum[cc[j] flo[j],{j,1,4}]],
"scalar_scale_of_M"->Map[FullSimplify,(t rMat).hMat.Transpose[t rMat]-t^2 mMat,{2}]
|>;
zeros=AssociationMap[(And@@(TrueQ[#==0]&/@Flatten[{groups[#]}]))&,Keys[groups]];
<|"group_count"->Length[groups],"all_zero"->And@@Values[zeros],
 "zero_groups"->zeros,"exact_residuals"->groups,
 "rational_boundary_M"->mBoundary,
 "continuous_source_boundary_eigenvalues"->Eigenvalues[IdentityMatrix[3]+qZero],
 "frozen_R_determinant"->Det[rMat]|>
];
cpu=TimeUsed[]-startCpu;
ExportString[Join[out,<|"kernel"->$Version,"wall_seconds"->wall,"cpu_seconds"->cpu|>],"RawJSON"]
