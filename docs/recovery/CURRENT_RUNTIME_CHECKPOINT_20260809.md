# BASS current-runtime recovery checkpoint

- Recorded: 2026-08-09
- Target repository: `cosmosapjw-quantum/bass`
- Working branch: `agent/longrun-checkpoints`
- Remote baseline: `d9e5ba7577ccb05b648b11ea7ac991bf6e09d8b9`
- Classification: `PARTIALLY_RECOVERED / IMPLEMENTATION_MISSING_OR_MASKED`

## Durable state now preserved

- 15 attached input identities in `manifests/PROJECT_SOURCE_SHA256_20260809.txt`.
- 72-file immutable harness in `harness/BASS_v1_background_highl_harness/`.
- 18-file historical partial overlay in
  `recovered_sources/legacy_partial/bianchirustcoreRDAGcomplete/`.
- Task 3–10 conversational evidence in
  `docs/recovery/TRANSCRIPT_TASK3_10_STATE_20260809.md`.
- Full search scope, outcomes, limitations, and validation in
  `docs/recovery/RECOVERY_REPORT_20260809.md`.

The harness is not a solver: its own manifest declares `solver_code_included=false`. The
partial overlay is quarantined and is not installed into a production package namespace.

The preserved immutable `docs/HARNESS_AUDIT_REPORT.md` contains stale prose saying OD0 was
completed. The source bundle identifies that sentence as a known quarantined defect. It is
not authorization: `state/gates.json` says `G-OD0=BLOCKED`, while `state/run_state.json`
keeps OD001–004 pending and has no OD0 authorization receipt. Machine state takes precedence.

## Unresolved implementation locators

`3347547`, `eaf13af`, `4e1a3b6`, `54fb3bf`, `29327f9`, `e993691`, `6d786e1`, and
`c3d45f3` remain `TRANSCRIPT_ONLY`. None resolves in a visible local object store, the
current public branch history, or the GitHub commit endpoint.

The original scratch-root `.git` is currently hidden by an empty read-only tmpfs. An object
store behind that mask cannot be inspected from this namespace, so the implementation is
classified `MISSING_OR_MASKED`, not proven destroyed.

## Verification boundary

- Recovered harness and overlay bytes match their source archives exactly.
- Harness governed-file manifest: 71/71 OK.
- Harness path-sensitivity control: validator PASS and 38/38 unit tests PASS at the exact
  recorded execution path; expected fail-closed after repository relocation.
- Recovered Python files: 4/4 compile in memory.
- Supplied Rust 1.94.1 toolchain: offline Cargo metadata PASS; offline tests stopped before
  compilation because `nalgebra` was absent from the empty temporary dependency cache.
- Partial-overlay Python tests: pytest unavailable and complete baseline absent.
- Remote tag advertisement: zero rows with successful `git ls-remote --tags`; server-side
  unreachable objects remain non-enumerable.
- No Task 3–10 production solver code was executed or scientifically validated.

## Checkpoint policy

1. `main` remains the integration target; recovery work is preserved on
   `agent/longrun-checkpoints` by fast-forward only.
2. WIP preservation never promotes a scientific claim.
3. Missing stages require observed RED, fresh GREEN, cumulative regression, and independent
   review before they may be called recovered.
4. Push after each approved task or fix round and checkpoint at runtime boundaries.
5. Do not commit credentials, caches, vendor toolchains, or unreviewed large binaries.

## Next safe boundary

First seek an authorized read-only export of the object store hidden behind the `.git`
tmpfs or another external checkout/bundle. If unavailable, obtain the complete canonical
Python baseline and reconstruct from Task 3 forward. Task 10 must not be resumed as if its
65 focused transcript-only tests constituted a final reviewed checkpoint.
