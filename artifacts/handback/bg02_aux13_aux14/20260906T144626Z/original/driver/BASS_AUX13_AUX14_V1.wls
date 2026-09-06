#!/usr/bin/env wolframscript
$HistoryLength = 0;
ClearAll[bassAuxMain];
bassAuxMain[] := Module[
 {root, rel, files, before, after, div, ham, aa, nn, ss, gg, gl,
  carrier, expected, lockedCarrier, lm, sf, s0, wfCarrier,
  av, n22, n23, n33, s11, s12, s13, s22, s23, ell, u, v, w,
  hh, kg, q1, a, nb, sig, hub, ric, r3, s2, state, rates,
  sigDot, aDot, nDot, r3Dot, s2Dot, hres, hresDot,
  required, tests, declared, report, results, rows, ids, complete,
  runtimeFailures, sameSource, allPassed, exitCode},
 root = Environment["BASS_REPO"];
 If[!StringQ[root] || !DirectoryQ[root],
  Return[<|"status"->"BLOCKED_MISSING_SOURCE_ROOT","exit_code"->2|>]];
 rel = {"Geometry/StructureConstants.wl",
   "Geometry/LeviCivitaConnection.wl",
   "Geometry/ONFConnectionCurvature.wl",
   "Background/EinsteinProjection.wl"};
 files = FileNameJoin[{root,"wolfram","BASS","Kernel",#}]& /@ rel;
 If[!AllTrue[files,FileExistsQ],
  Return[<|"status"->"BLOCKED_MISSING_SOURCE_FILES","exit_code"->2|>]];
 before = AssociationThread[rel,
   (IntegerString[FileHash[#,"SHA256"],16,64]& /@ files)];
 Print["AUX_SOURCE_BEFORE ",InputForm[before]];
 If[Check[Scan[Get,files],$Failed] === $Failed,
  Return[<|"status"->"BLOCKED_SOURCE_LOAD_MESSAGES","exit_code"->2|>]];
 div[connection_,tensor_] := Expand@Table[
   -Sum[connection[[k,j,i]] tensor[[k,j]] +
     connection[[k,j,j]] tensor[[i,k]],{j,3},{k,3}],{i,3}];
 aa={av,0,0};
 nn={{0,0,0},{0,n22,n23},{0,n23,n33}};
 ss={{s11,s12,s13},{s12,s22,s23},{s13,s23,-s11-s22}};
 gg=BASS`Geometry`LeviCivitaConnection[aa,nn];
 If[Dimensions[gg]=!={3,3,3},
  Return[<|"status"->"BLOCKED_CONNECTION_NOT_EVALUATED","exit_code"->2|>]];
 carrier=div[gg,ss];
 expected={-3 av s11+n23(s11+2 s22)+(n33-n22)s23,
   -(3 av+n23)s12-n33 s13,n22 s12+(n23-3 av)s13};
 gl=BASS`Geometry`ConnectionToLockedGammaOrder[gg];
 lockedCarrier=Expand@Table[-Sum[
   gl[[j,i,k]]ss[[k,j]]+gl[[j,j,k]]ss[[i,k]],{j,3},{k,3}],{i,3}];
 lm=Table[Coefficient[carrier[[i+1]],{s12,s13}[[j]]],{i,2},{j,2}];
 sf={{w,0,u},{0,v/3,v},{u,v,-w-v/3}}/ell;
 s0=sf/.u->0;
 wfCarrier=div[BASS`Geometry`LeviCivitaConnection[
   {1,0,0}/ell,{{0,0,0},{0,2,3},{0,3,0}}/ell],sf];
 ham[tensor_]:=BASS`Background`HamiltonianProjection[
   <|"sigma2"->Tr[tensor.tensor]|>];
 a={1,0,0}/ell;
 nb={{0,0,0},{0,2,3},{0,3,0}}/ell;
 sig={{0,0,1},{0,0,0},{1,0,0}}/ell;
 hub=1/ell;
 ric=BASS`Geometry`ONFRicciTensor[a,nb];
 If[Dimensions[ric]=!={3,3},
  Return[<|"status"->"BLOCKED_RICCI_NOT_EVALUATED","exit_code"->2|>]];
 r3=Simplify[Tr[ric]];s2=Tr[sig.sig];
 state=<|"R3"->r3,"H"->hub,"sigma2"->s2,"Lambda"->0,
   "rho"->0,"p"->0,"D.A"->0,"A2"->0|>;
 rates={BASS`Background`SpatialTraceRate[state],
   BASS`Background`ADMTraceRate[state],
   BASS`Background`RaychaudhuriRate[state]};
 sigDot=Table[BASS`Background`ShearProjectedRate[
   Join[state,<|"sigmaComponent"->sig[[i,j]],
     "R3PSTF"->ric[[i,j]]-r3 KroneckerDelta[i,j]/3,
     "DPSTFA"->0,"APSTFA"->0,"piComponent"->0|>]]["value"],{i,3},{j,3}];
 aDot=-hub a-sig.a;
 nDot=-hub nb+sig.nb+nb.sig;
 r3Dot=Expand[-12 a.aDot-2 Tr[nb.nDot]+Tr[nb]Tr[nDot]];
 s2Dot=Expand[2 Tr[sig.sigDot]];
 hres=BASS`Background`HamiltonianProjection[state];
 hresDot=Expand[((r3Dot+12 hub #-s2Dot)/2)& /@ rates];
 required={
  "AUX13_CLASS_B_DIVERGENCE","AUX13_STORAGE_ORDER_PARITY",
  "AUX13_ISOTROPIC_DIVERGENCE","AUX13_EXCEPTIONAL_DETERMINANT",
  "AUX13_FULL_MOMENTUM_WITNESS","AUX13_SHEAR_NORM_SURVIVAL",
  "AUX13_HAMILTONIAN_CONSUMER_SURVIVAL","AUX13_MOMENTUM_CONSUMER_SIGN",
  "AUX14_SPATIAL_RICCI","AUX14_NONZERO_HAMILTONIAN",
  "AUX14_ACTUAL_RATE_VALUES","AUX14_JACOBI_VECTOR_DERIVATIVE",
  "AUX14_CURVATURE_DERIVATIVE","AUX14_SHEAR_NORM_DERIVATIVE",
  "AUX14_DIRECT_HAMILTONIAN_DERIVATIVE","AUX14_PROPAGATION_RATE_SEPARATION",
  "AUX14_FERMI_ALIGNMENT_COUNTEREXAMPLE"};
 tests={
  TestCreate[Expand[carrier-expected],{0,0,0},TestID->"AUX13_CLASS_B_DIVERGENCE"],
  TestCreate[Expand[lockedCarrier-carrier],{0,0,0},TestID->"AUX13_STORAGE_ORDER_PARITY"],
  TestCreate[div[gg,hh IdentityMatrix[3]],{0,0,0},TestID->"AUX13_ISOTROPIC_DIVERGENCE"],
  TestCreate[Expand[Det[lm]-(9 av^2+n22 n33-n23^2)],0,TestID->"AUX13_EXCEPTIONAL_DETERMINANT"],
  TestCreate[Expand[wfCarrier],{0,0,0},TestID->"AUX13_FULL_MOMENTUM_WITNESS"],
  TestCreate[Expand[Tr[sf.sf]-Tr[s0.s0]-2 u^2/ell^2],0,TestID->"AUX13_SHEAR_NORM_SURVIVAL"],
  TestCreate[Expand[ham[sf]-ham[s0]+u^2/ell^2],0,TestID->"AUX13_HAMILTONIAN_CONSUMER_SURVIVAL"],
  TestCreate[Expand[BASS`Background`MomentumProjection[
    <|"DivergenceK"->carrier[[1]],"GradientK"->0,"kappaG"->kg,"qComponent"->q1|>]
    +carrier[[1]]+kg q1],0,TestID->"AUX13_MOMENTUM_CONSUMER_SIGN"],
  TestCreate[Simplify[ric-{{-22,0,0},{0,-6,8},{0,8,2}}/ell^2],ConstantArray[0,{3,3}],TestID->"AUX14_SPATIAL_RICCI"],
  TestCreate[Simplify[hres+11/ell^2],0,TestID->"AUX14_NONZERO_HAMILTONIAN"],
  TestCreate[Simplify[rates-{1/6,17/3,-5/3}/ell^2],{0,0,0},TestID->"AUX14_ACTUAL_RATE_VALUES"],
  TestCreate[Expand[nDot.a+nb.aDot],{0,0,0},TestID->"AUX14_JACOBI_VECTOR_DERIVATIVE"],
  TestCreate[Expand[r3Dot-52/ell^3],0,TestID->"AUX14_CURVATURE_DERIVATIVE"],
  TestCreate[Simplify[s2Dot+12/ell^3],0,TestID->"AUX14_SHEAR_NORM_DERIVATIVE"],
  TestCreate[Simplify[hresDot-{33,66,22}/ell^3],{0,0,0},TestID->"AUX14_DIRECT_HAMILTONIAN_DERIVATIVE"],
  TestCreate[Simplify[hresDot-{-3,-6,-2}hub hres],{0,0,0},TestID->"AUX14_PROPAGATION_RATE_SEPARATION"],
  TestCreate[Expand[aDot[[3]]+1/ell^2],0,TestID->"AUX14_FERMI_ALIGNMENT_COUNTEREXAMPLE"]};
 declared=#["TestID"]& /@ tests;
 If[Sort[declared]=!=Sort[required] || !DuplicateFreeQ[declared],
  Return[<|"status"->"BLOCKED_DECLARED_IDS","exit_code"->2|>]];
 Print["AUX_TESTS_BEGIN ",InputForm[declared]];
 report=TestReport[tests,HandlerFunctions-><|
   "TestEvaluated"->(Print["AUX_TEST_EVENT ",InputForm[#]]&)|>];
 If[Head[report]=!=TestReportObject,
  Return[<|"status"->"BLOCKED_INVALID_REPORT","exit_code"->2|>]];
 results=report["Results"];
 If[!ListQ[results],
  Return[<|"status"->"BLOCKED_RESULTS_PROPERTY","exit_code"->2|>]];
 ids=#["TestID"]& /@ results;
 complete=DuplicateFreeQ[ids] && Sort[ids]===Sort[required];
 rows=(<|"id"->#["TestID"],"outcome"->ToString[#["Outcome"],InputForm],
   "actual"->ToString[#["ActualOutput"],InputForm],
   "expected"->ToString[#["ExpectedOutput"],InputForm],
   "actual_messages"->ToString[#["ActualMessages"],InputForm],
   "expected_messages"->ToString[#["ExpectedMessages"],InputForm]|>& /@ results);
 runtimeFailures=report["RuntimeFailures"];
 after=AssociationThread[rel,(IntegerString[FileHash[#,"SHA256"],16,64]& /@ files)];
 sameSource=before===after;
 allPassed=TrueQ[report["ReportSucceeded"]] &&
   AllTrue[results,#["Outcome"]==="Success"&];
 exitCode=Which[!complete || !sameSource || runtimeFailures=!={},2,
   allPassed,0,True,1];
 <|"stage"->"BG02_AUX13_AUX14_V1",
   "status"->Switch[exitCode,0,"PASS_AUXILIARY_ONLY",1,"FAIL_AUXILIARY",_,"INVALID_AUXILIARY"],
   "exit_code"->exitCode,"wolfram_version"->$Version,
   "native_xact"->False,"production_admitted"->False,
   "required_ids"->required,"observed_ids"->ids,"exact_ids"->complete,
   "rows"->rows,"runtime_failures"->ToString[runtimeFailures,InputForm],
   "source_before"->before,"source_after"->after,"source_unchanged"->sameSource|>
];
result=CheckAbort[
 Check[TimeConstrained[bassAuxMain[],120,
   <|"status"->"AUXILIARY_TIMEOUT","exit_code"->2|>],
   <|"status"->"AUXILIARY_MESSAGE_ERROR","exit_code"->2|>],
 <|"status"->"AUXILIARY_ABORT","exit_code"->2|>];
If[!AssociationQ[result],
 result=<|"status"->"INVALID_AUXILIARY_RESULT","exit_code"->2|>];
Print["AUX_FINAL_BEGIN"];
Print[ExportString[result,"RawJSON"]];
Print["AUX_FINAL_END"];
Exit[Lookup[result,"exit_code",2]];
