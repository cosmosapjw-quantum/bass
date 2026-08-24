# Receipt — BASS-8B.2B.1 pure-Python exact-E2-parity seal

## Package and architecture

- Package SHA-256: `17aae4fb3bd704afda0db71c3398801b6457651cc9e87010033265195a0f4cce`
- Decision: pure-Python NumPy/SciPy/SymPy/pytest frontend with the locked Rust
  backend; JAX, JAXlib, Equinox, and Diffrax are not target dependencies.
- The exact ZIP is preserved unchanged under `archive/`; its sidecar verifies.

## Evidence summary

- Candidate internal manifest: **71/71** files verified.
- Self-contained test suite: **20/20** passed.
- Candidate physics: **17/17** passed.
- Candidate-vs-E2 parity: **5/5** passed.
- E2 predecessor: **13/13** passed, with **16 subtests** passed.
- Final marker: `BASS8B2B1_EXACT_E2_HOST_PARITY_PASS__PURE_PYTHON_FRONTEND`.
- The pure-Python owner-import receipt is present and the owner files remained
  unchanged (the replay checks their fixed SHA-256 values before and after).

The supplied raw transcript records the candidate and parity passes as their
17-dot and 5-dot pytest lines, respectively; the current permitted replay
reproduced those same lines and the final marker.

The historical browseable logs and Markdown evidence are byte-preserved. Their
inherited trailing whitespace is path-scoped as whitespace-ignored in
`.gitattributes`, allowing `git diff --check` to validate authored seal content
without rewriting evidence.

## Verification commands

```text
sha256sum -c archive/BASS8B2B1_DIRECTION_DEPENDENT_RATE_DUAL_PUREPY_CANDIDATE_20260824.zip.sha256
sha256sum -c browseable/MANIFEST.sha256
python -B -m py_compile <all browseable Python files>
python -B browseable/verify_package.py
python -B -m pytest -q -p no:cacheprovider browseable/tests/test_direction_dependent_rate_dual.py
browseable/host_replay/run_from_repo_checkpoint.sh /home/cosmosapjw/bass
```

The executable source/host-replay import scan found no `import jax`, `import
jaxlib`, `import equinox`, or `import diffrax`. Documentation and hostile
negative tests were outside that active-target scan.

## Scope boundary

Row 7, row 8, BASS-3, production runtime, and Join J1 remain blocked.
BASS-8B.2B.2 was not started. No frozen E1/E2 owner files, predecessor tests,
expected owner hashes, candidate physics, or numerical tolerances were changed.
