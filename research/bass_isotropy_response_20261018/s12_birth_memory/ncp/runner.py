#!/usr/bin/env python3
"""Fixed-manifest S12 executor. It never edits source, old runs, or other processes."""
from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import re
import resource
import shutil
import signal
import subprocess
import sys
import time
import uuid

import resources

SCHEMA = "BASS_S12_JOB_MANIFEST_V1"
KINDS = {"build", "new_rust_history", "paired_finite_difference",
         "matched_accuracy_performance", "failed_native_b9_n64"}
THREAD_ENV = {key: "1" for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS",
             "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
             "RAYON_NUM_THREADS", "BLIS_NUM_THREADS")}
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
JOB_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,95}\Z")


def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode()


def digest_file(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def atomic_json(path, value):
    """Atomic create, not atomic overwrite; a completed receipt is immutable."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp-" + uuid.uuid4().hex)
    try:
        with temporary.open("xb") as stream:
            stream.write(json.dumps(value, indent=2, ensure_ascii=False,
                                    allow_nan=False).encode() + b"\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path)
        fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
    finally:
        temporary.unlink(missing_ok=True)


def relative(name):
    if not isinstance(name, str):
        raise ValueError("file paths must be strings")
    p = Path(name)
    if not name or p.is_absolute() or ".." in p.parts or str(p) == ".":
        raise ValueError("a nonempty safe relative file path is required")
    return p


def under(root, name):
    p = root / relative(name)
    if not p.resolve().is_relative_to(root.resolve()) or p.is_symlink():
        raise ValueError("path escapes the declared root or is a symlink: " + name)
    return p


def validate_hashes(root, values):
    if not isinstance(values, dict):
        raise ValueError("file hash declarations must be objects")
    for name, expected in values.items():
        if not isinstance(expected, str) or not HEX64.fullmatch(expected):
            raise ValueError("invalid SHA256: " + name)
        p = under(root, name)
        if not p.is_file() or digest_file(p) != expected:
            raise ValueError("source/input SHA256 mismatch: " + name)


def load_manifest(path, repo):
    raw = Path(path).read_bytes()
    data = json.loads(raw)
    if data.get("schema") != SCHEMA or data.get("scope") != "new_s12_birth_memory":
        raise ValueError("this launcher admits only the explicit new S12 manifest schema/scope")
    if data.get("allow_completed_campaign_replay") is not False:
        raise ValueError("completed campaign replay must be explicitly false")
    if not data.get("source_files"):
        raise ValueError("source_files cannot be empty")
    validate_hashes(repo, data["source_files"])
    jobs = data.get("jobs")
    if not isinstance(jobs, list) or not jobs:
        raise ValueError("a fixed nonempty job list is required")
    ids = [j.get("id") for j in jobs]
    if any(not isinstance(x, str) or not JOB_ID.fullmatch(x) for x in ids) or len(set(ids)) != len(ids):
        raise ValueError("job IDs must be safe and unique")
    for job in jobs:
        if job.get("kind") not in KINDS:
            raise ValueError("unregistered S12 job kind")
        needs = job.get("needs", [])
        if not isinstance(needs, list) or len(needs) != len(set(needs)) or any(n not in ids or n == job["id"] for n in needs):
            raise ValueError("invalid dependency list")
        argv = job.get("argv")
        if not isinstance(argv, list) or not argv or any(not isinstance(x, str) or not x or "\0" in x for x in argv):
            raise ValueError("argv must be an explicit nonempty string list, not a shell command")
        if any(n not in needs for arg in argv for n in re.findall(r"\{dep:([^}]+)\}", arg)):
            raise ValueError("command references an undeclared dependency")
        for key in ("cpus", "ram_bytes", "output_budget_bytes"):
            if type(job.get(key)) is not int or job[key] < 1:
                raise ValueError("positive integer resource declaration required: " + key)
        timeout = job.get("timeout_s", resources.TIMEOUT_CAP_SECONDS)
        if type(timeout) not in (int, float) or not 0 < timeout <= resources.TIMEOUT_CAP_SECONDS:
            raise ValueError("job timeout must be positive and at most1800 seconds")
        job["timeout_s"] = timeout
        if type(job.get("expected_exit", 0)) is not int:
            raise ValueError("expected_exit must be an integer")
        inputs = job.get("input_files")
        validate_hashes(repo, inputs)
        if job["kind"] != "build" and not inputs:
            raise ValueError("non-build jobs require an explicit hashed input file")
        outputs = job.get("artifacts")
        if not isinstance(outputs, list) or not outputs or len(outputs) != len(set(outputs)):
            raise ValueError("unique expected artifact paths required")
        for name in outputs:
            relative(name)
            if name in ("STARTED.json", "receipt.json", "stdout.log", "stderr.log"):
                raise ValueError("artifact uses a reserved receipt/log name")
        acceptance = job.get("accept", [])
        if not isinstance(acceptance, list) or (job["kind"] != "build" and not acceptance):
            raise ValueError("scientific jobs require explicit JSON acceptance checks")
        for gate in acceptance:
            if gate.get("artifact") not in outputs or not isinstance(gate.get("pointer"), str) or "equals" not in gate:
                raise ValueError("accept entries need declared artifact, JSON pointer, and equals")
        if not isinstance(job.get("env", {}), dict) or any(not isinstance(k, str) or not isinstance(v, str) for k, v in job.get("env", {}).items()):
            raise ValueError("environment must map strings to strings")
        if any(k in THREAD_ENV and v != "1" for k, v in job.get("env", {}).items()):
            raise ValueError("nested numerical threads are not admitted")
    visited, pending = set(), set(ids)
    while pending:
        ready = {j["id"] for j in jobs if j["id"] in pending and set(j.get("needs", [])) <= visited}
        if not ready:
            raise ValueError("dependency cycle")
        visited |= ready
        pending -= ready
    for key in ("reserve_cpus", "reserve_ram_bytes"):
        value = data.get(key, 1 if key == "reserve_cpus" else resources.GiB)
        if type(value) is not int or value < 0:
            raise ValueError("reservation must be a nonnegative integer")
        data[key] = value
    if type(data.get("max_workers", 64)) is not int or not 1 <= data.get("max_workers", 64) <= 64:
        raise ValueError("max_workers must be in1..64")
    return data, hashlib.sha256(raw).hexdigest()


def capacity(manifest, observation, active=()):
    cpu_reserved = sum(a["job"]["cpus"] for a in active)
    ram_reserved = sum(a["job"]["ram_bytes"] for a in active)
    groups = observation.get("own_process_groups", {})
    ram_headroom = sum(max(0, a["job"]["ram_bytes"] - groups.get(a["process"].pid, {}).get("rss_bytes", 0)) for a in active)
    external_busy = max(0.0, observation["busy_cpus_estimate"] - observation.get("own_busy_cpus_estimate", 0.0))
    return {"cpus": max(0, observation["cpu_cap"] - cpu_reserved - manifest["reserve_cpus"] - math.ceil(external_busy)),
            "ram_bytes": max(0, min(observation["ram_cap_bytes"] - ram_reserved,
                                    observation["ram_available_bytes"] - ram_headroom) - manifest["reserve_ram_bytes"]),
            "output_bytes": max(0, min(resources.DISK_CAP_BYTES - observation["disk_allocated_bytes"],
                                       observation["disk_free_bytes"]) - sum(a["job"]["output_budget_bytes"] for a in active)),
            "workers": max(0, min(manifest.get("max_workers", 64), observation["configured"]["workers"], observation["cpu_cap"]) - len(active)),
            "existing_busy_cpus_estimate": external_busy, "own_reserved_cpus": cpu_reserved,
            "own_reserved_ram_bytes": ram_reserved}


def fits(job, cap):
    return cap["workers"] >= 1 and all(job[k] <= cap[c] for k, c in (("cpus", "cpus"), ("ram_bytes", "ram_bytes"), ("output_budget_bytes", "output_bytes")))


def preflight(manifest, profile, disk_root):
    obs = resources.snapshot(profile, disk_root)
    cap = capacity(manifest, obs)
    roots = [j for j in manifest["jobs"] if not j.get("needs")]
    impossible = [j["id"] for j in manifest["jobs"] if j["cpus"] > obs["cpu_cap"] or j["ram_bytes"] + manifest["reserve_ram_bytes"] > obs["ram_cap_bytes"] or j["output_budget_bytes"] > resources.DISK_CAP_BYTES]
    return {"schema": "BASS_S12_PREFLIGHT_V1", "observed_at_utc": utc(),
            "observation": obs, "currently_available": cap, "permanently_oversized_jobs": impossible,
            "can_start": not impossible and any(fits(j, cap) for j in roots),
            "no_other_processes_modified": True, "science_execution": False}


def command_for(job, repo, run, dependencies):
    def expand(arg):
        arg = arg.replace("{repo}", str(repo)).replace("{run}", str(run))
        return re.sub(r"\{dep:([^}]+)\}", lambda match: str(dependencies[match[1]]["directory"]), arg)
    return [expand(arg) for arg in job["argv"]]


def job_identity(manifest, job, repo, dependencies):
    validate_hashes(repo, manifest["source_files"])
    validate_hashes(repo, job["input_files"])
    # A stable marker, not a fresh attempt directory, enters command identity.
    argv = command_for(job, repo, "<NEW_ATTEMPT>", dependencies)
    executable = shutil.which(argv[0]) if "/" not in argv[0] else argv[0]
    if not executable or not Path(executable).is_file():
        raise ValueError("executable not available after its dependency: " + argv[0])
    identity = {"schema": SCHEMA, "job": job, "source_files": manifest["source_files"],
                "thread_environment": THREAD_ENV, "executable_sha256": digest_file(executable),
                "executable_realpath": str(Path(executable).resolve()),
                "dependencies": {name: {"identity_sha256": value["receipt"]["identity_sha256"],
                                         "artifacts": value["receipt"]["artifacts"]}
                                 for name, value in dependencies.items()}}
    return hashlib.sha256(canonical(identity)).hexdigest(), identity


def verified_pass(directory, identity_sha256, job):
    try:
        if directory.is_symlink() or not directory.is_dir():
            return None
        receipt = json.loads((directory / "receipt.json").read_bytes())
        required = set(job["artifacts"]) | {"stdout.log", "stderr.log"}
        if receipt["status"] != "PASS" or receipt["identity_sha256"] != identity_sha256 or set(receipt["artifacts"]) != required:
            return None
        for name, metadata in receipt["artifacts"].items():
            p = under(directory, name)
            if not p.is_file() or p.stat().st_size != metadata["bytes"] or digest_file(p) != metadata["sha256"]:
                return None
        return receipt
    except (OSError, ValueError, KeyError, TypeError):
        return None


def pointer(value, path):
    if path == "":
        return value
    if not path.startswith("/"):
        raise ValueError("JSON pointer must start with /")
    for part in path[1:].split("/"):
        part = part.replace("~1", "/").replace("~0", "~")
        value = value[int(part)] if isinstance(value, list) else value[part]
    return value


def _own_group_signal(process, sig):
    try:
        os.killpg(process.pid, sig)
    except ProcessLookupError:
        pass


def launch(job, identity_sha, identity, manifest_sha, repo, runs, dependencies, cpus):
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S") + "_" + uuid.uuid4().hex[:12]
    directory = runs / job["id"] / stamp
    directory.mkdir(parents=True, exist_ok=False)
    argv = command_for(job, repo, directory, dependencies)
    env = os.environ.copy()
    env.update(job.get("env", {}))
    env.update(THREAD_ENV)
    def child_limits():
        os.sched_setaffinity(0, cpus)
        resource.setrlimit(resource.RLIMIT_AS, (job["ram_bytes"], job["ram_bytes"]))
        resource.setrlimit(resource.RLIMIT_FSIZE, (job["output_budget_bytes"], job["output_budget_bytes"]))
    stdout, stderr = (directory / "stdout.log").open("xb"), (directory / "stderr.log").open("xb")
    started, tick = utc(), time.monotonic()
    atomic_json(directory / "STARTED.json", {"schema": "BASS_S12_JOB_STARTED_V1", "job_id": job["id"],
                "started_at_utc": started, "manifest_sha256": manifest_sha, "identity_sha256": identity_sha,
                "identity": identity, "argv": argv, "cwd": str(directory), "assigned_cpus": cpus,
                "declared_cpu_ram_timeout_output": {k: job[k] for k in ("cpus", "ram_bytes", "timeout_s", "output_budget_bytes")}})
    try:
        process = subprocess.Popen(argv, cwd=directory, env=env, stdin=subprocess.DEVNULL,
                                   stdout=stdout, stderr=stderr, start_new_session=True,
                                   preexec_fn=child_limits)
    except BaseException as error:
        stdout.close(); stderr.close()
        atomic_json(directory / "receipt.json", {"schema": "BASS_S12_JOB_RECEIPT_V1", "status": "FAIL",
                    "job_id": job["id"], "identity_sha256": identity_sha, "started_at_utc": started,
                    "ended_at_utc": utc(), "elapsed_seconds": time.monotonic() - tick,
                    "exit_code": None, "reason": "SPAWN_ERROR: " + repr(error), "artifacts": {}})
        raise
    return {"job": job, "directory": directory, "process": process, "stdout": stdout, "stderr": stderr,
            "started": started, "tick": tick, "identity_sha": identity_sha, "manifest_sha": manifest_sha,
            "cpus": cpus, "peak_group_rss_bytes": 0, "stop_reason": None, "term_at": None}


def finish(active):
    process, directory, job = active["process"], active["directory"], active["job"]
    code = process.wait()
    active["stdout"].close(); active["stderr"].close()
    failures, artifacts = [], {}
    # A zero exit does not certify completion if the command left writers alive.
    remaining = resources.process_groups([process.pid])[process.pid]["live_processes"]
    if remaining:
        failures.append("UNEXPECTED_CHILD_PROCESSES_REMAIN")
        _own_group_signal(process, signal.SIGTERM)
        deadline = time.monotonic() + 2
        while resources.process_groups([process.pid])[process.pid]["live_processes"] and time.monotonic() < deadline:
            time.sleep(0.04)
        _own_group_signal(process, signal.SIGKILL)
    if active["stop_reason"]:
        failures.append(active["stop_reason"])
    if code != job.get("expected_exit", 0):
        failures.append("UNEXPECTED_EXIT")
    for name in job["artifacts"] + ["stdout.log", "stderr.log"]:
        try:
            p = under(directory, name)
            artifacts[name] = {"bytes": p.stat().st_size, "sha256": digest_file(p)}
        except (OSError, ValueError) as error:
            failures.append("ARTIFACT: " + name + ": " + str(error))
    for gate in job.get("accept", []):
        try:
            value = pointer(json.loads(under(directory, gate["artifact"]).read_bytes()), gate["pointer"])
            if type(value) is not type(gate["equals"]) or value != gate["equals"]:
                failures.append("JSON_ACCEPTANCE: " + gate["artifact"] + gate["pointer"])
        except (OSError, ValueError, KeyError, TypeError, IndexError) as error:
            failures.append("JSON_ACCEPTANCE_ERROR: " + str(error))
    rec = {"schema": "BASS_S12_JOB_RECEIPT_V1", "status": "FAIL" if failures else "PASS",
           "status_scope": "Process exit, exact source/input/command identity, required artifacts and explicitly declared JSON acceptance only.",
           "job_id": job["id"], "identity_sha256": active["identity_sha"], "manifest_sha256": active["manifest_sha"],
           "started_at_utc": active["started"], "ended_at_utc": utc(), "elapsed_seconds": time.monotonic() - active["tick"],
           "exit_code": code, "expected_exit": job.get("expected_exit", 0), "failures": failures,
           "timed_out": active["stop_reason"] == "TIMEOUT",
           "sampled_peak_own_process_group_rss_bytes": active["peak_group_rss_bytes"],
           "RSS_observation_scope": "Polling observations of this own process group; not an exact continuous maximum.",
           "assigned_cpus": active["cpus"],
           "artifacts": artifacts, "other_owner_processes_signaled": 0}
    atomic_json(directory / "receipt.json", rec)
    return {"directory": directory, "receipt": rec}


def execute(manifest, manifest_sha, repo, runs, disk_root, profile):
    runs.mkdir(parents=True, exist_ok=True)
    with (runs / ".launcher.lock").open("a+b") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        initial = preflight(manifest, profile, disk_root)
        stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S") + "_" + uuid.uuid4().hex[:12]
        invocation = runs / "invocations" / stamp
        atomic_json(invocation / "PREFLIGHT.json", initial)
        pending = {j["id"]: j for j in manifest["jobs"]}
        completed, outcomes, active, interrupted = {}, {}, [], []
        old_handlers = {}
        for sig in (signal.SIGINT, signal.SIGTERM):
            old_handlers[sig] = signal.signal(sig, lambda signum, frame: interrupted.append(signum))
        error_text = None
        try:
            if initial["permanently_oversized_jobs"]:
                raise RuntimeError("resource profile cannot fit: " + ", ".join(initial["permanently_oversized_jobs"]))
            while pending or active:
                observation = resources.snapshot(profile, disk_root, own_group_ids=[a["process"].pid for a in active])
                finished_this_round = False
                for a in list(active):
                    p, job = a["process"], a["job"]
                    rss = observation.get("own_process_groups", {}).get(p.pid, {}).get("rss_bytes", 0)
                    a["peak_group_rss_bytes"] = max(a["peak_group_rss_bytes"], rss)
                    reason = ("INTERRUPTED" if interrupted else "TIMEOUT" if time.monotonic() - a["tick"] > job["timeout_s"]
                              else "RAM_BUDGET_EXCEEDED" if rss > job["ram_bytes"]
                              else "OUTPUT_BUDGET_EXCEEDED" if resources.allocated_bytes(a["directory"]) > job["output_budget_bytes"]
                              else "DISK_CAP_EXCEEDED" if observation["disk_allocated_bytes"] > resources.DISK_CAP_BYTES else None)
                    if reason and a["term_at"] is None:
                        a["stop_reason"], a["term_at"] = reason, time.monotonic()
                        _own_group_signal(p, signal.SIGTERM)
                    if a["term_at"] is not None and time.monotonic() - a["term_at"] > 2:
                        _own_group_signal(p, signal.SIGKILL)
                    if p.poll() is not None:
                        result = finish(a); active.remove(a)
                        finished_this_round = True
                        outcomes[job["id"]] = {"status": result["receipt"]["status"], "directory": str(result["directory"])}
                        if result["receipt"]["status"] == "PASS":
                            completed[job["id"]] = result
                if interrupted:
                    if active:
                        continue
                    break
                progress = finished_this_round
                for ident, job in list(pending.items()):
                    needs = job.get("needs", [])
                    if any(n in outcomes and outcomes[n]["status"] not in ("PASS", "SKIPPED_EXACT_PASS") for n in needs):
                        outcomes[ident] = {"status": "BLOCKED_DEPENDENCY"}; del pending[ident]; progress = True; continue
                    if not all(n in completed for n in needs):
                        continue
                    dependencies = {n: completed[n] for n in needs}
                    identity_sha, identity = job_identity(manifest, job, repo, dependencies)
                    for directory in sorted((runs / ident).glob("*"), reverse=True):
                        old = verified_pass(directory, identity_sha, job)
                        if old is not None:
                            completed[ident] = {"directory": directory, "receipt": old}
                            outcomes[ident] = {"status": "SKIPPED_EXACT_PASS", "directory": str(directory)}
                            del pending[ident]; progress = True; break
                    if ident not in pending:
                        continue
                    cap = capacity(manifest, observation, active)
                    if not fits(job, cap):
                        continue
                    used = {cpu for a in active for cpu in a["cpus"]}
                    cpus = [cpu for cpu in observation["affinity"] if cpu not in used][:job["cpus"]]
                    active.append(launch(job, identity_sha, identity, manifest_sha, repo, runs, dependencies, cpus))
                    del pending[ident]; progress = True
                if not active and pending and not progress:
                    for ident in pending:
                        outcomes[ident] = {"status": "NOT_STARTED_RESOURCE_UNAVAILABLE"}
                    break
                if active:
                    time.sleep(0.08)
        except BaseException as error:
            error_text = repr(error)
        finally:
            for a in active:
                a["stop_reason"] = a["stop_reason"] or "LAUNCHER_INTERRUPTED_OR_ERROR"
                _own_group_signal(a["process"], signal.SIGTERM)
            deadline = time.monotonic() + 2
            while any(a["process"].poll() is None for a in active) and time.monotonic() < deadline:
                time.sleep(0.04)
            for a in active:
                if a["process"].poll() is None:
                    _own_group_signal(a["process"], signal.SIGKILL)
                result = finish(a)
                outcomes[a["job"]["id"]] = {"status": result["receipt"]["status"], "directory": str(result["directory"])}
            for ident in pending:
                outcomes.setdefault(ident, {"status": "NOT_STARTED"})
            for sig, handler in old_handlers.items():
                signal.signal(sig, handler)
        summary = {"schema": "BASS_S12_LAUNCH_SUMMARY_V1", "finished_at_utc": utc(), "manifest_sha256": manifest_sha,
                   "profile": profile, "jobs": outcomes, "error": error_text, "interrupted_signals": interrupted,
                   "status": "PASS" if len(outcomes) == len(manifest["jobs"]) and all(v["status"] in ("PASS", "SKIPPED_EXACT_PASS") for v in outcomes.values()) else "INCOMPLETE_OR_FAIL",
                   "historical_replay_policy": "Forbidden by the reviewed fixed S12 manifest; process exit alone does not establish scientific provenance.", "old_owner_jobs_killed": 0,
                   "scientific_case_order": "Fixed manifest order for ready whole cases; launcher never reorders angular/cohort reductions."}
        atomic_json(invocation / "SUMMARY.json", summary)
        return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("preflight", "run"))
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--runs", type=Path, required=True)
    parser.add_argument("--disk-root", type=Path, required=True)
    parser.add_argument("--profile", choices=tuple(resources.PROFILES), default="sandbox")
    args = parser.parse_args()
    repo, runs, disk_root = args.repo.resolve(), args.runs.resolve(), args.disk_root.resolve()
    if not repo.is_dir() or not disk_root.is_dir() or not runs.is_relative_to(disk_root) or not repo.is_relative_to(disk_root):
        raise ValueError("repo and new runs directory must be within the explicitly measured disk root")
    data, manifest_sha = load_manifest(args.manifest, repo)
    result = preflight(data, args.profile, disk_root) if args.action == "preflight" else execute(data, manifest_sha, repo, runs, disk_root, args.profile)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("can_start", result.get("status") == "PASS") else 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, RuntimeError) as error:
        print(json.dumps({"status": "ERROR", "error": str(error)}), file=sys.stderr)
        sys.exit(2)
