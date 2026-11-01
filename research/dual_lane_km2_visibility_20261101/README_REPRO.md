# BASS KM2 source-owned normal-clock Thomson visibility

This is an executable, S2 source-input-backed local scientific calculation. It does **not** include a fresh Einstein-P8-Peebles solve; it reuses exactly four immutable KM2N/KM2L original NPZ arrays validated by SHA256. `source_inputs/` holds those four original arrays. `SOURCE_MANIFEST.json` contains their exact individual SHA256 and external S2 original PR reference. All original source arrays are read-only and never mutated.

Tested with Python 3.13, NumPy 2.3.5, SciPy 1.17.0, Matplotlib 3.10.8; reproduce with:

```sh
python source_visibility.py --output results
python -m unittest -v test_visibility.py
python -O -m unittest -q test_visibility.py
python make_plots.py
```

The repository CI route can fetch the exact original GitHub artifact #13035232055 (KM2N workflow #41181695902), then `python restore_pinned_km2n.py --artifact artifact.zip --dest .` verifies outer/inner and four original NPZ byte SHA256 before computing. The remote artifact expires eventually; preserve this local/source-inclusive ZIP and external Drive/Library backup for future restoration.

Reconstructed `g(u,n|U)=h(u,n) exp[-(tau(U,n)-tau(u,n))]`, with original `h=n_H x_e sigma_T c Tstar D`, describes a line-of-sight Thomson transfer kernel **per unit normal time u**, with probability `1-exp(-tau(U))`. The conditional median is for a photon existing at u=0, not a full emission-weighted or observed CMB last-scattering distribution. Original CE1AS PR #307 is different collisionless Einstein source, and source-matching is unresolved.

Scientific claim: finite GL12/GL16 original source-conditional visibility with positive probabilities and independent rate-integrated opacity and Wolfram constant-h exact identity. NOT a continuum convergence enclosure, measured data, production readiness or upper-DAG closure.