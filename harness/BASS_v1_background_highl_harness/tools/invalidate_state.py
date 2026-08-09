#!/usr/bin/env python3
"""Compute or apply transitive fail-closed DAG invalidation."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile

CHECKPOINT_BY_NODE = {
    "H0":"H0_INPUT_AUDIT", "H1":"H1_INSTALLATION_SELF_TEST",
    "OD0":"OD0_SCOPE_CONFIRMATION", "C0":"C0_CODE_INTAKE",
    "C1":"C1_CODE_REALITY_AUDIT", "IA0":"IA0_IMPLEMENTATION_AUTHORIZATION",
    "C2":"C2_EQUATION_CODE_MAP", "C3":"C3_BIANCHI_FAMILY_DYNAMICS",
    "C4":"C4_ANALYTIC_LIMITS", "C5":"C5_HIGH_ELL_CONVERGENCE",
    "C6":"C6_COLLISION_HISTORY", "C7":"C7_TILT_POLARIZATION",
    "C8":"C8_BACKEND_OUTPUT_EQUIVALENCE", "C9":"C9_RELEASE_HOSTILE_AUDIT",
    "C10":"C10_OWNER_RELEASE_DECISION", "TERMINAL":"TERMINAL_RELEASE",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def downstream_nodes(dag: dict, start: str) -> list[str]:
    nodes = dag["nodes"]
    known = {row["id"] for row in nodes}
    if start not in known:
        raise ValueError(f"unknown node: {start}")
    affected = {start}
    changed = True
    while changed:
        changed = False
        for row in nodes:
            if row["id"] not in affected and affected.intersection(row.get("depends_on", [])):
                affected.add(row["id"])
                changed = True
    return [row["id"] for row in nodes if row["id"] in affected]


def write_json_atomic(path: Path, value: dict) -> None:
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(value, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def invalidate(root: Path, start: str, reason: str, apply: bool = False) -> dict:
    if re.fullmatch(r"[A-Z][A-Z0-9_]{2,63}", reason) is None:
        raise ValueError("reason must be an uppercase machine code, not free-form instructions")
    dag_path = root / "state/dag.json"
    gates_path = root / "state/gates.json"
    run_path = root / "state/run_state.json"
    scope_path = root / "contracts/scope_lock.json"
    dag = json.loads(dag_path.read_text(encoding="utf-8"))
    gates = json.loads(gates_path.read_text(encoding="utf-8"))
    run_state = json.loads(run_path.read_text(encoding="utf-8"))
    scope = json.loads(scope_path.read_text(encoding="utf-8"))
    affected = downstream_nodes(dag, start)
    gate_by_node = {row["id"]: row["gate_id"] for row in dag["nodes"]}
    affected_gates = {gate_by_node[node_id] for node_id in affected}
    report = {"from_node":start,"reason_code":reason,"affected_nodes":affected,"affected_gates":sorted(affected_gates),"applied":apply}
    if not apply:
        return report
    for row in dag["nodes"]:
        if row["id"] in affected and row["status"] != "NOT_APPLICABLE":
            prior_receipt = row.get("receipt")
            prior_path = root / prior_receipt if prior_receipt is not None else None
            prior_ref = ({"path":prior_receipt, "bytes":prior_path.stat().st_size,
                          "sha256":sha256(prior_path)}
                         if prior_path is not None and prior_path.is_file() else None)
            row["status"] = "BLOCKED"
            row["receipt"] = None
            row["invalidation"] = {"reason_code":reason,"prior_receipt_ref":prior_ref}
    for row in gates["gates"]:
        if row["id"] in affected_gates and row["status"] != "NOT_APPLICABLE":
            row["status"] = "BLOCKED"
    run_state["current_node"] = start
    run_state["next_node"] = start
    run_state["current_phase"] = "INVALIDATION_REMEDIATION"
    run_state["artifact_status"] = "DURABLE_UNVERIFIED"
    latest_pass = next((row["id"] for row in reversed(dag["nodes"])
                        if row["status"] == "PASS"), None)
    run_state["last_durable_checkpoint"] = CHECKPOINT_BY_NODE.get(
        latest_pass, "NO_DURABLE_CHECKPOINT")
    run_state["blocker_codes"] = [f"INVALIDATION_{start}_{reason}"]
    run_state["resume_action"] = "REMEDIATE_INVALIDATED_NODE"
    scope["current_phase"] = "INVALIDATION_REMEDIATION"
    for authorization in scope["authorizations"]:
        scope["authorizations"][authorization] = False
    write_json_atomic(dag_path, dag)
    write_json_atomic(gates_path, gates)
    write_json_atomic(run_path, run_state)
    write_json_atomic(scope_path, scope)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--from-node", required=True)
    parser.add_argument("--reason", required=True,
                        help="uppercase machine code such as GOVERNING_BYTES_CHANGED")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    print(json.dumps(invalidate(args.root.resolve(), args.from_node, args.reason, args.apply), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
