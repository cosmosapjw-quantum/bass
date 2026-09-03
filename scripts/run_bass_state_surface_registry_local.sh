#!/usr/bin/env bash

# BASS-only local replay for the SYNC-MAP-02F-R2 state-surface registry.
# Run in a subshell if the caller wants to guarantee the interactive shell survives.

set +e
set +u
set +o pipefail 2>/dev/null || true

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="${1:-$REPO_ROOT/artifacts/sync_map02f_r2_state_surface_registry}"
PYTHON_BIN="$(command -v python3 2>/dev/null)"
WOLFRAM_BIN="$(command -v wolframscript 2>/dev/null)"

if [ -z "$PYTHON_BIN" ] || [ ! -x "$PYTHON_BIN" ]; then
    printf 'FAIL: python3 executable unavailable\n' >&2
    exit 2
fi
if [ -z "$WOLFRAM_BIN" ] || [ ! -x "$WOLFRAM_BIN" ]; then
    printf 'FAIL: wolframscript executable unavailable\n' >&2
    exit 3
fi

rm -rf -- "$OUT_DIR"
mkdir -p -- "$OUT_DIR" || exit 4

REGISTRY="$REPO_ROOT/docs/bass_master_ssot_v2/SYNC_MAP_02F_R2/BASS_STATE_SURFACE_REGISTRY.json"
VERIFIER="$REPO_ROOT/scripts/verify_bass_state_surface_registry.py"

"$PYTHON_BIN" "$VERIFIER" --input "$REGISTRY"
VERIFY_RC=$?
if [ "$VERIFY_RC" -ne 0 ]; then
    printf 'FAIL: Python registry verifier rc=%s\n' "$VERIFY_RC" >&2
    exit "$VERIFY_RC"
fi

cd "$REPO_ROOT" || exit 5
"$PYTHON_BIN" -m unittest -v tests.test_bass_state_surface_registry
TEST_RC=$?
if [ "$TEST_RC" -ne 0 ]; then
    printf 'FAIL: Python registry tests rc=%s\n' "$TEST_RC" >&2
    exit "$TEST_RC"
fi

"$WOLFRAM_BIN" -file \
    "$REPO_ROOT/wolfram/scripts/run_bass_state_surface_registry.wls" \
    "$OUT_DIR"
WL_RC=$?
if [ "$WL_RC" -ne 0 ]; then
    printf 'FAIL: Wolfram registry replay rc=%s\n' "$WL_RC" >&2
    exit "$WL_RC"
fi

{
    printf '%s  %s\n' \
      "$(sha256sum "$REGISTRY" | awk '{print $1}')" \
      "docs/bass_master_ssot_v2/SYNC_MAP_02F_R2/BASS_STATE_SURFACE_REGISTRY.json"
    if [ -f "$OUT_DIR/SYNC_MAP_02F_R2_STATE_SURFACE_WOLFRAM_RECEIPT.json" ]; then
      printf '%s  %s\n' \
        "$(sha256sum "$OUT_DIR/SYNC_MAP_02F_R2_STATE_SURFACE_WOLFRAM_RECEIPT.json" | awk '{print $1}')" \
        "SYNC_MAP_02F_R2_STATE_SURFACE_WOLFRAM_RECEIPT.json"
    fi
} > "$OUT_DIR/SHA256SUMS"

printf 'BASS-only state-surface registry validation PASS\n'
printf 'artifacts: %s\n' "$OUT_DIR"
exit 0
