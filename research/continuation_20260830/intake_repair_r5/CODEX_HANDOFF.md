# BASS RF-04 Git-2.43-compatible intake-repair R5 and local continuation handoff

## Controlling status

```text
Historical package status:
BLOCKED_IMMUTABLE_PAYLOAD_MANIFEST_MISMATCH

Immutable payload status:
PASS_REMOTE_RAW_OBJECT_PAYLOAD_CLOSURE_ONLY

R4 exact-host locator execution:
STOP_INVALID_GIT_GLOBAL_OPTION_INCOMPATIBILITY

R5 exact-host authenticated-clone execution:
DEFERRED_LOCAL_NOT_RUN_BY_PUBLISHER

Scientific status:
PASS_RF04_SCALAR_RAW_SLICE_PROOF retained
NO_PASS_RF04
```

This is an executable continuation contract, not a scientific PASS.  Do not
merge or mark PR #66 ready.  Do not change `main`.  Do not create an
implementation worktree until the raw-object intake below passes.

## Instruction precedence

This `intake_repair_r5/CODEX_HANDOFF.md` and its successor remote publication
`REMOTE_PUBLICATION.json` supersede only the intake and local-execution
instructions in the manifest-covered historical `continuation_20260830/
CODEX_HANDOFF.md`.  That older file is retained byte-identically as evidence of
the failed package and is **not an executable prompt**.  In particular, do not
use its `verify_payload.py` substitution, its `mktemp -u` command, or its
fallback that starts from the remote delivery when the local RED evidence is
missing.  Non-conflicting scientific prohibitions in the immutable contract
remain binding.  On any other conflict, stop and report the exact fields rather
than choosing one silently.

They also supersede every execution instruction and locator pin under
`execution_handoff_r1/**` and `execution_handoff_r2/**`.  In particular,
R2 at commit `468dd2ee6602a2ced4d6bbf015f0b2adb0e107a2` depended on R4.  Preserve
all earlier handoffs as evidence; do not execute their local prompts, ZIPs,
statuses, or validation matrices.

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

The first published locator-bundle commit
`0a9f726df916c3ddcf74b3a0bd17ba4c529f5a8d` is a superseded pre-final
candidate.  Its path-boundary audit found ambient Git routing, linked-worktree
metadata, and path-replacement gaps.  Do not execute or cite its locator/ZIP as
the final artifact.  Use the bytes at the final PR #66 head and require their
hashes to match the final `REMOTE_PUBLICATION.json`.

R4 locator commit `7373fb23d8b9d43bfc52707d9260ff83ee9b3e66`
(tree `da512efa34351582f0b42dc0b9dd05ddd48ce79a`) is immutable and remains
valid remote evidence, but it is not executable on the reported exact host.
Its unconditional global `--no-lazy-fetch` argument is unsupported by that
host's `/usr/bin/git 2.43.0`.  The externally reported ordinary run therefore
stopped with 2 PASS, 5 FAIL, and 23 ERROR; optimized tests and canonical
18-file intake were not run.  This is an execution-environment compatibility
failure, not a scientific result.  Do not modify or retry R4.

The old payload remains immutable evidence of failure.  Never relabel
`4538ac92...` or `989f9c38...` as valid intake.  The superseding payload commit
`16f5811...` changes only the two false manifest digests; the two payload files
themselves are unchanged.

## Required intake

Use the `FETCH_AND_VALIDATE.py` delivered beside this file.  The compatibility
wrapper `FETCH_AND_VALIDATE.sh` invokes that same Python file.  Validate this
locator bundle against `LOCATOR_MANIFEST.sha256` and the final
`REMOTE_PUBLICATION.json` readback before executing it.

From a machine with the authenticated BASS clone and all pinned objects:

```sh
python3 -m json.tool REPAIR_RECEIPT.json >/dev/null
python3 -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 python3 -O -m unittest discover -s tests -q
python3 FETCH_AND_VALIDATE.py /absolute/path/to/bass --validate-only
python3 FETCH_AND_VALIDATE.py /absolute/path/to/bass
```

The selected Git installation is an explicit trust boundary.  Before running,
set `PATH` so its first `git` is the intended trusted installation and require
an executable `git-upload-pack` below the exact directory reported by that
Git's `git --exec-path`.  On the reported target this means
`PATH=/usr/bin:/bin`, `/usr/bin/git 2.43.0`, and its matching helper.  Do not
prepend a wrapper or user-writable executable directory.

Require 56/56 ordinary and 56/56 optimized fixture tests with zero skips.  The published R5
receipt records separate fresh full-suite runs with `/usr/bin/git 2.43.0` and
`/usr/local/bin/git 2.51.1`; the exact host must still rerun the suite and the
authenticated-clone intake rather than inheriting the publisher's fixtures.

The locator invocation without `--validate-only` creates a fresh private
destination and reports its exact `materialized_root` in JSON.  To select a
location yourself, pass a new, nonexistent `--out` below an already-existing
trusted parent; do not pre-create the output directory.

Expected status:

```text
PASS_IMMUTABLE_PAYLOAD_INTAKE_ONLY
manifest_entries = 18
scientific_claim = NO_PASS_RF04
next_action = BASS-LOCAL-01_NATIVE_TELEMETRY_PARITY
```

R5 binds the resolved Git executable and upload-pack helper by canonical path,
stat signature, and SHA-256; rechecks path/stat signatures around every
invocation and rehashes both at successful probe completion.  It constructs a
minimal environment that drops ambient loader, shell, Python,
credential, proxy, editor, pager, temp, and Git-routing injection variables.
It always sets `GIT_NO_LAZY_FETCH=1` and `--no-replace-objects`.  When the bound
Git recognizes the global `--no-lazy-fetch` option, R5 retains that redundant
defense; otherwise it admits the environment-only lane only after a private,
offline, local-file promisor differential proves that the guarded lookup fails
without changing the names, identities, metadata, sizes, or SHA-256 values in
its object store while the control lookup retrieves the exact sentinel.  Any
inconclusive probe stops before a source payload object read.  A safely bound
probe tree is removed on both success and ordinary capability failure; a path
is reported and retained only when safe identity-checked cleanup itself fails.

All production source-object commands additionally deny every transport via
environment and command-line policy, disable hooks and automatic maintenance,
and use the canonical helper directory reported by the bound Git.  The
capability probe alone admits the `file` transport to its private origin and
uses a shell-quoted absolute command for the separately bound upload-pack
target.  The locator then validates exact
commit/tree and single-parent
ancestry, rejects non-regular tree modes and unsafe paths, reads bytes with
`git cat-file`, and checks manifest/contract closure.  It protects the current
and every currently resolvable worktree returned by `git worktree list`, plus
per-worktree and common Git metadata.
Materialization fails closed unless directory-FD and no-follow primitives are
available.  Ambient `TMPDIR`, `TEMP`, and `TMP` candidates are considered in
order without Python's write/delete probe; invalid or unsafe candidates are
skipped only in favor of a later explicitly supplied safe candidate, and the
selected parent is opened and checked before any destination is made.
The source worktree, Git directory, and common Git directory identities are
bound during validation and checked again after all writes.  Creation, writing,
and hashing stay anchored to retained directory/file descriptors; public
parent/root identities are rechecked before PASS.  Parent namespaces must be
owned by root or the current effective UID, and group/world-writable ancestors
must be sticky.

The threat model trusts the caller-selected `PATH` and the selected Git
installation, including its helper directory, helper command, wrapper
interpreter, and delegates.  It assumes no hostile process running under the
same effective UID during intake; run it without concurrent same-user
filesystem mutation.  Git subprocesses are not internally time- or
output-bounded; a hung or unbounded-output Git/helper is an accepted residual
outside this locator's fail-closed proof and must be controlled by the trusted
host or an external supervisor.
On any failure after destination creation, the locator performs no recursive or
pathname-based cleanup.  It returns `STOP_INVALID` with the requested partial
path; a private `0700` partial may remain there (or at its displaced inode after
a detected rename) and must never be used as accepted output.  Remove it only
after manual identity inspection.

Given that trusted Git boundary, the locator does not check out a branch,
install dependencies, modify the clone, apply a patch, or request a network
transport.  Production Git commands deny all transports.  Its local-file
capability probe writes only inside a new private `0700` temporary tree outside
all protected repository roots.  A later mutable branch tip does
not invalidate the pinned payload.  It also requires the contract's
repository, base commit/tree, current claim, exact next action, and
`scientific_promotion=false` to agree with the locator specification.

On any locator error, return `STOP_INVALID` with the first exact mismatch.  A
failed capability probe reports an evidence path only if safe cleanup could
not complete.  Do
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

On the ordinary telemetry-parity corpus, no existing numerical result field,
accepted interval, callback order, or background-call order may change.  This
invariant excludes only the two explicitly named pre-existing nonfinite cases
below.  Failed calls remain typed errors and expose no fabricated success
receipt or partial telemetry.  Overflow is a typed failure, never saturation.

For a successful call, the independently expected background-callback count is

```text
2 + N_root + 2*S
```

when the existing two endpoint samples are included.  Callback-owned external
side effects are not transactional and need not roll back on error; restrict
the no-partial-state claim to the returned top-level result, carrier/history,
and telemetry owned by this API.

Split, accepted-leaf, and depth counters certify adaptive work only.  They are
not a truncation-error estimator or an integration-accuracy certificate.  The
current `max_screen_leakage` is evaluated after screen projection and must not
be described as raw transport leakage without a separately authorized
pre-projection diagnostic contract.

### Mandatory pre-existing nonfinite-boundary REDs

The late evidence commits `dc10d24835141147674c60327cfb29f1a3ba6cb1`
and `5c024e48bcd3931201ab8ebd83830f760bbfdd39` reproduce two
source-owned boundary defects that predate and are not modified by the
telemetry patch.  Their old execution prompt is superseded, but these facts are
mandatory LOCAL-01 gates:

1. Finite transport inputs (`expansion=1.0`, `step=1.0e308`, one root panel,
   valid screen projector) return `Ok` while `log_bolometric_shift=-inf`.
   The focused scratch test exited 101 at the intended finiteness assertion;
   its raw log SHA-256 is
   `326f26db8342c464453dfae148f6dc1dff7e332dba07cc635cda84120580066b`.
2. Finite Type-II state `[f64::MAX, 0.0, 0.0, 1.0, 0.0]` returns `Ok` with a
   nonfinite derived background.  The focused scratch test exited 101 at the
   intended all-fields-finite assertion; its raw log SHA-256 is
   `cff06d701f4d581fbdb7f3ddd6c0e305ddc10e6e10297fd57f3f164c41ae8756`.

After the preserved-chain gate succeeds, recreate both focused tests through
their source-owned seams and run them separately against the verified baseline
and patched donor.  The published scratch logs establish provenance but do not
replace authenticated-host RED logs.  Every scalar in a successful returned
receipt and every field in a successful derived background must be finite.
Candidate behavior must be either a fully finite success or an existing,
authorized typed failure carried through the real result carrier and PyO3
error mapping.  Do not clamp, saturate, fabricate a success receipt, or invent
a public error variant or Python mapping.  If the public error authority is
ambiguous, stop with the measured authority blocker.

For these two cases only, the finite-success-or-authorized-typed-error rule is
the sole permitted behavioral exception to numerical/callback/bit parity.  A
typed failure may end callbacks at the source-owned rejection point; compare
all unaffected fields and callback history up to that point.  No other parity
waiver follows from these defects.  Keep any authorized boundary repair in a
separate safety-boundary commit above the byte-frozen telemetry delta, with its
own RED/GREEN evidence and public-schema review; do not relabel that repair as
telemetry-only behavior.

Retain baseline RED and candidate GREEN/error logs separately with exit codes
and SHA-256 values.  `FAIL` or `UNTESTED` for either case keeps LOCAL-01 failed
and LOCAL-02 closed.

For the bounded geometry-prefix test, do not use `mktemp -u`, do not run Python
with optimization, and disable Git replacement objects:

```sh
trusted_tmp=/absolute/path/to/existing/trusted-temp-parent
tmp_root=$(mktemp -d -p "$trusted_tmp" bass-geometry.XXXXXXXX)
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
- bit parity of all pre-existing result fields and numerical arrays on the
  ordinary telemetry-parity corpus, excluding only the two named safety cases;
- callback fractions, ordering, and call counts;
- first child succeeds then second child fails;
- failures after recursion in carrier/projection/realizability paths;
- exhaustive enum matches, struct destructuring, serialization, and Python
  success/error mapping;
- both pre-existing nonfinite-boundary REDs reproduced on the baseline and
  resolved on the candidate as finite success or an authorized typed failure,
  including the real carrier/PyO3 mapping;
- no partial telemetry/history on any failure;
- overflow behavior executed if safely reachable, otherwise explicitly marked
  source-reviewed and unexecuted.

Record compiler, Cargo/Rust pins, build flags, exact source blobs, command exit
codes, logs and their SHA-256 values.  Run one PHYS-MATH and one PHYS-MATH-CODE
audit at the changed boundary and repair only reproduced P0/P1 findings.
Treat the new fields and error variant as an API/schema change even if all
pre-existing numerical fields are bit-identical: audit exhaustive Rust matches,
serialized receipts, adapter registration, and Python-visible mappings.

Passing LOCAL-01 requires every matrix item above, including both nonfinite
boundary cases and separation of any safety-boundary delta from the telemetry
delta.  It permits a scoped ordinary-corpus telemetry-parity statement plus a
separately named boundary-safety result only.  The claim remains
`NO_PASS_RF04`.

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
