(* ::Package:: *)

BeginPackage["BASS`IR`"];

Begin["`Private`"];

Clear[BASS`IR`CrossRepositorySemanticGraphReceipt];
BASS`IR`CrossRepositorySemanticGraphReceipt[] := Module[
 {summary = BASS`IR`CrossRepositorySemanticGraphSummary[], adapters, reiDifference},
 adapters = BASS`IR`CrossRepositorySemanticAdapterReport[];
 reiDifference = Lookup[adapters, "REIHOnlyMinusGenericEnergyDrift"];
 <|
  "Status" -> If[
    BASS`IR`CrossRepositorySemanticGraphSummaryQ[summary] &&
     Lookup[adapters, "FuturePhotonOutwardSkyDopplerResidual"] === 0 &&
     Lookup[adapters, "RECEnergyRateAdapterResidual"] === 0 &&
     Lookup[adapters, "RECDirectionRateAdapterResidual"] === 0 &&
     !TrueQ[reiDifference === 0] &&
     Lookup[adapters, "REIHOnlyIsotropicControlResidual"] === 0 &&
     FalseQ[Lookup[adapters, "REIGenericEquivalenceQ"]],
    "PASS", "FAIL"],
  "FormulaCount" -> 6,
  "ConsumerRelationCount" -> 10,
  "AuthorityEffect" -> "NONE_BEYOND_BOUNDED_SEMANTIC_GRAPH",
  "Withheld" -> {
   "CONSUMER_IMPLEMENTATION_PARITY", "GLOBAL_MATTER_TILT",
   "FINITE_ELECTRON_TILT_COLLISION", "PROVIDER_ADMISSION",
   "NUMERICAL_PARITY", "SCIENCE_VALIDITY", "PASS_RF04"
  }
 |>
];

End[];
EndPackage[];
