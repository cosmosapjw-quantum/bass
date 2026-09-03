#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="${1:-${REPO_ROOT}/artifacts/sync_map02e_r1_local_replay}"
mkdir -p "${OUT_DIR}"

PARENT="${REPO_ROOT}/docs/bass_master_ssot_v2/SYNC_MAP_02E/BASS_SHARED_FRAME_PHOTON_EXPORT.json"
GENERATED="${OUT_DIR}/BASS_SHARED_FRAME_PHOTON_EXPORT_R1.json"
BUILD_RECEIPT="${OUT_DIR}/SYNC_MAP_02E_R1_LOCAL_BUILD_RECEIPT.json"
WOLFRAM_RECEIPT="${OUT_DIR}/SYNC_MAP_02E_R1_LOCAL_WOLFRAM_REPLAY_RECEIPT.json"
SUMMARY="${OUT_DIR}/SYNC_MAP_02E_R1_LOCAL_VALIDATION_SUMMARY.json"

for command in python3 wolframscript git sha256sum; do
  if ! command -v "${command}" >/dev/null 2>&1; then
    printf 'missing required command: %s\n' "${command}" >&2
    exit 10
  fi
done

# Resolve Python once in the shell, where command discovery is authoritative,
# and pass the absolute executable path into Wolfram explicitly.  Wolfram
# Language 15.0.1 does not provide System`FindExecutable.
PYTHON_BIN="$(command -v python3)"
if [[ -z "${PYTHON_BIN}" || ! -e "${PYTHON_BIN}" ]]; then
  printf 'resolved python3 path is unusable: %s\n' "${PYTHON_BIN:-<empty>}" >&2
  exit 10
fi

"${PYTHON_BIN}" "${REPO_ROOT}/scripts/build_sync_map02e_r1_hardening.py" \
  --input "${PARENT}" \
  --output "${GENERATED}" \
  --receipt "${BUILD_RECEIPT}"

"${PYTHON_BIN}" "${REPO_ROOT}/scripts/verify_sync_map02e_r1_hardening.py" \
  --input "${GENERATED}" \
  --receipt "${BUILD_RECEIPT}"

"${PYTHON_BIN}" -m unittest -v \
  "${REPO_ROOT}/tests/test_sync_map02e_r1_semantic_hardening.py"

wolframscript -file \
  "${REPO_ROOT}/wolfram/scripts/run_sync_map02e_r1_local_replay.wls" \
  "${OUT_DIR}" "${PYTHON_BIN}"

SOURCE_PATHS=(
  "scripts/build_sync_map02e_r1_hardening.py"
  "scripts/verify_sync_map02e_r1_hardening.py"
  "scripts/run_sync_map02e_r1_local_validation.sh"
  "tests/test_sync_map02e_r1_semantic_hardening.py"
  "wolfram/BASS/Kernel/IR/SharedFramePhotonExportHardeningR1.wl"
  "wolfram/BASS/Kernel/IR/SharedFramePhotonExportHardeningR1Fix1.wl"
  "wolfram/BASS/Tests/SYNCMAP02ER1SharedFramePhotonHardening.wlt"
  "wolfram/scripts/run_sync_map02e_r1_local_replay.wls"
  "docs/bass_master_ssot_v2/SYNC_MAP_02E_R1/SEMANTIC_HARDENING_PATCH_CONTRACT.json"
  "docs/bass_master_ssot_v2/SYNC_MAP_02E_R1/LOCAL_REPLAY_README.md"
)

{
  for relative_path in "${SOURCE_PATHS[@]}"; do
    sha256sum "${REPO_ROOT}/${relative_path}"
  done
  sha256sum "${GENERATED}" "${BUILD_RECEIPT}" "${WOLFRAM_RECEIPT}"
} > "${OUT_DIR}/SHA256SUMS"

"${PYTHON_BIN}" - "${REPO_ROOT}" "${OUT_DIR}" "${SUMMARY}" <<'PY'
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

repo = Path(sys.argv[1])
out = Path(sys.argv[2])
summary_path = Path(sys.argv[3])
head = subprocess.run(
    ["git", "-C", str(repo), "rev-parse", "HEAD"],
    check=True,
    capture_output=True,
    text=True,
).stdout.strip()

build = json.loads(
    (out / "SYNC_MAP_02E_R1_LOCAL_BUILD_RECEIPT.json").read_text(
        encoding="utf-8"
    )
)
replay = json.loads(
    (out / "SYNC_MAP_02E_R1_LOCAL_WOLFRAM_REPLAY_RECEIPT.json").read_text(
        encoding="utf-8"
    )
)
summary = {
    "schema_version": "1.0.0",
    "stage_id": "SYNC_MAP_02E_R1_LOCAL_VALIDATION_SUMMARY",
    "repository_scope": "BASS_ONLY",
    "git_head": head,
    "build_status": build["status"],
    "wolfram_status": replay["status"],
    "python_executable": replay["python_executable"],
    "python_probe_exit_code": replay["python_probe_exit_code"],
    "formula_count": build["formula_count"],
    "registry_semantic_hash": build["output_registry_semantic_hash"],
    "expected_top_level_munit_tests": replay["expected_top_level_munit_tests"],
    "tests_succeeded": replay["tests_succeeded"],
    "tests_failed": replay["tests_failed"],
    "tests_not_evaluated": replay["tests_not_evaluated"],
    "sha256_manifest": "SHA256SUMS",
    "status": (
        "PASS_LOCAL_BASS_ONLY"
        if replay["status"] == "PASS_LOCAL_EXACT_REPLAY"
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

printf 'BASS-only SYNC-MAP-02E-R1 local validation PASS\n'
printf 'artifacts: %s\n' "${OUT_DIR}"
