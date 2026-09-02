#!/usr/bin/env python3
"""Fail-closed verifier for SYNC-MAP-02D HTT relation classification."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter, deque
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "docs" / "bass_master_ssot_v2" / "SYNC_MAP_02D"
CLASSIFICATION = STAGE / "HTT_RELATION_CLASSIFICATION.json"
CSV_MATRIX = STAGE / "HTT_RELATION_CLASSES.csv"

EXPECTED_PARENT = "f1eab555b42ebfaa3aa9d4021e097750aa0dfd96"
EXPECTED_HTT_HEADS = {
    "wu010": "29427a1f7f2c5d46e43ffe03053c4ac13e969228",
    "wu011": "978fbe612a570b9973b17c51237965f16b630fc4",
}
EXPECTED_CLASSES = {
    "PINNED_IMPORT_PENDING_OWNER_EQUATIONIR": 4,
    "ADAPTER_SPECIALIZATION": 1,
    "INDEPENDENT_ORACLE": 2,
    "HTT_OWNED_PROCESSED_EXTENSION": 5,
}
EXPECTED_PENDING = {
    "BASS.FRAME.ABERRATED_DIRECTION.001",
    "BASS.FRAME.DOPPLER_FACTOR.001",
    "BASS.FRAME.SOLID_ANGLE_JACOBIAN.001",
    "BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001",
}
EXPECTED_NEW_HTT_GAPS = {
    "BASS.FRAME.SOLID_ANGLE_JACOBIAN.001",
    "BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001",
}
EXPECTED_REC_ONLY = {
    "BASS.PHOTON.DIRECTION_FLOW.001",
    "BASS.PHOTON.ENERGY_DRIFT.001",
}
EXPECTED_WITHHELD = {
    "BASS_SHARED_FRAME_PHOTON_EQUATIONIR_EXPORT",
    "CROSS_REPOSITORY_SEMANTIC_EQUIVALENCE",
    "GLOBAL_MATTER_TILT",
    "FINITE_ELECTRON_TILT_COLLISION",
    "EMPIRICAL_BETA",
    "BIANCHI_FAMILY_ATTRIBUTION",
    "PROVIDER_ADMISSION",
    "SCIENCE_VALIDITY",
}
HEX40 = re.compile(r"^[0-9a-f]{40}$")


class VerificationError(RuntimeError):
    """Raised when the committed classification violates its contract."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise VerificationError(f"cannot parse {path.relative_to(ROOT)}: {exc}") from exc
    require(isinstance(value, dict), "classification root must be an object")
    return value


def topological_order(nodes: list[str], edges: list[list[str]]) -> list[str]:
    require(len(nodes) == len(set(nodes)), "DAG node IDs are not unique")
    node_set = set(nodes)
    indegree = {node: 0 for node in nodes}
    outgoing: dict[str, list[str]] = {node: [] for node in nodes}
    for edge in edges:
        require(isinstance(edge, list) and len(edge) == 2, "every DAG edge must be a pair")
        source, target = edge
        require(source in node_set and target in node_set, f"foreign DAG endpoint: {edge}")
        outgoing[source].append(target)
        indegree[target] += 1
    ready = deque(sorted(node for node, degree in indegree.items() if degree == 0))
    order: list[str] = []
    while ready:
        node = ready.popleft()
        order.append(node)
        for target in sorted(outgoing[node]):
            indegree[target] -= 1
            if indegree[target] == 0:
                ready.append(target)
    require(len(order) == len(nodes), "impact graph contains a directed cycle")
    return order


def verify_csv(relations: list[dict[str, Any]]) -> None:
    try:
        with CSV_MATRIX.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
    except (OSError, UnicodeError, csv.Error) as exc:
        raise VerificationError(f"cannot parse CSV relation matrix: {exc}") from exc
    require(len(rows) == len(relations), "CSV/JSON relation counts differ")
    json_projection = [
        (
            row["relation_id"],
            row["formula_id"],
            row["relation"],
            row["authority_owner"],
            row["source_path"],
        )
        for row in relations
    ]
    csv_projection = [
        (
            row["relation_id"],
            row["formula_id"],
            row["relation"],
            row["authority_owner"],
            row["source_path"],
        )
        for row in rows
    ]
    require(csv_projection == json_projection, "CSV relation matrix drifted from JSON authority")


def verify(data: dict[str, Any]) -> dict[str, Any]:
    require(data.get("stage_id") == "SYNC_MAP_02D_HTT_RELATION_CLASSIFICATION", "wrong stage ID")
    require(data.get("status") == "PASS_WITH_SHARED_FORMULA_EXPORT_GAPS", "wrong stage status")
    require(data.get("bass_parent", {}).get("commit") == EXPECTED_PARENT, "moved BASS parent")
    for lane, head in EXPECTED_HTT_HEADS.items():
        require(data.get("htt_lineages", {}).get(lane, {}).get("commit") == head, f"moved HTT {lane} head")

    sources = data.get("exact_htt_sources")
    require(isinstance(sources, list) and len(sources) == 8, "expected eight exact HTT source pins")
    source_paths: set[str] = set()
    for source in sources:
        require(isinstance(source, dict), "source pin must be an object")
        path = source.get("path")
        digest = source.get("git_blob_sha1")
        require(isinstance(path, str) and path.startswith("htt/obsstat/"), f"invalid HTT source path: {path!r}")
        require(path not in source_paths, f"duplicate HTT source path: {path}")
        require(isinstance(digest, str) and HEX40.fullmatch(digest) is not None, f"invalid Git blob SHA-1 for {path}")
        source_paths.add(path)

    relations = data.get("relations")
    require(isinstance(relations, list) and len(relations) == 12, "expected twelve relation records")
    ids = [row.get("relation_id") for row in relations]
    formulas = [row.get("formula_id") for row in relations]
    require(len(ids) == len(set(ids)), "relation IDs are not unique")
    require(len(formulas) == len(set(formulas)), "formula IDs are not unique")
    require(all(row.get("source_path") in source_paths for row in relations), "relation references an unpinned source")

    observed_classes = Counter(row.get("relation") for row in relations)
    require(dict(observed_classes) == EXPECTED_CLASSES, f"relation class counts drifted: {dict(observed_classes)}")
    summary = data.get("relation_summary", {})
    require(summary.get("relation_count") == len(relations), "summary relation count drifted")
    require(summary.get("classes") == EXPECTED_CLASSES, "summary class counts drifted")
    require(summary.get("duplicate_authority_count") == 0, "duplicate authority is not allowed")
    require(summary.get("unresolved_count") == 0, "unresolved relation is not allowed in a PASS record")

    pending = set(data.get("pending_bass_imports", []))
    require(pending == EXPECTED_PENDING, f"pending BASS import set drifted: {sorted(pending)}")
    gap = data.get("shared_gap_union", {})
    require(set(gap.get("new_from_htt_02d", [])) == EXPECTED_NEW_HTT_GAPS, "HTT-only gap set drifted")
    require(set(gap.get("rec_only_pending_not_consumed_by_htt", [])) == EXPECTED_REC_ONLY, "REC-only flow gap set drifted")
    require(set(gap.get("union_after_02b_and_02d_before_02c", [])) == EXPECTED_PENDING | EXPECTED_REC_ONLY, "02B+02D gap union is incomplete")

    firewall = data.get("semantic_firewall", {})
    require(firewall.get("local_observer_boost") == "IMPLEMENTED_SCOPED_HTT_OUTPUT_SIDE", "local boost scope drifted")
    require(firewall.get("global_matter_frame_tilt") == "NO_ACTIVE_HTT_IMPLEMENTATION", "HTT must not own global tilt")
    require(firewall.get("finite_electron_tilt_collision") == "NO_ACTIVE_HTT_IMPLEMENTATION", "HTT must not own finite-tilt collision")
    require(firewall.get("processed_scalar_cutsky_response") == "IMPLEMENTED_SYNTHETIC_ONLY", "processed scalar scope drifted")
    require(firewall.get("empirical_beta_fit") == "NOT_IMPLEMENTED", "empirical beta was silently promoted")
    require(firewall.get("bianchi_family_attribution") == "NOT_IMPLEMENTED", "Bianchi attribution was silently promoted")

    checks = data.get("wolfram_exact_checks", {})
    require(checks.get("initial_aggregation_run", {}).get("status") == "FAIL_HARNESS_AGGREGATION", "failure-preserving first run missing")
    corrected = checks.get("corrected_run", {})
    require(corrected.get("status") == "PASS", "corrected Wolfram run is not PASS")
    require(all(value == 0 for value in corrected.get("residuals", {}).values()), "nonzero Wolfram exact residual")
    require(all(value is True for value in corrected.get("structural_checks", {}).values()), "failed Wolfram structural check")
    mutations = checks.get("hostile_mutations", {})
    mutation_keys = [
        "wrong_doppler_sign_detected",
        "wrong_jacobian_power_detected",
        "omitted_dipole_detected",
        "omitted_octupole_detected",
        "missing_02d_to_02e_dependency_detected",
    ]
    require(all(mutations.get(key) is True for key in mutation_keys), "hostile mutation escaped detection")

    impact = data.get("impact_dag", {})
    nodes = impact.get("nodes")
    edges = impact.get("edges")
    require(isinstance(nodes, list) and isinstance(edges, list), "impact DAG is missing")
    order = topological_order(nodes, edges)
    edge_set = {tuple(edge) for edge in edges}
    require(("02C_REI", "02E_SHARED_EXPORT") in edge_set, "shared export lacks REI relation prerequisite")
    require(("02D_HTT", "02E_SHARED_EXPORT") in edge_set, "shared export lacks HTT relation prerequisite")
    require(("02E_SHARED_EXPORT", "02F_SEMANTIC_GRAPH") in edge_set, "semantic graph must follow shared export")
    require(sum(target == "SYNC_GATE_01" for _, target in edge_set) == 3, "manual sync gate needs three inputs")

    withheld = set(data.get("withheld_claims", []))
    require(EXPECTED_WITHHELD <= withheld, "load-bearing withheld claims are incomplete")
    require(data.get("claim_boundary") == "HTT_RELATION_CLASSIFICATION_ONLY_NO_SHARED_EXPORT_GLOBAL_TILT_DATA_FIT_PROVIDER_OR_SCIENCE_PROMOTION", "claim boundary drifted")
    verify_csv(relations)
    return {
        "status": "PASS",
        "relations": len(relations),
        "source_pins": len(sources),
        "pending_bass_imports": len(pending),
        "new_htt_shared_gaps": len(EXPECTED_NEW_HTT_GAPS),
        "duplicate_authority_count": 0,
        "dag_nodes": len(nodes),
        "dag_edges": len(edges),
        "topological_order": order,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="emit compact machine-readable output")
    args = parser.parse_args()
    try:
        result = verify(load_json(CLASSIFICATION))
    except VerificationError as exc:
        if args.json:
            print(json.dumps({"status": "FAIL", "error": str(exc)}, sort_keys=True))
        else:
            print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    else:
        print("PASS")
        for key, value in result.items():
            if key != "status":
                print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
