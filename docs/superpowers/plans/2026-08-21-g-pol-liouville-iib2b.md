# G-POL-LIOUVILLE-II-B2B Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a deterministic icosphere face locator and one-step Type-II polarized semi-Lagrangian adapter on the B2A common-screen remap core.

**Architecture:** Generate a recursively refined icosphere without runtime geometry dependencies, locate departure directions by radial barycentric intersection with outward hull faces, and delegate tensor interpolation to B2A. Backward and forward ray transport use the sealed PR #11 Lie-midpoint characteristic.

**Tech Stack:** Rust 1.94.1, Python 3/SciPy independent oracle, pinned offline Cargo vendor.

**Spec:** `docs/superpowers/specs/2026-08-21-g-pol-liouville-iib2b-design.md`

## Global Constraints

- Metric signature remains `(-,+,+,+)`.
- Runtime interpolation weights remain convex and sum to one.
- No nearest-neighbour or antipodal silent fallback.
- `packed[8]=-V/2` remains inherited from PR #13.
- Rust runtime adds no new dependency.
- SciPy/Qhull is independent validation only.

---

### Task 1: RED mesh and locator contract

**Files:**
- Create: `runtime/rust/typeii/tests/typeii_spherical_grid_remap_unit.rs`
- Modify: isolated RustCore integration test registration only after RED is observed.

- [ ] Write tests for icosphere counts, outward/manifold validation, full directional coverage, deterministic edge/vertex tie-breaks, and orientation mutation rejection.
- [ ] Run the targeted test and record the unresolved-module RED.

### Task 2: GREEN deterministic icosphere and locator

**Files:**
- Create: `runtime/rust/typeii/typeii_spherical_grid_remap.rs`
- Modify: RustCore `src/generated/mod.rs` in the isolated verifier only.

- [ ] Implement level-0 icosahedron, recursive midpoint refinement, mesh validation, radial barycentric locator, and provenance diagnostics.
- [ ] Run targeted tests until green.

### Task 3: RED/GREEN departure and one-step adapter

**Files:**
- Modify: `runtime/rust/typeii/tests/typeii_spherical_grid_remap_unit.rs`
- Modify: `runtime/rust/typeii/typeii_spherical_grid_remap.rs`

- [ ] Add failing analytic solid-body rotation departure, combined one-step, error separation, and dimension/fail-closed tests.
- [ ] Implement generic and Type-II wrappers using PR #11 and PR #14 APIs.
- [ ] Verify refinement and roundtrip/diffusion tests.

### Task 4: Independent SciPy/Qhull fixture

**Files:**
- Create: `compiler/validation/typeii_spherical_grid_oracle.py`
- Create: `compiler/validation/typeii_spherical_grid_oracle.json`
- Create: `compiler/validation/test_typeii_spherical_grid.py`
- Create: `runtime/rust/typeii/tests/support/typeii_spherical_grid_fixture.rs`
- Create: `runtime/rust/typei/tests/typei_spherical_grid_fixture.rs`

- [ ] Generate level-1/2 convex hull facets with SciPy Qhull.
- [ ] Compare canonical face sets, sampled face keys/weights, and analytic solid-body outputs.
- [ ] Require byte-identical JSON/Rust fixture regeneration.

### Task 5: Hostile audit and closeout

**Files:**
- Create: `compiler/runtime/G_POL_LIOUVILLE_II_B2B_AUDIT.md`
- Create: `compiler/runtime/G_POL_LIOUVILLE_II_B2B_LITERATURE.md`
- Create: `compiler/runtime/G_POL_LIOUVILLE_II_B2B_RECEIPTnjson`

- [ ] Mutate face orientation check, deterministic tie-break, no-fallback path, and screen transport call; verify rejection.
- [ ] Run targeted Rust, independent Python, full locked/offline RustCore, and rustfmt.
- [ ] Package exact overlay/logs/plots and create one stacked PR on PR #14 without merge.
