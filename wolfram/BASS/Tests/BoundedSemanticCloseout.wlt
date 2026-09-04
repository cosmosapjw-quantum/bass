(* Top-level MUnit tests. The runner injects the closeout graph; this file performs no path inference. *)

graph = Global`$BASSBoundedSemanticCloseoutTestData;
residuals = BASS`IR`BoundedSemanticCloseout`BASSBoundedSemanticCloseoutResiduals[graph];

VerificationTest[
  AssociationQ[graph],
  True,
  TestID -> "02F-CLOSEOUT-INJECTED-GRAPH-ASSOCIATION"
]

VerificationTest[
  BASS`IR`BoundedSemanticCloseout`BASSBoundedSemanticCloseoutQ[graph],
  True,
  TestID -> "02F-CLOSEOUT-GRAPH-VALIDATOR"
]

VerificationTest[
  Lookup[residuals, "upstream_stage_count_residual"],
  0,
  TestID -> "02F-CLOSEOUT-UPSTREAM-STAGE-COUNT"
]

VerificationTest[
  Lookup[residuals, "formula_count_residual"],
  0,
  TestID -> "02F-CLOSEOUT-FORMULA-COUNT"
]

VerificationTest[
  Lookup[residuals, "state_surface_count_residual"],
  0,
  TestID -> "02F-CLOSEOUT-STATE-SURFACE-COUNT"
]

VerificationTest[
  Lookup[residuals, "formula_consumer_pair_count_residual"],
  0,
  TestID -> "02F-CLOSEOUT-FORMULA-CONSUMER-PAIR-COUNT"
]

VerificationTest[
  Lookup[residuals, "implementation_role_count_residual"],
  0,
  TestID -> "02F-CLOSEOUT-IMPLEMENTATION-ROLE-COUNT"
]

VerificationTest[
  Lookup[residuals, "named_source_symbol_count_residual"],
  0,
  TestID -> "02F-CLOSEOUT-NAMED-SOURCE-SYMBOL-COUNT"
]

VerificationTest[
  Lookup[residuals, "absent_slot_count_residual"],
  0,
  TestID -> "02F-CLOSEOUT-ABSENT-SLOT-COUNT"
]

VerificationTest[
  Lookup[residuals, "certificate_family_count_residual"],
  0,
  TestID -> "02F-CLOSEOUT-CERTIFICATE-FAMILY-COUNT"
]

VerificationTest[
  Lookup[residuals, "relation_certificate_count_residual"],
  0,
  TestID -> "02F-CLOSEOUT-RELATION-CERTIFICATE-COUNT"
]

VerificationTest[
  Lookup[residuals, "exact_witness_count_residual"],
  0,
  TestID -> "02F-CLOSEOUT-EXACT-WITNESS-COUNT"
]

VerificationTest[
  Lookup[residuals, "blocked_promotion_count_residual"],
  0,
  TestID -> "02F-CLOSEOUT-BLOCKED-PROMOTION-COUNT"
]

VerificationTest[
  Lookup[residuals, "stage_dag_acyclic"],
  True,
  TestID -> "02F-CLOSEOUT-STAGE-DAG-ACYCLIC"
]

VerificationTest[
  Lookup[residuals, "upstream_identity_exact"],
  True,
  TestID -> "02F-CLOSEOUT-UPSTREAM-IDENTITY-EXACT"
]

VerificationTest[
  Lookup[residuals, "bounded_claims_exact"],
  True,
  TestID -> "02F-CLOSEOUT-BOUNDED-CLAIMS-EXACT"
]

VerificationTest[
  And[
    Lookup[residuals, "promotion_firewall_exact"],
    Lookup[residuals, "consumer_binding_firewall_intact"]
  ],
  True,
  TestID -> "02F-CLOSEOUT-PROMOTION-AND-BINDING-FIREWALLS"
]
