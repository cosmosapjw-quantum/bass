# Reproduce the finite cascade/effective-rate bridge

Current Draft PR338, frozen parent PR337 `d29a08cb6e368339015dadb2b791044ba6af9848`. All changes reside under `research/typeii_cascade_effective_20261116`; production/main and parent code remain unchanged.

## Inputs, assumptions and scope
Parent finite-support nl-resolved bound-free kernels and tabulated source rates are under `research/typeii_boundfree_balance_20261116`. Source TypeII radiation fields and fixed parent FULL-half clock-corrected electron/Tm histories remain Git-owned. The four original HYREC source/header/two-photon tables copied under `sources/` are SHA256-locked. No network is needed to reproduce the calculation from this checkout.

The local tracer network consists of1s,2s,2p,3s,3p,3d and an ion with prescribed proper electron reservoir density. Its five E1 rates are constructed from exact nonrelativistic Coulomb radial amplitudes and parent binding-energy gaps. Only2s-1s nonresonant two-photon transitions are added, using the original HYREC half-spectrum normalized once to8.2206 s^-1. No high-n resonant two-photon terms are double counted on top of E1 cascades. Original source energy sharing is mapped to the parent's infinite-mass energy gap; this is documented, not an exact isotope claim.

The Schur reduction is stationary/zero-frequency. Reconstruct eliminated populations and total normalization before calculating full-atom quantities. The frequency-dependent memory/initial forcing is checked separately. A microscopic effective rate is not a replacement for the whole HYREC multilevel/line-transfer coefficient.

## Executable path
Python3, NumPy, SciPy and SymPy are used. From the repository root:

```bash
export PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
d=research/typeii_cascade_effective_20261116
python3 "$d/test_cascade.py"
python3 "$d/verify_kernels.py"
python3 "$d/run_cascade_sources.py"
python3 "$d/verify_final.py"
```

The final verifier executes16 unit contracts in normal and optimized Python, reruns kernels and the actual source campaign with `-O`, validates eight deterministic physics outputs byte-for-byte, checks12 bad-input cases and explicit wrong-model controls. The unchanged original four HYREC source files and nine BASS source blobs are checked. Test failures were retained as evidence before fixes; they are not expected failures in the final executable suite.

## Useful outputs
- `SOURCE_CASCADE_RESULTS.json`: source-state effective rates, stationary reconstruction, energy checks, actual z1100 probe and exact-memory diagnostics.
- `EFFECTIVE_BOUND_FREE.csv`:358 source states ×3 retained bound states =1074 effective/direct rate records.
- `FULL_GENERATORS.npy`, `REDUCED_GENERATORS.npy`, `FAST_LIFTS.npy`: full local generators, Schur generators and eliminated-state reconstruction matrices, with source order declared in the JSON.
- `SOURCE_TRACE_STATIONARY.csv`: full reconstructed local tracer stationary fractions, NOT cosmological electron fractions.
- `TRACE_DYNAMIC_MEMORY.csv`: full initially3s evolution, independent comparison and instantaneous-exit approximation.
- `KERNEL_VERIFICATION.json`: independent E1 radial/thermal/frame checks and standard-vs-hires two-photon resolution differences.
- `VERIFICATION_AND_HOSTILE.json`, `CONSERVATION_DIAGNOSIS.json`: actual bad-input, replay and wrong-model evidence.
- `DERIVATION_AND_SCOPE.md`: positive conservative Schur proof, memory/storage, photon/energy readouts and chemical-cycle argument.

## Preservation and continuation
Each K1-K4 phase is independently committed, pushed and archived with host and external-disk SHA256/CRC readback. Final receipt is outside Git to avoid a self-referential commit hash. Current upper DAG9/15 is scoped/source-mapped, not nine verified complete production nodes. No new full upper node, no merge, no native HYREC rerun or new xe/tau prediction. Next construction is the Lyman line transport/escape interface with thermal and optically-thin limits and directional frequency-flow assumptions tested explicitly.
