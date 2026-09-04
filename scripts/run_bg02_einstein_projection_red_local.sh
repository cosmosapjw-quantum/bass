#!/usr/bin/env bash

# Expected-RED runner for the BASS-only BG-02 Einstein projection implementation.
# Success means exactly 18 tests ran, 2 passed, 16 failed, 0 errored, and the
# failures are caused by the intentionally absent production module/registry.

set +e
set +u
set +o pipefail 2>/dev/null || true

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." 2>/dev/null && pwd)"
if [ -z "$ROOT" ]; then
    printf 'ERROR: repository root could not be resolved\n' >&2
    exit 2
fi

OUT="${1:-$ROOT/artifacts/bg02_einstein_projection_red}"
TEST="$ROOT/tests/test_bg02_einstein_projection_implementation.py"
CONTRACT="$ROOT/docs/bass_master_ssot_v2/BG_02_IMPLEMENTATION/BG_02_IMPLEMENTATION_RED_CONTRACT.json"
PLAN="$ROOT/docs/superpowers/plans/2026-09-04-bg02-einstein-projection-implementation.md"
LOG="$OUT/BG_02_IMPLEMENTATION_RED_TEST.log"
RECEIPT="$OUT/BG_02_IMPLEMENTATION_EXPECTED_RED_RECEIPT.json"
MANIFEST="$OUT/SHA256SUMS"

EXPECTED_HEAD='80d271cc528e1a0ffa813ecd3e3fb7610f3fa755'
EXPECTED_TREE='3fd8818938eaa0988988c6927cff799455a7a31d'

PYTHON_BIN="$(command -v python3 2>/dev/null)"
if [ -z "$PYTHON_BIN" ] || [ ! -x "$PYTHON_BIN" ]; then
    printf 'ERROR: python3 executable not found\n' >&2
    exit 3
fi

for REQUIRED in "$TEST" "$CONTRACT" "$PLAN"; do
    if [ ! -s "$REQUIRED" ]; then
        printf 'ERROR: expected RED input missing: %s\n' "$REQUIRED" >&2
        exit 4
    fi
done

if git -C "$ROOT" rev-parse --git-dir >/dev/null 2>&1; then
    HEAD="$(git -C "$ROOT" rev-parse HEAD 2>/dev/null)"
    TREE="$(git -C "$ROOT" show -s --format=%T HEAD 2>/dev/null)"
    BRANCH="$(git -C "$ROOT" branch --show-current 2>/dev/null)"
    TRACKED_DIRTY="$(
        git -C "$ROOT" status --porcelain --untracked-files=no 2>/dev/null
    )"
    if [ -n "$TRACKED_DIRTY" ]; then
        printf 'STOP: tracked worktree changes exist\n' >&2
        git -C "$ROOT" status --short || true
        exit 5
    fi
    TRACKED_CLEAN=true
    if git -C "$ROOT" merge-base --is-ancestor         "$EXPECTED_HEAD" "$HEAD" 2>/dev/null; then
        PARENT_ANCESTRY_PASS=true
    else
        PARENT_ANCESTRY_PASS=false
    fi
else
    HEAD="${BG02_EXPECTED_HEAD:-$EXPECTED_HEAD}"
    TREE="${BG02_EXPECTED_TREE:-$EXPECTED_TREE}"
    BRANCH="${BG02_EXPECTED_BRANCH:-SOURCE_PACKET_VALIDATION}"
    TRACKED_CLEAN=true
    if [ "$HEAD" = "$EXPECTED_HEAD" ] && [ "$TREE" = "$EXPECTED_TREE" ]; then
        PARENT_ANCESTRY_PASS=true
    else
        PARENT_ANCESTRY_PASS=false
    fi
fi

rm -rf -- "$OUT"
mkdir -p -- "$OUT" || exit 6

printf '===== BG-02 EINSTEIN PROJECTION EXPECTED RED =====\n'
printf 'branch: %s\n' "$BRANCH"
printf 'HEAD:   %s\n' "$HEAD"
printf 'tree:   %s\n' "$TREE"
printf 'python: %s\n' "$PYTHON_BIN"

(
    cd "$ROOT" || exit 90
    "$PYTHON_BIN" -S -m unittest -v \
        tests.test_bg02_einstein_projection_implementation
) >"$LOG" 2>&1
RAW_RC=$?

cat "$LOG"

METHOD_COUNT="$(
    "$PYTHON_BIN" -S - "$TEST" <<'PY'
from __future__ import annotations
import ast
import sys
from pathlib import Path

tree = ast.parse(Path(sys.argv[1]).read_text(encoding="utf-8"))
print(sum(
    1
    for node in ast.walk(tree)
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    and node.name.startswith("test_")
))
PY
)"

FAILURES="$(
    "$PYTHON_BIN" -S - "$LOG" <<'PY'
from __future__ import annotations
import re
import sys
from pathlib import Path

text = Path(sys.argv[1]).read_text(encoding="utf-8", errors="replace")
match = re.search(r"FAILED \(failures=(\d+)\)", text)
print(match.group(1) if match else "-1")
PY
)"

ERRORS="$(
    "$PYTHON_BIN" -S - "$LOG" <<'PY'
from __future__ import annotations
import re
import sys
from pathlib import Path

text = Path(sys.argv[1]).read_text(encoding="utf-8", errors="replace")
summary = re.search(r"FAILED \(([^)]*)\)", text)
if not summary:
    print("-1")
else:
    match = re.search(r"errors=(\d+)", summary.group(1))
    print(match.group(1) if match else "0")
PY
)"

PASSES=$((METHOD_COUNT - FAILURES - ERRORS))

MISSING_MODULE=false
MISSING_REGISTRY=false
UNEXPECTED_ENVIRONMENT=false

grep -Fq 'BG02 production module missing:' "$LOG" &&
    MISSING_MODULE=true
grep -Fq 'BG02 implementation registry missing:' "$LOG" &&
    MISSING_REGISTRY=true

if grep -Eq \
    'ModuleNotFoundError|ImportError|SyntaxError|PermissionError|No such file or directory.*python|command not found|Traceback.*OSError' \
    "$LOG"; then
    UNEXPECTED_ENVIRONMENT=true
fi

printf 'scientific parent is ancestor: %s\n' "$PARENT_ANCESTRY_PASS"
printf 'expected RED identity policy: SCIENTIFIC_PARENT_IS_ANCESTOR\n'

STATUS='FAIL_UNEXPECTED_RED_RESULT'
WRAPPER_RC=1

if [ "$PARENT_ANCESTRY_PASS" = true ] \
   && [ "$RAW_RC" -eq 1 ] \
   && [ "$METHOD_COUNT" -eq 18 ] \
   && [ "$FAILURES" -eq 16 ] \
   && [ "$ERRORS" -eq 0 ] \
   && [ "$PASSES" -eq 2 ] \
   && [ "$MISSING_MODULE" = true ] \
   && [ "$MISSING_REGISTRY" = true ] \
   && [ "$UNEXPECTED_ENVIRONMENT" = false ]; then
    STATUS='PASS_EXPECTED_RED'
    WRAPPER_RC=0
fi

"$PYTHON_BIN" -S - \
    "$RECEIPT" "$STATUS" "$HEAD" "$TREE" "$BRANCH" \
    "$RAW_RC" "$METHOD_COUNT" "$PASSES" "$FAILURES" "$ERRORS" \
    "$MISSING_MODULE" "$MISSING_REGISTRY" "$UNEXPECTED_ENVIRONMENT" \
    "$TRACKED_CLEAN" "$PARENT_ANCESTRY_PASS" "$EXPECTED_HEAD" "$EXPECTED_TREE" \
    "$LOG" "$TEST" "$CONTRACT" "$PLAN" <<'PY'
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path

(
    receipt_raw,
    status,
    head,
    tree,
    branch,
    raw_rc,
    methods,
    passes,
    failures,
    errors,
    missing_module,
    missing_registry,
    unexpected_environment,
    tracked_clean,
    parent_ancestry_pass,
    scientific_parent_commit,
    scientific_parent_tree,
    log_raw,
    test_raw,
    contract_raw,
    plan_raw,
) = sys.argv[1:]

def boolean(value: str) -> bool:
    return value.lower() == "true"

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

receipt_path = Path(receipt_raw)
log_path = Path(log_raw)
test_path = Path(test_raw)
contract_path = Path(contract_raw)
plan_path = Path(plan_raw)

payload = {
    "schema_version": "1.0.0",
    "stage_id": "BG_02_GR_BACKGROUND_EINSTEIN_PROJECTION_IMPLEMENTATION_EXPECTED_RED",
    "repository_scope": "BASS_ONLY",
    "git_branch": branch,
    "git_head": head,
    "git_tree": tree,
    "raw_unittest_exit_code": int(raw_rc),
    "test_methods": int(methods),
    "tests_passed": int(passes),
    "tests_failed": int(failures),
    "tests_errored": int(errors),
    "missing_production_module_marker": boolean(missing_module),
    "missing_implementation_registry_marker": boolean(missing_registry),
    "unexpected_environment_marker": boolean(unexpected_environment),
    "tracked_worktree_clean": boolean(tracked_clean),
    "scientific_parent_commit": scientific_parent_commit,
    "scientific_parent_tree": scientific_parent_tree,
    "scientific_parent_is_ancestor": boolean(parent_ancestry_pass),
    "expected_red_identity_policy": "SCIENTIFIC_PARENT_IS_ANCESTOR",
    "test_sha256": sha(test_path),
    "red_contract_sha256": sha(contract_path),
    "implementation_plan_sha256": sha(plan_path),
    "test_log_sha256": sha(log_path),
    "production_module_present": False,
    "implementation_registry_present": False,
    "native_xact_replay_effect": "NONE",
    "claim_boundary": [
        "NO_BG02_PRODUCTION_IMPLEMENTATION",
        "NO_NATIVE_XACT_BG02_PASS",
        "NO_CONSTRAINT_PROPAGATION_CLAIM",
        "NO_BACKGROUND_NUMERICAL_EVOLUTION",
        "NO_PROVIDER_OR_SCIENCE_PROMOTION",
        "NO_PASS_RF04",
    ],
    "status": status,
}
receipt_path.write_text(
    json.dumps(payload, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
PY
if [ "$?" -ne 0 ]; then
    printf 'ERROR: expected RED receipt generation failed\n' >&2
    exit 7
fi

sha256sum \
    "$TEST" \
    "$CONTRACT" \
    "$PLAN" \
    "$LOG" \
    "$RECEIPT" \
    > "$MANIFEST"
MANIFEST_RC=$?

if [ "$MANIFEST_RC" -ne 0 ]; then
    printf 'ERROR: SHA256SUMS generation failed\n' >&2
    exit 8
fi

sha256sum -c "$MANIFEST"
CHECK_RC=$?
if [ "$CHECK_RC" -ne 0 ]; then
    printf 'ERROR: SHA256SUMS verification failed\n' >&2
    exit 9
fi

printf '\n===== RED RECEIPT =====\n'
"$PYTHON_BIN" -S -m json.tool "$RECEIPT" 2>/dev/null || cat "$RECEIPT"

printf '\n===== RESULT =====\n'
printf 'raw unittest exit code: %s\n' "$RAW_RC"
printf 'test methods:           %s\n' "$METHOD_COUNT"
printf 'passes/failures/errors: %s/%s/%s\n' \
    "$PASSES" "$FAILURES" "$ERRORS"
printf 'wrapper status:         %s\n' "$STATUS"
printf 'wrapper exit code:      %s\n' "$WRAPPER_RC"
printf 'artifacts:              %s\n' "$OUT"

exit "$WRAPPER_RC"
