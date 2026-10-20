#!/usr/bin/env python3
"""Resolve and run only the published, fixed S12 NCP job template.

The scientific source and C8 delivery source may be different commits. Exact
file identities from both bindings are required; a current checkout is never
silently reclassified as the old scientific source. Toolchain preparation,
fixed-job execution, exact-PASS resume and a local return bundle are automatic.
"""
from __future__ import annotations

import argparse
import copy
import datetime as dt
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import sys
import time
import uuid

import bundle
import resources
import runner
import toolchain


def binding(path, repo):
    raw = path.read_bytes()
    data = json.loads(raw)
    if data.get("git_readback_pass") is not True or not re.fullmatch(r"[0-9a-f]{40}", data.get("source_commit", "")) or not re.fullmatch(r"[0-9a-f]{40}", data.get("source_tree", "")):
        raise ValueError("PUBLISHED_SOURCE_BINDING_REQUIRED")
    rows, identities = data.get("files"), {}
    if not isinstance(rows, list) or not rows:
        raise ValueError("EMPTY_SOURCE_BINDING")
    for row in rows:
        name = row["path"]
        if name in identities or row.get("pass", True) is not True:
            raise ValueError("DUPLICATE_OR_FAILED_SOURCE_BINDING")
        payload = runner.under(repo, name).read_bytes()
        digest = hashlib.sha256(payload).hexdigest()
        blob = hashlib.sha1(b"blob " + str(len(payload)).encode() + bytes([0]) + payload).hexdigest()
        if len(payload) != row["bytes"] or digest != row["sha256"] or blob != row["git_blob"]:
            raise ValueError("BOUND_SOURCE_BYTES_CHANGED:" + name)
        identities[name] = digest
    return data, identities, hashlib.sha256(raw).hexdigest()


def bound_file(path, repo, identities):
    path = path.resolve()
    if not path.is_relative_to(repo):
        raise ValueError("LAUNCH_SOURCE_OUTSIDE_REPO")
    name = path.relative_to(repo).as_posix()
    if name not in identities or runner.digest_file(path) != identities[name]:
        raise ValueError("LAUNCH_SOURCE_NOT_PUBLISHED:" + name)
    return name


def resolve(template, source_files, science, delivery, hashes, selected, paths, observation):
    """Resolve paths and resource width only; all scientific bytes stay fixed."""
    manifest = copy.deepcopy(template["manifest"])
    for name, digest in manifest.get("source_files", {}).items():
        if source_files.get(name) != digest:
            raise ValueError("TEMPLATE_SOURCE_OUTSIDE_PUBLISHED_BINDINGS:" + name)
    manifest["source_files"] = source_files
    for key, default in (("reserve_cpus", 0), ("reserve_ram_bytes", 1 << 30)):
        manifest.setdefault(key, default)
        if type(manifest[key]) is not int or manifest[key] < 0:
            raise ValueError("INVALID_RESOURCE_RESERVATION")
    cap = runner.capacity(manifest, observation)
    spec = template["case_parallel"]
    for name in ("max_workers", "case_count", "ram_per_worker_bytes"):
        if type(spec.get(name)) is not int or spec[name] < 1:
            raise ValueError("INVALID_CASE_PARALLEL_RESOURCE:" + name)
    if spec["max_workers"] > 64 or type(spec.get("fixed_ram_bytes")) is not int or spec["fixed_ram_bytes"] < 0:
        raise ValueError("CASE_PARALLEL_PROFILE_BOUND")
    width = min(64, spec["max_workers"], spec["case_count"], observation["configured"]["workers"], cap["cpus"],
                max(0, (cap["ram_bytes"] - spec["fixed_ram_bytes"]) // spec["ram_per_worker_bytes"]))
    if width < 1:
        raise RuntimeError("NO_RESOURCE_AVAILABLE_FOR_ONE_FIXED_CASE")
    manifest["max_workers"] = min(manifest.get("max_workers", 64), observation["configured"]["workers"], observation["cpu_cap"])
    tokens = {"@RUSTC@": selected["rustc"]["path"], "@CARGO@": selected["cargo"]["path"],
              "@SOURCE_BINDING@": str(paths["science"]), "@SOURCE_COMMIT@": science["source_commit"],
              "@PYTHON@": str(Path(sys.executable).resolve()), "@WORKERS@": str(width)}
    fixed_environment = {"BASS_S12_SCIENTIFIC_SOURCE_COMMIT": science["source_commit"],
                         "BASS_S12_SCIENCE_BINDING_SHA256": hashes["science"],
                         "BASS_S12_DELIVERY_SOURCE_COMMIT": delivery["source_commit"],
                         "BASS_S12_DELIVERY_BINDING_SHA256": hashes["delivery"],
                         "BASS_S12_RUSTC_SHA256": selected["rustc"]["sha256"],
                         "BASS_S12_CARGO_SHA256": selected["cargo"]["sha256"]}
    matched = 0
    for job in manifest["jobs"]:
        for name, digest in job.get("input_files", {}).items():
            if source_files.get(name) != digest:
                raise ValueError("JOB_INPUT_OUTSIDE_PUBLISHED_BINDINGS:" + name)
        is_parallel = job["id"] == spec["job_id"]
        if is_parallel:
            matched += 1
            if job["kind"] != "matched_accuracy_performance":
                raise ValueError("CASE_PARALLEL_JOB_KIND")
            job["cpus"] = width
            job["ram_bytes"] = spec["fixed_ram_bytes"] + width * spec["ram_per_worker_bytes"]
        argv = []
        for arg in job["argv"]:
            if "@WORKERS@" in arg and not is_parallel:
                raise ValueError("WORKER_TOKEN_OUTSIDE_CASE_PARALLEL_JOB")
            for token, value in tokens.items():
                arg = arg.replace(token, value)
            if re.search(r"@[A-Z_]+@", arg):
                raise ValueError("UNRESOLVED_TEMPLATE_TOKEN")
            argv.append(arg)
        job["argv"] = argv
        env = job.setdefault("env", {})
        for name, value in fixed_environment.items():
            if name in env and env[name] != value:
                raise ValueError("CONFLICTING_BINDING_ENVIRONMENT")
            env[name] = value
    if matched != 1:
        raise ValueError("EXACTLY_ONE_CASE_PARALLEL_JOB_REQUIRED")
    manifest["launch_binding"] = {"scientific_source_commit": science["source_commit"],
        "scientific_source_tree": science["source_tree"], "delivery_source_commit": delivery["source_commit"],
        "delivery_source_tree": delivery["source_tree"], "input_file_hashes": hashes,
        "toolchain_executables": selected, "selected_case_workers": width,
        "resource_observation": observation,
        "fixed_scope": "Published job list and inputs only; no old campaign, no angular-reduction reorder, no weight/tolerance changes."}
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("template", "binding", "delivery-binding", "repo", "work-dir", "disk-root"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--profile", choices=tuple(resources.PROFILES), default="ncp")
    parser.add_argument("--toolchain-archive", type=Path)
    parser.add_argument("--rustc")
    parser.add_argument("--cargo")
    parser.add_argument("--preflight-only", action="store_true",
                        help="Prepare/identify the exact toolchain and resolved manifest; run no scientific or build job.")
    args = parser.parse_args()
    repo, work, disk_root = (getattr(args, n).resolve() for n in ("repo", "work_dir", "disk_root"))
    if not repo.is_dir() or not disk_root.is_dir() or not all(p.is_relative_to(disk_root) for p in (repo, work)) or repo == work or work.is_relative_to(repo):
        raise ValueError("REPO_AND_SEPARATE_WORK_MUST_LIE_UNDER_MEASURED_DISK_ROOT")
    work.mkdir(parents=True, exist_ok=True)
    with (work/".c8-launch.lock").open("a+b") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S") + "_" + uuid.uuid4().hex[:10]
        record_root = work/"runs/launch_records"/stamp
        record = {"schema": "BASS_S12_C8_LAUNCH_RECEIPT_V1", "started_utc": runner.utc(),
                  "status": "STARTED", "profile": args.profile,
                  "old_campaign_executions": 0, "old_owner_jobs_killed": 0,
                  "remote_provider_uploads": 0, "source_edits": 0}
        runner.atomic_json(record_root/"LAUNCH_STARTED.json", record)
        old_handlers = {s: signal.getsignal(s) for s in (signal.SIGTERM, signal.SIGINT)}
        def interrupted(signum, frame):
            raise SystemExit(128 + signum)
        for signum in old_handlers:
            signal.signal(signum, interrupted)
        manifest_path = None
        exit_code = 2
        try:
            paths = {"science": args.binding.resolve(), "delivery": args.delivery_binding.resolve(), "template": args.template.resolve()}
            science, science_files, science_sha = binding(paths["science"], repo)
            delivery, delivery_files, delivery_sha = binding(paths["delivery"], repo)
            sources = dict(science_files)
            for name, digest in delivery_files.items():
                if name in sources and sources[name] != digest:
                    raise ValueError("CONFLICTING_SCIENTIFIC_DELIVERY_BINDINGS")
                sources[name] = digest
            bound_file(paths["template"], repo, delivery_files)
            for module in (sys.modules[__name__], runner, resources, bundle, toolchain, sys.modules["process_control"]):
                bound_file(Path(module.__file__), repo, sources)
            template = json.loads(paths["template"].read_bytes())
            if template.get("schema") != "BASS_S12_NCP_JOB_TEMPLATE_V1":
                raise ValueError("FIXED_S12_TEMPLATE_SCHEMA_REQUIRED")
            spec = template.get("toolchain", {})
            if spec.get("rustc_token") != "@RUSTC@" or spec.get("cargo_token") != "@CARGO@":
                raise ValueError("EXPLICIT_TOOLCHAIN_TOKENS_REQUIRED")
            hashes = {"science": science_sha, "delivery": delivery_sha, "template": runner.digest_file(paths["template"])}
            for name, path in paths.items():
                with (record_root/(name.upper()+"_INPUT.json")).open("xb") as stream:
                    stream.write(path.read_bytes()); stream.flush(); os.fsync(stream.fileno())
            before = resources.snapshot(args.profile, disk_root)
            reserve = {"reserve_cpus": template["manifest"].get("reserve_cpus", 0),
                       "reserve_ram_bytes": template["manifest"].get("reserve_ram_bytes", 1 << 30)}
            cap = runner.capacity(reserve, before)
            if cap["cpus"] < 1 or cap["ram_bytes"] < 2 << 30:
                raise RuntimeError("PRIVATE_TOOLCHAIN_PREFLIGHT_RESOURCE_UNAVAILABLE")
            record["bootstrap_preflight"] = before
            affinity = os.sched_getaffinity(0)
            old_alarm = signal.getsignal(signal.SIGALRM)
            if signal.getitimer(signal.ITIMER_REAL) != (0.0, 0.0):
                raise RuntimeError("EXISTING_CALLER_ALARM_MUST_NOT_BE_REPLACED")
            def bootstrap_timeout(signum, frame):
                raise TimeoutError("PRIVATE_TOOLCHAIN_1770_SECOND_DEADLINE")
            try:
                os.sched_setaffinity(0, sorted(affinity)[:min(2, cap["cpus"])])
                signal.signal(signal.SIGALRM, bootstrap_timeout)
                signal.setitimer(signal.ITIMER_REAL, 1770.0)
                selected = toolchain.ensure_toolchain(work/"toolchains", record_root, disk_root, time.monotonic()+1770.0,
                    archive_path=args.toolchain_archive, existing_rustc=args.rustc, existing_cargo=args.cargo)
            finally:
                signal.setitimer(signal.ITIMER_REAL, 0.0)
                signal.signal(signal.SIGALRM, old_alarm)
                os.sched_setaffinity(0, affinity)
            if "ready_receipt" in selected:
                ready = Path(selected["ready_receipt"])
                if runner.digest_file(ready) != selected["ready_receipt_sha256"]:
                    raise ValueError("TOOLCHAIN_READY_RECEIPT_CHANGED")
                with (record_root/"TOOLCHAIN_READY.json").open("xb") as stream:
                    stream.write(ready.read_bytes()); stream.flush(); os.fsync(stream.fileno())
            observation = resources.snapshot(args.profile, disk_root)
            manifest = resolve(template, sources, science, delivery, hashes, selected["executables"], paths, observation)
            manifest_path = record_root/"RESOLVED_MANIFEST.json"
            runner.atomic_json(manifest_path, manifest)
            manifest, manifest_sha = runner.load_manifest(manifest_path, repo)
            preflight = runner.preflight(manifest, args.profile, disk_root)
            runner.atomic_json(record_root/"RESOLVED_PREFLIGHT.json", preflight)
            record.update(scientific_source_commit=science["source_commit"], delivery_source_commit=delivery["source_commit"],
                input_hashes=hashes, resolved_manifest_sha256=manifest_sha, selected_case_workers=manifest["launch_binding"]["selected_case_workers"],
                toolchain=selected, toolchain_bootstrap_max_seconds=1770, job_timeout_cap_seconds=1800)
            if args.preflight_only:
                record["status"] = "READY_NOT_EXECUTED" if preflight["can_start"] else "NOT_READY_RESOURCE_UNAVAILABLE"
                exit_code = 0 if preflight["can_start"] else 2
            else:
                result = runner.execute(manifest, manifest_sha, repo, work/"runs", disk_root, args.profile)
                record["execution"] = result
                record["status"] = result["status"]
                exit_code = 0 if result["status"] == "PASS" else 2
            for executable in selected["executables"].values():
                if runner.digest_file(executable["path"]) != executable["sha256"]:
                    raise RuntimeError("TOOLCHAIN_CHANGED_DURING_INVOCATION")
        except BaseException as error:
            exit_code = error.code if isinstance(error, SystemExit) and isinstance(error.code, int) else 2
            record.update(status="FAILED_OR_INTERRUPTED", error={"type": type(error).__name__, "message": str(error)})
        finally:
            for signum, handler in old_handlers.items():
                signal.signal(signum, handler)
            record.update(finished_utc=runner.utc(), exit_code=exit_code)
            runner.atomic_json(record_root/"RETURN_LAUNCH.json", record)
        bundle_status = "NOT_CREATED_NO_VALID_RESOLVED_MANIFEST"
        if manifest_path is not None and manifest_path.is_file():
            try:
                archive = work/"returns"/("BASS_S12_NCP_RETURN_"+stamp+".zip")
                packaged = bundle.create(manifest_path, repo, work/"runs", archive, disk_root)
                runner.atomic_json(record_root/"RETURN_BUNDLE.json", {"archive": str(archive), **packaged})
                bundle_status = packaged["status"]
            except Exception as error:
                runner.atomic_json(record_root/"BUNDLE_FAILED.json", {"status": "FAILED", "error": str(error), "scientific_status_unchanged": True})
                exit_code = exit_code or 2
                bundle_status = "FAILED_LOCAL_PACKAGING"
        print(json.dumps({"status": record["status"], "exit_code": exit_code, "bundle_status": bundle_status,
                          "receipt": str(record_root/"RETURN_LAUNCH.json")}, ensure_ascii=False))
        return exit_code


if __name__ == "__main__":
    sys.exit(main())
