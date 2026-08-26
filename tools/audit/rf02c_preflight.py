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
from importlib import abc as importlib_abc
import importlib
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any, Iterable

PACKAGE_REL = Path("docs/audits/science_system_differential_20260826")
QUARANTINE_REL = Path("docs/rust_first_runtime/RF02C_OWNER_QUARANTINE_V1.json")
OWNER_PATH = Path("bianchi/symbolic/geometry_contract.py")
OWNER_STALE_TOKEN = "RF-02B owner"
OWNER_EXPECTED = "RF-03"
STOP_CODE = 78


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _git(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True).strip()


def _git_blob(path: str) -> str:
    return _git("rev-parse", f"HEAD:{path}")


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


class _OwnerImportFirewall(importlib_abc.MetaPathFinder):
    def __init__(self, blocked: str):
        self.blocked = blocked
        self.hits: list[str] = []

    def find_spec(self, fullname: str, path=None, target=None):
        del path, target
        if fullname == self.blocked or fullname.startswith(self.blocked + "."):
            self.hits.append(fullname)
            raise ImportError(f"RF-02C quarantined import attempted: {fullname}")
        return None


def _runtime_import_firewall(modules: list[str]) -> dict[str, Any]:
    blocked = "bianchi.symbolic.geometry_contract"
    firewall = _OwnerImportFirewall(blocked)
    imported: list[str] = []
    error: str | None = None
    sys.meta_path.insert(0, firewall)
    try:
        for module in modules:
            importlib.import_module(module)
            imported.append(module)
    except Exception as exc:  # fail-closed diagnostic
        error = f"{type(exc).__name__}: {exc}"
    finally:
        sys.meta_path.remove(firewall)
    return {
        "blocked_module": blocked,
        "requested_modules": modules,
        "imported_modules": imported,
        "firewall_hits": firewall.hits,
        "blocked_module_loaded": blocked in sys.modules,
        "error": error,
        "passed": (
            error is None
            and not firewall.hits
            and blocked not in sys.modules
            and imported == modules
        ),
    }


def _quarantine_proof(root: Path, owner_text: str) -> dict[str, Any]:
    path = root / QUARANTINE_REL
    if not path.is_file():
        return {
            "present": False,
            "valid": False,
            "reason": f"missing {QUARANTINE_REL.as_posix()}",
        }

    record = _load(path)
    pinned = record.get("public_route_files", {})
    blob_observations: dict[str, dict[str, Any]] = {}
    blobs_match = True
    forbidden_hits: dict[str, list[str]] = {}
    tokens = list(record.get("forbidden_route_tokens", []))

    expected_owner_blob = record.get("owner_git_blob")
    observed_owner_blob = _git_blob(OWNER_PATH.as_posix())
    owner_blob_match = expected_owner_blob == observed_owner_blob

    for rel, expected in pinned.items():
        observed = _git_blob(rel)
        matched = observed == expected
        blobs_match = blobs_match and matched
        text = (root / rel).read_text(encoding="utf-8")
        hits = [token for token in tokens if token in text]
        if hits:
            forbidden_hits[rel] = hits
        blob_observations[rel] = {
            "expected": expected,
            "observed": observed,
            "matched": matched,
        }

    runtime = _runtime_import_firewall(
        list(record.get("runtime_import_firewall_modules", []))
    )
    symbolic_init = (root / "bianchi/symbolic/__init__.py").read_text(
        encoding="utf-8"
    )
    symbolic_export_absent = (
        "geometry_contract" not in symbolic_init
        and "validate_geometry_state" not in symbolic_init
    )
    stale_token_present = record.get("stale_token") in owner_text
    base_matches = (
        record.get("base_package_overlay_head")
        == "b759a42911a7433212c1828bd7625d66f3af2d20"
    )
    schema_ok = record.get("schema") == "bass-rf02c-owner-quarantine/v1"
    disposition_ok = (
        record.get("disposition")
        == "QUARANTINED_NONPUBLIC_VALIDATION_IDENTITY_LAYER"
        and record.get("owner_mutation_permitted") is False
        and record.get("direct_import_supported_by_rf02c") is False
        and record.get("correct_owner") == OWNER_EXPECTED
    )
    valid = (
        schema_ok
        and disposition_ok
        and base_matches
        and owner_blob_match
        and blobs_match
        and stale_token_present
        and not forbidden_hits
        and symbolic_export_absent
        and runtime["passed"]
    )
    return {
        "present": True,
        "valid": valid,
        "path": QUARANTINE_REL.as_posix(),
        "sha256": _sha256(path),
        "schema_ok": schema_ok,
        "disposition_ok": disposition_ok,
        "base_matches": base_matches,
        "owner_blob": {
            "expected": expected_owner_blob,
            "observed": observed_owner_blob,
            "matched": owner_blob_match,
        },
        "pinned_public_route_blobs": blob_observations,
        "stale_token_present": stale_token_present,
        "forbidden_route_token_hits": forbidden_hits,
        "symbolic_export_absent": symbolic_export_absent,
        "runtime_import_firewall": runtime,
        "claim_boundary": record.get("claim_boundary"),
    }


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

    quarantine = _quarantine_proof(root, owner_text)
    owner_boundary_resolved = (
        not (owner_precondition and finding_requires_repair and owner_stale)
        or owner_allowed
        or quarantine["valid"]
    )
    conflict = not owner_boundary_resolved
    if conflict:
        status = "STOP_CONTRACT_SCOPE_CONFLICT"
    elif owner_stale and quarantine["valid"]:
        status = "PASS_PREFLIGHT_QUARANTINED_OWNER"
    else:
        status = "PASS_PREFLIGHT_SCOPE"

    report = {
        "schema": "bass-rf02c-preflight/v2",
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
            "git_blob": _git_blob(owner_rel),
            "stale_token_present": owner_stale,
            "compiled_precondition_requires_repair": owner_precondition,
            "critical_finding_requires_repair_before_solver": finding_requires_repair,
            "path_allowed_by_rf02c": owner_allowed,
            "expected_owner": OWNER_EXPECTED,
            "resolved": owner_boundary_resolved,
            "resolution": (
                "direct_allowed_repair"
                if owner_allowed
                else (
                    "quarantined_nonpublic_route"
                    if quarantine["valid"]
                    else "unresolved"
                )
            ),
        },
        "quarantine": quarantine,
        "allowed_paths": list(allowed),
        "classification": "PROCESS_CONTRACT_ONLY_NO_SCIENCE_MUTATION",
        "next_action": (
            "Stop before solver wiring and repair the compiled scope contract."
            if conflict
            else "Continue the ordered RF-02C implementation without importing or mutating the quarantined owner module."
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
