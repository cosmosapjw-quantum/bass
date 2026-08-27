#!/usr/bin/env python3
"""Validate the RF-02C / legacy optimization integration execution package."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any, NoReturn

ROOT = Path(__file__).resolve().parent
EXPECTED_FILES = {
    "README.md",
    "CURRENT_STATE.json",
    "WORK_UNITS.json",
    "ACCEPTANCE_MATRIX.json",
    "IMPLEMENTATION_PLAN.md",
    "CODEX_HANDOFF.md",
    "validate_package.py",
}


def fail(message: str) -> NoReturn:
    raise SystemExit(f"FAIL: {message}")


def load_json(name: str) -> dict[str, Any]:
    path = ROOT / name
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"{name}: invalid JSON: {exc}")
    if not isinstance(value, dict):
        fail(f"{name}: top level must be an object")
    return value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_manifest() -> None:
    manifest = ROOT / "MANIFEST.sha256"
    entries: dict[str, str] = {}
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        parts = line.split(maxsplit=1)
        if len(parts) != 2:
            fail(f"MANIFEST.sha256 malformed line: {line!r}")
        digest, name = parts
        name = name.lstrip("*")
        if name in entries:
            fail(f"duplicate manifest entry: {name}")
        entries[name] = digest
    if set(entries) != EXPECTED_FILES:
        fail(
            "manifest closure mismatch: "
            f"missing={sorted(EXPECTED_FILES-set(entries))} "
            f"extra={sorted(set(entries)-EXPECTED_FILES)}"
        )
    for name, expected in entries.items():
        actual = sha256(ROOT / name)
        if actual != expected:
            fail(f"{name}: sha256 {actual} != {expected}")


def topological_order(units: list[dict[str, Any]]) -> list[str]:
    by_id = {u["id"]: u for u in units}
    if len(by_id) != len(units):
        fail("duplicate work-unit id")
    indegree = {name: 0 for name in by_id}
    children = {name: [] for name in by_id}
    for unit in units:
        for dep in unit.get("dependencies", []):
            if dep not in by_id:
                fail(f"{unit['id']}: missing dependency {dep}")
            indegree[unit["id"]] += 1
            children[dep].append(unit["id"])
    queue = sorted(name for name, degree in indegree.items() if degree == 0)
    order: list[str] = []
    while queue:
        name = queue.pop(0)
        order.append(name)
        for child in sorted(children[name]):
            indegree[child] -= 1
            if indegree[child] == 0:
                queue.append(child)
                queue.sort()
    if len(order) != len(units):
        fail("work-unit graph is cyclic")
    return order


def validate_bass11_native_delta_policy(by_id: dict[str, dict[str, Any]]) -> None:
    policy = by_id["BASS-11"].get("entry", {}).get("dirty_path_policy", {})
    exact = policy.get("exact_files")
    prefixes = policy.get("allowed_prefixes")
    required_prefix = policy.get("required_native_delta_prefix")
    forbidden = policy.get("forbidden_stale_prefixes")

    expected_exact = [
        "artifacts/rust_first_runtime/rf02c/EVIDENCE.json",
        "artifacts/rust_first_runtime/rf02c/changed_paths.json",
    ]
    expected_prefix = "artifacts/rust_first_runtime/rf02c/native_delta/"

    if exact != expected_exact:
        fail(f"BASS-11 dirty_path_policy exact_files mismatch: {exact!r}")
    if prefixes != [expected_prefix]:
        fail(f"BASS-11 allowed_prefixes must be {[expected_prefix]!r}: {prefixes!r}")
    if required_prefix != expected_prefix:
        fail(f"BASS-11 required_native_delta_prefix mismatch: {required_prefix!r}")
    if forbidden != ["repro/native/"]:
        fail(f"BASS-11 forbidden_stale_prefixes must contain only repro/native/: {forbidden!r}")

    handoff = (ROOT / "CODEX_HANDOFF.md").read_text(encoding="utf-8")
    plan = (ROOT / "IMPLEMENTATION_PLAN.md").read_text(encoding="utf-8")
    for name, text in (("CODEX_HANDOFF.md", handoff), ("IMPLEMENTATION_PLAN.md", plan)):
        if expected_prefix not in text:
            fail(f"{name}: corrected native-delta prefix missing")
        if "repro/native/**" in text and "stale" not in text:
            fail(f"{name}: stale repro/native/** appears as active policy")


def validate_structure() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    state = load_json("CURRENT_STATE.json")
    graph = load_json("WORK_UNITS.json")
    matrix = load_json("ACCEPTANCE_MATRIX.json")
    package_ids = {state.get("package_id"), graph.get("package_id"), matrix.get("package_id")}
    if len(package_ids) != 1 or None in package_ids:
        fail(f"package_id mismatch: {sorted(map(str, package_ids))}")
    units = graph.get("work_units")
    if not isinstance(units, list) or not units:
        fail("WORK_UNITS.json: work_units must be a non-empty list")
    order = topological_order(units)
    expected = {"BASS-11", "BASS-12", "BASS-13", "BASS-14", "BASS-15"}
    ids = {u["id"] for u in units}
    if ids != expected:
        fail(f"unexpected work-unit ids: {sorted(ids)}")
    if graph.get("exact_next_action") != "BASS-11":
        fail("exact_next_action must be BASS-11")
    if state.get("current_action", {}).get("id") != "BASS-11":
        fail("CURRENT_STATE current_action must be BASS-11")
    by_id = {u["id"]: u for u in units}
    required_deps = {
        "BASS-11": [],
        "BASS-12": [],
        "BASS-13": ["BASS-11", "BASS-12"],
        "BASS-14": ["BASS-13"],
        "BASS-15": ["BASS-14"],
    }
    for name, deps in required_deps.items():
        if by_id[name].get("dependencies") != deps:
            fail(f"{name}: dependencies must be {deps}")
    if set(matrix.get("matrix", {})) != expected:
        fail("ACCEPTANCE_MATRIX does not cover exactly BASS-11..BASS-15")
    if order.index("BASS-13") < max(order.index("BASS-11"), order.index("BASS-12")):
        fail("BASS-13 precedes a required predecessor")

    validate_bass11_native_delta_policy(by_id)
    return state, graph, matrix


def run_git(args: list[str], cwd: Path) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode:
        fail(f"git {' '.join(args)}: {result.stderr.strip()}")
    return result.stdout.strip()


def validate_live(state: dict[str, Any]) -> None:
    repo_root_raw = run_git(["rev-parse", "--show-toplevel"], ROOT)
    repo_root = Path(repo_root_raw)
    contract = repo_root / "docs/rust_first_runtime/RF02C_EXECUTION_CONTRACT_V2.json"
    if not contract.is_file():
        fail(f"missing V2 contract: {contract}")
    expected_contract = "804826b9d5ce2f3333de0558447e351a8050dc8147d268e8a6055b6c5669e51c"
    if sha256(contract) != expected_contract:
        fail("RF02C_EXECUTION_CONTRACT_V2.json SHA-256 mismatch")
    source = state["source_authority"]["rf02c_remote_precloseout"]
    base = source["head"]
    branch = source["branch"]
    remote_ref = f"origin/{branch}"
    run_git(["rev-parse", "--verify", remote_ref], repo_root)
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", base, remote_ref],
        cwd=repo_root,
        check=False,
    )
    if result.returncode != 0:
        fail(f"{base} is not an ancestor of {remote_ref}")
    legacy = state["source_authority"]["legacy_performance_anchor"]
    legacy_ref = f"origin/{legacy['branch']}"
    actual = run_git(["rev-parse", "--verify", legacy_ref], repo_root)
    if actual != legacy["head"]:
        fail(f"legacy anchor moved: {actual} != {legacy['head']}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    validate_manifest()
    state, graph, _matrix = validate_structure()
    if args.live:
        validate_live(state)
    print(json.dumps({
        "status": "PASS",
        "package_id": state["package_id"],
        "exact_next_action": graph["exact_next_action"],
        "work_units": len(graph["work_units"]),
        "manifest_entries": len(EXPECTED_FILES),
        "native_delta_prefix": "artifacts/rust_first_runtime/rf02c/native_delta/",
        "live": args.live,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
