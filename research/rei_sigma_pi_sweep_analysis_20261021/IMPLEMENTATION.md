# ACCEL03 aggregation implementation

Status: **PENDING_INDEPENDENT_REVIEW**. This file records mechanical implementation
and stored-data verification. Scientific admission belongs to the controller.

## Scope and files

`aggregate.py` supplies the plan-driven saved-result CLI. `diagnostics.py` supplies
cancellation, component-scaled arithmetic checks and exact-cohort control matching.
`test_aggregate.py` supplies twelve focused saved-data tests. No original pilot,
ACCEL01 or ACCEL02 source/reference output was changed. There were **zero solver
calls, zero native builds and zero benchmark runs**.

The requested executor model was `gpt-6.1-sol`. Actual runtime model telemetry was
not exposed, so observed runtime model is recorded as null. Requested identity
is not treated as observed identity. Source hashes and observed analyst Python
are recorded in `evidence/aggregate_verification.json`; the analyst runtime is
not a scientific acceptance gate.

## Portable input path

The supplied plan owns the complete candidate set. The manifest describes pending
work only. The aggregator partitions candidates into pinned reused completions,
successful pending cases and explicit missing pending IDs. Missing data yield
`PARTIAL`; they are never filled with zero.

The implementation reuses `work_plan` case/science functions, its pinned original
completion registry, the original pure `initial_checks`, scalar projection and
`result_paths_from_scope`. It does not call `validate_pending`, `validate_plan`,
`PreparedContext`, `seed_for`, a solver, a native loader or a compiler. Stored
plan/science/toolchain/manifest values are checked against each other, rather than
against the analysis machine's NumPy, SciPy or Python versions. Owner source
identity comes from the pinned owner definition without creating a model.

Executor-scope imports select only successful receipts and verify the sibling
result hash using the existing portable helper. Explicit `--result` imports are
recorded as explicit imports. Original target absolute paths in recorded manifest
bindings are preserved as provenance and are not dereferenced on the analyst host.

Exact NCP plan/default-plan/manifest and five successful receipt/result pairs were
copied without modification to `results/inputs/ncp5/`. This is a small portable
fixture, not a copy of the target's full execution directory or native binary.
The production-shaped NCP projection is generated from that relocated fixture.
The existing ACCEL02 one-case first/second scopes supply the duplicate-reuse check.

Completed aliases map science ID to the pinned CSV's original case ID, then retain
the requested case label. All original endpoint values are preserved as floating
numbers or original scalar strings/booleans. Completed endpoints have no fabricated
history. For pending results, initial is step0 and exactly nsteps evolved rows
follow; final is not appended a second time.

Input failures distinguish `InputIntegrityError` from `PhysicsError`. The saved
case schema/seed/config/source, step count, interval, final/history equality,
finite physical values, all eight original gates, initial mapping and original
error reductions/limits are checked. Group reuse metadata is not part of a
scientific case body: identical bodies deduplicate; conflicting bodies reject.

## Frozen CSV and plot-consumer API

Outputs are `summary.json`, `cases.csv`, `history.csv`, `diagnostics.json` and
`provenance.json`. CSV null values are empty cells; JSON uses null. Cohorts retain
source ID, backend name, recorded toolchain, nsteps, physical context and interval.
A mixed projection does not label archived rows as native.

| File | Stable columns |
|---|---|
| cases.csv | Exact requested case fields; `science_id`, `science_context_id`, `source_id`, `backend`, `toolchain_id`, `toolchain_json`, `nsteps`, `cohort_id`, `origin`, `history_available`; original `initial_<scalar>` and `final_<scalar>` fields |
| history.csv | Same case/metadata fields; `step`; original unprefixed owner scalar fields including `a`, `signed_Sigma`, `signed_Pi_m`, `signed_Pi_r`, `signed_Pi_total` |
| cases.csv controls | `raw_delta_signed_Sigma`, `control_case_id`, `control_status`, `control_subtracted_final_signed_Sigma` |
| history.csv diagnostics | `diag_component_scale`, `diag_residual_fraction`, `diag_cancellation_fraction`, `diag_condition`, `diag_cancellation_status`, `diag_normalized_work_m`, `diag_normalized_work_r`, `diag_normalized_work_total`, `diag_arithmetic_pass` |
| cases.csv diagnostics | Same diagnostic names prefixed with `initial_` or `final_` |

Other flattened original scalar fields remain available. Plotting should consume
these outputs, preserve actual case/cohort/nsteps identities, and plot only available
samples. No plotting code was added by this implementation executor.

## Diagnostics and unchanged limits

Cancellation uses the signed sum with component scale A=abs(p)+abs(r). Ratios use
initialized NumPy arrays with masked division; no `np.vectorize` is used. A=0
produces `ZERO_COMPONENT_SCALE` with null ratios/condition. Nontrivial exact
cancellation has residual fraction0 and null divergent condition with
`EXACT_CANCELLATION`. The owner's historical `cancellation_fraction` is preserved
independently.

Original redundant fields are preserved, with explicit arithmetic residuals in
`diagnostics.json`. Total signed sums, component/total half and Frobenius norms,
physical pressure sums, work sums/aliases and normalized work use the frozen
`128*eps64` times the relevant component scale. If the scale is zero, exact zero
residual is required. No residual is divided by a near-zero signed total. Original
physics gate thresholds are unchanged.

Matched controls require exact requested signed initial shear and identical cohort
(including source/backend/toolchain, nsteps, context and interval), with both
requested stresses zero. An absent control gives `MISSING_CONTROL` and null
response. Raw final-minus-initial shear change remains a separate column.

## Observed bounded results

| Stored-data check | Observation |
|---|---|
| NCP five-case/two-step, relocated receipt path | COMPLETE:5 expected,5 successful pending,0 missing,15 history rows; source `aed4c55a61df37d97d8c0aa309b7875e5eb3629abbd284fe04faf23cb261115d` |
| Archived729 completion projection | COMPLETE:729 reused,0 pending,0 history rows; nsteps64; all pinned CSV fields reproduce exactly as floating numbers/scalars |
| Existing first/second worker scopes | COMPLETE:1 successful case,1 identical scientific duplicate,3 history rows |
| Focused tests |12 pass; includes missing/PARTIAL, unexpected/conflicting cases, duplicate reuse, wrong group/owner nsteps, wrong science binding, failed gate, malformed redundant row, zero/exact cancellation, missing same-cohort control and legitimate completed alias |

The largest component-scaled arithmetic residual was `2.528508284916226e-16` for
the NCP sample and `3.8369107064748666e-16` for the archived endpoint projection,
against the frozen `128 eps64` envelope. These are arithmetic reconstruction checks,
not solver convergence or new trajectory comparisons.

An initial JSON export encountered a NumPy boolean serialization error. It was
repaired by representing the already-frozen arithmetic factor as a Python float;
no formula, tolerance or scientific input changed. The original failed CLI stderr
is retained as `evidence/aggregate_initial_serialization_*.stderr`. Corrected CLI
returns and actual argv/exitstatus are in `evidence/aggregate_commands.json` and
`evidence/aggregate_{ncp5,baseline729,worker_duplicate}.{stdout,stderr}`. Focused test
stdout/stderr are in `evidence/aggregate_tests.*`.

## Runnable commands

From the repository root, using the existing Python environment:

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
export BLIS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
export RAYON_NUM_THREADS=1 REI_TRANSPORT_THREADS=1
python research/rei_sigma_pi_sweep_analysis_20261021/aggregate.py \
  --plan research/rei_sigma_pi_sweep_analysis_20261021/results/inputs/ncp5/small-plan.json \
  --manifest research/rei_sigma_pi_sweep_analysis_20261021/results/inputs/ncp5/small-prepared/manifest.json \
  --scope research/rei_sigma_pi_sweep_analysis_20261021/results/inputs/ncp5/small-scope \
  --out /tmp/accel03-ncp5-analysis
python research/rei_sigma_pi_sweep_analysis_20261021/aggregate.py \
  --plan research/rei_sigma_pi_sweep_analysis_20261021/results/inputs/ncp5/default-plan.json \
  --out /tmp/accel03-baseline729-analysis
python -m unittest discover \
  -s research/rei_sigma_pi_sweep_analysis_20261021 -p test_aggregate.py -v
```

For new explicitly planned saved outputs, substitute their plan/manifest and use
repeatable `--scope` and/or `--result` paths. No solver rerun, library compilation,
original729 history download or analyst-toolchain match is needed. A failed import
returns exit2 and writes `diagnosis.json`; missing expected outputs instead return
a `PARTIAL` summary with explicit identities. The original fixed729 aggregator and
its plotting assumptions are unchanged.
