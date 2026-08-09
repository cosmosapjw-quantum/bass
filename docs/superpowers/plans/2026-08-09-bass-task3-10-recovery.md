# BASS Task 3–10 Recovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Preserve every currently recoverable BASS artifact and its evidence classification on `agent/longrun-checkpoints` without promoting transcript-only Task 3–10 claims.

**Architecture:** The repository keeps four provenance lanes separate: current recovery evidence under `docs/recovery/`, the immutable H0/H1 harness under `harness/`, the incomplete historical Rust/Python overlay under `recovered_sources/legacy_partial/`, and machine-checkable hashes under `manifests/`. No recovered partial file is installed into a production `bianchi/full` package.

**Tech Stack:** Git, SHA-256, ZIP/TAR validation, Python 3 standard library, Rust source preservation, Markdown/TSV/JSON evidence records.

## Global Constraints

- Preserve `/workspace/scratch/5f62256bcea8/project_sources/` byte-for-byte and never commit the 192 MB Rust distribution or the xAct vendor archive.
- Treat Task 5–10 short SHAs as evidence locators unless a Git object resolves locally or remotely.
- Never label the harness baseline or legacy partial overlay as the lost Task 3–10 production tree.
- Use only fast-forward publication from remote baseline `d9e5ba7577ccb05b648b11ea7ac991bf6e09d8b9`; never force-push.
- Record every copied regular file by relative path, byte count, and SHA-256.

---

### Task 1: Capture the recovery inventory

**Files:**
- Create: `docs/recovery/RECOVERY_INVENTORY_20260809.tsv`
- Create: `docs/recovery/RECOVERY_REPORT_20260809.md`
- Create: `docs/recovery/GIT_OBJECT_SEARCH_20260809.tsv`
- Create: `docs/recovery/TRANSCRIPT_TASK3_10_STATE_20260809.md`
- Create: `manifests/PROJECT_SOURCE_SHA256_20260809.txt`

**Interfaces:**
- Consumes: the current filesystem, process snapshot, attachment metadata, local Git stores, and GitHub branch/commit responses.
- Produces: evidence records used to decide what can be materialized in Tasks 2 and 3.

- [x] **Step 1: Hash the 15 attached inputs**

Run: `sha256sum ../project_sources/*`

Expected: exactly 15 canonical named inputs, including BASS bundle SHA `79c36566c958cc260adf82a2795a992fe7723c9d37611ab7b8d94de73fe831fa`.

- [x] **Step 2: Record Git-object resolution**

Record local and remote outcomes for `3347547`, `eaf13af`, `4e1a3b6`, `54fb3bf`, `29327f9`, `e993691`, `6d786e1`, and `c3d45f3`.

Expected: unresolved locators remain `TRANSCRIPT_ONLY`; they are not fabricated as commits.

- [x] **Step 3: Write the evidence-classified report**

The report must use `DURABLE_VERIFIED`, `PARTIALLY_RECOVERED`, `RECONSTRUCTED`, `TRANSCRIPT_ONLY`, and `MISSING`, and must disclose the GitHub tag/dangling-object and block-level undelete limitations.

### Task 2: Materialize the immutable harness baseline

**Files:**
- Create: `harness/BASS_v1_background_highl_harness/**`
- Create: `docs/recovery/HARNESS_RELOCATION_CHECK_20260809.md`
- Create: `manifests/HARNESS_RECOVERED_SHA256_20260809.txt`

**Interfaces:**
- Consumes: nested archive `BASS_v1_background_highl_harness_v0.1.0.zip`, expected SHA `cd80b4e9ee4a0d292e99bba7fffd60bd313d765e4510498ae1c8e99ec0ff3b64`.
- Produces: a byte-preserved 72-entry H0/H1 harness tree, explicitly not a solver.

- [x] **Step 1: Validate archive safety and identity**

Check every member for absolute paths, `..`, symlinks, duplicate names, and special files; then stream-hash the nested ZIP.

Expected: safe archive and exact expected SHA.

- [x] **Step 2: Extract only the immutable harness ZIP**

Extract into `harness/BASS_v1_background_highl_harness/` without importing cache files or changing original attachments.

- [x] **Step 3: Verify the internal manifest**

Run from the harness root: `sha256sum -c audit/FILE_MANIFEST.sha256`.

Expected: every governed file reports `OK`.

- [x] **Step 4: Run the relocated harness checks**

Run: `python3 tools/validate_harness.py --root .` and `python3 -m unittest -v`.

Expected: current-run results are recorded as `RECONSTRUCTED`; historical H0/H1 receipts remain separate.

### Task 3: Preserve the historical partial solver overlay

**Files:**
- Create: `recovered_sources/legacy_partial/bianchirustcoreRDAGcomplete/**`
- Create: `recovered_sources/legacy_partial/README.md`
- Create: `manifests/LEGACY_PARTIAL_SHA256_20260809.txt`

**Interfaces:**
- Consumes: `bianchirustcoreRDAGcomplete.tar.gz`, expected SHA `53597fb5dd2aee25a75bfedc2f001574db90b1a5580ad60410b575f76c8aa9fb`.
- Produces: the exact 18-file Rust/Python/test overlay in a quarantine namespace.

- [x] **Step 1: Validate TAR safety and identity**

Check path traversal, links, special members, duplicates, gzip integrity, and the outer SHA.

- [x] **Step 2: Extract into the quarantine namespace**

Do not place `bianchi/backend.py`, `_rustcore/`, or tests at repository root.

- [x] **Step 3: Hash every extracted regular file**

Expected: manifest rows cover all 18 regular members and reproduce their streamed archive content.

- [x] **Step 4: Document execution limits**

State that the complete Python baseline, dependency environment, and lost `bianchi/full` modules are absent, so embedded test/performance claims are not inherited.

### Task 4: Verify and publish the checkpoint

**Files:**
- Modify: `docs/recovery/CURRENT_RUNTIME_CHECKPOINT_20260809.md`
- Create: `manifests/RECOVERY_TREE_SHA256_20260809.txt`

**Interfaces:**
- Consumes: Tasks 1–3 and remote head `d9e5ba7577ccb05b648b11ea7ac991bf6e09d8b9`.
- Produces: one fast-forward recovery commit on `agent/longrun-checkpoints`, followed by remote SHA verification.

- [x] **Step 1: Validate manifests and archive parity**

Run all SHA checks and compare each extracted file to bytes streamed directly from its source archive.

Expected: the final recovery-tree manifest contains decimal byte count, SHA-256, and path
for every recovery file except itself; missing, extra, size mismatch, and hash mismatch are zero.

- [x] **Step 2: Inspect scope before staging**

Run: `git status --short`, `git diff --check`, and an explicit changed-path review.

Expected: only the paths named in this plan changed.

- [x] **Step 3: Run available checks**

Run harness manifest validation, validator, unit suite, Python compilation for recovered Python files, and `cargo metadata --no-deps` if the installed Cargo version can parse the crate without network access.

- [ ] **Step 4: Commit intentionally**

Run: `git commit -m "chore: preserve recoverable BASS state"` after explicitly staging only the planned paths.

- [ ] **Step 5: Publish and verify**

Fast-forward `agent/longrun-checkpoints`, then independently fetch the remote commit and representative files. Record local SHA, remote SHA, test results, and clean worktree state.
