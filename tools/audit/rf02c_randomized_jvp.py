#!/usr/bin/env python3
"""Emit the RF-02C fixed-corpus native chart-JVP detector receipt."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import math
import random
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

import numpy as np


SCHEMA = "bass-rf02c-randomized-jvp-receipt/v1"
SEED = 318_961_711
CASE_COUNT = 250
CASES_PER_CHART = 50
FD_STEP = 2.0**-18
SCALE_ABSOLUTE = 2.0**-40
SCALE_RELATIVE = 2.0**-20
NORMALIZED_ERROR_THRESHOLD = 32.0
CHART_CORPUS = (
    ("class_a", 5, 0.0),
    ("class_b", 5, -1.0),
    ("exceptional", 6, -9.0),
    ("type_ix_d", 7, -1.0),
    ("type_ix_d_future", 7, -1.0),
)


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, allow_nan=False, separators=(",", ":"), sort_keys=True).encode(
        "utf-8"
    )


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _fixed_cases() -> list[dict[str, Any]]:
    """Create the source-frozen, code-level detector corpus without JAX."""
    rng = random.Random(SEED)
    cases: list[dict[str, Any]] = []
    for chart, dimension, kappa in CHART_CORPUS:
        for chart_index in range(CASES_PER_CHART):
            cases.append(
                {
                    "case": len(cases),
                    "chart": chart,
                    "chart_case": chart_index,
                    "gamma": round(0.9 + 0.8 * rng.random(), 12),
                    "kappa": kappa,
                    "state": [round(-0.35 + 0.70 * rng.random(), 12) for _ in range(dimension)],
                    "tangent": [round(-0.45 + 0.90 * rng.random(), 12) for _ in range(dimension)],
                }
            )
    assert len(cases) == CASE_COUNT
    return cases


def _native_identity(native: Any) -> dict[str, Any]:
    extension = getattr(native, "bianchi_rustcore", native)
    extension_path = Path(getattr(extension, "__file__", ""))
    if not extension_path.is_file():
        raise RuntimeError("direct installed native extension is unavailable")
    distribution = importlib.metadata.distribution("bianchi-rustcore")
    direct_url: dict[str, Any] | None = None
    try:
        direct_url = json.loads(distribution.read_text("direct_url.json") or "null")
    except json.JSONDecodeError as exc:
        raise RuntimeError("installed native direct_url.json is invalid") from exc
    record = distribution.read_text("RECORD")
    if record is None:
        raise RuntimeError("installed native distribution lacks RECORD")
    if not isinstance(direct_url, dict):
        raise RuntimeError("installed native direct_url.json is absent")
    try:
        wheel_sha256 = direct_url["archive_info"]["hashes"]["sha256"]
        wheel_filename = Path(unquote(urlparse(direct_url["url"]).path)).name
    except (KeyError, TypeError) as exc:
        raise RuntimeError("installed native direct_url.json lacks wheel identity") from exc
    if (
        not isinstance(wheel_sha256, str)
        or len(wheel_sha256) != 64
        or any(character not in "0123456789abcdefABCDEF" for character in wheel_sha256)
        or not wheel_filename.endswith(".whl")
    ):
        raise RuntimeError("installed native direct_url.json has invalid wheel identity")
    raw_execution_identity = native.rf02c_execution_identity()
    if isinstance(raw_execution_identity, bytes):
        raw_execution_identity = raw_execution_identity.decode("utf-8")
    if isinstance(raw_execution_identity, str):
        try:
            execution_identity = json.loads(raw_execution_identity)
        except json.JSONDecodeError as exc:
            raise RuntimeError("native RF-02C execution identity is invalid JSON") from exc
    elif isinstance(raw_execution_identity, dict):
        execution_identity = raw_execution_identity
    else:
        raise RuntimeError("native RF-02C execution identity has an unsupported type")
    payload_identity = execution_identity.get("native_payload_identity")
    capability_receipt = execution_identity.get("native_capability_receipt")
    if not isinstance(payload_identity, str) or not isinstance(capability_receipt, str):
        raise RuntimeError("native RF-02C execution identity lacks payload capability fields")
    return {
        "distribution": distribution.metadata["Name"],
        "distribution_version": distribution.version,
        "extension_filename": extension_path.name,
        "extension_sha256": _sha256_file(extension_path),
        "record_sha256": _sha256_bytes(record.encode("utf-8")),
        "wheel_filename": wheel_filename,
        "wheel_sha256": wheel_sha256.lower(),
        "execution_identity": execution_identity,
        "execution_identity_sha256": _sha256_bytes(_canonical_bytes(execution_identity)),
        "native_payload_identity": payload_identity,
        "native_capability_receipt": capability_receipt,
    }


def _evaluate_case(native: Any, case: dict[str, Any]) -> dict[str, Any]:
    state = np.asarray(case["state"], dtype=np.float64)
    tangent = np.asarray(case["tangent"], dtype=np.float64)
    kwargs = (case["chart"], state, case["gamma"], case["kappa"])
    jvp = np.asarray(native.chart_jvp(case["chart"], state, tangent, case["gamma"], case["kappa"]), dtype=np.float64)
    positive = np.asarray(native.chart_rhs(case["chart"], state + FD_STEP * tangent, case["gamma"], case["kappa"]), dtype=np.float64)
    negative = np.asarray(native.chart_rhs(case["chart"], state - FD_STEP * tangent, case["gamma"], case["kappa"]), dtype=np.float64)
    finite_difference = (positive - negative) / (2.0 * FD_STEP)
    if not (np.isfinite(jvp).all() and np.isfinite(finite_difference).all()):
        raise RuntimeError(f"non-finite native JVP result for case {case['case']}")
    scale = SCALE_ABSOLUTE + SCALE_RELATIVE * np.maximum(
        1.0, np.maximum(np.abs(jvp), np.abs(finite_difference))
    )
    normalized_error = np.abs(jvp - finite_difference) / scale
    maximum = float(np.max(normalized_error))
    if maximum > NORMALIZED_ERROR_THRESHOLD:
        raise RuntimeError(
            f"native JVP detector threshold exceeded for case {case['case']}: {maximum}"
        )
    return {
        "case": case["case"],
        "chart": case["chart"],
        "maximum_normalized_error": maximum,
        "output_dimension": int(jvp.size),
    }


def build_receipt(root: Path) -> dict[str, Any]:
    """Run the direct installed native calls and construct canonical evidence."""
    import bianchi_rustcore as native

    source = Path(__file__).resolve()
    source_before = _sha256_file(source)
    if not callable(getattr(native, "chart_rhs", None)) or not callable(
        getattr(native, "chart_jvp", None)
    ):
        raise RuntimeError("direct installed native chart_rhs/chart_jvp are unavailable")
    cases = _fixed_cases()
    log = [_evaluate_case(native, case) for case in cases]
    source_after = _sha256_file(source)
    if source_before != source_after:
        raise RuntimeError("detector source changed during execution")
    canonical_log_sha256 = _sha256_bytes(_canonical_bytes(log))
    result = {
        "schema": SCHEMA,
        "status": "PASS",
        "case_count": CASE_COUNT,
        "detector": {
            "source_path": "tools/audit/rf02c_randomized_jvp.py",
            "source_sha256": source_before,
            "frozen_corpus_source": "tools/audit/rf02c_randomized_jvp.py",
            "seed": SEED,
            "chart_domain_corpus": [
                {"chart": chart, "state_dimension": dimension, "kappa": kappa, "cases": CASES_PER_CHART}
                for chart, dimension, kappa in CHART_CORPUS
            ],
            "scale_formula": "abs(jvp-central_difference)/(2^-40 + 2^-20*max(1,abs(jvp),abs(central_difference)))",
            "finite_difference_step": "2^-18",
            "normalized_error_threshold": NORMALIZED_ERROR_THRESHOLD,
            "source_mutation_detected": False,
        },
        "execution": {
            "native_api": "direct installed bianchi_rustcore.chart_rhs/chart_jvp",
            "jax_used": False,
            "native_identity": _native_identity(native),
        },
        "canonical_log": log,
        "canonical_log_sha256": canonical_log_sha256,
    }
    result["canonical_result_sha256"] = _sha256_bytes(_canonical_bytes(result))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    output = args.output.resolve()
    receipt = build_receipt(root)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(_canonical_bytes(receipt) + b"\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
