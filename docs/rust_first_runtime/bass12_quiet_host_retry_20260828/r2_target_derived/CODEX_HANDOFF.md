# BASS-12R2 handoff

Local artifact: `BASS12_TARGET_DERIVED_HARNESS_RETRY_R2_20260828.zip`

```text
size     17464
SHA-256  175e010021d42e954b829cb9e5653e94d2cb6c946812526f3c4bbb0cecb2342d
```

Verify the ZIP, its internal manifest, package verifier, and eight package tests. Then follow the extracted `CODEX_HANDOFF.md` once.

Read `ROOT_CAUSE.json`, `TYPED_IDENTITY_POLICY.json`, and `WORK_UNIT.json` first.

The old R1 harness digest is retired plan metadata. The active harness identity is derived from the immutable target Git object at commit `efb3a45986820659e5bcbec2677729f28616e736`. Candidate source/test bytes and frozen scientific input/output remain hard-bound. Historical native binary hashes are record-only when one attributable environment is used consistently across both paired populations.

Run one real quiet-host gate. On PASS, run the 1T and 12T populations once each. Do not modify Candidate B, PR #23, PR #36, BASS-13, or main.
