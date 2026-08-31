# RF04 V2 Public-Mapping R2 Implementation Plan

> For agentic workers: use superpowers:executing-plans. Steps use checkbox syntax for tracking.

**Goal:** Publish an implementation-complete authority package and hand LOCAL-01 public-boundary source work to an isolated local Codex job.

**Architecture:** R2 updates only the authority package on top of PR #71. It changes the existing v2 identity symbol to contextual inputs, binds all remaining serialization and error semantics, and uses a strict validator plus a sealed delivery ZIP to prevent the earlier structural-only acceptance.

**Tech Stack:** Python 3 standard library package verifier, SHA-256, deterministic ZIP packaging, GitHub immutable object API.

**Spec:** R2_AUTHORITY_AMENDMENT.json and R2_DESIGN.md

## Global Constraints

- Parent authority head is a69b0516274648788e151046cc0233651e39e4b7; publication must be an ordinary fast-forward.
- PR #70 remains open/draft/unmerged and unchanged.
- No Rust/PyO3 production source, no numerical route decision, and no LOCAL-02 work is modified here.
- The final source donor is Git blob 693e9fff0d44f2b8e40966ceb8da3c348d830bd4.
- Claim ceiling remains PASS_RF04_SCALAR_RAW_SLICE_PROOF and NO_PASS_RF04.

### Task 1: Lock the contract gap with RED tests

**Files:** test_validate_mapping.py; validate_mapping.py

- [x] Write tests rejecting zero-argument dynamic identity, runtime wheel hash, absent receipt codecs, and absent batch/diagnostic semantics.
- [x] Run them and preserve the intended four failures.
- [x] Add the minimal semantic validator.
- [x] Rerun the tests to obtain GREEN.

### Task 2: Issue R2 authority and implementation-complete mapping

**Files:** R2_AUTHORITY_AMENDMENT.json; AUTHORITY_REBIND.json; V2_PUBLIC_MAPPING.json; R2_DESIGN.md

- [x] Record the approved decisions.
- [x] Bind every decision in the mapping.
- [x] Verify JSON parsing and semantic validator output.

### Task 3: Refresh the local-only handoff and sealed delivery

**Files:** LOCAL_IMPLEMENTATION_PROMPT_R2.md; LOCAL_CODEX_HANDOFF_CONTRACT.json; LOCAL_CODEX_HANDOFF.md; README.md; MANIFEST.sha256; delivery ZIP and SHA-256 sidecar

- [x] Write the local prompt.
- [x] Update the contract and generated Markdown.
- [x] Generate the deterministic ZIP and sidecar.
- [x] Validate manifest, ZIP contents, JSON, and test suite.

### Task 4: Publish and read back the immutable authority amendment

**Files:** Remote modify only: PR #71 head branch

- [ ] Create blobs, one tree, and one child commit.
- [ ] Fast-forward only the PR #71 head.
- [ ] Read back changed paths, blobs, commit parent/tree, draft state, and CI state.
