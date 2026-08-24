# Plot-driven CRAG audit

## Finite-difference convergence

`figures/rate_dual_fd_convergence.png` shows the expected truncation-to-roundoff
U-shaped convergence for `e_dot`, `D_dot`, and `nu_dot`.  Minimum relative
errors are approximately `3.1e-13`, `6.2e-13`, and `9.3e-14`, respectively.
The claim surviving this plot is limited to binary64 consistency of the
analytic jet on a smooth interior segment.

## Hostile mutations

`figures/rate_dual_mutation_defects.png` separates the correct paired dual
(roundoff, at most `1.1e-17` in this sweep) from unchanged-left, omitted-q, and
double-D mutations (minimum median defect `1.75e-4`).  This rejects the claim
that the direction-dependent factor can be treated as a harmless global
normalization.

## Global scalar cancellation

`figures/global_scalar_projector_cancellation.png` varies the scalar opacity by
16 orders of magnitude.  The generator norm follows the multiplier to relative
error `5.6e-16`, while the normalized projector is byte-identical in the tested
path.  The surviving claim is global-scalar cancellation from `P`, not removal
of the direction-dependent factor.

## SO(3) covariance

`figures/rate_dual_so3_covariance.png` keeps rate, rate jet, generator, and dual
residuals at roundoff over the tested speed range.  This supports the generic
three-vector restriction and rejects axis-only transplantation as an adequate
interpretation.

## CRAG classification

- Correctness: survives the exact and numerical residual checks.
- Retrieval: agrees with the frozen E2 rate convention and covariant
  electron-rest-frame transport literature.
- Augmented: survives random velocities, rotations, scalar-opacity sweeps, and
  hostile mutations.
- Generation: predicts that 2B.2 must differentiate moving nodes, weights,
  screen maps, and the rate-transformed left dual together.

Final claim class:

```text
SURVIVING_BOUNDED_DISCRETE_CANDIDATE
NOT_CONTINUUM_THEOREM
NOT_AUTHORITY_ROW_PROMOTION
```
