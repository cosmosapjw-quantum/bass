(* Top-level MUnit tests. The runner injects the contract; this file performs no path inference. *)

contract = Global`$BASSConsumerBindingContractsR3TestData;
residuals = BASS`IR`ConsumerBindingContractsR3`BASSConsumerBindingContractsR3Residuals[contract];

VerificationTest[
  AssociationQ[contract],
  True,
  TestID -> "02F-R3-INJECTED-CONTRACT-ASSOCIATION"
]

VerificationTest[
  BASS`IR`ConsumerBindingContractsR3`BASSConsumerBindingContractsR3Q[contract],
  True,
  TestID -> "02F-R3-CONTRACT-VALIDATOR"
]

VerificationTest[
  Lookup[residuals, "consumer_count_residual"],
  0,
  TestID -> "02F-R3-CONSUMER-COUNT"
]

VerificationTest[
  Lookup[residuals, "binding_request_count_residual"],
  0,
  TestID -> "02F-R3-BINDING-REQUEST-COUNT"
]

VerificationTest[
  Lookup[residuals, "source_role_pin_count_residual"],
  0,
  TestID -> "02F-R3-SOURCE-ROLE-PIN-COUNT"
]

VerificationTest[
  Lookup[residuals, "named_source_symbol_count_residual"],
  0,
  TestID -> "02F-R3-NAMED-SOURCE-SYMBOL-COUNT"
]

VerificationTest[
  Lookup[residuals, "absent_slot_count_residual"],
  0,
  TestID -> "02F-R3-ABSENT-SLOT-COUNT"
]

VerificationTest[
  Lookup[residuals, "formula_count_residual"],
  0,
  TestID -> "02F-R3-FORMULA-COUNT"
]

VerificationTest[
  Lookup[residuals, "state_surface_count_residual"],
  0,
  TestID -> "02F-R3-STATE-SURFACE-COUNT"
]

VerificationTest[
  Lookup[residuals, "certificate_family_count_residual"],
  0,
  TestID -> "02F-R3-CERTIFICATE-FAMILY-COUNT"
]

VerificationTest[
  Lookup[residuals, "blocked_promotion_count_residual"],
  0,
  TestID -> "02F-R3-BLOCKED-PROMOTION-COUNT"
]

VerificationTest[
  Lookup[residuals, "pair_coverage_exact"],
  True,
  TestID -> "02F-R3-PAIR-COVERAGE-EXACT"
]

VerificationTest[
  Lookup[residuals, "formula_authority_exact"],
  True,
  TestID -> "02F-R3-FORMULA-AUTHORITY-EXACT"
]

VerificationTest[
  Lookup[residuals, "source_role_pins_exact"],
  True,
  TestID -> "02F-R3-SOURCE-ROLE-PINS-EXACT"
]

VerificationTest[
  Lookup[residuals, "rei_absent_slot_intact"],
  True,
  TestID -> "02F-R3-REI-ABSENT-SLOT-INTACT"
]

VerificationTest[
  Lookup[residuals, "htt_blackbody_roles_distinct"],
  True,
  TestID -> "02F-R3-HTT-BLACKBODY-ROLES-DISTINCT"
]

VerificationTest[
  And[
    Lookup[residuals, "state_surface_firewall_intact"],
    Lookup[residuals, "authorization_firewall_intact"]
  ],
  True,
  TestID -> "02F-R3-STATE-AND-AUTHORIZATION-FIREWALLS"
]

VerificationTest[
  And[
    Lookup[residuals, "stage_dag_acyclic"],
    Lookup[residuals, "literature_authority_none"],
    Lookup[residuals, "parallel_r6c_nonpromotional"]
  ],
  True,
  TestID -> "02F-R3-DAG-LITERATURE-AND-R6C-FIREWALLS"
]
