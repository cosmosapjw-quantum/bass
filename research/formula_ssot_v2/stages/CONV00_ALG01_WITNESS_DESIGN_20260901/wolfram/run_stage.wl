(* ::Script:: *)
stageDirectory=DirectoryName[DirectoryName[ExpandFileName[$InputFileName]]]; wd=FileNameJoin[{stageDirectory,"wolfram"}];
Get[FileNameJoin[{wd,"00_bootstrap_xact.wl"}]];Get[FileNameJoin[{wd,"10_conv00_registry.wl"}]];
Get[FileNameJoin[{wd,"20_alg01_cartan_generator.wl"}]];Get[FileNameJoin[{wd,"30_alg01_witnesses.wl"}]];
offline=Environment["BASS_XACT_ARCHIVE"];
bootstrap=If[StringLength[offline]>0,BASSXActBootstrap["ArchivePath"->offline],BASSXActBootstrap[]];
If[FailureQ[bootstrap],Print[bootstrap];Exit[65]];
conv=ValidateCONV00[];generic=ValidateALG01Generic[];witness=ValidateALG01Witnesses[];
status=If[bootstrap["Status"]==="PASS"&&conv["Status"]==="PASS"&&generic["Status"]==="PASS"&&witness["Status"]==="PASS","PASS_CONV00_ALG01_SCOPED_SYMBOLIC_WITNESS","FAIL"];
receipt=<|"Schema"->"bass-formula-ssot-v2-conv00-alg01-receipt/v1","StageID"->"BASS-SSOT-V2-CONV00-ALG01-20260901","Status"->status,
 "ClaimCeiling"->"SYMBOLIC_WITNESS_ONLY_NO_BACKGROUND_RHS_NO_RUNTIME_NO_RF04_PROMOTION","WolframVersion"->$Version,"SystemID"->$SystemID,
 "xAct"->bootstrap,"CONV00"->conv,"ALG01Generic"->generic,"ALG01Witnesses"->witness|>;
Export[FileNameJoin[{stageDirectory,"receipts","WOLFRAM_EXECUTION_RECEIPT.generated.json"}],receipt,"RawJSON"];
rows=witness["AdversarialPlotData"];
Export[FileNameJoin[{stageDirectory,"plots","ALG01_WITNESS_RESIDUALS.generated.csv"}],Prepend[(Lookup[#,{"Witness","CorrectResidual","MutationResidual"}]&/@rows),{"witness","correct_residual","mutation_residual"}],"CSV"];
Export[FileNameJoin[{stageDirectory,"plots","ALG01_WITNESS_RESIDUALS.generated.svg"}],BarChart[{Lookup[rows,"CorrectResidual"],Lookup[rows,"MutationResidual"]},ChartLayout->"Grouped",ChartLegends->{"declared witness","adversarial mutation"},ChartLabels->Placed[Lookup[rows,"Witness"],Below],AxesLabel->{"witness","maximum exact residual"},PlotLabel->"CONV-00 + ALG-01 witness residual gate"],"SVG"];
Print[receipt];Exit[If[status==="PASS_CONV00_ALG01_SCOPED_SYMBOLIC_WITNESS",0,1]];
