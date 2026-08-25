#!/usr/bin/env python3
"""Fail-closed structural verification for the docs-only hostile-audit package."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import NoReturn


ROOT = Path(__file__).resolve().parent
ALLOWED_CANDIDATE_STATES = {
    "PROMOTED",
    "REFUTED",
    "UNRESOLVED",
    "DEFERRED",
    "NOT_ATTEMPTED",
}
PROMPT_KEYS = [
    "outcome",
    "success_criteria",
    "boundaries",
    "permissions",
    "tools",
    "evidence",
    "stop_conditions",
]
EXTERNAL_DEPENDENCIES = {"RF-01", "RF-BENCH-00"}
TERMINAL_NEXT = {
    "BASS-8_READJUDICATION",
    "EXPLICIT_AUTHORITY_DECISION",
    "HUMAN_MERGE_AND_AUTHORITY_DECISION",
}


def fail(message: str) -> NoReturn:
    raise SystemExit(f"FAIL: {message}")


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def load(name: str) -> dict:
    try:
        return json.loads((ROOT / name).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot load {name}: {exc}")


def require_unique(rows: list[dict], label: str) -> set[str]:
    ids = [row.get("id") for row in rows]
    require(all(isinstance(item, str) and item for item in ids), f"missing {label} id")
    require(len(ids) == len(set(ids)), f"duplicate {label} id")
    return set(ids)


def verify_manifest() -> None:
    manifest = ROOT / "MANIFEST.sha256"
    require(manifest.exists(), "MANIFEST.sha256 missing")
    lines = [line for line in manifest.read_text(encoding="utf-8").splitlines() if line]
    require(bool(lines), "empty manifest")
    seen: set[str] = set()
    for line in lines:
        parts = line.split("  ", 1)
        require(len(parts) == 2, f"malformed manifest line: {line}")
        digest, name = parts
        require(name != "MANIFEST.sha256", "manifest must not hash itself")
        require(name not in seen, f"duplicate manifest entry {name}")
        require((ROOT / name).is_file(), f"manifest target missing: {name}")
        seen.add(name)
        actual = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
        require(actual == digest, f"hash mismatch {name}")
    expected = {
        "AUDIT.json",
        "CURRENT_STATE.json",
        "HANDOFF.md",
        "INDEPENDENT_REVIEW.json",
        "PROMPT_CONTRACT.json",
        "README.md",
        "verify.py",
    }
    require(seen == expected, f"manifest inventory drift: {seen ^ expected}")


def main() -> None:
    audit = load("AUDIT.json")
    state = load("CURRENT_STATE.json")
    prompt = load("PROMPT_CONTRACT.json")
    review = load("INDEPENDENT_REVIEW.json")

    require(list(prompt) == PROMPT_KEYS, "prompt contract key order/schema drift")
    for key in PROMPT_KEYS:
        require(bool(prompt.get(key)), f"empty prompt field {key}")

    claims = audit.get("claim_register", [])
    findings = audit.get("findings", [])
    threats = audit.get("threat_catalogue", [])
    units = audit.get("work_units", [])
    claim_ids = require_unique(claims, "claim")
    finding_ids = require_unique(findings, "finding")
    threat_ids = require_unique(threats, "threat")
    unit_ids = require_unique(units, "work-unit")
    require(bool(claim_ids), "claim register empty")

    claim_by_id = {row["id"]: row for row in claims}
    finding_by_id = {row["id"]: row for row in findings}
    threat_by_id = {row["id"]: row for row in threats}

    for claim in claim_by_id.values():
        require(
            claim.get("candidate_state") in ALLOWED_CANDIDATE_STATES,
            f"{claim['id']} candidate state invalid",
        )

    for finding in finding_by_id.values():
        for key in ("severity", "state", "finding", "evidence", "impact", "confidence", "next_module"):
            require(bool(finding.get(key)), f"{finding['id']} missing {key}")
        require(finding["severity"] in {"Critical", "Watch", "Info"}, f"{finding['id']} severity")

    for threat in threat_by_id.values():
        require(threat.get("priority") in {"P0", "P1"}, f"{threat['id']} priority")
        for key in ("threat", "detector", "owner", "blocked_if"):
            require(bool(threat.get(key)), f"{threat['id']} missing {key}")
        if threat["priority"] == "P0":
            for key in ("evidence", "impact", "related_finding_ids"):
                require(bool(threat.get(key)), f"{threat['id']} P0 missing {key}")
            require(threat["owner"] in unit_ids, f"{threat['id']} owner is not a work-unit ID")
            for finding_id in threat["related_finding_ids"]:
                require(finding_id in finding_ids, f"{threat['id']} unknown finding {finding_id}")

    for finding in finding_by_id.values():
        if finding["severity"] != "Critical":
            continue
        related = finding.get("related_threat_ids", [])
        require(bool(related), f"{finding['id']} Critical missing P0 trace")
        for threat_id in related:
            require(threat_id in threat_ids, f"{finding['id']} unknown threat {threat_id}")
            threat = threat_by_id[threat_id]
            require(threat["priority"] == "P0", f"{finding['id']} traces to non-P0 {threat_id}")
            require(
                finding["id"] in threat.get("related_finding_ids", []),
                f"{finding['id']} <-> {threat_id} trace is not reciprocal",
            )

    unit_index = {unit["id"]: unit for unit in units}
    for unit in units:
        require(unit.get("schema") == "audit-compiled-work-unit/v1", f"{unit['id']} schema")
        require(bool(unit.get("goal")) and bool(unit.get("required_detectors")), f"{unit['id']} detectors")
        require(bool(unit.get("verification")) and bool(unit.get("stop_conditions")), f"{unit['id']} closure")
        for dependency in unit.get("depends_on", []):
            require(
                dependency in unit_ids or dependency in EXTERNAL_DEPENDENCIES,
                f"{unit['id']} unknown dependency {dependency}",
            )
        next_id = unit.get("next")
        require(next_id in unit_ids or next_id in TERMINAL_NEXT, f"{unit['id']} unknown next {next_id}")

    next_units = [unit["id"] for unit in units if unit.get("status") == "NEXT"]
    require(next_units == ["RF-02A"], f"expected exactly RF-02A NEXT, got {next_units}")
    require(
        state.get("exactly_one_next_action") == "RF-02A_BIANCHI_IDENTITY_AND_GEOMETRY_AUTHORITY",
        "CURRENT_STATE next action drift",
    )
    require("RF-02A only" in audit.get("exactly_one_next_action", ""), "AUDIT next action drift")
    require(unit_index["RF-02D"]["next"] == "RF-03", "optional SIMD placed on science critical path")
    require(unit_index["RF-BENCH-COMP-01"]["next"] == "RF-02E", "comparator next-ID drift")
    require(unit_index["RF-02E"].get("lane", "").startswith("OPTIONAL_"), "RF-02E not marked optional")

    audit_source = audit.get("bound_source", {})
    state_source = state.get("bound_source", {})
    for key in ("branch", "commit", "tree"):
        require(audit_source.get(key) == state_source.get(key), f"bound-source {key} drift")
    require(audit_source.get("repository") == state.get("repository"), "bound-source repository drift")
    prompt_evidence = "\n".join(prompt["evidence"])
    require(state_source["commit"] in prompt_evidence, "prompt does not bind source commit")

    require(
        review.get("outcome") in {"PASS", "PASS_WITH_NONBLOCKING_FINDINGS", "BLOCKED"},
        "independent review outcome invalid",
    )
    require(review.get("bound_source_commit") == state_source["commit"], "review source drift")
    require(review.get("blockers") == [], "independent review blockers remain")

    for name, limit in (("README.md", 80), ("HANDOFF.md", 80)):
        text = (ROOT / name).read_text(encoding="utf-8")
        require(len(text.splitlines()) <= limit, f"{name} exceeds {limit} lines")
        require("part-000" not in text and "PARTS.sha" not in text, f"{name} reproduces part evidence")

    verify_manifest()
    print("PASS: hostile-audit package structure, traceability, review, and manifest")


if __name__ == "__main__":
    main()
