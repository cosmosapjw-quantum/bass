# CE1-AH precise research-code reproduction

## Immutable upstream and source

- Repository: cosmosapjw-quantum/bass
- Immediate parent: Draft PR #286 commit `4d6a5d9c391bbd5aac1a885ff72b4f33f027e28a`.
- Read-only parent CE1-AF file: `research/ce1af_20261030/input/cellwise_gl_rust.py`, Git blob `6d254e9efc95acc1fd2079bd047d40662986d135`.
- Original exact 128-byte `<f8` angular-source arrays SHA256: `022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035`.
- Original CE1AF frozen GL6/8/16 baseline data are read (never rewritten).

## Runtime

Validated with Python 3.11 (or compatible), NumPy 2.3.5, SciPy 1.17.0, pytest 9.0.2, Matplotlib 3.10.8. Source imports the CE1AF *parent* cell maker; no copied/reconstructed spectral source is silently substituted.

```
python -m pip install numpy==2.3.5 scipy==1.17.0 pytest==9.0.2 matplotlib==3.10.8
python research/ce1ah_20261031/source/ce1ah_tangent.py --orders 6,8,16 --epochs 401
python research/ce1ah_20261031/source/plot_ce1ah.py
python -m pytest -q research/ce1ah_20261031/source/test_ce1ah.py
python -m pytest -q research/ce1af_20261030/source/test_ce1af.py
python -m compileall -q research/ce1ah_20261031/source
```

- Original `GL64` CE1AF is inherited and NOT recomputed in this scoped run, though source is unchanged. New response GL6/GL8/GL16 is empirical angular convergence not an interval enclosure.
- Initial `epsilon_A` or `epsilon_B` are **parameters in traceless shear**, not modified original angular source. For FD validation `epsilon=1e-4`, signs ± in separate **nonlinear** 6D Einstein–Vlasov IVPs; tangent 18D system solves both derivatives simultaneously.
- Validation includes 19 new tests, 24 original CE1AF tests, original-saved 401 states agreement, Hamiltonian/tangent Hamiltonian, harmonic polynomial vs SciPy, source tamper rejection, independent finite differences, energy transfer derivative balance.

## Expected outputs and status

- `data/CE1AH_BASELINE_PHYSICAL.csv`: 1,203 rows.
- `data/CE1AH_TANGENT_PHYSICAL.csv`: 2,406 rows.
- `data/CE1AH_FINITE_PERTURBED_PHYSICAL.csv`: 3,208 rows.
- `data/CE1AH_PHYSICAL_RESPONSE_RESULTS.json`: per angular order scientific endpoints, absolute-residual metrics, resource/exact source identity.
- `figures/*.png`: 5 actual scientific visualization files.

`UPPER_DAG=9/15`, `CE1=PARTIAL`, original `SCOPED_R_C=18/20`; distinct-author R6/C9 NOT_RUN; remote CI/backup must be independently verified; no merge/production/auto-next.
