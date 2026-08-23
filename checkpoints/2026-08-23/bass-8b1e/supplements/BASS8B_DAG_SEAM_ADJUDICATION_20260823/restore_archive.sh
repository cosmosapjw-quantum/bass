#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
name='BASS8B_DAG_SEAM_ADJUDICATION_20260823.zip'
parts="archive/${name}.parts"
out="${1:-$name}"
(
  cd "$parts"
  sha256sum -c ../PARTS.sha256
)
cat "$parts"/part-* > "$out"
actual=$(sha256sum "$out" | awk '{print $1}')
expected='beb0b30f22e3a7bd601a3e24ea57e45258cfaeb57fe633794513bac7a0ad2b8f'
[[ "$actual" == "$expected" ]] || { echo "SHA-256 mismatch: $actual" >&2; exit 1; }
unzip -t "$out"
echo "RESTORE_OK $out $actual"
