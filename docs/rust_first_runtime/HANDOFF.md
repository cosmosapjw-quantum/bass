# RF-00 handoff

## STATE

- Repository: `https://github.com/cosmosapjw-quantum/bass`
- Plan authority: `agent/architecture/rust-first-runtime-closure-20260824-r1` at `0cdcdbf20c867e9e29ef68ed1849f97d8af44ac4`; SPEC SHA-256 `dcd4f89fe7a2ad73f22574357df53fcbea437d83f1b4faae08250e2ab46b4efa`.
- RF-00 branch: `agent/architecture/rust-first-rf00-20260824-r1`; native implementation `4073f5a66910142545167b2987bfe350239fd7c9`, tree `f0d98afc9139281a04a0dece2221a055a85c2fb0`.
- Draft PR: [#25](https://github.com/cosmosapjw-quantum/bass/pull/25), stacked on the plan branch, open/draft/unmerged. The live branch tip after this evidence-only commit is the delivery receipt head.

## OUTCOME

- RF-00 is closed: supported routes fail closed through typed `rust_required`; explicit `python_oracle` propagates through nested calls; unmigrated routes remain visible `legacy_python_transitional`; RF-07 cutover was not performed.
- Capability reporting binds the loaded distribution-owned extension and distinguishes actual from configured Rayon threads. Normal root installation requires the compatible native wheel.
- One adversarial review found five RF-00 blockers; one repair-closeout fixed all five. Local focused proof, both focused GitHub jobs, pre-push restore, and fresh remote reconstructed restore pass.
- Paired no-regression gate passes: chart ratio `1.03037` (95% upper `1.04135`) and cold import `1.00913` (upper `1.02041`) against ceiling `1.05`. This is not a speedup claim.
- No physics, formula, tolerance, reference, grid, seed, solver, R5b, Wolfram, dependency, or Cargo.lock change was made.

## EVIDENCE

- Machine index: `artifacts/rust_first_runtime/rf00/EVIDENCE.json`, SHA-256 `7c664203712411a2335058a481b4045060fc0b615fce8a8895d0bb27c77183fe`.
- Raw digest index: `artifacts/rust_first_runtime/rf00/RAW_MANIFEST.sha256`, SHA-256 `6e8c5338b9f8d400af340cfb88a3e8eee417428776afa04d798d1a8418998194`.
- Native r3: `artifact/native-repro-bundle-20260824-r3` at `3aef681d2901e77ce638be5925688929800a822a`; archive SHA-256 `1c45dd93b46dc43c6d8c503d3ff1034d60b36fc7aa73ebf19b40ae48b080cec9`; manifest at `repro/native/BASS-RF00-NATIVE-20260824T194934Z/BUNDLE_MANIFEST.json`.
- r3 reuses exact r2 lock/config/vendor/licenses and unchanged wheelhouse inputs, but not the r2 native wheel or extension receipt.
- R5b PR #21 is reused as closed. Wolfram PR #22 remains reference-only and unpromoted; no Wolfram was run locally.

## BOUNDARIES AND ROLLBACK

- Do not merge or mark ready, promote formula authority, change tolerances/references/dependencies, or rerun inherited PASS without a changed precondition.
- After fetching the verified live RF-00 branch, rollback the delivery with `git revert --no-edit origin/agent/architecture/rust-first-rf00-20260824-r1 4073f5a66910142545167b2987bfe350239fd7c9`; never rewrite or delete immutable r3 evidence.

## EXACTLY ONE NEXT ACTION

Execute `RF-BENCH-00` — “Contention-controlled benchmark runner” — from `docs/rust_first_runtime/SPEC.json`; begin with the runner capability probe and accept only `RUNNER_VALIDATION_ONLY` evidence.
