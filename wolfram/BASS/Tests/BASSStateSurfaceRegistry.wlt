(* Top-level MUnit tests. The canonical runner preloads the module and injects the registry. *)

registry = If[
  AssociationQ[Global`$BASSStateSurfaceRegistryTestData],
  Global`$BASSStateSurfaceRegistryTestData,
  <||>
];
residuals = BASS`IR`BASSStateSurfaceRegistryExactResiduals[];

VerificationTest[
  BASS`IR`BASSStateSurfaceRegistryQ[registry],
  True,
  TestID -> "SYNC02F-R2-STATE-REGISTRY-VALID"
]

VerificationTest[
  residuals["band_limited_grid_pstf_reconstruction"],
  0,
  TestID -> "SYNC02F-R2-GRID-PSTF-BANDLIMITED-RECONSTRUCTION"
]

VerificationTest[
  residuals["same_integrated_G_state"],
  0,
  TestID -> "SYNC02F-R2-G-SAME-INTEGRATED-STATE"
]

VerificationTest[
  residuals["different_frequency_loss_residual"],
  0,
  TestID -> "SYNC02F-R2-G-SOURCE-CLOSURE-NOGO"
]

VerificationTest[
  residuals["universal_scalar_closure_residuals"],
  {0, 0},
  TestID -> "SYNC02F-R2-UNIVERSAL-SCALAR-CLOSURE-CONDITION"
]

VerificationTest[
  residuals["J_projection_noninvertibility_witness"],
  1,
  TestID -> "SYNC02F-R2-J-PROJECTION-NONINVERTIBLE"
]

VerificationTest[
  residuals["scalar_to_polarized_implicit_promotion_defined"],
  False,
  TestID -> "SYNC02F-R2-NO-IMPLICIT-POLARIZATION-PROMOTION"
]
