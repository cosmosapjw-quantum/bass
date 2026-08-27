# RF-02C Post-Closeout Reconciliation Implementation Plan

> Execute BASS-11 only. BASS-12–15 remain outside this run.

## Starting identity

```text
branch: agent/architecture/rust-first-rf02c-20260826-r1
HEAD:   c777ebb68c82aa8b9898f92159c2346a6e8ef892
tree:   524a541261c0384eedd79267671215dccd9c7147
PR:     #36, open/draft
```

The branch must be clean before repair. `a94dbe08...` must remain an ancestor.

## Task 1 — Reproduce only the known failures

Source Rust 1.94.1:

```bash
source /mnt/data/rust_1_94_1_env.sh
```

Run only:

```bash
pytest -q tests/test_backend_policy.py \
  tests/test_rf00_policy_adversarial.py \
  tests/test_rf00_route_inventory.py

cd _rustcore
cargo fmt --all -- --check
cargo clippy --workspace --all-targets --locked --offline -- -D warnings
```

Read the existing run logs before modifying code. Do not run the full suite.

## Task 2 — Commit 1: source/CI and integrated native identity

Allowed paths are exactly:

```text
.github/workflows/rf02c-preflight.yml
bianchi/backend_policy.py
tests/test_backend_policy.py
tests/test_rf00_policy_adversarial.py
tests/test_rf00_route_inventory.py
_rustcore/src/python/mod.rs
_rustcore/src/ode/background/events.rs
_rustcore/src/ode/background/exact.rs
_rustcore/src/ode/background/history.rs
_rustcore/src/ode/background/type_ix_dae.rs
_rustcore/src/ode/background/trajectory.rs
_rustcore/src/ode/charts.rs
_rustcore/src/lib.rs
```

Required repairs:

1. RF-02C preflight recognizes the old RF-02B wheel as
   `IncompatibleNativeExtensionError` because it lacks
   `rf02c_execution_identity`; the development override must not bypass this.
2. The scope detector executes independently and always exports an exit code.
3. Synthetic RF-00 fixtures expose the canonical RF-02C execution identity.
4. The q.group route inventory recognizes the literal route IDs delegated
   through `_native_geometry_route`.
5. Rust format/clippy findings are fixed without changing physics or public
   typed semantics.
6. Build the integrated wheel and update `RF02C_V2_NATIVE_PAYLOAD` to its exact
   wheel/installed-file identities. Rebuild once to verify deterministic
   normalized content.

Commit:

```text
fix(rf02c): reconcile post-closeout CI and native identity
```

No evidence/native-delta path belongs in Commit 1.

## Task 3 — Verify Commit 1

```bash
pytest -q tests/test_backend_policy.py \
  tests/test_rf00_policy_adversarial.py \
  tests/test_rf00_route_inventory.py

cd _rustcore
cargo fmt --all -- --check
cargo clippy --workspace --all-targets --locked --offline -- -D warnings
cargo test --lib --locked --offline rf02b_
cargo test --release --locked --offline rf02c_
```

Then run the exact PR #35 focused generic-vector commands from its committed
evidence, the affected RF-02C Python selectors, and a fresh no-index/no-override
production trajectory and deterministic batch.

## Task 4 — Commit 2: evidence rebind

Regenerate only:

```text
artifacts/rust_first_runtime/rf02c/EVIDENCE.json
artifacts/rust_first_runtime/rf02c/changed_paths.json
artifacts/rust_first_runtime/rf02c/native_delta/**
```

The delta and receipts must bind the exact Commit-1 SHA, tree, wheel, shared
object, installed files, content manifest, restore result, and changed paths.

Commit:

```text
chore(rf02c): rebind terminal evidence after CI closure
```

Its parent must be exactly Commit 1. No source, test, workflow, Cargo, formula,
or policy path may appear.

## Task 5 — Push and remote closure

Ordinary fast-forward push only. Keep PR #36 draft and unmerged. Wait for and
read back the RF-02C, RF-00, and RF-02B workflows. Reuse RF-BENCH success; do
not rerun it.

BASS-11 is PASS only when:

- all three previously failing workflows are GREEN at the terminal head;
- the terminal native artifact/delta binds the exact source commit;
- PR #36 base/head/draft state and 45-path science/runtime closure remain
  correct;
- no formula, tolerance, performance, or authority claim changed.
