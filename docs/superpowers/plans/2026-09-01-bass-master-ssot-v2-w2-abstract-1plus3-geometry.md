# BASS Master SSOT v2 W2 Abstract 1+3 Geometry Implementation Plan

> **For agentic workers:** Execute this plan with test-first changes, exact-pinned Wolfram/xAct identity, fresh headless verification, and immutable stage receipts.

**Goal:** Establish the abstract normal-frame 1+3 geometry required before any ONF Bianchi component or Einstein-background derivation.

**Architecture:** W2 registers one four-dimensional Lorentzian xTensor model, selects a deterministic pure-Wolfram canonicalization lane, verifies the projector and kinematic split by exact residuals, and publishes a semantic Gauss-Codazzi sign registry. W3, not W2, owns the independent xCoba/ONF component proof.

**Tech stack:** Wolfram Language 15.0.1; exact-pinned xAct/xTensor 1.3.0 and xPerm 1.2.4; MUnit `.wlt`; canonical RawJSON receipts.

**Spec:** `docs/bass_master_ssot_v2/W2/README.md`

## Global constraints

- Metric signature: `(-,+,+,+)`.
- Spatial orientation: `epsilon_123=+1`.
- Unit normal: `n^a n_a=-1`.
- Positive extrinsic-curvature convention: `K_ab=h_a^c h_b^d nabla_c n_d`.
- Split: `K_ab=H_geom h_ab+sigma_ab`, hence `K=3 H_geom`.
- Natural units are not assumed.
- No notebook-only authority and no pretty-print equality oracle.
- No xCoba component or Bianchi-type claim in W2.

## Task 1 — RED gate

- Verify that `CreateAbstract1Plus3Geometry`, `Abstract1Plus3Residuals`, and `Abstract1Plus3EquationRegistry` do not exist on the W0/W1 parent.
- Record the three expected failures in `TDD_RED_RECEIPT.json`.

## Task 2 — canonicalization and xTensor model

- Add `CanonicalizationBackend.wl`.
- Add `Abstract1Plus3.wl`.
- Register manifold, metric, covariant derivative, normal, acceleration, shear, and Hubble scalar.
- Select pure-Wolfram xPerm canonicalization explicitly before `DefMetric`.

## Task 3 — exact identities and semantic curvature registry

- Verify exact zero residuals for normal norm, projector spatiality/idempotence/trace, acceleration spatiality, and the trace/spatiality of the `K_ab=H h_ab+sigma_ab` split.
- Record the spatial volume-form definition and xAct symmetry metadata.
- Emit exact EquationIR entries for projector, volume form, acceleration, extrinsic curvature, normal derivative, expansion-shear split, Gauss, Codazzi, and contracted Gauss.

## Task 4 — headless stage runner and receipt

- Extend `run_stage.wls` with `--stage W2`.
- Run W0, W1, and W2 tests in a fresh kernel.
- Commit a JSON-safe W2 receipt, Git-object manifest, Dropbox readback, and Atlassian synchronization locators.

## Completion boundary

```text
W2_ABSTRACT_1PLUS3_PROJECTOR_AND_KINEMATIC_INFRASTRUCTURE_VERIFIED
GAUSS_CODAZZI_SIGN_REGISTRY_VERIFIED
NO_XCOBA_COMPONENT_DUAL_PROOF
NO_BACKGROUND_EINSTEIN_EQUATIONS
NO_IMPLEMENTATION_PARITY
NO_SCIENCE_VALIDITY
NO_PASS_RF04
```
