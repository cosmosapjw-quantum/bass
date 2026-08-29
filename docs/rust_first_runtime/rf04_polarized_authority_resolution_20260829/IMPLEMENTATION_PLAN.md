# RF-04 Polarized v2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` or `superpowers:executing-plans`
> task-by-task. Every task ends in a focused test cycle and commit.

**Goal:** Implement and independently prove a complete Type-II polarized
trajectory/batch route whose formerly ambiguous choices are explicit,
content-addressed inputs or frozen palindromic route semantics.

**Architecture:** Preserve the proven scalar v1 route. Add a separate polarized
v2 owner that validates a caller-supplied CSR remap plan, performs a two-half
backtrace/remap/geometric pullback, composes endpoint Kato and midpoint
collision actions palindromically, and commits fixed-Eulerian history rows plus
geometry receipts.

**Tech Stack:** Rust 1.94.1, PyO3, Rayon, existing generated/runtime Type-II
donors, Python/NumPy/SciPy test-only independent references, maturin offline
locked builds.

**Spec:** `docs/rust_first_runtime/rf04_polarized_authority_resolution_20260829/AUTHORITY_DECISIONS.json` and
`PUBLIC_ROUTE_SCHEMA_DELTA_V2.json`.

## Global Constraints

- Source HEAD/tree: `50b6e9f7a6741b7fd25b0421d2a674b9eb92cdda` / `b32fcc26ca51dcaca9e9225d48b03fe9e02988ed`.
- Preserve `PASS_RF04_SCALAR_RAW_SLICE_PROOF`; do not rerun it for reassurance.
- Existing formula source blobs in `PACKAGE.json` are immutable.
- No Python production loop or fallback.
- No hidden stencil-builder choice.
- Different remap-plan hashes are distinct numerical inputs.
- No clipping, silent projection, partial trajectory success or history-grid
  ambiguity.
- One dual review and at most one repair.
- No timing, GPU, Wolfram, full suite, RF-05+, merge or ready transition.

---

### Task 1: Import and bind the measured source-probe evidence

**Files:**
- Copy exactly:
  `artifacts/rust_first_runtime/rf04/polarized_source_probe/**`
- Create:
  `artifacts/rust_first_runtime/rf04/polarized_authority/EVIDENCE_IMPORT.json`
- Test:
  `tests/rf04/test_polarized_authority_package.py`

**Interfaces:**
- Consumes: local manifest SHA-256 `c05a78d373f3fd87c028e8535404c2b4723aff56c533163d3822355cf3987ea1`.
- Produces: `source_probe_manifest_sha256` and an exact evidence inventory.

- [ ] Verify the local manifest and source identity.

```bash
sha256sum artifacts/rust_first_runtime/rf04/polarized_source_probe/MANIFEST.sha256
sha256sum -c artifacts/rust_first_runtime/rf04/polarized_source_probe/MANIFEST.sha256
git rev-parse HEAD HEAD^{tree}
```

Expected: manifest file SHA-256 exactly `c05a78d373f3fd87c028e8535404c2b4723aff56c533163d3822355cf3987ea1` and source
identity exactly `50b6e9f7a6741b7fd25b0421d2a674b9eb92cdda` / `b32fcc26ca51dcaca9e9225d48b03fe9e02988ed` before the implementation
branch commit.

- [ ] Copy the directory without rewriting JSON or figure bytes.

- [ ] Write `EVIDENCE_IMPORT.json` with the source head/tree, manifest digest,
  exact copied paths, and `USER_LOCAL_EXECUTION_IMPORTED_NOT_RERUN`.

- [ ] Run the package/evidence selector.

```bash
python3 -m pytest -q tests/rf04/test_polarized_authority_package.py
```

- [ ] Commit.

```bash
git add artifacts/rust_first_runtime/rf04/polarized_source_probe   artifacts/rust_first_runtime/rf04/polarized_authority   tests/rf04/test_polarized_authority_package.py
git commit -m "chore(rf04): import measured polarized source-probe evidence"
```

### Task 2: Add the v2 schema and genuine RED

**Files:**
- Create: `_rustcore/src/kinetic/rf04_polarized_v2.rs`
- Create: `_rustcore/src/kinetic/rf04_polarized_v2_tests.rs`
- Create: `_rustcore/src/python/rf04_polarized_v2.rs`
- Create: `tests/rf04/test_polarized_route_v2.py`
- Modify: `_rustcore/src/kinetic/mod.rs`
- Modify: `_rustcore/src/python/mod.rs`

**Interfaces:**
- Produces:
  `RemapPlanV1`, `PolarizedTrajectoryV2`, `PolarizedBatchV2`,
  `validate_remap_plan_v1`.
- No native registration is added until Task 5.

- [ ] Define `RemapPlanV1` with target offsets, source indices, weights,
  direction-grid hash, builder identity, plan hash and serialized support bound.

```rust
pub struct RemapPlanV1 {
    pub target_offsets: Vec<usize>,
    pub source_indices: Vec<usize>,
    pub weights: Vec<f64>,
    pub direction_grid_sha256: String,
    pub builder_id: String,
    pub builder_version: String,
    pub plan_sha256: String,
    pub minimum_transport_dot: f64,
}
```

- [ ] Write failing Rust tests for empty rows, negative/nonfinite weights,
  wrong partition of unity, stale grid/plan hashes, free 0.75/0.80 support
  constants, history-grid mutation, and unsupported v1-polarized dispatch.

- [ ] Write Python boundary RED asserting the three v2 symbols are absent and
  v1 polarized remains `RF04_UNSUPPORTED_CAPABILITY`.

- [ ] Run RED.

```bash
cargo test --manifest-path _rustcore/Cargo.toml --offline --locked   rf04_polarized_v2_ -- --nocapture
python3 -m pytest -q tests/rf04/test_polarized_route_v2.py
```

Expected: numerical/schema assertion failures, not import collection failure.

- [ ] Commit RED only.

### Task 3: Implement plan validation and the geometric pullback

**Files:**
- Modify: `_rustcore/src/kinetic/rf04_polarized_v2.rs`
- Test: `_rustcore/src/kinetic/rf04_polarized_v2_tests.rs`

**Interfaces:**
- Consumes existing donor functions:
  `transport_characteristic_profile`, `remap_convex_packed`.
- Produces:
  `validated_plan`, `geometry_pullback_step`, `GeometryReceiptV1`.

- [ ] Implement canonical CSR validation and plan hashing.

- [ ] Compute the active support minimum from strictly positive-weight entries
  and require the serialized value to be exactly one binary64 step downward.

- [ ] For each fixed target direction, backtrace q3→mid and mid→q1 with one
  public half-panel each. Preserve the donor's internal fixed-point bisections.

- [ ] Remap source-grid tensors to the backtraced source direction, then apply
  the characteristic spatial transport and bolometric factor to the fixed
  target direction.

- [ ] Produce a receipt containing grid/plan/backtrace/transport hashes,
  screen leakage, minimum eigenvalue, panel count and bisection count.

- [ ] Run focused tests and independent geometric reference comparisons.

```bash
cargo test --manifest-path _rustcore/Cargo.toml --offline --locked   rf04_polarized_v2_geometry_ -- --nocapture
```

- [ ] Commit.

### Task 4: Implement palindromic composition and fixed history

**Files:**
- Modify: `_rustcore/src/kinetic/rf04_polarized_v2.rs`
- Test: `_rustcore/src/kinetic/rf04_polarized_v2_tests.rs`
- Create: `tests/rf04/rf04_polarized_dense_oracle.py`

**Interfaces:**
- Produces:
  `polarized_step_v2`, `polarized_trajectory_v2`,
  `PolarizedRestartStateV2`.

- [ ] Implement exactly:

```text
K(q1,h/2)
C(mid,h opacity_scale opacity_mid/2)
G_h
C(mid,h opacity_scale opacity_mid/2)
K(q3,h/2)
```

- [ ] Derive `vdot` only from the existing Type-II background RHS at q1/q3.

- [ ] Commit one fixed-grid state row only after all five actions and physical
  guards pass; rejected steps leave state/history/receipt chain unchanged.

- [ ] Store transient geometry only by receipt and restart chain identity.

- [ ] Build an independent dense small-grid oracle that assembles collision
  and Kato actions independently and uses the same declared geometric map, not
  production diagnostics.

- [ ] Prove second order, forward/reverse consistency and PSD/screen invariants.

- [ ] Commit.

### Task 5: Wire native v2 symbols, Python routes and batch isolation

**Files:**
- Modify: `_rustcore/src/python/register.rs`
- Modify: `_rustcore/src/lib.rs`
- Modify: `_rustcore/src/python/mod.rs`
- Modify: `bianchi/backend_policy.py`
- Modify: `bianchi/kinetic/__init__.py`
- Modify: `_rustcore/src/python/rf04_polarized_v2.rs`
- Test: `tests/rf04/test_polarized_route_v2.py`

**Interfaces:**
- Registers:
  `rf04_typeii_polarized_execution_identity_v2`,
  `rf04_typeii_polarized_trajectory_v2`,
  `rf04_typeii_polarized_batch_v2`.

- [ ] Marshal and validate arrays/CSR plan in PyO3; call Rust once per member,
  never a Python time-step loop.

- [ ] Keep shared-plan errors as whole-call failures and isolate malformed
  member state as ALL_NAN/nonzero status in batch.

- [ ] Include decision, plan, grid, source-owner and payload identities in the
  execution identity.

- [ ] Verify scalar v1 bytes/behavior and v1-polarized fail-closed behavior are
  unchanged with directly affected selectors only.

- [ ] Commit.

### Task 6: Build the targeted scientific proof

**Files:**
- Create: `tests/rf04/test_polarized_public_differential_v2.py`
- Create: `tools/audit/rf04_polarized_native_mutations_v2.py`
- Create:
  `artifacts/rust_first_runtime/rf04/polarized_v2/EVIDENCE.json`

**Interfaces:**
- Consumes the actual installed native extension.
- Produces state-array, invariant, mutation, restart and batch receipts.

- [ ] Build one pristine offline/locked wheel and install it with
  `--no-index --no-deps` in a fresh environment.

- [ ] Run public state-array comparison on nondegenerate Type-II cases,
  raw/AP/paired routes, at least two distinct valid plan hashes and
  2/4/8/16/32 refinement.

- [ ] Compile and run independent mutants for K sign, collision/geometry order,
  q1/mid/q3 collapse, support bound, plan row, screen association and history
  transaction. Each mutant must reach native execution and fail a numerical or
  schema assertion.

- [ ] Verify event-free restart and separate-process 1-thread/4-thread ordered
  batch identity.

- [ ] Generate the five source-probe figures plus full-trajectory state,
  invariant and convergence plots and host-read all of them.

- [ ] Commit proof/evidence.

### Task 7: Bounded audit, restore and remote delivery

**Files:**
- Update:
  `artifacts/rust_first_runtime/rf04/polarized_v2/EVIDENCE.json`
- Create:
  `artifacts/rust_first_runtime/rf04/polarized_v2/MANIFEST.sha256`

- [ ] Run one PHYS-MATH and one PHYS-MATH-CODE review.

- [ ] Reproduce every P0/P1 finding before repair; permit at most one repair
  cycle and one differential rereview.

- [ ] Rebuild in an independent output directory. Classify archive-only
  metadata differences separately from SO/normalized-content identity.

- [ ] Fresh no-index restore and production dispatch without development
  override.

- [ ] Verify changed-path closure, ordinary-push the implementation branch and
  open one stacked draft PR against the package branch.

- [ ] Read back exact head/tree/paths/workflows/artifacts and stop without
  merge or ready transition.
