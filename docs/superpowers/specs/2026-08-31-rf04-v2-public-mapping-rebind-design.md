# RF04 V2 Public-Mapping Rebind Design

## Purpose

Resolve the documented LOCAL-01 public-boundary authority gap without changing the frozen numerical route, production solver behavior, or scientific status. The resulting authority package is a child of PR #70 and is consumed only by a new local implementation branch.

## Components

AUTHORITY_REBIND.json fixes the parent commits, inherited Git blobs, and final safety-rebound donor. V2_PUBLIC_MAPPING.json completes the missing public contract: PyO3 argument order, NumPy dtypes and shapes, canonical identity codecs, trajectory and batch result shapes, and mappings onto the existing v1 Python exception classes. LOCAL_CODEX_HANDOFF_CONTRACT.json declares the local job outcome, measurable gates, permissions, evidence, and fail-closed stop conditions.

## Data flow

The local implementation must intake the authority package before source edits. It validates the source owner and derives route-decision hashes from the inherited direct texts. The native Rust route validates common v1 input and the v2 carrier/CSR additions, returns a canonical execution identity, and exposes fixed-grid trajectory or isolated batch results through PyO3. The local job writes evidence and opens only a draft implementation PR.

## Compatibility and failure semantics

Scalar v1 and polarized-on-v1 behavior remain unchanged. The v2 path gets a distinct schema and three distinct symbols. Whole-call schema, grid, plan, and capability failures use the existing typed exception classes. Batch-member failures return documented all-NaN/status/error-code rows. A trajectory failure returns no partial history.

## Scope ratchet

Only the raw fixed-grid v2 route is active in LOCAL-01. AP-corrected and paired-reference tokens remain explicit typed capability failures. The design does not start LOCAL-02, add an alternate numerical plan, or promote a science/performance claim.

## Verification

The package validator checks exact authority anchors, contract shape, result dimensions, raw-route activation, and its SHA-256 manifest. The local plan requires test-first implementation, locked-wheel readback, affected Rust/Python checks, two audits, and draft-only remote readback.
