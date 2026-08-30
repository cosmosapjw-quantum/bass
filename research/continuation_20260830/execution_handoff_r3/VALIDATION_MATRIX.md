# RF-04 R3 validation matrix

| Boundary | Status | Evidence / reason |
|---|---|---|
| Historical 16/18 manifest failure | PASS_EVIDENCE_ONLY | `4538ac92…` and `989f9c38…` remain immutable failure evidence. |
| Corrected immutable payload | PASS_REMOTE_BYTES | `16f5811…` / `85a9164…`; manifest blob `32473fb…`; 18/18 raw Git blobs match. |
| R4 remote locator bundle | PASS_EVIDENCE_ONLY | R4 commit `7373fb2…` remains byte-valid but is superseded for execution. |
| R4 exact-host locator execution | STOP_INVALID | User-reported `/usr/bin/git 2.43.0`: 2 PASS, 5 FAIL, 23 ERROR; unsupported global `--no-lazy-fetch`. |
| R4 optimized tests | NOT_RUN | Intake contract stopped at the ordinary test gate. |
| R4 canonical 18-file intake | NOT_RUN | No implementation worktree or source change followed. |
| R5 locator manifest | PASS | Blob `50ab58f…`, SHA-256 `5f9b952…`; 6/6 exact bytes. |
| R5 locator archive | PASS | Blob `e3ac728…`, SHA-256 `4f31624…`; 7/7 members, stored compression, fixed metadata, CRC/member/rebuild match. |
| Git 2.43.0 normal fixtures | PASS | Python 3.12.3, 56/56, zero skips. |
| Git 2.43.0 optimized fixtures | PASS | Python 3.12.3 `-O`, 56/56, zero skips. |
| Git 2.51.1 normal fixtures | PASS | Python 3.12.3, 56/56, zero skips. |
| Git 2.51.1 optimized fixtures | PASS | Python 3.12.3 `-O`, 56/56, zero skips. |
| R5 independent source/test review | PASS_SCOPED | Prior digest, probe-branch, cleanup/cache, helper quoting, inventory, and zero-skip blockers closed. |
| Trusted Git subprocess timeout/output bound | ACCEPTED_RESIDUAL | R5 trusts the selected Git installation; its subprocess runtime/output are not internally bounded. |
| R5 remote file readback | PASS | All 9 committed R5 blobs and base64 bytes matched local publication inputs. |
| Publication v6 binding | PASS | `cb9b2c8…` is a direct child of R5 and changes only `REMOTE_PUBLICATION.json`; blob `1580e8c…`. |
| R3 addendum authority | PASS_SCOPED | Subordinate to exact R5 handoff and publication v6; cannot widen scientific authority. |
| R3 package preserved bytes | PASS | Five R2 evidence files retain exact SHA-256 identities. |
| R3 package status freshness | PASS | R4 `STOP_INVALID`, R5 `DEFERRED_LOCAL`, intake `NOT_RUN`, local gate `NOT_REACHED`. |
| Authenticated exact-host R5 intake | DEFERRED_LOCAL | Must run on the host owning the authenticated complete clone and pinned objects. |
| Canonical 18-file materialization under R5 | NOT_RUN | Must follow exact-host R5 tests and locator byte validation. |
| Preserved source-probe commit | NOT_REACHED | Check `148d590…` only after R5 intake passes. |
| Genuine schema/native RED commit/tree | NOT_REACHED | Check `d3df4ce…` / `208dc7e…` only after R5 intake passes. |
| Implementation worktree | NOT_CREATED | Prohibited until intake and preserved-chain gates pass. |
| Telemetry patch application | NOT_STARTED | No production source is included in this package. |
| Genuine native/carrier/PyO3 RED | NOT_STARTED | Selector authority is owned by the preserved local commit. |
| Ordinary-corpus telemetry parity | NOT_STARTED | Requires actual owner, carrier, callback, serialization, and error-path evidence. |
| Finite transport-return boundary | HISTORICAL_RED_PENDING_AUTHENTICATED_RUN | Preserved diagnostic log SHA-256 `326f26d…`; baseline/candidate local runs mandatory later. |
| Finite Type-II background boundary | HISTORICAL_RED_PENDING_AUTHENTICATED_RUN | Preserved diagnostic log SHA-256 `cff06d7…`; baseline/candidate local runs mandatory later. |
| Mandatory nonfinite-boundary gates | NOT_REACHED | Become active only after intake and preserved-chain gates; `FAIL` or `UNTESTED` blocks LOCAL-02. |
| Counter algebra | CONTRACT_ONLY | Successful calls require `L=N_root+S`; callback count `2+N_root+2*S`; not yet dynamically proven on owner. |
| Screen-leakage meaning | CONTRACT_CONCERN | Current value is post-projection and cannot be called raw transport leakage. |
| Split telemetry meaning | CONTRACT_CONCERN | Work counters are not truncation-error or accuracy certificates. |
| PHYS-MATH implementation audit | NOT_RUN | No scientific implementation boundary was changed here. |
| PHYS-MATH-CODE implementation audit | NOT_RUN | No production delta exists to audit. |
| LOCAL-01 | NOT_STARTED_GATE_NOT_REACHED | Start only after R5 intake and local-object gate. |
| LOCAL-02 | NOT_STARTED | Strictly requires complete LOCAL-01. |
| Mock push/PR/merge | PASS_HISTORICAL | PR #67 merged only into a disposable mock base at `8f63715…`; `main` was not the target. |
| Production implementation push | FALSE | Only locator/publication/handoff evidence is published. |
| Scientific claim | NO_PASS_RF04 | Scoped `PASS_RF04_SCALAR_RAW_SLICE_PROOF` remains retained; no promotion. |
