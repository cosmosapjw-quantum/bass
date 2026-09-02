#!/usr/bin/env python3
"""Fail-closed verifier for SYNC-MAP-02C active REI relation classification.

This validates identity, ownership, relation classes, blockers, and the proposed
DAG adjustment.  It does not establish numerical parity, provider admission,
Bianchi-background implementation, or scientific validity.
"""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import re
import sys

EXPECTED_STAGE = "SYNC_MAP_02C_REI_RELATION_CLASSIFICATION"
EXPECTED_BASS_PARENT = "f1eab555b42ebfaa3aa9d4021e097750aa0dfd96"
EXPECTED_FORMULA_PARENT = "6587c081932d1dddda586781825d242616ca1357"
EXPECTED_REI_COMMIT = "f4eb2c893ce6449f8899ab6f02c83421fc7c7019"
EXPECTED_REI_TREE = "16d060d45ddfa401e4a5c22f9ca53cf65399ff51"
EXPECTED_REI_SRC_TREE = "f1708900abe8a912637d87ab506c7273b50266ae"
EXPECTED_CLASSES = {
    "PINNED_ARTIFACT_IMPORT_REQUIRED": 2,
    "BASELINE_CONTROL_ORACLE": 1,
    "ADAPTER_SPECIALIZATION": 2,
    "OWNED_EXTENSION": 5,
    "OWNED_FEASIBILITY_GATE": 1,
}
EXPECTED_REC_GAPS = [
    "BASS.FRAME.ABERRATED_DIRECTION.001",
    "BASS.FRAME.DOPPLER_FACTOR.001",
    "BASS.PHOTON.DIRECTION_FLOW.001",
    "BASS.PHOTON.ENERGY_DRIFT.001",
]
REQUIRED_WITHHELD = {
    "REI_BIANCHI_GEOMETRY_IMPLEMENTATION",
    "BASS_NUMERICAL_BACKGROUND_LOCK",
    "GLOBAL_TILT",
    "LOCAL_OBSERVER_BOOST",
    "EXACT_ELECTRON_FRAME_THOMSON_CMB_PATH",
    "FIRST_CANONICAL_INTERVAL",
    "REI_PROVIDER_EXPORT",
    "CROSS_REPOSITORY_SEMANTIC_EQUIVALENCE",
    "OFFICIAL_DAG_MUTATION",
    "SCIENCE_VALIDITY",
    "PASS_RF04",
}
SHA1 = re.compile(r"[0-9a-f]{40}\Z")


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def main() -> int:
    if len(sys.argv) > 2:
        fail("usage: verify_sync_map02c_rei_relations.py [classification.json]")
    path = Path(sys.argv[1]) if len(sys.argv) == 2 else Path(
        "docs/bass_master_ssot_v2/SYNC_MAP_02C/REI_RELATION_CLASSIFICATION.json"
    )
    data = json.loads(path.read_text(encoding="utf-8"))

    if data.get("stage_id") != EXPECTED_STAGE:
        fail("wrong stage ID")
    if data.get("bass_relation_parent", {}).get("commit") != EXPECTED_BASS_PARENT:
        fail("wrong BASS relation parent")
    if data.get("bass_formula_parent", {}).get("commit") != EXPECTED_FORMULA_PARENT:
        fail("wrong BASS formula parent")
    if data.get("bass_formula_parent", {}).get("formula_count") != 14:
        fail("BASS formula count must remain fourteen")

    rei = data.get("rei_lineage", {})
    expected_rei = {
        "commit": EXPECTED_REI_COMMIT,
        "tree": EXPECTED_REI_TREE,
        "src_tree": EXPECTED_REI_SRC_TREE,
        "src_file_count": 22,
    }
    for key, expected in expected_rei.items():
        if rei.get(key) != expected:
            fail(f"wrong REI lineage field {key}")

    sources = data.get("exact_rei_sources", [])
    if len(sources) != 9:
        fail("exact load-bearing REI source set must contain nine files")
    source_paths = [item.get("path") for item in sources]
    if len(source_paths) != len(set(source_paths)):
        fail("duplicate REI source path")
    for item in sources:
        if not isinstance(item.get("path"), str) or not item["path"].startswith("src/rei_bianchi/"):
            fail("non-source path in exact REI source set")
        if not isinstance(item.get("git_blob_sha1"), str) or SHA1.fullmatch(item["git_blob_sha1"]) is None:
            fail(f"invalid Git blob identity for {item.get('path')}")
        if not isinstance(item.get("role"), str) or not item["role"]:
            fail(f"missing source role for {item.get('path')}")

    scope = data.get("source_scope", {})
    if scope.get("all_src_paths_enumerated") is not True:
        fail("source path enumeration must be true")
    if scope.get("all_src_file_contents_semantically_adjudicated") is not False:
        fail("bounded source audit must not claim full content adjudication")
    if scope.get("historical_all_branch_deduplication") is not False:
        fail("historical all-branch deduplication must remain false")

    relations = data.get("relations", [])
    summary = data.get("relation_summary", {})
    if len(relations) != 11 or summary.get("relation_count") != 11:
        fail("relation count must be eleven")
    ids = [item.get("relation_id") for item in relations]
    if len(ids) != len(set(ids)) or any(not isinstance(item, str) or not item for item in ids):
        fail("relation IDs must be unique nonempty strings")
    classes = Counter(item.get("relation_class") for item in relations)
    if dict(classes) != EXPECTED_CLASSES or summary.get("classes") != EXPECTED_CLASSES:
        fail(f"unexpected relation classes: {dict(classes)}")
    if summary.get("duplicate_derivation_count") != 0:
        fail("duplicate derivation count must remain zero")
    source_set = set(source_paths)
    for item in relations:
        if item.get("consumer") != "rei_bianchi":
            fail(f"foreign consumer in {item.get('relation_id')}")
        if item.get("source_path") not in source_set:
            fail(f"unbound source in {item.get('relation_id')}")
        if item.get("source_blob") != next(
            source["git_blob_sha1"] for source in sources if source["path"] == item["source_path"]
        ):
            fail(f"source blob drift in {item.get('relation_id')}")
        if not isinstance(item.get("authority_effect"), str) or not item["authority_effect"]:
            fail(f"missing authority effect in {item.get('relation_id')}")

    matrix = data.get("bass_geometry_matrix", {})
    if matrix.get("formula_count") != 14:
        fail("geometry matrix formula count must be fourteen")
    if matrix.get("NO_ACTIVE_REI_REDERIVATION_DETECTED") != 14:
        fail("all fourteen geometry formulas must remain without active REI rederivation")
    if matrix.get("DUPLICATE_AUTHORITY") != 0:
        fail("duplicate BASS/REI geometry authority detected")

    shared = data.get("shared_export_result", {})
    if shared.get("rec_frame_photon_formula_gaps_retained") != EXPECTED_REC_GAPS:
        fail("REC shared frame/photon gaps drifted")
    if shared.get("new_rei_equationir_duplicate_gap_count") != 0:
        fail("unexpected REI EquationIR duplicate gap")
    if shared.get("new_rei_artifact_contract_gap") != "BASS_NUMERICAL_BACKGROUND_PROVIDER_AND_EXACT_LOCK":
        fail("REI numerical background lock gap is not explicit")

    boundaries = data.get("implementation_boundaries", {})
    required_false = {
        "numerical_bass_lock_implemented",
        "bianchi_geometry_implemented_in_rei",
        "global_tilt_implemented_in_rei",
        "local_observer_boost_implemented_in_rei",
        "exact_electron_frame_thomson_for_cmb_implemented_in_rei",
        "first_canonical_interval_passed",
        "provider_export_authorized",
    }
    bad_boundaries = sorted(key for key in required_false if boundaries.get(key) is not False)
    if bad_boundaries:
        fail(f"implementation boundary promoted: {bad_boundaries}")

    wolfram = data.get("wolfram", {})
    if wolfram.get("first_attempt") != "FAIL_HARNESS_JACOBIAN_CHECK_ONLY_14_OF_15":
        fail("initial Wolfram harness failure was not preserved")
    if wolfram.get("final_status") != "PASS_15_OF_15":
        fail("final Wolfram status is not 15/15 PASS")
    if wolfram.get("impact_dag_acyclic") is not True or wolfram.get("xact_required") is not False:
        fail("Wolfram graph or xAct scope drift")

    impact = data.get("impact_dag", {})
    if impact.get("proposal_only") is not True or impact.get("official_dag_mutated") is not False:
        fail("proposal/official DAG boundary violated")
    edge = impact.get("new_dependency_edge", {})
    if edge != {
        "from": "BASS.BG02_IMPLEMENT",
        "to": "REI.BASS_NUMERICAL_BACKGROUND_LOCK",
        "kind": "requires_execution",
    }:
        fail("background-lock dependency edge drifted")

    missing_withheld = sorted(REQUIRED_WITHHELD - set(data.get("withheld_claims", [])))
    if missing_withheld:
        fail(f"missing withheld claims: {missing_withheld}")

    print(json.dumps({
        "status": "PASS",
        "stage_id": EXPECTED_STAGE,
        "source_count": len(sources),
        "relation_count": len(relations),
        "class_counts": dict(classes),
        "bass_geometry_no_rederivation": 14,
        "duplicate_authority": 0,
        "shared_frame_photon_gaps": 4,
        "new_rei_artifact_contract_gap": shared["new_rei_artifact_contract_gap"],
        "claim_effect": "NONE",
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
