#!/usr/bin/env python3
"""Fail-closed aggregate verifier for XCAS-04 external-engine receipts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


EXPECTED_JAS_SHA256 = (
    "62a362d2fc2591d39f5973125aef71cf70267d486d9b321240454a242bd11976"
)


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ValueError(f"missing receipt: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"receipt is not an object: {path}")
    return value


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def verify_octave(receipt: dict[str, Any]) -> None:
    require(receipt.get("status") == "PASS", "Octave status is not PASS")
    require(receipt.get("engine") == "GNU Octave", "wrong Octave engine name")
    require(
        receipt.get("engine_role")
        == "INDEPENDENT_NUMERICAL_AND_MATRIX_ORACLE_NOT_SYMBOLIC_CAS",
        "Octave was misclassified as a symbolic CAS",
    )
    require(receipt.get("symbolic_backend") == "NONE", "Octave symbolic backend used")
    require(int(receipt.get("samples", 0)) >= 256, "insufficient Octave samples")
    tolerance = float(receipt.get("tolerance", 0.0))
    require(tolerance > 0.0, "invalid Octave tolerance")
    for key in (
        "max_clean_residual",
        "max_direction_tangency",
        "max_rei_delta_residual",
        "max_d1_skew_residual",
    ):
        require(float(receipt.get(key, float("inf"))) < tolerance, f"Octave {key} failed")
    for key in (
        "hostile_jacobian_signal",
        "hostile_sign_signal",
        "hostile_missing_aberration_signal",
        "min_d0_non_skew_signal",
    ):
        require(float(receipt.get(key, 0.0)) > 1.0e-6, f"Octave {key} too small")


def verify_jas(receipt: dict[str, Any]) -> None:
    require(receipt.get("status") == "PASS", "JAS status is not PASS")
    require(receipt.get("engine") == "Java Algebra System", "wrong JAS engine")
    require(receipt.get("version") == "2.7.200", "wrong JAS version")
    require(
        receipt.get("engine_role") == "INDEPENDENT_EXACT_POLYNOMIAL_CAS",
        "wrong JAS engine role",
    )
    require(receipt.get("jar_sha256") == EXPECTED_JAS_SHA256, "wrong JAS jar SHA-256")
    require(int(receipt.get("checks_total", 0)) == 14, "wrong JAS check count")
    require(int(receipt.get("checks_passed", -1)) == 14, "JAS checks did not all pass")
    checks = receipt.get("checks")
    require(isinstance(checks, dict) and len(checks) == 14, "bad JAS check map")
    require(all(value is True for value in checks.values()), "JAS check map contains failure")


def verify_julia(receipt: dict[str, Any]) -> None:
    require(receipt.get("status") == "PASS", "Julia/Nemo status is not PASS")
    require(receipt.get("engine") == "Julia/Nemo", "wrong Julia engine")
    require(receipt.get("julia_version") == "1.12.7", "wrong Julia version")
    require(receipt.get("nemo_version") == "0.56.1", "wrong Nemo version")
    require(
        receipt.get("engine_role")
        == "INDEPENDENT_EXACT_CAS_JULIA_FRONTEND_FLINT_BACKEND",
        "wrong Julia/Nemo role",
    )
    require(int(receipt.get("checks_total", 0)) == 14, "wrong Julia check count")
    require(int(receipt.get("checks_passed", -1)) == 14, "Julia checks did not all pass")
    manifest_sha = receipt.get("manifest_sha256")
    require(
        isinstance(manifest_sha, str)
        and len(manifest_sha) == 64
        and all(ch in "0123456789abcdef" for ch in manifest_sha),
        "resolved Julia manifest SHA-256 is missing or malformed",
    )
    checks = receipt.get("checks")
    require(isinstance(checks, dict) and len(checks) == 14, "bad Julia check map")
    require(all(value is True for value in checks.values()), "Julia check map contains failure")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--octave", type=Path, required=True)
    parser.add_argument("--jas", type=Path, required=True)
    parser.add_argument("--julia", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    try:
        octave = load_json(args.octave)
        jas = load_json(args.jas)
        julia = load_json(args.julia)
        verify_octave(octave)
        verify_jas(jas)
        verify_julia(julia)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"XCAS04 aggregate verification failed: {exc}", file=sys.stderr)
        return 1

    aggregate = {
        "schema_version": "1.0.0",
        "matrix_id": "XCAS04_OCTAVE_JAS_JULIA",
        "status": "PASS",
        "engines_executed": 3,
        "exact_symbolic_engines_executed": 2,
        "numerical_matrix_oracles_executed": 1,
        "exact_symbolic_engine_names": ["Java Algebra System", "Julia/Nemo"],
        "numerical_matrix_oracle_names": ["GNU Octave"],
        "authority_effect": "NONE_EXTERNAL_ORACLE",
        "claim_boundary": [
            "NO_OWNER_FORMULA_CHANGE",
            "NO_TENSOR_CAS_CLAIM",
            "NO_POSITIVITY_OR_INEQUALITY_PROOF",
            "NO_CONSUMER_SOFTWARE_PARITY",
            "NO_02E_OR_02F_SEMANTIC_CLOSEOUT",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(aggregate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(aggregate, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
