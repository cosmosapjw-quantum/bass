from __future__ import annotations

from pathlib import Path

import pytest

from benchmarks.rfbench.corpus import (
    CORPUS_PATH,
    REQUIRED_STRATA,
    describe,
    load_registry,
    select_workloads,
    sha256_file,
)
from benchmarks.rfbench.host import ClaimLevel
from benchmarks.rfbench.protocol import CONTAMINATION_LIMITS
from benchmarks.rfbench.runner import (
    ResolvedSource,
    _calibrated_repetitions,
    run_protocol,
)


def _config() -> dict:
    common_build = {
        "cargo_lock_sha256": "d500208e9353ade1cb74693918598846628219e6e7bd2e2bce9ec85e29eb6310",
        "rustc_version": "1.94.1",
        "python_abi": "cp312-cp312-manylinux_2_34_x86_64",
        "build_profile": "release",
        "cpu_variant": "strict-portable",
        "optional_features": [],
    }
    return {
        "schema": "bass-rfbench-run-config-v1",
        "requested_claim_level": "CONTROLLED_SHARED_PAIRED",
        "workload_id": "startup_cold_backend_import",
        "phase": "tuning",
        "stratum": "strict_1t",
        "baseline": {
            "root": "/baseline", "ref": "1" * 40,
            "python": "/usr/bin/python3",
            "command": ["{python}",
                        "{runner_root}/benchmarks/rfbench/workload_child.py",
                        "--workload-id", "startup_cold_backend_import"],
            "environment_identity_sha256": "3" * 64,
            "native_artifact_sha256": "4" * 64,
        },
        "candidate": {
            "root": "/candidate", "ref": "2" * 40,
            "python": "/usr/bin/python3",
            "command": ["{python}",
                        "{runner_root}/benchmarks/rfbench/workload_child.py",
                        "--workload-id", "startup_cold_backend_import"],
            "environment_identity_sha256": "3" * 64,
            "native_artifact_sha256": "5" * 64,
        },
        "valid_pairs_target": 30,
        "max_attempts": 90,
        "bootstrap_replicates": 10000,
        "seed": 20260825,
        "contamination_limits": CONTAMINATION_LIMITS,
        "corpus_sha256": sha256_file(CORPUS_PATH),
        "spec_sha256": "dcd4f89fe7a2ad73f22574357df53fcbea437d83f1b4faae08250e2ab46b4efa",
        "source_adapter_sha256": "a9f7a2f2bb516095b1f8bea7a09910fddf592752ae07796ff37a24b8200a1e71",
        "common_build_identity": common_build,
        "common_build_identity_sha256": "9074e0eb08c0be1e069a0b1ee5ac2e50716903f51bee65af2401cf20eb08ddde",
    }


def _host(level: ClaimLevel) -> dict:
    value = {
        "schema": "bass-rfbench-host-capability-v1",
        "claim_level": level.value,
        "blockers": ["synthetic_control_gap"] if level is ClaimLevel.EXPLORATORY_ONLY else [],
        "strata": {
            "strict_1t": [0],
            "strict_1t_smt_siblings": [0, 12],
            "physical_12t": list(range(12)),
            "physical_12t_smt_siblings": list(range(24)),
        },
    }
    import hashlib
    import json
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"),
                         ensure_ascii=True, allow_nan=False).encode("ascii")
    value["receipt_sha256"] = hashlib.sha256(encoded).hexdigest()
    return value


def _metrics(*, contaminated: bool = False) -> dict:
    perf_events = {
        event: {
            "value": 1,
            "running_ratio": 0.999,
            "time_running_ns": 999,
            "time_enabled_ns": 1000,
        }
        for event in (
            "task-clock", "cycles", "instructions", "branches",
            "branch-misses", "cache-references", "cache-misses",
            "context-switches", "cpu-migrations", "minor-faults",
            "major-faults",
        )
    }
    return {
        "cgroup_partition_before": "isolated",
        "cgroup_partition_after": "isolated",
        "cgroup_effective_cpuset_before": [0, 12],
        "cgroup_effective_cpuset_after": [0, 12],
        "cgroup_exclusive_cpuset_before": [0, 12],
        "cgroup_exclusive_cpuset_after": [0, 12],
        "expected_cpuset": [0, 12],
        "selected_cpu_evidence_set": [0, 12],
        "worker_affinities": [[0]],
        "expected_worker_affinities": [[0]],
        "worker_count": 1,
        "per_worker_task_clock_ns": [100],
        "perf_required_events_present": True,
        "perf_events": perf_events,
        "first_touch": {
            "status": "VERIFIED_NOT_APPLICABLE_STARTUP_WORKLOAD",
            "verified": True,
        },
        "thread_ownership": {
            "non_owner_libraries_forced_to_one": True,
            "verified": True,
        },
        "cpu_migrations": 1 if contaminated else 0,
        "major_faults_after_warmup": 0,
        "steal_time_delta": 0,
        "thermal_throttle_event_delta": 0,
        "perf_running_over_enabled": 0.999,
        "cgroup_cpu_psi_some_fraction": 0.0,
        "system_cpu_psi_some_fraction": 0.0,
        "external_busy_fraction": 0.0,
        "involuntary_context_switches": 0,
        "effective_frequency_hz": 4_000_000_000.0,
        "benchmark_cgroup_cpu_stat_delta": {"usage_usec": 1},
        "benchmark_cgroup_cpu_psi_delta_us": 0,
        "selected_cpu_proc_stat_delta": {"0": [1] * 10, "12": [1] * 10},
        "selected_cpu_irq_delta": {"0": 0, "12": 0},
        "temperature_max_millicelsius": 50_000,
        "cgroup_procs_before": [123],
        "cgroup_procs_after": [123],
        "expected_cgroup_procs": [123],
    }


class _Collector:
    def __init__(self, candidate_failures: int = 0, *, preflight_digest: str = "a" * 64):
        self.candidate_failures = candidate_failures
        self.preflight_digest = preflight_digest
        self.preflight_calls = 0
        self.warmup_calls = 0
        self.contracts: list[dict] = []

    def preflight(
        self, source, workload, execution_cpu_set, evidence_cpu_set,
        worker_count, run_contract,
    ):
        self.preflight_calls += 1
        assert execution_cpu_set == (0,)
        assert evidence_cpu_set == (0, 12)
        self.contracts.append(dict(run_contract))
        return {
            "status": "PASS",
            "reasons": [],
            "output_digest": self.preflight_digest,
            "input_identity_sha256": workload["input_identity_sha256"],
            "wall_time_ns": 250_000_000,
        }

    def warmup(
        self, source, workload, execution_cpu_set, evidence_cpu_set,
        worker_count, run_contract,
    ):
        self.warmup_calls += 1
        assert execution_cpu_set == (0,)
        assert evidence_cpu_set == (0, 12)
        self.contracts.append(dict(run_contract))
        return {
            "status": "PASS",
            "reasons": [],
            "output_digest": self.preflight_digest,
            "input_identity_sha256": workload["input_identity_sha256"],
        }

    def observe(
        self, source, workload, execution_cpu_set, evidence_cpu_set,
        worker_count, run_contract,
    ):
        assert execution_cpu_set == (0,)
        assert evidence_cpu_set == (0, 12)
        self.contracts.append(dict(run_contract))
        contaminated = source.head == "2" * 40 and self.candidate_failures > 0
        if contaminated:
            self.candidate_failures -= 1
        return {
            "wall_time_ns": 90 if source.head == "2" * 40 else 100,
            "output_digest": "a" * 64,
            "input_identity_sha256": workload["input_identity_sha256"],
            "metrics": _metrics(contaminated=contaminated),
        }


def _resolver_log(log: list[str]):
    def resolve(raw):
        log.append(raw["ref"])
        return ResolvedSource(
            Path(raw["root"]), raw["ref"], "d" * 40, ("true",),
            raw["environment_identity_sha256"], raw["native_artifact_sha256"],
        )
    return resolve


def test_registry_is_complete_but_future_owned_slots_fail_closed():
    registry = load_registry()
    assert set(registry["required_strata"]) == REQUIRED_STRATA
    assert len([item for item in registry["workloads"] if item["role"] == "holdout"]) == 1
    plan = next(item for item in registry["workloads"] if item["id"] == "runtime_plan_warm_construct")
    assert plan["implementation_state"] == "EXECUTABLE_CURRENT"
    assert plan["selector"] == "bianchi.runtime.RuntimePlan"
    with pytest.raises(RuntimeError, match="geometry_class_a_single"):
        select_workloads(registry)
    with pytest.raises(PermissionError, match="milestone_closeout"):
        select_workloads(registry, roles=("holdout",))
    assert registry["component_blockers"]["kato_collision"]["state"] == (
        "BLOCKED_BY_RF04_NO_PUBLIC_KATO_SELECTOR"
    )
    ray = next(item for item in registry["workloads"]
               if item["id"] == "rays_cmb_observable_batch")
    assert ray["components"] == ["ray_batch", "map_assembly", "observable_batch"]
    ensemble = next(item for item in registry["workloads"]
                    if item["id"] == "batch_q_fast_ensemble")
    assert ensemble["strata"] == ["batch and ensemble workloads"]
    assert [item["id"] for item in registry["workloads"]
            if item["implementation_state"] == "EXECUTABLE_CURRENT"] == [
        "startup_cold_backend_import",
        "startup_backend_initialization",
        "runtime_plan_warm_construct",
        "runtime_plan_memory_allocation_ffi_overhead",
    ]
    assert registry["component_blockers"]["serialization"]["state"] == (
        "BLOCKED_BY_RF06_NO_END_TO_END_SERIALIZATION_ADAPTER"
    )


def test_corpus_description_has_one_sealed_holdout_and_stable_digest():
    first = describe(CORPUS_PATH)
    second = describe(CORPUS_PATH)
    assert first == second
    assert first["holdout_id"] == "holdout_q_saha_internal_e2e"
    assert len(first["registry_sha256"]) == 64
    registry = load_registry()
    for workload in registry["workloads"]:
        if workload["output_contract"] is not None:
            assert len(workload["output_contract_sha256"]) == 64


def test_short_steady_state_work_is_batched_to_the_frozen_two_second_floor():
    assert _calibrated_repetitions(250_000_000, 2.0) == 8
    assert _calibrated_repetitions(2_500_000_000, 2.0) == 1
    assert _calibrated_repetitions(1, None) == 1


def test_environment_block_happens_before_any_source_resolution():
    resolutions: list[str] = []
    result = run_protocol(
        _config(), _host(ClaimLevel.EXPLORATORY_ONLY),
        live_host_probe=_host(ClaimLevel.EXPLORATORY_ONLY),
        resolver=_resolver_log(resolutions), collector=_Collector(),
    )
    assert result["status"] == "BLOCKED_ENVIRONMENT"
    assert result["candidate_resolved"] is False
    assert result["candidate_statistics_visible"] is False
    assert result["workload_executed"] is False
    assert resolutions == []


def test_dedicated_request_rejects_controlled_host_before_source_resolution():
    config = _config()
    config["requested_claim_level"] = "DEDICATED_BARE_METAL"
    resolutions: list[str] = []
    result = run_protocol(
        config, _host(ClaimLevel.CONTROLLED_SHARED_PAIRED),
        live_host_probe=_host(ClaimLevel.CONTROLLED_SHARED_PAIRED),
        resolver=_resolver_log(resolutions), collector=_Collector(),
    )
    assert result["status"] == "BLOCKED_ENVIRONMENT"
    assert result["candidate_resolved"] is False
    assert result["candidate_statistics_visible"] is False
    assert result["workload_executed"] is False
    assert "observed_claim_level_below_requested_claim_level" in result["blocking_reasons"]
    assert resolutions == []


def test_controlled_runner_closes_baseline_preflight_before_candidate_resolution():
    resolutions: list[str] = []
    collector = _Collector(candidate_failures=4)
    result = run_protocol(
        _config(), _host(ClaimLevel.CONTROLLED_SHARED_PAIRED),
        live_host_probe=_host(ClaimLevel.CONTROLLED_SHARED_PAIRED),
        resolver=_resolver_log(resolutions), collector=collector,
    )
    assert collector.preflight_calls == 1
    assert collector.warmup_calls == 1
    assert collector.contracts[0]["mode"] == "calibrate"
    assert collector.contracts[1]["mode"] == "warmup"
    assert all(item["repetitions"] == 1 for item in collector.contracts)
    assert resolutions == ["1" * 40, "2" * 40]
    assert result["status"] == "CONTROLLED_PAIRED_EVIDENCE"
    assert result["workload_executed"] is True
    assert result["accepted_by_order"] == {"AB": 15, "BA": 15}
    assert result["summary"]["candidate_statistics_visible"] is True
    assert len(result["rejected_pairs"]) == 4
    assert all(not pair["candidate_visible_to_statistics"] for pair in result["rejected_pairs"])
    assert all("wall_time_ns" not in repr(pair) for pair in result["rejected_pairs"])


def test_every_pair_is_bound_to_the_clean_baseline_preflight_output():
    result = run_protocol(
        _config(), _host(ClaimLevel.CONTROLLED_SHARED_PAIRED),
        live_host_probe=_host(ClaimLevel.CONTROLLED_SHARED_PAIRED),
        resolver=_resolver_log([]), collector=_Collector(preflight_digest="b" * 64),
    )
    assert result["status"] == "BLOCKED_CONTAMINATED"
    assert result["candidate_statistics_visible"] is False
    assert result["accepted_by_order"] == {"AB": 0, "BA": 0}
    assert len(result["rejected_pairs"]) == 90
    assert all("wall_time_ns" not in repr(pair) for pair in result["rejected_pairs"])


def test_holdout_is_refused_before_source_resolution_during_tuning():
    config = _config()
    config["workload_id"] = "holdout_q_saha_internal_e2e"
    resolutions: list[str] = []
    with pytest.raises(PermissionError, match="holdout"):
        run_protocol(
            config, _host(ClaimLevel.CONTROLLED_SHARED_PAIRED),
            live_host_probe=_host(ClaimLevel.CONTROLLED_SHARED_PAIRED),
            resolver=_resolver_log(resolutions), collector=_Collector(),
        )
    assert resolutions == []


def test_missing_live_probe_blocks_before_source_resolution():
    resolutions: list[str] = []
    result = run_protocol(
        _config(), _host(ClaimLevel.CONTROLLED_SHARED_PAIRED),
        resolver=_resolver_log(resolutions), collector=_Collector(),
    )
    assert result["status"] == "BLOCKED_ENVIRONMENT"
    assert result["candidate_resolved"] is False
    assert result["workload_executed"] is False
    assert result["blocking_reasons"] == [
        "live_host_probe_required_before_authority_run"
    ]
    assert resolutions == []


def test_live_probe_controls_authority_even_when_supplied_receipt_claims_controlled():
    resolutions: list[str] = []
    result = run_protocol(
        _config(), _host(ClaimLevel.CONTROLLED_SHARED_PAIRED),
        live_host_probe=_host(ClaimLevel.EXPLORATORY_ONLY),
        resolver=_resolver_log(resolutions), collector=_Collector(),
    )
    assert result["status"] == "BLOCKED_ENVIRONMENT"
    assert result["candidate_resolved"] is False
    assert result["workload_executed"] is False
    assert "observed_claim_level_below_requested_claim_level" in result["blocking_reasons"]
    assert resolutions == []
