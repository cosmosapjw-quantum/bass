#!/usr/bin/env python3
"""Portable completed-case reuse and pending-only plans; never launches work."""
from __future__ import annotations

import argparse
import csv
from dataclasses import asdict
import hashlib
import importlib
import json
import math
from pathlib import Path
import platform
import sys
import time

BASELINE = Path(__file__).resolve().parents[1] / "rei_sigma_pi_pilot_20261021"
BASELINE_RELATIVE = "research/rei_sigma_pi_pilot_20261021"
COMMIT = "26f4a89a54462c4e7c5705f281f187f33f45166a"
SOURCE_SHA = "9a3a36bf03885245e6910f2d544d13634fb1b82dac45ddcb484efc7ecdb91334"
ARCHIVED_TOOLCHAIN = {"python": "3.12.14", "numpy": "2.3.5", "scipy": "1.17.0"}
CASES = "results/split729/aggregate/cases.csv"
SUMMARY = "results/split729/aggregate/summary.json"
REVIEW = "physics/SPLIT_RESULT_REVIEW.json"
# Extracted from source_intake/BASELINE_DOWNLOAD.json at COMMIT, never self-pinned.
PINS = {
    CASES: "c322453eed4c4c236ff19501ea6eca50353d6ebecc604a6cab9647b3a090255c",
    SUMMARY: "538987eb68054eb93f429c287c42f4262a7187489c5e6a45e4617790ea49e2cb",
    REVIEW: "891cda1aa6bd038558761fd34b111874daccadb2337dfb6da479b48183c1e414",
    "SPLIT_CONTRACT.json": "edd1a02c5e513e9f86d92b76b48059c347d445e74dc8e6b642ed4bd4d5b6cc80",
    "PILOT_CONTRACT.json": "d023c2251a640e1a152e5795282e5de0d337f42b8ab2baa188d2b3642a0cf807",
    "split_sweep.py": "e5cee6270c31e10b244daa8b978a43793d6f8ecc058de81bb45dadc50d8384d0",
    "sweep.py": "d1f7ae9a2fc5756c5a8873ba8b5c3659298d6209fcab27dc42360a5b87042d98",
    "sigma_pi_map.py": "4e7f806fa36a72ae97068281813a1253ccb48e08394a203f7efe3cfdde0e3eaf",
    "vendor/rei_c15/SOURCE_FETCH_MANIFEST.json": "4d8a95c79b8eb1eaf6d766089a5e7eefc2fa596575962a2126d040808f83eb26",
}
MAGNITUDES = ("Sigma_half_requested", "Pi_m_half_requested", "Pi_r_half_requested")
SIGNS = ("shear_sign_requested", "matter_stress_sign_requested", "radiation_stress_sign_requested")
SIGNED = ("signed_Sigma_requested", "signed_Pi_m_requested", "signed_Pi_r_requested")
FIELDS = {*MAGNITUDES, *SIGNS, *SIGNED, "signed_Pi_total_requested", "case_id", "nominal_cancellation"}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def identity(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def modules():
    if str(BASELINE) not in sys.path:
        sys.path.insert(0, str(BASELINE))
    loaded = [importlib.import_module(name) for name in ("split_sweep", "shared_executor")]
    for name in ("split_sweep", "sweep", "sigma_pi_map", "shared_executor"):
        if Path(sys.modules[name].__file__).resolve().parent != BASELINE:
            raise ValueError("BASELINE_MODULE_PATH_MISMATCH")
    return loaded


def normalize_case(row):
    if set(row) != FIELDS or not isinstance(row["case_id"], str) or not row["case_id"]:
        raise ValueError("EXACT_CASE_SCHEMA_REQUIRED")
    case = {"case_id": row["case_id"]}
    for key in (*MAGNITUDES, *SIGNS, *SIGNED, "signed_Pi_total_requested"):
        value = float(row[key])
        if not math.isfinite(value):
            raise ValueError("NONFINITE_CASE")
        case[key] = (0.0 if value == 0 else value)
    for mag, sign, signed in zip(MAGNITUDES, SIGNS, SIGNED):
        if case[mag] < 0 or case[sign] not in (-1, 0, 1) or (case[mag] == 0) != (case[sign] == 0):
            raise ValueError("CASE_MAGNITUDE_SIGN_DOMAIN")
        case[sign] = int(case[sign])
        if case[signed] != case[mag] * case[sign]:
            raise ValueError("MISMATCHING_SIGNED_COORDINATE")
    total = case[SIGNED[1]] + case[SIGNED[2]]
    flag = row["nominal_cancellation"]
    if type(flag) is not bool:
        if flag not in ("True", "False"):
            raise ValueError("BOOLEAN_CANCELLATION_REQUIRED")
        flag = flag == "True"
    if case[MAGNITUDES[0]] >= math.sqrt(3) or case["signed_Pi_total_requested"] != total or flag != (total == 0):
        raise ValueError("CASE_DERIVED_COORDINATE_MISMATCH")
    case["nominal_cancellation"] = flag
    return case


def coordinate_key(case):
    return tuple(case[key] for key in SIGNED)


def validate_cases(rows):
    cases = [normalize_case(row) for row in rows]
    if len({c["case_id"] for c in cases}) != len(cases) or len({coordinate_key(c) for c in cases}) != len(cases):
        raise ValueError("DUPLICATE_CASE_OR_COORDINATE")
    return cases


def science_payload(case, parameters, context_id, toolchain, nsteps=64):
    return {"schema": "rei.split.case_science.v1", "context_id": context_id,
            "case": {k: v for k, v in case.items() if k != "case_id"},
            "parameters": parameters, "nsteps": nsteps, "compress": True,
            "feedback": True, "toolchain": toolchain}


def load_completed_registry(baseline=BASELINE):
    baseline = Path(baseline).resolve()
    for relative, expected in PINS.items():
        if file_hash(baseline / relative) != expected:
            raise ValueError(f"PIN_MISMATCH: {relative}")
    files = {p for p in (baseline / "vendor/rei_c15").rglob("*") if p.is_file() and p.suffix in (".py", ".csv", ".json")}
    files.update(baseline / p for p in ("split_sweep.py", "SPLIT_CONTRACT.json", "sweep.py", "sigma_pi_map.py", "PILOT_CONTRACT.json"))
    source = [{"path": p.relative_to(baseline).as_posix(), "sha256": file_hash(p)} for p in sorted(files)]
    if identity(source) != SOURCE_SHA:
        raise ValueError("BASELINE_SOURCE_BINDING_MISMATCH")
    contract = json.loads((baseline / "SPLIT_CONTRACT.json").read_text())
    summary = json.loads((baseline / SUMMARY).read_text())
    review = json.loads((baseline / REVIEW).read_text())
    if (summary["status"] != "COMPLETE" or summary["case_count"] != 729 or summary["expected_case_count"] != 729
            or summary["missing_case_ids"] or summary["all_stored_gates_pass"] is not True or summary["nsteps"] != 64
            or review["status"] != "PASS_PRELIMINARY_CONDITIONAL_SPLIT_RESPONSE" or review["issues"]
            or any(review["counts"][k] != v for k, v in {"groups": 243, "cases": 729, "histories": 47385}.items())
            or summary["science_binding"] != review["science_binding"] or summary["science_binding"]["source"] != SOURCE_SHA
            or summary["science_binding"]["toolchain"] != identity(ARCHIVED_TOOLCHAIN)):
        raise ValueError("COMPLETION_CONTRACT_MISMATCH")
    split, _ = modules()
    expected = validate_cases(split.signed_grid(contract))
    with (baseline / CASES).open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    cases = validate_cases([{k: row[k] for k in FIELDS} for row in rows])
    if {c["case_id"]: c for c in cases} != {c["case_id"]: c for c in expected}:
        raise ValueError("MISSING_OR_MISMATCHING_BASELINE_COORDINATES")
    defaults = asdict(split.parameters())
    context = {"source_binding": {"sha256": SOURCE_SHA, "files": source}, "baseline_contract": contract,
               "parameter_defaults": defaults, "initialization": {"a0": .1999, "fast_massive": True, "source_grid": "8X8"}}
    context_id, records = identity(context), {}
    for case, row in zip(cases, rows):
        seed = {key: float(row[key]) for key in ("alpha_m", "alpha_r")}
        if not all(math.isfinite(v) and -1 <= v <= 2 for v in seed.values()):
            raise ValueError("ARCHIVED_SEED_DOMAIN")
        params = {**defaults, "Sigma_initial": case[MAGNITUDES[0]], "orientation": case[SIGNS[0]],
                  "massive_quadrupole": seed["alpha_m"], "gamma_quadrupole": seed["alpha_r"], "nu_quadrupole": seed["alpha_r"]}
        payload = science_payload(case, params, context_id, ARCHIVED_TOOLCHAIN)
        records[coordinate_key(case)] = {"case": case, "seed": seed, "science": payload, "science_id": identity(payload),
                                        "evidence": {"kind": "external_pinned_completion", "csv_case_id": case["case_id"]}}
    url = f"https://raw.githubusercontent.com/cosmosapjw-quantum/bass/{COMMIT}/{BASELINE_RELATIVE}/"
    evidence = {p: {"url": url + p, "sha256": PINS[p]} for p in (CASES, SUMMARY, REVIEW)}
    return {"context": context, "context_id": context_id, "records": records, "evidence_sources": evidence}


def read_cases(path):
    path = Path(path)
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream)) if path.suffix == ".csv" else json.load(stream)


def build_plan(*, baseline=BASELINE, cases=None, nsteps=64, group_size=3, profile="ncp", backend="exact-cache", snapshot=None):
    if type(nsteps) is not int or not 2 <= nsteps <= 1024 or type(group_size) is not int or group_size < 1:
        raise ValueError("STEP_OR_GROUP_DOMAIN")
    registry = load_completed_registry(baseline)
    split, executor = modules()
    if profile not in executor.PROFILES:
        raise ValueError("UNKNOWN_RESOURCE_PROFILE")
    if cases is None:
        cases = [record["case"] for record in registry["records"].values()]
    cases = validate_cases(read_cases(cases) if isinstance(cases, (str, Path)) else cases)
    completed, pending, context = [], [], None
    for case in cases:
        prior = registry["records"].get(coordinate_key(case))
        if prior is not None and nsteps == 64:
            completed.append({"case_id": case["case_id"], "science_id": prior["science_id"], "evidence": prior["evidence"]})
            continue
        if context is None:
            context = split.PreparedContext()
        seed = split.seed_for(case, context)
        params = asdict(split.parameters(case[MAGNITUDES[0]], case[SIGNS[0]], seed["alpha_m"], seed["alpha_r"]))
        import numpy, scipy
        toolchain = {"python": platform.python_version(), "numpy": numpy.__version__, "scipy": scipy.__version__}
        payload = science_payload(case, params, registry["context_id"], toolchain, nsteps)
        pending.append({"case": case, "seed": seed, "science": payload, "science_id": identity(payload)})
    caps = executor.PROFILES[profile]
    execution = {"backend": backend, "planner_sha256": file_hash(__file__), "executor_sha256": file_hash(BASELINE / "shared_executor.py"),
                 "profile": profile, "cpu_cap": caps[0], "memory_cap_bytes": caps[1], "group_size": group_size,
                 "numeric_threads": 1, "thread_env": dict(executor.THREAD_ENV), "memory_per_worker_bytes": 384 * executor.MIB}
    budget, batches = None, []
    if pending:
        if snapshot is None:
            observer = executor.ResourceObserver()
            observer.sample()
            time.sleep(.1)
            snapshot = observer.sample()
        cpu, memory = executor.admission_budget(snapshot, [], profile=profile, max_workers=caps[0], reserve_bytes=executor.GIB)
        jobs = [pending[i:i + group_size] for i in range(0, len(pending), group_size)]
        width = min(cpu, memory // execution["memory_per_worker_bytes"], len(jobs))
        budget = {"snapshot": snapshot, "cpu_room": cpu, "memory_room_bytes": memory, "width": width,
                  "advisory_only": True, "executor_must_resample_at_launch": True}
        if width:
            batches = [[{"case_ids": [c["case"]["case_id"] for c in job], "science_ids": [c["science_id"] for c in job]}
                        for job in jobs[i:i + width]] for i in range(0, len(jobs), width)]
    return {"schema": "rei.split.pending_work_plan.v1", "status": "REUSED_ALL" if not pending else "PENDING",
            "science_context": registry["context"], "science_context_id": registry["context_id"],
            "evidence_sources": registry["evidence_sources"], "candidate_count": len(cases), "completed_count": len(completed),
            "pending_count": len(pending), "completed": completed, "pending": pending,
            "execution": execution, "execution_id": identity(execution), "resource_budget": budget, "batches": batches,
            "job_count": sum(map(len, batches)), "launched_jobs": 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, help="JSON list or CSV with exactly the signed_grid case schema")
    parser.add_argument("--nsteps", type=int, default=64)
    parser.add_argument("--group-size", type=int, default=3)
    parser.add_argument("--profile", choices=("sandbox", "ncp"), default="ncp")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    plan = build_plan(cases=args.cases, nsteps=args.nsteps, group_size=args.group_size, profile=args.profile)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(plan, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(json.dumps({k: plan[k] for k in ("status", "candidate_count", "completed_count", "pending_count", "job_count", "launched_jobs")}))


if __name__ == "__main__":
    main()
