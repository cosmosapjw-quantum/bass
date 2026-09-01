#!/usr/bin/env python3
"""Fail-closed tri-repository authority and DAG reconciliation.

This coordinator is deliberately read-only with respect to GitHub, Dropbox,
and Atlassian.  It validates repository-owned export/import manifests and
emits a shadow-DAG proposal.  External mutations require a separately reviewed
adapter and an approval receipt.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

PROGRAM_ID = "BIANCHI-WOLFRAM-TRIREPO-20260830"
SCHEMA_VERSION = "2.0.0"
REPOSITORIES = ("bass", "rec_bianchi", "rei_bianchi")
DEFAULT_APPROVED_EDGES = [
    ["rec_bianchi", "bass"],
    ["rec_bianchi", "rei_bianchi"],
    ["rei_bianchi", "bass"],
]
ALLOWED_CONSUMER_MODES = {
    "PINNED_IMPORT",
    "INDEPENDENT_ORACLE",
    "ADAPTER_SPECIALIZATION",
}
ALLOWED_AUTHORITY_EFFECTS = {
    "AUTHORITATIVE_DERIVATION",
    "AUTHORITATIVE_PROVIDER",
    "AUTHORITATIVE_SCHEMA",
    "NONE",
}
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


class ContractError(ValueError):
    """Raised when an input contract is malformed or internally inconsistent."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def compute_sync_run_id(payload: Mapping[str, Any]) -> str:
    return sha256_json(payload)


def example_repo_bindings() -> dict[str, dict[str, str]]:
    return {
        "bass": {"commit": "1" * 40, "tree": "2" * 40},
        "rec_bianchi": {"commit": "3" * 40, "tree": "4" * 40},
        "rei_bianchi": {"commit": "5" * 40, "tree": "6" * 40},
    }


def _require(condition: bool, code: str, message: str) -> None:
    if not condition:
        raise ContractError(code, message)


def _require_sha(value: Any, bits: int, field: str) -> None:
    pattern = HEX40 if bits == 160 else HEX64
    _require(isinstance(value, str) and pattern.fullmatch(value) is not None,
             "INVALID_DIGEST", f"{field} must be lowercase hexadecimal with {bits // 4} characters")


def _require_repo(value: Any, field: str) -> None:
    _require(value in REPOSITORIES, "INVALID_REPOSITORY", f"{field} must be one of {REPOSITORIES}")


def _validate_export(document: Mapping[str, Any]) -> None:
    _require(document.get("schema_version") == SCHEMA_VERSION,
             "EXPORT_SCHEMA_VERSION", "unsupported export schema version")
    _require(document.get("program_id") == PROGRAM_ID,
             "EXPORT_PROGRAM_ID", "export belongs to a different program")
    repository = document.get("repository")
    _require_repo(repository, "export.repository")
    _require(isinstance(document.get("exports"), list),
             "EXPORT_ENTRIES", "exports must be a list")
    seen: set[str] = set()
    for index, entry in enumerate(document["exports"]):
        _require(isinstance(entry, Mapping), "EXPORT_ENTRY", f"exports[{index}] must be an object")
        formula_id = entry.get("formula_id")
        _require(isinstance(formula_id, str) and formula_id,
                 "FORMULA_ID", f"exports[{index}].formula_id is required")
        _require(formula_id not in seen, "DUPLICATE_LOCAL_FORMULA_ID",
                 f"{repository} exports {formula_id} more than once")
        seen.add(formula_id)
        owner = entry.get("owner")
        _require_repo(owner, f"exports[{index}].owner")
        _require(entry.get("authority_effect") in ALLOWED_AUTHORITY_EFFECTS,
                 "AUTHORITY_EFFECT", f"unsupported authority effect for {formula_id}")
        _require_sha(entry.get("semantic_hash"), 256, f"{formula_id}.semantic_hash")
        _require_sha(entry.get("convention_hash"), 256, f"{formula_id}.convention_hash")
        modes = entry.get("allowed_consumer_modes")
        _require(isinstance(modes, list) and set(modes).issubset(ALLOWED_CONSUMER_MODES),
                 "CONSUMER_MODES", f"invalid consumer modes for {formula_id}")
        payload = entry.get("semantic_payload")
        if payload is not None:
            _require(sha256_json(payload) == entry["semantic_hash"],
                     "SEMANTIC_HASH_MISMATCH",
                     f"semantic_payload does not reproduce semantic_hash for {formula_id}")


def _validate_import_lock(document: Mapping[str, Any]) -> None:
    _require(document.get("schema_version") == SCHEMA_VERSION,
             "IMPORT_SCHEMA_VERSION", "unsupported import-lock schema version")
    _require(document.get("program_id") == PROGRAM_ID,
             "IMPORT_PROGRAM_ID", "import lock belongs to a different program")
    _require_repo(document.get("repository"), "import_lock.repository")
    _require(isinstance(document.get("imports"), list),
             "IMPORT_ENTRIES", "imports must be a list")
    _require(isinstance(document.get("local_formula_claims"), list),
             "LOCAL_CLAIMS", "local_formula_claims must be a list")
    for index, entry in enumerate(document["imports"]):
        _require(isinstance(entry, Mapping), "IMPORT_ENTRY", f"imports[{index}] must be an object")
        _require(isinstance(entry.get("formula_id"), str) and entry["formula_id"],
                 "IMPORT_FORMULA_ID", f"imports[{index}].formula_id is required")
        _require_repo(entry.get("producer_repository"), f"imports[{index}].producer_repository")
        _require_sha(entry.get("producer_commit"), 160, f"imports[{index}].producer_commit")
        _require_sha(entry.get("producer_tree"), 160, f"imports[{index}].producer_tree")
        _require_sha(entry.get("semantic_hash"), 256, f"imports[{index}].semantic_hash")
        _require_sha(entry.get("convention_hash"), 256, f"imports[{index}].convention_hash")
        _require(entry.get("local_mode") in ALLOWED_CONSUMER_MODES,
                 "IMPORT_MODE", f"invalid import mode for {entry['formula_id']}")
    for index, claim in enumerate(document["local_formula_claims"]):
        _require(isinstance(claim, Mapping), "LOCAL_CLAIM", f"local_formula_claims[{index}] must be an object")
        _require(isinstance(claim.get("local_formula_id"), str) and claim["local_formula_id"],
                 "LOCAL_FORMULA_ID", f"local_formula_claims[{index}].local_formula_id is required")
        _require_sha(claim.get("semantic_hash"), 256, f"local_formula_claims[{index}].semantic_hash")
        _require(claim.get("authority_effect") in ALLOWED_AUTHORITY_EFFECTS,
                 "LOCAL_AUTHORITY_EFFECT", f"invalid authority effect for {claim['local_formula_id']}")


def _normalise_bindings(bindings: Mapping[str, Mapping[str, str]]) -> dict[str, dict[str, str]]:
    _require(set(bindings) == set(REPOSITORIES),
             "REPOSITORY_BINDINGS", "bindings must cover exactly bass, rec_bianchi, and rei_bianchi")
    result: dict[str, dict[str, str]] = {}
    for repository in REPOSITORIES:
        binding = bindings[repository]
        _require_sha(binding.get("commit"), 160, f"{repository}.commit")
        _require_sha(binding.get("tree"), 160, f"{repository}.tree")
        result[repository] = {"commit": binding["commit"], "tree": binding["tree"]}
    return result


def _build_registry(exports: Sequence[Mapping[str, Any]]) -> tuple[dict[str, Any], dict[str, list[dict[str, Any]]]]:
    candidates: dict[str, list[dict[str, Any]]] = {}
    for document in exports:
        repository = document["repository"]
        for raw_entry in document["exports"]:
            entry = copy.deepcopy(dict(raw_entry))
            entry["producer_repository"] = repository
            candidates.setdefault(entry["formula_id"], []).append(entry)

    entries: list[dict[str, Any]] = []
    duplicate_ids: list[str] = []
    for formula_id in sorted(candidates):
        group = sorted(candidates[formula_id], key=lambda item: (item["owner"], item["producer_repository"]))
        owners = sorted({item["owner"] for item in group})
        producers = sorted({item["producer_repository"] for item in group})
        if len(group) != 1 or len(owners) != 1 or len(producers) != 1:
            duplicate_ids.append(formula_id)
            entries.append({
                "formula_id": formula_id,
                "status": "DUPLICATE_AUTHORITY",
                "owners": owners,
                "producers": producers,
                "candidates": group,
            })
        else:
            canonical = copy.deepcopy(group[0])
            canonical["status"] = canonical.get("status", "DECLARED")
            entries.append(canonical)

    registry = {
        "schema_version": SCHEMA_VERSION,
        "program_id": PROGRAM_ID,
        "registry_status": "FAIL" if duplicate_ids else "PASS",
        "formula_count": len(candidates),
        "duplicate_owner_formula_ids": duplicate_ids,
        "entries": entries,
    }
    return registry, candidates


def _detect_duplicate_paths(
    candidates: Mapping[str, Sequence[Mapping[str, Any]]],
    import_locks: Sequence[Mapping[str, Any]],
    observations: Mapping[str, Any],
) -> dict[str, Any]:
    semantic_index: dict[str, list[dict[str, str]]] = {}
    duplicate_owner_ids: list[str] = []
    for formula_id, group in candidates.items():
        if len(group) != 1:
            duplicate_owner_ids.append(formula_id)
        for entry in group:
            semantic_index.setdefault(entry["semantic_hash"], []).append({
                "formula_id": formula_id,
                "owner": entry["owner"],
                "producer_repository": entry["producer_repository"],
            })

    possible_semantic_duplicates: list[dict[str, Any]] = []
    for semantic_hash, group in sorted(semantic_index.items()):
        formula_ids = sorted({item["formula_id"] for item in group})
        owners = sorted({item["owner"] for item in group})
        if len(formula_ids) > 1 and len(owners) > 1:
            possible_semantic_duplicates.append({
                "semantic_hash": semantic_hash,
                "formula_ids": formula_ids,
                "owners": owners,
                "classification": "POSSIBLE_DUPLICATE_SEMANTICS",
            })

    allowed_replays: list[dict[str, Any]] = []
    unauthorized: list[dict[str, Any]] = []
    for lock in import_locks:
        repository = lock["repository"]
        for claim in lock["local_formula_claims"]:
            matching = semantic_index.get(claim["semantic_hash"], [])
            replay_of = claim.get("replay_of")
            replay_target = candidates.get(replay_of, []) if isinstance(replay_of, str) else []
            authorized_replay = (
                claim.get("authority_effect") == "NONE"
                and len(replay_target) == 1
                and replay_target[0]["semantic_hash"] == claim["semantic_hash"]
                and isinstance(claim.get("independence_class"), str)
                and bool(claim["independence_class"])
            )
            if authorized_replay:
                allowed_replays.append({
                    "repository": repository,
                    "local_formula_id": claim["local_formula_id"],
                    "replay_of": replay_of,
                    "independence_class": claim["independence_class"],
                    "authority_effect": "NONE",
                })
            elif matching:
                unauthorized.append({
                    "repository": repository,
                    "local_formula_id": claim["local_formula_id"],
                    "semantic_hash": claim["semantic_hash"],
                    "matches": matching,
                    "classification": "DUPLICATE_DERIVATION_PATH",
                    "required_repair": "declare replay_of plus authority_effect=NONE or remove duplicate authority",
                })
            elif claim.get("authority_effect") != "NONE":
                unauthorized.append({
                    "repository": repository,
                    "local_formula_id": claim["local_formula_id"],
                    "semantic_hash": claim["semantic_hash"],
                    "matches": [],
                    "classification": "UNREGISTERED_LOCAL_AUTHORITY",
                    "required_repair": "export the owned formula or bind it to an existing authority",
                })

    semantic_scan = observations.get("semantic_source_scan", "COMPLETE")
    hard_failure = bool(duplicate_owner_ids or possible_semantic_duplicates or unauthorized)
    status = "FAIL" if hard_failure else ("PARTIAL" if semantic_scan != "COMPLETE" else "PASS")
    return {
        "schema_version": SCHEMA_VERSION,
        "program_id": PROGRAM_ID,
        "status": status,
        "semantic_source_scan": semantic_scan,
        "duplicate_owner_formula_ids": sorted(duplicate_owner_ids),
        "possible_semantic_duplicates": possible_semantic_duplicates,
        "allowed_replays": sorted(allowed_replays, key=lambda item: (item["repository"], item["local_formula_id"])),
        "unauthorized_local_claims": sorted(unauthorized, key=lambda item: (item["repository"], item["local_formula_id"])),
        "claim_boundary": "DECLARED_MANIFEST_AUDIT_ONLY_NO_SOURCE_LEVEL_FORMULA_EQUIVALENCE_UNLESS_SCAN_COMPLETE",
    }


def _validate_imports(
    candidates: Mapping[str, Sequence[Mapping[str, Any]]],
    locks: Sequence[Mapping[str, Any]],
    bindings: Mapping[str, Mapping[str, str]],
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for lock in locks:
        consumer = lock["repository"]
        for entry in lock["imports"]:
            formula_id = entry["formula_id"]
            group = candidates.get(formula_id, [])
            if not group:
                findings.append({
                    "code": "MISSING_IMPORT_FORMULA",
                    "repository": consumer,
                    "formula_id": formula_id,
                })
                continue
            if len(group) != 1:
                findings.append({
                    "code": "DUPLICATE_AUTHORITY",
                    "repository": consumer,
                    "formula_id": formula_id,
                })
                continue
            authority = group[0]
            producer = entry["producer_repository"]
            if producer != authority["producer_repository"] or producer != authority["owner"]:
                findings.append({
                    "code": "WRONG_PRODUCER",
                    "repository": consumer,
                    "formula_id": formula_id,
                    "declared_producer": producer,
                    "authority_owner": authority["owner"],
                    "authority_producer": authority["producer_repository"],
                })
            if entry["semantic_hash"] != authority["semantic_hash"]:
                findings.append({
                    "code": "STALE_UPSTREAM",
                    "repository": consumer,
                    "formula_id": formula_id,
                    "locked_semantic_hash": entry["semantic_hash"],
                    "authority_semantic_hash": authority["semantic_hash"],
                })
            if entry["convention_hash"] != authority["convention_hash"]:
                findings.append({
                    "code": "CONVENTION_DRIFT",
                    "repository": consumer,
                    "formula_id": formula_id,
                    "locked_convention_hash": entry["convention_hash"],
                    "authority_convention_hash": authority["convention_hash"],
                })
            if entry["local_mode"] not in authority["allowed_consumer_modes"]:
                findings.append({
                    "code": "UNAUTHORIZED_CONSUMER_MODE",
                    "repository": consumer,
                    "formula_id": formula_id,
                    "local_mode": entry["local_mode"],
                })
            expected_binding = bindings.get(producer)
            if expected_binding and (
                entry["producer_commit"] != expected_binding["commit"]
                or entry["producer_tree"] != expected_binding["tree"]
            ):
                findings.append({
                    "code": "STALE_UPSTREAM_IDENTITY",
                    "repository": consumer,
                    "formula_id": formula_id,
                    "locked_commit": entry["producer_commit"],
                    "locked_tree": entry["producer_tree"],
                    "expected_commit": expected_binding["commit"],
                    "expected_tree": expected_binding["tree"],
                })
    return findings


def _shadow_statuses(findings: Sequence[Mapping[str, Any]]) -> dict[str, str]:
    statuses = {repository: "IN_SYNC" for repository in REPOSITORIES}
    for finding in findings:
        repository = finding.get("repository")
        if repository in statuses:
            statuses[repository] = finding.get("code", "DRIFT_DETECTED")
    return statuses


def audit_documents(
    exports: Sequence[Mapping[str, Any]],
    import_locks: Sequence[Mapping[str, Any]],
    repo_bindings: Mapping[str, Mapping[str, str]],
    approved_edges: Sequence[Sequence[str]],
    observations: Mapping[str, Any],
) -> dict[str, Any]:
    _require(len(exports) == 3 and len(import_locks) == 3,
             "TRIREPO_CARDINALITY", "exactly three exports and three import locks are required")
    for document in exports:
        _validate_export(document)
    for document in import_locks:
        _validate_import_lock(document)
    export_repositories = [document["repository"] for document in exports]
    lock_repositories = [document["repository"] for document in import_locks]
    _require(set(export_repositories) == set(REPOSITORIES) and len(set(export_repositories)) == 3,
             "EXPORT_REPOSITORY_SET", "exports must cover each repository exactly once")
    _require(set(lock_repositories) == set(REPOSITORIES) and len(set(lock_repositories)) == 3,
             "LOCK_REPOSITORY_SET", "import locks must cover each repository exactly once")

    bindings = _normalise_bindings(repo_bindings)
    normalised_edges = sorted([list(edge) for edge in approved_edges])
    _require(normalised_edges == sorted(DEFAULT_APPROVED_EDGES),
             "APPROVED_EDGE_DRIFT", "bootstrap cannot change the approved REC/REI/BASS edge set")

    registry, candidates = _build_registry(exports)
    duplicate_report = _detect_duplicate_paths(candidates, import_locks, observations)
    findings = _validate_imports(candidates, import_locks, bindings)
    for finding in observations.get("findings", []):
        _require(isinstance(finding, Mapping) and isinstance(finding.get("code"), str),
                 "OBSERVATION_FINDING", "every observation finding needs a string code")
        findings.append(copy.deepcopy(dict(finding)))

    if duplicate_report["status"] == "FAIL":
        findings.append({
            "code": "DUPLICATE_AUTHORITY_OR_DERIVATION",
            "repository": "program",
            "duplicate_owner_formula_ids": duplicate_report["duplicate_owner_formula_ids"],
            "unauthorized_local_claim_count": len(duplicate_report["unauthorized_local_claims"]),
        })

    coverage_status = observations.get("coverage_status", "COMPLETE")
    if findings:
        sync_status = "DRIFT_DETECTED"
    elif duplicate_report["status"] == "PARTIAL" or coverage_status != "COMPLETE":
        sync_status = "BOOTSTRAP_PARTIAL"
    else:
        sync_status = "IN_SYNC"

    document_digests: dict[str, str] = {}
    convention_hashes: set[str] = set()
    for document in exports:
        repository = document["repository"]
        document_digests[f"{repository}:export"] = sha256_json(document)
        convention_hashes.update(entry["convention_hash"] for entry in document["exports"])
    for document in import_locks:
        document_digests[f"{document['repository']}:import_lock"] = sha256_json(document)

    sync_id_payload = {
        "program_id": PROGRAM_ID,
        "dag_version": SCHEMA_VERSION,
        "repo_bindings": bindings,
        "document_digests": dict(sorted(document_digests.items())),
        "convention_hashes": sorted(convention_hashes),
        "approved_edges": normalised_edges,
        "observations_digest": sha256_json(observations),
    }
    sync_run_id = compute_sync_run_id(sync_id_payload)

    registry["sync_run_id"] = sync_run_id
    duplicate_report["sync_run_id"] = sync_run_id
    sync_state = {
        "schema_version": SCHEMA_VERSION,
        "program_id": PROGRAM_ID,
        "sync_run_id": sync_run_id,
        "status": sync_status,
        "coverage_status": coverage_status,
        "repo_bindings": bindings,
        "document_digests": dict(sorted(document_digests.items())),
        "findings": sorted(findings, key=lambda item: (str(item.get("repository", "")), item["code"], str(item.get("formula_id", "")))),
        "shadow_repository_status": _shadow_statuses(findings),
        "external_planes": copy.deepcopy(observations.get("external_planes", {
            "github": "AUDITED",
            "dropbox": "NOT_RUN",
            "atlassian": "NOT_RUN",
        })),
        "claim_boundary": "SYNC_METADATA_ONLY_NO_SCIENTIFIC_OR_OFFICIAL_DAG_PROMOTION",
    }
    dag_proposal = {
        "schema_version": SCHEMA_VERSION,
        "program_id": PROGRAM_ID,
        "sync_run_id": sync_run_id,
        "proposal_status": "PROPOSAL_ONLY_NO_DAG_MUTATION",
        "approved_edges": normalised_edges,
        "proposed_official_edge_mutations": [],
        "shadow_repository_status": _shadow_statuses(findings),
        "shadow_nodes": copy.deepcopy(observations.get("shadow_nodes", [
            {
                "node_id": "SYNC-MAP-01",
                "owner": "bass",
                "action": "inventory active formula and adapter paths in all three repositories",
                "status": "PROPOSED",
            },
            {
                "node_id": "SYNC-MAP-02",
                "owner": "bass",
                "action": "map common BASS geometry formula IDs to REC and REI replay or import declarations",
                "status": "BLOCKED_BY_SYNC_MAP_01",
            },
            {
                "node_id": "SYNC-REC-01",
                "owner": "rec_bianchi",
                "action": "replace unbound common-geometry derivations with pinned imports or explicit independent oracles",
                "status": "BLOCKED_BY_SYNC_MAP_02",
            },
            {
                "node_id": "SYNC-REI-01",
                "owner": "rei_bianchi",
                "action": "replace unbound common-geometry derivations with pinned imports or explicit independent oracles",
                "status": "BLOCKED_BY_SYNC_MAP_02",
            },
        ])),
        "approval_required_for": [
            "official Jira Blocks-link mutation",
            "scientific owner change",
            "claim-level promotion",
            "pull-request merge or close",
            "Dropbox-to-GitHub recovery",
        ],
    }
    sync_receipt = {
        "schema_version": SCHEMA_VERSION,
        "program_id": PROGRAM_ID,
        "sync_run_id": sync_run_id,
        "status": sync_status,
        "input_identity": sync_id_payload,
        "summary": {
            "formula_count": registry["formula_count"],
            "finding_count": len(findings),
            "duplicate_report_status": duplicate_report["status"],
            "official_edge_mutation_count": 0,
        },
        "authorized_claims": ["TRIREPO_BOOTSTRAP_AUDIT_EXECUTED"],
        "withheld_claims": [
            "FULL_SOURCE_LEVEL_SEMANTIC_DEDUPLICATION",
            "AUTOMATIC_OFFICIAL_DAG_MUTATION",
            "CROSS_REPOSITORY_COMPATIBILITY",
            "SCIENTIFIC_VALIDITY",
        ],
    }
    return {
        "sync_run_id": sync_run_id,
        "authority_registry": registry,
        "sync_state": sync_state,
        "duplicate_report": duplicate_report,
        "dag_proposal": dag_proposal,
        "sync_receipt": sync_receipt,
    }


OUTPUT_NAMES = {
    "authority_registry": "TRIREPO_AUTHORITY_REGISTRY.json",
    "sync_state": "TRIREPO_SYNC_STATE.json",
    "duplicate_report": "TRIREPO_DUPLICATE_REPORT.json",
    "dag_proposal": "TRIREPO_DAG_PROPOSAL.json",
    "sync_receipt": "TRIREPO_SYNC_RECEIPT.json",
}


def write_outputs(result: Mapping[str, Any], output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for key, filename in OUTPUT_NAMES.items():
        path = output_dir / filename
        path.write_text(
            json.dumps(result[key], ensure_ascii=False, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
        written.append(path)
    return written


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    _require(isinstance(value, dict), "JSON_ROOT", f"{path} must contain a JSON object")
    return value


def _parse_repo_path(value: str) -> tuple[str, Path]:
    repository, separator, raw_path = value.partition("=")
    _require(bool(separator) and bool(raw_path), "REPO_PATH", "expected REPOSITORY=PATH")
    _require_repo(repository, "repository selector")
    return repository, Path(raw_path)


def _parse_binding(value: str) -> tuple[str, dict[str, str]]:
    repository, separator, raw_binding = value.partition("=")
    _require(bool(separator), "BINDING", "expected REPOSITORY=COMMIT:TREE")
    commit, separator, tree = raw_binding.partition(":")
    _require(bool(separator), "BINDING", "expected REPOSITORY=COMMIT:TREE")
    _require_repo(repository, "binding.repository")
    _require_sha(commit, 160, f"{repository}.commit")
    _require_sha(tree, 160, f"{repository}.tree")
    return repository, {"commit": commit, "tree": tree}


def _derive_binding(export: Mapping[str, Any]) -> dict[str, str]:
    base = export.get("producer_base")
    _require(isinstance(base, Mapping), "MISSING_PRODUCER_BASE",
             f"{export.get('repository')} export needs producer_base when --binding is omitted")
    commit = base.get("commit")
    tree = base.get("tree")
    _require_sha(commit, 160, f"{export.get('repository')}.producer_base.commit")
    _require_sha(tree, 160, f"{export.get('repository')}.producer_base.tree")
    return {"commit": commit, "tree": tree}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--export", action="append", required=True, metavar="REPOSITORY=PATH")
    parser.add_argument("--import-lock", action="append", required=True, metavar="REPOSITORY=PATH")
    parser.add_argument("--binding", action="append", default=[], metavar="REPOSITORY=COMMIT:TREE")
    parser.add_argument("--observations", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--fail-on-drift", action="store_true")
    args = parser.parse_args(argv)

    try:
        export_paths = dict(_parse_repo_path(value) for value in args.export)
        lock_paths = dict(_parse_repo_path(value) for value in args.import_lock)
        _require(set(export_paths) == set(REPOSITORIES), "CLI_EXPORT_SET", "--export must cover all repositories")
        _require(set(lock_paths) == set(REPOSITORIES), "CLI_LOCK_SET", "--import-lock must cover all repositories")
        exports_by_repo = {repository: _load_json(export_paths[repository]) for repository in REPOSITORIES}
        locks_by_repo = {repository: _load_json(lock_paths[repository]) for repository in REPOSITORIES}
        explicit_bindings = dict(_parse_binding(value) for value in args.binding)
        bindings = {
            repository: explicit_bindings.get(repository, _derive_binding(exports_by_repo[repository]))
            for repository in REPOSITORIES
        }
        observations = _load_json(args.observations) if args.observations else {}
        result = audit_documents(
            [exports_by_repo[repository] for repository in REPOSITORIES],
            [locks_by_repo[repository] for repository in REPOSITORIES],
            bindings,
            DEFAULT_APPROVED_EDGES,
            observations,
        )
        paths = write_outputs(result, args.output_dir)
        print(json.dumps({
            "sync_run_id": result["sync_run_id"],
            "status": result["sync_state"]["status"],
            "outputs": [str(path) for path in paths],
        }, sort_keys=True))
        if args.fail_on_drift and result["sync_state"]["status"] == "DRIFT_DETECTED":
            return 2
        return 0
    except (ContractError, OSError, json.JSONDecodeError) as error:
        if isinstance(error, ContractError):
            payload = {"status": "BLOCKED", "code": error.code, "message": error.message}
        else:
            payload = {"status": "BLOCKED", "code": type(error).__name__, "message": str(error)}
        print(json.dumps(payload, sort_keys=True), file=sys.stderr)
        return 64


if __name__ == "__main__":
    raise SystemExit(main())
