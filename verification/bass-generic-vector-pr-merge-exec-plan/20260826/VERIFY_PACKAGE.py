#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys

MARKER = "PASS_BASS_GENERIC_VECTOR_PR_MERGE_PACKAGE"
EXPECTED_WORK_UNITS = ["WU-001", "WU-002", "WU-003"]
EXPECTED_THREATS = {f"FM-{index:03d}" for index in range(1, 11)}
EXPECTED_PATHS = [
    "_rustcore/src/kinetic/generic_vector.rs",
    "_rustcore/src/kinetic/mod.rs",
    "_rustcore/src/lib.rs",
    "_rustcore/src/python/generic_vector.rs",
    "_rustcore/src/python/mod.rs",
    "artifacts/rust_first_runtime/bass3/EXECUTION_EVIDENCE.json",
    "artifacts/rust_first_runtime/bass3/GREEN.log",
    "artifacts/rust_first_runtime/bass3/RED.log",
    "artifacts/rust_first_runtime/bass3/RED_ENVIRONMENT_ATTEMPT.log",
    "tests/oracles/bass3_generic_vector_oracle.py",
    "tests/test_bass3_generic_vector_host_parity.py",
    "tools/audit/run_bass3_generic_vector_host_parity.py",
]


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def fail(message: str) -> None:
    raise SystemExit(message)


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    required = [
        "PACKAGE_INDEX.json",
        "AUTHORITY_AND_SCOPE.json",
        "P0_P1_THREAT_CATALOGUE.jsonl",
        "INVARIANT_TEST_MATRIX.jsonl",
        "FRESH_CONTEXT_REVIEW_CONTRACT.json",
        "FINAL_DIFFERENTIAL_AUDIT_CONTRACT.json",
        "SOURCE_GUIDE_REFERENCES.json",
        "WORK_UNITS/WU-001-FRESH-DIFFERENTIAL-PR.json",
        "WORK_UNITS/WU-002-MERGE-COMMIT.json",
        "WORK_UNITS/WU-003-POST-MERGE-TARGETED-EXECUTION.json",
        "CODEX_HANDOFF.md",
    ]
    for relative in required:
        if not (root / relative).is_file():
            fail(f"missing package path: {relative}")

    index = load_json(root / "PACKAGE_INDEX.json")
    authority = load_json(root / "AUTHORITY_AND_SCOPE.json")
    threats = load_jsonl(root / "P0_P1_THREAT_CATALOGUE.jsonl")
    matrix = load_jsonl(root / "INVARIANT_TEST_MATRIX.jsonl")

    if index.get("schema") != "bass-generic-vector-pr-merge-package-index-v1":
        fail("unexpected package schema")
    implementation = index["implementation"]
    if implementation["base_sha"] != "445e50184823e58401a8212ceaaf736e72bb35f2":
        fail("base SHA drift")
    if implementation["head_sha"] != "a979af6b022eb832215a2342a01fe6b85374b914":
        fail("head SHA drift")
    if implementation["head_tree"] != "86cdac8dc695c4e6c012294c73eaedf4a55cc1ce":
        fail("head tree drift")
    if implementation["changed_path_count"] != len(EXPECTED_PATHS):
        fail("changed path count drift")

    candidate = authority["implementation_candidate"]
    if candidate["parent"] != implementation["base_sha"]:
        fail("candidate parent drift")
    if candidate["commit"] != implementation["head_sha"]:
        fail("candidate head drift")
    if candidate["commit_count_from_base"] != 1:
        fail("candidate is not exactly one commit")
    if candidate["changed_paths"] != EXPECTED_PATHS:
        fail("candidate path surface drift")

    work_units = index["work_units"]
    if [item["id"] for item in work_units] != EXPECTED_WORK_UNITS:
        fail("work-unit order drift")
    for item in work_units:
        unit = load_json(root / item["file"])
        if unit.get("schema") != "audit-compiled-work-unit/v1":
            fail(f"bad work-unit schema: {item['id']}")
        if unit.get("id") != item["id"]:
            fail(f"work-unit id mismatch: {item['id']}")

    if {item["id"] for item in threats} != EXPECTED_THREATS:
        fail("threat catalogue drift")
    if any(item["severity"] not in {"P0", "P1"} for item in threats):
        fail("non-P0/P1 item in threat catalogue")
    if any(item["disposition"] != "BLOCK_NOW" for item in threats):
        fail("untriaged P0/P1 threat")
    if len(matrix) != 9:
        fail("invariant matrix drift")

    budget = index["process_budget"]
    if budget != {
        "fresh_reviews": 1,
        "full_repository_suites": 0,
        "historical_replays": 0,
        "new_evidence_commits": 0,
        "repair_cycles_without_new_P0_P1": 0,
    }:
        fail("anti-meta-loop process budget drift")

    merge_unit = load_json(root / "WORK_UNITS/WU-002-MERGE-COMMIT.json")
    approval = next(item for item in merge_unit["preconditions"] if item["id"] == "PRE-103")
    if approval["expect"] != "MERGE_APPROVED":
        fail("explicit merge approval gate missing")

    post_unit = load_json(root / "WORK_UNITS/WU-003-POST-MERGE-TARGETED-EXECUTION.json")
    if post_unit["verification"]["full_relevant_suite"]:
        fail("post-merge full-suite reassurance enabled")

    handoff = (root / "CODEX_HANDOFF.md").read_text(encoding="utf-8")
    for token in (
        "PASS_WITH_NO_P0_P1",
        "PR_CREATED_READY_FOR_USER_MERGE_APPROVAL",
        "Do not run the full repository suite",
        "Do not merge",
        "typed",
    ):
        if token not in handoff:
            fail(f"handoff missing token: {token}")

    print(MARKER)
    print("work_units=3")
    print("threats=10")
    print("invariants=9")
    print("changed_paths=12")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
