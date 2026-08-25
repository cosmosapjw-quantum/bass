"""Read-only command collector for an already provisioned controlled cgroup."""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import signal
import shutil
import subprocess
import tempfile
import time
from typing import Any, Mapping

from .protocol import sample_contamination_reasons, sha256_json
from .runner import ResolvedSource


PERF_EVENTS = (
    "task-clock",
    "cycles",
    "instructions",
    "branches",
    "branch-misses",
    "cache-references",
    "cache-misses",
    "context-switches",
    "cpu-migrations",
    "minor-faults",
    "major-faults",
)


def _read(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8").strip()
    except OSError:
        return None


def _cpu_list(raw: str | None) -> list[int] | None:
    if raw is None:
        return None
    values: set[int] = set()
    if not raw.strip():
        return []
    try:
        for token in raw.split(","):
            bounds = token.strip().split("-", 1)
            first = int(bounds[0])
            last = first if len(bounds) == 1 else int(bounds[1])
            if last < first:
                return None
            values.update(range(first, last + 1))
    except ValueError:
        return None
    return sorted(values)


def _pid_list(raw: str | None) -> list[int] | None:
    if raw is None:
        return None
    try:
        return sorted({int(line) for line in raw.splitlines() if line.strip()})
    except ValueError:
        return None


def _kv(raw: str | None) -> dict[str, int] | None:
    if raw is None:
        return None
    values: dict[str, int] = {}
    for line in raw.splitlines():
        fields = line.split()
        if len(fields) != 2:
            return None
        try:
            values[fields[0]] = int(fields[1])
        except ValueError:
            return None
    return values or None


def _psi_total(raw: str | None, kind: str = "some") -> int | None:
    for line in (raw or "").splitlines():
        fields = line.split()
        if fields and fields[0] == kind:
            for field in fields[1:]:
                if field.startswith("total="):
                    try:
                        return int(field.split("=", 1)[1])
                    except ValueError:
                        return None
    return None


def _proc_cpu(raw: str | None, cpus: set[int]) -> dict[int, tuple[int, ...]]:
    result: dict[int, tuple[int, ...]] = {}
    for line in (raw or "").splitlines():
        fields = line.split()
        if not fields or not fields[0].startswith("cpu") or fields[0] == "cpu":
            continue
        try:
            cpu = int(fields[0][3:])
            values = tuple(int(value) for value in fields[1:])
        except ValueError:
            continue
        if cpu in cpus:
            result[cpu] = values
    return result


def _irq_totals(raw: str | None, cpus: set[int]) -> dict[int, int] | None:
    lines = (raw or "").splitlines()
    if not lines:
        return None
    header = lines[0].split()
    columns: dict[int, int] = {}
    for index, name in enumerate(header):
        if name.startswith("CPU"):
            try:
                cpu = int(name[3:])
            except ValueError:
                continue
            if cpu in cpus:
                columns[cpu] = index + 1
    if set(columns) != cpus:
        return None
    totals = {cpu: 0 for cpu in columns}
    for line in lines[1:]:
        fields = line.split()
        if not fields or fields[0] in {"ERR:", "MIS:"}:
            continue
        for cpu, index in columns.items():
            if index >= len(fields):
                return None
            try:
                totals[cpu] += int(fields[index])
            except ValueError:
                return None
    return totals


def _frequency(sys_root: Path, cpus: set[int]) -> dict[int, int] | None:
    values: dict[int, int] = {}
    for cpu in sorted(cpus):
        raw = _read(sys_root / f"devices/system/cpu/cpu{cpu}/cpufreq/scaling_cur_freq")
        try:
            if raw is not None:
                values[cpu] = int(raw) * 1000
        except ValueError:
            continue
    return values if set(values) == cpus else None


def _throttle(sys_root: Path, cpus: set[int]) -> int | None:
    values: list[int] = []
    for cpu in sorted(cpus):
        root = sys_root / f"devices/system/cpu/cpu{cpu}/thermal_throttle"
        paths = sorted(root.glob("*_throttle_count"))
        if not paths:
            return None
        for path in paths:
            raw = _read(path)
            try:
                if raw is not None:
                    values.append(int(raw))
            except ValueError:
                return None
    return sum(values) if values else None


def _temperature(sys_root: Path) -> int | None:
    values: list[int] = []
    for pattern in ("class/thermal/thermal_zone*/temp", "class/hwmon/hwmon*/temp*_input"):
        for path in sorted(sys_root.glob(pattern)):
            raw = _read(path)
            try:
                if raw is not None:
                    value = int(raw)
                    if -100_000 <= value <= 250_000:
                        values.append(value)
            except ValueError:
                pass
    return max(values) if values else None


def _snapshot(
    *, proc_root: Path, sys_root: Path, cgroup_path: Path, cpus: set[int]
) -> dict[str, Any]:
    return {
        "monotonic_ns": time.monotonic_ns(),
        "cgroup_cpu_stat": _kv(_read(cgroup_path / "cpu.stat")),
        "cgroup_cpu_psi_some_total_us": _psi_total(_read(cgroup_path / "cpu.pressure")),
        "system_cpu_psi_some_total_us": _psi_total(_read(proc_root / "pressure/cpu")),
        "proc_cpu": _proc_cpu(_read(proc_root / "stat"), cpus),
        "irq": _irq_totals(_read(proc_root / "interrupts"), cpus),
        "frequency_hz": _frequency(sys_root, cpus),
        "throttle_count": _throttle(sys_root, cpus),
        "temperature_millicelsius": _temperature(sys_root),
        "cgroup_partition": _read(cgroup_path / "cpuset.cpus.partition"),
        "cgroup_effective_cpus": _cpu_list(
            _read(cgroup_path / "cpuset.cpus.effective")
        ),
        "cgroup_exclusive_effective_cpus": _cpu_list(
            _read(cgroup_path / "cpuset.cpus.exclusive.effective")
        ),
        "cgroup_procs": _pid_list(_read(cgroup_path / "cgroup.procs")),
    }


def _delta_number(before: int | None, after: int | None) -> int | None:
    if before is None or after is None or after < before:
        return None
    return after - before


def _dict_delta(
    before: Mapping[str, int] | None, after: Mapping[str, int] | None,
) -> dict[str, int] | None:
    """Return a complete monotonic delta, never a plausible partial receipt."""

    if before is None or after is None or before.keys() != after.keys():
        return None
    if any(after[key] < before[key] for key in before):
        return None
    return {key: after[key] - before[key] for key in sorted(before)}


def _cpu_delta(
    before: Mapping[int, tuple[int, ...]], after: Mapping[int, tuple[int, ...]],
    cpus: set[int],
) -> dict[str, list[int]] | None:
    """Return all requested per-CPU deltas or fail the evidence cell closed."""

    if set(before) != cpus or set(after) != cpus:
        return None
    result: dict[str, list[int]] = {}
    for cpu in sorted(cpus):
        left, right = before[cpu], after[cpu]
        if len(left) != len(right) or len(left) < 8:
            return None
        if any(b < a for a, b in zip(left, right)):
            return None
        result[str(cpu)] = [b - a for a, b in zip(left, right)]
    return result


def _counter_delta(
    before: Mapping[int, int] | None, after: Mapping[int, int] | None,
    cpus: set[int],
) -> dict[str, int] | None:
    if before is None or after is None or set(before) != cpus or set(after) != cpus:
        return None
    if any(after[cpu] < before[cpu] for cpu in cpus):
        return None
    return {str(cpu): after[cpu] - before[cpu] for cpu in sorted(cpus)}


def _parse_perf(path: Path) -> dict[str, Any]:
    events: dict[str, dict[str, float | int | None]] = {}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        lines = []
    for line in lines:
        fields = line.split(";")
        if len(fields) < 3:
            continue
        raw_value, unit, event = (field.strip() for field in fields[:3])
        if raw_value.startswith("<"):
            events[event] = {"value": None, "unit": unit, "running_ratio": None}
            continue
        try:
            value: float | int = float(raw_value)
        except ValueError:
            continue
        try:
            time_running_ns = float(fields[3].strip())
            percentage = float(fields[4].strip().rstrip("%"))
            ratio = percentage / 100.0
        except (IndexError, ValueError):
            time_running_ns = None
            ratio = None
        time_enabled_ns = (
            None if time_running_ns is None or ratio is None or ratio <= 0.0
            else time_running_ns / ratio
        )
        events[event] = {
            "value": value,
            "unit": unit,
            "running_ratio": ratio,
            "time_running_ns": time_running_ns,
            "time_enabled_ns": time_enabled_ns,
        }
    ratios = [
        float(item["running_ratio"]) for item in events.values()
        if item["running_ratio"] is not None
    ]
    matched = {
        event for event in PERF_EVENTS
        if any(name == event or name.startswith(event + ":") for name in events)
    }
    observed = {
        next(
            (event for event in PERF_EVENTS
             if name == event or name.startswith(event + ":")),
            name,
        )
        for name in events
    }
    return {
        "events": events,
        "minimum_running_ratio": min(ratios) if ratios else None,
        "all_required_events_present": matched == set(PERF_EVENTS) and all(
            any(
                (name == event or name.startswith(event + ":"))
                and receipt.get("value") is not None
                and receipt.get("running_ratio") is not None
                for name, receipt in events.items()
            )
            for event in PERF_EVENTS
        ),
        "exact_event_set": observed == set(PERF_EVENTS),
    }


def _event_value(perf: Mapping[str, Any], event: str) -> float | None:
    for name, receipt in perf.get("events", {}).items():
        if name == event or name.startswith(event + ":"):
            value = receipt.get("value")
            return float(value) if isinstance(value, (int, float)) else None
    return None


def _event_unit(perf: Mapping[str, Any], event: str) -> str | None:
    for name, receipt in perf.get("events", {}).items():
        if name == event or name.startswith(event + ":"):
            unit = receipt.get("unit")
            return unit if isinstance(unit, str) else None
    return None


def _last_json_line(raw: str) -> dict[str, Any]:
    for line in reversed(raw.splitlines()):
        if line.strip():
            try:
                value = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(value, dict):
                return value
    raise RuntimeError("benchmark command did not emit a JSON object")


def _normalize_child(
    payload: Mapping[str, Any], *, workload_id: str, mode: str,
    repetitions: int, warmup_iterations: int, cpu_set: tuple[int, ...],
    worker_count: int,
) -> tuple[int, int, str, str, list[list[int]], list[int]]:
    if payload.get("schema") != "bass-rfbench-child-observation-v1":
        raise RuntimeError("benchmark child schema mismatch")
    if payload.get("workload_id") != workload_id or payload.get("mode") != mode:
        raise RuntimeError("benchmark child workload or mode mismatch")
    if payload.get("repetitions") != repetitions:
        raise RuntimeError("benchmark child repetition count mismatch")
    if payload.get("warmup_iterations") != warmup_iterations:
        raise RuntimeError("benchmark child warmup count mismatch")
    wall = payload.get("wall_time_ns")
    total_wall = payload.get("timed_total_wall_time_ns")
    output_digest = payload.get("output_digest")
    input_digest = payload.get("input_identity_sha256")
    if not isinstance(wall, int) or wall <= 0:
        raise RuntimeError("benchmark child did not emit a positive measured duration")
    if not isinstance(total_wall, int) or total_wall <= 0:
        raise RuntimeError("benchmark child did not emit total measured duration")
    if wall != max(1, round(total_wall / repetitions)):
        raise RuntimeError("benchmark child per-iteration duration is inconsistent")
    if not isinstance(output_digest, str) or len(output_digest) != 64:
        raise RuntimeError("benchmark child did not emit output_digest")
    if not isinstance(input_digest, str) or len(input_digest) != 64:
        raise RuntimeError("benchmark child did not emit input_identity_sha256")
    worker_affinities = payload.get("worker_affinities")
    if (
        not isinstance(worker_affinities, list)
        or len(worker_affinities) != worker_count
        or any(not isinstance(mask, list) for mask in worker_affinities)
        or any(any(isinstance(cpu, bool) or not isinstance(cpu, int) for cpu in mask)
               for mask in worker_affinities)
    ):
        raise RuntimeError("benchmark child worker affinity receipt is invalid")
    canonical_masks = [sorted(set(mask)) for mask in worker_affinities]
    if worker_count == 1:
        affinity_valid = canonical_masks == [list(cpu_set)]
    else:
        affinity_valid = (
            all(len(mask) == 1 for mask in canonical_masks)
            and sorted(mask[0] for mask in canonical_masks) == sorted(cpu_set)
        )
    if not affinity_valid:
        raise RuntimeError("benchmark child worker affinity does not match the stratum")
    task_clocks = payload.get("per_worker_task_clock_ns")
    if (
        not isinstance(task_clocks, list)
        or len(task_clocks) != worker_count
        or any(isinstance(value, bool) or not isinstance(value, int) or value <= 0
               for value in task_clocks)
    ):
        raise RuntimeError("benchmark child per-worker task-clock receipt is invalid")
    first_touch = payload.get("first_touch")
    ownership = payload.get("thread_ownership")
    if not isinstance(first_touch, Mapping) or first_touch.get("verified") is not True:
        raise RuntimeError("benchmark child first-touch receipt is unverified")
    if not isinstance(ownership, Mapping) or ownership.get("verified") is not True:
        raise RuntimeError("benchmark child thread-ownership receipt is unverified")
    for name in ("major_faults_after_warmup", "involuntary_context_switches"):
        value = payload.get(name)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise RuntimeError(f"benchmark child {name} receipt is invalid")
    return (
        wall, total_wall, output_digest, input_digest,
        canonical_masks, task_clocks,
    )


_OUTPUT_LIMIT_BYTES = 1_048_576
_TERMINATE_GRACE_SECONDS = 2.0


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _terminate_process_group(process: subprocess.Popen[bytes]) -> None:
    """Terminate the complete benchmark process group and always reap its leader."""

    def group_exists() -> bool:
        try:
            os.killpg(process.pid, 0)
            return True
        except ProcessLookupError:
            return False

    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    deadline = time.monotonic() + _TERMINATE_GRACE_SECONDS
    while group_exists() and time.monotonic() < deadline:
        process.poll()
        time.sleep(0.05)
    if group_exists():
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    try:
        process.wait(timeout=_TERMINATE_GRACE_SECONDS)
    except subprocess.TimeoutExpired:
        try:
            process.kill()
        except ProcessLookupError:
            pass
        process.wait()


def _wait_bounded(
    process: subprocess.Popen[bytes], *, stdout_path: Path, stderr_path: Path,
    timeout_seconds: float,
) -> int:
    """Wait while enforcing wall-time and file-backed output bounds."""

    deadline = time.monotonic() + timeout_seconds
    while process.poll() is None:
        if any(
            path.exists() and path.stat().st_size > _OUTPUT_LIMIT_BYTES
            for path in (stdout_path, stderr_path)
        ):
            _terminate_process_group(process)
            raise RuntimeError("benchmark command exceeded the 1 MiB output cap")
        remaining = deadline - time.monotonic()
        if remaining <= 0.0:
            _terminate_process_group(process)
            raise RuntimeError("benchmark command timed out and its process group was reaped")
        try:
            process.wait(timeout=min(0.05, remaining))
        except subprocess.TimeoutExpired:
            continue
    returncode = process.wait()
    if any(
        path.exists() and path.stat().st_size > _OUTPUT_LIMIT_BYTES
        for path in (stdout_path, stderr_path)
    ):
        raise RuntimeError("benchmark command exceeded the 1 MiB output cap")
    return returncode


def _run_fields(
    run_contract: Mapping[str, Any], workload: Mapping[str, Any],
) -> tuple[str, int, int, float | None]:
    mode = run_contract.get("mode")
    repetitions = run_contract.get("repetitions")
    warmups = run_contract.get("warmup_iterations")
    if mode not in {"calibrate", "warmup", "sample"}:
        raise ValueError("run_contract.mode must be calibrate, warmup, or sample")
    if (
        isinstance(repetitions, bool) or not isinstance(repetitions, int)
        or repetitions < 1
    ):
        raise ValueError("run_contract.repetitions must be a positive integer")
    if (
        isinstance(warmups, bool) or not isinstance(warmups, int) or warmups < 0
    ):
        raise ValueError("run_contract.warmup_iterations must be non-negative")
    minimum = workload.get("minimum_duration_seconds")
    declared_minimum = run_contract.get("minimum_duration_seconds", minimum)
    if declared_minimum != minimum:
        raise ValueError("run_contract minimum duration differs from the corpus")
    if minimum is not None:
        if (
            isinstance(minimum, bool) or not isinstance(minimum, (int, float))
            or not math.isfinite(float(minimum)) or float(minimum) <= 0.0
        ):
            raise ValueError("workload minimum_duration_seconds is invalid")
        minimum = float(minimum)
    return mode, repetitions, warmups, minimum


class CommandCollector:
    """Collect an observation in the caller's already isolated cgroup."""

    def __init__(
        self,
        host_probe: Mapping[str, Any],
        *,
        proc_root: Path = Path("/proc"),
        sys_root: Path = Path("/sys"),
    ) -> None:
        self.host_probe = host_probe
        self.proc_root = proc_root
        self.sys_root = sys_root
        relative = host_probe.get("cgroup", {}).get("relative_path")
        if not isinstance(relative, str):
            raise ValueError("host probe has no cgroup path")
        self.cgroup_path = sys_root / "fs/cgroup" / relative.lstrip("/")
        self.perf = shutil.which("perf")
        if self.perf is None:
            raise ValueError("perf is required for controlled collection")

    def _collect(
        self, source: ResolvedSource, workload: Mapping[str, Any],
        cpu_set: tuple[int, ...], worker_count: int,
        run_contract: Mapping[str, Any],
    ) -> dict[str, Any]:
        mode, repetitions, warmups, minimum = _run_fields(run_contract, workload)
        if not cpu_set or len(set(cpu_set)) != len(cpu_set):
            raise ValueError("requested cpu_set must be non-empty and unique")
        if worker_count < 1 or worker_count > len(cpu_set):
            raise ValueError("worker_count is incompatible with the requested cpu_set")
        evidence_cpus = set(cpu_set)
        before = _snapshot(
            proc_root=self.proc_root, sys_root=self.sys_root,
            cgroup_path=self.cgroup_path, cpus=evidence_cpus,
        )
        environment = os.environ.copy()
        environment.update({
            "PYTHONHASHSEED": "0",
            "PYTHONNOUSERSITE": "1",
            "RAYON_NUM_THREADS": str(worker_count),
            "OMP_NUM_THREADS": "1",
            "OPENBLAS_NUM_THREADS": "1",
            "MKL_NUM_THREADS": "1",
            "BLIS_NUM_THREADS": "1",
            "NUMEXPR_NUM_THREADS": "1",
            "BASS_RFBENCH_SOURCE_ROOT": str(source.root),
            "BASS_RFBENCH_MODE": mode,
            "BASS_RFBENCH_REPETITIONS": str(repetitions),
            "BASS_RFBENCH_WARMUPS": str(warmups),
        })

        def pin_child() -> None:
            os.sched_setaffinity(0, set(cpu_set))

        with tempfile.TemporaryDirectory(prefix="bass-rfbench-perf-") as temp:
            temp_path = Path(temp)
            perf_path = temp_path / "perf.csv"
            stdout_path = temp_path / "stdout.bin"
            stderr_path = temp_path / "stderr.bin"
            command = [self.perf, "stat", "--no-big-num", "-x", ";", "-o", str(perf_path)]
            for event in PERF_EVENTS:
                command.extend(("-e", event))
            command.extend(("--", *source.command))
            timeout = workload.get("timeout_seconds")
            if (
                isinstance(timeout, bool) or not isinstance(timeout, (int, float))
                or not math.isfinite(float(timeout)) or float(timeout) <= 0.0
            ):
                raise ValueError("executable workload must declare a positive timeout")
            with stdout_path.open("wb") as stdout_stream, stderr_path.open("wb") as stderr_stream:
                process = subprocess.Popen(
                    command, cwd=source.root, env=environment,
                    stdout=stdout_stream, stderr=stderr_stream,
                    start_new_session=True, preexec_fn=pin_child,
                )
                returncode = _wait_bounded(
                    process, stdout_path=stdout_path, stderr_path=stderr_path,
                    timeout_seconds=float(timeout),
                )
            after = _snapshot(
                proc_root=self.proc_root, sys_root=self.sys_root,
                cgroup_path=self.cgroup_path, cpus=evidence_cpus,
            )
            stdout_bytes = stdout_path.read_bytes()
            stderr_bytes = stderr_path.read_bytes()
            stdout_sha256 = _sha256_file(stdout_path)
            stderr_sha256 = _sha256_file(stderr_path)
            if returncode != 0:
                raise RuntimeError(
                    "benchmark command failed with output digests "
                    f"stdout={stdout_sha256}, stderr={stderr_sha256}"
                )
            try:
                stdout = stdout_bytes.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise RuntimeError("benchmark stdout was not UTF-8") from exc
            child = _last_json_line(stdout)
            (
                wall_ns, total_wall_ns, output_digest, input_digest,
                worker_affinities, per_worker_task_clock_ns,
            ) = _normalize_child(
                child, workload_id=str(workload["id"]), mode=mode,
                repetitions=repetitions, warmup_iterations=warmups,
                cpu_set=cpu_set, worker_count=worker_count,
            )
            perf = _parse_perf(perf_path)
            if perf_path.exists() and perf_path.stat().st_size > _OUTPUT_LIMIT_BYTES:
                raise RuntimeError("perf receipt exceeded the 1 MiB output cap")

        elapsed_us = max(1.0, (after["monotonic_ns"] - before["monotonic_ns"]) / 1000.0)
        cgroup_psi_delta = _delta_number(
            before["cgroup_cpu_psi_some_total_us"], after["cgroup_cpu_psi_some_total_us"]
        )
        system_psi_delta = _delta_number(
            before["system_cpu_psi_some_total_us"], after["system_cpu_psi_some_total_us"]
        )
        proc_before, proc_after = before["proc_cpu"], after["proc_cpu"]
        proc_delta = _cpu_delta(proc_before, proc_after, evidence_cpus)
        total_ticks: int | None = None
        busy_ticks: int | None = None
        steal_ticks: int | None = None
        if proc_delta is not None:
            per_cpu = list(proc_delta.values())
            total_ticks = sum(sum(values) for values in per_cpu)
            busy_ticks = sum(
                sum(values) - values[3] - values[4] for values in per_cpu
            )
            steal_ticks = sum(values[7] for values in per_cpu)
        usage_delta = _delta_number(
            None if before["cgroup_cpu_stat"] is None else before[
                "cgroup_cpu_stat"
            ].get("usage_usec"),
            None if after["cgroup_cpu_stat"] is None else after[
                "cgroup_cpu_stat"
            ].get("usage_usec"),
        )
        external_busy = None
        if total_ticks is not None and busy_ticks is not None and total_ticks > 0:
            hz = os.sysconf("SC_CLK_TCK")
            total_usec = total_ticks * 1_000_000.0 / hz
            busy_usec = busy_ticks * 1_000_000.0 / hz
            if usage_delta is not None:
                external_busy = max(0.0, busy_usec - usage_delta) / total_usec
        running_ratio = perf["minimum_running_ratio"]
        throttle_delta = _delta_number(before["throttle_count"], after["throttle_count"])
        irq_delta = _counter_delta(before["irq"], after["irq"], evidence_cpus)
        cycles = _event_value(perf, "cycles")
        task_clock_ms = _event_value(perf, "task-clock")
        effective_frequency_hz = None
        if (
            cycles is not None and task_clock_ms is not None and task_clock_ms > 0.0
            and _event_unit(perf, "task-clock") in {"msec", "milliseconds"}
        ):
            effective_frequency_hz = cycles / (task_clock_ms / 1000.0)
        live_partition = (
            before["cgroup_partition"]
            if before["cgroup_partition"] == after["cgroup_partition"] else None
        )
        live_effective = (
            before["cgroup_effective_cpus"]
            if before["cgroup_effective_cpus"] == after["cgroup_effective_cpus"] else None
        )
        live_exclusive = (
            before["cgroup_exclusive_effective_cpus"]
            if before["cgroup_exclusive_effective_cpus"]
            == after["cgroup_exclusive_effective_cpus"] else None
        )
        temperatures = (
            before["temperature_millicelsius"], after["temperature_millicelsius"]
        )
        temperature_max = (
            max(temperatures) if all(value is not None for value in temperatures)
            else None
        )
        expected_cpuset = self.host_probe.get("cgroup", {}).get("effective_cpus")
        if not isinstance(expected_cpuset, list):
            expected_cpuset = None
        expected_affinities = (
            [list(cpu_set)] if worker_count == 1
            else [[cpu] for cpu in cpu_set]
        )
        metrics = {
            "cpuset_partition": live_partition,
            "cpuset_partition_before": before["cgroup_partition"],
            "cpuset_partition_after": after["cgroup_partition"],
            "effective_cpuset": live_effective,
            "cgroup_effective_cpuset_before": before["cgroup_effective_cpus"],
            "cgroup_effective_cpuset_after": after["cgroup_effective_cpus"],
            "exclusive_effective_cpuset": live_exclusive,
            "cgroup_exclusive_cpuset_before": before[
                "cgroup_exclusive_effective_cpus"
            ],
            "cgroup_exclusive_cpuset_after": after[
                "cgroup_exclusive_effective_cpus"
            ],
            "expected_cpuset": expected_cpuset,
            "selected_cpu_evidence_set": list(cpu_set),
            "cgroup_procs_before": before["cgroup_procs"],
            "cgroup_procs_after": after["cgroup_procs"],
            "expected_cgroup_procs": [os.getpid()],
            "worker_affinities": worker_affinities,
            "expected_worker_affinities": expected_affinities,
            "worker_count": worker_count,
            "per_worker_affinity_verified": True,
            "first_touch": child["first_touch"],
            "thread_ownership": child["thread_ownership"],
            "cpu_migrations": _event_value(perf, "cpu-migrations"),
            "major_faults_after_warmup": child.get("major_faults_after_warmup"),
            "perf_minor_faults_total": _event_value(perf, "minor-faults"),
            "perf_major_faults_total": _event_value(perf, "major-faults"),
            "steal_time_delta": steal_ticks,
            "thermal_throttle_event_delta": throttle_delta,
            "perf_running_over_enabled": running_ratio,
            "perf_required_events_present": perf["all_required_events_present"],
            "perf_exact_event_set": perf["exact_event_set"],
            "cgroup_cpu_psi_some_fraction": (
                None if cgroup_psi_delta is None else cgroup_psi_delta / elapsed_us
            ),
            "system_cpu_psi_some_fraction": (
                None if system_psi_delta is None else system_psi_delta / elapsed_us
            ),
            "external_busy_fraction": external_busy,
            "benchmark_cgroup_cpu_stat_before": before["cgroup_cpu_stat"],
            "benchmark_cgroup_cpu_stat_after": after["cgroup_cpu_stat"],
            "benchmark_cgroup_cpu_stat_delta": _dict_delta(
                before["cgroup_cpu_stat"], after["cgroup_cpu_stat"]
            ),
            "selected_cpu_proc_stat_before": proc_before,
            "selected_cpu_proc_stat_after": proc_after,
            "selected_cpu_proc_stat_delta": proc_delta,
            "involuntary_context_switches": child.get("involuntary_context_switches"),
            "perf_context_switches_total": _event_value(perf, "context-switches"),
            "effective_frequency_hz": effective_frequency_hz,
            "effective_frequency_formula": "cycles/(task-clock-milliseconds/1000)",
            "selected_cpu_frequency_hz_before": before["frequency_hz"],
            "selected_cpu_frequency_hz_after": after["frequency_hz"],
            "temperature_millicelsius_before": temperatures[0],
            "temperature_millicelsius_after": temperatures[1],
            "temperature_max_millicelsius": temperature_max,
            "thermal_throttle_count_before": before["throttle_count"],
            "thermal_throttle_count_after": after["throttle_count"],
            "benchmark_cgroup_cpu_psi_some_total_us_before": before[
                "cgroup_cpu_psi_some_total_us"
            ],
            "benchmark_cgroup_cpu_psi_some_total_us_after": after[
                "cgroup_cpu_psi_some_total_us"
            ],
            "system_cpu_psi_some_total_us_before": before[
                "system_cpu_psi_some_total_us"
            ],
            "system_cpu_psi_some_total_us_after": after[
                "system_cpu_psi_some_total_us"
            ],
            "selected_cpu_irq_before": before["irq"],
            "selected_cpu_irq_after": after["irq"],
            "selected_cpu_irq_delta": irq_delta,
            "perf_events": perf["events"],
            "per_worker_task_clock_ns": per_worker_task_clock_ns,
            "timed_total_wall_time_ns": total_wall_ns,
            "steady_state_duration_seconds": total_wall_ns / 1e9,
            "minimum_duration_seconds": minimum,
        }
        if mode == "sample":
            metrics["sample_duration_below_minimum"] = (
                minimum is not None and total_wall_ns / 1e9 < minimum
            )
        return {
            "wall_time_ns": wall_ns,
            "output_digest": output_digest,
            "input_identity_sha256": input_digest,
            "metrics": metrics,
            "run_contract": {
                "mode": mode,
                "repetitions": repetitions,
                "warmup_iterations": warmups,
                "minimum_duration_seconds": minimum,
            },
            "command_stdout_sha256": stdout_sha256,
            "command_stderr_sha256": stderr_sha256,
        }

    def preflight(
        self, source: ResolvedSource, workload: Mapping[str, Any],
        cpu_set: tuple[int, ...], worker_count: int,
        run_contract: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        if run_contract.get("mode") != "calibrate":
            raise ValueError("preflight requires a calibrate run contract")
        observation = self._collect(
            source, workload, cpu_set, worker_count, run_contract
        )
        reasons = sample_contamination_reasons(observation["metrics"])
        expected = workload.get("output_contract", {}).get("expected_sha256")
        if expected is not None and observation["output_digest"] != expected:
            reasons.append("baseline_output_digest_mismatch")
        if observation["input_identity_sha256"] != workload["input_identity_sha256"]:
            reasons.append("baseline_input_identity_mismatch")
        return {
            "status": "PASS" if not reasons else "FAIL",
            "reasons": sorted(set(reasons)),
            "observation_sha256": sha256_json(observation),
            "output_digest": observation["output_digest"],
            "input_identity_sha256": observation["input_identity_sha256"],
            "single_iteration_wall_time_ns": observation["wall_time_ns"],
            "wall_time_ns": observation["wall_time_ns"],
        }

    def observe(
        self, source: ResolvedSource, workload: Mapping[str, Any],
        cpu_set: tuple[int, ...], worker_count: int,
        run_contract: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        if run_contract.get("mode") != "sample":
            raise ValueError("observe requires a sample run contract")
        return self._collect(
            source, workload, cpu_set, worker_count, run_contract
        )

    def warmup(
        self, source: ResolvedSource, workload: Mapping[str, Any],
        cpu_set: tuple[int, ...], worker_count: int,
        run_contract: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        if run_contract.get("mode") != "warmup":
            raise ValueError("warmup requires a warmup run contract")
        observation = self._collect(
            source, workload, cpu_set, worker_count, run_contract
        )
        reasons = sample_contamination_reasons(observation["metrics"])
        return {
            "status": "PASS" if not reasons else "FAIL",
            "reasons": sorted(set(reasons)),
            "observation_sha256": sha256_json(observation),
            "output_digest": observation["output_digest"],
            "input_identity_sha256": observation["input_identity_sha256"],
        }
