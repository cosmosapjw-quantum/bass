# CE1-AF exact scientific reproduction

From BASS Git checkout at a pinned CE1-AF PR commit, run:

```bash
python -m pip install numpy==2.3.5 scipy==1.17.0 pytest==9.0.2 matplotlib==3.10.8
python research/ce1af_20261030/source/certify_initial_shear_work.py
python research/ce1af_20261030/source/shear_work_physics.py
python -m pytest -q research/ce1af_20261030/source/test_ce1af.py
python research/ce1af_20261030/source/plot_ce1af.py
python -m compileall -q research/ce1af_20261030/source
```

Entrypoint is strictly source-locked. Original six-cell `input/cellwise_gl_rust.py` reused from CE1-AE original exact Git blob; frozen GL6/GL8 41 states SHA locked in `shear_work_physics.py`; parent `CE1AE_PARENT_C4_DENSE.csv.gz` exact SHA-256 locked in plotting module and cross-checked. Rechecks the exact SHA-locked `data/CE1AF_PHYSICAL_TIMELINE.csv.gz` snapshot by scientific values, not raw CSV cross-run bytes. Generates **1604 new 6D Einstein–Vlasov states × 43 fields**, exact dyadic cell initial shear-work rational lower, three source-science figures, and actual physics/evidence JSON. The input gz is *not* an independently recomputed l4 numerical certification.

No source mutation, spectral-gap rebinding, model entropy claim, general Bianchi implementation, observational likelihood, or merge. `UPPER_DAG=9/15`, `CE1=PARTIAL`, production HOLD. Source CSV numeric outputs may differ at last floating bits across platforms; compare physics, not byte identity, and never widen an inherited tolerance.
