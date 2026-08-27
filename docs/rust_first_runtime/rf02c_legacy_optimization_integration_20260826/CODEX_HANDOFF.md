# Codex Handoff — BASS-11 Post-Closeout Reconciliation

```text
PROCESS_DRIFT_DETECTED
STOPPING META-WORK
RETURNING TO USER OBJECTIVE
```

## Execute one node only

Execute BASS-11 only. Do not execute BASS-12–15, RF-03+, timing, GPU, Wolfram,
the full suite, merge, or ready transition.

## Required live identity

```text
repository: cosmosapjw-quantum/bass
branch: agent/architecture/rust-first-rf02c-20260826-r1
required HEAD: c777ebb68c82aa8b9898f92159c2346a6e8ef892
required tree: 524a541261c0384eedd79267671215dccd9c7147
required PR: #36, open/draft
required ancestor: a94dbe08a7a79a199f26eb33efab1155d2674d64
```

The branch moved after the original evidence commit because PR #35 merged
default-off generic-vector native bytes. Do not reset to `a94dbe08...` and do
not rewrite that ancestry.

Require a clean worktree, then source Rust:

```bash
git fetch origin
test "$(git branch --show-current)" = \
  agent/architecture/rust-first-rf02c-20260826-r1
git merge --ff-only origin/agent/architecture/rust-first-rf02c-20260826-r1
test "$(git rev-parse HEAD)" = \
  c777ebb68c82aa8b9898f92159c2346a6e8ef892
test "$(git rev-parse HEAD^{tree})" = \
  524a541261c0384eedd79267671215dccd9c7147
test -z "$(git status --porcelain)"
git merge-base --is-ancestor \
  a94dbe08a7a79a199f26eb33efab1155d2674d64 HEAD
source /mnt/data/rust_1_94_1_env.sh
```

## Why two commits are mandatory

One new commit is not authorized as a substitute. Commit 1 changes
source/workflow/test/native bytes. A content-addressed delta can bind that
source only after Commit 1 has an immutable SHA. Commit 2 performs the
deterministic evidence rebind. Do not amend, squash, rebase, or force-push.

## Commit 1 — exact scope

Message:

```text
fix(rf02c): reconcile post-closeout CI and native identity
```

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

No path outside this list is authorized.

### Required behavior

RF-02C preflight:
- restore/hash the historical RF-02B wheel only as a compatibility negative;
- expect `IncompatibleNativeExtensionError` caused by missing
  `rf02c_execution_identity`;
- prove `BASS_ALLOW_UNVERIFIED_NATIVE_DEV=1` does not bypass the missing
  mandatory capability identity;
- execute the scope detector with `if: always()` or an equivalent independent
  step and always publish its exit code;
- do not treat the historical wheel as the terminal RF-02C payload.

RF-00 Python:
- update synthetic background-route fixtures to expose the canonical identity
  returned by `bianchi.q.geometry_identity.geometry_route_identity()`;
- update only the detector/test seam needed to recognize literal q.group route
  IDs delegated through `_native_geometry_route`;
- do not relax production `rf02c_execution_identity`, payload, or route checks.

Rust:
- apply `cargo fmt`;
- make semantics-neutral Clippy rewrites;
- use precise local lint expectations for deliberately retained closed-AST,
  typed-error, or test-contract items rather than deleting/renaming them;
- do not alter equations, coefficients, tolerances, state order, root
  selection, transition/restart/history bytes, or public typed error strings.

Native identity:
- build the current integrated wheel;
- update `RF02C_V2_NATIVE_PAYLOAD` in `bianchi/backend_policy.py` to the exact
  wheel/SBOM/SO/installed-file identities;
- perform a second locked/offline build and require identical normalized
  content and installed-file identities.

## Focused verification

Run the failing surface first, then the directly affected integration proof:

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

Run the exact PR #35 focused generic-vector commands from its committed
evidence. Run the existing RF-02C primary/hostile selectors only where their
controlling bytes changed. Perform one fresh no-index/no-override install and
exercise one production trajectory and one deterministic batch.

Do not run the full suite or RF-BENCH.

Commit only after these checks are GREEN and the diff is confined to the exact
Commit-1 allowlist.

## Commit 2 — exact evidence rebind

Message:

```text
chore(rf02c): rebind terminal evidence after CI closure
```

Allowed paths:

```text
artifacts/rust_first_runtime/rf02c/EVIDENCE.json
artifacts/rust_first_runtime/rf02c/changed_paths.json
artifacts/rust_first_runtime/rf02c/native_delta/**
```

The parent must be exactly Commit 1. Regenerate the native delta and evidence
so they bind Commit 1's SHA/tree and the integrated wheel/SO/content/restore
identities. No source, test, workflow, Cargo, formula, or performance byte may
change.

## Delivery

Ordinary fast-forward push to the same RF-02C branch. Do not open another PR;
update/read PR #36. Wait for and inspect the terminal RF-02C, RF-00, and RF-02B
runs. RF-BENCH success is reused and must not be rerun for reassurance.

BASS-11 may emit `PASS_RF02C_REMOTE_CLOSEOUT` only after all three previously
failing workflows are GREEN at the terminal head and terminal evidence binds
the exact source/native identities.

## Final report

Use exactly:

```text
STATUS
ACTUAL PROGRESS
VERIFIED
DEFERRED
BLOCKERS
NEXT
```

On success, NEXT contains exactly one action: update Jira BASS-11 with terminal
head/tree, PR #36, workflow, artifact, wheel, SO, delta, and restore identities;
then wait for BASS-12 before opening BASS-13.
