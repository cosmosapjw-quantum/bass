# Codex handoff R3 — resume the existing AC-01 worktree

Do not restart implementation. The existing worktree already contains the seven
reported untracked files and valid RED/GREEN evidence. This run repairs only the
completion-binding contract and finishes WU-004-R3.

## Frozen identities

```text
repository              ~/bass
existing plan worktree  ~/bass-post-seal-plan-v3
existing impl worktree  ~/bass-ac01-impl-20260826
implementation base     d6a0b63fac09c3a6d0c9071206f0d51f01953341
implementation branch   agent/guard/bass-ac-01-artifact-identity-20260826
R3 plan branch          agent/audit/bass-ac01-nonselfreferential-binding-r3-20260826
attestation branch      agent/evidence/bass-ac-01-post-push-binding-20260826
```

## 1. Preflight without mutation

```bash
set -euo pipefail
REPO="$HOME/bass"
PLAN_WT="$HOME/bass-post-seal-plan-v3"
IMPL_WT="$HOME/bass-ac01-impl-20260826"
R3_BRANCH="agent/audit/bass-ac01-nonselfreferential-binding-r3-20260826"
IMPL_BRANCH="agent/guard/bass-ac-01-artifact-identity-20260826"
ATTEST_BRANCH="agent/evidence/bass-ac-01-post-push-binding-20260826"
BASE="d6a0b63fac09c3a6d0c9071206f0d51f01953341"

# Existing implementation state must match the blocker report.
test "$(git -C "$IMPL_WT" rev-parse HEAD)" = "$BASE"
test "$(git -C "$IMPL_WT" branch --show-current)" = "$IMPL_BRANCH"
test -z "$(git -C "$IMPL_WT" diff --name-only)"
test -z "$(git -C "$IMPL_WT" diff --cached --name-only)"

git -C "$REPO" fetch --no-tags origin "$R3_BRANCH"
R3_SHA="$(git -C "$REPO" rev-parse "origin/$R3_BRANCH^{commit}")"

test -z "$(git -C "$REPO" ls-remote --heads origin "$IMPL_BRANCH")"
test -z "$(git -C "$REPO" ls-remote --heads origin "$ATTEST_BRANCH")"
```

Do not touch the main checkout's untracked files. Do not delete or recreate the
implementation worktree.

## 2. Materialize R3 plan

Use a temporary detached worktree so the existing v3 plan worktree remains
available as predecessor evidence.

```bash
R3_WT="$HOME/bass-ac01-binding-plan-r3"
test ! -e "$R3_WT"
git -C "$REPO" worktree add --detach "$R3_WT" "$R3_SHA"
R3_ROOT="$R3_WT/verification/bass-ac01-nonselfreferential-binding-r3/20260826"
cd "$R3_ROOT"
sha256sum -c MANIFEST.sha256
PYTHONDONTWRITEBYTECODE=1 python3 scripts/verify_successor_package.py .
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_successor_contract -v
```

Require `PASS_AC01_NONSELFREFERENTIAL_BINDING_R3_PACKAGE`.

## 3. Preserve predecessor evidence and activate R3

Verify:

```text
old active contract SHA-256  88a21f1255d2a11bbb5ac2cd12abbb2d444c163dc2dceb8a0f4d9ec2e28ba01c
RED.log SHA-256              2da7607e2cda6129d51ee2002ac32f9a74fa1542de4e7cf73bddad0f606aeea6
GREEN.log SHA-256            245bba44e09a9e227b705172fa444ec919148d0e4aba2b88651b0c0abd29e048
```

Then:

```bash
EVID="$IMPL_WT/verification/bass-ac-01/20260826"
ACTIVE="$IMPL_WT/verification/audit-compiled/ACTIVE_WORK_UNIT.json"
mkdir -p "$EVID" "$(dirname "$ACTIVE")"
sha256sum "$ACTIVE" "$EVID/RED.log" "$EVID/GREEN.log"
cp "$R3_ROOT/WU-004-R3-NONSELFREFERENTIAL-BINDING.json" "$ACTIVE"
cp "$R3_ROOT/SPEC_CORRECTION.json" "$EVID/SPEC_CORRECTION.json"
```

## 4. Rerun GREEN evidence

Run all existing targeted, negative, self-test, and `tests/verification` checks.
Do not regenerate RED.log. Append the exact R3 rerun commands and results to
GREEN.log without deleting predecessor content.

## 5. Generate non-self-referential pre-commit receipt

Create `$EVID/RECEIPT.json` with schema
`bass-work-unit-precommit-evidence-v2`.

It MUST contain base, branch, contract SHA-256, commands, invariant results,
evidence keys, unresolved blockers, and
`binding_mode=separate_post_push_attestation`.

It MUST NOT contain `final_sha` or `attestation_commit_sha`.

Validate:

```bash
python3 "$R3_ROOT/scripts/verify_precommit_receipt.py"   --contract "$ACTIVE"   --receipt "$EVID/RECEIPT.json"
```

## 6. Final diff firewall and implementation commit

Generate `$EVID/DIFF_FIREWALL.log` after all candidate paths exist. Stage only
the R3 contract allowlist. Run the repository AC-01 allowed-diff verifier on the
staged/full candidate, `git diff --cached --check`, and a final changed-path
review. Preserve exact outputs in the log.

Create exactly one implementation commit:

```text
guard: add fail-closed BASS artifact identity verification
```

Push `agent/guard/bass-ac-01-artifact-identity-20260826` normally and require local HEAD equals the remote ref.

## 7. Separate post-push attestation

Create a clean attestation worktree from the implementation SHA:

```bash
SUBJECT="$(git -C "$IMPL_WT" rev-parse HEAD)"
ATTEST_WT="$HOME/bass-ac01-attestation-20260826"
test ! -e "$ATTEST_WT"
git -C "$REPO" worktree add -b "$ATTEST_BRANCH" "$ATTEST_WT" "$SUBJECT"
```

Generate exactly one file:

```text
verification/bass-ac-01/20260826/POST_PUSH_BINDING.json
```

Use schema `bass-post-push-binding-v1`. Its `subject_sha` is the implementation
SHA. Record subject tree/parent/message, receipt and diff-firewall Git blob SHAs
and SHA-256 values, and implementation remote readback. Do not put the future
attestation commit SHA in the JSON.

Commit exactly once:

```text
evidence: bind AC-01 implementation head for fresh review
```

Push `agent/evidence/bass-ac-01-post-push-binding-20260826` normally.

Run:

```bash
python3 "$R3_ROOT/scripts/verify_post_push_binding.py"   --repo "$REPO"   --binding "$ATTEST_WT/verification/bass-ac-01/20260826/POST_PUSH_BINDING.json"   --implementation-branch "$IMPL_BRANCH"   --attestation-branch "$ATTEST_BRANCH"
```

Require `PASS_POST_PUSH_BINDING`.

## 8. Stop

Report implementation SHA, attestation SHA, receipt/blob hashes, changed paths,
all GREEN/negative results, and unresolved blockers. Do not run WU-004R in this
context. Do not create a PR, merge, tag, or active-line bridge.
