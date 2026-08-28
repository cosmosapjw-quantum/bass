# Codex Handoff — RF-04 restored control

```text
PASS_RF03
PASS_SCI_AUTH_04_VALIDATOR
NO_PASS_RF04
exact next action: RF04-RED-01
```

Use an authenticated clone. Preserve every untracked file and worktree. Never clean/reset/stash/amend/rebase/force-push.

## Exact intake

```bash
set -euo pipefail
REPO="$(git rev-parse --show-toplevel)"
cd "$REPO"
git fetch origin
CONTROL="origin/agent/plans/rf04-sci-auth-intake-20260828-r1"
test "$(git rev-parse "$CONTROL")" = "f18e491f19f45accc8c87eb56b4a24f15a8a3d6c"
test "$(git rev-parse f18e491f19f45accc8c87eb56b4a24f15a8a3d6c^{tree})" = "3fd8201a3cb15bf8d882dd28d37bf0c31e8af7e0"
test "$(git rev-parse 4a0e97cbc26a80e1fecbe18799a07207cfd8e556^{tree})" = "3fd8201a3cb15bf8d882dd28d37bf0c31e8af7e0"
git merge-base --is-ancestor "695908d8501be141b163641cbe61e334d2189358" "f18e491f19f45accc8c87eb56b4a24f15a8a3d6c"
test "$(git rev-parse f18e491f19f45accc8c87eb56b4a24f15a8a3d6c:docs/rust_first_runtime/RF04_CURRENT_PACKAGE.json)" = "aff7c4270dd9481020836a1d1ad7420dd4f47fb7"
test "$(git rev-parse f18e491f19f45accc8c87eb56b4a24f15a8a3d6c:docs/rust_first_runtime/RF04_PUBLIC_ROUTE_SCHEMA_V1.json)" = "a5a503f96c8d85af265be67ac04fd3ff983d9b33"
```

Reuse only these retained checkpoints; do not rerun them:

```text
/tmp/bass-rf04-intake-20260828.cDFXIM/RF04_INTAKE_00_BLOCKER.json
SHA-256 e8793fe2fdf83e5ab2430e36714f3d445efff4790f5f17fc8188a90ee14929d8

/tmp/bass-sci-auth-04-20260828.0312rE/worktree/artifacts/authority/sci_auth_04/VALIDATION.json
SHA-256 d0d72dfaeb1bdef29353e05809619b2393176eca52f770a1d193115dad15033c
```

Create or safely resume `agent/architecture/rust-first-rf04-20260828-r1` from exact `6e53664d56694f7a7ad5f65be262302d5c8866b2` / tree `bb743717e8115821d72268d8384dc5cc7cc11975`. Start with genuine registration/schema and scientific-contract RED tests. Follow the frozen pointer and route schema, implement only RF-04 gaps, run targeted proof, four diagnostic readbacks and hostile mutations, PHYS-MATH then PHYS-MATH-CODE once, at most one reproduced P0/P1 repair, native delta/restore if invalidated, ordinary push, one stacked draft PR, exact remote readback, stop.

Candidate B and BASS-13–15 are closed; do not import or rerun them. No timing, GPU, Wolfram, full-suite reassurance, RF-05+, merge, ready, or scientific/performance promotion.
