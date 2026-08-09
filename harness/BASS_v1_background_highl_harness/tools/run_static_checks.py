#!/usr/bin/env python3
"""Capture honest, bounded H0/H1 static-check command records as JSON."""

from __future__ import annotations

import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

HARNESS_ROOT = Path(__file__).resolve().parents[1]
if str(HARNESS_ROOT) not in sys.path:
    sys.path.insert(0, str(HARNESS_ROOT))
from tools.validate_harness import governing_snapshot, load_json, validate_static_log
from tools.static_plan import (
    command_plan_fingerprint, execution_context, expected_command_plan,
)


def now() -> str:
    return datetime.now().astimezone().isoformat(timespec="microseconds")


def run(command_id: str, argv: list[str], cwd: Path) -> dict:
    started = now()
    completed = subprocess.run(argv, cwd=cwd, text=True, capture_output=True, check=False)
    ended = now()
    return {
        "id": command_id,
        "argv": argv,
        "cwd": str(cwd.resolve()),
        "started_at": started,
        "ended_at": ended,
        "exit_code": completed.returncode,
        "timed_out": False,
        "signal": None,
        "skipped": False,
        "fallback_used": False,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "result": "PASS" if completed.returncode == 0 else "FAIL",
    }


def tested_governing_snapshot(root: Path, node_id: str) -> dict:
    dag = load_json(root, "state/dag.json")
    gates = load_json(root, "state/gates.json")
    contract = load_json(root, "contracts/evidence_contract.json")
    node = next(row for row in dag["nodes"] if row["id"] == node_id)
    gate = next(row for row in gates["gates"] if row["id"] == node["gate_id"])
    errors: list[str] = []
    snapshot = governing_snapshot(root, node_id, gate, node, contract, errors)
    if errors or snapshot is None:
        raise RuntimeError("cannot bind static run to governing bytes: " + "; ".join(errors))
    return snapshot


def command_specs(plan: list[dict]) -> list[tuple[str, list[str], Path]]:
    return [(row["id"], row["argv"], Path(row["cwd"])) for row in plan]


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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("H0", "H1"))
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    started = now()
    pre_execution_governing = tested_governing_snapshot(root, args.mode)
    if args.mode == "H0":
        with tempfile.TemporaryDirectory(prefix="bass-h0-static-") as directory:
            temporary = Path(directory)
            (temporary / "gnupg").mkdir(mode=0o700)
            context = execution_context("H0", root, sys.executable, temporary)
            plan = expected_command_plan("H0", context)
            records = [run(command_id, argv, cwd)
                       for command_id, argv, cwd in command_specs(plan)]
    else:
        context = execution_context("H1", root, sys.executable)
        plan = expected_command_plan("H1", context)
        records = [run(command_id, argv, cwd)
                   for command_id, argv, cwd in command_specs(plan)]
    expected_rust_hash = "294b3d81fa72e62581276290c60c81eb8b58498d333d422ca1dfc432877d0c40"
    expected_key = "108F66205EAEB0AAA8DD5E1C85AB96E6FA1BE5FE"
    if args.mode == "H0":
        by_id = {row["id"]: row for row in records}
        if not by_id["CMD-H0-010"]["stdout"].startswith(expected_rust_hash + "  "):
            by_id["CMD-H0-010"]["result"] = "FAIL"
        if expected_key not in by_id["CMD-H0-015"]["stdout"].replace(":", ""):
            by_id["CMD-H0-015"]["result"] = "FAIL"
        if "Good signature" not in by_id["CMD-H0-016"]["stderr"]:
            by_id["CMD-H0-016"]["result"] = "FAIL"
        expected_commit = "539fcd6acc81dfd19d05951c2c5cbc3602eda077"
        if by_id["CMD-H0-017"]["stdout"].strip() != "https://github.com/cosmosapjw-quantum/bianchi_phase_r.git":
            by_id["CMD-H0-017"]["result"] = "FAIL"
        if re_full_sha(by_id["CMD-H0-018"]["stdout"].strip()) is False:
            by_id["CMD-H0-018"]["result"] = "FAIL"
        remote_lines = by_id["CMD-H0-019"]["stdout"].splitlines()
        if len(remote_lines) != 2 or any(not line.startswith(expected_commit + "\t") for line in remote_lines):
            by_id["CMD-H0-019"]["result"] = "FAIL"
    post_execution_governing = tested_governing_snapshot(root, args.mode)
    snapshot_stable = pre_execution_governing == post_execution_governing
    ended = now()
    value = {
        "schema": "bass.static_check_log/v2",
        "mode": args.mode,
        "started_at": started,
        "ended_at": ended,
        "pre_execution_governing": pre_execution_governing,
        "post_execution_governing": post_execution_governing,
        "governing_snapshot_stable": snapshot_stable,
        "execution_context": context,
        "command_plan_fingerprint": command_plan_fingerprint(plan),
        "commands": records,
        "all_passed": snapshot_stable and all(row["result"] == "PASS" for row in records),
    }
    semantic_errors: list[str] = []
    if value["all_passed"]:
        validate_static_log(root, value, args.mode, pre_execution_governing,
                            semantic_errors, f"runner self-check {args.mode}")
        if semantic_errors:
            value["all_passed"] = False
    output = args.output if args.output.is_absolute() else root / args.output
    write_atomic(output, value)
    print(json.dumps({"output":str(output),"commands":len(records),
                      "all_passed":value["all_passed"],
                      "semantic_error_count":len(semantic_errors)}))
    for error in semantic_errors:
        print(error, file=sys.stderr)
    return 0 if value["all_passed"] else 1


def re_full_sha(value: str) -> bool:
    return len(value) == 40 and all(character in "0123456789abcdef" for character in value)


if __name__ == "__main__":
    raise SystemExit(main())
