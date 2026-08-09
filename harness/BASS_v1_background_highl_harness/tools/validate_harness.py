#!/usr/bin/env python3
"""Fail-closed live validation for the BASS Work harness; imports no solver code."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path, PurePosixPath
import re
import sys
import unicodedata

HARNESS_ROOT = Path(__file__).resolve().parents[1]
if str(HARNESS_ROOT) not in sys.path:
    sys.path.insert(0, str(HARNESS_ROOT))
from tools.build_file_manifest import excluded
from tools.static_plan import (
    H1_TESTS, SOURCE_NAMES, command_plan_fingerprint, expected_command_plan,
)


GATE_STATES = {"NOT_RUN", "PASS", "FAIL", "BLOCKED", "NOT_APPLICABLE"}
CLAIM_STATES = {"LOCKED_OUT_OF_SCOPE", "LOCKED_PENDING_EVIDENCE", "SUPPORTED",
                "PARTIALLY_SUPPORTED", "REJECTED", "INVALIDATED"}
DECISION_STATES = {"PENDING_OWNER", "RESOLVED"}
ARTIFACT_STATES = {
    "DURABLE_VERIFIED", "DURABLE_UNVERIFIED", "TRANSCRIPT_ONLY",
    "MISSING", "INVALIDATED",
}
RUN_STATE_FIELDS = {
    "schema_version", "current_phase", "current_node", "next_node",
    "last_durable_checkpoint", "artifact_status", "solver_code_present",
    "solver_code_executed", "solver_code_modified", "external_oracle_executed",
    "activity_evidence_refs", "blocker_codes", "resume_action",
}
RUN_ACTIONS_BY_PHASE = {
    "USER_SCOPE_CONFIRMATION":{
        "RESOLVE_OWNER_DECISIONS_THEN_AWAIT_CANONICAL_CODE",
        "AWAIT_EXPLICIT_CODE_READ_AUTHORIZATION",
    },
    "CODE_INTAKE_READ_ONLY":{"AWAIT_CANONICAL_CODE_THEN_READ_ONLY_C0"},
    "CODE_REALITY_AUDIT_READ_ONLY":{"PERFORM_READ_ONLY_CODE_REALITY_AUDIT"},
    "IMPLEMENTATION_AUTHORIZATION":{"AWAIT_IMPLEMENTATION_AUTHORIZATION"},
    "IMPLEMENTATION":{"EXECUTE_CURRENT_AUTHORIZED_NODE"},
    "RELEASE_AUDIT":{"PERFORM_RELEASE_AUDIT"},
    "OWNER_RELEASE_DECISION":{"AWAIT_OWNER_RELEASE_DECISION"},
    "RELEASED":{"NO_FURTHER_ACTION_RELEASED"},
    "INVALIDATION_REMEDIATION":{"REMEDIATE_INVALIDATED_NODE"},
}
CHECKPOINT_BY_NODE = {
    "H0":"H0_INPUT_AUDIT",
    "H1":"H1_INSTALLATION_SELF_TEST",
    "OD0":"OD0_SCOPE_CONFIRMATION",
    "C0":"C0_CODE_INTAKE",
    "C1":"C1_CODE_REALITY_AUDIT",
    "IA0":"IA0_IMPLEMENTATION_AUTHORIZATION",
    "C2":"C2_EQUATION_CODE_MAP",
    "C3":"C3_BIANCHI_FAMILY_DYNAMICS",
    "C4":"C4_ANALYTIC_LIMITS",
    "C5":"C5_HIGH_ELL_CONVERGENCE",
    "C6":"C6_COLLISION_HISTORY",
    "C7":"C7_TILT_POLARIZATION",
    "C8":"C8_BACKEND_OUTPUT_EQUIVALENCE",
    "C9":"C9_RELEASE_HOSTILE_AUDIT",
    "C10":"C10_OWNER_RELEASE_DECISION",
    "TERMINAL":"TERMINAL_RELEASE",
}
PHASE_OPTIONAL_BLOCKER_CODES = {
    "USER_SCOPE_CONFIRMATION":set(),
    "CODE_INTAKE_READ_ONLY":set(),
    "CODE_REALITY_AUDIT_READ_ONLY":set(),
    "IMPLEMENTATION_AUTHORIZATION":set(),
    "IMPLEMENTATION":{"TOOLCHAIN_PLAN_PENDING", "EXECUTION_PLAN_PENDING",
                      "DEPENDENCY_LOCK_PENDING"},
    "RELEASE_AUDIT":set(),
    "OWNER_RELEASE_DECISION":set(),
    "RELEASED":set(),
    "INVALIDATION_REMEDIATION":set(),
}
HIGH_ELL_CHANNEL_IDS = {
    "photon_I", "photon_E", "photon_B", "photon_V", "massless_neutrinos"
}
OD002_SECTOR_KEYS = {
    "global_tilt", "photon_I", "photon_E", "photon_B", "photon_V",
    "massless_neutrinos", "exact_electron_frame_thomson", "recombination", "reionization"
}
ACTIVITY_CONTRACT = {
    "solver_code_executed": {
        "activity":"SOLVER_CODE_EXECUTED", "authorization_key":"solver_execute",
        "action":"EXECUTE_SOLVER_CODE", "environment_flag":"solver_executed",
    },
    "solver_code_modified": {
        "activity":"SOLVER_CODE_MODIFIED", "authorization_key":"code_write",
        "action":"MODIFY_SOLVER_CODE", "environment_flag":"solver_modified",
    },
    "external_oracle_executed": {
        "activity":"EXTERNAL_ORACLE_EXECUTED", "authorization_key":"external_oracle_execute",
        "action":"EXECUTE_PINNED_EXTERNAL_ORACLE", "environment_flag":"external_oracle_executed",
    },
}
ORACLE_PIN = "539fcd6acc81dfd19d05951c2c5cbc3602eda077"
FAMILY_LEAF_CRITERIA = {
    "CLM-FAMILY-I": {"G-C3-FAM-I-RUNTIME","G-C3-FAM-I-CONSTRAINT","G-C3-FAM-I-LIMIT"},
    "CLM-FAMILY-II": {"G-C3-FAM-II-RUNTIME","G-C3-FAM-II-CONSTRAINT","G-C3-FAM-II-LIMIT"},
    "CLM-FAMILY-III": {"G-C3-FAM-III-RUNTIME","G-C3-FAM-III-CONSTRAINT","G-C3-FAM-III-LIMIT"},
    "CLM-FAMILY-IV": {"G-C3-FAM-IV-RUNTIME","G-C3-FAM-IV-CONSTRAINT","G-C3-FAM-IV-LIMIT"},
    "CLM-FAMILY-V": {"G-C3-FAM-V-RUNTIME","G-C3-FAM-V-CONSTRAINT","G-C3-FAM-V-LIMIT"},
    "CLM-FAMILY-VI-0": {"G-C3-FAM-VI-0-RUNTIME","G-C3-FAM-VI-0-CONSTRAINT","G-C3-FAM-VI-0-LIMIT"},
    "CLM-FAMILY-VI-H-GENERIC": {"G-C3-FAM-VI-H-GENERIC-RUNTIME","G-C3-FAM-VI-H-GENERIC-CONSTRAINT","G-C3-FAM-VI-H-GENERIC-LIMIT","G-C3-FAM-VI-H-GENERIC-H-DOMAIN"},
    "CLM-FAMILY-VI-MINUS-1-9": {"G-C3-FAM-VI-MINUS-1-9-RUNTIME","G-C3-FAM-VI-MINUS-1-9-CONSTRAINT","G-C3-FAM-VI-MINUS-1-9-LIMIT","G-C3-FAM-VI-MINUS-1-9-EXACT-DISPATCH"},
    "CLM-FAMILY-VII-0": {"G-C3-FAM-VII-0-RUNTIME","G-C3-FAM-VII-0-CONSTRAINT","G-C3-FAM-VII-0-LIMIT"},
    "CLM-FAMILY-VII-H": {"G-C3-FAM-VII-H-RUNTIME","G-C3-FAM-VII-H-CONSTRAINT","G-C3-FAM-VII-H-LIMIT"},
    "CLM-FAMILY-VIII": {"G-C3-FAM-VIII-RUNTIME","G-C3-FAM-VIII-CONSTRAINT","G-C3-FAM-VIII-LIMIT"},
    "CLM-FAMILY-IX": {"G-C3-FAM-IX-RUNTIME","G-C3-FAM-IX-CONSTRAINT","G-C3-FAM-IX-LIMIT"},
}
SECTOR_CONTRACT = {
    "global_tilt": ({"CLM-GLOBAL-TILT"}, {("G-C3","G-C3-TILT-DYNAMICS"),("G-C7","G-C7-TILT-FRAME")}, set()),
    "photon_I": ({"CLM-HIGH-ELL-PHOTON-I"}, {("G-C5","G-C5-CH-PHOTON-I")}, {"photon_I"}),
    "photon_E": ({"CLM-HIGH-ELL-PHOTON-E","CLM-POLARIZATION-E"}, {("G-C5","G-C5-CH-PHOTON-E"),("G-C7","G-C7-POL-E")}, {"photon_E"}),
    "photon_B": ({"CLM-HIGH-ELL-PHOTON-B","CLM-POLARIZATION-B"}, {("G-C5","G-C5-CH-PHOTON-B"),("G-C7","G-C7-POL-B")}, {"photon_B"}),
    "photon_V": ({"CLM-HIGH-ELL-PHOTON-V","CLM-POLARIZATION-V"}, {("G-C5","G-C5-CH-PHOTON-V"),("G-C7","G-C7-POL-V")}, {"photon_V"}),
    "massless_neutrinos": ({"CLM-HIGH-ELL-MASSLESS-NEUTRINOS","CLM-MASSLESS-NEUTRINO-RUNTIME"}, {("G-C5","G-C5-CH-MASSLESS-NU"),("G-C6","G-C6-MASSLESS-NU")}, {"massless_neutrinos"}),
    "exact_electron_frame_thomson": ({"CLM-EXACT-ELECTRON-FRAME-THOMSON"}, {("G-C6","G-C6-THOMSON")}, set()),
    "recombination": ({"CLM-RECOMBINATION"}, {("G-C6","G-C6-RECOMBINATION")}, set()),
    "reionization": ({"CLM-REIONIZATION"}, {("G-C6","G-C6-REIONIZATION")}, set()),
}
HIGH_ELL_ROW_CONTRACT = {
    "photon_I": {"id":"photon_I","sector_key":"photon_I","species":"photon","spin_weights":[0],"component":"I","ell_min":0,"tolerance_ref":"OD001.value.channel_tolerances.photon_I"},
    "photon_E": {"id":"photon_E","sector_key":"photon_E","species":"photon","spin_weights":[-2,2],"component":"E","ell_min":2,"tolerance_ref":"OD001.value.channel_tolerances.photon_E"},
    "photon_B": {"id":"photon_B","sector_key":"photon_B","species":"photon","spin_weights":[-2,2],"component":"B","ell_min":2,"tolerance_ref":"OD001.value.channel_tolerances.photon_B"},
    "photon_V": {"id":"photon_V","sector_key":"photon_V","species":"photon","spin_weights":[0],"component":"V","ell_min":0,"tolerance_ref":"OD001.value.channel_tolerances.photon_V"},
    "massless_neutrinos": {"id":"massless_neutrinos","sector_key":"massless_neutrinos","species":"each_evolved_massless_neutrino_species_or_declared_massless_aggregate","mass_assumption":"m_nu=0_exact","collision_model":"collisionless","spin_weights":[0],"component":"intensity","ell_min":0,"tolerance_ref":"OD001.value.channel_tolerances.massless_neutrinos"},
}
ALLOWED_TOP_LEVEL_FILES = {
    "AGENTS.md", "Makefile", "README.md", "START_HERE.md", "VERSION", "manifest.json"
}
ALLOWED_TOP_LEVEL_DIRS = {
    "audit", "contracts", "docs", "evidence", "policies", "prompts", "receipts",
    "reviews", "state", "templates", "tests", "tools"
}
ALLOWED_EXECUTABLE_SOURCE = {
    "tests/__init__.py", "tests/test_harness_tools.py", "tools/__init__.py", "tools/audit_archive.py",
    "tools/build_file_manifest.py", "tools/create_bundle.py", "tools/invalidate_state.py",
    "tools/issue_harness_evidence.py", "tools/run_static_checks.py", "tools/static_plan.py",
    "tools/validate_harness.py"
}
ALLOWED_HARNESS_PATHS = frozenset("""AGENTS.md
Makefile
README.md
START_HERE.md
VERSION
audit/FILE_MANIFEST.sha256
audit/INPUT_INVENTORY.json
audit/REPO_ORACLE_SNAPSHOT.md
audit/RUST_1_94_1_AUTHENTICITY.json
audit/TOOLCHAIN_STATUS.md
audit/logs/H0_REVIEW.md
audit/logs/H0_REVIEW_STATIC_CHECKS.json
audit/logs/H0_STATIC_CHECKS.json
audit/logs/H1_REVIEW.md
audit/logs/H1_REVIEW_STATIC_CHECKS.json
audit/logs/H1_STATIC_CHECKS.json
contracts/conventions.json
contracts/evidence_contract.json
contracts/external_oracle_lock.json
contracts/family_registry.json
contracts/high_ell_acceptance.json
contracts/owner_decisions.json
contracts/scientific_contract.json
contracts/scope_lock.json
contracts/state_machine.json
docs/HARNESS_AUDIT_REPORT.md
docs/OWNER_DECISIONS_REQUIRED.md
docs/REFERENCE_SOURCES.md
docs/RUNTIME_RECOVERY.md
docs/TRANSPLANT_MAP.md
evidence/E-H0-20260801-V2.json
evidence/E-H1-20260801-V2.json
manifest.json
policies/ARTIFACT_AND_PROVENANCE.md
policies/MULTI_AGENT_AND_INDEPENDENCE.md
policies/STOP_RETRY_AND_INVALIDATION.md
policies/TOOLCHAIN_AND_EXECUTION.md
prompts/01_CODE_INTAKE_AUDIT.md
prompts/02_BACKGROUND_HIGH_L_EXECUTOR.md
prompts/03_EXTERNAL_ORACLE_JOB.md
prompts/04_RELEASE_HOSTILE_AUDIT.md
receipts/H0_INPUT_AUDIT.json
receipts/H1_INSTALLATION_SELF_TEST.json
reviews/R-H0-20260801-V2.json
reviews/R-H1-20260801-V2.json
state/DECISION_LOG.md
state/EVIDENCE_LEDGER.md
state/FAILURE_LOG.md
state/claims.json
state/dag.json
state/gates.json
state/run_state.json
templates/CAS_CONTRACT.json
templates/action_authorization.json
templates/activity_receipt.json
templates/code_read_authorization.json
templates/gate_receipt.json
templates/owner_decision_receipt.json
templates/producer_evidence.json
templates/result_envelope.json
templates/review_attestation.json
tests/__init__.py
tests/test_harness_tools.py
tools/__init__.py
tools/audit_archive.py
tools/build_file_manifest.py
tools/create_bundle.py
tools/invalidate_state.py
tools/issue_harness_evidence.py
tools/run_static_checks.py
tools/static_plan.py
tools/validate_harness.py""".splitlines())
OD0_OWNER_RECEIPT_PATH = "receipts/OD0_OWNER_DECISIONS.json"
OD0_CODE_READ_AUTHORIZATION_PATH = "receipts/OD0_CODE_READ_AUTHORIZATION.json"
OD0_PASS_PATHS = frozenset({
    OD0_CODE_READ_AUTHORIZATION_PATH,
    "evidence/E-OD0-20260801-V2.json",
    "audit/logs/OD0_REVIEW.md",
    "reviews/R-OD0-20260801-V2.json",
    "receipts/OD0_SCOPE_CONFIRMATION.json",
})
H0_GOVERNING_FILES = frozenset({
    "contracts/evidence_contract.json", "policies/ARTIFACT_AND_PROVENANCE.md",
    "policies/MULTI_AGENT_AND_INDEPENDENCE.md", "policies/TOOLCHAIN_AND_EXECUTION.md",
    "templates/gate_receipt.json", "templates/producer_evidence.json",
    "templates/review_attestation.json", "tools/audit_archive.py",
    "tools/issue_harness_evidence.py", "tools/run_static_checks.py", "tools/static_plan.py",
    "tools/validate_harness.py", "audit/INPUT_INVENTORY.json",
    "audit/RUST_1_94_1_AUTHENTICITY.json", "audit/REPO_ORACLE_SNAPSHOT.md",
})
H1_GOVERNING_FILES = frozenset("""AGENTS.md
Makefile
README.md
START_HERE.md
VERSION
manifest.json
audit/INPUT_INVENTORY.json
audit/REPO_ORACLE_SNAPSHOT.md
audit/RUST_1_94_1_AUTHENTICITY.json
audit/TOOLCHAIN_STATUS.md
contracts/conventions.json
contracts/evidence_contract.json
contracts/external_oracle_lock.json
contracts/family_registry.json
contracts/high_ell_acceptance.json
contracts/scientific_contract.json
contracts/state_machine.json
docs/HARNESS_AUDIT_REPORT.md
docs/OWNER_DECISIONS_REQUIRED.md
docs/REFERENCE_SOURCES.md
docs/RUNTIME_RECOVERY.md
docs/TRANSPLANT_MAP.md
policies/ARTIFACT_AND_PROVENANCE.md
policies/MULTI_AGENT_AND_INDEPENDENCE.md
policies/STOP_RETRY_AND_INVALIDATION.md
policies/TOOLCHAIN_AND_EXECUTION.md
prompts/01_CODE_INTAKE_AUDIT.md
prompts/02_BACKGROUND_HIGH_L_EXECUTOR.md
prompts/03_EXTERNAL_ORACLE_JOB.md
prompts/04_RELEASE_HOSTILE_AUDIT.md
state/DECISION_LOG.md
state/EVIDENCE_LEDGER.md
state/FAILURE_LOG.md
templates/CAS_CONTRACT.json
templates/action_authorization.json
templates/activity_receipt.json
templates/code_read_authorization.json
templates/gate_receipt.json
templates/owner_decision_receipt.json
templates/producer_evidence.json
templates/result_envelope.json
templates/review_attestation.json
tests/__init__.py
tests/test_harness_tools.py
tools/__init__.py
tools/audit_archive.py
tools/build_file_manifest.py
tools/create_bundle.py
tools/invalidate_state.py
tools/issue_harness_evidence.py
tools/run_static_checks.py
tools/static_plan.py
tools/validate_harness.py""".splitlines())
H1_LIVE_VALIDATED_FILES = frozenset({
    "contracts/owner_decisions.json", "contracts/scope_lock.json", "state/claims.json",
    "state/dag.json", "state/gates.json", "state/run_state.json",
})
H1_SELF_OR_DEPENDENCY_FILES = frozenset({
    "audit/FILE_MANIFEST.sha256",
    "audit/logs/H0_REVIEW.md", "audit/logs/H0_REVIEW_STATIC_CHECKS.json",
    "audit/logs/H0_STATIC_CHECKS.json", "audit/logs/H1_REVIEW.md",
    "audit/logs/H1_REVIEW_STATIC_CHECKS.json", "audit/logs/H1_STATIC_CHECKS.json",
    "evidence/E-H0-20260801-V2.json", "evidence/E-H1-20260801-V2.json",
    "receipts/H0_INPUT_AUDIT.json", "receipts/H1_INSTALLATION_SELF_TEST.json",
    "reviews/R-H0-20260801-V2.json", "reviews/R-H1-20260801-V2.json",
})
OD0_PRODUCER_INPUT_FILES = frozenset({
    "contracts/owner_decisions.json",
    OD0_OWNER_RECEIPT_PATH,
    OD0_CODE_READ_AUTHORIZATION_PATH,
})
FORBIDDEN_SOLVER_SUFFIXES = {
    ".rs", ".c", ".cc", ".cpp", ".cxx", ".h", ".hpp", ".f", ".f90", ".f95",
    ".so", ".dylib", ".dll", ".wasm", ".rlib", ".a", ".o", ".whl"
}
REQUIRED = [
    "VERSION", "README.md", "START_HERE.md", "AGENTS.md", "manifest.json",
    "contracts/scope_lock.json", "contracts/state_machine.json",
    "contracts/evidence_contract.json", "contracts/conventions.json",
    "contracts/owner_decisions.json", "contracts/scientific_contract.json",
    "contracts/family_registry.json", "contracts/high_ell_acceptance.json",
    "contracts/external_oracle_lock.json", "state/dag.json", "state/gates.json",
    "state/claims.json", "state/run_state.json", "audit/INPUT_INVENTORY.json",
    "audit/FILE_MANIFEST.sha256", "audit/RUST_1_94_1_AUTHENTICITY.json",
    "docs/HARNESS_AUDIT_REPORT.md", "receipts/H0_INPUT_AUDIT.json",
    "receipts/H1_INSTALLATION_SELF_TEST.json",
    "templates/owner_decision_receipt.json",
    "templates/code_read_authorization.json",
    "templates/action_authorization.json",
    "templates/activity_receipt.json",
]


def load_json(root: Path, relative: str):
    with (root / relative).open(encoding="utf-8") as handle:
        return json.load(handle)


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_bytes(value) -> bytes:
    def normalized(item):
        if isinstance(item, str):
            return unicodedata.normalize("NFC", item)
        if isinstance(item, list):
            return [normalized(row) for row in item]
        if isinstance(item, dict):
            return {normalized(key): normalized(val) for key, val in item.items()}
        if isinstance(item, float):
            raise ValueError("floats are forbidden in canonical evidence records")
        return item
    return json.dumps(normalized(value), sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def canonical_hash(value) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def valid_sha(value) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def valid_timestamp(value) -> bool:
    if not isinstance(value, str):
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None


def safe_local_path(root: Path, relative: str) -> Path | None:
    if not isinstance(relative, str) or not relative or "\\" in relative:
        return None
    pure = PurePosixPath(relative)
    if pure.is_absolute() or ".." in pure.parts:
        return None
    path = root / pure
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return None
    return path


def verify_file_ref(root: Path, ref: dict, errors: list[str], label: str) -> None:
    if not isinstance(ref, dict):
        errors.append(f"{label} is not an object")
        return
    path = safe_local_path(root, ref.get("path"))
    if path is None or not path.is_file() or path.is_symlink():
        errors.append(f"{label} path missing/not regular: {ref.get('path')}")
        return
    if ref.get("bytes") != path.stat().st_size:
        errors.append(f"{label} byte count mismatch: {ref.get('path')}")
    if not valid_sha(ref.get("sha256")) or ref.get("sha256") != file_hash(path):
        errors.append(f"{label} hash mismatch: {ref.get('path')}")


def project_gate(row: dict) -> dict:
    return {key: value for key, value in row.items() if key != "status"}


def project_node(row: dict) -> dict:
    return {key: value for key, value in row.items()
            if key not in {"status", "receipt", "invalidation"}}


def project_live_file(relative: str, value: dict) -> dict:
    if relative == "contracts/owner_decisions.json":
        projected = {key:val for key, val in value.items()
                     if key not in {"all_resolved", "owner_receipt", "decisions"}}
        projected["decisions"] = [
            {key:val for key, val in row.items() if key not in {"status", "value"}}
            for row in value.get("decisions", [])
        ]
        return projected
    if relative == "contracts/scope_lock.json":
        projected = {key:val for key, val in value.items()
                     if key not in {"current_phase", "authorizations"}}
        projected["authorization_keys"] = sorted(value.get("authorizations", {}))
        return projected
    if relative == "state/claims.json":
        projected = {key:val for key, val in value.items() if key != "claims"}
        projected["claims"] = [
            {key:val for key, val in row.items()
             if key not in {"status", "value", "evidence_ids"}}
            for row in value.get("claims", [])
        ]
        return projected
    if relative == "state/dag.json":
        projected = {key:val for key, val in value.items() if key != "nodes"}
        projected["nodes"] = [project_node(row) for row in value.get("nodes", [])]
        return projected
    if relative == "state/gates.json":
        projected = {key:val for key, val in value.items() if key != "gates"}
        projected["gates"] = [project_gate(row) for row in value.get("gates", [])]
        return projected
    if relative == "state/run_state.json":
        return {"schema_version":value.get("schema_version"),
                "field_names":sorted(value)}
    raise ValueError(f"no immutable projection rule for live file: {relative}")


def governing_snapshot(root: Path, node_id: str, gate: dict, node: dict,
                       evidence_contract: dict, errors: list[str]) -> dict | None:
    profile = evidence_contract.get("node_profiles", {}).get(node_id)
    if not isinstance(profile, dict):
        errors.append(f"missing evidence-contract node profile: {node_id}")
        return None
    rows: list[dict] = []
    for relative in profile.get("governing_files", []):
        path = safe_local_path(root, relative)
        if path is None or not path.is_file() or path.is_symlink():
            errors.append(f"governing file missing/not regular for {node_id}: {relative}")
            continue
        rows.append({"path":relative,"bytes":path.stat().st_size,"sha256":file_hash(path)})
    live_projections: list[dict] = []
    for relative in profile.get("live_validated_mutable_files", []):
        path = safe_local_path(root, relative)
        if path is None or not path.is_file() or path.is_symlink():
            errors.append(f"live projection file missing/not regular for {node_id}: {relative}")
            continue
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
            projection = project_live_file(relative, value)
        except (json.JSONDecodeError, UnicodeDecodeError, ValueError) as error:
            errors.append(f"live projection failed for {node_id} {relative}: {error}")
            continue
        live_projections.append({"path":relative,
                                 "projection_sha256":canonical_hash(projection)})
    core = {
        "algorithm": evidence_contract.get("governing_fingerprint_algorithm"),
        "files": rows,
        "live_file_projections": live_projections,
        "gate_projection": project_gate(gate),
        "node_projection": project_node(node),
    }
    return {**core, "fingerprint": canonical_hash(core)}


def validate_evidence_contract(contract: dict, errors: list[str]) -> None:
    if set(contract) != {
            "schema_version", "canonical_json", "governing_fingerprint_algorithm",
            "record_schemas", "pass_policy", "node_profiles"}:
        errors.append("evidence contract top-level field set mismatch")
    if contract.get("canonical_json") != {
            "encoding":"UTF-8", "unicode":"NFC", "sort_keys":True,
            "separators":[",", ":"], "allow_nan":False}:
        errors.append("evidence contract canonical-JSON rules mismatch")
    expected_schemas = {
        "bass.static_check_log/v2", "bass.producer_evidence/v2",
        "bass.review_attestation/v2", "bass.gate_receipt/v2",
        "bass.owner_decision_receipt/v1", "bass.code_read_authorization/v1",
        "bass.action_authorization/v1",
        "bass.activity_receipt/v1",
    }
    expected_pass_policy = {
        "producer_evidence_required":True,
        "independent_review_required":True,
        "independent_static_reexecution_required_for_H0_H1":True,
        "canonical_static_command_plan_required_for_H0_H1":True,
        "result_specific_semantic_oracles_required_for_H0_H1":True,
        "static_log_execution_snapshot_required":True,
        "no_timeout_signal_skip_or_fallback":True,
        "all_required_criteria_exactly_once":True,
        "all_gate_obligations_exactly_once":True,
        "nonempty_evidence_refs_for_pass":True,
    }
    if (contract.get("schema_version") != 2
            or contract.get("governing_fingerprint_algorithm")
            != "SHA256_OF_CANONICAL_JSON_V1"):
        errors.append("evidence contract schema/fingerprint algorithm mismatch")
    schemas = contract.get("record_schemas", [])
    if set(schemas) != expected_schemas or len(schemas) != len(expected_schemas):
        errors.append("evidence contract record schema set mismatch")
    if contract.get("pass_policy") != expected_pass_policy:
        errors.append("evidence contract fail-closed PASS policy mismatch")
    profiles = contract.get("node_profiles", {})
    if set(profiles) != {"H0", "H1", "OD0"}:
        errors.append("evidence contract bootstrap node-profile set mismatch")
        return
    expected_governing = {
        "H0":H0_GOVERNING_FILES,
        "H1":H1_GOVERNING_FILES,
        "OD0":H1_GOVERNING_FILES,
    }
    expected_profile_fields = {
        "H0":{"governing_files", "review_required"},
        "H1":{"governing_files", "live_validated_mutable_files", "review_required"},
        "OD0":{"governing_files", "producer_input_files",
               "live_validated_mutable_files", "review_required"},
    }
    for node_id, expected in expected_governing.items():
        if set(profiles.get(node_id, {})) != expected_profile_fields[node_id]:
            errors.append(f"{node_id} evidence profile field set mismatch")
        rows = profiles.get(node_id, {}).get("governing_files", [])
        if set(rows) != expected or len(rows) != len(expected):
            errors.append(f"{node_id} immutable governing-file set mismatch")
        if profiles.get(node_id, {}).get("review_required") is not True:
            errors.append(f"{node_id} independent review requirement missing")
    h1_live = profiles.get("H1", {}).get("live_validated_mutable_files", [])
    if set(h1_live) != H1_LIVE_VALIDATED_FILES or len(h1_live) != len(H1_LIVE_VALIDATED_FILES):
        errors.append("H1 live-validated mutable-file set mismatch")
    od0_live = profiles.get("OD0", {}).get("live_validated_mutable_files", [])
    if set(od0_live) != H1_LIVE_VALIDATED_FILES or len(od0_live) != len(H1_LIVE_VALIDATED_FILES):
        errors.append("OD0 live-validated mutable-file set mismatch")
    od0_inputs = profiles.get("OD0", {}).get("producer_input_files", [])
    if set(od0_inputs) != OD0_PRODUCER_INPUT_FILES or len(od0_inputs) != len(OD0_PRODUCER_INPUT_FILES):
        errors.append("OD0 producer input-file set mismatch")
    classified = H1_GOVERNING_FILES | H1_LIVE_VALIDATED_FILES | H1_SELF_OR_DEPENDENCY_FILES
    if (classified != ALLOWED_HARNESS_PATHS
            or (H1_GOVERNING_FILES & H1_LIVE_VALIDATED_FILES)
            or (H1_GOVERNING_FILES & H1_SELF_OR_DEPENDENCY_FILES)
            or (H1_LIVE_VALIDATED_FILES & H1_SELF_OR_DEPENDENCY_FILES)):
        errors.append("standalone H1 path-classification partition mismatch")


def downstream_nodes(node_map: dict[str, dict], start: str) -> list[str]:
    affected = {start}
    changed = True
    while changed:
        changed = False
        for node_id, row in node_map.items():
            if node_id not in affected and affected.intersection(row.get("depends_on", [])):
                affected.add(node_id)
                changed = True
    return [node_id for node_id in node_map if node_id in affected]


def validate_manifest_hashes(root: Path, errors: list[str]) -> None:
    manifest = root / "audit/FILE_MANIFEST.sha256"
    if not manifest.exists():
        errors.append("missing hash manifest")
        return
    seen: set[str] = set()
    for line_number, line in enumerate(manifest.read_text(encoding="utf-8").splitlines(), 1):
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        if not match:
            errors.append(f"malformed hash manifest line {line_number}")
            continue
        expected, relative = match.groups()
        if relative in seen:
            errors.append(f"duplicate manifest path: {relative}")
            continue
        seen.add(relative)
        path = safe_local_path(root, relative)
        if path is None or not path.is_file() or path.is_symlink():
            errors.append(f"manifest target missing/not regular: {relative}")
        elif file_hash(path) != expected:
            errors.append(f"manifest hash mismatch: {relative}")
    expected_paths: set[str] = set()
    for path in root.rglob("*"):
        relative_path = path.relative_to(root)
        if excluded(relative_path, Path("audit/FILE_MANIFEST.sha256")):
            continue
        if path.is_symlink():
            errors.append(f"symlink present in harness: {relative_path.as_posix()}")
        elif path.is_file():
            expected_paths.add(relative_path.as_posix())
        elif not path.is_dir():
            errors.append(f"special file present in harness: {relative_path.as_posix()}")
    missing = expected_paths - seen
    unexpected = seen - expected_paths
    if missing:
        errors.append(f"files missing from hash manifest: {sorted(missing)}")
    if unexpected:
        errors.append(f"unexpected paths in hash manifest: {sorted(unexpected)}")


def validate_harness_payload(root: Path, manifest: dict, scope: dict, decisions: dict,
                             errors: list[str]) -> None:
    if manifest.get("solver_code_included") is not False:
        errors.append("manifest must state solver_code_included=false")
    if manifest.get("payload_mode") != "HARNESS_ONLY":
        errors.append("manifest payload_mode must be HARNESS_ONLY")
    if manifest.get("declared_code_roots") != [] or scope.get("declared_code_roots") != []:
        errors.append("standalone harness may not contain canonical solver code roots")
    allowed_paths = set(ALLOWED_HARNESS_PATHS)
    if decisions.get("all_resolved") is True:
        allowed_paths.add(OD0_OWNER_RECEIPT_PATH)
    if (decisions.get("all_resolved") is True
            and (scope.get("authorizations", {}).get("code_read") is True
                 or scope.get("current_phase") == "INVALIDATION_REMEDIATION")):
        allowed_paths.update(OD0_PASS_PATHS)
    for path in root.rglob("*"):
        relative_path = path.relative_to(root)
        relative = relative_path.as_posix()
        if (relative != "audit/FILE_MANIFEST.sha256"
                and excluded(relative_path, Path("audit/FILE_MANIFEST.sha256"))):
            continue
        if path.is_symlink():
            errors.append(f"symlink present in harness payload: {relative}")
            continue
        if not path.is_file():
            continue
        if relative not in allowed_paths:
            errors.append(f"undeclared pre-code path: {relative}")
            continue
        if path.suffix.lower() in FORBIDDEN_SOLVER_SUFFIXES:
            errors.append(f"solver/binary payload forbidden in harness: {relative}")
        if path.suffix == ".py" and relative not in ALLOWED_EXECUTABLE_SOURCE:
            errors.append(f"undeclared executable harness source: {relative}")
        if path.stat().st_mode & 0o111:
            errors.append(f"executable mode forbidden in standalone harness: {relative}")
        raw = path.read_bytes()
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            errors.append(f"non-UTF-8/binary file forbidden in standalone harness: {relative}")
            continue
        if any(ord(character) < 32 and character not in "\t\n\r" for character in text):
            errors.append(f"binary control byte forbidden in standalone harness: {relative}")


def valid_tolerance_pair(value) -> bool:
    if not isinstance(value, dict) or set(value) != {"atol", "rtol"}:
        return False
    parsed: dict[str, Decimal] = {}
    for key in ("atol", "rtol"):
        encoded = value.get(key)
        if not isinstance(encoded, str) or not re.fullmatch(
                r"(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?", encoded):
            return False
        try:
            parsed[key] = Decimal(encoded)
        except InvalidOperation:
            return False
        if not parsed[key].is_finite() or parsed[key] < 0:
            return False
    return parsed["rtol"] > 0


def validate_decision_value(row: dict, errors: list[str]) -> bool:
    decision_id = row.get("id")
    status = row.get("status")
    value = row.get("value")
    if status not in DECISION_STATES:
        errors.append(f"invalid owner-decision status: {decision_id}")
        return False
    if status == "PENDING_OWNER":
        if value is not None:
            errors.append(f"pending owner decision must have value=null: {decision_id}")
            return False
        return True
    if not isinstance(value, dict):
        errors.append(f"resolved owner decision needs structured value: {decision_id}")
        return False
    valid = True
    if decision_id == "OD001":
        required = {"mode", "production_floor_L_prod", "channel_tolerances",
                    "low_ell_observable_tolerance"}
        if (set(row.get("required_value_fields", [])) != required
                or row.get("allowed_modes") != ["ADAPTIVE_CONFIGURABLE_WITH_PRODUCTION_FLOOR"]
                or row.get("tolerance_encoding")
                != "NONNEGATIVE_ATOL_AND_POSITIVE_RTOL_DECIMAL_STRINGS"
                or set(value) != required):
            errors.append("OD001 resolved value must contain the exact acceptance fields")
            valid = False
        if value.get("mode") != "ADAPTIVE_CONFIGURABLE_WITH_PRODUCTION_FLOOR":
            errors.append("OD001 mode is invalid")
            valid = False
        floor = value.get("production_floor_L_prod")
        if type(floor) is not int or floor < 2:
            errors.append("OD001 production_floor_L_prod must be an integer >=2")
            valid = False
        tolerances = value.get("channel_tolerances")
        if (not isinstance(tolerances, dict) or not tolerances
                or not set(tolerances).issubset(HIGH_ELL_CHANNEL_IDS)
                or any(not valid_tolerance_pair(pair) for pair in tolerances.values())):
            errors.append("OD001 channel tolerances are not a valid high-ell tolerance map")
            valid = False
        if not valid_tolerance_pair(value.get("low_ell_observable_tolerance")):
            errors.append("OD001 low-ell observable tolerance is invalid")
            valid = False
    elif decision_id == "OD002":
        keys = set(row.get("required_keys", []))
        if keys != OD002_SECTOR_KEYS or set(value) != keys or any(
                type(value[key]) is not bool for key in keys):
            errors.append("OD002 resolved value must be the exact boolean sector map")
            valid = False
        elif (not value["photon_I"] or value["photon_E"] != value["photon_B"]
              or ((value["recombination"] or value["reionization"])
                  and not value["exact_electron_frame_thomson"])):
            errors.append("OD002 dependency rule violated")
            valid = False
    elif decision_id == "OD003":
        required = {"role", "pinned_commit"}
        if (set(row.get("required_value_fields", [])) != required or set(value) != required
                or row.get("allowed_roles") != ["READ_ONLY_EXTERNAL_ORACLE"]
                or row.get("required_pinned_commit") != ORACLE_PIN
                or value.get("role") != "READ_ONLY_EXTERNAL_ORACLE"
                or value.get("pinned_commit") != ORACLE_PIN):
            errors.append("OD003 must select the exact pinned read-only oracle")
            valid = False
    elif decision_id == "OD004":
        required = {"rust_backend_in_v1", "provided_rustcore_role", "pyo3_surface_in_v1",
                    "independent_python_reference_required", "rust_1_94_1_policy"}
        expected_roles = {"EXCLUDED", "READ_ONLY_REFERENCE", "QUARANTINED_PRODUCTION_CANDIDATE"}
        expected_policies = {"STRICT_REPRODUCTION_PIN", "MINIMUM_SUPPORTED_VERSION", "NOT_REQUIRED"}
        if (set(row.get("required_value_fields", [])) != required
                or set(row.get("allowed_rustcore_roles", [])) != expected_roles
                or set(row.get("allowed_toolchain_policies", [])) != expected_policies
                or set(value) != required):
            errors.append("OD004 resolved value must contain the exact backend fields")
            return False
        backend = value.get("rust_backend_in_v1")
        pyo3 = value.get("pyo3_surface_in_v1")
        independent = value.get("independent_python_reference_required")
        role = value.get("provided_rustcore_role")
        policy = value.get("rust_1_94_1_policy")
        if any(type(item) is not bool for item in (backend, pyo3, independent)):
            errors.append("OD004 backend, PyO3, and independent-reference values must be booleans")
            valid = False
        if role not in expected_roles:
            errors.append("OD004 provided Rust-core role is invalid")
            valid = False
        if policy not in expected_policies:
            errors.append("OD004 Rust toolchain policy is invalid")
            valid = False
        if type(backend) is bool and type(pyo3) is bool and type(independent) is bool:
            if pyo3 and not backend:
                errors.append("OD004 PyO3 surface requires a v1 Rust backend")
                valid = False
            if backend and (not independent or policy == "NOT_REQUIRED"):
                errors.append("OD004 Rust backend requires an independent Python reference and toolchain policy")
                valid = False
            if not backend and (pyo3 or policy != "NOT_REQUIRED"):
                errors.append("OD004 disabled Rust backend requires no PyO3 and NOT_REQUIRED toolchain policy")
                valid = False
            if role == "QUARANTINED_PRODUCTION_CANDIDATE" and (not backend or not independent):
                errors.append("OD004 quarantined production candidate requires Rust and independent reference")
                valid = False
    else:
        errors.append(f"unknown owner decision: {decision_id}")
        valid = False
    return valid


def validate_phase_state(scope: dict, decisions: dict, state_machine: dict,
                         node_map: dict[str, dict], run_state: dict,
                         errors: list[str]) -> None:
    phase = scope.get("current_phase")
    if phase != run_state.get("current_phase"):
        errors.append("scope and run-state phases differ")
    rule_map = {row.get("id"): row for row in state_machine.get("phases", [])}
    rule = rule_map.get(phase)
    if rule is None:
        errors.append(f"unknown current phase: {phase}")
        return
    current_node = run_state.get("current_node")
    if current_node not in rule.get("current_nodes", []):
        errors.append(f"current node {current_node} is invalid for phase {phase}")
    for node_id in rule.get("requires_pass", []):
        if node_map.get(node_id, {}).get("status") != "PASS":
            errors.append(f"phase {phase} requires PASS node: {node_id}")
    authorizations = scope.get("authorizations", {})
    known_auth = {
        "code_read", "code_write", "solver_build", "solver_execute", "dependency_install",
        "external_oracle_execute", "external_repo_write", "github_write", "public_release"
    }
    if set(authorizations) != known_auth or any(type(value) is not bool for value in authorizations.values()):
        errors.append("authorization key set/value types invalid")
    true_auth = {key for key, value in authorizations.items() if value is True}
    required_true = set(rule.get("required_true", []))
    allowed_true = set(rule.get("allowed_true", []))
    if not required_true.issubset(true_auth):
        errors.append(f"phase {phase} lacks required authorizations: {sorted(required_true - true_auth)}")
    if not true_auth.issubset(allowed_true):
        errors.append(f"phase {phase} has forbidden authorizations: {sorted(true_auth - allowed_true)}")
    prohibitions = scope.get("permanent_prohibitions", {})
    if set(prohibitions) != {"spatial_perturbations", "stochastic_primordial_sector",
                            "likelihood_or_data_fitting"} or any(value is not True for value in prohibitions.values()):
        errors.append("permanent v1 scope prohibitions are incomplete or unlocked")
    transition = scope.get("transition_requirements", {})
    code_read_reqs = transition.get("code_read", [])
    if any("C0" in item or "code_intake_receipt" in item.lower() for item in code_read_reqs):
        errors.append("code-read authorization contains a circular C0 prerequisite")
    decision_rows = decisions.get("decisions", [])
    valid_rows = [validate_decision_value(row, errors) for row in decision_rows]
    derived_all = (bool(decision_rows) and all(valid_rows)
                   and all(row.get("status") == "RESOLVED" for row in decision_rows))
    if decisions.get("all_resolved") is not derived_all:
        errors.append("owner all_resolved is not derived from decision rows")
    owner_receipt = decisions.get("owner_receipt")
    if derived_all and not isinstance(owner_receipt, dict):
        errors.append("resolved owner decisions require a snapshot-bound owner receipt")
    if not derived_all and owner_receipt is not None:
        errors.append("pending/invalid owner decisions require owner_receipt=null")
    decision_map = {row.get("id"): row for row in decision_rows}
    if derived_all:
        od1 = decision_map["OD001"]["value"]
        od2 = decision_map["OD002"]["value"]
        expected_channels = {key for key in HIGH_ELL_CHANNEL_IDS if od2[key]}
        if set(od1["channel_tolerances"]) != expected_channels:
            errors.append("OD001 channel tolerances must exactly match enabled OD002 high-ell sectors")
    if phase not in {"USER_SCOPE_CONFIRMATION", "INVALIDATION_REMEDIATION"} and not derived_all:
        errors.append(f"phase {phase} requires all owner decisions resolved")


def parsed_timestamp(value: str) -> datetime | None:
    if not valid_timestamp(value):
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def referenced_json(root: Path, ref: dict, errors: list[str], label: str) -> dict | None:
    verify_file_ref(root, ref, errors, label)
    path = safe_local_path(root, ref.get("path") if isinstance(ref, dict) else None)
    if path is None or not path.is_file() or path.is_symlink():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        errors.append(f"{label} is not valid JSON")
        return None
    if not isinstance(value, dict):
        errors.append(f"{label} JSON root is not an object")
        return None
    return value


def validate_activity_receipt(root: Path, receipt: dict, activity_key: str,
                              node_map: dict[str, dict], errors: list[str], label: str) -> None:
    contract = ACTIVITY_CONTRACT[activity_key]
    expected_fields = {
        "schema", "activity_id", "activity", "occurred_at", "node_id",
        "authorization_key", "authorization_at_time_ref", "producer_evidence_ref",
        "independent_review_ref",
    }
    if set(receipt) != expected_fields:
        errors.append(f"activity receipt field set invalid: {label}")
        return
    if receipt.get("schema") != "bass.activity_receipt/v1":
        errors.append(f"activity receipt schema invalid: {label}")
    if (not isinstance(receipt.get("activity_id"), str)
            or re.fullmatch(r"[A-Z][A-Z0-9_.-]{2,127}", receipt["activity_id"]) is None):
        errors.append(f"activity receipt ID invalid: {label}")
    if (receipt.get("activity") != contract["activity"]
            or receipt.get("authorization_key") != contract["authorization_key"]):
        errors.append(f"activity receipt category/authorization mismatch: {label}")
    occurred = parsed_timestamp(receipt.get("occurred_at"))
    if occurred is None:
        errors.append(f"activity receipt timestamp invalid: {label}")
    activity_node = receipt.get("node_id")
    if activity_node not in node_map:
        errors.append(f"activity receipt node unknown: {label}")

    authorization_ref = receipt.get("authorization_at_time_ref")
    if (not isinstance(authorization_ref, dict)
            or set(authorization_ref) != {"path", "bytes", "sha256"}
            or re.fullmatch(r"receipts/authorizations/[A-Z0-9][A-Z0-9_.-]*\.json",
                            authorization_ref.get("path", "")) is None):
        errors.append(f"activity authorization reference invalid: {label}")
        authorization = None
    else:
        authorization = referenced_json(root, authorization_ref, errors,
                                        f"activity authorization {label}")
    authorization_time: datetime | None = None
    if authorization is not None:
        authorization_fields = {
            "schema", "authorization_id", "issued_at", "node_id", "authorization_key",
            "action", "granted", "owner_confirmation", "scope",
            "prerequisite_gate_receipt_refs", "approved_plan_ref",
        }
        if set(authorization) != authorization_fields:
            errors.append(f"activity action-authorization field set invalid: {label}")
        if (authorization.get("schema") != "bass.action_authorization/v1"
                or authorization.get("authorization_key") != contract["authorization_key"]
                or authorization.get("action") != contract["action"]
                or authorization.get("granted") is not True
                or authorization.get("owner_confirmation") != "EXPLICIT"):
            errors.append(f"activity action authorization is not an exact explicit grant: {label}")
        if (not isinstance(authorization.get("authorization_id"), str)
                or re.fullmatch(r"[A-Z][A-Z0-9_.-]{2,127}",
                                authorization["authorization_id"]) is None
                or not isinstance(authorization.get("scope"), str)
                or not authorization["scope"]):
            errors.append(f"activity action authorization identity/scope invalid: {label}")
        authorization_time = parsed_timestamp(authorization.get("issued_at"))
        if authorization_time is None:
            errors.append(f"activity action authorization timestamp invalid: {label}")
        authorization_node = authorization.get("node_id")
        if authorization_node not in node_map:
            errors.append(f"activity action authorization node unknown: {label}")
        elif activity_node in node_map:
            ancestors: set[str] = set()
            frontier = list(node_map[activity_node].get("depends_on", []))
            while frontier:
                ancestor = frontier.pop()
                if ancestor in ancestors or ancestor not in node_map:
                    continue
                ancestors.add(ancestor)
                frontier.extend(node_map[ancestor].get("depends_on", []))
            if authorization_node != activity_node and authorization_node not in ancestors:
                errors.append(f"activity authorization is not on the activity dependency chain: {label}")
        prerequisite_refs = authorization.get("prerequisite_gate_receipt_refs")
        if not isinstance(prerequisite_refs, list) or not prerequisite_refs:
            errors.append(f"activity authorization lacks prerequisite PASS receipts: {label}")
            prerequisite_refs = []
        prerequisite_nodes: list[str] = []
        for ref_index, prerequisite_ref in enumerate(prerequisite_refs):
            if (not isinstance(prerequisite_ref, dict)
                    or set(prerequisite_ref) != {"path", "bytes", "sha256"}):
                errors.append(f"activity prerequisite reference invalid: {label}[{ref_index}]")
                continue
            prerequisite = referenced_json(
                root, prerequisite_ref, errors,
                f"activity prerequisite {label}[{ref_index}]",
            )
            if (prerequisite is None or prerequisite.get("schema") != "bass.gate_receipt/v2"
                    or prerequisite.get("status") != "PASS"):
                errors.append(f"activity prerequisite is not a PASS gate receipt: {label}[{ref_index}]")
            else:
                prerequisite_nodes.append(prerequisite.get("node_id"))
        required_prerequisites = ({"C0", "C1"}
                                  if activity_key in {"solver_code_executed", "solver_code_modified"}
                                  else {"C0"})
        if not required_prerequisites.issubset(set(prerequisite_nodes)):
            errors.append(f"activity authorization prerequisite set incomplete: {label}")
        if len(prerequisite_nodes) != len(set(prerequisite_nodes)):
            errors.append(f"activity authorization prerequisite receipts duplicated: {label}")
        plan_ref = authorization.get("approved_plan_ref")
        if (not isinstance(plan_ref, dict) or set(plan_ref) != {"path", "bytes", "sha256"}
                or not plan_ref.get("path", "").startswith("evidence/plans/")):
            errors.append(f"activity authorization approved-plan reference invalid: {label}")
        else:
            verify_file_ref(root, plan_ref, errors, f"activity approved plan {label}")

    producer_ref = receipt.get("producer_evidence_ref")
    if (not isinstance(producer_ref, dict)
            or set(producer_ref) != {"path", "bytes", "sha256", "evidence_fingerprint"}
            or not producer_ref.get("path", "").startswith("evidence/")):
        errors.append(f"activity producer-evidence reference invalid: {label}")
        producer = None
    else:
        producer = referenced_json(root, producer_ref, errors,
                                   f"activity producer evidence {label}")
    producer_time: datetime | None = None
    if producer is not None:
        producer_fields = {
            "schema", "evidence_id", "node_id", "gate_id", "recorded_at", "producer",
            "governing", "dependencies", "inputs", "environment", "execution", "logs",
            "artifacts", "criterion_results", "obligation_results", "claim_effects",
            "claim_boundary", "evidence_fingerprint",
        }
        if set(producer) != producer_fields:
            errors.append(f"activity producer evidence field set invalid: {label}")
        producer_core = {key:value for key, value in producer.items()
                         if key != "evidence_fingerprint"}
        execution_record = producer.get("execution", {})
        if not isinstance(execution_record, dict):
            execution_record = {}
        commands = execution_record.get("commands", [])
        environment_record = producer.get("environment", {})
        if not isinstance(environment_record, dict):
            environment_record = {}
        environment = environment_record.get("details", {})
        if not isinstance(environment, dict):
            environment = {}
        producer_identity = producer.get("producer", {})
        if not isinstance(producer_identity, dict):
            producer_identity = {}
        governing = producer.get("governing", {})
        if not isinstance(governing, dict):
            governing = {}
        if (producer.get("schema") != "bass.producer_evidence/v2"
                or producer.get("node_id") != activity_node
                or producer.get("gate_id") != node_map.get(activity_node, {}).get("gate_id")
                or producer.get("evidence_fingerprint") != canonical_hash(producer_core)
                or producer_ref.get("evidence_fingerprint")
                != producer.get("evidence_fingerprint")):
            errors.append(f"activity producer evidence identity/fingerprint invalid: {label}")
        if (set(producer_identity) != {"run_id", "assignment_id", "lane_id", "role"}
                or producer_identity.get("role") != "producer"
                or any(not isinstance(producer_identity.get(field), str)
                       or not producer_identity[field]
                       for field in ("run_id", "assignment_id", "lane_id"))):
            errors.append(f"activity producer identity invalid: {label}")
        governing_core = {key:value for key, value in governing.items() if key != "fingerprint"}
        if (set(governing) != {"algorithm", "files", "live_file_projections",
                              "gate_projection", "node_projection", "fingerprint"}
                or governing.get("algorithm") != "SHA256_OF_CANONICAL_JSON_V1"
                or governing.get("fingerprint") != canonical_hash(governing_core)):
            errors.append(f"activity producer governing fingerprint invalid: {label}")
        if (set(environment_record) != {"details", "fingerprint"}
                or not isinstance(environment, dict)
                or environment_record.get("fingerprint") != canonical_hash(environment)):
            errors.append(f"activity producer environment fingerprint invalid: {label}")
        if (set(execution_record) != {"mode", "commands"}
                or not isinstance(execution_record.get("mode"), str)
                or not execution_record["mode"]):
            errors.append(f"activity producer execution envelope invalid: {label}")
        if (not isinstance(commands, list) or not commands
                or any(not isinstance(row, dict)
                       or set(row) != {"id", "argv", "cwd", "started_at", "ended_at",
                                          "exit_code", "timed_out", "signal", "skipped",
                                          "fallback_used", "result", "log_refs"}
                       or not isinstance(row.get("id"), str) or not row["id"]
                       or not isinstance(row.get("argv"), list) or not row["argv"]
                       or not isinstance(row.get("cwd"), str) or not row["cwd"]
                       or not valid_timestamp(row.get("started_at"))
                       or not valid_timestamp(row.get("ended_at"))
                       or row.get("exit_code") != 0 or row.get("timed_out") is not False
                       or row.get("signal") is not None or row.get("skipped") is not False
                       or row.get("fallback_used") is not False or row.get("result") != "PASS"
                       for row in commands)):
            errors.append(f"activity producer evidence lacks clean PASS commands: {label}")
        producer_logs = producer.get("logs", [])
        producer_artifacts = producer.get("artifacts", [])
        if not isinstance(producer_logs, list):
            errors.append(f"activity producer logs registry invalid: {label}")
            producer_logs = []
        if not isinstance(producer_artifacts, list):
            errors.append(f"activity producer artifacts registry invalid: {label}")
            producer_artifacts = []
        log_ids = {row.get("id") for row in producer_logs if isinstance(row, dict)}
        for log_index, log_ref in enumerate(producer_logs):
            verify_file_ref(root, log_ref, errors,
                            f"activity producer log {label}[{log_index}]")
        for artifact_index, artifact_ref in enumerate(producer_artifacts):
            verify_file_ref(root, artifact_ref, errors,
                            f"activity producer artifact {label}[{artifact_index}]")
        if any(not set(row.get("log_refs", [])).issubset(log_ids) or not row.get("log_refs")
               for row in commands if isinstance(row, dict)):
            errors.append(f"activity producer command log references invalid: {label}")
        if environment.get(contract["environment_flag"]) is not True:
            errors.append(f"activity producer environment flag missing: {label}")
        producer_time = parsed_timestamp(producer.get("recorded_at"))
        if producer_time is None:
            errors.append(f"activity producer timestamp invalid: {label}")

    review_ref = receipt.get("independent_review_ref")
    if (not isinstance(review_ref, dict)
            or set(review_ref) != {"path", "bytes", "sha256", "verdict"}
            or review_ref.get("verdict") != "PASS"
            or not review_ref.get("path", "").startswith("reviews/")):
        errors.append(f"activity independent-review reference invalid: {label}")
        review = None
    else:
        review = referenced_json(root, review_ref, errors,
                                 f"activity independent review {label}")
    review_time: datetime | None = None
    if review is not None and producer is not None:
        review_fields = {
            "schema", "review_id", "gate_id", "recorded_at", "producer_evidence_path",
            "producer_evidence_sha256", "reviewed_evidence_fingerprint",
            "governing_fingerprint", "reviewer", "independence", "verdict", "findings",
            "review_log_refs", "independent_execution_refs",
        }
        if set(review) != review_fields:
            errors.append(f"activity independent review field set invalid: {label}")
        reviewer = review.get("reviewer", {})
        if not isinstance(reviewer, dict):
            reviewer = {}
        producer_identity = producer.get("producer", {})
        if not isinstance(producer_identity, dict):
            producer_identity = {}
        independence = review.get("independence", {})
        if not isinstance(independence, dict):
            independence = {}
        if (review.get("schema") != "bass.review_attestation/v2"
                or review.get("verdict") != "PASS"
                or review.get("gate_id") != producer.get("gate_id")
                or review.get("producer_evidence_path") != producer_ref.get("path")
                or review.get("producer_evidence_sha256") != producer_ref.get("sha256")
                or review.get("reviewed_evidence_fingerprint")
                != producer.get("evidence_fingerprint")
                or reviewer.get("role") != "blocking_gate_reviewer"
                or set(reviewer) != {"run_id", "assignment_id", "lane_id", "role"}
                or any(not isinstance(reviewer.get(field), str) or not reviewer[field]
                       for field in ("run_id", "assignment_id", "lane_id"))
                or any(reviewer.get(field) == producer_identity.get(field)
                       for field in ("run_id", "assignment_id", "lane_id"))):
            errors.append(f"activity independent review identity/verdict invalid: {label}")
        if (set(independence) != {"producer_result_blinded_until_submission",
                                 "shared_code_or_oracle", "notes"}
                or independence.get("shared_code_or_oracle") is not False
                or not isinstance(independence.get("notes"), str)
                or not independence["notes"]):
            errors.append(f"activity independent review disclosure invalid: {label}")
        review_logs = review.get("review_log_refs", [])
        if not isinstance(review_logs, list) or not review_logs:
            errors.append(f"activity independent review lacks durable log: {label}")
            review_logs = []
        for log_index, log_ref in enumerate(review_logs):
            verify_file_ref(root, log_ref, errors,
                            f"activity independent review log {label}[{log_index}]")
        execution_refs = review.get("independent_execution_refs", [])
        if not isinstance(execution_refs, list):
            errors.append(f"activity independent execution refs invalid: {label}")
            execution_refs = []
        for execution_index, execution_ref in enumerate(execution_refs):
            verify_file_ref(root, execution_ref, errors,
                            f"activity independent execution {label}[{execution_index}]")
        review_time = parsed_timestamp(review.get("recorded_at"))
        if review_time is None:
            errors.append(f"activity review timestamp invalid: {label}")
    timeline = [authorization_time, occurred, producer_time, review_time]
    if all(value is not None for value in timeline) and timeline != sorted(timeline):
        errors.append(f"activity authorization/execution/review timeline invalid: {label}")


def validate_run_state_structure(root: Path, run_state: dict, scope: dict, decisions: dict,
                                 node_map: dict[str, dict], errors: list[str]) -> None:
    if set(run_state) != RUN_STATE_FIELDS or run_state.get("schema_version") != 1:
        errors.append("run-state field set/schema mismatch")
    for key in ("solver_code_present", "solver_code_executed", "solver_code_modified",
                "external_oracle_executed"):
        if type(run_state.get(key)) is not bool:
            errors.append(f"run-state boolean field invalid: {key}")
    if run_state.get("solver_code_executed") and not run_state.get("solver_code_present"):
        errors.append("run-state claims solver execution without solver code")
    if run_state.get("solver_code_modified") and not run_state.get("solver_code_present"):
        errors.append("run-state claims solver modification without solver code")
    activity_refs = run_state.get("activity_evidence_refs")
    activity_keys = set(ACTIVITY_CONTRACT)
    if not isinstance(activity_refs, dict) or set(activity_refs) != activity_keys:
        errors.append("run-state activity evidence-ref registry mismatch")
        activity_refs = {key:[] for key in activity_keys}
    for activity in sorted(activity_keys):
        refs = activity_refs.get(activity)
        if not isinstance(refs, list):
            errors.append(f"run-state activity refs are not a list: {activity}")
            refs = []
        identities: list[tuple] = []
        for index, ref in enumerate(refs):
            if not isinstance(ref, dict) or set(ref) != {"path", "bytes", "sha256"}:
                errors.append(f"run-state activity ref field set invalid: {activity}[{index}]")
                continue
            verify_file_ref(root, ref, errors, f"run-state activity {activity}[{index}]")
            identities.append((ref.get("path"), ref.get("bytes"), ref.get("sha256")))
            ref_path = safe_local_path(root, ref.get("path"))
            if (ref_path is None or not ref_path.is_file()
                    or re.fullmatch(r"receipts/activity/[A-Z0-9][A-Z0-9_.-]*\.json",
                                    ref.get("path", "")) is None):
                errors.append(f"run-state activity ref path invalid: {activity}[{index}]")
                continue
            try:
                record = json.loads(ref_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                errors.append(f"run-state activity ref is not JSON: {activity}[{index}]")
                continue
            validate_activity_receipt(root, record, activity, node_map, errors,
                                      f"{activity}[{index}]")
        if len(identities) != len(set(identities)):
            errors.append(f"run-state activity refs are duplicated: {activity}")
        if run_state.get(activity) is not bool(refs):
            errors.append(f"run-state activity flag/ref derivation mismatch: {activity}")
    registered_paths = {
        ref.get("path") for refs in activity_refs.values() if isinstance(refs, list)
        for ref in refs if isinstance(ref, dict)
    }
    activity_dir = root / "receipts/activity"
    actual_paths = ({path.relative_to(root).as_posix() for path in activity_dir.glob("*.json")
                     if path.is_file() and not path.is_symlink()}
                    if activity_dir.is_dir() else set())
    if registered_paths != actual_paths:
        errors.append("run-state activity registry does not exactly cover durable activity receipts")
    if run_state.get("artifact_status") not in ARTIFACT_STATES:
        errors.append("run-state artifact status invalid")
    if run_state.get("next_node") not in node_map:
        errors.append("run-state next node is unknown")
    if run_state.get("next_node") != run_state.get("current_node"):
        errors.append("run-state next node must equal the current actionable node")
    checkpoint = run_state.get("last_durable_checkpoint")
    if not isinstance(checkpoint, str) or re.fullmatch(r"[A-Z][A-Z0-9_]{2,95}", checkpoint) is None:
        errors.append("run-state durable checkpoint must be an uppercase machine code")
    blocker_codes = run_state.get("blocker_codes")
    if (not isinstance(blocker_codes, list) or len(blocker_codes) != len(set(blocker_codes))
            or any(not isinstance(code, str)
                   or re.fullmatch(r"[A-Z][A-Z0-9_]{2,127}", code) is None
                   for code in blocker_codes)):
        errors.append("run-state blocker codes are not unique uppercase machine codes")
        blocker_codes = []
    phase = scope.get("current_phase")
    expected_actions = RUN_ACTIONS_BY_PHASE.get(phase, set())
    action = run_state.get("resume_action")
    if action not in expected_actions:
        errors.append(f"run-state resume action is invalid for phase {phase}")
    all_resolved = decisions.get("all_resolved") is True
    if phase == "USER_SCOPE_CONFIRMATION":
        expected_user_action = ("AWAIT_EXPLICIT_CODE_READ_AUTHORIZATION" if all_resolved
                                else "RESOLVE_OWNER_DECISIONS_THEN_AWAIT_CANONICAL_CODE")
        if action != expected_user_action:
            errors.append("run-state user-scope action does not match owner-decision state")
    required_blockers: set[str] = set()
    if phase == "USER_SCOPE_CONFIRMATION":
        if all_resolved:
            required_blockers.add("CODE_READ_AUTHORIZATION_PENDING")
        else:
            required_blockers.update(
                f"{row.get('id')}_PENDING" for row in decisions.get("decisions", [])
                if row.get("status") != "RESOLVED"
            )
    if run_state.get("solver_code_present") is False and phase in {
            "USER_SCOPE_CONFIRMATION", "CODE_INTAKE_READ_ONLY"}:
        required_blockers.add("CANONICAL_SOLVER_CODE_NOT_UPLOADED")
    if phase == "IMPLEMENTATION_AUTHORIZATION":
        required_blockers.add("IMPLEMENTATION_AUTHORIZATION_PENDING")
    if phase == "OWNER_RELEASE_DECISION":
        required_blockers.add("OWNER_RELEASE_AUTHORIZATION_PENDING")
    invalidation_codes = {
        code for code in blocker_codes
        if isinstance(code, str) and code.startswith("INVALIDATION_")
    }
    expected_invalidation_codes: set[str] = set()
    if phase == "INVALIDATION_REMEDIATION":
        current_id = run_state.get("current_node")
        current_invalidation = node_map.get(current_id, {}).get("invalidation")
        if isinstance(current_invalidation, dict) and isinstance(
                current_invalidation.get("reason_code"), str):
            expected_invalidation_codes.add(
                f"INVALIDATION_{current_id}_{current_invalidation['reason_code']}")
        else:
            errors.append("remediation current node lacks a matching DAG invalidation record")
    optional = PHASE_OPTIONAL_BLOCKER_CODES.get(phase, set())
    expected_blockers = required_blockers | expected_invalidation_codes
    if (not set(blocker_codes).issubset(expected_blockers | optional)
            or not expected_blockers.issubset(set(blocker_codes))):
        errors.append("run-state blocker set is not derived from current decisions/phase")
    if action == "REMEDIATE_INVALIDATED_NODE" and invalidation_codes != expected_invalidation_codes:
        errors.append("run-state remediation action lacks an invalidation blocker")
    if any(code.startswith("INVALIDATION_") and re.fullmatch(
            r"INVALIDATION_(?:H0|H1|OD0|C(?:[0-9]|10)|IA0|TERMINAL)_[A-Z][A-Z0-9_]{2,63}",
            code) is None for code in invalidation_codes):
        errors.append("run-state invalidation blocker code is malformed")
    latest_pass = next((node_id for node_id in reversed(list(node_map))
                        if node_map[node_id].get("status") == "PASS"), None)
    expected_checkpoint = CHECKPOINT_BY_NODE.get(latest_pass, "NO_DURABLE_CHECKPOINT")
    if run_state.get("last_durable_checkpoint") != expected_checkpoint:
        errors.append("run-state checkpoint does not match the latest PASS node")
    expected_artifact_status = ("DURABLE_UNVERIFIED" if action == "REMEDIATE_INVALIDATED_NODE"
                                else "DURABLE_VERIFIED")
    if run_state.get("artifact_status") != expected_artifact_status:
        errors.append("run-state artifact status is not derived from remediation state")


def validate_family_and_high_ell(family: dict, high_ell: dict, science: dict,
                                 claim_map: dict[str, dict], errors: list[str]) -> None:
    canonical = ["I","II","III","IV","V","VI_0","VI_h","VII_0","VII_h","VIII","IX"]
    if family.get("canonical_family_ids") != canonical or science.get("target_families") != canonical:
        errors.append("canonical 11-family registry mismatch")
    rows = family.get("families", [])
    row_map = {row.get("id"): row for row in rows}
    if len(row_map) != 11:
        errors.append("family registry must contain 11 unique canonical rows")
        return
    expected_a = {"I","II","VI_0","VII_0","VIII","IX"}
    if {key for key, row in row_map.items() if row.get("class") == "A"} != expected_a:
        errors.append("class-A family map mismatch")
    convention = family.get("h_convention", {})
    if convention.get("relation") != "aB_sq=h*n2*n3" or convention.get("exact_rational_special_dispatch") is not True:
        errors.append("machine-readable Bianchi h convention/dispatch missing")
    vi_h = row_map.get("VI_h", {}).get("h", {})
    excluded_exact = vi_h.get("excluded_exact", [])
    if vi_h.get("upper") != {"numerator":0,"denominator":1} or {
        (row.get("numerator"), row.get("denominator")) for row in excluded_exact
    } != {(-1, 1), (-1, 9)}:
        errors.append("VI_h domain/alias/exceptional exclusions mismatch")
    vii_h = row_map.get("VII_h", {}).get("h", {})
    if vii_h.get("lower") != {"numerator":0,"denominator":1} or vii_h.get("lower_open") is not True:
        errors.append("VII_h domain must be h>0")
    for row in rows:
        if row.get("claim_id") not in claim_map:
            errors.append(f"family registry references missing claim: {row.get('id')}")
    exceptional = family.get("exceptional_branches", [])
    if (len(exceptional) != 1 or exceptional[0].get("h") != {"numerator":-1,"denominator":9}
            or exceptional[0].get("parent_family") != "VI_h"
            or exceptional[0].get("claim_id") != "CLM-FAMILY-VI-MINUS-1-9"
            or set(exceptional[0].get("required_criterion_ids", []))
            != FAMILY_LEAF_CRITERIA["CLM-FAMILY-VI-MINUS-1-9"]
            or exceptional[0].get("exact_branch_tag_required") is not True
            or exceptional[0].get("required_for_parent_claim") is not True):
        errors.append("VI_-1/9 exceptional branch is not exact/machine-readable")
    allocation = high_ell.get("allocation_contract", {})
    norms = high_ell.get("norm_contract", {})
    expected_allocation = {
        "retained_bulk_symbol":"L_keep", "closure_guard_symbol":"G",
        "allocated_max_symbol":"L_alloc", "allocated_max_rule":"L_alloc=L_keep+G",
        "structural_guard_minimum_rule":"G>=2*max_abs_operator_delta_ell",
        "structural_minimum_is_not_convergence_evidence":True,
        "closure_applied_only_at":"L_alloc", "production_outputs_must_satisfy":"ell<=L_keep",
        "minimum_allocation_levels":3, "common_bulk_projection_required":True,
    }
    expected_norms = {
        "basis":"canonical_orthonormal_spin_weighted_harmonics",
        "hybrid_test":"error<=atol+rtol*reference_scale",
        "required_bulk_norms":["parseval_weighted_l2","componentwise_linf","per_ell_l2_profile"],
        "required_guard_diagnostics":["guard_to_total_l2","outermost_shell_to_guard_l2",
                                      "bulk_delta_profile_under_allocation_refinement",
                                      "closure_reflection_indicator"],
        "guard_coefficients_excluded_from_bulk_norm":True,
        "cross_species_or_cross_spin_aggregation_forbidden":True,
        "pass_operator":"ALL_ENABLED_ROWS",
    }
    if allocation != expected_allocation:
        errors.append("high-ell allocation/refinement contract differs from the immutable v1 harness floor")
    if norms != expected_norms:
        errors.append("high-ell norm/aggregation contract differs from the immutable v1 harness floor")
    high_rows = high_ell.get("channel_rows", [])
    row_map = {row.get("id"): row for row in high_rows}
    if len(row_map) != len(high_rows) or row_map != HIGH_ELL_ROW_CONTRACT:
        errors.append("high-ell channel-row semantics differ from the immutable v1 contract")


def validate_owner_receipt(root: Path, decisions: dict, errors: list[str]) -> None:
    if decisions.get("all_resolved") is not True:
        return
    ref = decisions.get("owner_receipt")
    if not isinstance(ref, dict) or set(ref) != {"path", "bytes", "sha256"}:
        errors.append("owner receipt must be an exact path/bytes/sha256 file reference")
        return
    if ref.get("path") != OD0_OWNER_RECEIPT_PATH:
        errors.append("owner decision receipt path is not the reserved OD0 path")
    verify_file_ref(root, ref, errors, "owner decision receipt")
    path = safe_local_path(root, ref.get("path"))
    if path is None or not path.is_file() or path.is_symlink():
        return
    try:
        receipt = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        errors.append("owner decision receipt is not valid JSON")
        return
    snapshot = [
        {key: row.get(key) for key in ("id", "decision_type", "status", "value")}
        for row in sorted(decisions.get("decisions", []), key=lambda item: item.get("id", ""))
    ]
    required_receipt_fields = {"schema", "receipt_id", "issued_at", "decision_ids",
                               "decision_snapshot_sha256", "owner_confirmation", "scope"}
    if set(receipt) != required_receipt_fields:
        errors.append("owner decision receipt field set invalid")
    if receipt.get("schema") != "bass.owner_decision_receipt/v1":
        errors.append("owner decision receipt schema invalid")
    if not isinstance(receipt.get("receipt_id"), str) or not receipt["receipt_id"]:
        errors.append("owner decision receipt ID missing")
    if not valid_timestamp(receipt.get("issued_at")):
        errors.append("owner decision receipt timestamp invalid")
    if receipt.get("decision_ids") != ["OD001", "OD002", "OD003", "OD004"]:
        errors.append("owner decision receipt decision set mismatch")
    if receipt.get("decision_snapshot_sha256") != canonical_hash(snapshot):
        errors.append("owner decision receipt snapshot hash mismatch")
    if receipt.get("owner_confirmation") != "EXPLICIT":
        errors.append("owner decision receipt lacks explicit confirmation")
    if receipt.get("scope") != "OD001-OD004 decisions only; no code read/write/build/execute/install authorization":
        errors.append("owner decision receipt scope exceeds decision confirmation")


def validate_code_read_authorization(root: Path, decisions: dict, scope: dict,
                                     errors: list[str]) -> None:
    path = root / OD0_CODE_READ_AUTHORIZATION_PATH
    code_read = scope.get("authorizations", {}).get("code_read") is True
    if not code_read:
        historical_od0_present = any(
            (root / relative).exists()
            for relative in OD0_PASS_PATHS - {OD0_CODE_READ_AUTHORIZATION_PATH}
        )
        if path.exists() and not (
                scope.get("current_phase") == "INVALIDATION_REMEDIATION"
                and decisions.get("all_resolved") is True):
            errors.append("code-read authorization record present while code_read=false")
            return
        if (historical_od0_present and scope.get("current_phase") == "INVALIDATION_REMEDIATION"
                and not path.exists()):
            errors.append("historical OD0 graph lacks its code-read authorization record")
            return
        if not path.exists():
            return
    if decisions.get("all_resolved") is not True:
        errors.append("code-read authorization requires resolved owner decisions")
    if not path.is_file() or path.is_symlink():
        errors.append("code_read=true requires the reserved code-read authorization record")
        return
    try:
        authorization = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        errors.append("code-read authorization record is not valid JSON")
        return
    expected_fields = {
        "schema", "authorization_id", "issued_at", "action", "granted",
        "owner_decision_receipt_sha256", "owner_confirmation", "scope",
    }
    if set(authorization) != expected_fields:
        errors.append("code-read authorization field set invalid")
    if authorization.get("schema") != "bass.code_read_authorization/v1":
        errors.append("code-read authorization schema invalid")
    if not isinstance(authorization.get("authorization_id"), str) or not authorization["authorization_id"]:
        errors.append("code-read authorization ID missing")
    if not valid_timestamp(authorization.get("issued_at")):
        errors.append("code-read authorization timestamp invalid")
    if authorization.get("action") != "READ_CANONICAL_SOLVER_CODE" or authorization.get("granted") is not True:
        errors.append("code-read authorization action/grant invalid")
    owner_path = root / OD0_OWNER_RECEIPT_PATH
    if (not owner_path.is_file() or owner_path.is_symlink()
            or authorization.get("owner_decision_receipt_sha256") != file_hash(owner_path)):
        errors.append("code-read authorization is not bound to the current owner-decision receipt")
    if authorization.get("owner_confirmation") != "EXPLICIT":
        errors.append("code-read authorization lacks explicit owner confirmation")
    if authorization.get("scope") != (
            "Read canonical solver code only; no write/build/execute/install/remote authorization"):
        errors.append("code-read authorization exceeds read-only intake scope")


def validate_sector_registry(decisions: dict, science: dict, high_ell: dict,
                             claim_map: dict[str, dict], gate_map: dict[str, dict],
                             errors: list[str]) -> None:
    registry = science.get("sector_registry", {})
    decision_map = {row.get("id"): row for row in decisions.get("decisions", [])}
    od2 = decision_map.get("OD002", {})
    if set(registry) != OD002_SECTOR_KEYS or set(od2.get("required_keys", [])) != set(registry):
        errors.append("OD002 key set and scientific sector registry differ")
        return
    high_rows = {row.get("id"): row for row in high_ell.get("channel_rows", [])}
    conditional_claims: dict[str, set[str]] = {key:set() for key in registry}
    for claim_id, claim in claim_map.items():
        sector = claim.get("conditional_sector")
        if sector is not None:
            if sector not in registry:
                errors.append(f"claim references unknown conditional sector: {claim_id}")
            else:
                conditional_claims[sector].add(claim_id)
    actual_bindings: dict[str, set[tuple[str, str]]] = {key:set() for key in registry}
    for gate_id, gate in gate_map.items():
        for criterion in gate.get("requires", []):
            condition = criterion.get("applies_if")
            if condition is None:
                continue
            if (set(condition) != {"decision_id", "sector_key", "equals"}
                    or condition.get("decision_id") != "OD002"
                    or condition.get("equals") is not True
                    or condition.get("sector_key") not in registry):
                errors.append(f"conditional gate criterion is malformed: {criterion.get('id')}")
                continue
            actual_bindings[condition["sector_key"]].add((gate_id, criterion.get("id")))
    for key, row in registry.items():
        expected_claims, expected_bindings, expected_channels = SECTOR_CONTRACT[key]
        if row.get("decision_id") != "OD002":
            errors.append(f"sector registry decision binding mismatch: {key}")
        if set(row.get("claim_ids", [])) != expected_claims:
            errors.append(f"sector registry differs from immutable claim contract: {key}")
        if conditional_claims[key] != expected_claims:
            errors.append(f"sector registry claim binding mismatch: {key}")
        declared_bindings: set[tuple[str, str]] = set()
        for binding in row.get("gate_bindings", []):
            gate_id = binding.get("gate_id")
            for criterion_id in binding.get("criterion_ids", []):
                declared_bindings.add((gate_id, criterion_id))
        if declared_bindings != expected_bindings or actual_bindings[key] != expected_bindings:
            errors.append(f"sector registry gate/criterion binding mismatch: {key}")
        declared_channels = set(row.get("high_ell_channel_ids", []))
        actual_channels = {channel_id for channel_id, channel in high_rows.items()
                           if channel.get("sector_key") == key}
        if declared_channels != expected_channels or actual_channels != expected_channels:
            errors.append(f"sector registry high-ell channel binding mismatch: {key}")
    effects = science.get("conditional_sector_effects", {})
    if (effects.get("false", {}).get("leaf_claim_status") != "LOCKED_OUT_OF_SCOPE"
            or effects.get("false", {}).get("leaf_claim_value") is not False
            or effects.get("true_before_evidence", {}).get("leaf_claim_status")
            != "LOCKED_PENDING_EVIDENCE"):
        errors.append("conditional sector effect contract is incomplete")
    if od2.get("status") == "PENDING_OWNER":
        for claim_ids in conditional_claims.values():
            for claim_id in claim_ids:
                claim = claim_map[claim_id]
                if (claim.get("status") != "LOCKED_PENDING_EVIDENCE"
                        or claim.get("value") is not None or claim.get("evidence_ids") != []):
                    errors.append(f"pending OD002 sector claim is not locked: {claim_id}")
    elif od2.get("status") == "RESOLVED" and isinstance(od2.get("value"), dict):
        for key, claim_ids in conditional_claims.items():
            enabled = od2["value"].get(key)
            for claim_id in claim_ids:
                claim = claim_map[claim_id]
                if enabled is False and (claim.get("status") != "LOCKED_OUT_OF_SCOPE"
                                         or claim.get("value") is not False
                                         or claim.get("evidence_ids") != []):
                    errors.append(f"disabled sector claim is not locked out: {claim_id}")
                if enabled is True and claim.get("status") == "LOCKED_OUT_OF_SCOPE":
                    errors.append(f"enabled sector claim is incorrectly out of scope: {claim_id}")
    neutrino = science.get("neutrino_scope", {})
    nu_row = high_rows.get("massless_neutrinos", {})
    nu_claims = [claim_map.get("CLM-HIGH-ELL-MASSLESS-NEUTRINOS", {}),
                 claim_map.get("CLM-MASSLESS-NEUTRINO-RUNTIME", {})]
    if (neutrino.get("decision_key") != "massless_neutrinos"
            or neutrino.get("mass") != "exact_zero" or neutrino.get("mass_shell") != "p^a p_a=0"
            or neutrino.get("kinetic_regime") != "collisionless"
            or neutrino.get("massive_neutrino_transport") != "OUT_OF_SCOPE_V1"
            or nu_row.get("mass_assumption") != "m_nu=0_exact"
            or nu_row.get("collision_model") != "collisionless"
            or any(claim.get("species_scope") != "massless_only" for claim in nu_claims)):
        errors.append("massless collisionless-neutrino scope is not exact across contracts")


def validate_claim_criterion_bindings(family: dict, claim_map: dict[str, dict],
                                      gate_map: dict[str, dict], errors: list[str]) -> None:
    gate_criteria = {gate_id:{row.get("id") for row in gate.get("requires", [])}
                     for gate_id, gate in gate_map.items()}
    for claim_id, claim in claim_map.items():
        required = claim.get("required_criterion_ids", [])
        if len(required) != len(set(required)):
            errors.append(f"claim has duplicate required criteria: {claim_id}")
        gate_id = claim.get("gate")
        if required and not set(required).issubset(gate_criteria.get(gate_id, set())):
            errors.append(f"claim required criteria are absent from its gate: {claim_id}")
    expected_family_claims = {
        "I":"CLM-FAMILY-I", "II":"CLM-FAMILY-II", "III":"CLM-FAMILY-III",
        "IV":"CLM-FAMILY-IV", "V":"CLM-FAMILY-V", "VI_0":"CLM-FAMILY-VI-0",
        "VI_h":"CLM-FAMILY-VI-H", "VII_0":"CLM-FAMILY-VII-0",
        "VII_h":"CLM-FAMILY-VII-H", "VIII":"CLM-FAMILY-VIII", "IX":"CLM-FAMILY-IX",
    }
    expected_family_union = set().union(*FAMILY_LEAF_CRITERIA.values())
    for row in family.get("families", []):
        claim_id = row.get("claim_id")
        required = set(row.get("required_criterion_ids", []))
        expected_required = (FAMILY_LEAF_CRITERIA[claim_id] if claim_id in FAMILY_LEAF_CRITERIA
                             else FAMILY_LEAF_CRITERIA["CLM-FAMILY-VI-H-GENERIC"]
                             | FAMILY_LEAF_CRITERIA["CLM-FAMILY-VI-MINUS-1-9"])
        if expected_family_claims.get(row.get("id")) != claim_id or required != expected_required:
            errors.append(f"family registry differs from immutable criteria: {row.get('id')}")
        if set(claim_map.get(claim_id, {}).get("required_criterion_ids", [])) != expected_required:
            errors.append(f"family registry/claim criterion mismatch: {row.get('id')}")
        leaf_rows = row.get("leaf_claim_contracts", [])
        if row.get("id") == "VI_h" and {leaf.get("claim_id") for leaf in leaf_rows} != {
                "CLM-FAMILY-VI-H-GENERIC", "CLM-FAMILY-VI-MINUS-1-9"}:
            errors.append("VI_h leaf-claim contract set is incomplete")
        for leaf in leaf_rows:
            leaf_required = set(leaf.get("required_criterion_ids", []))
            expected_leaf = FAMILY_LEAF_CRITERIA.get(leaf.get("claim_id"), set())
            if (leaf_required != expected_leaf
                    or set(claim_map.get(leaf.get("claim_id"), {}).get("required_criterion_ids", []))
                    != expected_leaf):
                errors.append(f"family leaf criterion mismatch: {leaf.get('claim_id')}")
    actual_family = {criterion for criterion in gate_criteria.get("G-C3", set())
                     if criterion.startswith("G-C3-FAM-")}
    if actual_family != expected_family_union:
        errors.append("G-C3 family criterion set does not equal family-registry union")


def expected_criterion_statuses(gate: dict, decisions: dict,
                                errors: list[str]) -> dict[str, str]:
    decision_map = {row.get("id"): row for row in decisions.get("decisions", [])}
    statuses: dict[str, str] = {}
    for criterion in gate.get("requires", []):
        criterion_id = criterion.get("id")
        condition = criterion.get("applies_if")
        if condition is None:
            statuses[criterion_id] = "PASS"
            continue
        decision = decision_map.get(condition.get("decision_id"), {})
        if decision.get("status") != "RESOLVED" or not isinstance(decision.get("value"), dict):
            errors.append(f"PASS gate has unresolved conditional criterion: {criterion_id}")
            statuses[criterion_id] = "UNRESOLVED"
            continue
        selected = decision["value"].get(condition.get("sector_key"))
        statuses[criterion_id] = "PASS" if selected is condition.get("equals") else "NOT_APPLICABLE"
    return statuses


def validate_static_log(root: Path, static_log: dict, mode: str,
                        expected_governing: dict, errors: list[str], label: str) -> None:
    expected_fields = {
        "schema", "mode", "started_at", "ended_at", "pre_execution_governing",
        "post_execution_governing", "governing_snapshot_stable", "execution_context",
        "command_plan_fingerprint", "commands", "all_passed",
    }
    if not isinstance(static_log, dict) or set(static_log) != expected_fields:
        errors.append(f"{label} field set mismatch")
        return
    if (static_log.get("schema") != "bass.static_check_log/v2"
            or static_log.get("mode") != mode
            or static_log.get("all_passed") is not True
            or static_log.get("governing_snapshot_stable") is not True):
        errors.append(f"{label} mode/status mismatch")
    log_started = parsed_timestamp(static_log.get("started_at"))
    log_ended = parsed_timestamp(static_log.get("ended_at"))
    if log_started is None or log_ended is None or log_started > log_ended:
        errors.append(f"{label} timestamps invalid")
    if (static_log.get("pre_execution_governing") != expected_governing
            or static_log.get("post_execution_governing") != expected_governing):
        errors.append(f"{label} tested stale governing bytes")
    context = static_log.get("execution_context")
    context_fields = {
        "harness_root", "workspace_root", "temporary_root", "python_executable",
    }
    context_valid = isinstance(context, dict) and set(context) == context_fields
    if context_valid:
        harness_text = context.get("harness_root")
        workspace_text = context.get("workspace_root")
        python_text = context.get("python_executable")
        if (not all(isinstance(value, str) and value and "\x00" not in value
                    for value in (harness_text, workspace_text, python_text))
                or not Path(harness_text).is_absolute()
                or not Path(workspace_text).is_absolute()
                or Path(harness_text).parent != Path(workspace_text)
                or Path(harness_text).resolve() != root.resolve()
                or Path(workspace_text).resolve() != root.parent.resolve()
                or not Path(python_text).is_absolute()
                or re.fullmatch(r"python(?:3(?:\.[0-9]+)?)?", Path(python_text).name) is None
                or Path(python_text).resolve() != Path(sys.executable).resolve()):
            context_valid = False
        temporary_text = context.get("temporary_root")
        if mode == "H0":
            if (not isinstance(temporary_text, str) or not Path(temporary_text).is_absolute()
                    or not Path(temporary_text).name.startswith("bass-h0-static-")
                    or Path(temporary_text) == Path(harness_text)):
                context_valid = False
        elif temporary_text is not None:
            context_valid = False
    if not context_valid:
        errors.append(f"{label} execution context invalid")
        return
    try:
        plan = expected_command_plan(mode, context)
    except (KeyError, TypeError, ValueError):
        errors.append(f"{label} command plan cannot be reconstructed")
        return
    if static_log.get("command_plan_fingerprint") != command_plan_fingerprint(plan):
        errors.append(f"{label} command-plan fingerprint mismatch")
    commands = static_log.get("commands")
    if not isinstance(commands, list) or len(commands) != len(plan):
        errors.append(f"{label} command count mismatch")
        return
    command_fields = {
        "id", "argv", "cwd", "started_at", "ended_at", "exit_code", "timed_out",
        "signal", "skipped", "fallback_used", "stdout", "stderr", "result",
    }
    previous_command_ended = log_started
    for expected, command in zip(plan, commands):
        command_id = command.get("id") if isinstance(command, dict) else None
        if not isinstance(command, dict) or set(command) != command_fields:
            errors.append(f"{label} command field set invalid: {command_id}")
            continue
        if ({key:command.get(key) for key in ("id", "argv", "cwd")} != expected):
            errors.append(f"{label} command differs from canonical plan: {command_id}")
        if (command.get("exit_code") != 0 or command.get("timed_out") is not False
                or command.get("signal") is not None or command.get("skipped") is not False
                or command.get("fallback_used") is not False or command.get("result") != "PASS"):
            errors.append(f"{label} command is not clean PASS: {command_id}")
        command_started = parsed_timestamp(command.get("started_at"))
        command_ended = parsed_timestamp(command.get("ended_at"))
        if (command_started is None or command_ended is None
                or command_started > command_ended
                or (log_started is not None and command_started < log_started)
                or (log_ended is not None and command_ended > log_ended)
                or (previous_command_ended is not None
                    and command_started is not None
                    and command_started < previous_command_ended)):
            errors.append(f"{label} command timestamps invalid: {command_id}")
        if command_ended is not None:
            previous_command_ended = command_ended
        if not isinstance(command.get("stdout"), str) or not isinstance(command.get("stderr"), str):
            errors.append(f"{label} command output fields invalid: {command_id}")
    by_id = {row.get("id"):row for row in commands if isinstance(row, dict)}
    if len(by_id) != len(commands):
        errors.append(f"{label} command IDs duplicated")
        return
    if set(by_id) != {row["id"] for row in plan}:
        errors.append(f"{label} command ID set mismatch")
        return
    if mode == "H0":
        try:
            inventory_items = sorted(load_json(root, "audit/INPUT_INVENTORY.json")["items"],
                                     key=lambda row:row["id"])
        except (KeyError, OSError, json.JSONDecodeError):
            errors.append(f"{label} cannot load the H0 inventory semantic oracle")
            return
        hash_plan = plan[0]["argv"][1:]
        expected_hash_stdout = "".join(
            f"{row['sha256']}  {path}\n" for row, path in zip(inventory_items, hash_plan)
        )
        if (len(inventory_items) != len(SOURCE_NAMES)
                or by_id["CMD-H0-001"].get("stdout") != expected_hash_stdout
                or by_id["CMD-H0-001"].get("stderr") != ""):
            errors.append(f"{label} H0 source-hash output mismatch")
        archive_inventory_indexes = (0, 1, 11, 12)
        for command_number, inventory_index in enumerate(archive_inventory_indexes, 2):
            command = by_id[f"CMD-H0-{command_number:03d}"]
            try:
                archive = json.loads(command.get("stdout", ""))
            except json.JSONDecodeError:
                errors.append(f"{label} archive-audit output is not JSON: CMD-H0-{command_number:03d}")
                continue
            inventory_row = inventory_items[inventory_index]
            expected_archive_fields = {
                "archive", "bytes", "entries", "expanded_bytes", "format", "issues",
                "schema_version", "sha256", "status",
            }
            if (set(archive) != expected_archive_fields or archive.get("schema_version") != 1
                    or archive.get("archive") != plan[command_number - 1]["argv"][-1]
                    or archive.get("bytes") != inventory_row.get("bytes")
                    or archive.get("sha256") != inventory_row.get("sha256")
                    or not isinstance(archive.get("entries"), int) or archive["entries"] <= 0
                    or not isinstance(archive.get("expanded_bytes"), int)
                    or archive["expanded_bytes"] <= 0 or archive.get("issues") != []
                    or archive.get("status") != "PASS" or command.get("stderr") != ""):
                errors.append(f"{label} archive-audit semantic mismatch: CMD-H0-{command_number:03d}")
        expected_commit = ORACLE_PIN
        expected_rust_hash = "294b3d81fa72e62581276290c60c81eb8b58498d333d422ca1dfc432877d0c40"
        expected_key = "108F66205EAEB0AAA8DD5E1C85AB96E6FA1BE5FE"
        expected_tree = "7f155a4c815495c519f30d78ea8682bf3e3b0162"
        if by_id["CMD-H0-008"].get("stdout") != expected_commit + "\n":
            errors.append(f"{label} pinned local repository commit mismatch")
        if by_id["CMD-H0-009"].get("stdout") != "":
            errors.append(f"{label} local repository is not clean")
        if by_id["CMD-H0-010"].get("stdout") != (
                expected_rust_hash + "  rust-1.94.1-x86_64-unknown-linux-gnu.tar.xz\n"):
            errors.append(f"{label} official Rust hash output mismatch")
        if expected_key not in by_id["CMD-H0-015"].get("stdout", "").replace(":", ""):
            errors.append(f"{label} Rust release-key fingerprint output mismatch")
        signature_stderr = by_id["CMD-H0-016"].get("stderr", "")
        if "Good signature" not in signature_stderr or "85AB96E6FA1BE5FE" not in signature_stderr:
            errors.append(f"{label} Rust detached-signature output mismatch")
        if by_id["CMD-H0-017"].get("stdout") != (
                "https://github.com/cosmosapjw-quantum/bianchi_phase_r.git\n"):
            errors.append(f"{label} repository-origin output mismatch")
        if by_id["CMD-H0-018"].get("stdout") != expected_tree + "\n":
            errors.append(f"{label} repository-tree output mismatch")
        if by_id["CMD-H0-019"].get("stdout") != (
                f"{expected_commit}\tHEAD\n{expected_commit}\trefs/heads/main\n"):
            errors.append(f"{label} remote repository pin output mismatch")
        for command_id in ("CMD-H0-006", "CMD-H0-007", "CMD-H0-011",
                           "CMD-H0-012", "CMD-H0-013", "CMD-H0-014"):
            if by_id[command_id].get("stdout") != "" or by_id[command_id].get("stderr") != "":
                errors.append(f"{label} unexpected output from quiet command: {command_id}")
    else:
        if (by_id["CMD-H1-001"].get("stdout") != ""
                or by_id["CMD-H1-001"].get("stderr") != ""
                or by_id["CMD-H1-003"].get("stdout") != ""
                or by_id["CMD-H1-003"].get("stderr") != ""):
            errors.append(f"{label} H1 compile/portability output is not clean")
        test_output = by_id["CMD-H1-002"].get("stderr", "")
        if (by_id["CMD-H1-002"].get("stdout") != ""
                or any(test_name not in test_output for test_name in H1_TESTS)
                or test_output.count(" ... ok\n") != len(H1_TESTS)
                or f"Ran {len(H1_TESTS)} tests" not in test_output
                or not test_output.rstrip().endswith("OK")):
            errors.append(f"{label} H1 unittest semantic output mismatch")


def validate_evidence(root: Path, evidence_path: str, expected_node: str,
                      expected_gate: str, expected_governing: dict,
                      evidence_contract: dict,
                      expected_criteria: dict[str, str], expected_obligations: set[str],
                      dependency_rows: list[dict], inventory_map: dict[str, dict],
                      errors: list[str]) -> dict | None:
    path = safe_local_path(root, evidence_path)
    if path is None or not path.is_file() or path.is_symlink():
        errors.append(f"producer evidence missing/not regular: {evidence_path}")
        return None
    try:
        evidence = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        errors.append(f"producer evidence is not valid JSON: {evidence_path}")
        return None
    required = {"schema","evidence_id","node_id","gate_id","recorded_at","producer",
                "governing","dependencies","inputs","environment","execution","logs",
                "artifacts","criterion_results","obligation_results","claim_effects",
                "claim_boundary","evidence_fingerprint"}
    missing = required - set(evidence)
    extra = set(evidence) - required
    if missing or extra:
        errors.append(f"producer evidence field set mismatch missing={sorted(missing)} extra={sorted(extra)}: {evidence_path}")
    if missing:
        return evidence
    if evidence.get("schema") != "bass.producer_evidence/v2":
        errors.append(f"legacy/unknown producer evidence schema: {evidence_path}")
    if evidence.get("node_id") != expected_node or evidence.get("gate_id") != expected_gate:
        errors.append(f"producer evidence node/gate mismatch: {evidence_path}")
    if not valid_timestamp(evidence.get("recorded_at")):
        errors.append(f"producer evidence timestamp invalid: {evidence_path}")
    producer = evidence.get("producer", {})
    for field in ("run_id", "assignment_id", "lane_id", "role"):
        if not isinstance(producer.get(field), str) or not producer[field]:
            errors.append(f"producer identity field missing {field}: {evidence_path}")
    governing = evidence.get("governing", {})
    if governing != expected_governing:
        errors.append(f"stale governing fingerprint for PASS node {expected_node}")
    stored_core = {key: governing.get(key) for key in (
        "algorithm", "files", "live_file_projections", "gate_projection", "node_projection"
    )}
    if governing.get("fingerprint") != canonical_hash(stored_core):
        errors.append(f"producer governing fingerprint is internally invalid: {evidence_path}")
    expected_deps = {
        (row["node_id"], row["path"], row["sha256"], row["governing_fingerprint"])
        for row in dependency_rows
    }
    actual_deps = {
        (row.get("node_id"), row.get("path"), row.get("sha256"), row.get("governing_fingerprint"))
        for row in evidence.get("dependencies", []) if isinstance(row, dict)
    }
    if actual_deps != expected_deps:
        errors.append(f"producer dependency receipt set mismatch: {evidence_path}")
    inputs = evidence.get("inputs", {})
    local_source_ids: set[str] = set()
    for index, ref in enumerate(inputs.get("local", [])):
        retention = ref.get("retention")
        if retention == "EMBEDDED":
            verify_file_ref(root, ref, errors, f"producer local input {index}")
        elif retention == "AUDIT_SOURCE_NOT_BUNDLED":
            source_id = ref.get("source_id")
            local_source_ids.add(source_id)
            source = inventory_map.get(source_id, {})
            if ref.get("sha256") != source.get("sha256") or ref.get("bytes") != source.get("bytes"):
                errors.append(f"historical input/inventory mismatch: {source_id}")
            if ref.get("runtime_use") is not False:
                errors.append(f"non-bundled historical input may not be a runtime input: {source_id}")
        else:
            errors.append(f"unknown producer input retention: {retention}")
    if expected_node == "H0" and local_source_ids != set(inventory_map):
        errors.append("H0 historical input set is not exactly SRC01..SRC13")
    embedded_path_rows = [row.get("path") for row in inputs.get("local", [])
                          if row.get("retention") == "EMBEDDED"]
    if len(embedded_path_rows) != len(set(embedded_path_rows)):
        errors.append(f"producer embedded input paths are duplicated: {evidence_path}")
    if expected_node == "H1":
        if set(embedded_path_rows) != {row.get("path") for row in expected_governing.get("files", [])}:
            errors.append("H1 embedded input set does not equal governing-file set")
    elif expected_node == "OD0":
        expected_inputs = set(evidence_contract["node_profiles"]["OD0"]["producer_input_files"])
        if set(embedded_path_rows) != expected_inputs or len(embedded_path_rows) != len(expected_inputs):
            errors.append("OD0 embedded input set does not equal the exact decision/authorization set")
    artifact_ids = {row.get("id") for row in evidence.get("artifacts", [])}
    log_ids = {row.get("id") for row in evidence.get("logs", [])}
    for index, ref in enumerate(evidence.get("logs", [])):
        verify_file_ref(root, ref, errors, f"producer log {index}")
        if ref.get("nonempty_required") is True:
            path_ref = safe_local_path(root, ref.get("path"))
            if path_ref is not None and path_ref.is_file() and path_ref.stat().st_size == 0:
                errors.append(f"required producer log is empty: {ref.get('path')}")
    for index, ref in enumerate(evidence.get("artifacts", [])):
        verify_file_ref(root, ref, errors, f"producer artifact {index}")
        if ref.get("state") != "DURABLE_VERIFIED":
            errors.append(f"producer artifact is not durable verified: {ref.get('path')}")
    if expected_node == "OD0":
        expected_artifacts = {
            "ART-OD0-DECISIONS":"contracts/owner_decisions.json",
            "ART-OD0-OWNER":OD0_OWNER_RECEIPT_PATH,
            "ART-OD0-READ-AUTH":OD0_CODE_READ_AUTHORIZATION_PATH,
        }
        actual_artifacts = {row.get("id"):row.get("path") for row in evidence.get("artifacts", [])}
        if actual_artifacts != expected_artifacts or len(evidence.get("artifacts", [])) != len(expected_artifacts):
            errors.append("OD0 artifact set is not the exact decision/authorization set")
    environment = evidence.get("environment", {})
    if environment.get("fingerprint") != canonical_hash(environment.get("details", {})):
        errors.append(f"environment fingerprint mismatch: {evidence_path}")
    execution = evidence.get("execution", {})
    commands = execution.get("commands", [])
    expected_execution_mode = "NO_EXECUTION" if expected_node == "OD0" else "STATIC_AUDIT_COMMANDS"
    if execution.get("mode") != expected_execution_mode:
        errors.append(f"producer execution mode mismatch: {evidence_path}")
    if expected_execution_mode == "NO_EXECUTION" and commands:
        errors.append(f"NO_EXECUTION evidence contains commands: {evidence_path}")
    if expected_execution_mode == "STATIC_AUDIT_COMMANDS" and not commands:
        errors.append(f"command evidence contains no commands: {evidence_path}")
    for command in commands:
        if (not isinstance(command.get("argv"), list) or not command.get("argv")
                or command.get("exit_code") != 0 or command.get("timed_out") is not False
                or command.get("signal") is not None or command.get("skipped") is not False
                or command.get("fallback_used") is not False or command.get("result") != "PASS"):
            errors.append(f"producer command is not clean PASS: {command.get('id')}")
        if not valid_timestamp(command.get("started_at")) or not valid_timestamp(command.get("ended_at")):
            errors.append(f"producer command timestamps invalid: {command.get('id')}")
        refs = command.get("log_refs", [])
        if not refs or not set(refs).issubset(log_ids):
            errors.append(f"producer command log references invalid: {command.get('id')}")
    expected_command_ids = ({f"CMD-H0-{index:03d}" for index in range(1, 20)}
                            if expected_node == "H0" else
                            ({f"CMD-H1-{index:03d}" for index in range(1, 4)}
                             if expected_node == "H1" else set()))
    if {row.get("id") for row in commands} != expected_command_ids or len(commands) != len(expected_command_ids):
        errors.append(f"producer command ID set mismatch: {evidence_path}")
    static_log_paths = {row.get("path") for row in evidence.get("logs", [])}
    expected_log_ids = ({"LOG-H0-HASH","LOG-H0-ARCHIVE","LOG-H0-RUST","LOG-H0-REPO"}
                        if expected_node == "H0" else
                        ({"LOG-H1-STATIC"} if expected_node == "H1" else set()))
    if log_ids != expected_log_ids or len(evidence.get("logs", [])) != len(expected_log_ids):
        errors.append(f"producer log ID set mismatch: {evidence_path}")
    if expected_node == "OD0":
        if static_log_paths:
            errors.append(f"OD0 no-execution evidence contains a static log: {evidence_path}")
    elif (len(static_log_paths) != 1
          or static_log_paths != {f"audit/logs/{expected_node}_STATIC_CHECKS.json"}):
        errors.append(f"producer static log path set mismatch: {evidence_path}")
    else:
        static_path = safe_local_path(root, next(iter(static_log_paths)))
        if static_path is not None and static_path.is_file():
            try:
                static_log = json.loads(static_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                errors.append(f"producer static log is not JSON: {evidence_path}")
            else:
                validate_static_log(root, static_log, expected_node, expected_governing,
                                    errors, f"producer static log {evidence_path}")
                static_ended = parsed_timestamp(static_log.get("ended_at"))
                evidence_recorded = parsed_timestamp(evidence.get("recorded_at"))
                if (static_ended is not None and evidence_recorded is not None
                        and static_ended > evidence_recorded):
                    errors.append(f"producer evidence predates its static execution: {evidence_path}")
                static_commands = static_log.get("commands", [])
                if not isinstance(static_commands, list):
                    static_commands = []
                log_command_map = {row.get("id"): row for row in static_commands
                                   if isinstance(row, dict)}
                if len(log_command_map) != len(static_commands):
                    errors.append(f"producer static log command IDs duplicated: {evidence_path}")
                if set(log_command_map) != expected_command_ids:
                    errors.append(f"producer static log command ID set mismatch: {evidence_path}")
                for command in commands:
                    logged = log_command_map.get(command.get("id"), {})
                    comparable = {key:logged.get(key) for key in (
                        "id","argv","cwd","started_at","ended_at","exit_code","timed_out",
                        "signal","skipped","fallback_used","result"
                    )}
                    evidence_comparable = {key:command.get(key) for key in comparable}
                    if evidence_comparable != comparable:
                        errors.append(f"producer command differs from static log: {command.get('id')}")
    criteria = evidence.get("criterion_results", [])
    criterion_ids = [row.get("criterion_id") for row in criteria]
    if set(criterion_ids) != set(expected_criteria) or len(criterion_ids) != len(set(criterion_ids)):
        errors.append(f"criterion result set mismatch: {evidence_path}")
    for row in criteria:
        expected_status = expected_criteria.get(row.get("criterion_id"))
        if row.get("status") != expected_status or not row.get("evidence_refs"):
            errors.append(f"criterion status/evidence mismatch: {row.get('criterion_id')}")
        elif not set(row["evidence_refs"]).issubset(log_ids | artifact_ids):
            errors.append(f"criterion references unknown evidence: {row.get('criterion_id')}")
    obligations = evidence.get("obligation_results", [])
    obligation_ids = [row.get("obligation_id") for row in obligations]
    if set(obligation_ids) != expected_obligations or len(obligation_ids) != len(set(obligation_ids)):
        errors.append(f"obligation result set mismatch: {evidence_path}")
    for row in obligations:
        if row.get("status") not in {"SATISFIED_FOR_GATE_SCOPE", "NOT_APPLICABLE"}:
            errors.append(f"obligation result not gate-scoped PASS: {row.get('obligation_id')}")
        if row.get("status") == "SATISFIED_FOR_GATE_SCOPE" and (row.get("promotes_global") is not False
                                                                  or not row.get("evidence_refs")):
            errors.append(f"gate-scoped obligation overclaims or lacks evidence: {row.get('obligation_id')}")
    external_map = {row.get("id"): row for row in inputs.get("external", [])}
    for row in inputs.get("external", []):
        if not all(isinstance(row.get(key), str) and row.get(key)
                   for key in ("id","uri","pin_type","pin","cached_evidence_ref")):
            errors.append(f"external input is not pinned/cached: {row.get('id')}")
        elif row.get("cached_evidence_ref") not in artifact_ids | log_ids:
            errors.append(f"external input cache reference unknown: {row.get('id')}")
    if expected_node == "H0":
        if set(external_map) != {"EXT-RUST-CHANNEL","EXT-RUST-SIGNATURE","EXT-RUST-KEY","EXT-BIANCHI-PHASE-R"}:
            errors.append("H0 external input pin set mismatch")
        channel = external_map.get("EXT-RUST-CHANNEL", {})
        if (channel.get("pin_type") != "channel_entry_xz_hash"
                or channel.get("entry_selector") != "pkg.rust.target.x86_64-unknown-linux-gnu.xz_hash"
                or channel.get("pin") != inventory_map.get("SRC08", {}).get("sha256")):
            errors.append("Rust channel entry pin semantics mismatch")
        repo_pin = external_map.get("EXT-BIANCHI-PHASE-R", {})
        if repo_pin.get("pin_type") != "git_commit" or repo_pin.get("pin") != "539fcd6acc81dfd19d05951c2c5cbc3602eda077":
            errors.append("external repository commit pin mismatch")
    elif inputs.get("external") != []:
        errors.append(f"{expected_node} must not introduce external inputs")
    if expected_node in {"H0", "H1", "OD0"} and evidence.get("claim_effects") != []:
        errors.append(f"bootstrap/authorization evidence may not promote claims: {evidence_path}")
    core = {key:value for key, value in evidence.items() if key != "evidence_fingerprint"}
    if evidence.get("evidence_fingerprint") != canonical_hash(core):
        errors.append(f"producer evidence fingerprint mismatch: {evidence_path}")
    return evidence


def validate_review(root: Path, review_ref: dict, gate_id: str,
                    governing_fingerprint: str, evidence_by_path: dict[str, dict],
                    errors: list[str]) -> dict | None:
    verify_file_ref(root, review_ref, errors, "review reference")
    path = safe_local_path(root, review_ref.get("path"))
    if path is None or not path.is_file() or path.is_symlink():
        return None
    review = json.loads(path.read_text(encoding="utf-8"))
    required = {"schema","review_id","gate_id","recorded_at","producer_evidence_path",
                "producer_evidence_sha256","reviewed_evidence_fingerprint",
                "governing_fingerprint","reviewer","independence","verdict","findings",
                "review_log_refs","independent_execution_refs"}
    missing = required - set(review)
    extra = set(review) - required
    if missing or extra:
        errors.append(f"review field set mismatch missing={sorted(missing)} extra={sorted(extra)}: {review_ref.get('path')}")
    if missing:
        return review
    if review.get("schema") != "bass.review_attestation/v2" or review.get("gate_id") != gate_id:
        errors.append(f"review schema/gate mismatch: {review_ref.get('path')}")
    if not valid_timestamp(review.get("recorded_at")) or review.get("verdict") != "PASS":
        errors.append(f"review timestamp/verdict invalid: {review_ref.get('path')}")
    if review.get("governing_fingerprint") != governing_fingerprint:
        errors.append(f"review governing fingerprint stale: {review_ref.get('path')}")
    evidence_path = review.get("producer_evidence_path")
    evidence = evidence_by_path.get(evidence_path)
    actual_evidence_path = safe_local_path(root, evidence_path)
    if evidence is None or actual_evidence_path is None or not actual_evidence_path.is_file():
        errors.append(f"review references unknown producer evidence: {evidence_path}")
    else:
        if review.get("producer_evidence_sha256") != file_hash(actual_evidence_path):
            errors.append(f"reviewed producer evidence hash mismatch: {review_ref.get('path')}")
        if review.get("reviewed_evidence_fingerprint") != evidence.get("evidence_fingerprint"):
            errors.append(f"reviewed evidence fingerprint mismatch: {review_ref.get('path')}")
        producer = evidence.get("producer", {})
        reviewer = review.get("reviewer", {})
        if set(reviewer) != {"run_id", "assignment_id", "lane_id", "role"} or reviewer.get("role") != "blocking_gate_reviewer":
            errors.append(f"reviewer field set/role invalid: {review_ref.get('path')}")
        for field in ("run_id", "assignment_id", "lane_id"):
            if not isinstance(reviewer.get(field), str) or not reviewer[field]:
                errors.append(f"reviewer identity missing {field}: {review_ref.get('path')}")
            elif reviewer.get(field) == producer.get(field):
                errors.append(f"reviewer is not independent on {field}: {review_ref.get('path')}")
    independence = review.get("independence", {})
    if (set(independence) != {"producer_result_blinded_until_submission", "shared_code_or_oracle", "notes"}
            or independence.get("shared_code_or_oracle") is not False
            or independence.get("producer_result_blinded_until_submission") is not False
            or not isinstance(independence.get("notes"), str) or not independence["notes"]):
        errors.append(f"review independence caveat not closed: {review_ref.get('path')}")
    for index, log_ref in enumerate(review.get("review_log_refs", [])):
        verify_file_ref(root, log_ref, errors, f"review log {index}")
    if not review.get("review_log_refs"):
        errors.append(f"review has no durable log: {review_ref.get('path')}")
    node_id = evidence.get("node_id") if isinstance(evidence, dict) else None
    if isinstance(evidence, dict):
        producer_recorded = parsed_timestamp(evidence.get("recorded_at"))
        review_recorded = parsed_timestamp(review.get("recorded_at"))
        if (producer_recorded is not None and review_recorded is not None
                and review_recorded < producer_recorded):
            errors.append(f"review predates producer submission: {review_ref.get('path')}")
    expected_review_log = (f"audit/logs/{node_id}_REVIEW.md"
                           if node_id in {"H0", "H1", "OD0"} else None)
    review_logs = review.get("review_log_refs", [])
    if (expected_review_log is not None
            and (len(review_logs) != 1 or review_logs[0].get("path") != expected_review_log
                 or review_logs[0].get("bytes", 0) <= 0)):
        errors.append(f"review human-log path/content mismatch: {node_id}")
    execution_refs = review.get("independent_execution_refs", [])
    if node_id in {"H0", "H1"}:
        expected_path = f"audit/logs/{node_id}_REVIEW_STATIC_CHECKS.json"
        if (not isinstance(execution_refs, list) or len(execution_refs) != 1
                or execution_refs[0].get("path") != expected_path):
            errors.append(f"{node_id} review lacks the exact independent execution log")
        else:
            execution_ref = execution_refs[0]
            verify_file_ref(root, execution_ref, errors, "independent review execution")
            execution_path = safe_local_path(root, execution_ref.get("path"))
            if execution_path is not None and execution_path.is_file():
                try:
                    execution_log = json.loads(execution_path.read_text(encoding="utf-8"))
                except (json.JSONDecodeError, UnicodeDecodeError):
                    errors.append(f"independent review execution log is not JSON: {node_id}")
                else:
                    validate_static_log(
                        root, execution_log, node_id, evidence.get("governing"), errors,
                        f"independent review execution log {node_id}",
                    )
                    producer_log_hashes = {row.get("sha256") for row in evidence.get("logs", [])}
                    if execution_ref.get("sha256") in producer_log_hashes:
                        errors.append(f"review reused the producer static log: {node_id}")
                    if (valid_timestamp(execution_log.get("started_at"))
                            and valid_timestamp(evidence.get("recorded_at"))):
                        execution_started = datetime.fromisoformat(
                            execution_log["started_at"].replace("Z", "+00:00"))
                        evidence_recorded = datetime.fromisoformat(
                            evidence["recorded_at"].replace("Z", "+00:00"))
                        if execution_started < evidence_recorded:
                            errors.append(f"independent review execution predates producer submission: {node_id}")
                    execution_ended = parsed_timestamp(execution_log.get("ended_at"))
                    review_recorded = parsed_timestamp(review.get("recorded_at"))
                    if (execution_ended is not None and review_recorded is not None
                            and review_recorded < execution_ended):
                        errors.append(f"review attestation predates independent execution: {node_id}")
    elif execution_refs != []:
        errors.append("OD0 semantic review must not claim an execution log")
    return review


def validate_gate_receipt(root: Path, node: dict, gate: dict, node_map: dict[str, dict],
                          evidence_contract: dict, inventory_map: dict[str, dict], decisions: dict,
                          errors: list[str]) -> dict | None:
    receipt_path = node.get("receipt")
    path = safe_local_path(root, receipt_path)
    if path is None or not path.is_file() or path.is_symlink():
        errors.append(f"PASS node lacks durable receipt: {node.get('id')}")
        return None
    try:
        receipt = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        errors.append(f"gate receipt is not valid JSON: {receipt_path}")
        return None
    required = {"schema","receipt_id","node_id","gate_id","status","issued_at","scope",
                "governing_fingerprint","producer_evidence_refs","review_refs",
                "dependency_receipts","criteria_summary","obligation_summary",
                "claim_effects","claim_boundary","invalidates","supersedes"}
    if node.get("id") == "OD0":
        required.add("authorization")
    missing = required - set(receipt)
    extra = set(receipt) - required
    if missing or extra:
        errors.append(f"receipt field set mismatch missing={sorted(missing)} extra={sorted(extra)}: {node.get('id')}")
    if missing:
        return receipt
    if (receipt.get("schema") != "bass.gate_receipt/v2" or receipt.get("node_id") != node.get("id")
            or receipt.get("gate_id") != gate.get("id") or receipt.get("status") != "PASS"):
        errors.append(f"gate receipt identity/schema/status mismatch: {node.get('id')}")
    if not valid_timestamp(receipt.get("issued_at")):
        errors.append(f"gate receipt timestamp invalid: {node.get('id')}")
    expected_scopes = {
        "H0":"input/provenance audit",
        "H1":"harness structure and static tools only",
        "OD0":"owner decisions and read-only canonical-code intake authorization only",
    }
    if node.get("id") in expected_scopes and receipt.get("scope") != expected_scopes[node["id"]]:
        errors.append(f"gate receipt scope mismatch: {node.get('id')}")
    governing = governing_snapshot(root, node["id"], gate, node, evidence_contract, errors)
    if governing is None:
        return receipt
    if receipt.get("governing_fingerprint") != governing.get("fingerprint"):
        affected = downstream_nodes(node_map, node["id"])
        errors.append(f"stale PASS receipt for {node['id']}; invalidate {affected}")
    dependency_rows: list[dict] = []
    for dependency_id in node.get("depends_on", []):
        dependency = node_map[dependency_id]
        dependency_path = safe_local_path(root, dependency.get("receipt"))
        if dependency.get("status") != "PASS" or dependency_path is None or not dependency_path.is_file():
            errors.append(f"PASS node has missing/non-PASS dependency: {node['id']} <- {dependency_id}")
            continue
        dependency_receipt = json.loads(dependency_path.read_text(encoding="utf-8"))
        dependency_rows.append({"node_id":dependency_id,"path":dependency.get("receipt"),
                                "sha256":file_hash(dependency_path),
                                "governing_fingerprint":dependency_receipt.get("governing_fingerprint")})
    expected_dependency_set = {
        (row["node_id"], row["path"], row["sha256"], row["governing_fingerprint"])
        for row in dependency_rows
    }
    actual_dependency_set = {
        (row.get("node_id"), row.get("path"), row.get("sha256"), row.get("governing_fingerprint"))
        for row in receipt.get("dependency_receipts", []) if isinstance(row, dict)
    }
    if actual_dependency_set != expected_dependency_set:
        errors.append(f"gate receipt dependency set mismatch: {node.get('id')}")
    expected_criteria = expected_criterion_statuses(gate, decisions, errors)
    expected_obligations = set(gate.get("obligation_ids", []))
    evidence_by_path: dict[str, dict] = {}
    producer_identities: list[dict] = []
    for ref in receipt.get("producer_evidence_refs", []):
        verify_file_ref(root, ref, errors, "producer evidence reference")
        evidence = validate_evidence(root, ref.get("path"), node["id"], gate["id"], governing,
                                     evidence_contract,
                                     expected_criteria, expected_obligations, dependency_rows,
                                     inventory_map, errors)
        if evidence is not None:
            evidence_by_path[ref.get("path")] = evidence
            producer_identities.append(evidence.get("producer", {}))
            if ref.get("evidence_fingerprint") != evidence.get("evidence_fingerprint"):
                errors.append(f"gate receipt evidence fingerprint mismatch: {ref.get('path')}")
    if not evidence_by_path:
        errors.append(f"PASS gate has no valid producer evidence: {node.get('id')}")
    reviews = [validate_review(root, ref, gate["id"], governing["fingerprint"],
                               evidence_by_path, errors) for ref in receipt.get("review_refs", [])]
    if not any(review is not None and review.get("verdict") == "PASS" for review in reviews):
        errors.append(f"PASS gate lacks independent PASS review: {node.get('id')}")
    receipt_issued = parsed_timestamp(receipt.get("issued_at"))
    predecessor_times = [parsed_timestamp(evidence.get("recorded_at"))
                         for evidence in evidence_by_path.values()]
    predecessor_times.extend(parsed_timestamp(review.get("recorded_at"))
                             for review in reviews if isinstance(review, dict))
    if (receipt_issued is not None
            and any(timestamp is not None and timestamp > receipt_issued
                    for timestamp in predecessor_times)):
        errors.append(f"gate receipt predates its evidence/review: {node.get('id')}")
    required_count = len(expected_criteria)
    passed_count = sum(status == "PASS" for status in expected_criteria.values())
    not_applicable_count = sum(status == "NOT_APPLICABLE" for status in expected_criteria.values())
    summary = receipt.get("criteria_summary", {})
    if summary != {"required":required_count,"passed":passed_count,"not_applicable":not_applicable_count,
                   "failed":0,"skipped":0}:
        errors.append(f"gate receipt criterion summary mismatch: {node.get('id')}")
    obligation_summary = receipt.get("obligation_summary", {})
    if set(obligation_summary.get("required_ids", [])) != expected_obligations or obligation_summary.get("failed_ids") != []:
        errors.append(f"gate receipt obligation summary mismatch: {node.get('id')}")
    evidence_effects = []
    for evidence in evidence_by_path.values():
        evidence_effects.extend(evidence.get("claim_effects", []))
    if receipt.get("claim_effects") != evidence_effects:
        errors.append(f"gate receipt/evidence claim effects mismatch: {node.get('id')}")
    if not isinstance(receipt.get("claim_boundary"), str) or not receipt["claim_boundary"]:
        errors.append(f"gate receipt claim boundary missing: {node.get('id')}")
    evidence_boundaries = {row.get("claim_boundary") for row in evidence_by_path.values()}
    if len(evidence_boundaries) != 1 or receipt.get("claim_boundary") not in evidence_boundaries:
        errors.append(f"gate receipt/evidence claim boundary mismatch: {node.get('id')}")
    if node.get("id") == "OD0":
        authorization = receipt.get("authorization", {})
        expected_authorization_fields = {
            "action", "granted", "authorization_ref", "owner_decision_receipt_ref",
        }
        if set(authorization) != expected_authorization_fields:
            errors.append("OD0 gate receipt authorization field set invalid")
        if (authorization.get("action") != "READ_CANONICAL_SOLVER_CODE"
                or authorization.get("granted") is not True):
            errors.append("OD0 gate receipt authorization action/grant invalid")
        authorization_ref = authorization.get("authorization_ref", {})
        owner_ref = authorization.get("owner_decision_receipt_ref", {})
        verify_file_ref(root, authorization_ref, errors, "OD0 receipt code-read authorization")
        verify_file_ref(root, owner_ref, errors, "OD0 receipt owner-decision authorization source")
        if authorization_ref.get("path") != OD0_CODE_READ_AUTHORIZATION_PATH:
            errors.append("OD0 gate receipt points to the wrong code-read authorization path")
        if owner_ref.get("path") != OD0_OWNER_RECEIPT_PATH:
            errors.append("OD0 gate receipt points to the wrong owner-decision receipt path")
        artifact_refs = {
            row.get("id"):(row.get("path"), row.get("bytes"), row.get("sha256"))
            for evidence in evidence_by_path.values() for row in evidence.get("artifacts", [])
        }
        if artifact_refs.get("ART-OD0-READ-AUTH") != (
                authorization_ref.get("path"), authorization_ref.get("bytes"),
                authorization_ref.get("sha256")):
            errors.append("OD0 receipt/producer code-read authorization hashes differ")
        if artifact_refs.get("ART-OD0-OWNER") != (
                owner_ref.get("path"), owner_ref.get("bytes"), owner_ref.get("sha256")):
            errors.append("OD0 receipt/producer owner-decision receipt hashes differ")
    return receipt


def validate(root: Path) -> list[str]:
    root = root.resolve()
    errors: list[str] = []
    for relative in REQUIRED:
        if not (root / relative).is_file():
            errors.append(f"missing required file: {relative}")
    if errors:
        return errors
    try:
        version = (root / "VERSION").read_text(encoding="utf-8").strip()
        manifest = load_json(root, "manifest.json")
        scope = load_json(root, "contracts/scope_lock.json")
        state_machine = load_json(root, "contracts/state_machine.json")
        evidence_contract = load_json(root, "contracts/evidence_contract.json")
        decisions = load_json(root, "contracts/owner_decisions.json")
        conventions = load_json(root, "contracts/conventions.json")
        science = load_json(root, "contracts/scientific_contract.json")
        family = load_json(root, "contracts/family_registry.json")
        high_ell = load_json(root, "contracts/high_ell_acceptance.json")
        oracle = load_json(root, "contracts/external_oracle_lock.json")
        dag = load_json(root, "state/dag.json")
        gates = load_json(root, "state/gates.json")
        claims = load_json(root, "state/claims.json")
        run_state = load_json(root, "state/run_state.json")
        inventory = load_json(root, "audit/INPUT_INVENTORY.json")
        rust_auth = load_json(root, "audit/RUST_1_94_1_AUTHENTICITY.json")
    except (json.JSONDecodeError, UnicodeDecodeError, OSError) as error:
        return [f"required JSON/text load failed: {error}"]

    if manifest.get("version") != version:
        errors.append("VERSION and manifest version differ")
    validate_evidence_contract(evidence_contract, errors)
    if (manifest.get("initial_phase") != "USER_SCOPE_CONFIRMATION"
            or manifest.get("phase_state") != "contracts/scope_lock.json"
            or "current_phase" in manifest):
        errors.append("manifest must keep immutable initial-phase metadata and delegate live phase state")
    if manifest.get("evidence_schema") != (
            "static_check_log/producer_evidence/review_attestation/gate_receipt v2; "
            "owner_decision_receipt/code_read_authorization/action_authorization/activity_receipt v1"):
        errors.append("manifest evidence schema declaration mismatch")
    if conventions.get("metric_signature") != "(-,+,+,+)":
        errors.append("metric signature drift")
    if conventions.get("spatial_orientation") != "epsilon_123=+1":
        errors.append("orientation drift")
    if conventions.get("transport_frame") != "n^a normal frame":
        errors.append("transport-frame drift")
    if conventions.get("observer_local_boost") != "output_only":
        errors.append("local-boost firewall missing")
    if scope.get("background_dynamics") != "EXACT_NONLINEAR_TARGET_PENDING_EVIDENCE":
        errors.append("background exact/nonlinear target missing")
    if "ELLMAX" not in scope.get("angular_hierarchy", ""):
        errors.append("finite configurable ell_max policy missing")
    if science.get("spatial_perturbative_order") != "forbidden_in_v1":
        errors.append("spatial perturbation firewall missing in science contract")

    decision_rows = decisions.get("decisions", [])
    if {row.get("id") for row in decision_rows} != {"OD001","OD002","OD003","OD004"}:
        errors.append("owner-decision set must be OD001..OD004")
    if (decisions.get("schema_version") != 4
            or decisions.get("sector_registry_ref")
            != "contracts/scientific_contract.json#/sector_registry"):
        errors.append("owner-decision schema/sector-registry reference mismatch")
    obligation_rows = science.get("obligations", [])
    obligation_ids = [row.get("id") for row in obligation_rows]
    if len(obligation_ids) != len(set(obligation_ids)) or set(science.get("required_obligation_ids", [])) != set(obligation_ids):
        errors.append("scientific obligation registry is duplicate/incomplete")
    claim_rows = claims.get("claims", [])
    claim_map = {row.get("id"): row for row in claim_rows}
    if len(claim_map) != len(claim_rows):
        errors.append("duplicate claim ID")
    validate_family_and_high_ell(family, high_ell, science, claim_map, errors)

    if not re.fullmatch(r"[0-9a-f]{40}", oracle.get("pinned_commit", "")):
        errors.append("external oracle is not pinned to a commit")
    if oracle.get("role") != "READ_ONLY_EXTERNAL_ORACLE" or oracle.get("may_write_remote") is not False:
        errors.append("external-oracle write firewall missing")
    if oracle.get("production_dependency") is not False:
        errors.append("external oracle may not be a production dependency")
    decision_map = {row.get("id"): row for row in decision_rows}
    if (oracle.get("pinned_commit") != ORACLE_PIN
            or decision_map.get("OD003", {}).get("required_pinned_commit") != oracle.get("pinned_commit")
            or decision_map.get("OD003", {}).get("allowed_roles") != ["READ_ONLY_EXTERNAL_ORACLE"]):
        errors.append("OD003 and external-oracle pin/role contract mismatch")
    if oracle.get("audited_on") != "2026-08-01" or "audited_at" in oracle:
        errors.append("external-oracle lock must use an honest date-only audit field")
    if manifest.get("created_on") != "2026-08-01" or "created_at" in manifest:
        errors.append("harness manifest must use an honest date-only creation field")

    gate_rows = gates.get("gates", [])
    gate_map = {row.get("id"): row for row in gate_rows}
    if len(gate_map) != len(gate_rows):
        errors.append("duplicate gate ID")
    for row in gate_rows:
        if row.get("status") not in GATE_STATES:
            errors.append(f"invalid gate status: {row.get('id')}")
        criterion_ids = [item.get("id") for item in row.get("requires", []) if isinstance(item, dict)]
        if len(criterion_ids) != len(row.get("requires", [])) or len(criterion_ids) != len(set(criterion_ids)):
            errors.append(f"gate criteria need unique stable IDs: {row.get('id')}")
        unknown = set(row.get("obligation_ids", [])) - set(obligation_ids)
        if unknown:
            errors.append(f"unknown obligations in {row.get('id')}: {sorted(unknown)}")
    validate_sector_registry(decisions, science, high_ell, claim_map, gate_map, errors)
    validate_claim_criterion_bindings(family, claim_map, gate_map, errors)

    node_rows = dag.get("nodes", [])
    node_map = {row.get("id"): row for row in node_rows}
    if len(node_map) != len(node_rows):
        errors.append("duplicate DAG node ID")
    for row in node_rows:
        node_id = row.get("id")
        if row.get("status") not in GATE_STATES:
            errors.append(f"invalid node status: {node_id}")
        if row.get("status") != "PASS" and row.get("receipt") is not None:
            errors.append(f"non-PASS node retains an active receipt pointer: {node_id}")
        invalidation = row.get("invalidation")
        if invalidation is not None:
            if (not isinstance(invalidation, dict)
                    or set(invalidation) != {"reason_code", "prior_receipt_ref"}
                    or not isinstance(invalidation.get("reason_code"), str)
                    or re.fullmatch(r"[A-Z][A-Z0-9_]{2,63}", invalidation["reason_code"]) is None
                    or row.get("status") != "BLOCKED"):
                errors.append(f"node invalidation record is not a safe machine record: {node_id}")
            prior_ref = invalidation.get("prior_receipt_ref") if isinstance(invalidation, dict) else None
            if prior_ref is not None:
                if not isinstance(prior_ref, dict) or set(prior_ref) != {"path", "bytes", "sha256"}:
                    errors.append(f"node invalidation prior-receipt field set invalid: {node_id}")
                else:
                    verify_file_ref(root, prior_ref, errors, f"node invalidation prior receipt {node_id}")
                    prior_path = safe_local_path(root, prior_ref.get("path"))
                    if (prior_path is None or not prior_ref.get("path", "").startswith("receipts/")
                            or not prior_path.is_file()):
                        errors.append(f"node invalidation prior receipt path invalid: {node_id}")
                    else:
                        try:
                            prior_receipt = json.loads(prior_path.read_text(encoding="utf-8"))
                        except (json.JSONDecodeError, UnicodeDecodeError):
                            errors.append(f"node invalidation prior receipt is not JSON: {node_id}")
                        else:
                            if (prior_receipt.get("schema") != "bass.gate_receipt/v2"
                                    or prior_receipt.get("node_id") != node_id
                                    or prior_receipt.get("gate_id") != row.get("gate_id")
                                    or prior_receipt.get("status") != "PASS"
                                    or not valid_sha(prior_receipt.get("governing_fingerprint"))):
                                errors.append(f"node invalidation prior receipt identity invalid: {node_id}")
        if row.get("gate_id") not in gate_map:
            errors.append(f"unknown gate for node {node_id}")
        elif gate_map[row["gate_id"]].get("status") != row.get("status"):
            errors.append(f"DAG/gate status mismatch: {node_id}")
        for dependency in row.get("depends_on", []):
            if dependency not in node_map:
                errors.append(f"unknown dependency {dependency} for {node_id}")
            elif row.get("status") == "PASS" and node_map[dependency].get("status") != "PASS":
                errors.append(f"PASS node has non-PASS dependency: {node_id} <- {dependency}")
    visiting: set[str] = set()
    visited: set[str] = set()
    def visit(node_id: str) -> None:
        if node_id in visiting:
            errors.append(f"DAG cycle at {node_id}")
            return
        if node_id in visited:
            return
        visiting.add(node_id)
        for dependency in node_map[node_id].get("depends_on", []):
            if dependency in node_map:
                visit(dependency)
        visiting.remove(node_id)
        visited.add(node_id)
    for node_id in node_map:
        visit(node_id)

    validate_phase_state(scope, decisions, state_machine, node_map, run_state, errors)
    validate_run_state_structure(root, run_state, scope, decisions, node_map, errors)
    if (manifest.get("solver_code_included") is False
            and any(run_state.get(key) is not False for key in (
                "solver_code_present", "solver_code_executed", "solver_code_modified",
                "external_oracle_executed"))):
        errors.append("standalone harness run-state may not claim solver/oracle activity")
    validate_owner_receipt(root, decisions, errors)
    validate_code_read_authorization(root, decisions, scope, errors)
    if run_state.get("current_node") not in node_map:
        errors.append("run-state current node is unknown")
    elif node_map[run_state["current_node"]].get("status") not in {"BLOCKED","NOT_RUN","FAIL"}:
        errors.append("current DAG node may not already be PASS")

    inventory_map = {row.get("id"): row for row in inventory.get("items", [])}
    if len(inventory_map) != 13:
        errors.append("input inventory must contain 13 unique items")
    if inventory.get("audited_on") != "2026-08-01" or "audited_at" in inventory:
        errors.append("input inventory must use an honest date-only audit field")
    if inventory_map.get("SRC04", {}).get("verifies") != "SRC08":
        errors.append("Rust signature-to-payload relation missing")
    if rust_auth.get("local_sha256") != inventory_map.get("SRC08", {}).get("sha256"):
        errors.append("Rust authenticity evidence/input hash mismatch")
    if rust_auth.get("official_sha256") != rust_auth.get("local_sha256"):
        errors.append("Rust official/local hash evidence mismatch")
    if rust_auth.get("gpg_result") != "GOOD_SIGNATURE" or rust_auth.get("installed") is not False:
        errors.append("Rust signature/no-install evidence invalid")

    validate_harness_payload(root, manifest, scope, decisions, errors)

    gate_receipts: dict[str, dict] = {}
    for row in node_rows:
        if row.get("status") == "PASS" and row.get("gate_id") in gate_map:
            receipt = validate_gate_receipt(root, row, gate_map[row["gate_id"]], node_map,
                                            evidence_contract, inventory_map, decisions, errors)
            if receipt is not None:
                gate_receipts[row["gate_id"]] = receipt

    if any(row.get("status") not in CLAIM_STATES for row in claim_rows):
        errors.append("invalid claim status")
    permanently_out = {
        "CLM-V1-SPATIAL-PERTURBATIONS", "CLM-V1-PRIMORDIAL-STOCHASTIC",
        "CLM-V1-LIKELIHOOD-DATA-FITTING",
    }
    allowed_out = set(permanently_out)
    node_by_gate = {row.get("gate_id"):row for row in node_rows}
    od2 = decision_map.get("OD002", {})
    if od2.get("status") == "RESOLVED" and isinstance(od2.get("value"), dict):
        allowed_out.update(
            row.get("id") for row in claim_rows
            if row.get("conditional_sector") is not None
            and od2["value"].get(row["conditional_sector"]) is False
        )
    for aggregate_id, rule in claims.get("aggregate_rules", {}).items():
        if (isinstance(rule, dict) and rule.get("policy") == "ALL_IN_SCOPE"
                and rule.get("constituents")
                and all(claim_map.get(item, {}).get("status") == "LOCKED_OUT_OF_SCOPE"
                        for item in rule["constituents"])):
            allowed_out.add(aggregate_id)
    for claim_id in permanently_out:
        row = claim_map.get(claim_id, {})
        if (row.get("status") != "LOCKED_OUT_OF_SCOPE" or row.get("value") is not False
                or row.get("evidence_ids") != []):
            errors.append(f"out-of-scope claim unlocked: {claim_id}")
    for row in claim_rows:
        claim_id = row.get("id")
        status = row.get("status")
        gate_id = row.get("gate")
        evidence_ids = row.get("evidence_ids")
        if gate_id is not None and gate_id not in gate_map:
            errors.append(f"claim references unknown gate: {claim_id}")
        if (not isinstance(evidence_ids, list)
                or any(not isinstance(item, str) or re.fullmatch(
                    r"(?:[A-Z][A-Z0-9_.:-]{2,127}|sha256:[0-9a-f]{64})", item) is None
                    for item in evidence_ids)
                or len(evidence_ids) != len(set(evidence_ids))):
            errors.append(f"claim evidence IDs must be a unique list: {claim_id}")
            evidence_ids = []
        if status == "LOCKED_OUT_OF_SCOPE":
            if row.get("value") is not False or evidence_ids != []:
                errors.append(f"out-of-scope claim has invalid value/evidence: {claim_id}")
            if claim_id not in allowed_out:
                errors.append(f"claim is not eligible to be locked out of scope: {claim_id}")
        if status == "LOCKED_PENDING_EVIDENCE" and (row.get("value") is not None or evidence_ids != []):
            errors.append(f"pending claim contains value/evidence: {claim_id}")
        if status == "REJECTED" and (
                row.get("value") is not False or not evidence_ids
                or gate_map.get(gate_id, {}).get("status") != "FAIL"):
            errors.append(f"rejected claim lacks false value/evidence/FAIL gate: {claim_id}")
        if status == "REJECTED":
            errors.append(f"rejected claim is unsupported until a negative-evidence receipt schema exists: {claim_id}")
        if status == "INVALIDATED":
            invalidated_node = node_by_gate.get(gate_id, {})
            invalidation = invalidated_node.get("invalidation", {})
            prior_ref = (invalidation.get("prior_receipt_ref")
                         if isinstance(invalidation, dict) else None)
            expected_invalidation_evidence = ([f"sha256:{prior_ref.get('sha256')}"]
                                              if isinstance(prior_ref, dict)
                                              and valid_sha(prior_ref.get("sha256")) else None)
            if (row.get("value") is not None
                    or gate_map.get(gate_id, {}).get("status") != "BLOCKED"
                    or expected_invalidation_evidence is None
                    or evidence_ids != expected_invalidation_evidence):
                errors.append(f"invalidated claim is not bound to its prior gate receipt: {claim_id}")
        if status in {"SUPPORTED", "PARTIALLY_SUPPORTED"}:
            if row.get("value") is not True or not row.get("evidence_ids"):
                errors.append(f"supported claim lacks true value/durable evidence IDs: {claim_id}")
            if gate_map.get(gate_id, {}).get("status") != "PASS":
                errors.append(f"SUPPORTED claim has non-PASS gate: {claim_id}")
            receipt = gate_receipts.get(gate_id, {})
            effects = receipt.get("claim_effects", []) if isinstance(receipt, dict) else []
            matching = [effect for effect in effects
                        if effect.get("claim_id") == claim_id and effect.get("action") == "PROMOTE"
                        and effect.get("new_status") == status and effect.get("evidence_refs")]
            if not matching:
                errors.append(f"supported claim lacks matching gate receipt promotion: {claim_id}")
            else:
                effect = matching[0]
                if set(effect.get("criterion_ids", [])) != set(row.get("required_criterion_ids", [])):
                    errors.append(f"supported claim promotion criterion set mismatch: {claim_id}")
                if set(effect.get("evidence_refs", [])) != set(row.get("evidence_ids", [])):
                    errors.append(f"supported claim evidence IDs differ from promotion: {claim_id}")
    for aggregate_id, rule in claims.get("aggregate_rules", {}).items():
        if not isinstance(rule, dict) or rule.get("policy") not in {"ALL", "ALL_IN_SCOPE"}:
            errors.append(f"aggregate claim rule is malformed: {aggregate_id}")
            continue
        constituents = rule.get("constituents", [])
        if not constituents or len(constituents) != len(set(constituents)) or any(
                claim_id not in claim_map for claim_id in constituents):
            errors.append(f"aggregate claim constituents are invalid: {aggregate_id}")
            continue
        aggregate = claim_map.get(aggregate_id, {})
        statuses = [claim_map[claim_id].get("status") for claim_id in constituents]
        if rule["policy"] == "ALL_IN_SCOPE":
            all_out = all(status == "LOCKED_OUT_OF_SCOPE" for status in statuses)
            aggregate_out = (aggregate.get("status") == "LOCKED_OUT_OF_SCOPE"
                             and aggregate.get("value") is False
                             and aggregate.get("evidence_ids") == [])
            if all_out and not aggregate_out:
                errors.append(f"all-out-of-scope aggregate is not derived locked-out: {aggregate_id}")
            if not all_out and aggregate.get("status") == "LOCKED_OUT_OF_SCOPE":
                errors.append(f"aggregate locked out while an in-scope constituent remains: {aggregate_id}")
        if aggregate.get("status") == "SUPPORTED":
            if rule["policy"] == "ALL" and any(status != "SUPPORTED" for status in statuses):
                errors.append(f"aggregate claim promoted before all constituents: {aggregate_id}")
            if rule["policy"] == "ALL_IN_SCOPE" and (
                    not any(status == "SUPPORTED" for status in statuses)
                    or any(status not in {"SUPPORTED", "LOCKED_OUT_OF_SCOPE"} for status in statuses)):
                errors.append(f"conditional aggregate promoted before all in-scope constituents: {aggregate_id}")

    if scope.get("current_phase") in {"RELEASE_AUDIT", "OWNER_RELEASE_DECISION", "RELEASED"}:
        release_required = {
            "CLM-BACKGROUND-RUNTIME", "CLM-ALL-11-FAMILIES", "CLM-HIGH-ELL-CONVERGENCE",
        }
        if od2.get("status") == "RESOLVED" and isinstance(od2.get("value"), dict):
            if od2["value"].get("global_tilt"):
                release_required.add("CLM-GLOBAL-TILT")
            if any(od2["value"].get(key) for key in ("photon_E", "photon_B", "photon_V")):
                release_required.add("CLM-POLARIZATION")
            if od2["value"].get("massless_neutrinos"):
                release_required.add("CLM-MASSLESS-NEUTRINO-RUNTIME")
            for sector, claim_id in (
                ("exact_electron_frame_thomson", "CLM-EXACT-ELECTRON-FRAME-THOMSON"),
                ("recombination", "CLM-RECOMBINATION"),
                ("reionization", "CLM-REIONIZATION"),
            ):
                if od2["value"].get(sector):
                    release_required.add(claim_id)
        od4 = decision_map.get("OD004", {})
        if (od4.get("status") == "RESOLVED" and isinstance(od4.get("value"), dict)
                and od4["value"].get("rust_backend_in_v1") is True):
            release_required.add("CLM-RUST-PYTHON-EQUIVALENCE")
        if scope.get("current_phase") == "RELEASED":
            release_required.add("CLM-V1-RELEASE")
        for claim_id in sorted(release_required):
            if claim_map.get(claim_id, {}).get("status") != "SUPPORTED":
                errors.append(f"release phase lacks supported critical claim: {claim_id}")

    validate_manifest_hashes(root, errors)
    return errors


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    errors = validate(root)
    if errors:
        print("BASS_HARNESS_CHECK: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("BASS_HARNESS_CHECK: PASS")
    print("scope: background-only; spatial perturbations/likelihood permanently prohibited")
    print("authority: fresh v2 evidence/review/receipt graph; no solver claim promoted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
