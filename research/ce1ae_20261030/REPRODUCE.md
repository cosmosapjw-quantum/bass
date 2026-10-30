# CE1-AE independent reproduction

Execute from the GitHub repository working tree where `research/ce1ae_20261030` is present.

Pinned scientific runtime for remote CI: Python 3.13, NumPy 2.3.5, SciPy 1.17.0, mpmath 1.3.0, pytest 9.0.2 (actual CI logs must confirm status before PASS claim).

```
python research/ce1ae_20261030/source/spectral_gap_certificate.py
python research/ce1ae_20261030/source/continuous_kernel_physics.py
python research/ce1ae_20261030/source/certify_dyadic_integral_surrogate.py
python -m pytest -q research/ce1ae_20261030/source/test_ce1ae.py
python research/ce1ae_20261030/source/plot_physics.py
```

Inputs are immutable original code `input/cellwise_gl_rust.py`, 41-state saved DOP853 GL6/GL8 original physical geometry, frozen GL6/8 l4 timejets, CE1-AD raw conditional spectral gate. `frozen_source_identity` asserts original six exact binary64 positive cell SHA. Any mismatch is fatal.

Outputs: 1604 newly evaluated source-locked 6D Einstein–Vlasov time records, continuous-time deterministic Simpson Gram spectrum/physical energy powers, 41-Hermite and 1601-time numerical comparisons for GL6/8, exact-rational physical conditional spectral-gap witness, exact dyadic Simpson surrogate SPD witnesses, plots. Strict physical continuum lower **does not** come from Simpson, which is diagnostic only.

No original SHA, previous PR, main, user machine, or 1e-5 h target should be modified. Run all tests and inspect branch HEAD before publication.
