# BASS Type-II original production critical path | Source-owned embedded 4D chart and host-interface preflight

## R8 claim admission
**Established from BASS original source:** the Type-II aligned gamma-law five stored state components obey one independent nonzero Codazzi constraint on the positive-energy N1>0 branch. Source WE shear normalization Sigma13(raw)=sqrt(3)*Sigma13. The resulting regular physical state manifold has dimension four at fixed gamma, with Omega and Sigma13 given by the explicit unique-positive-root equations in S0. This is a precise *local Type-II state representation* claim, not a new literature-wide Bianchi classification theorem.

**Derived exact:** the quadratic root solves Omega + beta Omega² = A; Gauss-eliminated Codazzi Jacobian -sqrt(3)*N1*(1+2 beta Omega)<0. Exact SymPy check returned 0; independent Wolfram positive-root identity returned 0. This is the local regular N1>0 chart only; N1=0 Type I boundary not covered.

**Numerically checked:** original-parameter 401-RK4-epoch source-equivalent model (no new Einstein model): Codazzi max 3.3306690738754696e-16; physical chart Sigma13 max gap 2.0816681711721685e-16; Omega max gap 3.3306690738754696e-16; mock host inverse max 1.3877787807814457e-17; 401-patch implicit constraint Jacobian |det| min 1.5420104853760288. Independent saved-data reviewer max physics residual 4.440892098500626e-16. Negative inserted Sigma13 error 0.001 rejected. Original canonical 401-source fixture exact-byte replay only admitted after hosted CI verifies Git blob and computes on original canonical rows. Local output does not establish fixture byte identity.

**Implementation boundary:** Pure Rust `typeii_state_contract.rs` is a compile-only mock with no direct actual `_rustcore` state API wired. No local rustc/cargo installed; hosted Rust compilation must be separately verified. TypeIIState5 mapping is source-compatible with BASS `_rustcore` generic `BianchiGroup.n6` and `tracefree_from_5.shear5` layouts. Actual production host remains candidate only: `_rustcore` crate at fixed BASS main. Existing `_rustcore/src/runtime/plan.rs` is RF-01 fixture engine, *not* an approved Type-II production interface.

**Physical SI clock:** d tau=H dt; original collision scaled by nu_tau=n_e sigma_T c/H. The original Type-II generator already contains direction-dependent q_alpha=1-v2 n_y. Only one q_alpha admitted. The gamma-law tilted fluid and photon opacity/electron-bath model are separate sources. No native Saha/HyRec equivalent assertion.

## R9 executable scientific calculation contract
Selected source: BASS original 9 Git blobs in `SOURCE_LOCK.json`, including original TypeII generated Rust RHS, class A tilt, current RustCore geometry and `typeii_fixture_canonical.json`. Clean checkout workflow `.github/workflows/typeii-host-preflight.yml` verifies exact original Git SHA1 blobs before any Rust or Python test. Then (1) compile `rustc --edition=2021 --test` isolated mock source including original generated RHS/JVP, (2) read and check *401 exact original source fixture samples* from original Git blob, (3) run independent source-equivalent Python tests, (4) run explicit-error referee under normal and `-O`, (5) upload numerical CSV and result JSON. Keep generated output numerical identity distinct from original source byte identity.

Proposed next migration commands *only for actually provisioned and authorized crate vendor host*:

    cd _rustcore
    cargo metadata --locked --offline --format-version 1
    cargo test --locked --offline

These commands have **NOT** been executed here; `_rustcore` depends on pinned remote rec/rei git revisions and this model container does not have the owner-provisioned vendor/cache. Do not silently replace `cargo --offline` with online dependency downloads. Do not import mock into production or modify crate lockfiles in this PR.

Production architecture: BASS original full-dimensional Arnoldi/Pade13 reference backend, with `phi1` via augmented exponential and Kato-AEM2 from original PR #6. Adaptive Krylov optional, no silently promoted defaults. Original scalar frozen uniformization PR #316 and direct old-AEM2/Kato comparison PR #318 already source-scoped CI verified, not replaced or re-run. No new quantum tensor/P8 production or CMB claims.

## R6 same-author hostile check (final pass, nonrecursive)
Actually tested source-physical negative cases: wrong Sigma13 sign, missing sqrt3, nonzero forbidden n22/v1, incorrect normalization/frame/clock, wrong Omega, v2=1, gamma=2, N1=0, negative source budget, tampered stored data, external double-Doppler callback excluded. The latter was removed from contract API after review. Independent original-generated Rust RHS/JVP physical test planned at GH CI, not confused with local no-rustc state. Distinct author audit and native subagents NOT_RUN.

## R10 stage preservation and status
R1–R4 S0 published on isolated research branch commit `7b904935aa40b039ab810b723126d5f87540761d`; S0 ZIP SHA256 `b49134b4aa9181f5e7962853a82acc52789aba4f48645a65b3ec145baa48663f`.
R5–R7 S1 published on same branch commit `c17597d5de1624755f8dd1feaa505e1ed6b126d1`; S1 ZIP SHA256 `ab50abc22756b0c9dee193bbe18fd3c6141eebce6f29e4635fe8ca6d674720f1`.
R8–R10 S2 commits claim-scoped report, actual workflow, source lock, acceptance matrix and handoff, with final HEAD/CI to be recorded as a separate proof comment after GitHub run. This document deliberately does not preclaim success. Library and Google Drive backup are separately checked for provider upload ACK versus raw restored exact SHA and inner CRC.

`BASS upper=9/15 scoped/source-mapped (unchanged)`, historical Stage II `11/11` without current EvidenceBundle, `G-DYN-MANIFOLD-VI0=PARTIAL`, `P-MIG-II-PREFLIGHT=PARTIAL`, Join J1=`0/2 full PASS HOLD`, production_ready=false, merge_ready=false, auto_next=false, new completed production/upper nodes=0.

Next real critical-path blocker is actual RustCore crate-root locked/offline build and minimal adapter to a *real* source-owned host state/runtime call on an isolated branch, plus B1 convention reconciliation and VI0 classification; Stage II source-bound gate bundles are separate. Do not use an isolated mock to claim either production acceptance or Stage II recovery.