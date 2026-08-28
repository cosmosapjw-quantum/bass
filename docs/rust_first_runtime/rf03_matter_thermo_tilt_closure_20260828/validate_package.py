#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, NoReturn

ROOT = Path(__file__).resolve().parent
PACKAGE_ID = 'BASS-RF03-MATTER-THERMO-TILT-CLOSURE-20260828-R1'
REVISION = 'R1_RF02C_TERMINAL_BASE'
BASE_BRANCH = 'agent/architecture/rust-first-rf02c-20260826-r1'
BASE_HEAD = 'dfa17457d402bd441d3fdf786c2d79c529512ee5'
BASE_TREE = '9fc67fb0ba10e091e25a14d7e1fac88b77a0241e'
PACKAGE_BRANCH = 'agent/plans/rf03-matter-thermo-tilt-closure-20260828-r1'
IMPLEMENTATION_BRANCH = 'agent/architecture/rust-first-rf03-20260828-r1'

EXPECTED_MANIFEST = {
    "README.md",
    "CURRENT_STATE.json",
    "SOURCE_INVENTORY.json",
    "WORK_UNITS.json",
    "ACCEPTANCE_MATRIX.json",
    "IMPLEMENTATION_PLAN.md",
    "CODEX_HANDOFF.md",
    "validate_package.py",
}

EXPECTED_COMPILED_SCOPE = ['_rustcore/src/matter/**', '_rustcore/src/thermo/**', '_rustcore/src/tilt/**', 'bianchi/matter/**', 'bianchi/thermo/**', 'bianchi/tilt/**', 'tests/rf03/**', '.github/workflows/rf03*.yml', 'artifacts/rust_first_runtime/rf03/**', 'docs/rust_first_runtime/**']
EXPECTED_INTEGRATION_EXTENSION = ['_rustcore/src/lib.rs', '_rustcore/src/python/mod.rs', '_rustcore/src/python/register.rs', '_rustcore/src/python/rf03_matter.rs', '_rustcore/src/python/rf03_thermo.rs', '_rustcore/src/python/rf03_tilt.rs', 'bianchi/backend_policy.py']

EXPECTED_BLOBS = {
    "_rustcore/src/lib.rs": "3d50866e6d492762135086bb980c893f636c8d3a",
    "_rustcore/src/thermo/mod.rs": "695301b3280771dc410f2c5bb454cedfda44e11f",
    "_rustcore/src/thermo/dof.rs": "801f432538c63dbd23395885e94214288e48e4cf",
    "_rustcore/src/thermo/dof_table.rs": "a714b8d6cf1515e064f72ae6f25725dc09f50279",
    "_rustcore/src/thermo/fd.rs": "9c1a4ef4dd1743cab30e3ebf3212edbff5d28062",
    "bianchi/matter/tilted_rust.py": "e447ce30f80c173e69764150c329b911809af5bd",
    "bianchi/thermo/temperature.py": "4b792b04df072446a5d046524ea5323e4237d7e4",
    "bianchi/thermo/history_api.py": "f88d7a9459e9b40f87a6d5711d6a64e9a839eb37",
    "bianchi/backend_policy.py": "a8b690b9f5d7494fd3822ddaae5343ad83d23831",
}

def fail(message: str) -> NoReturn:
    raise SystemExit(f"FAIL: {message}")

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load(name: str) -> dict[str, Any]:
    value = json.loads((ROOT / name).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        fail(f"{name} top level must be an object")
    return value

def validate_manifest() -> int:
    entries: dict[str, str] = {}
    for line in (ROOT / "MANIFEST.sha256").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, name = line.split(maxsplit=1)
        if name in entries:
            fail(f"duplicate manifest entry {name}")
        entries[name] = digest
    if set(entries) != EXPECTED_MANIFEST:
        fail(f"manifest closure mismatch: {sorted(entries)}")
    for name, digest in entries.items():
        if sha256(ROOT / name) != digest:
            fail(f"{name} digest mismatch")
    return len(entries)

def validate_structure() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    state = load("CURRENT_STATE.json")
    inventory = load("SOURCE_INVENTORY.json")
    graph = load("WORK_UNITS.json")
    matrix = load("ACCEPTANCE_MATRIX.json")

    for name, value in (
        ("CURRENT_STATE", state),
        ("SOURCE_INVENTORY", inventory),
        ("WORK_UNITS", graph),
        ("ACCEPTANCE_MATRIX", matrix),
    ):
        if value.get("package_id") != PACKAGE_ID:
            fail(f"{name} package_id mismatch")

    if state.get("package_revision") != REVISION or graph.get("package_revision") != REVISION:
        fail("package revision mismatch")
    if graph.get("exact_next_action") != "RF-03":
        fail("exact_next_action must be RF-03")
    units = graph.get("work_units")
    if not isinstance(units, list) or len(units) != 1 or units[0].get("id") != "RF-03":
        fail("package must contain exactly one RF-03 work unit")
    unit = units[0]
    if unit.get("dependencies") != ["RF-02C"]:
        fail("RF-03 dependency must be RF-02C only")
    forbidden_dependency_tokens = {"BASS-12", "BASS-13", "BASS-14", "BASS-15"}
    if forbidden_dependency_tokens.intersection(unit.get("dependencies", [])):
        fail("legacy optimization dependency leaked into RF-03")

    entry = unit.get("entry", {})
    if entry.get("base_branch") != BASE_BRANCH or entry.get("base_head") != BASE_HEAD or entry.get("base_tree") != BASE_TREE:
        fail("RF-03 base identity mismatch")
    if entry.get("implementation_branch") != IMPLEMENTATION_BRANCH:
        fail("implementation branch mismatch")
    if entry.get("package_branch") != PACKAGE_BRANCH:
        fail("package branch mismatch")

    scope = unit.get("scope", {})
    if scope.get("compiled_allowed_paths") != EXPECTED_COMPILED_SCOPE:
        fail("compiled RF-03 scope mismatch")
    if scope.get("run_local_user_authorized_integration_extension") != EXPECTED_INTEGRATION_EXTENSION:
        fail("integration extension mismatch")
    if "bianchi/backend_policy.py" not in EXPECTED_INTEGRATION_EXTENSION:
        fail("route-policy integration path missing")
    if "_rustcore/Cargo.toml and _rustcore/Cargo.lock unless a reproduced compile failure receives a separate explicit authorization" not in scope.get("forbidden_paths", []):
        fail("Cargo scope guard missing")

    roles = unit.get("commit_policy", {}).get("roles", [])
    if unit.get("commit_policy", {}).get("max_commits") != 3 or len(roles) != 3:
        fail("role-based commit policy mismatch")
    if roles[-1].get("role") != "TERMINAL_EVIDENCE":
        fail("terminal evidence role missing")

    if matrix.get("matrix", {}).get("RF-03", {}).get("claim") != ["PASS_RF03"]:
        fail("acceptance claim mismatch")

    source_blobs = {
        item["path"]: item.get("git_blob_sha1")
        for item in inventory.get("reality_map", [])
        if item.get("git_blob_sha1")
    }
    for path, digest in EXPECTED_BLOBS.items():
        if source_blobs.get(path) != digest:
            fail(f"source inventory blob mismatch for {path}")

    all_text = "\n".join(
        (ROOT / name).read_text(encoding="utf-8")
        for name in EXPECTED_MANIFEST
        if name != "validate_package.py"
    )
    placeholder_token = "<" + "PLACEHOLDER>"
    todo_token = "TODO" + "_FILL"
    if placeholder_token in all_text or todo_token in all_text:
        fail("unresolved placeholder")
    return state, inventory, graph

def git(args: list[str], cwd: Path) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode:
        fail(f"git {' '.join(args)}: {result.stderr.strip()}")
    return result.stdout.strip()

def validate_live(inventory: dict[str, Any]) -> None:
    repo = Path(git(["rev-parse", "--show-toplevel"], ROOT))
    remote_ref = f"origin/{BASE_BRANCH}"
    remote_head = git(["rev-parse", "--verify", remote_ref], repo)
    if remote_head != BASE_HEAD:
        fail(f"RF-02C terminal branch moved: {remote_head}")
    tree = git(["rev-parse", f"{BASE_HEAD}^{{tree}}"], repo)
    if tree != BASE_TREE:
        fail(f"RF-02C terminal tree mismatch: {tree}")
    for path, expected in EXPECTED_BLOBS.items():
        observed = git(["rev-parse", f"{BASE_HEAD}:{path}"], repo)
        if observed != expected:
            fail(f"live blob mismatch for {path}: {observed}")
    impl_ref = f"refs/remotes/origin/{IMPLEMENTATION_BRANCH}"
    exists = subprocess.run(
        ["git", "show-ref", "--verify", "--quiet", impl_ref],
        cwd=repo,
    ).returncode == 0
    if exists:
        impl_head = git(["rev-parse", impl_ref], repo)
        result = subprocess.run(
            ["git", "merge-base", "--is-ancestor", BASE_HEAD, impl_head],
            cwd=repo,
        )
        if result.returncode:
            fail("existing RF-03 implementation branch does not descend from the frozen RF-02C base")

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()

    manifest_count = validate_manifest()
    state, inventory, graph = validate_structure()
    if args.live:
        validate_live(inventory)

    print(json.dumps({
        "status": "PASS",
        "package_id": PACKAGE_ID,
        "revision": REVISION,
        "exact_next_action": "RF-03",
        "base_head": BASE_HEAD,
        "base_tree": BASE_TREE,
        "implementation_branch": IMPLEMENTATION_BRANCH,
        "manifest_entries": manifest_count,
        "live": args.live,
    }, sort_keys=True))

if __name__ == "__main__":
    main()
