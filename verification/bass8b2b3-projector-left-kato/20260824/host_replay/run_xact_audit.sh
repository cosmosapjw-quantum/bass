#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ARCHIVE="${XACT_ARCHIVE:-/mnt/data/xAct_1.3.0.tgz}"
STAGE="${XACT_STAGE:-/mnt/data/xact_stage}"
EXPECTED='7a6c5f600868a3922668b020a15c0692f76574ff2a559808c62d460cef1b07be'

[[ -f "$ARCHIVE" ]] || { echo "missing xAct archive: $ARCHIVE" >&2; exit 2; }
printf '%s  %s\n' "$EXPECTED" "$ARCHIVE" | sha256sum -c -
mkdir -p "$STAGE"
if [[ ! -d "$STAGE/xAct" ]]; then
  tar -xzf "$ARCHIVE" -C "$STAGE"
fi
[[ -f "$STAGE/xAct/xTensor/xTensor.m" ]] || {
  echo "xTensor package not found under $STAGE/xAct" >&2
  exit 2
}

SCRIPT="$ROOT/source/xact_screen_projector_witness.wl"
if command -v wolframscript >/dev/null 2>&1; then
  wolframscript -file "$SCRIPT"
elif command -v WolframKernel >/dev/null 2>&1; then
  WolframKernel -script "$SCRIPT"
elif [[ -x /usr/local/Wolfram/WolframEngine/15.0/Executables/wolframscript ]]; then
  /usr/local/Wolfram/WolframEngine/15.0/Executables/wolframscript -file "$SCRIPT"
elif [[ -x /usr/local/Wolfram/WolframEngine/15.0/SystemFiles/Kernel/Binaries/Linux-x86-64/WolframKernel ]]; then
  /usr/local/Wolfram/WolframEngine/15.0/SystemFiles/Kernel/Binaries/Linux-x86-64/WolframKernel -script "$SCRIPT"
else
  echo "No local Wolfram CLI found. Use the sealed stateless plugin receipt instead." >&2
  exit 3
fi
