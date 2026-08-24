# BASS execution architecture decision — pure-Python frontend + Rust backend

**Date:** 2026-08-24  
**Status:** active project constraint for the current development DAG

## Decision

```text
frontend / orchestration / validation: pure Python (NumPy/SciPy/SymPy/pytest)
numerical backend / hot loops:         Rust 1.94.1, locked and offline-capable
JAX / jaxlib / Equinox / Diffrax:       excluded from the current target
```

JAX is not a required dependency, optional runtime, CI requirement, parity
requirement, or accepted source of numerical authority for the current BASS
path.  It may be reconsidered only through a new explicitly approved research
node; it must not re-enter transitively through a package initializer.

## Consequences

1. Python owns configuration, typed physical contracts, provenance, reference
   implementations, plots, tests, and Rust binding/orchestration.
2. Rust owns performance-sensitive collision, transport, linear algebra, and
   time-stepping kernels after same-physics parity gates are available.
3. A preserved legacy authority archive may contain JAX-coupled package roots.
   Such archives remain read-only evidence.  Bounded NumPy authority slices are
   imported through an isolated namespace loader that does not execute the
   legacy package initializers and fails if an optional-stack import is tried.
4. No production or verification command may silently install JAX merely to
   pass an import smoke test.
5. Performance claims compare pure-Python reference and Rust backend under the
   same equations, carrier, tolerances, inputs, and outputs.

## Current bounded application

`BASS-8B.2B.1-R1` needs only the frozen E2 `electron.py` and
`electron_rate.py` NumPy authority.  The exact E2 predecessor test already
contains a focused no-optional-stack loader.  The candidate parity harness now
uses the same policy through `host_replay/pure_python_e2_loader.py`.

The loader stubs only dependencies that are outside the E2 rate gate:

- `bianchi.thermo.history_api`: exact frozen constants consumed by E2;
- `bianchi.q.comoving.collide_log`: fail-closed, collision kernel out of scope;
- `bianchi.q.coupled.mat3`: exact reshape helper required at import time.

Owner source, owner hashes, rate formulas, parity expectations, and predecessor
tests are unchanged.

## Hard boundary

This decision does not promote rows 7–8, complete the moving projector, start
BASS-8B.2B.2, start the VI0 classifier, or wire a production solver.
