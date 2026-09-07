$HistoryLength=0;
Needs["xAct`xTensor`"];
Begin["APRegression`"];
DefManifold[RM,4,{ia,ib,ic,id,ie,iff}];
DefMetric[-1,met[-ia,-ib],RCD,{";","D"}];
DefTensor[nu[ia],RM]; DefTensor[flux[-ia],RM];
DefTensor[KK[-ia,-ib],RM,Symmetric[{-ia,-ib}]];
DefTensor[Sigma[-ia,-ib],RM,Symmetric[{-ia,-ib}]];
DefTensor[HH[],RM];
projector[x_,y_] := met[x,y]+nu[x]nu[y];
mode=Environment["AP_REGRESSION_MODE"];
green=mode==="green";
Block[{$MessageList={}},
 helperRules=If[green,
   Catch[MakeRule[Evaluate[{KK[-ia,-ib],HH[]projector[-ia,-ib]+Sigma[-ia,-ib]}],MetricOn->All,ContractMetrics->True]],
   Catch[MakeRule[{KK[-ia,-ib],HH[]projector[-ia,-ib]+Sigma[-ia,-ib]},MetricOn->All,ContractMetrics->True]]];
 helperMessages=ToString[#,InputForm]& /@ $MessageList;
];
orthogonalRules=If[green,
 Flatten[Table[MakeRule[Evaluate[{nu[ia]t[-ia,-ib],0}],MetricOn->All,ContractMetrics->True],{t,{KK,Sigma}}],1],
 Flatten[Table[MakeRule[{nu[ia]t[-ia,-ib],0},MetricOn->All,ContractMetrics->True],{t,{KK,Sigma}}],1]];
traceRules=If[green,
 Flatten[Table[MakeRule[Evaluate[{t[ia,-ia],0}],MetricOn->All,ContractMetrics->True],{t,{Sigma}}],1],
 Flatten[Table[MakeRule[{t[ia,-ia],0},MetricOn->All,ContractMetrics->True],{t,{Sigma}}],1]];
normalRules=MakeRule[{nu[ia]nu[-ia],-1},MetricOn->All,ContractMetrics->True];
mActual=flux[-ia]; sActual=Sigma[-ia,-ib];
If[green,
 mTensor[x_] := ReplaceIndex[Evaluate[ReplaceDummies[mActual]],{-ia->x}];
 sTensor[x_,y_] := ReplaceIndex[Evaluate[ReplaceDummies[sActual]],{-ia->x,-ib->y}],
 mTensor[x_] := ReplaceIndex[ReplaceDummies[mActual],{ia->-x}];
 sTensor[x_,y_] := ReplaceIndex[ReplaceDummies[sActual],{ia->-x,ib->-y}]
];
checks=<|
 "REG_MAKERULE_HELPER_EVALUATION"->ListQ[helperRules],
 "REG_ITERATOR_ORTHOGONALITY"->TrueQ[ToCanonical[nu[ia]KK[-ia,-ib]/.orthogonalRules]===0],
 "REG_ITERATOR_TRACE"->TrueQ[ToCanonical[Sigma[ia,-ia]/.traceRules]===0],
 "REG_COVARIANT_VECTOR_REINDEX"->TrueQ[ToCanonical[mTensor[-ib]-flux[-ib]]===0],
 "REG_COVARIANT_TENSOR_REINDEX"->TrueQ[ToCanonical[sTensor[-ic,-id]-Sigma[-ic,-id]]===0],
 "REG_TANGENTIAL_TENSOR_RETAINED"->TrueQ[ToCanonical[Sigma[-ia,-ib]/.orthogonalRules/.traceRules]===Sigma[-ia,-ib]],
 "REG_TIMELIKE_NORM_RETAINED"->TrueQ[ToCanonical[nu[ia]nu[-ia]/.normalRules]===-1]|>;
mActual=KK[-ia,ib]flux[-ib];
checks=Append[checks,"REG_REINDEX_WITH_EXISTING_DUMMY"->TrueQ[Catch[ToCanonical[mTensor[-ib]-KK[-ib,ic]flux[-ic]]]===0]];
tests=KeyValueMap[Function[{key,value},With[{id=key,actual=value},TestCreate[actual,True,TestID->id]]],checks];
report=TestReport[tests];
rows=(<|"id"->#["TestID"],"outcome"->#["Outcome"],"actual"->ToString[#["ActualOutput"],InputForm],"expected"->ToString[#["ExpectedOutput"],InputForm]|>& /@ report["Results"]);
Print["REGRESSION_JSON_BEGIN"];
Print[ExportString[<|"mode"->mode,"rows"->rows,"helper_messages"->helperMessages,"passed"->report["ReportSucceeded"]|>,"RawJSON"]];
Print["REGRESSION_JSON_END"];
Exit[If[TrueQ[report["ReportSucceeded"]],0,1]];
