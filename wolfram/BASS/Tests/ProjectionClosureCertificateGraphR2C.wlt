(* Top-level MUnit tests. The runner injects the graph; this file performs no path inference. *)

graph = Global`$BASSProjectionClosureCertificateGraphR2CTestData;
residuals =
  BASS`IR`ProjectionClosureCertificateGraphR2C`BASSProjectionClosureCertificateR2CResiduals[];

VerificationTest[
  AssociationQ[graph],
  True,
  TestID -> "02F-R2C-INJECTED-GRAPH-ASSOCIATION"
]

VerificationTest[
  BASS`IR`ProjectionClosureCertificateGraphR2C`BASSProjectionClosureCertificateGraphR2CQ[graph],
  True,
  TestID -> "02F-R2C-GRAPH-VALIDATOR"
]

VerificationTest[
  Lookup[residuals, "legendre_analysis_residuals"],
  {0, 0, 0},
  TestID -> "02F-R2C-LEGENDRE-ANALYSIS"
]

VerificationTest[
  Lookup[residuals, "legendre_grid_roundtrip_residuals"],
  {0, 0, 0},
  TestID -> "02F-R2C-LEGENDRE-GRID-ROUNDTRIP"
]

VerificationTest[
  Lookup[residuals, "radial_product_degree_residual"],
  0,
  TestID -> "02F-R2C-RADIAL-PRODUCT-DEGREE"
]

VerificationTest[
  Lookup[residuals, "radial_dropped_coefficient_residual"],
  0,
  TestID -> "02F-R2C-RADIAL-DROPPED-COEFFICIENT-RESIDUAL"
]

VerificationTest[
  Lookup[residuals, "radial_alias_witness_coefficient"],
  8,
  TestID -> "02F-R2C-RADIAL-ALIAS-WITNESS"
]

VerificationTest[
  Lookup[residuals, "g_integrated_state_residual"],
  0,
  TestID -> "02F-R2C-G-SAME-INTEGRATED-STATE"
]

VerificationTest[
  Lookup[residuals, "g_frequency_loss_difference"],
  -3,
  TestID -> "02F-R2C-G-DIFFERENT-FREQUENCY-LOSS"
]

VerificationTest[
  Lookup[residuals, "four_force_total_residual"],
  {0, 0, 0, 0},
  TestID -> "02F-R2C-FOUR-FORCE-CANCELLATION"
]

VerificationTest[
  Lookup[residuals, "screen_idempotence_residual"],
  ConstantArray[0, {3, 3}],
  TestID -> "02F-R2C-SCREEN-IDEMPOTENCE"
]

VerificationTest[
  Lookup[residuals, "screen_direction_residual"],
  {0, 0, 0},
  TestID -> "02F-R2C-SCREEN-DIRECTION-ORTHOGONALITY"
]

VerificationTest[
  Lookup[residuals, "screen_trace_residual"],
  0,
  TestID -> "02F-R2C-SCREEN-TRACE"
]

VerificationTest[
  Lookup[residuals, "scalar_intensity_trace_residual"],
  0,
  TestID -> "02F-R2C-SAME-SCALAR-INTENSITY"
]

VerificationTest[
  Lookup[residuals, "polarization_state_frobenius_difference_squared"],
  0,
  TestID -> "02F-R2C-POLARIZATION-NONUNIQUENESS-RESIDUAL"
]

VerificationTest[
  Lookup[residuals, "radial_work_order_residual"],
  0,
  TestID -> "02F-R2C-RADIAL-WORK-ORDER"
]

VerificationTest[
  Lookup[residuals, "angular_work_rank_residual"],
  0,
  TestID -> "02F-R2C-ANGULAR-WORK-RANK"
]
