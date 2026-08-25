"""Non-timed installed-wheel proof for the two RF-01 corpus adapters."""

from __future__ import annotations

import hashlib
import json

import pytest

from benchmarks.rfbench import workload_child
from benchmarks.rfbench.corpus import load_registry
from bianchi.backend_policy import BackendPolicy, capability_report


rust = pytest.importorskip("bianchi_rustcore")

UNVERIFIED_DEVELOPMENT_WARM_DIGEST = (
    "7b718708513a04993aaeb61947e090587e327395404c4c0d744010440928b26f"
)


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
    observed_digest = _canonical_digest(first)

    if workload_id == "runtime_plan_warm_construct":
        report = capability_report(
            BackendPolicy.RUST_REQUIRED,
            probe_legacy_global_pool=False,
        )
        if report["installed_native_payload_fingerprint_verified"]:
            assert report["native_dispatch_provenance_state"] == (
                "verified_installed_payload"
            )
            assert observed_digest == workload["functional_output_sha256"]
        else:
            assert report["native_dispatch_provenance_state"] == (
                "unverified_development_payload"
            )
            assert report["development_override_active"] is True
            assert report["development_override_diagnostic"] == (
                "UNVERIFIED_DEVELOPMENT_NATIVE_PAYLOAD"
            )
            assert observed_digest == UNVERIFIED_DEVELOPMENT_WARM_DIGEST
    else:
        assert observed_digest == workload["functional_output_sha256"]

    if workload_id == "runtime_plan_memory_allocation_ffi_overhead":
        assert first["ffi_compute_entries"] == 1
        assert first["input_copies"] == 2
        assert first["output_copies"] == 1
        assert first["workspace_growth_events"] == 0
        assert first["designated_rust_allocations"] == 0
