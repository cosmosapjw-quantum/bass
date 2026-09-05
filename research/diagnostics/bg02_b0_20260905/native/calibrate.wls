#!/usr/bin/env wolframscript
(* UNEXECUTED native component calibration; not the abstract BG-02 bridge.
   Run through run_native.py in a fresh kernel and a clean Linux checkout. *)
$HistoryLength=0;
ClearAll[jsonSafe, finish, simp, gamma, rup, gamma3, r3up, dk, nativeBody];
jsonSafe[v_Association]:=AssociationThread[Keys[v],jsonSafe/@Values[v]];
jsonSafe[v_List]:=jsonSafe/@v;
jsonSafe[v_String|v_Integer|v_Real]:=v;
jsonSafe[True]=True; jsonSafe[False]=False; jsonSafe[Null]=Null;
jsonSafe[v_]:=ToString[InputForm[v]];
repo=Environment["BASS_NATIVE_REPO"];
out=Environment["BASS_NATIVE_OUTPUT"];
archive=Environment["BASS_XACT_SOURCE"];
If[!And@@(StringQ[#]&&StringLength[#]>0&/@{repo,out,archive}),
 Print["BLOCKED_MISSING_LAUNCHER_CONTEXT"];Exit[2]];
receiptPath=FileNameJoin[{out,"native.json"}];
computed=False;
activation=<||>;
finish[payload_Association,code_Integer]:=Module[{safe,text,tmp,stream,back,renamed},
 safe=jsonSafe@Join[<|"schema_version"->"1.0.0",
  "stage_id"->"BG02_B0R1_NATIVE_TYPED_VIEW_CALIBRATION",
  "native_xact_evaluated"->computed,"activation"->activation,
  "production_modified"->False,"abstract_bridge_admitted"->False,
  "wolfram_version"->$Version|>,payload];
 If[FileExistsQ[receiptPath],Print["REFUSE_RECEIPT_OVERWRITE"];Exit[3]];
 text=Check[ExportString[safe,"RawJSON"],$Failed];
 If[!StringQ[text],Print["FAIL_RECEIPT_SERIALIZATION"];Exit[3]];
 tmp=receiptPath<>".tmp."<>ToString[$ProcessID];
 If[FileExistsQ[tmp],Print["REFUSE_TEMP_OVERWRITE"];Exit[3]];
 stream=Check[OpenWrite[tmp,CharacterEncoding->"UTF-8"],$Failed];
 If[Head[stream]=!=OutputStream,Print["FAIL_RECEIPT_OPEN"];Exit[3]];
 WriteString[stream,text];Close[stream];
 back=Check[Import[tmp,"RawJSON"],$Failed];
 If[back=!=safe,Print["FAIL_RECEIPT_ROUNDTRIP"];Exit[3]];
 renamed=Check[RenameFile[tmp,receiptPath],$Failed];
 If[renamed===$Failed,Print["FAIL_RECEIPT_RENAME"];Exit[3]];
 Print[InputForm[safe]];Exit[code]
];
contractPath=FileNameJoin[{DirectoryName[$InputFileName],"CONTRACT.json"}];
contract=Check[Import[contractPath,"RawJSON"],$Failed];
If[!AssociationQ[contract],finish[<|"status"->"BLOCKED_CONTRACT"|>,2]];
required=Lookup[contract,"required_ids",{}];
If[Length[required]=!=12 || !DuplicateFreeQ[required],
 finish[<|"status"->"BLOCKED_REQUIRED_IDS"|>,2]];
If[AnyTrue[$Packages,StringStartsQ[#,"xAct`"]&],
 finish[<|"status"->"BLOCKED_PRELOADED_XACT"|>,2]];
(* Do NOT Get the full BASS init; its production formulas are not this oracle. *)
Get[FileNameJoin[{repo,"wolfram","BASS","Kernel","Authority","Environment.wl"}]];
activation=TimeConstrained[
 BASS`Authority`ActivatePinnedXAct[archive,contract["xact_archive_sha256"]],
 90,<|"status"->"BLOCKED","reason"->"ACTIVATION_TIMEOUT"|>];
If[!TrueQ[BASS`Authority`XActActivationReceiptQ[activation]],
 finish[<|"status"->"BLOCKED_XACT_ACTIVATION"|>,2]];
xcobaFile=FindFile["xAct`xCoba`"];
If[!StringQ[xcobaFile] ||
 !StringStartsQ[ExpandFileName[xcobaFile],ExpandFileName[activation["install_parent"]]<>"/"],
 finish[<|"status"->"BLOCKED_XCOBA_PATH"|>,2]];
Get[xcobaFile];
packageOK=MemberQ[$Packages,"xAct`xTensor`"]&&MemberQ[$Packages,"xAct`xCoba`"]&&
 Length[DownValues[xAct`xTensor`DefTensor]]>0&&Length[DownValues[xAct`xCoba`MetricCompute]]>0;
If[!TrueQ[packageOK],finish[<|"status"->"BLOCKED_PACKAGE_DEFINITIONS"|>,2]];

nativeBody[]:=Module[{metric,nativeX,nativeRic,referenceB,referenceRic,rawContraction,
 spatial,inv3,kk,ktrace,div,grad,r3,gauss,codazzi,normal,normalDown,hfull,
 flux,stress,eNative,mNative,mReference,mOld,sentinel,residuals,simplified,checks,exactIDs},
 xAct`xTensor`DefManifold[Global`BASSN1M4,4,
  {Global`BASSN1a,Global`BASSN1b,Global`BASSN1c,Global`BASSN1d}];
 xAct`xTensor`DefMetric[-1,Global`BASSN1g[-Global`BASSN1a,-Global`BASSN1b],
  Global`BASSN1CD,{";","D"}];
 xAct`xCoba`DefChart[Global`BASSN1ch,Global`BASSN1M4,{0,1,2,3},
  {Global`BASSN1T[],Global`BASSN1X[],Global`BASSN1Y[],Global`BASSN1Z[]}];
 Scan[xAct`xTensor`DefConstantSymbol,
  {Global`BASSN1H1,Global`BASSN1H2,Global`BASSN1H3,Global`BASSN1A}];
 metric=DiagonalMatrix[{-1,Exp[2 Global`BASSN1H1 Global`BASSN1T[]],
  Exp[2 Global`BASSN1H2 Global`BASSN1T[]-2 Global`BASSN1A Global`BASSN1X[]],
  Exp[2 Global`BASSN1H3 Global`BASSN1T[]-2 Global`BASSN1A Global`BASSN1X[]]}];
 xAct`xCoba`MetricInBasis[Global`BASSN1g,-Global`BASSN1ch,metric];
 xAct`xCoba`MetricCompute[Global`BASSN1g,Global`BASSN1ch,All,
  xAct`xCoba`CVSimplify->Simplify,xAct`xCore`Verbose->False];
 nativeX=xAct`xCoba`ToValues@xAct`xCoba`ComponentArray[
  Global`RiemannBASSN1CD[{-Global`BASSN1a,-Global`BASSN1ch},
   {-Global`BASSN1b,-Global`BASSN1ch},{-Global`BASSN1c,-Global`BASSN1ch},
   {-Global`BASSN1d,-Global`BASSN1ch}]];
 nativeRic=xAct`xCoba`ToValues@xAct`xCoba`ComponentArray[
  Global`RicciBASSN1CD[{-Global`BASSN1a,-Global`BASSN1ch},
   {-Global`BASSN1b,-Global`BASSN1ch}]];
 If[Dimensions[nativeX]=!={4,4,4,4}||Dimensions[nativeRic]=!={4,4}||
  !FreeQ[nativeX,_Global`RiemannBASSN1CD]||!FreeQ[nativeRic,_Global`RicciBASSN1CD],
  Return[Failure["UNCOMPUTED_COMPONENTS",<||>]]];
 computed=True;
 coords={rT,rX,rY,rZ};
 coordinateRules=Thread[{Global`BASSN1T[],Global`BASSN1X[],Global`BASSN1Y[],Global`BASSN1Z[]}->coords];
 gref=metric/.coordinateRules; inv=Inverse[gref];
 nativeX=nativeX/.coordinateRules;nativeRic=nativeRic/.coordinateRules;
 assumptions=Element[Join[coords,{Global`BASSN1H1,Global`BASSN1H2,Global`BASSN1H3,
  Global`BASSN1A,rRho,rPressure,rQx,rQy,rQz,rKG,rLambda}],Reals]&&rEll>0;
 simp[v_]:=Simplify[v,assumptions];
 gamma[d_,a_,b_]:=gamma[d,a,b]=simp[Sum[inv[[d,j]](
  D[gref[[j,b]],coords[[a]]]+D[gref[[j,a]],coords[[b]]]-D[gref[[a,b]],coords[[j]]])/2,{j,4}]];
 rup[a_,b_,c_,d_]:=rup[a,b,c,d]=simp[D[gamma[d,b,c],coords[[a]]]-
  D[gamma[d,a,c],coords[[b]]]+Sum[gamma[d,a,k]gamma[k,b,c]-gamma[d,b,k]gamma[k,a,c],{k,4}]];
 referenceB=Array[Function[{a,b,c,d},simp[Sum[gref[[d,j]]rup[a,b,c,j],{j,4}]]],{4,4,4,4}];
 referenceRic=Array[Function[{a,b},simp[Sum[inv[[c,d]]referenceB[[c,b,a,d]],{c,4},{d,4}]]],{4,4}];
 rawContraction=Array[Function[{a,b},simp[Sum[inv[[c,d]]nativeX[[a,c,b,d]],{c,4},{d,4}]]],{4,4}];
 spatial=gref[[2;;4,2;;4]];inv3=Inverse[spatial];
 kk=D[spatial,rT]/2;ktrace=simp[Tr[inv3.kk]];
 gamma3[d_,a_,b_]:=gamma3[d,a,b]=simp[Sum[inv3[[d,j]](
  D[spatial[[j,b]],coords[[a+1]]]+D[spatial[[j,a]],coords[[b+1]]]-
  D[spatial[[a,b]],coords[[j+1]]])/2,{j,3}]];
 r3up[a_,b_,c_,d_]:=r3up[a,b,c,d]=simp[D[gamma3[d,b,c],coords[[a+1]]]-
  D[gamma3[d,a,c],coords[[b+1]]]+Sum[gamma3[d,a,k]gamma3[k,b,c]-
  gamma3[d,b,k]gamma3[k,a,c],{k,3}]];
 dk[a_,b_,c_]:=simp[D[kk[[b,c]],coords[[a+1]]]-Sum[
  gamma3[j,a,b]kk[[j,c]]+gamma3[j,a,c]kk[[b,j]],{j,3}]];
 div=Table[simp[Sum[inv3[[b,c]]dk[c,a,b],{b,3},{c,3}]],{a,3}];
 grad=Table[D[ktrace,coords[[a+1]]],{a,3}];
 r3=simp[Sum[inv3[[a,b]]r3up[c,b,a,c],{a,3},{b,3},{c,3}]];
 gauss=Table[-nativeX[[a+1,b+1,c+1,d+1]]-
  Sum[spatial[[d,j]]r3up[a,b,c,j],{j,3}]-kk[[b,c]]kk[[a,d]]+kk[[a,c]]kk[[b,d]],
  {a,3},{b,3},{c,3},{d,3}];
 codazzi=Table[-nativeX[[a+1,b+1,c+1,1]]+dk[a,b,c]-dk[b,a,c],{a,3},{b,3},{c,3}];
 normal={1,0,0,0};normalDown=gref.normal;hfull=gref+Outer[Times,normalDown,normalDown];
 flux={0,rQx,rQy,rQz};
 stress=rRho Outer[Times,normalDown,normalDown]+Outer[Times,normalDown,flux]+
  Outer[Times,flux,normalDown]+rPressure hfull;
 eNative=nativeRic-gref Sum[inv[[a,b]]nativeRic[[a,b]],{a,4},{b,4}]/2+rLambda gref-rKG stress;
 mNative=-((IdentityMatrix[4]+Outer[Times,normalDown,normal]).eNative.normal)[[2;;4]];
 mReference=-div+grad-rKG Rest[flux];mOld=div-grad-rKG Rest[flux];
 sentinel={rT->0,rX->0,Global`BASSN1A->1/rEll,Global`BASSN1H1->1/rEll,
  Global`BASSN1H2->0,Global`BASSN1H3->0};
 residuals=<|
  "PACKAGE_DEFINITIONS"->If[TrueQ[packageOK],0,1],
  "NORMAL_POSITIVE_K"->Join[{normal.gref.normal+1},Flatten[
   Table[kk[[a,b]]-gamma[1,a+1,b+1],{a,3},{b,3}]]],
  "RAW_TO_BASS_RIEMANN"->nativeX+referenceB,
  "PHYSICAL_RICCI_BASS"->nativeRic-referenceRic,
  "PHYSICAL_RICCI_XACT"->nativeRic-rawContraction,
  "GAUSS_POSITIVE_K"->gauss,"CODAZZI_POSITIVE_K"->codazzi,
  "MIXED_RICCI"->nativeRic[[2;;4,1]]-div+grad,
  "MOMENTUM_MATTER"->mNative-mReference,
  "HAMILTONIAN"->eNative[[1,1]]-(r3+ktrace^2-Tr[(inv3.kk).(inv3.kk)])/2+rLambda+rKG rRho,
  "NONZERO_BIANCHI_V"->((mNative[[1]]-mOld[[1]])/.sentinel)-4/rEll^2,
  "WRONG_RICCI_SIGN"->((nativeRic[[2,1]]+referenceRic[[2,1]])/.sentinel)+4/rEll^2|>;
 simplified=Map[simp,residuals];
 checks=Map[Function[v,AllTrue[Flatten[{v}],SameQ[#,0]&]],simplified];
 exactIDs=Sort[Keys[checks]]===Sort[required]&&DuplicateFreeQ[Keys[checks]];
 <|"status"->If[TrueQ[exactIDs]&&AllTrue[Values[checks],TrueQ],
   "PASS_NATIVE_TYPED_VIEW_CALIBRATION_ONLY","FAIL_NATIVE_TYPED_VIEW_CALIBRATION"],
  "required_ids"->required,"observed_ids"->Keys[checks],"checks"->checks,
  "failed_ids"->Keys@Select[checks,!TrueQ[#]&],
  "residuals"->Map[ToString[InputForm[#]]&,simplified],
  "observed_momentum_discrepancy"->ToString[InputForm[simp[(mNative[[1]]-mOld[[1]])/.sentinel]]],
  "xTensor_version"->ToString[InputForm[xAct`xTensor`$Version]],
  "xCoba_version"->ToString[InputForm[xAct`xCoba`$Version]],
  "xcoba_file"->xcobaFile,
  "comparison_scope"->"GENERIC_EXPONENTIAL_BIANCHI_V_COMPONENTS_NOT_GENERAL_ABSTRACT_PROOF"|>
];
Block[{$MessageList={}},
 result=CheckAbort[TimeConstrained[nativeBody[],180,Failure["NATIVE_TIMEOUT",<||>]],
  Failure["NATIVE_ABORT",<||>]];
 nativeMessages=ToString[InputForm[#]]&/@$MessageList;
];
If[FailureQ[result]||!AssociationQ[result],
 finish[<|"status"->"FAIL_NATIVE_EVALUATION","failure"->result,
  "messages"->nativeMessages|>,1]];
result=Append[result,"messages"->nativeMessages];
If[nativeMessages=!={},result=Append[result,"status"->"FAIL_NATIVE_MESSAGES"]];
finish[result,If[Lookup[result,"status",""]==="PASS_NATIVE_TYPED_VIEW_CALIBRATION_ONLY",0,1]];
