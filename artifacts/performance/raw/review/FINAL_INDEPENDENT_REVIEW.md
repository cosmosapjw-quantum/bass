# FINAL INDEPENDENT REVIEW — PERFORMANCE DELIVERY

## Verdict

`BOUNDED_FINDINGS`: specification scope and claim boundaries are honest, but one
medium evidence-index defect and two low closeout defects require the single
allowed repair-closeout before delivery.

## Findings

### F-01 — MEDIUM / high confidence — incomplete machine-reference closure

`artifacts/performance/EVIDENCE.json` parses and all 25 declared
`evidence_files` entries match their paths, SHA-256 values, and sizes. However,
`benchmark.corpus.harness_ref` names `benchmark_harness_source`, which is not an
`evidence_files` key. The index also claims Wolfram static `17_PASS`, eight-fixture
self-check PASS, and byte-compilation PASS without referencing the existing final
logs. This breaks the index's otherwise resolvable reference contract; it does
not invalidate those results.

Smallest repair: add one resolvable tracked-harness path/hash entry, copy the
three existing final Wolfram static logs into raw evidence, add their digest/size
entries, and point the Wolfram result fields to those keys. Do not rerun them.

### F-02 — LOW / high confidence — precise contention duration is not indexed

The indexed blocker log directly proves substantial unrelated Rabbit/pytest CPU
load at `2026-08-24T17:00:01Z`, so withholding Candidate B timing and claiming no
speedup is honest. It does not independently prove that no qualifying quiet pair
occurred throughout the stated 4,853-second interval.

Smallest repair: either index an existing timestamped monitoring trace, or narrow
the human claim to the directly evidenced final-snapshot contention and retained
`BLOCKED_HOST_CONTENTION` decision. Do not create retrospective synthetic data.

### F-03 — LOW / high confidence — HANDOFF omits explicit workspace state

`HANDOFF.md` is within its line/byte budget and identifies the accepted harness
head/tree plus the intentional self-reference boundary for the later metadata
head, but it does not state clean/dirty delivery-worktree status as its required
STATE schema requests.

Smallest repair: state that the delivery worktree must be clean after the atomic
evidence commit and that the final branch head/tree come from external remote
readback; report those exact values after push without trying to self-embed them.

## Confirmed PASS scope

- Remote identity: canonical, PR20 base, R5b, Wolfram, performance, and native r2
  branch heads match; PRs #20–#23 are OPEN, draft, unmerged, CLEAN, and have the
  intended bases/heads.
- R5b: PR #21 is one test-only commit on PR20. Its 34-case JUnit has zero failures
  and contains operator/matrix/RHS, backward-residual, direct-state, independent
  science, and no-fallback diagnostics. No production/tolerance/reference change
  or semantic-defect claim is hidden.
- Baseline/Q: indexed medians, contributions, profile values, output identities,
  and Q B1/B2 ratios match the referenced JSON. Both Q candidates remain below
  the predeclared 10% gate and uncommitted.
- Candidate B: preserved source/test bytes exactly match the dirty experiment
  worktree; baseline/candidate output digests match; the focused logs show 5 and
  34 PASS. Paired timing is explicitly NOT RUN, so these are not performance
  acceptance evidence.
- Wolfram: PR #22 is independent from PR20, manifest verification passes, the
  handoff has 19 nonblank lines, and authority remains
  `CANDIDATE_UNPROMOTED_FORMULA_BYTES_ABSENT`. No local Wolfram command appears in
  the phase logs and no project replay or historical recovery is claimed.
- Native artifact: PR20→R5b→performance changes only the R5b test and benchmark
  harness; Cargo.lock remains `d500208e...6310`, no native/generated/PyO3/wheel
  path changed, r2 matches `61045b6e...`, and no r3 branch exists. The no-r3
  decision is correct.
- Human reports: FINAL_CLOSEOUT is 13 nonblank lines/3,553 bytes; HANDOFF is 22
  nonblank lines/2,672 bytes; no placeholder or forbidden promotion claim was
  found. Both identify exactly one next action.

## Review limits and actions deliberately not performed

This was the one bounded read-only review. I ran no tests, benchmarks, builds,
profilers, Cargo, Python test commands, or Wolfram commands; made no repository,
Git, PR, or remote mutation; and wrote only this report. Evidence came from file
parsing/hash/size checks, source/diff inspection, existing raw receipts, manifest
hash verification, `git ls-remote`, and read-only `gh pr view`.

## Repair-closeout decision

`CONTINUE_CHANGED_CELL`: apply only F-01 through F-03 in one repair-closeout,
then mechanically recheck JSON/reference integrity, hashes, budgets, clean state,
and final remote identities. No additional review wave is authorized.
