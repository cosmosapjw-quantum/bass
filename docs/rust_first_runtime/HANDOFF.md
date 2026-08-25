# RF-00 handoff

## STATE

- Repository: `https://github.com/cosmosapjw-quantum/bass`.
- Branch: `agent/architecture/rust-first-rf00-20260824-r1`; code head `8f531540a0483541d088e222b1622ec9bc25ffd7`, tree `d14ede2b55e7e6d00f7aff767f7951f4b8012c02`.
- Receipt head: fetch the live branch containing this file; `EVIDENCE.json` declares the self-reference boundary.
- Draft PR: [#25](https://github.com/cosmosapjw-quantum/bass/pull/25), open/draft/unmerged and stacked on the runtime plan branch.

## OUTCOME

- RF-00 now has a 72-route typed inventory, fail-closed verified native dispatch, visible transitional domains, and transitive explicit Python oracles.
- AUD-12 is closed for RF-00: root import is dependency-light; JAX/diffrax/SciPy/SymPy load only through typed optional paths; minimal installation is native wheel plus NumPy.
- Fresh focused proof passed: 65 policy/import, 31 affected-route, and a no-index minimal-install smoke across 25 backend modules.
- The preserved timing ratios are `EXPLORATORY_ONLY` with acceptance claim `NONE`; the benchmark was not rerun.
- Native decision: `REUSED_NATIVE_R3_NO_R4_CONTRACT_REPAIR`; no Cargo/Rust/generated/PyO3/wheel/ABI byte changed.

## OPEN ITEMS

- No RF-00 engineering blocker remains. Remote check state is read live from PR #25.
- R5b PR #21 remains closed evidence; Wolfram PR #22 remains reference-only and unpromoted.
- No speedup, no-regression, formula-authority, full-solver, or production-readiness claim is opened.

## EVIDENCE

- `artifacts/rust_first_runtime/rf00/EVIDENCE.json` SHA-256 `7445b266ff46c5008d7f443f50c2a2d498e905163c027353c1f6a0f5dadd5960`.
- `artifacts/rust_first_runtime/rf00/RAW_MANIFEST.sha256` SHA-256 `2cc23c593a01067d9fe640217e93dd93d16d1dd529ef0d905e557d06600b13eb`.
- Native r3: `artifact/native-repro-bundle-20260824-r3` at `3aef681d2901e77ce638be5925688929800a822a`; archive SHA-256 `1c45dd93b46dc43c6d8c503d3ff1034d60b36fc7aa73ebf19b40ae48b080cec9`.

## BOUNDARIES

- Do not merge or mark ready; do not promote formula authority; do not change tolerances, references, dependencies, Cargo.lock, or physics.
- Do not rerun inherited PASS lanes without a changed lane-relevant precondition.

## EXACTLY ONE NEXT ACTION

Execute RF-BENCH-00 from `docs/rust_first_runtime/SPEC.json` with controlled cpuset/cgroup, effective CPU set, SMT isolation, migrations, CPU pressure/steal, frequency/throttling, and perf running-ratio metadata. If controls are unavailable, record only `EXPLORATORY_ONLY` and make no acceptance claim.
