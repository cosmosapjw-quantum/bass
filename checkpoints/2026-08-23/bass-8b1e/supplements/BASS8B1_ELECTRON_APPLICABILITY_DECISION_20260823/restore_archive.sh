#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
name='BASS8B1_ELECTRON_APPLICABILITY_DECISION_20260823.zip'
parts="archive/${name}.parts"
out="${1:-$name}"
(
  cd "$parts"
  sha256sum -c ../PARTS.sha256
)
cat "$parts"/part-* > "$out"
actual=$(sha256sum "$out" | awk '{print $1}')
expected='cbd1dc32971194de633aa03223d3a994e544621ba79805a3d58ed334fd276d1c'
[[ "$actual" == "$expected" ]] || { echo "SHA-256 mismatch: $actual" >&2; exit 1; }
unzip -t "$out"
echo "RESTORE_OK $out $actual"
