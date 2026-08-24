#!/usr/bin/env python3
"""Deterministic, non-default benchmark harness for representative BASS flows.

The corpus is deliberately small.  ``--once`` times only the selected workload;
module import and CLI startup are outside the timed region.  ``--sample`` launches
one fresh child per observation, but every child performs its requested warmups
before its own timed call so lazy caches and thread pools are steady-state inputs.
This also keeps Linux ``ru_maxrss`` comparable across refs.
Python allocation tracing is intentionally a separate ``--once --memory`` pass:
its instrumentation overhead must never enter timing or paired acceptance samples.
All output digests use named, finite, little-endian binary64 arrays in a fixed
order; they are scientific-output identities, not timings.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import random
import resource
import statistics
import subprocess
import sys
import time
import tracemalloc
from typing import Any, Callable


SCHEMA_VERSION = "bass-runtime-benchmark-v2"
REPO_ROOT = Path(__file__).resolve().parents[1]
WEIGHTED_CASES = (
    "r5b_tilted",
    "q_mode_a",
    "ray_map_final",
    "optical_map_final",
)
CONTROL_CASE = "r5b_small_control"

# These are canonical JSON values as well as the executable input contract.  Do
# not derive benchmark inputs from mutable environment defaults.
CORPUS: dict[str, dict[str, Any]] = {
    "r5b_tilted": {
        "weight": 0.30,
        "flow": "bianchi.matter.tilted_integrate.integrate",
        "background": {
            "a0": [1.0, 0.9, 1.2],
            "H": 1.0,
            "sigma_diag": [0.06, -0.02, -0.04],
            "v0": [0.08, -0.05, 0.12],
            "dv": [0.0, 0.0, 0.0],
        },
        "parameters": {
            "mass": 1.0,
            "t_end": 0.2,
            "nsteps": 200,
            "l_max": 3,
            "i_max": 3,
            "mode": "ratio",
            "jdot_closure": True,
            "n_star": None,
            "backend": None,
        },
    },
    "q_mode_a": {
        "weight": 0.30,
        "flow": "bianchi.q.model.run",
        "model": {
            "type": "VIII",
            "sigma": [[0.2, 0.0, 0.0], [0.0, -0.1, 0.0], [0.0, 0.0, -0.1]],
            "n": [[-0.3, 0.0, 0.0], [0.0, 0.3, 0.0], [0.0, 0.0, 0.3]],
            "a": [0.0, 0.0, 0.0],
            "grid": {"n_theta": 24, "n_phi": 48, "n_p": 0,
                     "lnq_min": -6.0, "lnq_max": 4.0},
            "collision": {"kernel": "thomson", "nu": 1.0,
                          "history": None, "rate_mode": "model"},
            "tau_span": [0.0, -1.0],
            "nsteps": 500,
            "lnH": 0.0,
        },
        "parameters": {"events": [], "keep_every": 0, "fast": True},
    },
    "ray_map_final": {
        "weight": 0.20,
        "flow": "bianchi.backend.ray_final_z_batch",
        "model": {"H0": 1.0, "Sigma0": [0.06, -0.02, -0.04],
                  "Omega0": 0.3, "gamma": 1.3333333333333333},
        "directions": {
            "algorithm": "fibonacci_midpoint_v1",
            "count": 256,
            "ordered_float64_sha256":
                "767788aaffed46cd05347c21ed09e72988deb6f73f17472018b5e8531b12182a",
        },
        "parameters": {"t0": 0.0, "t_end": -0.3, "nsteps": 2000,
                       "force_python": False},
    },
    "optical_map_final": {
        "weight": 0.20,
        "flow": "bianchi.backend.optical_batch",
        "model": {"H0": 1.0, "Sigma0": [0.06, -0.02, -0.04],
                  "Omega0": 0.3, "gamma": 1.3333333333333333},
        "directions": {
            "algorithm": "fibonacci_midpoint_v1",
            "count": 64,
            "ordered_float64_sha256":
                "82e2c40ec08ed112a2fc4a4544cb51913eabdc8a602b38d7cded235407eae519",
        },
        "parameters": {"t0": 0.0, "t_end": -0.3, "nsteps": 1000,
                       "force_python": False},
    },
    "r5b_small_control": {
        "weight": None,
        "role": "unweighted_correctness_sensitive_control",
        "flow": "bianchi.matter.tilted_integrate.integrate",
        "background": {
            "a0": [1.0, 0.9, 1.2],
            "H": 1.0,
            "sigma_diag": [0.06, -0.02, -0.04],
            "v0": [0.08, -0.05, 0.12],
            "dv": [0.0, 0.0, 0.0],
        },
        "parameters": {
            "mass": 1.0,
            "t_end": 0.2,
            "nsteps": 10,
            "l_max": 2,
            "i_max": 1,
            "mode": "frozen",
            "jdot_closure": True,
            "n_star": None,
            "backend": None,
        },
    },
}


def _canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def _sha256_json(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value)).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _git(*args: str) -> str | None:
    proc = subprocess.run(["git", *args], cwd=REPO_ROOT, text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                          check=False)
    return proc.stdout.strip() if proc.returncode == 0 else None


def _source_identity() -> dict[str, Any]:
    dirty = _git("status", "--porcelain=v1", "--untracked-files=normal")
    return {
        "head": _git("rev-parse", "HEAD"),
        "tree": _git("rev-parse", "HEAD^{tree}"),
        "branch": _git("branch", "--show-current"),
        "working_tree_dirty": None if dirty is None else bool(dirty),
    }


def _thread_count() -> int | None:
    try:
        for line in Path("/proc/self/status").read_text().splitlines():
            if line.startswith("Threads:"):
                return int(line.split(":", 1)[1])
    except (OSError, ValueError):
        pass
    return None


def _environment_identity() -> dict[str, Any]:
    affinity = None
    if hasattr(os, "sched_getaffinity"):
        affinity = sorted(os.sched_getaffinity(0))
    thread_vars = ("RAYON_NUM_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS",
                   "MKL_NUM_THREADS", "BLIS_NUM_THREADS", "NUMEXPR_NUM_THREADS")
    return {
        "python_executable": os.path.abspath(sys.executable),
        "python_executable_resolved": str(Path(sys.executable).resolve()),
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "cpu_count": os.cpu_count(),
        "affinity": affinity,
        "thread_overrides": {key: os.environ.get(key) for key in thread_vars},
        "pythonhashseed": os.environ.get("PYTHONHASHSEED"),
    }


def _native_fact(symbol: str, selected: bool = True) -> dict[str, Any]:
    import bianchi_rustcore as rustcore

    package_path = Path(rustcore.__file__).resolve()
    extension = sys.modules.get("bianchi_rustcore.bianchi_rustcore")
    extension_path = Path(extension.__file__).resolve() if extension is not None else None
    return {
        "selected": bool(selected),
        "fallback_forced": False,
        "symbol": symbol,
        "symbol_available": hasattr(rustcore, symbol),
        "module_path": None if extension_path is None else str(extension_path),
        "module_file_sha256": (None if extension_path is None
                               else _sha256_file(extension_path)),
        "package_path": str(package_path),
        "package_file_sha256": _sha256_file(package_path),
        "module_version": getattr(rustcore, "__version__", None),
    }


def _float64_array(value: Any):
    import numpy as np

    array = np.asarray(value, dtype=np.dtype("<f8"), order="C")
    if not np.isfinite(array).all():
        raise RuntimeError("benchmark output contains a non-finite float64 value")
    return np.ascontiguousarray(array)


def _digest_arrays(parts: list[tuple[str, Any]]) -> tuple[str, int]:
    digest = hashlib.sha256(b"BASS_BENCHMARK_OUTPUT_V1\0")
    nbytes = 0
    for name, value in parts:
        array = _float64_array(value)
        header = _canonical_json({"name": name, "shape": list(array.shape),
                                  "dtype": "float64-le"})
        raw = array.tobytes(order="C")
        digest.update(len(header).to_bytes(8, "big"))
        digest.update(header)
        digest.update(len(raw).to_bytes(8, "big"))
        digest.update(raw)
        nbytes += len(raw)
    return digest.hexdigest(), nbytes


def _fibonacci_directions(count: int, expected_sha256: str):
    import numpy as np

    golden_angle = math.pi * (3.0 - math.sqrt(5.0))
    directions = np.empty((count, 3), dtype=np.dtype("<f8"))
    for index in range(count):
        z = 1.0 - 2.0 * (index + 0.5) / count
        radius = math.sqrt(max(0.0, 1.0 - z * z))
        phi = golden_angle * index
        directions[index] = (radius * math.cos(phi), radius * math.sin(phi), z)
    actual = hashlib.sha256(directions.tobytes(order="C")).hexdigest()
    if actual != expected_sha256:
        raise RuntimeError(f"frozen direction bytes drifted: {actual} != {expected_sha256}")
    return directions


def _prepare_r5b(case_name: str):
    from bianchi.matter import tilted_integrate as TI
    from bianchi.matter import tilted_rust as TR

    spec = CORPUS[case_name]
    params = dict(spec["parameters"])
    bg = TI.Background(**spec["background"])
    if not TR.USE_RUST or not TI.rust_available(
            params["mode"], params["jdot_closure"], params["n_star"]):
        raise RuntimeError("R5b benchmark requires the native th_integrate path")
    def execute():
        return TI.integrate(bg, **params)

    def finalize(history):
        parts: list[tuple[str, Any]] = [("time", history["t"])]
        expected_keys = None
        for checkpoint, state in enumerate(history["J"]):
            keys = tuple(sorted(state))
            if expected_keys is None:
                expected_keys = keys
            elif keys != expected_keys:
                raise RuntimeError(f"R5b state keys changed at checkpoint {checkpoint}")
            for level, radial_index in keys:
                parts.append((f"J/{checkpoint:04d}/{level}/{radial_index}",
                              state[(level, radial_index)]))
        digest, output_nbytes = _digest_arrays(parts)
        rho_final = float(_float64_array(history["J"][-1][(0, 0)]).reshape(-1)[0])
        if rho_final <= 0.0:
            raise RuntimeError("R5b final density is not positive")
        return {
            "output_digest": digest,
            "output_nbytes": output_nbytes,
            "output_summary": {"checkpoints": len(history["t"]),
                               "state_blocks": len(expected_keys or ()),
                               "rho_final": rho_final},
            "native_use": _native_fact("th_integrate"),
        }

    return execute, finalize


def _prepare_q_mode_a():
    import numpy as np
    from bianchi.q import model as QM

    spec = CORPUS["q_mode_a"]
    raw = spec["model"]
    grid = QM.Grid(**raw["grid"])
    collision = QM.Collision(**raw["collision"])
    model = QM.Model(type=raw["type"], sigma=np.asarray(raw["sigma"], float),
                     n=np.asarray(raw["n"], float), a=np.asarray(raw["a"], float),
                     grid=grid, collision=collision,
                     tau_span=tuple(raw["tau_span"]), nsteps=raw["nsteps"],
                     lnH=raw["lnH"])
    native_use = _native_fact("qe_evolve")
    if not native_use["symbol_available"]:
        raise RuntimeError("Q benchmark requires the native qe_evolve path")

    def execute():
        return QM.run(model, **spec["parameters"])

    def finalize(raw_result):
        state, trajectory, events = raw_result
        if events:
            raise RuntimeError("event-free Q benchmark unexpectedly returned events")
        digest, output_nbytes = _digest_arrays([
            ("final_state", state.pack()),
            ("trajectory", trajectory),
        ])
        return {
            "output_digest": digest,
            "output_nbytes": output_nbytes,
            "output_summary": {"state_width": int(np.asarray(state.pack()).size),
                               "trajectory_shape": list(np.asarray(trajectory).shape)},
            "native_use": native_use,
        }

    return execute, finalize


def _prepare_ray_map():
    import numpy as np
    from bianchi import backend

    spec = CORPUS["ray_map_final"]
    if not backend.available():
        raise RuntimeError("ray benchmark requires the native trace_rays_batch path")
    directions = _fibonacci_directions(
        spec["directions"]["count"], spec["directions"]["ordered_float64_sha256"])
    native_use = _native_fact("trace_rays_batch")

    def execute():
        return backend.ray_final_z_batch(
            spec["model"], directions, **spec["parameters"])

    def finalize(output):
        digest, output_nbytes = _digest_arrays([("final_z", output)])
        values = _float64_array(output)
        return {
            "output_digest": digest,
            "output_nbytes": output_nbytes,
            "output_summary": {"directions": int(values.size),
                               "z_min": float(np.min(values)),
                               "z_max": float(np.max(values))},
            "native_use": native_use,
        }

    return execute, finalize


def _prepare_optical_map():
    import numpy as np
    from bianchi import backend

    spec = CORPUS["optical_map_final"]
    if not backend.available():
        raise RuntimeError("optical benchmark requires the native trace_optical_batch path")
    directions = _fibonacci_directions(
        spec["directions"]["count"], spec["directions"]["ordered_float64_sha256"])
    native_use = _native_fact("trace_optical_batch")

    def execute():
        return backend.optical_batch(spec["model"], directions, **spec["parameters"])

    def finalize(raw_result):
        redshift, distance = raw_result
        digest, output_nbytes = _digest_arrays([
            ("final_z", redshift),
            ("final_dA", distance),
        ])
        z_values, d_values = _float64_array(redshift), _float64_array(distance)
        return {
            "output_digest": digest,
            "output_nbytes": output_nbytes,
            "output_summary": {"directions": int(z_values.size),
                               "z_min": float(np.min(z_values)),
                               "z_max": float(np.max(z_values)),
                               "dA_min": float(np.min(d_values)),
                               "dA_max": float(np.max(d_values))},
            "native_use": native_use,
        }

    return execute, finalize


PREPARERS: dict[str, Callable[[], tuple[Callable[[], Any], Callable[[Any], dict[str, Any]]]]] = {
    "r5b_tilted": lambda: _prepare_r5b("r5b_tilted"),
    "q_mode_a": _prepare_q_mode_a,
    "ray_map_final": _prepare_ray_map,
    "optical_map_final": _prepare_optical_map,
    "r5b_small_control": lambda: _prepare_r5b("r5b_small_control"),
}


def _describe() -> dict[str, Any]:
    weights = {name: CORPUS[name]["weight"] for name in WEIGHTED_CASES}
    if not math.isclose(sum(weights.values()), 1.0, rel_tol=0.0, abs_tol=0.0):
        raise RuntimeError("weighted corpus must sum exactly to one")
    return {
        "schema_version": SCHEMA_VERSION,
        "corpus_identity_sha256": _sha256_json(CORPUS),
        "weighted_cases": list(WEIGHTED_CASES),
        "unweighted_control": CONTROL_CASE,
        "weights": weights,
        "cases": CORPUS,
        "aggregate_definition":
            "speedup=1/sum(weight*median_candidate/median_baseline)",
    }


def _once(case_name: str, *, trace_memory: bool = False,
          warmups: int = 0) -> dict[str, Any]:
    if case_name not in PREPARERS:
        raise ValueError(f"unknown benchmark case: {case_name}")
    if warmups < 0:
        raise ValueError("warmups must be non-negative")
    # Scientific imports, native-module loading, and immutable input construction
    # are setup.  The measured interval is exactly one public workload call.
    execute, finalize = PREPARERS[case_name]()
    warmup_digests = []
    for _ in range(warmups):
        warmup_digests.append(finalize(execute())["output_digest"])
    before_threads = _thread_count()
    before_blocks = sys.getallocatedblocks() if hasattr(sys, "getallocatedblocks") else None
    if trace_memory:
        tracemalloc.start()
    started_wall = time.perf_counter_ns()
    started_cpu = time.process_time_ns()
    raw_result = execute()
    ended_cpu = time.process_time_ns()
    ended_wall = time.perf_counter_ns()
    after_blocks = sys.getallocatedblocks() if hasattr(sys, "getallocatedblocks") else None
    if trace_memory:
        _, peak_traced = tracemalloc.get_traced_memory()
        tracemalloc.stop()
    else:
        peak_traced = None
    result = finalize(raw_result)
    if any(digest != result["output_digest"] for digest in warmup_digests):
        raise RuntimeError(f"{case_name} output changed between warmup and measurement")
    usage = resource.getrusage(resource.RUSAGE_SELF)
    return {
        "schema_version": SCHEMA_VERSION,
        "mode": "once_memory" if trace_memory else "once",
        "case": case_name,
        "weight": CORPUS[case_name]["weight"],
        "warmup": {
            "calls_before_measurement": warmups,
            "output_digest": (result["output_digest"] if warmups else None),
            "output_digest_stable": True,
        },
        "input_identity_sha256": _sha256_json(CORPUS[case_name]),
        "source": _source_identity(),
        "environment": _environment_identity(),
        "measurement": {
            "instrumentation": "tracemalloc" if trace_memory else "timing_only",
            "wall_seconds": (ended_wall - started_wall) / 1e9,
            "process_cpu_seconds": (ended_cpu - started_cpu) / 1e9,
            "tracemalloc_peak_bytes": peak_traced,
            "ru_maxrss_kib": usage.ru_maxrss,
            "allocated_blocks_delta": (None if before_blocks is None or after_blocks is None
                                       else after_blocks - before_blocks),
            "threads_before": before_threads,
            "threads_after": _thread_count(),
        },
        **result,
    }


def _percentile(values: list[float], percentile: float) -> float:
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * percentile
    lower = int(math.floor(position))
    upper = int(math.ceil(position))
    fraction = position - lower
    return ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction


def _summary(observations: list[dict[str, Any]]) -> dict[str, Any]:
    wall = [item["measurement"]["wall_seconds"] for item in observations]
    cpu = [item["measurement"]["process_cpu_seconds"] for item in observations]
    rss = [item["measurement"]["ru_maxrss_kib"] for item in observations]
    wall_median = statistics.median(wall)
    digests = sorted({item["output_digest"] for item in observations})
    inputs = sorted({item["input_identity_sha256"] for item in observations})
    warmups = sorted({item["warmup"]["calls_before_measurement"]
                      for item in observations})
    if len(digests) != 1 or len(inputs) != 1 or len(warmups) != 1:
        raise RuntimeError(
            "sample observations changed output, input identity, or warmup contract")
    return {
        "samples": len(observations),
        "warmups_per_observation": warmups[0],
        "wall_median_seconds": wall_median,
        "wall_p95_seconds": _percentile(wall, 0.95),
        "wall_mad_seconds": statistics.median([abs(value - wall_median) for value in wall]),
        "process_cpu_median_seconds": statistics.median(cpu),
        "ru_maxrss_median_kib": statistics.median(rss),
        "ru_maxrss_p95_kib": _percentile(rss, 0.95),
        "output_digest": digests[0],
        "input_identity_sha256": inputs[0],
        "output_digest_stable": True,
    }


def _child_once_at(python: Path, harness: Path, case_name: str,
                   timeout_seconds: float, warmups: int) -> dict[str, Any]:
    python = python.absolute()
    harness = harness.absolute()
    if not python.is_file() or not os.access(python, os.X_OK):
        raise RuntimeError(f"benchmark Python is not executable: {python}")
    if not harness.is_file():
        raise RuntimeError(f"benchmark harness does not exist: {harness}")
    repo_root = harness.parents[1]
    env = os.environ.copy()
    previous_path = env.get("PYTHONPATH")
    env["PYTHONPATH"] = str(repo_root) + (os.pathsep + previous_path
                                           if previous_path else "")
    env.setdefault("PYTHONHASHSEED", "0")
    command = [str(python), str(harness), "--once", "--case", case_name,
               "--warmups", str(warmups)]
    proc = subprocess.run(command, cwd=repo_root, env=env, text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          timeout=timeout_seconds, check=False)
    if proc.returncode != 0:
        raise RuntimeError(
            f"child benchmark failed for {case_name} (exit {proc.returncode}):\n{proc.stderr}")
    lines = [line for line in proc.stdout.splitlines() if line.strip()]
    if not lines:
        raise RuntimeError(f"child benchmark for {case_name} produced no JSON")
    try:
        result = json.loads(lines[-1])
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"child benchmark emitted invalid JSON: {proc.stdout}") from exc
    result["child_stderr_sha256"] = hashlib.sha256(proc.stderr.encode()).hexdigest()
    return result


def _child_once(case_name: str, timeout_seconds: float,
                warmups: int) -> dict[str, Any]:
    return _child_once_at(Path(sys.executable), Path(__file__), case_name,
                          timeout_seconds, warmups)


def _sample(case_arg: str, samples: int, warmups: int,
            timeout_seconds: float) -> dict[str, Any]:
    case_names = list(WEIGHTED_CASES) if case_arg == "all" else [case_arg]
    all_observations: dict[str, list[dict[str, Any]]] = {}
    summaries: dict[str, dict[str, Any]] = {}
    for case_name in case_names:
        observations = [
            _child_once(case_name, timeout_seconds, warmups)
            for _ in range(samples)
        ]
        all_observations[case_name] = observations
        summaries[case_name] = _summary(observations)
    return {
        "schema_version": SCHEMA_VERSION,
        "mode": "sample",
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "corpus_identity_sha256": _sha256_json(CORPUS),
        "requested_case": case_arg,
        "warmups_per_observation": warmups,
        "samples_per_case": samples,
        "observations": all_observations,
        "summaries": summaries,
    }


def _bootstrap_median_ci(values: list[float], seed: int,
                         replicates: int = 10_000) -> list[float]:
    rng = random.Random(seed)
    count = len(values)
    medians = [statistics.median(values[rng.randrange(count)] for _ in range(count))
               for _ in range(replicates)]
    return [_percentile(medians, 0.025), _percentile(medians, 0.975)]


def _paired(case_arg: str, pairs: int, warmups: int, timeout_seconds: float,
            baseline_python: Path, baseline_harness: Path,
            candidate_python: Path, candidate_harness: Path,
            seed: int) -> dict[str, Any]:
    case_names = list(WEIGHTED_CASES) if case_arg == "all" else [case_arg]
    labels = {
        "baseline": (baseline_python, baseline_harness),
        "candidate": (candidate_python, candidate_harness),
    }
    case_results: dict[str, Any] = {}
    for case_index, case_name in enumerate(case_names):
        first = "baseline" if random.Random(seed + case_index).randrange(2) == 0 \
            else "candidate"
        second = "candidate" if first == "baseline" else "baseline"
        observations: dict[str, list[dict[str, Any]]] = {key: [] for key in labels}
        raw_pairs: list[dict[str, Any]] = []
        for pair_index in range(pairs):
            order = [first, second] if pair_index % 2 == 0 else [second, first]
            pair_observations: dict[str, dict[str, Any]] = {}
            for label in order:
                python, harness = labels[label]
                observation = _child_once_at(
                    python, harness, case_name, timeout_seconds, warmups)
                observations[label].append(observation)
                pair_observations[label] = observation
            baseline = pair_observations["baseline"]["measurement"]
            candidate = pair_observations["candidate"]["measurement"]
            raw_pairs.append({
                "pair_index": pair_index,
                "order": order,
                "baseline": pair_observations["baseline"],
                "candidate": pair_observations["candidate"],
                "wall_ratio_candidate_over_baseline":
                    candidate["wall_seconds"] / baseline["wall_seconds"],
                "cpu_ratio_candidate_over_baseline":
                    candidate["process_cpu_seconds"] / baseline["process_cpu_seconds"],
                "rss_ratio_candidate_over_baseline":
                    candidate["ru_maxrss_kib"] / baseline["ru_maxrss_kib"],
            })

        for label in labels:
            population_digests = {
                item["output_digest"] for item in observations[label]
            }
            if len(population_digests) != 1:
                raise RuntimeError(
                    f"{case_name} {label} output changed within the paired run")
        input_identities = {
            item["input_identity_sha256"]
            for population in observations.values() for item in population
        }
        if len(input_identities) != 1:
            raise RuntimeError(f"{case_name} baseline/candidate input identity differs")
        wall_ratios = [item["wall_ratio_candidate_over_baseline"]
                       for item in raw_pairs]
        ratio_median = statistics.median(wall_ratios)
        case_results[case_name] = {
            "order_seed": seed + case_index,
            "first_pair_order": [first, second],
            "pairs": raw_pairs,
            "population_summaries": {
                label: _summary(observations[label]) for label in labels
            },
            "paired_summary": {
                "pairs": pairs,
                "wall_ratio_candidate_over_baseline_median": ratio_median,
                "wall_ratio_candidate_over_baseline_p95":
                    _percentile(wall_ratios, 0.95),
                "wall_ratio_candidate_over_baseline_mad":
                    statistics.median(abs(value - ratio_median) for value in wall_ratios),
                "wall_ratio_median_bootstrap_95_ci":
                    _bootstrap_median_ci(wall_ratios, seed + 1000 + case_index),
                "bootstrap_replicates": 10_000,
                "cross_ref_output_digest_equal":
                    (observations["baseline"][0]["output_digest"]
                     == observations["candidate"][0]["output_digest"]),
                "input_identity_sha256": next(iter(input_identities)),
            },
        }
    return {
        "schema_version": SCHEMA_VERSION,
        "mode": "paired",
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "requested_case": case_arg,
        "warmups_per_observation_per_population": warmups,
        "pairs_per_case": pairs,
        "seed": seed,
        "baseline": {"python": str(baseline_python.absolute()),
                     "harness": str(baseline_harness.absolute())},
        "candidate": {"python": str(candidate_python.absolute()),
                      "harness": str(candidate_harness.absolute())},
        "cases": case_results,
    }


def _emit(payload: dict[str, Any], output: Path | None) -> None:
    encoded = json.dumps(payload, sort_keys=True, indent=2, allow_nan=False) + "\n"
    if output is None:
        # One physical line makes parent-process extraction insensitive to unrelated warnings.
        print(json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False))
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(output.name + f".tmp-{os.getpid()}")
    temporary.write_text(encoded, encoding="utf-8")
    os.replace(temporary, output)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--describe", action="store_true",
                      help="emit the frozen corpus and exact identity")
    mode.add_argument("--once", action="store_true",
                      help="run one internally timed observation")
    mode.add_argument("--sample", action="store_true",
                      help="collect fresh-child observations and summary statistics")
    mode.add_argument("--paired", action="store_true",
                      help="collect deterministic baseline/candidate observation pairs")
    parser.add_argument("--case", choices=[*CORPUS, "all"],
                        help="case name; --sample also accepts all weighted cases")
    parser.add_argument("--samples", type=int, default=15)
    parser.add_argument("--pairs", type=int, default=15)
    parser.add_argument("--warmups", type=int, default=3)
    parser.add_argument("--seed", type=int, default=20260824)
    parser.add_argument("--baseline-python", type=Path)
    parser.add_argument("--baseline-harness", type=Path)
    parser.add_argument("--candidate-python", type=Path)
    parser.add_argument("--candidate-harness", type=Path)
    parser.add_argument("--child-timeout", type=float, default=1800.0,
                        help="per-child timeout in seconds for --sample")
    parser.add_argument("--memory", action="store_true",
                        help="with --once only, collect a separate tracemalloc pass")
    parser.add_argument("--output", type=Path,
                        help="atomically write JSON here instead of stdout")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.describe:
        if args.case is not None or args.memory:
            raise SystemExit("--describe does not accept --case or --memory")
        payload = _describe()
    elif args.once:
        if args.case is None or args.case == "all":
            raise SystemExit("--once requires one concrete --case")
        if args.warmups < 0:
            raise SystemExit("--warmups >= 0 required")
        payload = _once(args.case, trace_memory=args.memory,
                        warmups=args.warmups)
    elif args.sample:
        if args.memory:
            raise SystemExit("--memory is a separate --once pass, not a timing sample")
        if args.case is None:
            raise SystemExit("--sample requires --case NAME or --case all")
        if args.samples < 1 or args.warmups < 0 or args.child_timeout <= 0.0:
            raise SystemExit("--samples >= 1, --warmups >= 0, and --child-timeout > 0 required")
        payload = _sample(args.case, args.samples, args.warmups, args.child_timeout)
    else:
        if args.memory:
            raise SystemExit("--memory is a separate --once pass, not a paired sample")
        if args.case is None:
            raise SystemExit("--paired requires --case NAME or --case all")
        paired_paths = (args.baseline_python, args.baseline_harness,
                        args.candidate_python, args.candidate_harness)
        if any(path is None for path in paired_paths):
            raise SystemExit("--paired requires baseline/candidate Python and harness paths")
        if args.pairs < 1 or args.warmups < 0 or args.child_timeout <= 0.0:
            raise SystemExit("--pairs >= 1, --warmups >= 0, and --child-timeout > 0 required")
        payload = _paired(args.case, args.pairs, args.warmups, args.child_timeout,
                          args.baseline_python, args.baseline_harness,
                          args.candidate_python, args.candidate_harness, args.seed)
    _emit(payload, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
