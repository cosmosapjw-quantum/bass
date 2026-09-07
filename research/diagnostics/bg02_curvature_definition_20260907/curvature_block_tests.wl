(* Test specification for BG02 curvature-definition-to-block derivation.
   PREPARED_UNEXECUTED. These CB IDs are new and do not consume AP/SC/AUX/native17 counts. *)
ClearAll[BG02CBTests];
BG02CBTests[proof_Association] := Module[{ids,residuals},
 ids={
  "CB00_POSITIVE_K_ACCELERATION_SIGN_LOCK",
  "CB01_GAUSS_OPERATOR_COMMUTATOR",
  "CB02_GAUSS_TENSOR",
  "CB03_CODAZZI_OPERATOR_COMMUTATOR",
  "CB04_CODAZZI_TENSOR",
  "CB05_NORMAL_RICCI_OPERATOR_COMMUTATOR",
  "CB06_LIE_VS_PROJECTED_NORMAL_K",
  "CB07_NORMAL_RICCI_TENSOR",
  "CB08_XTENSOR_INDUCED_DECOMPOSITION_RECONSTRUCTION"};
 residuals=Lookup[proof,"residuals",Missing["NoResiduals"]];
 If[!AssociationQ[residuals]||Sort[Keys[residuals]]=!=Sort[ids],
   Return[Failure["CBResidualSet",<|"required"->ids,"observed"->If[AssociationQ[residuals],Keys[residuals],{}]|>]]];
 <|"required_ids"->ids,
   "tests"->(With[{key=#},TestCreate[residuals[key],0,TestID->key]]& /@ ids)|>
];
BG02CBTests[_] := Failure["CBProofNotEvaluated",<||>];
