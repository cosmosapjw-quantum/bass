# WSC-4 Jacobian / Sparsity / JVP Implementation Plan

**Goal:** Generate exact residual Jacobians, distinct structural/exact/numerical
sparsity metadata, and matrix-free JVP programs suitable for Rust lowering.

- [x] `J_x` and `J_dx`
- [x] symbolic exact sparsity
- [x] structural incidence sparsity
- [x] pointwise numerical sparsity diagnostic
- [x] exact symbolic JVP
- [x] hostile finite-difference JVP oracle
- [x] Type-II 5-state Jacobian/JVP example
- [x] low-rank moving-projector/Kato JVP
- [x] Wolfram exact Jacobian oracle receipt
- [x] stacked regression
- [x] atomic commit/push and stacked PR
