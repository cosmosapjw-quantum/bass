#!/usr/bin/env bash
set -euo pipefail
UNIT="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$UNIT/../.." && pwd)"
SOURCE="$REPO/research/bass_rei_f08_native_hhe_firststage_20261101/original_rei_rust"
OUT="$UNIT/replay_results"
if test "$#" -ge 1; then OUT="$1"; fi
STEPS=160
if test "$#" -ge 2; then STEPS="$2"; fi
if [[ ! "$STEPS" =~ ^[0-9]+$ ]] || (( STEPS < 1 || STEPS > 160 )); then
  echo "STEPS must be integer in 1..160" >&2; exit 2
fi
(cd "$SOURCE" && sha256sum -c original_source_sha256.txt >/dev/null)
test "$(sha256sum "$SOURCE/src/paired_runtime.rs" | cut -d' ' -f1)" = b6c1d2a07ab51ff02318139ae18387b77f61859c08037347f788524df770ebe7
test "$(sha256sum "$SOURCE/src/coupled_primary.rs" | cut -d' ' -f1)" = 915d0a898100a54d04a525227e7fbeb870e321fcc14aaa91afd61352b6d4cf4b
WORK="$(mktemp -d /tmp/bass_f08_paired_replay.XXXXXXXX)"
trap 'rm -rf "$WORK"' EXIT
cp -a "$SOURCE" "$WORK/rei_microphysics"
printf '\npub mod paired_runtime;\n' >> "$WORK/rei_microphysics/src/bass_scoped_lib.rs"
cp "$UNIT/bass_f08_consecutive_physical_support.rs" "$WORK/rei_microphysics/examples/bass_f08_consecutive_physical_support.rs"
test "$(sha256sum "$SOURCE/src/paired_runtime.rs" | cut -d' ' -f1)" = "$(sha256sum "$WORK/rei_microphysics/src/paired_runtime.rs" | cut -d' ' -f1)"
test "$(sha256sum "$SOURCE/src/coupled_primary.rs" | cut -d' ' -f1)" = "$(sha256sum "$WORK/rei_microphysics/src/coupled_primary.rs" | cut -d' ' -f1)"
(cd "$WORK/rei_microphysics" && CARGO_TARGET_DIR="$WORK/target" cargo build --release --offline --example bass_f08_consecutive_physical_support)
mkdir -p "$OUT"
"$WORK/target/release/examples/bass_f08_consecutive_physical_support" "$OUT" "$STEPS"
echo "NATIVE_PAIRED_REPLAY_DONE $OUT"
