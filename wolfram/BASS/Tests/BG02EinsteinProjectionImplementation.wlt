(* Top-level MUnit contract for the future BG-02 production implementation.
   The canonical native runner injects the already loaded registry and exact
   native-audit association. This file performs no path inference. *)

testContext = Global`$BASSBG02EinsteinProjectionTestContext;
registry = Lookup[testContext, "registry", <||>];
audit = Lookup[testContext, "audit", <||>];

VerificationTest[
  TrueQ[
    Lookup[testContext, "package_loaded", False] &&
    Lookup[audit, "xTensor_projection_derivation_verified", False]
  ],
  True,
  TestID -> "BG02-XTENSOR-PROJECTION-DERIVATION"
]

VerificationTest[
  TrueQ[Lookup[testContext, "registry_valid", False]],
  True,
  TestID -> "BG02-REGISTRY-VALID"
]

VerificationTest[
  Lookup[registry, "formula_count", Missing["Absent"]],
  14,
  TestID -> "BG02-FORMULA-COUNT"
]

VerificationTest[
  DuplicateFreeQ[Lookup[Lookup[registry, "formulas", {}], "formula_id", {}]],
  True,
  TestID -> "BG02-FORMULA-IDS-UNIQUE"
]

VerificationTest[
  DeleteDuplicates[Lookup[Lookup[registry, "formulas", {}], "dimension", {}]],
  {"L^-2"},
  TestID -> "BG02-DIMENSIONS"
]

VerificationTest[
  TrueQ[Lookup[audit, "dependency_graph_closed", False]],
  True,
  TestID -> "BG02-DEPENDENCY-CLOSED"
]

VerificationTest[
  TrueQ[Lookup[audit, "single_off_shell_residual_authority", False]],
  True,
  TestID -> "BG02-SINGLE-RESIDUAL"
]

VerificationTest[
  Lookup[audit, "hamiltonian_projection_residual", Missing["Absent"]],
  0,
  TestID -> "BG02-HAMILTONIAN-PROJECTION"
]

VerificationTest[
  Lookup[audit, "momentum_projection_residual", Missing["Absent"]],
  0,
  TestID -> "BG02-MOMENTUM-PROJECTION"
]

VerificationTest[
  Lookup[audit, "spatial_trace_projection_residual", Missing["Absent"]],
  0,
  TestID -> "BG02-SPATIAL-TRACE-PROJECTION"
]

VerificationTest[
  Lookup[audit, "spatial_pstf_projection_residual", Missing["Absent"]],
  0,
  TestID -> "BG02-SPATIAL-PSTF-PROJECTION"
]

VerificationTest[
  Lookup[audit, "adm_minus_trace_plus_half_hres", Missing["Absent"]],
  0,
  TestID -> "BG02-OFF-SHELL-ADM-TRACE"
]

VerificationTest[
  Lookup[audit, "trace_minus_ray_plus_sixth_hres", Missing["Absent"]],
  0,
  TestID -> "BG02-OFF-SHELL-TRACE-RAY"
]

VerificationTest[
  Lookup[audit, "adm_minus_ray_plus_two_thirds_hres", Missing["Absent"]],
  0,
  TestID -> "BG02-OFF-SHELL-ADM-RAY"
]

VerificationTest[
  TrueQ[
    Lookup[audit, "shear_rate_adapter_residual", Missing["Absent"]] === 0 &&
    Lookup[audit, "lie_shear_derivative_kind", ""] ===
      "LIE_DERIVATIVE_PSTF" &&
    Lookup[audit, "projected_shear_derivative_kind", ""] ===
      "PROJECTED_COVARIANT_NORMAL_DERIVATIVE"
  ],
  True,
  TestID -> "BG02-SHEAR-DERIVATIVE-ADAPTER"
]

VerificationTest[
  Lookup[audit, "flat_flrw_hamiltonian_residual", Missing["Absent"]],
  0,
  TestID -> "BG02-FLAT-FLRW-HAMILTONIAN"
]

VerificationTest[
  Lookup[audit, "flat_flrw_rate_residual", Missing["Absent"]],
  0,
  TestID -> "BG02-FLAT-FLRW-RATE"
]

VerificationTest[
  Lookup[audit, "flat_de_sitter_rate_residuals", Missing["Absent"]],
  {0, 0, 0},
  TestID -> "BG02-FLAT-DE-SITTER"
]

VerificationTest[
  Lookup[audit, "kasner_hamiltonian_residual", Missing["Absent"]],
  0,
  TestID -> "BG02-KASNER-HAMILTONIAN"
]

VerificationTest[
  Lookup[audit, "kasner_rate_residuals", Missing["Absent"]],
  {0, 0, 0},
  TestID -> "BG02-KASNER-RATES"
]

VerificationTest[
  Lookup[audit, "bianchi_I_scalar_curvature_residual", Missing["Absent"]],
  0,
  TestID -> "BG02-BIANCHI-I-CURVATURE"
]

VerificationTest[
  Lookup[audit, "bianchi_V_scalar_curvature_residual", Missing["Absent"]],
  0,
  TestID -> "BG02-BIANCHI-V-CURVATURE"
]

VerificationTest[
  Lookup[audit, "bianchi_II_scalar_curvature_residual", Missing["Absent"]],
  0,
  TestID -> "BG02-BIANCHI-II-CURVATURE"
]

VerificationTest[
  Lookup[audit, "bianchi_IX_scalar_curvature_residual", Missing["Absent"]],
  0,
  TestID -> "BG02-BIANCHI-IX-CURVATURE"
]

VerificationTest[
  TrueQ[
    Lookup[audit, "wrong_connection_order_V_detected", False] &&
    Lookup[audit, "wrong_connection_order_II_detected", False] &&
    Lookup[audit, "I_IX_only_witness_set_rejected", False] &&
    Lookup[audit, "second_koszul_implementation_absent", False]
  ],
  True,
  TestID -> "BG02-CONNECTION-ORDER-GUARD"
]

VerificationTest[
  TrueQ[
    Lookup[audit, "exceptional_VI_minus_one_ninth_residual",
      Missing["Absent"]] === 0 &&
    Lookup[audit, "sigma13_deletion_mutant_detected", False] &&
    Lookup[audit, "normal_acceleration_distinct_from_bianchi_a", False] &&
    Lookup[audit, "hamiltonian_surface_projection_absent", False]
  ],
  True,
  TestID -> "BG02-EXCEPTIONAL-VI-AND-CLAIM-GUARD"
]
