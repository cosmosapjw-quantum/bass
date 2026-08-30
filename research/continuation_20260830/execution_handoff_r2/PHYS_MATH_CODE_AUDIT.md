# PHYS-MATH-CODE audit

## Verdict

```text
FAIL — DO NOT PUSH THE SCRATCH PRODUCTION DELTA
BLOCKED_BY_MISSING_LOCAL_EVIDENCE
```

The scratch delta is useful preparatory work but is not a contract-valid
continuation worktree and does not satisfy LOCAL-01. A blocker-only
handoff/receipt may be published; the production source may not.

| Classification | Area | Finding |
|---|---|---|
| PASS | Controlling handoff | Final R4 handoff blob `23f40ea…` matches canonical locator `7373fb2…`; locator manifest is 6/6. |
| PASS | Remote publication | PR #66 was read back open/draft at terminal publication `ed3f502…`, tree `1e7ced1…`; publication v5 blob is `75d19c6…`. |
| PASS | Locator verification | Exact seven-member archive matches remote bytes; fresh 30/30 normal and 30/30 optimized fixture tests pass. |
| PASS_EVIDENCE_ONLY | Superseded intake | Pre-final locator `0a9f726…`, the gate-incomplete `4b816641…` / `230581f9…` pair, and execution handoff R1 are retained but non-executable. |
| FAIL | Preserved chain | Both local-only commits are absent remotely and `bass_work` is not a Git worktree. Commit/tree/ancestry/clean-state and genuine RED logs are unavailable. |
| PASS | Immutable donor patch | Scratch donor blob is exactly `e4d0f9…`, SHA-256 `ae38f315…`, and its delta matches the frozen telemetry patch. |
| PASS, static | Counter logic | Split/leaf/depth bookkeeping gives `L=N_root+S`; checked arithmetic prevents saturation. |
| PASS static / CONCERN dynamic | Numerical safety | The patch does not reorder existing arithmetic or callbacks, but full old-field bit parity through the actual carrier is unproved. |
| PASS, scoped | Native smoke | The Rust 1.94.1 test artifact executes four owner tests successfully. |
| RED, pre-existing static / severity unclassified | Finite output boundary | A focused candidate RED returns `Ok` with nonfinite `log_bolometric_shift` from finite inputs. Static comparison shows telemetry does not alter the baseline arithmetic; baseline execution is not retained. |
| RED, pre-existing static / owner unclassified | Finite background boundary | A focused candidate RED returns `Ok` with a nonfinite derived background from finite Type-II state. The adapter is unchanged and downstream transport revalidates; owner/exposure severity remains local. |
| FAIL | Mandatory safety gates | Final R4 requires both named cases on authenticated baseline and candidate, resolving each to finite success or an existing authorized typed failure through real carrier/PyO3 mapping. Neither gate is complete here. |
| CONCERN | Leakage diagnostic semantics | The reported maximum is evaluated after screen projection and is not demonstrated to measure raw transport leakage. |
| CONCERN | Split diagnostic semantics | Fixed-point split counts measure computational work; no truncation-error estimator makes them an accuracy certificate. |
| FAIL | Genuine RED/TDD | No retained RED log from `d3df4ce…`; scratch tests cannot substitute for it. |
| FAIL | Owner acceptance matrix | Independent depth, callback fractions/order, second-child failure, post-recursion failures, full result parity, mutation evidence, and failure-history atomicity are missing. |
| CONCERN | Generated owner coverage | The module is compiled, but the tests call the guard and Liouville donor rather than generated polarized-kernel functions. |
| PASS, source-reviewed | Overflow | Both additions are checked; runtime overflow is explicitly unexecuted. |
| CONCERN | Geometry prefix | Supportive sampled parity exists, but the script has an optimization-removable identity gate and replacement-object exposure. |
| NOT_YET_TESTABLE | Rust API consumers | The missing genuine RED owns the exact exhaustive match/destructure contract. |
| NOT_YET_TESTABLE | PyO3 mapping | Current wrapper exposes scalar/raw v1 only; no authorized telemetry mapping is present. |
| NOT_YET_TESTABLE | Serialization | No authorized telemetry receipt schema exists in the scratch snapshot. |
| CONCERN | Formatting | Pinned Rust 1.94.1 `rustfmt --check` exits 1 on one private module-declaration ordering diff. |
| FAIL | Push readiness | Do not commit or push the scratch production delta. |
| N/A | LOCAL-02 | Explicitly prohibited after partial LOCAL-01. |
| PASS | Scientific status | Retain scoped scalar/raw proof and overall `NO_PASS_RF04`; this non-authoritative host assigns no P0/P1 classification to the two late REDs. |

## Required local sequence

1. Validate the R4 locator manifest and run `FETCH_AND_VALIDATE.py` against the
   authenticated clone.
2. Require both local commits, RED tree `208dc7e2…`, expected ancestry, a clean
   clone, and preserved worktrees. On any failure return only
   `BLOCKED_BY_MISSING_LOCAL_EVIDENCE`.
3. Create a new non-force linked worktree at `d3df4ce…`.
4. Inspect that commit and execute its recorded native/PyO3 RED selectors;
   selector names cannot be stated safely until the commit is recovered.
5. Reproduce both cases in `NONFINITE_RECEIPT_FINDING.md` on the baseline and
   retain separate raw logs and source/run identities.
6. Copy only the three authorized payload tools, harden the geometry validator,
   apply the frozen donor patch, and verify exact blob `e4d0f9…`.
7. Rerun both boundary cases on that exact candidate, classify them under the
   local owner/exposure contract, and retain separate candidate logs. Both are
   mandatory regardless of severity: require finite success or an existing
   authorized typed failure through the real carrier/PyO3 mapping. If a
   candidate remains invalid, make the smallest authorized source-owned change
   in a separate safety commit. Do not clamp or invent a public error
   variant/mapping; ambiguous authority is a blocker.
8. Run pinned `cargo fmt --check`, offline/locked native tests, the production
   wheel build, and the recovered carrier/PyO3/serialization/failure selectors.
9. Retain raw logs and machine receipts. Any `UNTESTED` required item remains
   blocking. Only then may an ordinary stacked draft implementation PR be
   pushed; do not merge or mark ready.

If an authorized boundary fix changes the donor beyond frozen blob `e4d0f9…`,
record the final rebound Git blob/SHA-256. Exactly the two named safety cases
may resolve either through a fully finite-success correction or an existing
authorized success-to-typed-error transition. Preserve bit parity on the
ordinary telemetry corpus and compare unaffected fields/callbacks through any
source-owned rejection point.

See `LOCAL_ONLY_PROMPT.md` for exact fail-closed commands.
