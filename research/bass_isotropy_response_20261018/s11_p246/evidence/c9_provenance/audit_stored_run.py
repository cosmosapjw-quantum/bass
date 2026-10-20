#!/usr/bin/env python3
"""Read-only C9 observer of S11 r1 stored evidence.

Never imports the projector or runner, invokes Rust, fits weights, or reruns a
history. Legendre moments below use the closed factorial polynomial, independent
of both implementations' recurrence. Git tree verification reconstructs Git tree
objects from the previously observed full recursive listing and anchors the root
to a fresh GitHub commit/tree read. The author implemented Rust, so this report
is independent of the root Python runner but not sole independent Rust approval.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
from decimal import Decimal, localcontext
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import struct
import sys

SOURCE = "7fb9b83cba01d37ce4cabbc4772527710601cd96"
TREE = "963a43f26df1f9c6f462b9df9a2c34cf99f525c9"
REL_UNIT = "research/bass_isotropy_response_20261018/s11_p246"
GATE = Fraction(3, 10**15)
CROSS = Fraction(1, 10**12)
read_files = {}

def read(path):
    data = path.read_bytes()
    read_files[str(path)] = {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
    return data

def obj(path):
    return json.loads(read(path))

def sha(data):
    return hashlib.sha256(data).hexdigest()

def git_object(kind, data):
    return hashlib.sha1(kind.encode() + b" " + str(len(data)).encode() + b"\0" + data).hexdigest()

def digest(values):
    return sha(b"".join(struct.pack("<d", float(x)) for x in values))

def legendre_closed(x, degree):
    x = Fraction(x)
    return sum((Fraction((-1)**j * math.factorial(2*degree-2*j),
                         2**degree * math.factorial(j) * math.factorial(degree-j)
                         * math.factorial(degree-2*j)) * x**(degree-2*j)
                for j in range(degree//2+1)), Fraction(0))

def exact_moments(mu, weights, order):
    return {"0": sum(map(Fraction, weights), Fraction(0))-1,
            **{str(n): sum((Fraction(w)*legendre_closed(m,n) for m,w in zip(mu,weights)),
                           Fraction(0)) for n in range(2,order+1,2)}}

def parse_stdin(text):
    tokens = text.split()
    order, size = int(tokens[0]), int(tokens[1])
    if len(tokens) != 2+2*size:
        raise ValueError("stdin token cardinality differs from its size")
    return order, [float(tokens[2+2*i]) for i in range(size)], [float(tokens[3+2*i]) for i in range(size)]

def reflected(values):
    return all(x == -y for x,y in zip(values, reversed(values)))

def tree_hash(entries):
    payload = b""
    for entry in sorted(entries, key=lambda e:e["path"].encode()+ (b"/" if e["type"]=="tree" else b"")):
        mode = entry["mode"].lstrip("0") or "0"
        payload += mode.encode()+b" "+entry["path"].encode()+b"\0"+bytes.fromhex(entry["sha"])
    return git_object("tree",payload)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.workspace.resolve()
    unit = root/"bass_work"/REL_UNIT
    run = unit/"evidence/run_r1"
    github = root/"bass_intake_github"
    here = Path(__file__).resolve().parent
    output = args.output.resolve()
    checks = []
    def check(name, condition, **evidence):
        checks.append({"id":name,"pass":bool(condition),**evidence})
    result = obj(run/"RETURN.json")
    executions = obj(run/"EXECUTIONS.json")
    rows = obj(run/"PROJECTIONS.json")
    fixed = obj(run/"FIXED_INPUTS.json")
    domains = obj(run/"DOMAIN_CONTROLS.json")
    certificate_domains = obj(run/"CERTIFICATE_DOMAIN_CONTROLS.json")
    responses = obj(run/"ANGULAR_RESPONSES.json")
    references = obj(run/"REFERENCE_VALUES.json")
    taylors = obj(run/"TAYLOR_COEFFICIENTS.json")
    small = obj(run/"SMALL_STRAIN_CHECKS.json")
    slopes = obj(run/"ASYMPTOTIC_SLOPES.json")
    source_manifest = obj(run/"SOURCE_MANIFEST.json")
    binding = obj(github/"STAGE2_EXECUTION_BINDING.json")
    stage2 = obj(github/"STAGE2_REMOTE_READBACK.json")
    stage2_summary = obj(github/"STAGE2_GIT_READBACK.json")
    local_manifest = obj(github/"STAGE2_LOCAL_MANIFEST.json")
    commit = obj(here/"commit_fresh.json")
    top_tree = obj(here/"tree_fresh.json")
    main_process = obj(github/"S11_MAIN_PROCESS_R1.json")
    main_stdout = read(github/main_process["stdout_file"])
    main_stderr = read(github/main_process["stderr_file"])
    main_summary = json.loads(main_stdout)
    check("source_commit_tree_identity",
          commit["sha"] == SOURCE and commit["tree"]["sha"] == TREE
          and binding["source_commit"] == SOURCE and binding["tree"] == TREE
          and result["source_commit"] == SOURCE and source_manifest["source_commit"] == SOURCE
          and stage2_summary == stage2["readback"]
          and stage2_summary["source_commit"] == SOURCE and stage2_summary["tree"] == TREE)
    check("fresh_root_tree_object_hash", not top_tree["truncated"] and top_tree["sha"] == TREE
          and tree_hash(top_tree["tree"]) == TREE)
    recursive = stage2["tree"]
    by_path = {e["path"]:e for e in recursive["tree"]}
    children = defaultdict(list)
    for entry in recursive["tree"]:
        path = PurePosixPath(entry["path"])
        parent = "" if str(path.parent) == "." else str(path.parent)
        children[parent].append({**entry,"path":path.name})
    tree_mismatches = []
    for parent, entries in children.items():
        expected = TREE if not parent else by_path[parent]["sha"]
        actual = tree_hash(entries)
        if actual != expected:
            tree_mismatches.append({"path":parent,"expected":expected,"actual":actual})
    check("recursive_git_tree_objects",
          recursive["sha"] == TREE and not recursive["truncated"]
          and len(recursive["tree"]) == len(by_path) == 2972
          and not tree_mismatches,
          entries=len(by_path),tree_objects=len(children),mismatches=tree_mismatches)
    top_from_recursive = [{k:v for k,v in e.items()} for e in recursive["tree"] if "/" not in e["path"]]
    check("fresh_root_matches_stored_recursive_root", top_from_recursive == top_tree["tree"])
    check("source_published_before_process",
          datetime.fromisoformat(commit["committer"]["date"].replace("Z","+00:00"))
          < datetime.fromisoformat(main_process["started_utc"])
          <= datetime.fromisoformat(result["completed_at_utc"])
          <= datetime.fromisoformat(main_process["ended_utc"]))
    check("manifest_hash_chain",
          binding["readback_sha256"] == sha(read(github/"STAGE2_REMOTE_READBACK.json"))
          and source_manifest["published_binding_sha256"] == sha(read(github/"STAGE2_EXECUTION_BINDING.json"))
          and result["source_manifest_sha256"] == sha(read(run/"SOURCE_MANIFEST.json"))
          and source_manifest["published_binding_matches"] is True)
    bound = {f["path"]:f for f in binding["files"]}
    local_bound = {f["path"]:f for f in source_manifest["files"]}
    check("execution_source_manifest_cardinality",
          len(bound) == len(binding["files"]) == len(local_bound) == 18
          and set(bound) == set(local_bound))
    for name, expected in bound.items():
        data = read(unit/name)
        tree_entry = by_path[REL_UNIT+"/"+name]
        check("bound_source:"+name,
              len(data) == expected["bytes"] == local_bound[name]["bytes"] == tree_entry["size"]
              and sha(data) == expected["sha256"] == local_bound[name]["sha256"]
              and git_object("blob",data) == expected["git_blob"] == tree_entry["sha"])
    full_binding_ok = all(by_path[f["path"]]["sha"] == f["git_blob"]
                          and by_path[f["path"]]["size"] == f["bytes"]
                          for f in local_manifest["files"])
    check("stage2_all_published_manifest_entries_match_tree", full_binding_ok,
          file_count=len(local_manifest["files"]))
    check("stage2_changed_path_scope",
          stage2_summary["no_deletions"] is True and stage2_summary["unexpected_changed_paths"] == []
          and all(f["path"] == "research/bass_isotropy_response_20261018/DAG.json"
                  or f["path"].startswith(REL_UNIT+"/") for f in stage2_summary["changed_files"]),
          scope="Recorded stage2 changed-path list; not a fresh parent-tree diff.")
    expected_command = ["python3",str(unit/"run_validation.py"),"--rustc",
                        str(root/"runtime_s11/rust/bin/rustc"),"--source-commit",SOURCE,
                        "--published-file-manifest",str(github/"STAGE2_EXECUTION_BINDING.json"),
                        "--output",str(run)]
    check("main_command_streams_exit",
          main_process["command"] == expected_command and main_process["exit_code"] == 0
          and main_process["timed_out"] is False and main_stderr == b""
          and sha(main_stdout) == main_process["stdout_sha256"]
          and sha(main_stderr) == main_process["stderr_sha256"]
          and main_summary == {k:result[k] for k in main_summary})
    check("main_recorded_resource_limits",
          0 < main_process["elapsed_seconds"] < main_process["limits"]["timeout_seconds"] <= 1800
          and main_process["limits"]["science_processes"] == 1
          and main_process["limits"]["address_space_bytes"] <= 16*2**30
          and main_process["main_child_peak_RSS_KiB"] == result["max_individual_child_RSS_KiB"],
          elapsed_seconds=main_process["elapsed_seconds"],
          peak_individual_child_RSS_KiB=main_process["main_child_peak_RSS_KiB"],
          RSS_limit="Observed maximum individual child RSS, not a simultaneous process-tree peak.")
    check("reported_101_checks_consistent",
          result["status"] == "PASS_SCOPED" and result["check_count"] == result["pass_count"] == 101
          and len(result["checks"]) == len({c["id"] for c in result["checks"]}) == 101
          and all(c["pass"] is True for c in result["checks"]) and result["failures"] == [])
    check("zero_replay_recorded",
          all(main_process[k] == 0 for k in ("completed_campaigns_replayed","native_history_replays",
                                             "ODE_runs","benchmark_runs","NCP_runs"))
          and all(result[k] == 0 for k in ("old_campaign_replays","old_native_history_replays",
                                           "optimization_cycles","NCP_runs")))
    probe, build = obj(run/"COMPILER.json"), obj(run/"BUILD.json")
    binary = run/"p246_projector"
    binary_bytes = read(binary)
    check("compiler_build_binary_identity",
          executions[:2] == [probe,build]
          and probe["command"] == [str(root/"runtime_s11/rust/bin/rustc"),"-vV"]
          and "release: 1.94.1\n" in probe["stdout"]
          and "commit-hash: e408947bfd200af42db322daf0fadfe7e26d3bd1\n" in probe["stdout"]
          and probe["exit_code"] == build["exit_code"] == 0
          and probe["stderr"] == build["stderr"] == build["stdout"] == ""
          and build["command"] == [str(root/"runtime_s11/rust/bin/rustc"),"--edition=2021",
                                    "-O","-D","warnings",str(unit/"rust/cli.rs"),"-o",str(binary)]
          and result["binary_sha256"] == sha(binary_bytes),
          binary_sha256=sha(binary_bytes),binary_bytes=len(binary_bytes))
    calls = {x["id"]:x for x in executions[2:]}
    check("subprocess_execution_completeness",
          len(executions) == 26 and len(calls) == 24
          and all(x["execution_status"] == "COMPLETED" and isinstance(x["exit_code"],int)
                  and 0 <= x["elapsed_seconds"] <= x["timeout_seconds"] == 120 for x in executions))
    fixed_by_id = {c["id"]:c for c in fixed}
    expected_case_names = ["dyadic_uniform","dyadic_biased_prior","P24_only_support",
                           "b9_n64","b9_n128","b9_n256","b6_n64"]
    check("fixed_case_identities", [c["id"] for c in fixed] == expected_case_names
          and len(fixed_by_id) == 7
          and fixed[0]["mu"] == [-1.,-.75,-.5,0.,.5,.75,1.]
          and fixed[0]["prior"] == [1.]*7
          and fixed[1]["mu"] == fixed[0]["mu"] and fixed[1]["prior"] == [1.,2.,3.,4.,3.,2.,1.]
          and fixed[2]["mu"] == [-1.,-.5,-.25,0.,.25,.5,1.] and fixed[2]["prior"] == [1.]*7)
    for name in expected_case_names[3:]:
        source_input = obj(unit/"inputs"/(name+"_birth11_input.json"))
        case = fixed_by_id[name]
        check("archived_input_identity:"+name, digest(case["mu"]) == digest(source_input["mu"])
              and digest(case["prior"]) == digest(source_input["prior"]))
    expected_ids = [name+"_P"+str(order) for name in expected_case_names for order in (4,6)]
    check("projection_ids_complete_unique", [r["id"] for r in rows] == expected_ids)
    positive = []
    recomputed = []
    for row in rows:
        identity, order = row["id"], row["order"]
        case = fixed_by_id[row["case"]]
        mu, prior = case["mu"],case["prior"]
        call = calls[identity]
        parsed_order, parsed_mu, parsed_prior = parse_stdin(call["stdin"])
        check(identity+":raw_stdin_source_identity",
              parsed_order == order and digest(parsed_mu) == digest(mu)
              and digest(parsed_prior) == digest(prior)
              and row["input_mu_sha256"] == digest(mu) and row["input_prior_sha256"] == digest(prior)
              and call["command"] == [str(binary),"--isotropic-birth"])
        native = json.loads(call["stdout"])
        check(identity+":raw_stdout_identity", native == row["rust"] and call["stderr"] == "")
        infeasible = identity in ("P24_only_support_P6","b9_n64_P6")
        if infeasible:
            negative = [f for f in row["support"]["facets"] if Fraction(f["slack"]["exact"]) < 0]
            check(identity+":expected_infeasible_retained",
                  call["exit_code"] == 3 and native["status"] == "INFEASIBLE_SUPPORT"
                  and row["python"]["status"] == row["registered_support"] == "INFEASIBLE_SUPPORT"
                  and len(negative)>0 and "weights" not in native,
                  minimum_slack_exact=row["support"]["minimum_slack"]["exact"],
                  negative_facet_count=len(negative),native_message=native.get("message"))
            continue
        positive.append(identity)
        check(identity+":provisional_process_success",
              call["exit_code"] == 0 and native["status"] == "PROJECTED_NEEDS_EXACT_CERTIFICATE"
              and native["order"] == order and row["python"]["status"] == "PROJECTED"
              and row["registered_support"] == "STRICT_INTERIOR"
              and len(native["lambda"]) == order//2 and len(native["residuals"]) == order//2+1)
        for implementation,weights,certificate in (
            ("rust",native["weights"],row["rust_exact_certificate"]),
            ("python",row["python"]["weights"],row["python"]["certificate"])):
            residuals = exact_moments(mu,weights,order)
            invariant = (len(weights)==len(mu) and all(math.isfinite(w) and w>0 for w in weights)
                         and reflected(mu) and weights==list(reversed(weights))
                         and all(mu[i]<mu[i+1] for i in range(len(mu)-1)))
            stored = {"0":Fraction(certificate["normalization"]["exact"]),
                      **{key:Fraction(value["exact"]) for key,value in certificate["moments"].items()}}
            check(identity+":"+implementation+"_independent_exact_polynomial_certificate",
                  invariant and all(abs(v)<=GATE for v in residuals.values())
                  and residuals == stored and certificate["status"] == "PASS_SCOPED"
                  and Fraction(certificate["gate_exact"]) == GATE
                  and certificate["mu_sha256"] == digest(mu)
                  and certificate["weight_sha256"] == digest(weights)
                  and certificate["max_abs_residual"] == float(max(map(abs,residuals.values())))
                  and certificate["minimum_weight"] == min(weights))
            recomputed.append({"id":identity,"implementation":implementation,
                               "residuals_exact":{key:str(value) for key,value in residuals.items()},
                               "max_abs_residual":float(max(map(abs,residuals.values()))),
                               "minimum_weight":min(weights),"weight_sha256":digest(weights)})
        difference = max(abs(Fraction(a)-Fraction(b)) for a,b in zip(native["weights"],row["python"]["weights"]))
        check(identity+":independent_cross_weights",
              difference<=CROSS and float(difference)==row["cross_weight_max_abs"],
              max_abs=float(difference),exact=str(difference))
    beta = [Fraction(286,945),Fraction(32,105),Fraction(2048,6615),Fraction(61,735)]
    z = [Fraction(0),Fraction(1,4),Fraction(9,16),Fraction(1)]
    ideal = [beta[3]/2,beta[2]/2,beta[1]/2,beta[0],beta[1]/2,beta[2]/2,beta[3]/2]
    check("fixed_rational_orbit_masses",
          all(x>0 for x in beta)
          and [sum((w*x**k for w,x in zip(beta,z)),Fraction(0)) for k in range(4)]
              == [Fraction(1,2*k+1) for k in range(4)],
          exact_orbit_masses=list(map(str,beta)))
    rational_metrics = []
    for row in rows:
        if row["case"].startswith("dyadic_") and row["order"]==6:
            for implementation in ("python","rust"):
                error = max(abs(Fraction(w)-i) for w,i in zip(row[implementation]["weights"],ideal))
                check(row["id"]+":"+implementation+"_fixed_rational_weights",
                      error <= (Fraction(1,10**16) if implementation=="python" else CROSS),
                      exact_max_abs=str(error),max_abs=float(error))
                rational_metrics.append({"id":row["id"],"implementation":implementation,
                                         "max_abs":float(error),"exact_max_abs":str(error)})
    expected_python = {"not_isotropic":"NOT_ISOTROPIC_BIRTH","asymmetric_mu":"REFLECTION_SOURCE_REQUIRED",
        "asymmetric_prior":"REFLECTION_PRIOR_REQUIRED","zero_prior":"PRIOR_POSITIVITY_DOMAIN",
        "negative_prior":"PRIOR_POSITIVITY_DOMAIN","nonfinite":"ANGULAR_INPUT_DOMAIN",
        "out_of_range":"ANGULAR_INPUT_DOMAIN","duplicate_mu":"ANGULAR_ORDER_DOMAIN",
        "rank_deficient":"INFEASIBLE_AFFINE_SUPPORT","invalid_order":"ORDER_DOMAIN"}
    check("domain_case_completeness", len(domains)==len(expected_python)==10
          and {r["id"] for r in domains}==set(expected_python))
    for row in domains:
        name = row["id"]
        call = calls["domain_"+name]
        native = json.loads(call["stdout"])
        expected_exit = 2 if name=="not_isotropic" else 3
        expected_status = ("NOT_ISOTROPIC_BIRTH" if name=="not_isotropic"
                           else "FEASIBILITY_UNRESOLVED" if name=="rank_deficient" else "INVALID_INPUT")
        check("domain:"+name,
              {k:v for k,v in call.items() if k!="id"} == row["rust"]
              and row["python_status"] == expected_python[name] == row["expected_python_status"]
              and native["status"] == expected_status == row["expected_rust_status"]
              and call["exit_code"] == expected_exit == row["expected_rust_exit"]
              and call["stderr"] == ""
              and call["command"] == [str(binary)]+([] if name=="not_isotropic" else ["--isotropic-birth"]))
    dup_order, dup_mu, dup_prior = parse_stdin(calls["domain_duplicate_mu"]["stdin"])
    check("duplicate_control_remains_full_rank",
          dup_order==6 and dup_mu==[-1.,-.75,-.5,-.5,0.,.5,.5,.75,1.]
          and dup_prior==[1.]*9 and len({Fraction(m)**2 for m in dup_mu})==4)
    expected_certificate = {"certificate_invalid_order":"ORDER_DOMAIN","certificate_fractional_order":"ORDER_DOMAIN",
       "certificate_outside_exact_moments":"ANGULAR_INPUT_DOMAIN","certificate_duplicate_mu":"ANGULAR_ORDER_DOMAIN",
       "certificate_nonfinite_weight":"CERTIFICATE_NONFINITE"}
    check("certificate_domain_results", len(certificate_domains)==5
          and {r["id"]:r["status"] for r in certificate_domains}==expected_certificate
          and all(r["status"]==r["expected_status"] for r in certificate_domains))
    strains = {Fraction(k,40) for k in range(-24,25)} | {Fraction(s,d) for s in (-1,1) for d in (1000,2000,4000)}
    response_keys = [(r["id"],Fraction(r["d"])) for r in responses]
    expected_response_keys = {(identity,d) for identity in positive for d in strains}
    check("full_registered_output_cardinality",
          len(rows)==14 and len(positive)==12 and len(responses)==len(set(response_keys))==660
          and set(response_keys)==expected_response_keys
          and len(references)==55 and {Fraction(d) for d in references}==strains
          and len(taylors)==12 and {r["id"] for r in taylors}==set(positive)
          and len(small)==9 and len(slopes)==6)
    references_by_d = {Fraction(d):v for d,v in references.items()}
    with localcontext() as context:
        context.prec = 80
        response_integrity = all(
            Decimal(r["A"]).is_finite() and Decimal(r["A_iso"]).is_finite()
            and r["A_iso"] == references_by_d[Fraction(r["d"])]["A"]
            and Decimal(r["signed_error"])==Decimal(r["A"])-Decimal(r["A_iso"])
            for r in responses)
        check("stored_response_arithmetic_and_reference_identity",response_integrity)
        small_integrity = all(
            Decimal(r["relative_error"])==abs((Decimal(r["measured_coefficient"])
                       -Decimal(r["exact_stored_coefficient"]))/Decimal(r["exact_stored_coefficient"]))
            and Decimal(r["relative_error"])<=Decimal(".02") for r in small)
        check("stored_small_strain_ratio_arithmetic",small_integrity)
        small_by_key = {(r["id"],r["d"]):r for r in small}
        slope_integrity = True
        for r in slopes:
            a,b = [small_by_key[r["id"],d] for d in r["d_pair"]]
            value = Decimal(r["registered_power"])+abs(Decimal(a["measured_coefficient"])
                      /Decimal(b["measured_coefficient"])).ln()/Decimal(2).ln()
            slope_integrity = slope_integrity and value==Decimal(r["observed_order"])
        check("stored_asymptotic_slope_arithmetic",slope_integrity)
    row_by_id = {r["id"]:r for r in rows}
    for taylor in taylors:
        row = row_by_id[taylor["id"]]
        mu = fixed_by_id[row["case"]]["mu"]
        weights = row["python"]["weights"]
        moments = {str(n):sum((Fraction(w)*legendre_closed(m,n) for m,w in zip(mu,weights)),Fraction(0))
                   for n in (2,4,6,8,10,12)}
        check(taylor["id"]+":higher_stored_moment_identity",
              all(moments[n]==Fraction(taylor["moments"][n]["exact"]) for n in moments))
    unchanged = []
    for name, identity in read_files.items():
        data = Path(name).read_bytes()
        if len(data)!=identity["bytes"] or sha(data)!=identity["sha256"]:
            unchanged.append(name)
    check("audited_inputs_unchanged",not unchanged,changed=unchanged)
    failure = [c for c in checks if not c["pass"]]
    audit = {
        "schema":"BASS_S11_C9_STORED_PROVENANCE_AUDIT_V1",
        "status":"PASS_SCOPED" if not failure else "FAIL",
        "created_at_utc":datetime.now(timezone.utc).isoformat(),
        "source_commit":SOURCE,"tree":TREE,
        "reviewer":"/root/new_branch_intake",
        "independence":{
            "authored_Rust_projector_and_CLI":True,
            "authored_root_Python_reference_or_validation_runner":False,
            "scope":"Independent source/process/output provenance observer and independent exact polynomial checks of stored weights.",
            "not_sole_independent_Rust_implementation_approval":True,
            "projector_imports":0,"Rust_or_Python_solver_reruns":0,
            "compiler_invocations":0,"old_campaign_replays":0,"ODE_runs":0,"NCP_runs":0,
            "limits":["Does not reproduce OS process execution; it audits retained raw process records.",
                      "Python solver output is retained by its main runner, not a separately rerun process.",
                      "No new continuum integration, spectral deposition or native history is executed.",
                      "The stage2 changed-path scope check uses its retained list, not a fresh parent-tree diff."]
        },
        "metrics":{
            "check_count":len(checks),"pass_count":len(checks)-len(failure),
            "original_runner_check_count":101,"source_files_bound":18,
            "published_manifest_entries":len(local_manifest["files"]),
            "recursive_tree_entries":len(by_path),"git_tree_objects_rehashed":len(children),
            "subprocess_records":26,"compiler_and_build_records":2,"projection_cli_records":14,
            "positive_pairs":12,"expected_infeasible_pairs":2,"domain_cli_records":10,
            "standalone_certificate_domain_controls":5,
            "independent_exact_output_certificates":len(recomputed),
            "stored_response_values":660,
            "main_process_elapsed_seconds":main_process["elapsed_seconds"],
            "max_individual_child_RSS_KiB":main_process["main_child_peak_RSS_KiB"],
            "binary_sha256":sha(binary_bytes),
            "max_rust_exact_residual":max(r["max_abs_residual"] for r in recomputed if r["implementation"]=="rust"),
            "max_python_exact_residual":max(r["max_abs_residual"] for r in recomputed if r["implementation"]=="python"),
            "max_cross_implementation_weight_difference":max(r.get("cross_weight_max_abs",0) for r in rows),
        },
        "rational_controls":rational_metrics,
        "recomputed_exact_certificates":recomputed,
        "input_manifest":read_files,
        "checks":checks,"failures":failure,
    }
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open("x") as stream:
        json.dump(audit,stream,indent=2,ensure_ascii=False,allow_nan=False)
        stream.write("\n")
    print(json.dumps({"status":audit["status"],**audit["metrics"],"failures":failure},ensure_ascii=False))
    return 0 if not failure else 1

if __name__ == "__main__":
    raise SystemExit(main())
