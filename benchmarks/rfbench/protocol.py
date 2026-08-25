"""Pure RF-BENCH-00 schedule, contamination, and paired-statistics contract."""

from __future__ import annotations

import hashlib
import json
import math
import random
import statistics
from typing import Any, Iterable, Mapping

from .host import ClaimLevel


CONTAMINATION_LIMITS: dict[str, float | int | bool | str] = {
    "cpuset_partition_state": "isolated",
    "effective_cpuset_exact_match": True,
    "cpu_migrations": 0,
    "major_faults_after_warmup": 0,
    "steal_time_delta": 0,
    "thermal_throttle_event_delta": 0,
    "perf_running_over_enabled_min": 0.95,
    "benchmark_cgroup_cpu_psi_some_fraction_max": 0.001,
    "external_busy_fraction_on_selected_cpus_max": 0.001,
    "paired_effective_frequency_relative_delta_max": 0.005,
    "involuntary_context_switches_max_per_worker_sample": 1,
    "system_wide_cpu_psi": "CONTEXT_WARNING_ONLY_NOT_A_HARD_GATE",
}

REQUIRED_PERF_EVENTS = (
    "task-clock",
    "cycles",
    "instructions",
    "branches",
    "branch-misses",
    "cache-references",
    "cache-misses",
    "context-switches",
    "cpu-migrations",
    "minor-faults",
    "major-faults",
)


def _canonical_json(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def sha256_json(value: object) -> str:
    return hashlib.sha256(_canonical_json(value)).hexdigest()


def balanced_schedule(pairs: int, seed: int) -> list[str]:
    if pairs < 2:
        raise ValueError("at least two paired blocks are required")
    schedule = ["AB", "BA"] * (pairs // 2)
    if pairs % 2:
        schedule.append("AB" if seed % 2 == 0 else "BA")
    random.Random(seed).shuffle(schedule)
    return schedule


def _quantile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    if not ordered:
        raise ValueError("quantile requires at least one value")
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def bootstrap_log_median_ci(
    log_ratios: Iterable[float], *, seed: int, replicates: int
) -> tuple[float, float]:
    values = list(log_ratios)
    if not values:
        raise ValueError("bootstrap requires at least one paired log-ratio")
    if replicates < 1:
        raise ValueError("bootstrap replicates must be positive")
    rng = random.Random(seed)
    count = len(values)
    medians = [
        statistics.median(values[rng.randrange(count)] for _ in range(count))
        for _ in range(replicates)
    ]
    return math.exp(_quantile(medians, 0.025)), math.exp(_quantile(medians, 0.975))


def _required_number(metrics: Mapping[str, Any], name: str) -> float | None:
    value = metrics.get(name)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    if not math.isfinite(float(value)):
        return None
    return float(value)


def _canonical_nonnegative_int_list(value: object) -> list[int] | None:
    if (
        not isinstance(value, list)
        or any(isinstance(item, bool) or not isinstance(item, int) or item < 0
               for item in value)
        or value != sorted(set(value))
    ):
        return None
    return value


def _canonical_positive_int_list(value: object) -> list[int] | None:
    result = _canonical_nonnegative_int_list(value)
    if result is None or not result or any(item == 0 for item in result):
        return None
    return result


def _canonical_affinities(value: object, worker_count: int) -> list[list[int]] | None:
    if not isinstance(value, list) or len(value) != worker_count:
        return None
    result: list[list[int]] = []
    for item in value:
        affinity = _canonical_nonnegative_int_list(item)
        if affinity is None or not affinity:
            return None
        result.append(affinity)
    return result


def _raw_cpu_vectors_complete(
    value: object, evidence_cpus: list[int], *, vector: bool,
) -> bool:
    if not isinstance(value, Mapping) or set(value) != {
        str(cpu) for cpu in evidence_cpus
    }:
        return False
    for item in value.values():
        if vector:
            if (
                not isinstance(item, list)
                or len(item) < 8
                or any(isinstance(entry, bool) or not isinstance(entry, int) or entry < 0
                       for entry in item)
            ):
                return False
        elif isinstance(item, bool) or not isinstance(item, int) or item < 0:
            return False
    return True


def _perf_receipt_reasons(metrics: Mapping[str, Any]) -> list[str]:
    reasons: list[str] = []
    receipts = metrics.get("perf_events")
    if not isinstance(receipts, Mapping) or set(receipts) != set(REQUIRED_PERF_EVENTS):
        return ["perf_required_events_incomplete"]

    ratios: list[float] = []
    for event in REQUIRED_PERF_EVENTS:
        receipt = receipts.get(event)
        if not isinstance(receipt, Mapping):
            reasons.append("perf_event_receipt_invalid")
            continue
        value = receipt.get("value")
        ratio = receipt.get("running_ratio")
        running = receipt.get("time_running_ns")
        enabled = receipt.get("time_enabled_ns")
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(float(value))
            or float(value) < 0.0
        ):
            reasons.append("perf_event_value_invalid")
        if (
            isinstance(ratio, bool)
            or not isinstance(ratio, (int, float))
            or not math.isfinite(float(ratio))
            or not 0.0 < float(ratio) <= 1.0
            or isinstance(running, bool)
            or not isinstance(running, (int, float))
            or not math.isfinite(float(running))
            or float(running) <= 0.0
            or isinstance(enabled, bool)
            or not isinstance(enabled, (int, float))
            or not math.isfinite(float(enabled))
            or float(enabled) <= 0.0
            or float(running) > float(enabled)
            or not math.isclose(
                float(ratio), float(running) / float(enabled),
                rel_tol=0.0, abs_tol=1e-12,
            )
        ):
            reasons.append("perf_event_running_ratio_invalid")
        else:
            ratios.append(float(ratio))

    aggregate = _required_number(metrics, "perf_running_over_enabled")
    if aggregate is None:
        reasons.append("perf_running_ratio_unavailable")
    elif ratios and not math.isclose(
        aggregate, min(ratios), rel_tol=0.0, abs_tol=1e-12,
    ):
        reasons.append("perf_running_ratio_not_exact_event_minimum")
    elif aggregate < float(CONTAMINATION_LIMITS["perf_running_over_enabled_min"]):
        reasons.append("perf_running_ratio_below_minimum")
    return reasons


def sample_contamination_reasons(metrics: Mapping[str, Any]) -> list[str]:
    """Evaluate hard sample gates; system-wide PSI remains context only."""

    reasons: list[str] = []
    for phase in ("before", "after"):
        if metrics.get(f"cgroup_partition_{phase}") != "isolated":
            reasons.append(f"cgroup_partition_{phase}_not_isolated")

    expected = _canonical_nonnegative_int_list(metrics.get("expected_cpuset"))
    if not expected:
        reasons.append("expected_cpuset_invalid")
    for prefix, reason in (
        ("cgroup_effective_cpuset", "cgroup_effective_cpuset_mismatch"),
        ("cgroup_exclusive_cpuset", "cgroup_exclusive_cpuset_mismatch"),
    ):
        before = _canonical_nonnegative_int_list(metrics.get(f"{prefix}_before"))
        after = _canonical_nonnegative_int_list(metrics.get(f"{prefix}_after"))
        if not expected or before != expected or after != expected:
            reasons.append(reason)

    expected_procs = _canonical_positive_int_list(metrics.get("expected_cgroup_procs"))
    before_procs = _canonical_positive_int_list(metrics.get("cgroup_procs_before"))
    after_procs = _canonical_positive_int_list(metrics.get("cgroup_procs_after"))
    if (
        expected_procs is None
        or before_procs != expected_procs
        or after_procs != expected_procs
    ):
        reasons.append("cgroup_procs_mismatch")

    evidence_cpus = _canonical_nonnegative_int_list(
        metrics.get("selected_cpu_evidence_set")
    )
    if not evidence_cpus or not expected or not set(evidence_cpus).issubset(expected):
        reasons.append("selected_cpu_evidence_set_invalid")
        evidence_cpus = []

    workers = _required_number(metrics, "worker_count")
    if workers is None or workers < 1.0 or not workers.is_integer():
        reasons.append("worker_count_invalid")
        worker_count = 0
    else:
        worker_count = int(workers)
    expected_affinities = _canonical_affinities(
        metrics.get("expected_worker_affinities"), worker_count,
    )
    affinities = _canonical_affinities(metrics.get("worker_affinities"), worker_count)
    if (
        expected_affinities is None
        or affinities != expected_affinities
        or not expected
        or any(not set(mask).issubset(expected) for mask in affinities or ())
    ):
        reasons.append("worker_affinities_mismatch")
    task_clocks = metrics.get("per_worker_task_clock_ns")
    if (
        not isinstance(task_clocks, list)
        or len(task_clocks) != worker_count
        or any(isinstance(value, bool) or not isinstance(value, int) or value <= 0
               for value in task_clocks)
    ):
        reasons.append("per_worker_task_clock_invalid")
    first_touch = metrics.get("first_touch")
    if (
        not isinstance(first_touch, Mapping)
        or first_touch.get("verified") is not True
        or not isinstance(first_touch.get("status"), str)
        or not first_touch.get("status")
    ):
        reasons.append("first_touch_unverified")
    ownership = metrics.get("thread_ownership")
    if (
        not isinstance(ownership, Mapping)
        or ownership.get("verified") is not True
        or ownership.get("non_owner_libraries_forced_to_one") is not True
    ):
        reasons.append("thread_ownership_unverified")

    if metrics.get("perf_required_events_present") is not True:
        reasons.append("perf_required_events_missing")
    reasons.extend(_perf_receipt_reasons(metrics))
    if metrics.get("sample_duration_below_minimum") is True:
        reasons.append("sample_duration_below_minimum")

    cgroup_stat = metrics.get("benchmark_cgroup_cpu_stat_delta")
    if (
        not isinstance(cgroup_stat, Mapping)
        or "usage_usec" not in cgroup_stat
        or any(isinstance(value, bool) or not isinstance(value, int) or value < 0
               for value in cgroup_stat.values())
    ):
        reasons.append("benchmark_cgroup_cpu_stat_delta_unavailable")
    if not _raw_cpu_vectors_complete(
        metrics.get("selected_cpu_proc_stat_delta"), evidence_cpus, vector=True,
    ):
        reasons.append("selected_cpu_proc_stat_delta_incomplete")
    if not _raw_cpu_vectors_complete(
        metrics.get("selected_cpu_irq_delta"), evidence_cpus, vector=False,
    ):
        reasons.append("selected_cpu_irq_delta_incomplete")

    system_psi = _required_number(metrics, "system_cpu_psi_some_fraction")
    if system_psi is None or system_psi < 0.0:
        reasons.append("system_cpu_psi_context_unavailable")
    temperature = _required_number(metrics, "temperature_max_millicelsius")
    if temperature is None:
        reasons.append("temperature_observation_unavailable")

    exact_zero = (
        "cpu_migrations",
        "major_faults_after_warmup",
        "steal_time_delta",
        "thermal_throttle_event_delta",
    )
    for name in exact_zero:
        value = _required_number(metrics, name)
        if value is None:
            reasons.append(f"{name}_unavailable")
        elif value != 0.0:
            reasons.append(f"{name}_nonzero")

    upper_bounds = {
        "cgroup_cpu_psi_some_fraction": float(
            CONTAMINATION_LIMITS["benchmark_cgroup_cpu_psi_some_fraction_max"]
        ),
        "external_busy_fraction": float(
            CONTAMINATION_LIMITS["external_busy_fraction_on_selected_cpus_max"]
        ),
    }
    for name, maximum in upper_bounds.items():
        value = _required_number(metrics, name)
        if value is None:
            reasons.append(f"{name}_unavailable")
        elif value > maximum:
            reasons.append(f"{name}_above_maximum")

    switches = _required_number(metrics, "involuntary_context_switches")
    workers = _required_number(metrics, "worker_count")
    if switches is None or workers is None or workers < 1.0:
        reasons.append("involuntary_context_switch_budget_unavailable")
    elif switches > workers * int(
        CONTAMINATION_LIMITS["involuntary_context_switches_max_per_worker_sample"]
    ):
        reasons.append("involuntary_context_switch_budget_exceeded")
    return sorted(set(reasons))


def _redacted_arm() -> dict[str, Any]:
    return {"status": "REDACTED_CONTAMINATED"}


def _visible_arm(observation: Mapping[str, Any]) -> dict[str, Any]:
    wall = observation.get("wall_time_ns")
    if isinstance(wall, bool) or not isinstance(wall, int) or wall <= 0:
        raise ValueError("accepted observation requires positive integer wall_time_ns")
    output_digest = observation.get("output_digest")
    input_digest = observation.get("input_identity_sha256")
    if not isinstance(output_digest, str) or len(output_digest) != 64:
        raise ValueError("accepted observation requires output_digest")
    if not isinstance(input_digest, str) or len(input_digest) != 64:
        raise ValueError("accepted observation requires input_identity_sha256")
    return {
        "status": "VISIBLE_AFTER_CONTAMINATION_PASS",
        "candidate_visible_to_statistics": True,
        "wall_time_ns": wall,
        "output_digest": output_digest,
        "input_identity_sha256": input_digest,
        "metrics": observation["metrics"],
    }


def evaluate_pair(
    *,
    pair_index: int,
    order: str,
    baseline: Mapping[str, Any],
    candidate: Mapping[str, Any],
    claim_level: ClaimLevel | str,
    expected_output_digest: str | None = None,
) -> dict[str, Any]:
    """Gate both arms before exposing candidate timing to paired statistics."""

    if order not in {"AB", "BA"}:
        raise ValueError("pair order must be AB or BA")
    level = ClaimLevel(claim_level)
    reasons = [f"baseline:{value}" for value in sample_contamination_reasons(
        baseline.get("metrics", {})
    )]
    reasons.extend(
        f"candidate:{value}" for value in sample_contamination_reasons(
            candidate.get("metrics", {})
        )
    )
    if level is ClaimLevel.EXPLORATORY_ONLY:
        reasons.append("claim_level_below_controlled_shared_paired")

    baseline_frequency = _required_number(baseline.get("metrics", {}), "effective_frequency_hz")
    candidate_frequency = _required_number(candidate.get("metrics", {}), "effective_frequency_hz")
    if baseline_frequency is None or candidate_frequency is None:
        reasons.append("paired_effective_frequency_unavailable")
    else:
        denominator = max(abs(baseline_frequency), abs(candidate_frequency), 1.0)
        relative = abs(candidate_frequency - baseline_frequency) / denominator
        if relative > float(
            CONTAMINATION_LIMITS["paired_effective_frequency_relative_delta_max"]
        ):
            reasons.append("paired_effective_frequency_delta_above_maximum")

    for name, observation in (("baseline", baseline), ("candidate", candidate)):
        output_digest = observation.get("output_digest")
        input_digest = observation.get("input_identity_sha256")
        if not isinstance(output_digest, str) or len(output_digest) != 64:
            reasons.append(f"{name}:output_digest_invalid")
        if not isinstance(input_digest, str) or len(input_digest) != 64:
            reasons.append(f"{name}:input_identity_invalid")
    if baseline.get("input_identity_sha256") != candidate.get("input_identity_sha256"):
        reasons.append("paired_input_identity_mismatch")
    if expected_output_digest is not None:
        if not isinstance(expected_output_digest, str) or len(expected_output_digest) != 64:
            raise ValueError("expected_output_digest must be a 64-character digest")
        if baseline.get("output_digest") != expected_output_digest:
            reasons.append("baseline_output_differs_from_preflight_binding")
        if candidate.get("output_digest") != expected_output_digest:
            reasons.append("candidate_output_differs_from_preflight_binding")
    reasons = sorted(set(reasons))
    if reasons:
        return {
            "pair_index": pair_index,
            "order": order,
            "accepted": False,
            "candidate_visible_to_statistics": False,
            "reasons": reasons,
            "arms": {
                "baseline": _redacted_arm(),
                "candidate": _redacted_arm(),
            },
        }
    return {
        "pair_index": pair_index,
        "order": order,
        "accepted": True,
        "candidate_visible_to_statistics": True,
        "reasons": [],
        "arms": {
            "baseline": _visible_arm(baseline),
            "candidate": _visible_arm(candidate),
        },
    }


def summarize_pairs(
    pairs: Iterable[Mapping[str, Any]],
    *,
    claim_level: ClaimLevel | str,
    valid_pairs_target: int = 30,
    bootstrap_seed: int,
    bootstrap_replicates: int = 10_000,
) -> dict[str, Any]:
    """Summarize only accepted pairs; never peek through rejected records."""

    level = ClaimLevel(claim_level)
    pair_list = list(pairs)
    accepted = [item for item in pair_list if item.get("accepted") is True]
    if valid_pairs_target < 2 or valid_pairs_target % 2:
        raise ValueError("valid_pairs_target must be a positive even number")
    quota = valid_pairs_target // 2
    accepted_by_order = {
        order: [item for item in accepted if item.get("order") == order]
        for order in ("AB", "BA")
    }
    if level is ClaimLevel.EXPLORATORY_ONLY:
        return {
            "status": "EXPLORATORY_ONLY",
            "acceptance_claim": "NONE",
            "candidate_statistics_visible": False,
            "accepted_pairs": len(accepted),
            "rejected_pairs": len(pair_list) - len(accepted),
            "reason": "authority claims require CONTROLLED_SHARED_PAIRED or stronger",
        }
    if any(len(accepted_by_order[order]) < quota for order in ("AB", "BA")):
        return {
            "status": "BLOCKED_CONTAMINATED",
            "acceptance_claim": "NONE",
            "candidate_statistics_visible": False,
            "accepted_pairs": len(accepted),
            "accepted_by_order": {
                order: len(values) for order, values in accepted_by_order.items()
            },
            "rejected_pairs": len(pair_list) - len(accepted),
            "required_pairs": valid_pairs_target,
            "required_by_order": {"AB": quota, "BA": quota},
        }
    selected = [
        item for order in ("AB", "BA")
        for item in accepted_by_order[order][:quota]
    ]
    log_ratios = [
        math.log(
            item["arms"]["candidate"]["wall_time_ns"]
            / item["arms"]["baseline"]["wall_time_ns"]
        )
        for item in selected
    ]
    ratio = math.exp(statistics.median(log_ratios))
    low, high = bootstrap_log_median_ci(
        log_ratios, seed=bootstrap_seed, replicates=bootstrap_replicates,
    )
    return {
        "status": "CONTROLLED_PAIRED_EVIDENCE",
        "acceptance_claim": "DECISION_DEFERRED_TO_NODE_SPECIFIC_GATE",
        "candidate_statistics_visible": True,
        "accepted_pairs": valid_pairs_target,
        "accepted_by_order": {"AB": quota, "BA": quota},
        "rejected_pairs": len(pair_list) - len(accepted),
        "statistic": "exp(median(log(candidate_ns/baseline_ns)))",
        "candidate_over_baseline": ratio,
        "bootstrap_95_ci": [low, high],
        "bootstrap_replicates": bootstrap_replicates,
        "replay": {
            "bootstrap_algorithm": "paired_log_ratio_nonparametric_resample_v1",
            "bootstrap_replicates": bootstrap_replicates,
            "bootstrap_rng": "python_random_mt19937",
            "bootstrap_seed": bootstrap_seed,
            "quantile_method": "linear_interpolation_at_(n_minus_1)_p",
            "selection_algorithm": "first_clean_quota_per_order_AB_then_BA_v1",
            "selected_log_ratio_sha256": sha256_json(log_ratios),
            "statistic_algorithm": "exp_median_log_candidate_over_baseline_v1",
        },
    }
