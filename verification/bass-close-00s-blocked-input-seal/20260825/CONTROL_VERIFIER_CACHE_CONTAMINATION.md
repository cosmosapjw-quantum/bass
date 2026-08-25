# Control-verifier cache-contamination record

The first final verification used a previously exercised temporary extraction
and failed closed with:

```text
FAIL: unmanifested file scripts/__pycache__/verify_package.cpython-312.pyc
```

That file was a Python bytecode cache created by an earlier verifier run, not
an entry in the immutable control ZIP. The original control ZIP's manifest had
already passed. A fresh extraction of that exact ZIP subsequently produced:

```text
BASS_CLOSURE_PACKAGE_VERIFY_PASS files=47 tasks=16 claims=12 risks=12
BASS_SCIENTIFIC_CLOSURE_AUDIT_CODEX_PLAN_VERIFY_PASS
```

Classification: deterministic generated cache contamination. It does not
alter the ZIP bytes, candidate physics, or the blocked-input adjudication.
