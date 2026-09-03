#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="${1:-$ROOT/artifacts/sync_map02f_bounded_closeout}"
PYTHON_BIN="$(command -v python3)"
WOLFRAM_BIN="$(command -v wolframscript)"

GRAPH="$ROOT/docs/bass_master_ssot_v2/SYNC_MAP_02F_CLOSEOUT/BOUNDED_SEMANTIC_CLOSEOUT.json"
VERIFIER="$ROOT/scripts/verify_sync_map02f_bounded_closeout.py"
PYTHON_TEST="$ROOT/tests/test_sync_map02f_bounded_closeout.py"
WOLFRAM_MODULE="$ROOT/wolfram/BASS/Kernel/IR/BoundedSemanticCloseout.wl"
WOLFRAM_TEST="$ROOT/wolfram/BASS/Tests/BoundedSemanticCloseout.wlt"
WOLFRAM_RUNNER="$ROOT/wolfram/scripts/run_bounded_semantic_closeout.wls"
RECEIPT="$OUT/SYNC_MAP_02F_BOUNDED_CLOSEOUT_WOLFRAM_RECEIPT.json"
SUMMARY="$OUT/SYNC_MAP_02F_BOUNDED_CLOSEOUT_LOCAL_VALIDATION_SUMMARY.json"
MANIFEST="$OUT/SHA256SUMS"

mkdir -p "$OUT"
rm -f "$RECEIPT" "${RECEIPT}.tmp" "$SUMMARY" "$MANIFEST"

"$PYTHON_BIN" "$VERIFIER" --graph "$GRAPH"
(
  cd "$ROOT"
  "$PYTHON_BIN" -m unittest -v tests.test_sync_map02f_bounded_closeout
)

"$WOLFRAM_BIN" -file "$WOLFRAM_RUNNER" "$OUT"

test -s "$RECEIPT"
test ! -e "${RECEIPT}.tmp"

"$PYTHON_BIN" - "$GRAPH" "$RECEIPT" "$SUMMARY" "$ROOT" <<'PY'
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

graph_path = Path(sys.argv[1])
receipt_path = Path(sys.argv[2])
summary_path = Path(sys.argv[3])
root = Path(sys.argv[4])

graph = json.loads(graph_path.read_text(encoding="utf-8"))
receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
head = subprocess.run(
    ["git", "-C", str(root), "rev-parse", "HEAD"],
    check=True,
    capture_output=True,
    text=True,
).stdout.strip()

assert receipt["git_head"] == head
assert receipt["status"] == "PASS_LOCAL_EXACT_REPLAY"
assert receipt["validator_pass"] is True
assert receipt["expected_top_level_munit_tests"] == 17
assert receipt["tests_succeeded"] == 17
assert receipt["tests_failed"] == 0
assert receipt["tests_not_evaluated"] == 0
assert receipt["json_safe_probe_pass"] is True

residuals = receipt["exact_residuals"]
for key in (
    "upstream_stage_count_residual",
    "formula_count_residual",
    "state_surface_count_residual",
    "formula_consumer_pair_count_residual",
    "implementation_role_count_residual",
    "named_source_symbol_count_residual",
    "absent_slot_count_residual",
    "certificate_family_count_residual",
    "relation_certificate_count_residual",
    "exact_witness_count_residual",
    "blocked_promotion_count_residual",
):
    assert residuals[key] == 0, (key, residuals[key])

for key in (
    "stage_dag_acyclic",
    "upstream_identity_exact",
    "bounded_claims_exact",
    "promotion_firewall_exact",
    "consumer_binding_firewall_intact",
):
    assert residuals[key] is True, (key, residuals[key])

counts = graph["count_contract"]
summary = {
    "schema_version": "1.0.0",
    "stage_id": "SYNC_MAP_02F_BOUNDED_CLOSEOUT_LOCAL_VALIDATION_SUMMARY",
    "repository_scope": "BASS_ONLY",
    "git_head": head,
    "upstream_stage_count": counts["upstream_stage_rows"],
    "formula_count": counts["authority_formulas"],
    "state_surface_count": counts["state_surfaces"],
    "formula_consumer_pair_count": counts["formula_consumer_pairs"],
    "implementation_role_count": counts["implementation_role_rows"],
    "certificate_family_count": counts["certificate_families"],
    "relation_certificate_count": counts["relation_certificate_rows"],
    "blocked_promotion_count": counts["blocked_promotions"],
    "expected_python_unittest_methods": 10,
    "expected_top_level_munit_tests": 17,
    "tests_succeeded": receipt["tests_succeeded"],
    "tests_failed": receipt["tests_failed"],
    "tests_not_evaluated": receipt["tests_not_evaluated"],
    "wolfram_status": receipt["status"],
    "promotion_status": graph["promotion_status"],
    "sha256_manifest": "SHA256SUMS",
    "status": "PASS_LOCAL_BASS_ONLY_BOUNDED_CLOSEOUT",
}
summary_path.write_text(
    json.dumps(summary, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
print(json.dumps(summary, sort_keys=True))
PY

sha256sum \
  "$GRAPH" \
  "$VERIFIER" \
  "$PYTHON_TEST" \
  "$WOLFRAM_MODULE" \
  "$WOLFRAM_TEST" \
  "$WOLFRAM_RUNNER" \
  "$RECEIPT" \
  "$SUMMARY" \
  > "$MANIFEST"

sha256sum -c "$MANIFEST"

echo "BASS-only SYNC-MAP-02F bounded semantic closeout validation PASS"
echo "artifacts: $OUT"
