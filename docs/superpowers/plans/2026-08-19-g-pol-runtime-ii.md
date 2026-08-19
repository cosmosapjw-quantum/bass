# G-POL-RUNTIME-II implementation plan

## Goal

Extend the accepted Type-II scalar reference runtime with a bounded polarized reference lane without migrating production code. The load-bearing path is

`rank-9 coherency authority -> deterministic Rust lowering -> finite-v collision/Kato actions -> exact PR #6 full-Arnoldi expm_action -> independent Python dense oracle`.

The aligned Type-II electron tilt is the existing `v2` lane. This PR does not generalize the moving manifold to other Bianchi families.

## TDD sequence

1. RED: require a generated polarized Rust module before implementation exists.
2. Lower the basis-free rank-9 coherency carrier (symmetric 6 + antisymmetric/V 3).
3. Add finite-v Thomson action with canonical screen boost, `D^4` amplitude, `dOmega/D^2` rest weights and the inherited normal-time relative-flux factor `q=1-v.e`.
4. Add boosted equilibrium, left functional, rank-one projector, `P_,v`, and `K=vdot[P_,v,P]` actions.
5. Bind collision and Kato actions to the exact PR #6 `expm_action` reference backend.
6. Validate against independent Python dense construction and rest-frame spectral modes.
7. Enforce V=0, screen constraint, coherency cone, intensity reduction and intensity-quadrupole polarization gates.
8. Repeat paired-rest-normal versus fixed-normal finite-tilt quadrature checks.
9. Replay midpoint Kato transport on the source-derived PR #7 Type-II `v2(t),v2dot(t)` schedule in both Python and Rust.
10. Record provenance and fail closed on exact full-RustCore replay if the pinned offline vendor is unavailable.

## Adversarial failures retained as evidence

- A fixed six-ray normal-frame grid gave a finite-v equilibrium-null defect `9.605220075e-3`. This was not tuned away; it is a negative control. The paired rest->normal grid is the structure-preserving reference lane and fixed-normal grids require refinement gates.
- A synthetic endpoint schedule with an inconsistent `v2dot` destroyed Kato order. It was rejected; the test now consumes the exact source-derived PR #7 schedule.
- An API-compatible local exponential shim was initially used for fast TDD. Closeout replaced it with the exact PR #6 runtime source, SHA-256 `78dc3dc28cfade9ea0066b2033c16b28faf570d591b806590da54138b6b2eb0d`, before accepting Rust runtime evidence.

## Hard claim boundary

Allowed after this gate: **Type-II aligned-tilt polarized collision/Kato reference runtime lane**.

Not allowed: full polarized Liouville/free-streaming transport, arbitrary external screen-basis Wigner phase, cross-family polarized runtime, adaptive/restarted `m<n` Krylov, production migration, or data/statistics readiness.
