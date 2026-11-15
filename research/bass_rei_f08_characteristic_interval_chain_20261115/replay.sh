#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
BASS="$(cd "$ROOT/../.." && pwd)"
ORIGINAL="$BASS/research/bass_rei_f08_native_hhe_firststage_20261101/original_rei_rust"
STEPS=8
if test "$#" -ge 1; then STEPS="$1"; fi
OUT="$ROOT/results"
if test "$#" -ge 2; then OUT="$2"; fi
case "$STEPS" in ''|*[!0-9]*) echo "BAD_STEPS" >&2; exit 2;; esac
test "$STEPS" -ge 1 && test "$STEPS" -le 160
(cd "$ORIGINAL"; sha256sum -c original_source_sha256.txt >/dev/null)
test "$(sha256sum "$ORIGINAL/src/coupled_primary.rs" | cut -d' ' -f1)" = 915d0a898100a54d04a525227e7fbeb870e321fcc14aaa91afd61352b6d4cf4b
SCRATCH="$(mktemp -d /tmp/bass_f08_char_chain.XXXXXXXX)"
trap 'rm -rf "$SCRATCH"' EXIT
cp -a "$ORIGINAL" "$SCRATCH/rei_microphysics"
cp "$ROOT/bass_f08_characteristic_interval_root.rs" "$SCRATCH/rei_microphysics/examples/bass_f08_characteristic_interval_root.rs"
(cd "$SCRATCH/rei_microphysics"; CARGO_TARGET_DIR="$SCRATCH/target" cargo build --release --offline --example bass_f08_characteristic_interval_root)
python3 "$ROOT/characteristic_interval_chain.py" --steps "$STEPS" --rust-exe "$SCRATCH/target/release/examples/bass_f08_characteristic_interval_root" --out "$OUT"
