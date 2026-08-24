# G-POL-LIOUVILLE-IIA Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a Type-II paired-characteristic polarized Liouville authority lane with structure-preserving screen transport and independent coordinate validation.

**Architecture:** Use the first-principles homogeneous tetrad generator reduced to a three-dimensional angular velocity. Advance direction and the rank-9 screen coherency tensor with a self-adjoint Lie midpoint rule, while exposing a callback background profile and cumulative proper rotation for independent coordinate comparison.

**Tech Stack:** Rust 1.94.1, pinned offline Cargo vendor, Python/NumPy independent validation.

**Spec:** `docs/superpowers/specs/2026-08-20-g-pol-liouville-iia-design.md`

## Global Constraints

- Preserve metric signature `(-,+,+,+)` and the existing BASS tetrad/commutator conventions.
- Keep `v2` out of geometric Liouville transport.
- Use the checked physical screen carrier from PR #10.
- Do not add fixed-grid remapping, harmonic projection, collision splitting, or observables.
- Every counted test source must be committed.
- Run Rust 1.94.1 from the pinned crate root with `--locked --offline`.

---

### Task 1: Instantaneous geometric generator

**Files:**
- Create: `runtime/rust/typeii/typeii_polarized_liouville.rs`
- Test: `runtime/rust/typeii/tests/typeii_polarized_liouville_unit.rs`

**Interfaces:**
- Produces: `HomogeneousRayBackground`, `LiouvilleCoefficients`, `typeii_background_from_state`, `liouville_coefficients`, `polarized_bolometric_rhs`.

- [ ] Add RED tests for FLRW, pure screen twist, Type-II closed formulas, direct connection reduction, and global-tilt exclusion.
- [ ] Run targeted Rust test and confirm missing-module/API failures.
- [ ] Implement the minimal generator and checked tensor RHS.
- [ ] Run targeted tests to GREEN.

### Task 2: Structure-preserving finite characteristic

**Files:**
- Modify: `runtime/rust/typeii/typeii_polarized_liouville.rs`
- Modify: `runtime/rust/typeii/tests/typeii_polarized_liouville_unit.rs`

**Interfaces:**
- Produces: `transport_characteristic_profile`, `transport_characteristic`, `transport_typeii_characteristic`, `PolarizedCharacteristicResult`.

- [ ] Add RED tests for central-difference RHS, cone/screen preservation, roundtrip, frame covariance, and second-order convergence.
- [ ] Verify the explicit predictor-only midpoint fails the roundtrip gate.
- [ ] Implement the fixed-point Lie midpoint and cumulative rotation diagnostics.
- [ ] Run targeted tests to GREEN and remove diagnostic prints.

### Task 3: Independent coordinate and source-derived oracles

**Files:**
- Create: `compiler/validation/typeii_polarized_liouville_coordinate_oracle.py`
- Create: `compiler/validation/test_typeii_polarized_liouville.py`
- Create: `runtime/rust/typeii/tests/typeii_polarized_liouville_fixture.rs`

**Interfaces:**
- Consumes: exact background-profile callback and existing Type-II fixture.
- Produces: independent coordinate Bianchi-II values and source-derived screen/cone receipt.

- [ ] Generate the coordinate Bianchi-II geodesic plus parallel-transport oracle independently of Rust.
- [ ] Add a Rust RED test for the static direction/redshift/rotation values.
- [ ] Add the exact profile callback and cumulative rotation result.
- [ ] Run Python and Rust tests to GREEN.

### Task 4: Audit, provenance, and full replay

**Files:**
- Create: `compiler/runtime/G_POL_LIOUVILLE_IIA_AUDIT.md`
- Create: `compiler/runtime/G_POL_LIOUVILLE_IIA_RECEIPT.json`

**Interfaces:**
- Produces: machine-readable claim boundary, hashes, metrics, and next-DAG declaration.

- [ ] Run targeted Python and Rust suites.
- [ ] Run inherited PR #10 tests and full `cargo test --locked --offline`.
- [ ] Run direct `rustfmt --check` only on changed Rust files.
- [ ] Perform PHYS-MATH and PHYS-MATH-CODE hostile review.
- [ ] Record exact hashes, counts, errors, and nonclaims.

### Task 5: Atomic stacked PR

**Files:** all files above under their repository paths.

**Interfaces:**
- Consumes: PR #10 HEAD `c4bdd3ea0ca4db4fd8b975968063fa128c4a55d3`.
- Produces: one-commit `agent/g-pol-liouville-iia` stacked PR.

- [ ] Construct the exact tree on PR #10.
- [ ] Verify parent, tree, changed-file list, and one-commit topology.
- [ ] Push the branch and create a non-draft PR with the narrow claim boundary.
- [ ] Re-fetch the remote PR and verify open/mergeable state.
