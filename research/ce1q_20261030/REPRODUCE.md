# CE1-Q reproducibility and authority

Source identity is locked to BASS parent PR258 and PR253; reference independent Rust sibling PR257. New code under `research/ce1q_20261030/` is opt-in and must not alter canonical BASS physics.

- Requirements: Python>=3.11, numpy, scipy, pytest, matplotlib, mpmath, MPFR6 runtime and `rustc` >=1.94.
- BASS repository layout contains `_rustcore/src/kinetic/comoving.rs`, `bianchi/nonperturbative/einstein_tabulated_source.py` and its existing dependencies, with original source Git blob `fdeb83a65cd424786ba6bb8ddadbcb2b2e2d45bf`. The original BASS `Frame` must be imported from its real file. Do not replace this path with a self-written Frame.
- The parent CE1-P data and generator are in `research/ce1p_20261029/` (PR258). Their CSV bytes and source SHA must remain unchanged.

From repo root:

```bash
rustc --edition=2021 -C opt-level=2 -A dead_code \
  research/ce1q_20261030/sky_native.rs -o research/ce1q_20261030/sky_native
research/ce1q_20261030/sky_native --selftest
PYTHONPATH="$PWD" BASS_CE1Q_PARENT="$PWD/research/ce1p_20261029" \
  BASS_CE1Q_RUST="$PWD/research/ce1q_20261030/sky_native" \
  python research/ce1q_20261030/produce_sky.py --output research/ce1q_20261030/data
PYTHONPATH="$PWD" BASS_CE1Q_PARENT="$PWD/research/ce1p_20261029" \
  BASS_CE1Q_RUST="$PWD/research/ce1q_20261030/sky_native" \
  BASS_CE1Q_DATA="$PWD/research/ce1q_20261030/data" \
  pytest -q research/ce1q_20261030/tests/test_sky.py
python research/ce1q_20261030/plots.py \
  --data research/ce1q_20261030/data \
  --output research/ce1q_20261030/figures
```

`--quick` runs only ref8+GL24 and preserves the science contract but does not replace the six-channel full campaign. The Stage ZIPs store individual status receipts, not independent scientific proof. The full local backup can restore the parent CE1P ZIP and the local archived BASS Rust module for independent local testing, but **the archive Rust source differs in Git blob from the live current BASS module**; GitHub CI pins and recompiles the live source. No Rust executable binary in Git commits or scientific acceptance claims.
