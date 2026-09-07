(* ::Package:: *)
BeginPackage["BASS`Authority`"];
BG02ConventionRegistry::usage="Read the pinned versioned BG-02 owner convention; no tensor admission.";
BG02ConventionRegistryQ::usage="Validate the typed curvature/momentum semantic contract.";
BG02MomentumComponent::usage="Evaluate the positive-K component momentum using owner coefficients.";
BG02TypedCurvature::usage="Bind all-lower components to an explicit curvature view and Ricci slots.";
BG02PhysicalRicci::usage="Contract a typed component view; this is a component adapter, not a native tensor API.";
Begin["`Private`"];
ClearAll[BG02ConventionRegistry,BG02ConventionRegistryQ,BG02MomentumComponent,
 BG02TypedCurvature,BG02PhysicalRicci];
$BG02OwnerRoot=ExpandFileName@FileNameJoin[{DirectoryName[$InputFileName],"..","..","..",".."}];
$BG02OwnerRegistryPath=FileNameJoin[{$BG02OwnerRoot,"docs","bass_master_ssot_v2",
 "BG_02_IMPLEMENTATION","BG_02_CONVENTION_V2.json"}];
$BG02OwnerRegistrySHA256="60dd32c8185d37850a6f0878ba7c461644f332b96f6fcf92ec12823cfd487868";
BG02ConventionRegistryQ[c_Association]:=Module[{cur,views,hist,msg},
 cur=Lookup[c,"curvature",<||>];views=Lookup[cur,"views",<||>];
 hist=Lookup[c,"historical_native",<||>];msg=Lookup[c,"message_policy",<||>];
 And[Lookup[c,"schema_version",None]==="2.0.0",
  Lookup[c,"contract_id",None]==="BASS_BG02_OWNER_CONVENTION_V2",
  Lookup[c,"metric_signature",None]==={-1,1,1,1},Lookup[c,"epsilon_123",None]===1,
  Lookup[cur,"index_order",None]==={"a","b","c","d"},
  Lookup[Lookup[views,"RAW_XACT",<||>],"physical_ricci_slots",None]==={"a","c","b","d"},
  Lookup[Lookup[views,"BASS_DERIVATIVE_FIRST",<||>],"physical_ricci_slots",None]==={"c","b","a","d"},
  Lookup[cur,"raw_to_bass_sign",None]===-1,Lookup[cur,"physical_ricci_negated",None]===False,
  Lookup[Lookup[c,"momentum",<||>],"coefficients_divK_gradK_kappa_q",None]==={-1,1,-1},
  Lookup[msg,"version",None]==="BG02_WHOLE_INVOCATION_STRICT_V2",
  Lookup[msg,"allowed_message_ids",None]==={},
  Lookup[hist,"bass_commit",None]==="477371143f15ef2625a7de21a5d178b09ffc1c32",
  Lookup[hist,"native_sha256",None]==="5b28385a1e2d80b4e9281675f45c3f4e92c611864c4afdf4852b840f88c5ec33"]];
BG02ConventionRegistryQ[_]:=False;
BG02ConventionRegistry[]:=Module[{c},
 If[!FileExistsQ[$BG02OwnerRegistryPath],Return[Failure["MissingBG02OwnerRegistry",<||>]]];
 If[IntegerString[FileHash[$BG02OwnerRegistryPath,"SHA256"],16,64]=!=$BG02OwnerRegistrySHA256,
  Return[Failure["BG02OwnerRegistryByteIdentityMismatch",<||>]]];
 c=Check[Import[$BG02OwnerRegistryPath,"RawJSON"],$Failed];
 If[!TrueQ[BG02ConventionRegistryQ[c]],Return[Failure["InvalidBG02OwnerConvention",<||>]]];c];
BG02MomentumComponent[divK_,gradK_,kg_,q_]:=Module[{c=BG02ConventionRegistry[]},
 If[FailureQ[c],Return[c]];
 c["momentum"]["coefficients_divK_gradK_kappa_q"].{divK,gradK,kg q}];
BG02TypedCurvature[components_List,view_String,order_List,slots_List]:=Module[{c,views,n},
 c=BG02ConventionRegistry[];If[FailureQ[c],Return[c]];
 views=c["curvature"]["views"];n=Length[components];
 If[!KeyExistsQ[views,view]||order=!={"a","b","c","d"}||
  slots=!=Lookup[Lookup[views,view,<||>],"physical_ricci_slots",None]||
  !MemberQ[{3,4},n]||Dimensions[components]=!=ConstantArray[n,4],
  Return[Failure["IncompatibleBG02CurvatureView",<|"view"->view,"order"->order,"ricci_slots"->slots|>]]];
 <|"contract_id"->c["contract_id"],"view"->view,"index_order"->order,
   "physical_ricci_slots"->slots,"components"->components|>];
BG02TypedCurvature[___]:=Failure["InvalidBG02CurvatureInput",<||>];
BG02PhysicalRicci[t_Association,inverse_List]:=Module[{checked,r,n},
 checked=BG02TypedCurvature[Lookup[t,"components",None],Lookup[t,"view",None],
  Lookup[t,"index_order",None],Lookup[t,"physical_ricci_slots",None]];
 If[FailureQ[checked]||Lookup[t,"contract_id",None]=!="BASS_BG02_OWNER_CONVENTION_V2",
  Return[Failure["InvalidBG02TypedCurvature",<||>]]];
 r=checked["components"];n=Length[r];
 If[Dimensions[inverse]=!={n,n},Return[Failure["InvalidBG02InverseMetricShape",<||>]]];
 If[checked["view"]==="RAW_XACT",
  Table[Sum[inverse[[c,d]]r[[a,c,b,d]],{c,n},{d,n}],{a,n},{b,n}],
  Table[Sum[inverse[[c,d]]r[[c,b,a,d]],{c,n},{d,n}],{a,n},{b,n}]]];
BG02PhysicalRicci[___]:=Failure["InvalidBG02RicciInput",<||>];
End[];
EndPackage[];
