#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import re
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
GRAPH_PATH = ROOT / "docs/bass_master_ssot_v2/SYNC_MAP_02F/CROSS_REPOSITORY_SEMANTIC_GRAPH.json"
EXPORT_PATH = ROOT / "docs/bass_master_ssot_v2/SYNC_MAP_02E/BASS_SHARED_FRAME_PHOTON_EXPORT.json"
REC_PATH = ROOT / "docs/bass_master_ssot_v2/SYNC_MAP_02B/REC_RELATION_CLASSIFICATION.json"
REI_PATH = ROOT / "docs/bass_master_ssot_v2/SYNC_MAP_02C/REI_RELATION_CLASSIFICATION_R3.json"
HTT_PATH = ROOT / "docs/bass_master_ssot_v2/SYNC_MAP_02D/HTT_RELATION_CLASSIFICATION.json"

HEX40 = re.compile(r"[0-9a-f]{40}\Z")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")

EXPECTED_FORMULA_HASHES = {
    "BASS.FRAME.ABERRATED_DIRECTION.001": "7d212853f2f5aead7bc338605112d510d2793ebc9fc1192de61fea9d757536e5",
    "BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001": "5ef8a90ff34b6df1f6075e8208faeca76e53921addc47441d0d877ee66bcc67f",
    "BASS.FRAME.DOPPLER_FACTOR.001": "6932f72745ed092dd2c356a9db984de4dc6197b77f2bcf881ad1699f87010fc8",
    "BASS.FRAME.SOLID_ANGLE_JACOBIAN.001": "937a9b46dece8df45590bfa895ede33c027cefd211a48a0f4b8ca49f4bcb94c4",
    "BASS.PHOTON.DIRECTION_FLOW.001": "a76d3e1ea11488b9e4269e169bf1f95d2d6f4a1ccd63715be36f76b85975df4e",
    "BASS.PHOTON.ENERGY_DRIFT.001": "d296e7686dce3feb4a932b81427f918df06d4690e57a4ba2b998cf96897e7b2d",
}

EXPECTED_COVERAGE = {
    "BASS.FRAME.ABERRATED_DIRECTION.001": {"rec_bianchi", "htt_base"},
    "BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001": {"htt_base"},
    "BASS.FRAME.DOPPLER_FACTOR.001": {"rec_bianchi", "htt_base"},
    "BASS.FRAME.SOLID_ANGLE_JACOBIAN.001": {"htt_base"},
    "BASS.PHOTON.DIRECTION_FLOW.001": {"rec_bianchi", "rei_bianchi"},
    "BASS.PHOTON.ENERGY_DRIFT.001": {"rec_bianchi", "rei_bianchi"},
}

ALLOWED_RELATION_CLASSES = {
    "SEMANTIC_EQUIVALENT_IDENTITY_CHART",
    "SEMANTIC_EQUIVALENT_WITH_DIRECTION_ADAPTER",
    "SEMANTIC_EQUIVALENT_WITH_RATE_AND_NOTATION_ADAPTER",
    "ADAPTER_SPECIALIZATION_STRICT_SUBDOMAIN",
    "NON_EQUIVALENT_RESTRICTED_CONTROL",
    "ABSENT_REQUIRED_DEPENDENCY",
    "INDEPENDENT_ORACLE",
}

REQUIRED_WITHHELD = {
    "CONSUMER_IMPLEMENTATION_PARITY",
    "CROSS_REPOSITORY_NUMERICAL_PARITY",
    "GLOBAL_MATTER_TILT",
    "FINITE_ELECTRON_TILT_COLLISION",
    "BACKGROUND_PROVIDER_ADMISSION",
    "REC_PROVIDER_ADMISSION",
    "REI_PROVIDER_ADMISSION",
    "OBSERVATIONAL_OR_STATISTICAL_READINESS",
    "DATA_FITTING",
    "SCIENCE_VALIDITY",
    "PASS_RF04",
    "MERGE_OR_READY_TRANSITION",
}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _hex40(value: object) -> bool:
    return isinstance(value, str) and HEX40.fullmatch(value) is not None


def _hex64(value: object) -> bool:
    return isinstance(value, str) and HEX64.fullmatch(value) is not None


def _acyclic(nodes: list[str], edges: list[list[str]]) -> bool:
    indegree = {node: 0 for node in nodes}
    outgoing: dict[str, list[str]] = defaultdict(list)
    for edge in edges:
        if not isinstance(edge, list) or len(edge) != 2:
            return False
        source, target = edge
        if source not in indegree or target not in indegree:
            return False
        outgoing[source].append(target)
        indegree[target] += 1
    queue = deque(sorted(node for node, degree in indegree.items() if degree == 0))
    visited = 0
    while queue:
        node = queue.popleft()
        visited += 1
        for target in outgoing[node]:
            indegree[target] -= 1
            if indegree[target] == 0:
                queue.append(target)
    return visited == len(nodes)


def validate_graph(graph: dict[str, Any], root: Path = ROOT) -> list[str]:
    errors: list[str] = []

    if graph.get("stage_id") != "SYNC_MAP_02F_CROSS_REPOSITORY_SEMANTIC_GRAPH":
        errors.append("stage_id mismatch")
    if graph.get("authority_effect") != "BOUNDED_SEMANTIC_RELATION_GRAPH_ONLY":
        errors.append("authority effect exceeds bounded semantic graph")

    conventions = graph.get("convention_contract", {})
    required_conventions = {
        "metric_signature": "(-,+,+,+)",
        "spatial_orientation": "epsilon_123=+1",
        "photon_propagation_direction": "e",
        "outward_sky_direction": "n_sky=-e",
        "rec_rate_adapter": "R_t=c*R_ell and V_t=c*V_ell",
    }
    for key, expected in required_conventions.items():
        if conventions.get(key) != expected:
            errors.append(f"convention mismatch: {key}")

    inputs = graph.get("exact_inputs", {})
    expected_input_commits = {
        ("sync_map_02a", "commit"): "6587c081932d5a6b97f4efa77293e93f5675f11b" if False else "6587c081932d1dddda586781825d242616ca1357",
        ("sync_map_02b", "commit"): "f1eab555b42ebfaa3aa9d4021e097750aa0dfd96",
        ("sync_map_02c", "commit"): "9e39e2468b9efec05f33b9945de02fe2c8c6a66d",
        ("sync_map_02d", "classification_head"): "7006aaab27834af37d5034f8f1e50943fe85c0f3",
        ("sync_map_02d", "cross_cas_head"): "7054cc094209c056c7d278a4cc6354a89927f35d",
        ("sync_map_02e", "tested_formula_payload_commit"): "0b569c00c063e0a13807af5777f61efcced4b95c",
        ("sync_map_02e", "append_only_receipt_head"): "e1467825c8f4c5e3f47df5da5b8a6202e8f96f30",
    }
    for (section, key), expected in expected_input_commits.items():
        actual = inputs.get(section, {}).get(key)
        if actual != expected or not _hex40(actual):
            errors.append(f"exact input mismatch: {section}.{key}")
    if inputs.get("sync_map_02e", {}).get("tested_formula_payload_commit") == inputs.get("sync_map_02e", {}).get("append_only_receipt_head"):
        errors.append("receipt head substituted for tested formula payload")
    if inputs.get("sync_map_02d", {}).get("cross_cas_receipt_blob") != "00908bf880805a70726436f0faa9ac6f93b6600d":
        errors.append("02D cross-CAS receipt blob mismatch")

    authorities = graph.get("authority_formulas", [])
    ids = [record.get("formula_id") for record in authorities if isinstance(record, dict)]
    if len(authorities) != 6 or set(ids) != set(EXPECTED_FORMULA_HASHES) or len(ids) != len(set(ids)):
        errors.append("authority formula ID set is not exactly the six-formula export")
    for record in authorities:
        if not isinstance(record, dict):
            errors.append("authority record is not an object")
            continue
        formula_id = record.get("formula_id")
        if record.get("owner") != "bass":
            errors.append(f"non-BASS or compound authority owner: {formula_id}")
        if record.get("semantic_hash") != EXPECTED_FORMULA_HASHES.get(formula_id) or not _hex64(record.get("semantic_hash")):
            errors.append(f"semantic hash mismatch: {formula_id}")
        if record.get("tested_payload_commit") != "0b569c00c063e0a13807af5777f61efcced4b95c":
            errors.append(f"authority payload mismatch: {formula_id}")

    export = load_json(root / EXPORT_PATH.relative_to(ROOT))
    export_hashes = {item["formula_id"]: item["semantic_hash"] for item in export.get("formulas", [])}
    if export_hashes != EXPECTED_FORMULA_HASHES:
        errors.append("inherited 02E export hashes do not match the frozen six-formula set")

    relations = graph.get("consumer_relations", [])
    relation_ids = [record.get("relation_id") for record in relations if isinstance(record, dict)]
    if len(relations) != 10 or len(relation_ids) != len(set(relation_ids)):
        errors.append("consumer relation set must contain ten unique records")
    actual_coverage: dict[str, set[str]] = defaultdict(set)
    for relation in relations:
        if not isinstance(relation, dict):
            errors.append("consumer relation is not an object")
            continue
        formula_id = relation.get("formula_id")
        consumer = relation.get("consumer_repository")
        actual_coverage[str(formula_id)].add(str(consumer))
        if formula_id not in EXPECTED_FORMULA_HASHES:
            errors.append(f"relation targets unknown formula: {formula_id}")
        if consumer not in {"rec_bianchi", "rei_bianchi", "htt_base"}:
            errors.append(f"unknown consumer: {consumer}")
        if relation.get("relation_class") not in ALLOWED_RELATION_CLASSES:
            errors.append(f"unknown relation class: {relation.get('relation_class')}")
        if not _hex40(relation.get("source_commit")) or not _hex40(relation.get("source_blob")):
            errors.append(f"invalid exact source pin: {relation.get('relation_id')}")
        if not isinstance(relation.get("source_path"), str) or not relation.get("source_path"):
            errors.append(f"missing source path: {relation.get('relation_id')}")
        if relation.get("relation_class") == "INDEPENDENT_ORACLE" and relation.get("authority_effect") != "NONE":
            errors.append(f"oracle has authority effect: {relation.get('relation_id')}")

    if {key: value for key, value in actual_coverage.items()} != EXPECTED_COVERAGE:
        errors.append("formula-consumer coverage mismatch")
    declared_coverage = {key: set(value) for key, value in graph.get("formula_consumer_coverage", {}).items()}
    if declared_coverage != EXPECTED_COVERAGE:
        errors.append("declared formula-consumer coverage mismatch")

    by_id = {record.get("relation_id"): record for record in relations}
    if by_id.get("02F-REC-DIRECTION-FLOW", {}).get("adapter") != "REC n=e and V_t=c*V_ell; REC A_s_inv is the Bianchi structure vector aB expressed per physical time":
        errors.append("REC direction-flow rate adapter missing")
    if by_id.get("02F-REC-ENERGY-DRIFT", {}).get("adapter") != "REC n=e and R_t=c*R_ell":
        errors.append("REC energy-drift rate adapter missing")
    if by_id.get("02F-REI-DIRECTION-FLOW", {}).get("relation_class") != "ABSENT_REQUIRED_DEPENDENCY" or by_id.get("02F-REI-DIRECTION-FLOW", {}).get("source_symbol") is not None:
        errors.append("REI direction flow must remain absent")
    rei_energy = by_id.get("02F-REI-ENERGY-DRIFT", {})
    if rei_energy.get("relation_class") != "NON_EQUIVALENT_RESTRICTED_CONTROL" or "omits -sigma_ab e^a e^b" not in str(rei_energy.get("adapter")):
        errors.append("REI H-only redshift was promoted beyond its strict control domain")
    htt_temperature = by_id.get("02F-HTT-BLACKBODY-T", {})
    if htt_temperature.get("relation_class") != "ADAPTER_SPECIALIZATION_STRICT_SUBDOMAIN" or "Doppler weight d=1" not in str(htt_temperature.get("adapter")):
        errors.append("HTT blackbody-temperature domain restriction missing")

    rec = load_json(root / REC_PATH.relative_to(ROOT))
    if set(rec.get("pending_bass_imports", [])) != {
        "BASS.FRAME.ABERRATED_DIRECTION.001",
        "BASS.FRAME.DOPPLER_FACTOR.001",
        "BASS.PHOTON.DIRECTION_FLOW.001",
        "BASS.PHOTON.ENERGY_DRIFT.001",
    }:
        errors.append("02B pending import set drifted")
    rei = load_json(root / REI_PATH.relative_to(ROOT))
    if set(rei.get("shared_formula_consumer_union", {})) != set(EXPECTED_FORMULA_HASHES):
        errors.append("02C shared formula union drifted")
    htt = load_json(root / HTT_PATH.relative_to(ROOT))
    if set(htt.get("pending_bass_imports", [])) != {
        "BASS.FRAME.ABERRATED_DIRECTION.001",
        "BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001",
        "BASS.FRAME.DOPPLER_FACTOR.001",
        "BASS.FRAME.SOLID_ANGLE_JACOBIAN.001",
    }:
        errors.append("02D pending import set drifted")

    dag = graph.get("dag", {})
    nodes = dag.get("nodes", [])
    edges = dag.get("edges", [])
    if len(nodes) != 10 or len(nodes) != len(set(nodes)):
        errors.append("DAG must contain ten unique nodes")
    if len(edges) != 12 or len({tuple(edge) for edge in edges if isinstance(edge, list)}) != 12:
        errors.append("DAG must contain twelve unique edges")
    if not _acyclic(nodes, edges):
        errors.append("DAG is not closed and acyclic")
    required_edges = {
        ("SYNC_MAP_02C_REI", "SYNC_MAP_02E_SHARED_EXPORT"),
        ("SYNC_MAP_02D_HTT", "SYNC_MAP_02E_SHARED_EXPORT"),
        ("SYNC_MAP_02E_SHARED_EXPORT", "SYNC_MAP_02F_SEMANTIC_GRAPH"),
        ("SYNC_MAP_02F_SEMANTIC_GRAPH", "SYNC_REC_01"),
        ("SYNC_MAP_02F_SEMANTIC_GRAPH", "SYNC_REI_01"),
        ("SYNC_MAP_02F_SEMANTIC_GRAPH", "SYNC_HTT_01A"),
    }
    if not required_edges.issubset({tuple(edge) for edge in edges}):
        errors.append("required federation ordering edge missing")
    if dag.get("sync_gate_manual_only") is not True or dag.get("official_jira_edges_mutated") is not False:
        errors.append("manual gate or official-edge firewall drifted")

    firewalls = set(graph.get("semantic_firewalls", []))
    required_firewalls = {
        "local observer boost is not global matter-frame tilt",
        "local observer boost is not finite-electron-tilt Thomson collision",
        "full-sky Lorentz formulas are not mask beam or processed-estimator formulas",
        "formula-level relation is not consumer runtime parity",
        "eleven-branch formula atlas is not eleven-family numerical solver support",
        "REI scalar H-only group redshift is not generic anisotropic photon energy drift",
    }
    if firewalls != required_firewalls:
        errors.append("semantic firewall set mismatch")
    if not REQUIRED_WITHHELD.issubset(set(graph.get("withheld_claims", []))):
        errors.append("required withheld claims missing")

    return errors


def verify(path: Path = GRAPH_PATH) -> dict[str, Any]:
    graph = load_json(path)
    errors = validate_graph(graph)
    if errors:
        raise SystemExit("SYNC_MAP_02F_VERIFY_FAIL:\n- " + "\n- ".join(errors))
    return {
        "status": "PASS",
        "authority_formula_count": len(graph["authority_formulas"]),
        "consumer_relation_count": len(graph["consumer_relations"]),
        "dag_node_count": len(graph["dag"]["nodes"]),
        "dag_edge_count": len(graph["dag"]["edges"]),
        "unique_authority_owner": "bass",
        "sync_gate": "MANUAL_ONLY",
        "claim_boundary": "SEMANTIC_GRAPH_ONLY_NO_RUNTIME_OR_SCIENCE_PROMOTION",
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
