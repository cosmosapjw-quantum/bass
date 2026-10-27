"""One endpoint invocation, or one explicitly authorized targeted repair.

Standard-library resource accounting only. This module never imports science.
The fresh allocation is cumulative across both invocations; closed allocations
and historical unknown preparation costs are never carried into it.
"""
import datetime
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parents[1]
COMMANDS = {"endpoint": [sys.executable, "code/run_endpoint.py"]}
CPU_CAP = 120
WALL_CAP = 300
AS_CAP = 768 * 1024 * 1024
REQUIRED_ENV = {
    "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1",
    "BLIS_NUM_THREADS": "1", "VECLIB_MAXIMUM_THREADS": "1",
    "OMP_DYNAMIC": "FALSE", "MKL_DYNAMIC": "FALSE",
    "PYTHONDONTWRITEBYTECODE": "1",
    "PYTHONPATH": "/workspace/scratch/2a7ffd1a5e61/runtime_deps",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def append(path, row):
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, allow_nan=False, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def main():
    own_start = resource.getrusage(resource.RUSAGE_SELF)
    if sys.argv[1:] != ["endpoint"]:
        raise ValueError("frozen invocation is python3 code/metered.py endpoint")
    freeze_path = ROOT / "inputs/EXECUTION_FREEZE_ENDPOINT.json"
    freeze = json.loads(freeze_path.read_text())
    if (freeze["status"] != "READY_FOR_AUTHORIZED_ENDPOINT"
            or freeze["commands"] != COMMANDS):
        raise ValueError("endpoint execution freeze/command does not match")
    environment = freeze["environment"]
    if any(environment.get(key) != value for key, value in REQUIRED_ENV.items()):
        raise ValueError("freeze must record exact numerical/dependency environment")
    if any(not isinstance(k, str) or not isinstance(v, str)
           for k, v in environment.items()):
        raise ValueError("frozen environment must contain string keys and values")
    ack = json.loads((ROOT / "delivery/S0_ROOT_ACK.json").read_text())
    if not all(ack.get(k) for k in (
            "root_authorized_endpoint_run", "actual_source_commit",
            "Drive_ACK", "Dropbox_ACK")):
        raise ValueError("actual S0 checkpoint/root endpoint authorization required")
    pre_path = ROOT / "provenance/PRE_NODE_endpoint.json"
    pre = json.loads(pre_path.read_text())
    if pre["node"] != "endpoint" or not pre.get("actual_readback"):
        raise ValueError("fresh actual AGENTS/HEAD/parallel pre-node read required")
    for item in freeze["files"]:
        if sha(ROOT / item["path"]) != item["sha256"]:
            raise ValueError("frozen byte mismatch: " + item["path"])

    budget = json.loads((ROOT / "BUDGET_LEDGER.json").read_text())
    expected = {"child_CPU_s": CPU_CAP, "child_wall_s": WALL_CAP,
                "max_RSS_MiB": 768, "threads": 1}
    if budget["allocation"] != expected:
        raise ValueError("fresh allocation differs from frozen resource contract")
    if (budget["prior_allocation_reopened"]
            or budget["prior_remainder_carried_forward"]
            or budget["historical_remaining_CPU_s"] is not None
            or budget["historical_remaining_wall_s"] is not None):
        raise ValueError("old allocation must remain closed with unknown remainder")

    out = ROOT / "results"
    out.mkdir(exist_ok=True)
    ledger = out / "EXECUTION_LEDGER.jsonl"
    events = ([json.loads(line) for line in ledger.read_text().splitlines()]
              if ledger.exists() else [])
    starts = [row for row in events if row["event"] == "STARTED"]
    terminals = [row for row in events if row["event"] in ("COMPLETED", "FAILED")]
    if (len(starts) != len(terminals)
            or [r["invocation"] for r in starts]
            != [r["invocation"] for r in terminals]):
        raise ValueError("incomplete prior debit; root must interpret before execution")
    if len(starts) >= 2:
        raise ValueError("one production plus at most one targeted repair exhausted")
    repair = bool(starts)
    if repair:
        if (freeze.get("root_authorized_targeted_repair") is not True
                or not freeze.get("targeted_repair_reason")):
            raise ValueError("another invocation requires root-authorized targeted repair")
    cpu = sum(row["child_cpu_s"] for row in terminals)
    wall = sum(row["child_wall_s"] for row in terminals)
    remain_cpu = math.floor(CPU_CAP - cpu)
    remain_wall = WALL_CAP - wall
    if remain_cpu < 1 or remain_wall <= 0:
        raise ValueError("fresh cumulative allocation exhausted")
    invocation = "endpoint_repair1" if repair else "endpoint"
    common = {
        "stage": "endpoint", "invocation": invocation,
        "command": COMMANDS["endpoint"], "cwd": str(ROOT),
        "freeze_sha256": sha(freeze_path), "pre_node_sha256": sha(pre_path),
        "requested_model": budget["requested_executor_model"],
        "observed_runtime_model": None,
        "aggregate_limits": {"child_CPU_s": CPU_CAP, "child_wall_s": WALL_CAP,
                             "address_space_bytes": AS_CAP, "threads": 1},
        "invocation_limits": {"child_CPU_s": remain_cpu,
                              "child_wall_s": remain_wall,
                              "address_space_bytes": AS_CAP},
        "historical_remaining_cpu_s": None,
        "historical_remaining_wall_s": None,
        "old_allocation_reopened": False, "prior_remainder_carried_forward": False,
        "preparation_cost": "UNMEASURED_UNKNOWN_NOT_ZERO",
        "environment": environment,
        "stdout_path": "results/" + invocation + ".stdout",
        "stderr_path": "results/" + invocation + ".stderr",
        "targeted_repair": repair,
    }
    if repair:
        common["targeted_repair_reason"] = freeze["targeted_repair_reason"]
    append(ledger, {**common, "event": "STARTED", "utc": utc(),
                    "python_version": sys.version,
                    "python_executable": sys.executable})

    def limits():
        resource.setrlimit(resource.RLIMIT_CPU, (remain_cpu, remain_cpu))
        resource.setrlimit(resource.RLIMIT_AS, (AS_CAP, AS_CAP))

    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    start = time.monotonic()
    failure = None
    rc = 125
    try:
        with (ROOT / common["stdout_path"]).open("wb") as stdout, \
                (ROOT / common["stderr_path"]).open("wb") as stderr:
            try:
                child = subprocess.run(
                    COMMANDS["endpoint"], cwd=ROOT, stdout=stdout, stderr=stderr,
                    env={**os.environ, **environment}, timeout=remain_wall,
                    preexec_fn=limits, check=False,
                )
                rc = child.returncode
            except subprocess.TimeoutExpired:
                rc = 124
                failure = "child wall timeout; child killed and reaped"
    except Exception as exc:
        failure = type(exc).__name__ + ": " + str(exc)
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    child_wall = time.monotonic() - start
    own_end = resource.getrusage(resource.RUSAGE_SELF)
    child_cpu = (after.ru_utime + after.ru_stime
                 - before.ru_utime - before.ru_stime)
    append(ledger, {
        **common, "event": "COMPLETED" if rc == 0 else "FAILED", "utc": utc(),
        "returncode": rc, "failure": failure,
        "child_cpu_s": child_cpu, "child_wall_s": child_wall,
        "child_user_cpu_s": after.ru_utime - before.ru_utime,
        "child_system_cpu_s": after.ru_stime - before.ru_stime,
        "child_peak_RSS_KiB": after.ru_maxrss,
        "wrapper_cpu_s": (own_end.ru_utime + own_end.ru_stime
                          - own_start.ru_utime - own_start.ru_stime),
        "cumulative_child_cpu_s": cpu + child_cpu,
        "cumulative_child_wall_s": wall + child_wall,
        "remaining_new_cpu_s": CPU_CAP - cpu - child_cpu,
        "remaining_new_wall_s": WALL_CAP - wall - child_wall,
    })
    return rc if rc >= 0 else 128 - rc


if __name__ == "__main__":
    sys.exit(main())
