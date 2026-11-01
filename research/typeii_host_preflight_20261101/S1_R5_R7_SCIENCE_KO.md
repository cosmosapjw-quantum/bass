# R5–R7 Type-II exact physical chart, real source-conditioned data and hostile tests

## Newly constructed science, not governance inflation

The exact Type-II aligned gamma-law 5-state invariant slice uses one nontrivial Codazzi condition. The physically regular locus has four independent coordinates `(SigmaPlus,SigmaMinus,N1,v2)` at fixed gamma, with the Sigma13 and Omega positive-root formulas in S0. The full constrained Jacobian minor in the original s13 variable equals `-sqrt(3)*N1*(1+2*beta*Omega)`, with N1>0 and Omega>0; it cannot vanish on this branch. SymPy verified the general expression as exact zero residual. Wolfram independently simplified the quadratic positive-density relation to exactly zero.

New calculation of the 401 preserved Type-II time samples from the independent source-equivalent RK4 model (gamma=1.3, dt=0.0005, tau=[0,.2], no new gravitational physics assumption):
- max abs original Codazzi = 3.3306690738754696e-16
- max Sigma13 reconstruction difference = 2.0816681711721685e-16
- max Omega reconstruction difference = 3.3306690738754696e-16
- max mock host state roundtrip = 1.3877787807814457e-17
- smallest abs Type-II constraint Jacobian = 1.5420104853760288 > 0
- original source initial RHS comparator point matched to within 3e-14; known endpoint state retained.

These are **local rederivation, not byte-exact recovery of the canonical 401-state fixture**. Hosted clean checkout must read original `compiler/validation/typeii_fixture_canonical.json` Git blob `dea22f0fce116b61314b13cea7d0bdd38efe48bc`, verify all nine frozen original blobs, replay 401 rows, and test generated Rust `rhs/jvp`. Separate scoped results from original source identity.

## Compile-only Rust host mock

New contract `source/typeii_state_contract.rs` has TypeII5, MockHostState layout matching existing generic `_rustcore` `BianchiGroup.n6` and `tracefree_from_5.shear5`. It is deliberately **not an installed production adapter** and not imported by `_rustcore/src/lib.rs`, `_rustcore/src/runtime/mod.rs`, or any dispatch. It can be compiled in isolation using `rustc --edition 2021 --test`. The original generated Type-II Rust background is imported into the unit test via a relative `#[path]` without editing original code.

Physically explicit SI clock is separate from the Hubble-normalized Type-II phase-space state: `d tau=H dt`, `nu_tau = n_e sigma_T c/H`, with source collision `q_alpha=1-v2 n_y` included **once in the original generator**. Host contract intentionally has **no public angular-rate callback**, after hostile audit found that this would invite q_alpha double-counting. No hidden H=H_LCDM, c=1 SI, or reconstructed SahaHistory.

## Actual tests and adversarial negatives

Local `python -m unittest` 10/10 PASS and `python -O -m unittest` 10/10 PASS. Separate source-RHS-free data reviewer under ordinary and optimized Python: 401/401 rows, max physics independent residual 4.440892098500626e-16, positive Jacobian margin 1.542..., plus tampered Sigma13 input rejected at 1.498e-3 defect. Source initial RHS and 401 rederived positions checked.

Rust source **has not been compiled locally** because this task container has no `rustc` or `cargo`; seven Rust tests only become `IMPLEMENTATION_VERIFIED` once clean hosted CI actually compiles and runs them. Rust source syntax and source-path are subject to this real test, not hypothetical PASS. Host crate root `_rustcore/Cargo.toml` includes remote `rec_microphysics`/`rei_microphysics` dependencies; actual `cargo test --locked --offline` with available vendor bundle remains a separate unperformed production-host gate.

Hostile counterexamples in Python and Rust include wrong sqrt(3) scaling, reversing Sigma13, nonzero shear or curvature outside Type-II aligned slice, invalid N1=0 boundary, v2 at light speed, nonpositive energy, wrong gamma, wrong host clock, Ringstrom-vs-WE normalization, electron-rest vs normal frame, unauthorized double relative-flux factor, source fixture mutation and false production-ready. Codazzi/Gauss thresholds are 1e-12; actual science residuals ~1e-16, not a loosened tolerance to fix observed failure.

## Actual DAG admission

This closes only a **scoped mathematical sub-obligation** of `P-MIG-II-PREFLIGHT`; full preflight remains PARTIAL until real host compiled/imported state+callbacks and crate-root locked/offline return. `G-DYN-MANIFOLD-VI0=PARTIAL`; Join J1 0/2 FULL PASS; BASS upper 9/15 scoped-source-mapped; Stage II current source evidence and validator NOT_RECOVERED (historical 11/11 not admitted), no new fully complete upper or production node. No source owner mutation, no forced GH ref update, no production ready.