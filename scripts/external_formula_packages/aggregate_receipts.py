#!/usr/bin/env python3
"""Aggregate XCAS-01 package receipts without relabelling blockers as passes."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


EXPECTED_ATTEMPTS = {
    "einsteinpy",
    "OGRePy",
    "pytearcat",
    "cadabra2",
    "maxima",
    "reduce",
    "BowenPing/STensor",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    receipts: list[dict[str, Any]] = []
    parse_errors: list[dict[str, str]] = []
    for path in sorted(args.input.rglob("*.json")):
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(value, dict) and "package" in value and "status" in value:
                value["receipt_path"] = str(path.relative_to(args.input))
                receipts.append(value)
        except Exception as exc:
            parse_errors.append({"path": str(path), "error": str(exc)})

    package_names = {str(item.get("package")) for item in receipts}
    missing = sorted(EXPECTED_ATTEMPTS - package_names)
    statuses = Counter(str(item.get("status")) for item in receipts)
    axes = Counter(str(item.get("package_axis", "UNCLASSIFIED")) for item in receipts)

    formula_failures = [
        item for item in receipts if item.get("status") == "FAIL_FORMULA"
    ]
    independent_cas_pass = any(
        item.get("status") == "PASS"
        and item.get("package_axis") in {
            "INDEPENDENT_TENSOR_CAS",
            "INDEPENDENT_SCALAR_CAS",
        }
        for item in receipts
    )
    independent_package_pass = any(
        item.get("status") == "PASS"
        and item.get("package_axis") in {
            "INDEPENDENT_GR_PACKAGE_SHARED_SYMPY_ENGINE",
            "INDEPENDENT_GR_PACKAGE_GIAC_ENGINE",
            "INDEPENDENT_TENSOR_PACKAGE_SHARED_WOLFRAM_KERNEL",
        }
        for item in receipts
    )

    if parse_errors or formula_failures:
        overall = "FAIL_FORMULA_OR_RECEIPT"
    elif missing:
        overall = "PARTIAL_MISSING_ATTEMPTS"
    elif independent_cas_pass and independent_package_pass:
        overall = "PASS_BOUNDED_WITH_PRESERVED_BLOCKERS"
    else:
        overall = "PARTIAL_INSUFFICIENT_INDEPENDENCE"

    aggregate = {
        "schema_version": "1.0.0",
        "stage_id": "XCAS_01_EXTERNAL_FORMULA_PACKAGE_VERIFICATION",
        "status": overall,
        "authority_effect": "NONE",
        "expected_attempt_count": len(EXPECTED_ATTEMPTS),
        "observed_attempt_count": len(package_names),
        "missing_attempts": missing,
        "status_counts": dict(sorted(statuses.items())),
        "axis_counts": dict(sorted(axes.items())),
        "independent_cas_pass": independent_cas_pass,
        "independent_package_pass": independent_package_pass,
        "formula_failure_packages": sorted(
            str(item.get("package")) for item in formula_failures
        ),
        "parse_errors": parse_errors,
        "receipts": receipts,
        "claim_boundary": [
            "NO_02E_SEMANTIC_PROMOTION",
            "NO_02F_SEMANTIC_CLOSEOUT",
            "NO_CONSUMER_PARITY_PROMOTION",
            "NO_PROVIDER_ADMISSION",
            "NO_SCIENCE_PROMOTION",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(aggregate, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(aggregate, indent=2, sort_keys=True))
    return 1 if overall == "FAIL_FORMULA_OR_RECEIPT" else 0


if __name__ == "__main__":
    raise SystemExit(main())
