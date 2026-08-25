# Codex handoff — execute only WU-004 AC-01 in this context

Repository: `~/bass`

Plan branch:

```text
agent/audit/bass-post-seal-audit-compiled-exec-plan-v3-20260826
```

Exact implementation base:

```text
d6a0b63fac09c3a6d0c9071206f0d51f01953341
```

Scientific seal branch:

```text
agent/verify/bass-close-00r-fresh-2b3-reproduction-20260825
```

## 1. Create isolated plan and implementation worktrees

```bash
set -euo pipefail
cd ~/bass

test -z "$(git status --porcelain)" || {
  git status --short
  echo "BLOCKED: canonical checkout is dirty" >&2
  exit 1
}

git fetch origin \
  agent/audit/bass-post-seal-audit-compiled-exec-plan-v3-20260826 \
  agent/verify/bass-close-00r-fresh-2b3-reproduction-20260825

PLAN_WT=../bass-post-seal-plan-v3
IMPL_WT=../bass-ac01-impl-20260826
IMPL_BR=agent/guard/bass-ac-01-artifact-identity-20260826

test ! -e "$PLAN_WT"
test ! -e "$IMPL_WT"
test -z "$(git ls-remote --heads origin "$IMPL_BR")"

git worktree add --detach "$PLAN_WT" "origin/agent/audit/bass-post-seal-audit-compiled-exec-plan-v3-20260826"
git worktree add -b "$IMPL_BR" "$IMPL_WT" d6a0b63fac09c3a6d0c9071206f0d51f01953341

PLAN_SOURCE="$PLAN_WT/verification/bass-post-seal-audit-compiled-exec-plan-v3/20260826"
IMPL_ROOT="$IMPL_WT"
ACTIVE_CONTRACT="$IMPL_ROOT/verification/audit-compiled/ACTIVE_WORK_UNIT.json"

if [[ -f "$PLAN_SOURCE/scripts/verify_compiled_package.py" ]]; then
  PLAN_ROOT="$PLAN_SOURCE"
else
  test -x "$PLAN_SOURCE/UNPACK_AND_VERIFY.sh"
  PLAN_TMP="$(mktemp -d)"
  "$PLAN_SOURCE/UNPACK_AND_VERIFY.sh" "$PLAN_TMP"
  PLAN_ROOT="$PLAN_TMP/BASS_POST_SEAL_AUDIT_COMPILED_EXEC_PLAN_V3_20260826"
fi
```

## 2. Verify the plan before any code edit

```bash
cd "$PLAN_ROOT"
sha256sum -c MANIFEST.sha256
PYTHONDONTWRITEBYTECODE=1 python scripts/verify_compiled_package.py .
PYTHONDONTWRITEBYTECODE=1 python -m unittest tests.test_compiled_package -v
```

Require:

```text
BASS_POST_SEAL_AUDIT_COMPILED_PLAN_V3_VERIFY_PASS
```

Read, in order:

```text
CURRENT_STATE.json
SOURCE_PRECEDENCE.json
P0_P1_POLICY.md
AUDIT_COMPILED_EXECUTION_CONTRACT.md
DAG.json
WORK_UNITS/WU-004-AC01-IDENTITY-GUARD.json
FINAL_DIFFERENTIAL_AUDIT_CONTRACT.json
```

## 3. Freeze the active contract in the implementation branch

```bash
mkdir -p "$IMPL_ROOT/verification/audit-compiled"
cp "$PLAN_ROOT/WORK_UNITS/WU-004-AC01-IDENTITY-GUARD.json" "$ACTIVE_CONTRACT"
cmp "$PLAN_ROOT/WORK_UNITS/WU-004-AC01-IDENTITY-GUARD.json" "$ACTIVE_CONTRACT"
sha256sum "$ACTIVE_CONTRACT"
```

## 4. Primary rule

Do not ask the user questions. Do not guess across a specification boundary.
Inspect repository authority first. If observable semantics remain unresolved,
stop with `BLOCKED_BY_UNRESOLVED_SPEC` and preserve exact conflicting evidence.

Implement **only WU-004** using test-first development. Do not execute WU-001,
WU-002, WU-003, WU-004R, WU-005, or WU-006 in this context.

## 5. Required TDD loop

1. Confirm exact base and clean worktree.
2. Write all specified failing tests.
3. Run each test to RED and preserve `verification/bass-ac-01/20260826/RED.log`.
4. Implement the minimal pure-stdlib verifier.
5. Implement the exact-base allowed-diff firewall.
6. Document identity classes A/B/C/D:
   - immutable source/input;
   - deterministic generated evidence;
   - scientific/numerical content equivalence;
   - packaging/build metadata.
7. Run targeted and negative tests to GREEN.
8. Run only `tests/verification`; do not run unrelated historical campaigns.
9. Generate the machine receipt and allowed-diff log.
10. Self-review the diff.
11. Commit exactly once and push normally.
12. Stop. Do not perform WU-004R in the same context.

Commit message:

```text
guard: add fail-closed BASS artifact identity verification
```

## 6. Hard bans

Do not modify scientific source, sealed content, historical evidence, expected
hashes, tolerances, goldens, predecessor tests, ZIPs, PNGs, or physics tests.

Do not add JAX/JAXlib/Equinox/Diffrax.

Do not create a PR, merge, tag, classifier, runtime route, Rust lowering,
solver, fitting code, or `main` mutation.

Do not treat a different packaging/container SHA as a scientific failure unless
the identity class says byte identity is authoritative. Conversely, do not use
content equivalence to excuse an immutable-source byte mismatch.

## 7. Final report

Report exact base/head, changed files, RED/GREEN logs, every negative-test
classification, receipt SHA-256, diff-firewall result, unresolved blockers, and
confirmation that all science/runtime boundaries remain blocked.

For the subsequent independent review, start a new Codex context and use
`prompts/AC01_FRESH_REVIEW_PROMPT.md`.

For BASS-9, start a different fresh context and use
`prompts/BASS9_FRESH_CONTEXT_PROMPT.md`.
