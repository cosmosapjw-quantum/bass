# Local Codex prompt — BASS-8B.2B.1-R1 pure-Python exact E2 parity

Work from `~/bass`.  The active architecture decision is:

```text
pure-Python frontend/reference/validation + Rust backend
JAX/JAXlib/Equinox/Diffrax excluded from the current target
```

Do not install JAX to make a legacy package initializer importable.  The
preserved E4 archive is read-only authority, not the current frontend
architecture.

## Goal

Execute the prepared exact E2 host-parity gate through the isolated
pure-Python loader.  Diagnose only the first failure if any and apply at most
one bounded host-adapter patch.  Do not modify E2 owners, predecessor tests,
candidate physics source, expected hashes, or the BASS-8B.2B.0 carrier.

## Commands

```bash
cd /path/to/extracted/BASS8B2B1_DIRECTION_DEPENDENT_RATE_DUAL_PUREPY_CANDIDATE_20260824

TERM=xterm ./run_all.sh

./host_replay/run_from_repo_checkpoint.sh ~/bass \
  2>&1 | tee /tmp/bass8b2b1-purepy-e2-host-parity.log
```

Required success marker:

```text
BASS8B2B1_EXACT_E2_HOST_PARITY_PASS__PURE_PYTHON_FRONTEND
```

Expected gates:

```text
candidate physics tests             17/17
pure-Python loader tests             3/3
candidate-vs-E2 parity               5/5
E2 predecessor suite                13/13
owner hashes before/after            identical
legacy bianchi package initializers  not executed
optional JAX stack                    not imported
```

## Failure classes

```text
ARCHIVE_INTEGRITY_FAILURE
E2_OWNER_HASH_MISMATCH
PURE_PYTHON_LOADER_FAILURE
OPTIONAL_STACK_IMPORT_ATTEMPT
CANDIDATE_FOCUSED_TEST_FAILURE
E2_RATE_PARITY_FAILURE
E2_PREDECESSOR_REGRESSION
OWNER_MUTATION_FAILURE
```

## Allowed patch surface

Only:

- `host_replay/pure_python_e2_loader.py`;
- host replay shell/bootstrap code;
- verification-only tests and receipts.

Forbidden:

- installing or adding JAX dependencies;
- editing frozen E2 owner source or predecessor tests;
- changing candidate physical formulas or expected hashes;
- weakening parity tolerances;
- starting 2B.2, rows 7–8 promotion, BASS-3, runtime wiring, PR, merge, or tag.

On success, preserve a timestamped receipt containing environment, package and
owner hashes, loader receipt, full logs, and before/after hashes.  Stop after
reporting the bounded result.
