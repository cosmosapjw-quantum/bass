# BASS-8B.2B.1 — Direction-dependent rate / dual binding candidate

This package binds the frozen BASS-8B.2A typed electron-state jet and the
BASS-8B.2B.0 generic-vector paired physical carrier to the E2 normal-time
cold-Thomson rate.

Current execution architecture:

```text
pure-Python frontend / reference / validation
Rust backend for performance-sensitive implementation
JAX stack excluded from the current development target
```

Current verdict:

```text
LOCAL_CANDIDATE_GREEN
PURE_PYTHON_EXACT_E2_HOST_PARITY_REQUIRED_BEFORE_BOUNDED_AUTHORITY_PASS
```

The package is not a production solver, does not promote rows 7–8, and does not
start the VI0 classifier.  Run `python verify_package.py` for the self-contained
local checks.  On an exact BASS repository checkout containing the preserved E4
archive parts, run:

```bash
./host_replay/run_from_repo_checkpoint.sh /path/to/bass
```

The host gate deliberately does not import or install JAX.  It loads the frozen
E2 NumPy owner through an isolated, fail-closed package namespace.  A successful
host run must end with:

```text
BASS8B2B1_EXACT_E2_HOST_PARITY_PASS__PURE_PYTHON_FRONTEND
```
