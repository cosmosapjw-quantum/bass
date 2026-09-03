#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="${1:-${REPO_ROOT}/artifacts/sync_map02f_r2a_role_graph}"
mkdir -p "${OUT_DIR}"

GRAPH="${REPO_ROOT}/docs/bass_master_ssot_v2/SYNC_MAP_02F_R2A/FORMULA_CONSUMER_ROLE_GRAPH.json"
VERIFIER="${REPO_ROOT}/scripts/verify_sync_map02f_r2a_role_graph.py"
TEST="${REPO_ROOT}/tests/test_sync_map02f_r2a_role_graph.py"
WOLFRAM_RUNNER="${REPO_ROOT}/wolfram/scripts/run_formula_consumer_role_graph_r2a.wls"
WOLFRAM_RECEIPT="${OUT_DIR}/SYNC_MAP_02F_R2A_WOLFRAM_REPLAY_RECEIPT.json"
SUMMARY="${OUT_DIR}/SYNC_MAP_02F_R2A_LOCAL_VALIDATION_SUMMARY.json"

for command in python3 wolframscript git sha256sum; do
  if ! command -v "${command}" >/dev/null 2>&1; then
    printf 'missing required command: %s\n' "${command}" >&2
    exit 10
  fi
done

python3 "${VERIFIER}" --graph "${GRAPH}"
python3 -m unittest -v "${TEST}"

wolframscript -file "${WOLFRAM_RUNNER}" "${OUT_DIR}"

sha256sum \
  "${GRAPH}" \
  "${VERIFIER}" \
  "${TEST}" \
  "${REPO_ROOT}/wolfram/BASS/Kernel/IR/FormulaConsumerRoleGraphR2A.wl" \
  "${REPO_ROOT}/wolfram/BASS/Tests/FormulaConsumerRoleGraphR2A.wlt" \
  "${WOLFRAM_RUNNER}" \
  "${WOLFRAM_RECEIPT}" \
  > "${OUT_DIR}/SHA256SUMS"

python3 - "${REPO_ROOT}" "${GRAPH}" "${WOLFRAM_RECEIPT}" "${SUMMARY}" <<'PY'
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

repo = Path(sys.argv[1])
graph_path = Path(sys.argv[2])
receipt_path = Path(sys.argv[3])
summary_path = Path(sys.argv[4])

graph = json.loads(graph_path.read_text(encoding="utf-8"))
receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
head = subprocess.run(
    ["git", "-C", str(repo), "rev-parse", "HEAD"],
    check=True,
    capture_output=True,
    text=True,
).stdout.strip()

summary = {
    "schema_version": "1.0.0",
    "stage_id": "SYNC_MAP_02F_R2A_LOCAL_VALIDATION_SUMMARY",
    "repository_scope": "BASS_ONLY",
    "git_head": head,
    "formula_consumer_pair_count": len(graph["formula_consumer_pairs"]),
    "implementation_role_count": len(graph["implementation_roles"]),
    "named_source_symbol_count": sum(
        len(row["source_symbols"]) for row in graph["implementation_roles"]
    ),
    "absent_implementation_slot_count": sum(
        row["role_type"] == "ABSENT_IMPLEMENTATION_SLOT"
        for row in graph["implementation_roles"]
    ),
    "wolfram_status": receipt["status"],
    "expected_top_level_munit_tests": receipt["expected_top_level_munit_tests"],
    "tests_succeeded": receipt["tests_succeeded"],
    "tests_failed": receipt["tests_failed"],
    "tests_not_evaluated": receipt["tests_not_evaluated"],
    "sha256_manifest": "SHA256SUMS",
    "status": (
        "PASS_LOCAL_BASS_ONLY"
        if receipt["status"] == "PASS_LOCAL_EXACT_REPLAY"
        else "FAIL_LOCAL_BASS_ONLY"
    ),
}
summary_path.write_text(
    json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
if summary["status"] != "PASS_LOCAL_BASS_ONLY":
    raise SystemExit(1)
PY

printf 'BASS-only SYNC-MAP-02F-R2A role-graph validation PASS\n'
printf 'artifacts: %s\n' "${OUT_DIR}"
