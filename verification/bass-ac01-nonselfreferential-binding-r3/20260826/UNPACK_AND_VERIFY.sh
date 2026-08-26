#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
TARGET="${1:-$ROOT/materialized}"
test ! -e "$TARGET" || { echo "STOP: target exists: $TARGET" >&2; exit 1; }
cd "$ROOT"
sha256sum -c REMOTE_MANIFEST.sha256
(
  cd archive
  sha256sum -c PARTS.sha256
  cat BASS_AC01_NONSELFREFERENTIAL_BINDING_R3_20260826.zip.part* > ../BASS_AC01_NONSELFREFERENTIAL_BINDING_R3_20260826.zip
)
sha256sum -c BASS_AC01_NONSELFREFERENTIAL_BINDING_R3_20260826.zip.sha256
mkdir -p "$TARGET"
unzip -q BASS_AC01_NONSELFREFERENTIAL_BINDING_R3_20260826.zip -d "$TARGET"
rm -f BASS_AC01_NONSELFREFERENTIAL_BINDING_R3_20260826.zip
PKG="$TARGET/BASS_AC01_NONSELFREFERENTIAL_BINDING_R3_20260826"
cd "$PKG"
sha256sum -c MANIFEST.sha256
PYTHONDONTWRITEBYTECODE=1 python3 scripts/verify_successor_package.py .
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_successor_contract -v
printf '%s\n' PASS_AC01_NONSELFREFERENTIAL_BINDING_R3_MATERIALIZE
