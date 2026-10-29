# CE1-V reproducible scientific execution

Python 3.13, numpy 2.3.5, scipy 1.17.0, pytest 9.0.2, matplotlib 3.10.7. No external new spectra or observed data. Original source binary64 cells and actual coupled 41-epoch CE1-U GL6/8 CSVs are archived under `inputs/` with SHA256 checked at read.

From the extracted package root (with `BASS_CE1V_TWO_TIME_20261030` directory):

```sh
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
python source/build_crosstime.py --source-dir inputs --out-dir data
python -m pytest -q tests/test_two_time_physics.py
python -m compileall -q source
python source/plot_crosstime.py
```

Expected source hash checks: GL6 `6eff8cd9f31d027bbee55720332302b6fbad71b3639b5809aab6b9ce6f53e489`; GL8 `1398980ec71662494273e05eb4bd52a78f6e6c7f208702638da6c739698f7502`; CE1-U source archive `d3f0e8196dc0a4a466cfc1932ed0d9385bcc79175773a5f9ecaee69871527fa4`.

Scientific comparisons: `data/RESULTS.json`, `GL{6,8}_two_time_1681.csv` (two real physical 41×41 matrices), `GL{6,8}_two_time_rotation_average.npz` (full 181-angle l=2/4 truncated correlation cubes), and `figures/*.png`. CI may only compare content/numerical tolerances, not canonical ZIP byte identity unless archived bytes are explicitly locked. Do not treat GL6/8 agreement or PR265 conditional four-panel bound as certified two-time kernel error.
