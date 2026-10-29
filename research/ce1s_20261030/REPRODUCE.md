# BASS CE1-S reproduction from immutable physical-source ZIPs

Unzip the CE1-S full source archive to one directory. Python 3.11+, NumPy, pytest, matplotlib needed for optional figures. No Rust compiler needed to reproduce new CE1-S postprocessing **because the original BASS-native Rust model output is preserved**; to regenerate the upstream Rust Liouville output itself, see PR #261 CI workflow and its fixed original source pins.

```bash
python source/generate_fractional_sky.py \
  --rust-ci input/CI_PR261_4CHANNEL_ATLAS_PINNED.zip \
  --ce1p-zip input/CE1P_SOURCE_PINNED.zip \
  --ce1q-zip input/CE1Q_SOURCE_PINNED.zip --out data
python -m pytest -q tests/test_fractional_sky.py
python -m compileall -q source tests
python source/plot_fractional_sky.py data figures
```

Expected exact source ZIP SHA256: CI `21fe3b9b91b9de4e23f80fb5cba4df4b56b44b3c388bcb6999df9ad838231aa9`; CE1-P `162097533f0bc88ec5ddee8f10edcc08aaf4b81cbf2e4c14c42982dbf73ca6b7`; CE1-Q `cc4d9cba73e4e290d2b44d892b151a429d84d6db157f029dade4c929d9183042`. Invalid/mutated archive is rejected before computation.

NOTE: `CI_PR261_4CHANNEL_ATLAS_PINNED.zip` has stored_ref8, stored_ref16, gl24, gl40, NOT stored_ref1/ref4. 164 rows, not 246. This is the real source-locked physical atlas generated in BASS Rust CI; synthetic-only previous tests are not counted as physical input.
