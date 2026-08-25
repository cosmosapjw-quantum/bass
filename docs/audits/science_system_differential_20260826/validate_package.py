#!/usr/bin/env python3
"""Fail-closed structural validator for the BASS audit-compiled package."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys


OPEN_THREAT_STATES = {
    "open",
    "open_pre_rf02c",
    "open_parallel",
    "blocked_input",
    "optional_open",
}
CONTROLLED_THREAT_STATES = {"controlled", "controlled_by_package"}
CLAIM_STATES = {"Candidate", "Promoted", "Refuted", "Unresolved", "Not Attempted"}


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def no_duplicate_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            fail(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=no_duplicate_object)
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot parse {path.name}: {exc}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def run(command: list[str], *, cwd: Path, binary: bool = False):
    result = subprocess.run(command, cwd=cwd, capture_output=True)
    if result.returncode != 0:
        stderr = result.stderr.decode("utf-8", "replace").strip()
        fail(f"command failed ({' '.join(command)}): {stderr}")
    if binary:
        return result.stdout
    return result.stdout.decode("utf-8").strip()


def verify_manifest(root: Path) -> dict[str, str]:
    manifest = root / "MANIFEST.sha256"
    if not manifest.is_file():
        fail("MANIFEST.sha256 is absent")
    entries = {}
    for number, line in enumerate(manifest.read_text(encoding="utf-8").splitlines(), 1):
        match = re.fullmatch(r"([0-9a-f]{64})  ([A-Za-z0-9_.-]+)", line)
        if not match:
            fail(f"invalid manifest line {number}")
        digest, name = match.groups()
        if name in entries or name == "MANIFEST.sha256":
            fail(f"invalid/duplicate manifest entry: {name}")
        entries[name] = digest
    nested_directories = sorted(
        str(path.relative_to(root))
        for path in root.rglob("*")
        if path.is_dir()
    )
    if nested_directories:
        fail(f"package subdirectories are forbidden: {nested_directories}")
    actual_names = {
        str(path.relative_to(root))
        for path in root.rglob("*")
        if path.is_file() and path.name != "MANIFEST.sha256"
    }
    if set(entries) != actual_names:
        fail(f"manifest inventory mismatch: listed={sorted(entries)} actual={sorted(actual_names)}")
    for name, expected in entries.items():
        if sha256(root / name) != expected:
            fail(f"manifest digest mismatch: {name}")
    return entries


def visit_acyclic(node: str, units: dict, active: set, complete: set) -> None:
    if node in active:
        fail(f"work-unit dependency cycle at {node}")
    if node in complete:
        return
    active.add(node)
    for dependency in units[node]["dependencies"]:
        if dependency not in units:
            fail(f"{node} has unknown dependency {dependency}")
        visit_acyclic(dependency, units, active, complete)
    active.remove(node)
    complete.add(node)


def live_remote_closure(
    root: Path,
    state: dict,
    graph: dict,
    manifest_entries: dict[str, str],
) -> dict:
    repo_root = Path(run(["git", "rev-parse", "--show-toplevel"], cwd=root))
    remote_url = run(["git", "remote", "get-url", "origin"], cwd=repo_root)
    if "cosmosapjw-quantum/bass" not in remote_url:
        fail(f"unexpected origin: {remote_url}")

    source = state["source_authority"]
    first = graph["work_units"][0]["authority_and_base"]
    source_branch = source["branch"]
    overlay_branch = first["package_overlay_branch"]

    def remote_head(branch: str) -> str:
        output = run(
            ["git", "ls-remote", "--heads", "origin", f"refs/heads/{branch}"],
            cwd=repo_root,
        )
        lines = [line for line in output.splitlines() if line]
        if len(lines) != 1:
            fail(f"cannot resolve exactly one live branch head: {branch}")
        return lines[0].split()[0]

    live_source_head = remote_head(source_branch)
    live_overlay_head = remote_head(overlay_branch)
    run(
        ["git", "fetch", "--quiet", "--no-tags", "origin", source_branch, overlay_branch],
        cwd=repo_root,
    )
    if live_source_head != source["head"]:
        fail("live RF-02B source head drift")
    live_source_tree = run(
        ["git", "show", "-s", "--format=%T", live_source_head],
        cwd=repo_root,
    )
    if live_source_tree != source["tree"]:
        fail("live RF-02B source tree drift")

    evidence_path = source["evidence"]["path"]
    evidence_bytes = run(
        ["git", "show", f"{live_source_head}:{evidence_path}"],
        cwd=repo_root,
        binary=True,
    )
    if sha256_bytes(evidence_bytes) != source["evidence"]["sha256"]:
        fail("live RF-02B evidence byte hash drift")

    parents = run(
        ["git", "show", "-s", "--format=%P", live_overlay_head],
        cwd=repo_root,
    ).split()
    if parents != [source["head"]]:
        fail(f"package overlay parent mismatch: {parents}")

    package_path = "docs/audits/science_system_differential_20260826"
    remote_tree_output = run(
        ["git", "ls-tree", "-r", "--name-only", live_overlay_head, "--", package_path],
        cwd=repo_root,
    )
    prefix = package_path + "/"
    remote_names = {
        path[len(prefix):]
        for path in remote_tree_output.splitlines()
        if path.startswith(prefix)
    }
    expected_remote_names = set(manifest_entries) | {"MANIFEST.sha256"}
    if remote_names != expected_remote_names:
        fail(
            "remote package inventory mismatch: "
            f"listed={sorted(expected_remote_names)} remote={sorted(remote_names)}"
        )
    remote_manifest = run(
        ["git", "show", f"{live_overlay_head}:{package_path}/MANIFEST.sha256"],
        cwd=repo_root,
        binary=True,
    )
    if remote_manifest != (root / "MANIFEST.sha256").read_bytes():
        fail("remote package manifest bytes differ from checked package")
    for name, expected in manifest_entries.items():
        remote_bytes = run(
            ["git", "show", f"{live_overlay_head}:{package_path}/{name}"],
            cwd=repo_root,
            binary=True,
        )
        if sha256_bytes(remote_bytes) != expected:
            fail(f"remote package file digest mismatch: {name}")

    source_pr = json.loads(
        run(["gh", "api", "repos/cosmosapjw-quantum/bass/pulls/32"], cwd=repo_root)
    )
    if not (
        source_pr.get("state") == "open"
        and source_pr.get("draft") is True
        and source_pr.get("merged_at") is None
        and source_pr.get("head", {}).get("sha") == live_source_head
        and source_pr.get("head", {}).get("ref") == source_branch
    ):
        fail("source PR #32 is not the bound open/draft/unmerged head")

    overlay_prs = json.loads(
        run(
            [
                "gh",
                "api",
                "-X",
                "GET",
                "repos/cosmosapjw-quantum/bass/pulls",
                "-f",
                "state=open",
                "-f",
                f"head=cosmosapjw-quantum:{overlay_branch}",
            ],
            cwd=repo_root,
        )
    )
    matches = [
        pr
        for pr in overlay_prs
        if pr.get("head", {}).get("ref") == overlay_branch
    ]
    if len(matches) != 1:
        fail("cannot resolve exactly one open package-overlay PR")
    overlay_pr = matches[0]
    if not (
        overlay_pr.get("draft") is True
        and overlay_pr.get("merged_at") is None
        and overlay_pr.get("head", {}).get("sha") == live_overlay_head
        and overlay_pr.get("base", {}).get("ref") == source_branch
    ):
        fail("package-overlay PR is not open/draft/unmerged on the bound base")

    return {
        "source_head": live_source_head,
        "source_tree": live_source_tree,
        "overlay_head": live_overlay_head,
        "source_pr": 32,
        "overlay_pr": overlay_pr["number"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--live", action="store_true")
    mode.add_argument("--offline-pinned", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()

    state = load_json(root / "CURRENT_STATE.json")
    audit = load_json(root / "AUDIT.json")
    graph = load_json(root / "WORK_UNITS.json")
    load_json(root / "INDEPENDENT_REVIEW.json")

    if graph.get("exact_next_action") != "RF-02C":
        fail("exactly one next action is not RF-02C")
    units_list = graph.get("work_units", [])
    units = {unit["id"]: unit for unit in units_list}
    if len(units) != len(units_list):
        fail("duplicate work-unit ID")
    if "RF-02C" not in units:
        fail("RF-02C work unit absent")
    for unit in units_list:
        if unit.get("schema") != "audit-compiled-work-unit/v1":
            fail(f"wrong work-unit schema: {unit.get('id')}")
        if not unit.get("verification", {}).get("primary"):
            fail(f"missing primary detector: {unit['id']}")
        for allowed in unit["scope"]["allowed_paths"]:
            if "(" in allowed or ")" in allowed or "<" in allowed or ">" in allowed:
                fail(f"non-path annotation in allowed_paths for {unit['id']}: {allowed}")
        allowed_paths = set(unit["scope"]["allowed_paths"])
        for ruled_path in unit["scope"].get("semantic_path_rules", {}):
            if ruled_path not in allowed_paths:
                fail(f"semantic path rule is outside allowed_paths for {unit['id']}: {ruled_path}")
        for key, command in unit["verification"].items():
            if isinstance(command, str) and re.search(r"<[^=]", command):
                fail(f"unresolved command placeholder in {unit['id']} verification.{key}")
    active, complete = set(), set()
    for unit_id in units:
        visit_acyclic(unit_id, units, active, complete)

    threats = {item["id"]: item for item in audit["sections"]["B_threat_catalogue"]}
    counts = {threat_id: 0 for threat_id in threats}
    for unit in units_list:
        for threat_id in set(unit["risk_ids"]):
            if threat_id not in threats:
                fail(f"unknown threat {threat_id} in {unit['id']}")
            counts[threat_id] += 1
    for threat_id, threat in threats.items():
        if not threat.get("primary_detector") or not threat.get("command"):
            fail(f"missing detector contract for {threat_id}")
        if threat["status"] in OPEN_THREAT_STATES and counts[threat_id] != 1:
            fail(f"open threat {threat_id} has {counts[threat_id]} primary owners")
        if threat["status"] in CONTROLLED_THREAT_STATES and not threat.get("detector_exists_now"):
            fail(f"controlled threat lacks an existing detector: {threat_id}")

    for claim in audit["claim_register"]:
        if claim["state"] not in CLAIM_STATES:
            fail(f"invalid claim state: {claim['id']}")
        for threat_id in claim["related_threat_ids"]:
            if threat_id not in threats:
                fail(f"claim {claim['id']} references unknown threat {threat_id}")
    for finding in audit["findings"]:
        for threat_id in finding["related_threat_ids"]:
            if threat_id not in threats:
                fail(f"finding {finding['id']} references unknown threat {threat_id}")

    registry = graph["reuse_registry"]
    for unit in units_list:
        for reuse_id in unit["reuse_evidence_ids"]:
            if reuse_id not in registry:
                fail(f"{unit['id']} references unresolved reuse ID {reuse_id}")
    for reuse_id, entry in registry.items():
        if not entry.get("source") or not entry.get("predicate"):
            fail(f"reuse entry lacks source/predicate: {reuse_id}")
        if not entry.get("dependency_paths") and not entry.get("dependency_paths_from"):
            fail(f"reuse entry lacks dependency set: {reuse_id}")

    first = units["RF-02C"]
    required_order = [
        "Bind RF02B payload",
        "Route q.group",
        "Add deterministic composite-receipt",
        "Add fail-closed projection",
        "Implement Rust-owned integration",
    ]
    positions = []
    joined_steps = "\n".join(first["ordered_steps"])
    for marker in required_order:
        position = joined_steps.find(marker)
        if position < 0:
            fail(f"RF-02C ordered step missing: {marker}")
        positions.append(position)
    if positions != sorted(positions):
        fail("RF-02C safety/provenance repairs do not precede solver wiring")

    manifest_entries = verify_manifest(root)
    live_result = live_remote_closure(root, state, graph, manifest_entries) if args.live else None

    result = {
        "status": "PASS",
        "package_id": state["package_id"],
        "exact_next_action": graph["exact_next_action"],
        "claims": len(audit["claim_register"]),
        "findings": len(audit["findings"]),
        "threats": len(threats),
        "work_units": len(units),
        "dag_acyclic": True,
        "reuse_resolution": True,
        "one_primary_owner_per_open_threat": True,
        "manifest_verified": True,
        "live_remote_verified": args.live,
        "live": live_result,
    }
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
