"""Non-timed installed-wheel proof for the two RF-01 corpus adapters."""

from __future__ import annotations

import hashlib
import json

import pytest

from benchmarks.rfbench import workload_child
from benchmarks.rfbench.corpus import load_registry


rust = pytest.importorskip("bianchi_rustcore")


def _canonical_digest(value: object) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


@pytest.mark.parametrize(
    ("workload_id", "adapter_name"),
    (
        ("runtime_plan_warm_construct", "_runtime_plan_warm_construct"),
        (
            "runtime_plan_memory_allocation_ffi_overhead",
            "_runtime_plan_memory_allocation_ffi_overhead",
        ),
    ),
)
def test_real_rf01_adapter_is_repeatable_and_bound_without_timing(
    monkeypatch, workload_id, adapter_name
):
    monkeypatch.setenv("RAYON_NUM_THREADS", "1")
    workload_child._runtime_build_fields.cache_clear()
    workload_child._runtime_overhead_context.cache_clear()

    def forbidden_global_probe():
        raise AssertionError("RF-01 corpus adapter probed the global Rayon pool")

    monkeypatch.setattr(rust, "rayon_thread_pool_size", forbidden_global_probe)
    registry = load_registry()
    workload = next(item for item in registry["workloads"] if item["id"] == workload_id)
    adapter = getattr(workload_child, adapter_name)

    first = adapter(workload["inputs"])
    second = adapter(workload["inputs"])
    assert first == second
    assert _canonical_digest(first) == workload["functional_output_sha256"]

    if workload_id == "runtime_plan_memory_allocation_ffi_overhead":
        assert first["ffi_compute_entries"] == 1
        assert first["input_copies"] == 2
        assert first["output_copies"] == 1
        assert first["workspace_growth_events"] == 0
        assert first["designated_rust_allocations"] == 0
