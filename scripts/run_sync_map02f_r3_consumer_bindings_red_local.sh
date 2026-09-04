#!/usr/bin/env bash

# Expected-RED runner for SYNC-MAP-02F-R3 consumer-binding contracts.
# This script does not use `set -e`; all failures are classified explicitly.

set +e
set +u
set +o pipefail 2>/dev/null || true

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." 2>/dev/null && pwd)"
if [ -z "$ROOT" ] || [ ! -d "$ROOT/.git" ]; then
    printf 'ERROR: repository root could not be resolved\n' >&2
    exit 2
fi

OUT="${1:-$ROOT/artifacts/sync_map02f_r3_consumer_bindings_red}"
LOG="$OUT/SYNC_MAP_02F_R3_CONSUMER_BINDING_RED_TEST.log"
RECEIPT="$OUT/SYNC_MAP_02F_R3_CONSUMER_BINDING_EXPECTED_RED_RECEIPT.json"
MANIFEST="$OUT/SHA256SUMS"
TEST="$ROOT/tests/test_sync_map02f_r3_consumer_bindings.py"
WORKFLOW="$ROOT/.github/workflows/sync-map02f-r3-consumer-bindings.yml"
DESIGN="$ROOT/docs/bass_master_ssot_v2/SYNC_MAP_02F_R3/CONSUMER_BINDING_CONTRACT_DESIGN.md"

PYTHON_BIN="$(command -v python3 2>/dev/null)"
if [ -z "$PYTHON_BIN" ] || [ ! -x "$PYTHON_BIN" ]; then
    printf 'ERROR: python3 executable not found\n' >&2
    exit 3
fi

for REQUIRED in "$TEST" "$WORKFLOW" "$DESIGN"; do
    if [ ! -f "$REQUIRED" ]; then
        printf 'ERROR: required RED input missing: %s\n' "$REQUIRED" >&2
        exit 4
    fi
done

TRACKED_DIRTY="$(git -C "$ROOT" status --porcelain --untracked-files=no 2>/dev/null)"
if [ -n "$TRACKED_DIRTY" ]; then
    printf 'STOP: tracked worktree changes exist\n' >&2
    git -C "$ROOT" status --short || true
    exit 5
fi

rm -rf -- "$OUT"
mkdir -p -- "$OUT" || {
    printf 'ERROR: could not create output directory: %s\n' "$OUT" >&2
    exit 6
}

HEAD="$(git -C "$ROOT" rev-parse HEAD 2>/dev/null)"
TREE="$(git -C "$ROOT" show -s --format=%T HEAD 2>/dev/null)"
BRANCH="$(git -C "$ROOT" branch --show-current 2>/dev/null)"
TEST_BLOB="$(git -C "$ROOT" rev-parse HEAD:tests/test_sync_map02f_r3_consumer_bindings.py 2>/dev/null)"
WORKFLOW_BLOB="$(git -C "$ROOT" rev-parse HEAD:.github/workflows/sync-map02f-r3-consumer-bindings.yml 2>/dev/null)"
DESIGN_BLOB="$(git -C "$ROOT" rev-parse HEAD:docs/bass_master_ssot_v2/SYNC_MAP_02F_R3/CONSUMER_BINDING_CONTRACT_DESIGN.md 2>/dev/null)"

printf '===== SYNC-MAP-02F-R3 EXPECTED RED =====\n'
printf 'branch: %s\n' "$BRANCH"
printf 'HEAD:   %s\n' "$HEAD"
printf 'tree:   %s\n' "$TREE"
printf 'python: %s\n' "$PYTHON_BIN"

(
    cd "$ROOT" || exit 90
    "$PYTHON_BIN" -m unittest -v tests.test_sync_map02f_r3_consumer_bindings
) >"$LOG" 2>&1
RAW_RC=$?

cat "$LOG"

MISSING_MARKER=false
FAILURE_SUMMARY=false
ERROR_MARKER=false
ENVIRONMENT_MARKER=false

if grep -Fq 'consumer-binding graph missing:' "$LOG"; then
    MISSING_MARKER=true
fi
if grep -Fq 'FAILED (failures=12)' "$LOG"; then
    FAILURE_SUMMARY=true
fi
if grep -Eq '^ERROR:|FAILED \(errors=|errors=[1-9]' "$LOG"; then
    ERROR_MARKER=true
fi
if grep -Eq 'ModuleNotFoundError|SyntaxError|PermissionError|Traceback \(most recent call last\).*No such file' "$LOG"; then
    ENVIRONMENT_MARKER=true
fi

STATUS='FAIL_UNEXPECTED_RED_RESULT'
WRAPPER_RC=30
if [ "$RAW_RC" -eq 1 ] \
   && [ "$MISSING_MARKER" = true ] \
   && [ "$FAILURE_SUMMARY" = true ] \
   && [ "$ERROR_MARKER" = false ] \
   && [ "$ENVIRONMENT_MARKER" = false ]; then
    STATUS='PASS_EXPECTED_RED'
    WRAPPER_RC=0
fi

LOG_SHA256="$(sha256sum "$LOG" | awk '{print $1}')"

"$PYTHON_BIN" - \
    "$RECEIPT" \
    "$HEAD" \
    "$TREE" \
    "$BRANCH" \
    "$TEST_BLOB" \
    "$WORKFLOW_BLOB" \
    "$DESIGN_BLOB" \
    "$RAW_RC" \
    "$STATUS" \
    "$MISSING_MARKER" \
    "$FAILURE_SUMMARY" \
    "$ERROR_MARKER" \
    "$ENVIRONMENT_MARKER" \
    "$LOG_SHA256" <<'PY'
from __future__ import annotations

import json
import sys
from pathlib import Path

(
    receipt_path,
    head,
    tree,
    branch,
    test_blob,
    workflow_blob,
    design_blob,
    raw_rc,
    status,
    missing_marker,
    failure_summary,
    error_marker,
    environment_marker,
    log_sha256,
) = sys.argv[1:]

receipt = {
    "schema_version": "1.0.0",
    "stage_id": "SYNC_MAP_02F_R3_CONSUMER_BINDING_EXPECTED_RED",
    "repository_scope": "BASS_ONLY",
    "git_branch": branch,
    "git_head": head,
    "git_tree": tree,
    "tracked_worktree_clean": True,
    "test_blob": test_blob,
    "workflow_blob": workflow_blob,
    "design_blob": design_blob,
    "raw_unittest_exit_code": int(raw_rc),
    "expected_test_methods": 12,
    "expected_failure_count": 12,
    "expected_error_count": 0,
    "missing_contract_surface_marker": missing_marker == "true",
    "exact_failure_summary_marker": failure_summary == "true",
    "unexpected_error_marker": error_marker == "true",
    "unexpected_environment_marker": environment_marker == "true",
    "test_log_sha256": log_sha256,
    "production_contract_present": False,
    "consumer_source_mutation": False,
    "runtime_parity_effect": "NONE",
    "status": status,
}
Path(receipt_path).write_text(
    json.dumps(receipt, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
PY
RECEIPT_RC=$?

if [ "$RECEIPT_RC" -ne 0 ] || [ ! -s "$RECEIPT" ]; then
    printf 'ERROR: RED receipt write failed\n' >&2
    exit 31
fi

sha256sum \
    "$TEST" \
    "$WORKFLOW" \
    "$DESIGN" \
    "$LOG" \
    "$RECEIPT" \
    > "$MANIFEST"
MANIFEST_WRITE_RC=$?
if [ "$MANIFEST_WRITE_RC" -ne 0 ] || [ ! -s "$MANIFEST" ]; then
    printf 'ERROR: RED SHA256SUMS write failed\n' >&2
    exit 32
fi

sha256sum -c "$MANIFEST"
MANIFEST_CHECK_RC=$?
if [ "$MANIFEST_CHECK_RC" -ne 0 ]; then
    printf 'ERROR: RED SHA256SUMS verification failed\n' >&2
    exit 33
fi

printf '\n===== RED RECEIPT =====\n'
"$PYTHON_BIN" -m json.tool "$RECEIPT" 2>/dev/null || cat "$RECEIPT"
printf '\n===== RESULT =====\n'
printf 'raw unittest exit code: %s\n' "$RAW_RC"
printf 'wrapper status:         %s\n' "$STATUS"
printf 'wrapper exit code:      %s\n' "$WRAPPER_RC"
printf 'artifacts:              %s\n' "$OUT"

exit "$WRAPPER_RC"
