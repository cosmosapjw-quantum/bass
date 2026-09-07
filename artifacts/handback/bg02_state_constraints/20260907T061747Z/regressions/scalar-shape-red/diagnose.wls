$HistoryLength=0;
result=TimeConstrained[Module[{root,paths,s,u,ell,h},
root=Environment["BASS_REPO"];
paths={"Authority/BG02Convention.wl","Geometry/StructureConstants.wl","Geometry/LeviCivitaConnection.wl","Geometry/ONFConnectionCurvature.wl","Background/EinsteinProjection.wl"};
Scan[Get[FileNameJoin[{root,"wolfram","BASS","Kernel",#}]]&,paths];
Get[FileNameJoin[{Environment["BG02_CODE_ROOT"],"StateConstraints.wl"}]];
h=Sqrt[14/3];
s=<|"Hgeom"->h,"aB"->{1,0,0},"nB"->{{0,0,0},{0,2,3},{0,3,0}},"sigma"->{{0,0,1},{0,0,0},{1,0,0}},"rho"->0,"q"->{0,0,0},"Lambda"->0,"kappaG"->1|>;
Print["SCALAR_DIMENSIONS ",InputForm[Dimensions/@{1,h,Sqrt[(13+u^2)/3]/ell,u/ell}]];
Print["SCALAR_HEADS ",InputForm[Head/@{1,h,Sqrt[(13+u^2)/3]/ell,u/ell}]];
Print["RAW_MAPPER_RESULT ",InputForm[BASS`Research`BG02StateConstraints[s]]];
Print["SCALAR_LISTQ ",InputForm[ListQ/@{1,h,Sqrt[(13+u^2)/3]/ell,u/ell}]];
0],120,2];Exit[result];
