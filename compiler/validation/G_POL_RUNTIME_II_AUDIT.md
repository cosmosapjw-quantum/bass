# G-POL-RUNTIME-II audit

## Scope and claim boundary

This checkpoint extends the accepted scalar Type-II reference architecture to a polarized finite-electron-tilt collision/Kato lane. The strongest supported claim remains narrow: a basis-free rank-9 coherency-tensor Thomson generator and moving-equilibrium Kato connection are lowered to Rust and exercised through the exact PR #6 full-dimensional Arnoldi/Pade13 exponential-action source. This is **not** a complete polarized Einstein-Boltzmann time-stepper, production migration, cross-family runtime, or statistics-ready layer.

Polarization authority SHA-256: `b4becce7e7162991c63b7f065d56c6a29c4123b9b9030eb8eba1b30eee3a3a6b`.

## Physics and numerical gates

The implemented finite-tilt collision lane uses `D=gamma(1-v e_axis)` and `q=1-v e_axis`, with the canonical rest-frame screen transform, `D^4` radiation-amplitude transform, `D^-2` solid-angle weight transform, and the inherited normal-time relative-flux factor `q`. The boosted unpolarized equilibrium is `r_i=D_i^-4 Pi_i/2`; the moving rank-one equilibrium projector is differentiated explicitly and its Kato connection is evaluated matrix-free as `K=vdot[P_,v,P]`.

Previously closed targeted gates remain:

- paired-grid right-null max `3.731582943878999e-16`;
- paired-grid left-invariant max `1.115402857041025e-16`;
- `P^2-P = 0`;
- `[K,P]-Pdot = 2.6020852139652106e-18`;
- symmetric polarized input produces no tested `V` leakage;
- polarized intensity generator reduces to the scalar authority to `1.249000902703301e-16`;
- rest physical-Stokes dimension 104 with spectrum multiplicities `0:1`, `-0.3:5`, `-0.5:3`, `-1:95` and max cluster defect `1.9984e-15`;
- explicit intensity quadrupole sources linear polarization;
- Rust deep collision exponential at depth 20 preserves the tested coherency cone with margin `0.7459613827690769` and screen leakage `1.6715954190263236e-16`;
- actual Type-II moving-projector Kato endpoint defects are `(8.858e-8,2.214e-8,5.534e-9,1.383e-9,3.459e-10)`, fitted order `2.0000505423`.

Low-order fixed-normal quadrature remains a negative-control lane and is not silently tuned away.

## Full RustCore locked/offline replay — CLOSED

The previously open environment gate is now closed using the supplied archive `BASS_RUSTCORE_OFFLINE_LOCKED_20260818-105221.zip`.

Provenance:

- outer archive SHA-256: `f30a4da90c68819d16df44632da91fa76e443df3b8dcf1d55c843bede1e1fb29`;
- exact `Cargo.lock` SHA-256: `d500208e9353ade1cb74693918598846628219e6e7bd2e2bce9ec85e29eb6310`;
- vendor directories: 176;
- Rust: `rustc 1.94.1 (e408947bf 2026-03-25)`;
- Cargo: `cargo 1.94.1 (29ea6fb6a 2026-03-24)`;
- exact PR #6 runtime source SHA-256: `78dc3dc28cfade9ea0066b2033c16b28faf570d591b806590da54138b6b2eb0d`.

Replay sequence from the crate root:

1. untouched supplied RustCore: `cargo test --lib --locked --offline` -> **122 passed, 0 failed**;
2. integrate the PR #5 generated Type-II scalar modules -> **128 passed, 0 failed**;
3. integrate exact PR #6 runtime plus PR #8 polarized generated/runtime modules and the polarized integration target;
4. fresh `cargo test --locked --offline --quiet` -> **128 library + 12 polarized integration tests passed, 0 failed**;
5. `rustfmt --check` on the integrated generated/runtime/test source -> **PASS**.

The supplied `.cargo/config.toml` routes crates.io to the bundled directory source, so the successful replay does not depend on network dependency resolution.

## Remote-test defect found during replay

The exact PR #8 test support blob contained a code-only typo:

`type TMaT = [[f64;3];3];`

while subsequent helpers referenced `TMat`. A minimal unchanged reproduction fails with Rust `E0425` (`cannot find type TMat`). The root cause is the split-file upload spelling mismatch, not the polarized physics/runtime code. The minimal repair is `TMaT -> TMat`; after that repair the full 12-test polarized integration target passes in the exact locked/offline RustCore environment.

This finding also explains why an isolated pre-push 12/12 result could coexist with a non-compiling remote support blob: the tested local support file and the uploaded split blob were not byte-identical at that alias line. The remote branch must carry the corrected alias before the merge gate is considered closed.

## Failure ledger after replay

- **P0:** none in the tested Type-II aligned polarized collision/Kato reference lane.
- **P1:** full polarized Liouville/free-streaming/geometric polarization-basis transport remains unimplemented here.
- **P1:** arbitrary external screen-basis/Wigner-phase transport remains outside this canonical basis-free lane.
- **P2:** fixed-normal low-order finite-boost quadrature requires explicit refinement/Gram/null gates.
- **P2:** adaptive/restarted `m<n` Krylov remains open; full-dimensional Arnoldi is still a reference backend rather than scalable production machinery.
- **Closed:** exact RustCore locked/offline vendor replay.
- **Closed:** remote test-support alias typo after the one-token repair.

## Verdict and next

**PASS as a Type-II aligned-tilt polarized collision/Kato reference runtime, with the exact RustCore locked/offline integration gate now reproduced and closed.**

The numerical-performance DAG may proceed to `G-KRYLOV-ADAPT`. A separate physics gate is still required before calling this a full polarized Type-II Boltzmann runtime: geometric/free-streaming polarization transport and basis-rotation/Wigner handling must be connected and validated. Cross-family generalization remains separate.
