"""Read-only Linux resource observations; no process control or host changes."""
from __future__ import annotations

import math
import os
from pathlib import Path
import shutil
import time

GiB = 1 << 30
PROFILES = {
    "sandbox": {"cpus": 16, "ram_bytes": 16 * GiB, "workers": 16},
    "ncp": {"cpus": 64, "ram_bytes": 128 * GiB, "workers": 64},
}
DISK_CAP_BYTES = 4 * GiB
TIMEOUT_CAP_SECONDS = 1800


def text(path: Path) -> str | None:
    try:
        return path.read_text().strip()
    except (OSError, ValueError):
        return None


def number(path: Path) -> int | None:
    value = text(path)
    try:
        return int(value) if value not in (None, "max") else None
    except ValueError:
        return None


def cgroup_directories() -> list[Path]:
    root = Path("/sys/fs/cgroup")
    found = [root]
    for row in (text(Path("/proc/self/cgroup")) or "").splitlines():
        parts = row.split(":", 2)
        if len(parts) != 3 or parts[0] != "0":
            continue
        candidate = (root / parts[2].lstrip("/")).resolve()
        if candidate.is_relative_to(root) and candidate.exists():
            while candidate != root:
                found.append(candidate)
                candidate = candidate.parent
    return list(dict.fromkeys(found))


def _cpu_counters(affinity: list[int]) -> dict[int, tuple[int, int]]:
    result = {}
    wanted = set(affinity)
    for line in (text(Path("/proc/stat")) or "").splitlines():
        fields = line.split()
        if not fields or not fields[0].startswith("cpu") or not fields[0][3:].isdigit():
            continue
        cpu = int(fields[0][3:])
        if cpu in wanted:
            values = [int(x) for x in fields[1:9]]
            result[cpu] = (sum(values), values[3] + values[4])
    return result


def _cgroup_usage(directories: list[Path]) -> int | None:
    # Deepest readable cgroup is closest to this workload's actual allocation.
    for directory in sorted(directories, key=lambda x: len(x.parts), reverse=True):
        values = dict(line.split() for line in (text(directory / "cpu.stat") or "").splitlines()
                      if len(line.split()) == 2)
        if "usage_usec" in values:
            return int(values["usage_usec"]) * 1000
    return number(Path("/sys/fs/cgroup/cpuacct/cpuacct.usage"))


def allocated_bytes(root: Path) -> int:
    """Count allocated blocks once per inode without following symlinks."""
    seen, total = set(), 0
    for directory, subdirs, files in os.walk(root, followlinks=False):
        subdirs[:] = [n for n in subdirs if not (Path(directory) / n).is_symlink()]
        for name in files:
            try:
                st = (Path(directory) / name).lstat()
            except FileNotFoundError:
                continue
            key = (st.st_dev, st.st_ino)
            if key not in seen:
                seen.add(key)
                total += getattr(st, "st_blocks", math.ceil(st.st_size / 512)) * 512
    return total


def _namespace_numbers(status, name):
    value = status.get(name)
    if value is None:
        return None
    result = [int(x) for x in value.split()]
    if not result or any(x < 0 for x in result):
        raise RuntimeError("invalid procfs namespace identifiers: " + name)
    return result


def procfs_identity() -> dict:
    """Prove how this process's POSIX IDs relate to the mounted procfs view."""
    raw = Path("/proc/self/stat").read_text()
    tail = raw.rsplit(") ", 1)[1].split()
    host_pid, host_pgid = int(raw.split(" ", 1)[0]), int(tail[2])
    status = dict(line.split(":", 1) for line in Path("/proc/self/status").read_text().splitlines() if ":" in line)
    pids, groups = _namespace_numbers(status, "NSpid"), _namespace_numbers(status, "NSpgid")
    namespace = os.readlink("/proc/self/ns/pid")
    if not namespace.startswith("pid:["):
        raise RuntimeError("PID namespace identity unavailable")
    if pids is not None and groups is not None:
        if pids[0] != host_pid or groups[0] != host_pgid or pids[-1] != os.getpid() or groups[-1] != os.getpgrp() or len(pids) != len(groups):
            raise RuntimeError("ambiguous local/procfs namespace identity")
        mode, depth = "VERIFIED_NSPID_NSPGID", len(pids)
    elif pids is None and groups is None and host_pid == os.getpid() and host_pgid == os.getpgrp():
        mode, depth = "VERIFIED_PLAIN_PROCFS_SELF_IDS", 1
    else:
        raise RuntimeError("cannot prove local/procfs PID mapping")
    return {"mode": mode, "pid_namespace": namespace, "namespace_depth": depth,
            "local_pid": os.getpid(), "local_pgid": os.getpgrp(),
            "procfs_self_pid": host_pid, "procfs_self_pgid": host_pgid,
            "self_NSpid": pids, "self_NSpgid": groups}


def process_groups(group_ids) -> dict[int, dict]:
    """Observe owned groups plus PPID descendants, including nested sessions.

    This is accounting only. Signal targets remain exact owned process groups.
    A child reparented before this /proc snapshot may no longer be attributable;
    reviewed wrappers must retain supervision until their owned children finish.
    """
    proof = procfs_identity()
    result = {int(group): {"rss_bytes": 0, "cpu_seconds": 0.0, "live_processes": 0,
                          "process_ids": [], "procfs_pids": [], "namespace_proof": proof,
                          "nested_session_processes": 0,
                          "nested_session_rss_bytes": 0} for group in group_ids}
    if not result:
        return result
    ticks, page = os.sysconf("SC_CLK_TCK"), os.sysconf("SC_PAGE_SIZE")
    processes, children, local_pids = {}, {}, {}
    for proc in Path("/proc").iterdir():
        if not proc.name.isdigit():
            continue
        try:
            status = dict(line.split(":", 1) for line in (proc / "status").read_text().splitlines() if ":" in line)
            pids, groups = _namespace_numbers(status, "NSpid"), _namespace_numbers(status, "NSpgid")
            # Processes in an ancestor namespace cannot be in this namespace.
            # This also avoids probing inaccessible host-owner namespace links.
            if pids is not None and len(pids) < proof["namespace_depth"]:
                continue
            if os.readlink(proc / "ns/pid") != proof["pid_namespace"]:
                continue
            raw = (proc / "stat").read_text()
            row = raw.rsplit(") ", 1)[1].split()
            pid, parent, host_group = int(proc.name), int(row[1]), int(row[2])
            if int(raw.split(" ", 1)[0]) != pid:
                raise RuntimeError("procfs PID changed during namespace observation")
            if pids is not None and groups is not None:
                if pids[0] != pid or groups[0] != host_group or len(pids) != proof["namespace_depth"] or len(groups) != len(pids):
                    raise RuntimeError("inconsistent same-namespace process mapping")
                local_pid, group = pids[-1], groups[-1]
            elif pids is None and groups is None and proof["mode"] == "VERIFIED_PLAIN_PROCFS_SELF_IDS":
                local_pid, group = pid, host_group
            else:
                raise RuntimeError("same-namespace process mapping unavailable")
            if local_pid in local_pids and local_pids[local_pid] != pid:
                raise RuntimeError("ambiguous local PID mapping")
            local_pids[local_pid] = pid
            processes[pid] = {"parent": parent, "group": group, "procfs_group": host_group,
                              "local_pid": local_pid, "rss_bytes": int(row[21]) * page,
                              "cpu_seconds": (int(row[11]) + int(row[12])) / ticks,
                              "live": row[0] != "Z"}
            children.setdefault(parent, []).append(pid)
        except (FileNotFoundError, ProcessLookupError):
            continue
        except (OSError, ValueError, IndexError) as error:
            raise RuntimeError("cannot verify procfs process namespace: " + proc.name) from error
    for group, total in result.items():
        pending = [pid for pid, value in processes.items() if value["group"] == group]
        mapped_groups = {processes[pid]["procfs_group"] for pid in pending}
        if len(mapped_groups) > 1:
            raise RuntimeError("ambiguous owned local PGID mapping")
        total["local_process_group"] = group
        total["procfs_process_group"] = next(iter(mapped_groups), None)
        if not pending:
            try:
                os.killpg(group, 0)  # Existence probe of the exact local owned group.
            except ProcessLookupError:
                pass
            else:
                raise RuntimeError("live owned group is absent from verified procfs namespace mapping")
        seen = set()
        while pending:
            pid = pending.pop()
            if pid in seen:
                continue
            seen.add(pid)
            value = processes[pid]
            # An explicitly tracked peer group retains its own accounting.
            if value["group"] in result and value["group"] != group:
                continue
            total["procfs_pids"].append(pid)
            total["process_ids"].append(value["local_pid"])
            total["rss_bytes"] += value["rss_bytes"]
            total["cpu_seconds"] += value["cpu_seconds"]
            total["live_processes"] += value["live"]
            if value["group"] != group:
                total["nested_session_processes"] += value["live"]
                total["nested_session_rss_bytes"] += value["rss_bytes"]
            pending.extend(children.get(pid, []))
        total["procfs_pids"].sort()
        total["process_ids"].sort()
    return result


def snapshot(profile: str, disk_root: Path, sample_seconds: float = 0.12,
             own_group_ids=()) -> dict:
    """Admission observations, not an exclusive reservation of other users' CPUs."""
    if profile not in PROFILES:
        raise ValueError("unknown resource profile")
    namespace_proof = procfs_identity()
    affinity = sorted(os.sched_getaffinity(0))
    groups = cgroup_directories()
    quota_values = []
    memory_caps, memory_available = [], []
    for group in groups:
        cpu_max = text(group / "cpu.max")
        if cpu_max:
            quota, period = cpu_max.split()
            if quota != "max":
                quota_values.append(int(quota) / int(period))
        cap, current = number(group / "memory.max"), number(group / "memory.current")
        if cap is not None and current is not None:
            memory_caps.append(cap)
            memory_available.append(max(0, cap - current))
    if not quota_values:
        quota = number(Path("/sys/fs/cgroup/cpu/cpu.cfs_quota_us"))
        period = number(Path("/sys/fs/cgroup/cpu/cpu.cfs_period_us"))
        if quota is not None and quota > 0 and period:
            quota_values.append(quota / period)
    if not memory_caps:
        cap = number(Path("/sys/fs/cgroup/memory/memory.limit_in_bytes"))
        current = number(Path("/sys/fs/cgroup/memory/memory.usage_in_bytes"))
        if cap is not None and current is not None and cap < 1 << 60:
            memory_caps.append(cap)
            memory_available.append(max(0, cap - current))
    info = {}
    for line in (text(Path("/proc/meminfo")) or "").splitlines():
        key, value = line.split(":", 1)
        info[key] = int(value.split()[0]) * 1024
    if not affinity or not info.get("MemAvailable") or not info.get("MemTotal"):
        raise RuntimeError("Linux affinity/MemAvailable observation unavailable; cannot admit resources")
    configured = PROFILES[profile]
    cpu_cap = min(configured["cpus"], len(affinity), *(math.floor(q) for q in quota_values))
    ram_cap = min(configured["ram_bytes"], info["MemTotal"], *memory_caps)
    available = min(ram_cap, info["MemAvailable"], *memory_available)
    own_first = process_groups(own_group_ids)
    first, used_first, started = _cpu_counters(affinity), _cgroup_usage(groups), time.monotonic()
    time.sleep(sample_seconds)
    second, used_second, ended = _cpu_counters(affinity), _cgroup_usage(groups), time.monotonic()
    own_second = process_groups(own_group_ids)
    busy_affinity = 0.0
    for cpu, (total, idle) in second.items():
        if cpu in first and total > first[cpu][0]:
            busy_affinity += max(0.0, min(1.0, 1 - (idle - first[cpu][1]) / (total - first[cpu][0])))
    scaled_host_busy = busy_affinity * cpu_cap / len(affinity)
    scaled_load = os.getloadavg()[0] * cpu_cap / (os.cpu_count() or len(affinity))
    group_busy = ((used_second - used_first) / 1e9 / (ended - started)
                  if used_first is not None and used_second is not None else 0.0)
    own_busy = sum(max(0.0, value["cpu_seconds"] - own_first[group]["cpu_seconds"])
                   for group, value in own_second.items()) / (ended - started)
    return {"profile": profile, "configured": configured, "affinity": affinity,
            "cgroup_cpu_quota_cores": quota_values, "cgroup_memory_caps": memory_caps,
            "cpu_cap": cpu_cap, "ram_cap_bytes": ram_cap, "ram_available_bytes": available,
            "busy_cpus_estimate": min(cpu_cap, max(scaled_host_busy, scaled_load, group_busy)),
            "own_busy_cpus_estimate": own_busy, "own_process_groups": own_second,
            "procfs_namespace_proof": namespace_proof,
            "own_process_accounting": "Verified local-PGID to procfs-PGID mapping within the same PID namespace, then observed procfs PPID descendants across nested sessions; reparenting before observation can remove ancestry. No procfs PID or PGID is a signal target.",
            "cpu_load_components": {"scaled_host_busy": scaled_host_busy,
                                    "scaled_load1": scaled_load, "cgroup_busy": group_busy},
            "cpu_sample_seconds": ended - started,
            "disk_root": str(disk_root), "disk_allocated_bytes": allocated_bytes(disk_root),
            "disk_free_bytes": shutil.disk_usage(disk_root).free,
            "disk_cap_bytes": DISK_CAP_BYTES,
            "reservation_semantics": "Hard own-job allocation ledger plus refreshed load/memory admission; other owner jobs are never killed or modified."}
