# Original BASS high-z H-only Saha Type-II optical-depth research slice

Protected original main: 9c6506e4e2087129a8b674ff10438e5db1a55c9d
Frozen input parent PR327: 97359596c3d640d5ad306e2285b248a5105cf40e
Original 401x26 normal-ray CSV sha256:
9f1400588d39ba3a61020542e14b0e372c8e9be1af130f8c64ed8829b23ad217

Run from repository root:
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 python3 research/typeii_conserved_saha_20261102/source_saha_transport.py
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 python3 research/typeii_conserved_saha_20261102/independent_referee.py
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 python3 research/typeii_conserved_saha_20261102/first_scattering.py
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 python3 research/typeii_conserved_saha_20261102/test_owner_density_rate.py
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 python3 research/typeii_conserved_saha_20261102/model_sensitivity.py
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 python3 research/typeii_conserved_saha_20261102/hostile_science.py
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 python3 research/typeii_conserved_saha_20261102/replay_verify.py

replay_verify.py runs all six science programs normally and with python -O,
checks all original source blobs and byte identity of ten scientific artifacts.
The 3+1 PNG figures are generated with source science_figures.py and
first_scatter_plot.py, which require Matplotlib.

Physics: prescribed BASS five-state gamma=1.3 Type II, Class A conserved
hydrogen nucleus current, exact source-owned hydrogen Saha function,
mean thermal label z=1700->1391.661, assumed isotropic matter temperature.
Initial Hubble and proper n_H normalization are imported from fiducial FLRW
parameters, not a coupled Bianchi Einstein-thermodynamic IVP.
Electron proper density n_e=x_e n_H_rest and comoving-electron closure are
explicit CONDITIONAL assumptions. The density frame Gamma cancels with the
current conservation law in the scalar Thomson prefactor; source q is used once.

Not implemented: HyRec H/He x_e(z), true SahaHistory import due optional JAX,
recoil/KN energy-domain confidence, original polarized gain/loss and full
Bianchi Einstein-Boltzmann system, or observational CMB visibility.
Do not merge or enable the production dispatcher from this slice.
Actual per-stage commits and SHA256 ZIP receipts are kept in
/home/cosmosapjw/research_backups/bass_typeii_conserved_saha_20261102/STAGE_RECEIPTS.tsv.
BASS upper DAG 9/15 scoped source-mapped, newly full-complete upper nodes 0;
Stage II historical 11/11 current not verified, Join J1 0/2 HOLD.
