(* ::Package:: *)

BeginPackage["BASS`IR`"];

CanonicalizeData::usage = "CanonicalizeData[expr] recursively sorts association keys.";
CanonicalRawJSON::usage = "CanonicalRawJSON[expr] exports canonical RawJSON text.";
CanonicalSHA256::usage = "CanonicalSHA256[expr] hashes canonical RawJSON.";
RawJSONRoundTripQ::usage = "RawJSONRoundTripQ[expr] checks canonical JSON round-trip identity.";

Begin["`Private`"];

ClearAll[CanonicalizeData, CanonicalRawJSON, CanonicalSHA256, RawJSONRoundTripQ, keyOrder];
keyOrder[key_] := ToString[Unevaluated[key], InputForm];
CanonicalizeData[assoc_Association] := Association @ Map[
 Rule[First[#], CanonicalizeData[Last[#]]] &,
 SortBy[Normal[assoc], keyOrder[First[#]] &]];
CanonicalizeData[list_List] := CanonicalizeData /@ list;
CanonicalizeData[rule_Rule] := Rule[CanonicalizeData[First[rule]], CanonicalizeData[Last[rule]]];
CanonicalizeData[expr_] := expr;
CanonicalRawJSON[expr_] := ExportString[CanonicalizeData[expr], "RawJSON", "Compact" -> True];
CanonicalSHA256[expr_] := IntegerString[Hash[CanonicalRawJSON[expr], "SHA256"], 16, 64];
RawJSONRoundTripQ[expr_] := SameQ[
 ImportString[CanonicalRawJSON[expr], "RawJSON"], CanonicalizeData[expr]];

End[];
EndPackage[];
