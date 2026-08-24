# BASS Rust-first runtime closure

Status: `DRAFT_PLAN_ONLY / NO_RUNTIME_CHANGE / NO_AUTHORITY_PROMOTION`

This package converts the current recovery/performance state into one executable
program for a Rust-default numerical runtime with a thin Python frontend. The
machine authority is `SPEC.json`; this file is only its short human index.

## Audited starting point

- Performance base: PR #23 head `4c6150578d1e7fea43e0d32c01664c92094c8c05`,
  tree `e097263a8d9657edee6976b138534634b1be4d48`.
- R5b contract: PR #21 head `b810092755837ccfa96502aa7e132a50c3fcbd33`;
  34-case receipt reused. The ill-conditioned error-of-error comparator remains retired.
- Wolfram generic candidate: PR #22 head
  `75f0b128634ec60b853519f9f6d530f113b54a81`; static-only and unpromoted.
- Native reproduction: `artifact/native-repro-bundle-20260824-r2` at
  `61045b6e5a0d7b026437e0d3586df66706578161`; archive SHA-256
  `ef0f35b76ab4ef4877ed577afe391ed677a7a6767bcbc64db62dd853d757afca`.
- Existing PR #23 evidence SHA-256:
  `f4ab66fc575122460d554c152deca5ad6c57fd80cb85e0ee11c892318abc358a`.

No inherited PASS was rerun. No Wolfram command, benchmark, Cargo build, dependency
change, tolerance change, reference change, merge, ready-for-review transition, or
formula-authority promotion was performed for this package.

## Adversarial verdict

`AT_RISK_BUT_READY_FOR_CONTROLLED_MIGRATION`.

The repository already contains substantial Rust compute coverage and an older
Rust-core/Python-frontend plan. The remaining problem is architectural closure:
production numerical work is split across Rust, Python/NumPy/SciPy, and JAX;
backend import failures silently select Python; the PyO3 surface is concentrated in
a large `lib.rs`; there is no checked-in GitHub workflow; current human docs are
materially behind the code; and the benchmark host evidence cannot support an
external-contention-independent claim.

Candidate B is correctness-qualified but performance-unmeasured. The frozen 10%
materiality rule remains valid for that candidate only. It is not a universal gate
for the full migration: architecture-enabling steps use correctness plus no-regression,
while cumulative milestones use pre-registered end-to-end performance gates.

The legacy PR #23 timing corpus remains useful for continuity, but Q and R5b already
cross a coarse Rust boundary and dominate it. It therefore cannot certify the whole
runtime. `RF-BENCH-00` freezes a broader `whole-runtime-v1` corpus and holdout before
any migration speedup result is inspected.

## Chosen architecture

- Python owns configuration, validation, orchestration, result objects, plotting,
  and an explicit slow oracle. Optional JAX/diffrax/SciPy/SymPy stacks load lazily.
- Rust owns every production numerical loop from validated input through completed
  trajectories, batches, moments, rays, collisions, observables, and checkpoints.
- RF-00 first installs a typed capability matrix: already native-supported routes
  are fail-closed Rust, while unmigrated routes remain visibly transitional rather
  than exception-driven fallbacks. RF-07 performs the global `rust_required` cutover.
  `python_oracle` is always explicit.
- Calls cross PyO3 at coarse operation boundaries using contiguous typed buffers,
  persistent plans/workspaces, GIL detachment, and no Python callback in inner loops.
- Parallelism is deterministic and coarse first (ensembles/rays/modes), with one
  owned Rayon pool and explicit prevention of nested BLAS/OpenMP oversubscription.
- Stable scalar/autovectorized code is the portable authority. Target-specific
  `std::arch` variants use runtime dispatch and keep scalar fallback. Nightly
  `portable_simd`, global `target-cpu=native`, fast-math, and reduced precision are
  not authority paths.
- GPU support is optional and batch-driven. JAX, PyTorch, or a custom CUDA kernel is
  admitted only when transfer-inclusive f64 evidence beats the Rust CPU path; the
  CPU backend remains mandatory and authoritative.

The Wolfram/xAct lane is separate and non-blocking. `WF-00` starts from the archived
PR #22 bytes and turns a `LieAlgebraSpec` into deterministic equations and typed
SymIR, with sparse/memoized/staged evaluation and fresh Wolfram evidence before any
formula-authority decision.

## Performance evidence classes

Literal independence from other CPU use is not claimed on a shared host.

- `DEDICATED_BARE_METAL`: absolute and paired claims allowed.
- `CONTROLLED_SHARED_PAIRED`: valid isolated cgroup-v2 partition plus contamination
  rejection; same-session paired claims only.
- `EXPLORATORY_ONLY`: affinity/taskset without proven exclusivity; no promotion.

The new protocol selects physical cores from topology, reserves SMT siblings,
prevents nested pools, balances randomized `AB/BA` pairs, records wall time and PMU
counters, rejects steal/thermal/migration/PSI/external-work contamination, and uses a
paired bootstrap confidence interval. A contaminated sample is discarded, not
explained away. A shared-host run is never described as contention-independent.

## Delivery surfaces

- `SPEC.json`: sole machine-readable audit, architecture, DAG, benchmark contract,
  acceptance rules, risk register, and exact legacy lock.
- `HANDOFF.md`: short Codex resume prompt.
- `README.md`: this human index.

Machine evidence is referenced, not reproduced. Raw logs, archive-part hashes, and
legacy PASS matrices remain in their existing authority artifacts.

## Next action

Execute work item `RF-00` from `SPEC.json`: create the Rust-required backend-policy
and packaging boundary on a fresh stacked branch, without moving numerical physics.
Do not start subsystem ports until its API/error/no-silent-fallback contract passes.
