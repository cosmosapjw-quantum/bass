(* Top-level MUnit tests. The runner injects the graph; this file does no path inference. *)

graph = Global`$BASSFormulaConsumerRoleGraphR2ATestData;
residuals = BASS`IR`FormulaConsumerRoleGraphR2A`BASSFormulaConsumerRoleGraphR2AResiduals[graph];
wrongSignResidual = Lookup[residuals, "rei_wrong_sign_mutant_residual"];
wrongSignVariables = Variables[{wrongSignResidual}];
wrongSignCoefficient = If[
  Length[wrongSignVariables] === 1 &&
  PolynomialQ[wrongSignResidual, First[wrongSignVariables]],
  Coefficient[wrongSignResidual, First[wrongSignVariables]],
  Missing["NotSingleVariablePolynomial"]
];

VerificationTest[
  AssociationQ[graph],
  True,
  TestID -> "02F-R2A-INJECTED-GRAPH-ASSOCIATION"
]

VerificationTest[
  BASS`IR`FormulaConsumerRoleGraphR2A`BASSFormulaConsumerRoleGraphR2AQ[graph],
  True,
  TestID -> "02F-R2A-GRAPH-VALIDATOR"
]

VerificationTest[
  Lookup[residuals, "pair_count_residual"],
  0,
  TestID -> "02F-R2A-PAIR-COUNT"
]

VerificationTest[
  Lookup[residuals, "pair_uniqueness_residual"],
  0,
  TestID -> "02F-R2A-PAIR-UNIQUENESS"
]

VerificationTest[
  Lookup[residuals, "role_count_residual"],
  0,
  TestID -> "02F-R2A-ROLE-COUNT"
]

VerificationTest[
  Lookup[residuals, "named_symbol_count_residual"],
  0,
  TestID -> "02F-R2A-NAMED-SYMBOL-COUNT"
]

VerificationTest[
  Lookup[residuals, "absent_slot_count_residual"],
  0,
  TestID -> "02F-R2A-ABSENT-SLOT-COUNT"
]

VerificationTest[
  Lookup[residuals, "htt_blackbody_role_count_residual"],
  0,
  TestID -> "02F-R2A-HTT-BLACKBODY-ROLE-SPLIT"
]

VerificationTest[
  Lookup[residuals, "rei_energy_exact_residual"],
  0,
  TestID -> "02F-R2A-REI-EXACT-SIGMAEE-RESIDUAL"
]

VerificationTest[
  wrongSignCoefficient,
  -2,
  TestID -> "02F-R2A-REI-WRONG-SIGN-MUTANT-COEFFICIENT"
]

VerificationTest[
  Lookup[residuals, "stage_dag_acyclic"],
  True,
  TestID -> "02F-R2A-STAGE-DAG-ACYCLIC"
]
