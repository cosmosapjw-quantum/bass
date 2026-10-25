# Saved-input consumer implementation

The root authorized the frozen execution after source and code review. All
three ordered children completed successfully once: 13 focused tests passed,
the consumer saved 512 actual births and 514 geometry endpoints with four
algebraic core RHS evaluations, and the plotter saved three actual-input
figures. The cumulative measured child cost was 3.739223223001318 wall seconds
and 3.7262999999999997 CPU seconds. `results/EXECUTION_LEDGER.json` preserves
the exact commands, frozen Python hashes, runtime/dependency identities and
per-child costs; `results/attempt_01` through `attempt_03` preserve their
start receipts and raw stdout/stderr. There were no retries or further
scientific executions. Independent final scientific admission remains a root
decision.

The mechanical preparation copied 35 immutable selected inputs and parsed all
eight new Python files with `ast.parse`. No scientific execution occurred
during preparation; no source transaction or trajectory was run in this unit.

## Frozen reproduction commands

Run from `research/bass_b3g_actual_cohort_binding_20261025`:

```sh
python code/metered_run.py tests/test_binding.py
python code/metered_run.py code/consume_saved.py
python code/metered_run.py code/plot_saved.py
```

`FROZEN_COMMANDS.json` records exact ordered commands and Python byte hashes.
The driver allows one initial test, one consumer and one plotting child. A
failed or incomplete attempt prevents automatic replay. The implementation
allocation is 60 wall / 40 child CPU seconds, inside the task ceiling of 120
wall / 60 CPU seconds. Each child is limited to 30 wall / 20 CPU seconds.
Historical remaining budgets are null and budget_reset is false. The unchanged
B3f execution ledger and B3c resource ledger preserve historical costs and
failures; their allocations are not transferred into this task.

## Immutable input reproduction

All mandatory consumer inputs are beneath `inputs/`, with exact SHA256 and byte
counts in `inputs/MANIFEST.json`. The unchanged B3f `ball`/`compose`, angular
helpers, line-card imports and core are included beneath `inputs/b3f`; they
are imported after byte checks. No B3f sweep or old tests are called.

The original REC NPZ is included in the full source ZIP and excluded from the
public Git file selection to avoid duplicating its existing immutable public
blob. It is optional for this postprocessor because the exact saved owner
`HISTORY_ADMISSION.json` supplies the 313 previously admitted query rows; no
NPZ interpolation/JVP is executed. If present, the full NPZ is byte-verified.
To restore it in a Git checkout, run from this lane directory:

```sh
curl --fail --location --output inputs/rec_history/pr05b2_source_history_v060.npz https://raw.githubusercontent.com/cosmosapjw-quantum/rec_bianchi/ea89c97abeb7a663a813f00e9aadddaf0b32a6a9/data/pr05b2_source_history_v060.npz
```

Its required size is 35,239,470 bytes and SHA256 is
`d4f82542e13fed4ff0bb60b17865d8b9de5e090a2366108169c3da7a21fcb4b1`.
The next consumer import verifies it if present. All runtime paths are local
to the source tree. Absolute recovery paths in the manifest document original
copy provenance only.

## Result schemas and interpretation

- `BIRTH_ROWS.json` contains all 512 original transfer keys, receipt snapshot
  hashes, original model/card/clock/frame labels, integrated counts, birth
  tensor and signed anisotropic stress. Representation residuals use emitted
  energy; atom stock residuals use their separately declared positive stock.
  `BIRTH_ROWS.csv` provides a numeric view with the same keys and times.
- `SAVED_ENDPOINT_BRIDGE.json` retains all 514 endpoints and separate R, X,
  radiation stress tensors. Source rates are zero because kicks were already
  applied. Only the first/final endpoints in each fixture call the existing
  core RHS, four algebraic evaluations in total.
- `NATIVE_SOURCE_READINESS.json` preserves native departure/reference identity,
  original instantaneous ledger, native constants and all 313 saved history
  rows. Native Wien and standalone LINE01 Planck occupations have separate
  names. Current finite donor structural fields remain missing and finite
  absorption is false.
- `CONDITIONAL_TRANSPORT.json` keeps actual final cohort transport dependent
  on midpoint beta and its interpolation error bound. Recovered alpha is a
  nominal log-density reconstruction, with numerical error bound null. G1C
  bounds apply only to supplied radii or interval-wide envelopes; saved
  samples do not establish such envelopes.
- `SUMMARY.json`, `TEST_RESULTS.json` and `EXECUTION_LEDGER.json` report the
  observed numerical scope and actual execution costs, without setting a
  whole BASS physical percentage or L4 admission.
- `ACTUAL_BIRTHS.png`, `SECTOR_STRESS.png` and `GEOMETRY_RESIDUALS.png` plot
  saved consumer data. Linear residual axes retain exact zeros. Symlog density
  panels show the distinct sector scales without replacing zeros.

The source-energy physical radius remains null, outside the unchanged
fixed-energy B3f theorem. Numerical reconstruction residuals never populate
physical uncertainty columns. No synthetic finite donor becomes an actual
input admission. Independent scientific admission remains a root decision.
