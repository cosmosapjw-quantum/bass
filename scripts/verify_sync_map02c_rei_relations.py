#!/usr/bin/env python3
"""Fail-closed verifier for the bounded SYNC-MAP-02C REI closeout.

The verifier establishes exact source-path coverage, relation ownership and
federation-gate structure only. It does not establish provider admission,
numerical Bianchi transport, cross-repository semantic equivalence or science
validity.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import json
from pathlib import Path
from typing import NoReturn


EXPECTED_SOURCE_BLOBS = {
    "src/rei_bianchi/absorption_decomposition.py": "5f797469eaa67847fa3c5f3701a5b8416a55d98e",
    "src/rei_bianchi/b2b_physical_model.py": "b3cc5e45988687b76d5be04c6335009b4c9bd17f",
    "src/rei_bianchi/bass_integration_substrate.py": "3c0f68cb0e40e3826a3d80dfce2fcdd5065fd826",
    "src/rei_bianchi/certificate_graph.py": "afe9c5afc6b2d2b75283f50e4223c371b90746d0",
    "src/rei_bianchi/gamma_conditioned_reconciliation.py": "1328e49baa0f4bb5d4e1d5a5ca0940c10e8852d5",
    "src/rei_bianchi/global_moment_constrained_macro_sink.py": "389753d94a291fffbfb2b09092029d61afb3ea19",
    "src/rei_bianchi/hi_transmission_kernel_b2c1a.py": "7ec9bd5548db4c024c075b70d0affc81eccfe0d7",
    "src/rei_bianchi/hierarchical_two_scale_closure.py": "ecb55acd39aba9d609f2eb704ef282018d6666b2",
    "src/rei_bianchi/joint_implicit_remainder.py": "cdd24e2e17897bf2bfe102814b123668d884c456",
    "src/rei_bianchi/joint_sink_reservoir_history.py": "604697415f4de9363951653165f90273f297e0b0",
    "src/rei_bianchi/matched_history_feasibility_gate.py": "3d80474e7ba1ecba4f102c5dd85b6efa2bfb0ec3",
    "src/rei_bianchi/monolithic_model_b2a.py": "3d806e1c1d3bb523bb3c339d1a141f67d7f10069",
    "src/rei_bianchi/multigroup_hhe_transmission.py": "5b74a4036c8cb21a2cb772dd3d373c5f96d5a36c",
    "src/rei_bianchi/node_lift_operator.py": "6f5c13f02d0e549e581a02d3c4d8b8313b209bbf",
    "src/rei_bianchi/node_resolved_joint_history.py": "69e671769d70804be6f7debc4b9ba1f11519bbfc",
    "src/rei_bianchi/phase_space_kernel_b2c0.py": "026a22b1843ab3a3336b210317727e216202fc75",
    "src/rei_bianchi/primary_exact_zero_model.py": "ea2a10a60114622fd1215b692be3dd0d04ef0c6d",
    "src/rei_bianchi/reiaff1.py": "80a7627baf5981375de10ae55d862b09b0071432",
    "src/rei_bianchi/run_first_interval_refinement.py": "5d39fef633662178a71685dac90e4ffe9a0a788d",
    "src/rei_bianchi/run_node_lift.py": "83abebd1a4f7e7a6f5fba83d4a20e1b23063fa02",
    "src/rei_bianchi/run_primary_diagnostics.py": "1c295b27d692618fffef442182d1595feac56d7d",
    "src/rei_bianchi/source_bound_mprk_sdirk_operator.py": "fba94e59d20d640237290911abd774ede3fe5360",
}

EXPECTED_SHARED_CONSUMERS = {
    "BASS.FRAME.ABERRATED_DIRECTION.001": {"rec_bianchi", "htt_base"},
    "BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001": {"htt_base"},
    "BASS.FRAME.DOPPLER_FACTOR.001": {"rec_bianchi", "htt_base"},
    "BASS.FRAME.SOLID_ANGLE_JACOBIAN.001": {"htt_base"},
    "BASS.PHOTON.DIRECTION_FLOW.001": {"rec_bianchi", "rei_bianchi"},
    "BASS.PHOTON.ENERGY_DRIFT.001": {"rec_bianchi", "rei_bianchi"},
}

EXPECTED_CLASS_COUNTS = Counter(
    {
        "PINNED_ARTIFACT_IMPORT_REQUIRED": 3,
        "BASELINE_CONTROL_ORACLE": 1,
        "ADAPTER_SPECIALIZATION": 2,
        "OWNED_EXTENSION": 5,
        "OWNED_FEASIBILITY_GATE": 1,
    }
)
ALLOWED_OWNERS = {"bass", "rec_bianchi", "rei_bianchi", "htt_base"}
EXPECTED_GATE_PREDECESSORS = {"SYNC_MAP_02C_REI", "SYNC_MAP_02D_HTT"}
REQUIRED_WITHHELD = {
    "SYNC_MAP_02E_STARTED",
    "CROSS_REPOSITORY_SEMANTIC_EQUIVALENCE",
    "GENERIC_BIANCHI_GROUP_REDSHIFT_TRANSPORT",
    "BASS_NUMERICAL_BACKGROUND_LOCK",
    "FIRST_CANONICAL_INTERVAL",
    "REI_PROVIDER_EXPORT",
    "SCIENCE_VALIDITY",
    "PASS_RF04",
}


def fail(code: str, detail: str) -> NoReturn:
    print(f"{code}: {detail}")
    raise SystemExit(1)


def load_json(path: Path) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail("FAIL_JSON_LOAD", f"{path}: {exc}")
    if not isinstance(value, dict):
        fail("FAIL_JSON_TYPE", "classification root must be an object")
    return value


def load_coverage(path: Path) -> list[dict[str, str]]:
    try:
        with path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
    except OSError as exc:
        fail("FAIL_COVERAGE_LOAD", f"{path}: {exc}")
    if len(rows) != 22:
        fail("FAIL_COVERAGE_COUNT", f"expected 22 rows, observed {len(rows)}")
    return rows


def verify(classification: dict[str, object], rows: list[dict[str, str]]) -> dict[str, object]:
    if classification.get("stage_id") != "SYNC_MAP_02C_REI_RELATION_CLASSIFICATION":
        fail("FAIL_STAGE_ID", repr(classification.get("stage_id")))
    if classification.get("schema_version") != "1.0.3":
        fail("FAIL_SCHEMA_VERSION", repr(classification.get("schema_version")))

    source_scope = classification.get("source_scope")
    if not isinstance(source_scope, dict):
        fail("FAIL_SOURCE_SCOPE", "source_scope must be an object")
    if source_scope.get("coverage_row_count") != 22:
        fail("FAIL_SOURCE_SCOPE", "coverage_row_count must be 22")
    if source_scope.get("all_exact_src_paths_bound") is not True:
        fail("FAIL_SOURCE_SCOPE", "all_exact_src_paths_bound must be true")
    if source_scope.get("all_src_paths_have_machine_bound_relation_or_exclusion") is not True:
        fail("FAIL_SOURCE_SCOPE", "every source path requires a relation or exclusion")
    if source_scope.get("historical_all_branch_deduplication") is not False:
        fail("FAIL_CLAIM_BOUNDARY", "historical all-branch closure is forbidden")

    observed_paths = [row.get("source_path", "") for row in rows]
    if len(observed_paths) != len(set(observed_paths)):
        fail("FAIL_COVERAGE_PATH_SET", "duplicate source path")
    if set(observed_paths) != set(EXPECTED_SOURCE_BLOBS):
        missing = sorted(set(EXPECTED_SOURCE_BLOBS) - set(observed_paths))
        extra = sorted(set(observed_paths) - set(EXPECTED_SOURCE_BLOBS))
        fail("FAIL_COVERAGE_PATH_SET", f"missing={missing}, extra={extra}")
    for row in rows:
        path = row["source_path"]
        if row.get("git_blob_sha1") != EXPECTED_SOURCE_BLOBS[path]:
            fail(
                "FAIL_COVERAGE_BLOB",
                f"{path}: expected {EXPECTED_SOURCE_BLOBS[path]}, observed {row.get('git_blob_sha1')}",
            )
        for field in (
            "source_role",
            "semantic_disposition",
            "relation_ids",
            "shared_owner_occurrence",
            "shared_owner_gap_effect",
            "evidence_scope",
        ):
            if not row.get(field):
                fail("FAIL_COVERAGE_FIELD", f"{path}: empty {field}")

    relations = classification.get("relations")
    if not isinstance(relations, list) or len(relations) != 12:
        observed = 0 if not isinstance(relations, list) else len(relations)
        fail("FAIL_RELATION_COUNT", f"expected 12, observed {observed}")
    relation_ids: list[str] = []
    relation_classes: list[str] = []
    for relation in relations:
        if not isinstance(relation, dict):
            fail("FAIL_RELATION_TYPE", "every relation must be an object")
        relation_id = relation.get("relation_id")
        if not isinstance(relation_id, str) or not relation_id:
            fail("FAIL_RELATION_ID", repr(relation_id))
        relation_ids.append(relation_id)
        owner = relation.get("owner")
        if owner not in ALLOWED_OWNERS:
            fail("FAIL_MULTI_OWNER", f"{relation_id}: {owner!r}")
        relation_class = relation.get("relation_class")
        if not isinstance(relation_class, str):
            fail("FAIL_RELATION_CLASS", relation_id)
        relation_classes.append(relation_class)
    if len(relation_ids) != len(set(relation_ids)):
        fail("FAIL_RELATION_ID", "duplicate relation IDs")
    if Counter(relation_classes) != EXPECTED_CLASS_COUNTS:
        fail("FAIL_RELATION_CLASSES", repr(Counter(relation_classes)))

    relation_id_set = set(relation_ids)
    for row in rows:
        declared = row["relation_ids"]
        if declared == "NONE":
            continue
        unknown = set(declared.split(";")) - relation_id_set
        if unknown:
            fail("FAIL_COVERAGE_RELATION", f"{row['source_path']}: {sorted(unknown)}")

    summary = classification.get("relation_summary")
    if not isinstance(summary, dict):
        fail("FAIL_RELATION_SUMMARY", "missing relation summary")
    if summary.get("relation_count") != 12 or summary.get("single_owner_invariant") is not True:
        fail("FAIL_RELATION_SUMMARY", "count or single-owner flag mismatch")
    if Counter(summary.get("relation_class_counts", {})) != EXPECTED_CLASS_COUNTS:
        fail("FAIL_RELATION_SUMMARY", "declared class counts mismatch")
    if summary.get("duplicate_derivation_count") != 0:
        fail("FAIL_DUPLICATE_AUTHORITY", "duplicate relation authority is forbidden")
    if summary.get("new_rei_frame_photon_formula_gap_count") != 0:
        fail("FAIL_SHARED_UNION", "REI may not silently add an unclassified gap")

    union = classification.get("shared_formula_consumer_union")
    if not isinstance(union, dict) or set(union) != set(EXPECTED_SHARED_CONSUMERS):
        observed = sorted(union) if isinstance(union, dict) else union
        fail("FAIL_SHARED_UNION", f"observed={observed!r}")
    for formula_id, consumers in EXPECTED_SHARED_CONSUMERS.items():
        observed = union.get(formula_id)
        if not isinstance(observed, list) or set(observed) != consumers:
            fail("FAIL_SHARED_CONSUMERS", f"{formula_id}: {observed!r}")

    export_result = classification.get("shared_export_result")
    if not isinstance(export_result, dict):
        fail("FAIL_SHARED_UNION", "missing shared_export_result")
    if export_result.get("union_formula_count") != 6:
        fail("FAIL_SHARED_UNION", "union_formula_count must be six")
    if export_result.get("frame_photon_export_is_separate_from_background_provider") is not True:
        fail("FAIL_EXPORT_CONFLATION", "frame/photon and background-provider lanes must be separate")

    gate = classification.get("next_stage_gate")
    if not isinstance(gate, dict):
        fail("FAIL_02E_GATE", "missing next-stage gate")
    if gate.get("node") != "SYNC_MAP_02E_SHARED_FRAME_PHOTON_EXPORT":
        fail("FAIL_02E_GATE", repr(gate.get("node")))
    if gate.get("status") != "HELD_UNTIL_02C_AND_02D_FROZEN_READBACK":
        fail("FAIL_02E_GATE", repr(gate.get("status")))
    predecessors = gate.get("required_predecessors")
    if not isinstance(predecessors, list) or set(predecessors) != EXPECTED_GATE_PREDECESSORS:
        fail("FAIL_02E_GATE", f"predecessors={predecessors!r}")

    geometry = classification.get("bass_geometry_matrix")
    if not isinstance(geometry, dict):
        fail("FAIL_GEOMETRY_MATRIX", "missing BASS geometry matrix")
    if geometry.get("formula_count") != 14 or geometry.get("NO_ACTIVE_REI_REDERIVATION_DETECTED") != 14:
        fail("FAIL_GEOMETRY_MATRIX", repr(geometry))
    if geometry.get("DUPLICATE_AUTHORITY") != 0:
        fail("FAIL_DUPLICATE_AUTHORITY", "BASS geometry duplicate detected")

    authorities = classification.get("exact_authorities")
    if not isinstance(authorities, dict):
        fail("FAIL_AUTHORITY", "missing exact authorities")
    htt = authorities.get("htt_relation_map")
    if not isinstance(htt, dict):
        fail("FAIL_AUTHORITY", "missing HTT relation authority")
    if htt.get("commit") != "06aa29f78c26bcafeb60d85b719a4d3aa5c4c2e8":
        fail("FAIL_AUTHORITY", "wrong HTT relation-map head")
    if htt.get("workflow_run") != 33601836772 or htt.get("workflow_conclusion") != "success":
        fail("FAIL_AUTHORITY", "HTT exact-head workflow is not frozen as success")

    withheld = classification.get("withheld_claims")
    if not isinstance(withheld, list) or not REQUIRED_WITHHELD <= set(withheld):
        fail("FAIL_CLAIM_BOUNDARY", "required withheld claims missing")

    return {
        "status": "PASS",
        "stage_id": classification["stage_id"],
        "source_rows": len(rows),
        "relation_count": len(relations),
        "relation_class_counts": dict(sorted(Counter(relation_classes).items())),
        "shared_union": sorted(union),
        "bass_geometry_no_rederivation": 14,
        "single_owner_invariant": True,
        "next_stage": gate["node"],
        "next_stage_status": gate["status"],
        "claim_effect": "NONE",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    root = Path("docs/bass_master_ssot_v2/SYNC_MAP_02C")
    parser.add_argument(
        "--classification",
        type=Path,
        default=root / "REI_RELATION_CLASSIFICATION_R3.json",
    )
    parser.add_argument(
        "--coverage",
        type=Path,
        default=root / "REI_SOURCE_COVERAGE_MATRIX.csv",
    )
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = verify(load_json(args.classification), load_coverage(args.coverage))
    if args.json:
        print(json.dumps(report, sort_keys=True))
    else:
        for key, value in report.items():
            print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
