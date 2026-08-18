# G-SYMBOLIC-LOWERING-II implementation plan

**Goal:** Lower the validated Type-II symbolic authority and moving-equilibrium
operator programs to generated Rust source and test them against the pinned
offline RustCore.

- [x] TDD generator contract
- [x] Type-II 5-state RHS generation
- [x] Type-II exact state JVP generation
- [x] low-rank scalar projector / dP-dv / Kato action
- [x] matrix-free finite-tilt scalar Thomson generator action
- [x] formula/compiler/Cargo.lock provenance manifest
- [x] pinned Rust 1.94.1 rustfmt canonicalization
- [x] generated-module Rust tests
- [x] full `cargo test --lib --locked --offline`
- [x] Python stacked compiler regression
- [x] atomic Git commit/push and stacked PR

## Scope boundary

This PR does not yet implement the complete Kato-AEM2 exponential/phi-action
time integrator in Rust.  It provides the generated operator kernels that the
next runtime-integration gate consumes.
