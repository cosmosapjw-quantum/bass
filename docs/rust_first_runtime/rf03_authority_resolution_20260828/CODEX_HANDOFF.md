# Codex Bootstrap — RF-03 Authority Resolution R2

Use the canonical direct-text package only. The earlier multipart ZIP objects in
this directory are deprecated transport artifacts and are not authority for
execution or byte identity.

```text
repository:       cosmosapjw-quantum/bass
package branch:   agent/plans/rf03-authority-resolution-20260828-r2
package path:     docs/rust_first_runtime/rf03_authority_resolution_20260828/direct
source base:      dfa17457d402bd441d3fdf786c2d79c529512ee5
source tree:      9fc67fb0ba10e091e25a14d7e1fac88b77a0241e
implementation:   agent/architecture/rust-first-rf03-20260828-r2
next action:      RF03-AUTH-01
claim now:        NO PASS_RF03 CLAIM
```

Run:

```bash
set -euo pipefail

git fetch origin
REPO_ROOT="$(git rev-parse --show-toplevel)"
PKG_REF="origin/agent/plans/rf03-authority-resolution-20260828-r2"
PKG_PATH="docs/rust_first_runtime/rf03_authority_resolution_20260828/direct"
BASE_REF="origin/agent/architecture/rust-first-rf02c-20260826-r1"
EXPECTED_BASE="dfa17457d402bd441d3fdf786c2d79c529512ee5"
EXPECTED_TREE="9fc67fb0ba10e091e25a14d7e1fac88b77a0241e"
TMP="$(mktemp -d)"

trap 'rm -rf "$TMP"' EXIT

test "$(git rev-parse "$BASE_REF")" = "$EXPECTED_BASE"
test "$(git rev-parse "${EXPECTED_BASE}^{tree}")" = "$EXPECTED_TREE"

for f in README.md AUTHORITY_CONTRACT.json WORK_UNITS.json CODEX_HANDOFF.md validate_package.py MANIFEST.sha256; do
  git show "$PKG_REF:$PKG_PATH/$f" > "$TMP/$f"
done

(
  cd "$TMP"
  sha256sum -c MANIFEST.sha256
  python validate_package.py
  python validate_package.py --live --repo "$REPO_ROOT"
)

cat "$TMP/CODEX_HANDOFF.md"
```

After reading the internal handoff, execute it in this same Codex session. Keep
PR #36, PR #37, and this package PR draft/unmerged. Do not use the deprecated
multipart files, BASS-12–15 optimization bytes, or any invented tilted-temperature formula.
