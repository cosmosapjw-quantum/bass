# Reproduce the BASS evolving redistribution experiment

Draft PR341, frozen parent PR339 `0577ef0a40cf10130a5933eb52c7230d4de1f11b`. Current authority: `FINAL_REPORT.md`, `STATUS.json`, `SOURCE_PACKET_RESULTS.json`, `TIME_DEPENDENCE_AND_CONVERGENCE.json`, `VERIFICATION_AND_HOSTILE.json`. The full finite-domain model and approximation order are in `DESIGN_AND_THEORY.md`.

## Inputs and interpretation
All parent source inputs are Git-owned. `redistribution.background()` verifies five original input blobs at the frozen parent SHA before invoking the original five-state RHS. It re-integrates geometry and derives the moving angular measure, rather than inventing sky weights for the old26 rays. The positive angular quadrature is new and convergence-tested. Prescribed trace populations, thermal history and finite n<=3 tagged photon-destruction fates remain external source functions.

The adopted collision approximation is leading frequency FP plus a factorized Rayleigh angular operator, not the full joint R_II redistribution kernel. The tagged source runs are dilute linear response; stimulated BE behavior is tested in the separate nonlinear equilibrium problem. Finite red/blue boundaries are absorbing terminal events, not global escape. Energy ledgers distinguish normal bulk exchange, atom-frame frequency heat, redshift work and removed-photon energy; no self-consistent gas/metric update is performed.

## Commands
From the repository root, using Python3 with NumPy/SciPy/SymPy (inherited cascade import), run:

```bash
export PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
d=research/typeii_redistribution_phase_20261116
python3 "$d/test_redistribution.py"
python3 "$d/verify_kernels.py"
python3 "$d/packet_campaign.py"
python3 "$d/verify_time_dependence.py"
python3 "$d/verify_final.py"
```

`packet_campaign.py` produces10 cases; `verify_time_dependence.py` adds5 higher-resolution/boundary/source-time cases and the independent unsplit sparse BDF comparison. The final verification actually reruns the kernel, baseline packet and fine evolving packet under optimized Python, checking7 deterministic output hashes. It does not claim an independent author or subagent.

Do not treat `max_count_ledger_defect` as a physical model error estimate. The actual frequency/time refinement, angular resolution, paired evolving-minus-frozen difference and boundary sensitivity are separate evidence. The extremely small final survival in the z1100 band is not meaningful to many decimal digits; the terminal-event probabilities and their resolution dependence are the useful observables.

## Files
- `redistribution.py`: exact tetrad/measure, angular generator and conservative thermal frequency primitives.
- `packet_campaign.py`: evolving source packet and separate number/energy/fate counters.
- `verify_kernels.py`: Jacobian, BE equilibrium, entropy, heat and stiff-storage controls.
- `verify_time_dependence.py`: independent temporal solver and extra source/refinement runs.
- `verify_final.py`: unit/rejection/replay and hostile physical-model controls.
- `PACKET_CASE_SUMMARY.csv`: inspectable table of15 actual cases.
- `PACKET_*_TRACE.csv`, `PACKET_*_RESULT.json`, `PACKET_*_FINAL_COUNTS.npy`: complete individual case outputs.
- `KERNEL_AND_GEOMETRY_VERIFICATION.json`, `SOURCE_PACKET_RESULTS.json`, `TIME_DEPENDENCE_AND_CONVERGENCE.json`, `VERIFICATION_AND_HOSTILE.json`: evidence, not substitutes for the actual data.

## Preservation and next step
Each phase is committed, pushed with exact remote HEAD check, and archived under `/home/cosmosapjw/research_backups/bass_typeii_redistribution_phase_20261116/`. The final commit hash is recorded in an external receipt to avoid a self-referential file. External copies were not attempted because PR339's repeated ENOSPC is unresolved. No cleanup/storage-configuration change was authorized or performed. Upper DAG9/15, zero new full-production nodes, StageII and JoinJ1 remain held. Keep Draft, no auto-merge.

Next: source-matched correlated angular-frequency redistribution and conservative outer-frequency boundary matching/re-entry. Reuse the current count measure and equilibrium tests, rather than treating factorization or finite-band exit as exact physics.
