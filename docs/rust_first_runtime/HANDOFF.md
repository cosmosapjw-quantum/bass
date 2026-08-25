# RF-BENCH-00 handoff

## STATE

- Repository: `https://github.com/cosmosapjw-quantum/bass`.
- Branch: `agent/architecture/rust-first-rf-bench-00-20260825-r1`, stacked on
  PR #25 head `980050fcb7cec466a94cdd0c5534254013901d51`.
- Code head: `0ec0966f03ac3293157e78c8094c1e218c687a6b`, tree
  `9ca6c3d464c9a9053889ef21eac255aeb79ebb94`.
- Draft PR: [#26](https://github.com/cosmosapjw-quantum/bass/pull/26), open,
  draft, and unmerged. Keep both stacked PRs draft and unmerged.

## OUTCOME

- The runner is read-only and fails closed below
  `CONTROLLED_SHARED_PAIRED`; candidate resolution and statistics remain hidden
  when host authority is insufficient.
- Strict-1T and physical-12T selections bind execution CPUs plus reserved SMT
  sibling evidence. AB/BA scheduling, contamination gates, duration floor,
  pair/attempt limits, and deterministic bootstrap are frozen.
- `whole-runtime-v1` has eight strata, 11 entries, and one default-off holdout;
  future adapters remain typed blockers and make campaigns ineligible.
- Final focused proof: 30 passed. Independent repair closeout:
  `PASS_CODE_CONTRACT_ONLY`.
- Current host: `EXPLORATORY_ONLY`; controlled request:
  `BLOCKED_ENVIRONMENT`; performance: `NOT_RUN`.

## EVIDENCE

- Machine index: `artifacts/rust_first_runtime/rfbench00/EVIDENCE.json`.
- Raw manifest: `artifacts/rust_first_runtime/rfbench00/RAW_MANIFEST.sha256`.
- Native decision: `REUSED_NATIVE_R3_NO_R4_RF_BENCH_00`; immutable r3 head
  `3aef681d2901e77ce638be5925688929800a822a`.

## BOUNDARIES

- No performance acceptance/rejection, speedup, no-regression, scaling,
  formula-authority, full-suite, Wolfram, Cargo, or native-rebuild claim opened.
- Do not merge, mark ready, promote formula authority, or rerun inherited PASS
  lanes without a changed lane-relevant precondition.

## EXACTLY ONE NEXT ACTION

Execute RF-01: Runtime object, data model, workspace, and modular PyO3 boundary.
