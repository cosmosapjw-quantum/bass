#!/usr/bin/env python3
"""Fail-closed verifier for the BASS-only SYNC-MAP-02F-R2 state registry."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

EXPECTED_STATES = {
    "GRID_F_Q_E",
    "PSTF_F_AELL_Q",
    "J_I_AELL",
    "G_ANGULAR_ENERGY",
    "FLUID_COMPONENT_SUMMARY",
    "POLARIZED_COHERENCY",
}
EXPECTED_RELATIONS = {
    "GRID_TO_PSTF",
    "PSTF_TO_GRID",
    "PSTF_TO_J",
    "GRID_TO_G",
    "KINETIC_TO_FLUID_SUMMARY",
    "SCALAR_TO_POLARIZED_PROHIBITED",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def keyed(rows: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    result = {row.get(key): row for row in rows}
    require(None not in result, f"row missing {key}")
    require(len(result) == len(rows), f"duplicate {key}")
    return result


def verify(data: dict[str, Any]) -> dict[str, Any]:
    require(data.get("schema_version") == "1.0.0", "schema version mismatch")
    require(
        data.get("stage_id") == "SYNC_MAP_02F_R2_BASS_STATE_SURFACE_REGISTRY",
        "stage id mismatch",
    )
    require(data.get("repository_scope") == "BASS_ONLY", "scope is not BASS_ONLY")
    require(data.get("owner") == "bass", "owner is not bass")

    ancestry = data.get("normal_ancestry", {})
    require(
        ancestry.get("parent_commit")
        == "8b73919e0e2a2326c338c796ac80b0684fe49db1",
        "normal ancestry parent mismatch",
    )
    require(
        ancestry.get("native_replay_source_head")
        == "65be780c06b014e8b699a8af4835b2290f39b252",
        "native replay source head mismatch",
    )
    require(
        ancestry.get("hardened_formula_registry_semantic_hash")
        == "5951f566d911c81848743055c1573f6d11b0b00937d36747b71e6bc12dd96416",
        "hardened registry semantic hash mismatch",
    )

    relation_contract = data.get("relation_graph_contract", {})
    require(relation_contract.get("required_formula_consumer_pairs") == 10, "pair count")
    require(relation_contract.get("required_implementation_role_rows") == 11, "role count")
    require(relation_contract.get("required_named_source_symbols") == 12, "symbol count")
    require(relation_contract.get("required_absent_implementation_slots") == 1, "absent count")

    ell_policy = data.get("ell_policy", {})
    require(ell_policy.get("hardcoded_numeric_cutoff_forbidden") is True, "hardcoded ell cutoff allowed")
    require(ell_policy.get("target_cutoff") == "RUNTIME_PARAMETER", "target cutoff not runtime")

    states = keyed(data.get("states", []), "state_id")
    relations = keyed(data.get("relations", []), "relation_id")
    require(set(states) == EXPECTED_STATES, "state surface set mismatch")
    require(set(relations) == EXPECTED_RELATIONS, "relation set mismatch")

    for state_id in ("GRID_F_Q_E", "PSTF_F_AELL_Q", "POLARIZED_COHERENCY"):
        require(states[state_id].get("spectral_variable_retained") is True, f"{state_id} lost q")
    for state_id in ("J_I_AELL", "G_ANGULAR_ENERGY", "FLUID_COMPONENT_SUMMARY"):
        require(states[state_id].get("spectral_variable_retained") is False, f"{state_id} falsely retains q")

    for relation_id in ("GRID_TO_PSTF", "PSTF_TO_GRID"):
        row = relations[relation_id]
        require(
            row.get("semantic_relation")
            == "REPRESENTATION_EQUIVALENT_WITH_DECLARED_BASIS_AND_MEASURE",
            f"{relation_id} representation relation mismatch",
        )
        require(
            row.get("runtime_parity") == "WITHHELD_PENDING_NUMERICAL_TRANSFORM_CERTIFICATE",
            f"{relation_id} prematurely claims runtime parity",
        )
        required = set(row.get("required_certificates", []))
        require("FORWARD_INVERSE_RESIDUAL" in required, f"{relation_id} missing inverse residual")

    for relation_id in ("PSTF_TO_J", "GRID_TO_G", "KINETIC_TO_FLUID_SUMMARY"):
        row = relations[relation_id]
        require(row.get("invertibility") == "NONINVERTIBLE_IN_GENERAL", f"{relation_id} invertibility")
        require(
            row.get("runtime_parity") == "NOT_APPLICABLE_AS_STATE_EQUIVALENCE",
            f"{relation_id} falsely treated as state parity",
        )

    require(
        "SOURCE_GRID_QUADRATURE_OR_SPECTRAL_CLOSURE"
        in relations["PSTF_TO_J"].get("required_certificates", []),
        "J projection closure certificate missing",
    )
    require(
        "SOURCE_GRID_QUADRATURE_OR_SPECTRAL_CLOSURE"
        in relations["GRID_TO_G"].get("required_certificates", []),
        "G projection closure certificate missing",
    )

    polarized = relations["SCALAR_TO_POLARIZED_PROHIBITED"]
    require(polarized.get("runtime_parity") == "FORBIDDEN", "scalar polarization promotion allowed")
    polarized_requirements = set(polarized.get("required_certificates", []))
    require("SCREEN_BASIS_TRANSPORT" in polarized_requirements, "screen transport missing")
    require("SPIN_PHASE_CONVENTION" in polarized_requirements, "spin phase missing")

    no_go = data.get("closure_no_go", {})
    witness = no_go.get("two_bin_witness", {})
    require(witness.get("integrated_state_A") == witness.get("integrated_state_B") == 1, "no-go states differ")
    require(witness.get("loss_difference") == "chi_1-chi_2", "no-go loss difference mismatch")
    require(
        no_go.get("universal_scalar_closure_condition")
        == ["chi_1=chi_eff", "chi_2=chi_eff"],
        "universal closure condition mismatch",
    )

    claims = set(data.get("claim_boundary", []))
    require("NO_J_OR_G_EXACT_STATE_EQUIVALENCE" in claims, "J/G firewall missing")
    require("NO_CROSS_REPOSITORY_SOURCE_MUTATION" in claims, "cross-repository firewall missing")

    return {
        "stage_id": data["stage_id"],
        "repository_scope": data["repository_scope"],
        "state_count": len(states),
        "relation_count": len(relations),
        "hardened_registry_semantic_hash": ancestry["hardened_formula_registry_semantic_hash"],
        "status": "PASS",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    args = parser.parse_args()
    data = json.loads(args.input.read_text(encoding="utf-8"))
    print(json.dumps(verify(data), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
