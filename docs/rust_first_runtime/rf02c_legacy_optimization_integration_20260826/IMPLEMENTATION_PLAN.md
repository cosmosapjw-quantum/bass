# RF-02C Legacy Optimization Integration Implementation Plan

> **For agentic workers:** Execute one work unit at a time. The current handoff authorizes BASS-11 only. Later tasks open only through the verdict predicates in `WORK_UNITS.json`.

**Goal:** Close RF-02C with ancestry-correct terminal evidence, freeze the separate legacy optimization result, and integrate only a rederived RF-02C-native survivor after focused parity and bounded performance qualification.

**Architecture:** BASS-11 and BASS-12 are parallel identity-producing predecessors. BASS-13 is a read-only join that decides whether the legacy mechanism remains relevant. BASS-14 reimplements an approved mechanism from the frozen RF-02C head, and BASS-15 requalifies and integrates it through one stacked draft PR.

**Tech Stack:** Git, GitHub draft/stacked pull requests, Python 3, Rust 1.94.1, Cargo offline/locked mode, PyO3/maturin, pytest, Jira lifecycle tracking.

**Spec:** `docs/rust_first_runtime/rf02c_legacy_optimization_integration_20260826/WORK_UNITS.json`

## Global Constraints

- Preserve metric/sign/formula/state-order/tolerance and RF-02C V2 event/restart/history semantics.
- Use `source /mnt/data/rust_1_94_1_env.sh` before Rust commands; require Rust 1.94.1.
- Reuse unchanged PASS evidence. Never run the full suite merely for reassurance.
- The legacy lane is exploratory and may not mutate RF-02C.
- Performance acceptance requires the predeclared quiet-host predicate and exact identity binding.
- No merge, ready transition, RF-03+, Wolfram, GPU, formula promotion, or broad claim without explicit authorization.

---

### Task 1: BASS-11 — RF-02C terminal evidence closeout

**Files:**
- Existing dirty: `artifacts/rust_first_runtime/rf02c/EVIDENCE.json`
- Existing dirty: `artifacts/rust_first_runtime/rf02c/changed_paths.json`
- Existing dirty: `repro/native/**`
- Read: `docs/rust_first_runtime/rf02c_legacy_optimization_integration_20260826/CURRENT_STATE.json`
- Read: `docs/rust_first_runtime/rf02c_legacy_optimization_integration_20260826/WORK_UNITS.json`

**Interfaces:**
- Consumes: local RF-02C head `8770c766581f5ad6fa65712e33631fc3da98810c`
- Produces: terminal RF-02C remote head/tree, one stacked draft PR, workflow/artifact identities

- [ ] **Step 1: Verify exact local and remote identities without modifying the worktree**

```bash
git fetch origin
test "$(git branch --show-current)" = "agent/architecture/rust-first-rf02c-20260826-r1"
test "$(git rev-parse HEAD)" = "8770c766581f5ad6fa65712e33631fc3da98810c"
test "$(git rev-parse HEAD^{tree})" = "bb7fce7af4fb9ec2557320e9516595046372f025"
test "$(git rev-parse origin/agent/architecture/rust-first-rf02c-20260826-r1)" = "445e50184823e58401a8212ceaaf736e72bb35f2"
```

Expected: every command exits 0.

- [ ] **Step 2: Validate the complete dirty-path union, including untracked files**

```bash
{
  git diff --name-only
  git diff --cached --name-only
  git ls-files --others --exclude-standard
} | sed '/^$/d' | sort -u > /tmp/rf02c-terminal-dirty-paths.txt

python - <<'PY'
from pathlib import Path
paths = [p for p in Path("/tmp/rf02c-terminal-dirty-paths.txt").read_text().splitlines() if p]
exact = {
    "artifacts/rust_first_runtime/rf02c/EVIDENCE.json",
    "artifacts/rust_first_runtime/rf02c/changed_paths.json",
}
bad = [p for p in paths if p not in exact and not p.startswith("repro/native/")]
if bad or not exact.issubset(paths):
    raise SystemExit(f"dirty-path closure failure: missing={sorted(exact-set(paths))} bad={bad}")
print("\n".join(paths))
PY
```

Expected: only the two exact files and generated `repro/native/**` paths.

- [ ] **Step 3: Verify ancestry and post-review dirty closure**

```bash
PARENT="$(git rev-parse HEAD^)"
case "$PARENT" in
  80ab514*) ;;
  *) echo "unexpected implementation parent: $PARENT" >&2; exit 1 ;;
esac

git diff --check
test -z "$(git diff --cached --name-only)"
```

Expected: the bounded-review commit still has the implementation commit as its
parent, the unstaged evidence delta is whitespace-clean, and nothing is already
staged.

- [ ] **Step 4: Stage exactly the path union frozen in Step 2**

```bash
while IFS= read -r path
do
  git add -- "$path"
done < /tmp/rf02c-terminal-dirty-paths.txt

git diff --cached --check
git diff --cached --name-only | sort -u > /tmp/rf02c-terminal-staged-paths.txt
cmp /tmp/rf02c-terminal-dirty-paths.txt /tmp/rf02c-terminal-staged-paths.txt
```

Expected: the staged set is byte-for-byte the same path set approved in Step 2.

- [ ] **Step 5: Create the single authorized evidence-only commit**

```bash
git commit -m "chore(rf02c): bind terminal evidence and native delta"
test "$(git rev-parse HEAD^)" = "8770c766581f5ad6fa65712e33631fc3da98810c"
git diff-tree --no-commit-id --name-only -r HEAD | sort -u \
  > /tmp/rf02c-terminal-committed-paths.txt
cmp /tmp/rf02c-terminal-dirty-paths.txt \
    /tmp/rf02c-terminal-committed-paths.txt
test -z "$(git status --porcelain)"
```

Expected: one new commit, exact parent `8770c766...`, clean worktree.

- [ ] **Step 6: Push by ordinary fast-forward**

```bash
git push origin HEAD:agent/architecture/rust-first-rf02c-20260826-r1
test "$(git rev-parse HEAD)" = "$(git ls-remote origin refs/heads/agent/architecture/rust-first-rf02c-20260826-r1 | awk '{print $1}')"
```

Expected: no force option; remote equals local terminal head.

- [ ] **Step 7: Open one stacked draft RF-02C PR if absent**

```bash
gh pr list   --repo cosmosapjw-quantum/bass   --head agent/architecture/rust-first-rf02c-20260826-r1   --json number,state,isDraft,baseRefName,headRefName
```

If the returned array is empty:

```bash
cat > /tmp/rf02c-pr-body.md <<'EOF'
## Outcome

Closes RF-02C verified non-tilted scalar background execution: native
provenance/default dispatch, public typed routing, deterministic receipts,
checked projection, Rust-owned trajectories, exact events, Type-IX
transition/restart/history, and deterministic independent batches.

## Verification

The terminal evidence records the focused Rust/Python/hostile/native-delta
checks, randomized JVP receipt, changed-path closure, fresh no-index
no-override restore, and the Type-IX analytic root/restart comparator.

## Boundaries

Claim ceiling: `PASS_RF02C / PASS_SCOPED_BACKGROUND_EXECUTION`.
Performance and authority promotion remain `NONE`. Keep this PR draft and
unmerged. Do not start RF-03+, timing, GPU, Wolfram, or full-suite reassurance.
EOF

gh pr create   --repo cosmosapjw-quantum/bass   --draft   --base agent/audit/science-system-differential-20260826-r1   --head agent/architecture/rust-first-rf02c-20260826-r1   --title "runtime: close verified RF-02C background execution"   --body-file /tmp/rf02c-pr-body.md
```

Expected: one open draft PR whose base is the PR #33 branch.

- [ ] **Step 8: Read back exact remote state**

```bash
HEAD_SHA="$(git rev-parse HEAD)"
TREE_SHA="$(git rev-parse HEAD^{tree})"

gh pr view   --repo cosmosapjw-quantum/bass   --json number,state,isDraft,baseRefName,headRefName,headRefOid,url

RUN_ID=""
for _attempt in $(seq 1 12)
do
  RUN_ID="$(
    gh run list \
      --repo cosmosapjw-quantum/bass \
      --commit "$HEAD_SHA" \
      --limit 1 \
      --json databaseId,headSha \
      --jq '.[0].databaseId // empty'
  )"
  test -n "$RUN_ID" && break
  sleep 5
done

test -n "$RUN_ID"
gh run watch "$RUN_ID" --repo cosmosapjw-quantum/bass --exit-status
gh run view \
  "$RUN_ID" \
  --repo cosmosapjw-quantum/bass \
  --json status,conclusion,headSha,url,jobs
gh api "repos/cosmosapjw-quantum/bass/actions/runs/$RUN_ID/artifacts"
printf 'head=%s\ntree=%s\nrun=%s\n' "$HEAD_SHA" "$TREE_SHA" "$RUN_ID"
```

Expected: exact terminal head/tree, open draft PR, and the RF-02C workflow/artifact readback.
Stop after reporting BASS-11.

---

### Task 2: BASS-12 — Freeze the separate legacy optimization result

**Files:**
- Read: `artifacts/performance/EVIDENCE.json`
- Read: `artifacts/performance/HANDOFF.md`
- Candidate: exact paths recorded by the live optimization branch
- Test: focused legacy correctness paths recorded in its evidence

**Interfaces:**
- Consumes: `agent/recovery/measured-performance-20260824-r1@4c615057...`
- Produces: exact candidate branch/head/tree/payload and one bounded verdict

- [ ] Freeze the live candidate branch and payload identities before measurement.
- [ ] Verify focused correctness and exact output identity using only frozen commands.
- [ ] Require two quiet-host snapshots ten seconds apart before paired timing.
- [ ] Emit exactly one BASS-12 terminal verdict and preserve exact evidence.
- [ ] Do not touch the RF-02C worktree or claim RF-02C compatibility.

---

### Task 3: BASS-13 — Read-only adoption decision

**Files:**
- Read: terminal RF-02C evidence/PR from BASS-11
- Read: terminal legacy candidate evidence from BASS-12
- Create only if required by repository convention: bounded decision receipt

**Interfaces:**
- Consumes: exact terminal identities from BASS-11 and accepted BASS-12
- Produces: `REIMPLEMENT_ON_RF02C`, `REJECT_AS_OBSOLETE_OR_INCOMPATIBLE`, or `DEFER_WITH_EXPLICIT_MISSING_INPUT`

- [ ] Reconstruct the affected equation, ownership, route, state, output, and benchmark contracts.
- [ ] Verify whether the legacy hotspot still exists in RF-02C.
- [ ] Compare semantics and ABI without code mutation.
- [ ] Emit exactly one verdict and stop.

---

### Task 4: BASS-14 — RF-02C-native reimplementation

**Files:**
- Create/modify only paths named by the BASS-13 decision
- Test: focused RF-02C correctness, hostile negative, determinism, and integration paths
- Evidence: bounded changed-path and result receipt

**Interfaces:**
- Consumes: exact BASS-11 terminal RF-02C head and BASS-13 mechanism
- Produces: one frozen RF-02C-native candidate branch/head/tree

- [ ] Create a new branch from the live terminal RF-02C head.
- [ ] Write focused failing tests.
- [ ] Implement the smallest RF-02C-native mechanism.
- [ ] Run only affected tests and comparators.
- [ ] Perform one bounded review and at most one reproduced P0/P1 repair.
- [ ] Freeze exact candidate identity without a speedup claim.

---

### Task 5: BASS-15 — Requalification and integration

**Files:**
- Read: frozen pre-optimization RF-02C evidence
- Read: BASS-14 candidate evidence
- Test/benchmark: affected correctness and frozen quiet-host performance commands
- Deliver: one stacked draft PR

**Interfaces:**
- Consumes: PASS RF-02C-native candidate
- Produces: accepted/rejected/blocked qualification and, only on PASS, an integration PR

- [ ] Re-run the smallest affected correctness and negative set.
- [ ] Verify output/trajectory/restart/history/thread determinism where affected.
- [ ] Run the predeclared quiet-host paired benchmark and resource gate.
- [ ] Bind exact source, binary, input, host, affinity, threads, and commands.
- [ ] Reject on parity or benefit failure without altering RF-02C.
- [ ] On PASS, push one candidate branch and open one stacked draft PR.
- [ ] Integrate only after explicit merge approval.
