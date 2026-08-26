#!/usr/bin/env python3
"""Compose the content-addressed RF-02C step-3 provenance receipt."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


PARENT = "0563c080e54fcd90d6160bec35e4f20d240d8d2e"
V2_CONTRACT = "docs/rust_first_runtime/RF02C_EXECUTION_CONTRACT_V2.json"
JVP_SOURCE = "tools/audit/rf02c_randomized_jvp.py"
JVP_SEED = 318_961_711
JVP_CASE_COUNT = 250
JVP_THRESHOLD = 32.0
JVP_CORPUS = [
    {"chart": "class_a", "state_dimension": 5, "kappa": 0.0, "cases": 50},
    {"chart": "class_b", "state_dimension": 5, "kappa": -1.0, "cases": 50},
    {"chart": "exceptional", "state_dimension": 6, "kappa": -9.0, "cases": 50},
    {"chart": "type_ix_d", "state_dimension": 7, "kappa": -1.0, "cases": 50},
    {
        "chart": "type_ix_d_future",
        "state_dimension": 7,
        "kappa": -1.0,
        "cases": 50,
    },
]
INHERITED = {
    "audit_manifest": ("audit/manifest.json", "f4e1fd4de82a8ada0dcc4623af240eaa413bcba2"),
    "rf02a_evidence": ("artifacts/rust_first_runtime/rf02a/EVIDENCE.json", "8d2321f75dd299a52b06b352a9e743d1cabd594b"),
    "rf02b_evidence": ("artifacts/rust_first_runtime/rf02b/EVIDENCE.json", "02e2a71bec0228a749b98c3b1a92c60071bdcc6b"),
}


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, allow_nan=False, separators=(",", ":"), sort_keys=True).encode(
        "utf-8"
    )


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def _git_bytes(root: Path, revision_path: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(root), "show", revision_path])


def _parent_file(root: Path, path: str, expected_blob: str) -> dict[str, str]:
    blob = _git(root, "rev-parse", f"{PARENT}:{path}")
    if blob != expected_blob:
        raise RuntimeError(f"unexpected immutable parent blob for {path}: {blob}")
    content = _git_bytes(root, f"{PARENT}:{path}")
    return {"path": path, "git_blob": blob, "content_sha256": _sha256(content)}


def _current_contract(root: Path) -> dict[str, str]:
    path = root / V2_CONTRACT
    if not path.is_file():
        raise RuntimeError(f"missing execution contract: {V2_CONTRACT}")
    return {
        "path": V2_CONTRACT,
        "git_blob": _git(root, "rev-parse", f"HEAD:{V2_CONTRACT}"),
        "content_sha256": _sha256(path.read_bytes()),
    }


def _is_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _validated_jvp_receipt(root: Path, path: Path) -> dict[str, Any]:
    content = path.read_bytes()
    receipt = json.loads(content)
    if receipt.get("schema") != "bass-rf02c-randomized-jvp-receipt/v1":
        raise RuntimeError("JVP receipt schema is not RF-02C v1")
    if receipt.get("status") != "PASS" or receipt.get("case_count") != JVP_CASE_COUNT:
        raise RuntimeError("JVP receipt is not a passing 250-case detector result")
    detector = receipt.get("detector", {})
    expected_detector = {
        "source_path": JVP_SOURCE,
        "source_sha256": _sha256((root / JVP_SOURCE).read_bytes()),
        "frozen_corpus_source": JVP_SOURCE,
        "seed": JVP_SEED,
        "chart_domain_corpus": JVP_CORPUS,
        "scale_formula": "abs(jvp-central_difference)/(2^-40 + 2^-20*max(1,abs(jvp),abs(central_difference)))",
        "finite_difference_step": "2^-18",
        "normalized_error_threshold": JVP_THRESHOLD,
        "source_mutation_detected": False,
    }
    if detector != expected_detector:
        raise RuntimeError("JVP receipt detector source/corpus/scale/threshold mismatch")
    execution = receipt.get("execution", {})
    if execution.get("native_api") != "direct installed bianchi_rustcore.chart_rhs/chart_jvp":
        raise RuntimeError("JVP receipt did not use direct installed native calls")
    if execution.get("jax_used") is not False:
        raise RuntimeError("JVP receipt must record JAX as unused")
    native_identity = execution.get("native_identity", {})
    if not all(
        _is_sha256(native_identity.get(key))
        for key in (
            "extension_sha256",
            "record_sha256",
            "wheel_sha256",
            "execution_identity_sha256",
            "native_capability_receipt",
        )
    ):
        raise RuntimeError("JVP receipt lacks content-addressed native identity")
    wheel_filename = native_identity.get("wheel_filename")
    if not isinstance(wheel_filename, str) or not wheel_filename.endswith(".whl"):
        raise RuntimeError("JVP receipt lacks normalized wheel filename")
    if "wheel_direct_url" in native_identity or "file://" in json.dumps(native_identity):
        raise RuntimeError("JVP receipt contains ephemeral native installation provenance")
    from bianchi.q.geometry_identity import geometry_route_identity

    expected_execution_identity = geometry_route_identity()
    if native_identity.get("execution_identity") != expected_execution_identity:
        raise RuntimeError("JVP receipt native execution identity mismatch")
    if native_identity.get("execution_identity_sha256") != _sha256(
        _canonical_bytes(expected_execution_identity)
    ):
        raise RuntimeError("JVP receipt execution identity digest mismatch")
    if native_identity.get("native_payload_identity") != expected_execution_identity.get(
        "native_payload_identity"
    ):
        raise RuntimeError("JVP receipt native payload identity mismatch")
    if native_identity.get("native_capability_receipt") != expected_execution_identity.get(
        "native_capability_receipt"
    ):
        raise RuntimeError("JVP receipt native capability receipt mismatch")
    log = receipt.get("canonical_log")
    if not isinstance(log, list) or len(log) != JVP_CASE_COUNT:
        raise RuntimeError("JVP receipt canonical log has the wrong case count")
    dimensions = {item["chart"]: item["state_dimension"] for item in JVP_CORPUS}
    for case_index, entry in enumerate(log):
        if not isinstance(entry, dict) or set(entry) != {
            "case",
            "chart",
            "maximum_normalized_error",
            "output_dimension",
        }:
            raise RuntimeError("JVP receipt canonical log schema mismatch")
        maximum = entry["maximum_normalized_error"]
        if (
            entry["case"] != case_index
            or entry["chart"] not in dimensions
            or entry["output_dimension"] != dimensions[entry["chart"]]
            or not isinstance(maximum, (int, float))
            or not (0.0 <= maximum <= JVP_THRESHOLD)
        ):
            raise RuntimeError("JVP receipt canonical log value mismatch")
    expected_log_digest = _sha256(_canonical_bytes(log))
    if receipt.get("canonical_log_sha256") != expected_log_digest:
        raise RuntimeError("JVP receipt canonical log digest mismatch")
    claimed_result_digest = receipt.get("canonical_result_sha256")
    if not _is_sha256(claimed_result_digest):
        raise RuntimeError("JVP receipt lacks canonical_result_sha256")
    unsigned_receipt = dict(receipt)
    del unsigned_receipt["canonical_result_sha256"]
    if claimed_result_digest != _sha256(_canonical_bytes(unsigned_receipt)):
        raise RuntimeError("JVP receipt canonical result digest mismatch")
    return {"path": path.name, "content_sha256": _sha256(content), "receipt": receipt}


def build_receipt(root: Path, jvp_path: Path) -> dict[str, Any]:
    parent_tree = _git(root, "rev-parse", f"{PARENT}^{{tree}}")
    inherited = {name: _parent_file(root, path, blob) for name, (path, blob) in INHERITED.items()}
    result = {
        "schema": "bass-rf02c-composite-receipt/v1",
        "status": "PASS",
        "inherited": {
            "git_parent": {"commit": PARENT, "tree": parent_tree},
            **inherited,
        },
        "execution_contract_v2": _current_contract(root),
        "inherited_randomized_jvp": {
            "status": "NOT_REUSED_INCOMPLETE_REPLAY_MATERIAL",
            "reason": "The inherited material lacks the frozen corpus, seed, scale, threshold, and canonical log required by RF-02C step 3.",
        },
        "jvp_receipt": _validated_jvp_receipt(root, jvp_path),
        "invalidation_predicates": [
            "git_parent_or_tree_changes",
            "audit_manifest_parent_blob_or_content_changes",
            "rf02a_or_rf02b_evidence_parent_blob_or_content_changes",
            "execution_contract_v2_blob_or_content_changes",
            "jvp_receipt_content_or_canonical_digest_changes",
            "jvp_native_identity_changes",
            "jvp_frozen_corpus_seed_scale_or_threshold_changes",
        ],
    }
    result["canonical_result_sha256"] = _sha256(_canonical_bytes(result))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--jvp-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    output = args.output.resolve()
    receipt = build_receipt(root, args.jvp_receipt.resolve())
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(_canonical_bytes(receipt) + b"\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
