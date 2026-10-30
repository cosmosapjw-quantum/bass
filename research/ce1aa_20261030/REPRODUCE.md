# CE1-AA source-locked local recreation

1. Original source frozen: SHA256 `022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035`, exact positive six cells, GL6/8 ray/mass SHA values asserted in `source/mpfr192_sky.py`.
2. Original DOP853 41-row GL6, GL8 input binaries in `input/`. Their file SHA is verified before any source computation. Original PR270 exact real `l4_source_and_transfer.json` likewise included, and the proof conditions apply for 0<=ell_i<=.08.
3. Runtime: Linux x86-64 with `libmpfr.so.6`, Python 3.13, numpy 2.3.5, mpmath 1.3.0, pytest 9.0.2, matplotlib optional. MPFR precision=192 bits. No `float` string source smoothing, no source renormalization.
4. Commands from this package root:

```bash
python source/interval_k4_spectrum.py
python -m pytest -q tests/test_mpfr192_physics.py
python -m compileall -q source tests
python source/plot_physics.py
python source/make_package.py
```

Generated: `data/GL6_mpfr192_source_41.json`, `GL8_mpfr192_source_41.json` (exact MPFR192 hex endpoints), `GL6_MPFR192_K4_1681.csv`, `GL8_MPFR192_K4_1681.csv`, `GL6_CUMULATIVE_41_PREFIX_SPECTRA.csv`, `GL8_CUMULATIVE_41_PREFIX_SPECTRA.csv`, `SCIENCE_RESULTS.json`, figures and evidence.

Important scope: interval evaluates exact source at the **given binary64 DOP853 geometry states**, not a certified solution to DOP853 continuous Einstein–Vlasov IVP. Do not transfer to cosmic evolution or DOP853 trajectory automatically.
