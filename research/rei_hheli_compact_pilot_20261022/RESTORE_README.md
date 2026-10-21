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
see `intake/RUNTIME_INTAKE.json` for the timestamp and raw observations. Start
with at most four workers, and use current quota, load, memory and peer-work
observations when admitting work. A 64 CPU / 128 GiB NCP host must be measured
on that host; no NCP resource or execution claim is made by this checkpoint.

## Source entry points

These are the implemented commands, expressed from the restored repository
root. Their presence here does not assert that the complete campaign has run.
Current execution evidence covers127 compact cases and2 full62 oracles,193
epochs each, with all owner gates passed. Final independent scientific admission
remains pending at the checkpoint B boundary; see its actual receipts.

```bash
python research/rei_hheli_compact_pilot_20261022/code/verify_compact.py
python research/rei_hheli_compact_pilot_20261022/code/run_pilot.py --plan
python research/rei_hheli_compact_pilot_20261022/code/run_full62_oracles.py --execute
python research/rei_hheli_compact_pilot_20261022/code/run_pilot.py --execute --output research/rei_hheli_compact_pilot_20261022/results/pilot_v2
```

The two full62 oracles are `s04_m04_r04` and `cancel_positive_matter`.
The dispatcher must preserve completed raw results, bound concurrency, and
report failed gates without silently retrying with changed scientific inputs.
Use the root Stage B release after the operational resource-admission repair
before executing the planned campaign. Completed plot/aggregation entry point is `code/analyze_pilot.py`; paired
implementation checks are in `code/verify_paired.py`. See `IMPLEMENTATION.md`
and execution receipts for exact completed command lines.

The required actual campaign has 127 distinct cases, each with 193 epochs from
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
checkpoint and continue from the `next_node` in `DAG.json`. A pending independent
review or root admission remains pending after restoration. Preserve failed
results and diagnosis records; do not clip or renormalize output to pass a gate.

## Checkpoint B and C payload distinction

Checkpoint B is a compact source/evidence snapshot. It includes the exact case
completion manifests and `results/analysis/SUMMARY.json`, and intentionally
excludes raw NPZ arrays, figures and history/plot-source tables. Checkpoint C
will carry the complete successful `results/pilot_v2` and full62 oracle arrays,
figures, history tables, plot-source arrays, final report and review.

The first attempt `results/pilot` wrote127 raw trajectories before final JSON
metadata failed on a NumPy boolean. Its original33,131,538-byte directory stays
locally preserved. The repaired scalar serializer reran the same127 cases in
`results/pilot_v2`; physical dynamics, numerical controls and gate thresholds
were unchanged. Failure logs/receipts and the old/new source relation are kept
in the checkpoints; the first-attempt raw arrays are not duplicated in them.
