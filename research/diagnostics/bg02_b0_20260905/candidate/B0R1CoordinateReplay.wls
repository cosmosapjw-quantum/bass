#!/usr/bin/env wolframscript
(* Coordinate component replay only. This does not load xAct or admit BASS. *)
ClearAll[bgT,bgX,bgY,bgZ,bgH1,bgH2,bgH3,bgA,bgEll];
bgOut=Environment["BASS_B0R1_RECEIPT"];
If[!StringQ[bgOut] || StringLength[bgOut]==0,
 Print["BLOCKED: set BASS_B0R1_RECEIPT to a new JSON path"];Exit[2]];
If[FileExistsQ[bgOut],Print["BLOCKED: receipt already exists"];Exit[2]];
bgResult=TimeConstrained[
 Module[{qq,gg,iv,ga,ric,expected,mismatch,raw},
 qq={bgT,bgX,bgY,bgZ};
 gg=DiagonalMatrix[{-1,Exp[2 bgH1 bgT],
  Exp[2 bgH2 bgT-2 bgA bgX],Exp[2 bgH3 bgT-2 bgA bgX]}];
 iv=Inverse[gg];
 ga=Table[Simplify[Sum[iv[[d,j]](D[gg[[j,b]],qq[[a]]]+
  D[gg[[j,a]],qq[[b]]]-D[gg[[a,b]],qq[[j]]])/2,{j,4}]],
  {d,4},{a,4},{b,4}];
 ric=Table[Simplify[Sum[D[ga[[d,c,b]],qq[[d]]]-
  D[ga[[d,d,c]],qq[[b]]]+Sum[ga[[d,d,k]]ga[[k,c,b]]-
  ga[[d,b,k]]ga[[k,d,c]],{k,4}],{d,4}]],{c,4},{b,4}];
 expected=bgA(-2 bgH1+bgH2+bgH3);
 mismatch=Simplify[(-ric[[2,1]]-expected)/.
  {bgA->1/bgEll,bgH1->1/bgEll,bgH2->0,bgH3->0}];
 raw=<|"mixed_ricci_residual"->Simplify[ric[[2,1]]-expected],
  "old_momentum_counterexample_residual"->Simplify[mismatch-4/bgEll^2]|>;
 <|"schema_version"->"1.0.0","stage_id"->"BG02_B0R1_WL_COORDINATE_REPLAY",
  "wolfram_version"->$Version,
  "checks"->Map[SameQ[#,0]&,raw],
  "Ricci_x_tau"->ToString[InputForm[ric[[2,1]]]],
  "old_momentum_counterexample"->ToString[InputForm[mismatch]],
  "native_xtensor_executed"->False,"production_source_modified"->False,
  "status"->If[AllTrue[Values[raw],SameQ[#,0]&],
   "PASS_COORDINATE_REPLAY_ONLY","FAIL_COORDINATE_REPLAY"]|>
 ],60,<|"status"->"BLOCKED_WL_TIME_LIMIT","native_xtensor_executed"->False|>];
If[!AssociationQ[bgResult],bgResult=<|"status"->"FAIL_NO_ASSOCIATION"|>];
bgParent=DirectoryName[ExpandFileName[bgOut]];
If[!DirectoryQ[bgParent],CreateDirectory[bgParent,CreateIntermediateDirectories->True]];
bgTmp=bgOut<>".tmp."<>ToString[$ProcessID];
If[FileExistsQ[bgTmp],Print["BLOCKED: temporary path exists"];Exit[2]];
bgSerialized=Quiet@Check[ExportString[bgResult,"RawJSON"],$Failed];
If[!StringQ[bgSerialized],Print["FAIL_JSON_SERIALIZATION"];Exit[3]];
bgStream=OpenWrite[bgTmp,CharacterEncoding->"UTF8"];
WriteString[bgStream,bgSerialized];Close[bgStream];
bgRound=Quiet@Check[Import[bgTmp,"RawJSON"],$Failed];
If[!AssociationQ[bgRound] || bgRound=!=bgResult,
 Print["FAIL_JSON_ROUNDTRIP"];Exit[3]];
bgRename=Quiet@Check[RenameFile[bgTmp,bgOut],$Failed];
If[bgRename===$Failed,Print["FAIL_RECEIPT_PUBLICATION"];Exit[3]];
Print[InputForm[bgResult]];
Exit[If[Lookup[bgResult,"status",""]==="PASS_COORDINATE_REPLAY_ONLY",0,1]];
