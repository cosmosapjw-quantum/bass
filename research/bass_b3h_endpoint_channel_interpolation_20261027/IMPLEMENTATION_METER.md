# Endpoint resource wrapper

The executable boundary is `python3 code/metered.py endpoint`, run from this
unit. The wrapper launches exactly `sys.executable code/run_endpoint.py`. It
contains standard-library accounting and metadata handling only, imports no
scientific module, and performs no numerical work itself.

## Frozen execution interface

`inputs/EXECUTION_FREEZE_ENDPOINT.json` has status
`READY_FOR_AUTHORIZED_ENDPOINT`, `commands` equal to
`{"endpoint": [actual_sys_executable, "code/run_endpoint.py"]}`, a `files`
list of path/SHA256 records, and an `environment` map. Paths in `files` are
relative to the unit; admitted external immutable files may use `../` paths.
The coordinator records actual dependency identities and the invocation in this
freeze. `provenance/PRE_NODE_endpoint.json` records node `endpoint` with
`actual_readback: true` for the actual fresh AGENTS/HEAD/parallel observation.
The wrapper checks these existing execution requirements and the actual S0
root authorization in `delivery/S0_ROOT_ACK.json`; it adds no further root
permission step.

Required environment values are `OMP_NUM_THREADS`, `OPENBLAS_NUM_THREADS`,
`MKL_NUM_THREADS`, `NUMEXPR_NUM_THREADS`, `BLIS_NUM_THREADS`, and
`VECLIB_MAXIMUM_THREADS` all `1`; `OMP_DYNAMIC` and `MKL_DYNAMIC` both `FALSE`;
`PYTHONDONTWRITEBYTECODE=1`; and
`PYTHONPATH=/workspace/scratch/2a7ffd1a5e61/runtime_deps`. Other exact overrides
may be recorded in the same map. The driver obtains its code directory from
normal Python script execution. Root identified that the default interpreter
does not discover mpmath and authorized this dependency-path correction. The
execution coordinator reported that the first child had already failed its
mpmath import; its debit remains in the cumulative execution ledger and any
targeted repair still requires root authorization. The runtime dependency
directory was confirmed by file
inventory only; this worker imported no dependency or scientific module.

## Fresh cumulative meter

The wrapper reads the fresh allocation in `BUDGET_LEDGER.json` and enforces
120 cumulative child CPU seconds, 300 cumulative child wall seconds,
768 MiB address space, and one numerical thread. `RLIMIT_CPU` uses the floor
of the remaining CPU budget; `RLIMIT_AS` is 805306368 bytes. Child wall timeout
kills and reaps the child. Measured elapsed wall can exceed the configured
timeout by the small termination/accounting overhead, which is retained in the
actual debit rather than hidden. Memory is an address-space limit; observed
peak RSS is recorded separately, not mislabeled as the address-space cap.

Each attempted launch appends and fsyncs a `STARTED` record to
`results/EXECUTION_LEDGER.jsonl`, then a `COMPLETED` record on zero exit or a
`FAILED` record on nonzero exit, timeout, or launch/output error. The terminal
record preserves child user/system/total CPU, elapsed wall, Linux peak RSS in
KiB, wrapper CPU from entry through accounting, cumulative debit, remaining
allocation, return code, and any wrapper-observed error. Raw output is retained
in `results/endpoint.stdout` and `results/endpoint.stderr`. No result is inferred
from a successful process status; scientific checks remain the driver's and
root reviewer's responsibility.

The local stage-coverage reconciliation restored the actual ST receipt into
`STAGE_LEDGER.json` and `DAG.json`: requested bookkeeping executor model
`gpt-6.1-sol`, observed runtime model null. It used saved local JSON only,
performed no scientific execution, and left S0/ST archived snapshots unchanged.

There is one planned invocation and no automatic retry. An incomplete debit
stops execution for root interpretation. After a production invocation,
at most one targeted repair can run within the same remaining budget, only if
the freeze explicitly records `root_authorized_targeted_repair: true` and a
nonempty `targeted_repair_reason`. Its raw files are
`results/endpoint_repair1.stdout` and `.stderr`. This also permits a root-diagnosed
acceptance defect after a zero process exit; a zero exit does not itself grant
repair authorization. No earlier allocation is reopened and no
historical remainder is carried forward; historical remaining CPU/wall stay
null. Preparation outside this wrapper is unknown, never represented as zero.

Requested execution identity comes from the budget's
`requested_executor_model`; observed runtime model identity is null because
this worker has no actual runtime identity observation. Python executable and
version are recorded as observable software metadata.

## Mechanical validation

Only syntax parsing of `code/metered.py` was performed while implementing this
wrapper. No scientific source was imported, no driver was executed, and no
scientific budget was consumed by this worker. The driver/freeze coordinator
owns the sole authorized scientific execution after the freeze and pre-node
records are complete.
