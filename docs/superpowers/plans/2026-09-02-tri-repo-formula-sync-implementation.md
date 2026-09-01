# Tri-Repository Formula Authority Synchronization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a fail-closed BASS/REC/REI formula-authority registry, deterministic DAG compiler, repository-local lane manifests, and synchronized GitHub/Dropbox/Atlassian receipts.

**Architecture:** BASS owns the canonical registry and compiler. Each repository owns only its lane manifest and exact local authority/export state. The compiler detects duplicate authority, stale imports, missing durability, dependency cycles, and weakest-upstream claim ceilings; it generates a proposed DAG and mutation plan but never auto-promotes science or merges code.

**Tech Stack:** Node.js 20 standard library, JSON, GitHub Actions, GitHub/Dropbox/Atlassian REST-compatible payloads, existing Wolfram/xAct authority receipts.

**Spec:** `docs/superpowers/specs/2026-09-02-tri-repo-formula-sync-design.md`

## Global Constraints

- Formula/source authority is GitHub exact objects; Dropbox is recovery storage; Atlassian is workflow/ownership state.
- Every formula family has exactly one authority owner.
- Scientific PASS, provider export, Jira Done, PR ready, and merge are never automatically applied.
- Missing credentials or missing receipts are fail-closed states, not PASS.
- Current scientific blockers and claim ceilings must remain unchanged.
- No access token, email credential, or API secret may be committed.

---

### Task 1: Commit the RED contract

**Files:**
- Create: `coordination/tri_repo_sync/tests/compile-dag.test.mjs`
- Create: `.github/workflows/tri-repo-sync-ci.yml`
- Create: `docs/superpowers/specs/2026-09-02-tri-repo-formula-sync-design.md`
- Create: `docs/superpowers/plans/2026-09-02-tri-repo-formula-sync-implementation.md`

**Interfaces:**
- Consumes: exact BASS ALG-01 head `c35177409909b7eef0f5c99c0c61a456b5e55117`.
- Produces: executable tests importing `compileControlPlane` and `canonicalHash` from `coordination/tri_repo_sync/compile-dag.mjs`.

- [ ] **Step 1: Commit tests before the implementation module exists.**
- [ ] **Step 2: Push the branch and observe CI fail with `ERR_MODULE_NOT_FOUND` for `compile-dag.mjs`.**
- [ ] **Step 3: Record the failing workflow run ID, head SHA, and failure classification in `TDD_RED_RECEIPT.json`.**

### Task 2: Implement the deterministic compiler

**Files:**
- Create: `coordination/tri_repo_sync/compile-dag.mjs`
- Create: `coordination/tri_repo_sync/schemas/formula-authority-registry.schema.json`
- Create: `coordination/tri_repo_sync/schemas/lane-manifest.schema.json`
- Create: `coordination/tri_repo_sync/schemas/compiled-dag.schema.json`

**Interfaces:**
- Consumes: registry object plus an array of lane-manifest objects.
- Produces:
  - `canonicalHash(value) -> lowercase SHA-256 string`;
  - `compileControlPlane(registry, manifests) -> compiled DAG object`;
  - CLI arguments `--registry`, repeated `--manifest`, and `--output`.

- [ ] **Step 1: Implement recursive canonical key ordering with array order preserved.**
- [ ] **Step 2: Implement registry and manifest structural validation.**
- [ ] **Step 3: Detect duplicate authorities and owner mismatch.**
- [ ] **Step 4: Detect cycles in family prerequisites.**
- [ ] **Step 5: Evaluate maturity, promotion evidence, and automatic states.**
- [ ] **Step 6: Detect stale imported authority commits.**
- [ ] **Step 7: Emit deterministic ready/blocked/non-durable/invalid sets and `manual_promotion_required: true`.**
- [ ] **Step 8: Run `node --test coordination/tri_repo_sync/tests/compile-dag.test.mjs`; require zero failures.**

### Task 3: Publish the canonical registry and BASS lane

**Files:**
- Create: `coordination/tri_repo_sync/FORMULA_FAMILY_REGISTRY.json`
- Create: `coordination/tri_repo_sync/LANE_MANIFEST.json`
- Create: `coordination/tri_repo_sync/README.md`
- Create: `coordination/tri_repo_sync/CURRENT_COMPILED_DAG.json`
- Create: `coordination/tri_repo_sync/SYNC_POLICY.json`

**Interfaces:**
- Consumes: BASS W0/W1 and ALG-01 exact receipts; REC PR #47 and REI PR #32 exact heads.
- Produces: canonical owner partition and current BASS state.

- [ ] **Step 1: Assign each formula family exactly one owner.**
- [ ] **Step 2: Mark BG-02 as `validated_non_durable`, not PASS.**
- [ ] **Step 3: Pin REC and REI imports to the exact observed heads.**
- [ ] **Step 4: Compile the three fixture/current manifests and commit the deterministic DAG.**
- [ ] **Step 5: Re-run tests and byte-for-byte deterministic compilation.**

### Task 4: Publish REC lane manifest

**Files:**
- Create in `rec_bianchi`: `coordination/tri_repo_sync/LANE_MANIFEST.json`
- Create in `rec_bianchi`: `coordination/tri_repo_sync/README.md`

**Interfaces:**
- Consumes: REC PR #47 head `c4bf37d7271caf651bca41b6eaab8caff436452b` and BASS registry pin.
- Produces: REC-owned authority state and explicit BASS imports.

- [ ] **Step 1: Create a child branch from the exact PR #47 head.**
- [ ] **Step 2: Declare REC authority only for recombination formula families.**
- [ ] **Step 3: Preserve `SOURCE_DEFINED_26_DIRECTION_FACE_RECONSTRUCTION_ABSENT` and `NO_PASS_REC_PHYSICAL_SPLIT`.**
- [ ] **Step 4: Open a Draft PR targeting the PR #47 branch.**
- [ ] **Step 5: Read back branch, commit, tree, PR head, and committed files.**

### Task 5: Publish REI lane manifest

**Files:**
- Create in `rei_bianchi`: `coordination/tri_repo_sync/LANE_MANIFEST.json`
- Create in `rei_bianchi`: `coordination/tri_repo_sync/README.md`

**Interfaces:**
- Consumes: REI PR #32 head `f4eb2c893ce6449f8899ab6f02c83421fc7c7019`, REC provider state, and BASS registry pin.
- Produces: REI-owned thermochemistry/OTS state and explicit BASS/REC imports.

- [ ] **Step 1: Create a child branch from the exact PR #32 head.**
- [ ] **Step 2: Declare REI authority only for late-time thermochemistry, OTS, opacity/source, interval, and export families.**
- [ ] **Step 3: Preserve `UNDECLARED_IMPORT: ntpath`, `STOP_INVALID`, and `NO_PASS_FIRST_CANONICAL_INTERVAL`.**
- [ ] **Step 4: Open a Draft PR targeting the PR #32 branch.**
- [ ] **Step 5: Read back branch, commit, tree, PR head, and committed files.**

### Task 6: Add scheduled audit automation

**Files:**
- Create: `.github/workflows/tri-repo-sync-audit.yml`
- Create: `coordination/tri_repo_sync/fetch-lanes.mjs`
- Create: `coordination/tri_repo_sync/render-sync-plan.mjs`

**Interfaces:**
- Consumes: public REC/REI raw manifest URLs and local BASS manifest/registry.
- Produces: compiled DAG artifact, drift receipt, and non-mutating proposed publication payloads.

- [ ] **Step 1: Trigger on manifest changes, manual dispatch, and cron `15 18 * * *`.**
- [ ] **Step 2: Fetch exact configured branch manifests and verify expected repository names.**
- [ ] **Step 3: Compile and compare with the committed snapshot.**
- [ ] **Step 4: Fail on duplicate authority, cycle, stale required import, or unexpected claim promotion.**
- [ ] **Step 5: Upload `COMPILED_DAG.json`, `SYNC_RECEIPT.json`, and destination payloads as workflow artifacts.**
- [ ] **Step 6: Keep cross-system mutation disabled unless all required secrets and `SYNC_APPLY=true` are present.**

### Task 7: Dropbox stage snapshot

**Files:**
- Create in Dropbox: `/bianchi/control-plane/BASS-REC-REI-FORMULA-SYNC/2026-09-02/SYNC_01/`
- Include: registry, three manifests, compiled DAG, restore map, GitHub readback, and backup receipt.

**Interfaces:**
- Consumes: exact committed GitHub text and object IDs.
- Produces: versioned recovery mirror with Dropbox file IDs and content metadata.

- [ ] **Step 1: Create the versioned folder hierarchy.**
- [ ] **Step 2: Upload exact UTF-8 snapshot files.**
- [ ] **Step 3: Read back folder and every file.**
- [ ] **Step 4: Record Dropbox IDs and paths in the backup receipt.**
- [ ] **Step 5: Do not call Dropbox formula authority.**

### Task 8: Atlassian synchronization

**Files/objects:**
- Create: one Confluence child page under the tri-repository control plane.
- Create: one Jira task for synchronization governance.
- Link: Jira task with BASS-17, BASS-18, and BASS-19 using `Relates`.
- Append: comments to BASS-16/17/18/19 and the relevant Confluence parent pages.

**Interfaces:**
- Consumes: compiled DAG and exact GitHub/Dropbox receipts.
- Produces: workflow mirror and proposed transitions, without changing scientific issue states.

- [ ] **Step 1: Create the control-plane receipt page.**
- [ ] **Step 2: Create the Jira synchronization task.**
- [ ] **Step 3: Add `Relates` links to BASS-17/18/19.**
- [ ] **Step 4: Mirror current blockers and the next ready node.**
- [ ] **Step 5: Read back page, issue, and links.**

### Task 9: Final verification and publication

**Files:**
- Create: `coordination/tri_repo_sync/SYNC_01_RECEIPT.json`
- Create: `coordination/tri_repo_sync/GITHUB_READBACK.json`
- Update: Draft PR descriptions in all three repositories.

**Interfaces:**
- Consumes: CI runs, exact GitHub readback, Dropbox readback, Atlassian readback.
- Produces: scope-limited `PASS_SYNC01_CONTROL_PLANE` or a fail-closed blocker.

- [ ] **Step 1: Verify all tests and compiled output on the committed BASS head.**
- [ ] **Step 2: Verify all three manifest commits and trees.**
- [ ] **Step 3: Verify Dropbox snapshot completeness.**
- [ ] **Step 4: Verify Atlassian mirror and unchanged scientific statuses/dependencies.**
- [ ] **Step 5: Publish exact claim boundary and next node.**

## Completion claim

Only the following may be claimed after Task 9 passes:

```text
PASS_SYNC01_UNIQUE_FORMULA_AUTHORITY_REGISTRY
PASS_SYNC01_DETERMINISTIC_DAG_COMPILER
PASS_SYNC01_THREE_LANE_MANIFESTS
PASS_SYNC01_GITHUB_DROPBOX_ATLASSIAN_SNAPSHOT
```

The following remain separately gated:

```text
BG_02_DURABLE_PROMOTION
REC_PHYSICAL_FACE
REC_PROVIDER_EXPORT
REI_RUNTIME_BRIDGE
REI_FIRST_CANONICAL_INTERVAL
REI_PROVIDER_EXPORT
BASS_REC_REI_INTEGRATION
ARBITRARY_L_COMPILER
SCIENCE_VALIDITY
```