$HistoryLength=0;
result=TimeConstrained[Module[{root,paths,s,q1,q2,q3,h,asm,radical,symbolic,flux,rows,report},
root=Environment["BASS_REPO"];
paths={"Authority/BG02Convention.wl","Geometry/StructureConstants.wl","Geometry/LeviCivitaConnection.wl","Geometry/ONFConnectionCurvature.wl","Background/EinsteinProjection.wl"};
Scan[Get[FileNameJoin[{root,"wolfram","BASS","Kernel",#}]]&,paths];
Get[FileNameJoin[{Environment["BG02_CODE_ROOT"],"StateConstraints.wl"}]];
s=<|"Hgeom"->0,"aB"->{0,0,0},"nB"->ConstantArray[0,{3,3}],"sigma"->ConstantArray[0,{3,3}],"rho"->0,"q"->{0,0,0},"Lambda"->0,"kappaG"->1|>;
asm=Element[{h,q1,q2,q3},Reals];
radical=BASS`Research`BG02StateConstraints[Join[s,<|"Hgeom"->Sqrt[2]|>]];
symbolic=BASS`Research`BG02StateConstraints[Join[s,<|"Hgeom"->h|>],Assumptions->asm];
flux=BASS`Research`BG02StateConstraints[Join[s,<|"q"->{q1+q2,q2+q3,q3+q1}|>],Assumptions->asm];
rows={
 TestCreate[AssociationQ[radical]&&radical["Hamiltonian"]===6,True,TestID->"REG_RADICAL_SCALAR"],
 TestCreate[AssociationQ[symbolic]&&TrueQ[FullSimplify[symbolic["Hamiltonian"]==3 h^2,Assumptions->asm]],True,TestID->"REG_SYMBOLIC_SCALAR_OUTPUT"],
 TestCreate[AssociationQ[flux]&&TrueQ[FullSimplify[flux["Momentum"]==-{q1+q2,q2+q3,q3+q1},Assumptions->asm]],True,TestID->"REG_COMPOUND_VECTOR_ELEMENTS"],
 TestCreate[MatchQ[BASS`Research`BG02StateConstraints[Join[s,<|"Hgeom"->{1,2}|>]],Failure["StateShape",_Association]],True,TestID->"REG_LIST_IS_NOT_SCALAR"],
 TestCreate[MatchQ[BASS`Research`BG02StateConstraints[Join[s,<|"nB"->{{0,0,0},{0,0},{0,0,0}}|>]],Failure["StateShape",_Association]],True,TestID->"REG_RAGGED_TENSOR_REJECTED"]};
report=TestReport[rows];Print["REGRESSION_RESULTS ",InputForm[({#["TestID"],#["Outcome"],#["ActualMessages"]}& /@ report["Results"])]];
If[TrueQ[report["ReportSucceeded"]]&&report["RuntimeFailures"]==={},0,1]],120,2];Exit[result];
