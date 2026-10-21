# Restore and rerun the H–Li compact preliminary pilot

This is the separate ACCEL04 → PHYS04 → PILOT04 campaign. Read
`FROZEN_CONTRACT.md` before interpreting results. Source availability, a local
archive, or an upload payload is not proof of scientific admission or remote
backup. Current status is recorded in `DAG.json`, `LOOP_RECORD.json` and
`delivery/`; actual provider acknowledgements and Git commits determine saved
status.

## Restore the checkpoint

Extract its ZIP at an empty working directory. The archive contains the
repository-relative directory
`research/rei_hheli_compact_pilot_20261022/` and `CHECKPOINT_FILES.json`.
The latter records sizes and SHA-256 values of the exact frozen bytes. Compare
those records if accidental corruption or an incomplete extraction is suspected.
Original selected donor source and provenance are under `vendor/rec_hheli/`;
selected intake summaries and primary-source citations are under `intake/`.

Use Python 3.12 and install the versions observed during preparation:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -r research/rei_hheli_compact_pilot_20261022/requirements.txt
```

These pins reproduce the preparation environment. They do not assert a
cross-platform bit-identical ODE trajectory. Retained numerical residuals and
scientific gates determine numerical agreement.

## Execution environment

Set one numerical library thread per worker before running Python:

```bash
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
```

The current sandbox observation is 8 CPU quota cores and an 8 GiB memory limit;
see `evidence/FINAL_RESOURCE_SNAPSHOT.json` for the final timestamp and current
read-only observation, and `intake/RUNTIME_INTAKE.json` for initial preparation.
Start with at most four workers and admit work using actual quota, sampled
cgroup/affinity CPU capacity, memory and peer reservations. Host load is a
diagnostic; it is not itself the CPU-admission gate. A 64 CPU / 128 GiB NCP host must be measured
on that host; no NCP resource or execution claim is made by this checkpoint.

## Source entry points

These are the implemented commands, expressed from the restored repository
root. The completed campaign contains 127 compact cases and 2 full62 oracles,
193 epochs each, with all owner gates passed. Independent final review and root
admission accepted this preliminary finite model:
`PASS_SCOPED_COMPLETED_SANDBOX_PRELIMINARY_PILOT`. See
`evidence/ROOT_ADMISSION_C.json` and
`evidence/independent_review/FINAL_REVIEW.json` for the accepted scope.

```bash
python research/rei_hheli_compact_pilot_20261022/code/verify_compact.py
python research/rei_hheli_compact_pilot_20261022/code/run_pilot.py --plan
python research/rei_hheli_compact_pilot_20261022/code/run_full62_oracles.py --execute
python research/rei_hheli_compact_pilot_20261022/code/run_pilot.py --execute
```

The dispatcher default output is the successful `results/pilot_v2` campaign.
A completed default `--execute` resumes it without launching new integrations;
`evidence/FINAL_RESUME_VERIFICATION.json` records 127 `complete_reused`, zero
new workers and zero integrations/RHS calls. The first failed output remains
at `results/pilot`.

The two full62 oracles are `s04_m04_r04` and `cancel_positive_matter`.
The dispatcher must preserve completed raw results, bound concurrency, and
report failed gates without silently retrying with changed scientific inputs.
The admitted Stage B release and serializer repair receipts preserve the
completed execution history. The plot/aggregation entry point is
`code/analyze_pilot.py`; paired
implementation checks are in `code/verify_paired.py`. See `IMPLEMENTATION.md`
and execution receipts for exact completed command lines.

The completed actual campaign has 127 distinct cases, each with 193 epochs from
z=20 to z=2. It retains both 33 compact coordinates and the reconstructed
62-state owner representation, all 21 isotope/ion abundance columns (including
zero n/T), signed matter/radiation/total stresses, both tensor conventions, and
plot-source arrays. Previous warm729 or ACCEL01–03 data do not fill this new
campaign's case inventory.

## Scientific interpretation and recovery

This finite model prescribes gas temperature and a local external 5–200 eV UV
reservoir. It evolves atomic ionization/recombination and Thomson feedback;
thermal fusion, charge exchange, collisional ionization, molecules, secondary
electrons and complete thermal/radiative energy closure are outside its scope.
The compact coordinates require the frozen isotope-electronic equality, zero
initial n/T, common isotope initial fractions, and the reflection-even geometry
subspace. Expanded physics must use the unreduced owner or a newly approved
invariant-subspace contract.

Checkpoint A preserves optimization, B preserves adopted physics and
execution-ready source, and C preserves actual trajectories, figures,
independent review and handoffs. Restore the most recent acknowledged
checkpoint and continue from the `next_node` in `DAG.json`. Scientific admission
is complete within the explicit preliminary scope. The frozen C snapshot keeps
C10 remote delivery pending until actual acknowledgements are recorded in the
closing receipt; it does not require an archive to contain its own hash. Preserve
failed results and diagnosis records; do not clip or renormalize output to pass a gate.

## Checkpoint B and C payload distinction

Checkpoint B is a compact source/evidence snapshot. It includes the exact case
completion manifests and `results/analysis/SUMMARY.json`, and intentionally
excludes raw NPZ arrays, figures and history/plot-source tables. Checkpoint C
contains the complete successful `results/pilot_v2` and full62 oracle arrays,
figures, history tables, plot-source arrays, final report and review.

The first attempt `results/pilot` wrote 127 raw trajectories before final JSON
metadata failed on a NumPy boolean. Its original 33,131,538-byte directory stays
locally preserved. The repaired scalar serializer reran the same 127 cases in
`results/pilot_v2`; physical dynamics, numerical controls and gate thresholds
were unchanged. Failure logs/receipts and the old/new source relation are kept
in the checkpoints; the first-attempt raw arrays are not duplicated in them.

## Publication payload

The final C ZIP contains the two full history aggregates
`results/analysis/all_histories.csv.gz` and
`results/analysis/all_histories_plot_source.npz`. These large redundant
aggregates are backup-only payloads and are excluded from Git. All successful
raw case NPZ files, figures, smaller source tables/arrays, source and evidence
are intended for both repositories. `delivery/GIT_PAYLOAD_SCOPE.json` records
the exact distinction. Final remote commits and provider acknowledgements
must be read from the final delivery receipts once available.

## Final scope and late donor refresh

The scientific PASS applies to the frozen finite non-tilted LRS model, the
prescribed temperature/external UV inputs and the adopted atomic inventory.
It does not establish full thermal/radiative energy closure, every possible
nuclear channel, continuum/global convergence, general non-LRS results or a
measured speedup. No additional ODE run or benchmark is required by the final
admission.

The donor heads advanced during the campaign.
`evidence/FINAL_DONOR_DELTA_REVIEW.json` records the bounded comparison: REC
added 126 unique donor IVPs and a serializer-only change; HE added a 52-state
preflight with no science IVPs. The frozen donor pins and this campaign's raw
results remain unchanged; donor runs are counted separately.
