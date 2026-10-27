# Endpoint-channel implementation and observed finite run

The single selected unit is `BASS_B3H_ENDPOINT_CHANNEL_INTERPOLATION_20261027`. Its repaired invocation finished on **2026-10-28 00:58:19 KST** with all **50 recorded checks passing**. This is a conditional numerical transaction result pending root scientific admission and publication. No next node was started. Original DAG remains 28/88, delta 0.

## Implementation completed

`code/run_endpoint.py` now composes only the existing new endpoint modules. It loads admitted saved operands and left maps, constructs the 1,414 right gross maps once, checks native source/operator parity including the absolute diffusion correction, and retains separate endpoint energies for all 2,828 tags. Its partial writer saves every completed stage and each endpoint/moment update. Driver failures save a structured traceback and stop; no driver retry exists.

`code/controls_endpoint.py` supplies the prescribed new constant-M/affine-source control. It uses a nonzero initial layer, independently evaluates the affine matrix-exponential solution and polynomial-weight moment, and compares them with the new q2 slow jet and m3 adjoint routines. The selected weight `1+t+t^2` exercises all three adjoint terms. Both endpoint and moment checks passed. Existing actual nonconstant-M m2/m3 moment comparisons are saved with their separate analytic bounds; agreement is diagnostic only.

The new proper clock, q2 endpoints, m3 shared moments and positive Gauss24 integration use the frozen choices. Existing finite-solver corrections for upper-duration slow bounds, retained-layer duration error, and the per-sector core-adapter representation errors are retained. No old scientific driver, left builder, spectral preparation, old tests, consume or plots was executed.

## Actual observations

| Quantity | Saved result |
|---|---:|
| New proper duration | 1708251102.50266885687673938619749 s |
| New proper-duration bound | 1.7082511025517891e-46 s |
| Final 2s fraction | 6.5631873161091926e-15 |
| Final 2p fraction | 1.9731060921618626e-14 |
| Endpoint fraction one-norm bound | 1.4504998149734245e-48 |
| 2s storage residual | 9.42303323692386e-64 nuclei/V0 |
| 2s storage bound | 5.10737835870817e-26 nuclei/V0 |
| 2s bound / actual nonzero storage | 3.90573341212682e-17 |
| 2p storage residual | 1.94308699033301e-60 nuclei/V0 |
| 2p storage bound | 2.84474710857724e-25 nuclei/V0 |
| 2p bound / actual nonzero storage | 7.25327818136165e-17 |
| New outgoing count | 9140.5578708052686205281 nuclei-equivalent events/V0 |
| New outgoing count bound | 6.61967046449805e-31 events/V0 |
| New pulled-back outgoing energy | 1.4936435468613864423108e-14 J/V0 |
| New pulled-back outgoing energy bound | 1.08279173227809e-48 J/V0 |
| Count difference from frozen-left finite model | -3.6091548622898313 events/V0 |
| Count difference from saved QSS baseline | +0.00118363170832454 events/V0 |
| Actual new B3i RHS calls | 1 |
| Maximum own-nonzero RHS relative difference | 0 |

All tagged weighted counts, gross finite donor margins, individual energy tags, common-V0 storage and adiabatic geometry-work checks passed. The core consumer preserves the five sector stress tensors and separate cQ/Q arrays, new bounded duration and right-volume conversion. Expected-zero RHS components are exactly zero. No Friedmann-closure claim is made.

## Actual invocation history and resource debit

The first invocation, at 2026-10-28 00:56:30 KST, failed while importing `mpmath` before the driver entered. The frozen empty PYTHONPATH omitted the existing admitted `runtime_deps`. No map, control, numerical solver or RHS ran. Its CPU/wall debit remains in the same fresh allocation.

Root diagnosed the environment wiring failure and authorized the sole targeted repair. The repair sets PYTHONPATH to the existing dependency directory and leaves the model, precision, solver, bounds and tolerances unchanged. The QSS reporting binding had already been corrected before the initial source freeze to the admitted prior `baseline_correction.old_reference_Nout` and `old_reference_Uout0`; no old outgoing result was recomputed.

| Invocation | Exit | Child CPU | Child wall | Peak RSS |
|---|---:|---:|---:|---:|
| Initial import failure | 1 | 0.082589 s | 0.117552552 s | 11136 KiB |
| Root-authorized environment repair | 0 | 22.551978 s | 22.588370317 s | 167192 KiB |
| Cumulative debit | — | 22.634567 s | 22.705922869 s | 167192 KiB maximum |

The allocation was 120 child CPU seconds, 300 wall seconds, 768 MiB and one numerical thread. Remaining recorded quantities are 97.365433 CPU seconds and 277.294077131 wall seconds. These do not authorize another invocation: the single targeted repair has been used. Wrapper CPU was recorded separately; unmetered preparation cost remains unknown, not zero. Requested executor model is `gpt-6.1-sol`; observed runtime model is null because it was not exposed.

## Evidence locations and identity interpretation

- `results/ENDPOINT_RESULT.json`: complete accepted-by-checks raw transaction, maps, tags, moments, bounds, owners and actual RHS.
- `results/ENDPOINT_PARTIAL.json`: last saved partial state, completed.
- `results/ENDPOINT_SUMMARY.json`: saved-result-only summary.
- `results/EXECUTION_LEDGER.jsonl`: actual STARTED/FAILED and STARTED/COMPLETED meter records.
- `results/endpoint.stdout`, `endpoint.stderr`: preserved initial failure streams.
- `results/endpoint_repair1.stdout`, `endpoint_repair1.stderr`: repaired invocation streams.
- `results/ENDPOINT_INITIAL_IMPORT_FAILURE.json` and `ENDPOINT_FAILURE.json`: the preserved initial pre-driver failure, not a failure of the subsequent completed transaction.
- `provenance/INITIAL_EXECUTION_FREEZE_ENDPOINT.json` and `INITIAL_PRE_NODE_endpoint.json`: initial invocation identities.
- `inputs/EXECUTION_FREEZE_ENDPOINT.json` and `provenance/PRE_NODE_endpoint.json`: actual repaired source/input/environment freeze and near-run readback.
- `provenance/EXECUTION_ENTRY_BUDGET_LEDGER.json`: frozen entry budget bytes. The freeze refers to these same entry bytes under the original `BUDGET_LEDGER.json` path; the current ledger was updated after execution to report the actual debit.

Fresh own/central/AGENTS and parallel readbacks came from root's actual remote reads, explicitly attributed in preflight. The local central AGENTS content and current live-agent inventory were also read. Source code, dependencies and saved immutable inputs were frozen before the repaired invocation. Post-run ledger/summary/report writes are reporting changes.

All new numerical bounds are **analytic truncation plus declared MP arithmetic allowance, conditional on admitted saved input values**. They are not interval-arithmetic proofs. Historical incoming quadrature remainder stays null. The two baseline differences are finite-model differences, not error estimates. Physical eS/en/eE/geometry/temporal/total and global radii remain null; L4 remains false. Independent reviewer reads actual saved code/results without scientific reruns. Root owns admission and publication.
