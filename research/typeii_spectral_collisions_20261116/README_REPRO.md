# Reproduce the electron-frame spectral collision unit

Parent: PR334 `7ad4e4b1cf841e0a974715bcece739ec06b38014`. Draft PR336. All changes are confined to `research/typeii_spectral_collisions_20261116`; parent/main and production source are unchanged.

Authoritative results: `FINAL_REPORT.md`, `STATUS.json`, `SPECTRAL_SOURCE_RESULTS.json`, `VERIFICATION_AND_HOSTILE.json`. Mathematical definitions/units and source roles: `DESIGN_AND_THEORY.md`, `DERIVATION_SUPPLEMENT.md`. Primary cross-section files and hashes: `sources/PROVENANCE.json`. All three original downloaded source files are preserved; generated Fortran binaries live only in ignored `native_run/`.

Requires Python3 with NumPy/SciPy, Git and gfortran. No network or original host-specific installed HYREC source is required once this Git tree is present. The parent source fixture and FULL-half both output remain repository files. From the repository root:

```bash
export PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
d=research/typeii_spectral_collisions_20261116
python3 "$d/test_collisions.py"
python3 "$d/verify_sources_and_kernels.py"
python3 "$d/source_campaign.py"
python3 "$d/verify_final.py"
```

The final verification actually recompiles original phfit2.f and repeats the source and physical calculation under optimized Python, checking output SHA256. Twelve analytic tests run normally and optimized; original Fortran REAL cross sections are compared with the independent double evaluator at 24 energies/species. Photo rates and heat use SI, while the source fit takes eV and returns Mb (1Mb=1e-22m^2). Ground-state rates are not a replacement for native HYREC effective recombination/photoionization coefficients.

`GROUND_PHOTOIONIZATION.csv` preserves log(rate/s^-1), floating rate, log(photoelectron power/W), mean excess energy and scalar-temperature comparisons. Deep Wien-tail rates can be subnormal; use the log columns for relative comparisons. Large ratios are not evidence for large absolute physical rates or a net change in xe.

`SPECTRAL_COMPTON_FIELDS.csv` stores the induced angular moment and alternative scalar temperatures. `PASSIVE_FIXED_XE_TEMPERATURE.csv` has five differential-equation trajectories with identical parent xe, geometry and finite initial Tm. Only scalar, energy-matched and spectral lanes are physical comparison models; omitted-induced and monopole-induced lanes are wrong-kernel controls. This is not a native population rerun, a variable-composition energy closure, momentum backreaction or global radiation solution. No new Thomson optical-depth prediction is claimed because xe was held fixed.

The small test-normalization defect and its concrete repair are preserved in ADAPTIVE_NORMALIZATION_FAILURE.log and DESIGN_AND_THEORY.md. It arose from threshold eV->J->eV roundoff in the verifier, not from changing the source cross-section threshold. Tolerances were not widened.

Publication is four local checkpoints S1..S4, separate from the upper BASS DAG. Every checkpoint is pushed/read back and archived on the owner host plus external disk. Receipts are outside Git to avoid self-referential final commit hashes. Do not auto-merge.
