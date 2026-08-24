# BASS-8B.2B.1 pure-Python parity patch ledger

## Observed failure

The candidate package and its 17 focused tests passed.  Archive reconstruction,
ZIP CRC, outer hash, and frozen E2 owner hashes also passed.  The first exact
host-parity boundary failed in the bootstrap import smoke test:

```text
ModuleNotFoundError: No module named 'jax'
```

The failing command explicitly included `jax` in the required import list.
Normal import of the preserved legacy `bianchi` package would also execute a
JAX-enforcing root initializer.  Neither behavior belongs to the bounded E2
rate authority.

## Root cause

The verification adapter conflated two layers:

1. the exact NumPy E2 `electron` / `electron_rate` authority slice;
2. the historical full-package runtime initializer and its JAX backend policy.

The E2 predecessor test already demonstrates that the rate slice is intended to
run without the optional JAX/Rust stack through an isolated loader.

## Bounded patch

Changed:

- `host_replay/pure_python_e2_loader.py` — new fail-closed isolated loader;
- `host_replay/test_exact_e2_rate_parity.py` — explicit loader binding;
- `host_replay/run_exact_e2_host_parity.sh` — no JAX import, no legacy root on
  `PYTHONPATH`, new pure-Python success marker;
- `tests/test_pure_python_e2_loader.py` — RED/GREEN loader tests;
- package verifier and decision/architecture documents.

Unchanged:

- E2 `electron.py` and `electron_rate.py`;
- E2 predecessor tests and expected owner hashes;
- BASS-8B.2B.1 physical formulas and tolerances;
- BASS-8B.2B.0 carrier;
- rows 7–8, BASS-3, solver/runtime, and production wiring.

## Verification so far

```text
candidate physical tests       17/17 PASS
pure-Python loader tests        3/3 PASS
all self-contained tests       20/20 PASS
optional-stack import AST gate PASS
package initializer bypass     PASS on hostile synthetic package
missing-owner fail-closed      PASS
contaminated-import fail-close PASS
```

Exact restored-E2 host parity remains the next required gate.
