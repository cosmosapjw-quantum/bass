#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT/archive"
sha256sum -c PARTS.sha256
cat BASS8B2B3_FRESH_CONTENT_REPRODUCTION_20260825.tar.xz.part* > BASS8B2B3_FRESH_CONTENT_REPRODUCTION_20260825.tar.xz
sha256sum -c BASS8B2B3_FRESH_CONTENT_REPRODUCTION_20260825.tar.xz.sha256
rm -rf restored
mkdir restored
tar -xJf BASS8B2B3_FRESH_CONTENT_REPRODUCTION_20260825.tar.xz -C restored
cd restored/BASS8B2B3_FRESH_CONTENT_REPRODUCTION_20260825
sha256sum -c CONTENT_MANIFEST.sha256
python verify_content_identity.py
printf '%s\n' BASS8B2B3_FRESH_REMOTE_CONTENT_RESTORE_PASS
