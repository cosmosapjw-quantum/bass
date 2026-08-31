# RF04 V2 Public Mapping LOCAL-01 Implementation Plan

> For agentic workers: required process is superpowers:subagent-driven-development or superpowers:executing-plans. Follow each checkbox in order.

**Goal:** Implement only the authorized RF04 polarized-v2 public boundary and collect the remaining LOCAL-01 evidence.

**Architecture:** Keep the v2 Rust core, PyO3 adapter, registration, backend policy, and Python wrappers as a thin native route. The v2 route consumes the final donor and a caller-supplied content-addressed CSR plan; it never falls back to a Python time-step loop.

**Tech Stack:** Rust 1.94.1 offline locked cargo, PyO3, maturin, repository-pinned Python 3.12, pytest.

**Spec:** docs/superpowers/specs/2026-08-31-rf04-v2-public-mapping-rebind-design.md

## Global Constraints

- Parent must be the exact authority-PR head; PR #70 remains unmodified and unmerged.
- runtime/rust/typeii/typeii_polarized_liouville.rs must resolve to Git blob 693e9fff0d44f2b8e40966ceb8da3c348d830bd4.
- Preserve P1 through P5 and all v1 public behavior.
- Implement only fixed_grid_raw_v1; retain explicit typed capability failure for the other two v2 tokens.
- No Python production fallback, no Python time-step loop, no new Python exception class, no LOCAL-02 work, and no claim promotion.

---

### Task 1: Verify authority before source edits

**Files:**
- Read: docs/rust_first_runtime/rf04_v2_public_mapping_rebind_20260831/AUTHORITY_REBIND.json
- Read: docs/rust_first_runtime/rf04_v2_public_mapping_rebind_20260831/V2_PUBLIC_MAPPING.json
- Create: artifacts/rust_first_runtime/rf04/local01_v2_public_mapping/AUTHORITY_RECEIPT.json

**Interfaces:**
- Consumes: exact authority branch head and inherited v1/v2 Git blobs.
- Produces: a fail-closed authority receipt for later tasks.

- [ ] Run the package validator and Git object checks. Expected: package PASS and final donor blob 693e9fff0d44f2b8e40966ceb8da3c348d830bd4.
- [ ] Write only verified parent/head/tree/blob/SHA values to AUTHORITY_RECEIPT.json with status PASS_AUTHORITY_INTAKE_ONLY.
- [ ] Parse the receipt with python3 -m json.tool. Expected: exit 0.

### Task 2: Establish focused RED coverage

**Files:**
- Modify: tests/rf04/test_polarized_route_v2.py
- Modify: _rustcore/src/kinetic/rf04_polarized_v2.rs
- Modify: _rustcore/src/python/rf04_polarized_v2.rs

**Interfaces:**
- Consumes: exact v2 symbol names and mapping.
- Produces: focused failing tests while the v2 public route is absent.

- [ ] Add one independent test each for identity final-donor binding, raw trajectory result shape, batch shape/status, shared-plan whole-call error, member isolation, no partial trajectory result, AP/paired typed capability errors, and both mandatory nonfinite cases through PyO3.
- [ ] Run pytest -q tests/rf04/test_polarized_route_v2.py. Expected: new public-route assertions fail for the intended missing-symbol or reservation reason; preserve the RED log.

### Task 3: Implement the native carrier and error bridge

**Files:**
- Modify: _rustcore/src/kinetic/rf04_polarized_v2.rs
- Modify: _rustcore/src/python/rf04_polarized_v2.rs
- Modify: _rustcore/src/python/register.rs
- Modify: _rustcore/src/python/mod.rs
- Modify: _rustcore/src/lib.rs

**Interfaces:**
- Produces: rf04_typeii_polarized_execution_identity_v2 returning canonical JSON UTF-8, rf04_typeii_polarized_trajectory_v2 returning a mapping, and rf04_typeii_polarized_batch_v2 returning a mapping.

- [ ] Marshal v1 common arrays plus v2 float64 C-contiguous [9*M] or [B,9*M] arrays, uint64 CSR arrays, and float64 CSR weights. Every uint64-to-usize conversion is checked.
- [ ] Build canonical grid/plan identity bytes, bind the final donor, parent route/decision hashes, fixed composition/history IDs, and exact wheel SHA-256.
- [ ] Use existing classes only: input to RF04InputError, capability to RF04CapabilityError, physical carrier to RF04PhysicalDomainError, checked numerical/certificate failures to RF04CertificateError, and batch-local failures in result rows.
- [ ] Run the focused route suite. Expected: every Task 2 test passes without weakening its assertion.

### Task 4: Register and expose v2 without changing v1

**Files:**
- Modify: bianchi/backend_policy.py
- Modify: bianchi/kinetic/__init__.py
- Modify: tests/rf04/test_polarized_route_v2.py

**Interfaces:**
- Produces: backend-policy inventory and Python wrappers for the exact v2 routes.

- [ ] Register only the three defined v2 symbols and wrappers.
- [ ] Assert all three v1 symbols and their fail-closed polarized behavior remain unchanged.
- [ ] Assert production calls Rust once per trajectory/member and have no Python loop over K.
- [ ] Run the focused suite again. Expected: pass.

### Task 5: Build and collect LOCAL-01 evidence

**Files:**
- Create: artifacts/rust_first_runtime/rf04/local01_v2_public_mapping/LOCAL01_V2_VALIDATION.json
- Create: artifacts/rust_first_runtime/rf04/local01_v2_public_mapping/RAW_MANIFEST.sha256

**Interfaces:**
- Consumes: completed public v2 route.
- Produces: evidence, not a science claim.

- [ ] Build the wheel with Rust 1.94.1 in offline locked mode and outside every Git worktree. Capture its SHA-256.
- [ ] Install in a clean environment; prove three v1 and three v2 symbols resolve; rerun the v2 public-route suite against that installed wheel.
- [ ] Run all repository-prescribed affected Rust/PyO3/Python selectors and record full exit status.
- [ ] Record raw/AP/paired route status, shared-plan failure, member failure, no partial result, both nonfinite cases, wheel identity, and whether LOCAL-01 can pass. Retain NO_PASS_RF04 if any requirement lacks evidence.

### Task 6: Audit and publish draft-only

**Files:**
- Create: artifacts/rust_first_runtime/rf04/local01_v2_public_mapping/PHYS_MATH_AUDIT.md
- Create: artifacts/rust_first_runtime/rf04/local01_v2_public_mapping/PHYS_MATH_CODE_AUDIT.md

**Interfaces:**
- Consumes: fresh LOCAL-01 evidence.
- Produces: a draft implementation PR or a fail-closed terminal receipt.

- [ ] Perform one PHYS-MATH and one PHYS-MATH-CODE audit; any unresolved P0/P1 stops the branch.
- [ ] Run git diff --check and inspect git status --short. Expected: no whitespace errors and allowlisted paths only.
- [ ] Push by ordinary fast-forward and create one draft PR based on the authority branch. Read back parent, head, tree, changed paths, and draft/unmerged state. Do not touch PR #70.
