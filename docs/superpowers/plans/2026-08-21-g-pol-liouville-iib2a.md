# G-POL-LIOUVILLE-II-B2A Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a fail-closed common-screen convex remap core for packed polarized coherency tensors.

**Architecture:** Validate physical source tensors and convex weights, parallel transport each source by the minimal SO(3) rotation along the shortest sphere geodesic, interpolate only after all tensors share the target screen, and expose diagnostics. Grid-specific stencil construction stays outside this checkpoint.

**Tech Stack:** Rust 1.94.1, Python 3 / NumPy / SciPy independent oracle, pinned offline Cargo vendor.

**Spec:** `docs/superpowers/specs/2026-08-21-g-pol-liouville-iib2a-design.md`

## Global Constraints

- Base is PR #13, `agent/g-pol-liouville-ii-b1`, HEAD `6067501f24bba03b317f5de19b5625c79b9e6467`.
- Metric signature remains `(-,+,+,+)`; directions and weights are dimensionless.
- Use the existing BASS packed-9 ordering; do not reinterpret B1 Stokes signs.
- Require non-negative convex weights and fail closed near antipodes.
- Do not add a HEALPix/grid dependency.

### Task 1: Geometry and fail-closed contract

- [ ] Write RED tests for exact direction mapping, roundtrip, antipodal rejection, nonphysical-source rejection and invalid weights.
- [ ] Run the targeted Rust test and record the expected unresolved-module RED.
- [ ] Implement minimal rotation, tensor congruence, screen validation and convex interpolation.
- [ ] Run the targeted tests to GREEN.

### Task 2: Polarization invariants and negative control

- [ ] Add RED tests for monopole exactness, covariantly constant tensor exactness, V=0/cone preservation and source-dyad gauge invariance.
- [ ] Add the deliberately wrong component-wise Q/U interpolation in test code only and require a finite failure witness.
- [ ] Run targeted tests to GREEN.

### Task 3: Spatial refinement and independent oracle

- [ ] Add symmetric-stencil l=1/spin-2 amplitude refinement tests with second-order ratios.
- [ ] Generate an independent SciPy rotation fixture and compare Rust output.
- [ ] Run Python and Rust oracle tests.

### Task 4: Closeout

- [ ] Run full locked/offline Cargo regression and rustfmt.
- [ ] Record audit, literature boundary, receipt and hashes.
- [ ] Create one stacked commit/PR; do not merge.
