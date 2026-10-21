#!/usr/bin/env python3
"""Bounded C8 observer verification using already-completed SHORT S12 data.

No solver, projector, compiler, subprocess, network or extended history runs.
This is implementation-author verification, not independent physics approval.
The full production launcher/receipt chain is deliberately NOT fabricated.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import datetime as dt
import hashlib
import json
from pathlib import Path
import resource
import signal
import sys
import time
from types import SimpleNamespace


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--aggregate", required=True, type=Path)
    parser.add_argument("--aggregate-sha256", required=True)
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--short-dir", required=True, type=Path)
    parser.add_argument("--upstream-root", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    for key in ("aggregate", "repo", "short_dir", "upstream_root", "out"):
        setattr(args, key, getattr(args, key).resolve())
    if args.out.exists():
        raise SystemExit("OUT_EXISTS_CREATE_NEW_ATTEMPT")
    args.out.mkdir(parents=True)
    resource.setrlimit(resource.RLIMIT_AS, (512*1024**2, 512*1024**2))
    resource.setrlimit(resource.RLIMIT_FSIZE, (32*1024**2, 32*1024**2))
    signal.alarm(90)
    started = time.monotonic()
    started_utc = dt.datetime.now(dt.timezone.utc).isoformat()
    checks, details, evidence, error = [], {}, None, None

    def check(name, passed, **kw):
        checks.append({"name": name, "pass": bool(passed), **kw})

    def rejects(name, callback, expected):
        try:
            callback()
        except ValueError as exc:
            check(name, str(exc).startswith(expected), observed_error=str(exc), expected_prefix=expected)
        else:
            check(name, False, expected_prefix=expected, observed_error=None)

    try:
        source = args.aggregate.read_bytes()
        actual = hashlib.sha256(source).hexdigest()
        if actual != args.aggregate_sha256:
            raise ValueError("AGGREGATE_SOURCE_SHA256")
        namespace = {"__name__": "bass_c8_verified_observer", "__file__": str(args.aggregate)}
        exec(compile(source, str(args.aggregate), "exec"), namespace)
        m = SimpleNamespace(**namespace)
        evidence = m.Evidence()
        evidence.file(args.aggregate, role="published_aggregate_source")
        evidence.file(Path(__file__), role="verification_script")
        unit = args.repo/m.UNIT
        binding = evidence.load(unit/"ncp/SCIENCE_BINDING.json", role="science_binding")
        sources = {row["path"]: row["sha256"] for row in binding["files"]}
        for relative in ("ncp/runner.py", "ncp/aggregate.py"):
            sources[m.UNIT+relative] = evidence.file(unit/relative, role="actual_orchestration_source")["sha256"]
        manifest_args = SimpleNamespace(repo=args.repo, source_commit=m.SOURCE,
            histories=unit/"ncp/inputs/HISTORIES.json", science_binding=unit/"ncp/SCIENCE_BINDING.json",
            preregistration=unit/"PREREGISTRATION.json")
        # Only validate source/input files. This object has no receipt, process,
        # job identity or alleged actual NCP execution.
        histories, _, _, _, fixed_inputs = m.validate_manifests(evidence, manifest_args,
                                                               SimpleNamespace(sources=sources))
        check("actual_extended_input_manifest_only", len(fixed_inputs) == 14
              and histories["fixed_config"]["k"] == 16 and len(histories["output_times"]) == 49,
              science_execution=False, execution_status="NOT_RUN")
        upstream = evidence.load(args.repo/"research/bass_isotropy_response_20261018/s9_vigilode/VIGILODE_SOURCE.json",
                                 role="pinned_upstream_manifest")
        upstream_result = m.verify_upstream_tree(evidence, args.upstream_root, upstream)
        check("actual_existing_upstream_tree_readback", upstream_result == {"files": 178, "bytes": 5196962},
              **upstream_result, compilation=False)
        bad = deepcopy(upstream)
        bad["files"][0]["git_blob"] = "0"*40
        rejects("upstream_wrong_git_blob_rejected",
                lambda: m.verify_upstream_tree(evidence, args.upstream_root, bad),
                "BUILD_UPSTREAM_ACTUAL_BYTES_SHA_OR_GIT_BLOB:")
        bad_path = deepcopy(upstream)
        bad_path["files"][0]["path"] = "../outside"
        rejects("upstream_path_escape_rejected",
                lambda: m.verify_upstream_tree(evidence, args.upstream_root, bad_path), "UNSAFE_RELATIVE_PATH:")

        manifest = evidence.load(args.short_dir/"ARTIFACT_MANIFEST.json", role="completed_short_manifest")
        if (manifest.get("source_commit") != m.SOURCE
                or manifest.get("validation_source_commit") != "4e3615dd75ff1a1efc2792edb3ba5b702a8a9b06"):
            raise ValueError("COMPLETED_SHORT_SOURCE_IDENTITY")
        names = set()
        for row in manifest["files"]:
            if row["path"] in names:
                raise ValueError("DUPLICATE_SHORT_MANIFEST_PATH")
            names.add(row["path"])
            evidence.file(m.under(args.short_dir, row["path"]), role="completed_short_payload", expected=row)
        summary = evidence.load(args.short_dir/"SUMMARY.json", role="completed_short_summary")
        check("reused_completed_short_summary", summary["status"] == "PASS_SCOPED"
              and summary["checks_passed"] == summary["checks_total"] == 72)
        old_fd = evidence.load(args.short_dir/"FD_RICHARDSON.json", role="completed_short_fd")
        old_cross = evidence.load(args.short_dir/"CROSS_IMPLEMENTATION.json", role="completed_short_cross")
        old_controls = evidence.load(args.short_dir/"OMISSION_CONTROLS.json", role="completed_short_controls")
        times, cases = old_fd["output_times"], {}
        for ident in m.CASE_IDS:
            raw = evidence.load(args.short_dir/(ident+".stdout"), role="completed_short_raw")
            assessment = evidence.load(args.short_dir/(ident+".assessment.json"), role="completed_short_assessment")
            inp = evidence.load(args.short_dir/(ident+".input.json"), role="completed_short_input")
            check(ident+"_is_short_reused_case", inp["config"]["k"] == 4 and inp["config"]["n"] == 32
                  and inp["config"]["x_end"] == 0.4 and inp["output_times"] == times)
            cases[ident] = {"state6": m.selected_states(raw["observations"], times),
                           "assessment": assessment,
                           "all_gauge_values": [max(abs(r["state"][3]), abs(r["state"][4]-1), abs(r["state"][5]))
                                                for r in raw["observations"]]}
        def ensemble_check(name, passed, **kw):
            check("short_reused_arithmetic_"+name, passed, **kw)
        fd, cross, controls = m.ensemble(cases, times, ensemble_check)
        for key, value in old_fd.items():
            check("short_saved_fd_exact_"+key, key in fd and m.equal(fd[key], value))
        check("short_saved_MF6_exact", cross["MF6_clock7"]["max_scaled"] == old_cross["MF6_clock7_scaled"])
        check("short_saved_baseline_exact", cross["baseline_fused"]["max_scaled"] == old_cross["baseline_fused_scaled"]
              and cross["baseline_fused"]["state6_binary64_equal"] is True)
        check("short_saved_gauge_exact_zero", cross["source_frame_GL_b0_gauge"]["max_absolute"] == 0)
        for new, old in zip(controls, old_controls):
            check("short_saved_control_exact_"+old["control"], all(k in new and m.equal(new[k], v) for k, v in old.items())
                  and new["full_scientific_pass"] is False and new["internal_numerical_gates_pass"] is False)
        details["short_reused_arithmetic"] = {"case_count": len(cases), "output_times": len(times),
            "fine_Richardson_max_absolute": fd["fine_Richardson_max_absolute"],
            "raw_fine_max_scaled": fd["raw_fine_max_scaled"],
            "MF6_clock7_scaled": cross["MF6_clock7"]["max_scaled"],
            "baseline_fused_scaled": cross["baseline_fused"]["max_scaled"],
            "omission_full_gaps": {r["control"]: r["full_vs_omitted_max_absolute"] for r in controls}}

        for label, data, prefix in (
                ("duplicate_json", b'{"x":1,"x":2}', "DUPLICATE_JSON_KEY:"),
                ("json_nan", b'{"x":NaN}', "NONFINITE_JSON_CONSTANT:"),
                ("json_inf", b'{"x":Infinity}', "NONFINITE_JSON_CONSTANT:"),
                ("json_overflow", b'{"x":1e999}', "NONFINITE_JSON_NUMBER")):
            rejects(label+"_rejected", lambda data=data: m.strict_json(data), prefix)
        rejects("comparison_empty_rejected", lambda: m.comparison([], []), "COMPARISON_SHAPE")
        rejects("comparison_shape_rejected", lambda: m.comparison([[1,2]], [[1]]), "COMPARISON_SHAPE")
        rejects("comparison_nan_rejected", lambda: m.comparison([[float("nan")]], [[1]]), "COMPARISON_NONFINITE")
        rejects("comparison_bool_rejected", lambda: m.comparison([[True]], [[1]]), "COMPARISON_NONFINITE")
        rejects("comparison_difference_overflow_rejected", lambda: m.comparison([[1e308]], [[-1e308]]),
                "COMPARISON_NONFINITE_DIFFERENCE")
        rejects("linear_zero_denominator_rejected", lambda: m.linear([[1]], [[1]], 1, -1, 0),
                "LINEAR_DENOMINATOR_OR_SHAPE")
        rejects("linear_ragged_rejected", lambda: m.linear([[1,2]], [[1]], 1, -1, 1),
                "LINEAR_NONFINITE_OR_SHAPE")
        observation = {"x": 0.0, "state": [0.0]*6}
        rejects("duplicate_observation_time_rejected", lambda: m.selected_states([observation, observation], [0.0]),
                "OBSERVATION_DOMAIN_OR_DUPLICATE")
        rejects("missing_observation_time_rejected", lambda: m.selected_states([observation], [1.0]),
                "MISSING_COMMON_OUTPUT_TIME")
        evidence.unchanged()
        check("all_observed_files_unchanged", True, files=len(evidence.files))
    except Exception as exc:
        error = type(exc).__name__+": "+str(exc)
        check("verification_completed", False, error=error)
    result = {"schema": "BASS_S12_C8_AGGREGATE_BOUNDED_VERIFICATION_V1",
        "status": "PASS_SCOPED_SAVED_DATA_ONLY" if checks and all(r["pass"] for r in checks) else "FAIL",
        "started_utc": started_utc, "ended_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "elapsed_seconds": time.monotonic()-started, "aggregate_sha256": args.aggregate_sha256,
        "checks_passed": sum(r["pass"] for r in checks), "checks_total": len(checks),
        "checks": checks, "details": details, "error": error,
        "evidence": evidence.files if evidence else {}, "solver_calls": 0, "projector_calls": 0,
        "compiler_calls": 0, "subprocess_calls": 0, "network_calls": 0,
        "completed_campaign_replays": 0, "extended_history_runs": 0,
        "actual_NCP_execution_status": "NOT_RUN", "production_receipt_chain_verified": False,
        "scope": "Published observer arithmetic on exact reused SHORT S12 bytes; actual extended input manifest and existing upstream source readback; malformed inputs rejected. No full production receipt chain, new histories, or independent C9 approval."}
    destination = args.out/"RETURN_VERIFY_AGGREGATE.json"
    with destination.open("x") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")
    print(json.dumps({k: result[k] for k in ("status", "checks_passed", "checks_total", "error", "elapsed_seconds")}))
    return 0 if result["status"].startswith("PASS_") else 1


if __name__ == "__main__":
    sys.exit(main())
