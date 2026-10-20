#!/usr/bin/env python3
"""Aggregate the fourteen fixed NEW S12 extended histories from saved evidence.

This stdlib-only observer runs no solver, projector, compiler or subprocess. It
checks the source-bound launcher/build/process chain, re-evaluates each stored
history with the hash-verified frozen stdlib assessor, then applies the existing
ensemble gates. Omission controls remain controls, never full physics passes.
The outer job must depend on precisely the fourteen supplied history jobs.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import re
import struct
import sys
import uuid


UNIT = "research/bass_isotropy_response_20261018/s12_birth_memory/"
SOURCE = "f4cd0d53760783e6a58c3b0a98c64311ca489d28"
TREE = "a9048818707ef3f446528631c3b5d6c8171116cc"
ASSESSOR_SHA = "a84ad1884ce382d3ca0a12d155a7b44668dc27f5c12d5564631bb93521e786f3"
UPSTREAM = "a21d573980f66fe02891bd216153443b5352f921"
PROJECTOR_SHA = "1f937f16dcb5a7dbdce92a66881d45276b67b202c56bdc232c1d281ad7fc6fcb"
OWNER = "0e25846433170d0f420c4cda44a0bedbf02cd177"
THREAD_ENV = {key: "1" for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
    "RAYON_NUM_THREADS", "BLIS_NUM_THREADS")}
STEPS = (1e-4, 5e-5, 2.5e-5)
CONTROLS = ("omit_birth_memory", "omit_mu_b", "omit_alpha_b")
BASE_IDS = ("p24_y0_full", "gl_y0_full", "gl_b0_gauge", "p24_y0_mf6", "p24_y0_baseline")
FD_IDS = tuple("fd_" + format(h, ".1e").replace(".", "p").replace("-", "m")
               + "_" + sign for h in STEPS for sign in ("plus", "minus"))
CASE_IDS = BASE_IDS + FD_IDS + CONTROLS
FIXED_CONFIG = {"k": 16, "n": 64, "b0": 0.65, "y0": 0.025,
    "donor0": 0.8, "old_isotropic": 0.015, "old_anisotropic": 0.01,
    "cosmological_constant": 0.7, "decay_lambda": 0.9, "birth_end": 0.8, "x_end": 1.2}
GATES = {"MF6_clock7_state6_scaled_gate": 1e-9,
    "additional_driver_state6_scaled_gate": 1e-9,
    "baseline_fused_history_state6_scaled_gate": 2e-13,
    "Richardson_h_b_y_max_absolute_gate": 1e-8,
    "raw_fine_FD_scaled_gate": 1e-6,
    "primal_and_tangent_constraints_event_gates": 1e-11,
    "source_frame_gauge_absolute_gate": 1e-11}
OUTPUTS = ("RETURN.json", "CHECKS.json", "EVIDENCE.json", "CASE_ASSESSMENTS.json",
           "FD_RICHARDSON.json", "CROSS_DRIVER.json", "OMISSION_CONTROLS.json")
HISTORY_ARTIFACTS = {"INPUT.json", "HISTORY.json", "history.stdout", "history.stderr",
    "ASSESSMENT.json", "PROCESS.json", "RETURN.json", "BOUNDARY_CHECKPOINT.json"}
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
DEP = re.compile(r"\{dep:([^}]+)\}")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode()


def equal(a, b):
    """Preserve JSON boolean/type distinctions for receipts and identities."""
    return canonical(a) == canonical(b)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def strict_json(data):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "DUPLICATE_JSON_KEY:" + key)
            result[key] = value
        return result
    def number(text):
        value = float(text)
        require(math.isfinite(value), "NONFINITE_JSON_NUMBER")
        return value
    def constant(text):
        raise ValueError("NONFINITE_JSON_CONSTANT:" + text)
    return json.loads(data, object_pairs_hook=pairs, parse_float=number,
                      parse_constant=constant)


def under(root, name):
    require(isinstance(name, str), "PATH_NOT_STRING")
    relative = Path(name)
    require(name and not relative.is_absolute() and ".." not in relative.parts
            and str(relative) != ".", "UNSAFE_RELATIVE_PATH:" + name)
    path = root / relative
    require(not path.is_symlink() and path.resolve().is_relative_to(root.resolve()),
            "PATH_ESCAPES_ROOT_OR_SYMLINK:" + name)
    return path


def within(root, path):
    path = Path(path)
    require(path.is_absolute() and not path.is_symlink()
            and path.resolve().is_relative_to(root.resolve()), "ABSOLUTE_PATH_OUTSIDE_ATTEMPT")
    return path.resolve()


def atomic_create(path, value):
    """Atomic create only; no input, old attempt or completed output is changed."""
    path = Path(path)
    temporary = path.with_name(path.name + ".tmp-" + uuid.uuid4().hex)
    try:
        with temporary.open("xb") as stream:
            stream.write(json.dumps(value, indent=2, ensure_ascii=False,
                                    allow_nan=False).encode() + b"\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


class Evidence:
    """Hash every observed file and detect changes before issuing the result."""
    def __init__(self):
        self.files = {}

    def file(self, path, *, role, expected=None):
        path = Path(path)
        require(not path.is_symlink() and path.is_file(), "EVIDENCE_NOT_REGULAR:" + str(path))
        resolved = path.resolve()
        before = path.stat()
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(1 << 20), b""):
                digest.update(block)
        after = path.stat()
        require((before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns),
                "EVIDENCE_CHANGED_WHILE_READING:" + str(path))
        result = {"bytes": after.st_size, "sha256": digest.hexdigest()}
        if expected is not None:
            require(type(expected.get("bytes")) is int and expected["bytes"] >= 0
                    and isinstance(expected.get("sha256"), str)
                    and HEX64.fullmatch(expected["sha256"]), "INVALID_ARTIFACT_METADATA")
            require(result == {k: expected[k] for k in result}, "ARTIFACT_BYTES_OR_SHA256:" + str(path))
        old = self.files.get(str(resolved))
        if old is not None:
            require({k: old[k] for k in result} == result, "EVIDENCE_CHANGED:" + str(path))
            old["roles"] = sorted(set(old["roles"]) | {role})
        else:
            self.files[str(resolved)] = {**result, "roles": [role]}
        return result

    def read(self, path, *, role, maximum=64*1024**2):
        metadata = self.file(path, role=role)
        require(metadata["bytes"] <= maximum, "EVIDENCE_READ_SIZE_LIMIT:" + str(path))
        data = Path(path).read_bytes()
        require(len(data) == metadata["bytes"] and sha(data) == metadata["sha256"],
                "EVIDENCE_CHANGED_AFTER_HASH:" + str(path))
        return data

    def load(self, path, *, role):
        return strict_json(self.read(path, role=role))

    def hashes(self, root, values, *, role):
        require(isinstance(values, dict) and values, "MISSING_SOURCE_OR_INPUT_HASHES")
        for name, expected in values.items():
            require(isinstance(expected, str) and HEX64.fullmatch(expected), "INVALID_SHA256:" + name)
            actual = self.file(under(root, name), role=role)
            require(actual["sha256"] == expected, "SOURCE_OR_INPUT_SHA256:" + name)

    def unchanged(self):
        for path, metadata in list(self.files.items()):
            self.file(path, role="final_unchanged_readback", expected=metadata)


def options(argv, script):
    require(isinstance(argv, list) and len(argv) >= 2 and all(isinstance(a, str) for a in argv),
            "ARGV_SHAPE")
    require(Path(argv[1]).resolve() == script.resolve(), "SOURCE_BOUND_SCRIPT_PATH")
    result = {}
    i = 2
    while i < len(argv):
        key = argv[i]
        require(key.startswith("--") and key not in result, "DUPLICATE_OR_INVALID_OPTION")
        if i+1 == len(argv) or argv[i+1].startswith("--"):
            result[key] = True
            i += 1
        else:
            result[key] = argv[i+1]
            i += 2
    return result


def pointer(value, path):
    require(isinstance(path, str) and (path == "" or path.startswith("/")), "JSON_POINTER")
    for part in path[1:].split("/") if path else ():
        part = part.replace("~1", "/").replace("~0", "~")
        value = value[int(part)] if isinstance(value, list) else value[part]
    return value


class Chain:
    """Read the fixed launcher identities, including the build dependency."""
    def __init__(self, evidence, repo, manifest_path):
        self.evidence, self.repo = evidence, repo
        data = evidence.read(manifest_path, role="fixed_job_manifest")
        self.manifest, self.manifest_sha = strict_json(data), sha(data)
        require(self.manifest.get("schema") == "BASS_S12_JOB_MANIFEST_V1"
                and self.manifest.get("scope") == "new_s12_birth_memory"
                and self.manifest.get("allow_completed_campaign_replay") is False,
                "FIXED_JOB_MANIFEST_SCOPE")
        self.sources = self.manifest["source_files"]
        evidence.hashes(repo, self.sources, role="launcher_source")
        self.jobs = {}
        for job in self.manifest["jobs"]:
            job = deepcopy(job)
            job.setdefault("timeout_s", 1800)
            require(job["id"] not in self.jobs, "DUPLICATE_JOB_ID")
            self.jobs[job["id"]] = job
        require(self.jobs, "EMPTY_JOB_MANIFEST")
        self.cache, self.visiting = {}, set()
        self.failures = {}

    def started(self, directory):
        require(directory.is_dir() and not directory.is_symlink(), "ATTEMPT_DIRECTORY")
        start = self.evidence.load(directory/"STARTED.json", role="launcher_started")
        require(start.get("schema") == "BASS_S12_JOB_STARTED_V1", "STARTED_SCHEMA")
        job = self.jobs[start["job_id"]]
        require(start["manifest_sha256"] == self.manifest_sha, "STARTED_MANIFEST_SHA")
        identity = start["identity"]
        require(start["identity_sha256"] == sha(canonical(identity)), "STARTED_IDENTITY_SHA")
        require(identity.get("schema") == "BASS_S12_JOB_MANIFEST_V1"
                and equal(identity["job"], job) and equal(identity["source_files"], self.sources)
                and equal(identity["thread_environment"], THREAD_ENV), "STARTED_IDENTITY_CONTRACT")
        self.evidence.hashes(self.repo, job["input_files"], role="declared_job_input")
        executable = Path(identity["executable_realpath"])
        executable_meta = self.evidence.file(executable, role="outer_python_executable")
        require(executable.is_absolute() and str(executable.resolve()) == str(executable)
                and executable_meta["sha256"] == identity["executable_sha256"], "EXECUTABLE_IDENTITY")
        require(Path(start["cwd"]).resolve() == directory, "STARTED_CWD")
        require(equal(start["declared_cpu_ram_timeout_output"],
                      {k: job[k] for k in ("cpus", "ram_bytes", "timeout_s", "output_budget_bytes")}),
                "STARTED_RESOURCE_DECLARATION")
        template, actual = job["argv"], start["argv"]
        require(len(template) == len(actual), "EXPANDED_ARGV_LENGTH")
        directories = {}
        for before, after in zip(template, actual):
            expanded = before.replace("{repo}", str(self.repo)).replace("{run}", str(directory))
            hits = list(DEP.finditer(expanded))
            require(len(hits) <= 1, "UNSUPPORTED_MULTIPLE_DEPENDENCIES_PER_ARGUMENT")
            if not hits:
                require(expanded == after, "EXPANDED_ARGV_MISMATCH")
                continue
            hit = hits[0]
            prefix, suffix = expanded[:hit.start()], expanded[hit.end():]
            require(after.startswith(prefix) and after.endswith(suffix), "DEPENDENCY_ARGV_MISMATCH")
            captured = after[len(prefix):len(after)-len(suffix) if suffix else None]
            depdir = Path(captured)
            require(depdir.is_absolute() and not depdir.is_symlink(), "DEPENDENCY_DIRECTORY_PATH")
            depdir = depdir.resolve()
            ident = hit.group(1)
            require(ident not in directories or directories[ident] == depdir, "DEPENDENCY_PATH_CONFLICT")
            directories[ident] = depdir
        require(set(directories) == set(job.get("needs", [])) == set(identity["dependencies"]),
                "EXPLICIT_DEPENDENCY_SET")
        # argv[0] may be a PATH-resolved name; the runner records its actual hash.
        if "/" in actual[0]:
            require(Path(actual[0]).resolve() == executable, "OUTER_EXECUTABLE_PATH")
        return start, job, directories

    def completed(self, directory):
        directory = directory.resolve()
        if directory in self.cache:
            return self.cache[directory]
        require(directory not in self.failures,
                "DEPENDENCY_PREVIOUSLY_INVALID:" + self.failures.get(directory, ""))
        require(directory not in self.visiting, "DEPENDENCY_CYCLE")
        self.visiting.add(directory)
        try:
            return self._completed(directory)
        except Exception as error:
            self.failures[directory] = type(error).__name__ + ":" + str(error)
            raise
        finally:
            self.visiting.discard(directory)

    def _completed(self, directory):
        start, job, depdirs = self.started(directory)
        receipt = self.evidence.load(directory/"receipt.json", role="launcher_receipt")
        require(receipt.get("schema") == "BASS_S12_JOB_RECEIPT_V1"
                and receipt.get("status") == "PASS" and receipt.get("exit_code") == 0
                and type(receipt.get("exit_code")) is int and receipt.get("expected_exit") == 0
                and receipt.get("failures") == [] and receipt.get("timed_out") is False
                and receipt.get("other_owner_processes_signaled") == 0, "LAUNCHER_NOT_COMPLETED_PASS")
        for key in ("job_id", "identity_sha256", "manifest_sha256", "started_at_utc", "assigned_cpus"):
            require(equal(receipt[key], start[key]), "LAUNCHER_STARTED_RETURN_BINDING:" + key)
        require(finite(receipt["elapsed_seconds"]) and receipt["elapsed_seconds"] >= 0
                and job.get("expected_exit", 0) == 0, "LAUNCHER_ELAPSED_OR_EXPECTED_EXIT")
        required = set(job["artifacts"]) | {"stdout.log", "stderr.log"}
        require(set(receipt["artifacts"]) == required, "LAUNCHER_ARTIFACT_SET")
        for name, meta in receipt["artifacts"].items():
            self.evidence.file(under(directory, name), role="declared_attempt_artifact", expected=meta)
        for gate in job.get("accept", []):
            value = self.evidence.load(under(directory, gate["artifact"]), role="launcher_acceptance")
            require(equal(pointer(value, gate["pointer"]), gate["equals"]), "LAUNCHER_JSON_ACCEPTANCE")
        dependencies = {}
        for ident, depdir in depdirs.items():
            dep = self.completed(depdir)
            require(dep["job"]["id"] == ident, "DEPENDENCY_JOB_ID")
            expected = {"identity_sha256": dep["receipt"]["identity_sha256"],
                        "artifacts": dep["receipt"]["artifacts"]}
            require(equal(start["identity"]["dependencies"][ident], expected), "DEPENDENCY_IDENTITY_BINDING")
            dependencies[ident] = dep
        result = {"directory": directory, "started": start, "job": job,
                  "receipt": receipt, "dependencies": dependencies}
        self.cache[directory] = result
        return result


def owned_process(evidence, directory, process, stdout, stderr, *, expected_input):
    require(process.get("schema") == "BASS_S12_OWNED_PROCESS_V1"
            and process.get("status") == "EXITED" and type(process.get("exit_code")) is int
            and process["exit_code"] == 0 and process.get("cleanup_actions") == [], "OWNED_PROCESS_STATUS")
    require(process.get("input_sha256") == expected_input, "OWNED_PROCESS_STDIN_HASH")
    require(finite(process.get("elapsed_s")) and process["elapsed_s"] >= 0,
            "OWNED_PROCESS_ELAPSED")
    for label, name in (("stdout", stdout), ("stderr", stderr)):
        path = under(directory, name)
        require(Path(process[label+"_path"]).resolve() == path.resolve(), "OWNED_PROCESS_RAW_PATH")
        require(evidence.file(path, role="owned_process_raw")["sha256"] == process[label+"_sha256"],
                "OWNED_PROCESS_RAW_SHA")


def verify_upstream_tree(evidence, root, manifest):
    """Read back every pinned source file actually used by this build.

    The manifest is itself bound to the immutable f4 source binding. This
    additional post-build readback covers bytes, SHA256 and Git blob identity;
    it does not infer an earlier compiler invocation from file existence.
    """
    require(manifest.get("repo") == "cosmosapjw-quantum/vigilode"
            and manifest.get("source_commit") == UPSTREAM, "BUILD_UPSTREAM_SOURCE_IDENTITY")
    files = manifest.get("files")
    require(isinstance(files, list) and files, "BUILD_UPSTREAM_EMPTY_MANIFEST")
    seen, total = set(), 0
    for row in files:
        name = row["path"]
        require(name not in seen, "BUILD_UPSTREAM_DUPLICATE_PATH:" + name)
        seen.add(name)
        require(type(row.get("size")) is int and row["size"] >= 0
                and isinstance(row.get("sha256"), str) and HEX64.fullmatch(row["sha256"])
                and isinstance(row.get("git_blob"), str)
                and re.fullmatch(r"[0-9a-f]{40}", row["git_blob"]), "BUILD_UPSTREAM_METADATA")
        data = evidence.read(under(root, name), role="actual_compiled_upstream_source")
        require(len(data) == row["size"] and sha(data) == row["sha256"]
                and hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest() == row["git_blob"],
                "BUILD_UPSTREAM_ACTUAL_BYTES_SHA_OR_GIT_BLOB:" + name)
        total += len(data)
    return {"files": len(seen), "bytes": total}


def verify_build(chain, build, binding, binding_meta):
    evidence, repo, directory = chain.evidence, chain.repo, build["directory"]
    require(build["job"]["kind"] == "build" and not build["dependencies"], "FIXED_BUILD_DEPENDENCY")
    opts = options(build["started"]["argv"], repo/UNIT/"prepare.py")
    require(opts.get("--source-commit") == SOURCE
            and evidence.file(Path(opts["--binding"]), role="build_binding")["sha256"] == binding_meta["sha256"],
            "BUILD_ARGUMENT_BINDING")
    work = within(directory, opts["--work-dir"])
    build_path = work/"BUILD_RECEIPT.json"
    record = evidence.load(build_path, role="source_bound_build_receipt")
    require(record.get("schema") == "BASS_S12_BUILD_RECEIPT_V1"
            and record.get("status") == "COMPILED_SOURCE_BOUND"
            and record.get("source_commit") == SOURCE
            and record.get("scientific_campaign_executed") is False
            and record.get("binding_sha256") == binding_meta["sha256"], "BUILD_SOURCE_BINDING")
    require(equal(record["source_files"], {r["path"]: r["sha256"] for r in binding["files"]}),
            "BUILD_EXACT_SOURCE_FILE_SET")
    require(record.get("projector_sha256") == PROJECTOR_SHA
            and record["upstream"]["commit"] == UPSTREAM
            and record.get("rustc_version", "").startswith("rustc 1.94.1 "), "BUILD_PINNED_RUNTIME")
    client_files = {row["path"][len(UNIT):]: row["sha256"] for row in binding["files"]
                    if row["path"].startswith(UNIT+"src/")
                    or row["path"] in (UNIT+"Cargo.toml", UNIT+"Cargo.lock")}
    require(equal(record["runtime_client_files"], client_files), "BUILD_RUNTIME_CLIENT_SOURCE_MAP")
    evidence.hashes(work/"client/s12_birth_memory", client_files, role="actual_compiled_client_source")
    require(evidence.file(work/"client/s11_p246/rust/projector.rs", role="actual_compiled_projector")["sha256"]
            == PROJECTOR_SHA, "BUILD_RUNTIME_PROJECTOR_BYTES")
    upstream_path = repo/"research/bass_isotropy_response_20261018/s9_vigilode/VIGILODE_SOURCE.json"
    upstream = evidence.load(upstream_path, role="pinned_upstream_source_manifest")
    require(record["upstream"]["manifest_sha256"] == evidence.file(upstream_path, role="pinned_upstream_source_manifest")["sha256"]
            and record["upstream"]["tree"] == upstream["source_tree"]
            and record["upstream"]["files"] == len(upstream["files"])
            and record["upstream"]["bytes"] == sum(row["size"] for row in upstream["files"]),
            "BUILD_UPSTREAM_MANIFEST_IDENTITY")
    upstream_actual = verify_upstream_tree(evidence, work/"vigilode", upstream)
    require(upstream_actual == {k: record["upstream"][k] for k in ("files", "bytes")},
            "BUILD_UPSTREAM_ACTUAL_FILE_COUNT_AND_BYTES")
    process = evidence.load(work/"COMPILE_PROCESS.json", role="compile_process_receipt")
    require(equal(record["commands"], [process]), "BUILD_COMPILE_PROCESS_READBACK")
    owned_process(evidence, work, process, "compile.stdout", "compile.stderr", expected_input=None)
    binary_record = record["binaries"]["s12-history"]
    binary = within(work, binary_record["path"])
    binary_meta = evidence.file(binary, role="source_bound_history_binary")
    require(binary_meta["sha256"] == binary_record["sha256"], "BUILD_BINARY_SHA")
    for path in (build_path, work/"COMPILE_PROCESS.json", work/"compile.stdout", work/"compile.stderr", binary):
        relative = str(path.relative_to(directory))
        require(relative in build["receipt"]["artifacts"], "BUILD_EVIDENCE_NOT_DECLARED:" + relative)
    return binary, binary_meta


def selected_states(rows, times):
    require(isinstance(rows, list) and rows, "EMPTY_OBSERVATIONS")
    by_time = {}
    for row in rows:
        x, state = row["x"], row["state"]
        require(finite(x) and x not in by_time and isinstance(state, list) and len(state) == 6
                and all(finite(v) for v in state), "OBSERVATION_DOMAIN_OR_DUPLICATE")
        by_time[x] = state
    require(all(t in by_time for t in times), "MISSING_COMMON_OUTPUT_TIME")
    return [by_time[t] for t in times]


def flat(rows):
    return [value for row in rows for value in row]


def comparison(a, b):
    require(len(a) == len(b) and a and all(len(x) == len(y) and x for x, y in zip(a, b)),
            "COMPARISON_SHAPE")
    a, b = flat(a), flat(b)
    require(all(finite(x) for x in a+b), "COMPARISON_NONFINITE")
    den = [1+max(abs(x), abs(y)) for x, y in zip(a, b)]
    require(all(finite(x) and x > 0 for x in den), "COMPARISON_DENOMINATOR")
    errors = [x-y for x, y in zip(a, b)]
    require(all(finite(x) for x in errors), "COMPARISON_NONFINITE_DIFFERENCE")
    return {"max_absolute": max(abs(x) for x in errors),
            "max_scaled": max(abs(x)/d for x, d in zip(errors, den)),
            "minimum_scaled_denominator": min(den), "values": len(a)}


def linear(a, b, factor_a, factor_b, denominator):
    require(finite(denominator) and denominator > 0 and len(a) == len(b), "LINEAR_DENOMINATOR_OR_SHAPE")
    result = [[(factor_a*x+factor_b*y)/denominator for x, y in zip(ra, rb)] for ra, rb in zip(a, b)]
    require(all(len(ra) == len(rb) and ra for ra, rb in zip(a, b))
            and result and all(finite(v) for v in flat(result)), "LINEAR_NONFINITE_OR_SHAPE")
    return result


def validate_manifests(evidence, args, chain):
    histories = evidence.load(args.histories, role="fixed_extended_history_manifest")
    prereg = evidence.load(args.preregistration, role="fixed_preregistered_gates")
    binding = evidence.load(args.science_binding, role="immutable_science_binding")
    require(args.source_commit == SOURCE and binding.get("schema") == "BASS_S12_IMMUTABLE_RUNTIME_SOURCE_BINDING_V1"
            and binding.get("source_commit") == SOURCE and binding.get("source_tree") == TREE
            and binding.get("git_readback_pass") is True, "IMMUTABLE_SOURCE_BINDING")
    seen = set()
    for row in binding["files"]:
        require(row["path"] not in seen and row.get("pass") is True, "SOURCE_BINDING_DUPLICATE_OR_UNVERIFIED")
        seen.add(row["path"])
        path = under(args.repo, row["path"])
        raw = evidence.read(path, role="immutable_f4_source")
        require(len(raw) == row["bytes"] and sha(raw) == row["sha256"]
                and hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest() == row["git_blob"],
                "IMMUTABLE_SOURCE_BYTES_OR_GIT_BLOB:" + row["path"])
    for relative in ("assess_history.py", "process_control.py", "ncp/history_job.py", "prepare.py"):
        path = UNIT+relative
        row = next(r for r in binding["files"] if r["path"] == path)
        require(chain.sources.get(path) == row["sha256"], "LAUNCHER_MISSING_FROZEN_HELPER:" + path)
    for relative in ("ncp/runner.py", "ncp/aggregate.py"):
        require(UNIT+relative in chain.sources, "LAUNCHER_MISSING_ORCHESTRATION_SOURCE")
    observer_source = evidence.read(args.repo/UNIT/"assess_history.py", role="frozen_stdlib_assessor")
    require(sha(observer_source) == ASSESSOR_SHA, "FROZEN_ASSESSOR_HASH")
    # Compile/exec only defines the verified read-only observer; its __main__ is
    # deliberately not invoked and no bytecode cache is written into the repo.
    namespace = {"__name__": "bass_s12_frozen_observer", "__file__": str(args.repo/UNIT/"assess_history.py")}
    exec(compile(observer_source, namespace["__file__"], "exec"), namespace)
    require(histories.get("schema") == "BASS_S12_EXTENDED_FIXED_HISTORIES_V1"
            and histories.get("primary") == "p24_y0_full"
            and [r["id"] for r in histories["cases"]] == list(CASE_IDS)
            and equal(histories["fixed_config"], FIXED_CONFIG), "FIXED_EXTENDED_HISTORY_SET")
    require(all(type(histories.get(key)) is int and histories[key] == 0
                for key in ("completed_campaign_replays", "solver_calls_during_generation", "old_stock_changes")),
            "NO_COMPLETED_CAMPAIGN_REPLAY")
    expected_fd = [{"step": h, "plus": FD_IDS[2*i], "minus": FD_IDS[2*i+1]} for i, h in enumerate(STEPS)]
    require(equal(histories["fd_pairs"], expected_fd), "FIXED_FD_PAIRS")
    times = histories["output_times"]
    require(len(times) == 49 and all(finite(t) for t in times)
            and times[0] == 0 and times[-1] == 1.2
            and all(a < b for a, b in zip(times, times[1:])), "FIXED_COMMON_TIME_DOMAIN")
    require(prereg.get("schema") == "BASS_S12_LIGHTWEIGHT_PREREGISTRATION_V1"
            and prereg.get("recorded_before_scientific_execution") is True, "PREREGISTRATION_SCHEMA")
    for key, expected in GATES.items():
        require(type(prereg["histories"].get(key)) in (float, int)
                and prereg["histories"][key] == expected, "UNALTERED_PREREGISTERED_GATE:" + key)
    require(prereg["histories"]["negative_controls"] == list(CONTROLS), "REGISTERED_OMISSION_CONTROLS")
    inputs = {}
    for row in histories["cases"]:
        path = under(args.histories.parent, row["path"])
        data = evidence.read(path, role="fixed_history_input")
        require(len(data) == row["bytes"] and sha(data) == row["sha256"], "FIXED_HISTORY_INPUT_SHA")
        inp = strict_json(data)
        require(inp.get("schema") == "BASS_S12_HISTORY_INPUT_V1"
                and inp["provenance"]["completed_campaign_replay"] is False
                and inp["provenance"]["spectral_owner"] == OWNER
                and equal(inp["output_times"], times), "INPUT_SCOPE_OR_COMMON_TIMES")
        require(all(inp[key] == row[key] for key in ("control", "parameter", "birth_rule"))
                and inp["solver"]["arm"] == row["solver_arm"], "MANIFEST_INPUT_LABELS")
        inputs[row["id"]] = (inp, data, path, row)
    base = inputs["p24_y0_full"][0]
    require(equal(base["config"], FIXED_CONFIG) and base["parameter"] == "y0"
            and base["birth_rule"] == "P24" and base["control"] == "full" and base["mode"] == "fused"
            and base["solver"]["arm"] == "small_clock7", "PRIMARY_CASE_CONTRACT")
    for key in ("rtol", "atol", "max_step"):
        require(base["solver"][key] == prereg["histories"][key], "FIXED_SOLVER_SETTING:" + key)
    for ident, (inp, _, _, _) in inputs.items():
        expected = deepcopy(base)
        if ident in ("gl_y0_full", "gl_b0_gauge"):
            expected["birth_rule"] = "source_frame_GL"
        if ident == "gl_b0_gauge": expected["parameter"] = "b0"
        if ident == "p24_y0_mf6": expected["solver"]["arm"] = "mf_into_ls6"
        if ident == "p24_y0_baseline": expected["mode"] = "baseline"
        if ident in CONTROLS: expected["control"] = ident
        if ident in FD_IDS:
            index = FD_IDS.index(ident)
            expected["config"]["y0"] += (1 if index % 2 == 0 else -1)*STEPS[index//2]
        require(equal(inp, expected), "UNREGISTERED_INPUT_CHANGE:" + ident)
    return histories, prereg, binding, namespace["assess"], inputs


def case_evidence(ident, directory, chain, binding, binding_meta, observer, item, times):
    inp, expected_input, input_path, row = item
    e = chain.evidence
    outer = chain.completed(directory)
    require(outer["job"]["kind"] == "new_rust_history" and len(outer["dependencies"]) == 1,
            "HISTORY_JOB_KIND_OR_BUILD_DEPENDENCY")
    require(HISTORY_ARTIFACTS <= set(outer["job"]["artifacts"]), "UNDECLARED_HISTORY_ARTIFACTS")
    opts = options(outer["started"]["argv"], chain.repo/UNIT/"ncp/history_job.py")
    require(set(opts) == {"--binary", "--input", "--source-commit", "--out"}
            and opts["--source-commit"] == SOURCE and Path(opts["--input"]).resolve() == input_path.resolve()
            and Path(opts["--out"]).resolve() == directory, "HISTORY_WRAPPER_EXACT_COMMAND")
    relative_input = str(input_path.resolve().relative_to(chain.repo))
    require(outer["job"]["input_files"].get(relative_input) == row["sha256"], "JOB_FIXED_INPUT_HASH")
    build = next(iter(outer["dependencies"].values()))
    binary, binary_meta = verify_build(chain, build, binding, binding_meta)
    require(Path(opts["--binary"]).resolve() == binary, "WRAPPER_BUILD_BINARY_PATH")
    require(e.read(directory/"INPUT.json", role="actual_history_stdin") == expected_input,
            "ACTUAL_STDIN_NOT_EXACT_FIXED_INPUT")
    raw_bytes = e.read(directory/"history.stdout", role="raw_history_stdout")
    raw = strict_json(raw_bytes)
    stored_history = e.load(directory/"HISTORY.json", role="parsed_history_readback")
    require(equal(raw, stored_history), "HISTORY_JSON_NOT_RAW_STDOUT")
    process = e.load(directory/"PROCESS.json", role="history_process_receipt")
    owned_process(e, directory, process, "history.stdout", "history.stderr", expected_input=row["sha256"])
    expected_argv = [str(binary), "--source-commit", SOURCE, "--input-sha256", row["sha256"],
                     "--checkpoint", str(directory/"BOUNDARY_CHECKPOINT.json")]
    require(process["argv"] == expected_argv and Path(process["cwd"]).resolve() == directory
            and process["timeout_s"] == 1700
            and process["limits"] == {"address_space_bytes": 2*1024**3, "file_bytes": 64*1024**2},
            "EXACT_HISTORY_PROCESS_ARGUMENTS_OR_LIMITS")
    result = e.load(directory/"RETURN.json", role="history_wrapper_return")
    require(result.get("schema") == "BASS_S12_HISTORY_JOB_V1"
            and equal(result["execution"], process) and result["source_commit"] == SOURCE
            and result["input_sha256"] == row["sha256"]
            and result["binary_sha256"] == binary_meta["sha256"] and "error" not in result,
            "WRAPPER_RETURN_IDENTITY")
    expected_binding = {"source_commit": SOURCE, "input_sha256": row["sha256"],
                        "binary_sha256": binary_meta["sha256"]}
    require(equal(raw["binding"], expected_binding) and raw.get("status") == "completed"
            and raw.get("failure") is None and raw.get("resumed") is False
            and raw.get("resume_boundary") is None, "RAW_HISTORY_COMPLETION_BINDING")
    diag = e.load(directory/"history.stderr", role="raw_process_completion_status")
    require(diag.get("schema") == "BASS_S12_PROCESS_STATUS_V1" and diag.get("status") == "completed"
            and equal(diag["binding"], expected_binding), "STDERR_STATUS_BINDING")
    for key, expected in {"segments": len(raw["segments"]), "admitted_births": len(raw["events"]),
            "observations": len(raw["observations"]), "resumed": False,
            "checkpoint_writes": raw["checkpoint_writes"], "elapsed_seconds": raw["elapsed_seconds"]}.items():
        require(equal(diag[key], expected), "STDERR_STATUS_CARDINALITY:" + key)
    require(finite(raw["elapsed_seconds"]) and raw["elapsed_seconds"] >= 0, "RAW_ELAPSED_SECONDS")
    assessment = observer(inp, raw, input_sha256=row["sha256"], source_commit=SOURCE,
                          binary_sha256=binary_meta["sha256"])
    stored_assessment = e.load(directory/"ASSESSMENT.json", role="stored_history_assessment")
    require(equal(assessment, stored_assessment) and equal(result["assessment"], assessment),
            "INDEPENDENT_READONLY_REASSESSMENT_MISMATCH")
    require(assessment["execution_completed"] is True and assessment["structural_pass"] is True
            and assessment["external_binding_verified"] is True, "CASE_STRUCTURAL_GATES")
    expected_status = "PASS_CONTROL_RECORD" if ident in CONTROLS else "PASS_FULL"
    require(result.get("status") == expected_status, "HISTORY_WRAPPER_STATUS_SCOPE")
    if ident in CONTROLS:
        require(assessment["full_scientific_pass"] is False
                and assessment["omission_is_not_a_full_physics_pass"] is True, "OMISSION_NOT_FULL_PHYSICS_PASS")
    else:
        require(assessment["full_scientific_pass"] is True and assessment["numerical_gates_pass"] is True,
                "FULL_CASE_NUMERICAL_GATES")
    wrapper_log = e.load(directory/"stdout.log", role="outer_history_stdout")
    require(equal(wrapper_log, {"status": expected_status, "receipt": str(directory/"RETURN.json")}),
            "OUTER_STDOUT_RETURN_READBACK")
    # The final checkpoint is retained and hash-bound as evidence. No checkpoint
    # resume is performed or claimed by this extended-ensemble observer.
    selected = selected_states(raw["observations"], times)
    return {"id": ident, "job_id": outer["job"]["id"], "attempt": str(directory),
        "outer_identity_sha256": outer["receipt"]["identity_sha256"],
        "build_identity_sha256": build["receipt"]["identity_sha256"],
        "input_sha256": row["sha256"], "binary_sha256": binary_meta["sha256"],
        "raw_stdout_sha256": sha(raw_bytes), "state6": selected,
        "all_gauge_values": [max(abs(o["state"][3]), abs(o["state"][5]), abs(o["state"][4]-1))
                             for o in raw["observations"]] if ident == "gl_b0_gauge" else [],
        "assessment": assessment, "event_count": len(raw["events"]),
        "segment_count": len(raw["segments"]), "observation_count": len(raw["observations"]),
        "old_stock_digests": raw["old_stock_digests"]}


def ensemble(cases, times, check):
    primary = cases["p24_y0_full"]["state6"]
    tangent = [r[3:] for r in primary]
    cross = {"output_times": times, "primary_state6": primary}
    for ident, label, gate_key in (("p24_y0_mf6", "MF6_clock7", "MF6_clock7_state6_scaled_gate"),
        ("p24_y0_baseline", "baseline_fused", "baseline_fused_history_state6_scaled_gate")):
        metric = comparison(cases[ident]["state6"], primary)
        metric["gate"] = GATES[gate_key]
        metric["state6_binary64_equal"] = all(struct.pack("<d", float(a)) == struct.pack("<d", float(b))
            for a, b in zip(flat(cases[ident]["state6"]), flat(primary)))
        cross[label] = metric
        cross[ident+"_state6"] = cases[ident]["state6"]
        check(label+"_state6", metric["max_scaled"] <= metric["gate"], **metric)
    def numerical_map(ident):
        checks = cases[ident]["assessment"]["checks"]
        pairs = [(r["name"], r["pass"]) for r in checks if r["category"] == "numerical"]
        require(len({p[0] for p in pairs}) == len(pairs), "DUPLICATE_ASSESSMENT_NUMERICAL_GATE")
        return dict(pairs)
    base_gates, fused_gates = numerical_map("p24_y0_baseline"), numerical_map("p24_y0_full")
    check("baseline_fused_internal_gate_identity", base_gates == fused_gates and bool(fused_gates)
          and all(v is True for v in fused_gates.values()), numerical_gates=len(fused_gates))
    gauge = cases["gl_b0_gauge"]["all_gauge_values"]
    require(gauge and all(finite(x) for x in gauge), "GAUGE_NONFINITE")
    gauge_max = max(gauge)
    cross["source_frame_GL_b0_gauge"] = {"max_absolute": gauge_max,
        "observations": len(gauge), "gate": GATES["source_frame_gauge_absolute_gate"]}
    check("source_frame_GL_b0_gauge_absolute", gauge_max <= GATES["source_frame_gauge_absolute_gate"],
          **cross["source_frame_GL_b0_gauge"])
    estimates = []
    for i, h in enumerate(STEPS):
        plus, minus = ([r[:3] for r in cases[FD_IDS[2*i]]["state6"]],
                       [r[:3] for r in cases[FD_IDS[2*i+1]]["state6"]])
        estimates.append(linear(plus, minus, 1, -1, 2*h))
        check("FD_"+str(h)+"_finite_positive_denominator", finite(2*h) and 2*h > 0,
              denominator=2*h, values=len(flat(estimates[-1])))
    coarse = linear(estimates[1], estimates[0], 4, -1, 3)
    fine = linear(estimates[2], estimates[1], 4, -1, 3)
    rich = comparison(tangent, fine)
    raw = comparison(tangent, estimates[2])
    change = comparison(coarse, fine)
    check("fine_Richardson_absolute_h_b_y", rich["max_absolute"] <= GATES["Richardson_h_b_y_max_absolute_gate"],
          max_absolute_error=rich["max_absolute"], gate=GATES["Richardson_h_b_y_max_absolute_gate"],
          values=rich["values"])
    check("raw_fine_FD_scaled_h_b_y", raw["max_scaled"] <= GATES["raw_fine_FD_scaled_gate"],
          max_scaled_error=raw["max_scaled"], gate=GATES["raw_fine_FD_scaled_gate"],
          minimum_denominator=raw["minimum_scaled_denominator"], values=raw["values"])
    fd = {"steps": list(STEPS), "output_times": times, "full_tangent": tangent,
        "raw_centered_derivatives": estimates, "coarse_Richardson": coarse, "fine_Richardson": fine,
        "fine_Richardson_error": linear(tangent, fine, 1, -1, 1),
        "fine_Richardson_max_absolute": rich["max_absolute"], "raw_fine_max_scaled": raw["max_scaled"],
        "raw_fine_minimum_scaled_denominator": raw["minimum_scaled_denominator"],
        "coarse_to_fine_Richardson_difference_max_absolute": change["max_absolute"],
        "comparison_scalar_count": rich["values"], "old_completed_S8_Richardson_campaign_replayed": False}
    controls = []
    for ident in CONTROLS:
        omitted = [r[3:] for r in cases[ident]["state6"]]
        full_error, reference_error = comparison(omitted, tangent), comparison(omitted, fine)
        threshold = 10*rich["max_absolute"]
        require(finite(threshold) and threshold >= 0, "OMISSION_THRESHOLD_NONFINITE")
        identified = full_error["max_absolute"] > threshold
        row = {"control": ident, "identified": identified,
            "full_vs_omitted_max_absolute": full_error["max_absolute"],
            "omitted_vs_Richardson_max_absolute": reference_error["max_absolute"],
            "full_vs_Richardson_max_absolute": rich["max_absolute"],
            "required_strict_lower_bound": threshold,
            "internal_numerical_gates_pass": cases[ident]["assessment"]["numerical_gates_pass"],
            "full_scientific_pass": False, "tangent": omitted,
            "failed_numerical_checks": [c for c in cases[ident]["assessment"]["checks"]
                                        if c["category"] == "numerical" and c["pass"] is False]}
        controls.append(row)
        check(ident+"_identified_against_full_error", identified,
              **{k: v for k, v in row.items() if k not in ("tangent", "failed_numerical_checks")})
    return fd, cross, controls


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("histories", "science-binding", "preregistration", "job-manifest", "repo", "out"):
        parser.add_argument("--"+name, required=True, type=Path)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--case", action="append", required=True, metavar="ID=ATTEMPT_DIRECTORY")
    args = parser.parse_args()
    for key in ("histories", "science_binding", "preregistration", "job_manifest", "repo", "out"):
        setattr(args, key, getattr(args, key).resolve())
    args.out.mkdir(parents=True, exist_ok=True)
    require(all(not (args.out/name).exists() for name in OUTPUTS), "AGGREGATE_ATTEMPT_ALREADY_USED")
    evidence, checks, case_rows, errors = Evidence(), [], {}, []
    fd = cross = {"status": "NOT_EVALUATED"}
    controls = []
    started_at = dt.datetime.now(dt.timezone.utc).isoformat()
    def check(name, passed, **details):
        checks.append({"name": name, "pass": bool(passed), **details})
    try:
        evidence.file(Path(__file__), role="actual_aggregate_source")
        require(Path(__file__).resolve() == (args.repo/UNIT/"ncp/aggregate.py").resolve(),
                "AGGREGATE_MUST_BE_THE_DECLARED_REPO_SOURCE")
        chain = Chain(evidence, args.repo, args.job_manifest)
        histories, prereg, binding, observer, inputs = validate_manifests(evidence, args, chain)
        binding_meta = evidence.file(args.science_binding, role="science_binding_argument")
        case_paths = {}
        for entry in args.case:
            ident, separator, path = entry.partition("=")
            require(separator and ident in CASE_IDS and ident not in case_paths and path, "CASE_ARGUMENT_SET")
            case_paths[ident] = Path(path).resolve()
        require(set(case_paths) == set(CASE_IDS) and len(set(case_paths.values())) == 14,
                "EXACT_FOURTEEN_DISTINCT_ATTEMPTS_REQUIRED")
        aggregate_started, aggregate_job, depdirs = chain.started(args.out)
        require(aggregate_job["kind"] == "paired_finite_difference"
                and set(depdirs.values()) == set(case_paths.values()) and len(depdirs) == 14,
                "AGGREGATE_EXACT_FOURTEEN_HISTORY_DEPENDENCIES")
        for path in (args.histories, args.preregistration, args.science_binding):
            relative = str(path.relative_to(args.repo))
            require(aggregate_job["input_files"].get(relative) == evidence.file(path, role="aggregate_fixed_input")["sha256"],
                    "AGGREGATE_FIXED_INPUT_BINDING:" + relative)
        check("fixed_manifest_source_and_fourteen_job_contract", True,
              source_commit=SOURCE, source_tree=TREE, assessor_sha256=ASSESSOR_SHA,
              job_manifest_sha256=chain.manifest_sha, cases=14)
        for ident in CASE_IDS:
            try:
                row = case_evidence(ident, case_paths[ident], chain, binding, binding_meta,
                                    observer, inputs[ident], histories["output_times"])
                expected = aggregate_started["identity"]["dependencies"][row["job_id"]]
                outer = chain.cache[case_paths[ident]]
                require(equal(expected, {"identity_sha256": outer["receipt"]["identity_sha256"],
                        "artifacts": outer["receipt"]["artifacts"]}), "AGGREGATE_DEPENDENCY_RECEIPT_BINDING")
                case_rows[ident] = row
                check(ident+"_source_process_artifact_and_internal_gates", True,
                    input_sha256=row["input_sha256"], binary_sha256=row["binary_sha256"],
                    internal_checks_passed=row["assessment"]["checks_passed"],
                    internal_checks_total=row["assessment"]["checks_total"],
                    full_scientific_pass=row["assessment"]["full_scientific_pass"],
                    control=ident in CONTROLS)
            except Exception as error:
                item = {"case": ident, "type": type(error).__name__, "message": str(error)}
                errors.append(item)
                check(ident+"_source_process_artifact_and_internal_gates", False, error=item)
        check("exact_14_cases_11_full_3_controls", len(case_rows) == 14
              and sum(r["assessment"]["full_scientific_pass"] for r in case_rows.values()) == 11,
              admitted_cases=len(case_rows), admitted_full_cases=sum(r["assessment"]["full_scientific_pass"] for r in case_rows.values()))
        if len(case_rows) == 14:
            require(len({r["binary_sha256"] for r in case_rows.values()}) == 1
                    and len({r["build_identity_sha256"] for r in case_rows.values()}) == 1,
                    "ENSEMBLE_MIXED_BINARY_OR_BUILD")
            old = inputs["p24_y0_full"][0]["expected_old_digests"]
            check("ensemble_old_physical_stock_unchanged", all(r["old_stock_digests"] == old for r in case_rows.values()),
                  old_physical_digests=old)
            fd, cross, controls = ensemble(case_rows, histories["output_times"], check)
        else:
            check("ensemble_comparison_requires_all_fourteen_verified_cases", False)
        evidence.unchanged()
        check("all_evidence_unchanged_after_assessment", True, files=len(evidence.files))
    except Exception as error:
        item = {"type": type(error).__name__, "message": str(error)}
        errors.append(item)
        check("aggregate_exception", False, error=item)
    status = "PASS_NEW_EXTENDED_ENSEMBLE" if not errors and checks and all(c["pass"] for c in checks) else "FAIL"
    summaries = {ident: {k: v for k, v in row.items() if k not in ("state6", "all_gauge_values")}
                 for ident, row in case_rows.items()}
    documents = {"CHECKS.json": checks,
        "EVIDENCE.json": {"schema": "BASS_S12_EXTENDED_AGGREGATE_EVIDENCE_V1", "files": evidence.files,
            "scope": "Actual byte hashes and source/launcher/build/owned-process bindings; remote Git publication/readback is separately recorded."},
        "CASE_ASSESSMENTS.json": summaries, "FD_RICHARDSON.json": fd,
        "CROSS_DRIVER.json": cross, "OMISSION_CONTROLS.json": controls}
    generated = {}
    for name, document in documents.items():
        atomic_create(args.out/name, document)
        raw = (args.out/name).read_bytes()
        generated[name] = {"bytes": len(raw), "sha256": sha(raw)}
    result = {"schema": "BASS_S12_EXTENDED_ENSEMBLE_AGGREGATE_V1", "status": status,
        "scope": "Fixed k16/n64 manufactured histories: per-case source/process/internal gates, three-step y0 FD/Richardson, GL b0 gauge, MF6/clock7, baseline/fused, and omission identification only.",
        "source_commit": SOURCE, "source_tree": TREE, "assessor_sha256": ASSESSOR_SHA,
        "aggregate_source_sha256": sha(Path(__file__).read_bytes()),
        "declared_file_sha256": {name: evidence.files.get(str(path), {}).get("sha256")
            for name, path in (("job_manifest", args.job_manifest), ("histories", args.histories),
                ("preregistration", args.preregistration), ("science_binding", args.science_binding))},
        "started_at_utc": started_at, "ended_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "checks_passed": sum(c["pass"] for c in checks), "checks_total": len(checks),
        "cases_expected": 14, "cases_verified": len(case_rows), "full_cases_expected": 11,
        "omission_controls_expected": 3, "source_bound_binary_sha256": sorted({r["binary_sha256"] for r in case_rows.values()}),
        "fixed_thresholds": GATES, "errors": errors, "artifacts": generated,
        "history_integrations_performed": 0, "projector_calls_performed": 0,
        "builds_performed": 0, "completed_campaign_replays": 0,
        "omission_controls_are_full_physics_passes": False,
        "independent_python_reference_for_extended_histories": "NOT_RUN_BY_THIS_AGGREGATOR",
        "checkpoint_resume_exercised": False, "NCP64_hardware_verified_by_this_aggregate": False,
        "native_full_spectral_history_or_continuum_convergence_certified": False,
        "code_author_independent_review_claim": False}
    atomic_create(args.out/"RETURN.json", result)
    print(json.dumps({"status": status, "checks_passed": result["checks_passed"],
                      "checks_total": result["checks_total"], "cases_verified": len(case_rows)}, allow_nan=False))
    return 0 if status == "PASS_NEW_EXTENDED_ENSEMBLE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
