(* ::Package:: *)

BeginPackage["BASS`Bianchi`", {"BASS`IR`"}];
Begin["`Private`"];

Clear[nullableMatchQ];
nullableMatchQ[Null, _] := True;
nullableMatchQ[expected_Association, actual_] /;
  BASS`IR`ExactScalarASTQ[expected] := SameQ[
 BASS`IR`CanonicalizeData[expected],
 BASS`IR`CanonicalizeData[BASS`IR`ExactScalarAST[actual]]
];
nullableMatchQ[expected_, actual_] := SameQ[expected, actual];

End[];
EndPackage[];
