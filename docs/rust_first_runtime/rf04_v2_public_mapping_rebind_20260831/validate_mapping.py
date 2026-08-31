#!/usr/bin/env python3
"""Fail-closed verifier for the RF04 LOCAL-01 v2 public-mapping package."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


PACKAGE_FILES = (
    "AUTHORITY_REBIND.json",
    "V2_PUBLIC_MAPPING.json",
    "LOCAL_CODEX_HANDOFF_CONTRACT.json",
    "LOCAL_CODEX_HANDOFF.md",
    "README.md",
    "test_validate_mapping.py",
    "validate_mapping.py",
)
CONTRACT_KEYS = (
    "outcome",
    "success_criteria",
    "boundaries",
    "permissions",
    "tools",
    "evidence",
    "stop_conditions",
)
FINAL_DONOR_BLOB = "693e9fff0d44f2b8e40966ceb8da3c348d830bd4"
FINAL_DONOR_SHA256 = "f1f624d47b35208d339e6ea298f023d70012e54c80357973a65dc63c9491de6e"


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_manifest(root: Path, errors: list[str]) -> None:
    manifest = root / "MANIFEST.sha256"
    if not manifest.is_file():
        errors.append("manifest missing")
        return
    entries: dict[str, str] = {}
    for line in manifest.read_text(encoding="utf-8").splitlines():
        digest, separator, relative = line.partition("  ")
        if not separator or len(digest) != 64 or not relative:
            errors.append(f"invalid manifest line: {line!r}")
            continue
        entries[relative] = digest
    expected = set(PACKAGE_FILES)
    if set(entries) != expected:
        errors.append("manifest file set does not match package contents")
    for relative, expected_digest in entries.items():
        candidate = root / relative
        if not candidate.is_file():
            errors.append(f"manifest target missing: {relative}")
            continue
        if sha256(candidate) != expected_digest:
            errors.append(f"manifest digest mismatch: {relative}")


def require_value(errors: list[str], actual: Any, expected: Any, name: str) -> None:
    if actual != expected:
        errors.append(f"{name} mismatch: expected {expected!r}, observed {actual!r}")


def validate_contract(contract: Any, errors: list[str]) -> None:
    if not isinstance(contract, dict):
        errors.append("handoff contract is not an object")
        return
    if tuple(contract) != CONTRACT_KEYS:
        errors.append("handoff contract keys are not the required canonical order")
    for key in CONTRACT_KEYS:
        value = contract.get(key)
        if key == "outcome":
            if not isinstance(value, str) or not value.strip():
                errors.append("handoff outcome is empty")
            continue
        if not isinstance(value, list) or not value:
            errors.append(f"handoff {key} must be a nonempty list")
            continue
        if any(not isinstance(item, str) or not item.strip() for item in value):
            errors.append(f"handoff {key} contains an empty item")
        if len(set(value)) != len(value):
            errors.append(f"handoff {key} contains a duplicate item")


def render_handoff(contract: dict[str, Any]) -> str:
    sections: list[str] = []
    for key in CONTRACT_KEYS:
        value = contract[key]
        sections.append(f"# {key}")
        sections.append("")
        if key == "outcome":
            sections.append(value)
        else:
            sections.extend(f"- {item}" for item in value)
        sections.append("")
    return "\n".join(sections)


def validate_package(root: Path) -> list[str]:
    errors: list[str] = []
    for relative in PACKAGE_FILES:
        if not (root / relative).is_file():
            errors.append(f"required package file missing: {relative}")
    if errors:
        return errors
    authority = load_json(root / "AUTHORITY_REBIND.json")
    mapping = load_json(root / "V2_PUBLIC_MAPPING.json")
    contract = load_json(root / "LOCAL_CODEX_HANDOFF_CONTRACT.json")
    try:
        final_donor = authority["base_state"]["final_source_owner"]
        require_value(errors, final_donor["git_blob_sha1"], FINAL_DONOR_BLOB, "final donor blob")
        require_value(errors, final_donor["sha256"], FINAL_DONOR_SHA256, "final donor sha256")
        require_value(errors, authority["base_state"]["pr70"]["head"], "380ce6fe6aebe0c76c59c0d2a0f8707aac0ce14c", "PR #70 head")
        require_value(errors, authority["base_state"]["pr70"]["tree"], "0062a719173dc0c40dcc1202ab0d305f8fe2e2bb", "PR #70 tree")
        require_value(errors, authority["inherited_authorities"]["v2_route_design"]["route_schema_git_blob_sha1"], "333fe95fe5a0159490f6ae095aeff11b649d1d32", "v2 route schema blob")
        require_value(errors, authority["inherited_authorities"]["v2_route_design"]["decisions_git_blob_sha1"], "70d9575ae6dc4e8c5c1e1f60f549094fe53c1daa", "v2 decisions blob")
        require_value(errors, authority["inherited_authorities"]["v1_public_schema"]["git_blob_sha1"], "a5a503f96c8d85af265be67ac04fd3ff983d9b33", "v1 public schema blob")
        require_value(errors, mapping["schema_id"], "bass-rf04-typeii-polarized-public-route/v2", "v2 schema id")
        require_value(errors, mapping["execution_identity"]["fixed_values"]["source_owner_blob_sha1"], FINAL_DONOR_BLOB, "mapping final donor")
        native_symbols = mapping["symbols"]
        require_value(errors, native_symbols["identity"]["native"], "rf04_typeii_polarized_execution_identity_v2", "identity native symbol")
        require_value(errors, native_symbols["trajectory"]["native"], "rf04_typeii_polarized_trajectory_v2", "trajectory native symbol")
        require_value(errors, native_symbols["batch"]["native"], "rf04_typeii_polarized_batch_v2", "batch native symbol")
        require_value(errors, mapping["trajectory_result"]["fields"]["radiation_history"]["shape"], ["K+1", "9*M"], "trajectory history shape")
        require_value(errors, mapping["batch_result"]["fields"]["final_radiation"]["shape"], ["B", "9*M"], "batch final radiation shape")
        require_value(errors, mapping["polarized_request_additions"]["quadrature_route"]["local01_activation"]["fixed_grid_raw_v1"], "AUTHORIZED_TO_IMPLEMENT_AND_TEST", "raw LOCAL-01 activation")
    except (KeyError, TypeError) as exc:
        errors.append(f"required mapping structure missing: {exc}")
    validate_contract(contract, errors)
    if isinstance(contract, dict) and tuple(contract) == CONTRACT_KEYS:
        actual_handoff = (root / "LOCAL_CODEX_HANDOFF.md").read_text(encoding="utf-8")
        if actual_handoff != render_handoff(contract):
            errors.append("handoff markdown does not exactly render the handoff contract")
    validate_manifest(root, errors)
    return errors


def main(argv: list[str]) -> int:
    root = Path(argv[1]).resolve() if len(argv) == 2 else Path(__file__).resolve().parent
    errors = validate_package(root)
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("PASS_RF04_V2_PUBLIC_MAPPING_AUTHORITY_PACKAGE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
