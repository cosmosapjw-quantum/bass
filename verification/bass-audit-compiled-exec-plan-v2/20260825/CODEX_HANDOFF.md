# Codex handoff — execute only BASS-AC-01

Repository: `~/bass`

Exact base: `f0fb24b55967e0dcbcc4d875c5a9b2677e680655`

Source branch: `agent/verify/bass-close-00s-blocked-input-seal-20260825`

Create a separate worktree and branch:

```text
agent/guard/bass-ac-01-artifact-identity-20260825
```

## Primary rule

Do not ask the user questions. Do not guess across a specification boundary. If repository evidence cannot resolve a required behavior, stop with `BLOCKED_BY_UNRESOLVED_SPEC` and preserve the exact evidence.

## Read first

1. `verification/bass-audit-compiled-exec-plan-v2/20260825/CURRENT_STATE.json`
2. `P0_P1_POLICY.md`
3. `P0_P1_THREAT_CATALOGUE.jsonl`
4. `PR_CONTRACTS/BASS-AC-01.json`
5. `FRESH_CONTEXT_REVIEW_CONTRACT.json`

## Execute

Implement exactly the files and tests in `BASS-AC-01.json` using test-first development. The verifier must be pure Python standard library. It must classify:

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

1. Confirm exact base SHA and clean worktree.
2. Copy the compiled contract into `verification/audit-compiled/ACTIVE_PR_CONTRACT.json` without semantic edits.
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
