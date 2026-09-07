#!/usr/bin/env wolframscript
(* PREPARED_UNEXECUTED. New conditional abstract contraction task only.
   Uses already-installed xTensor. Does not call xCoba, native17 or capture6. *)
$HistoryLength=0;
$APDirectory=DirectoryName[$InputFileName];
ClearAll[apSafe,apMain];
apSafe[x_Association] := AssociationThread[Keys[x],apSafe /@ Values[x]];
apSafe[x_List] := apSafe /@ x;
apSafe[x_String|x_Integer|x_Real] := x;
apSafe[True]=True; apSafe[False]=False; apSafe[Null]=Null;
apSafe[x_] := ToString[x,InputForm];
apMain[] := Module[{root,paths,files,local,hashes,before,after,xtensorFile,
  xactBefore,xactAfter,loaded,proof,spec,report,results,ids,required,complete,
  rows,runtime,allSuccess,exitCode},
 root=Environment["BASS_REPO"];
 If[!StringQ[root]||!DirectoryQ[root],Return[<|"status"->"BLOCKED_SOURCE_ROOT","exit_code"->2|>]];
 paths={"wolfram/BASS/Kernel/Authority/BG02Convention.wl",
   "wolfram/BASS/Kernel/Geometry/StructureConstants.wl",
   "wolfram/BASS/Kernel/Geometry/LeviCivitaConnection.wl",
   "wolfram/BASS/Kernel/Geometry/ONFConnectionCurvature.wl",
   "wolfram/BASS/Kernel/Background/EinsteinProjection.wl",
   "docs/bass_master_ssot_v2/BG_02_IMPLEMENTATION/BG_02_CONVENTION_V2.json"};
 files=FileNameJoin[{root,#}]& /@ paths;
 local=FileNameJoin[{$APDirectory,#}]& /@
   {"AbstractProjection.wl","projection_tests.wl","run_projection.wls"};
 If[!AllTrue[Join[files,local],FileExistsQ],
   Return[<|"status"->"BLOCKED_INPUT_FILES","exit_code"->2,
     "missing"->Select[Join[files,local],!FileExistsQ[#]&]|>]];
 hashes[] := AssociationThread[Join[paths,FileNameTake /@ local],
   IntegerString[FileHash[#,"SHA256"],16,64]& /@ Join[files,local]];
 before=hashes[]; Print["AP_SOURCE_BEFORE ",InputForm[before]];
 If[AnyTrue[$Packages,StringStartsQ[#,"xAct`"]&],
   Return[<|"status"->"BLOCKED_PRELOADED_XACT","exit_code"->2|>]];
 xtensorFile=FindFile["xAct`xTensor`"];
 If[!StringQ[xtensorFile]||!FileExistsQ[xtensorFile],
   Return[<|"status"->"BLOCKED_INSTALLED_XTENSOR_UNAVAILABLE","exit_code"->2|>]];
 xactBefore=IntegerString[FileHash[xtensorFile,"SHA256"],16,64];
 Print["AP_XTENSOR_INIT ",InputForm[{xtensorFile,xactBefore}]];
 loaded=Check[Needs["xAct`xTensor`"];
   Get[files[[1]]];Get[files[[5]]];Get[local[[1]]];Get[local[[2]]];True,$Failed];
 If[loaded=!=True || !MemberQ[$Packages,"xAct`xTensor`"] ||
    Length[DownValues[xAct`xTensor`ToCanonical]]===0,
   Return[<|"status"->"BLOCKED_NATIVE_DEPENDENCY_LOAD","exit_code"->2|>]];
 Print["AP_PROOF_BEGIN"];
 proof=BASS`Research`AP1`BuildAbstractProjectionProof[];
 If[!AssociationQ[proof],Return[<|"status"->"AP_PROOF_INVALID","exit_code"->2,"failure"->proof|>]];
 spec=BG02APTests[proof];
 If[!AssociationQ[spec],Return[<|"status"->"AP_TEST_SPEC_INVALID","exit_code"->2,"failure"->spec|>]];
 required=spec["required_ids"];
 If[Length[required]=!=13 || !DuplicateFreeQ[required],
   Return[<|"status"->"AP_DECLARED_IDS_INVALID","exit_code"->2|>]];
 Print["AP_TESTS_BEGIN ",InputForm[required]];
 report=TestReport[spec["tests"],HandlerFunctions-><|
   "TestEvaluated"->(Print["AP_TEST_EVENT ",InputForm[#]]&)|>];
 If[Head[report]=!=TestReportObject,Return[<|"status"->"AP_REPORT_INVALID","exit_code"->2|>]];
 results=report["Results"];runtime=report["RuntimeFailures"];
 If[!ListQ[results]||!ListQ[runtime],Return[<|"status"->"AP_REPORT_PROPERTIES_INVALID","exit_code"->2|>]];
 ids=#["TestID"]& /@ results;
 complete=DuplicateFreeQ[ids]&&Sort[ids]===Sort[required];
 rows=(<|"id"->#["TestID"],"outcome"->#["Outcome"],
   "actual"->ToString[#["ActualOutput"],InputForm],
   "expected"->ToString[#["ExpectedOutput"],InputForm],
   "actual_messages"->ToString[#["ActualMessages"],InputForm],
   "expected_messages"->ToString[#["ExpectedMessages"],InputForm]|>& /@ results);
 after=hashes[];xactAfter=IntegerString[FileHash[xtensorFile,"SHA256"],16,64];
 allSuccess=TrueQ[report["ReportSucceeded"]]&&AllTrue[results,#["Outcome"]==="Success"&];
 exitCode=Which[!complete||before=!=after||xactBefore=!=xactAfter||runtime=!={},2,
   allSuccess,0,True,1];
 <|"task"->"BG02_ABSTRACT_CURVATURE_BLOCK_CONTRACTION_V1",
   "status"->Switch[exitCode,0,"PASS_CONDITIONAL_ABSTRACT_CONTRACTION_ONLY",1,"FAIL_ABSTRACT_CONTRACTION",_,"INVALID_ABSTRACT_RUN"],
   "exit_code"->exitCode,"wolfram_version"->$Version,
   "xtensor_version"->ToString[xAct`xTensor`$Version,InputForm],
   "xtensor_init"->xtensorFile,"xtensor_init_sha256"->xactAfter,
   "xtensor_archive_seal_verified_by_this_runner"->False,
   "required_ids"->required,"observed_ids"->ids,"exact_ids"->complete,
   "rows"->rows,"runtime_failures"->ToString[runtime,InputForm],
   "source_before"->before,"source_after"->after,"source_unchanged"->(before===after),
   "proof"->proof,"native_xTensor_evaluated"->True,
   "curvature_definition_to_blocks_verified"->False,
   "general_native_bridge_admitted"->False,"production_admitted"->False|>
];
Block[{$MessageList={}},
 apResult=CheckAbort[TimeConstrained[Catch[apMain[]],180,
   <|"status"->"AP_TIMEOUT","exit_code"->2|>],
   <|"status"->"AP_ABORT","exit_code"->2|>];
 apMessages=ToString[#,InputForm]& /@ $MessageList;
];
If[!AssociationQ[apResult],apResult=<|"status"->"AP_INVALID_RESULT","exit_code"->2|>];
apResult=Join[apResult,<|"whole_invocation_messages"->apMessages|>];
If[apMessages=!={} && Lookup[apResult,"exit_code",2]===0,
 apResult=Join[apResult,<|"mathematical_status"->apResult["status"],
   "status"->"AP_MESSAGE_ADMISSION_FAILED","exit_code"->2|>]];
Print["AP_FINAL_BEGIN"];
Print[ExportString[apSafe[apResult],"RawJSON"]];
Print["AP_FINAL_END"];
Exit[Lookup[apResult,"exit_code",2]];
