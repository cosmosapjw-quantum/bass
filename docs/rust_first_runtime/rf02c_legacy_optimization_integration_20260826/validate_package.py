#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, subprocess
from pathlib import Path
from typing import Any, NoReturn

ROOT = Path(__file__).resolve().parent
EXPECTED_MANIFEST = {
    "README.md", "CURRENT_STATE.json", "WORK_UNITS.json",
    "ACCEPTANCE_MATRIX.json", "IMPLEMENTATION_PLAN.md",
    "CODEX_HANDOFF.md", "validate_package.py",
}
PACKAGE_ID = "BASS-RF02C-LEGACY-OPT-INTEGRATION-20260826-R1"
REVISION = "R2_POST_CLOSEOUT_NATIVE_MERGE_RECONCILIATION_20260827"
CURRENT_HEAD = "c777ebb68c82aa8b9898f92159c2346a6e8ef892"
CURRENT_TREE = "524a541261c0384eedd79267671215dccd9c7147"
CORRECT_NATIVE_PREFIX = "artifacts/rust_first_runtime/rf02c/native_delta/"
STALE_NATIVE_PREFIX = "repro/native/"

def fail(msg: str) -> NoReturn:
    raise SystemExit(f"FAIL: {msg}")

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()

def load(name: str) -> dict[str, Any]:
    obj = json.loads((ROOT / name).read_text())
    if not isinstance(obj, dict):
        fail(f"{name}: top level must be object")
    return obj

def manifest() -> None:
    entries = {}
    for line in (ROOT / "MANIFEST.sha256").read_text().splitlines():
        if not line.strip():
            continue
        digest, name = line.split(maxsplit=1)
        if name in entries:
            fail(f"duplicate manifest entry {name}")
        entries[name] = digest
    if set(entries) != EXPECTED_MANIFEST:
        fail(f"manifest closure mismatch {sorted(entries)}")
    for name, digest in entries.items():
        if sha256(ROOT / name) != digest:
            fail(f"{name}: digest mismatch")

def topo(units):
    by = {u["id"]: u for u in units}
    indeg = {k: 0 for k in by}
    children = {k: [] for k in by}
    for u in units:
        for dep in u.get("dependencies", []):
            if dep not in by:
                fail(f"{u['id']}: missing dep {dep}")
            indeg[u["id"]] += 1
            children[dep].append(u["id"])
    q = sorted(k for k, v in indeg.items() if v == 0)
    out = []
    while q:
        k = q.pop(0)
        out.append(k)
        for child in children[k]:
            indeg[child] -= 1
            if indeg[child] == 0:
                q.append(child)
                q.sort()
    if len(out) != len(by):
        fail("cyclic DAG")
    return out

def structure():
    state = load("CURRENT_STATE.json")
    graph = load("WORK_UNITS.json")
    matrix = load("ACCEPTANCE_MATRIX.json")
    if state["package_id"] != PACKAGE_ID or graph["package_id"] != PACKAGE_ID or matrix["package_id"] != PACKAGE_ID:
        fail("package_id mismatch")
    if state.get("package_revision") != REVISION or graph.get("package_revision") != REVISION:
        fail("package revision mismatch")
    if state["current_action"]["id"] != "BASS-11" or graph["exact_next_action"] != "BASS-11":
        fail("exact next action must be BASS-11")
    units = graph["work_units"]
    by = {u["id"]: u for u in units}
    if set(by) != {"BASS-11", "BASS-12", "BASS-13", "BASS-14", "BASS-15"}:
        fail("unexpected work units")
    topo(units)
    b11 = by["BASS-11"]
    budget = b11["commit_budget"]
    if budget.get("count") != 2:
        fail("BASS-11 must authorize exactly two reconciliation commits")
    required_c1 = {
        ".github/workflows/rf02c-preflight.yml",
        "bianchi/backend_policy.py",
        "tests/test_backend_policy.py",
        "tests/test_rf00_policy_adversarial.py",
        "tests/test_rf00_route_inventory.py",
        "_rustcore/src/python/mod.rs",
        "_rustcore/src/ode/background/events.rs",
        "_rustcore/src/ode/background/exact.rs",
        "_rustcore/src/ode/background/history.rs",
        "_rustcore/src/ode/background/type_ix_dae.rs",
        "_rustcore/src/ode/background/trajectory.rs",
        "_rustcore/src/ode/charts.rs",
        "_rustcore/src/lib.rs",
    }
    if set(budget["commit_1"]["allowed_exact_paths"]) != required_c1:
        fail("Commit-1 allowlist mismatch")
    c2 = budget["commit_2"]
    if c2.get("allowed_prefix") != CORRECT_NATIVE_PREFIX:
        fail("correct native-delta prefix missing")
    if any(STALE_NATIVE_PREFIX in item for item in c2.get("allowed_exact_paths", [])):
        fail("stale native prefix active")
    if c2.get("required_parent") != "EXACT_COMMIT_1_SHA":
        fail("Commit 2 must bind exact Commit 1")
    if state["source_authority"]["rf02c_current_remote"]["head"] != CURRENT_HEAD:
        fail("current head mismatch")
    if state["source_authority"]["rf02c_current_remote"]["tree"] != CURRENT_TREE:
        fail("current tree mismatch")
    if state["source_authority"]["post_closeout_native_merge"]["merge_commit"] != CURRENT_HEAD:
        fail("post-closeout merge not recorded")
    return state, graph

def git(args, cwd):
    result = subprocess.run(["git", *args], cwd=cwd, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode:
        fail(f"git {' '.join(args)}: {result.stderr.strip()}")
    return result.stdout.strip()

def live(state):
    repo = Path(git(["rev-parse", "--show-toplevel"], ROOT))
    ref = "origin/agent/architecture/rust-first-rf02c-20260826-r1"
    git(["rev-parse", "--verify", ref], repo)
    result = subprocess.run(["git", "merge-base", "--is-ancestor", CURRENT_HEAD, ref], cwd=repo)
    if result.returncode:
        fail(f"{CURRENT_HEAD} is not ancestor of {ref}")
    legacy = state["source_authority"]["legacy_performance_anchor"]
    actual = git(["rev-parse", "--verify", f"origin/{legacy['branch']}"], repo)
    if actual != legacy["head"]:
        fail("legacy anchor moved")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    manifest()
    state, graph = structure()
    if args.live:
        live(state)
    print(json.dumps({
        "status": "PASS",
        "package_id": PACKAGE_ID,
        "revision": REVISION,
        "exact_next_action": "BASS-11",
        "commit_budget": 2,
        "live": args.live,
        "manifest_entries": len(EXPECTED_MANIFEST),
    }, sort_keys=True))

if __name__ == "__main__":
    main()
