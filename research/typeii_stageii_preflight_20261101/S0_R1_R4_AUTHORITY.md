# Type-II / Stage II authority recovery | R1–R4 (2026-11-01)
Original main `9c6506e4e2087129a8b674ff10438e5db1a55c9d`; reference PR #5–#7 and original realignment PR #15 protected, no runtime mutation. BASS upper physics `9/15` scoped/source-mapped (not production full pass); historical Stage II `11/11` is not canonical source admission; Join J1 `0/2` FULL PASS; VI0 PARTIAL; P-MIG-II-PREFLIGHT OPEN.

## Actual connected-original recovery
The recovered Dropbox `/bianchi_phase_r_bootstrap_v1.2/bianchi_phase_r/ssot/contracts/GATE_BUNDLE_RECORD_SCHEMA.yaml` (PATCH34) **declares schema_only_non_evidence** and `gate_bundle_record_constructed=0`, `validation_gate_pass_claims_authorized=0`, `evidence_bundle_constructed=0`, `evidence_token_mint_allowed=false`. Its **12** gate IDs are a different node set from Stage II's historical **11** components. The connected Python `.../ssot/python/lowell_bianchi_solver/validation/gate_bundle.py` expressly raises `GateBundleLockedError` on actual construction. The Rust `ssot/crates/lbs-core/src/validation/gate_bundle.rs` is a draft/fail-closed executor with no evidence-token authority. Reading extracted text is not a Dropbox raw SHA256 readback and is **not** fresh Rust compilation.

The BASS main source `provenance/formula_core/registries/BRANCH_REGISTRY_PHYSICAL.json` carries 11 physical Bianchi branch labels and historical Stage7 SHA256 refs, but no current Stage II `source→GateBundleRecord→EvidenceBundle→validator` chain was recovered in this bounded search. `S_current∧G_current∧E_current∧V_current∧P_harmonic∧P_physics∧P_tier` remains NOT_ESTABLISHED. This is a claim admission bound, not a mathematical no-go.

## Source-owned useful original physics
The original `generated/rust/typeii/typeii_collision.rs` and `compiler/validation/typeii_conservation_quad.py` define a **scalar** finite-tilt Thomson matrix
[
C={\rm diag}(q){\rm diag}(D^{-4})(K_{rest}-I){\rm diag}(D^4),
\quad D_i=\Gamma(1-vn_{i2}),\quad q_i=1-vn_{i2}.
]
For a *paired rest→normal positive quadrature* with `Cr=0,aᵀC=0,r>0,a>0,Cij≥0 (i≠j)`, scalar Poisson uniformization is admissible: `B=I+C/λ≥0`, `M=diag(r)^-1 B diag(r)` row-stochastic and `π∝ar` stationary. Wrong finite-boost fixed-normal grids must not be promoted to an exact-invariant reference. Numerical source-matched computation is R5–R7.

## Host choice still conditional
Candidate: BASS main `_rustcore`, Cargo crate `bianchi_rustcore` at main. Actual `_rustcore/src/runtime/mod.rs` says production kernel migration begins at RF-02; `RuntimePlanCore::run_fixture` is not a Type-II production dispatch. No canonical production owner claim, Cargo.lock/offline vendor verification, real host state roundtrip, old AEM2 vs Kato AEM2 parity, or rollback receipt yet. The full `P-MIG-II-PREFLIGHT` is **PARTIAL** at most.

**R1–R4 published scientific/evidence scope only. No fake full gate PASS; native subagent NOT_RUN per user instruction.**
