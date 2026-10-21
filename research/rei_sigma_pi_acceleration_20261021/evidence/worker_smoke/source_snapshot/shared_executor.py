#!/usr/bin/env python3
"""Run independent, source-bound science cases in the host's available capacity.

The immutable science identity excludes worker count and resource estimates.
Successful declared outputs are checked before reuse. This module verifies
execution and file integrity; the case program owns scientific acceptance.
The scope disk cap controls new admission, not active output or a kernel quota.
"""
from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import time
import uuid


SCHEMA = "rei.shared_case_science.v1"
GIB = 1024 ** 3
MIB = 1024 ** 2
FILESYSTEM_FREE_RESERVE = 256 * MIB
PROFILES = {"sandbox": (8, 8 * GIB), "ncp": (64, 128 * GIB)}
THREAD_ENV = {key: "1" for key in (
    "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS",
    "RAYON_NUM_THREADS", "REI_TRANSPORT_THREADS",
)}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def file_sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def utc_now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def write_json_new(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(json.dumps(value, indent=2, sort_keys=True,
                                allow_nan=False).encode("utf-8") + b"\n")


def validate_manifest(manifest):
    if manifest.get("schema") != SCHEMA:
        raise ValueError("UNSUPPORTED_MANIFEST_SCHEMA")
    binding = manifest.get("science_binding", {})
    if not isinstance(binding, dict) or any(not binding.get(key) for key in
                                           ("source", "input", "toolchain")):
        raise ValueError("SOURCE_INPUT_TOOLCHAIN_BINDING_REQUIRED")
    files = manifest.get("bound_files", [])
    if not isinstance(files, list) or not files:
        raise ValueError("BOUND_SOURCE_INPUT_FILES_REQUIRED")
    for item in files:
        if (not isinstance(item, dict) or not isinstance(item.get("path"), str)
                or not re.fullmatch(r"[0-9a-f]{64}", item.get("sha256", ""))):
            raise ValueError("INVALID_BOUND_FILE")
    jobs = manifest.get("jobs")
    if not isinstance(jobs, list) or not jobs:
        raise ValueError("NONEMPTY_JOB_LIST_REQUIRED")
    seen = set()
    for job in jobs:
        name = job.get("id", "")
        if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", name):
            raise ValueError("INVALID_JOB_ID")
        if name in seen:
            raise ValueError("DUPLICATE_JOB_ID: " + name)
        seen.add(name)
        argv = job.get("argv")
        if not isinstance(argv, list) or not argv or any(not isinstance(x, str) or "\0" in x for x in argv):
            raise ValueError("ARGV_LIST_REQUIRED")
        outputs = job.get("outputs")
        if not isinstance(outputs, list) or not outputs or len(set(outputs)) != len(outputs):
            raise ValueError("DECLARED_OUTPUT_FILES_REQUIRED")
        for output in outputs:
            if not isinstance(output, str) or not output or Path(output).is_absolute() or ".." in Path(output).parts:
                raise ValueError("OUTPUT_MUST_BE_ATTEMPT_RELATIVE")
        memory = job.get("memory_mb", 256)
        timeout = job.get("timeout_s", 1800)
        if not isinstance(memory, (int, float)) or not math.isfinite(memory) or memory <= 0:
            raise ValueError("POSITIVE_JOB_MEMORY_REQUIRED")
        if not isinstance(timeout, (int, float)) or not math.isfinite(timeout) or not 0 < timeout <= 1800:
            raise ValueError("JOB_TIMEOUT_MUST_BE_IN_0_1800_SECONDS")
        if "cwd" in job and not isinstance(job["cwd"], str):
            raise ValueError("CWD_MUST_BE_STRING")
    canonical(manifest)
    return manifest


def job_identity(manifest, job):
    # Admission and timeout policy are execution metadata, not new science.
    payload = {key: value for key, value in job.items()
               if key not in ("memory_mb", "timeout_s")}
    return digest({"schema": SCHEMA, "science_binding": manifest["science_binding"],
                   "bound_files": manifest["bound_files"], "job": payload})


def verify_bound_files(manifest, manifest_directory):
    for item in manifest["bound_files"]:
        path = Path(item["path"])
        if not path.is_absolute():
            path = Path(manifest_directory) / path
        if not path.is_file() or file_sha256(path) != item["sha256"]:
            raise ValueError("SOURCE_INPUT_BINDING_MISMATCH: " + str(path))


@contextlib.contextmanager
def execution_lock(scope):
    scope = Path(scope)
    scope.mkdir(parents=True, exist_ok=True)
    with (scope / ".executor.lock").open("a+") as handle:
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError("ACTIVE_RUN_LOCK: " + str(scope)) from exc
        handle.seek(0)
        handle.truncate()
        handle.write(json.dumps({"pid": os.getpid(), "started": utc_now()}))
        handle.flush()
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def verify_completed(attempt, identity, outputs):
    """Return (reusable, reason, receipt); never modify historical evidence."""
    attempt = Path(attempt)
    try:
        receipt = json.loads((attempt / "receipt.json").read_text())
    except (OSError, ValueError):
        return False, "INCOMPLETE_PREVIOUS_ATTEMPT", None
    if receipt.get("job_identity") != identity:
        return False, "IDENTITY_MISMATCH", receipt
    if receipt.get("status") != "PASS":
        return False, "FAILED_PREVIOUS_ATTEMPT", receipt
    records = receipt.get("outputs", {})
    if set(records) != set(outputs):
        return False, "STALE_OUTPUT", receipt
    for name in outputs:
        path = attempt / name
        record = records[name]
        try:
            valid = (path.is_file() and path.stat().st_size == record["bytes"]
                     and file_sha256(path) == record["sha256"])
        except (OSError, KeyError, TypeError):
            valid = False
        if not valid:
            return False, "STALE_OUTPUT", receipt
    return True, "SKIPPED_PASS", receipt


def _read_text(path):
    try:
        return Path(path).read_text()
    except OSError:
        return ""


def _cgroup_directories():
    root = Path("/sys/fs/cgroup")
    relative = ""
    for line in _read_text("/proc/self/cgroup").splitlines():
        if line.startswith("0::"):
            relative = line[3:].lstrip("/")
            break
    current = root / relative
    if not current.is_dir() or root not in (current, *current.parents):
        current = root
    result = []
    while current == root or root in current.parents:
        result.append(current)
        if current == root:
            break
        current = current.parent
    return result


def _cpu_ticks():
    result = {}
    for line in _read_text("/proc/stat").splitlines():
        parts = line.split()
        if not parts or not re.fullmatch(r"cpu\d+", parts[0]):
            continue
        values = [int(x) for x in parts[1:]]
        # Guest time is already included in user/nice time.
        total = sum(values[:8])
        idle = values[3] + (values[4] if len(values) > 4 else 0)
        result[int(parts[0][3:])] = (total, idle)
    return result


def _cgroup_observation():
    quotas, memory_remaining, usages = [], [], {}
    for directory in _cgroup_directories():
        maximum = _read_text(directory / "cpu.max").split()
        if len(maximum) == 2 and maximum[0] != "max":
            quotas.append(int(maximum[0]) / int(maximum[1]))
        memory_max = _read_text(directory / "memory.max").strip()
        memory_current = _read_text(directory / "memory.current").strip()
        if memory_max and memory_max != "max" and memory_current:
            memory_remaining.append(max(0, int(memory_max) - int(memory_current)))
        usage = dict(line.split() for line in _read_text(directory / "cpu.stat").splitlines() if len(line.split()) == 2)
        if "usage_usec" in usage:
            usages[str(directory)] = {"usage_usec": int(usage["usage_usec"]),
                                      "quota": (int(maximum[0]) / int(maximum[1])
                                                if len(maximum) == 2 and maximum[0] != "max" else None)}
    return {"quota": min(quotas) if quotas else None,
            "memory_remaining": min(memory_remaining) if memory_remaining else None,
            "usages": usages}


def process_tree_rss(pid):
    """Observe only this executor's child and descendants, in bytes."""
    seen, pending, total = set(), [pid], 0
    while pending:
        current = pending.pop()
        if current in seen:
            continue
        seen.add(current)
        for line in _read_text(f"/proc/{current}/status").splitlines():
            if line.startswith("VmRSS:"):
                total += int(line.split()[1]) * 1024
        children = _read_text(f"/proc/{current}/task/{current}/children")
        pending.extend(int(child) for child in children.split())
    return total


class ResourceObserver:
    def __init__(self):
        self.previous = None

    def sample(self):
        now = time.monotonic()
        ticks = _cpu_ticks()
        cgroup = _cgroup_observation()
        try:
            affinity = sorted(os.sched_getaffinity(0))
        except AttributeError:
            affinity = list(range(os.cpu_count() or 1))
        memory = {}
        for line in _read_text("/proc/meminfo").splitlines():
            pieces = line.split()
            if len(pieces) >= 2:
                memory[pieces[0].rstrip(":")] = int(pieces[1]) * 1024
        idle, quota_remaining, sampled_s = 0.0, cgroup["quota"], 0.0
        if self.previous is not None:
            prior_time, prior_ticks, prior_cgroup = self.previous
            sampled_s = now - prior_time
            for cpu in affinity:
                if cpu in ticks and cpu in prior_ticks:
                    total = ticks[cpu][0] - prior_ticks[cpu][0]
                    idle_ticks = ticks[cpu][1] - prior_ticks[cpu][1]
                    if total > 0:
                        idle += max(0., min(1., idle_ticks / total))
            remaining = []
            for directory, current in cgroup["usages"].items():
                prior = prior_cgroup["usages"].get(directory)
                if current["quota"] is not None and prior and sampled_s > 0:
                    used = max(0., (current["usage_usec"] - prior["usage_usec"]) / 1e6 / sampled_s)
                    remaining.append(max(0., current["quota"] - used))
            if remaining:
                quota_remaining = min(remaining)
        self.previous = (now, ticks, cgroup)
        return {"affinity_cpus": affinity, "cpu_quota_cores": cgroup["quota"],
                "sampled_idle_cores": idle, "quota_remaining_cores": quota_remaining,
                "sampled_seconds": sampled_s,
                "mem_available_bytes": memory.get("MemAvailable", 0),
                "cgroup_remaining_bytes": cgroup["memory_remaining"]}


def admission_budget(snapshot, running, *, profile, max_workers, reserve_bytes):
    """Pure calculation for synthetic control tests and actual admission.

    Host/cgroup free memory already excludes resident own jobs. Reserve their
    not-yet-resident declared estimates once, then honor the profile RSS cap.
    """
    cpu_cap, memory_cap = PROFILES[profile]
    cpu_capacity = min(cpu_cap, max_workers, len(snapshot["affinity_cpus"]))
    if snapshot["cpu_quota_cores"] is not None:
        cpu_capacity = min(cpu_capacity, snapshot["cpu_quota_cores"])
    cpu_room = min(max(0., cpu_capacity - len(running)), snapshot["sampled_idle_cores"])
    if snapshot["quota_remaining_cores"] is not None:
        cpu_room = min(cpu_room, snapshot["quota_remaining_cores"])
    own_rss = sum(item.get("rss_bytes", 0) for item in running)
    unrealized = sum(max(0, item["memory_bytes"] - item.get("rss_bytes", 0)) for item in running)
    memory_room = min(snapshot["mem_available_bytes"], max(0, memory_cap - own_rss))
    if snapshot["cgroup_remaining_bytes"] is not None:
        memory_room = min(memory_room, snapshot["cgroup_remaining_bytes"])
    memory_room = max(0, memory_room - reserve_bytes - unrealized)
    return max(0, math.floor(cpu_room)), int(memory_room)


def scope_disk_observation(scope):
    """Count scope file bytes without following links outside the scope."""
    total = 0
    for directory, _, filenames in os.walk(scope, followlinks=False):
        for name in filenames:
            try:
                total += (Path(directory) / name).lstat().st_size
            except FileNotFoundError:
                pass  # A child may atomically replace a file while sampled.
    return {"scope_bytes": total,
            "filesystem_free_bytes": shutil.disk_usage(scope).free}


def disk_admission_reason(observation, max_scope_bytes):
    """Return a gate reason; active jobs may finish across either threshold."""
    if observation["scope_bytes"] >= max_scope_bytes:
        return "SCOPE_DISK_ADMISSION_CAP"
    if observation["filesystem_free_bytes"] <= FILESYSTEM_FREE_RESERVE:
        return "FILESYSTEM_FREE_SPACE_RESERVE"
    return None


def _finish(active, *, stop_reason=None):
    process = active["process"]
    if stop_reason is not None and process.poll() is None:
        # Every process has its own session. Only our own job group is signalled.
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait()
    returncode = process.wait()
    active["stdout"].close()
    active["stderr"].close()
    status = stop_reason or ("PASS" if returncode == 0 else "FAILED_EXIT")
    outputs = {}
    if status == "PASS":
        for name in active["job"]["outputs"]:
            path = active["attempt"] / name
            if not path.is_file():
                status = "FAILED_MISSING_OUTPUT"
                break
            outputs[name] = {"bytes": path.stat().st_size, "sha256": file_sha256(path)}
    receipt = {"job_id": active["job"]["id"], "job_identity": active["identity"],
               "status": status, "returncode": returncode, "outputs": outputs,
               "argv": active["argv"], "pid": process.pid,
               "elapsed_wall_s": time.monotonic() - active["started"],
               "peak_observed_tree_rss_bytes": active["peak_rss_bytes"],
               "finished_at": utc_now(),
               "acceptance_scope": "worker exit and declared output integrity; worker owns science criteria"}
    write_json_new(active["attempt"] / "receipt.json", receipt)
    return {"id": active["job"]["id"], "job_identity": active["identity"],
            "status": status, "attempt_dir": str(active["attempt"])}


def run(manifest_path, scope, *, profile="sandbox", max_workers=None,
        resource_wait_s=300., poll_s=.5, reserve_mb=256, retry_failed=False,
        max_scope_gib=4.):
    manifest_path, scope = Path(manifest_path).resolve(), Path(scope).resolve()
    manifest = validate_manifest(json.loads(manifest_path.read_text()))
    verify_bound_files(manifest, manifest_path.parent)
    cpu_cap, _ = PROFILES[profile]
    max_workers = cpu_cap if max_workers is None else min(cpu_cap, max_workers)
    if (max_workers < 1 or not 0 < resource_wait_s <= 1800
            or not .05 <= poll_s <= 10 or reserve_mb < 0
            or not math.isfinite(max_scope_gib) or max_scope_gib <= 0):
        raise ValueError("INVALID_EXECUTION_POLICY")
    max_scope_bytes = int(max_scope_gib * GIB)
    with execution_lock(scope):
        run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S") + "_" + uuid.uuid4().hex[:10]
        run_dir = scope / "executions" / run_id
        run_dir.mkdir(parents=True)
        manifest_hash = digest(manifest)
        immutable_path = scope / "manifests" / (manifest_hash + ".json")
        if not immutable_path.exists():
            write_json_new(immutable_path, manifest)
        elif canonical(json.loads(immutable_path.read_text())) != canonical(manifest):
            raise ValueError("SAVED_MANIFEST_CHANGED")
        policy = {"profile": profile, "max_workers": max_workers,
                  "profile_limits": {"cpu": cpu_cap, "memory_bytes": PROFILES[profile][1]},
                  "resource_wait_s": resource_wait_s, "poll_s": poll_s,
                  "memory_reserve_mb": reserve_mb, "retry_failed": retry_failed,
                  "max_scope_bytes": max_scope_bytes,
                  "filesystem_free_reserve_bytes": FILESYSTEM_FREE_RESERVE,
                  "disk_cap_scope": "new admission only; active output may finish beyond cap",
                  "nested_threads": THREAD_ENV, "manifest_sha256": manifest_hash,
                  "python": sys.version, "executable": sys.executable, "started_at": utc_now()}
        write_json_new(run_dir / "execution_policy.json", policy)
        results, pending, active = {}, [], []
        executor_error = None
        for job in manifest["jobs"]:
            identity = job_identity(manifest, job)
            job_dir = scope / "jobs" / job["id"] / identity
            attempts = sorted(job_dir.glob("attempt_*"))
            if attempts:
                reusable, reason, _ = verify_completed(attempts[-1], identity, job["outputs"])
                if reusable:
                    results[job["id"]] = {"id": job["id"], "job_identity": identity,
                                         "status": "SKIPPED_PASS", "attempt_dir": str(attempts[-1])}
                    continue
                if not retry_failed or reason == "INCOMPLETE_PREVIOUS_ATTEMPT":
                    results[job["id"]] = {"id": job["id"], "job_identity": identity,
                                         "status": "BLOCKED_" + reason, "attempt_dir": str(attempts[-1])}
                    continue
            pending.append({"job": job, "identity": identity, "job_dir": job_dir,
                            "next_attempt": len(attempts) + 1})
        observer = ResourceObserver()
        observer.sample()
        last_progress = time.monotonic()
        resource_log = (run_dir / "resource_observations.jsonl").open("x")
        try:
            while pending or active:
                time.sleep(poll_s)
                for item in list(active):
                    rss = process_tree_rss(item["process"].pid)
                    item["rss_bytes"] = rss
                    item["peak_rss_bytes"] = max(item["peak_rss_bytes"], rss)
                    finished = item["process"].poll() is not None
                    timed_out = (not finished and time.monotonic() - item["started"] >= item["job"].get("timeout_s", 1800))
                    if finished or timed_out:
                        results[item["job"]["id"]] = _finish(item, stop_reason="TIMEOUT" if timed_out else None)
                        active.remove(item)
                        last_progress = time.monotonic()
                snapshot = observer.sample()
                slots, memory = admission_budget(snapshot, active, profile=profile,
                    max_workers=max_workers, reserve_bytes=int(reserve_mb * MIB))
                disk = scope_disk_observation(scope)
                disk_gate = disk_admission_reason(disk, max_scope_bytes)
                if disk_gate:
                    slots = 0
                resource_log.write(json.dumps({"at": utc_now(), "snapshot": snapshot,
                    "active_jobs": len(active), "pending_jobs": len(pending),
                    "admission_slots": slots, "admission_memory_bytes": memory,
                    "disk_observation": disk, "disk_admission_gate": disk_gate}) + "\n")
                resource_log.flush()
                if slots:
                    verify_bound_files(manifest, manifest_path.parent)
                for candidate in list(pending):
                    job = candidate["job"]
                    needed = int(math.ceil(job.get("memory_mb", 256) * MIB))
                    if slots <= 0:
                        break
                    if needed > memory:
                        continue
                    # Outputs can grow during a multi-job admission batch.
                    if disk_admission_reason(scope_disk_observation(scope), max_scope_bytes):
                        break
                    attempt = candidate["job_dir"] / f"attempt_{candidate['next_attempt']:04d}"
                    attempt.mkdir(parents=True, exist_ok=False)
                    argv = [value.replace("{attempt_dir}", str(attempt)) for value in job["argv"]]
                    stdout, stderr = (attempt / "stdout.log").open("xb"), (attempt / "stderr.log").open("xb")
                    started = time.monotonic()
                    env = dict(os.environ)
                    env.update(THREAD_ENV)
                    try:
                        process = subprocess.Popen(argv, cwd=job.get("cwd", str(attempt)),
                            env=env, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr,
                            shell=False, start_new_session=True, close_fds=True)
                    except OSError as exc:
                        stdout.close()
                        stderr.write((repr(exc) + "\n").encode())
                        stderr.close()
                        receipt = {"job_identity": candidate["identity"], "status": "FAILED_LAUNCH",
                                   "outputs": {}, "error": repr(exc), "argv": argv}
                        write_json_new(attempt / "receipt.json", receipt)
                        results[job["id"]] = {"id": job["id"], "job_identity": candidate["identity"],
                                              "status": "FAILED_LAUNCH", "attempt_dir": str(attempt)}
                        pending.remove(candidate)
                        continue
                    write_json_new(attempt / "launch.json", {"pid": process.pid, "argv": argv,
                        "job_identity": candidate["identity"], "started_at": utc_now(),
                        "memory_estimate_bytes": needed, "timeout_s": job.get("timeout_s", 1800)})
                    active.append({**candidate, "process": process, "attempt": attempt,
                        "argv": argv, "stdout": stdout, "stderr": stderr, "started": started,
                        "memory_bytes": needed, "rss_bytes": 0, "peak_rss_bytes": 0})
                    pending.remove(candidate)
                    slots -= 1
                    memory -= needed
                    last_progress = time.monotonic()
                if pending and not active and time.monotonic() - last_progress >= resource_wait_s:
                    for item in pending:
                        results[item["job"]["id"]] = {"id": item["job"]["id"],
                            "job_identity": item["identity"], "status": "PENDING_RESOURCE_WAIT_TIMEOUT"}
                    pending.clear()
        except (Exception, KeyboardInterrupt) as exc:
            executor_error = {"type": type(exc).__name__, "message": str(exc)}
            for item in pending:
                results[item["job"]["id"]] = {"id": item["job"]["id"],
                    "job_identity": item["identity"], "status": "BLOCKED_EXECUTOR_ERROR"}
        finally:
            resource_log.close()
            # Interrupted coordinator: stop only jobs this invocation created.
            for item in active:
                results[item["job"]["id"]] = _finish(item, stop_reason="COORDINATOR_INTERRUPTED")
        ordered = [results[job["id"]] for job in manifest["jobs"]]
        complete = all(item["status"] in ("PASS", "SKIPPED_PASS") for item in ordered)
        summary = {"status": "COMPLETE" if complete else "INCOMPLETE_OR_FAILED",
                   "manifest_sha256": manifest_hash, "execution_directory": str(run_dir),
                   "jobs": ordered, "finished_at": utc_now()}
        if executor_error is not None:
            summary["executor_error"] = executor_error
        write_json_new(run_dir / "summary.json", summary)
        return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--scope", required=True, type=Path)
    parser.add_argument("--profile", choices=sorted(PROFILES), default="sandbox")
    parser.add_argument("--max-workers", type=int)
    parser.add_argument("--resource-wait-s", type=float, default=300)
    parser.add_argument("--poll-s", type=float, default=.5)
    parser.add_argument("--reserve-mb", type=float, default=256)
    parser.add_argument("--max-scope-gib", type=float, default=4.)
    parser.add_argument("--retry-failed", action="store_true")
    args = parser.parse_args(argv)
    try:
        summary = run(args.manifest, args.scope, profile=args.profile,
            max_workers=args.max_workers, resource_wait_s=args.resource_wait_s,
            poll_s=args.poll_s, reserve_mb=args.reserve_mb, retry_failed=args.retry_failed,
            max_scope_gib=args.max_scope_gib)
    except (ValueError, RuntimeError, OSError) as exc:
        print(json.dumps({"status": "EXECUTOR_REFUSAL", "reason": str(exc)}), file=sys.stderr)
        return 2
    print(json.dumps(summary, indent=2))
    return 0 if summary["status"] == "COMPLETE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
