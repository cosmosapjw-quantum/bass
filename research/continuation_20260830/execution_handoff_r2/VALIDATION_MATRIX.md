# RF-04 validation matrix

| Boundary | Status | Evidence / reason |
|---|---|---|
| Historical failure preserved | PASS | `4538ac92…` and `989f9c38…` remain explicitly classified as 16/18 manifest failure evidence. |
| Corrected immutable payload | PASS | `16f5811…` / `85a9164…`; manifest blob `32473fb…`; 18/18 raw Git blobs match. |
| Superseded locators preserved | PASS_EVIDENCE_ONLY | `0a9f726…` / `53ac002…`, `4b816641…` / `230581f9…`, and execution handoff R1 are retained but explicitly superseded and non-executable. |
| Final publication binding | PASS | `REMOTE_PUBLICATION.json` v5 at `ed3f502…` binds corrected payload and canonical hardened locator `7373fb2…`; publication blob is `75d19c6…`. |
| Hardened locator byte manifest | PASS | Manifest blob `3934c51…`, SHA-256 `dd5c30c…`; 6/6 exact remote/ZIP text bytes match. |
| Hardened locator archive | PASS | Blob `a5e4213…`, SHA-256 `907a30b…`; seven exact members, CRC and member bytes pass. |
| Locator fixture tests | PASS | Fresh execution: 30/30 normal and 30/30 under `python -O` with Python 3.12.13; JSON validation passes. |
| R2 execution addendum authority | PASS_SCOPED | This package is subordinate to final R4 handoff/publication and cannot widen their authority. |
| Authenticated exact-host locator run | NOT_YET_TESTABLE | This host has no authenticated full BASS Git clone. |
| Preserved source-probe commit | NOT_YET_TESTABLE | `148d590…` is absent from GitHub; must be checked in the user's local object database. |
| Genuine schema/native RED commit and tree | NOT_YET_TESTABLE | `d3df4ce…` is absent from GitHub; required tree is `208dc7e…`. |
| Immutable donor patch identity | PASS | Sparse diagnostic application produced blob `e4d0f9c…` and SHA-256 `ae38f315…`. This is identity only. |
| Donor geometry prefix | CONCERN | 2/2 passed with sampled bit/error parity, but the R4-required validator hardening was not applied and the extracted prefix files are not cryptographically bound to the named full donor blobs; result is diagnostic-only. |
| Native owner no/nested/multiple-panel semantics | CONCERN | Four sandbox tests passed, but not from the genuine RED worktree and no durable raw Cargo log was retained. Pinned `rustfmt --check` also reports one module-order formatting diff. |
| Pre-existing numerical field bit parity in real carrier | NOT_YET_TESTABLE | Genuine result-carrier boundary is supplied only by the missing local RED chain. |
| Callback fraction/order/count parity | NOT_YET_TESTABLE | Prefix tested call-count parity, but the full R4 callback matrix was not executed. |
| Post-recursion and second-child failure transactionality | NOT_YET_TESTABLE | Missing genuine owner/carrier schema and selectors. |
| PyO3 success/error mapping | NOT_YET_TESTABLE | Exact symbol and receipt schema are intentionally not inferred. |
| Serialization and exhaustive consumers | NOT_YET_TESTABLE | Requires the genuine schema/native RED diff. |
| Counter overflow behavior | CONCERN | Checked arithmetic is visible in the donor patch, but safe execution or a formal source-only disposition remains local. |
| Finite returned scalar contract | RED / UNCLASSIFIED | Patched-sandbox Rust RED exits 101: finite inputs return `Ok` with `log_bolometric_shift = -inf`. Exact static comparison shows unchanged baseline arithmetic; baseline execution and authenticated severity classification remain local. |
| Finite Type-II background contract | RED / UNCLASSIFIED | Patched-sandbox Rust RED exits 101: finite state `[f64::MAX, 0, 0, 1, 0]` returns `Ok` with a nonfinite derived background. The unchanged adapter makes this pre-existing statically, but downstream transport rejects it and owner/exposure severity is not yet classified. |
| Mandatory nonfinite-boundary gates | FAIL | Final R4 requires authenticated baseline/candidate runs and finite success or an existing authorized typed failure through real carrier/PyO3 mapping for both cases. `FAIL` or `UNTESTED` keeps LOCAL-02 closed; severity cannot waive a gate. |
| Screen-leakage meaning | CONCERN | `max_screen_leakage` is computed after screen projection; current evidence does not establish a bound on raw transported longitudinal leakage. |
| Split-count meaning | CONCERN | Split/leaf/depth telemetry measures fixed-point subdivision work, not a truncation-error or integration-accuracy certificate. |
| PHYS-MATH audit | FAIL | Counter algebra passes, but authenticated baseline/candidate safety gates plus provenance, hardened-prefix, independent-depth, carrier/PyO3, and failure-transaction evidence remain incomplete. Any required safety correction must use an authorized source-owned transition in a separate commit. |
| PHYS-MATH-CODE audit | FAIL | Independent review says the scratch production delta is not push-ready and must not substitute for the genuine RED chain. |
| LOCAL-01 | FAIL | Gate result is `BLOCKED_BY_MISSING_LOCAL_EVIDENCE`; this is not a scientific defect and earns no telemetry-parity promotion. |
| LOCAL-02 | NOT_STARTED | LOCAL-01 is an explicit prerequisite. |
| Scientific claim | PASS_RETAINED_SCOPE | `PASS_RF04_SCALAR_RAW_SLICE_PROOF` retained; overall status remains `NO_PASS_RF04`. |
| Mock push/PR/merge | PASS | PR #67 merged expected head `bec5df0…` only into disposable mock base; marker blob `20ba428…` read back at merge commit `8f63715…`. |
| Production implementation push | N/A | Prohibited while the local-evidence gate is closed; no sandbox source is uploaded. |
