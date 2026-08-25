# BASS Rust-first runtime closure

Status: `RF-BENCH-00 RUNNER VALIDATION PASS / HOST EXPLORATORY_ONLY /
PERFORMANCE NOT RUN / DRAFT UNMERGED`

`SPEC.json` remains the machine authority. Detailed receipts and exact digests
are indexed by `artifacts/rust_first_runtime/rfbench00/EVIDENCE.json` rather
than repeated here.

## Current delivery

- RF-BENCH-00 is stacked from PR #25 head
  `980050fcb7cec466a94cdd0c5534254013901d51` in draft PR #26.
- Runner implementation and bounded repairs end at
  `0ec0966f03ac3293157e78c8094c1e218c687a6b`, tree
  `9ca6c3d464c9a9053889ef21eac255aeb79ebb94`.
- Neither PR may be merged or marked ready without approval.

## Validated contract

- The read-only probe emits only `DEDICATED_BARE_METAL`,
  `CONTROLLED_SHARED_PAIRED`, or `EXPLORATORY_ONLY`; missing evidence fails
  closed and no privileged host mutation is performed.
- Topology-derived strict-1T and physical-12T strata reserve SMT siblings and
  use one logical CPU per physical core on one NUMA node where available.
- The runner freezes balanced seeded AB/BA pairs, 30 valid pairs within 90
  attempts, a two-second steady-state floor, a deterministic 10,000-replicate
  paired bootstrap, and rejection before candidate-statistics visibility.
- `whole-runtime-v1` covers all eight required strata with 11 entries and one
  sealed, default-off holdout. Nine future-node or partial adapters remain
  explicit, so a whole-runtime performance campaign is not yet eligible.
- CI runs only the three RF-BENCH focused files and static corpus/config
  validation. It never probes the host, runs a workload, or builds native code.

## Current host boundary

This session is `EXPLORATORY_ONLY`. The controlled request returned
`BLOCKED_ENVIRONMENT` before candidate resolution or statistics visibility.
Isolation/exclusive-cpuset, PMU running/event capacity, and complete thermal
counter evidence are insufficient here. No workload, timing sample, or holdout
ran.

RF-BENCH-00 therefore makes no acceptance, rejection, speedup, no-regression,
scaling, or contention-independent claim. The old affinity-only receipt remains
historical exploratory evidence and was not rerun.

## Native and review boundary

Native object identities are unchanged from RF-00, so the decision is
`REUSED_NATIVE_R3_NO_R4_RF_BENCH_00`; Cargo, wheel, ABI, and restore lanes were
not rerun. The final 30 focused checks pass. The bounded independent repair
closeout passes for code and contract only; it does not promote host authority
or supply performance evidence.

## Exactly one next action

Execute `RF-01`: Runtime object, data model, workspace, and modular PyO3
boundary.
