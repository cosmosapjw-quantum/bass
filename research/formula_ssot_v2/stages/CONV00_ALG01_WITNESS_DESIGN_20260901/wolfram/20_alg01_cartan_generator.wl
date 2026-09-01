(* ::Package:: *)
ClearAll[BianchiStructureConstants,SpatialKoszulConnection,BianchiJacobi123,ValidateALG01Generic];
BianchiStructureConstants[a_List,n_List]/;Dimensions[a]==={3}&&Dimensions[n]==={3,3}:=Module[{eps=LeviCivitaTensor[3]},
 Table[Sum[eps[[i,j,d]]n[[d,g]],{d,3}]+a[[i]]KroneckerDelta[g,j]-a[[j]]KroneckerDelta[g,i],{i,3},{j,3},{g,3}]];
SpatialKoszulConnection[c_List]/;Dimensions[c]==={3,3,3}:=Table[(c[[i,j,k]]-c[[j,k,i]]+c[[k,i,j]])/2,{i,3},{j,3},{k,3}];
BianchiJacobi123[c_List]/;Dimensions[c]==={3,3,3}:=FullSimplify@Table[Sum[c[[1,2,d]]c[[d,3,g]]+c[[2,3,d]]c[[d,1,g]]+c[[3,1,d]]c[[d,2,g]],{d,3}],{g,3}];
ValidateALG01Generic[]:=Module[{a=Table[Unique["a$"],{3}],u,n,c,gamma,nda,r},
 u=Table[Unique["n$"],{6}]; n={{u[[1]],u[[4]],u[[5]]},{u[[4]],u[[2]],u[[6]]},{u[[5]],u[[6]],u[[3]]}};
 c=BianchiStructureConstants[a,n]; gamma=SpatialKoszulConnection[c]; nda=n.a;
 r=<|"StructureAntisymmetry"->FullSimplify@Table[c[[i,j,k]]+c[[j,i,k]],{i,3},{j,3},{k,3}],
     "JacobiMinus2nDotA"->FullSimplify[BianchiJacobi123[c]-2nda],
     "MetricCompatibility"->FullSimplify@Table[gamma[[i,j,k]]+gamma[[i,k,j]],{i,3},{j,3},{k,3}],
     "TorsionReconstruction"->FullSimplify@Table[gamma[[i,j,k]]-gamma[[j,i,k]]-c[[i,j,k]],{i,3},{j,3},{k,3}]|>;
 <|"Status"->If[And@@Values[Map[BASSZeroQ,r]],"PASS","FAIL"],
   "JacobiIdentity"->"J^gamma_123 = 2 n^(gamma beta) a_beta","Residuals"->r,"ResidualZeroQ"->Map[BASSZeroQ,r]|>];
