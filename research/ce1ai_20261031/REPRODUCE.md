# CE1AI original source source-cell response: deterministic reproducibility

## Git inputs

Pin parent Draft PR #287 HEAD `c7660436f233bfe94d954146017059fd79385dd5`. New CE1AI code must live **only** in `research/ce1ai_20261031/`, and CI in `.github/workflows/ce1ai-sixcell-source-response.yml`. It imports original `research/ce1af_20261030/input/cellwise_gl_rust.py` (source SHA256 `022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035`) and existing `research/ce1ah_20261031/source/ce1ah_tangent.py` without modifying either. The six source cells are original positive dyadic binary64 masses, and 5 physical independent source directions + 1 dependent dark direction are **new** conditional initial-data families.

Python 3.13 with NumPy 2.3.5, SciPy 1.17.0, pytest 9.0.2, matplotlib 3.10.8:

```bash
python -m pip install numpy==2.3.5 scipy==1.17.0 pytest==9.0.2 matplotlib==3.10.8
python research/ce1ai_20261031/source/certify_dark_initial_jet.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python research/ce1ai_20261031/source/ce1ai_source_response.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -m pytest -q research/ce1ai_20261031/source/test_ce1ai.py research/ce1ai_20261031/source/test_dark_jet.py
python research/ce1ai_20261031/source/plot_ce1ai.py
python -m compileall -q research/ce1ai_20261031/source
```

For inherited controls, ensure the **derived uncompressed** parent CSV exists (restore exact sha-frozen original gzip only if missing):

```bash
python research/ce1af_20261030/source/shear_work_physics.py
python -m pytest -q research/ce1ah_20261031/source/test_ce1ah.py research/ce1af_20261030/source/test_ce1af.py
```

`CE1AI_SOURCE_TANGENT_PHYSICAL.csv` = `3 GL×401 time×6 source modes = 7218 rows`; `CE1AI_BASELINE_PHYSICAL.csv` = `3×401=1203`; `CE1AI_FINITE_FAMILY_PHYSICAL.csv` = `2 GL×401×6×2 signs=9624`; `CE1AI_HARMONIC_RESPONSE_SINGULAR_VALUES.csv` = `3×401=1203`; 7 actual physics PNGs. `CE1AI_EXACT_DARK_INITIAL_JET_CERTIFICATE.json` is pure rational continuum source analysis, **not** a time-sampled ODE. No hidden source smoothing.

**Numerical comparison:** compare source identity as SHA-256 exact, old frozen GL6/8 41-time records and prior CE1AH 401-time baseline in physical variables. Numeric data from different CPU/SciPy versions compare with the justified original tolerance (not hardcoded generated CSV hash). Snapshot/packaging SHA can be checked exactly for a frozen archive. No angular-continuum integration error bound or observational likelihood is claimed.
