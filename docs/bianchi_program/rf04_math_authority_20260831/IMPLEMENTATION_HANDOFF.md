# Implementation handoff — subordinate to RF04 gates

This handoff is informational only. It does not authorize bypassing R5 intake, LOCAL-01, the preserved-local-evidence gate, or `NO_PASS_RF04`.

After every LOCAL-01 gate passes, LOCAL-02 should consume `FROZEN_OPERATOR_CONTRACT.json` without changing its formula semantics.

## Required bindings

1. Name runtime time and provide `ds/dtau`.
2. Name opacity convention: `kappa_rest` with prefactor `D`, or `kappa_n` with prefactor `q=1-v.e`.
3. Bind node-major rank-nine carrier and exact storage order.
4. Bind screen-map orientation and packed `V` sign.
5. Bind quadrature and boosted weights `w_i/D_i^2`.
6. Type each remap as scalar pullback or conservative density pushforward.
7. Expose raw pre-projection leakage separately from post-projection residual.
8. Implement the Higham `gamma_3` interval with outward rounding.
9. Assemble independent dense `A`, `C`, and `A+C` on one frozen grid.
10. Run the first-order differential before any split trajectory.

Required mutants: added uncompensated `K`; node/rank permutation; omitted `D^-2`; screen orientation mismatch; missing/extra gamma; packed circular sign flip.

A successful LOCAL-02 receipt may claim at most `SCOPED_FROZEN_PHYSICAL_OPERATOR_PROOF`. It must retain `NO_PASS_RF04` until trajectory, convergence, AP/stiff, and all remaining RF04 gates pass.
