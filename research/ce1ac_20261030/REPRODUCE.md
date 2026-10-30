# CE1-AC deterministic scientific reproduction

Requirements: Python 3.11+, numpy, scipy, pytest. No GPU/MPFR needed. Proof is integer rational fixed-point interval with 80 decimal digits, π via exact Machin arctan rational remainder and sqrt2/H0 via integer sqrt. Baseline original positive six-cell source must satisfy exact `frozen_source_identity()` SHA256 `022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035`. It must be the exact copied `cellwise_gl_rust.py` in `original_source/`.

From archive root:

```bash
export OPENBLAS_NUM_THREADS=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
python source/initial_jet_certificate.py
python source/l4_kinematic_history.py
python -m pytest -q tests/test_scoped_physics.py
python -m compileall -q source tests
```

Results:
- `data/ORIGINAL_CONTINUUM_L4_JET_INTERVAL.json`: exact interval rank3 proof for original *continuum angular cell* and true local IVP via initial jets, no numeric ODE.
- `data/GL6/GL8_ORIGINAL_L4_TIMEJET_41.csv`: 82 initial-history normalized multipoles and first/second proper-time jets, pressure/E diagnostics.
- `data/GL6/GL8_ORIGINAL_L4_K4_TIME_DERIV_1681.csv`: 3,362 two-time physical kernel/derivative values, sample-specific, not continuum certified.
- `data/GL6/GL8_L4_TIMEJET_SUMMARY.json`: fractional vs absolute-energy multipole sign and numerical 41-sample third mode.

Scope: `UPPER_DAG=9/15`, `CE1=PARTIAL`, production, merge, automatic successor prohibited. New exact-continuum *qualitative* rank3 theorem does not by itself provide sampled Gram λ3 positivity or quantitative continuous-time spectral gap. True distinct-author R6/C9 NOT_RUN.
