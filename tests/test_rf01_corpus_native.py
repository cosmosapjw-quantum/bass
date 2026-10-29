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
    observed_digest = _canonical_digest(first)
    if workload_id == "runtime_plan_warm_construct":
        from bianchi.backend_policy import (
            BackendPolicy, REFERENCE_NATIVE_BUILD, capability_report,
        )

        provenance = capability_report(
            BackendPolicy.RUST_REQUIRED,
            probe_legacy_global_pool=False,
        )
        if provenance["installed_native_payload_fingerprint_verified"]:
            # Exact frozen output is admitted only for the verified installed wheel.
            assert observed_digest == workload["functional_output_sha256"]
        else:
            # This CI job intentionally builds an unverified development wheel.
            # Do NOT assign frozen release/feature provenance to that wheel or
            # report its actual payload as matching the reference artifact.
            assert provenance["native_dispatch_provenance_state"] == (
                "unverified_development_payload"
            )
            assert provenance["production_native_dispatch_permitted"] is False
            assert provenance["development_override_active"] is True
            assert first["build_profile"] is None
            assert first["optional_features"] == []
            assert observed_digest != workload["functional_output_sha256"]

            # Compare the invariant architecture fields against the immutable
            # reference output, with the *reference* provenance used solely
            # as a comparison fixture, not as the observed build identity.
            reference_projection = dict(first)
            reference_projection["build_profile"] = REFERENCE_NATIVE_BUILD[
                "build_profile"
            ]
            reference_projection["optional_features"] = list(
                REFERENCE_NATIVE_BUILD["optional_features"]
            )
            assert _canonical_digest(reference_projection) == (
                workload["functional_output_sha256"]
            )
            print("RF01_DEV_ARCH_EQUIVALENT_REFERENCE_NOT_VERIFIED")
    else:
        # The overhead fixture has no artifact-provenance-dependent fields.
        assert observed_digest == workload["functional_output_sha256"], (
            "RF01_FROZEN_OUTPUT_MISMATCH: "
            + json.dumps({
                "workload_id": workload_id,
                "expected_digest": workload["functional_output_sha256"],
                "observed_digest": observed_digest,
                "observed_output": first,
            }, sort_keys=True)
        )

    if workload_id == "runtime_plan_memory_allocation_ffi_overhead":
        assert first["ffi_compute_entries"] == 1
        assert first["input_copies"] == 2
        assert first["output_copies"] == 1
        assert first["workspace_growth_events"] == 0
        assert first["designated_rust_allocations"] == 0
