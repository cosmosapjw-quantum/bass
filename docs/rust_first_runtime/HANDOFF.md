# CODEX HANDOFF — BASS Rust-first runtime closure

Resume from the draft plan PR created by this package. Do not restart recovery,
rerun inherited PASS suites, or execute Wolfram locally.

## Fixed inputs

- Repository: `https://github.com/cosmosapjw-quantum/bass`.
- Plan base: PR #23 head `4c6150578d1e7fea43e0d32c01664c92094c8c05`.
- Plan branch: `agent/architecture/rust-first-runtime-closure-20260824-r1`.
- Required `docs/rust_first_runtime/SPEC.json` SHA-256:
  `dcd4f89fe7a2ad73f22574357df53fcbea437d83f1b4faae08250e2ab46b4efa`.
- R5b: PR #21 `b810092755837ccfa96502aa7e132a50c3fcbd33`; closed contract.
- Wolfram candidate: PR #22 `75f0b128634ec60b853519f9f6d530f113b54a81`;
  reference only, never promote without a fresh Wolfram authority receipt.
- Native r2: `61045b6e5a0d7b026437e0d3586df66706578161`;
  archive SHA-256 `ef0f35b76ab4ef4877ed577afe391ed677a7a6767bcbc64db62dd853d757afca`.
- Read `docs/rust_first_runtime/SPEC.json` as the machine authority.
- Resolve the live open draft PR by the exact plan head branch, fetch its live head,
  and verify the SPEC digest above before creating a child branch.

## Exactly one action

Execute work item `RF-00` (`Typed backend capability policy, unified packaging, and CI skeleton`) only.

1. Create a fresh stacked branch from the plan PR head. Do not mutate PRs #21–#23.
2. Replace ambient `HAVE_RUST` plus broad import-exception fallback with a typed
   per-route capability matrix. Routes already supported natively use fail-closed
   `rust_required`; inventoried unmigrated routes preserve current behavior through
   a visible `legacy_python_transitional` state; `python_oracle` remains explicit.
   Do not perform the global default cutover before RF-07.
3. Preserve all public numerical results, formulae, tolerances, references, grids,
   seeds, solver semantics, and the R5b state/operator/science contract.
4. Add a capability report with extension version, ABI, Cargo.lock digest, build
   profile, CPU dispatch variant, thread-pool size, and enabled optional features.
5. Unify the install/build entry point so a normal installation either installs a
   compatible `bianchi_rustcore` wheel or fails with an actionable error. Do not
   download dependencies during tests and do not upgrade packages opportunistically.
6. Add focused tests for policy selection, missing extension, ABI mismatch, explicit
   oracle selection, no silent fallback, and unchanged supported Rust results.
7. Run only changed-path proof. Reuse unchanged scientific, Wolfram, and native r2
   receipts. Do not run the 1,849/full legacy collection for reassurance.
8. Perform one independent adversarial change review. Fix only blockers in RF-00
   scope, then rerun affected proof once.
9. Commit atomically, push, and open a draft stacked PR. Do not merge or mark ready.

## Native artifact rule

- If RF-00 changes no Cargo/Rust/generated/PyO3/wheel/ABI byte, record
  `REUSED_NATIVE_R2_NO_R3` with a mechanical changed-path predicate.
- If any such byte changes, build from the exact lock and pinned Rust toolchain,
  run focused native proof plus `cargo test --locked --offline` from `_rustcore`,
  build/import the wheel, and push a new immutable cargo bundle artifact branch with
  Cargo.lock, vendor/config, toolchain identity, wheel, receipts, ordered parts, and
  root SHA-256. Never claim r2 covers changed native bytes.

## Performance boundary

RF-00 is an architecture boundary, not a speedup claim. Require no statistically
supported regression in affected startup/call-overhead checks; do not apply Candidate
B's 10% materiality gate. Do not run Candidate B unless resuming PR #23 itself.

## Stop conditions

Stop with a precise blocker if the base/head changed, authority hashes differ, the
workspace is dirty in an overlapping path, exact native inputs are unavailable, or
scientific behavior would need to change. Never change tolerance/reference/physics,
merge, promote formula authority, use fast-math/reduced precision, or hide a fallback.

## Required output

Return: branch/head/tree, changed files, focused proof, reused receipts and predicates,
native-bundle decision, draft PR URL, rollback command, and the next single work item
from `SPEC.json`. Human closeout must reference machine evidence instead of copying it.
