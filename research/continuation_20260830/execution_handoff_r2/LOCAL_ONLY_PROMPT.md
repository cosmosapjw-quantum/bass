# Local execution prompt R2 — BASS RF-04 telemetry parity

You are continuing `cosmosapjw-quantum/bass` on the machine that owns the
preserved local RF-04 evidence objects. This is a non-authoritative checklist
addendum executable only there and only under the controlling final handoff.

## Frozen status and prohibitions

```text
PASS_REMOTE_RAW_OBJECT_PAYLOAD_CLOSURE_ONLY
PASS_REMOTE_LOCATOR_BYTE_READBACK_ONLY
PASS_RF04_SCALAR_RAW_SLICE_PROOF retained
NO_PASS_RF04
```

Do not merge or mark PR #66 ready. Do not change `main`. Do not force-push,
amend, rebase, or overwrite existing worktrees. Do not infer a PyO3 symbol,
receipt schema, physical grid, remap, closure, q1/q3 node, frame, units, or
operator from names or from the non-authoritative sandbox spike. Do not run
P1--P5, scalar/thermo campaigns, the full suite, timing, GPU, Wolfram, or RF-05
for reassurance.

The authoritative local contract and publication are the exact bytes at:

```text
locator commit 7373fb23d8b9d43bfc52707d9260ff83ee9b3e66
research/continuation_20260830/intake_repair_r4/CODEX_HANDOFF.md

publication commit ed3f502cdcea0b83aab6ccc8de3ec31dd1cee12b
research/continuation_20260830/REMOTE_PUBLICATION.json
```

Read both fully before acting. They supersede the pre-final `0a9f726…` locator,
the handoff-gate-incomplete `4b816641…` / `230581f9…` pair, and execution
handoff R1. On conflict, stop and report the exact fields; this addendum cannot
expand their authority.

## 1. Read back remote authority

Fetch without rewriting history and require the continuation branch to contain
terminal publication commit `ed3f502cdcea0b83aab6ccc8de3ec31dd1cee12b`.

```sh
(
set -euo pipefail
trap 'printf "STOP_INVALID\\n" >&2' ERR
git fetch origin agent/continuation/research-followthrough-20260830-r2
git --no-replace-objects merge-base --is-ancestor \
  ed3f502cdcea0b83aab6ccc8de3ec31dd1cee12b \
  origin/agent/continuation/research-followthrough-20260830-r2
)
```

Read back and require the final locator/publication identities:

```text
locator commit/tree
7373fb23d8b9d43bfc52707d9260ff83ee9b3e66
da512efa34351582f0b42dc0b9dd05ddd48ce79a

locator manifest blob/SHA-256
3934c51532186f91ca7b08b874e3163f8d4b8f48
dd5c30c523ea8ba8a6a77e41fa291c0df3c955d7bb9940dd61ea73cba588c286

publication blob/SHA-256
75d19c6ce4ee33b6458248c2e7198800864d306e
2c4a5abe75b11a8e974ca4bd46dbaf14d71fc707d6dbec9c708c8f5ff41ff8a3
```

Verify those pins from raw committed bytes, not a working-tree copy:

```sh
(
set -euo pipefail
trap 'printf "STOP_INVALID\\n" >&2' ERR
test "$(git --no-replace-objects rev-parse \
  7373fb23d8b9d43bfc52707d9260ff83ee9b3e66^{tree})" = \
  da512efa34351582f0b42dc0b9dd05ddd48ce79a
test "$(git --no-replace-objects rev-parse \
  ed3f502cdcea0b83aab6ccc8de3ec31dd1cee12b^{tree})" = \
  1e7ced1d109155c612436f2c37943805ad71c35d
test "$(git --no-replace-objects rev-parse \
  ed3f502cdcea0b83aab6ccc8de3ec31dd1cee12b^)" = \
  7373fb23d8b9d43bfc52707d9260ff83ee9b3e66
test "$(git --no-replace-objects rev-parse \
  7373fb23d8b9d43bfc52707d9260ff83ee9b3e66:research/continuation_20260830/intake_repair_r4/LOCATOR_MANIFEST.sha256)" = \
  3934c51532186f91ca7b08b874e3163f8d4b8f48
test "$(git --no-replace-objects rev-parse \
  ed3f502cdcea0b83aab6ccc8de3ec31dd1cee12b:research/continuation_20260830/REMOTE_PUBLICATION.json)" = \
  75d19c6ce4ee33b6458248c2e7198800864d306e
)
```

If the branch advanced beyond this addendum, inspect the added commits and
re-read the PR before continuing. Never reset it to a pin.

## 2. Validate the locator and immutable payload

From the locator directory extracted from exact commit `7373fb23…`, bind the
working manifest itself to the published SHA-256 before trusting any entry it
names, then validate the locator bytes:

```sh
(
set -euo pipefail
trap 'printf "STOP_INVALID\\n" >&2' ERR
test "$(sha256sum LOCATOR_MANIFEST.sha256 | awk '{print $1}')" = \
  dd5c30c523ea8ba8a6a77e41fa291c0df3c955d7bb9940dd61ea73cba588c286
sha256sum -c LOCATOR_MANIFEST.sha256
python3 -m json.tool REPAIR_RECEIPT.json >/dev/null
python3 -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 python3 -O -m unittest discover -s tests -q
)
```

Require 6/6 manifest entries, 30/30 normal tests, and 30/30 optimized tests.
Do not execute the superseded 15-test locator.

Then run the canonical raw-object locator against the authenticated clone:

```sh
(
set -euo pipefail
trap 'printf "STOP_INVALID\\n" >&2' ERR
python3 FETCH_AND_VALIDATE.py /absolute/path/to/bass --validate-only
trusted_parent=/absolute/path/to/existing/trusted-private-parent
intake_output="$trusted_parent/bass-rf04-intake-unique"
test ! -e "$intake_output"
python3 FETCH_AND_VALIDATE.py /absolute/path/to/bass \
  --out "$intake_output"
)
```

Require `PASS_IMMUTABLE_PAYLOAD_INTAKE_ONLY`, 18 entries, `NO_PASS_RF04`, and
next action `BASS-LOCAL-01_NATIVE_TELEMETRY_PARITY`. On any error return
`STOP_INVALID`; do not reconstruct extraction manually. The output path must
not be pre-created. Run without a concurrent same-EUID filesystem mutator. If
failure occurs after destination creation, preserve the reported private
partial for manual identity inspection; do not use it and do not perform
pathname-based recursive cleanup.

## 3. Enforce the preserved-local-evidence gate

In the clean authenticated clone, run:

```sh
(
set -euo pipefail
trap 'printf "BLOCKED_BY_MISSING_LOCAL_EVIDENCE\\n" >&2' ERR
git --no-replace-objects cat-file -e \
  148d590bd45ebcc5e4f2ac8a778c30d26d5f9f31^{commit}
git --no-replace-objects cat-file -e \
  d3df4ceb140a9810b0d5219e0e9e748c388a977d^{commit}
test "$(git --no-replace-objects rev-parse \
  d3df4ceb140a9810b0d5219e0e9e748c388a977d^{tree})" = \
  208dc7e2f5981db9d6af2eac7a5455829e431c9e
git --no-replace-objects merge-base --is-ancestor \
  148d590bd45ebcc5e4f2ac8a778c30d26d5f9f31 \
  d3df4ceb140a9810b0d5219e0e9e748c388a977d
worktree_status=$(git status --porcelain=v1)
test -z "$worktree_status"
)
```

If any command fails, stop with:

```text
BLOCKED_BY_MISSING_LOCAL_EVIDENCE
```

Do not recreate the RED or schema from memory, PR #66, or the sandbox spike.

## 4. Create one preserved linked worktree

Choose a new explicit path outside every existing worktree, confirm it does not
exist, and create it at the genuine RED commit. Preserve all existing
worktrees. Create an ordinary implementation branch there. Before combining
histories, inspect ancestry between the RED and the current PR #66 head. The
eventual implementation head must descend from both histories so the PR diff
against the continuation branch contains only authorized local implementation
work. Use an ordinary non-force merge if required; do not rebase. Stop on any
conflict outside the contract allowlist.

Copy only these three files from the validated materialization:

```text
research/continuation_20260830/liouville_telemetry.patch
research/continuation_20260830/apply_telemetry.py
research/continuation_20260830/check_geometry_core.py
```

## 5. Reproduce the genuine RED before implementation

Inspect the two preserved commits and their recorded commands. Run the exact
narrow native and PyO3 selectors supplied by `d3df4ce…`; do not invent selector
names. Retain raw stdout/stderr, exit codes, compiler/Python/Cargo/maturin
versions, environment flags, source blobs, and SHA-256 for every log. A valid
RED must fail on the intended missing telemetry/schema assertion, not on import,
collection, linker, dependency, or unrelated compilation failure.

### Capture baseline runs for the two late boundary REDs

Read `NONFINITE_RECEIPT_FINDING.md`, verify both raw-log hashes, and verify the
hash of `SANDBOX_LATE_RED_REPRODUCER.rs`. That source is diagnostic reference,
not authority to replace the genuine owner module. Before applying telemetry,
add only the two focused regressions through the source-owned baseline test
seams and retain a separate baseline run for each. The two patched-sandbox
observations to challenge are:

1. finite transport input returning `Ok` with
   `log_bolometric_shift = -inf`;
2. finite Type-II state `[f64::MAX, 0, 0, 1, 0]` returning `Ok` with a
   nonfinite derived background.

This package executed only the patched sandbox and established the pre-existing
basis by exact static comparison; it did not execute baseline. Record the
baseline donor blob/hash, test-source blob/hash, command, environment, binary,
exit, and raw-log hash. Record severity only after the genuine owner and public
exposure route are identified, but do not use severity to waive either
mandatory final-R4 boundary gate.

## 6. Harden the geometry validator locally

Before accepting its output as evidence, make an allowlisted validator-only
change that:

- replaces every optimization-removable Python `assert` gate with an explicit
  exception;
- invokes internal `git show` through `git --no-replace-objects`;
- retains the same old/new donor pins and numerical comparison contract;
- proves the historical bad donor/manifest mismatch is detected;
- passes its gate-hardening unit tests both normally and under `python3 -O`;
- runs the accepted bounded geometry-prefix comparison only under the normal
  interpreter with the exact final-R4 command, never under `python3 -O`.

The optimized unit run is non-evidence hardening only. Record this as validator
hardening, not physics or telemetry proof.

## 7. Apply the frozen telemetry patch and run LOCAL-01

Run the fail-closed applicator once. Require old/new donor identity:

```text
old Git blob da6fade06f717ab938b0ec4c712ab239e78c998a
new Git blob e4d0f9c44fc26740d3a1cad6938b522fe514ae37
new SHA-256 ae38f315e84314ed7fef5360ac7f3a44c8f140c5d27d4ddb3a0a539bcef70cab
```

Immediately after this exact pin is established, rerun the same two focused
boundary tests and retain separate candidate logs. Compare baseline and
candidate results, then classify severity under the authenticated owner and
exposure contract. Public-route severity may differ because full transport
revalidates the Type-II background, but both named cases remain mandatory
LOCAL-01 gates regardless of severity.

For each named case, require the candidate to return either a fully finite
success or an existing authorized typed failure carried through the real
result carrier and PyO3 mapping. If the exact patched donor still violates that
rule, make the smallest source-owned authorized correction. Do not clamp,
saturate, fabricate a receipt, or invent a public error schema or Python
mapping. If the required public error authority is ambiguous, stop with that
measured blocker. Keep any safety correction in a separate commit above the
byte-frozen telemetry delta. It will move the donor beyond frozen blob
`e4d0f9…`; record the final rebound Git blob and SHA-256, retain baseline,
candidate, and GREEN/error logs separately, and preserve bit parity on the
ordinary corpus. Only these two named safety cases may change behavior, with
unaffected fields and callbacks compared through the source-owned rejection
point. `FAIL` or `UNTESTED` for either case keeps LOCAL-01 failed and LOCAL-02
closed.

Then compile the real native owner and build the locked production wheel in
the pinned environment (Rust/Cargo 1.94.1, Python 3.12, maturin 1.14.1). Use
offline/locked Cargo operation. Exercise the exact owner/result-carrier/PyO3
surface from the genuine RED.

The acceptance matrix is all-or-nothing:

1. no split;
2. nested/nonuniform split;
3. multiple root panels;
4. `L = N_root + S` and independently checked maximum accepted-leaf depth;
5. independently expected callback count `2 + N_root + 2*S` and exact callback
   fractions/order;
6. bit parity of every pre-existing result field and numerical array on the
   ordinary telemetry corpus, excluding only the two named safety cases under
   their finite-success-or-existing-authorized-typed-failure rule;
7. first child succeeds and second child fails;
8. failures after recursion in carrier, projection, and realizability paths;
9. no partial returned telemetry/history on any failure;
10. exhaustive enum matches, struct destructuring, serialization, adapter
    registration, and Python success/error mapping;
11. counter overflow executed if safely reachable, otherwise explicitly
    source-reviewed and marked unexecuted;
12. no dependency, Cargo lock, equation, tolerance, accepted-interval, or
    background-order change.

Also preserve the semantic boundary: split counts certify adaptive work, not
truncation accuracy, and the current `max_screen_leakage` is computed after
screen projection, so it must not be promoted as a bound on raw transported
longitudinal leakage without a separately authorized definition and test.

Failed calls expose no fabricated success receipt. Callback-owned external
side effects are not transactional; scope transactionality to the returned
top-level result, carrier/history, and API-owned telemetry.

Run one PHYS-MATH and one independent PHYS-MATH-CODE audit on the actual diff
and raw evidence. Repair only reproduced, contract-authorized gate violations;
do not use severity to bypass either named safety case. LOCAL-01 passes only if
every required item is PASS; otherwise retain `NO_PASS_RF04` and stop.

## 8. LOCAL-02 remains gated

Start `BASS-LOCAL-02_SOURCE_BOUND_PHYSICAL_GENERATOR_DIFFERENTIAL` only after a
complete LOCAL-01 pass. If any operator representation, grid, quadrature,
frame, screen basis, time variable, unit, remap/boundary rule, opacity state, or
owner binding is absent, return that measured blocker. Do not invent it. The
maximum permitted conclusion is `SCOPED_FROZEN_PHYSICAL_OPERATOR_PROOF`; the
overall claim remains `NO_PASS_RF04`.

## 9. Delivery

Commit ordinary append-only changes only. Push one implementation branch and
open one stacked **draft** PR against
`agent/continuation/research-followthrough-20260830-r2`. Before push, prove the
head descends from the current remote continuation head and that the PR diff is
inside the allowlist. Read back branch SHA/tree, PR base/head/state, changed
paths, and CI. Do not merge or mark ready.

The final report must include intake JSON, distinct baseline/candidate boundary
logs, any authorized GREEN/error logs, native/PyO3/failure logs, frozen and
final rebound source identities, validation matrix, both audits, remote
readback, retained `PASS_RF04_SCALAR_RAW_SLICE_PROOF`, and current
`NO_PASS_RF04`.
