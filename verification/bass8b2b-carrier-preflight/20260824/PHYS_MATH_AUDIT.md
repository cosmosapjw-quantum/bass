# PHYS-MATH audit — BASS-8B.2B carrier preflight

## Verdict

`PASS_BOUNDED_CARRIER_CHOICE__P0_RATE_DUAL_DEPENDENCY_CORRECTED`

## Load-bearing checks

1. **Sign convention:** metric `(-,+,+,+)` and future-directed Doppler factor
   `D=gamma(1-beta.e)>0` for `|beta|<1`.
2. **Dimensions:** beta, D, q, weights, and normalized P are dimensionless;
   `n_e sigma_T c` is `T^-1`; Q-time rate divides by `H_normal`.
3. **Measure:** paired normal weights satisfy `w_normal/D^2=w_rest` node by
   node.
4. **Physical carrier:** `J=P(e)JP(e)` has four real degrees of freedom; rank-9
   is a redundant ambient embedding, not an unrestricted physical space.
5. **Zero tilt:** rest nodes, weights, equilibrium, and rest spectrum recover.
6. **SO(3):** generic-vector collision and projector covariance survive 30
   random proper rotations to at most `8.89e-15` and `4.00e-15`.
7. **Type-II restriction:** `beta=v2 e2` is a restriction of the generic-vector
   map, never a source for cross-family component transplantation.
8. **Rate/dual theorem:** a direction-dependent diagonal multiplier changes
   the left kernel even when it preserves the right kernel. Exact SymPy
   counterexample passes.
9. **Collision-off:** at zero scalar opacity the full operator is zero and does
   not identify a nontrivial projector.
10. **Scope:** no continuum finite-tilt theorem, near-light-speed theorem,
    generic positivity theorem, or solver claim is made.
