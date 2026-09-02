#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATRIX_PATH = ROOT / "docs/bass_master_ssot_v2/SYNC_MAP_02F/EXTERNAL_CAS_MATRIX.json"
MANDATORY_ENGINES = {"maxima", "form", "ginac", "symengine", "z3"}
EXPLORATORY_ENGINES = {"symbolica", "cadabra2", "reduce"}
ALLOWED_EXPLORATORY_STATUS = {"PASS", "EXPLORATORY_UNAVAILABLE_OR_EXECUTION_FAILED"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("receipt_root", type=Path)
    args = parser.parse_args()

    matrix = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
    contracts = {row["engine"]: row for row in matrix["engines"]}
    errors: list[str] = []
    if {name for name, row in contracts.items() if row["required_for_axis_closeout"]} != MANDATORY_ENGINES:
        errors.append("mandatory engine set drifted")
    if set(contracts) - MANDATORY_ENGINES != EXPLORATORY_ENGINES:
        errors.append("exploratory engine set drifted")

    receipts: dict[str, dict[str, object]] = {}
    for path in sorted(args.receipt_root.rglob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        engine = data.get("engine")
        if engine in contracts:
            if engine in receipts:
                errors.append(f"duplicate receipt for {engine}")
            receipts[str(engine)] = data

    for engine in sorted(MANDATORY_ENGINES):
        receipt = receipts.get(engine)
        if receipt is None:
            errors.append(f"missing mandatory receipt: {engine}")
            continue
        contract = contracts[engine]
        expected_identity_ids = set(contract["expected_identity_ids"])
        hostile_mutations = set(contract["hostile_mutations"])
        identity_results = receipt.get("identity_results", {})
        mutation_results = receipt.get("mutation_results", {})
        download_sha256 = receipt.get("download_sha256", {})
        if receipt.get("status") != "PASS":
            errors.append(f"mandatory engine did not pass: {engine}")
        if set(identity_results) != expected_identity_ids or not all(identity_results.values()):
            errors.append(f"identity contract failed: {engine}")
        if set(mutation_results) != hostile_mutations or not all(mutation_results.values()):
            errors.append(f"mutation contract failed: {engine}")
        if not isinstance(download_sha256, dict) or not download_sha256:
            errors.append(f"download SHA-256 evidence absent: {engine}")
        if not str(receipt.get("version", "")).strip():
            errors.append(f"version evidence absent: {engine}")
        if receipt.get("authority_effect") != "NONE":
            errors.append(f"external engine gained authority: {engine}")

    for engine in sorted(EXPLORATORY_ENGINES):
        receipt = receipts.get(engine)
        if receipt is None:
            errors.append(f"missing exploratory attempt receipt: {engine}")
            continue
        if receipt.get("status") not in ALLOWED_EXPLORATORY_STATUS:
            errors.append(f"invalid exploratory status: {engine}")
        if not isinstance(receipt.get("download_sha256"), dict):
            errors.append(f"exploratory download evidence malformed: {engine}")

    coverage = Counter()
    mutation_coverage = Counter()
    passing_families: set[str] = set()
    for engine, receipt in receipts.items():
        if receipt.get("status") != "PASS":
            continue
        passing_families.add(str(receipt.get("implementation_family")))
        for identity_id, passed in receipt.get("identity_results", {}).items():
            if passed:
                coverage[identity_id] += 1
        for mutation_id, passed in receipt.get("mutation_results", {}).items():
            if passed:
                mutation_coverage[mutation_id] += 1

    for identity_id, minimum in matrix["coverage_minimums"].items():
        if coverage[identity_id] < minimum:
            errors.append(
                f"independent coverage below minimum: {identity_id} "
                f"{coverage[identity_id]} < {minimum}"
            )
    for mutation_id in sorted({m for row in matrix["engines"] if row["required_for_axis_closeout"] for m in row["hostile_mutations"]}):
        if mutation_coverage[mutation_id] < 3:
            errors.append(f"hostile mutation coverage below three engines: {mutation_id}")
    if len(passing_families) < 5:
        errors.append("fewer than five independent implementation families passed")
    if matrix.get("authority_effect") != "NONE":
        errors.append("matrix authority effect is not NONE")
    if "NO_02F_SEMANTIC_CLOSEOUT" not in matrix.get("withheld_claims", []):
        errors.append("02F closeout claim was not withheld")

    result = {
        "status": "PASS_EXTERNAL_CAS_MATRIX" if not errors else "FAIL_EXTERNAL_CAS_MATRIX",
        "mandatory_engines": sorted(MANDATORY_ENGINES),
        "exploratory_engines": sorted(EXPLORATORY_ENGINES),
        "receipts_found": sorted(receipts),
        "identity_coverage": dict(sorted(coverage.items())),
        "mutation_coverage": dict(sorted(mutation_coverage.items())),
        "passing_implementation_families": sorted(passing_families),
        "errors": errors,
        "authority_effect": "NONE",
        "claim_effect": "INDEPENDENT_FORMULA_REGRESSION_ONLY",
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
