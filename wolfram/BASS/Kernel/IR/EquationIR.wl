(* ::Package:: *)

BeginPackage["BASS`IR`"];

MakeEquationIR::usage = "MakeEquationIR[spec] fills defaults and canonicalizes an equation IR.";
EquationRequiredKeys::usage = "EquationRequiredKeys[] returns required equation keys.";
EquationIRQ::usage = "EquationIRQ[ir] validates an equation IR.";

Begin["`Private`"];

ClearAll[MakeEquationIR, EquationRequiredKeys, EquationIRQ];
EquationRequiredKeys[] := {"schema_version", "formula_id", "authority_theorem",
 "target", "free_indices", "representation", "assumptions", "domain",
 "dimensions", "terms", "structural_zero_rules", "branch_predicates",
 "known_limits", "provenance"};

MakeEquationIR[spec_Association] := BASS`IR`CanonicalizeData @ Join[
 <|"schema_version" -> "1.0.0", "formula_id" -> Missing["Required"],
  "authority_theorem" -> Missing["Required"], "target" -> Missing["Required"],
  "free_indices" -> {}, "representation" -> "abstract", "assumptions" -> {},
  "domain" -> <||>, "dimensions" -> <||>, "terms" -> {},
  "structural_zero_rules" -> {}, "branch_predicates" -> {},
  "known_limits" -> {}, "provenance" -> <||>|>, spec];

EquationIRQ[ir_Association] := And[
 SubsetQ[Keys[ir], EquationRequiredKeys[]],
 Lookup[ir, "schema_version", None] === "1.0.0",
 StringQ[Lookup[ir, "formula_id", None]],
 StringQ[Lookup[ir, "authority_theorem", None]],
 StringQ[Lookup[ir, "target", None]],
 ListQ[Lookup[ir, "free_indices", None]],
 StringQ[Lookup[ir, "representation", None]],
 ListQ[Lookup[ir, "assumptions", None]],
 AssociationQ[Lookup[ir, "domain", None]],
 AssociationQ[Lookup[ir, "dimensions", None]],
 ListQ[Lookup[ir, "terms", None]],
 AllTrue[Lookup[ir, "terms", {}],
  AssociationQ[#] && BASS`IR`ExactScalarASTQ[Lookup[#, "coefficient", None]] &],
 ListQ[Lookup[ir, "structural_zero_rules", None]],
 ListQ[Lookup[ir, "branch_predicates", None]],
 ListQ[Lookup[ir, "known_limits", None]],
 AssociationQ[Lookup[ir, "provenance", None]]];
EquationIRQ[_] := False;

End[];
EndPackage[];
