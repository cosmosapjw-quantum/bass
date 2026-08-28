# Codex Handoff — RF-03 Exact R2 Direct-Package Rebind

```text
PROCESS_DRIFT_DETECTED
STOPPING META-WORK
RETURNING TO USER OBJECTIVE
```

## Task

Resume RF-03 from the exact R2 authority package. Do not use the historical R1
handoff and do not look for a ZIP, sidecar, or multipart archive.

```text
repository: cosmosapjw-quantum/bass

authority package branch:
agent/plans/rf03-authority-resolution-20260828-r2

authority package HEAD:
55335d3817a82da7e0f9bf24ef7632a2533645d3

authority package tree:
7c02689430d01abdf998c5b7ab1c5a6eb48859f4

authority package PR:
#39 OPEN / DRAFT / UNMERGED

canonical transport:
DIRECT_TEXT_FILES

package index:
docs/rust_first_runtime/rf03_authority_resolution_20260828/PACKAGE_INDEX.json

canonical direct package:
docs/rust_first_runtime/rf03_authority_resolution_20260828/direct

implementation base:
agent/architecture/rust-first-rf02c-20260826-r1
@ dfa17457d402bd441d3fdf786c2d79c529512ee5
tree 9fc67fb0ba10e091e25a14d7e1fac88b77a0241e

implementation branch:
agent/architecture/rust-first-rf03-20260828-r2

exact next action:
RF03-AUTH-01

claim:
NO PASS_RF03 CLAIM
```

## Preserve existing local state

The canonical root previously had no tracked/staged changes but had 41 unrelated
untracked entries. Preserve them. Preserve the prior blocker worktree and its
`SCHEMA_AND_ROUTE_FREEZE.json` if present.

Do not run `git clean`, `git reset`, `git stash`, branch switching in an occupied
worktree, rebase, amend, squash, or force-push.

Use a new isolated worktree for R2. Do not attempt to repair the historical R1
worktree in place.

## Materialize and validate the exact direct package

From an authenticated BASS clone:

```bash
set -euo pipefail

REPO="$(git rev-parse --show-toplevel)"
cd "$REPO"
git fetch origin

AUTH_REF="origin/agent/plans/rf03-authority-resolution-20260828-r2"
AUTH_HEAD="55335d3817a82da7e0f9bf24ef7632a2533645d3"
AUTH_TREE="7c02689430d01abdf998c5b7ab1c5a6eb48859f4"
PKG_ROOT="docs/rust_first_runtime/rf03_authority_resolution_20260828/direct"
PKG_INDEX="docs/rust_first_runtime/rf03_authority_resolution_20260828/PACKAGE_INDEX.json"

test "$(git rev-parse "$AUTH_REF")" = "$AUTH_HEAD"
test "$(git rev-parse "$AUTH_HEAD^{tree}")" = "$AUTH_TREE"

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

git show "$AUTH_HEAD:$PKG_INDEX" > "$TMP/PACKAGE_INDEX.json"

for f in README.md AUTHORITY_CONTRACT.json WORK_UNITS.json CODEX_HANDOFF.md \
         validate_package.py MANIFEST.sha256
do
  git show "$AUTH_HEAD:$PKG_ROOT/$f" > "$TMP/$f"
done

python - "$TMP" <<'PY'
from pathlib import Path
import hashlib, json, sys

root = Path(sys.argv[1])
index = json.loads((root / "PACKAGE_INDEX.json").read_text())
assert index["canonical_transport"] == "DIRECT_TEXT_FILES"
assert index["canonical_path"] == "docs/rust_first_runtime/rf03_authority_resolution_20260828/direct"
expected = {x["name"]: x["sha256"] for x in index["canonical_files"]}
for name, digest in expected.items():
    got = hashlib.sha256((root / name).read_bytes()).hexdigest()
    if got != digest:
        raise SystemExit(f"FAIL: {name} SHA-256 {got} != {digest}")
print("DIRECT_PACKAGE_INDEX_SHA256_PASS")
PY

(
  cd "$TMP"
  sha256sum -c MANIFEST.sha256
  python validate_package.py
  python validate_package.py --live --repo "$REPO"
)
```

Do not substitute a newer branch head. If the exact authority ref has moved,
stop and report the observed head; do not guess.

## Create or resume the isolated R2 implementation branch

First confirm that the base is unchanged:

```bash
BASE_REF="origin/agent/architecture/rust-first-rf02c-20260826-r1"
test "$(git rev-parse "$BASE_REF")" = "dfa17457d402bd441d3fdf786c2d79c529512ee5"
test "$(git rev-parse dfa17457d402bd441d3fdf786c2d79c529512ee5^{tree})" = "9fc67fb0ba10e091e25a14d7e1fac88b77a0241e"
```

If no local or remote R2 implementation branch exists:

```bash
WORKTREE="$(mktemp -d -p /tmp bass-rf03-r2-20260828.XXXXXX)/worktree"
git worktree add \
  -b agent/architecture/rust-first-rf03-20260828-r2 \
  "$WORKTREE" \
  dfa17457d402bd441d3fdf786c2d79c529512ee5
cd "$WORKTREE"
```

If it exists, continue only when it descends from the exact base and its dirty
paths are clearly RF-03 R2 work. Never discard unknown bytes.

## Execute local work only

Read the exact direct package in this order:

1. `AUTHORITY_CONTRACT.json`
2. `WORK_UNITS.json`
3. `CODEX_HANDOFF.md`
4. the historical R1 package only for unaffected implementation scope

Then execute:

```text
RF03-AUTH-01
→ authority verifier + focused authority test
→ PASS_RF03_AUTHORITY only if both pass
→ genuine RF-03 RED in the same run
→ RF-03 implementation
→ targeted parity/domain/determinism proof
→ four bounded figures and hostile mutations
→ PHYS-MATH then PHYS-MATH-CODE audit once
→ at most one reproduced P0/P1 repair
→ reproducible native wheel/delta/restore evidence
→ ordinary push and one draft RF-03 implementation PR
→ stop without merge or ready transition
```

Authority paths first:

```text
provenance/authority/rf03/RF03_AUTHORITY.json
tools/authority/verify_thermodynamics_authority.py
tests/rf03/test_authority_contract.py
artifacts/rust_first_runtime/rf03/authority/**
```

Do not invent a new EOS or a tilted-temperature formula. The selected production
model is the explicit source gamma-law model; `T_gamma` is exogenous and must
not affect its force/JVP. Historical Type-II thermodynamics remains
surrogate-reference-only.

Do not consume BASS-12 through BASS-15 optimization bytes, run timing/GPU/
Wolfram/full-suite reassurance, merge, or mark a PR ready.

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

`PASS_RF03_AUTHORITY` is not `PASS_RF03`. Claim `PASS_RF03` only after the full
implementation, targeted proof, native evidence, and exact remote readback.
