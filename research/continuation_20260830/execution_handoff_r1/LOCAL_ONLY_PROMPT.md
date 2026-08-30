# Local execution prompt — BASS RF-04 telemetry parity

You are continuing `cosmosapjw-quantum/bass` on the machine that owns the
preserved local RF-04 evidence objects. This prompt is executable only there.

## Frozen status and prohibitions

```text
PASS_IMMUTABLE_PAYLOAD_INTAKE_ONLY
PASS_RF04_SCALAR_RAW_SLICE_PROOF retained
NO_PASS_RF04
```

Do not merge or mark PR #66 ready. Do not change `main`. Do not force-push,
amend, rebase, or overwrite existing worktrees. Do not infer a PyO3 symbol,
receipt schema, physical grid, remap, closure, q1/q3 node, frame, units, or
operator from names or from the non-authoritative sandbox spike. Do not run
P1--P5, scalar/thermo campaigns, the full suite, timing, GPU, Wolfram, or RF-05
for reassurance.

The authoritative local contract is:

```text
research/continuation_20260830/intake_repair_r4/CODEX_HANDOFF.md
```

Read it fully before acting. On conflict, stop and report the exact fields.

## 1. Read back remote authority

Fetch without rewriting history and require the continuation branch to contain
publication commit `53ac002bdc541f04d4eac6930c4ae1bcf53f1935`.

```sh
git fetch origin agent/continuation/research-followthrough-20260830-r2
git --no-replace-objects merge-base --is-ancestor \
  53ac002bdc541f04d4eac6930c4ae1bcf53f1935 \
  origin/agent/continuation/research-followthrough-20260830-r2
```

If the branch advanced, inspect the added commits and re-read the PR before
continuing. Never reset it to the pin.

## 2. Validate the locator and immutable payload

From the locator directory, validate its own exact bytes first:

```sh
sha256sum -c LOCATOR_MANIFEST.sha256
python3 -m json.tool REPAIR_RECEIPT.json >/dev/null
python3 -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 python3 -O -m unittest discover -s tests -q
```

Then run the canonical raw-object locator against the authenticated clone:

```sh
python3 FETCH_AND_VALIDATE.py /absolute/path/to/bass --validate-only
intake_parent=$(mktemp -d)
python3 FETCH_AND_VALIDATE.py /absolute/path/to/bass \
  --out "$intake_parent/payload"
```

Require `PASS_IMMUTABLE_PAYLOAD_INTAKE_ONLY`, 18 entries, `NO_PASS_RF04`, and
next action `BASS-LOCAL-01_NATIVE_TELEMETRY_PARITY`. On any error return
`STOP_INVALID`; do not reconstruct extraction manually.

## 3. Enforce the preserved-local-evidence gate

In the clean authenticated clone, run:

```sh
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
test -z "$(git status --porcelain=v1)"
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

### Reproduce the late pre-existing boundary RED

Read `NONFINITE_RECEIPT_FINDING.md` and verify its log hash. In the genuine
worktree, add the focused regression through the source-owned test seam and run
it against both the baseline and patched donor. The observed scratch failure is
finite input returning `Ok` with `log_bolometric_shift = -inf`; the immutable
telemetry patch does not touch the responsible arithmetic. Classify severity
under the project contract. If a fix is authorized, return a typed failure or a
fully finite result through the existing source-owned API and real PyO3 mapping.
Do not clamp, saturate, fabricate a receipt, or invent a public error schema.
Retain RED and GREEN logs separately.

## 6. Harden the geometry validator locally

Before accepting its output as evidence, make an allowlisted validator-only
change that:

- replaces every optimization-removable Python `assert` gate with an explicit
  exception;
- invokes internal `git show` through `git --no-replace-objects`;
- retains the same old/new donor pins and numerical comparison contract;
- proves the historical bad donor/manifest mismatch is detected;
- passes both normal and `python3 -O` tests.

Record this as validator hardening, not physics or telemetry proof.

## 7. Apply the frozen telemetry patch and run LOCAL-01

Run the fail-closed applicator once. Require old/new donor identity:

```text
old Git blob da6fade06f717ab938b0ec4c712ab239e78c998a
new Git blob e4d0f9c44fc26740d3a1cad6938b522fe514ae37
new SHA-256 ae38f315e84314ed7fef5360ac7f3a44c8f140c5d27d4ddb3a0a539bcef70cab
```

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
6. bit parity of every pre-existing result field and numerical array;
7. first child succeeds and second child fails;
8. failures after recursion in carrier, projection, and realizability paths;
9. no partial returned telemetry/history on any failure;
10. exhaustive enum matches, struct destructuring, serialization, adapter
    registration, and Python success/error mapping;
11. counter overflow executed if safely reachable, otherwise explicitly
    source-reviewed and marked unexecuted;
12. no dependency, Cargo lock, equation, tolerance, accepted-interval, or
    background-order change.

Failed calls expose no fabricated success receipt. Callback-owned external
side effects are not transactional; scope transactionality to the returned
top-level result, carrier/history, and API-owned telemetry.

Run one PHYS-MATH and one independent PHYS-MATH-CODE audit on the actual diff
and raw evidence. Repair only reproduced P0/P1 findings. LOCAL-01 passes only
if every required item is PASS; otherwise retain `NO_PASS_RF04` and stop.

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

The final report must include intake JSON, RED/GREEN/native/PyO3/failure logs,
source identities, validation matrix, both audits, remote readback, retained
`PASS_RF04_SCALAR_RAW_SLICE_PROOF`, and current `NO_PASS_RF04`.
