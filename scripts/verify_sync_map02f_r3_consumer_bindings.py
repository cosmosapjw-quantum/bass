#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter, deque
from pathlib import Path
from typing import Any

EXPECTED_PARENT = "4a78ea05310126f720719e369a782466fdd1111e"
EXPECTED_COUNTS = {
    "consumers": 3,
    "binding_requests": 10,
    "source_role_pins": 11,
    "named_source_symbols": 12,
    "absent_implementation_slots": 1,
    "owner_formulas": 6,
    "state_surfaces": 6,
    "certificate_families": 4,
    "blocked_promotions": 13,
}
EXPECTED_CONSUMERS = ["rec_bianchi", "rei_bianchi", "htt_base"]
EXPECTED_PAIR_IDS = [
    "02F-R2A-REC-ABERRATION",
    "02F-R2A-REC-DOPPLER",
    "02F-R2A-REC-DIRECTION-FLOW",
    "02F-R2A-REC-ENERGY-DRIFT",
    "02F-R2A-REI-DIRECTION-FLOW",
    "02F-R2A-REI-ENERGY-DRIFT",
    "02F-R2A-HTT-ABERRATION",
    "02F-R2A-HTT-DOPPLER",
    "02F-R2A-HTT-SOLID-ANGLE",
    "02F-R2A-HTT-BLACKBODY-T",
]
EXPECTED_BINDING_IDS = [
    "BINDING-REC-ABERRATION",
    "BINDING-REC-DOPPLER",
    "BINDING-REC-DIRECTION-FLOW",
    "BINDING-REC-ENERGY-DRIFT",
    "BINDING-REI-DIRECTION-FLOW",
    "BINDING-REI-ENERGY-DRIFT",
    "BINDING-HTT-ABERRATION",
    "BINDING-HTT-DOPPLER",
    "BINDING-HTT-SOLID-ANGLE",
    "BINDING-HTT-BLACKBODY-T",
]
EXPECTED_BINDING_CORE = {
    "02F-R2A-REC-ABERRATION": (
        "rec_bianchi",
        "BASS.FRAME.ABERRATED_DIRECTION.001",
        ("ROLE-REC-ABERRATION",),
        ("ANGULAR_REPRESENTATION_CERTIFICATE",),
        "REC_BINDING_RUNTIME_VALIDATION",
    ),
    "02F-R2A-REC-DOPPLER": (
        "rec_bianchi",
        "BASS.FRAME.DOPPLER_FACTOR.001",
        ("ROLE-REC-DOPPLER",),
        ("ANGULAR_REPRESENTATION_CERTIFICATE",),
        "REC_BINDING_RUNTIME_VALIDATION",
    ),
    "02F-R2A-REC-DIRECTION-FLOW": (
        "rec_bianchi",
        "BASS.PHOTON.DIRECTION_FLOW.001",
        ("ROLE-REC-DIRECTION-FLOW",),
        ("ANGULAR_REPRESENTATION_CERTIFICATE",),
        "REC_BINDING_RUNTIME_VALIDATION",
    ),
    "02F-R2A-REC-ENERGY-DRIFT": (
        "rec_bianchi",
        "BASS.PHOTON.ENERGY_DRIFT.001",
        ("ROLE-REC-ENERGY-DRIFT",),
        ("ANGULAR_REPRESENTATION_CERTIFICATE",),
        "REC_BINDING_RUNTIME_VALIDATION",
    ),
    "02F-R2A-REI-DIRECTION-FLOW": (
        "rei_bianchi",
        "BASS.PHOTON.DIRECTION_FLOW.001",
        ("ROLE-REI-DIRECTION-FLOW-ABSENT",),
        (),
        "REI_BINDING_RUNTIME_VALIDATION",
    ),
    "02F-R2A-REI-ENERGY-DRIFT": (
        "rei_bianchi",
        "BASS.PHOTON.ENERGY_DRIFT.001",
        ("ROLE-REI-ENERGY-DRIFT-CONTROL",),
        (),
        "REI_BINDING_RUNTIME_VALIDATION",
    ),
    "02F-R2A-HTT-ABERRATION": (
        "htt_base",
        "BASS.FRAME.ABERRATED_DIRECTION.001",
        ("ROLE-HTT-ABERRATION-BIDIRECTIONAL",),
        (),
        "HTT_BINDING_RUNTIME_VALIDATION",
    ),
    "02F-R2A-HTT-DOPPLER": (
        "htt_base",
        "BASS.FRAME.DOPPLER_FACTOR.001",
        ("ROLE-HTT-DOPPLER-BIDIRECTIONAL",),
        (),
        "HTT_BINDING_RUNTIME_VALIDATION",
    ),
    "02F-R2A-HTT-SOLID-ANGLE": (
        "htt_base",
        "BASS.FRAME.SOLID_ANGLE_JACOBIAN.001",
        ("ROLE-HTT-SOLID-ANGLE-ORACLE",),
        (),
        "HTT_BINDING_RUNTIME_VALIDATION",
    ),
    "02F-R2A-HTT-BLACKBODY-T": (
        "htt_base",
        "BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001",
        ("ROLE-HTT-BLACKBODY-FULL", "ROLE-HTT-BLACKBODY-PREPULLED"),
        (),
        "HTT_BINDING_RUNTIME_VALIDATION",
    ),
}
EXPECTED_FORMULAS = [
    (
        "BASS.FRAME.ABERRATED_DIRECTION.001",
        "b20aa445f5e2890674480a6e8e71fd919aa9efd13a1a8c4780e98b67b9974eec",
        "1",
    ),
    (
        "BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001",
        "99ededbaa9c04ab51f2ffda4c19a55236b243021271445d3dad916e2e660c143",
        "K",
    ),
    (
        "BASS.FRAME.DOPPLER_FACTOR.001",
        "fb56218a0256edde59a1d89eb4e3ce69ce82800d852908ee84ce8aec83f2fb47",
        "1",
    ),
    (
        "BASS.FRAME.SOLID_ANGLE_JACOBIAN.001",
        "0436b513724b09fe826aa486c5dd3def19d0dc5e6daf9fabdd8d899fd1618dc4",
        "1",
    ),
    (
        "BASS.PHOTON.DIRECTION_FLOW.001",
        "1eb20b3b46b596139d781d529a1511df983c2b6c00fbe85208ef03e7888f08ce",
        "L^-1",
    ),
    (
        "BASS.PHOTON.ENERGY_DRIFT.001",
        "840fe1d68d87b78bb5b5d831fb3d8025b26c29fda1f9da49b0f387e1a8d7bcfd",
        "L^-1",
    ),
]
EXPECTED_ROLE_IDS = [
    "ROLE-REC-ABERRATION",
    "ROLE-REC-DOPPLER",
    "ROLE-REC-DIRECTION-FLOW",
    "ROLE-REC-ENERGY-DRIFT",
    "ROLE-REI-DIRECTION-FLOW-ABSENT",
    "ROLE-REI-ENERGY-DRIFT-CONTROL",
    "ROLE-HTT-ABERRATION-BIDIRECTIONAL",
    "ROLE-HTT-DOPPLER-BIDIRECTIONAL",
    "ROLE-HTT-SOLID-ANGLE-ORACLE",
    "ROLE-HTT-BLACKBODY-FULL",
    "ROLE-HTT-BLACKBODY-PREPULLED",
]
EXPECTED_ROLE_CORE = {
    "ROLE-REC-ABERRATION": (
        "02F-R2A-REC-ABERRATION",
        "CONSUMER_IMPLEMENTATION",
        "c4bf37d7271caf651bca41b6eaab8caff436452b",
        "src/full_bianchi_hyrec/background/characteristics.py",
        "f71ec2607daac808b871279ad0893d4653169343",
        ("aberrate_direction",),
        True,
    ),
    "ROLE-REC-DOPPLER": (
        "02F-R2A-REC-DOPPLER",
        "CONSUMER_IMPLEMENTATION",
        "c4bf37d7271caf651bca41b6eaab8caff436452b",
        "src/full_bianchi_hyrec/background/characteristics.py",
        "f71ec2607daac808b871279ad0893d4653169343",
        ("doppler_factor",),
        True,
    ),
    "ROLE-REC-DIRECTION-FLOW": (
        "02F-R2A-REC-DIRECTION-FLOW",
        "CONSUMER_IMPLEMENTATION",
        "c4bf37d7271caf651bca41b6eaab8caff436452b",
        "src/full_bianchi_hyrec/background/characteristics.py",
        "f71ec2607daac808b871279ad0893d4653169343",
        ("normal_frame_characteristic.D0_direction_normal_s_inv",),
        True,
    ),
    "ROLE-REC-ENERGY-DRIFT": (
        "02F-R2A-REC-ENERGY-DRIFT",
        "CONSUMER_IMPLEMENTATION",
        "c4bf37d7271caf651bca41b6eaab8caff436452b",
        "src/full_bianchi_hyrec/background/characteristics.py",
        "f71ec2607daac808b871279ad0893d4653169343",
        ("normal_frame_characteristic.R_normal_s_inv",),
        True,
    ),
    "ROLE-REI-DIRECTION-FLOW-ABSENT": (
        "02F-R2A-REI-DIRECTION-FLOW",
        "ABSENT_IMPLEMENTATION_SLOT",
        "f4eb2c893ce6449f8899ab6f02c83421fc7c7019",
        "src/rei_bianchi/b2b_physical_model.py",
        "b3cc5e45988687b76d5be04c6335009b4c9bd17f",
        (),
        False,
    ),
    "ROLE-REI-ENERGY-DRIFT-CONTROL": (
        "02F-R2A-REI-ENERGY-DRIFT",
        "RESTRICTED_SUBSPACE_IMPLEMENTATION",
        "f4eb2c893ce6449f8899ab6f02c83421fc7c7019",
        "src/rei_bianchi/b2b_physical_model.py",
        "b3cc5e45988687b76d5be04c6335009b4c9bd17f",
        ("SpectrumLane.redshift_coeff",),
        False,
    ),
    "ROLE-HTT-ABERRATION-BIDIRECTIONAL": (
        "02F-R2A-HTT-ABERRATION",
        "BIDIRECTIONAL_DIRECTION_MAP",
        "29427a1f7f2c5d46e43ffe03053c4ac13e969228",
        "htt/obsstat/lorentz_sky_pullback.py",
        "c518cdd0dcdd3ca628c71f6dd9e6a75e174ba805",
        ("aberrate_sky_direction", "deaberrate_sky_direction"),
        True,
    ),
    "ROLE-HTT-DOPPLER-BIDIRECTIONAL": (
        "02F-R2A-HTT-DOPPLER",
        "BIDIRECTIONAL_CHART_FACTOR",
        "29427a1f7f2c5d46e43ffe03053c4ac13e969228",
        "htt/obsstat/lorentz_sky_pullback.py",
        "c518cdd0dcdd3ca628c71f6dd9e6a75e174ba805",
        ("doppler_factor_unboosted", "doppler_factor_boosted"),
        True,
    ),
    "ROLE-HTT-SOLID-ANGLE-ORACLE": (
        "02F-R2A-HTT-SOLID-ANGLE",
        "INDEPENDENT_ORACLE",
        "29427a1f7f2c5d46e43ffe03053c4ac13e969228",
        "htt/obsstat/lorentz_sky_pullback.py",
        "c518cdd0dcdd3ca628c71f6dd9e6a75e174ba805",
        ("solid_angle_jacobian",),
        False,
    ),
    "ROLE-HTT-BLACKBODY-FULL": (
        "02F-R2A-HTT-BLACKBODY-T",
        "FULL_FIELD_PULLBACK",
        "29427a1f7f2c5d46e43ffe03053c4ac13e969228",
        "htt/obsstat/lorentz_sky_pullback.py",
        "c518cdd0dcdd3ca628c71f6dd9e6a75e174ba805",
        ("pullback_thermodynamic_temperature_field",),
        True,
    ),
    "ROLE-HTT-BLACKBODY-PREPULLED": (
        "02F-R2A-HTT-BLACKBODY-T",
        "PREPULLED_VALUE_PRIMITIVE",
        "29427a1f7f2c5d46e43ffe03053c4ac13e969228",
        "htt/obsstat/lorentz_sky_pullback.py",
        "c518cdd0dcdd3ca628c71f6dd9e6a75e174ba805",
        ("thermodynamic_temperature_pullback",),
        False,
    ),
}
EXPECTED_NAMED_SYMBOLS = [
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
]
EXPECTED_STATE_SURFACES = [
    "GRID_F_Q_E",
    "PSTF_F_AELL_Q",
    "J_I_AELL",
    "G_ANGULAR_ENERGY",
    "FLUID_COMPONENT_SUMMARY",
    "POLARIZED_COHERENCY",
]
EXPECTED_CERTIFICATE_FAMILIES = [
    "ANGULAR_REPRESENTATION_CERTIFICATE",
    "SPECTRAL_PROJECTION_CLOSURE_CERTIFICATE",
    "MOMENT_EXCHANGE_CERTIFICATE",
    "POLARIZED_SCREEN_CERTIFICATE",
]
EXPECTED_BLOCKED_PROMOTIONS = [
    "CROSS_REPOSITORY_CONSUMER_RUNTIME_PARITY",
    "GRID_PSTF_NUMERICAL_PARITY",
    "J_SPECTRAL_CLOSURE_ADMISSION",
    "G_SPECTRAL_CLOSURE_ADMISSION",
    "FLUID_EXCHANGE_RUNTIME_PASS",
    "SCREEN_BASIS_TRANSPORT_IMPLEMENTED",
    "POLARIZED_COLLISION_RUNTIME",
    "POLARIZED_ARBITRARY_ELL_COMPILER",
    "BASS_BACKGROUND_PROVIDER",
    "GLOBAL_MATTER_TILT",
    "LIKELIHOOD_READY",
    "SCIENCE_PROMOTION",
    "PASS_RF04",
]
EXPECTED_AUTHORIZATION_FIREWALL = {
    "consumer_source_mutation_authorized": False,
    "runtime_parity_admitted": False,
    "provider_promotion_authorized": False,
    "science_promotion_authorized": False,
    "merge_or_ready_transition_authorized": False,
    "formula_occurrence_implies_runtime_parity": False,
    "source_role_pin_implies_runtime_parity": False,
    "certificate_schema_implies_runtime_certificate": False,
}
EXPECTED_DAG_NODES = [
    "BOUNDED_SEMANTIC_CLOSEOUT",
    "CONSUMER_BINDING_CONTRACTS",
    "REC_RUNTIME_VALIDATION",
    "REI_RUNTIME_VALIDATION",
    "HTT_RUNTIME_VALIDATION",
    "CROSS_REPOSITORY_PARITY_FEDERATION",
]
EXPECTED_DAG_EDGES = [
    ["BOUNDED_SEMANTIC_CLOSEOUT", "CONSUMER_BINDING_CONTRACTS"],
    ["CONSUMER_BINDING_CONTRACTS", "REC_RUNTIME_VALIDATION"],
    ["CONSUMER_BINDING_CONTRACTS", "REI_RUNTIME_VALIDATION"],
    ["CONSUMER_BINDING_CONTRACTS", "HTT_RUNTIME_VALIDATION"],
    ["REC_RUNTIME_VALIDATION", "CROSS_REPOSITORY_PARITY_FEDERATION"],
    ["REI_RUNTIME_VALIDATION", "CROSS_REPOSITORY_PARITY_FEDERATION"],
    ["HTT_RUNTIME_VALIDATION", "CROSS_REPOSITORY_PARITY_FEDERATION"],
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def graph_acyclic(nodes: list[str], edges: list[list[str]]) -> bool:
    if len(nodes) != len(set(nodes)):
        return False
    node_set = set(nodes)
    if any(
        not isinstance(edge, list)
        or len(edge) != 2
        or edge[0] not in node_set
        or edge[1] not in node_set
        for edge in edges
    ):
        return False
    outgoing: dict[str, list[str]] = {node: [] for node in nodes}
    indegree = {node: 0 for node in nodes}
    for source, target in edges:
        outgoing[source].append(target)
        indegree[target] += 1
    queue = deque(node for node in nodes if indegree[node] == 0)
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
    require(data.get("schema_version") == "1.0.0", "schema version mismatch")
    require(
        data.get("stage_id") == "SYNC_MAP_02F_R3_CONSUMER_BINDING_CONTRACTS",
        "stage id mismatch",
    )
    require(data.get("repository_scope") == "BASS_ONLY", "scope is not BASS_ONLY")
    require(data.get("owner") == "bass", "owner mismatch")

    ancestry = data.get("normal_ancestry")
    require(isinstance(ancestry, dict), "normal ancestry missing")
    require(ancestry.get("parent_commit") == EXPECTED_PARENT, "parent commit mismatch")
    require(
        ancestry.get("validated_closeout_source_head")
        == "25dc6a75fc781d329dbe9a2b6d68eeb5f8a6607e",
        "parent closeout source identity mismatch",
    )
    require(
        ancestry.get("expected_red_source_head")
        == "21f5b08b704a90af19e617a372c994239e9046a2",
        "expected RED source identity mismatch",
    )
    require(
        ancestry.get("expected_red_gate")
        == "PASS_EXPECTED_RED_12_FAILURES_0_ERRORS",
        "expected RED gate missing",
    )

    counts = data.get("count_contract")
    require(counts == EXPECTED_COUNTS, "count contract mismatch")

    consumers = data.get("consumer_repositories")
    require(isinstance(consumers, list), "consumer rows missing")
    require(
        [row.get("repository") for row in consumers] == EXPECTED_CONSUMERS,
        "consumer repository contract mismatch",
    )
    require(
        all(
            row.get("source_mutation_authorized") is False
            and row.get("runtime_parity_admitted") is False
            for row in consumers
        ),
        "consumer authorization weakened",
    )

    bindings = data.get("binding_requests")
    require(isinstance(bindings, list), "binding request rows missing")
    require(len(bindings) == 10, "binding request count mismatch")
    pair_ids = [row.get("pair_id") for row in bindings]
    binding_ids = [row.get("binding_id") for row in bindings]
    require(pair_ids == EXPECTED_PAIR_IDS, "binding request pair coverage mismatch")
    require(binding_ids == EXPECTED_BINDING_IDS, "binding request ID contract mismatch")
    require(len(pair_ids) == len(set(pair_ids)), "binding request pair IDs are not unique")
    require(len(binding_ids) == len(set(binding_ids)), "binding request IDs are not unique")
    for row in bindings:
        pair_id = row.get("pair_id")
        require(pair_id in EXPECTED_BINDING_CORE, "binding request pair is unknown")
        expected = EXPECTED_BINDING_CORE[pair_id]
        observed = (
            row.get("consumer_repository"),
            row.get("formula_id"),
            tuple(row.get("source_role_ids", [])),
            tuple(row.get("conditional_certificate_families", [])),
            row.get("next_owner_stage"),
        )
        require(observed == expected, f"binding request contract mismatch for {pair_id}")
        require(
            isinstance(row.get("required_gate_templates"), list)
            and len(row["required_gate_templates"]) >= 2,
            f"binding request gate templates missing for {pair_id}",
        )
        require(row.get("runtime_parity_admitted") is False, "binding request parity promoted")
        require(
            row.get("consumer_source_mutation_authorized") is False,
            "binding request source mutation authorized",
        )

    formula_authority = data.get("formula_authority")
    require(isinstance(formula_authority, dict), "formula authority missing")
    require(
        formula_authority.get("registry_semantic_hash")
        == "5951f566d911c81848743055c1573f6d11b0b00937d36747b71e6bc12dd96416",
        "formula authority registry hash mismatch",
    )
    observed_formulas = [
        (row.get("formula_id"), row.get("semantic_hash"), row.get("dimension"))
        for row in formula_authority.get("formulas", [])
    ]
    require(observed_formulas == EXPECTED_FORMULAS, "formula authority contract mismatch")

    roles = data.get("source_role_pins")
    require(isinstance(roles, list), "source role rows missing")
    role_ids = [row.get("role_id") for row in roles]
    require(role_ids == EXPECTED_ROLE_IDS, "source role ordering mismatch")
    require(len(role_ids) == len(set(role_ids)), "source role IDs are not unique")
    role_map = {row["role_id"]: row for row in roles}

    rei_absent = role_map.get("ROLE-REI-DIRECTION-FLOW-ABSENT", {})
    require(
        rei_absent.get("role_type") == "ABSENT_IMPLEMENTATION_SLOT"
        and rei_absent.get("source_symbols") == []
        and rei_absent.get("implements_full_formula") is False
        and rei_absent.get("implementation_status") == "ABSENT_IMPLEMENTATION_SLOT",
        "REI absent direction-flow slot was promoted",
    )

    htt_full = role_map.get("ROLE-HTT-BLACKBODY-FULL", {})
    htt_prepulled = role_map.get("ROLE-HTT-BLACKBODY-PREPULLED", {})
    require(
        htt_full.get("role_type") == "FULL_FIELD_PULLBACK"
        and htt_full.get("implements_full_formula") is True
        and htt_full.get("source_symbols")
        == ["pullback_thermodynamic_temperature_field"]
        and htt_prepulled.get("role_type") == "PREPULLED_VALUE_PRIMITIVE"
        and htt_prepulled.get("implements_full_formula") is False
        and htt_prepulled.get("source_symbols")
        == ["thermodynamic_temperature_pullback"],
        "HTT blackbody full and prepulled roles were collapsed",
    )

    for role_id, expected in EXPECTED_ROLE_CORE.items():
        row = role_map.get(role_id)
        require(isinstance(row, dict), f"source role missing: {role_id}")
        observed = (
            row.get("pair_id"),
            row.get("role_type"),
            row.get("source_commit"),
            row.get("source_path"),
            row.get("source_blob"),
            tuple(row.get("source_symbols", [])),
            row.get("implements_full_formula"),
        )
        require(observed == expected, f"source role contract mismatch for {role_id}")

    flattened_symbols = [symbol for row in roles for symbol in row.get("source_symbols", [])]
    require(flattened_symbols == EXPECTED_NAMED_SYMBOLS, "source role symbol projection mismatch")
    require(
        data.get("named_source_symbols") == EXPECTED_NAMED_SYMBOLS,
        "named source-symbol registry mismatch",
    )
    require(len(set(flattened_symbols)) == 12, "named source symbols are not unique")

    state_policy = data.get("state_surface_policy")
    require(isinstance(state_policy, dict), "state-surface policy missing")
    require(
        state_policy.get("state_surfaces") == EXPECTED_STATE_SURFACES,
        "state-surface registry mismatch",
    )
    require(
        state_policy.get("primary_frequency_resolved_pair")
        == ["GRID_F_Q_E", "PSTF_F_AELL_Q"],
        "state-surface primary representation pair mismatch",
    )
    require(
        state_policy.get("j_and_g_generic_binding")
        == "WITHHELD_REQUIRES_SPECTRAL_PROJECTION_CLOSURE_CERTIFICATE",
        "state-surface J/G closure firewall weakened",
    )
    require(
        state_policy.get("scalar_to_polarized_binding")
        == "FORBIDDEN_REQUIRES_POLARIZED_SCREEN_CERTIFICATE",
        "state-surface polarization firewall weakened",
    )
    require(
        state_policy.get("certificate_schema_is_certificate_instance") is False,
        "state-surface certificate schema promoted to instance",
    )
    require(
        state_policy.get("hardcoded_numeric_ell_cutoff_forbidden") is True,
        "state-surface hardcoded ell policy weakened",
    )

    certificates = data.get("certificate_families")
    require(
        certificates == EXPECTED_CERTIFICATE_FAMILIES,
        "certificate-family contract mismatch",
    )
    gate_ids = [row.get("gate_id") for row in data.get("gate_templates", [])]
    for gate_id in (
        "FORMULA_IDENTITY_GATE",
        "CONVENTION_DOMAIN_UNIT_GATE",
        "ANGULAR_REPRESENTATION_GATE",
        "SPECTRAL_PROJECTION_GATE",
        "MOMENT_EXCHANGE_GATE",
        "POLARIZED_SCREEN_GATE",
        "RESTRICTED_SUBSPACE_GATE",
        "ABSENT_IMPLEMENTATION_GATE",
    ):
        require(gate_id in gate_ids, f"certificate or gate template missing: {gate_id}")

    blocked = data.get("blocked_promotions")
    require(blocked == EXPECTED_BLOCKED_PROMOTIONS, "blocked-promotion contract mismatch")
    require(len(blocked) == len(set(blocked)), "blocked promotions contain duplicates")

    firewall = data.get("authorization_firewall")
    require(
        firewall == EXPECTED_AUTHORIZATION_FIREWALL,
        "authorization firewall mismatch",
    )

    dag = data.get("stage_dag")
    require(isinstance(dag, dict), "DAG missing")
    nodes = dag.get("nodes")
    edges = dag.get("edges")
    require(nodes == EXPECTED_DAG_NODES, "DAG node contract mismatch")
    require(edges == EXPECTED_DAG_EDGES, "DAG edge contract mismatch")
    require(graph_acyclic(nodes, edges), "DAG is cyclic or malformed")
    require(
        dag.get("future_nodes_are_routing_declarations_not_pass_claims") is True,
        "DAG future-node claim firewall missing",
    )

    parallel = data.get("parallel_bass_runtime_evidence")
    require(isinstance(parallel, list) and len(parallel) == 1, "parallel R6C evidence missing")
    r6c = parallel[0]
    require(
        r6c.get("classification")
        == "PASS_BASS_REC_SOURCE_R6C_CLEAN_BACKEND_NONREGRESSION"
        and r6c.get("publication_head")
        == "3f605360eae96a7fbe5dd9c31ec510c5d56e255b"
        and r6c.get("green_source_commit")
        == "92d67dc79cf645947beb93ac01a9505ee277dabd"
        and r6c.get("clean_worktrees") is True
        and r6c.get("runtime_parity_effect") == "NONE"
        and r6c.get("remaining_trusted_gate")
        == "PASS_R5D_TRUSTED_RF00_PAYLOAD_PROVENANCE_AND_BACKEND_GATE",
        "parallel R6C evidence contract mismatch",
    )

    literature = data.get("literature_regression")
    require(isinstance(literature, list) and len(literature) >= 3, "literature block missing")
    require(
        all(row.get("authority_effect") == "NONE" for row in literature),
        "literature authority escalated",
    )

    require(
        data.get("status") == "IMPLEMENTED_CONTRACT_LOCAL_REPLAY_REQUIRED",
        "source-stage status mismatch",
    )

    per_consumer = Counter(row["consumer_repository"] for row in bindings)
    require(
        per_consumer == Counter({"rec_bianchi": 4, "rei_bianchi": 2, "htt_base": 4}),
        "binding request consumer partition mismatch",
    )

    return {
        "schema_version": "1.0.0",
        "stage_id": "SYNC_MAP_02F_R3_CONSUMER_BINDING_CONTRACTS",
        "repository_scope": "BASS_ONLY",
        "consumer_count": len(consumers),
        "binding_request_count": len(bindings),
        "source_role_pin_count": len(roles),
        "named_source_symbol_count": len(flattened_symbols),
        "absent_implementation_slot_count": sum(
            row.get("role_type") == "ABSENT_IMPLEMENTATION_SLOT" for row in roles
        ),
        "formula_count": len(formula_authority["formulas"]),
        "state_surface_count": len(state_policy["state_surfaces"]),
        "certificate_family_count": len(certificates),
        "blocked_promotion_count": len(blocked),
        "dag_acyclic": True,
        "parallel_r6c_nonpromotional": True,
        "status": "PASS",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--graph",
        type=Path,
        default=Path(
            "docs/bass_master_ssot_v2/SYNC_MAP_02F_R3/"
            "CONSUMER_BINDING_CONTRACTS.json"
        ),
    )
    args = parser.parse_args()
    data = json.loads(args.graph.read_text(encoding="utf-8"))
    print(json.dumps(verify(data), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
