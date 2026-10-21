# ACCEL02: reflected massive three-moment kernel

Frozen by the Astra controller on 2026-10-21 (Asia/Seoul). This is an explicitly
authorized continuation of the completed warm C15 729-case pilot and ACCEL01.
It is a bounded theory-to-implementation unit; no performance benchmark or
full sweep is requested.

## Source and ownership

- BASS base: `4f19e6eaf50e8458d59d27ff47f03e9d8c8b22ca`, root tree
  `09dfc58050105f8169b1d7d21c3fbef2eb60d0ba` (PR177).
- REI base: `98fcf3943fa54e089b0292d166c3a47becb5edb8`, root tree
  `3fc9dd32bb11cf3e120fd06e3cde5006a35c4d53` (PR214).
- Original pilot subtree: `b51ac26b65339197c800069cbdb04efda872bd83`.
- ACCEL01 source/backend identity before this change:
  `525177ac2a705852664ba22ed2d41722fb21a497ceb63c15ec73e75bbcb764b6`.
- Scientific context:
  `f5ab253bfd65a3af5b62dcc236cddb18e702b368b7e87e6213943617c1aab398`.
- New lane: `research/rei_sigma_pi_native_moments_20261021` (ACCEL02).
- New branch: `research/rei-sigma-pi-native-moments-20261021`, based on each
  repo's current ACCEL01 branch. Do not modify shared existing remote branches.
- Implementation may add files in this new lane and make a small optional
  backend interface change in ACCEL01 `batch_worker.py`. Original pilot,
  cached_context.py, work_plan.py and shared_executor.py remain unchanged.
- Use the existing `bass_work` source checkout/snapshot. No clone, worktree,
  installation, bootstrap, process termination, or unrelated file mutation.
- REI root policy: Astra framing/criteria; lower-tier implementation and runs;
  one fresh read-only Astra review; one bounded authorized repair if needed.
  Requested executor model is recorded separately from observed identity.

## Physical scope and exact-arithmetic statement

Non-tilted LRS Bianchi I, independent matter/radiation P2 seeds, warm conditional
interval a=0.1999 to0.2, L=8, 8X8 source grid, massive fraction0.1, mass/T=30.
All solver, chemistry, Thomson, UV, time-step, compression and output conventions
remain the pinned owner implementation. No full EoR, general non-LRS, full Q^a,
global convergence or measured speedup claim follows.

The existing 96 radial by32 angular quadrature is retained. It is evaluated
through16 reflected pairs, NOT replaced by a new16-node quadrature. For
r=exp(-x), u=mu^2, R2=exp(2b)(1-u)+exp(-4b)u, p2=r^2 q^2 R2,
E=sqrt(m^2+p2), v2=p2/E^2 and u_phys=exp(-4b)u/R2, the kernels are
r^3 W E, r^3 W E v2, r^3 W E v2(3u_phys-1)/2.
Paired nodes have identical kernels; combine their ORIGINAL weights once.

Require actual input parity, fixed96x32 binary64 contiguous shape, finite
nonnegative weights, mu2 in[0,1], nonnegative q2 and positive finite mass.
Actual mu, P2 and w_mu pairing must agree as well. Copy/freeze data per-model
before caching. A failed parity/shape check rejects native selection explicitly;
do not silently call a different backend. Odd/tilted distributions are outside
this native backend's scope.

## Implementation requirements

1. A dependency-light C++17 shared library with a narrow C ABI, Python ctypes
   wrapper and a build command. Folded data are prepared once per model. Evaluate
   the three moments in one call without full96x32 runtime temporary arrays.
   Precompute the16 angle factors once per call. Use Neumaier compensated sums
   (documented in Ogita/Rump/Oishi2005, introductory Eq.1.3); no sorting or
   new quadrature. Keep a consistent explicit multiplication order.
2. Use `-O3 -std=c++17 -fPIC -shared -fno-fast-math -ffp-contract=off` (or
   exactly equivalent supported compiler flags). No `-ffast-math`, `-Ofast`,
   architecture-specific mandatory ISA, OpenMP, GPU, MPI or new Python package.
   Build once on the target. Record source hash, compiler/version, flags, loaded
   shared-library hash and platform. Do not commit compiled binaries as source.
   Native availability is explicit and does not affect default completed729
   no-work. A stale source/build binding must give a clear rebuild instruction.
3. Compose the existing exact per-model binary64 (x,b) cache with this new miss
   evaluator. Retain domain0<=x<=4, abs(b)<=1, finite rejection, immutable cache
   lifetime and fresh model state. Identical calls within the native model may
   reuse its tuple exactly; native-vs-owner agreement is numerical, not bitwise.
4. Add an explicit optional backend specification to the existing worker API,
   and a native lane CLI that selects it. No mutation of module globals or
   monkeypatching. Default worker behavior remains the Python exact-cache path.
   Backend source identity must include the changed dispatcher, new loader,
   C++ source, build recipe, frozen numerical contract and actual binary/build
   identity. It must not falsely reuse ACCEL01's exact-cache source namespace.
   Keep scientific coordinates/physics identity distinct from execution backend.
5. Reuse work_plan and shared_executor for completed-case exclusion, dynamic
   NCP resource admission, case locking, partial completion and restart. All
   pending jobs use numerical-library threads1; NCP caps64 CPU/128GiB are
   ceilings, not reserved resources. Resample real availability at launch;
   other sessions do not justify stopping or killing their processes.
6. CLI supports plan, prepare and run-group, and documented compilation and
   executor commands. Pending0 produces a no-work receipt without compilation,
   native library load or job creation. Custom inputs retain distinct records.

## Frozen primary verification

This is a scientific correctness check, not a timing benchmark. Preserve raw
reference/native tuples and representative output values in small JSON/CSV.
Do not broaden tests solely to accumulate PASS counts.

A. Kernel comparison:140points with alpha_m in[-0.9,0,0.4,1.8],
x in[0,log(0.2/0.1999),0.1,1,4], b in[-1,-0.1,-1e-8,0,1e-8,0.1,1].
For k=0,1,2 require abs(J_native[k]-J_owner[k])/J_owner[0] <=64*eps64,
eps64=2^-52. This is a predeclared empirical acceptance envelope, not a global
analytic bound on exp/sqrt, quadrature or the coupled solution. Also check
0<=J1<=J0 and -J1/2<=J2<=J1 up to the same absolute rounding envelope.
Use absolute energy-scaled error for near-zero signed stress, not relative J2.

B. Differential identities at three interior (x,b)=(0.01,0),(0.5,0.02),(2,-0.3),
alpha_m=0.4: a five-point centered derivative with h=2^-15 must satisfy
abs(d_x J0+3J0+J1)/J0<=2e-9 and abs(d_b J0+2J2)/J0<=2e-9.
This verifies an implementation identity, not time/grid convergence.

C. Five original-vs-native warm trajectories, each nsteps=2, signed coordinates
(Sigma,Pi_m,Pi_r): (0,0,0), (2.5e-4,0,0), (0,1e-5,0), (0,0,1e-5),
(0,4e-4,-4e-4). These are new coarse verification runs, not replacements for
the completed64-step pilot. All original8 stored gates must PASS unchanged:
number5e-12, energy5e-11, gamma/nu monopole3e-9, initial mapping3e-13,
positive matter/radiation P2, finite success JSON.
Compare initial/history/final normalized signed Sigma, Pi_m, Pi_r, Pi_total:
absolute difference<=5e-14. H relative difference<=5e-13, Tgas relative<=5e-12,
x_HII and x_HeII absolute<=5e-13. Retain signed totals and never clip to zero.
Report tensor work differences in units H^3/kappa_t, equivalent to2 Sigma Pi;
absolute normalized difference<=5e-14. No physical tolerance may be widened
merely to obtain PASS; return unexpected failures to the controller.

D. Targeted integration checks: native cache hit, explicit bad parity rejection,
changed build/source rejection, numeric backend distinction, completed729
pending0 no native load/build, and one native pending worker execution followed
by same-case reuse (no second solve). Reuse one of the five native cases for
the worker if practical. Run existing worker unit tests because its dispatcher
changes; do not rerun unchanged cache/planner suites or the original729 sweep.

## Limits, stopping and release

Local runtime observed8CPU/8GiB, current Python3.12.14 and C++17 build available.
Use at most2 worker processes for bounded verification and threads1. Initial
numerical budget: at most10 tiny trajectories (5reference+5native), plus1 worker
case only if needed to exercise the real pipeline; at most3 compile attempts.
Stop and report ambiguous physics/identity, criterion failure, or need to alter
solver/closure. A controller-authorized targeted repair is the only test-loop
extension. No benchmark suite, original729 rerun or fresh large parameter grid.

Stage A=intake/theory/contract published+backed up. Stage B=implementation+raw
verification published+backed up, admission pending review. Stage C=one independent
review, scoped decision, report, runnable Codex/next-thread handoffs, final push
and backup. Every R/C node records its evidence, current publication/backup
checkpoint and next executable transition. Do not claim a submitted backup
complete without an actual provider acknowledgement.
