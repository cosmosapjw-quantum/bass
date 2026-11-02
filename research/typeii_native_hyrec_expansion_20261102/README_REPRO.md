# Original BASS Type II Hubble + conserved proper hydrogen in native HYREC-2

**Frozen parent PR #330 HEAD:** `9f10e1145c8582f71f7d81dcebfd3c125c70c04c`.
**Protected BASS main:** `9c6506e4e2087129a8b674ff10438e5db1a55c9d`.
**New Draft PR:** #332. No production dispatcher/source or parent changes.

## Scientific model, definitions, and limitations
Signature (-,+,+,+). Original BASS gamma-law 1.3 positive-N1 Bianchi Type-II normal-frame source in Hubble-normalized time `d tau_H=H dt_normal`, with exactly original five-state source `q_dec=N1'/N1+4 SigmaPlus`, `d ln H/dtau_H=-(1+q_dec)`. The mean-scale-factor thermal label is `1+z_mean=1701 e^{-tau_H}`, **not** a directionally observed redshift. H(zmean1700) is normalized to original native HYREC-2 FLRW expansion; H(zmean>1700) remains the original HYREC FLRW H, H(zmean<=1700) is original source BASS Type-II gamma-law continuation.

Actual original HYREC-2 C source `history.c::rec_build_history(HYREC_DATA *,int,double *hubble_array)` receives the BASS H table on the *source-owned* 2248-point uniform-z grid. Original source C hydrogen+helium atomic kinetics and SWIFT fit rate tables are unchanged. Only 12 original `history.c` and four original `helium.c` hydrogen proper density accessors in **ignored scratch copies** are changed to `nH0(1+z_mean)^3 Gamma(1700)/Gamma(zmean)`. All original atomic C data sources are untouched and SHA256 pinned in parent HYREC source report. The extra conserved Class-A hydrogen number current and electron comoving assumption are explicit model closures.

Full native C kinetic 2×2 lanes:
- FLRW H, native FLRW hydrogen density
- original BASS Type-II H, native FLRW hydrogen density
- FLRW H, tilted conserved proper hydrogen density
- original BASS Type-II H, tilted conserved proper hydrogen density

Only native x_e and matter T are compared, not resampled arbitrary proxies. HYREC-2 SWIFT effective rate correction `fit_swift.dat` was originally calibrated near FLRW, so a Type-II H rate 13% off FLRW at z1100 is **not covered by a new precision-accuracy validation**. The C atom model retains isotropic photon background source; original BASS gamma-law gravity is not recomputed with actual atom/Thomson baryon-photon backreaction. No z0 observed CMB visibility, full angular Thomson gain/polarization, or physical late-time cosmology claimed.

## Exact owner host and executable reproduction
Original native HYREC C/atomic tables at `/home/cosmosapjw/src/TEFF_CLASSIER_CLEAN_BUILD_v1_3/external/HyRec2020`; scratch binaries, symlinks and native outputs **only** under ignored `research/typeii_native_hyrec_expansion_20261102/native_run/`. From this Git repository root run sequentially:

```bash
export PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
d=research/typeii_native_hyrec_expansion_20261102
python3 "$d/verify_native_external_api.py"
python3 "$d/generate_typeii_H_grid.py"
python3 "$d/run_native_typeii_atomic_H.py"
python3 "$d/run_native_typeii_proper_current.py"
python3 "$d/transport_native_atomic_photons.py"
python3 "$d/verify_atomic_rays.py"
python3 "$d/native_atomic_homotopy.py"
python3 "$d/hostile_physics.py"
python3 "$d/replay_verify.py"
python3 "$d/science_figures.py"
```

The replay executes the eight science/source programs normally and optimized `python -O`, checking exact source identities: BASS original nine Git blobs, HYREC2 original 18 C/header/atomic files, 19 source science artifact SHA256 identities. If any original source is missing or modified, fail closed, do not replace it silently. The original source HYREC-2 `rec_build_history` Hubble-grid control at 300≤z≤1700 has native H source xe absolute error 1e-12, but the native 2248-table low z ~1 error means all-z identity is **not** established.

## Key actual outputs
`NATIVE_TYPEII_HUBBLE_HHE_ATOMIC_XE_TM_8000.dat`: original native HYREC2 atomic kinetic xe/Tm with original BASS H input only.
`NATIVE_TYPEII_H_AND_PROPER_NH_XE_TM_8000.dat`: same native source H and source proper hydrogen nH on original C kinetic solver, published SHA256 `f28662a1932bf2674abc1c1a2f6e7f1504157e7df0034294579c8c8cfd0db872`. Original HYREC2 C raw H+nH output SHA256 `7e44f1e33765f09e8d0eba4ed7559a19b80964f1d5d8d9189bccae888881caf4`.
`TYPEII_ATOMIC_THOMSON_EXTENDED_26RAY.csv`: actual BASS source 1167×26 normal geodesic Thomson hazard, original C kinetic histories and zmean=300 finite endpoint attenuation.
`R5_SOURCE_ATOMIC_TYPEII_PHOTON_RESULTS.json`: native full H+proper nucleus atomic xe Type-II ray optical depth T(+ey)=42.58661549845179, T(-ey)=46.825380255796695, asymmetry .0474071149132525.
`R6_ATOMIC_PHOTON_NUMERIC_VALIDATION.json`: independent six-ray Radau max gap 5.056783436e-9, 1933-knot refinement max gap2.353885975e-10, Codazzi max2.498e-16, original 401×26 electron normal-rate SI/CGS max rel 6.661338e-16.
`R7_ATOMIC_H_NH_HOMOTOPY.json`: actual source native C kinetic response λ=0,.25,.5,.75,1 (diagnostic only), xe max deviation .01018856, midpoint nonlinear difference 4.670675e-5.
`R9_HOSTILE_PHYSICS.json`: double q, missing Gamma, wrong proper nH, low z extrapolation, invalid negative C inputs; same-author hostile pass.
`R8_SOURCE_REPLAY_RESULTS.json`: 8 programs normal+optimized, 16/16 actual science source replays, 19 output SHA256 stable.
`FIG01_ORIGINAL_TYPEII_H_RATIO.png`, `FIG02_ORIGINAL_HYREC_ATOMIC_4_LANES.png`, `FIG03_BASS_TYPEII_NATIVE_ATOM_26_DEPTH.png`: source conditional science figures.

## Scope admission, DAG and preservation
Admit **source C implementation verified and mathematically derived/conditionally numerically checked** original HYREC2 H+He atomic rates with original BASS TypeII mean H and tilted conserved proper nH, propagating resulting source electrons on genuine original BASS 26 photon characteristics. Do **not** admit coupled Einstein-baryon-photon self-consistency, HyRec SWIFT off-FLRW precision, full angular scattering/polarization, z0 CMB visibility, current StageII canonical gate, or production dispatcher.

BASS upper DAG 9/15 **scoped/source-mapped** unchanged, new fully complete upper production nodes 0. StageII historical 11/11 only; P_MIG_II_PREFLIGHT PARTIAL; G_DYN_MANIFOLD_VI0 PARTIAL; Join J1 0/2 FULL PASS HOLD. Production=false, merge=false, auto_next=false. No native subagent; same-author hostile review performed, different-author blind referee NOT_RUN. Each R1/C1..R10/C10 stage separately Git committed and pushed with remote SHA readback and owner-local Git ZIP SHA256, receipts at `/home/cosmosapjw/research_backups/bass_typeii_native_hyrec_expansion_20261102/STAGE_RECEIPTS.tsv`. Do not auto-merge.
