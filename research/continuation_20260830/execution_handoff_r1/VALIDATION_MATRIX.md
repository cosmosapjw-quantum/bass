# RF-04 validation matrix

| Boundary | Status | Evidence / reason |
|---|---|---|
| Historical failure preserved | PASS | `4538ac92…` and `989f9c38…` remain explicitly classified as 16/18 manifest failure evidence. |
| Corrected immutable payload | PASS | `16f5811…` / `85a9164…`; manifest blob `32473fb…`; 18/18 raw Git blobs match. |
| Publication binding | PASS | `REMOTE_PUBLICATION.json` v2 at `53ac002…` binds corrected payload and R4 locator; no manifested byte changed. |
| Locator byte manifest | PASS | 6/6 locator entries match exact remote text bytes. |
| Locator fixture tests | PASS | 15/15 normal and 15/15 under `python -O`; AST, shell, and JSON validation pass. |
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
| PHYS-MATH audit | FAIL | Counter algebra passes, but provenance, hardened-prefix, independent-depth, carrier/PyO3, and failure-transaction evidence remain blocking. |
| PHYS-MATH-CODE audit | FAIL | Independent review says the scratch production delta is not push-ready and must not substitute for the genuine RED chain. |
| LOCAL-01 | FAIL | Gate result is `BLOCKED_BY_MISSING_LOCAL_EVIDENCE`; this is not a scientific defect and earns no telemetry-parity promotion. |
| LOCAL-02 | NOT_STARTED | LOCAL-01 is an explicit prerequisite. |
| Scientific claim | PASS_RETAINED_SCOPE | `PASS_RF04_SCALAR_RAW_SLICE_PROOF` retained; overall status remains `NO_PASS_RF04`. |
| Mock push/PR/merge | PASS | PR #65 merged expected head only into disposable mock base; marker read back at merge commit `6123a67…`. |
| Production implementation push | N/A | Prohibited while the local-evidence gate is closed; no sandbox source is uploaded. |
