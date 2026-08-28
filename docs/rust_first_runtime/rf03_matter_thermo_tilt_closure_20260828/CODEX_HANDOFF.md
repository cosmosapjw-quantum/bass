# Codex Handoff — Execute RF-03 from the Latest RF-02C Development Head

```text
PROCESS_DRIFT_DETECTED
STOPPING META-WORK
RETURNING TO USER OBJECTIVE
```

## Task

Execute RF-03 only: native collisionless matter, thermodynamics and tilt
closure from the latest frozen RF-02C development head.

This is independent of the legacy/backup optimization lane. Do not wait for,
read from, cherry-pick, merge or benchmark BASS-12/BASS-13/BASS-14/BASS-15.

## Package authority

```text
repository: cosmosapjw-quantum/bass
package branch: agent/plans/rf03-matter-thermo-tilt-closure-20260828-r1
package path: docs/rust_first_runtime/rf03_matter_thermo_tilt_closure_20260828
package id: BASS-RF03-MATTER-THERMO-TILT-CLOSURE-20260828-R1
```

Read and validate the package without using the package branch as the
implementation parent:

```bash
git fetch origin

PKG_REF="origin/agent/plans/rf03-matter-thermo-tilt-closure-20260828-r1"
PKG_PATH="docs/rust_first_runtime/rf03_matter_thermo_tilt_closure_20260828"
PKG_TMP="$(mktemp -d)"

for f in README.md CURRENT_STATE.json SOURCE_INVENTORY.json WORK_UNITS.json \
         ACCEPTANCE_MATRIX.json IMPLEMENTATION_PLAN.md CODEX_HANDOFF.md \
         validate_package.py MANIFEST.sha256
do
  git show "$PKG_REF:$PKG_PATH/$f" > "$PKG_TMP/$f"
done

(
  cd "$PKG_TMP"
  sha256sum -c MANIFEST.sha256
  python validate_package.py
  python validate_package.py --live
)
```

## Exact implementation base

```text
base branch: agent/architecture/rust-first-rf02c-20260826-r1
base head:   dfa17457d402bd441d3fdf786c2d79c529512ee5
base tree:   9fc67fb0ba10e091e25a14d7e1fac88b77a0241e
base PR:     #36 OPEN / DRAFT
new branch:  agent/architecture/rust-first-rf03-20260828-r1
```

Create a separate worktree or clone. Never switch branches inside a worktree
used by the backup optimization lane.

```bash
git fetch origin
test "$(git rev-parse origin/agent/architecture/rust-first-rf02c-20260826-r1)" = "dfa17457d402bd441d3fdf786c2d79c529512ee5"
test "$(git rev-parse dfa17457d402bd441d3fdf786c2d79c529512ee5^{tree})" = "9fc67fb0ba10e091e25a14d7e1fac88b77a0241e"

git worktree add \
  ../bass-rf03-20260828 \
  -b agent/architecture/rust-first-rf03-20260828-r1 \
  dfa17457d402bd441d3fdf786c2d79c529512ee5

cd ../bass-rf03-20260828
test -z "$(git status --porcelain)"
```

If the implementation branch already exists, continue only if it descends from
the exact base and its worktree is clean or contains clearly identified
in-progress RF-03 changes. Do not reset, clean, stash, amend, rebase, squash or
force-push.

## Read once

1. `docs/audits/science_system_differential_20260826/WORK_UNITS.json`
   — RF-03 only.
2. RF-02C terminal `artifacts/rust_first_runtime/rf02c/EVIDENCE.json`.
3. package `SOURCE_INVENTORY.json`.
4. `bianchi/matter/tilted_rust.py`.
5. the current matter/tilt/thermo Python owners actually reached by public
   routes.
6. `_rustcore/src/thermo/**`.
7. current `th_integrate`, `th_rhs`, and `th_force_and_matrix` implementation
   and registration.
8. `bianchi/backend_policy.py` route entries for tilted/matter/thermo.

README or comments are context, not implementation evidence. Trace the actual
call path.

## Exact scope

Use the compiled RF-03 paths plus only this narrow integration extension:

```text
_rustcore/src/lib.rs                         # registration/import wiring only
_rustcore/src/python/mod.rs                  # module declarations only
_rustcore/src/python/register.rs             # RF-03 registration only
_rustcore/src/python/rf03_matter.rs           # new thin adapter
_rustcore/src/python/rf03_thermo.rs           # new thin adapter
_rustcore/src/python/rf03_tilt.rs             # new thin adapter
bianchi/backend_policy.py                    # exact RF-03 route policy only
```

No other path extension is authorized. Do not edit Cargo manifests/lockfiles
without a reproduced compile blocker and separate explicit authorization.

## Execute, do not produce another planning layer

### 1. Source/schema reality and immediate RED

Write one bounded
`artifacts/rust_first_runtime/rf03/SCHEMA_AND_ROUTE_FREEZE.json` containing the
actual:

- matter state order, types, units and public shapes;
- supported current model/EOS and the seven closure modes;
- hatted/unhatted and tilt normalization conventions;
- thermo interpolation/derivative conventions;
- exact public production/oracle/transitional route inventory;
- equation-to-code owners and blob identities.

Then, in the same run, write and execute genuine failing tests. Do not stop
after the freeze document.

Required RED classes:

```text
native-only path absent or shortcut-reachable
force/JVP/C-path parity unproved
negative/nonfinite/superluminal domain not typed
unsupported EOS/model not rejected before coercion
constant-w reference not isolated from production default
RF-02C + matter trajectory contract not yet green
thread determinism not yet proven
```

### 2. Rust-owned implementation

Implement source-derived modules under:

```text
_rustcore/src/matter/**
_rustcore/src/thermo/**
_rustcore/src/tilt/**
```

Preserve equations, signs, normalization, units, state order and approved model
support.

Move RF-03 numerical bodies out of `_rustcore/src/lib.rs`; leave only wiring.

Use analytic JVPs for the approved force path. No finite-difference JVP as
authority.

### 3. Modular adapters and public route

Add thin PyO3 adapters and thin Python typed models. Preserve current public
call shapes where they are part of the contract.

Production defaults must not silently select Python or constant-w. Any retained
reference must be explicit test/oracle behavior with a typed route state.

### 4. Coupled execution

Compose one complete RF-02C trajectory with native matter ownership. No Python
inner-step callback. Require typed termination on physical-domain boundaries
and byte-identical 1-thread/N-thread results.

### 5. Targeted verification

Run only:

```bash
source /mnt/data/rust_1_94_1_env.sh

cd _rustcore
cargo test --release rf03_

cd ..
pytest -q tests/rf03
pytest -q tests/rf03 -k \
  'invalid or hostile or fallback or superluminal or domain'
```

Run directly invalidated RF-02C interface tests, not the full suite.

### 6. Plot evidence and hostile mutations

Generate and directly inspect:

```text
native_oracle_force_jvp_residual
log_density_vs_log_mean_scale
tilt_normalization_and_domain_margin
entropy_temperature_invariant
```

Test at least:

```text
expansion sign mutation
Gamma/normalization omission
superluminal input
silent constant-w fallback attempt
```

Store machine results and `PLOT_AUDIT.json`. Reject or narrow claims when the
figures demand it.

### 7. One bounded dual audit

Perform exactly:

```text
PHYS-MATH
→ PHYS-MATH-CODE
→ repair reproduced P0/P1 only
→ at most one differential repair review
```

Do not start an audit-of-audit loop.

### 8. Native evidence and draft PR

Build the locked native wheel, produce a content-addressed RF-03 delta and
fresh no-index restore proof, then bind terminal evidence.

Allowed role-based commits:

```text
feat(rf03): add native matter thermo and tilt closure
fix(rf03): close bounded matter-tilt review findings       # optional
chore(rf03): bind terminal evidence and native delta       # generated evidence
```

Ordinary fast-forward push only.

Open one draft PR:

```text
head: agent/architecture/rust-first-rf03-20260828-r1
base: agent/architecture/rust-first-rf02c-20260826-r1
```

Do not merge or mark ready.

## Claim boundary

Before every acceptance condition and remote readback:

```text
NO PASS_RF03 CLAIM
```

After complete targeted and remote GREEN only:

```text
PASS_RF03
scientific scope: scoped collisionless matter/thermo/tilt closure
performance claim: NONE
authority promotion: NONE
```

## Stop policy

`BLOCK_NOW` only for a concrete defect that:

- changes an approved equation/sign/normalization/state order;
- makes the EOS/model authority unresolved;
- requires a path outside the exact scope;
- corrupts physical-domain or public-route behavior;
- prevents native reproducibility;
- leaves a reproduced P0/P1 unresolved;
- causes destructive or non-fast-forward mutation.

Do not stop for style, future hardening, publication-grade concerns,
performance ideas, or the separate backup optimization.

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

`NEXT` must contain exactly one action. On success it is remote readback of the
single RF-03 draft PR and its terminal evidence; on a genuine blocker it is the
smallest implementation- or scope-level repair, not another contract.
