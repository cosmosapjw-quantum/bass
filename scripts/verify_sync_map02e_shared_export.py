#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EXPORT_PATH = ROOT / "docs/bass_master_ssot_v2/SYNC_MAP_02E/BASS_SHARED_FRAME_PHOTON_EXPORT.json"
EXPECTED_PARENT = "9e39e2468b9efec05f33b9945de02fe2c8c6a66d"
EXPECTED_HTT_PRE_REPAIR = "06aa29f78c26bcafeb60d85b719a4d3aa5c4c2e8"
EXPECTED_HTT_REPAIR_PAYLOAD = "6203b1343a6adb0f53d7abd0667e6d76b80fec53"
EXPECTED_HTT_REPAIR_TREE = "db49005f8dc77431dc4b76d67d8b7a242877fa46"
EXPECTED_HTT_FINAL_RECEIPT_HEAD = "7006aaab27834af37d5034f8f1e50943fe85c0f3"
EXPECTED_WOLFRAM_SHA = "60ea9b894f955c2599628ae3ebf51b0e6d3a9ab2c512551fdef86e8c022f254b"
EXPECTED_FORMULA_IDS = {
    "BASS.FRAME.DOPPLER_FACTOR.001",
    "BASS.FRAME.ABERRATED_DIRECTION.001",
    "BASS.FRAME.SOLID_ANGLE_JACOBIAN.001",
    "BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001",
    "BASS.PHOTON.ENERGY_DRIFT.001",
    "BASS.PHOTON.DIRECTION_FLOW.001",
}
EXPECTED_INTERNAL_EDGES = {
    ("BASS.FRAME.ABERRATED_DIRECTION.001", "BASS.FRAME.DOPPLER_FACTOR.001"),
    ("BASS.FRAME.SOLID_ANGLE_JACOBIAN.001", "BASS.FRAME.DOPPLER_FACTOR.001"),
    ("BASS.FRAME.SOLID_ANGLE_JACOBIAN.001", "BASS.FRAME.ABERRATED_DIRECTION.001"),
    ("BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001", "BASS.FRAME.DOPPLER_FACTOR.001"),
}
EXPECTED_EXTERNAL_EDGES = {
    ("BASS.PHOTON.ENERGY_DRIFT.001", "BASS.GEO.EXTRINSIC_CURVATURE_SHEAR_SPLIT.001"),
    ("BASS.PHOTON.DIRECTION_FLOW.001", "BASS.GEO.EXTRINSIC_CURVATURE_SHEAR_SPLIT.001"),
    ("BASS.PHOTON.DIRECTION_FLOW.001", "BASS.GEO.STRUCTURE_CONSTANTS.001"),
}
EXPECTED_CONSUMERS = {
    "BASS.FRAME.ABERRATED_DIRECTION.001": ["rec_bianchi", "htt_base"],
    "BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001": ["htt_base"],
    "BASS.FRAME.DOPPLER_FACTOR.001": ["rec_bianchi", "htt_base"],
    "BASS.FRAME.SOLID_ANGLE_JACOBIAN.001": ["htt_base"],
    "BASS.PHOTON.DIRECTION_FLOW.001": ["rec_bianchi", "rei_bianchi"],
    "BASS.PHOTON.ENERGY_DRIFT.001": ["rec_bianchi", "rei_bianchi"],
}
EXPECTED_TERMS = {
    "BASS.FRAME.DOPPLER_FACTOR.001": [
        ("gamma*(1+beta_dot_n_sky)", 1),
    ],
    "BASS.FRAME.ABERRATED_DIRECTION.001": [
        ("[n_sky^a+(gamma+((gamma-1)/beta_squared)*beta_dot_n_sky)*beta^a]/doppler_factor", 1),
    ],
    "BASS.FRAME.SOLID_ANGLE_JACOBIAN.001": [
        ("doppler_factor^(-2)*dOmega", 1),
    ],
    "BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001": [
        ("doppler_factor*temperature(n_sky)", 1),
    ],
    "BASS.PHOTON.ENERGY_DRIFT.001": [
        ("H_geom", -1),
        ("sigma_ab*e^a*e^b", -1),
    ],
    "BASS.PHOTON.DIRECTION_FLOW.001": [
        ("(sigma_bc*e^b*e^c+aB_b*e^b)*e^a", 1),
        ("sigma^a_b*e^b", -1),
        ("aB^a", -1),
        ("epsilon^a_bc*Omega_triad^b*e^c", 1),
        ("epsilon^a_bc*e^b*nB^c_d*e^d", -1),
    ],
}
EXPECTED_DIMENSIONS = {
    "BASS.FRAME.DOPPLER_FACTOR.001": "1",
    "BASS.FRAME.ABERRATED_DIRECTION.001": "1",
    "BASS.FRAME.SOLID_ANGLE_JACOBIAN.001": "1",
    "BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001": "K",
    "BASS.PHOTON.ENERGY_DRIFT.001": "L^-1",
    "BASS.PHOTON.DIRECTION_FLOW.001": "L^-1",
}
FORBIDDEN_INCLUDED_TOKENS = (
    "background provider",
    "global matter",
    "electron tilt",
    "recombination",
    "reionization",
    "mask",
    "estimator",
    "likelihood",
    "statistics",
)

class ValidationError(ValueError):
    pass

def load_export(path: Path = EXPORT_PATH) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"cannot load export: {exc}") from exc

def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).replace("/", r"\/").encode("utf-8")

def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()

def _semantic_projection(ir: dict[str, Any]) -> dict[str, Any]:
    dropped = {"schema_version", "formula_id", "authority_theorem", "provenance"}
    return {key: value for key, value in ir.items() if key not in dropped}

def _integer_value(ast: Any) -> int | None:
    if not isinstance(ast, dict):
        return None
    if ast.get("type") != "integer" or set(ast) != {"type", "value"}:
        return None
    value = ast.get("value")
    return value if isinstance(value, int) and not isinstance(value, bool) else None

def _edge_set(edges: Any, label: str) -> set[tuple[str, str]]:
    if not isinstance(edges, list):
        raise ValidationError(f"{label} dependency edges must be a list")
    result: set[tuple[str, str]] = set()
    for edge in edges:
        if not isinstance(edge, dict) or set(edge) != {"from", "to", "relation"}:
            raise ValidationError(f"malformed {label} dependency edge")
        if edge["relation"] != "depends_on":
            raise ValidationError(f"invalid {label} dependency relation")
        pair = (edge["from"], edge["to"])
        if pair in result:
            raise ValidationError(f"duplicate {label} dependency edge")
        result.add(pair)
    return result

def _assert_acyclic(nodes: set[str], edges: set[tuple[str, str]]) -> None:
    outgoing = {node: set() for node in nodes}
    indegree = {node: 0 for node in nodes}
    for source, target in edges:
        if source not in nodes or target not in nodes:
            raise ValidationError("internal dependency edge closure failed")
        outgoing[source].add(target)
        indegree[target] += 1
    queue = sorted(node for node, degree in indegree.items() if degree == 0)
    visited = 0
    while queue:
        node = queue.pop(0)
        visited += 1
        for target in sorted(outgoing[node]):
            indegree[target] -= 1
            if indegree[target] == 0:
                queue.append(target)
                queue.sort()
    if visited != len(nodes):
        raise ValidationError("internal dependency cycle detected")

def _validate_metadata(data: dict[str, Any]) -> None:
    expected = {
        "schema_version": "1.0.0",
        "program_id": "BIANCHI-WOLFRAM-FOUR-REPO-20260902",
        "stage_id": "SYNC_MAP_02E_SHARED_FRAME_PHOTON_EXPORT",
        "owner": "bass",
        "source_repository": "cosmosapjw-quantum/bass",
    }
    for key, value in expected.items():
        if data.get(key) != value:
            raise ValidationError(f"metadata mismatch: {key}")
    parent = data.get("source_parent", {})
    if parent.get("commit") != EXPECTED_PARENT or parent.get("workflow_conclusion") != "success":
        raise ValidationError("source-parent exact-head contract failed")
    predecessors = data.get("predecessors", {})
    htt = predecessors.get("sync_map_02d", {})
    if (
        htt.get("pre_repair_commit_superseded") != EXPECTED_HTT_PRE_REPAIR
        or htt.get("commit") != EXPECTED_HTT_REPAIR_PAYLOAD
        or htt.get("tree") != EXPECTED_HTT_REPAIR_TREE
        or htt.get("final_receipt_head") != EXPECTED_HTT_FINAL_RECEIPT_HEAD
        or htt.get("workflow_conclusion") != "success"
    ):
        raise ValidationError("stale HTT predecessor or incomplete repaired readback")
    if predecessors.get("sync_map_02c", {}).get("commit") != EXPECTED_PARENT:
        raise ValidationError("02C predecessor pin mismatch")
    conventions = data.get("conventions", {})
    if conventions.get("outward_sky_direction") != "n_sky^a=-e^a":
        raise ValidationError("sky-direction adapter mismatch")
    if conventions.get("metric_signature") != "(-,+,+,+)":
        raise ValidationError("metric signature mismatch")
    oracle = data.get("wolfram_oracle", {})
    if (
        oracle.get("clean_run_status") != "PASS"
        or oracle.get("inputform_sha256") != EXPECTED_WOLFRAM_SHA
        or oracle.get("zero_residual_count") != 10
        or oracle.get("structural_check_count") != 6
        or oracle.get("hostile_mutation_count") != 7
        or oracle.get("dag_check_count") != 5
        or oracle.get("native_repository_file_replay") is not False
    ):
        raise ValidationError("Wolfram oracle receipt mismatch")

def _validate_formula_signatures(formulas: list[dict[str, Any]]) -> None:
    for record in formulas:
        fid = record.get("formula_id")
        if fid not in EXPECTED_FORMULA_IDS:
            raise ValidationError("six-formula union contains an unknown formula")
        ir = record.get("equation_ir")
        if not isinstance(ir, dict) or ir.get("formula_id") != fid:
            raise ValidationError(f"EquationIR identity mismatch for {fid}")
        terms = ir.get("terms")
        if not isinstance(terms, list):
            raise ValidationError(f"term list missing for {fid}")
        actual = []
        for term in terms:
            if not isinstance(term, dict) or set(term) != {"input", "coefficient"}:
                raise ValidationError(f"malformed term in {fid}")
            actual.append((term["input"], _integer_value(term["coefficient"])))
        if actual != EXPECTED_TERMS[fid]:
            labels = {
                "BASS.FRAME.DOPPLER_FACTOR.001": "Doppler signature",
                "BASS.FRAME.ABERRATED_DIRECTION.001": "aberrated-direction signature",
                "BASS.FRAME.SOLID_ANGLE_JACOBIAN.001": "solid-angle signature",
                "BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001": "temperature-pullback signature",
                "BASS.PHOTON.ENERGY_DRIFT.001": "energy-drift signature",
                "BASS.PHOTON.DIRECTION_FLOW.001": "direction-flow signature",
            }
            raise ValidationError(f"{labels[fid]} mismatch")
        if ir.get("dimensions", {}).get("target") != EXPECTED_DIMENSIONS[fid]:
            raise ValidationError(f"dimension mismatch for {fid}")
        if record.get("owner") != "bass" or record.get("authority_effect") != "AUTHORITATIVE_DERIVATION":
            raise ValidationError(f"formula ownership mismatch for {fid}")
        if record.get("consumer_repositories") != EXPECTED_CONSUMERS[fid]:
            raise ValidationError(f"consumer binding mismatch for {fid}")

def _validate_hashes(data: dict[str, Any], formulas: list[dict[str, Any]]) -> None:
    projection_rows = []
    for record in formulas:
        fid = record["formula_id"]
        projection = _semantic_projection(record["equation_ir"])
        if record.get("semantic_projection") != projection:
            raise ValidationError(f"semantic projection mismatch for {fid}")
        if record.get("semantic_hash") != _sha256(projection):
            raise ValidationError(f"semantic hash mismatch for {fid}")
        projection_rows.append({
            "formula_id": fid,
            "semantic_hash": record["semantic_hash"],
            "dependencies": record.get("dependencies"),
            "external_dependencies": record.get("external_dependencies"),
            "consumer_repositories": record.get("consumer_repositories"),
        })
    registry_projection = {
        "formulas": sorted(projection_rows, key=lambda row: row["formula_id"]),
        "internal_dependency_edges": data.get("internal_dependency_edges"),
        "external_dependency_edges": data.get("external_dependency_edges"),
    }
    if data.get("registry_semantic_projection") != registry_projection:
        raise ValidationError("registry semantic projection mismatch")
    if data.get("registry_semantic_hash") != _sha256(registry_projection):
        raise ValidationError("registry semantic hash mismatch")

def validate_export(data: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise ValidationError("export root must be an object")
    _validate_metadata(data)
    formulas = data.get("formulas")
    if not isinstance(formulas, list) or data.get("formula_count") != 6 or len(formulas) != 6:
        raise ValidationError("six-formula union is incomplete")
    ids = [record.get("formula_id") for record in formulas if isinstance(record, dict)]
    if len(ids) != 6 or set(ids) != EXPECTED_FORMULA_IDS or len(ids) != len(set(ids)):
        raise ValidationError("six-formula union identity mismatch")
    _validate_formula_signatures(formulas)
    included = data.get("coverage", {}).get("included")
    if not isinstance(included, list):
        raise ValidationError("scope firewall coverage is malformed")
    included_text = " ".join(str(item).lower() for item in included)
    if any(token in included_text for token in FORBIDDEN_INCLUDED_TOKENS):
        raise ValidationError("scope firewall rejected a forbidden included feature")
    internal_edges = _edge_set(data.get("internal_dependency_edges"), "internal")
    _assert_acyclic(EXPECTED_FORMULA_IDS, internal_edges)
    if internal_edges != EXPECTED_INTERNAL_EDGES:
        raise ValidationError("internal dependency edge set mismatch")
    external_edges = _edge_set(data.get("external_dependency_edges"), "external")
    if external_edges != EXPECTED_EXTERNAL_EDGES:
        raise ValidationError("external dependency edge set mismatch")
    by_id = {record["formula_id"]: record for record in formulas}
    for fid in EXPECTED_FORMULA_IDS:
        expected_internal = sorted(target for source, target in EXPECTED_INTERNAL_EDGES if source == fid)
        expected_external = sorted(target for source, target in EXPECTED_EXTERNAL_EDGES if source == fid)
        if by_id[fid].get("dependencies") != expected_internal:
            raise ValidationError(f"internal dependency record mismatch for {fid}")
        if by_id[fid].get("external_dependencies") != expected_external:
            raise ValidationError(f"external dependency record mismatch for {fid}")
    if data.get("consumer_bindings") != EXPECTED_CONSUMERS:
        raise ValidationError("consumer union mismatch")
    _validate_hashes(data, formulas)
    boundary = data.get("claim_boundary", "")
    for token in ("NO_BACKGROUND_PROVIDER", "GLOBAL_TILT", "FINITE_ELECTRON_COLLISION", "NO", "SCIENCE_PROMOTION"):
        if token not in boundary:
            raise ValidationError("claim boundary is incomplete")
    return {
        "status": "PASS",
        "formula_count": 6,
        "formula_ids": sorted(EXPECTED_FORMULA_IDS),
        "internal_dependency_edges": len(internal_edges),
        "external_dependency_edges": len(external_edges),
        "registry_semantic_hash": data["registry_semantic_hash"],
        "htt_repair_payload": EXPECTED_HTT_REPAIR_PAYLOAD,
        "wolfram_inputform_sha256": EXPECTED_WOLFRAM_SHA,
        "native_wolfram_replay": "NOT_RUN",
    }

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--path", type=Path, default=EXPORT_PATH)
    args = parser.parse_args()
    try:
        report = validate_export(load_export(args.path))
    except ValidationError as exc:
        if args.json:
            print(json.dumps({"status": "FAIL", "error": str(exc)}, sort_keys=True))
        else:
            print(f"FAIL: {exc}")
        return 1
    if args.json:
        print(json.dumps(report, sort_keys=True))
    else:
        print("PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
