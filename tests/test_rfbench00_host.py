from __future__ import annotations

import json
from pathlib import Path
import os

from benchmarks.rfbench.collector import _throttle, _throttle_delta
from benchmarks.rfbench.host import ClaimLevel, parse_cpu_list, probe_host


def _put(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def _controlled_roots(
    tmp_path: Path, *, throttle: bool = True, package_throttle: bool = True,
) -> tuple[Path, Path]:
    proc = tmp_path / "proc"
    sys = tmp_path / "sys"
    cgroup = sys / "fs/cgroup/bench"
    _put(sys / "fs/cgroup/cgroup.controllers", "cpuset cpu\n")
    _put(proc / "self/cgroup", "0::/bench\n")
    _put(cgroup / "cgroup.controllers", "cpuset cpu\n")
    _put(cgroup / "cgroup.subtree_control", "\n")
    _put(cgroup / "cpuset.cpus.effective", "0-23\n")
    _put(cgroup / "cpuset.cpus.exclusive.effective", "0-23\n")
    _put(cgroup / "cpuset.cpus.partition", "isolated\n")
    _put(cgroup / "cpu.stat", "usage_usec 1\n")
    _put(cgroup / "cpu.pressure", "some avg10=0.00 avg60=0.00 avg300=0.00 total=0\n")
    _put(cgroup / "cgroup.procs", f"{os.getpid()}\n")
    _put(proc / "sys/kernel/nmi_watchdog", "1\n")
    _put(sys / "bus/event_source/devices/cpu/caps/num_counters", "8\n")
    _put(sys / "bus/event_source/devices/cpu/caps/num_counters_fixed", "3\n")
    _put(sys / "devices/system/cpu/smt/active", "1\n")
    _put(sys / "devices/system/cpu/smt/control", "on\n")
    _put(sys / "devices/system/cpu/isolated", "0-23\n")
    _put(sys / "devices/system/cpu/nohz_full", "0-23\n")
    _put(proc / "stat", "cpu 1 0 1 100 0 0 0 0\n")
    _put(proc / "interrupts", "           CPU0\n")
    _put(proc / "pressure/cpu", "some avg10=0.00 avg60=0.00 avg300=0.00 total=0\n")
    for cpu in range(24):
        root = sys / f"devices/system/cpu/cpu{cpu}"
        _put(root / "topology/physical_package_id", "0\n")
        _put(root / "topology/core_id", f"{cpu % 12}\n")
        _put(root / "topology/thread_siblings_list", f"{cpu % 12},{cpu % 12 + 12}\n")
        _put(root / "cache/index3/shared_cpu_list", "0-23\n")
        _put(root / "cpufreq/scaling_cur_freq", "4200000\n")
        if throttle and cpu < 12:
            _put(root / "thermal_throttle/core_throttle_count", "0\n")
        if throttle and package_throttle and cpu == 0:
            _put(root / "thermal_throttle/package_throttle_count", "0\n")
    _put(sys / "class/hwmon/hwmon0/temp1_input", "55000\n")
    return proc, sys


def _perf_ok(_: str | None) -> dict[str, object]:
    return {
        "available": True,
        "exit_code": 0,
        "required_events_complete": True,
        "minimum_running_ratio": 1.0,
    }


def test_linux_cpu_list_parser_is_strict_and_canonical():
    assert parse_cpu_list("0-2,4,2") == (0, 1, 2, 4)
    assert parse_cpu_list("") == ()
    try:
        parse_cpu_list("3-1")
    except ValueError as exc:
        assert "descending" in str(exc)
    else:
        raise AssertionError("descending CPU ranges must fail")


def test_controlled_probe_derives_one_thread_per_physical_core(tmp_path):
    proc, sys = _controlled_roots(tmp_path)
    report = probe_host(
        proc_root=proc, sys_root=sys, affinity=range(24), perf_probe=_perf_ok,
    )
    assert report["claim_level"] == ClaimLevel.CONTROLLED_SHARED_PAIRED
    assert report["authority_eligible"] is True
    assert report["strata"]["strict_1t"] == [0]
    assert report["strata"]["strict_1t_smt_siblings"] == [0, 12]
    assert report["strata"]["physical_12t"] == list(range(12))
    assert report["strata"]["physical_12t_smt_siblings"] == list(range(24))
    assert report["privileged_mutation_performed"] is False
    receipt = report.pop("receipt_sha256")
    canonical = json.dumps(report, sort_keys=True, separators=(",", ":"),
                           ensure_ascii=True, allow_nan=False).encode("ascii")
    import hashlib
    assert receipt == hashlib.sha256(canonical).hexdigest()


def test_dedicated_level_requires_explicit_attestation(tmp_path):
    proc, sys = _controlled_roots(tmp_path)
    report = probe_host(
        proc_root=proc, sys_root=sys, affinity=range(24), perf_probe=_perf_ok,
        dedicated_host_attestation={
            "attestation_id": "synthetic-dedicated-fixture",
            "bare_metal": True,
            "no_unrelated_workloads": True,
            "zero_vm_steal_observable": True,
            "topology_and_thermal_controls": True,
        },
    )
    assert report["claim_level"] == ClaimLevel.DEDICATED_BARE_METAL


def test_boolean_like_or_incomplete_dedicated_claim_never_promotes(tmp_path):
    proc, sys = _controlled_roots(tmp_path)
    report = probe_host(
        proc_root=proc, sys_root=sys, affinity=range(24), perf_probe=_perf_ok,
        dedicated_host_attestation={"attestation_id": "incomplete"},
    )
    assert report["claim_level"] == ClaimLevel.CONTROLLED_SHARED_PAIRED
    assert report["dedicated_host_attestation_valid"] is False


def test_missing_throttle_signal_forces_exploratory_only(tmp_path):
    proc, sys = _controlled_roots(tmp_path, throttle=False)
    report = probe_host(
        proc_root=proc, sys_root=sys, affinity=range(24), perf_probe=_perf_ok,
    )
    assert report["claim_level"] == ClaimLevel.EXPLORATORY_ONLY
    assert report["acceptance_claim_allowed"] is False
    assert "throttle_counter_unavailable" in report["blockers"]


def test_core_only_throttle_signal_cannot_authorize_a_controlled_claim(tmp_path):
    proc, sys = _controlled_roots(tmp_path, package_throttle=False)
    report = probe_host(
        proc_root=proc, sys_root=sys, affinity=range(24), perf_probe=_perf_ok,
    )
    assert report["claim_level"] == ClaimLevel.EXPLORATORY_ONLY
    assert report["interfaces"]["throttling"] == {
        "available": False,
        "core_counter_complete": True,
        "package_counter_complete": False,
        "core_counter_count": 12,
        "package_counter_count": 0,
    }
    assert "throttle_counter_unavailable" in report["blockers"]


def test_collector_requires_complete_core_and_package_throttle_receipts(tmp_path):
    proc, sys = _controlled_roots(tmp_path)
    report = probe_host(
        proc_root=proc, sys_root=sys, affinity=range(24), perf_probe=_perf_ok,
    )
    before = _throttle(sys, {0, 12}, report["topology"])
    assert before == {"core": {"0:0": 0}, "package": {"0": 0}}
    after = {"core": {"0:0": 2}, "package": {"0": 3}}
    assert _throttle_delta(before, after) == {
        "core": {"0:0": 2}, "package": {"0": 3}, "total": 5,
    }

    package_path = (
        sys / "devices/system/cpu/cpu0/thermal_throttle/package_throttle_count"
    )
    package_path.unlink()
    assert _throttle(sys, {0, 12}, report["topology"]) is None


def test_affinity_without_delegated_cpuset_is_never_authority(tmp_path):
    proc, sys = _controlled_roots(tmp_path)
    cgroup = sys / "fs/cgroup/bench"
    (cgroup / "cpuset.cpus.exclusive.effective").unlink()
    (cgroup / "cpuset.cpus.partition").write_text("member\n", encoding="utf-8")
    report = probe_host(
        proc_root=proc, sys_root=sys, affinity=range(24), perf_probe=_perf_ok,
    )
    assert report["claim_level"] == ClaimLevel.EXPLORATORY_ONLY
    assert "cpuset_partition_not_isolated" in report["blockers"]
    assert "exclusive_effective_cpuset_unproven" in report["blockers"]
