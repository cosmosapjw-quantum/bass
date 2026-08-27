#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
TARGET="${1:-$ROOT/materialized}"
test ! -e "$TARGET" || { echo "STOP: target exists: $TARGET" >&2; exit 1; }
TMP="$(mktemp -d /tmp/bass12-retry-unpack.XXXXXX)"
trap 'rm -rf "$TMP"' EXIT

(
  cd "$ROOT/archive"
  sha256sum -c PARTS.sha256
)

cat \
  "$ROOT/archive/BASS12_QUIET_HOST_RETRY_HANDOFF_20260828.zip.part000" \
  "$ROOT/archive/BASS12_QUIET_HOST_RETRY_HANDOFF_20260828.zip.part001" \
  "$ROOT/archive/BASS12_QUIET_HOST_RETRY_HANDOFF_20260828.zip.part002" \
  "$ROOT/archive/BASS12_QUIET_HOST_RETRY_HANDOFF_20260828.zip.part003.sub00" \
  "$ROOT/archive/BASS12_QUIET_HOST_RETRY_HANDOFF_20260828.zip.part003.sub01" \
  "$ROOT/archive/BASS12_QUIET_HOST_RETRY_HANDOFF_20260828.zip.part004" \
  > "$TMP/BASS12_QUIET_HOST_RETRY_HANDOFF_20260828.zip"

EXPECTED="$(awk 'NR==1 {print $1}' "$ROOT/BASS12_QUIET_HOST_RETRY_HANDOFF_20260828.zip.sha256")"
ACTUAL="$(sha256sum "$TMP/BASS12_QUIET_HOST_RETRY_HANDOFF_20260828.zip" | awk '{print $1}')"
test "$ACTUAL" = "$EXPECTED" || {
  echo "STOP: reconstructed ZIP SHA-256 mismatch" >&2
  echo "expected=$EXPECTED" >&2
  echo "actual=$ACTUAL" >&2
  exit 1
}

mkdir -p "$TARGET"
unzip -q "$TMP/BASS12_QUIET_HOST_RETRY_HANDOFF_20260828.zip" -d "$TARGET"
PKG="$TARGET/BASS12_QUIET_HOST_RETRY_HANDOFF_20260828"
cd "$PKG"
sha256sum -c MANIFEST.sha256
PYTHONDONTWRITEBYTECODE=1 python3 scripts/verify_package.py .
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_package -v
printf '%s\n' PASS_BASS12_QUIET_HOST_RETRY_GITHUB_PACKAGE
