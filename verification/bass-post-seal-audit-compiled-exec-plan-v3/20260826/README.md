# BASS post-seal audit-compiled execution package v3

This directory contains a checksum-addressed split deterministic ZIP package and is the machine-readable successor to the old blocked-input v2
plan. It is compiled from the current fresh-content seal at `d6a0b63fac09c3a6d0c9071206f0d51f01953341` and
the supplied Universal Audit-Compiled Execution guide.

## Verify

```bash
cd verification/bass-post-seal-audit-compiled-exec-plan-v3/20260826
sha256sum -c MANIFEST.sha256
./UNPACK_AND_VERIFY.sh
```

Required marker:

```text
BASS_POST_SEAL_AUDIT_COMPILED_PLAN_V3_VERIFY_PASS
```

## Read order

1. `CURRENT_STATE.json`
2. `SOURCE_PRECEDENCE.json`
3. `P0_P1_POLICY.md`
4. `AUDIT_COMPILED_EXECUTION_CONTRACT.md`
5. `P0_P1_THREAT_CATALOGUE.jsonl`
6. `INVARIANT_TEST_MATRIX.jsonl`
7. `DAG.json`
8. the selected `WORK_UNITS/*.json`
9. `CODEX_HANDOFF.md`

## Current launch split

- Current Codex implementation context: execute **WU-004 AC-01 only**.
- Separate fresh Codex context: execute **WU-001 BASS-9 only**.
- Control-plane operator: WU-000 may run in parallel.
- WU-002 remains blocked until WU-000 and WU-001 pass.

No PR, merge, tag, authority promotion, classifier, runtime, Rust, solver,
fitting, or `main` mutation is authorized by this package.
