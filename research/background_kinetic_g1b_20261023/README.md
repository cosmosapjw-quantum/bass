# BASS G1B reproduction and evidence

Start with REPORT_KO.md, THEORY.md, CONTRACT.md, RESULTS.json and DAG.json.
The code is opt-in. Parent core/kinetic/freestream bytes are kept in vendor/.
The small symmetric_bridge only changes how six analytic symmetric components
are represented; it does not widen tolerances or project physical moments.

Requirements observed: Python3.13.5, NumPy2.3.5, SciPy1.17.0,
mpmath1.3.0, pytest9.0.2, Matplotlib3.10.8. See requirements-research.txt.

Use one CPU BLAS thread for this vectorized small-tensor workload:

```sh
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
python verify_saved.py
```

The saved verifier reads preserved arrays and hashes only. Do not rerun completed
histories if source/configuration is identical. For an explicitly changed-input
reproduction in a fresh SOURCE-ONLY copy (not a full archive re-extraction):

```sh
mkdir -p evidence
python -m pytest test_smooth.py test_curved.py -q
python run_frozen.py
python run_curved.py
python run_time_control.py
python plot_results.py
python repair_fixed_figure.py
```

The frozen and time/plot drivers refuse overwrite of existing named evidence.
Move to a separate new copy or deliberately select a new output path for changed
work. Do not delete old evidence to make a replay appear new. run_curved --output
supports new locations; the other scripts have source-local output locations.
The archive contains raw NPZ, source-bound receipts and all preserved failures.
Git selected publication is not a claim that all raw binary evidence is in Git.

Both rho/flux ledger mismatch and constraints computed from actual kinetic moments
are required. Constraint preservation alone is not microscopic validation.
No collision, spectral response, production default or global error certificate.
