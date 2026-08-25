# Codex handoff — execute only BASS-AC-01

Repository: `~/bass`

Exact implementation base: `f0fb24b55967e0dcbcc4d875c5a9b2677e680655`

Compiled-plan branch: `agent/audit/bass-audit-compiled-exec-plan-v2-20260825`

Create **two** separate worktrees so the immutable plan remains readable while the implementation starts from the exact base:

```bash
cd ~/bass
git fetch origin \
  agent/audit/bass-audit-compiled-exec-plan-v2-20260825 \
  agent/verify/bass-close-00s-blocked-input-seal-20260825

git worktree add \
  ../bass-ac01-plan \
  origin/agent/audit/bass-audit-compiled-exec-plan-v2-20260825

git worktree add -b \
  agent/guard/bass-ac-01-artifact-identity-20260825 \
  ../bass-ac01-impl \
  f0fb24b55967e0dcbcc4d875c5a9b2677e680655
```

Set:

```bash
PLAN_ROOT=../bass-ac01-plan/verification/bass-audit-compiled-exec-plan-v2/20260825
IMPL_ROOT=../bass-ac01-impl
```

## Primary rule

Do not ask the user questions. Do not guess across a specification boundary. If repository evidence cannot resolve a required behavior, stop with `BLOCKED_BY_UNRESOLVED_SPEC` and preserve the exact evidence.

## Read first from `$PLAN_ROOT`

1. `CURRENT_STATE.json`
2. `P0_P1_POLICY.md`
3. `P0_P1_THREAT_CATALOGUE.jsonl`
4. `PR_CONTRACTS/BASS-AC-01.json`
5. `FRESH_CONTEXT_REVIEW_CONTRACT.json`

Before any code edit, verify the contract bytes and copy them into the implementation worktree:

```bash
cd "$PLAN_ROOT"
echo 'e7837c0ecd92793c19ecc53c5559fd9f67cd4884a393eaf4c323fbbbebe46cca  PR_CONTRACTS/BASS-AC-01.json' | sha256sum -c -

mkdir -p "$IMPL_ROOT/verification/audit-compiled"
cp PR_CONTRACTS/BASS-AC-01.json \
  "$IMPL_ROOT/verification/audit-compiled/ACTIVE_PR_CONTRACT.json"
cmp PR_CONTRACTS/BASS-AC-01.json \
  "$IMPL_ROOT/verification/audit-compiled/ACTIVE_PR_CONTRACT.json"
```

The active-contract copy is an explicitly allowed path and must remain byte-identical to the compiled contract.

## Execute in `$IMPL_ROOT`

Implement exactly the files and tests in `ACTIVE_PR_CONTRACT.json` using test-first development. The verifier must be pure Python standard library. It must classify:

```text
PASS_EXACT_IDENTITY
BLOCKED_INPUT_REQUIRED
ARTIFACT_IDENTITY_COLLISION
UNBOUND_HISTORICAL_EVIDENCE
NON_PORTABLE_SIDECAR
CACHE_CONTAMINATION
FORBIDDEN_REFERENCE_MUTATION
```

Do not touch science source, historical evidence, expected hashes, tolerances, goldens, physics tests, package ZIPs, or PNGs. Do not recover or supersede 2B.3. Do not add JAX. Do not start BASS-3, Rust, runtime, fitting, PR, merge, or tag.

## Required loop

1. Confirm exact base SHA and clean implementation worktree.
2. Confirm `ACTIVE_PR_CONTRACT.json` is byte-identical to the plan copy.
3. Write failing tests for every P0/P1 failure mode.
4. Run each test and preserve the RED log.
5. Implement the minimal verifier/diff firewall.
6. Run targeted, negative, regression, and full relevant suites.
7. Run PHYS-MATH audit: identity semantics, no scientific inference from missing bytes, no unit/sign/frame changes.
8. Run PHYS-MATH-CODE audit: exit codes, path confinement, digest computation, receipt binding, cache behavior.
9. Create machine receipt and evidence bundle.
10. Self-review the diff.
11. Stop. Do not perform the fresh-context review in the same session.
12. Commit once and push normally only after all required evidence passes.

Commit message:

```text
guard: add fail-closed BASS artifact identity verification
```

Final report: base/head, files changed, RED/GREEN logs, negative results, machine receipt, diff firewall, unresolved blockers, and confirmation that all science/runtime boundaries remain blocked.
