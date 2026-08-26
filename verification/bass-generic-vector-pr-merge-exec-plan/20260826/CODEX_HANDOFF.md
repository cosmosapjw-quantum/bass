# Codex handoff — BASS generic-vector PR, merge, and post-merge execution

## Current launch

Execute **WU-001 only** in a fresh Codex context.

Repository:

```text
~/bass
```

Plan branch:

```text
agent/audit/bass-generic-vector-pr-merge-exec-plan-20260826
```

Plan root:

```text
verification/bass-generic-vector-pr-merge-exec-plan/20260826
```

Frozen PR base:

```text
agent/architecture/rust-first-rf02c-20260826-r1
445e50184823e58401a8212ceaaf736e72bb35f2
```

Frozen implementation candidate:

```text
agent/integration/bass-generic-vector-host-parity-20260826
a979af6b022eb832215a2342a01fe6b85374b914
```

Scientific oracle:

```text
58d649d438415def3e646d8eee8d0e1f3159ed7f
```

## 1. Fetch and verify the plan

```bash
set -euo pipefail
cd ~/bass

git fetch origin \
  agent/audit/bass-generic-vector-pr-merge-exec-plan-20260826 \
  agent/architecture/rust-first-rf02c-20260826-r1 \
  agent/integration/bass-generic-vector-host-parity-20260826

PLAN_WT=../bass-generic-vector-pr-merge-plan-20260826
REVIEW_WT=../bass-generic-vector-pr-review-20260826

test ! -e "$PLAN_WT"
test ! -e "$REVIEW_WT"

git worktree add --detach "$PLAN_WT" \
  "origin/agent/audit/bass-generic-vector-pr-merge-exec-plan-20260826"

PLAN_ROOT="$PLAN_WT/verification/bass-generic-vector-pr-merge-exec-plan/20260826"
cd "$PLAN_ROOT"
PYTHONDONTWRITEBYTECODE=1 python3 VERIFY_PACKAGE.py .
```

Require:

```text
PASS_BASS_GENERIC_VECTOR_PR_MERGE_PACKAGE
```

Read:

```text
AUTHORITY_AND_SCOPE.json
P0_P1_THREAT_CATALOGUE.jsonl
INVARIANT_TEST_MATRIX.jsonl
WORK_UNITS/WU-001-FRESH-DIFFERENTIAL-PR.json
FRESH_CONTEXT_REVIEW_CONTRACT.json
FINAL_DIFFERENTIAL_AUDIT_CONTRACT.json
```

The plan branch Git tree is the byte identity for the GitHub text package. Do
not compare JSON formatting or key order against a separately transported ZIP.
Use semantic verification for the parsed package, and use byte identity only
for the frozen repository inputs and oracle objects that explicitly require it.

## 2. Freeze remote identities

```bash
test "$(git ls-remote origin refs/heads/agent/architecture/rust-first-rf02c-20260826-r1 | cut -f1)" = \
  "445e50184823e58401a8212ceaaf736e72bb35f2"

test "$(git ls-remote origin refs/heads/agent/integration/bass-generic-vector-host-parity-20260826 | cut -f1)" = \
  "a979af6b022eb832215a2342a01fe6b85374b914"

git merge-base --is-ancestor \
  445e50184823e58401a8212ceaaf736e72bb35f2 \
  a979af6b022eb832215a2342a01fe6b85374b914

test "$(git rev-list --count \
  445e50184823e58401a8212ceaaf736e72bb35f2..a979af6b022eb832215a2342a01fe6b85374b914)" = "1"
```

If either ref moved, stop with:

```text
BLOCKED_BY_REF_MOVEMENT
```

Do not rebase, retarget, or update the package.

## 3. Create a fresh read-only review worktree

```bash
git worktree add --detach "$REVIEW_WT" \
  a979af6b022eb832215a2342a01fe6b85374b914
cd "$REVIEW_WT"

test -z "$(git status --porcelain)"
git diff --check \
  445e50184823e58401a8212ceaaf736e72bb35f2..a979af6b022eb832215a2342a01fe6b85374b914

git diff --name-only \
  445e50184823e58401a8212ceaaf736e72bb35f2..a979af6b022eb832215a2342a01fe6b85374b914 \
  > /tmp/bass-generic-vector.paths

cat > /tmp/bass-generic-vector.expected-paths <<'EOF'
_rustcore/src/kinetic/generic_vector.rs
_rustcore/src/kinetic/mod.rs
_rustcore/src/lib.rs
_rustcore/src/python/generic_vector.rs
_rustcore/src/python/mod.rs
artifacts/rust_first_runtime/bass3/EXECUTION_EVIDENCE.json
artifacts/rust_first_runtime/bass3/GREEN.log
artifacts/rust_first_runtime/bass3/RED.log
artifacts/rust_first_runtime/bass3/RED_ENVIRONMENT_ATTEMPT.log
tests/oracles/bass3_generic_vector_oracle.py
tests/test_bass3_generic_vector_host_parity.py
tools/audit/run_bass3_generic_vector_host_parity.py
EOF

diff -u \
  /tmp/bass-generic-vector.expected-paths \
  /tmp/bass-generic-vector.paths
```

The first review pass is read-only. Use the finding schema in
`FRESH_CONTEXT_REVIEW_CONTRACT.json`. Do not edit any file.

## 4. Build only the affected native path

```bash
if [[ -f /mnt/data/rust_1_94_1_env.sh ]]; then
  source /mnt/data/rust_1_94_1_env.sh
fi

rustc --version
cargo --version

python3 -m venv .venv-pr-review
source .venv-pr-review/bin/activate
python -m pip install --upgrade pip
python -m pip install maturin numpy pytest

(
  cd _rustcore
  cargo test --release generic_vector -- --nocapture
  maturin develop --release
)
```

Do not install or activate JAX/JAXlib/Equinox/Diffrax.

## 5. Run the bounded verification set

```bash
python -m pytest -q \
  tests/test_bass3_generic_vector_host_parity.py \
  -k 'not mutation'

python -m pytest -q \
  tests/test_bass3_generic_vector_host_parity.py \
  -k 'mutation'
```

Required:

```text
7 targeted parity PASS
6/6 hostile mutations PASS
2 native generic_vector tests PASS
```

Do not run the full repository suite, historical 53+14 replay,
500/80/120 audit, SymPy, Wolfram, xAct, figures, performance benchmarks,
classifier, fitting, or Jira/Confluence work.

## 6. Review verdict

If any reproducible P0 or P1 exists, emit findings and stop:

```text
BLOCKED_BY_P0
```

or

```text
BLOCKED_BY_P1
```

P2/P3 findings are nonblocking unless they violate a current invariant.

If P0=0 and P1=0, emit:

```text
PASS_WITH_NO_P0_P1
```

## 7. Create the PR

Confirm no open PR already exists for the frozen head. Then create exactly:

```text
title
BASS-3: integrate default-off generic-vector native host parity

base
agent/architecture/rust-first-rf02c-20260826-r1

head
agent/integration/bass-generic-vector-host-parity-20260826

draft
false
```

Recommended body:

```markdown
## Scope

Integrates the bounded, explicit opt-in native generic-vector
collision/projector/Kato host parity path.

## Frozen identities

- base: `445e50184823e58401a8212ceaaf736e72bb35f2`
- head: `a979af6b022eb832215a2342a01fe6b85374b914`
- scientific oracle: `58d649d438415def3e646d8eee8d0e1f3159ed7f`
- changed paths: 12
- implementation commits: 1

## Verified

- targeted parity: 7 passed
- hostile mutations: 6/6 detected
- native generic-vector unit tests: 2 passed
- default-off and public-export firewall: passed
- exact vacuum: collision off, no projector selected
- fresh differential review: P0=0, P1=0

## Claim boundaries

This does not authorize default-on runtime, VI0 classifier, fitting,
inference, continuum finite-tilt authority, or a publication-grade solver.

## Merge method

Merge commit. Do not squash or rebase.
```

Use `gh pr create` or the GitHub connector. Do not merge.

Stop with:

```text
PR_CREATED_READY_FOR_USER_MERGE_APPROVAL
<PR number>
<PR URL>
```

## Later work units

After explicit user merge approval, execute `WU-002`. After merge, execute
`WU-003`.

Do not perform WU-002 or WU-003 in the current context.
