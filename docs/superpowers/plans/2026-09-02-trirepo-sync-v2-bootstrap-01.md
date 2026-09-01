# TRI-SYNC-V2 Bootstrap-01 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first fail-closed, read-only synchronization control plane for `bass`, `rec_bianchi`, and `rei_bianchi`, then publish one identity-linked receipt across GitHub, Dropbox, and Atlassian.

**Architecture:** BASS hosts a standard-library Python auditor; each repository exports its owned namespaces and exact imports. The auditor emits a shadow DAG and duplicate/staleness reports but cannot mutate official Jira dependencies or scientific state. GitHub owns source identity, Dropbox owns append-only recovery, and Atlassian owns approved work decisions.

**Tech Stack:** Python 3.12 standard library, GitHub Actions, GitHub Git-data API, Dropbox text backup, Jira/Confluence, canonical JSON SHA-256.

**Spec:** `docs/superpowers/specs/2026-09-02-trirepo-sync-v2-design.md`

## Global Constraints

- Program ID is exactly `BIANCHI-WOLFRAM-TRIREPO-20260830`.
- Bootstrap ID is exactly `TRI-SYNC-V2-BOOTSTRAP-01`.
- Base only on BASS PR #68, REC PR #44, and REI PR #21 exact policy heads.
- Keep every PR Draft; do not merge, close, retarget scientific branches, or force-push.
- Preserve the approved edge set `REC -> REI`, `REC -> BASS`, `REI -> BASS`.
- Official DAG mutations require a later explicit approval receipt.
- No external dependency is permitted in the coordinator or unit tests.
- A valid bootstrap may report drift; drift is data, not a test failure.
- Dropbox paths are append-only and no existing backup is overwritten.
- No scientific, numerical, provider, RF04, REC, or REI claim is promoted.

---

### Task 1: Establish isolated policy branches and TDD RED

**Files:**
- Create: `tests/test_trirepo_sync_audit.py`
- Create: `.github/workflows/trirepo-sync-audit.yml`

**Interfaces:**
- Consumes: exact BASS policy commit `289a2d31d6fae38122191be73ec9c9d28acaf4d7`.
- Produces: branch `agent/policy/trirepo-sync-control-plane-v2-20260902-r1` and a failing contract run proving the production module is absent.

- [x] Create the BASS policy-child branch from the exact approved SHA.
- [x] Write tests for canonical hashes, run identity, duplicate authority, replay/oracle classification, stale/missing imports, immutable official edges, and output emission.
- [x] Add a workflow that runs only the new focused suite.
- [x] Commit the test without production code.
- [x] Confirm GitHub Actions fails in the coordinator-test step and confirm `scripts/trirepo_sync_audit.py` is absent at the RED commit.

### Task 2: Implement the minimal fail-closed coordinator

**Files:**
- Create: `scripts/trirepo_sync_audit.py`
- Test: `tests/test_trirepo_sync_audit.py`

**Interfaces:**
- Consumes: six parsed manifest associations, three Git bindings, approved edges, and observation metadata.
- Produces: `audit_documents(...)`, `compute_sync_run_id(...)`, `write_outputs(...)`, and a CLI with exit codes 0, 2, and 64.

- [x] Add deterministic UTF-8 canonical JSON and SHA-256 helpers.
- [x] Validate schema/program/repository/digest/cardinality inputs.
- [x] Build a unique-owner authority registry.
- [x] Detect authorized replays, unbound semantic duplicates, missing imports, stale hashes, convention drift, wrong producers, and stale Git bindings.
- [x] Emit the five canonical output documents.
- [x] Keep official edge mutations empty and label the result proposal-only.
- [x] Commit and confirm a fresh GitHub Actions GREEN run.

### Task 3: Publish repository contracts and schemas

**Files:**
- Create in BASS: `docs/bianchi_program/TRIREPO_SYNC_POLICY_V2.md`
- Create in all repositories: `docs/bianchi_program/TRIREPO_AUTHORITY_EXPORT.json`
- Create in all repositories: `docs/bianchi_program/TRIREPO_IMPORT_LOCK.json`
- Create in all repositories: `docs/bianchi_program/TRIREPO_SYNC_POINTER.json`
- Create in BASS: `docs/bianchi_program/TRIREPO_BOOTSTRAP_OBSERVATIONS.json`
- Create in BASS: `schemas/trirepo-authority-export.schema.json`
- Create in BASS: `schemas/trirepo-import-lock.schema.json`
- Create in BASS: `schemas/trirepo-sync-state.schema.json`

**Interfaces:**
- Consumes: namespace ownership from the existing tri-repo policy and exact policy PR identities.
- Produces: three exact exports, three exact import locks, and one honest bootstrap observation set.

- [ ] Register BASS conventions, geometry/background, matter-source envelope, and REC/REI splice ownership.
- [ ] Register REC recombination-history and shared atomic-rate ownership without claiming provider readiness.
- [ ] Register REI reionization-history and matter-source-value ownership without claiming provider readiness.
- [ ] Bind all declared imports to exact producer policy commit/tree and semantic/convention hashes.
- [ ] Record the active-lineage inventory gaps and REC PR #47 remote/body identity mismatch.
- [ ] Parse every JSON file and validate semantic payload hashes in the coordinator.
- [ ] Commit source contracts on three isolated policy-child branches.

### Task 4: Execute the first real tri-repository audit

**Files:**
- Create in BASS: `docs/bianchi_program/TRIREPO_AUTHORITY_REGISTRY.json`
- Create in BASS: `docs/bianchi_program/TRIREPO_SYNC_STATE.json`
- Create in BASS: `docs/bianchi_program/TRIREPO_DUPLICATE_REPORT.json`
- Create in BASS: `docs/bianchi_program/TRIREPO_DAG_PROPOSAL.json`
- Create in BASS: `docs/bianchi_program/TRIREPO_SYNC_RECEIPT.json`

**Interfaces:**
- Consumes: exact three-repository source commits and six contract documents.
- Produces: one deterministic `sync_run_id` and five matching output documents.

- [ ] Run the coordinator against the exact GitHub source commits.
- [ ] Confirm namespace ownership is unique and declared imports match.
- [ ] Confirm overall status remains `DRIFT_DETECTED` because active formula-level coverage is incomplete.
- [ ] Confirm `proposed_official_edge_mutations` is empty.
- [ ] Commit the exact generated outputs to BASS.
- [ ] Re-run focused tests and a committed-output replay.

### Task 5: Open three linked Draft PRs

**Files:** PR metadata only.

**Interfaces:**
- Consumes: exact branch source/control heads and shared `sync_run_id`.
- Produces: one BASS coordinator PR, one REC export/import PR, and one REI export/import PR.

- [ ] Open each PR against its exact policy branch.
- [ ] Include all peer PR URLs, source/base/head/tree identities, run ID, findings, tests, Dropbox path, Atlassian locators, and claim ceiling.
- [ ] Keep all three Draft and mergeable state read back without modifying scientific PRs.

### Task 6: Create append-only Dropbox recovery packet

**Files:**
- Create under `/bianchi/program-sync/BIANCHI-TRIREPO-SYNC-V2/2026-09-02/BOOTSTRAP-01/`:
  - `bass-export.json`, `rec-export.json`, `rei-export.json`
  - `bass-import-lock.json`, `rec-import-lock.json`, `rei-import-lock.json`
  - five generated output JSON files
  - `restore-map.json`
  - `publication-receipt.json`

**Interfaces:**
- Consumes: exact committed GitHub text and output identities.
- Produces: a non-overwriting reconstruction packet tied to the same run ID.

- [ ] Create missing parent folders one level at a time.
- [ ] Upload all text contracts without overwriting existing content.
- [ ] List the folder recursively and read back file metadata.
- [ ] Record every Dropbox path, file ID, size, and Git source locator.
- [ ] Do not call the backup byte-identical to Git objects; preserve the identity-domain distinction.

### Task 7: Synchronize Atlassian control plane

**Files:** Confluence and Jira records.

**Interfaces:**
- Consumes: final GitHub PRs, Dropbox receipt, and `sync_run_id`.
- Produces: one Confluence child page, one Jira automation task, and comments on BASS-16/17/18/19.

- [ ] Create `Bianchi Tri-Repository Synchronization Control Plane v2` under Confluence page `19464193`.
- [ ] Create one BASS Jira task under BASS-16 for the semantic inventory and scheduled-audit rollout.
- [ ] Add the same run ID and links to BASS-16, BASS-17, BASS-18, and BASS-19.
- [ ] Leave all existing official `Blocks` links unchanged.
- [ ] Read back the page/task/comments and record IDs.

### Task 8: Seal publication and verify completion boundaries

**Files:**
- Create in BASS: `docs/bianchi_program/TRIREPO_PUBLICATION_RECEIPT.json`
- Update in all repositories: `docs/bianchi_program/TRIREPO_SYNC_POINTER.json`

**Interfaces:**
- Consumes: GitHub, Dropbox, and Atlassian publication identities.
- Produces: final cross-plane locator receipt without changing the core audit run ID.

- [ ] Commit final pointers and publication receipt.
- [ ] Re-run GitHub Actions on every changed source/control head.
- [ ] Read back branches, commits, trees, PR state, Dropbox listing, and Atlassian records.
- [ ] Verify all recorded identities match their source systems.
- [ ] Report `DRIFT_DETECTED / BOOTSTRAP_NAMESPACE_ONLY` rather than a complete deduplication PASS.
- [ ] Preserve the next nodes `SYNC-MAP-01 -> SYNC-MAP-02 -> {SYNC-REC-01,SYNC-REI-01} -> SYNC-GATE-01`.
