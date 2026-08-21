# P-MIG-II-PREFLIGHT Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Select and contract the canonical Type-II production landing zone without mutating production execution.

**Architecture:** A repository/crate inventory classifies candidate hosts, then a compile-only Rust contract and mock roundtrip adapter freeze state, units, callbacks and errors. A machine-readable acceptance matrix defines the later isolated migration tests.

**Tech Stack:** Git, Rust 1.94.1, Cargo locked/offline vendor, JSON, pytest/cargo test.

**Spec:** `docs/superpowers/specs/2026-08-21-p-mig-ii-preflight-design.md`

## Global Constraints

- No production runtime file or dispatch mutation.
- Run Cargo from the selected crate root with the pinned lockfile and vendor configuration.
- Full-dimensional Arnoldi/Pade13 is the initial reference backend.
- Adaptive Krylov is optional until real-hierarchy parity and benchmark gates pass.
- Uniformization is restricted to an eligible scalar collision generator.
- Preserve explicit `c`, `hbar`, and normalization metadata unless the authority declares normalized units.

---

### Task 1: Production-host inventory

**Files:**
- Create: `docs/development/P_MIG_II_HOST_INVENTORY.json`
- Create: `docs/development/P_MIG_II_PREFLIGHT.md`

**Interfaces:**
- Produces: one selected host and classifications for every candidate repository/crate/artifact.

- [ ] Inventory the public BASS repo, exact offline RustCore, archived complete RustCore and any current production branch with commit/tree/crate-root hashes.
- [ ] Write a failing schema check that rejects multiple production owners or a missing rollback boundary.
- [ ] Classify every candidate as `PRODUCTION_OWNER`, `REFERENCE`, `LAB`, or `QUARANTINE`.
- [ ] Select exactly one host and record the reason, branch and crate root.
- [ ] Run the schema check and commit with `docs: select Type-II production host`.

### Task 2: Compile-only state and callback contract

**Files:**
- Create: `runtime/contracts/typeii_production_contract.rs`
- Create: `runtime/contracts/tests/typeii_production_contract.rs`

**Interfaces:**
- Produces: `TypeIIState`, normalization metadata, kernel callbacks, exp/phi backend trait and structured errors.

- [ ] Write failing compile/tests for host→TypeII→host roundtrip, invalid normalization and dimension mismatch.
- [ ] Implement the smallest compile-only structs/traits and a mock adapter.
- [ ] Verify no production module imports the contract.
- [ ] Run crate-root `cargo test --locked --offline` for the contract target.
- [ ] Commit with `runtime: define Type-II production migration contract`.

### Task 3: Acceptance matrix and independent auditors

**Files:**
- Create: `docs/development/P_MIG_II_ACCEPTANCE_MATRIX.json`
- Modify: `docs/development/P_MIG_II_PREFLIGHT.md`

**Interfaces:**
- Produces: executable commands and tolerances for migration PR `II-0`.

- [ ] Specify dense small-system, full-Arnoldi and scalar-uniformization oracle commands.
- [ ] Specify the old midpoint-frozen AEM2 and Kato-AEM2 comparator with the same fixture and output norm.
- [ ] Specify `alpha={1,1e3,1e5}`, conservation, rollback and offline-replay gates.
- [ ] Add a negative control that rejects use of polarized uniformization without a proven rate structure.
- [ ] Validate the JSON and commit with `docs: freeze Type-II migration acceptance matrix`.

### Task 4: Preflight hostile review

**Files:**
- Modify: `docs/development/P_MIG_II_PREFLIGHT.md`

**Interfaces:**
- Produces: final PASS/BLOCKED decision for opening `G-PRODUCTION-MIGRATION-II-0`.

- [ ] Audit state ownership, units, sign conventions, rollback, offline reproducibility and backend substitution.
- [ ] Attempt to route through a lab/quarantine crate and require rejection.
- [ ] Attempt to make adaptive Krylov the default without benchmark evidence and require rejection.
- [ ] Verify that no production source changed in the preflight diff.
- [ ] Record P0/P1/P2 and commit with `audit: close Type-II migration preflight`.
