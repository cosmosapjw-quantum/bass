# CE1-Y reproducibility

Require Python 3.11+ with numpy and pytest, scipy is NOT required to regenerate the fixed saved 41×41 kernels. The original CI-produced Rust CSV evidence and two DOP853 history CSVs are included byte-for-byte in input/.

```sh
python source/generate_rk4_k4_transfer.py
python -m pytest -q tests/test_ce1y_physical.py
python -m compileall -q source tests
python source/plot_physical.py
```

Each original input filename and SHA is documented in data/SCIENCE_RESULTS.json. This package does not need a compiler, a cloned GitHub checkout or external dependencies besides Python/numpy/matplotlib/pytest to reproduce the **numerical analysis of saved native Rust data**. To regenerate raw original Rust sky and MPFR192 source/time certificates, use PR270 pinned CI #40991211526, the exact original BASS Rust and its verified source tree.

The six output CSVs list all proper-time pair observations and mathematical **functional** source+geometry bounds, not formally verified intervals around the printed binary64 center or DOP853. A user must not rename them as observed CMB or unqualified likelihood data.
