# PHYS-MATH boundary audit

## Verdict

```text
BLOCKED_BY_MISSING_LOCAL_EVIDENCE
LOCAL-01 INCOMPLETE
LOCAL-02 MUST NOT START
NO_PASS_RF04
```

No P0/P1 mathematical defect was reproduced in the counter implementation.
The decisive blockers are provenance and missing boundary evidence, not a
demonstrated scientific error.

| Classification | Boundary | Finding |
|---|---|---|
| PASS | Remote locator/publication | PR #66 was read back open, draft, and unmerged at `53ac002b…`, tree `3b8be833…`; all changed paths are research/package files. |
| NOT_YET_TESTABLE | Exact-host intake | The authenticated-clone run remains explicitly deferred to the local host. |
| FAIL | Preserved local chain | `148d590…` and `d3df4ce…` are absent remotely. This workspace is not a BASS Git worktree, so object identity, RED tree `208dc7e2…`, ancestry, and clean state cannot be proven. |
| PASS | Donor bytes, sandbox scope | Baseline blob `da6fade…` and patched blob `e4d0f9…` match the frozen pair. This does not establish authorized worktree ancestry. |
| PASS | Counter mathematics | One increment per split and one per accepted leaf imply `L=N_root+S` for the forest of full binary recursion trees. |
| PASS | Callback formula, source inspection | Successful recursion visits `N_root+2S` interval nodes; with two endpoint samples, the expected total is `2+N_root+2S`. |
| PASS | Scoped prefix regression | The retained log reports 90 bit-parity successes, 22 split cases, 18 matching failures, and stress receipt `S=98, L=102, D=7`. |
| FAIL | Prefix admissibility | The validator still contains a Python `assert`, uses plain `git show`, and has no hardened old-mismatch demonstration. R4 forbids treating this run as final evidence. |
| FAIL | Independent depth oracle | Tests check relations/bounds but do not independently record the recursion tree or assert a known exact depth. A depth undercount could survive. |
| NOT_YET_TESTABLE | Full old-field parity | Final carrier projection, coherency, leakage/eigenvalue diagnostics, and the complete returned object were not compared. |
| CONCERN | Failure transactionality | One midpoint failure exists, but there is no first-child-success/second-child-failure case or post-recursion carrier/projection/realizability failure evidence. |
| PASS / NOT_YET_TESTABLE | Overflow | Checked additions return `DiagnosticCounterOverflow`; runtime propagation remains unexecuted. |
| FAIL | Public/PyO3 schema | Serialization, exhaustive consumers, registration, Python success mapping, and Python error mapping are absent and must not be inferred. |
| PASS, sandbox only | Owner smoke | Four prebuilt owner tests pass, but source-to-binary provenance, genuine RED ancestry, and durable build/test logs are absent. |
| FAIL | Complete LOCAL-01 | Mandatory acceptance items and the preserved-chain gate are incomplete. |
| N/A | LOCAL-02 physics | Not evaluated because LOCAL-01 is a strict prerequisite. |

## Evidence identities

- R4 handoff: Git blob `10b4373f793538c1ed890f1fae634ea809c9cec2`,
  SHA-256 `e281b432b6b40d3aa4324114246da788ccbc2bad32b1c7ab75e86379e639a257`.
- Publication v2: Git blob `784ad7fe8c1565cb8a1fe5ebcdd94047a2cbe0a0`,
  SHA-256 `7f72d7a4170cfe6c77fe53d417604e33752d4f84aba6fcd4d170d3b4e07b36d0`.
- Baseline donor: Git blob `da6fade06f717ab938b0ec4c712ab239e78c998a`,
  SHA-256 `b9178128388a384fdbd3593aa39a409db5a230f8bf7794747f0458347f6393bb`.
- Patched donor: Git blob `e4d0f9c44fc26740d3a1cad6938b522fe514ae37`,
  SHA-256 `ae38f315e84314ed7fef5360ac7f3a44c8f140c5d27d4ddb3a0a539bcef70cab`.
- Geometry receipt: `9924fa9b03a6fc806859e25de8721f240598c517ca6a3912e8ba419963395e5b`.
- Geometry test log: `4ccc8e29ed6264f5b6f37ed7bb405a1488bf4bcad12335a9580dcecc4e1eb4e5`.
- Geometry test source: `36abcf023c7869092e3e28948178c0ca90eaaa7090e31fca733195e5147e4c89`.
- Unhardened validator: `83d3eb258d9dafd6cefe5fd7d26a73a9822977a46c60306f7c192c9cdf9a395d`.

