#!/usr/bin/env python3
"""Fail-closed verifier for the BASS-only SYNC-MAP-02E-R1 export."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

FORMULA_IDS = [
    "BASS.FRAME.ABERRATED_DIRECTION.001",
    "BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001",
    "BASS.FRAME.DOPPLER_FACTOR.001",
    "BASS.FRAME.SOLID_ANGLE_JACOBIAN.001",
    "BASS.PHOTON.DIRECTION_FLOW.001",
    "BASS.PHOTON.ENERGY_DRIFT.001",
]
EXPECTED_CLAIMS = [
    "BASS_OWNER_FORMULA_HARDENING_ONLY",
    "NO_CROSS_REPOSITORY_SOURCE_MUTATION",
    "NO_CONSUMER_PARITY",
    "NO_BACKGROUND_PROVIDER",
    "NO_GLOBAL_TILT",
    "NO_SCREEN_TRANSPORT",
    "NO_NUMERICAL_OR_SCIENCE_PROMOTION",
]
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def sha256_object(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def formula_map(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = data.get("formulas")
    require(isinstance(rows, list), "formulas must be a list")
    result: dict[str, dict[str, Any]] = {}
    for row in rows:
        require(isinstance(row, dict), "formula row must be an object")
        formula_id = row.get("formula_id")
        require(isinstance(formula_id, str), "formula_id must be a string")
        require(formula_id not in result, f"duplicate formula_id: {formula_id}")
        result[formula_id] = row
    return result


def check_graph(data: dict[str, Any]) -> None:
    ids = set(FORMULA_IDS)
    edges = data.get("internal_dependency_edges")
    require(isinstance(edges, list), "internal_dependency_edges must be a list")
    adjacency = {formula_id: set() for formula_id in ids}
    indegree = {formula_id: 0 for formula_id in ids}
    seen: set[tuple[str, str, str]] = set()
    for edge in edges:
        source = edge.get("from")
        target = edge.get("to")
        relation = edge.get("relation")
        require(source in ids and target in ids, "internal edge endpoint outside formula set")
        require(relation == "depends_on", "unexpected internal edge relation")
        key = (source, target, relation)
        require(key not in seen, f"duplicate internal edge: {key}")
        seen.add(key)
        if target not in adjacency[source]:
            adjacency[source].add(target)
            indegree[target] += 1

    expected = {
        ("BASS.FRAME.ABERRATED_DIRECTION.001", "BASS.FRAME.DOPPLER_FACTOR.001"),
        (
            "BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001",
            "BASS.FRAME.ABERRATED_DIRECTION.001",
        ),
        (
            "BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001",
            "BASS.FRAME.DOPPLER_FACTOR.001",
        ),
        (
            "BASS.FRAME.SOLID_ANGLE_JACOBIAN.001",
            "BASS.FRAME.ABERRATED_DIRECTION.001",
        ),
        (
            "BASS.FRAME.SOLID_ANGLE_JACOBIAN.001",
            "BASS.FRAME.DOPPLER_FACTOR.001",
        ),
    }
    require({(a, b) for a, b, _ in seen} == expected, "unexpected internal edge set")

    # The graph stores formula -> prerequisite. Reversing it gives execution order.
    execution_adjacency = {formula_id: set() for formula_id in ids}
    execution_indegree = {formula_id: 0 for formula_id in ids}
    for source, target in expected:
        execution_adjacency[target].add(source)
        execution_indegree[source] += 1
    queue = sorted(k for k, value in execution_indegree.items() if value == 0)
    visited: list[str] = []
    while queue:
        node = queue.pop(0)
        visited.append(node)
        for successor in sorted(execution_adjacency[node]):
            execution_indegree[successor] -= 1
            if execution_indegree[successor] == 0:
                queue.append(successor)
                queue.sort()
    require(len(visited) == len(ids), "internal dependency graph contains a cycle")


def check_formula_hashes(data: dict[str, Any]) -> None:
    for row in data["formulas"]:
        semantic_hash = row.get("semantic_hash")
        require(isinstance(semantic_hash, str) and HEX64.fullmatch(semantic_hash), "bad semantic hash")
        require(
            semantic_hash == sha256_object(row.get("semantic_projection")),
            f"semantic hash mismatch: {row['formula_id']}",
        )
    registry_hash = data.get("registry_semantic_hash")
    require(isinstance(registry_hash, str) and HEX64.fullmatch(registry_hash), "bad registry hash")
    require(
        registry_hash == sha256_object(data.get("registry_semantic_projection")),
        "registry semantic hash mismatch",
    )


def check_aberration(row: dict[str, Any]) -> None:
    ir = row["equation_ir"]

    # Only coefficient-bearing executable slots are subject to the singular-form
    # prohibition.  known_limits deliberately preserves the superseded algebraic
    # form as provenance for the exact regularization identity.
    executable_serialized = json.dumps(
        {
            "target": ir.get("target"),
            "terms": ir.get("terms"),
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    history_serialized = json.dumps(
        {"known_limits": ir.get("known_limits", [])},
        ensure_ascii=False,
        sort_keys=True,
    )
    require("gamma^2/(gamma+1)" in executable_serialized, "regular coefficient missing")
    require(
        "(gamma-1)/beta_squared" not in executable_serialized,
        "singular coefficient serialized in executable aberration expression",
    )
    require(
        "(gamma-1)/beta_squared" in history_serialized
        and "gamma^2/(gamma+1)" in history_serialized,
        "regularization equivalence provenance missing",
    )
    require(
        ir["domain"].get("zero_boost") == "direct evaluation without 0/0",
        "zero-boost direct evaluation missing",
    )
    require(ir.get("base_map_orientation") == "SOURCE_SKY_TO_TARGET_SKY", "base-map orientation missing")
    require(ir.get("inverse_map_for_target_evaluation") == "A_(-beta)", "inverse map missing")


def check_blackbody(row: dict[str, Any]) -> None:
    require(
        row["dependencies"]
        == [
            "BASS.FRAME.ABERRATED_DIRECTION.001",
            "BASS.FRAME.DOPPLER_FACTOR.001",
        ],
        "blackbody dependencies must contain base map and fiber weight",
    )
    roles = {
        item["formula_id"]: item["role"] for item in row["dependency_roles"]
    }
    require(
        roles
        == {
            "BASS.FRAME.ABERRATED_DIRECTION.001": "BASE_MAP_REQUIRED",
            "BASS.FRAME.DOPPLER_FACTOR.001": "FIBER_WEIGHT_REQUIRED",
        },
        "blackbody dependency roles are wrong",
    )
    ir = row["equation_ir"]
    require(ir.get("mathematical_kind") == "WEIGHTED_SECTION_PUSHFORWARD", "wrong blackbody kind")
    operator = ir.get("operator_ir")
    require(isinstance(operator, dict), "blackbody operator_ir missing")
    require(
        operator["base_map"].get("target_evaluation_uses") == "INVERSE_MAP",
        "target evaluation must use inverse aberration",
    )
    require(operator["fiber_weight"].get("exponent") == 1, "Doppler weight must be one")
    require(
        operator["defining_equation"]
        == {
            "lhs": "Pullback[A_beta,temperature_tilde]",
            "rhs": "doppler_factor_source*temperature_source",
        },
        "defining weighted-pullback equation mismatch",
    )
    serialized = json.dumps(ir, ensure_ascii=False, sort_keys=True)
    require("inverse_aberration_beta" in serialized, "source-direction pullback missing")
    require("POSITIVE_REAL_KELVIN" in serialized, "positive Kelvin fiber missing")


def check_photon(row: dict[str, Any]) -> None:
    ir = row["equation_ir"]
    target = ir.get("target", "")
    require("/ds" in target, f"physical ray parameter absent: {row['formula_id']}")
    require("/d ell" not in target, f"multipole/ray symbol collision: {row['formula_id']}")
    assumptions = "\n".join(ir.get("assumptions", []))
    require("ray_parameter s = c*t" in assumptions, "s=c*t assumption missing")
    require(
        "normal_congruence_acceleration A_normal^a = 0" in assumptions,
        "geodesic-normal assumption missing",
    )
    require(
        row.get("structural_specializations")
        == [
            {
                "formula_id": "BASS.GEO.NORMAL_ACCELERATION.001",
                "role": "SPECIALIZES_UNDER_ZERO",
                "value": "A_normal^a=0",
            }
        ],
        "normal-acceleration structural specialization mismatch",
    )


def verify(data: dict[str, Any], receipt: dict[str, Any] | None) -> dict[str, Any]:
    require(data.get("schema_version") == "1.1.0", "schema_version must be 1.1.0")
    require(data.get("stage_id") == "SYNC_MAP_02E_R1_SEMANTIC_HARDENING", "bad stage_id")
    require(data.get("repository_scope") == "BASS_ONLY", "not BASS-only")
    require(data.get("owner") == "bass", "owner must be bass")
    require(data.get("formula_count") == 6, "formula_count must be six")
    require("consumer_bindings" not in data, "legacy consumer_bindings must be absent")
    require(data.get("claim_boundary") == EXPECTED_CLAIMS, "claim boundary mismatch")

    rows = formula_map(data)
    require(set(rows) == set(FORMULA_IDS), "formula set mismatch")
    require(set(data.get("declared_consumer_targets", {})) == set(FORMULA_IDS), "consumer-target map mismatch")
    for row in rows.values():
        require(row.get("owner") == "bass", "non-BASS formula owner")
        require(row.get("authority_effect") == "AUTHORITATIVE_DERIVATION", "bad authority effect")
        require("consumer_repositories" not in row, "legacy formula consumer field present")
        require(isinstance(row.get("declared_consumer_targets"), list), "consumer target list missing")

    check_aberration(rows["BASS.FRAME.ABERRATED_DIRECTION.001"])
    check_blackbody(rows["BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001"])
    check_photon(rows["BASS.PHOTON.DIRECTION_FLOW.001"])
    check_photon(rows["BASS.PHOTON.ENERGY_DRIFT.001"])
    require(
        rows["BASS.PHOTON.DIRECTION_FLOW.001"]["equation_ir"].get(
            "screen_basis_transport_status"
        )
        == "EXCLUDED_NEXT_BASS_NODE",
        "screen-transport firewall missing",
    )

    check_graph(data)
    check_formula_hashes(data)

    if receipt is not None:
        require(
            receipt.get("output_registry_semantic_hash")
            == data["registry_semantic_hash"],
            "build receipt registry hash mismatch",
        )
        require(receipt.get("formula_count") == 6, "build receipt formula count mismatch")

    return {
        "stage_id": data["stage_id"],
        "repository_scope": data["repository_scope"],
        "formula_count": data["formula_count"],
        "internal_dependency_edge_count": len(data["internal_dependency_edges"]),
        "external_dependency_edge_count": len(data["external_dependency_edges"]),
        "registry_semantic_hash": data["registry_semantic_hash"],
        "status": "PASS",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--receipt", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    data = json.loads(args.input.read_text(encoding="utf-8"))
    receipt = None
    if args.receipt is not None:
        receipt = json.loads(args.receipt.read_text(encoding="utf-8"))
    result = verify(data, receipt)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
