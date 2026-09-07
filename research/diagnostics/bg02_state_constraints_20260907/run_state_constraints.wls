#!/usr/bin/env wolframscript
(* SC research runner. PREPARED_UNEXECUTED; not the existing AUX/native suites. *)
$HistoryLength=0;
$BG02StateScriptDirectory=DirectoryName[$InputFileName];
ClearAll[bg02StateMain];
bg02StateMain[] := Module[
 {root, wlRel, allRel, sourceFiles, codeNames, codeFiles, tracked, hashes,
  before, after, loaded, spec, required, tests, declared, report, results,
  observed, outcomes, complete, runtime, rows, unchanged, code, diagnostics},
 root=Environment["BASS_REPO"];
 If[!StringQ[root] || !DirectoryQ[root],
   Return[<|"status"->"BLOCKED_SOURCE_ROOT","exit_code"->2|>]];
 wlRel={"wolfram/BASS/Kernel/Authority/BG02Convention.wl",
   "wolfram/BASS/Kernel/Geometry/StructureConstants.wl",
   "wolfram/BASS/Kernel/Geometry/LeviCivitaConnection.wl",
   "wolfram/BASS/Kernel/Geometry/ONFConnectionCurvature.wl",
   "wolfram/BASS/Kernel/Background/EinsteinProjection.wl"};
 allRel=Append[wlRel,"docs/bass_master_ssot_v2/BG_02_IMPLEMENTATION/BG_02_CONVENTION_V2.json"];
 sourceFiles=FileNameJoin[{root,#}]& /@ allRel;
 codeNames={"StateConstraints.wl","state_constraints_tests.wl",
   "run_state_constraints.wls","plot_state_constraints.py"};
 codeFiles=FileNameJoin[{$BG02StateScriptDirectory,#}]& /@ codeNames;
 tracked=Join[sourceFiles,codeFiles];
 If[!AllTrue[tracked,FileExistsQ],
   Return[<|"status"->"BLOCKED_INPUT_FILES","exit_code"->2,
     "missing"->Select[tracked,!FileExistsQ[#]&]|>]];
 hashes[] := AssociationThread[Join[allRel,codeNames],
   IntegerString[FileHash[#,"SHA256"],16,64]& /@ tracked];
 before=hashes[];
 Print["SC_SOURCE_BEFORE ",InputForm[before]];
 loaded=Check[Scan[Get,Take[sourceFiles,Length[wlRel]]];
   Get[codeFiles[[1]]]; True,$Failed];
 If[loaded =!= True, Return[<|"status"->"BLOCKED_SOURCE_LOAD","exit_code"->2|>]];
 spec=Get[codeFiles[[2]]];
 If[!AssociationQ[spec],Return[<|"status"->"INVALID_TEST_SPEC","exit_code"->2|>]];
 required=spec["required_ids"]; tests=spec["tests"];
 If[!ListQ[required] || !ListQ[tests] || Length[required]=!=19,
   Return[<|"status"->"INVALID_TEST_SPEC","exit_code"->2|>]];
 declared=#["TestID"]& /@ tests;
 If[!DuplicateFreeQ[declared] || Sort[declared]=!=Sort[required],
   Return[<|"status"->"INVALID_DECLARED_IDS","exit_code"->2|>]];
 Print["SC_TESTS_BEGIN ",InputForm[declared]];
 report=TestReport[tests,HandlerFunctions-><|
   "TestEvaluated"->(Print["SC_TEST_EVENT ",InputForm[#]]&)|>];
 If[Head[report]=!=TestReportObject,
   Return[<|"status"->"INVALID_REPORT","exit_code"->2|>]];
 results=report["Results"]; runtime=report["RuntimeFailures"];
 If[!ListQ[results] || !ListQ[runtime],
   Return[<|"status"->"INVALID_REPORT_PROPERTIES","exit_code"->2|>]];
 observed=#["TestID"]& /@ results; outcomes=#["Outcome"]& /@ results;
 complete=DuplicateFreeQ[observed] && Sort[observed]===Sort[required];
 rows=(<|"id"->#["TestID"],"outcome"->#["Outcome"],
   "actual"->ToString[#["ActualOutput"],InputForm],
   "expected"->ToString[#["ExpectedOutput"],InputForm],
   "actual_messages"->ToString[#["ActualMessages"],InputForm],
   "expected_messages"->ToString[#["ExpectedMessages"],InputForm]|>& /@ results);
 after=hashes[]; unchanged=before===after;
 code=Which[!complete || !unchanged || runtime=!={},2,
   TrueQ[report["ReportSucceeded"]] && AllTrue[outcomes,#==="Success"&],0,True,1];
 diagnostics=spec["diagnostic_rows"];
 If[!ListQ[diagnostics] || !AllTrue[diagnostics,AssociationQ], diagnostics={}; code=2];
 <|"stage"->"BG02_STATE_TO_CONSTRAINT_MAP_V1",
   "status"->Switch[code,0,"PASS_RESEARCH_COMPONENT_ONLY",1,"FAIL_RESEARCH_COMPONENT",_,"INVALID_RESEARCH_RUN"],
   "exit_code"->code,"wolfram_version"->$Version,
   "native_xact"->False,"production_admitted"->False,
   "required_ids"->required,"observed_ids"->observed,"exact_ids"->complete,
   "rows"->rows,"runtime_failures"->ToString[runtime,InputForm],
   "source_before"->before,"source_after"->after,"source_unchanged"->unchanged,
   "diagnostic_rows"->diagnostics,"diagnostic_units"->spec["diagnostic_units"]|>
];
scResult=CheckAbort[Check[TimeConstrained[bg02StateMain[],120,
   <|"status"->"RESEARCH_TIMEOUT","exit_code"->2|>],
   <|"status"->"RESEARCH_MESSAGE_ERROR","exit_code"->2|>],
   <|"status"->"RESEARCH_ABORT","exit_code"->2|>];
If[!AssociationQ[scResult],scResult=<|"status"->"INVALID_RESULT","exit_code"->2|>];
Print["SC_FINAL_BEGIN"];
Print[ExportString[scResult,"RawJSON"]];
Print["SC_FINAL_END"];
Exit[Lookup[scResult,"exit_code",2]];
