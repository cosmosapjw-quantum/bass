# RF-04 external-review continuation: native scalar raw slice

## Goal and starting state

Implement and prove the existing fixed-node scalar Kato-AEM2 raw route through
its real native boundary. This is an intermediate RF04-GREEN-02 work unit,
not a replacement of the full polarized RF-04 goal.

Exact source baseline: `d43e4e9039f8cd9303340ed216e76a650138adef` /
`27f37630c42c5c39e705a84202d687363260d908`.
Preserve the external-review worktree
`/tmp/bass-rf04-external-revision-20260829.pg4QTD/worktree`, its logs, the old
4508 RED checkpoint, and the original ZIPs. Do not run the withdrawn A2 prompt.

Use the delivery's exact publication commit/tree from START_HERE.md. Make a
new isolated implementation worktree from that commit, so the pushed tests,
wrapper and review fixes are already present. Do not reset/clean/stash/rebase
or amend a retained worktree. Do not require the old temporary worktree to
exist when the exact pushed source and package objects are available.

Read CONTRACT.json and REVIEW_RECONCILIATION.md. Run:

```bash
python3 docs/rust_first_runtime/rf04_external_review_resume_20260829/validate_handoff.py --repo .
python3 -m pytest -q tests/rf04/test_dense_oracle.py tests/rf04/test_thin_dispatch.py tests/rf04/test_handoff_payload.py
```

Do not replay RF03, SCI-AUTH-04, old intake or old RED. Retained tests that
actually depend on changed owners may be rerun as targeted regression, with
that purpose recorded. Do not count missing imports as killed physics mutants.

## 1. Preserve the existing authority and integrate the correct donor

The authoritative modular sources are under `generated/rust/typeii/` and
`runtime/rust/typeii/`, pinned in CONTRACT.json. The full repository, not a
pair of copied donor files, supplies their dependency closure. Read the existing
generated-module integration and preserve it; link unchanged donor files or
use a behavior-equivalent modular bridge under `_rustcore/src/kinetic/`.
Do not edit generated formulas or import SCI-AUTH-04 source files. Consume its
retained checkpoint identity only.

Create `_rustcore/src/kinetic/rf04_typeii.rs`, declare it in kinetic/mod.rs, and
implement the small public owner. Existing `rf04_contract_tests.rs` imports
Carrier, QuadratureRoute, parse_carrier, parse_quadrature_route and
rf04_deterministic_batch_probe. Parsing a known A1 enum is not evidence that
the execution capability is implemented: the executor must reject unsupported
combinations. The deterministic probe must execute real scalar batch work,
not return a hardcoded vector.

Use `typeii_krylov_adapt::kato_aem2_step_adaptive` with the exact source-backed
options in CONTRACT.json (12/8/20 basis sizes, tol=1e-11, budgets=4096; clip
basis sizes to the actual state dimension). Preserve the donor's augmented
phi1 policy. A full-basis reference action may be used for a test cross-check,
not to fabricate an adaptive certificate. The declared numerical options come
from the pinned pre-Liouville safety test; they are not performance tuning.

For each step call the donor using supplied q1/mid/q3 rows, gamma, opacity_mid,
opacity_scale and positive h. Keep K_q1 half, central A_mid-K_mid and K_q3 half
in exactly that order. Do not call legacy qe_evolve/qe_ensemble. Do not add
angular remapping to this scalar reference slice.

Store input row 0 exactly and each accepted full-step row. No clipping of
negative/nonfinite radiation into the physical domain. State validation and
operator-vector validation are different: signed Krylov vectors are allowed.
Validate common grid/plan data before the member loop. A malformed member is
isolated in batch (ALL_NAN final row, nonzero status, completed count, typed
error); malformed shared plan aborts the call. Trajectory failure raises the
frozen typed exception and step index, not a partial success object.

## 2. Wire the native boundary without fake capabilities

Implement `_rustcore/src/python/rf04_typeii.rs` as validation/marshalling only.
It makes one bounded-count call into the Rust owner, never a Python step loop.
Add only the RF04 module declaration and registration to:

```text
_rustcore/src/python/mod.rs
_rustcore/src/python/register.rs
_rustcore/src/lib.rs
bianchi/backend_policy.py
```

Register the three frozen symbol names and five frozen exception classes from
A1. The Python wrapper is already supplied. Keep native_required and
python_oracle_supported=False in production. Independent test-only Python
code does not require enabling production fallback.

The native identity must include the old A1 schema/SCI-AUTH pins AND the new
execution_profile_id/profile_sha256/diagnostic_semantics. Only advertise the
raw scalar capability pair in this intermediate build. Unsupported polarized,
paired-grid and AP combinations raise RF04CapabilityError with
RF04_UNSUPPORTED_CAPABILITY. Do not weaken the original complete-capability
assertions to make this partial build look like full RF04.

Native-payload identity is an external build/install receipt bound to the
source owner identity, not a demand to embed the final wheel's own hash inside
itself. Publish the new content-addressed delta according to the existing RF03
mechanism. Do not change old expected payload hashes to bless a new wheel.

## 3. Diagnostics must describe what was computed

Use the exact definitions and units in CONTRACT.json. Recompute the state and
operator diagnostics independently with scalar_diagnostics in the dense oracle.
On the raw fixed grid, a nonzero right-null defect is allowed and must be
reported, not replaced by zero or secretly corrected to AP.

The full-step midpoint-left-covector drift includes the physical bolometric
transport contribution; it is not asserted to vanish. The right/equilibrium
null arrays are compatibility aliases of one quantity, not two independent
proofs. The residual array is the actual aggregated
AdaptiveKrylovStats.max_accepted_error_ratio, explicitly a dimensionless target
ratio, NOT a global forward-error bound. Preserve the real action ledger and
nonnormal target semantics. Never substitute a constant diagnostic.

## 4. Build and run only the new bounded proof

Use the retained Rust 1.94.1/offline cargo environment and the repository's
existing Python build environment. Check their actual identities first; do
not install a different toolchain or update Cargo.lock. In the isolated
worktree, use a separate output/target directory and record commands:

```bash
OUT="$(mktemp -d -p /tmp bass-rf04-scalar-proof.XXXXXX)"
export CARGO_TARGET_DIR="$OUT/target"
export PYO3_PYTHON="$(python3 -c 'import sys; print(sys.executable)')"
set -o pipefail
cargo test --manifest-path _rustcore/Cargo.toml --offline --locked rf04_scalar_raw -- --nocapture 2>&1 | tee "$OUT/rust.log"
python3 -m maturin build --manifest-path _rustcore/Cargo.toml --release --offline --locked --features extension-module --out "$OUT/wheels" 2>&1 | tee "$OUT/build.log"
```

Add real Rust tests named with the rf04_scalar_raw prefix; zero selected tests
is not a pass. Install the resulting single expected wheel into an isolated
proof environment with --no-index --no-deps; preserve the canonical installed
native extension. Do not use a wheel chosen by an ambiguous glob. Bind the new
payload receipt, then run with development override removed:

```bash
env -u BASS_ALLOW_UNVERIFIED_NATIVE_DEV python3 -m pytest -q tests/rf04/test_public_dense_differential.py
```

All six new public tests must execute real native calls and compare arrays to
the independent oracle. No skip/xfail or monkeypatched native module is allowed
for this proof. Then run the original frozen-symbol, thin-wrapper and raw-route
applicable selectors. Report the remaining full-capability failures separately
as NOT_IMPLEMENTED, not as a passing full suite.

Check serial/parallel batch identity using the same ordered valid inputs and
separate processes/thread pools (one and four threads). No timing measurement.

## 5. Prove detection on actual compiled native mutants

In disposable copies, make one compiled mutation at a time, while leaving the
independent oracle unchanged. At minimum reverse the central K subtraction,
remove/misapply the direction-dependent collision rate, and collapse q1/mid/q3.
Use a nonzero-opacity/nonzero-tilt case for the rate mutation. The same state-
array differential test must reach the native function and fail its numerical
assertion. Import/link failures, digest rejection, hardcoded wrong output, or
fake diagnostics do not count as killed numerical mutants.

Run a pristine control build under the same mutation harness. Do not relax
production backend identity checking to run mutants: load disposable extension
builds directly in dedicated test subprocesses and separately prove normal
production route identity on the pristine build. Keep native-call receipt,
mutant source diff, test selector, build identity and assertion failure.

The supplied check_oracle_mutations.py is only an offline oracle self-test:

```bash
python3 docs/rust_first_runtime/rf04_external_review_resume_20260829/check_oracle_mutations.py "$OUT/reference_mutants"
```

It is not a substitute for compiled-native mutation evidence.

## 6. Review, publish and stop at the actual ceiling

Run one focused PHYS-MATH review and one focused PHYS-MATH-CODE review of this
slice. Audit K cancellation, opacity units, native ownership, real diagnostics,
member isolation, and oracle independence. Repair only reproduced defects and
rerun their dependent tests; do not expand into a whole-project review loop.
An unavailable/rejected exploratory local LLM is nonblocking: use
HOST_CODEX_CONTINUE and retain its typed rejection without adopting output.

Publish the implementation branch by ordinary push and create one stacked
draft PR against this delivery branch. Check exact head/tree and changed paths
remotely. Include source/binary identities, raw logs, retained native restore
receipt and remaining full RF04 capability failures. No merge or ready.

Successful bounded terminal:

```text
PASS_RF04_SCALAR_RAW_SLICE_PROOF
NO_PASS_RF04
```

If the numeric comparison fails, preserve the counterexample and report
BLOCKED_SCALAR_NATIVE_DIFFERENTIAL_DEFECT. Do not tune the oracle or thresholds
to match an incorrect implementation. Full polarized remap/composition remains
open; report those exact five requirements from CONTRACT.json without
inventing a legacy replacement. This slice does not close them.
