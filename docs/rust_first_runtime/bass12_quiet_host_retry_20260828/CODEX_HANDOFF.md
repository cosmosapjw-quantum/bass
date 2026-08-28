# Codex handoff — BASS-12R2 target-derived retry

The previous R1 archive is preserved as historical evidence but is no longer the
active execution package. Its benchmark-harness checksum was stale and caused a
false `BLOCKED_HOST_OR_ENVIRONMENT` before any host snapshot or timing run.

Active package:

```text
docs/rust_first_runtime/bass12_quiet_host_retry_20260828/
r2_target_derived/
```

Read `r2_target_derived/ROOT_CAUSE.json`, then materialize, verify, and execute
`r2_target_derived/CODEX_HANDOFF.md`.

Required package markers:

```text
PASS_BASS12_TARGET_DERIVED_RETRY_R2
8 tests / OK
```

The immutable Candidate B source/test bytes and scientific input/output digests
remain hard-bound. The benchmark harness is derived from the frozen target Git
object. The retired R1 harness checksum and historical native-build hashes are
provenance metadata, not scientific admission gates.

Execute exactly one quiet-host preflight. Only if it passes, execute one strict
1T population and one physical 12T population. Do not create another planning,
audit, or review package.
