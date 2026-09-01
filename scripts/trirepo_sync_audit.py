#!/usr/bin/env python3
"""Read-only authority, import-lock, and shadow-DAG auditor for BASS/REC/REI.

This program never mutates GitHub, Dropbox, or Atlassian.  It consumes exact
JSON snapshots and emits proposals and receipts.  External mutation requires a
separate approved delivery layer.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Iterable

PROGRAM_ID = "BIANCHI-WOLFRAM-TRIREPO-20260830"
SCHEMA_VERSION = "2.0.0"
REPOSITORIES = {"bass", "rec_bianchi", "rei_bianchi"}
AUTHORITY_MODES = {
    "AUTHORITATIVE_DERIVATION",
    "PINNED_IMPORT",
    "AUTHORIZED_REPLAY",
    "INDEPENDENT_ORACLE",
    "ADAPTER_SPECIALIZATION",
    "OWNED_EXTENSION",
}
CONSUMER_MODES = {
    "PINNED_IMPORT",
    "AUTHORIZED_REPLAY",
    "INDEPENDENT_ORACLE",
    "ADAPTER_SPECIALIZATION",
}
DEPENDENCY_BLOCK_STATES = {
    "BLOCKED_PROVIDER_NOT_PUBLISHED",
    "STOP_INVALID_NOT_PUBLISHED",
    "NOT_RUN",
    "BLOCKED_DEPENDENCY",
}


class ContractError(ValueError):
    """Raised when an input manifest violates the structural contract."""


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def load_json(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    with source.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ContractError(f"{source}: top-level JSON value must be an object")
    return value


def require_keys(record: dict[str, Any], keys: Iterable[str], where: str) -> None:
    missing = sorted(set(keys) - set(record))
    if missing:
        raise ContractError(f"{where}: missing required keys {missing}")


def _hex(value: Any, length: int) -> bool:
    return isinstance(value, str) and len(value) == length and all(
        character in "0123456789abcdef" for character in value
    )


def _nullable_hex(value: Any, length: int) -> bool:
    return value is None or _hex(value, length)


def validate_export(document: dict[str, Any]) -> None:
    require_keys(
        document,
        {
            "schema_version",
            "program_id",
            "change_id",
            "sync_run_id",
            "repository",
            "policy_base",
            "exports",
            "claim_boundary",
        },
        "authority export",
    )
    if document["schema_version"] != SCHEMA_VERSION:
        raise ContractError("authority export: unsupported schema_version")
    if document["program_id"] != PROGRAM_ID:
        raise ContractError("authority export: unexpected program_id")
    if document["repository"] not in REPOSITORIES:
        raise ContractError("authority export: invalid repository")
    if not _hex(document["sync_run_id"], 64):
        raise ContractError("authority export: invalid sync_run_id")
    policy_base = document["policy_base"]
    if not isinstance(policy_base, dict):
        raise ContractError("authority export: policy_base must be an object")
    require_keys(policy_base, {"branch", "commit", "tree"}, "policy_base")
    if not _hex(policy_base["commit"], 40) or not _hex(policy_base["tree"], 40):
        raise ContractError("authority export: invalid policy commit/tree")
    exports = document["exports"]
    if not isinstance(exports, list):
        raise ContractError("authority export: exports must be an array")
    seen: set[str] = set()
    for index, record in enumerate(exports):
        where = f"authority export record {index}"
        if not isinstance(record, dict):
            raise ContractError(f"{where}: record must be an object")
        require_keys(
            record,
            {
                "formula_id",
                "owner",
                "authority_mode",
                "producer_ref",
                "producer_commit",
                "source_path",
                "semantic_hash",
                "convention_hash",
                "status",
                "consumers",
                "allowed_consumer_modes",
                "dependencies",
            },
            where,
        )
        formula_id = record["formula_id"]
        if not isinstance(formula_id, str) or not formula_id:
            raise ContractError(f"{where}: invalid formula_id")
        if formula_id in seen:
            raise ContractError(f"{where}: duplicate formula_id in one export")
        seen.add(formula_id)
        if record["owner"] not in REPOSITORIES:
            raise ContractError(f"{where}: invalid owner")
        if record["authority_mode"] not in AUTHORITY_MODES:
            raise ContractError(f"{where}: invalid authority_mode")
        if not _nullable_hex(record["producer_commit"], 40):
            raise ContractError(f"{where}: invalid producer_commit")
        if not _nullable_hex(record["semantic_hash"], 64):
            raise ContractError(f"{where}: invalid semantic_hash")
        if not _nullable_hex(record["convention_hash"], 64):
            raise ContractError(f"{where}: invalid convention_hash")
        if not isinstance(record["consumers"], list) or not set(record["consumers"]).issubset(REPOSITORIES):
            raise ContractError(f"{where}: invalid consumers")
        if not isinstance(record["allowed_consumer_modes"], list) or not set(record["allowed_consumer_modes"]).issubset(CONSUMER_MODES):
            raise ContractError(f"{where}: invalid allowed_consumer_modes")
        if not isinstance(record["dependencies"], list) or not all(
            isinstance(item, str) and item for item in record["dependencies"]
        ):
            raise ContractError(f"{where}: invalid dependencies")


def validate_import_lock(document: dict[str, Any]) -> None:
    require_keys(
        document,
        {
            "schema_version",
            "program_id",
            "change_id",
            "sync_run_id",
            "repository",
            "imports",
            "no_silent_fallback",
            "claim_boundary",
        },
        "import lock",
    )
    if document["schema_version"] != SCHEMA_VERSION:
        raise ContractError("import lock: unsupported schema_version")
    if document["program_id"] != PROGRAM_ID:
        raise ContractError("import lock: unexpected program_id")
    if document["repository"] not in REPOSITORIES:
        raise ContractError("import lock: invalid repository")
    if not _hex(document["sync_run_id"], 64):
        raise ContractError("import lock: invalid sync_run_id")
    if document["no_silent_fallback"] is not True:
        raise ContractError("import lock: no_silent_fallback must be true")
    imports = document["imports"]
    if not isinstance(imports, list):
        raise ContractError("import lock: imports must be an array")
    seen: set[str] = set()
    for index, record in enumerate(imports):
        where = f"import lock record {index}"
        if not isinstance(record, dict):
            raise ContractError(f"{where}: record must be an object")
        require_keys(
            record,
            {
                "formula_id",
                "producer_repository",
                "producer_ref",
                "producer_commit",
                "semantic_hash",
                "convention_hash",
                "local_mode",
                "use",
                "status",
                "required_claim_level",
            },
            where,
        )
        formula_id = record["formula_id"]
        if not isinstance(formula_id, str) or not formula_id:
            raise ContractError(f"{where}: invalid formula_id")
        if formula_id in seen:
            raise ContractError(f"{where}: duplicate formula_id in one import lock")
        seen.add(formula_id)
        if record["producer_repository"] not in REPOSITORIES:
            raise ContractError(f"{where}: invalid producer_repository")
        if record["local_mode"] not in CONSUMER_MODES:
            raise ContractError(f"{where}: invalid local_mode")
        if not _nullable_hex(record["producer_commit"], 40):
            raise ContractError(f"{where}: invalid producer_commit")
        if not _nullable_hex(record["semantic_hash"], 64):
            raise ContractError(f"{where}: invalid semantic_hash")
        if not _nullable_hex(record["convention_hash"], 64):
            raise ContractError(f"{where}: invalid convention_hash")


def _finding(code: str, detail: str, **extra: Any) -> dict[str, Any]:
    return {"code": code, "detail": detail, **extra}


def audit_documents(
    exports: list[dict[str, Any]],
    imports: list[dict[str, Any]],
    expected_run_id: str | None = None,
) -> dict[str, Any]:
    for document in exports:
        validate_export(document)
    for document in imports:
        validate_import_lock(document)

    structural: list[dict[str, Any]] = []
    dependencies: list[dict[str, Any]] = []
    duplicates: list[dict[str, Any]] = []

    run_ids = {document["sync_run_id"] for document in exports + imports}
    if expected_run_id is not None:
        run_ids.add(expected_run_id)
    if len(run_ids) != 1:
        structural.append(_finding("SYNC_RUN_ID_MISMATCH", "input manifests do not share one sync_run_id", values=sorted(run_ids)))
    sync_run_id = sorted(run_ids)[0] if len(run_ids) == 1 else None

    formula_index: dict[str, list[dict[str, Any]]] = {}
    semantic_index: dict[str, list[dict[str, Any]]] = {}
    for document in exports:
        repository = document["repository"]
        for source_record in document["exports"]:
            record = dict(source_record)
            record["exporting_repository"] = repository
            formula_index.setdefault(record["formula_id"], []).append(record)
            semantic_hash = record.get("semantic_hash")
            if semantic_hash:
                semantic_index.setdefault(semantic_hash, []).append(record)

    for formula_id, records in sorted(formula_index.items()):
        authoritative = [
            record
            for record in records
            if record["authority_mode"] in {"AUTHORITATIVE_DERIVATION", "OWNED_EXTENSION"}
        ]
        owners = {record["owner"] for record in authoritative}
        if len(owners) > 1 or len(authoritative) > 1:
            finding = _finding(
                "DUPLICATE_AUTHORITY",
                f"{formula_id} has more than one authoritative record",
                formula_id=formula_id,
                owners=sorted(owners),
                repositories=sorted({record["exporting_repository"] for record in authoritative}),
            )
            structural.append(finding)
            duplicates.append(finding)

    for semantic_hash, records in sorted(semantic_index.items()):
        authoritative = [
            record
            for record in records
            if record["authority_mode"] in {"AUTHORITATIVE_DERIVATION", "OWNED_EXTENSION"}
        ]
        owner_formula_pairs = {(record["owner"], record["formula_id"]) for record in authoritative}
        if len(owner_formula_pairs) > 1:
            finding = _finding(
                "DUPLICATE_SEMANTIC_AUTHORITY",
                "one semantic hash is claimed by multiple authoritative owner/formula pairs",
                semantic_hash=semantic_hash,
                owner_formula_pairs=sorted([list(pair) for pair in owner_formula_pairs]),
            )
            structural.append(finding)
            duplicates.append(finding)

    for document in imports:
        consumer = document["repository"]
        for lock in document["imports"]:
            formula_id = lock["formula_id"]
            candidates = formula_index.get(formula_id, [])
            if not candidates:
                if lock["status"] in DEPENDENCY_BLOCK_STATES:
                    dependencies.append(_finding("BLOCKED_DEPENDENCY", f"{consumer} awaits unpublished {formula_id}", consumer=consumer, formula_id=formula_id, status=lock["status"]))
                else:
                    structural.append(_finding("MISSING_AUTHORITY_EXPORT", f"{consumer} imports {formula_id}, but no export exists", consumer=consumer, formula_id=formula_id))
                continue
            if len(candidates) != 1:
                structural.append(_finding("AMBIGUOUS_AUTHORITY_EXPORT", f"{consumer} imports {formula_id}, but authority is ambiguous", consumer=consumer, formula_id=formula_id, count=len(candidates)))
                continue
            export = candidates[0]
            if export["owner"] != lock["producer_repository"]:
                structural.append(_finding("OWNER_MISMATCH", f"{consumer} import owner differs from export owner", consumer=consumer, formula_id=formula_id, expected=export["owner"], actual=lock["producer_repository"]))
            if lock["local_mode"] not in export["allowed_consumer_modes"]:
                structural.append(_finding("UNAUTHORIZED_CONSUMER_MODE", f"{consumer} uses a mode not authorized by the owner", consumer=consumer, formula_id=formula_id, mode=lock["local_mode"]))
            if lock["producer_commit"] and export["producer_commit"] and lock["producer_commit"] != export["producer_commit"]:
                structural.append(_finding("STALE_UPSTREAM", f"{consumer} pins a different producer commit", consumer=consumer, formula_id=formula_id, pinned=lock["producer_commit"], current=export["producer_commit"]))
            if lock["semantic_hash"] and export["semantic_hash"] and lock["semantic_hash"] != export["semantic_hash"]:
                structural.append(_finding("SEMANTIC_HASH_MISMATCH", f"{consumer} semantic pin differs from authority", consumer=consumer, formula_id=formula_id))
            if lock["convention_hash"] and export["convention_hash"] and lock["convention_hash"] != export["convention_hash"]:
                structural.append(_finding("CONVENTION_HASH_MISMATCH", f"{consumer} convention pin differs from authority", consumer=consumer, formula_id=formula_id))
            if export["status"] in DEPENDENCY_BLOCK_STATES or lock["status"] in DEPENDENCY_BLOCK_STATES:
                dependencies.append(_finding("BLOCKED_DEPENDENCY", f"{consumer} import is structurally declared but not consumption-ready", consumer=consumer, formula_id=formula_id, export_status=export["status"], import_status=lock["status"]))

    nodes: dict[str, dict[str, Any]] = {}
    edges: list[dict[str, str]] = []
    for formula_id, records in sorted(formula_index.items()):
        record = records[0]
        nodes[formula_id] = {
            "id": formula_id,
            "owner": record["owner"],
            "status": record["status"],
        }
        for dependency in record["dependencies"]:
            edges.append({"from": dependency, "to": formula_id, "type": "requires"})
            if dependency not in formula_index:
                dependencies.append(_finding("UNRESOLVED_DAG_DEPENDENCY", f"{formula_id} depends on an unexported formula", formula_id=formula_id, dependency=dependency))
    for document in imports:
        for lock in document["imports"]:
            edges.append({"from": lock["formula_id"], "to": f"consumer:{document['repository']}", "type": "imports"})

    structural = sorted(structural, key=lambda item: (item["code"], item.get("formula_id", ""), item.get("consumer", "")))
    dependencies = sorted(dependencies, key=lambda item: (item["code"], item.get("formula_id", ""), item.get("consumer", "")))
    duplicates = sorted(duplicates, key=lambda item: (item["code"], item.get("formula_id", "")))

    if structural:
        classification = "FAIL_STRUCTURE"
    elif dependencies:
        classification = "PASS_STRUCTURE_WITH_BLOCKED_DEPENDENCIES"
    else:
        classification = "PASS_IN_SYNC"

    return {
        "schema_version": SCHEMA_VERSION,
        "program_id": PROGRAM_ID,
        "sync_run_id": sync_run_id,
        "classification": classification,
        "structural_findings": structural,
        "dependency_findings": dependencies,
        "duplicate_report": duplicates,
        "shadow_dag": {
            "proposal_only": True,
            "nodes": [nodes[key] for key in sorted(nodes)],
            "edges": sorted(edges, key=lambda item: (item["from"], item["to"], item["type"])),
        },
        "input_identity": {
            "exports_sha256": sha256_json(exports),
            "imports_sha256": sha256_json(imports),
        },
        "claim_boundary": "READ_ONLY_AUDIT_NO_EXTERNAL_MUTATION_OR_SCIENCE_PROMOTION",
    }


def write_outputs(result: dict[str, Any], output_directory: str | Path) -> None:
    destination = Path(output_directory)
    destination.mkdir(parents=True, exist_ok=True)
    products = {
        "TRIREPO_DUPLICATE_REPORT.json": {
            "schema_version": SCHEMA_VERSION,
            "program_id": PROGRAM_ID,
            "sync_run_id": result["sync_run_id"],
            "classification": result["classification"],
            "findings": result["duplicate_report"],
        },
        "TRIREPO_DAG_PROPOSAL.generated.json": {
            "schema_version": SCHEMA_VERSION,
            "program_id": PROGRAM_ID,
            "sync_run_id": result["sync_run_id"],
            **result["shadow_dag"],
        },
        "TRIREPO_SYNC_RECEIPT.json": result,
    }
    for name, product in products.items():
        (destination / name).write_text(
            json.dumps(product, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--export", action="append", default=[], help="authority export JSON; repeat for each repository")
    parser.add_argument("--import-lock", action="append", default=[], help="import-lock JSON; repeat for each repository")
    parser.add_argument("--expected-run-id", default=None)
    parser.add_argument("--out-dir", default=None)
    parser.add_argument("--fail-on", choices=("structural", "any", "never"), default="structural")
    return parser


def main(argv: list[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    if not arguments.export:
        print("at least one --export is required", file=sys.stderr)
        return 2
    try:
        exports = [load_json(path) for path in arguments.export]
        imports = [load_json(path) for path in arguments.import_lock]
        result = audit_documents(exports, imports, arguments.expected_run_id)
    except (OSError, json.JSONDecodeError, ContractError) as error:
        print(json.dumps({"classification": "INPUT_CONTRACT_FAILURE", "error": str(error)}, sort_keys=True), file=sys.stderr)
        return 2
    if arguments.out_dir:
        write_outputs(result, arguments.out_dir)
    print(json.dumps({
        "sync_run_id": result["sync_run_id"],
        "classification": result["classification"],
        "structural_findings": len(result["structural_findings"]),
        "dependency_findings": len(result["dependency_findings"]),
    }, sort_keys=True))
    if arguments.fail_on == "never":
        return 0
    if arguments.fail_on == "any":
        return 1 if result["structural_findings"] or result["dependency_findings"] else 0
    return 1 if result["structural_findings"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
