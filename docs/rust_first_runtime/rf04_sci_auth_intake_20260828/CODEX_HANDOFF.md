# Codex Handoff — SCI-AUTH-04 then RF-04

```text
PROCESS_DRIFT_DETECTED
STOPPING META-WORK
RETURNING TO USER OBJECTIVE
```

## Entry

```text
repository: cosmosapjw-quantum/bass
RF-03 branch: agent/architecture/rust-first-rf03-20260828-r2
RF-03 HEAD: 6e53664d56694f7a7ad5f65be262302d5c8866b2
RF-03 tree: bb743717e8115821d72268d8384dc5cc7cc11975
RF-03 PR: #45 OPEN / DRAFT / UNMERGED

SCI-AUTH-04 exact base:
agent/architecture/rust-first-rf02b-20260826-r1
0563c080e54fcd90d6160bec35e4f20d240d8d2e
tree 40ae99f9e7465d6332e98b65a5269a1f71eadfb5
PR #32

exact next action: SCI-AUTH-04
current claims: PASS_RF03; NO PASS_SCI_AUTH_04; NO PASS_RF04
```

Read `PACKAGE.json`, `CURRENT_STATE.json`, `DAG.json`, `WORK_UNITS.json`,
`ACCEPTANCE_MATRIX.json`, `SOURCE_INVENTORY.json`, and
`IMPLEMENTATION_PLAN.md` once.

## Preserve local state

Use separate isolated worktrees. Do not clean/reset/stash/switch an occupied
worktree, discard untracked files, amend/rebase/squash, or force-push.

## Execute SCI-AUTH-04

Create `agent/authority/sci-auth-04-20260828-r1` from exact `0563c080e54fcd90d6160bec35e4f20d240d8d2e`.
Mutate only its compiled authority allowlist. Freeze coefficients/generated
source/runtime bytes. Create the verifier and hostile scope fixtures first,
run only targeted checks, one review, at most one repair, ordinary push and one
draft authority PR. Read back exact evidence.

If and only if terminal state is `PASS_SCI_AUTH_04_VALIDATOR`, proceed in the
same orchestration run.

## Execute RF04-INTAKE-00 and RF-04

Read-only verify exact RF-03 and authority receipts. Create
`agent/architecture/rust-first-rf04-20260828-r1` from exact `6e53664d56694f7a7ad5f65be262302d5c8866b2`.

Follow the genuine RED → implementation → targeted proof → four diagnostic
readbacks → hostile mutations → PHYS-MATH → PHYS-MATH-CODE → at most one
repair → native evidence → draft PR sequence in `IMPLEMENTATION_PLAN.md`.

Do not invent formulas or broaden capability claims. Existing Rust kinetic
code must be reused when correct; implement only actual ownership/runtime gaps.
No Python production inner loop or silent fallback.

## Forbidden

- BASS-12 through BASS-15 optimization bytes
- full-suite reassurance
- timing, GPU, Wolfram
- RF-05+
- merge or ready transition
- performance or scientific promotion

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

Distinguish `PASS_SCI_AUTH_04_VALIDATOR` from `PASS_RF04`. On successful RF-04
delivery, `NEXT` is human review and CI observation of the draft PR; do not
merge.
