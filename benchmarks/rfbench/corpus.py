"""Validation and selection for the frozen whole-runtime-v1 registry."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable


CORPUS_PATH = Path(__file__).resolve().parents[1] / "corpora/whole_runtime_v1.json"
REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SPEC_PATH = REPOSITORY_ROOT / "docs/rust_first_runtime/SPEC.json"
ADAPTER_PATH = Path(__file__).resolve().with_name("workload_child.py")
EXPECTED_SCHEMA = "bass-whole-runtime-corpus-v1"
EXPECTED_SPEC_SHA256 = "dcd4f89fe7a2ad73f22574357df53fcbea437d83f1b4faae08250e2ab46b4efa"
REQUIRED_STRATA = {
    "cold import and backend initialization",
    "warm RuntimePlan construction",
    "single and batched geometry/background trajectories",
    "matter and thermodynamics evolution",
    "kinetic hierarchy and Kato/collision evolution",
    "ray, map, and observable batches",
    "representative end-to-end production workflow",
    "memory, allocation, FFI-call, and serialization overhead",
}
SUPPLEMENTAL_STRATA = {"batch and ensemble workloads"}
SUPPLEMENTAL_COMPONENTS = {"batch_ensemble"}
COMMAND_ARGV_TEMPLATE = [
    "{python}", "{runner_root}/benchmarks/rfbench/workload_child.py",
    "--workload-id", "{workload_id}",
]
BLOCKED_PREFIXES = ("BLOCKED_", "PARTIAL_")


def canonical_json(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def sha256_json(value: object) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_registry(path: Path = CORPUS_PATH) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    validate_registry(payload)
    return payload


def validate_registry(payload: dict[str, Any]) -> None:
    errors: list[str] = []
    if payload.get("schema") != EXPECTED_SCHEMA:
        errors.append("unexpected corpus schema")
    if payload.get("spec_sha256") != EXPECTED_SPEC_SHA256:
        errors.append("corpus is not bound to the RF-BENCH-00 SPEC")
    if not SPEC_PATH.is_file() or sha256_file(SPEC_PATH) != EXPECTED_SPEC_SHA256:
        errors.append("live RF-BENCH-00 SPEC bytes do not match the corpus authority")
    if payload.get("source_command_argv_template") != COMMAND_ARGV_TEMPLATE:
        errors.append("source command template is not the runner-owned adapter")
    if (
        not ADAPTER_PATH.is_file()
        or payload.get("source_adapter_sha256") != sha256_file(ADAPTER_PATH)
    ):
        errors.append("runner-owned workload adapter digest mismatch")
    declared_strata = payload.get("required_strata")
    if not isinstance(declared_strata, list) or set(declared_strata) != REQUIRED_STRATA:
        errors.append("required_strata does not exactly match the SPEC")
    required_components = payload.get("required_components")
    if (
        not isinstance(required_components, dict)
        or set(required_components) != REQUIRED_STRATA
        or any(not isinstance(values, list) or not values
               for values in required_components.values())
    ):
        errors.append("required_components does not define every SPEC stratum")
        required_component_set: set[str] = set()
    else:
        flattened = [item for values in required_components.values() for item in values]
        required_component_set = set(flattened)
        if len(flattened) != len(required_component_set):
            errors.append("required component atoms must be globally unique")
    component_blockers = payload.get("component_blockers")
    if not isinstance(component_blockers, dict):
        errors.append("component_blockers must be an object")
        component_blockers = {}
    for component, receipt in component_blockers.items():
        if component not in required_component_set:
            errors.append(f"unknown blocked component: {component}")
        if (
            not isinstance(receipt, dict)
            or not str(receipt.get("state", "")).startswith("BLOCKED_")
            or not isinstance(receipt.get("owner_node"), str)
            or not isinstance(receipt.get("reason"), str)
        ):
            errors.append(f"component blocker is invalid: {component}")
    workloads = payload.get("workloads")
    if not isinstance(workloads, list) or not workloads:
        errors.append("workloads must be a non-empty list")
        workloads = []
    ids: set[str] = set()
    covered: set[str] = set()
    holdouts: list[dict[str, Any]] = []
    covered_components: set[str] = set(component_blockers)
    for index, workload in enumerate(workloads):
        prefix = f"workloads[{index}]"
        if not isinstance(workload, dict):
            errors.append(f"{prefix} is not an object")
            continue
        workload_id = workload.get("id")
        if not isinstance(workload_id, str) or not workload_id:
            errors.append(f"{prefix}.id is missing")
        elif workload_id in ids:
            errors.append(f"duplicate workload id: {workload_id}")
        else:
            ids.add(workload_id)
        strata = workload.get("strata")
        if (
            not isinstance(strata, list)
            or not strata
            or not set(strata) <= (REQUIRED_STRATA | SUPPLEMENTAL_STRATA)
        ):
            errors.append(f"{prefix}.strata is invalid")
        else:
            covered.update(set(strata) & REQUIRED_STRATA)
        role = workload.get("role")
        if role not in {"tuning", "control", "holdout"}:
            errors.append(f"{prefix}.role is invalid")
        if role == "holdout":
            holdouts.append(workload)
        components = workload.get("components")
        if (
            not isinstance(components, list)
            or not components
            or not set(components) <= (required_component_set | SUPPLEMENTAL_COMPONENTS)
        ):
            errors.append(f"{prefix}.components is invalid")
        else:
            overlap = covered_components & set(components)
            if overlap:
                errors.append(f"duplicate component coverage: {sorted(overlap)}")
            covered_components.update(components)
        inputs = workload.get("inputs")
        identity = workload.get("input_identity_sha256")
        if inputs is None:
            if identity is not None:
                errors.append(f"{prefix} has a hash for null inputs")
        elif identity != sha256_json(inputs):
            errors.append(f"{prefix}.input_identity_sha256 mismatch")
        state = workload.get("implementation_state")
        selector = workload.get("selector")
        if not isinstance(state, str):
            errors.append(f"{prefix}.implementation_state is missing")
        elif state.startswith("BLOCKED_") and selector is not None:
            errors.append(f"{prefix} blocked entry must have null selector")
        if not isinstance(workload.get("owner_node"), str):
            errors.append(f"{prefix}.owner_node is missing")
        warmups = workload.get("warmup_iterations")
        if isinstance(warmups, bool) or not isinstance(warmups, int) or warmups < 0:
            errors.append(f"{prefix}.warmup_iterations is invalid")
        measurement_kind = workload.get("measurement_kind")
        if measurement_kind not in {"cold_start", "separate_overhead", "steady_state"}:
            errors.append(f"{prefix}.measurement_kind is invalid")
        minimum_duration = workload.get("minimum_duration_seconds")
        if measurement_kind == "steady_state":
            if minimum_duration != 2.0:
                errors.append(f"{prefix} steady-state duration must equal 2.0 seconds")
        elif minimum_duration is not None:
            errors.append(f"{prefix} startup/overhead duration must be null")
        timeout = workload.get("timeout_seconds")
        if timeout is not None and (
            isinstance(timeout, bool) or not isinstance(timeout, int) or timeout <= 0
        ):
            errors.append(f"{prefix}.timeout_seconds is invalid")
        comparator = workload.get("correctness_comparator")
        if not isinstance(comparator, dict) or not isinstance(comparator.get("kind"), str):
            errors.append(f"{prefix}.correctness_comparator is invalid")
        elif not str(state).startswith(BLOCKED_PREFIXES) and (
            comparator.get("kind") != "EXACT_OUTPUT_DIGEST"
        ):
            errors.append(f"{prefix} executable comparator is not implemented")
        output_contract = workload.get("output_contract")
        output_contract_identity = workload.get("output_contract_sha256")
        if output_contract is None:
            if output_contract_identity is not None:
                errors.append(f"{prefix} has a hash for null output_contract")
        elif output_contract_identity != sha256_json(output_contract):
            errors.append(f"{prefix}.output_contract_sha256 mismatch")
    if covered != REQUIRED_STRATA:
        errors.append("workload entries do not cover every required stratum")
    if not required_component_set <= covered_components:
        errors.append("required component atoms are neither covered nor typed-blocked")
    if len(holdouts) != 1:
        errors.append("the registry must contain exactly one holdout")
    else:
        holdout = holdouts[0]
        if holdout.get("allowed_phase") != "milestone_closeout":
            errors.append("holdout allowed_phase must be milestone_closeout")
        if holdout.get("default_selected") is not False:
            errors.append("holdout must not be selected by default")
        if holdout.get("tuning_access") != "FORBIDDEN":
            errors.append("holdout must be forbidden during tuning")
    if errors:
        raise ValueError("invalid whole-runtime-v1 registry: " + "; ".join(errors))


def select_workloads(
    payload: dict[str, Any],
    *,
    roles: Iterable[str] = ("tuning", "control"),
    milestone_closeout: bool = False,
    require_complete: bool = True,
) -> list[dict[str, Any]]:
    validate_registry(payload)
    requested_roles = set(roles)
    if "holdout" in requested_roles and not milestone_closeout:
        raise PermissionError("holdout selection requires milestone_closeout=True")
    selected = [item for item in payload["workloads"] if item["role"] in requested_roles]
    if require_complete:
        blocked = [
            item["id"] for item in selected
            if item["implementation_state"].startswith(BLOCKED_PREFIXES)
        ]
        if blocked:
            raise RuntimeError(
                "whole-runtime-v1 campaign is not executable: " + ", ".join(blocked)
            )
    return selected


def describe(path: Path = CORPUS_PATH) -> dict[str, Any]:
    payload = load_registry(path)
    return {
        "schema": payload["schema"],
        "version": payload["version"],
        "corpus_id": payload["corpus_id"],
        "spec_sha256": payload["spec_sha256"],
        "registry_path": str(path.resolve()),
        "registry_sha256": sha256_file(path),
        "workload_count": len(payload["workloads"]),
        "holdout_id": next(
            item["id"] for item in payload["workloads"] if item["role"] == "holdout"
        ),
        "blocked_workloads": [
            {"id": item["id"], "state": item["implementation_state"],
             "owner_node": item["owner_node"]}
            for item in payload["workloads"]
            if item["implementation_state"].startswith(BLOCKED_PREFIXES)
        ],
    }
