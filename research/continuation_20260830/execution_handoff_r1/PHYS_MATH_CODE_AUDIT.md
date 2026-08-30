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
| PASS | Controlling handoff | Local R4 handoff blob `10b4373f…` matches the remote locator; locator manifest is 6/6. |
| PASS | Remote publication | PR #66 was read back open/draft at `53ac002b…`, tree `3b8be833…`. |
| FAIL | Preserved chain | Both local-only commits are absent remotely and `bass_work` is not a Git worktree. Commit/tree/ancestry/clean-state and genuine RED logs are unavailable. |
| PASS | Immutable donor patch | Scratch donor blob is exactly `e4d0f9…`, SHA-256 `ae38f315…`, and its delta matches the frozen telemetry patch. |
| PASS, static | Counter logic | Split/leaf/depth bookkeeping gives `L=N_root+S`; checked arithmetic prevents saturation. |
| PASS static / CONCERN dynamic | Numerical safety | The patch does not reorder existing arithmetic or callbacks, but full old-field bit parity through the actual carrier is unproved. |
| PASS, scoped | Native smoke | The Rust 1.94.1 test artifact executes four owner tests successfully. |
| FAIL, pre-existing | Finite output boundary | A focused RED returns `Ok` with nonfinite `log_bolometric_shift` from finite inputs. The telemetry patch does not alter the responsible baseline arithmetic. |
| FAIL, pre-existing | Finite background boundary | A focused RED returns `Ok` with a nonfinite derived background from finite Type-II state. The telemetry patch does not alter the adapter arithmetic. |
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
| PASS | Scientific status | Retain scoped scalar/raw proof and overall `NO_PASS_RF04`; no P0/P1 scientific defect was reproduced. |

## Required local sequence

1. Validate the R4 locator manifest and run `FETCH_AND_VALIDATE.py` against the
   authenticated clone.
2. Require both local commits, RED tree `208dc7e2…`, expected ancestry, a clean
   clone, and preserved worktrees. On any failure return only
   `BLOCKED_BY_MISSING_LOCAL_EVIDENCE`.
3. Create a new non-force linked worktree at `d3df4ce…`.
4. Inspect that commit and execute its recorded native/PyO3 RED selectors;
   selector names cannot be stated safely until the commit is recovered.
5. Reproduce both cases in `NONFINITE_RECEIPT_FINDING.md` against the baseline
   and patched donor, classify them under the local contract, and retain both
   raw logs. Do not clamp or invent a public error variant/mapping.
6. Copy only the three authorized payload tools, harden the geometry validator,
   and apply the frozen donor patch.
7. Run pinned `cargo fmt --check`, offline/locked native tests, the production
   wheel build, and the recovered carrier/PyO3/serialization/failure selectors.
8. Retain raw logs and machine receipts. Any `UNTESTED` required item remains
   blocking. Only then may an ordinary stacked draft implementation PR be
   pushed; do not merge or mark ready.

See `LOCAL_ONLY_PROMPT.md` for exact fail-closed commands.
