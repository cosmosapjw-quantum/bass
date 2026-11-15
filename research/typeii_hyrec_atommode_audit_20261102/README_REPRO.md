# Reproduce the recovered BASS/HYREC atomic-mode experiment

Current PR: 333, stacked on immutable PR332 `ee298e24a6bac85bb11a81393f37499a8b0ddbe3`. Current authority: `RECOVERY_AND_FINAL_REPORT.md`, `WORK_UNIT_STATUS.json`, `MODE_COMPARISON_RESULTS.json`. The prior `THEORY_AND_RESULTS.md` is retained as historical R1/R2 context and visibly superseded.

## Inputs and source identity
Run from this repository checkout. Parent data under `research/typeii_hyrec2_history_20261102` and `research/typeii_native_hyrec_expansion_20261102` remain Git-owned and unchanged. Original HYREC sources are recovered from `HYREC_EXECUTION_SOURCE_16.zip` into ignored `native_run/original_source`; every executable source/header/atomic-table SHA256 is checked against the original parent lock. No network is required for a fresh restore of those 16 files. The two old distribution fixture files input.dat/output_xe.dat are not required and are not claimed recovered. The actual cosmological input is the pinned parent HYREC2_FLRW_INPUT_20261102.dat.

Requires Python 3 with NumPy and SciPy, GCC, Git. Current executed environment was Python3.12, NumPy2.4.2, SciPy1.17.0, GCC13.3.0. No Rust production dispatch was changed. Source patches exist only in isolated scratch builds and can be regenerated from `native_modes.py`.

```bash
export PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
d=research/typeii_hyrec_atommode_audit_20261102
python3 "$d/test_native_modes.py"
python3 "$d/native_modes.py"
python3 "$d/analyze_recovered.py"
python3 "$d/verify_recovered.py"
python3 "$d/summarize_convergence.py"
python3 "$d/hostile_source_control.py"
```

`native_modes.py` builds compile-time-isolated modes and resumes the current campaign using manifest/hash-bound current results when present. It prints PRESERVED_CURRENT_RUN for reuse, not NATIVE_RUN. A completely fresh numerical rerun can use the public functions below, which bypass this resume cache without deleting the evidence manifest:

```bash
PYTHONPATH="$d" python3 - <<'PY'
from native_modes import compile_mode, execute, inputs
for mode,refinement in [('SWIFT',1),('SWIFT',2),('SWIFT','matched'),('EMLA2s2p',1),('EMLA2s2p',2),('FULL',1),('FULL',2),('FULL',4)]:
    build,_=compile_mode(mode,refinement)
    for background,(H,nH) in inputs().items():
        result=execute(build,mode,refinement,background,H,nH)
        if result['exit']!=0:
            raise RuntimeError(result)
PY
```

The excluded SWIFT step0.001 case is a preserved native numerical failure, not an ordinary reproducibility test expected to pass. `hostile_source_control.py` independently demonstrates the same failure using native builtin FLRW H and no BASS patches. That original standalone program returns exit0 despite an error, so inspect the generated control JSON and scientific output validity. The new mode driver explicitly propagates solver error and validates output.

## Interpret the results
All mode comparisons hold the parent prescribed H(z_mean) and hydrogen-density function fixed; the 2248-point external-input grid is distinct from the mode's atomic timestep. FULL is an isotropic radiative-transfer reference inside this closure, not an exact Bianchi solution. SWIFT_matched uses the default FULL timestep; comparing it with FULL_r1 is genuinely equal-step, while FULL_r4 is the finer reference. Successful histories are stored as native 8000-row tables with compiled-mode metadata.

The photon observable is scalar conditional attenuation on 26 original source geodesics ending at mean z=300. It is not today's visibility function and contains no full angular/polarized scattering gain. `THEORY_MODE_AND_CLOCK.md` derives the outstanding proper reaction-clock and thermal-expansion conditions. No all-redshift/arbitrary-expansion accuracy or production readiness is asserted.

## Preservation
R1/R2 retain their historical checkpoints. R3-R10 are separately committed, pushed, remotely read back and archived on the authorized host. The final receipt is outside Git to avoid a self-referential commit hash. Use `NEXT_THREAD_HANDOFF.txt` and read the live branch HEAD before continuation. Do not merge automatically or mutate parent/main.
