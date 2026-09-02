#!/usr/bin/env python3
"""Validate and fingerprint the bounded SYNC-MAP-01 path inventory.

This stage classifies formula-like paths on exact active lineages. It does not
claim formula equivalence; EquationIR-level semantic comparison belongs to
SYNC-MAP-02.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Mapping

PROGRAM_ID = "BIANCHI-WOLFRAM-TRIREPO-20260830"
STAGE_ID = "SYNC-MAP-01"
REPOSITORIES = {"bass", "rec_bianchi", "rei_bianchi"}
PATH_ROLES = {
    "FORMULA_SOURCE",
    "SCHEMA",
    "ADAPTER",
    "PROVIDER",
    "ORACLE",
    "TEST",
    "RUNTIME_BRIDGE",
    "GENERATED_SOURCE",
    "RUNNER",
    "PROVENANCE",
    "RECEIPT",
    "SUPPORT",
}
CLASSIFICATIONS = {
    "AUTHORITATIVE_DERIVATION",
    "AUTHORITATIVE_SCHEMA",
    "AUTHORITATIVE_PROVIDER",
    "ADAPTER_SPECIALIZATION",
    "INDEPENDENT_ORACLE",
    "OWNED_EXTENSION",
    "RUNTIME_BRIDGE",
    "PROVENANCE_ONLY",
    "SUPPORT_ONLY",
    "MIXED_OWNERSHIP_REQUIRES_SPLIT",
}
AUTHORITY_EFFECTS = {
    "AUTHORITATIVE_DERIVATION",
    "AUTHORITATIVE_SCHEMA",
    "AUTHORITATIVE_PROVIDER",
    "NONE",
}
SEMANTIC_STATUSES = {"PENDING_SYNC_MAP_02", "NOT_APPLICABLE"}
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


class InventoryError(ValueError):
    """A fail-closed path-inventory contract violation."""

    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


def _require(condition: bool, code: str, detail: str) -> None:
    if not condition:
        raise InventoryError(code, detail)


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _identity_payload(document: Mapping[str, Any]) -> dict[str, Any]:
    payload = copy.deepcopy(dict(document))
    for key in (
        "inventory_run_id",
        "status",
        "summary",
        "verification",
        "wolfram_verification",
    ):
        payload.pop(key, None)
    entries = payload.get("entries", [])
    if isinstance(entries, list):
        payload["entries"] = sorted(
            entries,
            key=lambda item: (item.get("repository", ""), item.get("path", "")),
        )
    return payload


def canonical_identity_text(document: Mapping[str, Any]) -> str:
    return canonical_json_bytes(_identity_payload(document)).decode("utf-8")


def compute_inventory_run_id(document: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_json_bytes(_identity_payload(document))).hexdigest()


def _validate_lineage(repository: str, lineage: Mapping[str, Any]) -> None:
    _require(HEX40.fullmatch(str(lineage.get("commit", ""))) is not None,
             "LINEAGE_COMMIT", f"{repository} commit must be a 40-hex Git object")
    _require(HEX40.fullmatch(str(lineage.get("tree", ""))) is not None,
             "LINEAGE_TREE", f"{repository} tree must be a 40-hex Git object")
    _require(isinstance(lineage.get("pull_request"), int) and lineage["pull_request"] > 0,
             "LINEAGE_PR", f"{repository} pull_request must be positive")
    _require(isinstance(lineage.get("branch"), str) and bool(lineage["branch"]),
             "LINEAGE_BRANCH", f"{repository} branch is required")


def _validate_entry(entry: Mapping[str, Any], index: int) -> None:
    repository = entry.get("repository")
    path = entry.get("path")
    prefix = f"entries[{index}]"
    _require(repository in REPOSITORIES, "ENTRY_REPOSITORY", f"{prefix} has invalid repository")
    _require(isinstance(path, str) and path and not path.startswith("/") and ".." not in Path(path).parts,
             "ENTRY_PATH", f"{prefix} path must be repository-relative")
    blob_sha = entry.get("blob_sha")
    _require(blob_sha is None or (isinstance(blob_sha, str) and HEX40.fullmatch(blob_sha) is not None),
             "ENTRY_BLOB", f"{repository}:{path} blob_sha must be null or 40-hex")
    _require(entry.get("path_role") in PATH_ROLES,
             "PATH_ROLE", f"{repository}:{path} has unsupported path_role")
    classification = entry.get("classification")
    _require(classification in CLASSIFICATIONS,
             "CLASSIFICATION", f"{repository}:{path} has unsupported classification")
    owners = entry.get("owner_candidates")
    _require(isinstance(owners, list) and owners and set(owners).issubset(REPOSITORIES),
             "OWNER_CANDIDATES", f"{repository}:{path} needs repository owner candidates")
    _require(len(owners) == len(set(owners)),
             "OWNER_CANDIDATES_DUPLICATE", f"{repository}:{path} repeats an owner candidate")
    authority_effect = entry.get("authority_effect")
    _require(authority_effect in AUTHORITY_EFFECTS,
             "AUTHORITY_EFFECT", f"{repository}:{path} has unsupported authority effect")
    formula_candidates = entry.get("formula_candidates")
    replay_candidates = entry.get("replay_of_candidates")
    _require(isinstance(formula_candidates, list) and all(isinstance(value, str) and value for value in formula_candidates),
             "FORMULA_CANDIDATES", f"{repository}:{path} formula_candidates must be strings")
    _require(isinstance(replay_candidates, list) and all(isinstance(value, str) and value for value in replay_candidates),
             "REPLAY_CANDIDATES", f"{repository}:{path} replay_of_candidates must be strings")
    mixed = entry.get("mixed_ownership")
    split = entry.get("split_required")
    _require(isinstance(mixed, bool) and isinstance(split, bool),
             "SPLIT_FLAGS", f"{repository}:{path} needs Boolean mixed/split flags")
    if mixed:
        _require(split and len(owners) >= 2,
                 "MIXED_PATH_REQUIRES_SPLIT", f"{repository}:{path} must retain all owners and a split obligation")
    if split:
        _require(mixed, "SPLIT_REQUIRES_MIXED_PATH", f"{repository}:{path} cannot split a single-owner path")
    if classification == "MIXED_OWNERSHIP_REQUIRES_SPLIT":
        _require(mixed and split and authority_effect == "NONE",
                 "MIXED_CLASSIFICATION_CONTRACT", f"{repository}:{path} mixed path cannot assert authority")
    if classification == "INDEPENDENT_ORACLE":
        _require(authority_effect == "NONE",
                 "ORACLE_AUTHORITY_EFFECT", f"{repository}:{path} oracle must have authority_effect NONE")
        _require(bool(replay_candidates),
                 "ORACLE_REPLAY_CANDIDATE", f"{repository}:{path} oracle needs a replay target candidate")
    if classification == "AUTHORITATIVE_DERIVATION":
        _require(owners == [repository] and authority_effect == "AUTHORITATIVE_DERIVATION",
                 "AUTHORITATIVE_DERIVATION_OWNER", f"{repository}:{path} derivation authority must be local and unique")
    if classification == "AUTHORITATIVE_SCHEMA":
        _require(owners == [repository] and authority_effect == "AUTHORITATIVE_SCHEMA",
                 "AUTHORITATIVE_SCHEMA_OWNER", f"{repository}:{path} schema authority must be local and unique")
    if classification == "AUTHORITATIVE_PROVIDER":
        _require(owners == [repository] and authority_effect == "AUTHORITATIVE_PROVIDER",
                 "AUTHORITATIVE_PROVIDER_OWNER", f"{repository}:{path} provider authority must be local and unique")
    if classification in {"ADAPTER_SPECIALIZATION", "RUNTIME_BRIDGE", "PROVENANCE_ONLY", "SUPPORT_ONLY"}:
        _require(authority_effect == "NONE",
                 "NONAUTHORITY_CLASS_EFFECT", f"{repository}:{path} nonauthority class must have effect NONE")
    _require(entry.get("semantic_status") in SEMANTIC_STATUSES,
             "SEMANTIC_STATUS", f"{repository}:{path} must defer equivalence to SYNC-MAP-02 or mark it not applicable")
    evidence = entry.get("evidence")
    _require(isinstance(evidence, list) and evidence and all(isinstance(value, str) and value for value in evidence),
             "ENTRY_EVIDENCE", f"{repository}:{path} needs at least one evidence locator")


def validate_inventory(document: Mapping[str, Any]) -> dict[str, Any]:
    _require(document.get("schema_version") == "1.0.0", "SCHEMA_VERSION", "expected 1.0.0")
    _require(document.get("program_id") == PROGRAM_ID, "PROGRAM_ID", "wrong tri-repository program")
    _require(document.get("stage_id") == STAGE_ID, "STAGE_ID", "wrong inventory stage")
    _require(isinstance(document.get("parent_sync_run_id"), str)
             and HEX64.fullmatch(document["parent_sync_run_id"]) is not None,
             "PARENT_SYNC_RUN_ID", "parent sync_run_id must be a SHA-256")
    control = document.get("control_parent")
    _require(isinstance(control, Mapping) and control.get("repository") == "bass",
             "CONTROL_PARENT", "BASS must own the active coordinator parent")
    _require(HEX40.fullmatch(str(control.get("commit", ""))) is not None
             and HEX40.fullmatch(str(control.get("tree", ""))) is not None,
             "CONTROL_PARENT_IDENTITY", "control parent commit/tree must be exact Git objects")
    lineages = document.get("lineages")
    _require(isinstance(lineages, Mapping) and set(lineages) == REPOSITORIES,
             "LINEAGE_SET", "lineages must cover exactly bass, rec_bianchi, and rei_bianchi")
    for repository in sorted(REPOSITORIES):
        lineage = lineages[repository]
        _require(isinstance(lineage, Mapping), "LINEAGE_OBJECT", f"{repository} lineage must be an object")
        _validate_lineage(repository, lineage)
    scope = document.get("scope")
    _require(isinstance(scope, Mapping)
             and scope.get("coverage") == "ACTIVE_LINEAGE_FORMULA_LIKE_PATHS_BOUNDED"
             and scope.get("semantic_equivalence") == "DEFERRED_TO_SYNC_MAP_02",
             "SCOPE_BOUNDARY", "SYNC-MAP-01 must remain a bounded path inventory")
    entries = document.get("entries")
    _require(isinstance(entries, list) and entries, "ENTRIES", "inventory entries must be a nonempty list")
    seen: set[tuple[str, str]] = set()
    for index, entry in enumerate(entries):
        _require(isinstance(entry, Mapping), "ENTRY_OBJECT", f"entries[{index}] must be an object")
        _validate_entry(entry, index)
        key = (entry["repository"], entry["path"])
        _require(key not in seen, "DUPLICATE_PATH", f"{key[0]}:{key[1]} appears more than once")
        seen.add(key)

    ordered_entries = sorted((copy.deepcopy(dict(entry)) for entry in entries), key=lambda item: (item["repository"], item["path"]))
    by_repo = Counter(entry["repository"] for entry in ordered_entries)
    by_classification = Counter(entry["classification"] for entry in ordered_entries)
    by_role = Counter(entry["path_role"] for entry in ordered_entries)
    mixed_paths = [f"{entry['repository']}:{entry['path']}" for entry in ordered_entries if entry["mixed_ownership"]]
    semantic_pending = [f"{entry['repository']}:{entry['path']}" for entry in ordered_entries if entry["semantic_status"] == "PENDING_SYNC_MAP_02"]
    result = copy.deepcopy(dict(document))
    result["entries"] = ordered_entries
    result["inventory_run_id"] = compute_inventory_run_id(document)
    result["status"] = "PASS_BOUNDED_PATH_INVENTORY"
    result["summary"] = {
        "entry_count": len(ordered_entries),
        "entries_by_repository": dict(sorted(by_repo.items())),
        "entries_by_classification": dict(sorted(by_classification.items())),
        "entries_by_role": dict(sorted(by_role.items())),
        "mixed_ownership_path_count": len(mixed_paths),
        "mixed_ownership_paths": mixed_paths,
        "semantic_mapping_pending_count": len(semantic_pending),
        "semantic_source_scan": "NOT_RUN_SYNC_MAP_01",
        "duplicate_path_count": 0,
        "official_dag_edge_mutation_count": 0,
    }
    result["verification"] = {
        "canonical_identity_encoding": "UTF-8 JSON sort_keys separators_comma_colon ensure_ascii_false allow_nan_false",
        "identity_payload_excludes": ["inventory_run_id", "status", "summary", "verification", "wolfram_verification"],
        "claim_boundary": "PATH_LEVEL_INVENTORY_ONLY_NO_FORMULA_EQUIVALENCE_PROVIDER_ADMISSION_OR_SCIENCE_PROMOTION",
    }
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--canonical-payload", type=Path)
    arguments = parser.parse_args(argv)
    try:
        source = json.loads(arguments.input.read_text(encoding="utf-8"))
        result = validate_inventory(source)
    except (OSError, json.JSONDecodeError, InventoryError) as exc:
        print(f"SYNC_MAP_01_FAIL: {exc}", file=sys.stderr)
        return 2
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    if arguments.canonical_payload is not None:
        arguments.canonical_payload.parent.mkdir(parents=True, exist_ok=True)
        arguments.canonical_payload.write_text(canonical_identity_text(source), encoding="utf-8")
    print("INVENTORY_RUN_ID=" + result["inventory_run_id"])
    print("ENTRY_COUNT=" + str(result["summary"]["entry_count"]))
    print("MIXED_PATH_COUNT=" + str(result["summary"]["mixed_ownership_path_count"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
