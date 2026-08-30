# BASS RF-04 intake-repair and local continuation handoff

## Controlling status

```text
Historical package status:
BLOCKED_IMMUTABLE_PAYLOAD_MANIFEST_MISMATCH

Superseding delivery status:
PASS_IMMUTABLE_PAYLOAD_INTAKE_ONLY

Scientific status:
PASS_RF04_SCALAR_RAW_SLICE_PROOF retained
NO_PASS_RF04
```

This is an executable continuation contract, not a scientific PASS.  Do not
merge or mark PR #66 ready.  Do not change `main`.  Do not create an
implementation worktree until the raw-object intake below passes.

## Instruction precedence

This `intake_repair_r4/CODEX_HANDOFF.md` and the final v2
`REMOTE_PUBLICATION.json` supersede only the intake and local-execution
instructions in the manifest-covered historical `continuation_20260830/
CODEX_HANDOFF.md`.  That older file is retained byte-identically as evidence of
the failed package and is **not an executable prompt**.  In particular, do not
use its `verify_payload.py` substitution, its `mktemp -u` command, or its
fallback that starts from the remote delivery when the local RED evidence is
missing.  Non-conflicting scientific prohibitions in the immutable contract
remain binding.  On any other conflict, stop and report the exact fields rather
than choosing one silently.

## Exact remote authority

Repository: `cosmosapjw-quantum/bass`

```text
PR #66 base
2aaad1d72064ddeb60b27a0ec15536d0a2ec6a28
tree 5b9a15c4a378a28e9592ede5a208e8cafc45c482

historical invalid payload
4538ac92fcf5cf70a4d73e2cb3e53125a49590ba
tree 982173d6e3fa1760c58cd547545c2b17f37c7a11

historical terminal retaining the same invalid manifest
989f9c38ba625f1de74941fd3e5f51bdd753d1bd
tree f101c0560fa9b719892365561d7b2d0f2a1054ed

superseding immutable payload
16f5811beb7d73fae800ff90caf30f69deebc9fd
tree 85a9164e01ea77d312b185809b3698363c750526

corrected manifest
Git blob 32473fb754c9b6b84e5e5980c551860297f1054a
SHA-256 af2ed1220c76d36bd82e5362b1f4a5fb0bb8061eb6470129458333c533b320de
18 entries, 18 raw-byte matches
```

The old payload remains immutable evidence of failure.  Never relabel
`4538ac92...` or `989f9c38...` as valid intake.  The successor changes only the
two false manifest digests; the two payload files themselves are unchanged.

## Required intake

Use the `FETCH_AND_VALIDATE.py` delivered beside this file.  The compatibility
wrapper `FETCH_AND_VALIDATE.sh` invokes that same Python file.  Validate this
locator bundle against `LOCATOR_MANIFEST.sha256` and the final
`REMOTE_PUBLICATION.json` readback before executing it.

From a machine with the authenticated BASS clone and all pinned objects:

```sh
python3 FETCH_AND_VALIDATE.py /absolute/path/to/bass --validate-only

intake_parent=$(mktemp -d)
python3 FETCH_AND_VALIDATE.py /absolute/path/to/bass \
  --out "$intake_parent/payload"
```

Expected status:

```text
PASS_IMMUTABLE_PAYLOAD_INTAKE_ONLY
manifest_entries = 18
scientific_claim = NO_PASS_RF04
next_action = BASS-LOCAL-01_NATIVE_TELEMETRY_PARITY
```

The locator uses `git --no-replace-objects`, validates exact commit/tree and
single-parent ancestry, rejects non-regular tree modes and unsafe paths, reads
bytes with `git cat-file`, checks manifest/contract closure, and refuses to
overwrite or materialize inside the source clone.  It does not check out a
branch, install dependencies, modify the clone, apply a patch, or access the
network.  A later mutable branch tip does not invalidate the pinned payload.
It also requires the contract's repository, base commit/tree, current claim,
exact next action, and `scientific_promotion=false` to agree with the locator
specification.

On any locator error, return `STOP_INVALID` with the first exact mismatch.  Do
not manually reconstruct extraction and do not substitute `verify_payload.py`:
the latter is a payload-internal byte check, not the commit/tree locator.

## Preserved local chain gate

Only after intake succeeds, locate the user-reported local evidence chain in a
clean repository:

```text
source-probe evidence commit
148d590bd45ebcc5e4f2ac8a778c30d26d5f9f31

genuine schema/native RED commit
d3df4ceb140a9810b0d5219e0e9e748c388a977d

reported RED tree
208dc7e2f5981db9d6af2eac7a5455829e431c9e
```

Verify object existence, exact tree, ancestry, and clean worktree.  If a pin is
absent or the tree differs, stop with `BLOCKED_BY_MISSING_LOCAL_EVIDENCE`; do
not replace it with the remote research branch or recreate its evidence from
memory.  Preserve all existing worktrees.  Create one new linked worktree at
the verified RED commit using an ordinary non-force operation.

## BASS-LOCAL-01_NATIVE_TELEMETRY_PARITY

Copy only these immutable payload artifacts from the materialized intake:

```text
research/continuation_20260830/liouville_telemetry.patch
research/continuation_20260830/apply_telemetry.py
research/continuation_20260830/check_geometry_core.py
```

Run the existing genuine RED first and retain its raw log.  Then apply the
patch with the supplied fail-closed applicator.  Its donor binding is:

```text
old Git blob da6fade06f717ab938b0ec4c712ab239e78c998a
new Git blob e4d0f9c44fc26740d3a1cad6938b522fe514ae37
```

Counter semantics are frozen:

```text
S = total actual split events on the successful call
D = maximum accepted-leaf recursion depth
L = accepted subinterval count
N_root = input/root subinterval count

L = N_root + S
```

No existing numerical result field, accepted interval, callback order, or
background-call order may change.  Failed calls remain typed errors and expose
no fabricated success receipt or partial telemetry.  Overflow is a typed
failure, never saturation.

For a successful call, the independently expected background-callback count is

```text
2 + N_root + 2*S
```

when the existing two endpoint samples are included.  Callback-owned external
side effects are not transactional and need not roll back on error; restrict
the no-partial-state claim to the returned top-level result, carrier/history,
and telemetry owned by this API.

For the bounded geometry-prefix test, do not use `mktemp -u`, do not run Python
with optimization, and disable Git replacement objects:

```sh
tmp_root=$(mktemp -d)
PYTHONOPTIMIZE= GIT_NO_REPLACE_OBJECTS=1 \
python3 check_geometry_core.py \
  --repo /absolute/path/to/new/worktree \
  --out "$tmp_root/geometry-core"
```

That prefix test is not carrier/PyO3 proof.  In the pinned native environment,
build and exercise the real owner crate, result carrier, and Python wrapper.
Before using the prefix script as evidence, replace its optimization-removable
Python `assert` gates with explicit exceptions and make its internal `git show`
use `--no-replace-objects`; demonstrate that the hardened script detects the
old mismatch.  This is validator hardening, not a physics change.
The minimum acceptance matrix is:

- no split, nested/nonuniform split, and multiple root panels;
- `L=N_root+S` and independently checked maximum depth;
- bit parity of all pre-existing result fields and numerical arrays;
- callback fractions, ordering, and call counts;
- first child succeeds then second child fails;
- failures after recursion in carrier/projection/realizability paths;
- exhaustive enum matches, struct destructuring, serialization, and Python
  success/error mapping;
- no partial telemetry/history on any failure;
- overflow behavior executed if safely reachable, otherwise explicitly marked
  source-reviewed and unexecuted.

Record compiler, Cargo/Rust pins, build flags, exact source blobs, command exit
codes, logs and their SHA-256 values.  Run one PHYS-MATH and one PHYS-MATH-CODE
audit at the changed boundary and repair only reproduced P0/P1 findings.
Treat the new fields and error variant as an API/schema change even if all
pre-existing numerical fields are bit-identical: audit exhaustive Rust matches,
serialized receipts, adapter registration, and Python-visible mappings.

Passing LOCAL-01 permits a scoped telemetry-parity statement only.  The claim
remains `NO_PASS_RF04`.

## BASS-LOCAL-02_SOURCE_BOUND_PHYSICAL_GENERATOR_DIFFERENTIAL

Proceed only after every LOCAL-01 acceptance item is demonstrated.  Bind the
actual source-owned geometric generator/action `A` and collision generator
`C` to the same carrier, grid, quadrature measure, frame, screen bases, time
variable, units, boundary/remap rule, opacity/electron state, and owner blobs.
If any binding is missing, return the measured blocker; do not invent it.

Use a nondegenerate frozen small grid where both operators are nonzero and
noncommuting and polarization/screen rotation are active.  Compare the native
linear action `(A+C)y` with an independently assembled dense oracle that does
not reuse production assembly/indexing.  Detect at least added-`K`, index
permutation, measure omission, and screen mismatch mutants.  If `A` is exposed
only through a finite map `G_h`, use a multi-`h` extrapolation with explicit
truncation and roundoff bounds; a single finite step is not a generator proof.

Bind these representation details explicitly in the receipt:

- both `A` and `C` have the same inverse-time unit and time orientation;
- the Hubble-normalized time convention, step sign, bolometric factor four,
  and opacity scaling `kappa = opacity_scale * opacity`;
- future-photon propagation direction rather than silently substituting its
  negative;
- the native node-major rank-9 carrier and four-real-dimensional physical
  screen subspace, including the local packed-`V`/antisymmetric sign convention;
- fixed-grid quadrature weights versus interpolation/remap weights;
- raw Thomson and discrete-AP lanes as different numerical operators, never
  reassurance-parity inputs.

If the owner exposes only the ray-level extended characteristic `(e,J)`, label
the result as a local tensor action.  A fixed-grid Eulerian `A` additionally
requires a source-bound angular map, departure rule, measure, frame, and screen
association.  Their absence is a typed authority blocker.

The maximum allowed conclusion is:

```text
SCOPED_FROZEN_PHYSICAL_OPERATOR_PROOF
```

It does not prove a full trajectory, stiff/AP behavior, positivity, restart,
batch determinism, convergence, performance, or RF-04.

Never execute or promote:

- uncompensated `K/2-C/2-G-C/2-K/2` (its leading generator is `A+C+K`);
- a Bloch/dephasing toy as Thomson physics;
- exact reversibility of a dissipative full remap;
- row sums as a replacement for weighted conservation;
- `nextDown(computed dot)` as a rigorous support bound;
- source-absent q1/q3 nodes, stencil, closure, or physical adapter;
- rewritten historical evidence hashes or reassurance reruns of P1--P5.

## Required final local deliverables

Commit only ordinary append-only changes in the new worktree.  Push one stacked
draft implementation PR against the RF-04 continuation delivery branch; do not
merge or mark ready.  The final report must include:

1. intake JSON and locator-bundle hashes;
2. exact base/head/tree and clean-state evidence;
3. RED, focused GREEN, native/carrier/PyO3, mutation, and failure-path logs;
4. changed-path allowlist and source-identity rebinding;
5. PHYS-MATH and PHYS-MATH-CODE reports;
6. machine receipt with each acceptance item `PASS`, `FAIL`, or `UNTESTED`;
7. remote branch/PR readback and CI classified only for what it executed;
8. retained claim `PASS_RF04_SCALAR_RAW_SLICE_PROOF` and current claim
   `NO_PASS_RF04`.

Do not continue to LOCAL-02 after a partial LOCAL-01 result.
