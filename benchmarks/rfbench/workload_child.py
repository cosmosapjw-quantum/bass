"""Runner-owned RF-BENCH-00 workload adapter.

RF-BENCH-00 implements only the two RF-00 startup strata.  Every numerical
workload owned by RF-01 or later remains typed-blocked in the corpus until its
owner adds a frozen scientific comparator and an adapter here.
"""

from __future__ import annotations

import argparse
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


ADAPTERS: dict[str, Callable[[dict[str, Any]], object]] = {
    "startup_cold_backend_import": _cold_import,
    "startup_backend_initialization": _backend_initialization,
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
