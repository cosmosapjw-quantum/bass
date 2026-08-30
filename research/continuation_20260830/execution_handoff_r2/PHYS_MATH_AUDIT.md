# PHYS-MATH boundary audit

## Verdict

```text
BLOCKED_BY_MISSING_LOCAL_EVIDENCE
LOCAL-01 INCOMPLETE
LOCAL-02 MUST NOT START
NO_PASS_RF04
```

No mathematical defect was reproduced in the counter implementation. A late
audit reproduced two separate owner-boundary REDs on the patched sandbox:
finite transport inputs can return `Ok` with a nonfinite bolometric log shift,
and finite Type-II state can return `Ok` with a nonfinite derived background.
Exact static comparison shows the telemetry patch does not touch either path;
baseline execution was not run. Severity is unclassified because the
authenticated owner/exposure contract is unavailable. Final R4 nevertheless
makes both cases mandatory baseline/candidate LOCAL-01 gates.

| Classification | Boundary | Finding |
|---|---|---|
| PASS | Remote locator/publication | PR #66 was read back open, draft, and unmerged at publication `ed3f502…`, tree `1e7ced1…`; canonical locator is `7373fb2…` / `da512ef…`, and all changed paths are research/package files. |
| PASS | Hardened locator fixtures | Exact archive/manifest bytes pass 7/7 and 6/6; fresh execution passes 30/30 normally and under optimized Python 3.12.13. |
| PASS_EVIDENCE_ONLY | Superseded locators | `0a9f726…`, publication v2, `4b816641…` / `230581f9…`, and execution handoff R1 are superseded and must not be executed. |
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
| RED, pre-existing static / severity unclassified | Finite-result scalar contract | Candidate execution with finite `step=1e308` and `expansion=1` returns `Ok` while `log_bolometric_shift` is `-inf`. Exact source comparison finds the same baseline arithmetic; baseline execution remains local. |
| RED, pre-existing static / owner unclassified | Finite-background contract | Candidate execution with finite Type-II state `[f64::MAX, 0, 0, 1, 0]` returns `Ok` with a nonfinite derived background. The unchanged adapter establishes non-regression statically; downstream transport revalidates, so public severity awaits owner/exposure classification. |
| FAIL | Mandatory nonfinite-boundary gates | Final R4 requires authenticated baseline/candidate runs and finite success or an existing authorized typed failure through the real carrier/PyO3 mapping for both named cases. Neither gate is complete here; severity cannot waive them. |
| CONCERN | Leakage interpretation | Leakage is evaluated after `project_screen_state`, so it is a post-projection residual rather than demonstrated raw transport leakage. |
| CONCERN | Accuracy interpretation | Subdivision is driven by midpoint fixed-point convergence without a truncation-error estimate; split telemetry is not an accuracy certificate. |
| FAIL | Complete LOCAL-01 | Mandatory acceptance items and the preserved-chain gate are incomplete. |
| N/A | LOCAL-02 physics | Not evaluated because LOCAL-01 is a strict prerequisite. |

## Evidence identities

- Final R4 handoff: Git blob `23f40ea31e5d9d6a5b07ceaec99406fda05b603c`,
  SHA-256 `45809b3548a557c9bebc2552e1e317032e4895b304b2ec3182cdebaf3c1f00fa`.
- Publication v5: Git blob `75d19c6ce4ee33b6458248c2e7198800864d306e`,
  SHA-256 `2c4a5abe75b11a8e974ca4bd46dbaf14d71fc707d6dbec9c708c8f5ff41ff8a3`.
- Hardened locator: Git blob `35e0024734491b7dcd4eb264b23c7e3171439995`,
  SHA-256 `ff43cecdc03846a4b73b2acf3b618236444614f0d124f467ddb98e3bb405524f`.
- Locator manifest/archive SHA-256: `dd5c30c523ea8ba8a6a77e41fa291c0df3c955d7bb9940dd61ea73cba588c286` / `907a30badc0cd6cb55375a45c4dc36fe7ad4cb1246592bcdf9aa482f19453f6f`.
- Baseline donor: Git blob `da6fade06f717ab938b0ec4c712ab239e78c998a`,
  SHA-256 `b9178128388a384fdbd3593aa39a409db5a230f8bf7794747f0458347f6393bb`.
- Patched donor: Git blob `e4d0f9c44fc26740d3a1cad6938b522fe514ae37`,
  SHA-256 `ae38f315e84314ed7fef5360ac7f3a44c8f140c5d27d4ddb3a0a539bcef70cab`.
- Geometry receipt: `9924fa9b03a6fc806859e25de8721f240598c517ca6a3912e8ba419963395e5b`.
- Geometry test log: `4ccc8e29ed6264f5b6f37ed7bb405a1488bf4bcad12335a9580dcecc4e1eb4e5`.
- Geometry test source: `36abcf023c7869092e3e28948178c0ca90eaaa7090e31fca733195e5147e4c89`.
- Unhardened validator: `83d3eb258d9dafd6cefe5fd7d26a73a9822977a46c60306f7c192c9cdf9a395d`.
- Nonfinite-receipt RED log: `326f26db8342c464453dfae148f6dc1dff7e332dba07cc635cda84120580066b`.
- Nonfinite-background RED log: `cff06d701f4d581fbdb7f3ddd6c0e305ddc10e6e10297fd57f3f164c41ae8756`.
- Final sandbox reproducer source: Git blob `8b4fb327aa4bf2480c6d829936d838d56cd1ade3`, SHA-256 `8530b875e0011c9f76ff90f52d0b7ee60637b5a08fc8aab88e19c131ed40acc4`.
- Cargo lock: Git blob `98e67c4be673f342c254495b3f340c9252910aaf`, SHA-256 `18b62b9b792058ab789521d1c69764bed7915b550cd4fc389e848a6ec02c07ed`.
- Receipt/background test binaries: SHA-256 `b8d40804…12fc2` / `6ceeec9f…125c`.

The counter identities remain intact. Both reproduced nonfinite-boundary
REDs must be carried into the authenticated worktree and classified at their
source-owned boundaries. Both are mandatory gates: require finite success or
an existing authorized typed failure through the real carrier/PyO3 mapping.
If a candidate remains invalid, make only the smallest authorized source-owned
correction in a separate safety commit; ambiguous authority blocks LOCAL-01.
