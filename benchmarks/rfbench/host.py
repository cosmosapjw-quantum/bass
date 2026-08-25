"""Read-only Linux host capability probe for RF-BENCH-00.

The probe observes an already configured execution environment.  It never
creates cgroups, changes affinity, disables SMT, writes a governor, moves IRQs,
or performs another privileged host mutation.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import re
import shutil
import subprocess
from typing import Callable, Iterable


HOST_PERF_EVENTS = (
    "task-clock", "cycles", "instructions", "branches", "branch-misses",
    "cache-references", "cache-misses", "context-switches", "cpu-migrations",
    "minor-faults", "major-faults",
)


class ClaimLevel(StrEnum):
    DEDICATED_BARE_METAL = "DEDICATED_BARE_METAL"
    CONTROLLED_SHARED_PAIRED = "CONTROLLED_SHARED_PAIRED"
    EXPLORATORY_ONLY = "EXPLORATORY_ONLY"


@dataclass(frozen=True)
class CpuTopology:
    cpu: int
    package: int
    core: int
    numa_node: int | None
    thread_siblings: tuple[int, ...]
    last_level_cache_siblings: tuple[int, ...]


def _canonical_json(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def _sha256_json(value: object) -> str:
    return hashlib.sha256(_canonical_json(value)).hexdigest()


def parse_cpu_list(raw: str) -> tuple[int, ...]:
    """Parse the Linux cpulist syntax into a sorted, duplicate-free tuple."""

    raw = raw.strip()
    if not raw:
        return ()
    cpus: set[int] = set()
    for token in raw.split(","):
        token = token.strip()
        match = re.fullmatch(r"([0-9]+)(?:-([0-9]+))?", token)
        if match is None:
            raise ValueError(f"invalid Linux CPU-list token: {token!r}")
        first = int(match.group(1))
        last = first if match.group(2) is None else int(match.group(2))
        if last < first:
            raise ValueError(f"descending Linux CPU range: {token!r}")
        cpus.update(range(first, last + 1))
    return tuple(sorted(cpus))


def _read(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8").strip()
    except OSError:
        return None


def _read_int(path: Path) -> int | None:
    value = _read(path)
    try:
        return None if value is None else int(value)
    except ValueError:
        return None


def _pid_set(raw: str | None) -> tuple[int, ...] | None:
    if raw is None:
        return None
    try:
        return tuple(sorted({int(line) for line in raw.splitlines() if line.strip()}))
    except ValueError:
        return None


def _current_cgroup(proc_root: Path, cgroup_root: Path) -> tuple[str | None, Path | None]:
    raw = _read(proc_root / "self/cgroup")
    if raw is None:
        return None, None
    for line in raw.splitlines():
        fields = line.split(":", 2)
        if len(fields) == 3 and fields[0] == "0" and fields[1] == "":
            relative = PurePosixPath(fields[2])
            if ".." in relative.parts:
                return fields[2], None
            return fields[2], cgroup_root.joinpath(*relative.parts[1:])
    return None, None


def _numa_node(cpu_path: Path) -> int | None:
    for entry in sorted(cpu_path.glob("node[0-9]*")):
        match = re.fullmatch(r"node([0-9]+)", entry.name)
        if match:
            return int(match.group(1))
    return None


def _topology(sys_root: Path, cpus: Iterable[int]) -> list[CpuTopology]:
    records: list[CpuTopology] = []
    for cpu in sorted(set(cpus)):
        cpu_path = sys_root / f"devices/system/cpu/cpu{cpu}"
        package = _read_int(cpu_path / "topology/physical_package_id")
        core = _read_int(cpu_path / "topology/core_id")
        siblings_raw = _read(cpu_path / "topology/thread_siblings_list")
        llc_raw = _read(cpu_path / "cache/index3/shared_cpu_list")
        if package is None or core is None or siblings_raw is None:
            continue
        records.append(
            CpuTopology(
                cpu=cpu,
                package=package,
                core=core,
                numa_node=_numa_node(cpu_path),
                thread_siblings=parse_cpu_list(siblings_raw),
                last_level_cache_siblings=parse_cpu_list(llc_raw or str(cpu)),
            )
        )
    return records


def derive_cpu_sets(
    topology: Iterable[CpuTopology], effective_cpus: Iterable[int]
) -> dict[str, object]:
    """Derive one-thread and twelve-physical-core strata without using SMT twice."""

    effective = set(effective_cpus)
    by_node: dict[int | None, dict[tuple[int, int], CpuTopology]] = {}
    for record in topology:
        if record.cpu not in effective:
            continue
        if not set(record.thread_siblings).issubset(effective):
            continue
        node = by_node.setdefault(record.numa_node, {})
        key = (record.package, record.core)
        existing = node.get(key)
        if existing is None or record.cpu < existing.cpu:
            node[key] = record
    ranked = sorted(
        by_node.items(),
        key=lambda item: (-len(item[1]), -1 if item[0] is None else item[0]),
    )
    chosen_node, core_map = ranked[0] if ranked else (None, {})
    physical = [core_map[key] for key in sorted(core_map)]
    strict = [physical[0].cpu] if physical else []
    strict_siblings = list(physical[0].thread_siblings) if physical else []
    twelve = [item.cpu for item in physical[:12]] if len(physical) >= 12 else []
    reserved_siblings = sorted(
        {sibling for item in physical[:12] for sibling in item.thread_siblings}
    ) if twelve else []
    return {
        "numa_node": chosen_node,
        "eligible_physical_cores": len(physical),
        "strict_1t": strict,
        "strict_1t_smt_siblings": strict_siblings,
        "physical_12t": twelve,
        "physical_12t_smt_siblings": reserved_siblings,
        "capacity_12t": len(twelve) == 12,
    }


def _perf_probe(perf_binary: str | None) -> dict[str, object]:
    if perf_binary is None:
        return {"available": False, "reason": "perf executable not found"}
    command = [perf_binary, "stat", "--no-big-num", "-x", ";"]
    for event in HOST_PERF_EVENTS:
        command.extend(("-e", event))
    command.extend(("--", "true"))
    try:
        completed = subprocess.run(
            command, check=False, capture_output=True, text=True, timeout=10.0,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"available": False, "reason": f"perf probe failed: {exc}"}
    text = completed.stderr + completed.stdout
    observed: dict[str, dict[str, object]] = {}
    for line in text.splitlines():
        fields = [field.strip() for field in line.split(";")]
        if len(fields) < 5 or fields[2] not in HOST_PERF_EVENTS:
            continue
        value_ok = bool(fields[0]) and not fields[0].startswith("<")
        try:
            running_ratio = float(fields[4].rstrip("%")) / 100.0
        except ValueError:
            running_ratio = None
        observed[fields[2]] = {
            "value_available": value_ok,
            "running_ratio": running_ratio,
        }
    complete = all(
        event in observed
        and observed[event]["value_available"] is True
        and isinstance(observed[event]["running_ratio"], float)
        for event in HOST_PERF_EVENTS
    )
    ratios = [
        float(observed[event]["running_ratio"])
        for event in HOST_PERF_EVENTS
        if event in observed and isinstance(observed[event]["running_ratio"], float)
    ]
    minimum_ratio = min(ratios) if len(ratios) == len(HOST_PERF_EVENTS) else None
    available = (
        completed.returncode == 0
        and "not supported" not in text.lower()
        and complete
        and minimum_ratio is not None
    )
    return {
        "available": available,
        "exit_code": completed.returncode,
        "command": command,
        "output_sha256": hashlib.sha256(text.encode()).hexdigest(),
        "required_events_complete": complete,
        "minimum_running_ratio": minimum_ratio,
        "reason": None if available else "perf stat permission, event, or ratio proof failed",
    }


def _interface_availability(sys_root: Path, topology: list[CpuTopology]) -> dict[str, object]:
    cpu_paths = [sys_root / f"devices/system/cpu/cpu{record.cpu}" for record in topology]
    frequency_paths = [
        path / "cpufreq/scaling_cur_freq" for path in cpu_paths
        if (path / "cpufreq/scaling_cur_freq").is_file()
    ]
    throttle_paths: list[Path] = []
    for path in cpu_paths:
        throttle_paths.extend(sorted((path / "thermal_throttle").glob("*_throttle_count")))
    thermal_paths = sorted((sys_root / "class/thermal").glob("thermal_zone*/temp"))
    thermal_paths.extend(sorted((sys_root / "class/hwmon").glob("hwmon*/temp*_input")))
    return {
        "frequency": {
            "available": bool(frequency_paths),
            "path_count": len(frequency_paths),
        },
        "temperature": {
            "available": bool(thermal_paths),
            "path_count": len(thermal_paths),
        },
        "throttling": {
            "available": bool(throttle_paths),
            "path_count": len(throttle_paths),
        },
    }


def _perf_capacity(proc_root: Path, sys_root: Path) -> dict[str, object]:
    caps = sys_root / "bus/event_source/devices/cpu/caps"
    generic = _read_int(caps / "num_counters")
    fixed = _read_int(caps / "num_counters_fixed")
    watchdog = _read_int(proc_root / "sys/kernel/nmi_watchdog")
    required_generic_events = 6
    usable_generic = None
    if generic is not None:
        usable_generic = max(0, generic - (1 if watchdog else 0))
    return {
        "generic_counters": generic,
        "fixed_counters": fixed,
        "nmi_watchdog": watchdog,
        "required_simultaneous_generic_events": required_generic_events,
        "usable_generic_counters": usable_generic,
        "simultaneous_event_capacity_sufficient": (
            usable_generic is not None and usable_generic >= required_generic_events
        ),
    }


def probe_host(
    *,
    proc_root: Path = Path("/proc"),
    sys_root: Path = Path("/sys"),
    affinity: Iterable[int] | None = None,
    perf_probe: Callable[[str | None], dict[str, object]] = _perf_probe,
    dedicated_host_attestation: dict[str, object] | None = None,
) -> dict[str, object]:
    """Return a deterministic capability receipt without changing host state."""

    cgroup_root = sys_root / "fs/cgroup"
    cgroup_v2 = (cgroup_root / "cgroup.controllers").is_file()
    cgroup_relative, cgroup_path = _current_cgroup(proc_root, cgroup_root)
    affinity_values = tuple(sorted(
        os.sched_getaffinity(0) if affinity is None else set(affinity)
    ))
    effective_raw = _read(cgroup_path / "cpuset.cpus.effective") if cgroup_path else None
    exclusive_raw = (
        _read(cgroup_path / "cpuset.cpus.exclusive.effective") if cgroup_path else None
    )
    partition = _read(cgroup_path / "cpuset.cpus.partition") if cgroup_path else None
    try:
        effective = parse_cpu_list(effective_raw or "")
    except ValueError:
        effective = ()
    try:
        exclusive = parse_cpu_list(exclusive_raw or "")
    except ValueError:
        exclusive = ()
    topology = _topology(sys_root, effective or affinity_values)
    strata = derive_cpu_sets(topology, effective or affinity_values)
    perf_capacity = _perf_capacity(proc_root, sys_root)
    if perf_capacity["simultaneous_event_capacity_sufficient"]:
        perf = perf_probe(shutil.which("perf"))
    else:
        perf = {
            "available": False,
            "reason": "exact event group exceeds statically usable PMU capacity",
            "runtime_probe": "NOT_RUN_STATIC_CAPACITY_BLOCKER",
        }
    interfaces = _interface_availability(sys_root, topology)
    cgroup_cpu_stat = bool(cgroup_path and (cgroup_path / "cpu.stat").is_file())
    cgroup_cpu_psi = bool(cgroup_path and (cgroup_path / "cpu.pressure").is_file())
    cgroup_procs = _pid_set(_read(cgroup_path / "cgroup.procs")) if cgroup_path else None
    dedicated_required = {
        "bare_metal": True,
        "no_unrelated_workloads": True,
        "zero_vm_steal_observable": True,
        "topology_and_thermal_controls": True,
    }
    dedicated_valid = (
        isinstance(dedicated_host_attestation, dict)
        and all(dedicated_host_attestation.get(key) is value
                for key, value in dedicated_required.items())
        and isinstance(dedicated_host_attestation.get("attestation_id"), str)
        and bool(dedicated_host_attestation["attestation_id"])
    )

    blockers: list[str] = []
    if not cgroup_v2:
        blockers.append("cgroup_v2_unavailable")
    if partition != "isolated":
        blockers.append("cpuset_partition_not_isolated")
    if not effective or set(effective) != set(affinity_values):
        blockers.append("effective_cpuset_affinity_mismatch")
    if not exclusive or set(exclusive) != set(effective):
        blockers.append("exclusive_effective_cpuset_unproven")
    if not strata["capacity_12t"]:
        blockers.append("twelve_physical_cores_on_one_numa_node_unavailable")
    if not cgroup_cpu_stat or not cgroup_cpu_psi:
        blockers.append("cgroup_cpu_accounting_or_psi_unavailable")
    if cgroup_procs != (os.getpid(),):
        blockers.append("benchmark_cgroup_not_dedicated_to_probe_process")
    if not bool(perf.get("available")):
        blockers.append("perf_counters_unavailable")
    ratio = perf.get("minimum_running_ratio")
    if not isinstance(ratio, (int, float)) or ratio < 0.95:
        blockers.append("perf_running_ratio_unproven_or_below_minimum")
    if not perf_capacity["simultaneous_event_capacity_sufficient"]:
        blockers.append("perf_simultaneous_event_capacity_insufficient")
    if not bool(interfaces["frequency"]["available"]):
        blockers.append("frequency_observation_unavailable")
    if not bool(interfaces["temperature"]["available"]):
        blockers.append("temperature_observation_unavailable")
    if not bool(interfaces["throttling"]["available"]):
        blockers.append("throttle_counter_unavailable")
    if not (proc_root / "stat").is_file():
        blockers.append("proc_stat_unavailable")
    if not (proc_root / "interrupts").is_file():
        blockers.append("proc_interrupts_unavailable")
    if not (proc_root / "pressure/cpu").is_file():
        blockers.append("system_cpu_pressure_context_unavailable")

    if blockers:
        claim_level = ClaimLevel.EXPLORATORY_ONLY
    elif dedicated_valid:
        claim_level = ClaimLevel.DEDICATED_BARE_METAL
    else:
        claim_level = ClaimLevel.CONTROLLED_SHARED_PAIRED

    topology_payload = [asdict(record) for record in topology]
    payload: dict[str, object] = {
        "schema": "bass-rfbench-host-capability-v1",
        "read_only": True,
        "privileged_mutation_performed": False,
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
        },
        "cgroup": {
            "v2": cgroup_v2,
            "relative_path": cgroup_relative,
            "partition": partition,
            "effective_cpus": list(effective),
            "exclusive_effective_cpus": list(exclusive),
            "affinity": list(affinity_values),
            "effective_matches_affinity": set(effective) == set(affinity_values),
            "cpu_stat_available": cgroup_cpu_stat,
            "cpu_pressure_available": cgroup_cpu_psi,
            "processes": list(cgroup_procs) if cgroup_procs is not None else None,
            "dedicated_to_probe_process": cgroup_procs == (os.getpid(),),
            "controllers": (_read(cgroup_path / "cgroup.controllers") or "").split()
            if cgroup_path else [],
            "subtree_control": (_read(cgroup_path / "cgroup.subtree_control") or "").split()
            if cgroup_path else [],
        },
        "topology": topology_payload,
        "strata": strata,
        "kernel_cpu_control": {
            "smt_active": _read(sys_root / "devices/system/cpu/smt/active"),
            "smt_control": _read(sys_root / "devices/system/cpu/smt/control"),
            "isolated_cpus": list(parse_cpu_list(
                _read(sys_root / "devices/system/cpu/isolated") or ""
            )),
            "nohz_full_cpus": list(parse_cpu_list(
                _read(sys_root / "devices/system/cpu/nohz_full") or ""
            )),
        },
        "sample_signal_interfaces": {
            "proc_stat": (proc_root / "stat").is_file(),
            "proc_interrupts": (proc_root / "interrupts").is_file(),
            "system_cpu_pressure": (proc_root / "pressure/cpu").is_file(),
            "steal_delta": (proc_root / "stat").is_file(),
            "migrations": bool(perf.get("available")),
        },
        "interfaces": interfaces,
        "perf": perf,
        "perf_capacity": perf_capacity,
        "dedicated_host_attestation": dedicated_host_attestation,
        "dedicated_host_attestation_valid": dedicated_valid,
        "dedicated_claim_requirements": dedicated_required,
        "claim_level": claim_level.value,
        "authority_eligible": claim_level is not ClaimLevel.EXPLORATORY_ONLY,
        "acceptance_claim_allowed": claim_level is not ClaimLevel.EXPLORATORY_ONLY,
        "scaling_claim_allowed": False,
        "blockers": blockers,
        "unavailable_controls_policy": "EXPLORATORY_ONLY_NO_ACCEPTANCE_CLAIM",
    }
    payload["receipt_sha256"] = _sha256_json(payload)
    return payload
