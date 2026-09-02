#!/usr/bin/env python3
"""Fail-closed validator for the SYNC-MAP-01 federation packet."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

DOC_NAMES = (
    "SYNC_MAP_01_FORMULA_PATH_INVENTORY.json",
    "SYNC_MAP_01_OVERLAP_LEDGER.json",
    "SYNC_MAP_01_WOLFRAM_RECEIPT.json",
    "SYNC_MAP_01_DAG_UPDATE.json",
    "SYNC_MAP_01_RECEIPT.json",
)


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: top-level JSON must be an object")
    return value


def git_blob_sha1(path: Path) -> str:
    payload = path.read_bytes()
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload).hexdigest()


def validate(root: Path) -> dict[str, Any]:
    docs = root / "docs" / "bianchi_program"
    loaded = {name: load_json(docs / name) for name in DOC_NAMES}
    inventory = loaded[DOC_NAMES[0]]
    overlaps = loaded[DOC_NAMES[1]]
    wolfram = loaded[DOC_NAMES[2]]
    dag = loaded[DOC_NAMES[3]]
    receipt = loaded[DOC_NAMES[4]]

    assert inventory["stage_id"] == "SYNC-MAP-01"
    families = inventory["formula_families"]
    ids = [entry["formula_family_id"] for entry in families]
    assert len(ids) == len(set(ids)), "duplicate formula family IDs"
    assert all(entry["owner"] in {"bass", "rec_bianchi", "rei_bianchi"} for entry in families)
    assert inventory["active_control_line"]["pr"] == 86
    assert inventory["parallel_control_donor"]["automatic_disposition"] == "NONE"

    overlap_ids = {entry["id"] for entry in overlaps["overlaps"]}
    assert overlap_ids == {f"OVL-{index:03d}" for index in range(1, 8)}
    geometry = next(entry for entry in overlaps["overlaps"] if entry["id"] == "OVL-001")
    assert geometry["required_action"] == "SYNC-MAP-01C_GEOMETRY_LINEAGE_COMPOSITION"
    shared = next(entry for entry in overlaps["overlaps"] if entry["id"] == "OVL-003")
    assert shared["automatic_action_taken"] == "PROVISIONAL_WOLFRAM_EQUIVALENCE_ONLY"

    assert wolfram["status"] == "PASS"
    assert set(wolfram["verified_residuals"].values()) == {"0"}
    hashes = wolfram["provisional_formula_hashes"]
    assert len(hashes) == 5
    assert all(len(value) == 64 and int(value, 16) >= 0 for value in hashes.values())
    assert "NO_GLOBAL_SEMANTIC_IDENTITY_PROMOTION" in wolfram["claim_boundary"]

    assert dag["proposed_official_edge_mutations"] == []
    assert dag["automatic_scientific_claim_changes"] == []
    assert receipt["status"] == "PASS_WITH_FINDINGS"
    assert receipt["next_node"] == "SYNC-MAP-01C_GEOMETRY_LINEAGE_COMPOSITION"
    assert "PROVIDER_ADMISSION" in receipt["withheld_claims"]

    manifest = load_json(docs / "SYNC_MAP_01_GIT_BLOB_MANIFEST.json")
    assert manifest["identity_domain"] == "git_blob_sha1"
    entries = manifest["entries"]
    assert len(entries) >= 7
    for entry in entries:
        path = root / entry["path"]
        assert path.is_file(), f"missing manifest path: {entry['path']}"
        assert git_blob_sha1(path) == entry["git_blob_sha1"], f"Git blob mismatch: {entry['path']}"

    return {
        "status": "PASS",
        "formula_families": len(families),
        "overlap_findings": len(overlaps["overlaps"]),
        "wolfram_hashes": len(hashes),
        "manifest_entries": len(entries),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    print(json.dumps(validate(args.root), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
