"""Static and functional RF-01 corpus-cell contracts; no timing is executed."""

from __future__ import annotations

import hashlib

import numpy as np
import pytest

from benchmarks.rfbench import workload_child
from benchmarks.rfbench.corpus import (
    ADAPTER_PATH,
    load_registry,
    sha256_file,
    sha256_json,
)


RF01_EXECUTABLE_IDS = {
    "runtime_plan_warm_construct",
    "runtime_plan_memory_allocation_ffi_overhead",
}


class _FakeWorkspace:
    def __init__(self, size: int):
        self.size = size
        self.reset_calls = 0

    def snapshot(self) -> dict[str, object]:
        return {
            "size": self.size,
            "capacities": [self.size, self.size, 4 * self.size, self.size, self.size],
            "all_zero": False,
            "busy": False,
            "poisoned": False,
        }

    def reset(self) -> None:
        self.reset_calls += 1


class _FakePlan:
    instances: list["_FakePlan"] = []

    def __init__(
        self,
        thread_count: int,
        *,
        fixture_size: int,
        require_finite: bool,
        cpu_variant: str,
    ):
        self.thread_count = thread_count
        self.private_pool_size = thread_count
        self.fixture_size = fixture_size
        self.require_finite = require_finite
        self.cpu_variant = cpu_variant
        self.fingerprint = f"fake-plan:{thread_count}:{fixture_size}:{cpu_variant}"
        self._workspace = _FakeWorkspace(fixture_size)
        self._counters = self._zero_counters()
        self.run_steps: list[int] = []
        type(self).instances.append(self)

    @staticmethod
    def _zero_counters() -> dict[str, int]:
        return {
            "ffi_compute_entries": 0,
            "input_copies": 0,
            "output_copies": 0,
            "workspace_growth_events": 0,
            "designated_rust_allocations": 0,
        }

    def capability_receipt(self) -> dict[str, object]:
        return {
            "schema": "bass-runtime-plan-capability-v1",
            "fingerprint": self.fingerprint,
            "thread_count": self.thread_count,
            "private_pool_size": self.private_pool_size,
            "cpu_variant": self.cpu_variant,
            "build_profile": "release",
        }

    def workspace(self) -> _FakeWorkspace:
        return self._workspace

    def reset_counters(self) -> None:
        self._counters = self._zero_counters()

    def counters(self) -> dict[str, int]:
        return dict(self._counters)

    def run_fixture(
        self,
        values: np.ndarray,
        workspace: _FakeWorkspace,
        *,
        steps: int,
    ) -> np.ndarray:
        assert workspace is self._workspace
        self.run_steps.append(steps)
        self._counters.update(
            ffi_compute_entries=1,
            input_copies=2,
            output_copies=1,
        )
        return np.asarray(values, dtype=np.float64) + float(steps)


@pytest.fixture(autouse=True)
def _isolated_runtime_adapter(monkeypatch):
    _FakePlan.instances.clear()
    workload_child._runtime_overhead_context.cache_clear()
    monkeypatch.setattr(workload_child, "_runtime_plan_type", lambda: _FakePlan)
    monkeypatch.setattr(
        workload_child,
        "_runtime_build_fields",
        lambda: {
            "extension_version": "0.1.0",
            "optional_features": ["cpu", "pyo3/extension-module"],
        },
    )
    monkeypatch.setenv("RAYON_NUM_THREADS", "2")
    yield
    workload_child._runtime_overhead_context.cache_clear()


def _workload(registry: dict, workload_id: str) -> dict:
    return next(item for item in registry["workloads"] if item["id"] == workload_id)


def test_rf01_cells_are_the_only_new_executable_entries_and_hashes_are_bound():
    registry = load_registry()
    executable = {
        item["id"]
        for item in registry["workloads"]
        if item["implementation_state"] == "EXECUTABLE_CURRENT"
    }
    assert executable == {
        "startup_cold_backend_import",
        "startup_backend_initialization",
        *RF01_EXECUTABLE_IDS,
    }
    assert set(workload_child.ADAPTERS) == executable
    assert registry["source_adapter_sha256"] == sha256_file(ADAPTER_PATH)

    for workload_id in RF01_EXECUTABLE_IDS:
        item = _workload(registry, workload_id)
        assert item["owner_node"] == "RF-01"
        assert item["selector"] is not None
        assert item["correctness_comparator"] == {"kind": "EXACT_OUTPUT_DIGEST"}
        assert item["input_identity_sha256"] == sha256_json(item["inputs"])
        assert item["output_contract_sha256"] == sha256_json(item["output_contract"])
        assert len(item["functional_output_sha256"]) == 64


def test_later_owner_blockers_and_sealed_holdout_are_unchanged():
    registry = load_registry()
    serialization = registry["component_blockers"]["serialization"]
    assert serialization["state"] == (
        "BLOCKED_BY_RF06_NO_END_TO_END_SERIALIZATION_ADAPTER"
    )
    assert serialization["owner_node"] == "RF-06"

    for owner in ("RF-02", "RF-03", "RF-04", "RF-05"):
        owned = [item for item in registry["workloads"] if item["owner_node"] == owner]
        assert owned
        assert all(item["implementation_state"].startswith("BLOCKED_") for item in owned)
        assert all(item["selector"] is None for item in owned)

    holdout = _workload(registry, "holdout_q_saha_internal_e2e")
    assert holdout["implementation_state"].startswith("BLOCKED_")
    assert holdout["selector"] is None
    assert holdout["default_selected"] is False
    assert holdout["tuning_access"] == "FORBIDDEN"


def test_runtime_plan_adapter_returns_only_the_frozen_architecture_receipt():
    inputs = _workload(load_registry(), "runtime_plan_warm_construct")["inputs"]
    first = workload_child._runtime_plan_warm_construct(inputs)
    second = workload_child._runtime_plan_warm_construct(inputs)

    assert first == second == {
        "runtime_schema": "bass-runtime-plan-capability-v1",
        "plan_fingerprint": "fake-plan:2:64:scalar",
        "thread_count": 2,
        "private_pool_size": 2,
        "cpu_variant": "scalar",
        "workspace_capacities": [64, 64, 256, 64, 64],
        "build_profile": "release",
        "extension_version": "0.1.0",
        "optional_features": ["cpu", "pyo3/extension-module"],
    }
    assert len(_FakePlan.instances) == 2


def test_runtime_overhead_adapter_reuses_context_and_reports_exact_counters():
    inputs = _workload(
        load_registry(), "runtime_plan_memory_allocation_ffi_overhead"
    )["inputs"]
    first = workload_child._runtime_plan_memory_allocation_ffi_overhead(inputs)
    second = workload_child._runtime_plan_memory_allocation_ffi_overhead(inputs)

    assert first == second
    assert set(first) == {
        "plan_fingerprint",
        "workspace_capacity_elements",
        "workspace_capacity_bytes",
        "input_bytes",
        "output_bytes",
        "ffi_compute_entries",
        "input_copies",
        "output_copies",
        "workspace_growth_events",
        "designated_rust_allocations",
        "result_digest",
    }
    assert first["plan_fingerprint"] == "fake-plan:2:64:scalar"
    assert first["workspace_capacity_elements"] == 512
    assert first["workspace_capacity_bytes"] == 4096
    assert first["input_bytes"] == 512
    assert first["output_bytes"] == 512
    assert first["ffi_compute_entries"] == 1
    assert first["input_copies"] == 2
    assert first["output_copies"] == 1
    assert first["workspace_growth_events"] == 0
    assert first["designated_rust_allocations"] == 0
    assert len(first["result_digest"]) == 64
    assert len(_FakePlan.instances) == 1
    assert _FakePlan.instances[0].run_steps == [1, 100, 100]


@pytest.mark.parametrize("value", [None, "", "0", "-1", "one", " 2"])
def test_runtime_adapters_fail_closed_without_one_canonical_thread_count(
    monkeypatch, value
):
    if value is None:
        monkeypatch.delenv("RAYON_NUM_THREADS", raising=False)
    else:
        monkeypatch.setenv("RAYON_NUM_THREADS", value)
    with pytest.raises(RuntimeError, match="RAYON_NUM_THREADS"):
        workload_child._runtime_thread_count()


def test_runtime_result_digest_binds_dtype_shape_and_bytes():
    values = np.arange(4, dtype=np.float64)
    same_bytes_other_shape = values.reshape(2, 2)
    expected = workload_child._runtime_result_digest(values)
    assert expected == workload_child._runtime_result_digest(values.copy())
    assert expected != workload_child._runtime_result_digest(same_bytes_other_shape)
    assert expected != hashlib.sha256(values.tobytes()).hexdigest()
