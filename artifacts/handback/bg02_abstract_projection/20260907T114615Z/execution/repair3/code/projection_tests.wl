(* Test specification for the conditional abstract projection bridge.
   PREPARED_UNEXECUTED. These AP IDs are not AUX17, SC19, capture6 or native17.
   No observed RED/GREEN is claimed by authoring this file. *)
ClearAll[BG02APTests];
BG02APTests[proof_Association] := Module[{ids, expected, residuals},
 ids={
  "AP00_XTENSOR_RICCI_CONTRACTION",
  "AP01_CURVATURE_SYMMETRIES",
  "AP02_GAUSS_BLOCK",
  "AP03_CODAZZI_BLOCK",
  "AP04_NORMAL_RICCI_BLOCK",
  "AP05_HAMILTONIAN_PROJECTION",
  "AP06_MOMENTUM_PROJECTION",
  "AP07_SPATIAL_TRACE_PROJECTION",
  "AP08_SPATIAL_PSTF_PROJECTION",
  "AP09_FULL_RESIDUAL_RECONSTRUCTION",
  "AP10_EXISTING_CONSUMER_ADAPTER",
  "AP11_LIE_METRIC_TRACE_ADAPTER",
  "AP12_TRACE_MUTATION_NONZERO_WITNESS"};
 expected={0,{0,0,0,0},0,0,0,0,0,0,0,0,{0,0,0,0},{0,0},{0,0}};
 residuals=Lookup[proof,"residuals",Missing["NoResiduals"]];
 If[!AssociationQ[residuals] || Sort[Keys[residuals]]=!=Sort[ids],
   Return[Failure["APResidualSet",<|"required"->ids|>]]];
 <|"required_ids"->ids,
   "tests"->MapThread[
     Function[{id,value},With[{key=id,target=value},
       TestCreate[residuals[key],target,TestID->key]]],{ids,expected}]|>
];
BG02APTests[_] := Failure["APProofNotEvaluated",<||>];
