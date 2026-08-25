from __future__ import annotations

from benchmarks.rfbench.host import ClaimLevel
from benchmarks.rfbench.protocol import (
    balanced_schedule,
    bootstrap_log_median_ci,
    evaluate_pair,
    sample_contamination_reasons,
    summarize_pairs,
)


DIGEST = "a" * 64
INPUT = "b" * 64
REQUIRED_PERF_EVENTS = (
    "task-clock", "cycles", "instructions", "branches", "branch-misses",
    "cache-references", "cache-misses", "context-switches", "cpu-migrations",
    "minor-faults", "major-faults",
)


def _perf_events():
    return {
        event: {
            "value": 1,
            "running_ratio": 0.999,
            "time_running_ns": 999,
            "time_enabled_ns": 1000,
        }
        for event in REQUIRED_PERF_EVENTS
    }


def _metrics(**updates):
    value = {
        "cgroup_partition_before": "isolated",
        "cgroup_partition_after": "isolated",
        "cgroup_effective_cpuset_before": [0, 1],
        "cgroup_effective_cpuset_after": [0, 1],
        "cgroup_exclusive_cpuset_before": [0, 1],
        "cgroup_exclusive_cpuset_after": [0, 1],
        "cgroup_procs_before": [101],
        "cgroup_procs_after": [101],
        "expected_cgroup_procs": [101],
        "expected_cpuset": [0, 1],
        "selected_cpu_evidence_set": [0, 1],
        "worker_affinities": [[0, 1]],
        "expected_worker_affinities": [[0, 1]],
        "worker_count": 1,
        "per_worker_task_clock_ns": [1_000],
        "perf_required_events_present": True,
        "perf_events": _perf_events(),
        "first_touch": {
            "status": "VERIFIED_NOT_APPLICABLE_STARTUP_WORKLOAD",
            "verified": True,
        },
        "thread_ownership": {
            "non_owner_libraries_forced_to_one": True,
            "verified": True,
        },
        "cpu_migrations": 0,
        "major_faults_after_warmup": 0,
        "steal_time_delta": 0,
        "thermal_throttle_event_delta": 0,
        "perf_running_over_enabled": 0.999,
        "cgroup_cpu_psi_some_fraction": 0.0,
        "system_cpu_psi_some_fraction": 0.99,
        "external_busy_fraction": 0.0,
        "benchmark_cgroup_cpu_stat_delta": {
            "usage_usec": 100,
            "user_usec": 80,
            "system_usec": 20,
        },
        "selected_cpu_proc_stat_delta": {
            "0": [1, 0, 1, 10, 0, 0, 0, 0],
            "1": [1, 0, 1, 10, 0, 0, 0, 0],
        },
        "selected_cpu_irq_delta": {"0": 0, "1": 0},
        "involuntary_context_switches": 0,
        "effective_frequency_hz": 4_000_000_000.0,
        "temperature_max_millicelsius": 45_000,
    }
    value.update(updates)
    return value


def _observation(wall: int, **metric_updates):
    return {
        "wall_time_ns": wall,
        "output_digest": DIGEST,
        "input_identity_sha256": INPUT,
        "metrics": _metrics(**metric_updates),
    }


def test_schedule_and_bootstrap_are_seeded_and_deterministic():
    first = balanced_schedule(30, 20260825)
    second = balanced_schedule(30, 20260825)
    assert first == second
    assert first.count("AB") == first.count("BA") == 15
    assert bootstrap_log_median_ci([0.0, 0.1, -0.1], seed=9, replicates=1000) == \
        bootstrap_log_median_ci([0.0, 0.1, -0.1], seed=9, replicates=1000)


def test_system_wide_psi_is_context_only():
    assert sample_contamination_reasons(_metrics(system_cpu_psi_some_fraction=1.0)) == []


def test_live_cgroup_state_must_remain_exact_before_and_after_sample():
    assert "cgroup_partition_after_not_isolated" in sample_contamination_reasons(
        _metrics(cgroup_partition_after="member")
    )
    assert "cgroup_exclusive_cpuset_mismatch" in sample_contamination_reasons(
        _metrics(cgroup_exclusive_cpuset_after=[0])
    )
    assert "cgroup_procs_mismatch" in sample_contamination_reasons(
        _metrics(cgroup_procs_after=[101, 202])
    )


def test_worker_receipt_requires_exact_affinity_task_clock_and_ownership():
    reasons = sample_contamination_reasons(_metrics(
        worker_affinities=[[0]],
        per_worker_task_clock_ns=[0],
        first_touch={"status": "UNKNOWN", "verified": False},
        thread_ownership={
            "non_owner_libraries_forced_to_one": False,
            "verified": False,
        },
    ))
    assert "worker_affinities_mismatch" in reasons
    assert "per_worker_task_clock_invalid" in reasons
    assert "first_touch_unverified" in reasons
    assert "thread_ownership_unverified" in reasons


def test_missing_raw_observation_sources_never_become_clean_zeroes():
    reasons = sample_contamination_reasons(_metrics(
        benchmark_cgroup_cpu_stat_delta={},
        selected_cpu_proc_stat_delta={"0": [0] * 8},
        selected_cpu_irq_delta={"0": 0},
        system_cpu_psi_some_fraction=None,
        temperature_max_millicelsius=None,
        thermal_throttle_event_delta=None,
    ))
    assert "benchmark_cgroup_cpu_stat_delta_unavailable" in reasons
    assert "selected_cpu_proc_stat_delta_incomplete" in reasons
    assert "selected_cpu_irq_delta_incomplete" in reasons
    assert "system_cpu_psi_context_unavailable" in reasons
    assert "temperature_observation_unavailable" in reasons
    assert "thermal_throttle_event_delta_unavailable" in reasons


def test_perf_requires_every_exact_event_and_its_enabled_running_receipt():
    missing = _perf_events()
    missing.pop("cache-misses")
    reasons = sample_contamination_reasons(_metrics(perf_events=missing))
    assert "perf_required_events_incomplete" in reasons

    bad_ratio = _perf_events()
    bad_ratio["cycles"] = {
        "value": 1,
        "running_ratio": None,
        "time_running_ns": None,
        "time_enabled_ns": None,
    }
    reasons = sample_contamination_reasons(_metrics(perf_events=bad_ratio))
    assert "perf_event_running_ratio_invalid" in reasons

    reasons = sample_contamination_reasons(_metrics(
        perf_running_over_enabled=1.0,
    ))
    assert "perf_running_ratio_not_exact_event_minimum" in reasons


def test_contaminated_pair_redacts_both_arms_before_candidate_visibility():
    pair = evaluate_pair(
        pair_index=0,
        order="AB",
        baseline=_observation(100),
        candidate=_observation(90, cpu_migrations=1),
        claim_level=ClaimLevel.CONTROLLED_SHARED_PAIRED,
    )
    assert pair["accepted"] is False
    assert pair["candidate_visible_to_statistics"] is False
    encoded = repr(pair)
    assert "wall_time_ns" not in encoded
    assert DIGEST not in encoded
    assert INPUT not in encoded
    assert "sha256" not in encoded
    assert pair["arms"]["candidate"] == {"status": "REDACTED_CONTAMINATED"}


def test_output_must_match_the_preflight_binding_even_when_arms_match_each_other():
    pair = evaluate_pair(
        pair_index=0,
        order="AB",
        baseline=_observation(100),
        candidate=_observation(90),
        claim_level=ClaimLevel.CONTROLLED_SHARED_PAIRED,
        expected_output_digest="c" * 64,
    )
    assert pair["accepted"] is False
    assert pair["candidate_visible_to_statistics"] is False
    assert pair["reasons"] == [
        "baseline_output_differs_from_preflight_binding",
        "candidate_output_differs_from_preflight_binding",
    ]


def test_non_exact_comparator_does_not_apply_output_digest_identity():
    baseline = _observation(100)
    candidate = _observation(90)
    candidate["output_digest"] = "d" * 64
    pair = evaluate_pair(
        pair_index=0,
        order="AB",
        baseline=baseline,
        candidate=candidate,
        claim_level=ClaimLevel.CONTROLLED_SHARED_PAIRED,
        expected_output_digest=None,
    )
    assert pair["accepted"] is True


def test_exploratory_level_never_exposes_candidate_statistics():
    pair = evaluate_pair(
        pair_index=0, order="AB", baseline=_observation(100),
        candidate=_observation(90), claim_level=ClaimLevel.EXPLORATORY_ONLY,
    )
    result = summarize_pairs(
        [pair], claim_level=ClaimLevel.EXPLORATORY_ONLY,
        valid_pairs_target=30, bootstrap_seed=1,
    )
    assert result["status"] == "EXPLORATORY_ONLY"
    assert result["acceptance_claim"] == "NONE"
    assert result["candidate_statistics_visible"] is False


def test_summary_requires_fifteen_clean_pairs_in_each_order():
    pairs = []
    for index in range(30):
        order = "AB" if index < 15 else "BA"
        pairs.append(evaluate_pair(
            pair_index=index, order=order, baseline=_observation(100),
            candidate=_observation(90),
            claim_level=ClaimLevel.CONTROLLED_SHARED_PAIRED,
        ))
    summary = summarize_pairs(
        pairs, claim_level=ClaimLevel.CONTROLLED_SHARED_PAIRED,
        valid_pairs_target=30, bootstrap_seed=7, bootstrap_replicates=1000,
    )
    assert summary["status"] == "CONTROLLED_PAIRED_EVIDENCE"
    assert summary["accepted_by_order"] == {"AB": 15, "BA": 15}
    assert summary["candidate_over_baseline"] == 0.9
    assert summary["replay"] == {
        "bootstrap_algorithm": "paired_log_ratio_nonparametric_resample_v1",
        "bootstrap_replicates": 1000,
        "bootstrap_rng": "python_random_mt19937",
        "bootstrap_seed": 7,
        "quantile_method": "linear_interpolation_at_(n_minus_1)_p",
        "selection_algorithm": "first_clean_quota_per_order_AB_then_BA_v1",
        "selected_log_ratio_sha256": (
            "31812e05e87f229717e4045b7540a2dd9d0ae5e5a9b2636c634d4b22ad1993ef"
        ),
        "statistic_algorithm": "exp_median_log_candidate_over_baseline_v1",
    }


def test_unbalanced_clean_population_is_blocked_without_statistics():
    pairs = [
        evaluate_pair(
            pair_index=index, order="AB", baseline=_observation(100),
            candidate=_observation(90),
            claim_level=ClaimLevel.CONTROLLED_SHARED_PAIRED,
        )
        for index in range(30)
    ]
    summary = summarize_pairs(
        pairs, claim_level=ClaimLevel.CONTROLLED_SHARED_PAIRED,
        valid_pairs_target=30, bootstrap_seed=7,
    )
    assert summary["status"] == "BLOCKED_CONTAMINATED"
    assert summary["candidate_statistics_visible"] is False
    assert "candidate_over_baseline" not in summary
