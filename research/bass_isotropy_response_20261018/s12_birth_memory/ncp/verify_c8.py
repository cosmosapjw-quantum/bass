#!/usr/bin/env python3
"""Bounded C8 controls: published bytes, synthetic capacity, two version probes.

Run only after this file and the production C8 modules have been published and
their full Git readback is available. This is not an NCP execution, build,
positive full-launcher run or scientific campaign.
"""
from __future__ import annotations

import argparse
import copy
import json
import os
from pathlib import Path
import sys
import tarfile
import time

sys.dont_write_bytecode = True

import launch
import resources
import runner
import toolchain
from process_control import run_owned


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("repo", "binding", "delivery-binding", "template", "disk-root", "out", "rustc", "cargo"):
        parser.add_argument("--"+name, type=Path, required=True)
    parser.add_argument("--source-commit", required=True, help="Published C8 delivery source commit, not the older Rust source commit.")
    args = parser.parse_args()
    repo, out, disk_root = (getattr(args, name).resolve() for name in ("repo", "out", "disk_root"))
    if not all(path.is_relative_to(disk_root) for path in (repo, out)) or out.is_relative_to(repo):
        raise ValueError("VERIFY_OUTPUT_MUST_BE_SEPARATE_AND_WITHIN_MEASURED_DISK_ROOT")
    out.mkdir(parents=True, exist_ok=False)
    checks, processes = [], []
    record = {"schema": "BASS_S12_C8_BOUNDED_VERIFICATION_V1", "started_utc": runner.utc(),
              "status": "RUNNING", "delivery_source_commit": args.source_commit,
              "NCP_executions": 0, "builds": 0, "scientific_histories": 0, "old_campaign_replays": 0,
              "network_requests": 0, "production_positive_full_CLI_claim": False,
              "synthetic_capacity_is_not_hardware_evidence": True}
    runner.atomic_json(out/"STARTED.json", record)

    def check(name, passed, **details):
        checks.append({"name": name, "pass": bool(passed), **details})
        if not passed:
            raise AssertionError(name)

    def reject(name, action, message=None):
        try:
            action()
        except (ValueError, RuntimeError) as error:
            check(name, message is None or message in str(error), rejected_type=type(error).__name__, rejection=str(error))
        else:
            check(name, False, rejection="unexpected acceptance")

    try:
        science, science_files, science_sha = launch.binding(args.binding.resolve(), repo)
        delivery, delivery_files, delivery_sha = launch.binding(args.delivery_binding.resolve(), repo)
        check("two_published_source_bindings", delivery["source_commit"] == args.source_commit and science["source_commit"] != delivery["source_commit"],
              scientific_source_commit=science["source_commit"], scientific_files=len(science_files), delivery_files=len(delivery_files))
        sources = dict(science_files)
        for name, digest in delivery_files.items():
            if name in sources and sources[name] != digest:
                raise ValueError("BINDING_CONFLICT")
            sources[name] = digest
        for module in (sys.modules[__name__], launch, toolchain, runner, resources, sys.modules["bundle"], sys.modules["process_control"]):
            launch.bound_file(Path(module.__file__), repo, sources)
        launch.bound_file(args.template, repo, delivery_files)
        template = json.loads(args.template.read_bytes())
        jobs = template["manifest"]["jobs"]
        check("explicit_production_scope", template["admissible_profiles"] == ["ncp"] and len(jobs) == 17
              and template["manifest"]["allow_completed_campaign_replay"] is False,
              job_count=len(jobs), old_campaign_replay_allowed=False)
        input_map = {}
        for job in jobs:
            for name, digest in job["input_files"].items():
                if name in input_map and input_map[name] != digest:
                    raise ValueError("CONFLICTING_JOB_INPUT")
                input_map[name] = digest
        runner.validate_hashes(repo, input_map)
        check("all_fixed_job_inputs_bound", len(input_map) == 82 and all(sources.get(name) == digest for name, digest in input_map.items()),
              unique_job_inputs=len(input_map), note="Includes fixed scientific preregistration and SCIENCE_BINDING; distinct from the earlier97-payload publication checkpoint.")
        fixed_root = Path(launch.__file__).resolve().parent/"inputs"
        fixed_files = sorted(p for p in fixed_root.rglob("*") if p.is_file())
        for path in fixed_files:
            launch.bound_file(path, repo, sources)
        check("fixed_data_cardinality", len(fixed_files) == 81 and len(list((fixed_root/"histories").glob("*.json"))) == 14
              and len(list((fixed_root/"core_packs").glob("pack*.txt"))) == 64,
              data_files=len(fixed_files), extended_histories=14, independent_core_packs=64)

        executables = toolchain.probe(args.rustc, args.cargo, out/"actual_version_probes", time.monotonic()+50)
        selected = {"status": "PASS_EXISTING_VERSION_HASH_IDENTIFIED", "executables": executables,
                    "archive_identity_claim": False, "existing_toolchain_modified": False}
        processes.extend(executables[name]["probe_process"] for name in ("rustc", "cargo"))
        check("actual_two_version_probes", len(processes) == 2 and all(x["status"] == "EXITED" and x["exit_code"] == 0 for x in processes),
              rustc_sha256=executables["rustc"]["sha256"], cargo_sha256=executables["cargo"]["sha256"], pinned_version=toolchain.VERSION)
        check("exact_existing_toolchain_reuse", toolchain.verify_selected(selected, out/"unused_cache", time.monotonic()+30) == selected,
              additional_processes=0)
        tampered = copy.deepcopy(selected)
        (out/"tampered_rustc").write_bytes(b"deliberately different verification fixture\n")
        tampered["executables"]["rustc"]["path"] = str(out/"tampered_rustc")
        reject("changed_toolchain_bytes_rejected", lambda: toolchain.verify_selected(tampered, out/"unused_cache", time.monotonic()+30), "SEALED_TOOLCHAIN_EXECUTABLE_CHANGED")

        fixture = {"fixture_kind": "EXPLICIT_SYNTHETIC_NOT_OBSERVED_HARDWARE", "profile": "ncp", "configured": resources.PROFILES["ncp"],
            "cpu_cap": 64, "ram_cap_bytes": 128 << 30, "ram_available_bytes": 128 << 30,
            "busy_cpus_estimate": 0.0, "own_busy_cpus_estimate": 0.0, "own_process_groups": {},
            "affinity": list(range(64)), "cgroup_cpu_quota_cores": [64.0], "cgroup_memory_caps": [128 << 30],
            "disk_allocated_bytes": 0, "disk_free_bytes": 4 << 30}
        fixture_work = out/"SYNTHETIC_FIXTURE_ONLY"
        paths = {"science": args.binding.resolve(), "delivery": args.delivery_binding.resolve(), "template": args.template.resolve(),
                 "job_manifest": fixture_work/"JOB_MANIFEST.json", "repo": repo, "work": fixture_work, "disk_root": disk_root}
        hashes = {"science": science_sha, "delivery": delivery_sha, "template": runner.digest_file(args.template)}
        def resolved(observation):
            return launch.resolve(template, sources, science, delivery, hashes, selected, paths, observation, "ncp")
        idle = resolved(fixture)
        check("synthetic_idle64_resolution", idle["launch_binding"]["selected_case_workers"] == 64,
              actual_hardware_claim=False)
        quota = copy.deepcopy(fixture); quota.update(cpu_cap=12, cgroup_cpu_quota_cores=[12.5])
        check("synthetic_quota_cap_resolution", resolved(quota)["launch_binding"]["selected_case_workers"] == 12,
              fixture_cpu_cap_is_floor_of_quota=True)
        busy = copy.deepcopy(fixture); busy["busy_cpus_estimate"] = 9.25
        check("synthetic_owner_load_subtracted", resolved(busy)["launch_binding"]["selected_case_workers"] == 54)
        memory = copy.deepcopy(fixture)
        memory["ram_available_bytes"] = template["manifest"]["reserve_ram_bytes"] + template["case_parallel"]["fixed_ram_bytes"] + 3*template["case_parallel"]["ram_per_worker_bytes"]
        check("synthetic_memory_width_reduction", resolved(memory)["launch_binding"]["selected_case_workers"] == 3)
        empty = copy.deepcopy(fixture); empty["busy_cpus_estimate"] = 64.0
        reject("synthetic_zero_available_refused", lambda: resolved(empty), "NO_RESOURCE_AVAILABLE")
        # The completed-job width is reconstructed from its saved observation;
        # hypothetical later load is only an admission input, never a new width.
        reconstruction = resolved(idle["launch_binding"]["resource_observation"])
        cap_now = runner.capacity(idle, busy)
        parallel = next(j for j in idle["jobs"] if j["id"] == template["case_parallel"]["job_id"])
        check("frozen_manifest_reconstruction_and_defer", runner.canonical(idle) == runner.canonical(reconstruction)
              and not runner.fits(parallel, cap_now), saved_width=parallel["cpus"], later_available_cpus=cap_now["cpus"],
              full_positive_CLI_resume_executed=False)
        check("aggregate_uses_stable_manifest_token", any(str(paths["job_manifest"]) in j["argv"] for j in idle["jobs"] if j["id"] == "ensemble_assessment"))
        runner.atomic_json(out/"SYNTHETIC_RESOLVED_MANIFEST.json", idle)
        _, _ = runner.load_manifest(out/"SYNTHETIC_RESOLVED_MANIFEST.json", repo)
        check("resolved_fixed_DAG_validated", True, scientific_commands_executed=0)

        corrupted_binding = copy.deepcopy(science)
        corrupted_binding["files"][0]["sha256"] = "0"*64
        runner.atomic_json(out/"NEGATIVE_CORRUPTED_BINDING.json", corrupted_binding)
        reject("source_hash_mismatch_rejected", lambda: launch.binding(out/"NEGATIVE_CORRUPTED_BINDING.json", repo), "BOUND_SOURCE_BYTES_CHANGED")
        bad_member = tarfile.TarInfo(toolchain.ARCHIVE_ROOT+"/rustc/../../outside")
        reject("malformed_archive_path_rejected", lambda: toolchain.selected_path(bad_member), "UNSAFE_TOOLCHAIN_ARCHIVE_PATH")

        forbidden_work = out/"forbidden_profile_work"
        argv = [str(Path(sys.executable).resolve()), str(Path(launch.__file__).resolve()),
            "--template", str(args.template.resolve()), "--binding", str(args.binding.resolve()),
            "--delivery-binding", str(args.delivery_binding.resolve()), "--repo", str(repo),
            "--work-dir", str(forbidden_work), "--disk-root", str(disk_root), "--profile", "sandbox"]
        execution = run_owned(argv, stdout_path=out/"forbidden_profile.stdout", stderr_path=out/"forbidden_profile.stderr",
            receipt_path=out/"FORBIDDEN_PROFILE_PROCESS.json", timeout_s=60,
            env={**os.environ, **runner.THREAD_ENV, "PYTHONDONTWRITEBYTECODE": "1"}, as_bytes=512 << 20, file_bytes=4 << 20)
        processes.append(execution)
        launch_returns = list((forbidden_work/"runs/launch_records").glob("*/RETURN_LAUNCH.json"))
        rejected = json.loads(launch_returns[0].read_bytes()) if len(launch_returns) == 1 else {}
        check("actual_sandbox_CLI_refused_before_bootstrap_or_science", execution["status"] == "EXITED" and execution["exit_code"] == 2
              and rejected.get("error", {}).get("message") == "TEMPLATE_PROFILE_EXECUTION_FORBIDDEN"
              and not (forbidden_work/"JOB_MANIFEST.json").exists() and not list(forbidden_work.rglob("TOOLCHAIN.json"))
              and not (forbidden_work/"toolchains").exists(), additional_version_probes=0, builds=0, scientific_children=0)
        for name, digest in sources.items():
            if runner.digest_file(repo/name) != digest:
                raise ValueError("PUBLISHED_SOURCE_CHANGED_DURING_BOUNDED_VERIFY")
        check("published_bytes_unchanged_after", True, verified_files=len(sources))
        record["status"] = "PASS_BOUNDED_C8_CONTROLS"
    except BaseException as error:
        record.update(status="FAIL_OR_INCOMPLETE", error={"type": type(error).__name__, "message": str(error)})
    record.update(finished_utc=runner.utc(), checks=checks, passed=sum(c["pass"] for c in checks), check_count=len(checks),
                  actual_process_records=processes, actual_process_count=len(processes),
                  intended_version_probe_processes=2, intended_forbidden_profile_CLI_processes=1)
    runner.atomic_json(out/"RETURN_C8_VERIFICATION.json", record)
    print(json.dumps({"status": record["status"], "passed": record["passed"], "check_count": len(checks), "receipt": str(out/"RETURN_C8_VERIFICATION.json")}, ensure_ascii=False))
    return 0 if record["status"] == "PASS_BOUNDED_C8_CONTROLS" else 2


if __name__ == "__main__":
    sys.exit(main())
