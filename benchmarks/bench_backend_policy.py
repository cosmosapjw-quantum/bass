#!/usr/bin/env python3
"""Non-default paired RF-00 startup and native-dispatch benchmark.

The driver compares two immutable source roots using this exact interpreter and
the same installed native module bytes.  Process startup is outside the child
timer.  Cold backend import and warmed ``chart_rhs`` dispatch are separate
populations.  Run explicitly with ``--run``; pytest never imports this file.

This legacy runner records affinity but does not prove exclusive CPU/cgroup
control.  Its output is therefore always ``EXPLORATORY_ONLY`` and carries no
performance or no-regression acceptance authority.  RF-BENCH-00 owns any later
controlled acceptance runner.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import random
import statistics
import subprocess
import sys
from typing import Any


RF00_R3_ARTIFACT_BRANCH = "artifact/native-repro-bundle-20260824-r3"
RF00_R3_WHEEL_SHA256 = (
    "e050974a78e5e02dc5ce8b77aa1dff5bf2bd62d2f52cb2cdcccf8b49d57f3917"
)
DEFAULT_SEED = 20260824
EXPLORATORY_ONLY_REASON = (
    "CPU affinity was recorded, but exclusive cpuset/cgroup control, effective "
    "CPU-set and SMT isolation, migrations, CPU pressure/steal, frequency and "
    "throttling, and perf running-ratio metadata were not verified"
)


_CHILD = r"""
import hashlib
from importlib import metadata
import json
import os
from pathlib import Path
import sys
import time

import numpy as np

cfg = json.loads(sys.argv[1])
root = Path(cfg["root"]).resolve()
sys.path.insert(0, str(root))

state = np.array([0.21, -0.13, 0.31, 0.19, 0.0], dtype=np.float64)
gamma = 4.0 / 3.0

if cfg["case"] == "cold_import":
    start = time.perf_counter_ns()
    from bianchi import backend
    duration_ns = time.perf_counter_ns() - start
elif cfg["case"] == "chart_rhs":
    from bianchi import backend
else:
    raise RuntimeError(f"unknown case: {cfg['case']}")

import bianchi_rustcore as native

native_extension = getattr(native, "bianchi_rustcore", native)
native_path = Path(native_extension.__file__).resolve()
native_sha256 = hashlib.sha256(native_path.read_bytes()).hexdigest()
direct = np.asarray(native.chart_rhs("class_a", state, gamma, 0.0), dtype=np.float64)

if cfg["case"] == "chart_rhs":
    for _ in range(cfg["inner_warmups"]):
        backend.chart_rhs("class_a", state, gamma)
    start = time.perf_counter_ns()
    for _ in range(cfg["iterations"]):
        observed = np.asarray(
            backend.chart_rhs("class_a", state, gamma), dtype=np.float64
        )
    duration_ns = time.perf_counter_ns() - start
else:
    observed = np.asarray(backend.chart_rhs("class_a", state, gamma), dtype=np.float64)

if not np.array_equal(observed, direct):
    raise RuntimeError("public chart_rhs output differs from direct native output")

digest = hashlib.sha256()
digest.update(observed.dtype.str.encode("ascii"))
digest.update(json.dumps(observed.shape, separators=(",", ":")).encode("ascii"))
digest.update(observed.tobytes(order="C"))

print(json.dumps({
    "case": cfg["case"],
    "duration_ns": duration_ns,
    "iterations": cfg["iterations"] if cfg["case"] == "chart_rhs" else 1,
    "per_call_ns": (
        duration_ns / cfg["iterations"]
        if cfg["case"] == "chart_rhs"
        else None
    ),
    "output_sha256": digest.hexdigest(),
    "native_module_path": str(native_path),
    "native_module_sha256": native_sha256,
    "native_distribution_version": metadata.version("bianchi-rustcore"),
    "python_executable": str(Path(sys.executable).resolve()),
    "python_version": sys.version,
    "cpu_affinity": sorted(os.sched_getaffinity(0)),
}, sort_keys=True, separators=(",", ":")))
"""


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _source_identity(root: Path, expected_ref: str) -> dict[str, Any]:
    head = _git(root, "rev-parse", "HEAD")
    if head != expected_ref:
        raise RuntimeError(f"{root}: expected HEAD {expected_ref}, observed {head}")
    dirty = _git(root, "status", "--porcelain=v1", "--untracked-files=all")
    if dirty:
        raise RuntimeError(f"{root}: benchmark source must be clean:\n{dirty}")
    return {
        "root": str(root),
        "head": head,
        "tree": _git(root, "rev-parse", "HEAD^{tree}"),
        "branch": _git(root, "rev-parse", "--abbrev-ref", "HEAD"),
        "dirty": False,
    }


def _child_environment(root: Path, rayon_threads: int) -> dict[str, str]:
    env = os.environ.copy()
    existing_pythonpath = env.get("PYTHONPATH")
    env.update(
        {
            "PYTHONHASHSEED": "0",
            "PYTHONNOUSERSITE": "1",
            "PYTHONPATH": (
                str(root)
                if not existing_pythonpath
                else os.pathsep.join((str(root), existing_pythonpath))
            ),
            "RAYON_NUM_THREADS": str(rayon_threads),
            "OMP_NUM_THREADS": "1",
            "OPENBLAS_NUM_THREADS": "1",
            "MKL_NUM_THREADS": "1",
            "NUMEXPR_NUM_THREADS": "1",
        }
    )
    return env


def _observe(
    root: Path,
    case: str,
    *,
    iterations: int,
    inner_warmups: int,
    rayon_threads: int,
    timeout: float,
) -> dict[str, Any]:
    cfg = {
        "root": str(root),
        "case": case,
        "iterations": iterations,
        "inner_warmups": inner_warmups,
    }
    completed = subprocess.run(
        [sys.executable, "-c", _CHILD, json.dumps(cfg, sort_keys=True)],
        cwd=root,
        env=_child_environment(root, rayon_threads),
        check=True,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    try:
        result = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"child did not emit one JSON observation: {completed.stdout!r}"
        ) from exc
    if not isinstance(result.get("duration_ns"), int) or result["duration_ns"] <= 0:
        raise RuntimeError(f"invalid child duration: {result!r}")
    return result


def _balanced_schedule(pairs: int, seed: int) -> list[str]:
    schedule = ["AB", "BA"] * (pairs // 2)
    if pairs % 2:
        schedule.append("AB" if seed % 2 == 0 else "BA")
    random.Random(seed).shuffle(schedule)
    return schedule


def _quantile(sorted_values: list[float], probability: float) -> float:
    position = (len(sorted_values) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return sorted_values[lower]
    weight = position - lower
    return sorted_values[lower] * (1.0 - weight) + sorted_values[upper] * weight


def _bootstrap_log_median_ci(
    log_ratios: list[float], seed: int, replicates: int
) -> tuple[float, float]:
    rng = random.Random(seed)
    count = len(log_ratios)
    samples = sorted(
        statistics.median(log_ratios[rng.randrange(count)] for _ in range(count))
        for _ in range(replicates)
    )
    return math.exp(_quantile(samples, 0.025)), math.exp(_quantile(samples, 0.975))


def _assert_common_identity(
    observations: list[dict[str, Any]], expected_native_sha256: str
) -> dict[str, Any]:
    python_paths = {item["python_executable"] for item in observations}
    native_paths = {item["native_module_path"] for item in observations}
    native_hashes = {item["native_module_sha256"] for item in observations}
    native_versions = {item["native_distribution_version"] for item in observations}
    output_hashes = {item["output_sha256"] for item in observations}
    affinities = {tuple(item["cpu_affinity"]) for item in observations}
    if python_paths != {str(Path(sys.executable).resolve())}:
        raise RuntimeError(f"arms used different Python interpreters: {python_paths}")
    if len(native_paths) != 1 or native_hashes != {expected_native_sha256}:
        raise RuntimeError(
            "arms did not use the predeclared identical native module bytes: "
            f"paths={native_paths}, hashes={native_hashes}"
        )
    if native_versions != {"0.1.0"}:
        raise RuntimeError(f"unexpected native distribution versions: {native_versions}")
    if len(output_hashes) != 1:
        raise RuntimeError(f"cross-ref scientific output changed: {output_hashes}")
    if len(affinities) != 1:
        raise RuntimeError(f"arms used different CPU affinities: {affinities}")
    return {
        "python_executable": next(iter(python_paths)),
        "native_module_path": next(iter(native_paths)),
        "native_module_sha256": next(iter(native_hashes)),
        "native_distribution_version": next(iter(native_versions)),
        "output_sha256": next(iter(output_hashes)),
        "cpu_affinity": list(next(iter(affinities))),
    }


def _measure_case(
    case: str,
    roots: dict[str, Path],
    *,
    pairs: int,
    warmups: int,
    seed: int,
    iterations: int,
    inner_warmups: int,
    rayon_threads: int,
    timeout: float,
    bootstrap_replicates: int,
    expected_native_sha256: str,
    minimum_chart_sample_seconds: float,
) -> dict[str, Any]:
    for warmup in range(warmups):
        order = ("baseline", "candidate") if warmup % 2 == 0 else ("candidate", "baseline")
        for arm in order:
            _observe(
                roots[arm],
                case,
                iterations=iterations,
                inner_warmups=inner_warmups,
                rayon_threads=rayon_threads,
                timeout=timeout,
            )

    schedule = _balanced_schedule(pairs, seed)
    raw_pairs = []
    observations = []
    for pair_index, order in enumerate(schedule):
        arms = ("baseline", "candidate") if order == "AB" else ("candidate", "baseline")
        measured = {}
        for arm in arms:
            measured[arm] = _observe(
                roots[arm],
                case,
                iterations=iterations,
                inner_warmups=inner_warmups,
                rayon_threads=rayon_threads,
                timeout=timeout,
            )
            observations.append(measured[arm])
        raw_pairs.append(
            {"pair_index": pair_index, "order": order, "observations": measured}
        )

    identity = _assert_common_identity(observations, expected_native_sha256)
    if case == "chart_rhs":
        too_short = [
            item["duration_ns"] / 1e9
            for item in observations
            if item["duration_ns"] / 1e9 < minimum_chart_sample_seconds
        ]
        if too_short:
            raise RuntimeError(
                "chart_rhs steady-state sample shorter than the predeclared minimum; "
                f"increase --chart-iterations (minimum observed {min(too_short):.6f}s)"
            )

    log_ratios = [
        math.log(
            pair["observations"]["candidate"]["duration_ns"]
            / pair["observations"]["baseline"]["duration_ns"]
        )
        for pair in raw_pairs
    ]
    median_ratio = math.exp(statistics.median(log_ratios))
    ci_low, ci_high = _bootstrap_log_median_ci(
        log_ratios, seed + 10_000, bootstrap_replicates
    )
    return {
        "case": case,
        "schedule": schedule,
        "raw_pairs": raw_pairs,
        "identity": identity,
        "paired_summary": {
            "pairs": pairs,
            "statistic": "exp(median(paired log(candidate_ns/baseline_ns)))",
            "candidate_over_baseline": median_ratio,
            "bootstrap_95_ci": [ci_low, ci_high],
            "bootstrap_replicates": bootstrap_replicates,
            "evidence_class": "EXPLORATORY_ONLY",
            "acceptance_claim": "NONE",
        },
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true", help="required explicit execution opt-in")
    parser.add_argument("--baseline-root", type=Path, required=True)
    parser.add_argument("--baseline-ref", required=True)
    parser.add_argument("--candidate-root", type=Path, required=True)
    parser.add_argument("--candidate-ref", required=True)
    parser.add_argument("--expected-native-module-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--pairs", type=int, default=30)
    parser.add_argument("--warmups", type=int, default=3)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--chart-iterations", type=int, default=500_000)
    parser.add_argument("--chart-inner-warmups", type=int, default=1_000)
    parser.add_argument("--minimum-chart-sample-seconds", type=float, default=2.0)
    parser.add_argument("--bootstrap-replicates", type=int, default=10_000)
    parser.add_argument("--rayon-threads", type=int, default=1)
    parser.add_argument("--child-timeout", type=float, default=120.0)
    return parser


def main() -> int:
    args = _parser().parse_args()
    if not args.run:
        raise SystemExit("refusing to time by default; pass --run explicitly")
    if args.pairs < 2 or args.warmups < 1 or args.bootstrap_replicates < 1:
        raise SystemExit("pairs >= 2, warmups >= 1, and bootstrap replicates >= 1 are required")
    if args.chart_iterations < 1 or args.chart_inner_warmups < 1:
        raise SystemExit("chart iteration and warmup counts must be positive")
    if args.rayon_threads < 1:
        raise SystemExit("--rayon-threads must be positive")
    if len(args.expected_native_module_sha256) != 64:
        raise SystemExit("--expected-native-module-sha256 must be 64 hexadecimal characters")
    try:
        int(args.expected_native_module_sha256, 16)
    except ValueError as exc:
        raise SystemExit("--expected-native-module-sha256 is not hexadecimal") from exc

    roots = {
        "baseline": args.baseline_root.resolve(),
        "candidate": args.candidate_root.resolve(),
    }
    if roots["baseline"] == roots["candidate"]:
        raise SystemExit("baseline and candidate roots must be distinct")
    source = {
        "baseline": _source_identity(roots["baseline"], args.baseline_ref),
        "candidate": _source_identity(roots["candidate"], args.candidate_ref),
    }

    cases = {}
    expected_native_sha256 = args.expected_native_module_sha256.lower()
    for case_index, case in enumerate(("cold_import", "chart_rhs")):
        cases[case] = _measure_case(
            case,
            roots,
            pairs=args.pairs,
            warmups=args.warmups,
            seed=args.seed + case_index,
            iterations=args.chart_iterations,
            inner_warmups=args.chart_inner_warmups,
            rayon_threads=args.rayon_threads,
            timeout=args.child_timeout,
            bootstrap_replicates=args.bootstrap_replicates,
            expected_native_sha256=expected_native_sha256,
            minimum_chart_sample_seconds=args.minimum_chart_sample_seconds,
        )

    payload = {
        "schema": "bass-rf00-backend-policy-paired-v1",
        "source": source,
        "native_receipt": {
            "artifact_branch": RF00_R3_ARTIFACT_BRANCH,
            "artifact_head_source": "external_remote_readback_after_artifact_push",
            "wheel_sha256": RF00_R3_WHEEL_SHA256,
            "installed_module_sha256": expected_native_sha256,
            "wheel_receipt_is_external_to_installed_module_hash": True,
        },
        "design": {
            "python_executable": str(Path(sys.executable).resolve()),
            "pairs_per_case": args.pairs,
            "warmups_per_arm": args.warmups,
            "schedule": "balanced shuffled AB/BA",
            "seed": args.seed,
            "chart_iterations": args.chart_iterations,
            "chart_inner_warmups": args.chart_inner_warmups,
            "minimum_chart_sample_seconds": args.minimum_chart_sample_seconds,
            "rayon_threads": args.rayon_threads,
            "blas_openmp_threads": 1,
            "process_startup_excluded": True,
            "cold_backend_import_timed_separately": True,
            "compile_or_build_time_included": False,
        },
        "cases": cases,
        "decision": {
            "evidence_class": "EXPLORATORY_ONLY",
            "acceptance_claim": "NONE",
            "reason": EXPLORATORY_ONLY_REASON,
        },
    }
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(f".{output.name}.tmp-{os.getpid()}")
    temporary.write_text(
        json.dumps(payload, sort_keys=True, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, output)
    print(
        json.dumps(
            {
                "output": str(output),
                "decision": payload["decision"],
                "summary": {
                    name: result["paired_summary"] for name, result in cases.items()
                },
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
