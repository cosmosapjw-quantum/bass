#!/usr/bin/env python3
"""Fail-closed verifier for the RF04 LOCAL-01 v2 R2 authority package."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


PACKAGE_FILES = (
    "AUTHORITY_REBIND.json",
    "V2_PUBLIC_MAPPING.json",
    "R2_AUTHORITY_AMENDMENT.json",
    "LOCAL_CODEX_HANDOFF_CONTRACT.json",
    "LOCAL_CODEX_HANDOFF.md",
    "LOCAL_IMPLEMENTATION_PROMPT_R2.md",
    "R2_DESIGN.md",
    "R2_IMPLEMENTATION_PLAN.md",
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
R2_AMENDMENT_ID = "RF04-V2-PUBLIC-MAPPING-R2-20260831"
CONTEXTUAL_IDENTITY_ARGUMENTS = ["directions", "weights", "remap_plan"]
STATIC_NATIVE_PAYLOAD_IDENTITY = "bass-rf04-polarized-v2-native-local01/v1"
REJECT_TOLERANCE_BITS = "3ddb7cdfd9d7bdbb"
GEOMETRY_RECEIPT_FIELDS = [
    "schema_id",
    "step_index",
    "input_direction_grid_sha256",
    "remap_plan_sha256",
    "backtrace_direction_sha256",
    "spatial_transport_sha256",
    "maximum_screen_leakage_binary64_hex",
    "minimum_coherency_eigenvalue_binary64_hex",
    "outer_panel_count",
    "internal_bisection_count",
]
PUBLIC_GEOMETRY_RECEIPT_FIELDS = [
    "schema_id",
    "step_index",
    "input_direction_grid_sha256",
    "remap_plan_sha256",
    "backtrace_direction_sha256",
    "spatial_transport_sha256",
    "maximum_screen_leakage",
    "minimum_coherency_eigenvalue",
    "outer_panel_count",
    "internal_bisection_count",
    "receipt_sha256",
    "receipt_chain_head_sha256",
]


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_value(errors: list[str], actual: Any, expected: Any, name: str) -> None:
    if actual != expected:
        errors.append(f"{name} mismatch: expected {expected!r}, observed {actual!r}")


def require_mapping(errors: list[str], value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(f"{name} missing or not an object")
        return {}
    return value


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


def validate_r2_authority(authority: dict[str, Any], amendment: Any, errors: list[str]) -> None:
    rebind = require_mapping(errors, authority.get("r2_public_contract_amendment"), "R2 authority rebind")
    require_value(errors, rebind.get("file"), "R2_AUTHORITY_AMENDMENT.json", "R2 authority file")
    require_value(errors, rebind.get("amendment_id"), R2_AMENDMENT_ID, "R2 authority amendment id")
    require_value(errors, rebind.get("approval"), "B_RECOMMENDATION_APPROVED", "R2 authority approval")
    amendment_object = require_mapping(errors, amendment, "R2 authority amendment")
    require_value(errors, amendment_object.get("amendment_id"), R2_AMENDMENT_ID, "R2 amendment id")
    amendment_authority = require_mapping(errors, amendment_object.get("authority"), "R2 amendment authority")
    require_value(errors, amendment_authority.get("approval"), "B_RECOMMENDATION_APPROVED", "R2 amendment approval")
    decisions = require_mapping(errors, amendment_object.get("decisions"), "R2 authority decisions")
    contextual = require_mapping(
        errors, decisions.get("contextual_execution_identity"), "contextual identity authority"
    )
    require_value(
        errors,
        contextual.get("argument_order"),
        CONTEXTUAL_IDENTITY_ARGUMENTS,
        "R2 contextual identity arguments",
    )
    payload = require_mapping(
        errors,
        decisions.get("native_payload_and_installation_evidence"),
        "R2 native payload authority",
    )
    require_value(
        errors,
        payload.get("runtime_native_payload_identity"),
        STATIC_NATIVE_PAYLOAD_IDENTITY,
        "R2 native payload identity",
    )


def validate_mapping_semantics(mapping: Any, errors: list[str]) -> None:
    mapping_object = require_mapping(errors, mapping, "v2 public mapping")
    require_value(errors, mapping_object.get("authority_revision"), R2_AMENDMENT_ID, "mapping authority revision")
    require_value(
        errors,
        mapping_object.get("schema_id"),
        "bass-rf04-typeii-polarized-public-route/v2",
        "v2 schema id",
    )
    symbols = require_mapping(errors, mapping_object.get("symbols"), "v2 native symbols")
    identity = require_mapping(errors, symbols.get("identity"), "identity symbol")
    require_value(
        errors,
        identity.get("native"),
        "rf04_typeii_polarized_execution_identity_v2",
        "identity native symbol",
    )
    require_value(errors, identity.get("arguments"), CONTEXTUAL_IDENTITY_ARGUMENTS, "identity arguments")
    argument_contract = require_mapping(errors, identity.get("argument_contract"), "identity argument contract")
    for name, shape in (("directions", ["M", "3"]), ("weights", ["M"])):
        argument = require_mapping(errors, argument_contract.get(name), f"identity {name} contract")
        require_value(errors, argument.get("dtype"), "float64", f"identity {name} dtype")
        require_value(errors, argument.get("shape"), shape, f"identity {name} shape")
    remap = require_mapping(errors, argument_contract.get("remap_plan"), "identity remap_plan contract")
    require_value(errors, remap.get("container"), "mapping", "identity remap_plan container")
    if "byte-identical" not in str(identity.get("identity_equivalence_rule", "")).lower():
        errors.append("identity equivalence rule missing")

    require_value(
        errors,
        require_mapping(errors, symbols.get("trajectory"), "trajectory symbol").get("native"),
        "rf04_typeii_polarized_trajectory_v2",
        "trajectory native symbol",
    )
    require_value(
        errors,
        require_mapping(errors, symbols.get("batch"), "batch symbol").get("native"),
        "rf04_typeii_polarized_batch_v2",
        "batch native symbol",
    )

    additions = require_mapping(errors, mapping_object.get("polarized_request_additions"), "polarized additions")
    route = require_mapping(errors, additions.get("quadrature_route"), "quadrature route")
    activation = require_mapping(errors, route.get("local01_activation"), "LOCAL-01 route activation")
    require_value(
        errors,
        activation.get("fixed_grid_raw_v1"),
        "AUTHORIZED_TO_IMPLEMENT_AND_TEST",
        "raw LOCAL-01 activation",
    )

    identity_codecs = require_mapping(errors, mapping_object.get("identity_codecs"), "identity codecs")
    direction_codec = require_mapping(errors, identity_codecs.get("direction_grid"), "direction grid codec")
    require_value(errors, direction_codec.get("schema_id"), "bass-rf04-direction-grid/v1", "direction grid codec")
    plan_codec = require_mapping(errors, identity_codecs.get("remap_plan"), "remap plan codec")
    require_value(errors, plan_codec.get("schema_id"), "bass-rf04-convex-csr-remap/v1", "remap plan codec")

    execution_identity = require_mapping(errors, mapping_object.get("execution_identity"), "execution identity")
    fixed_values = require_mapping(errors, execution_identity.get("fixed_values"), "execution identity fixed values")
    require_value(errors, fixed_values.get("source_owner_blob_sha1"), FINAL_DONOR_BLOB, "mapping final donor")
    native_payload = fixed_values.get("native_payload_identity")
    require_value(errors, native_payload, STATIC_NATIVE_PAYLOAD_IDENTITY, "native payload identity")
    if isinstance(native_payload, str) and native_payload.startswith("wheel-sha256:"):
        errors.append("native payload identity must not be a wheel hash")
    dynamic = require_mapping(errors, execution_identity.get("dynamic_value_rules"), "execution identity dynamic rules")
    if "native_payload_identity" in dynamic:
        errors.append("native payload identity must be static rather than a dynamic rule")
    if any("wheel-sha256" in str(value) for value in dynamic.values()):
        errors.append("native payload identity must not use wheel-sha256 dynamic values")
    installation = require_mapping(errors, execution_identity.get("installation_evidence"), "installation evidence")
    exact_wheel = require_mapping(errors, installation.get("exact_wheel_sha256"), "exact wheel evidence")
    require_value(
        errors,
        exact_wheel.get("location"),
        "LOCAL01_V2_VALIDATION.json.locked_wheel_sha256",
        "exact wheel evidence location",
    )
    if "wheel SHA-256" not in str(execution_identity.get("encoding", "")):
        errors.append("execution identity wheel exclusion missing")

    carrier = require_mapping(errors, mapping_object.get("carrier_validation"), "carrier validation")
    input_policy = require_mapping(errors, carrier.get("input_policy"), "carrier input policy")
    require_value(errors, input_policy.get("rust_variant"), "ScreenInputPolicy::Reject", "carrier input policy")
    require_value(errors, input_policy.get("tolerance_decimal"), "1e-10", "carrier tolerance")
    require_value(errors, input_policy.get("tolerance_binary64_hex"), REJECT_TOLERANCE_BITS, "carrier tolerance bits")
    if "Do not invoke ScreenInputPolicy::Project" not in str(input_policy.get("rule", "")):
        errors.append("carrier input policy permits silent projection")
    realizability = require_mapping(errors, carrier.get("input_realizability"), "carrier realizability")
    require_value(errors, realizability.get("failure_code"), "RF04_NONPHYSICAL_CARRIER", "carrier failure code")

    geometry = mapping_object.get("geometry_receipt_codecs")
    if not isinstance(geometry, dict):
        errors.append("geometry receipt codecs missing")
    else:
        require_value(errors, geometry.get("schema_id"), "bass-rf04-geometry-receipt/v1", "geometry receipt codec")
        for name in ("backtrace_direction", "spatial_transport", "receipt", "chain"):
            if not isinstance(geometry.get(name), dict):
                errors.append(f"geometry receipt codecs missing {name}")
        receipt = require_mapping(errors, geometry.get("receipt"), "geometry receipt body")
        require_value(
            errors,
            receipt.get("canonical_json_fields"),
            GEOMETRY_RECEIPT_FIELDS,
            "geometry receipt canonical fields",
        )
        chain = require_mapping(errors, geometry.get("chain"), "geometry receipt chain")
        if "H_0" not in str(chain.get("initial_head", "")) or "H_(i+1)" not in str(chain.get("next_head", "")):
            errors.append("geometry receipt chain formulas missing")

    trajectory = require_mapping(errors, mapping_object.get("trajectory_result"), "trajectory result")
    fields = require_mapping(errors, trajectory.get("fields"), "trajectory result fields")
    history = require_mapping(errors, fields.get("radiation_history"), "trajectory history")
    require_value(errors, history.get("shape"), ["K+1", "9*M"], "trajectory history shape")
    trajectory_identity = require_mapping(errors, fields.get("execution_identity"), "trajectory identity field")
    if "byte-identical" not in str(trajectory_identity.get("semantics", "")).lower():
        errors.append("trajectory identity equivalence missing")
    diagnostics = require_mapping(errors, fields.get("diagnostics"), "trajectory diagnostics")
    semantics = diagnostics.get("v2_semantics")
    if not isinstance(semantics, dict):
        errors.append("diagnostic semantics missing")
    else:
        for name in (
            "raw_pre_projection_screen_leakage",
            "post_projection_screen_leakage",
            "screen_leakage",
            "minimum_coherency_eigenvalue",
        ):
            if not isinstance(semantics.get(name), str) or not semantics[name].strip():
                errors.append(f"diagnostic semantics missing {name}")
    receipts = require_mapping(errors, fields.get("geometry_receipts"), "geometry receipts")
    require_value(errors, receipts.get("required_fields"), PUBLIC_GEOMETRY_RECEIPT_FIELDS, "public geometry receipt fields")
    chain_head = require_mapping(errors, fields.get("geometry_receipt_chain_head_sha256"), "trajectory geometry chain head")
    require_value(errors, chain_head.get("dtype"), "lowercase_sha256_hex", "trajectory geometry chain head")

    batch = require_mapping(errors, mapping_object.get("batch_result"), "batch result")
    batch_fields = require_mapping(errors, batch.get("fields"), "batch fields")
    final_radiation = require_mapping(errors, batch_fields.get("final_radiation"), "batch final radiation")
    require_value(errors, final_radiation.get("shape"), ["B", "9*M"], "batch final radiation shape")
    status = require_mapping(errors, batch_fields.get("member_status"), "batch member status")
    require_value(errors, status.get("success_code"), 0, "batch success code")
    require_value(errors, status.get("failure_code"), 1, "batch failure code")
    batch_identity = require_mapping(errors, batch_fields.get("execution_identity"), "batch identity field")
    if "byte-identical" not in str(batch_identity.get("semantics", "")).lower():
        errors.append("batch identity equivalence missing")
    status_codes = batch.get("member_status_codes")
    if not isinstance(status_codes, dict):
        errors.append("batch status code table missing")
    else:
        require_value(errors, list(status_codes), ["0", "1"], "batch status code table keys")
        success = require_mapping(errors, status_codes.get("0"), "batch success status")
        require_value(errors, success.get("member_error_code"), None, "batch success error code")
        failure = require_mapping(errors, status_codes.get("1"), "batch failure status")
        require_value(
            errors,
            failure.get("member_error_code_one_of"),
            [
                "RF04_NONPHYSICAL_CARRIER",
                "RF04_NUMERICAL_DOMAIN",
                "RF04_KRYLOV_CERTIFICATE_FAILURE",
                "RF04_MEMBER_FAILURE",
            ],
            "batch failure error codes",
        )


def validate_package(root: Path) -> list[str]:
    errors: list[str] = []
    for relative in PACKAGE_FILES:
        if not (root / relative).is_file():
            errors.append(f"required package file missing: {relative}")
    if errors:
        return errors
    try:
        authority = load_json(root / "AUTHORITY_REBIND.json")
        mapping = load_json(root / "V2_PUBLIC_MAPPING.json")
        amendment = load_json(root / "R2_AUTHORITY_AMENDMENT.json")
        contract = load_json(root / "LOCAL_CODEX_HANDOFF_CONTRACT.json")
    except (OSError, json.JSONDecodeError) as exc:
        return [f"package JSON cannot be read: {exc}"]
    authority_object = require_mapping(errors, authority, "authority rebind")
    try:
        final_donor = authority_object["base_state"]["final_source_owner"]
        require_value(errors, final_donor["git_blob_sha1"], FINAL_DONOR_BLOB, "final donor blob")
        require_value(errors, final_donor["sha256"], FINAL_DONOR_SHA256, "final donor sha256")
        require_value(errors, authority_object["base_state"]["pr70"]["head"], "380ce6fe6aebe0c76c59c0d2a0f8707aac0ce14c", "PR #70 head")
        require_value(errors, authority_object["base_state"]["pr70"]["tree"], "0062a719173dc0c40dcc1202ab0d305f8fe2e2bb", "PR #70 tree")
        route_authority = authority_object["inherited_authorities"]["v2_route_design"]
        require_value(errors, route_authority["route_schema_git_blob_sha1"], "333fe95fe5a0159490f6ae095aeff11b649d1d32", "v2 route schema blob")
        require_value(errors, route_authority["decisions_git_blob_sha1"], "70d9575ae6dc4e8c5c1e1f60f549094fe53c1daa", "v2 decisions blob")
        require_value(errors, authority_object["inherited_authorities"]["v1_public_schema"]["git_blob_sha1"], "a5a503f96c8d85af265be67ac04fd3ff983d9b33", "v1 public schema blob")
    except (KeyError, TypeError) as exc:
        errors.append(f"required authority structure missing: {exc}")
    validate_r2_authority(authority_object, amendment, errors)
    validate_mapping_semantics(mapping, errors)
    validate_contract(contract, errors)
    if isinstance(contract, dict) and tuple(contract) == CONTRACT_KEYS:
        actual_handoff = (root / "LOCAL_CODEX_HANDOFF.md").read_text(encoding="utf-8")
        if actual_handoff != render_handoff(contract):
            errors.append("handoff markdown does not exactly render the handoff contract")
    prompt = (root / "LOCAL_IMPLEMENTATION_PROMPT_R2.md").read_text(encoding="utf-8")
    if "rf04_typeii_polarized_execution_identity_v2(directions, weights, remap_plan)" not in prompt:
        errors.append("R2 local prompt identity signature missing")
    if STATIC_NATIVE_PAYLOAD_IDENTITY not in prompt:
        errors.append("R2 local prompt native payload identity missing")
    validate_manifest(root, errors)
    return errors


def main(argv: list[str]) -> int:
    root = Path(argv[1]).resolve() if len(argv) == 2 else Path(__file__).resolve().parent
    errors = validate_package(root)
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("PASS_RF04_V2_PUBLIC_MAPPING_R2_AUTHORITY_PACKAGE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
