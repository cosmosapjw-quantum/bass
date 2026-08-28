#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import NoReturn

ROOT = Path(__file__).resolve().parent
PACKAGE_ID = "BASS-RF04-SCI-AUTH-INTAKE-20260828-R1"
RF03_BRANCH = "agent/architecture/rust-first-rf03-20260828-r2"
RF03_HEAD = "6e53664d56694f7a7ad5f65be262302d5c8866b2"
RF03_TREE = "bb743717e8115821d72268d8384dc5cc7cc11975"
RF02B_BRANCH = "agent/architecture/rust-first-rf02b-20260826-r1"
RF02B_HEAD = "0563c080e54fcd90d6160bec35e4f20d240d8d2e"
RF02B_TREE = "40ae99f9e7465d6332e98b65a5269a1f71eadfb5"
WORK_GRAPH_PATH = "docs/audits/science_system_differential_20260826/WORK_UNITS.json"
WORK_GRAPH_BLOB = "026afd0348d29b0afa90d30fcf8a11b9cf1187dd"
KINETIC_PATH = "_rustcore/src/kinetic"
KINETIC_TREE = "de19a1472a69d8ef3879a30dd67d1d90df193e07"
FILES = {
    "README.md", "PACKAGE.json", "CURRENT_STATE.json", "DAG.json",
    "SOURCE_INVENTORY.json", "WORK_UNITS.json", "ACCEPTANCE_MATRIX.json",
    "IMPLEMENTATION_PLAN.md", "CODEX_HANDOFF.md",
    "GITHUB_ROUNDTRIP_RECEIPT.json", "validate_package.py"
}

def fail(message: str) -> NoReturn:
    raise SystemExit("FAIL: " + message)

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "--no-replace-objects", *args], cwd=repo, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30
    )
    if result.returncode:
        fail("git " + " ".join(args) + ": " + result.stderr.strip())
    return result.stdout.removesuffix("\n")

def local() -> None:
    entries = {}
    for line in (ROOT / "MANIFEST.sha256").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, name = line.split(maxsplit=1)
        if name in entries:
            fail("duplicate manifest entry " + name)
        entries[name] = digest
    if set(entries) != FILES:
        fail("manifest closure")
    for name, digest in entries.items():
        if sha(ROOT / name) != digest:
            fail(name + " digest")

    package = json.loads((ROOT / "PACKAGE.json").read_text(encoding="utf-8"))
    if package.get("package_id") != PACKAGE_ID:
        fail("package id")
    if package["execution"]["exact_next_action"] != "SCI-AUTH-04":
        fail("next action")
    if package["current_source"]["head"] != RF03_HEAD:
        fail("RF03 head in package")
    if package["claim_boundary"]["current"] != "NO_PASS_SCI_AUTH_04_AND_NO_PASS_RF04":
        fail("claim boundary")

    dag = json.loads((ROOT / "DAG.json").read_text(encoding="utf-8"))
    ids = [node["id"] for node in dag["nodes"]]
    if len(ids) != len(set(ids)):
        fail("duplicate DAG node")
    edges = dag["edges"]
    known = set(ids)
    if any(a not in known or b not in known for a, b in edges):
        fail("DAG edge endpoint")
    incoming = {node: 0 for node in ids}
    outgoing = {node: [] for node in ids}
    for a, b in edges:
        incoming[b] += 1
        outgoing[a].append(b)
    queue = [node for node, count in incoming.items() if count == 0]
    seen = 0
    while queue:
        node = queue.pop()
        seen += 1
        for child in outgoing[node]:
            incoming[child] -= 1
            if incoming[child] == 0:
                queue.append(child)
    if seen != len(ids):
        fail("DAG cycle")
    if ["SCI-AUTH-04", "RF04-INTAKE-00"] not in edges:
        fail("authority dependency")
    if ["RF04-INTAKE-00", "RF-04"] not in edges:
        fail("RF04 join")

    units = json.loads((ROOT / "WORK_UNITS.json").read_text(encoding="utf-8"))
    if units["exact_next_action"] != "SCI-AUTH-04":
        fail("work-unit next action")
    if [u["id"] for u in units["work_units"]] != ["SCI-AUTH-04", "RF04-INTAKE-00", "RF-04"]:
        fail("work-unit closure")

def live(repo_arg: Path) -> None:
    repo = Path(git(repo_arg, "rev-parse", "--show-toplevel"))
    for branch, head, tree in (
        (RF03_BRANCH, RF03_HEAD, RF03_TREE),
        (RF02B_BRANCH, RF02B_HEAD, RF02B_TREE),
    ):
        if git(repo, "rev-parse", "--verify", "refs/remotes/origin/" + branch) != head:
            fail(branch + " moved")
        if git(repo, "rev-parse", head + "^{tree}") != tree:
            fail(branch + " tree")
    if git(repo, "rev-parse", RF03_HEAD + ":" + WORK_GRAPH_PATH) != WORK_GRAPH_BLOB:
        fail("compiled work graph blob")
    if git(repo, "rev-parse", RF03_HEAD + ":" + KINETIC_PATH) != KINETIC_TREE:
        fail("kinetic tree")
    for absent in ("_rustcore/src/collision", "_rustcore/src/kato", "_rustcore/src/polarization"):
        result = subprocess.run(
            ["git", "cat-file", "-e", RF03_HEAD + ":" + absent],
            cwd=repo, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        if result.returncode == 0:
            fail("source inventory changed: " + absent + " now exists")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()
    local()
    if args.live:
        live(Path(args.repo))
    print(json.dumps({
        "status": "PASS",
        "package_id": PACKAGE_ID,
        "rf03_head": RF03_HEAD,
        "rf03_tree": RF03_TREE,
        "sci_auth_base": RF02B_HEAD,
        "kinetic_tree": KINETIC_TREE,
        "exact_next_action": "SCI-AUTH-04",
        "claim": "NO_PASS_SCI_AUTH_04_AND_NO_PASS_RF04",
        "live": args.live,
    }, sort_keys=True))
