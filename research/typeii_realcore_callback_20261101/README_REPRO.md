# BASS original Type-II: real RustCore callback bridge and original 401-fixture proof

## Authority and scope
Original main `9c6506e4e2087129a8b674ff10438e5db1a55c9d`; immutable stacked PR #320 HEAD `bd7938b55fde2095504bac2eed4083f51a15097b`; immutable parent PR #318 `52e77e59e0d37b75b892efa38d05784ddb731757`. Use `research/typeii_host_preflight_20261101/SOURCE_LOCK.json` for the nine original Git blobs. Original generated Type-II source, `_rustcore/Cargo.lock`, `runtime/plan.rs` and main remain unchanged.

**New actual RustCore module:** `_rustcore/src/runtime/typeii_host.rs` is exported as `runtime::typeii_host` with an opt-in, source-owned `OriginalTypeIIBackground::{rhs,jvp,physical_rhs_four}` callback. It directly invokes the immutable original `generated/rust/typeii/typeii_background.rs`, imports actual `BianchiGroup` and `tracefree_from_5`, maps the constrained WE 5-state to the real generic BASS RustCore geometry, checks Gauss/Codazzi and physical slice, and uses an exact 4D tangent lift. The source RHS is checked tangent to the 4D Codazzi slice at all 401 canonical states. Frame is normal, normalization Hubble WE, prime is d/dtau with d tau=H dt; no implicit SI opacity or second q_alpha. The N1=0 Type I boundary is excluded.

**Not installed:** No RF-01 `RuntimePlanCore::run_fixture` substitution, production dispatcher change, radiative transport consumer, polarized P8 admission, SahaHistory physical ownership, or large-scale simulation. This is an actual crate-compiled source callback *interface*, not an active production runtime engine.

## Reproduction on a provisioned Rust host

```bash
# Run from repo root, with the original Cargo.lock and source files retained.
(cd _rustcore && CARGO_BUILD_JOBS=4 cargo test --locked --offline)
(cd research/typeii_realcore_callback_20261101 && CARGO_TARGET_DIR=/tmp/bass-typeii-minihost-target cargo test --locked --offline --lib)
(cd research/typeii_realcore_callback_20261101 && python3 fixture_stream.py | CARGO_TARGET_DIR=/tmp/bass-typeii-minihost-target cargo run --locked --offline --quiet --bin source_fixture_401)
```

`fixture_stream.py` verifies immutable Git object hashes of the original Type-II source, 401-row fixture, original real group and conventions, before reading the exact fixture and streaming decimal64 states/RHS. The reproducibility crate compiles the original owner source by `#[path]`, not a rewritten stand-in. The native `_rustcore` crate test was also run; passing the narrow crate alone does not certify the full owner.

## Actually observed (cosmosapjw host, 2026-11-01)

- `rustc --edition=2021 --test research/typeii_host_preflight_20261101/source/typeii_state_contract.rs` followed by tests: **9/9 PASS** (immutable parent contract).
- `cargo test --locked --offline` from `_rustcore`: **exit 0, 141 passed, 0 failed**. This includes newly installed module tests; Rust toolchain cargo 1.99.0.
- Standalone source-bound narrow crate `cargo test --locked --offline --lib`: **13/13 PASS**.
- Original full 401-row fixture through compiled bridge: **PASS**, `max_source_rhs=4.44089e-16`, `max_codazzi=3.33067e-16`, `max_roundtrip=2.08167e-16`, `max_rhs_tangency=1.80411e-16`.
- Negative control: changing the initial stored Sigma13 sign is rejected as `CodazziViolation`, expected nonzero exit. Wrong normalization/frame/clock, off-slice geometry, wrong Gauss and Type I boundary also rejected by Rust tests.
- `rustfmt --check`, `python3 -m py_compile`, `git diff --check`: PASS after formatting.
- `cargo metadata --locked --offline --format-version 1 --no-deps`: exit 0. Full metadata resolution: **exit 101 (aho-corasick v1.1.4 not locally cached)**. This is a separate cache/environment limitation and does not negate observed `cargo test --locked --offline` PASS. No lockfile change and no online fetch was performed.

## Stage II independent recovery check
Existing `research/typeii_stageii_preflight_20261101` documents already classified historical Stage II 11/11 as *historical-only*, with current `GateBundleRecord -> EvidenceBundle -> source validator` **NOT_RECOVERED**. Direct 2026-11-01 Dropbox source read of historical PATCH34 closeout confirms `GATE_BUNDLE_RECORD_SCHEMA_PRESENT_TRUE` but `GATEBUNDLERECORD_CONSTRUCTED_0`, `EVIDENCEBUNDLE_CONSTRUCTED_0`, `VALIDATION_GATE_PASS_CLAIMS_AUTHORIZED_0`. This is an unrelated 12-row schema and cannot certify BASS historical 11/11. Drive `STAGEII_TYPEII_PREFLIGHT_20261101` contains S0/S1/S2 backup ZIPs for the scoped preflight, not new canonical Stage II records. Scoped search is not global absence proof.

## Decision
- **Actual offline RustCore build and opt-in callback module: IMPLEMENTATION_VERIFIED, source-scoped**.
- **Active production callback dispatch: NOT_RUN; production_ready=false, merge_ready=false, auto_next=false.**
- **BASS upper DAG: 9/15 scoped/source-mapped unchanged; new upper completed 0**.
- **Stage II: 11/11 historical only; current canonical evidence NOT_RECOVERED**.
- **P-MIG-II-PREFLIGHT: PARTIAL until dispatch and migration backend parity**.
- **Join J1: 0/2 full-pass HOLD**. `G_DYN_MANIFOLD_VI0=PARTIAL`.
- **Native subagents and distinct-author review: NOT_RUN**; self-hostile engineering checks performed. This new draft branch is not a merge approval.
