#!/usr/bin/env python3
"""Fail-closed verifier for the BASS-only 02F-R2A role graph."""

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
    / "SYNC_MAP_02F_R2A"
    / "FORMULA_CONSUMER_ROLE_GRAPH.json"
)

EXPECTED_PARENT = "6bb65476a87d1ac8daa9f7239d884c369c51ce33"
EXPECTED_STATE_SHA256 = (
    "5a5042d4b4cd653b3455dda45f9cd5aa67314cb03416b532ff34dbc9695f621c"
)
EXPECTED_REGISTRY_HASH = (
    "5951f566d911c81848743055c1573f6d11b0b00937d36747b71e6bc12dd96416"
)
EXPECTED_EXPORT_SHA256 = (
    "d3398cc283f1d88301496aff3014a9dbc57de4bceaa89de997e687c1f8c44723"
)
EXPECTED_FORMULA_HASHES = {
    "BASS.FRAME.ABERRATED_DIRECTION.001": (
        "b20aa445f5e2890674480a6e8e71fd919aa9efd13a1a8c4780e98b67b9974eec"
    ),
    "BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001": (
        "99ededbaa9c04ab51f2ffda4c19a55236b243021271445d3dad916e2e660c143"
    ),
    "BASS.FRAME.DOPPLER_FACTOR.001": (
        "fb56218a0256edde59a1d89eb4e3ce69ce82800d852908ee84ce8aec83f2fb47"
    ),
    "BASS.FRAME.SOLID_ANGLE_JACOBIAN.001": (
        "0436b513724b09fe826aa486c5dd3def19d0dc5e6daf9fabdd8d899fd1618dc4"
    ),
    "BASS.PHOTON.DIRECTION_FLOW.001": (
        "1eb20b3b46b596139d781d529a1511df983c2b6c00fbe85208ef03e7888f08ce"
    ),
    "BASS.PHOTON.ENERGY_DRIFT.001": (
        "840fe1d68d87b78bb5b5d831fb3d8025b26c29fda1f9da49b0f387e1a8d7bcfd"
    ),
}
EXPECTED_PAIRS = {
    ("BASS.FRAME.ABERRATED_DIRECTION.001", "rec_bianchi"),
    ("BASS.FRAME.DOPPLER_FACTOR.001", "rec_bianchi"),
    ("BASS.PHOTON.DIRECTION_FLOW.001", "rec_bianchi"),
    ("BASS.PHOTON.ENERGY_DRIFT.001", "rec_bianchi"),
    ("BASS.PHOTON.DIRECTION_FLOW.001", "rei_bianchi"),
    ("BASS.PHOTON.ENERGY_DRIFT.001", "rei_bianchi"),
    ("BASS.FRAME.ABERRATED_DIRECTION.001", "htt_base"),
    ("BASS.FRAME.DOPPLER_FACTOR.001", "htt_base"),
    ("BASS.FRAME.SOLID_ANGLE_JACOBIAN.001", "htt_base"),
    ("BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001", "htt_base"),
}
EXPECTED_SYMBOLS = {
    "aberrate_direction",
    "doppler_factor",
    "normal_frame_characteristic.D0_direction_normal_s_inv",
    "normal_frame_characteristic.R_normal_s_inv",
    "SpectrumLane.redshift_coeff",
    "aberrate_sky_direction",
    "deaberrate_sky_direction",
    "doppler_factor_unboosted",
    "doppler_factor_boosted",
    "solid_angle_jacobian",
    "pullback_thermodynamic_temperature_field",
    "thermodynamic_temperature_pullback",
}
REQUIRED_RELATION_FIELDS = {
    "algebraic_relation",
    "domain_relation",
    "convention_adapter",
    "unit_parameter_adapter",
    "input_policy",
    "numerical_policy",
    "validity_subspace",
    "authority_effect",
    "parity_status",
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
    node_set = set(nodes)
    require(len(node_set) == len(nodes), "duplicate DAG node")
    indegree = {node: 0 for node in nodes}
    outgoing: dict[str, list[str]] = defaultdict(list)
    for edge in edges:
        require(isinstance(edge, list) and len(edge) == 2, "malformed DAG edge")
        source, target = edge
        require(source in node_set and target in node_set, "DAG edge references unknown node")
        outgoing[source].append(target)
        indegree[target] += 1
    queue = deque(node for node, degree in indegree.items() if degree == 0)
    visited = 0
    while queue:
        node = queue.popleft()
        visited += 1
        for target in outgoing[node]:
            indegree[target] -= 1
            if indegree[target] == 0:
                queue.append(target)
    return visited == len(nodes)


def verify(data: dict[str, Any]) -> dict[str, Any]:
    require(data.get("repository_scope") == "BASS_ONLY", "scope is not BASS_ONLY")
    require(data.get("owner") == "bass", "owner is not bass")
    require("consumer_bindings" not in data, "overstated consumer_bindings key present")
    require("relation_class_vocabulary" not in data, "overloaded relation vocabulary present")

    ancestry = data.get("normal_ancestry", {})
    require(ancestry.get("parent_commit") == EXPECTED_PARENT, "normal ancestry mismatch")
    require(
        ancestry.get("state_surface_registry_sha256") == EXPECTED_STATE_SHA256,
        "state-surface registry SHA-256 mismatch",
    )
    require(
        ancestry.get("hardened_formula_registry_semantic_hash")
        == EXPECTED_REGISTRY_HASH,
        "hardened formula registry hash mismatch",
    )
    require(
        ancestry.get("hardened_formula_export_sha256") == EXPECTED_EXPORT_SHA256,
        "hardened formula export SHA-256 mismatch",
    )

    convention = data.get("convention_contract", {})
    require(convention.get("ray_length_parameter") == "s=c*t with dimension L", "s=c*t missing")
    require(convention.get("angular_multipole_rank") == "ell", "ell rank contract missing")
    require("ell with dimension L" not in json.dumps(convention), "legacy ell ray length present")
    require(convention.get("normal_congruence_acceleration") is not None, "normal acceleration typing absent")

    count_contract = data.get("count_contract", {})
    require(count_contract == {
        "formula_consumer_pairs": 10,
        "implementation_role_rows": 11,
        "named_source_symbols": 12,
        "explicit_absent_implementation_slots": 1,
    }, "count contract mismatch")

    formulas = data.get("authority_formulas", [])
    formula_map = rows_by_id(formulas, "formula_id")
    require(set(formula_map) == set(EXPECTED_FORMULA_HASHES), "authority formula set mismatch")
    for formula_id, expected_hash in EXPECTED_FORMULA_HASHES.items():
        require(
            formula_map[formula_id].get("semantic_hash") == expected_hash,
            f"semantic hash mismatch for {formula_id}",
        )
        require(
            "declared_consumer_targets" in formula_map[formula_id],
            f"declared targets missing for {formula_id}",
        )

    pairs = data.get("formula_consumer_pairs", [])
    pair_map = rows_by_id(pairs, "pair_id")
    require(len(pairs) == 10, "formula-consumer pair count mismatch")
    observed_pairs = {
        (row.get("formula_id"), row.get("consumer_repository")) for row in pairs
    }
    require(observed_pairs == EXPECTED_PAIRS, "formula-consumer pair coverage mismatch")
    for row in pairs:
        require("relation_class" not in row, f"overloaded relation_class in {row['pair_id']}")
        missing = REQUIRED_RELATION_FIELDS - set(row)
        require(not missing, f"missing relation fields in {row['pair_id']}: {sorted(missing)}")
        require(row.get("formula_id") in formula_map, "pair references unknown formula")

    roles = data.get("implementation_roles", [])
    role_map = rows_by_id(roles, "role_id")
    require(len(roles) == 11, "implementation-role row count mismatch")
    for row in roles:
        require(row.get("pair_id") in pair_map, f"role references unknown pair: {row['role_id']}")
        require(isinstance(row.get("source_symbols"), list), "source_symbols must be a list")
        require(isinstance(row.get("implements_full_formula"), bool), "full-formula flag must be Boolean")

    named_symbols = [symbol for row in roles for symbol in row["source_symbols"]]
    require(len(named_symbols) == 12, "named source-symbol count mismatch")
    require(set(named_symbols) == EXPECTED_SYMBOLS, "named source-symbol inventory mismatch")
    require(len(set(named_symbols)) == 12, "duplicate named source symbol")

    absent = [
        row for row in roles if row.get("role_type") == "ABSENT_IMPLEMENTATION_SLOT"
    ]
    require(len(absent) == 1, "explicit absent implementation count mismatch")
    require(absent[0].get("pair_id") == "02F-R2A-REI-DIRECTION-FLOW", "wrong absent slot")
    require(absent[0].get("source_symbols") == [], "absent slot has source symbols")
    require(absent[0].get("implements_full_formula") is False, "absent slot promoted")

    blackbody_roles = [
        row for row in roles if row.get("pair_id") == "02F-R2A-HTT-BLACKBODY-T"
    ]
    require(len(blackbody_roles) == 2, "HTT blackbody role split missing")
    blackbody_by_type = {row.get("role_type"): row for row in blackbody_roles}
    require(set(blackbody_by_type) == {
        "FULL_FIELD_PULLBACK",
        "PREPULLED_VALUE_PRIMITIVE",
    }, "HTT blackbody role types mismatch")
    full_role = blackbody_by_type["FULL_FIELD_PULLBACK"]
    primitive_role = blackbody_by_type["PREPULLED_VALUE_PRIMITIVE"]
    require(full_role.get("implements_full_formula") is True, "full pullback not marked full")
    require(primitive_role.get("implements_full_formula") is False, "primitive promoted to full formula")
    require(
        any("inverse-aberrated" in item for item in primitive_role.get("preconditions", [])),
        "pre-pulled primitive precondition missing",
    )

    rei_energy = pair_map["02F-R2A-REI-ENERGY-DRIFT"]
    require(
        rei_energy.get("exact_relation_residual")
        == "Expand(((-H)-(-H-sigmaEE))-sigmaEE)=0",
        "REI exact energy-drift residual weakened",
    )
    require(
        rei_energy.get("parity_status")
        == "GENERIC_PARITY_FORBIDDEN_CONTROL_SUBSPACE_ONLY",
        "REI generic parity incorrectly admitted",
    )

    state_firewall = data.get("state_surface_firewall", {})
    require("NONINVERTIBLE" in state_firewall.get("j_and_g", ""), "J/G projection firewall absent")
    require("NO_IMPLICIT" in state_firewall.get("polarization", ""), "polarization firewall absent")

    dag = data.get("stage_dag", {})
    nodes = dag.get("nodes", [])
    edges = dag.get("edges", [])
    require(graph_is_acyclic(nodes, edges), "stage DAG is cyclic")
    require(
        ["BASS_STATE_SURFACE_REGISTRY", "FORMULA_CONSUMER_ROLE_GRAPH"] in edges,
        "state registry does not precede role graph",
    )

    return {
        "stage_id": data.get("stage_id"),
        "repository_scope": data.get("repository_scope"),
        "formula_count": len(formulas),
        "formula_consumer_pair_count": len(pairs),
        "implementation_role_count": len(roles),
        "named_source_symbol_count": len(named_symbols),
        "absent_implementation_slot_count": len(absent),
        "htt_blackbody_role_count": len(blackbody_roles),
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
