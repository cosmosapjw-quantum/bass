# Local execution prompt R3 — BASS RF-04 telemetry parity

Continue `cosmosapjw-quantum/bass` only on the host that owns the authenticated
complete clone and the preserved RF-04 local evidence objects.  This prompt is
subordinate to the exact R5 handoff and publication v6; it cannot widen their
authority.

## Frozen status and prohibitions

```text
PASS_REMOTE_RAW_OBJECT_PAYLOAD_CLOSURE_ONLY
PASS_REMOTE_R5_LOCATOR_BYTE_READBACK_ONLY
R4_EXACT_HOST = STOP_INVALID
R5_EXACT_HOST_AUTHENTICATED_CLONE = DEFERRED_LOCAL
LOCAL_EVIDENCE_GATE = NOT_REACHED
PASS_RF04_SCALAR_RAW_SLICE_PROOF retained
NO_PASS_RF04
```

Do not merge or mark PR #66 ready.  Do not change `main`.  Do not force-push,
amend, rebase, reset, overwrite existing worktrees, or remove pre-existing
untracked files.  Do not use R4 or R2 execution instructions, recreate evidence
from memory, or use the historical sandbox as implementation source.  Do not
infer a PyO3 schema, error mapping, physical grid, remap, closure, q1/q3 node,
frame, unit, or operator from names.

The exact authority is:

```text
R5 locator commit/tree
57ec56393de43eb78d758222f78478aea8b14517
ef1b4463547fad4aa36d068a6b538b806d1b15ac

R5 handoff blob/SHA-256
c1d0a740e79db3fb2ec0792ecf01837d4f502d53
b9aa8a6a3cb1e380fb7fc9cde5f594dfd40d3e39df6a079c8a768302a073ffa4

R5 locator manifest blob/SHA-256
50ab58fa5268e18d9a857cee32bd2e475999194a
5f9b95207a252293c2678872dd5945a718157fdd83b40a8c24920794151a5d6e

R5 archive blob/SHA-256
e3ac728cb499528a71a2e50161b92293daf69f80
4f31624154c2b8c09383f17e1dac8977134c21ef024d876dc9e2b04727fcd486

publication v6 commit/tree/blob/SHA-256
cb9b2c84c593733e6f8944b417d3876a2aad9407
1d9dded878c7e6dc7323bd2def8a89bc85df36a0
1580e8ce9ecb6f4d1d85c7c208e4610a62b01747
d597c92eda2944a4d4ce6a4525b1eb0c3e234c1965594ca1fc482188d3c09cca
```

Read the R5 `CODEX_HANDOFF.md` and publication v6 fully from those committed
bytes before acting.  On conflict, stop and report the exact fields.

## 1. Record and preserve canonical state

From the canonical clone, record before mutation:

```sh
git status --porcelain=v1 --untracked-files=all
git worktree list --porcelain
git rev-parse HEAD HEAD^{tree}
git rev-parse main
```

Do not require a globally clean state by deleting anything.  The controlling
preserved-chain gate below requires no tracked/staged changes; retain and report
pre-existing untracked files.  If tracked/staged state is already dirty, stop
rather than cleaning it.

## 2. Fetch and verify remote authority

Use the intended trusted Git installation.  On the reported host:

```sh
trusted_git=/usr/bin/git
test -x "$trusted_git"
test "$($trusted_git --version)" = "git version 2.43.0"
trusted_exec_path=$($trusted_git --exec-path)
test -x "$trusted_exec_path/git-upload-pack"
$trusted_git fetch origin agent/continuation/research-followthrough-20260830-r2
```

Then disable replacement objects and lazy fetching for the exact local object
checks.  Require all commands below to pass:

```sh
export GIT_NO_REPLACE_OBJECTS=1
export GIT_NO_LAZY_FETCH=1

test "$($trusted_git rev-parse 57ec56393de43eb78d758222f78478aea8b14517^{tree})" = \
  ef1b4463547fad4aa36d068a6b538b806d1b15ac
test "$($trusted_git rev-parse 57ec56393de43eb78d758222f78478aea8b14517^)" = \
  468dd2ee6602a2ced4d6bbf015f0b2adb0e107a2
test "$($trusted_git rev-parse cb9b2c84c593733e6f8944b417d3876a2aad9407^{tree})" = \
  1d9dded878c7e6dc7323bd2def8a89bc85df36a0
test "$($trusted_git rev-parse cb9b2c84c593733e6f8944b417d3876a2aad9407^)" = \
  57ec56393de43eb78d758222f78478aea8b14517
$trusted_git merge-base --is-ancestor \
  cb9b2c84c593733e6f8944b417d3876a2aad9407 \
  origin/agent/continuation/research-followthrough-20260830-r2

test "$($trusted_git rev-parse \
  57ec56393de43eb78d758222f78478aea8b14517:research/continuation_20260830/intake_repair_r5/CODEX_HANDOFF.md)" = \
  c1d0a740e79db3fb2ec0792ecf01837d4f502d53
test "$($trusted_git rev-parse \
  57ec56393de43eb78d758222f78478aea8b14517:research/continuation_20260830/intake_repair_r5/LOCATOR_MANIFEST.sha256)" = \
  50ab58fa5268e18d9a857cee32bd2e475999194a
test "$($trusted_git rev-parse \
  57ec56393de43eb78d758222f78478aea8b14517:research/continuation_20260830/intake_repair_r5/BASS_RF04_INTAKE_REPAIR_HANDOFF_R5.zip)" = \
  e3ac728cb499528a71a2e50161b92293daf69f80
test "$($trusted_git rev-parse \
  cb9b2c84c593733e6f8944b417d3876a2aad9407:research/continuation_20260830/REMOTE_PUBLICATION.json)" = \
  1580e8ce9ecb6f4d1d85c7c208e4610a62b01747
```

If the remote branch contains later addendum commits, inspect them and re-read
PR #66; never reset the branch back to these pins.  Any missing/mismatched pin
is `STOP_INVALID`.

## 3. Extract and validate the exact R5 locator bundle

Choose an existing trusted private temporary parent outside every BASS
worktree.  The following writes only a new private extraction tree:

```sh
trusted_tmp=/absolute/path/to/existing/trusted-private-parent
locator_root=$(mktemp -d -p "$trusted_tmp" bass-rf04-r5.XXXXXXXX)
$trusted_git cat-file blob e3ac728cb499528a71a2e50161b92293daf69f80 \
  > "$locator_root/BASS_RF04_INTAKE_REPAIR_HANDOFF_R5.zip"
test "$(sha256sum "$locator_root/BASS_RF04_INTAKE_REPAIR_HANDOFF_R5.zip" | awk '{print $1}')" = \
  4f31624154c2b8c09383f17e1dac8977134c21ef024d876dc9e2b04727fcd486
mkdir "$locator_root/locator"
unzip -q "$locator_root/BASS_RF04_INTAKE_REPAIR_HANDOFF_R5.zip" \
  -d "$locator_root/locator"
cd "$locator_root/locator"
test "$(sha256sum LOCATOR_MANIFEST.sha256 | awk '{print $1}')" = \
  5f9b95207a252293c2678872dd5945a718157fdd83b40a8c24920794151a5d6e
sha256sum -c LOCATOR_MANIFEST.sha256
python_bin=$(command -v python3)
test -x "$python_bin"
PATH=/usr/bin:/bin "$python_bin" -m json.tool REPAIR_RECEIPT.json >/dev/null
PATH=/usr/bin:/bin "$python_bin" -m unittest discover -s tests -v
PATH=/usr/bin:/bin PYTHONDONTWRITEBYTECODE=1 \
  "$python_bin" -O -m unittest discover -s tests -v
```

Require 6/6 manifest entries and 56/56 tests with zero skips in both modes.
Do not accept a failure caused by collection, dependency, or an unintended Git
binary as test evidence.  R5 trusts the selected `PATH` and Git installation;
its Git subprocess runtime/output are not internally bounded, so use only the
trusted responsive installation or an external host supervisor.

## 4. Run R5 authenticated-clone intake

Still in the validated locator directory:

```sh
canonical_bass=/absolute/path/to/authenticated/bass
PATH=/usr/bin:/bin "$python_bin" FETCH_AND_VALIDATE.py \
  "$canonical_bass" --validate-only

intake_parent=/absolute/path/to/existing/trusted-private-parent
intake_output="$intake_parent/bass-rf04-intake-r5-unique"
test ! -e "$intake_output"
PATH=/usr/bin:/bin "$python_bin" FETCH_AND_VALIDATE.py \
  "$canonical_bass" --out "$intake_output"
```

Require:

```text
status = PASS_IMMUTABLE_PAYLOAD_INTAKE_ONLY
manifest_entries = 18
scientific_claim = NO_PASS_RF04
next_action = BASS-LOCAL-01_NATIVE_TELEMETRY_PARITY
```

On any error, stop with `STOP_INVALID`; do not manually reconstruct payload
extraction and do not create an implementation worktree.  A normal failed
capability probe is identity-checked and removed; a retained probe path is
reported only when safe cleanup could not complete.  Never use any partial as
accepted output.

## 5. Enforce the preserved-local-evidence gate

Only after Step 4 passes, return to the canonical clone and require:

```sh
cd "$canonical_bass"
$trusted_git cat-file -e \
  148d590bd45ebcc5e4f2ac8a778c30d26d5f9f31^{commit}
$trusted_git cat-file -e \
  d3df4ceb140a9810b0d5219e0e9e748c388a977d^{commit}
test "$($trusted_git rev-parse \
  d3df4ceb140a9810b0d5219e0e9e748c388a977d^{tree})" = \
  208dc7e2f5981db9d6af2eac7a5455829e431c9e
$trusted_git merge-base --is-ancestor \
  148d590bd45ebcc5e4f2ac8a778c30d26d5f9f31 \
  d3df4ceb140a9810b0d5219e0e9e748c388a977d
test -z "$($trusted_git status --porcelain=v1 --untracked-files=no)"
```

If any check fails, return `BLOCKED_BY_MISSING_LOCAL_EVIDENCE`.  Do not use PR
#66, the sandbox spike, or recreated tests as a substitute.  Preserve every
existing worktree and untracked file.

## 6. Create one new linked worktree and reproduce genuine RED

Choose a new absent path and an unused implementation branch.  Create the
worktree at `d3df4ce…` with an ordinary non-force `git worktree add -b`.
Inspect ancestry to the current PR #66 branch before combining histories.  The
eventual implementation must descend from both histories so its diff against
the continuation branch contains only authorized local work.  Use an ordinary
merge if required; do not rebase or force.  Stop on a conflict outside the
allowlist.

Inspect the preserved commits and execute their exact narrow native and PyO3
RED selectors.  Do not invent selector names.  Retain command, environment,
compiler/Python/Cargo/maturin versions, source blobs, stdout/stderr, exit code,
and log SHA-256.  A valid RED fails on the intended missing telemetry/schema
assertion—not import, collection, linker, dependency, or unrelated compile
failure.

Before applying telemetry, reproduce separately on the authenticated baseline
the two cases described by `NONFINITE_RECEIPT_FINDING.md`.  Verify the five
preserved evidence hashes in `PACKAGE_MANIFEST.sha256`, but treat those files
only as diagnostic references.  Retain independent baseline logs for:

1. finite transport input producing nonfinite `log_bolometric_shift`;
2. finite Type-II state `[f64::MAX, 0, 0, 1, 0]` producing a nonfinite derived
   background.

## 7. Harden the validator, apply telemetry, and run LOCAL-01

Copy only these from the validated 18-file materialization:

```text
research/continuation_20260830/liouville_telemetry.patch
research/continuation_20260830/apply_telemetry.py
research/continuation_20260830/check_geometry_core.py
```

Make only the R5-authorized validator hardening: replace optimization-removable
Python `assert` gates with explicit exceptions, force internal Git reads to
ignore replacement objects, and prove the old mismatch is detected.  This is
validator hardening, not physics.

Run the genuine RED first, then the fail-closed applicator.  Require:

```text
old donor Git blob da6fade06f717ab938b0ec4c712ab239e78c998a
new donor Git blob e4d0f9c44fc26740d3a1cad6938b522fe514ae37
new donor SHA-256 ae38f315e84314ed7fef5360ac7f3a44c8f140c5d27d4ddb3a0a539bcef70cab
```

Run focused GREEN and the complete native/carrier/PyO3/serialization/failure
matrix in the controlling R5 handoff.  Check ordinary-corpus bit parity,
accepted intervals, callback fractions/order/count, `L=N_root+S`, independent
maximum depth, second-child and post-recursion failures, overflow disposition,
and no fabricated or partial receipt/history.

Re-run the two nonfinite cases on the exact candidate.  Every successful
receipt/background field must be finite.  A candidate may instead take an
existing authorized typed-failure path through the real carrier and PyO3
mapping.  Do not clamp, saturate, fabricate success, or invent a public error
variant/mapping.  If the exact telemetry donor remains invalid and the owner
authorizes repair, use a separate safety-boundary commit with its own RED/GREEN
and public-schema review.  Ambiguous authority is blocking.  Exactly these two
cases may differ from ordinary parity; no other waiver follows.

Run independent PHYS-MATH and PHYS-MATH-CODE audits on the actual diff and
repair only reproduced P0/P1 findings.  Any required `FAIL` or `UNTESTED`
item means LOCAL-01 failed and LOCAL-02 remains closed.  The claim is still
`NO_PASS_RF04`.

## 8. LOCAL-02 only after complete LOCAL-01

Bind source-owned `A` and `C` to the same carrier, grid, measure, frame, screen
bases, time/units, boundary/remap, and opacity/electron state.  Use a
nondegenerate frozen grid where both are nonzero and noncommuting; compare
native `(A+C)y` to an independently assembled dense oracle and require added-
`K`, index, omitted-measure, and screen-mismatch mutants to be detected.
Missing representation authority is a blocker.  Maximum claim:
`SCOPED_FROZEN_PHYSICAL_OPERATOR_PROOF`.

## 9. Delivery

Commit ordinary append-only changes in the new worktree.  Record exact
base/head/tree, changed-path allowlist, clean-state evidence, all raw logs and
hashes, machine acceptance receipt, and both independent audits.  Push one
stacked draft implementation PR against the RF-04 continuation branch only
after every LOCAL-01 gate passes.  Read back the remote head and CI, classifying
only what CI executed.  Do not merge or mark ready.  If LOCAL-01 is partial,
publish only an honest blocker/evidence update and do not start LOCAL-02.
