(* ::Package:: *)

ClearAll[BG02FormulaRegistryValidation];

BG02FormulaRegistryValidation[] := Module[
 {path, registry, formulas, ids, dependencies, localDependencies,
  duplicateFree, dependencyClosed, dimensionsValid, countValid,
  status},

 path = FileNameJoin[{DirectoryName[$InputFileName],
    "BG_02_FORMULA_REGISTRY.json"}];
 registry = Quiet@Check[Import[path, "RawJSON"], $Failed];

 If[registry === $Failed || !AssociationQ[registry],
  Return[<|
    "status" -> "FAIL",
    "reason" -> "FORMULA_REGISTRY_JSON_IMPORT_FAILED",
    "path" -> path
  |>]
 ];

 formulas = Lookup[registry, "formulas", {}];
 ids = Lookup[formulas, "formula_id", {}];
 dependencies = Flatten[Lookup[formulas, "depends_on", {}]];
 localDependencies = Select[dependencies,
   StringStartsQ[#, "BASS.BG."] &];

 duplicateFree = DuplicateFreeQ[ids];
 dependencyClosed = Complement[localDependencies, ids] === {};
 dimensionsValid = AllTrue[
   Lookup[formulas, "dimension", {}],
   SameQ[#, "L^-2"] &
 ];
 countValid = Lookup[registry, "formula_count", -1] === Length[ids] === 14;

 status = If[
   And[duplicateFree, dependencyClosed, dimensionsValid, countValid],
   "PASS", "FAIL"
 ];

 <|
  "status" -> status,
  "formula_count" -> Length[ids],
  "unique_formula_ids" -> duplicateFree,
  "local_dependencies_closed" -> dependencyClosed,
  "all_dimensions_L_minus_2" -> dimensionsValid,
  "declared_count_matches" -> countValid,
  "external_dependencies" ->
    Sort@DeleteDuplicates@Complement[dependencies, ids],
  "claim_boundary" ->
    "REGISTRY_STRUCTURE_ONLY_NOT_FORMULA_SEMANTICS_OR_NATIVE_XACT_PROJECTION"
 |>
];

Print@ExportString[BG02FormulaRegistryValidation[], "RawJSON"];
