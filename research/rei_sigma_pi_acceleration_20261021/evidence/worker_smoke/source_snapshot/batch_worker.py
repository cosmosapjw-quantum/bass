#!/usr/bin/env python3
"""Prepare shared_executor jobs and reuse verified individual case checkpoints."""
from __future__ import annotations

import argparse
import copy
from dataclasses import asdict
import datetime as dt
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import sys
import tempfile
import traceback
import uuid

import work_plan as wp

LANE = Path(__file__).resolve().parent
PRODUCTION_FILES = ("work_plan.py", "cached_context.py", "batch_worker.py")
GATES = {"number_5e-12", "energy_5e-11", "gamma_monopole_3e-9", "nu_monopole_3e-9",
         "initial_mapping_3e-13", "positive_matter_P2", "positive_radiation_P2", "finite_success_json"}


def toolchain():
    import numpy, scipy
    return {"python": platform.python_version(), "numpy": numpy.__version__, "scipy": scipy.__version__}


def bytes_for(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()


def write_json(path, value, *, replace=False):
    """Atomic publication; immutable same-content input reuse is allowed."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = bytes_for(value)
    if not replace and path.exists():
        if path.is_symlink() or path.read_bytes() != raw:
            raise ValueError(f"IMMUTABLE_OUTPUT_DIFFERS: {path}")
        return
    temporary = path.with_name(path.name + ".tmp-" + uuid.uuid4().hex)
    with temporary.open("xb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    try:
        if replace:
            os.replace(temporary, path)
        else:
            os.link(temporary, path)  # create-only, including concurrent publishers
    finally:
        temporary.unlink(missing_ok=True)


def backend_binding(registry):
    """Relative identity is independent of host paths and resource/group choices."""
    files = [wp.BASELINE / item["path"] for item in registry["context"]["source_binding"]["files"]]
    files += [wp.BASELINE / "shared_executor.py", *(LANE / name for name in PRODUCTION_FILES)]
    bound = [{"path": str(path.resolve()), "sha256": wp.file_hash(path)} for path in sorted(set(files))]
    relative = [{"path": Path(item["path"]).relative_to(LANE.parents[1]).as_posix(), "sha256": item["sha256"]} for item in bound]
    return wp.identity({"backend": "exact-cache-v1", "files": relative}), bound


def validate_pending(records, registry, context_factory=None):
    split, _ = wp.modules()
    cases = wp.validate_cases([record["case"] for record in records])
    context = (context_factory or split.PreparedContext)() if records else None
    actual, steps = toolchain(), set()
    for record, case in zip(records, cases):
        if set(record) != {"case", "seed", "science", "science_id"} or record["case"] != case:
            raise ValueError("PENDING_RECORD_SCHEMA")
        nsteps = record["science"]["nsteps"]
        if type(nsteps) is not int or not 2 <= nsteps <= 1024:
            raise ValueError("PENDING_STEP_DOMAIN")
        if nsteps == 64 and wp.coordinate_key(case) in registry["records"]:
            raise ValueError("COMPLETED729_MUST_NOT_BE_PENDING")
        seed = split.seed_for(case, context)
        params = asdict(split.parameters(case[wp.MAGNITUDES[0]], case[wp.SIGNS[0]], seed["alpha_m"], seed["alpha_r"]))
        science = wp.science_payload(case, params, registry["context_id"], actual, nsteps)
        if (record["science"] != science or record["science_id"] != wp.identity(science)
                or wp.canonical(record["seed"]) != wp.canonical(seed)):
            raise ValueError("PENDING_SCIENCE_OR_TOOLCHAIN_MISMATCH")
        steps.add(nsteps)
    if len(steps) > 1:
        raise ValueError("ONE_NSTEPS_PER_PLAN_REQUIRED")
    return context


def validate_plan(plan, registry):
    if (plan.get("schema") != "rei.split.pending_work_plan.v1" or plan["science_context"] != registry["context"]
            or plan["science_context_id"] != registry["context_id"] or plan["evidence_sources"] != registry["evidence_sources"]
            or plan["pending_count"] != len(plan["pending"]) or plan["completed_count"] != len(plan["completed"])
            or plan["candidate_count"] != plan["pending_count"] + plan["completed_count"]):
        raise ValueError("PLAN_CONTEXT_OR_COUNTS_MISMATCH")
    known = {r["science_id"]: r for r in registry["records"].values()}
    labels, ids = [], []
    for item in plan["completed"]:
        record = known.get(item["science_id"])
        if record is None or item["evidence"] != record["evidence"]:
            raise ValueError("UNVERIFIED_COMPLETION")
        labels.append(item["case_id"])
        ids.append(item["science_id"])
    labels += [r["case"]["case_id"] for r in plan["pending"]]
    ids += [r["science_id"] for r in plan["pending"]]
    if len(set(labels)) != len(labels) or len(set(ids)) != len(ids):
        raise ValueError("DUPLICATE_PLAN_CASE")
    validate_pending(plan["pending"], registry)


def prepare(plan_path, out, case_store, group_size="auto"):
    plan_path, out, case_store = (Path(p).resolve() for p in (plan_path, out, case_store))
    plan = json.loads(plan_path.read_text())
    registry = wp.load_completed_registry()
    validate_plan(plan, registry)
    if not plan["pending"]:
        if (out / "manifest.json").exists():
            raise ValueError("NO_WORK_OUTPUT_HAS_OLD_MANIFEST")
        receipt = {"schema": "rei.split.no_work.v1", "status": "REUSED_ALL", "plan_sha256": wp.file_hash(plan_path),
                   "completed_count": plan["completed_count"], "pending_count": 0, "jobs": 0, "launched_jobs": 0,
                   "science_context_id": registry["context_id"], "evidence_sources": registry["evidence_sources"]}
        write_json(out / "no_work.json", receipt)
        return receipt
    pending = sorted(plan["pending"], key=lambda item: item["science_id"])
    if group_size == "auto":
        width = max(1, int((plan.get("resource_budget") or {}).get("width", 1)))
        size = min(16, max(1, math.ceil(len(pending) / width)))
    else:
        size = int(group_size)
        if not 1 <= size <= 16:
            raise ValueError("GROUP_SIZE_1_TO_16_REQUIRED")
    source_id, bound = backend_binding(registry)
    actual = toolchain()
    binding = {"source": source_id, "input": wp.identity({"context": registry["context_id"], "cases": sorted(p["science_id"] for p in pending)}),
               "toolchain": wp.identity(actual)}
    bound.append({"path": str(plan_path), "sha256": wp.file_hash(plan_path)})
    all_bound, jobs = list(bound), []
    nsteps = pending[0]["science"]["nsteps"]
    for start in range(0, len(pending), size):
        records = pending[start:start + size]
        name = f"split_cache_group_{start // size:04d}"
        path = out / "inputs" / f"{name}.json"
        data = {"schema": "rei.split.cache_group_input.v1", "science_binding": binding, "source_id": source_id,
                "science_context_id": registry["context_id"], "toolchain": actual, "nsteps": nsteps, "pending": records,
                "bound_files": bound, "case_store": str(case_store), "input_path": str(path), "plan_path": str(plan_path)}
        data["content_sha256"] = wp.identity(data)
        write_json(path, data)
        all_bound.append({"path": str(path), "sha256": wp.file_hash(path)})
        jobs.append({"id": name, "argv": [sys.executable, str(Path(__file__).resolve()), "run-group", "--input", str(path), "--output", "{attempt_dir}/result.json"],
                     "outputs": ["result.json"], "cwd": str(LANE), "memory_mb": 384, "timeout_s": 1800})
    manifest = {"schema": "rei.shared_case_science.v1", "science_binding": binding, "bound_files": all_bound,
                "jobs": jobs, "toolchain": actual, "split_pilot": {"case_count": len(pending), "group_size": size, "nsteps": nsteps},
                "completion_reuse": {"completed": plan["completed_count"], "pending": len(pending), "source_plan_sha256": wp.file_hash(plan_path)}}
    wp.modules()[1].validate_manifest(manifest)
    write_json(out / "manifest.json", manifest)
    return {"status": "PREPARED", "manifest": str(out / "manifest.json"), "jobs": len(jobs), "group_size": size, "pending": len(pending), "launched_jobs": 0}


def validate_result(result, record, context):
    split, _ = wp.modules()
    wp.canonical(result)  # all exported scalars must be finite JSON values
    owner = result["owner_result"]
    if (result["case"] != record["case"] or result["seed"] != record["seed"] or result["calibration"] != context.calibration
            or set(result["gates"]) != GATES or any(value is not True for value in result["gates"].values())
            or owner["nsteps"] != record["science"]["nsteps"] or len(owner["history"]) != owner["nsteps"]
            or result["initial"]["a"] != .1999 or owner["history"][-1]["a"] != .2 or owner["final"]["a"] != .2):
        raise ValueError("CASE_RESULT_CONTRACT")
    if result["numeric_checks"] != split.initial_checks(record["case"], result["initial"]):
        raise ValueError("CASE_INITIAL_CHECKS")
    for name, limit in {"photochemical_number_abs_max": 5e-12, "photochemical_energy_eV_H_abs_max": 5e-11,
                        "gamma_number_monopole_abs_max": 3e-9, "nu_number_monopole_abs_max": 3e-9}.items():
        if not 0 <= owner["errors"][name] <= limit:
            raise ValueError("CASE_ERROR_GATE")
    for row in [result["initial"], *owner["history"], owner["final"]]:
        if not (row["H"] > 0 and 10000 <= row["Tgas_K"] <= 24000 and 0 <= row["x_HII"] <= 1 and 0 <= row["x_HeII"] <= 1):
            raise ValueError("CASE_PHYSICAL_DOMAIN")


def case_from_store(data, record, context, runner):
    namespace = Path(data["case_store"]) / data["source_id"]
    sid = record["science_id"]
    entry = namespace / sid
    lock = namespace / "locks" / (sid + ".lock")
    lock.parent.mkdir(parents=True, exist_ok=True)
    with lock.open("a+") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        if entry.is_symlink():
            raise ValueError("CORRUPT_CASE_STORE_SYMLINK")
        reused = entry.exists()
        if reused:
            receipt = json.loads((entry / "receipt.json").read_text())
            raw = (entry / "case.json").read_bytes()
            if (receipt.get("status") != "PASS" or receipt.get("science_id") != sid or receipt.get("source_id") != data["source_id"]
                    or receipt.get("bytes") != len(raw) or receipt.get("sha256") != hashlib.sha256(raw).hexdigest()
                    or receipt.get("toolchain") != data["toolchain"]):
                raise ValueError("CORRUPT_CASE_STORE")
            result = json.loads(raw)
            if receipt["original_case_id"] != result["case"]["case_id"]:
                raise ValueError("CORRUPT_CASE_STORE_LABEL")
        else:
            try:
                split, _ = wp.modules()
                result = json.loads(split.canonical(runner(record["case"], context, record["science"]["nsteps"])))
                validate_result(result, record, context)
                model = getattr(context, "last_model", None)
                raw = bytes_for(result)
                receipt = {"schema": "rei.split.case_receipt.v1", "status": "PASS", "science_id": sid, "source_id": data["source_id"],
                           "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw), "original_case_id": record["case"]["case_id"],
                           "toolchain": data["toolchain"], "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
                           "origin_input_sha256": data["content_sha256"], "moment_cache": model.moment_cache_info() if model else None}
                stage = Path(tempfile.mkdtemp(prefix=".staging-", dir=namespace))
                write_json(stage / "case.json", result)
                write_json(stage / "receipt.json", receipt)
                os.rename(stage, entry)  # both files become visible together, under the per-case lock
            except Exception:
                write_json(namespace / "failures" / (sid + "-" + uuid.uuid4().hex + ".json"),
                           {"status": "FAILED", "science_id": sid, "case_id": record["case"]["case_id"], "traceback": traceback.format_exc()})
                raise
        result = copy.deepcopy(result)
        result["case"]["case_id"] = record["case"]["case_id"]
        validate_result(result, record, context)
        diagnostics = {"science_id": sid, "reused": reused, "original_case_id": receipt["original_case_id"],
                       "receipt_sha256": wp.file_hash(entry / "receipt.json"), "moment_cache": receipt["moment_cache"]}
        return result, diagnostics


def run_group(input_path, output_path, *, runner=None, context_factory=None):
    input_path, output = Path(input_path).resolve(), Path(output_path).resolve()
    if output.exists():
        raise ValueError("GROUP_RESULT_ALREADY_EXISTS")
    result, active = None, None
    try:
        data = json.loads(input_path.read_text())
        if (data.get("schema") != "rei.split.cache_group_input.v1" or data["input_path"] != str(input_path)
                or data["content_sha256"] != wp.identity({k: v for k, v in data.items() if k != "content_sha256"})):
            raise ValueError("GROUP_INPUT_IDENTITY_MISMATCH")
        for item in data["bound_files"]:
            if wp.file_hash(item["path"]) != item["sha256"]:
                raise ValueError("BOUND_SOURCE_OR_PLAN_CHANGED")
        registry = wp.load_completed_registry()
        source_plan = json.loads(Path(data["plan_path"]).read_text())
        plan_bound = {item["path"]: item["sha256"] for item in data["bound_files"]}
        plan_records = {item["science_id"]: item for item in source_plan["pending"]}
        input_binding = wp.identity({"context": registry["context_id"], "cases": sorted(plan_records)})
        if (data["source_id"] != backend_binding(registry)[0] or data["science_context_id"] != registry["context_id"]
                or data["toolchain"] != toolchain() or data["science_binding"]["source"] != data["source_id"]
                or data["science_binding"]["toolchain"] != wp.identity(toolchain())
                or plan_bound.get(data["plan_path"]) != wp.file_hash(data["plan_path"])
                or data["science_binding"]["input"] != input_binding
                or any(plan_records.get(item["science_id"]) != item for item in data["pending"])):
            raise ValueError("BACKEND_CONTEXT_OR_TOOLCHAIN_CHANGED")
        from cached_context import PreparedContext
        context = validate_pending(data["pending"], registry, context_factory or PreparedContext)
        if not data["pending"] or any(r["science"]["nsteps"] != data["nsteps"] for r in data["pending"]):
            raise ValueError("GROUP_PENDING_OR_STEPS")
        split, _ = wp.modules()
        result = {"schema": "rei.sigma_pi_split.group_result.v1", "science_binding": data["science_binding"],
                  "owner_ref": split.OWNER_REF, "nsteps": data["nsteps"], "cases": [], "case_cache": []}
        for active in data["pending"]:
            scientific, diagnostics = case_from_store(data, active, context, runner or split.run_case)
            result["cases"].append(scientific)
            result["case_cache"].append(diagnostics)
            write_json(output.with_name(output.stem + ".checkpoint.json"), result, replace=True)
        result["status"] = "SUCCEEDED"
        write_json(output, result)
        return result
    except Exception:
        write_json(output.with_name(output.stem + ".failure-" + uuid.uuid4().hex + ".json"),
                   {"status": "FAILED", "case": active, "traceback": traceback.format_exc(),
                    "completed_cases": [r["case"]["case_id"] for r in result["cases"]] if result else []})
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    prepare_parser = sub.add_parser("prepare")
    for key in ("plan", "out", "case-store"):
        prepare_parser.add_argument("--" + key, required=True, type=Path)
    prepare_parser.add_argument("--group-size", default="auto")
    run_parser = sub.add_parser("run-group")
    run_parser.add_argument("--input", required=True, type=Path)
    run_parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.command == "prepare":
        result = prepare(args.plan, args.out, args.case_store, args.group_size)
    else:
        data = run_group(args.input, args.output)
        result = {"status": data["status"], "cases": len(data["cases"]), "reused": sum(r["reused"] for r in data["case_cache"])}
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
