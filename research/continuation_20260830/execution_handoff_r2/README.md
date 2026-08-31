# BASS RF-04 execution handoff R2

## Controlling outcome

```text
PASS_REMOTE_RAW_OBJECT_PAYLOAD_CLOSURE_ONLY
PASS_REMOTE_LOCATOR_BYTE_READBACK_ONLY
BLOCKED_BY_MISSING_LOCAL_EVIDENCE
NO_PASS_RF04
```

The immutable payload is repaired and the final hardened locator is remotely
bound, but exact-host intake and the implementation gate are not satisfied on
this host. The user-reported local source-probe and schema/native RED commits
are absent from GitHub and this workspace is not the authenticated BASS clone
that owns them. No production source from the local sandbox spike is included
in this package or authorized for cherry-pick.

## Remote results already read back

- PR #66 remains open, draft, and unmerged.
- Corrected payload: `16f5811beb7d73fae800ff90caf30f69deebc9fd`,
  tree `85a9164e01ea77d312b185809b3698363c750526`.
- Canonical hardened locator:
  `7373fb23d8b9d43bfc52707d9260ff83ee9b3e66`, tree
  `da512efa34351582f0b42dc0b9dd05ddd48ce79a`.
- Terminal publication v5 before this addendum:
  `ed3f502cdcea0b83aab6ccc8de3ec31dd1cee12b`, tree
  `1e7ced1d109155c612436f2c37943805ad71c35d`.
- Publication v5 blob `75d19c6ce4ee33b6458248c2e7198800864d306e`,
  SHA-256 `2c4a5abe75b11a8e974ca4bd46dbaf14d71fc707d6dbec9c708c8f5ff41ff8a3`.
- The pre-final locator `0a9f726…`, publication v2 `53ac002…`, the
  handoff-gate-incomplete `4b816641…` / `230581f9…` pair, and execution
  handoff R1 remain evidence-only and must not be executed.
- The original failed payload/terminal remain historical failure evidence.
- Mock PR #67 pushed one marker, merged only into its disposable mock base,
  and was read back at merge commit
  `8f6371518605cc28df6b7a9fb0744e2529ad7066`.

## Independent checks on this host

- Corrected manifest: 18/18 raw Git payload blobs match.
- Final locator bundle: 6/6 manifest entries match exact remote bytes; its
  seven-member ZIP has matching bytes and CRC. Fresh local execution passed
  30/30 fixture tests normally and 30/30 under optimized Python 3.12.13.
- Remote lookup for commits `148d590bd45ebcc5e4f2ac8a778c30d26d5f9f31`
  and `d3df4ceb140a9810b0d5219e0e9e748c388a977d` returns no commit.

## Non-authoritative sandbox spike

Before the authoritative R4 locator appeared, a sparse source snapshot was
used to exercise the immutable donor patch. Four Rust owner-level tests and
the two-test geometry prefix passed. This is useful diagnostic evidence only:
the spike did not originate at the genuine local RED commit, did not exercise
the specified result carrier or PyO3 schema, and used the unhardened prefix
validator. It cannot satisfy LOCAL-01 and must not be pushed as implementation.

A late independent audit also reproduced two pre-existing owner-boundary REDs
on the non-authoritative patched sandbox. Finite transport inputs can return `Ok` with
`log_bolometric_shift = -inf`, and finite Type-II state can return `Ok` with a
nonfinite derived background. The immutable telemetry patch does not touch
either arithmetic path; the pre-existing classification is based on exact
static baseline/candidate comparison because baseline execution was not run on
this host. Severity remains unclassified pending the authenticated owner
contract. See `NONFINITE_RECEIPT_FINDING.md`, both RED logs, and
`SANDBOX_LATE_RED_REPRODUCER.rs`. Final R4 makes both cases mandatory LOCAL-01
gates: baseline and candidate must be run, and each candidate must become a
fully finite success or an existing authorized typed failure through the real
carrier/PyO3 mapping. Any safety repair is a separate commit above the frozen
telemetry delta; ambiguous error authority is a blocker.

This R2 package is a non-authoritative execution addendum subordinate to the
final `intake_repair_r4/CODEX_HANDOFF.md` and `REMOTE_PUBLICATION.json` v5. Read
those exact remote bytes first, then use `LOCAL_ONLY_PROMPT.md` on the machine
that contains the preserved local Git objects. Stop immediately if either
object or the exact RED tree is absent. Do not begin LOCAL-02 until every
LOCAL-01 acceptance item passes.
