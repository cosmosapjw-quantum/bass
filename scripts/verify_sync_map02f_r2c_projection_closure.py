#!/usr/bin/env python3
"""Fail-closed verifier for the BASS-only 02F-R2C certificate graph."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict, deque
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GRAPH = (
    ROOT
    / "docs"
    / "bass_master_ssot_v2"
    / "SYNC_MAP_02F_R2C"
    / "PROJECTION_CLOSURE_CERTIFICATE_GRAPH.json"
)

EXPECTED_PARENT = "0967a801d7baa9c4845cbcf07d9f967ae48f37c5"
EXPECTED_NATIVE_ROLE_HEAD = "bc7ea693bd8ac4f14376aaac51d4007467702803"
EXPECTED_ROLE_GRAPH_SHA256 = (
    "23e4f1a01cbb7f5844cb151148a8ef359c17a27d4317e9dd4c6227e5c0f1bfe6"
)
EXPECTED_ROLE_RECEIPT_SHA256 = (
    "3e675324b1abe8673df3d7111d811cfffe9cea4edaeb9a72732dea039daec59d"
)
EXPECTED_STATE_SHA256 = (
    "5a5042d4b4cd653b3455dda45f9cd5aa67314cb03416b532ff34dbc9695f621c"
)
EXPECTED_FORMULA_HASH = (
    "5951f566d911c81848743055c1573f6d11b0b00937d36747b71e6bc12dd96416"
)

EXPECTED_COUNTS = {
    "certificate_families": 4,
    "relation_certificate_rows": 6,
    "exact_hostile_or_control_witnesses": 6,
    "explicit_blocked_promotions": 3,
}

EXPECTED_FAMILIES = {
    "ANGULAR_REPRESENTATION_CERTIFICATE": {
        "GRID_TO_PSTF",
        "PSTF_TO_GRID",
    },
    "SPECTRAL_PROJECTION_CLOSURE_CERTIFICATE": {
        "PSTF_TO_J",
        "GRID_TO_G",
    },
    "MOMENT_EXCHANGE_CERTIFICATE": {
        "KINETIC_TO_FLUID_SUMMARY",
    },
    "POLARIZED_SCREEN_CERTIFICATE": {
        "SCALAR_TO_POLARIZED_PROHIBITED",
    },
}

EXPECTED_RELATIONS = {
    "GRID_TO_PSTF": (
        "ANGULAR_REPRESENTATION_CERTIFICATE",
        "ANALYSIS",
        "SPECIFIED_RUNTIME_CERTIFICATE_PENDING",
    ),
    "PSTF_TO_GRID": (
        "ANGULAR_REPRESENTATION_CERTIFICATE",
        "SYNTHESIS",
        "SPECIFIED_RUNTIME_CERTIFICATE_PENDING",
    ),
    "PSTF_TO_J": (
        "SPECTRAL_PROJECTION_CLOSURE_CERTIFICATE",
        "NONINVERTIBLE_PROJECTION",
        "CLOSURE_REQUIRED_NOT_ADMITTED",
    ),
    "GRID_TO_G": (
        "SPECTRAL_PROJECTION_CLOSURE_CERTIFICATE",
        "NONINVERTIBLE_PROJECTION",
        "CLOSURE_REQUIRED_NOT_ADMITTED",
    ),
    "KINETIC_TO_FLUID_SUMMARY": (
        "MOMENT_EXCHANGE_CERTIFICATE",
        "COVARIANT_MOMENT_REDUCTION",
        "EXCHANGE_LEDGER_REQUIRED_NOT_ADMITTED",
    ),
    "SCALAR_TO_POLARIZED_PROHIBITED": (
        "POLARIZED_SCREEN_CERTIFICATE",
        "NO_IMPLICIT_PROMOTION",
        "FORBIDDEN_UNTIL_ALL_POLARIZED_PREREQUISITES_EXIST",
    ),
}

EXPECTED_WITNESSES = {
    "GAUSS_LEGENDRE_L2_ROUNDTRIP",
    "RADIAL_MULTIPLICATION_WORK_ORDER",
    "G_TWO_BIN_FREQUENCY_CLOSURE_NOGO",
    "RADIATION_MATTER_FOUR_FORCE_CANCELLATION",
    "SCREEN_PROJECTOR_RATIONAL_DIRECTION",
    "SCALAR_INTENSITY_DOES_NOT_FIX_POLARIZATION",
}

EXPECTED_BLOCKED = {
    "PSTF_TO_J_AS_STATE_EQUIVALENCE",
    "GRID_TO_G_GENERIC_SCALAR_SOURCE_CLOSURE",
    "SCALAR_TO_POLARIZED_STATE",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def rows_by_id(rows: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    result = {row.get(key): row for row in rows}
    require(None not in result, f"row without {key}")
    require(len(result) == len(rows), f"duplicate {key}")
    return result


def graph_is_acyclic(nodes: list[str], edges: list[list[str]]) -> bool:
    require(len(nodes) == len(set(nodes)), "duplicate DAG node")
    node_set = set(nodes)
    indegree = {node: 0 for node in nodes}
    outgoing: dict[str, list[str]] = defaultdict(list)
    for edge in edges:
        require(isinstance(edge, list) and len(edge) == 2, "malformed DAG edge")
        source, target = edge
        require(source in node_set and target in node_set, "unknown DAG node")
        indegree[target] += 1
        outgoing[source].append(target)
    queue = deque(node for node, degree in indegree.items() if degree == 0)
    visited = 0
    while queue:
        source = queue.popleft()
        visited += 1
        for target in outgoing[source]:
            indegree[target] -= 1
            if indegree[target] == 0:
                queue.append(target)
    return visited == len(nodes)


def verify(data: dict[str, Any]) -> dict[str, Any]:
    require(data.get("repository_scope") == "BASS_ONLY", "scope is not BASS_ONLY")
    require(data.get("owner") == "bass", "owner is not bass")
    require("consumer_runtime_bindings" not in data, "runtime bindings overstated")

    ancestry = data.get("normal_ancestry", {})
    require(ancestry.get("parent_commit") == EXPECTED_PARENT, "parent mismatch")
    require(
        ancestry.get("native_role_graph_source_head") == EXPECTED_NATIVE_ROLE_HEAD,
        "native role-graph head mismatch",
    )
    require(
        ancestry.get("role_graph_sha256") == EXPECTED_ROLE_GRAPH_SHA256,
        "role-graph SHA-256 mismatch",
    )
    require(
        ancestry.get("role_graph_wolfram_receipt_sha256")
        == EXPECTED_ROLE_RECEIPT_SHA256,
        "role-graph receipt SHA-256 mismatch",
    )
    require(
        ancestry.get("state_surface_registry_sha256") == EXPECTED_STATE_SHA256,
        "state registry SHA-256 mismatch",
    )
    require(
        ancestry.get("hardened_formula_registry_semantic_hash")
        == EXPECTED_FORMULA_HASH,
        "formula registry hash mismatch",
    )

    counts = data.get("count_contract", {})
    require(counts == EXPECTED_COUNTS, "count contract mismatch")

    families = data.get("certificate_families", [])
    family_map = rows_by_id(families, "certificate_family_id")
    require(set(family_map) == set(EXPECTED_FAMILIES), "family inventory mismatch")
    for family_id, expected_relations in EXPECTED_FAMILIES.items():
        row = family_map[family_id]
        require(
            set(row.get("applies_to_relations", [])) == expected_relations,
            f"family relation coverage mismatch for {family_id}",
        )
        required_fields = row.get("required_fields")
        require(isinstance(required_fields, list) and required_fields, "empty obligations")
        require(len(required_fields) == len(set(required_fields)), "duplicate obligation")
        require(
            row.get("runtime_status") == "CERTIFICATE_SCHEMA_ONLY",
            "runtime certificate overstated",
        )

    relations = data.get("relation_certificates", [])
    relation_map = rows_by_id(relations, "relation_id")
    require(set(relation_map) == set(EXPECTED_RELATIONS), "relation inventory mismatch")
    for relation_id, expected in EXPECTED_RELATIONS.items():
        row = relation_map[relation_id]
        observed = (
            row.get("certificate_family_id"),
            row.get("direction"),
            row.get("status"),
        )
        require(observed == expected, f"relation contract mismatch for {relation_id}")

    require(
        relation_map["PSTF_TO_J"].get("invertibility_claim") == "FORBIDDEN",
        "J projection promoted to equivalence",
    )
    require(
        relation_map["GRID_TO_G"].get("invertibility_claim") == "FORBIDDEN",
        "G projection promoted to equivalence",
    )
    require(
        relation_map["SCALAR_TO_POLARIZED_PROHIBITED"].get("direction")
        == "NO_IMPLICIT_PROMOTION",
        "scalar state promoted to polarization",
    )

    rank = data.get("rank_and_aliasing_policy", {})
    require(rank.get("hardcoded_numeric_ell_cutoff_forbidden") is True, "ell hardcode allowed")
    require(rank.get("ell_target") == "RUNTIME_PARAMETER", "ell_target not runtime")
    require(
        rank.get("ell_work") == "ADAPTIVE_OR_EXPLICIT_RUNTIME_PARAMETER",
        "ell_work not adaptive or explicit",
    )
    require(
        rank.get("radial_polynomial_product_sufficient_condition")
        == "radial_work_order >= radial_output_order + radial_source_order",
        "radial anti-aliasing condition weakened",
    )
    require(
        rank.get("angular_harmonic_product_sufficient_condition")
        == "angular_work_rank >= angular_output_rank + angular_source_rank",
        "angular anti-aliasing condition weakened",
    )
    require(
        "DOES_NOT_CERTIFY" in rank.get("dealiasing_claim", ""),
        "linear roundtrip incorrectly promoted to source-product certificate",
    )

    witnesses = data.get("exact_witnesses", [])
    witness_map = rows_by_id(witnesses, "witness_id")
    require(set(witness_map) == EXPECTED_WITNESSES, "witness inventory mismatch")

    roundtrip = witness_map["GAUSS_LEGENDRE_L2_ROUNDTRIP"]
    require(roundtrip.get("quadrature_exactness_degree") == 5, "quadrature degree mismatch")
    require(roundtrip.get("expected_analysis_residuals") == [0, 0, 0], "analysis residual changed")
    require(roundtrip.get("expected_grid_roundtrip_residuals") == [0, 0, 0], "grid residual changed")

    radial = witness_map["RADIAL_MULTIPLICATION_WORK_ORDER"]
    require(radial.get("minimum_radial_work_order") == 2, "radial work order weakened")
    require(
        radial.get("dropped_high_order_coefficient_if_truncated_at_output_order") == 8,
        "radial alias witness changed",
    )

    g_nogo = witness_map["G_TWO_BIN_FREQUENCY_CLOSURE_NOGO"]
    require(g_nogo.get("integrated_G_A") == g_nogo.get("integrated_G_B") == 1, "G witness mismatch")
    require(g_nogo.get("loss_A_minus_loss_B") == -3, "G loss witness mismatch")
    require(g_nogo.get("generic_scalar_closure") is False, "G closure incorrectly admitted")

    four_force = witness_map["RADIATION_MATTER_FOUR_FORCE_CANCELLATION"]
    require(four_force.get("expected_total_residual") == [0, 0, 0, 0], "four-force residual changed")

    screen = witness_map["SCREEN_PROJECTOR_RATIONAL_DIRECTION"]
    require(screen.get("unit_direction") == ["3/5", "4/5", "0"], "screen direction changed")
    require(screen.get("expected_trace") == 2, "screen trace changed")

    polarization = witness_map["SCALAR_INTENSITY_DOES_NOT_FIX_POLARIZATION"]
    require(polarization.get("trace_difference") == 0, "intensity equality witness changed")
    require(polarization.get("frobenius_difference_squared") == 8, "polarization witness changed")

    blocked = data.get("explicit_blocked_promotions", [])
    blocked_map = rows_by_id(blocked, "promotion")
    require(set(blocked_map) == EXPECTED_BLOCKED, "blocked promotion inventory mismatch")

    dag = data.get("stage_dag", {})
    nodes = dag.get("nodes", [])
    edges = dag.get("edges", [])
    require(graph_is_acyclic(nodes, edges), "stage DAG is cyclic")
    require(
        ["FORMULA_CONSUMER_ROLE_GRAPH", "PROJECTION_CLOSURE_CERTIFICATE_GRAPH"] in edges,
        "R2A does not precede R2C",
    )
    require(
        ["PROJECTION_CLOSURE_CERTIFICATE_GRAPH", "CONSUMER_BINDING_CONTRACTS"] in edges,
        "R2C does not precede consumer bindings",
    )

    literature = data.get("literature_regression", [])
    require(literature, "literature regression missing")
    require(
        all(row.get("authority_effect") == "NONE" for row in literature),
        "literature given authority over BASS contract",
    )

    require(
        data.get("status") == "IMPLEMENTED_CONTRACT_LOCAL_REPLAY_REQUIRED",
        "stage status overstated",
    )

    return {
        "stage_id": data.get("stage_id"),
        "repository_scope": data.get("repository_scope"),
        "certificate_family_count": len(families),
        "relation_certificate_count": len(relations),
        "exact_witness_count": len(witnesses),
        "blocked_promotion_count": len(blocked),
        "dag_acyclic": True,
        "status": "PASS",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--graph", type=Path, default=DEFAULT_GRAPH)
    args = parser.parse_args()
    data = json.loads(args.graph.read_text(encoding="utf-8"))
    print(json.dumps(verify(data), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
