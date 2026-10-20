#!/usr/bin/env python3
"""Read-only final S11 result/tree/data audit. No solver, build, plot or upload."""
from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal
from fractions import Fraction
import hashlib, json, posixpath, re
from pathlib import Path, PurePosixPath
import argparse

SOURCE="7fb9b83cba01d37ce4cabbc4772527710601cd96"
RESULT="85d5833b4486d14855b84a9d967f5819788d05e5"
TREE="fd3e994212059228501e26f7bf3d3b96462ba1d5"
UNIT_REL="research/bass_isotropy_response_20261018/s11_p246"
def sha(b): return hashlib.sha256(b).hexdigest()
def git_hash(kind,b): return hashlib.sha1(kind.encode()+b" "+str(len(b)).encode()+b"\0"+b).hexdigest()
def tree_hash(entries):
    b=b""
    for e in sorted(entries,key=lambda x:x["path"].encode()+(b"/" if x["type"]=="tree" else b"")):
        b+=(e["mode"].lstrip("0") or "0").encode()+b" "+e["path"].encode()+b"\0"+bytes.fromhex(e["sha"])
    return git_hash("tree",b)
def main():
    p=argparse.ArgumentParser();p.add_argument("--workspace",type=Path,required=True);p.add_argument("--output",type=Path,required=True);args=p.parse_args()
    root=args.workspace.resolve();here=Path(__file__).resolve().parent;unit=root/"bass_work"/UNIT_REL
    read_files={}
    def raw(p):
        b=p.read_bytes();read_files[str(p)]={"bytes":len(b),"sha256":sha(b)};return b
    def obj(p):return json.loads(raw(p))
    checks=[]
    def check(name,passed,**details):checks.append({"id":name,"pass":bool(passed),**details})
    commit=obj(here/"result_commit_fresh.json");top=obj(here/"result_tree_fresh.json")
    stage3=obj(root/"bass_intake_github/STAGE3_REMOTE_READBACK.json")
    prior=obj(root/"bass_intake_github/STAGE2_REMOTE_READBACK.json")
    pub=obj(root/"bass_intake_github/STAGE3_LOCAL_MANIFEST.json")
    binding=obj(root/"bass_intake_github/STAGE2_EXECUTION_BINDING.json")
    metadata=obj(root/"bass_intake_github/STAGE3_GIT_READBACK.json")
    tree=stage3["tree"];entries=tree["tree"];lookup={e["path"]:e for e in entries}
    check("fresh_result_parent_tree",commit["sha"]==RESULT and commit["tree"]["sha"]==TREE and [p["sha"] for p in commit["parents"]]==[SOURCE] and top["sha"]==TREE and tree_hash(top["tree"])==TREE and not top["truncated"])
    check("fresh_commit_matches_retained_remote_commit",commit==stage3["commit"])
    children=defaultdict(list)
    for e in entries:
        path=PurePosixPath(e["path"]);parent="" if str(path.parent)=="." else str(path.parent)
        children[parent].append({**e,"path":path.name})
    mismatch=[]
    for name,contents in children.items():
        expected=TREE if not name else lookup[name]["sha"]
        if tree_hash(contents)!=expected:mismatch.append(name)
    check("all_result_git_tree_objects",len(entries)==len(lookup)==3056 and not tree["truncated"] and not mismatch and tree["sha"]==TREE,objects=len(children),mismatches=mismatch)
    check("fresh_root_matches_recursive_root",[e for e in entries if "/" not in e["path"]]==top["tree"])
    bad=[]
    for f in pub["files"]:
        b=raw(root/"bass_work"/f["path"]);e=lookup[f["path"]]
        if not(len(b)==f["bytes"]==e["size"] and sha(b)==f["sha256"] and git_hash("blob",b)==f["git_blob"]==e["sha"]):bad.append(f["path"])
    check("all120_published_payload_bytes_and_blobs",len(pub["files"])==pub["payload_count"]==120 and not bad,failed_paths=bad,payload_bytes=sum(f["bytes"] for f in pub["files"]))
    old_blobs={e["path"]:e for e in prior["tree"]["tree"] if e["type"]=="blob"}
    new_blobs={e["path"]:e for e in entries if e["type"]=="blob"}
    removed=sorted(set(old_blobs)-set(new_blobs))
    added=sorted(set(new_blobs)-set(old_blobs))
    modified=sorted(p for p in old_blobs.keys()&new_blobs.keys() if old_blobs[p]["sha"]!=new_blobs[p]["sha"])
    unexpected=[p for p in added+modified if p!="research/bass_isotropy_response_20261018/DAG.json" and not p.startswith(UNIT_REL+"/")]
    check("independent_parent_result_blob_diff_scope",not removed and not unexpected and len(added)+len(modified)==77,added_files=len(added),modified_files=len(modified),removed_paths=removed,unexpected_paths=unexpected)
    check("recorded_stage3_scope_agrees",metadata["result_commit"]==RESULT and metadata["tree"]==TREE and metadata["source_commit"]==SOURCE and metadata["unexpected_paths"]==[] and metadata["removed_paths"]==[] and metadata["old_science_source_or_owner_files_changed"] is False)
    source_mismatches=[]
    for f in binding["files"]:
        b=raw(unit/f["path"]);new=new_blobs[UNIT_REL+"/"+f["path"]]
        if sha(b)!=f["sha256"] or git_hash("blob",b)!=f["git_blob"] or new["sha"]!=f["git_blob"]:source_mismatches.append(f["path"])
    check("all18_execution_source_inputs_preserved",len(binding["files"])==18 and not source_mismatches,failed_paths=source_mismatches)
    narrative=raw(unit/"RESULTS_KO.md").decode();ledger=obj(unit/"RESULT_LEDGER.json")
    mdtargets=re.findall(r"!?(?:\[[^\]]*\])\(([^)]+)\)",narrative)
    relative=[t.split("#",1)[0] for t in mdtargets if not t.startswith(("http://","https://","#"))]
    md_missing=[t for t in relative if posixpath.normpath(posixpath.join(UNIT_REL,t)) not in lookup]
    check("all_relative_narrative_evidence_links_exist",not md_missing,links=len(relative),unique_links=len(set(relative)),missing=md_missing)
    def strings(value):
        if isinstance(value,str):yield value
        elif isinstance(value,dict):
            for v in value.values():yield from strings(v)
        elif isinstance(value,list):
            for v in value:yield from strings(v)
    ledger_paths=[s for s in strings(ledger) if not s.startswith("http") and re.fullmatch(r"[A-Za-z0-9_./-]+\.(?:json|md|png|csv|py)",s)]
    ledger_missing=[t for t in ledger_paths if posixpath.normpath(posixpath.join(UNIT_REL,t)) not in lookup]
    check("all_ledger_artifact_links_exist",not ledger_missing,links=len(ledger_paths),unique_links=len(set(ledger_paths)),missing=ledger_missing)
    run=obj(unit/"evidence/run_r1/RETURN.json");proj=obj(unit/"evidence/run_r1/PROJECTIONS.json")
    process=obj(unit/"evidence/run_r1/PROCESS_RECEIPT.json");physics=obj(unit/"evidence/c9_physics/RETURN.json")
    provenance=obj(unit/"evidence/c9_provenance/AUDIT_R1.json");stats=obj(unit/"evidence/figure/FIGURE_STATS.json")
    check("ledger_source_and_binary_identity",ledger["immutable_identities"]["main_source_commit"]==SOURCE and ledger["immutable_identities"]["main_source_tree"]==binding["tree"] and ledger["immutable_identities"]["main_binary_sha256"]==run["binary_sha256"])
    check("ledger_main_process_record",all(ledger["admitted_main_execution"][lk]==process[pk] for lk,pk in [("started_at_utc","started_utc"),("ended_at_utc","ended_utc"),("elapsed_seconds","elapsed_seconds"),("exit_code","exit_code"),("timed_out","timed_out")]) and ledger["admitted_main_execution"]["stderr_bytes"]==0 and ledger["admitted_main_execution"]["subprocess_records"]==26)
    verification=ledger["separate_verification_sets"]
    check("separate_verification_sets_unchanged",[v["pass"] for v in verification]==[101,25,235,152] and [v["total"] for v in verification]==[101,25,235,152] and run["pass_count"]==101 and provenance["metrics"]["pass_count"]==152 and "not summed" in ledger["verification_count_policy"])
    positive=[p for p in proj if p["python"]["status"]=="PROJECTED"]
    check("ledger_projection_extrema",len(proj)==ledger["projection_matrix"]["pair_rows"]==14 and len(positive)==ledger["projection_matrix"]["strict_interior_positive_pairs"]==12 and max(p["rust_exact_certificate"]["max_abs_residual"] for p in positive)==ledger["projection_matrix"]["largest_Rust_exact_residual"] and max(p["python"]["certificate"]["max_abs_residual"] for p in positive)==ledger["projection_matrix"]["largest_Python_exact_residual"] and max(p["cross_weight_max_abs"] for p in positive)==ledger["projection_matrix"]["largest_cross_implementation_weight_difference"])
    failures={r["id"]:r for r in proj if r["python"]["status"]!="PROJECTED"}
    check("both_support_failures_preserved",len(failures)==2 and all(Fraction(r["minimum_exact_slack"])==Fraction(failures[r["id"]]["support"]["minimum_slack"]["exact"]) and r["admissible_positive_P246_weights"] is False for r in ledger["preserved_support_failures"]))
    fix=next(p for p in proj if p["id"]=="b9_n64_P4");scope=ledger["S8_pointwise_repair"]
    check("S8_pointwise_only_and_identity",scope["original_history_rerun"] is False and scope["original_failed_history_receipt_retained"] is True and scope["mu_sha256_le_f64"]==fix["input_mu_sha256"] and scope["python_minimum_weight"]==min(fix["python"]["weights"]) and scope["rust_minimum_weight"]==min(fix["rust"]["weights"]) and "POINTWISE" in scope["status"])
    gm={r["id"]:r for r in stats["grid_errors"]}
    check("all12_ledger_grid_maxima_match",len(ledger["finite_strain_diagnostics"]["grid_maxima"])==12 and all(r["max_abs_bias"]==gm[r["id"]]["max_abs_angular_bias"] and r["argmax_d"]==gm[r["id"]]["argmax_d"] for r in ledger["finite_strain_diagnostics"]["grid_maxima"]))
    counter=ledger["finite_strain_diagnostics"]["preserved_counterexample"]
    check("finite_strain_worsening_preserved",counter["P246_over_P24_absolute_bias_ratio"]==stats["dyadic_P246_vs_P24_worst_bias_ratio"]==1.54913989382294 and counter["P24_signed_bias"]==gm["dyadic_uniform_P4"]["signed_worst_bias"] and counter["P246_signed_bias"]==gm["dyadic_uniform_P6"]["signed_worst_bias"] and ledger["finite_strain_diagnostics"]["monotone_P246_improvement_claim"] is False)
    check("author_role_distinction_and_historical_pending_time", "authored Rust" in verification[-1]["independence"] and "not sole independent Rust" in verification[-1]["independence"] and "did not author" in verification[-2]["independence"] and ledger["publication_and_delivery"]["result_commit_recorded_here"] is False and ledger["publication_and_delivery"]["original_S10_delivery_status"]=="COMPLETE_REUSED" and "status_at_results_authoring" in ledger["publication_and_delivery"])
    gate=ledger["gates"]
    check("moment_gates_unchanged",all(Fraction(gate[k])==Fraction(3,10**15) for k in ("normalization_exact","P2_exact_unchanged","P4_exact_unchanged","P6_exact_new")) and gate["diagnostic_gates_do_not_replace_moment_gate"] is True)
    old=ledger["reused_completed_evidence"]
    check("old_campaign_evidence_performance_and_delivery_preserved",old["S9_fixed_histories"]==8 and [(old[k]["pass"],old[k]["total"]) for k in ("S10_targeted","S10_kernel","S10_representative_RAW_scientific_identity","S10_science","S10_independent_review")]==[(11,11),(108,108),(24,24),(68,68),(155,155)] and old["closed_MF_speedup_rounded"]==2.973 and old["FLRW_MF_speedup_rounded"]==4.115 and old["closed_small"]["decision"]=="GAIN_UNCERTAIN" and old["changing_n16_cohort2_speedup"]==0.9498173837599284 and old["original_delivery"]["ZIP_count"]==9 and old["original_delivery"]["ZIP_total_bytes"]==4399983 and old["original_delivery"]["payload_entries_with_duplicates"]==383)
    remaining={r["id"]:r["status"] for r in ledger["remaining_obligations"]}
    check("remaining_physics_obligations_and_scope",remaining=={"actual_MD14_and_native_shared_Q":"OPEN","evolving_reactive_full_finite_bin_spectral_history":"OPEN","broader_finite_d_angular_higher_moments":"OPEN","new_Rust_full_birth_memory_parameter_tangent":"OPEN","S8_history":"HISTORICAL_FAILURE_PRESERVED"} and ledger["limited_source_deposition_fact"]["value"]=="5.369926725506957e-12" and ledger["limited_source_deposition_fact"]["full_spectral_history_convergence_claim"] is False and all(ledger["resource_and_scope_counters"][k] is False for k in ("REI_production_admission","full_EoR_admission","merge_admission")))
    changes=[p for p,ident in read_files.items() if sha(Path(p).read_bytes())!=ident["sha256"]]
    check("reviewed_inputs_unchanged",not changes,changed=changes)
    failed=[c for c in checks if not c["pass"]]
    report={"schema":"BASS_S11_FINAL_RESULT_TREE_FACTUAL_AUDIT_V1","status":"PASS_SCOPED" if not failed else "FAIL","created_utc":datetime.now(timezone.utc).isoformat(),"reviewer":"/root/new_branch_intake","source_commit":SOURCE,"result_commit":RESULT,"result_tree":TREE,"check_count":len(checks),"pass_count":len(checks)-len(failed),"read_only":True,"new_solver_compile_history_plot_or_Drive_calls":0,"scope":"Stored result prose/ledger facts, complete published payload hashes, independent source-to-result Git blob diff, rooted result tree, and artifact links. Cloud delivery state is outside this result-commit approval.","independence_limit":"Reviewer authored Rust but not result documents, plot, or root Python runner. Not sole independent Rust implementation approval.","manual_narrative_review":"Entire RESULTS_KO.md and RESULT_LEDGER.json read. No unsupported scientific expansion or regression of prior evidence found; S8pointwise, support failures, finite-d worsening, author roles and remaining physical obligations retained.","checks":checks,"failures":failed,"input_manifest":read_files}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open("x") as f:json.dump(report,f,indent=2,ensure_ascii=False);f.write("\n")
    print(json.dumps({"status":report["status"],"check_count":len(checks),"pass_count":len(checks)-len(failed),"tree_entries":len(entries),"tree_objects":len(children),"payload_files":len(pub["files"]),"added_files":len(added),"modified_files":len(modified),"narrative_links":len(relative),"ledger_links":len(ledger_paths),"failures":failed},ensure_ascii=False))
    return 0 if not failed else 1
if __name__=="__main__":raise SystemExit(main())
