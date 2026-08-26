# Codex Handoff — Execute BASS-11 Only

```text
PROCESS_DRIFT_DETECTED
STOPPING META-WORK
RETURNING TO USER OBJECTIVE
```

## Task

Close the already-implemented and reviewed RF-02C lane by committing only its
already-generated terminal evidence/native delta, pushing by ordinary
fast-forward, opening one stacked draft PR, and reading back exact remote
identity.

Do not execute BASS-12, BASS-13, BASS-14, BASS-15, RF-03+, performance,
Wolfram, GPU, full-suite reassurance, merge, or ready transition in this run.

## Package authority

```text
repository: cosmosapjw-quantum/bass
package branch: agent/plans/rf02c-legacy-optimization-integration-20260826-r1
package path: docs/rust_first_runtime/rf02c_legacy_optimization_integration_20260826
package base at compilation: 445e50184823e58401a8212ceaaf736e72bb35f2
```

Read the package without switching or cleaning the dirty RF-02C worktree:

```bash
git fetch origin

PKG_REF="origin/agent/plans/rf02c-legacy-optimization-integration-20260826-r1"
PKG_PATH="docs/rust_first_runtime/rf02c_legacy_optimization_integration_20260826"
PKG_TMP="$(mktemp -d)"

for f in   README.md   CURRENT_STATE.json   WORK_UNITS.json   ACCEPTANCE_MATRIX.json   IMPLEMENTATION_PLAN.md   CODEX_HANDOFF.md   validate_package.py   MANIFEST.sha256
do
  mkdir -p "$PKG_TMP/$(dirname "$f")"
  git show "$PKG_REF:$PKG_PATH/$f" > "$PKG_TMP/$f"
done

(
  cd "$PKG_TMP"
  sha256sum -c MANIFEST.sha256
  python validate_package.py
)
```

## Required worktree identity

Continue in the existing intentionally dirty RF-02C worktree:

```text
branch: agent/architecture/rust-first-rf02c-20260826-r1
required local HEAD: 8770c766581f5ad6fa65712e33631fc3da98810c
required local tree: bb7fce7af4fb9ec2557320e9516595046372f025
required remote HEAD before push: 445e50184823e58401a8212ceaaf736e72bb35f2
implementation commit: 80ab514
bounded-review repair commit: 8770c76
```

Never run `git reset`, `git clean`, `git stash`, branch switching, amend,
rebase, squash, or force-push.

## Authorized mutation

Exactly one evidence-only third commit is authorized. Its parent must be
`8770c766581f5ad6fa65712e33631fc3da98810c`.

Allowed dirty paths are:

```text
artifacts/rust_first_runtime/rf02c/EVIDENCE.json
artifacts/rust_first_runtime/rf02c/changed_paths.json
repro/native/**
```

Use the union of tracked unstaged, staged, and untracked paths. Do not repeat
the earlier `git diff --name-only` mistake that omits untracked files.

The commit message is:

```text
chore(rf02c): bind terminal evidence and native delta
```

No implementation, formula, tolerance, reference, state-order, public-route,
test, performance, or authority byte may change.

## Execution

Follow Task 1 in `IMPLEMENTATION_PLAN.md` exactly.

After the commit:

1. verify the parent and clean worktree;
2. push by ordinary fast-forward;
3. open one draft PR from
   `agent/architecture/rust-first-rf02c-20260826-r1` to
   `agent/audit/science-system-differential-20260826-r1` if absent;
4. read back exact head/tree, PR number/base/head/draft state, changed paths,
   workflow run, and artifact identity;
5. stop.

Reuse the reported targeted GREEN evidence if controlling bytes are unchanged:

```text
Rust RF-02C selector: 49 passed
Python primary: 40 passed
hostile/negative: 13 passed, 27 deselected
native-delta tooling: 5 passed
randomized JVP: 250 PASS
changed-path closure: 45/45
fresh no-index/no-override production trajectory and batch: verified
Type-IX root error: 1.869836729895269e-9
root budget: 2.84536516942666e-9
restart time/state bytes: identical
```

Do not rerun those lanes for reassurance. Run only checks needed to prove that
the evidence-only commit did not alter their controlling bytes.

## Block policy

`BLOCK_NOW` only for:

- local or remote identity mismatch;
- dirty path outside the authorized closure;
- staged source/test/workflow mutation;
- evidence/native digest mismatch;
- non-fast-forward remote movement;
- PR base/head mismatch;
- false success or destructive behavior.

Do not stop for style, publication-grade concerns, another audit, or possible
future hardening.

## Final report

Use exactly:

```text
STATUS
ACTUAL PROGRESS
VERIFIED
DEFERRED
BLOCKERS
NEXT
```

`NEXT` must contain exactly one action. On success, it is:

```text
Update BASS-11 with the terminal RF-02C remote head/tree, draft PR, workflow,
and artifact identities; then wait for BASS-12's exact terminal candidate
identity before opening BASS-13.
```
