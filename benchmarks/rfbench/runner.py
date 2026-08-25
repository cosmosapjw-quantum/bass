"""RF-BENCH-00 state machine.

Host authority is decided before candidate source resolution.  A collector may
buffer arm observations, but the protocol exposes candidate timing only after
the complete pair's contamination envelope passes.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import os
from pathlib import Path
import random
import subprocess
from typing import Any, Callable, Mapping, Protocol

from .corpus import load_registry, sha256_file
from .host import ClaimLevel
from .protocol import CONTAMINATION_LIMITS, evaluate_pair, sha256_json, summarize_pairs


RUN_CONFIG_SCHEMA = "bass-rfbench-run-config-v1"
RUN_RESULT_SCHEMA = "bass-rfbench-controlled-paired-result-v1"
EXPECTED_SPEC_SHA256 = "dcd4f89fe7a2ad73f22574357df53fcbea437d83f1b4faae08250e2ab46b4efa"
EXPECTED_ADAPTER_SHA256 = "e07fbf602c61e02171d8621e72d028b7a5f7a9805fb90b1b78f314b536430f5e"

_CLAIM_LEVEL_RANK = {
    ClaimLevel.EXPLORATORY_ONLY: 0,
    ClaimLevel.CONTROLLED_SHARED_PAIRED: 1,
    ClaimLevel.DEDICATED_BARE_METAL: 2,
}


class Collector(Protocol):
    def preflight(
        self, source: "ResolvedSource", workload: Mapping[str, Any],
        execution_cpu_set: tuple[int, ...], evidence_cpu_set: tuple[int, ...],
        worker_count: int,
        run_contract: Mapping[str, Any],
    ) -> Mapping[str, Any]: ...

    def observe(
        self, source: "ResolvedSource", workload: Mapping[str, Any],
        execution_cpu_set: tuple[int, ...], evidence_cpu_set: tuple[int, ...],
        worker_count: int,
        run_contract: Mapping[str, Any],
    ) -> Mapping[str, Any]: ...

    def warmup(
        self, source: "ResolvedSource", workload: Mapping[str, Any],
        execution_cpu_set: tuple[int, ...], evidence_cpu_set: tuple[int, ...],
        worker_count: int,
        run_contract: Mapping[str, Any],
    ) -> Mapping[str, Any]: ...


@dataclass(frozen=True)
class ResolvedSource:
    root: Path
    head: str
    tree: str
    command: tuple[str, ...]
    environment_identity_sha256: str
    native_artifact_sha256: str

    def as_receipt(self) -> dict[str, Any]:
        return {
            "root": str(self.root),
            "head": self.head,
            "tree": self.tree,
            "command_sha256": hashlib.sha256(
                b"\0".join(part.encode() for part in self.command)
            ).hexdigest(),
            "environment_identity_sha256": self.environment_identity_sha256,
            "native_artifact_sha256": self.native_artifact_sha256,
        }


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args], check=True, capture_output=True,
        text=True, timeout=10.0,
    ).stdout.strip()


def resolve_source(raw: Mapping[str, Any]) -> ResolvedSource:
    root_raw = raw.get("root")
    expected_ref = raw.get("ref")
    python_raw = raw.get("python")
    command = raw.get("command")
    environment_identity = raw.get("environment_identity_sha256")
    native_artifact = raw.get("native_artifact_sha256")
    if (
        not isinstance(root_raw, str)
        or not isinstance(expected_ref, str)
        or not isinstance(python_raw, str)
    ):
        raise ValueError("source root, ref, and python must be strings")
    if not isinstance(command, list) or not command or not all(
        isinstance(item, str) and item for item in command
    ):
        raise ValueError("source command must be a non-empty argv list")
    for name, value in (
        ("environment_identity_sha256", environment_identity),
        ("native_artifact_sha256", native_artifact),
    ):
        if not isinstance(value, str) or len(value) != 64:
            raise ValueError(f"source {name} must be a 64-character digest")
    root = Path(root_raw).resolve()
    if not root.is_dir():
        raise ValueError(f"source root does not exist: {root}")
    head = _git(root, "rev-parse", "HEAD")
    if head != expected_ref:
        raise ValueError(f"source ref mismatch: expected {expected_ref}, observed {head}")
    dirty = _git(root, "status", "--porcelain=v1", "--untracked-files=all")
    if dirty:
        raise ValueError(f"benchmark source is dirty: {root}")
    python_path = Path(python_raw).resolve()
    if not python_path.is_file() or not os.access(python_path, os.X_OK):
        raise ValueError(f"source python is not an executable file: {python_path}")
    runner_root = Path(__file__).resolve().parents[2]
    expanded = tuple(
        item.replace("{root}", str(root))
        .replace("{python}", str(python_path))
        .replace("{runner_root}", str(runner_root))
        for item in command
    )
    return ResolvedSource(
        root, head, _git(root, "rev-parse", "HEAD^{tree}"), expanded,
        environment_identity, native_artifact,
    )


def validate_host_probe(host_probe: Mapping[str, Any]) -> None:
    if host_probe.get("schema") != "bass-rfbench-host-capability-v1":
        raise ValueError("host receipt schema mismatch")
    receipt = host_probe.get("receipt_sha256")
    if not isinstance(receipt, str) or len(receipt) != 64:
        raise ValueError("host receipt digest is missing")
    unsigned = dict(host_probe)
    unsigned.pop("receipt_sha256", None)
    if sha256_json(unsigned) != receipt:
        raise ValueError("host receipt digest mismatch")
    try:
        ClaimLevel(host_probe.get("claim_level"))
    except (TypeError, ValueError) as exc:
        raise ValueError("host receipt claim level is invalid") from exc


def _host_control_identity(host_probe: Mapping[str, Any]) -> str:
    """Hash non-volatile host controls that must survive probe-to-run handoff."""

    cgroup = host_probe.get("cgroup", {})
    if not isinstance(cgroup, Mapping):
        cgroup = {}
    stable_cgroup = {
        key: cgroup.get(key)
        for key in (
            "v2", "relative_path", "partition", "effective_cpus",
            "exclusive_effective_cpus", "affinity", "controllers",
            "subtree_control",
        )
    }
    return sha256_json({
        "platform": host_probe.get("platform"),
        "cgroup": stable_cgroup,
        "topology": host_probe.get("topology"),
        "strata": host_probe.get("strata"),
        "kernel_cpu_control": host_probe.get("kernel_cpu_control"),
        "perf_capacity": host_probe.get("perf_capacity"),
        "interfaces": host_probe.get("interfaces"),
        "dedicated_host_attestation": host_probe.get("dedicated_host_attestation"),
    })


def _validate_source_command(
    raw: Mapping[str, Any], registry: Mapping[str, Any], workload: Mapping[str, Any]
) -> None:
    expected = [
        part.replace("{workload_id}", str(workload["id"]))
        for part in registry["source_command_argv_template"]
    ]
    if raw.get("command") != expected:
        raise ValueError(
            "source command must equal the corpus-bound runner-owned workload adapter"
        )


def validate_run_config(config: Mapping[str, Any]) -> None:
    errors: list[str] = []
    if config.get("schema") != RUN_CONFIG_SCHEMA:
        errors.append("unexpected run config schema")
    try:
        ClaimLevel(config.get("requested_claim_level"))
    except (TypeError, ValueError):
        errors.append("requested_claim_level is invalid")
    if config.get("requested_claim_level") == ClaimLevel.EXPLORATORY_ONLY.value:
        errors.append("run-paired is an authority path and cannot request EXPLORATORY_ONLY")
    if config.get("stratum") not in {"strict_1t", "physical_12t"}:
        errors.append("stratum must be strict_1t or physical_12t")
    for name in ("baseline", "candidate"):
        if not isinstance(config.get(name), Mapping):
            errors.append(f"{name} source is missing")
        else:
            if not isinstance(config[name].get("python"), str):
                errors.append(f"{name}.python is missing")
            for digest_name in ("environment_identity_sha256", "native_artifact_sha256"):
                value = config[name].get(digest_name)
                if not isinstance(value, str) or len(value) != 64:
                    errors.append(f"{name}.{digest_name} is missing")
    integer_contract = {
        "valid_pairs_target": 30,
        "max_attempts": 90,
        "bootstrap_replicates": 10_000,
    }
    for name, required in integer_contract.items():
        if config.get(name) != required:
            errors.append(f"{name} must equal the frozen value {required}")
    seed = config.get("seed")
    if isinstance(seed, bool) or not isinstance(seed, int):
        errors.append("seed must be an integer")
    if not isinstance(config.get("workload_id"), str):
        errors.append("workload_id is missing")
    corpus_sha = config.get("corpus_sha256")
    if not isinstance(corpus_sha, str) or len(corpus_sha) != 64:
        errors.append("corpus_sha256 is missing")
    if config.get("spec_sha256") != EXPECTED_SPEC_SHA256:
        errors.append("spec_sha256 does not match RF-BENCH-00 authority")
    if config.get("source_adapter_sha256") != EXPECTED_ADAPTER_SHA256:
        errors.append("source_adapter_sha256 does not match the runner-owned adapter")
    common_build = config.get("common_build_identity")
    common_build_sha = config.get("common_build_identity_sha256")
    if not isinstance(common_build, Mapping):
        errors.append("common_build_identity is missing")
    elif common_build_sha != sha256_json(common_build):
        errors.append("common_build_identity_sha256 mismatch")
    if config.get("phase") not in {"tuning", "milestone_closeout"}:
        errors.append("phase must be tuning or milestone_closeout")
    if config.get("contamination_limits") != CONTAMINATION_LIMITS:
        errors.append("contamination_limits must equal the frozen SPEC values")
    if errors:
        raise ValueError("invalid RF-BENCH-00 run config: " + "; ".join(errors))


def _choose_order(
    rng: random.Random, accepted_by_order: Mapping[str, int], quota: int
) -> str:
    needed = [order for order in ("AB", "BA") if accepted_by_order[order] < quota]
    if not needed:
        raise RuntimeError("order requested after both quotas were filled")
    return needed[rng.randrange(len(needed))]


def _calibrated_repetitions(
    single_iteration_wall_time_ns: int, minimum_duration_seconds: float | int | None,
) -> int:
    if (
        isinstance(single_iteration_wall_time_ns, bool)
        or not isinstance(single_iteration_wall_time_ns, int)
        or single_iteration_wall_time_ns <= 0
    ):
        raise ValueError("single iteration wall time must be a positive integer")
    if minimum_duration_seconds is None:
        return 1
    if (
        isinstance(minimum_duration_seconds, bool)
        or not isinstance(minimum_duration_seconds, (int, float))
        or not math.isfinite(float(minimum_duration_seconds))
        or minimum_duration_seconds <= 0
    ):
        raise ValueError("minimum duration must be a positive finite number or null")
    repetitions = max(
        1,
        math.ceil(
            float(minimum_duration_seconds) * 1_000_000_000
            / single_iteration_wall_time_ns
        ),
    )
    if repetitions > 1_000_000:
        raise ValueError("calibrated repetition count exceeds hard cap")
    return repetitions


def run_protocol(
    config: Mapping[str, Any],
    host_probe: Mapping[str, Any],
    *,
    live_host_probe: Mapping[str, Any] | None = None,
    resolver: Callable[[Mapping[str, Any]], ResolvedSource] = resolve_source,
    collector: Collector,
    corpus_path: Path | None = None,
) -> dict[str, Any]:
    """Execute the paired state machine or fail before candidate resolution."""

    validate_run_config(config)
    validate_host_probe(host_probe)
    if live_host_probe is None:
        return {
            "schema": RUN_RESULT_SCHEMA,
            "status": "BLOCKED_ENVIRONMENT",
            "acceptance_claim": "NONE",
            "candidate_resolved": False,
            "candidate_statistics_visible": False,
            "workload_executed": False,
            "supplied_host_probe_receipt_sha256": host_probe.get("receipt_sha256"),
            "blocking_reasons": ["live_host_probe_required_before_authority_run"],
        }
    validate_host_probe(live_host_probe)
    registry = load_registry() if corpus_path is None else load_registry(corpus_path)
    actual_corpus_path = corpus_path or (
        Path(__file__).resolve().parents[1] / "corpora/whole_runtime_v1.json"
    )
    actual_corpus_sha256 = sha256_file(actual_corpus_path)
    if config["corpus_sha256"] != actual_corpus_sha256:
        raise ValueError("run config corpus_sha256 does not match the selected corpus")
    workload_matches = [
        item for item in registry["workloads"] if item["id"] == config["workload_id"]
    ]
    if len(workload_matches) != 1:
        raise ValueError("workload_id does not identify exactly one corpus entry")
    workload = workload_matches[0]
    milestone = config["phase"] == "milestone_closeout"
    if workload["role"] == "holdout" and not milestone:
        raise PermissionError("holdout execution is forbidden outside milestone_closeout")
    if workload["implementation_state"].startswith(("BLOCKED_", "PARTIAL_")):
        raise RuntimeError(
            f"workload is not executable: {workload['id']} "
            f"({workload['implementation_state']})"
        )
    if config["stratum"] not in workload["thread_strata"]:
        raise ValueError("workload does not support the requested thread stratum")
    _validate_source_command(config["baseline"], registry, workload)
    _validate_source_command(config["candidate"], registry, workload)
    requested_level = ClaimLevel(config["requested_claim_level"])
    observed_level = ClaimLevel(live_host_probe["claim_level"])
    host_binding_matches = (
        _host_control_identity(host_probe) == _host_control_identity(live_host_probe)
    )
    corpus_receipt = {
        "path": str(actual_corpus_path.resolve()),
        "sha256": actual_corpus_sha256,
        "workload_id": workload["id"],
        "input_identity_sha256": workload["input_identity_sha256"],
    }
    if (
        not host_binding_matches
        or _CLAIM_LEVEL_RANK[observed_level] < _CLAIM_LEVEL_RANK[requested_level]
    ):
        binding_reason = ([] if host_binding_matches else [
            "supplied_host_control_identity_does_not_match_live_probe"
        ])
        return {
            "schema": RUN_RESULT_SCHEMA,
            "status": "BLOCKED_ENVIRONMENT",
            "requested_claim_level": requested_level.value,
            "observed_claim_level": observed_level.value,
            "acceptance_claim": "NONE",
            "candidate_resolved": False,
            "candidate_statistics_visible": False,
            "workload_executed": False,
            "supplied_host_probe_receipt_sha256": host_probe.get("receipt_sha256"),
            "live_host_probe_receipt_sha256": live_host_probe.get("receipt_sha256"),
            "blocking_reasons": [
                *live_host_probe.get("blockers", []),
                *binding_reason,
                *([] if _CLAIM_LEVEL_RANK[observed_level] >= _CLAIM_LEVEL_RANK[requested_level]
                  else ["observed_claim_level_below_requested_claim_level"]),
            ],
            "corpus": corpus_receipt,
        }

    strata = live_host_probe.get("strata", {})
    execution_cpu_set_raw = strata.get(config["stratum"], [])
    evidence_cpu_set_raw = strata.get(f"{config['stratum']}_smt_siblings", [])
    if not isinstance(execution_cpu_set_raw, list) or not execution_cpu_set_raw:
        raise RuntimeError("host probe does not provide the requested CPU stratum")
    if not isinstance(evidence_cpu_set_raw, list) or not evidence_cpu_set_raw:
        raise RuntimeError("host probe does not provide the stratum SMT reservation")
    execution_cpu_set = tuple(int(value) for value in execution_cpu_set_raw)
    evidence_cpu_set = tuple(int(value) for value in evidence_cpu_set_raw)
    if not set(execution_cpu_set).issubset(evidence_cpu_set):
        raise RuntimeError("execution CPUs are outside the reserved SMT evidence set")
    worker_count = 1 if config["stratum"] == "strict_1t" else 12

    # Baseline identity and preflight are resolved before candidate identity.
    baseline = resolver(config["baseline"])
    calibration_contract = {
        "mode": "calibrate",
        "repetitions": 1,
        "warmup_iterations": workload["warmup_iterations"],
        "minimum_duration_seconds": workload.get("minimum_duration_seconds"),
    }
    preflight = dict(collector.preflight(
        baseline, workload, execution_cpu_set, evidence_cpu_set, worker_count,
        calibration_contract,
    ))
    baseline_output_digest = preflight.get("output_digest")
    baseline_input_digest = preflight.get("input_identity_sha256")
    preflight_reasons = list(preflight.get("reasons", []))
    if not isinstance(baseline_output_digest, str) or len(baseline_output_digest) != 64:
        preflight_reasons.append("baseline_preflight_output_digest_unavailable")
    if baseline_input_digest != workload["input_identity_sha256"]:
        preflight_reasons.append("baseline_preflight_input_identity_mismatch")
    if preflight.get("status") != "PASS" or preflight_reasons:
        return {
            "schema": RUN_RESULT_SCHEMA,
            "status": "BLOCKED_ENVIRONMENT",
            "requested_claim_level": requested_level.value,
            "observed_claim_level": observed_level.value,
            "acceptance_claim": "NONE",
            "candidate_resolved": False,
            "candidate_statistics_visible": False,
            "workload_executed": True,
            "preflight_receipt_sha256": sha256_json(preflight),
            "blocking_reasons": sorted(set(preflight_reasons or ["baseline_preflight_failed"])),
            "corpus": corpus_receipt,
        }
    single_iteration_wall_time_ns = preflight.get("wall_time_ns")
    minimum_duration = workload.get("minimum_duration_seconds")
    try:
        repetitions = _calibrated_repetitions(
            single_iteration_wall_time_ns, minimum_duration,
        )
    except ValueError as exc:
        preflight_reasons.append(str(exc).replace(" ", "_"))
        repetitions = 1
    if preflight_reasons:
        return {
            "schema": RUN_RESULT_SCHEMA,
            "status": "BLOCKED_ENVIRONMENT",
            "requested_claim_level": requested_level.value,
            "observed_claim_level": observed_level.value,
            "acceptance_claim": "NONE",
            "candidate_resolved": False,
            "candidate_statistics_visible": False,
            "workload_executed": True,
            "preflight_receipt_sha256": sha256_json(preflight),
            "blocking_reasons": sorted(set(preflight_reasons)),
            "corpus": corpus_receipt,
        }
    sample_contract = {
        "mode": "sample",
        "repetitions": repetitions,
        "warmup_iterations": workload["warmup_iterations"],
        "minimum_duration_seconds": minimum_duration,
    }
    warmup_contract = {
        "mode": "warmup",
        "repetitions": 1,
        "warmup_iterations": workload["warmup_iterations"],
        "minimum_duration_seconds": minimum_duration,
    }
    calibration = {
        "limits": config.get("contamination_limits"),
        "execution_cpu_set": list(execution_cpu_set),
        "evidence_cpu_set": list(evidence_cpu_set),
        "calibration_contract": calibration_contract,
        "sample_contract": sample_contract,
        "baseline_preflight_sha256": sha256_json(preflight),
        "baseline_output_digest": baseline_output_digest,
        "baseline_input_identity_sha256": baseline_input_digest,
        "closed_before_candidate_resolution": True,
    }
    calibration["sha256"] = sha256_json(calibration)
    candidate = resolver(config["candidate"])
    candidate_warmup = dict(
        collector.warmup(
            candidate, workload, execution_cpu_set, evidence_cpu_set, worker_count,
            warmup_contract,
        )
    )
    warmup_reasons = list(candidate_warmup.get("reasons", []))
    if candidate_warmup.get("output_digest") != baseline_output_digest:
        warmup_reasons.append("candidate_warmup_output_differs_from_baseline_binding")
    if candidate_warmup.get("input_identity_sha256") != workload["input_identity_sha256"]:
        warmup_reasons.append("candidate_warmup_input_identity_mismatch")
    if candidate_warmup.get("status") != "PASS" or warmup_reasons:
        return {
            "schema": RUN_RESULT_SCHEMA,
            "status": "BLOCKED_CANDIDATE_WARMUP",
            "requested_claim_level": requested_level.value,
            "observed_claim_level": observed_level.value,
            "acceptance_claim": "NONE",
            "candidate_resolved": True,
            "candidate_statistics_visible": False,
            "workload_executed": True,
            "host_probe_receipt_sha256": live_host_probe.get("receipt_sha256"),
            "corpus": corpus_receipt,
            "sources": {"baseline": baseline.as_receipt(), "candidate": candidate.as_receipt()},
            "calibration": calibration,
            "candidate_warmup_receipt_sha256": sha256_json(candidate_warmup),
            "blocking_reasons": sorted(set(warmup_reasons or ["candidate_warmup_failed"])),
        }

    quota = config["valid_pairs_target"] // 2
    accepted_by_order = {"AB": 0, "BA": 0}
    accepted_pairs: list[dict[str, Any]] = []
    rejected_pairs: list[dict[str, Any]] = []
    rng = random.Random(config["seed"])
    for attempt in range(config["max_attempts"]):
        if accepted_by_order == {"AB": quota, "BA": quota}:
            break
        order = _choose_order(rng, accepted_by_order, quota)
        arm_order = ("baseline", "candidate") if order == "AB" else ("candidate", "baseline")
        observations: dict[str, Mapping[str, Any]] = {}
        for arm in arm_order:
            source = baseline if arm == "baseline" else candidate
            observations[arm] = collector.observe(
                source, workload, execution_cpu_set, evidence_cpu_set,
                worker_count, sample_contract,
            )
        pair = evaluate_pair(
            pair_index=attempt,
            order=order,
            baseline=observations["baseline"],
            candidate=observations["candidate"],
            claim_level=observed_level,
            expected_output_digest=(
                baseline_output_digest
                if workload["correctness_comparator"]["kind"] == "EXACT_OUTPUT_DIGEST"
                else None
            ),
        )
        if pair["accepted"]:
            accepted_pairs.append(pair)
            accepted_by_order[order] += 1
        else:
            rejected_pairs.append(pair)

    selected = [
        item for order in ("AB", "BA")
        for item in accepted_pairs if item["order"] == order
    ][: config["valid_pairs_target"]]
    summary = summarize_pairs(
        selected + rejected_pairs,
        claim_level=observed_level,
        valid_pairs_target=config["valid_pairs_target"],
        bootstrap_seed=config["seed"] + 10_000,
        bootstrap_replicates=config["bootstrap_replicates"],
    )
    return {
        "schema": RUN_RESULT_SCHEMA,
        "status": summary["status"],
        "acceptance_claim": summary["acceptance_claim"],
        "requested_claim_level": requested_level.value,
        "observed_claim_level": observed_level.value,
        "supplied_host_probe_receipt_sha256": host_probe.get("receipt_sha256"),
        "live_host_probe_receipt_sha256": live_host_probe.get("receipt_sha256"),
        "host_control_identity_sha256": _host_control_identity(live_host_probe),
        "corpus": corpus_receipt,
        "sources": {"baseline": baseline.as_receipt(), "candidate": candidate.as_receipt()},
        "calibration": calibration,
        "candidate_warmup_receipt_sha256": sha256_json(candidate_warmup),
        "schedule_contract": {
            "algorithm": "seeded_balanced_dynamic_quota_AB_BA",
            "seed": config["seed"],
            "valid_pairs_target": config["valid_pairs_target"],
            "max_attempts": config["max_attempts"],
            "bootstrap_replicates": config["bootstrap_replicates"],
            "bootstrap_seed": config["seed"] + 10_000,
        },
        "run_config_sha256": sha256_json(config),
        "common_build_identity_sha256": config["common_build_identity_sha256"],
        "attempts": len(accepted_pairs) + len(rejected_pairs),
        "accepted_by_order": accepted_by_order,
        "accepted_pairs": selected,
        "rejected_pairs": rejected_pairs,
        "summary": summary,
        "candidate_resolved": True,
        "candidate_statistics_visible": summary["candidate_statistics_visible"],
        "workload_executed": True,
    }
