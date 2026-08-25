# RF-01 handoff

## STATE

- Repository: `https://github.com/cosmosapjw-quantum/bass`.
- Stack base: draft PR #26 branch
  `agent/architecture/rust-first-rf-bench-00-20260825-r1` at
  `8a21642d6b42f882cf8e0233e8579fb2a267f491`.
- RF-01 implementation: `agent/architecture/rust-first-rf01-20260825-r1` at
  `dea69b0d82a3e157cc452c8dfd4a27b1dbb3bd49`, tree
  `1bd251b0dfa098fa5d15790aec29c0355b23ab73`.
- Delivery: stacked draft PR #27, `https://github.com/cosmosapjw-quantum/bass/pull/27`.
  Resolve its exact enclosing head/tree from the live draft PR before work because
  a commit cannot embed its own hash.

## OUTCOME

- `CODE_CONTRACT_PASS`; private-pool RuntimePlan, plan-bound Workspace, typed
  buffer/GIL errors, counters, and two non-timed RF-01 corpus adapters are closed.
- The verified R4 warm-plan digest remains authoritative; source-built CI uses
  the separately typed `UNVERIFIED_DEVELOPMENT_NATIVE_PAYLOAD` digest. Runtime
  architecture fields are identical and only verified build provenance differs.
- Native R4: `artifact/native-repro-bundle-20260825-r4` at
  `b069e46eeb649b7b33e5ca30c3508d144fcd0e2c`, tree
  `53da650f50cc140acf57a6e6044f0675bfb8b17c`.
- Archive SHA-256 `1c587e04e93095d39ec821b2a7cb6824132d9c2ded635ee8c6101410490fabd3`;
  fresh remote reassembly and offline restore PASS.
- `PERFORMANCE_NOT_RUN_BLOCKED_ENVIRONMENT`; acceptance `NONE`; scientific
  behavior change `NONE`; formula authority `UNCHANGED_UNPROMOTED`.

## EVIDENCE

- Sole authority: `artifacts/rust_first_runtime/rf01/EVIDENCE.json`, SHA-256
  `d2208e4f8dca8e13c04a12e1c14e2a97dabbba8fc96ef64895bd74a553f704be`.
- Raw remote receipts: `artifacts/rust_first_runtime/rf01/raw/`.
- Reassemble after authenticated shallow clone:
  `python repro/native/BASS-RF01-NATIVE-20260825T035620Z/reassemble_bundle.py --manifest repro/native/BASS-RF01-NATIVE-20260825T035620Z/BUNDLE_MANIFEST.json --output BASS_NATIVE_REPRO_BASS-RF01-NATIVE-20260825T035620Z.tar.xz`.
- Run the reconstructed archive's `scripts/restore_and_verify.sh --help`, then use
  its fail-closed `--repo-url/--source-commit/--expected-tree/--bundle/--dest/--python`
  interface with pinned Rust 1.94.1 and Python 3.12.

## BOUNDARIES

- Do not merge or mark ready; do not change dependencies, physics, formulae,
  tolerances, references, scientific authority, or start RF-03+.
- Do not rerun inherited PASS or RF-BENCH timing lanes without changed inputs and
  a controlled host.
- Roll back the RF-01 source stack only with the base-verifying revert command in
  `EVIDENCE.json`; preserve immutable R4 as evidence.

## EXACTLY ONE NEXT ACTION

Execute `RF-02` from the live RF-01 draft-PR head, preserving the RF-01 receipts
and leaving RF-03+, SIMD, GPU, timing, and Wolfram work closed.
