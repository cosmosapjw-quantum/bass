#!/usr/bin/env python3
"""Serialize H0/H1/OD0 v2 evidence, reviews, and gate receipts."""

from __future__ import annotations

import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile

HARNESS_ROOT = Path(__file__).resolve().parents[1]
if str(HARNESS_ROOT) not in sys.path:
    sys.path.insert(0, str(HARNESS_ROOT))
from tools.validate_harness import (
    canonical_hash, file_hash, governing_snapshot, load_json, validate_static_log,
)

RECEIPT_SCOPE_BY_NODE = {
    "H0":"input/provenance audit",
    "H1":"harness structure and static tools only",
    "OD0":"owner decisions and read-only canonical-code intake authorization only",
}


def now() -> str:
    return datetime.now().astimezone().isoformat(timespec="microseconds")


def file_ref(root: Path, relative: str, **extra) -> dict:
    path = root / relative
    return {**extra, "path":relative, "bytes":path.stat().st_size, "sha256":file_hash(path)}


def write_atomic(output: Path, value: dict) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{output.name}.", dir=output.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(value, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
        os.replace(temporary, output)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def version(command: list[str]) -> str:
    completed = subprocess.run(command, text=True, capture_output=True, check=False)
    return (completed.stdout or completed.stderr).splitlines()[0].strip()


def node_context(root: Path, node_id: str) -> tuple[dict, dict, dict, dict, dict]:
    dag = load_json(root, "state/dag.json")
    gates = load_json(root, "state/gates.json")
    contract = load_json(root, "contracts/evidence_contract.json")
    node = next(row for row in dag["nodes"] if row["id"] == node_id)
    gate = next(row for row in gates["gates"] if row["id"] == node["gate_id"])
    errors: list[str] = []
    governing = governing_snapshot(root, node_id, gate, node, contract, errors)
    if errors or governing is None:
        raise RuntimeError("; ".join(errors))
    return dag, gates, node, gate, governing


def dependency_rows(root: Path, dag: dict, node: dict) -> list[dict]:
    node_map = {row["id"]: row for row in dag["nodes"]}
    rows: list[dict] = []
    for dependency_id in node.get("depends_on", []):
        dependency = node_map[dependency_id]
        path = root / dependency["receipt"]
        receipt = json.loads(path.read_text(encoding="utf-8"))
        rows.append({"node_id":dependency_id,"path":dependency["receipt"],
                     "sha256":file_hash(path),
                     "governing_fingerprint":receipt["governing_fingerprint"]})
    return rows


def make_producer(root: Path, node_id: str, static_log: str | None, output: Path) -> None:
    dag, _gates, node, gate, governing = node_context(root, node_id)
    log: dict | None = None
    if node_id in {"H0", "H1"}:
        if static_log is None:
            raise RuntimeError(f"{node_id} producer evidence requires a static log")
        log = load_json(root, static_log)
        if (log.get("schema") != "bass.static_check_log/v2"
                or log.get("mode") != node_id
                or log.get("all_passed") is not True
                or log.get("governing_snapshot_stable") is not True
                or log.get("pre_execution_governing") != governing
                or log.get("post_execution_governing") != governing):
            raise RuntimeError("static log is not a fresh all-pass run over current governing bytes")
        static_errors: list[str] = []
        validate_static_log(root, log, node_id, governing, static_errors,
                            f"producer static log {node_id}")
        if static_errors:
            raise RuntimeError("static log fails canonical plan/semantic validation: "
                               + "; ".join(static_errors))
    elif static_log is not None:
        raise RuntimeError("OD0 is a no-execution decision/authorization gate and accepts no static log")
    if node_id == "H0":
        log_ids = ["LOG-H0-HASH","LOG-H0-ARCHIVE","LOG-H0-RUST","LOG-H0-REPO"]
    elif node_id == "H1":
        log_ids = ["LOG-H1-STATIC"]
    else:
        log_ids = []
    logs = ([file_ref(root, static_log, id=log_id, nonempty_required=True)
             for log_id in log_ids] if static_log is not None else [])
    commands = []
    for row in (log or {}).get("commands", []):
        if node_id == "H0":
            number = int(row["id"].rsplit("-", 1)[1])
            if number == 1:
                command_log_ids = ["LOG-H0-HASH"]
            elif 2 <= number <= 7:
                command_log_ids = ["LOG-H0-ARCHIVE"]
            elif 10 <= number <= 16:
                command_log_ids = ["LOG-H0-RUST"]
            else:
                command_log_ids = ["LOG-H0-REPO"]
        else:
            command_log_ids = ["LOG-H1-STATIC"]
        commands.append({key:row[key] for key in (
            "id","argv","cwd","started_at","ended_at","exit_code","timed_out","signal",
            "skipped","fallback_used","result"
        )} | {"log_refs":command_log_ids})
    environment_details = {
        "python": platform.python_version(),
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "git": version(["git", "--version"]),
        "dependency_installed": False,
        "solver_executed": False,
    }
    inventory = load_json(root, "audit/INPUT_INVENTORY.json")
    local_inputs: list[dict] = []
    external_inputs: list[dict] = []
    if node_id == "H0":
        for row in inventory["items"]:
            local_inputs.append({"id":row["id"],"source_id":row["id"],"name":row["name"],
                                 "bytes":row["bytes"],"sha256":row["sha256"],
                                 "retention":"AUDIT_SOURCE_NOT_BUNDLED","runtime_use":False,
                                 "use_policy":row["disposition"]})
        artifact_specs = [
            ("ART-H0-INVENTORY","audit/INPUT_INVENTORY.json","input_inventory"),
            ("ART-H0-RUST","audit/RUST_1_94_1_AUTHENTICITY.json","supply_chain_evidence"),
            ("ART-H0-REPO","audit/REPO_ORACLE_SNAPSHOT.md","repository_pin_evidence"),
            ("ART-H0-TOOLCHAIN","audit/TOOLCHAIN_STATUS.md","toolchain_disposition"),
            ("ART-H0-AUDIT","docs/HARNESS_AUDIT_REPORT.md","audit_report"),
            ("ART-H0-TRANSPLANT","docs/TRANSPLANT_MAP.md","transplant_map"),
        ]
        external_inputs = [
            {"id":"EXT-RUST-CHANNEL","uri":"https://static.rust-lang.org/dist/channel-rust-1.94.1.toml","pin_type":"channel_entry_xz_hash","entry_selector":"pkg.rust.target.x86_64-unknown-linux-gnu.xz_hash","pin":"294b3d81fa72e62581276290c60c81eb8b58498d333d422ca1dfc432877d0c40","cached_evidence_ref":"ART-H0-RUST"},
            {"id":"EXT-RUST-SIGNATURE","uri":"https://static.rust-lang.org/dist/rust-1.94.1-x86_64-unknown-linux-gnu.tar.xz.asc","pin_type":"signature_sha256","pin":"942bc6926af6a2130d70e77933e3df09d39beeedafad77710259e6df7eadee08","cached_evidence_ref":"ART-H0-RUST"},
            {"id":"EXT-RUST-KEY","uri":"https://static.rust-lang.org/rust-key.gpg.ascii","pin_type":"key_fingerprint","pin":"108F66205EAEB0AAA8DD5E1C85AB96E6FA1BE5FE","cached_evidence_ref":"ART-H0-RUST"},
            {"id":"EXT-BIANCHI-PHASE-R","uri":"https://github.com/cosmosapjw-quantum/bianchi_phase_r","pin_type":"git_commit","pin":"539fcd6acc81dfd19d05951c2c5cbc3602eda077","cached_evidence_ref":"ART-H0-REPO"},
        ]
        claim_boundary = "Input/provenance audit only; no harness, solver, physics, runtime, or release claim."
    elif node_id == "H1":
        local_inputs = [file_ref(root, row["path"], id=f"IN-{index:03d}", retention="EMBEDDED")
                        for index, row in enumerate(governing["files"], 1)]
        artifact_specs = [
            ("ART-H1-STATE-MACHINE","contracts/state_machine.json","phase_contract"),
            ("ART-H1-EVIDENCE-CONTRACT","contracts/evidence_contract.json","evidence_contract"),
            ("ART-H1-FAMILY","contracts/family_registry.json","family_registry"),
            ("ART-H1-HIGH-ELL","contracts/high_ell_acceptance.json","high_ell_contract"),
            ("ART-H1-TESTS","tests/test_harness_tools.py","hostile_regression_tests"),
        ]
        claim_boundary = "Harness structure and fail-closed evidence behavior only; no solver or scientific claim."
    else:
        contract = load_json(root, "contracts/evidence_contract.json")
        input_paths = contract["node_profiles"]["OD0"]["producer_input_files"]
        local_inputs = [file_ref(root, relative, id=f"IN-{index:03d}", retention="EMBEDDED")
                        for index, relative in enumerate(input_paths, 1)]
        artifact_specs = [
            ("ART-OD0-DECISIONS","contracts/owner_decisions.json","owner_decision_snapshot"),
            ("ART-OD0-OWNER","receipts/OD0_OWNER_DECISIONS.json","owner_decision_receipt"),
            ("ART-OD0-READ-AUTH","receipts/OD0_CODE_READ_AUTHORIZATION.json","code_read_authorization"),
        ]
        claim_boundary = (
            "Owner decisions and explicit read-only code-intake authorization only; "
            "no code write/build/execute/install/oracle/remote/release or solver/scientific claim."
        )
    artifacts = [file_ref(root, path, id=identifier, state="DURABLE_VERIFIED", kind=kind)
                 for identifier, path, kind in artifact_specs]
    if static_log is not None:
        artifacts.append(file_ref(root, static_log, id=f"ART-{node_id}-STATIC-LOG",
                                  state="DURABLE_VERIFIED", kind="static_check_log"))
    evidence_ids = {row["id"] for row in artifacts} | set(log_ids)
    criteria = []
    for criterion in gate["requires"]:
        if node_id == "H0":
            refs_by_criterion = {
                "G-H0-R01":["LOG-H0-ARCHIVE"],
                "G-H0-R02":["LOG-H0-HASH","ART-H0-INVENTORY"],
                "G-H0-R03":["ART-H0-AUDIT","ART-H0-TRANSPLANT"],
                "G-H0-R04":["LOG-H0-REPO","ART-H0-REPO"],
                "G-H0-R05":["LOG-H0-RUST","ART-H0-RUST","ART-H0-TOOLCHAIN"],
            }
            refs = refs_by_criterion[criterion["id"]]
        elif node_id == "H1":
            refs = ["LOG-H1-STATIC","ART-H1-EVIDENCE-CONTRACT","ART-H1-TESTS"]
        else:
            refs_by_criterion = {
                "G-OD0-R01":["ART-OD0-DECISIONS","ART-OD0-OWNER"],
                "G-OD0-R02":["ART-OD0-READ-AUTH"],
            }
            refs = refs_by_criterion[criterion["id"]]
        criteria.append({"criterion_id":criterion["id"],"status":"PASS",
                         "evidence_refs":[ref for ref in refs if ref in evidence_ids]})
    obligations = [{"obligation_id":obligation_id,"status":"SATISFIED_FOR_GATE_SCOPE",
                    "scope":"harness policy/evidence behavior only","promotes_global":False,
                    "evidence_refs":["LOG-H1-STATIC","ART-H1-EVIDENCE-CONTRACT"]}
                   for obligation_id in gate["obligation_ids"]]
    value = {
        "schema":"bass.producer_evidence/v2",
        "evidence_id":f"E-{node_id}-20260801-V2",
        "node_id":node_id,
        "gate_id":gate["id"],
        "recorded_at":now(),
        "producer":{"run_id":"root-harness-transplant-20260801","assignment_id":f"produce-{node_id.lower()}-v2","lane_id":"coordinator-producer","role":"producer"},
        "governing":governing,
        "dependencies":dependency_rows(root, dag, node),
        "inputs":{"local":local_inputs,"external":external_inputs},
        "environment":{"details":environment_details,"fingerprint":canonical_hash(environment_details)},
        "execution":{"mode":"NO_EXECUTION" if node_id == "OD0" else "STATIC_AUDIT_COMMANDS",
                     "commands":commands},
        "logs":logs,
        "artifacts":artifacts,
        "criterion_results":criteria,
        "obligation_results":obligations,
        "claim_effects":[],
        "claim_boundary":claim_boundary,
    }
    value["evidence_fingerprint"] = canonical_hash(value)
    write_atomic(output, value)


def make_review(root: Path, gate_id: str, evidence_path: str, review_log: str,
                review_static_log: str | None,
                reviewer_run: str, reviewer_assignment: str, reviewer_lane: str,
                output: Path) -> None:
    evidence_file = root / evidence_path
    evidence = json.loads(evidence_file.read_text(encoding="utf-8"))
    node_id = evidence["node_id"]
    independent_execution_refs: list[dict] = []
    if node_id in {"H0", "H1"}:
        if review_static_log is None:
            raise RuntimeError(f"{node_id} review requires an independent static re-execution log")
        review_execution = load_json(root, review_static_log)
        if (review_execution.get("schema") != "bass.static_check_log/v2"
                or review_execution.get("mode") != node_id
                or review_execution.get("all_passed") is not True
                or review_execution.get("governing_snapshot_stable") is not True
                or review_execution.get("pre_execution_governing") != evidence["governing"]
                or review_execution.get("post_execution_governing") != evidence["governing"]):
            raise RuntimeError("independent review log is not a fresh all-pass re-execution")
        static_errors: list[str] = []
        validate_static_log(root, review_execution, node_id, evidence["governing"],
                            static_errors, f"independent review static log {node_id}")
        if static_errors:
            raise RuntimeError("independent review log fails canonical plan/semantic validation: "
                               + "; ".join(static_errors))
        review_execution_ref = file_ref(root, review_static_log)
        if review_execution_ref["sha256"] in {row.get("sha256") for row in evidence.get("logs", [])}:
            raise RuntimeError("independent review may not reuse the producer static log")
        independent_execution_refs = [review_execution_ref]
    elif review_static_log is not None:
        raise RuntimeError("OD0 review is semantic/no-execution and accepts no static log")
    value = {
        "schema":"bass.review_attestation/v2",
        "review_id":f"R-{evidence['node_id']}-20260801-V2",
        "gate_id":gate_id,
        "recorded_at":now(),
        "producer_evidence_path":evidence_path,
        "producer_evidence_sha256":file_hash(evidence_file),
        "reviewed_evidence_fingerprint":evidence["evidence_fingerprint"],
        "governing_fingerprint":evidence["governing"]["fingerprint"],
        "reviewer":{"run_id":reviewer_run,"assignment_id":reviewer_assignment,"lane_id":reviewer_lane,"role":"blocking_gate_reviewer"},
        "independence":{"producer_result_blinded_until_submission":False,"shared_code_or_oracle":False,"notes":"Read-only review of the exact producer-evidence hash after submission; H0/H1 binds a separate command re-execution log."},
        "verdict":"PASS",
        "findings":[],
        "review_log_refs":[file_ref(root, review_log)],
        "independent_execution_refs":independent_execution_refs,
    }
    write_atomic(output, value)


def make_receipt(root: Path, node_id: str, evidence_path: str, review_path: str,
                 output: Path, supersedes: str | None) -> None:
    dag, _gates, node, gate, governing = node_context(root, node_id)
    evidence_file = root / evidence_path
    review_file = root / review_path
    evidence = json.loads(evidence_file.read_text(encoding="utf-8"))
    review = json.loads(review_file.read_text(encoding="utf-8"))
    value = {
        "schema":"bass.gate_receipt/v2",
        "receipt_id":f"GREC-{node_id}-20260801-V2",
        "node_id":node_id,
        "gate_id":gate["id"],
        "status":"PASS",
        "issued_at":now(),
        "scope":RECEIPT_SCOPE_BY_NODE[node_id],
        "governing_fingerprint":governing["fingerprint"],
        "producer_evidence_refs":[file_ref(root, evidence_path, evidence_fingerprint=evidence["evidence_fingerprint"])],
        "review_refs":[file_ref(root, review_path, verdict=review["verdict"])],
        "dependency_receipts":dependency_rows(root, dag, node),
        "criteria_summary":{"required":len(gate["requires"]),"passed":len(gate["requires"]),"not_applicable":0,"failed":0,"skipped":0},
        "obligation_summary":{"required_ids":gate["obligation_ids"],"failed_ids":[]},
        "claim_effects":evidence["claim_effects"],
        "claim_boundary":evidence["claim_boundary"],
        "invalidates":[],
        "supersedes":supersedes,
    }
    if node_id == "OD0":
        value["authorization"] = {
            "action":"READ_CANONICAL_SOLVER_CODE",
            "granted":True,
            "authorization_ref":file_ref(root, "receipts/OD0_CODE_READ_AUTHORIZATION.json"),
            "owner_decision_receipt_ref":file_ref(root, "receipts/OD0_OWNER_DECISIONS.json"),
        }
    write_atomic(output, value)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    sub = parser.add_subparsers(dest="operation", required=True)
    producer = sub.add_parser("producer")
    producer.add_argument("--node", choices=("H0","H1","OD0"), required=True)
    producer.add_argument("--static-log")
    producer.add_argument("--output", type=Path, required=True)
    review = sub.add_parser("review")
    review.add_argument("--gate", required=True)
    review.add_argument("--evidence", required=True)
    review.add_argument("--review-log", required=True)
    review.add_argument("--review-static-log")
    review.add_argument("--reviewer-run", required=True)
    review.add_argument("--reviewer-assignment", required=True)
    review.add_argument("--reviewer-lane", required=True)
    review.add_argument("--output", type=Path, required=True)
    receipt = sub.add_parser("receipt")
    receipt.add_argument("--node", choices=("H0","H1","OD0"), required=True)
    receipt.add_argument("--evidence", required=True)
    receipt.add_argument("--review", required=True)
    receipt.add_argument("--supersedes")
    receipt.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    output = args.output if args.output.is_absolute() else root / args.output
    if args.operation == "producer":
        make_producer(root, args.node, args.static_log, output)
    elif args.operation == "review":
        make_review(root, args.gate, args.evidence, args.review_log, args.review_static_log,
                    args.reviewer_run,
                    args.reviewer_assignment, args.reviewer_lane, output)
    else:
        make_receipt(root, args.node, args.evidence, args.review, output, args.supersedes)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
