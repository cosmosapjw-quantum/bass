(* ::Package:: *)

BeginPackage["BASS`IR`"];

Begin["`Private`"];

ClearAll[claimBoundaryQ];

claimBoundaryQ[data_Association] :=
 Lookup[data, "claim_boundary", None] ===
  "SHARED_FRAME_PHOTON_EQUATIONIR_EXPORT_ONLY_NO_BACKGROUND_PROVIDER_GLOBAL_TILT_FINITE_ELECTRON_COLLISION_CONSUMER_EQUIVALENCE_OBSERVATIONAL_STATISTICAL_OR_SCIENCE_PROMOTION";
claimBoundaryQ[_] := False;

End[];
EndPackage[];
