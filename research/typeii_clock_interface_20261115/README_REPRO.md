# Reproduce PR334's separated-clock and radiation-interface experiment

Frozen parent: PR333 commit `27a3c7cfb57e145ed35526d4613de2e9d613d4ea`. Only `research/typeii_clock_interface_20261115` changes. Authoritative result: `FINAL_REPORT.md`, `STATUS.json`, `NATIVE_RESULTS.json`, `VERIFICATION.json`.

The source-native FULL model is compiled independently at steps8.49e-5 and4.245e-5. All12 histories use original parent input H/nH functions on their fixed2248 grid. Cases: legacy, reaction-only, thermal-only, both, zero-clock-tilt adapter, and intentionally naive global H substitution. Zero-adapter is an implementation limit at fixed other inputs, not a claim that a tilted geometry is FLRW.

## Reproduction
Run from this Git checkout with Python3, NumPy, SciPy and GCC available. The parent HYREC source archive is already in Git; original16 computational files are extracted to this unit's ignored native_run and checked against the immutable SHA256 lock. No network or original machine-specific source installation is required.

```bash
export PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
d=research/typeii_clock_interface_20261115
python3 "$d/test_clocks.py"
python3 "$d/source_fields.py"
python3 "$d/native_experiment.py"
python3 "$d/analyze_native.py"
python3 "$d/verify_interface.py"
```

`native_experiment.py` performs real current native executions, not cache-only receipts. `verify_interface.py` performs20 unit-test executions, a fresh FULL-half both-lane rebuild/replay,8 native state/lane component probes,5 invalid actual C clock-input cases, and an optimized physics-analysis replay. These are separate categories of evidence; no fabricated aggregate pass count is used. Raw logs are retained.

## Equations and limitations
`clocks.py` implements homogeneous proper reaction time and fixed-composition fluid cooling; `clock_adapter.c/.h` and `thermal_wrappers.c.txt` provide source-bound native interfaces. `DESIGN_AND_THEORY.md` defines units, signs, mean-redshift boundary and the tracking-temperature approximation. The exact local angular Planck and radiation moments are tested separately. They are NOT converted into a single scalar blackbody and NOT yet coupled to native atomic photoionization/Compton kernels.

The atom experiment deliberately retains an imposed scalar thermal radiation reservoir and original isotropic effective photon/escape model. No full anisotropic collision gain/polarization, reacting-mixture heat-capacity closure, coupled metric backreaction, or observed z0 visibility is implemented. Prescribed clocks are identity above mean z1700, as specified by the inherited intervention boundary. Numerical timestep checks do not certify arbitrary onset prescriptions or a globally exact tilted cosmology.

## Preservation and continuation
T1..T4 are separately committed/pushed with exact remote SHA readback, and backed up to host plus external disk with matching SHA256. Receipt path:
`/home/cosmosapjw/research_backups/bass_typeii_clock_interface_20261115/STAGE_RECEIPTS.tsv`.
External copies:
`/mnt/extdrive/research_backups/bass_typeii_clock_interface_20261115/`.
The final HEAD/archive receipt is outside Git to avoid a self-referential commit. `NEXT_THREAD_HANDOFF.txt` says read live HEAD before further work.

Local unit4/4 scoped complete; BASS upper9/15 scoped/source-mapped, new full upper nodes0. Keep Draft; production_ready=false, merge_ready=false, auto_next=false. Next constructive unit: electron-frame spectral photoionization and Compton moment closure using the implemented exact radiation distribution, before full atom/radiation coupling.
