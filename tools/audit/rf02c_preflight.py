#!/usr/bin/env python3
"""Fail-closed RF-02C preflight for package identity and scope consistency.

This detector does not change scientific authority or execute solver code. It
checks whether every mandatory RF-02C precondition can be repaired inside the
compiled path allowlist before implementation begins.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any, Iterable

PACKAGE_REL = Path("docs/audits/science_system_differential_20260826")
OWNER_PATH = Path("bianchi/symbolic/geometry_contract.py")
OWNER_STALE_TOKEN = "RF-02B owner"
OWNER_EXPECTED = "RF-03"
STOP_CODE = 78


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _git(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True).strip()


def _matches(path: str, pattern: str) -> bool:
    if pattern.endswith("/**"):
        prefix = pattern[:-3].rstrip("/")
        return path == prefix or path.startswith(prefix + "/")
    return fnmatch.fnmatchcase(path, pattern)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _walk(value: Any) -> Iterable[Any]:
    yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def _find_by_id(value: Any, target: str) -> dict[str, Any]:
    matches = [
        item
        for item in _walk(value)
        if isinstance(item, dict) and item.get("id") == target
    ]
    if len(matches) != 1:
        raise RuntimeError(
            f"expected exactly one {target!r} record, observed {len(matches)}"
        )
    return matches[0]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/rust_first_runtime/rf02c/PREFLIGHT.json"),
    )
    args = parser.parse_args()
    root = args.root.resolve()
    package = root / PACKAGE_REL

    work_graph = _load(package / "WORK_UNITS.json")
    audit = _load(package / "AUDIT.json")
    unit = _find_by_id(work_graph, "RF-02C")
    finding = _find_by_id(audit, "FIND-DIFF-008")

    allowed = tuple(unit["scope"]["allowed_paths"])
    owner_rel = OWNER_PATH.as_posix()
    owner_allowed = any(_matches(owner_rel, pattern) for pattern in allowed)
    owner_file = root / OWNER_PATH
    owner_text = owner_file.read_text(encoding="utf-8")
    owner_stale = OWNER_STALE_TOKEN in owner_text
    owner_precondition = any(
        "owner-string drift" in text for text in unit["preconditions"]
    )
    finding_requires_repair = (
        finding.get("severity") == "Critical"
        and "repair before solver wiring" in finding.get("impact", "")
        and "RF-02B" in finding.get("finding", "")
        and OWNER_EXPECTED in finding.get("finding", "")
    )

    conflict = (
        owner_precondition
        and finding_requires_repair
        and owner_stale
        and not owner_allowed
    )
    status = "STOP_CONTRACT_SCOPE_CONFLICT" if conflict else "PASS_PREFLIGHT_SCOPE"

    report = {
        "schema": "bass-rf02c-preflight/v1",
        "status": status,
        "stop_code": STOP_CODE if conflict else 0,
        "repository": "cosmosapjw-quantum/bass",
        "branch": os.environ.get("GITHUB_REF_NAME") or _git("branch", "--show-current"),
        "head": _git("rev-parse", "HEAD"),
        "tree": _git("rev-parse", "HEAD^{tree}"),
        "package": {
            "exact_next_action": work_graph["exact_next_action"],
            "work_units_sha256": _sha256(package / "WORK_UNITS.json"),
            "audit_sha256": _sha256(package / "AUDIT.json"),
        },
        "owner_boundary": {
            "path": owner_rel,
            "sha256": _sha256(owner_file),
            "stale_token_present": owner_stale,
            "compiled_precondition_requires_repair": owner_precondition,
            "critical_finding_requires_repair_before_solver": finding_requires_repair,
            "path_allowed_by_rf02c": owner_allowed,
            "expected_owner": OWNER_EXPECTED,
        },
        "allowed_paths": list(allowed),
        "classification": "PROCESS_CONTRACT_ONLY_NO_SCIENCE_MUTATION",
        "next_action": (
            "Add bianchi/symbolic/geometry_contract.py to the RF-02C allowlist "
            "for the one-line owner metadata repair, or explicitly declare the "
            "stale module quarantined and non-public in the compiled work unit."
            if conflict
            else "Continue the ordered RF-02C implementation."
        ),
    }
    output = args.output if args.output.is_absolute() else root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return STOP_CODE if conflict else 0


if __name__ == "__main__":
    sys.exit(main())
