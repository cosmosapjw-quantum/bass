#!/usr/bin/env python3
"""Compile/run only the previously failed S8 case under a new frozen S12 source.

No legacy campaign CLI is called. Owner materialization is automatic, pinned,
small-file-only and read-only with respect to any supplied existing owner tree.
The current NCP delivery can be ready while actual execution remains NOT_RUN.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import resource
import shutil
import signal
import subprocess
import sys
import time
import urllib.request

from validate import load_json, validate

ROOT = Path(__file__).resolve().parent
REMOTE_PREFIX = "research/bass_isotropy_response_20261018/s12_birth_memory/native_followup/"
REPO = "cosmosapjw-quantum/bass"
OWNER = "0e25846433170d0f420c4cda44a0bedbf02cd177"
OWNER_REPO = "cosmosapjw-quantum/rei_bianchi"
GiB = 1 << 30
BUILD_FILES = ("native_followup.rs", "native_adapter.rs", "balance.rs", "balance_p24.rs", "s11_projector.rs")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git_blob(data):
    return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()


def write_once(path, data):
    if not isinstance(data, bytes):
        data = (json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False)+"\n").encode()
    with Path(path).open("xb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())


class JobInterrupted(Exception):
    def __init__(self, signum):
        self.signum = signum
        super().__init__("WRAPPER_SIGNAL:"+signal.Signals(signum).name)


class ChildGuard:
    """Only the process group created by this wrapper may be stopped."""
    signals = (signal.SIGTERM, signal.SIGINT)

    def __init__(self, out, receipt):
        self.out, self.receipt = out, receipt
        self.process = self.record = None
        self.previous = {}

    def install(self):
        for sig in self.signals:
            self.previous[sig] = signal.signal(sig, self.interrupt)

    def restore(self):
        for sig, handler in self.previous.items():
            signal.signal(sig, handler)

    def stop(self, reason):
        process = self.process
        result = {"reason": reason, "owned_child_pgid": None,
                  "term_sent": False, "kill_sent": False,
                  "term_wait_seconds_max": .75, "kill_reap_seconds_max": .15,
                  "unrelated_owner_processes_touched": False}
        if process is None:
            return result
        result["owned_child_pgid"] = process.pid
        start = time.monotonic()
        for sig, wait in ((signal.SIGTERM, .75), (signal.SIGKILL, .15)):
            key = "term" if sig == signal.SIGTERM else "kill"
            try:
                # start_new_session=True makes this exact child pid its pgid.
                # KILL also removes any descendant left after its leader exits.
                os.killpg(process.pid, sig)
                result[key+"_sent"] = True
            except ProcessLookupError:
                result[key+"_group_already_absent"] = True
            except OSError as error:
                result[key+"_error"] = str(error)
            try:
                process.wait(timeout=wait)
            except subprocess.TimeoutExpired:
                result[key+"_reap_timeout"] = True
        result["exit_code"] = process.poll()
        result["cleanup_elapsed_seconds"] = time.monotonic()-start
        if self.record is not None:
            self.record["termination"] = result
        return result

    def interrupt(self, signum, _frame):
        # A second TERM/INT must not interrupt cleanup or receipt persistence.
        for sig in self.signals:
            signal.signal(sig, signal.SIG_IGN)
        detail = {"schema": "BASS_S12_NATIVE_INTERRUPTION_V1",
                  "received_utc": datetime.now(timezone.utc).isoformat(),
                  "signal": int(signum), "signal_name": signal.Signals(signum).name,
                  "source_commit": self.receipt["source_commit"],
                  "command_label": None if self.record is None else self.record["label"],
                  "child_cleanup": self.stop("WRAPPER_SIGNAL")}
        self.receipt["interruption"] = detail
        # Persist separately before unwinding a potentially waiting download pool.
        # The external two-second grace may end before the final wrapper receipt.
        try:
            write_once(self.out/"INTERRUPTION.json", detail)
        except OSError as error:
            self.receipt["interruption_receipt_error"] = str(error)
        raise JobInterrupted(signum)


def safe_path(path):
    p = PurePosixPath(path)
    if p.is_absolute() or not p.parts or any(part in ("", ".", "..") for part in p.parts):
        raise ValueError("UNSAFE_MANIFEST_PATH")
    return str(p)


def identity(data, entry):
    if len(data) != entry["bytes"] or sha(data) != entry["sha256"]:
        raise ValueError("SOURCE_BYTES_OR_SHA256:"+entry["path"])
    if "git_blob" in entry and git_blob(data) != entry["git_blob"]:
        raise ValueError("SOURCE_GIT_BLOB:"+entry["path"])


def remaining(deadline):
    value = deadline-time.monotonic()
    if value <= 0:
        raise TimeoutError("JOB_DEADLINE")
    return value


def fetch_exact(url, size, deadline):
    request = urllib.request.Request(url, headers={"User-Agent": "BASS-S12-pinned-native-followup"})
    with urllib.request.urlopen(request, timeout=min(30.0, remaining(deadline))) as response:
        data = response.read(size+1)
    if len(data) != size:
        raise ValueError("REMOTE_SIZE:"+url)
    return data


def verify_source(commit, deadline):
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("IMMUTABLE_GIT_SOURCE_COMMIT_REQUIRED")
    manifest_bytes = (ROOT/"SOURCE_MANIFEST.json").read_bytes()
    manifest = load_json(manifest_bytes)
    if manifest.get("schema") != "BASS_S12_NATIVE_RUNTIME_SOURCE_MANIFEST_V1":
        raise ValueError("RUNTIME_MANIFEST_SCHEMA")
    entries = manifest["files"]
    names = [safe_path(e["path"]) for e in entries]
    required = set(BUILD_FILES) | {"run.py", "validate.py", "CONTRACT.json", "native_owner_manifest.json",
                                  "inputs/ORIGINAL_S8_FAILURE.json", "inputs/BASELINE_IDENTITY.json"}
    if len(set(names)) != len(names) or set(names) != required:
        raise ValueError("RUNTIME_MANIFEST_FILE_SET")
    url_base = "https://raw.githubusercontent.com/"+REPO+"/"+commit+"/"+REMOTE_PREFIX
    if fetch_exact(url_base+"SOURCE_MANIFEST.json", len(manifest_bytes), deadline) != manifest_bytes:
        raise ValueError("UNPUBLISHED_RUNTIME_MANIFEST")
    checked = []
    for entry in entries:
        path = safe_path(entry["path"])
        local = (ROOT/path).read_bytes()
        identity(local, entry)
        remote = fetch_exact(url_base+path, entry["bytes"], deadline)
        identity(remote, entry)
        if local != remote:
            raise ValueError("LOCAL_REMOTE_SOURCE_MISMATCH:"+path)
        checked.append(dict(entry))
    return {"method": "full immutable Git raw byte readback", "source_commit": commit,
            "manifest_sha256": sha(manifest_bytes), "files": checked}


def verify_local_source(binding):
    if sha((ROOT/"SOURCE_MANIFEST.json").read_bytes()) != binding["manifest_sha256"]:
        raise ValueError("MANIFEST_CHANGED_DURING_RUN")
    for entry in binding["files"]:
        identity((ROOT/entry["path"]).read_bytes(), entry)


def owner_entries():
    manifest = load_json((ROOT/"native_owner_manifest.json").read_bytes())
    if manifest.get("repo") != OWNER_REPO or manifest.get("commit") != OWNER:
        raise ValueError("ORIGINAL_OWNER_AUTHORITY")
    rows = []
    for entry in manifest["files"]:
        path = safe_path(entry["path"])
        if not path.startswith("rust/rei_microphysics/src/"):
            raise ValueError("OWNER_PATH_SCOPE")
        rows.append({"path": path, "bytes": entry["size"], "sha256": entry["sha256"], "git_blob": entry["sha"]})
    if len(rows) != 57 or len({e["path"] for e in rows}) != 57 or sum(e["bytes"] for e in rows) != 614313:
        raise ValueError("OWNER_MANIFEST_CARDINALITY")
    return rows


def verify_owner(root):
    rows = owner_entries()
    for entry in rows:
        identity((root/entry["path"]).read_bytes(), entry)
    return {"commit": OWNER, "repo": OWNER_REPO, "files": len(rows),
            "bytes": sum(e["bytes"] for e in rows), "all_git_blob_sha256_size_pass": True}


def stage_owner(destination, deadline, workers, downloads):
    destination.mkdir()
    entries = owner_entries()
    def fetch(entry):
        start = time.monotonic()
        url = "https://raw.githubusercontent.com/"+OWNER_REPO+"/"+OWNER+"/"+entry["path"]
        record = {"path": entry["path"], "url": url, "attempts": 1, "status": "STARTED"}
        downloads.append(record)
        try:
            data = fetch_exact(url, entry["bytes"], deadline)
            identity(data, entry)
            target = destination/entry["path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            write_once(target, data)
            record.update(status="PASS", bytes=len(data), sha256=sha(data), git_blob=git_blob(data))
        except Exception as error:
            record.update(status="FAILED", error_type=type(error).__name__, error=str(error))
            raise
        finally:
            record["elapsed_seconds"] = time.monotonic()-start
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for _ in pool.map(fetch, entries):
            pass
    return verify_owner(destination)


def allocated_bytes(roots):
    seen, total = set(), 0
    for root in roots:
        for directory, dirs, files in os.walk(root, followlinks=False):
            dirs[:] = [d for d in dirs if not (Path(directory)/d).is_symlink()]
            for name in files:
                stat = (Path(directory)/name).lstat()
                key = (stat.st_dev, stat.st_ino)
                if key not in seen:
                    seen.add(key)
                    total += stat.st_blocks*512
    return total


def resource_snapshot(out):
    affinity = sorted(os.sched_getaffinity(0))
    memory = {}
    for line in Path("/proc/meminfo").read_text().splitlines():
        key, value = line.split(":", 1)
        memory[key] = int(value.split()[0])*1024
    caps, free = [4*GiB, memory["MemTotal"]], [memory["MemAvailable"]]
    quotas = []
    cgroot = Path("/sys/fs/cgroup")
    groups = [cgroot]
    for line in Path("/proc/self/cgroup").read_text().splitlines():
        parts = line.split(":", 2)
        if len(parts) == 3 and parts[0] == "0":
            group = (cgroot/parts[2].lstrip("/")).resolve()
            if group.is_relative_to(cgroot):
                while group != cgroot:
                    groups.append(group)
                    group = group.parent
    for group in set(groups):
        try:
            cap, current = (group/"memory.max").read_text().strip(), int((group/"memory.current").read_text())
            if cap != "max":
                caps.append(int(cap)); free.append(max(0, int(cap)-current))
            quota, period = (group/"cpu.max").read_text().split()
            if quota != "max":
                quotas.append(int(quota)/int(period))
        except FileNotFoundError:
            continue
    available = min(free)
    if not affinity or (quotas and min(quotas) < 1) or available < GiB:
        raise RuntimeError("CURRENT_CPU_OR_RAM_UNAVAILABLE")
    cap = min(*caps, available-GiB//2)
    if cap < GiB//2:
        raise RuntimeError("MEMORY_RESERVATION_UNAVAILABLE")
    used = allocated_bytes((ROOT.parent, out))
    disk_free = shutil.disk_usage(out).free
    if used >= 4*GiB or disk_free < GiB//2:
        raise RuntimeError("TASK_DISK_UNAVAILABLE")
    return {"affinity": affinity, "cgroup_cpu_quota_cores": quotas,
            "ram_available_bytes_observed": available, "child_address_space_cap_bytes": cap,
            "task_allocated_bytes": used, "disk_free_bytes": disk_free,
            "native_threads": 1, "existing_owner_processes_modified": False,
            "admission_note": "Root batch resource scheduler remains responsible for whole-batch reservations; no exclusive CPU claim."}


def command(label, args, out, deadline, ram_cap, receipt, guard):
    stdout_path, stderr_path = out/(label+".stdout"), out/(label+".stderr")
    start = time.monotonic()
    record = {"label": label, "argv": [str(a) for a in args], "status": "STARTED",
              "stdout": stdout_path.name, "stderr": stderr_path.name}
    receipt["commands"].append(record)
    def limits():
        signal.pthread_sigmask(signal.SIG_SETMASK, previous_mask)
        resource.setrlimit(resource.RLIMIT_AS, (ram_cap, ram_cap))
        resource.setrlimit(resource.RLIMIT_FSIZE, (4*GiB, 4*GiB))
    env = dict(os.environ, RUST_TEST_THREADS="1", RAYON_NUM_THREADS="1", OMP_NUM_THREADS="1",
               OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1")
    process = None
    try:
        with stdout_path.open("xb") as stdout, stderr_path.open("xb") as stderr:
            # Prevent the signal-before-child-registration orphan race. The
            # child restores the prior mask before exec; the parent restores it
            # only after the exact owned process group is registered.
            previous_mask = signal.pthread_sigmask(signal.SIG_BLOCK, guard.signals)
            try:
                process = subprocess.Popen(record["argv"], stdout=stdout, stderr=stderr, env=env,
                                           start_new_session=True, preexec_fn=limits)
                guard.process, guard.record = process, record
                record["owned_child_pgid"] = process.pid
            finally:
                signal.pthread_sigmask(signal.SIG_SETMASK, previous_mask)
            try:
                status = process.wait(timeout=remaining(deadline))
            except (subprocess.TimeoutExpired, TimeoutError):
                guard.stop("COMMAND_DEADLINE")
                record.update(status="TIMEOUT", exit_code=process.returncode)
                raise TimeoutError("COMMAND_DEADLINE:"+label)
            record.update(status="PASS" if status == 0 else "FAILED", exit_code=status)
            # wait() reaped this leader. Any remaining member of its exact
            # owned group is unfinished work even when the leader returned zero.
            try:
                os.killpg(process.pid, 0)
            except ProcessLookupError:
                pass
            else:
                guard.stop("LEFTOVER_OWNED_CHILDREN")
                record.update(status="FAILED", failure="LEFTOVER_OWNED_CHILDREN")
                raise RuntimeError("LEFTOVER_OWNED_CHILDREN:"+label)
        if status:
            raise RuntimeError("COMMAND_FAILED:"+label)
        if allocated_bytes((ROOT.parent, out)) > 4*GiB:
            raise RuntimeError("TASK_DISK_CAP")
        return stdout_path.read_text(errors="replace")
    except JobInterrupted:
        record.update(status="INTERRUPTED", exit_code=None if process is None else process.poll())
        raise
    except BaseException:
        if process is not None and process.poll() is None:
            guard.stop("COMMAND_EXCEPTION")
            record.update(status="FAILED", exit_code=process.poll())
        raise
    finally:
        if guard.process is process:
            guard.process = guard.record = None
        record["elapsed_seconds"] = time.monotonic()-start
        for field, path in (("stdout", stdout_path), ("stderr", stderr_path)):
            if path.exists():
                data = path.read_bytes()
                record[field+"_bytes"] = len(data)
                record[field+"_sha256"] = sha(data)


def run(args):
    if not 1 <= args.download_workers <= 4 or not 60 <= args.timeout <= 1800:
        raise ValueError("EXECUTION_LIMIT")
    out = args.out.resolve()
    if out.exists():
        raise FileExistsError("CREATE_ONLY_OUTPUT_REQUIRED:"+str(out))
    out.mkdir(parents=True)
    start = time.monotonic()
    deadline = start+min(1740, args.timeout-15)
    receipt = {"schema": "BASS_S12_NATIVE_EXECUTION_V1", "status": "STARTED",
               "started_utc": datetime.now(timezone.utc).isoformat(), "source_commit": args.source_commit,
               "owner_commit": OWNER, "argv": sys.argv, "commands": [], "downloads": [],
               "completed_old_cases_replayed": 0, "case_count": 1,
               "resume_semantics": "One new initial-state attempt of one previously failed case; not checkpoint resume."}
    exit_code = 2
    guard = ChildGuard(out, receipt)
    guard.install()
    try:
        observation = resource_snapshot(out)
        receipt["resources_before"] = observation
        binding = verify_source(args.source_commit, deadline)
        receipt["source_binding"] = binding
        contract = load_json((ROOT/"CONTRACT.json").read_bytes())
        if (contract["owner_commit"] != OWNER or contract["owner_repo"] != OWNER_REPO
                or contract["cases_csv"] != "b9_n64_P2P4,64,0.9,P2P4\n"):
            raise ValueError("ONE_CASE_CONTRACT")
        failure = load_json((ROOT/"inputs/ORIGINAL_S8_FAILURE.json").read_bytes())
        baseline = load_json((ROOT/"inputs/BASELINE_IDENTITY.json").read_bytes())
        if args.verify_only:
            receipt.update(status="SOURCE_AND_INPUT_VERIFIED_NOT_COMPILED_NOT_EXECUTED", native_histories_executed=0)
            exit_code = 0
        else:
            owner = args.owner_root.resolve() if args.owner_root else out/"owner_source"
            receipt["owner_verification_before"] = (verify_owner(owner) if args.owner_root else
                stage_owner(owner, deadline, args.download_workers, receipt["downloads"]))
            rustc = args.rustc or shutil.which("rustc")
            if not rustc:
                raise FileNotFoundError("RUST_COMPILER_UNAVAILABLE")
            receipt["rustc_version"] = command("compiler_version", [rustc, "-Vv"], out, deadline,
                                               observation["child_address_space_cap_bytes"], receipt, guard)
            build = out/"build"
            build.mkdir()
            for name in BUILD_FILES:
                write_once(build/name, (ROOT/name).read_bytes())
            rlib, binary = build/"librei_microphysics.rlib", build/"native_followup"
            command("compile_pinned_owner", [rustc, "--crate-name", "rei_microphysics", "--crate-type", "rlib",
                    "--edition=2021", "-O", "-C", "codegen-units=1", owner/"rust/rei_microphysics/src/lib.rs", "-o", rlib],
                    out, deadline, observation["child_address_space_cap_bytes"], receipt, guard)
            command("compile_s12_followup", [rustc, "--edition=2021", "-O", "-C", "codegen-units=1",
                    build/"native_followup.rs", "--extern", "rei_microphysics="+str(rlib), "-o", binary],
                    out, deadline, observation["child_address_space_cap_bytes"], receipt, guard)
            receipt["compiled_sha256"] = {p.name: sha(p.read_bytes()) for p in (rlib, binary)}
            if args.compile_only:
                receipt.update(status="COMPILED_NOT_EXECUTED", native_histories_executed=0)
                exit_code = 0
            else:
                cases = out/"CASES.csv"
                write_once(cases, contract["cases_csv"].encode())
                raw = out/"NATIVE_FOLLOWUP.jsonl"
                receipt["native_histories_attempted"] = 1
                command("measure_single_failed_case", [binary, cases, raw], out, deadline,
                        observation["child_address_space_cap_bytes"], receipt, guard)
                receipt["raw_sha256"] = sha(raw.read_bytes())
                analysis = validate(raw, contract, failure, baseline)
                write_once(out/"ANALYSIS.json", analysis)
                receipt["analysis_sha256"] = sha((out/"ANALYSIS.json").read_bytes())
                receipt.update({key: analysis[key] for key in ("status", "integrity_gates_pass", "angular_accuracy_target_met", "completed_native_histories")})
                exit_code = 0 if analysis["integrity_gates_pass"] else 2
            receipt["owner_verification_after"] = verify_owner(owner)
        verify_local_source(binding)
    except JobInterrupted as error:
        exit_code = 128+error.signum
        receipt.update(status="INTERRUPTED", failure_type=type(error).__name__, failure=str(error))
    except Exception as error:
        exit_code = 2
        receipt.update(status="FAILED", failure_type=type(error).__name__, failure=str(error))
    finally:
        receipt["elapsed_seconds"] = time.monotonic()-start
        receipt["finished_utc"] = datetime.now(timezone.utc).isoformat()
        receipt["wrapper_exit_code"] = exit_code
        receipt["children_peak_rss_kib_linux"] = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
        receipt["python_peak_rss_kib_linux"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        receipt["task_allocated_bytes_end"] = allocated_bytes((ROOT.parent, out))
        try:
            write_once(out/"RETURN_NATIVE_FOLLOWUP.json", receipt)
        finally:
            guard.restore()
    print(json.dumps({k: receipt.get(k) for k in ("status", "integrity_gates_pass", "angular_accuracy_target_met", "elapsed_seconds", "wrapper_exit_code")}, allow_nan=False))
    return exit_code


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-commit", required=True, help="Frozen actual S12 execution source commit, supplied by the published batch job")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--owner-root", type=Path, help="Optional existing pinned owner source, verified read-only; otherwise fetch automatically")
    parser.add_argument("--rustc")
    parser.add_argument("--download-workers", type=int, default=4)
    parser.add_argument("--timeout", type=int, default=1800)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--verify-only", action="store_true")
    modes.add_argument("--compile-only", action="store_true")
    return run(parser.parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
