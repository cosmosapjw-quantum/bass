"""Runner-owned RF-BENCH workload adapters.

RF-00 owns the two startup strata.  RF-01 adds only architecture-level
RuntimePlan construction and synthetic memory/allocation/FFI accounting.  All
RF-02+ numerical workloads remain typed-blocked until their owner supplies a
frozen scientific comparator and an adapter here.
"""

from __future__ import annotations

import argparse
from functools import lru_cache
import hashlib
import json
import os
from pathlib import Path
import resource
import sys
import time
from typing import Any, Callable

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from benchmarks.rfbench.corpus import load_registry
else:
    from .corpus import load_registry


def _canonical_json(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def _capability_fields(info: dict[str, Any], requested: list[str]) -> dict[str, Any]:
    return {name: info.get(name) for name in requested}


def _cold_import(inputs: dict[str, Any]) -> object:
    from bianchi import backend

    state = inputs["state"]
    rhs = backend.chart_rhs(
        "class_a", state, inputs["gamma"], policy="rust_required"
    )
    report = backend.info()
    return {
        "chart_rhs": [float(value) for value in rhs],
        "native_module_sha256": report.get("wheel_sha256"),
    }


def _backend_initialization(inputs: dict[str, Any]) -> object:
    from bianchi import backend

    return _capability_fields(backend.info(), inputs["capability_fields"])


def _runtime_thread_count() -> int:
    raw = os.environ.get("RAYON_NUM_THREADS")
    if raw is None or not raw.isascii() or not raw.isdecimal():
        raise RuntimeError(
            "RAYON_NUM_THREADS must be one canonical positive decimal integer"
        )
    value = int(raw)
    if value < 1:
        raise RuntimeError("RAYON_NUM_THREADS must be positive")
    return value


def _runtime_plan_type():
    from bianchi.runtime import RuntimePlan

    return RuntimePlan


@lru_cache(maxsize=1)
def _runtime_build_fields() -> dict[str, Any]:
    from bianchi.backend_policy import BackendPolicy, capability_report

    report = capability_report(
        BackendPolicy.RUST_REQUIRED,
        probe_legacy_global_pool=False,
    )
    extension_version = report.get("extension_version")
    optional_features = report.get("optional_features")
    if not isinstance(extension_version, str) or not extension_version:
        raise RuntimeError("RuntimePlan extension version is not available")
    if not isinstance(optional_features, list) or not all(
        isinstance(feature, str) and feature for feature in optional_features
    ):
        raise RuntimeError("RuntimePlan optional-feature receipt is not available")
    return {
        "extension_version": extension_version,
        "optional_features": sorted(optional_features),
    }


def _require_runtime_inputs(
    inputs: dict[str, Any], *, schema: str, expected_keys: set[str]
) -> None:
    if set(inputs) != expected_keys:
        raise ValueError(f"{schema} inputs do not match the frozen key set")
    if inputs.get("fixture_schema") != schema:
        observed = inputs.get("fixture_schema")
        raise ValueError(f"unexpected RuntimePlan fixture schema: {observed!r}")
    fixture_size = inputs.get("fixture_size")
    if isinstance(fixture_size, bool) or not isinstance(fixture_size, int) or fixture_size < 1:
        raise ValueError("fixture_size must be a positive integer")
    if not isinstance(inputs.get("require_finite"), bool):
        raise ValueError("require_finite must be boolean")
    if inputs.get("cpu_variant") != "scalar":
        raise ValueError("RF-01 corpus permits only the scalar CPU variant")


def _runtime_plan_warm_construct(inputs: dict[str, Any]) -> object:
    _require_runtime_inputs(
        inputs,
        schema="bass-rf01-runtime-plan-v1",
        expected_keys={
            "cpu_variant", "fixture_schema", "fixture_size", "require_finite"
        },
    )
    thread_count = _runtime_thread_count()
    runtime_plan = _runtime_plan_type()
    plan = runtime_plan(
        thread_count,
        fixture_size=inputs["fixture_size"],
        require_finite=inputs["require_finite"],
        cpu_variant=inputs["cpu_variant"],
    )
    workspace = plan.workspace()
    receipt = dict(plan.capability_receipt())
    snapshot = dict(workspace.snapshot())
    build = _runtime_build_fields()
    required_receipt = {
        "schema", "fingerprint", "thread_count", "private_pool_size",
        "cpu_variant", "build_profile",
    }
    if not required_receipt <= set(receipt):
        missing = sorted(required_receipt - set(receipt))
        raise RuntimeError(f"RuntimePlan capability receipt is incomplete: {missing}")
    capacities = snapshot.get("capacities")
    if not isinstance(capacities, list) or not capacities or not all(
        isinstance(value, int) and not isinstance(value, bool) and value >= 0
        for value in capacities
    ):
        raise RuntimeError("RuntimePlan workspace capacities are not canonical")
    result = {
        "runtime_schema": receipt["schema"],
        "plan_fingerprint": receipt["fingerprint"],
        "thread_count": receipt["thread_count"],
        "private_pool_size": receipt["private_pool_size"],
        "cpu_variant": receipt["cpu_variant"],
        "workspace_capacities": capacities,
        "build_profile": receipt["build_profile"],
        "extension_version": build["extension_version"],
        "optional_features": build["optional_features"],
    }
    if result["thread_count"] != thread_count:
        raise RuntimeError("RuntimePlan thread count differs from the runner stratum")
    if result["private_pool_size"] != result["thread_count"]:
        raise RuntimeError("RuntimePlan private pool size differs from its thread contract")
    return result


def _runtime_result_digest(values: object) -> str:
    import numpy as np

    array = np.asarray(values)
    if array.dtype != np.dtype(np.float64) or not array.flags.c_contiguous:
        raise RuntimeError("RuntimePlan result must be contiguous float64")
    header = _canonical_json({"dtype": array.dtype.str, "shape": list(array.shape)})
    digest = hashlib.sha256()
    digest.update(header)
    digest.update(b"\0")
    digest.update(array.tobytes(order="C"))
    return digest.hexdigest()


@lru_cache(maxsize=None)
def _runtime_overhead_context(
    thread_count: int,
    fixture_size: int,
    require_finite: bool,
    cpu_variant: str,
    input_algorithm: str,
):
    import numpy as np

    if input_algorithm != "linspace_-0.25_0.75_f64_v1":
        raise ValueError("unsupported RF-01 synthetic input algorithm")
    runtime_plan = _runtime_plan_type()
    plan = runtime_plan(
        thread_count,
        fixture_size=fixture_size,
        require_finite=require_finite,
        cpu_variant=cpu_variant,
    )
    workspace = plan.workspace()
    values = np.linspace(-0.25, 0.75, fixture_size, dtype=np.float64)
    values.setflags(write=False)
    plan.run_fixture(values, workspace, steps=1)
    workspace.reset()
    plan.reset_counters()
    return plan, workspace, values


def _runtime_plan_memory_allocation_ffi_overhead(inputs: dict[str, Any]) -> object:
    _require_runtime_inputs(
        inputs,
        schema="bass-rf01-runtime-overhead-v1",
        expected_keys={
            "cpu_variant", "fixture_schema", "fixture_size", "input_algorithm",
            "require_finite", "steps",
        },
    )
    steps = inputs["steps"]
    if isinstance(steps, bool) or not isinstance(steps, int) or steps < 1:
        raise ValueError("steps must be a positive integer")
    plan, workspace, values = _runtime_overhead_context(
        _runtime_thread_count(),
        inputs["fixture_size"],
        inputs["require_finite"],
        inputs["cpu_variant"],
        inputs["input_algorithm"],
    )
    workspace.reset()
    plan.reset_counters()
    output = plan.run_fixture(values, workspace, steps=steps)
    counters = dict(plan.counters())
    counter_names = {
        "ffi_compute_entries", "input_copies", "output_copies",
        "workspace_growth_events", "designated_rust_allocations",
    }
    if set(counters) != counter_names or not all(
        isinstance(value, int) and not isinstance(value, bool) and value >= 0
        for value in counters.values()
    ):
        raise RuntimeError("RuntimePlan counter receipt is incomplete or invalid")
    capacities = workspace.snapshot().get("capacities")
    if not isinstance(capacities, list) or not capacities or not all(
        isinstance(value, int) and not isinstance(value, bool) and value >= 0
        for value in capacities
    ):
        raise RuntimeError("RuntimePlan workspace capacities are not canonical")
    import numpy as np

    output_array = np.asarray(output)
    return {
        "plan_fingerprint": plan.fingerprint,
        "workspace_capacity_elements": sum(capacities),
        "workspace_capacity_bytes": sum(capacities) * 8,
        "input_bytes": int(values.nbytes),
        "output_bytes": int(output_array.nbytes),
        **{name: counters[name] for name in sorted(counter_names)},
        "result_digest": _runtime_result_digest(output_array),
    }


ADAPTERS: dict[str, Callable[[dict[str, Any]], object]] = {
    "startup_cold_backend_import": _cold_import,
    "startup_backend_initialization": _backend_initialization,
    "runtime_plan_warm_construct": _runtime_plan_warm_construct,
    "runtime_plan_memory_allocation_ffi_overhead": (
        _runtime_plan_memory_allocation_ffi_overhead
    ),
}


def _thread_contract() -> tuple[list[list[int]], list[int], bool]:
    affinity = sorted(os.sched_getaffinity(0))
    owners = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
              "BLIS_NUM_THREADS", "NUMEXPR_NUM_THREADS")
    ownership = all(os.environ.get(name) == "1" for name in owners)
    return [affinity], [time.process_time_ns()], ownership


def execute(workload_id: str) -> dict[str, Any]:
    registry = load_registry()
    matches = [item for item in registry["workloads"] if item["id"] == workload_id]
    if len(matches) != 1:
        raise ValueError("workload_id does not identify one corpus entry")
    workload = matches[0]
    if workload["implementation_state"] != "EXECUTABLE_CURRENT":
        raise RuntimeError(
            f"workload adapter is not executable: {workload_id} "
            f"({workload['implementation_state']})"
        )
    try:
        adapter = ADAPTERS[workload_id]
    except KeyError as exc:
        raise RuntimeError(f"runner-owned adapter is absent: {workload_id}") from exc

    source_root = os.environ.get("BASS_RFBENCH_SOURCE_ROOT")
    if not source_root or not Path(source_root).is_dir():
        raise RuntimeError("BASS_RFBENCH_SOURCE_ROOT must identify the source checkout")
    sys.path.insert(0, str(Path(source_root).resolve()))

    mode = os.environ.get("BASS_RFBENCH_MODE", "sample")
    if mode not in {"calibrate", "warmup", "sample"}:
        raise ValueError(f"invalid BASS_RFBENCH_MODE: {mode!r}")
    repetitions = int(os.environ.get("BASS_RFBENCH_REPETITIONS", "1"))
    warmups = int(os.environ.get("BASS_RFBENCH_WARMUPS", "0"))
    if repetitions < 1 or warmups < 0:
        raise ValueError("repetitions must be positive and warmups non-negative")

    inputs = workload["inputs"]
    for _ in range(warmups):
        adapter(inputs)
    usage_before = resource.getrusage(resource.RUSAGE_SELF)
    cpu_before = time.process_time_ns()
    started = time.perf_counter_ns()
    result = None
    for _ in range(repetitions):
        result = adapter(inputs)
    total_wall_ns = time.perf_counter_ns() - started
    cpu_delta_ns = time.process_time_ns() - cpu_before
    usage_after = resource.getrusage(resource.RUSAGE_SELF)
    worker_affinities, _, ownership = _thread_contract()
    output_digest = hashlib.sha256(_canonical_json(result)).hexdigest()
    return {
        "schema": "bass-rfbench-child-observation-v1",
        "workload_id": workload_id,
        "mode": mode,
        "input_identity_sha256": workload["input_identity_sha256"],
        "output_digest": output_digest,
        "wall_time_ns": max(1, round(total_wall_ns / repetitions)),
        "timed_total_wall_time_ns": total_wall_ns,
        "repetitions": repetitions,
        "warmup_iterations": warmups,
        "worker_affinities": worker_affinities,
        "per_worker_task_clock_ns": [cpu_delta_ns],
        "first_touch": {
            "status": "VERIFIED_NOT_APPLICABLE_STARTUP_WORKLOAD",
            "verified": True,
        },
        "thread_ownership": {
            "non_owner_libraries_forced_to_one": ownership,
            "verified": ownership,
        },
        "major_faults_after_warmup": usage_after.ru_majflt - usage_before.ru_majflt,
        "involuntary_context_switches": usage_after.ru_nivcsw - usage_before.ru_nivcsw,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workload-id", required=True)
    args = parser.parse_args(argv)
    print(json.dumps(execute(args.workload_id), sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
