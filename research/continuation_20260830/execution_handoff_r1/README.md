# BASS RF-04 execution handoff R1

## Controlling outcome

```text
PASS_IMMUTABLE_PAYLOAD_INTAKE_ONLY
BLOCKED_BY_MISSING_LOCAL_EVIDENCE
NO_PASS_RF04
```

The immutable payload is repaired and remotely bound, but the implementation
gate is not satisfied on this host. The user-reported local source-probe and
schema/native RED commits are absent from GitHub and this workspace is not the
authenticated BASS clone that owns them. No production source from the local
sandbox spike is included in this package or authorized for cherry-pick.

## Remote results already read back

- PR #66 remains open, draft, and unmerged.
- Corrected payload: `16f5811beb7d73fae800ff90caf30f69deebc9fd`,
  tree `85a9164e01ea77d312b185809b3698363c750526`.
- Intake locator: `0a9f726df916c3ddcf74b3a0bd17ba4c529f5a8d`,
  tree `80b0238f04ebfb92441aaa52428bdaf45e282154`.
- Publication v2 terminal before this package:
  `53ac002bdc541f04d4eac6930c4ae1bcf53f1935`, tree
  `3b8be8331630c566c81bd90bb005dfcfc2b45c87`.
- The original failed payload/terminal remain historical failure evidence.
- Mock PR #65 pushed one marker, merged only into its disposable mock base,
  and was read back at merge commit
  `6123a67bf80d653a3e1f3ddd8fd79a8997cc516e`.

## Independent checks on this host

- Corrected manifest: 18/18 raw Git payload blobs match.
- Locator bundle: 6/6 manifest entries match after preserving exact remote
  bytes; 15/15 fixture tests pass normally and under optimized Python.
- Remote lookup for commits `148d590bd45ebcc5e4f2ac8a778c30d26d5f9f31`
  and `d3df4ceb140a9810b0d5219e0e9e748c388a977d` returns no commit.

## Non-authoritative sandbox spike

Before the authoritative R4 locator appeared, a sparse source snapshot was
used to exercise the immutable donor patch. Four Rust owner-level tests and
the two-test geometry prefix passed. This is useful diagnostic evidence only:
the spike did not originate at the genuine local RED commit, did not exercise
the specified result carrier or PyO3 schema, and used the unhardened prefix
validator. It cannot satisfy LOCAL-01 and must not be pushed as implementation.

A late independent audit also reproduced two pre-existing owner-boundary
defects. Finite transport inputs can return `Ok` with
`log_bolometric_shift = -inf`, and finite Type-II state can return `Ok` with a
nonfinite derived background. The immutable telemetry patch does not touch
either arithmetic path. See `NONFINITE_RECEIPT_FINDING.md`,
`NONFINITE_RECEIPT_RED.log`, and `NONFINITE_BACKGROUND_RED.log`. No fix is
pushed without the genuine local evidence worktree and authorized public error
schema.

Read `LOCAL_ONLY_PROMPT.md` on the machine that contains the preserved local
Git objects. Stop immediately if either object or the exact RED tree is absent.
Do not begin LOCAL-02 until every LOCAL-01 acceptance item passes.
