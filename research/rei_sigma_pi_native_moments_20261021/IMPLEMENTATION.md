# ACCEL02 implementation and bounded observations

This file records implementation facts. Scientific admission is pending the
controller's independent Astra review. No performance benchmark, speedup estimate,
full729 rerun, new convergence claim, or solver/closure change was performed.

## Executed identity and limits

The controller requested executor model `gpt-6.1-sol`. No runtime model telemetry
was exposed to this executor, so the observed runtime model is recorded as null;
the requested model is not presented as an observed identity.
`evidence/IMPLEMENTATION_IDENTITY.json` records source hashes, the observed Python
and platform identity, counts and numerical comparison maxima.

There was one compiler invocation. There were five original plus five native
two-step direct trajectories and one additional native two-step worker solve.
A second launched worker reused that case. No more than two worker processes
were allowed; numerical-library thread counts were one.

## Implementation

`moments.cpp` exports a single C ABI function, `rei_moments_v1`, and uses C++17
plus the standard mathematics library. The loop retains the original96 radial
nodes and evaluates16 reflected pairs of the original32 angular nodes. Python
combines the original paired weights once for each model. This is the original
quadrature evaluated by symmetry; no16-node quadrature is introduced.

The loader validates actual `mu`, `mu2`, `p2`, `wmu`, momentum-square and complete
96x32 weight arrays before folding. It requires original contiguous binary64
layouts, finite values, finite positive mass, nonnegative momentum-square and
weights, angular squares in[0,1], reflected angular and weight parity, and
consistency of `mu2=mu*mu` and `p2=(3*mu2-1)/2`. Bad parity explicitly raises
`NATIVE_REFLECTION_PARITY_REQUIRED_NO_FALLBACK`. It never substitutes the Python
backend for a rejected native model.

`native_context.py` copies the angular data into independent immutable bytes-backed
arrays per model. Folded96x16 weights,96 momentum-squares and16 angular squares
are prepared once. The native call precomputes16 angular factors and makes one
fused radial/angular pass, maintaining three Neumaier compensated sums. It
allocates no full96x32 runtime temporary. The reference for Neumaier compensation
is Ogita/Rump/Oishi2005, introductory Eq.1.3, as frozen in the contract and recorded
in the source comment.

The existing ACCEL01 `_ExactMomentCache` is composed through explicit class MRO:
binding guard, existing cache, native miss evaluator, unchanged owner class.
Domain rejection, exact binary64 `(x,b)` keys, fresh per-case model state,
bounded cache capacity and immutable cache binding remain in effect. Native
and owner results are compared numerically. A cache hit returns the very same
stored tuple.

`build_native.py` invokes the compiler explicitly with
`-O3 -std=c++17 -fPIC -shared -fno-fast-math -ffp-contract=off`. It records source
hashes, compiler location/version, flags/command, loaded-library hash and platform.
`evidence/BUILD_RECEIPT.json` and `evidence/BUILD_STDOUT.json` preserve the actual
one-build receipt. The generated library and build directory are ignored as
source artifacts. A missing, changed or stale build produces a rebuild command;
compilation is never implicit.

The only existing production file changed is ACCEL01 `batch_worker.py`. Its
optional `BackendSpec` supplies a context factory, source files, native entrypoint,
actual build identity and CLI arguments. Default callers retain the exact-cache
path. There is no mutation or monkeypatching of production module globals.
Source namespaces bind the dispatcher, loader, C++ source, build recipe, frozen
contract, actual library and receipt. Scientific coordinates and the frozen
science-context identity remain planner-owned and separate from backend identity.
The unchanged planner and executor provide completed-case exclusion, NCP resource
admission, locks, partial completion and restart. Native preparation delegates to
the existing no-work branch before inspecting or loading any native build.

## Frozen verification observations

| Check | Observed outcome | Raw evidence |
|---|---|---|
|140 predeclared kernel points|All pass; maximum energy-scaled absolute error `3.0017696087628955e-16`, limit `1.4210854715202004e-14`|`evidence/KERNEL_RAW.json`|
|Three five-point derivatives, h=2^-15|All pass; maximum normalized residual `3.730718793634552e-12`, limit `2e-9`|`evidence/DERIVATIVE_RAW.json`|
|Five original/native two-step pairs|Original eight gates pass for both backends; all frozen comparisons pass|`evidence/TRAJECTORY_RAW.json`, `evidence/TRAJECTORY_COMPARISON.json`|
|Native hit/parity/stale build/source/backend distinction|Requested rejections and exact tuple hit observed|`evidence/INTEGRATION_CHECKS.json`|
|Completed729 plan|pending0/jobs0, no compilation/library load/store creation|`evidence/completed729/`|
|Existing worker tests|Nine tests pass, including two-process case locking|`evidence/WORKER_UNIT_TESTS.log`|
|Real native worker and same-case reuse|First fresh scope solves one case; second fresh scope launches a worker and reuses it, receipt bytes unchanged|`evidence/worker/WORKER_CHECKS.json` and executor scopes|

Maximum absolute signed differences across initial, history and final comparisons
were `4.400213117869973e-23` for Sigma, `1.1777890328282316e-20` for Pi_m,
`5.169878828456423e-26` for Pi_r, and `1.1777890328403265e-20` for Pi_total.
Maximum normalized total tensor-work difference was `3.268686181550334e-24`.
H, Tgas, x_HII and x_HeII comparisons were exactly equal for these stored
trajectories. Signed totals, including tiny near-isotropic stresses, are retained
in raw output. Work comparison uses `2*Sigma*Pi`, in units `H^3/kappa_t`.
These empirical observations apply to the frozen finite test set.

`verify_native.py` preserves data incrementally and stops on the first failed
numerical acceptance check. The worker input intentionally rejected by the wrong
backend is preserved as a failure artifact with
`NUMERIC_BACKEND_SELECTION_MISMATCH`; it is evidence of the requested rejection,
not a failed scientific trajectory.

## Runnable commands

From the repository root, using the existing Python environment with its NumPy
and SciPy dependencies (no package installation is required):

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
export BLIS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
export RAYON_NUM_THREADS=1 REI_TRANSPORT_THREADS=1
python research/rei_sigma_pi_native_moments_20261021/build_native.py
```

Completed-case planning and no-work receipt do not need that build command:

```bash
python research/rei_sigma_pi_native_moments_20261021/native_worker.py plan --out /tmp/accel02-plan.json
python research/rei_sigma_pi_native_moments_20261021/native_worker.py prepare --plan /tmp/accel02-plan.json --out /tmp/accel02-prepared --case-store /tmp/accel02-case-store
```

For the supplied five coarse verification coordinates, choose fresh output paths:

```bash
python research/rei_sigma_pi_native_moments_20261021/native_worker.py plan --cases research/rei_sigma_pi_native_moments_20261021/evidence/CUSTOM_CASES.json --nsteps 2 --group-size 1 --out /tmp/accel02-coarse-plan.json
python research/rei_sigma_pi_native_moments_20261021/native_worker.py prepare --plan /tmp/accel02-coarse-plan.json --out /tmp/accel02-coarse-prepared --case-store /tmp/accel02-coarse-store --group-size 1
python research/rei_sigma_pi_pilot_20261021/shared_executor.py /tmp/accel02-coarse-prepared/manifest.json --scope /tmp/accel02-coarse-scope --profile ncp --max-workers 2 --resource-wait-s 30 --poll-s 0.1
```

The executor resamples actual availability at launch. NCP64 CPU/128GiB caps are
ceilings; `--max-workers 2` bounds this lane's verification. Use the unchanged
executor for resource-controlled launches; the lower-level group command is:

```bash
python research/rei_sigma_pi_native_moments_20261021/native_worker.py run-group --input /tmp/accel02-coarse-prepared/inputs/split_cache_group_0000.json --output /tmp/accel02-group-result.json
```

The optional `--build-dir` argument on prepare/run-group selects a different
explicit build location; generated jobs preserve that location. Default worker
commands remain valid and select the Python exact-cache backend.

The checks that produced the stored evidence were:

```bash
python research/rei_sigma_pi_native_moments_20261021/verify_native.py kernel
python research/rei_sigma_pi_native_moments_20261021/verify_native.py trajectories
python research/rei_sigma_pi_native_moments_20261021/verify_native.py integration
python -m unittest discover -s research/rei_sigma_pi_acceleration_20261021 -p test_batch_worker.py -v
python research/rei_sigma_pi_native_moments_20261021/verify_worker.py
```

These verification commands consume the frozen run budget. Re-executing the
worker check requires a fresh evidence/work location or it will intentionally
observe stored reuse; no additional numerical runs are required for delivery.
