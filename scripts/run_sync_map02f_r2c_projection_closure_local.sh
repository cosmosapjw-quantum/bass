#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="${1:-${REPO_ROOT}/artifacts/sync_map02f_r2c_projection_closure}"
mkdir -p "${OUT_DIR}"

GRAPH="${REPO_ROOT}/docs/bass_master_ssot_v2/SYNC_MAP_02F_R2C/PROJECTION_CLOSURE_CERTIFICATE_GRAPH.json"
VERIFIER="${REPO_ROOT}/scripts/verify_sync_map02f_r2c_projection_closure.py"
TEST="${REPO_ROOT}/tests/test_sync_map02f_r2c_projection_closure.py"
WOLFRAM_MODULE="${REPO_ROOT}/wolfram/BASS/Kernel/IR/ProjectionClosureCertificateGraphR2C.wl"
WOLFRAM_TEST="${REPO_ROOT}/wolfram/BASS/Tests/ProjectionClosureCertificateGraphR2C.wlt"
WOLFRAM_RUNNER="${REPO_ROOT}/wolfram/scripts/run_projection_closure_certificate_graph_r2c.wls"
WOLFRAM_RECEIPT="${OUT_DIR}/SYNC_MAP_02F_R2C_WOLFRAM_REPLAY_RECEIPT.json"
SUMMARY="${OUT_DIR}/SYNC_MAP_02F_R2C_LOCAL_VALIDATION_SUMMARY.json"
MANIFEST="${OUT_DIR}/SHA256SUMS"

for command in python3 wolframscript git sha256sum; do
  if ! command -v "${command}" >/dev/null 2>&1; then
    printf 'missing required command: %s\n' "${command}" >&2
    exit 10
  fi
done

python3 "${VERIFIER}" --graph "${GRAPH}"
python3 -m unittest -v "${TEST}"

wolframscript -file "${WOLFRAM_RUNNER}" "${OUT_DIR}"

if [ ! -s "${WOLFRAM_RECEIPT}" ]; then
  printf 'Wolfram receipt absent or empty: %s\n' "${WOLFRAM_RECEIPT}" >&2
  exit 11
fi

sha256sum \
  "${GRAPH}" \
  "${VERIFIER}" \
  "${TEST}" \
  "${WOLFRAM_MODULE}" \
  "${WOLFRAM_TEST}" \
  "${WOLFRAM_RUNNER}" \
  "${WOLFRAM_RECEIPT}" \
  > "${MANIFEST}"

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
    "stage_id": "SYNC_MAP_02F_R2C_LOCAL_VALIDATION_SUMMARY",
    "repository_scope": "BASS_ONLY",
    "git_head": head,
    "certificate_family_count": len(graph["certificate_families"]),
    "relation_certificate_count": len(graph["relation_certificates"]),
    "exact_witness_count": len(graph["exact_witnesses"]),
    "blocked_promotion_count": len(graph["explicit_blocked_promotions"]),
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

printf 'BASS-only SYNC-MAP-02F-R2C projection/closure validation PASS\n'
printf 'artifacts: %s\n' "${OUT_DIR}"
