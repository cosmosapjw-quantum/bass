# RF-02C / Legacy Optimization Integration Package

Status: `CURRENT ACTION BASS-11 / POST-CLOSEOUT RECONCILIATION / DRAFT UNMERGED`

Package ID: `BASS-RF02C-LEGACY-OPT-INTEGRATION-20260826-R1`  
Revision: `R2_POST_CLOSEOUT_NATIVE_MERGE_RECONCILIATION_20260827`

The original BASS-11 evidence-only closeout landed at `a94dbe08...`, but PR #35
then merged native generic-vector bytes into the same RF-02C branch at
`c777ebb6...`. That moved the native source after the recorded terminal delta.
At the current head, RF-00 and RF-02B reproduce Python-fixture and Rust
lint/format failures, and the RF-02C preflight still asserts a historical
pre-RF-02C error type.

The current task is therefore not another audit and not a one-commit evidence
patch. It is a bounded two-commit reconciliation:

1. one source/CI/integrated-native-identity repair commit;
2. one deterministic evidence/native-delta commit bound to the exact first
   commit.

No formula, tolerance, state order, event/restart/history semantics,
performance claim, or authority promotion is authorized.

## Validate

```bash
sha256sum -c MANIFEST.sha256
python validate_package.py
python validate_package.py --live
```

## Exactly one next action

Execute `CODEX_HANDOFF.md` against the current RF-02C branch at
`c777ebb68c82aa8b9898f92159c2346a6e8ef892`. Complete BASS-11 only and stop.
