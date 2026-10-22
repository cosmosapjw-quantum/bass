# BASS sandbox affine chemistry

Implemented an opt-in exact33→30coordinate adapter on the existing compactH–Li model. Actual finite-state RHS/Jacobian verification passes; no IVP rerun or measured speedup is claimed. Read THEORY.md and INTAKE.md.

From a checkout containing PR180 and this research folder:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 python research/sandbox_affine_chemistry_20261022/code/verify_affine.py --output /tmp/bass_affine_verification.json
```

The default baseline is the sibling research/rei_hheli_compact_pilot_20261022 folder. An explicit --baseline path may select the recovered immutable baseline. Instantiate AffineSystem(CompactSystem(config)); use its rhs,jac,lift andfull62 methods. The owner verifies its own donor identity. Remaining: connect the companion full33lifted error norm to an actual adaptive solver and perform one bounded paired trajectory; preserve all original tolerances and saved results.

Publication and cloud delivery are owned by the parent orchestration receipt. No remote write is claimed by this lane.
