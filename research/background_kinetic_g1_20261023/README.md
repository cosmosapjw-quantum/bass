# G1A: fixed-scale Einstein + positive collisionless packets

Read REPORT_KO.md, THEORY.md and DAG.json. This is an opt-in research unit stacked
on BASS PR182; neither production dispatch nor the parent source is changed.

Dependencies actually observed: Python3.13.5, NumPy2.3.5, SciPy1.17.0,
pytest9.0.2. Plotting additionally uses Matplotlib. No JAX, native BASS extension,
network API, or Rust compiler is required by this new unit.

From this directory:

```sh
python verify_saved.py
# Only to reproduce changed scientific inputs, with a fresh output path:
python -m pytest -q test_packets.py
python run_controls.py evidence/new_reproduction
```

The saved verifier does not integrate, render, or replay old test suites. The
campaign refuses to overwrite an existing output directory. Its 18 histories
include17 valid finite controls and1 intentionally wrong Class-B weight evolution.
`plot_controls.py` consumes `evidence/controls_001`; it refuses to overwrite existing
PNGs. Full archive includes code, original vendor bytes, rawNPZ, figures, CSVs,
actual failures and receipts. Git selected publication may omit rawNPZ; restore the
full stage archive before `verify_saved.py` if those files are absent.

The public entry points are `moments`, `flow`, `boost`, `fd_packets` and
`CoupledPackets`. The normal-frame kinetic input is a positive finite measure,
not a universal perfect-fluid closure. Cosmological initial constraints are not
projected away. G1B smooth-source refinement, all collision/emitter energy-momentum
partners, production/restart integration and global convergence remain separate.
