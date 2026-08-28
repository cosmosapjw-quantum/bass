# Codex Bootstrap — BASS RF-03 Authority Resolution R2

Reconstruct the durable multipart package, verify both checksum layers, validate
the internal manifest, then execute the internal `CODEX_HANDOFF.md`. Do not
implement from this bootstrap alone.

```text
repository:          cosmosapjw-quantum/bass
package branch:      agent/plans/rf03-authority-resolution-20260828-r2
package path:        docs/rust_first_runtime/rf03_authority_resolution_20260828
archive SHA-256:     8528ab1508755828c89192be4f6467d7cc13b84862373d3fabdccb2d345d2a3a
exact source base:   dfa17457d402bd441d3fdf786c2d79c529512ee5
source tree:         9fc67fb0ba10e091e25a14d7e1fac88b77a0241e
implementation:      agent/architecture/rust-first-rf03-20260828-r2
next action:         RF03-AUTH-01
claim now:           NO PASS_RF03 CLAIM
```

```bash
set -euo pipefail

git fetch origin
REPO_ROOT="$(git rev-parse --show-toplevel)"
PKG_REF="origin/agent/plans/rf03-authority-resolution-20260828-r2"
PKG_PATH="docs/rust_first_runtime/rf03_authority_resolution_20260828"
ARCHIVE="BASS_RF03_AUTHORITY_RESOLUTION_20260828_R2.zip"
PARTS=("BASS_RF03_AUTHORITY_RESOLUTION_20260828_R2.zip.part01" "BASS_RF03_AUTHORITY_RESOLUTION_20260828_R2.zip.part02" "BASS_RF03_AUTHORITY_RESOLUTION_20260828_R2.zip.part03" "BASS_RF03_AUTHORITY_RESOLUTION_20260828_R2.zip.part04" "BASS_RF03_AUTHORITY_RESOLUTION_20260828_R2.zip.part05")
PARTS_SIDECAR="BASS_RF03_AUTHORITY_RESOLUTION_20260828_R2.zip.parts.sha256"
ARCHIVE_SIDECAR="BASS_RF03_AUTHORITY_RESOLUTION_20260828_R2.zip.sha256"
DOWNLOAD_DIR="$(mktemp -d)"
EXTRACT_DIR="$(mktemp -d)"

for part in "${PARTS[@]}"; do
  git show "$PKG_REF:$PKG_PATH/$part" > "$DOWNLOAD_DIR/$part"
done
git show "$PKG_REF:$PKG_PATH/$PARTS_SIDECAR" > \
  "$DOWNLOAD_DIR/$PARTS_SIDECAR"
git show "$PKG_REF:$PKG_PATH/$ARCHIVE_SIDECAR" > \
  "$DOWNLOAD_DIR/$ARCHIVE_SIDECAR"

(
  cd "$DOWNLOAD_DIR"
  sha256sum -c "$PARTS_SIDECAR"
  cat "${PARTS[@]}" > "$ARCHIVE"
  sha256sum -c "$ARCHIVE_SIDECAR"
)

test "$(sha256sum "$DOWNLOAD_DIR/$ARCHIVE" | awk '{print $1}')" = \
  "8528ab1508755828c89192be4f6467d7cc13b84862373d3fabdccb2d345d2a3a"

unzip -q "$DOWNLOAD_DIR/$ARCHIVE" -d "$EXTRACT_DIR"
PKG_ROOT="$EXTRACT_DIR/BASS_RF03_AUTHORITY_RESOLUTION_20260828_R2"

(
  cd "$PKG_ROOT"
  sha256sum -c MANIFEST.sha256
  python validate_package.py
  python validate_package.py --live --repo "$REPO_ROOT"
)

cat "$PKG_ROOT/CODEX_HANDOFF.md"
```

After reading the internal handoff, execute it in this same Codex session.
The resolution binds the existing explicit gamma-law matter source, rejects
implicit constant-w/Python fallback, and deliberately authorizes no
tilted-temperature formula. Keep PR #36 and PR #37 draft/unmerged.
