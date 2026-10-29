# Reproduce the bounded CE1-OBS numerical unit

Python >=3.11, NumPy, SciPy, pytest. No new Einstein–Vlasov integration, spectrum or polarization.

Source authority: CE1-P source ZIP `BASS_CE1P_PHYSICAL_HISTORY_20261029_FINAL.zip` SHA256 `162097533f0bc88ec5ddee8f10edcc08aaf4b81cbf2e4c14c42982dbf73ca6b7` available in the user-provided Drive link. Unzip into `PARENT_DIR`, preserving MANIFEST.json, source and data paths. The generator checks the ZIP sha, *all* parent manifest member hashes, and the input binary64 hash before producing results. If checked out inside the stacked GitHub branch, `PARENT_DIR=research/ce1p_20261029` is also possible: however the verified original ZIP must still be supplied.

```
python source/generate_observer_sky.py --parent "$PARENT_DIR" --source-archive "$SOURCE_ZIP" --output ./
python -m pytest -q tests/test_observer_sky.py
python -m compileall -q source tests
```

Pytest tests accept `CE1P_PARENT_DIR` and `CE1P_ARCHIVE_PATH` env variables; otherwise the local source_package layout from the original execution is used. The generated outputs are `data/results.json`, `data/multipoles_all_histories.csv` (246 rows), `data/gl40_observer_sky_positive_octant_u008.csv` (9,600 positive-octant nodes; reconstruct full sky with eight independent sign flips), and `generation_stdout.json`. The test file confirms the outputs. Exact CSV bytes may depend on Python/NumPy/SciPy environment; scientific and source identities are separately checked.

At each GL node the eight reflected rays carry equal weights. `J_obs` is per observed steradian in dimensionless energy normalization; `energy_total8_node` already includes the combined eight octants. NEVER sum both `energy_total8_node` and its `8*J_obs*dOmegaObs_oct_node` representation together.

Source repo PR #258 is left open/unmerged. Scientific claim remains a non-certified Bianchi-I collisionless unpolarized observer-frame angular-energy sky, NOT CMB temperature/polarization/likelihood.
