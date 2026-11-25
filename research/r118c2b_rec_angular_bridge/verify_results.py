"""Verify scoped R118-C2B evidence; --raw additionally checks original bytes."""
import argparse, collections, csv, gzip, hashlib, json, pathlib, re, math
p=argparse.ArgumentParser(); p.add_argument("--raw",action="store_true"); args=p.parse_args()
d=pathlib.Path(__file__).resolve().parent
r=json.loads((d/"RESULTS.json").read_text()); s=json.loads((d/"SOURCE_RECEIPT.json").read_text())
cs=r["cases"]; good=[c for c in cs if c["status"]=="PASS_SCOPED"]; bad=[c for c in cs if c["status"]=="COUNTEREXAMPLE_VERIFIED"]
assert len(cs)==32 and len(good)==28 and len(bad)==4 and all(c["returncode"]==0 for c in cs)
assert all(c["dt_s"]>0 and c["run"]["implicit_status"]=="PASS" for c in good)
assert all(c["dt_s"]==0 and c["metrics"]["negative_gain_target"]<-2e-8 for c in bad)
assert {c["adversarial"]["floor"] for c in bad}=={1e-8,1e-12,1e-16,1e-20}
def maxkey(rows,section,k):
    vals=[c[section][k] for c in rows if k in c[section] and c[section][k] is not None]
    assert vals and all(math.isfinite(v) for v in vals)
    return max(abs(v) for v in vals)
metrics={k:maxkey(cs,"metrics",k) for k in ("action_rel","boundary_rel","action_gross_scaled","boundary_gross_scaled","jvp_rel","boundary_jvp_rel","q_h_scaled","q_n_scaled","clock_rel","doppler_rel","number_scaled","direction_abs","drift_abs_over_H","source_be_relative","source_updated_rel","packet_increment_rel","bass_occupation_integral_rel","independent_implicit_residual")}
assert all(v<2e-10 for v in metrics.values()),metrics
runs={k:maxkey(good,"run",k) for k in ("gram_defect","frame_roundtrip","force_relative_defect","equilibrium_action_max","implicit_residual","implicit_number_defect","implicit_iterations","implicit_krylov")}
assert all(runs[k]<2e-10 for k in runs if k not in ("implicit_iterations","implicit_krylov"))
assert all(c["run"]["entropy_rate"]<=1e-20 and c["run"]["implicit_free_energy_change"]<=0 for c in good if not c["packets"])
bb=[c for c in good if c["bass"]]; pp=[c for c in good if c["packets"]]
assert len(bb)==15 and len(pp)==3 and len({c["bass"][0] for c in bb})==13
assert {c["case"] for c in pp}=={"interface_z1300","interface_z1100","interface_z900"}
assert all(c["metrics"]["packet_increment_rel"]==0 and len(c["packets"])==2 for c in pp)
bm={k:maxkey(bb,"run",k) for k in ("bass_landing_error","bass_temperature_gap","bass_source_measure_defect","bass_source_momentum_defect","bass_cell_energy_projection_defect")}
assert all(v<2e-10 for k,v in bm.items() if k!="bass_cell_energy_projection_defect")
assert 0<bm["bass_cell_energy_projection_defect"]<1e-7
cross=next(c for c in cs if c["case"]=="directional_crossing")
assert (cross["metrics"]["drift_positive"],cross["metrics"]["drift_negative"])==(114,860)
assert [a["L"] for a in r["kernel_sign_audit"]]==[12,20,24]
assert all(a["pairs"]==442 and a["sample_points"]==2001 and a["minimum_relative_to_pair_monopole"]<0 for a in r["kernel_sign_audit"])
def count(name):
    t=gzip.decompress((d/"logs"/name).read_bytes()).decode()
    m=re.findall(r"test result: ok\. (\d+) passed; (\d+) failed;",t)
    assert m and all(int(f)==0 for _,f in m)
    return sum(int(a) for a,_ in m)
assert count("all.log.gz")==262 and count("examples.log.gz")==3
def sha(path):return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()
assert s["binary_sha256"]==r["binary_sha256"] and s["source_sha256"]==r["source_sha256"]
if args.raw:
    for path,expected_hash in (r["source_sha256"]|s["source_code_sha256"]).items(): assert sha(path)==expected_hash,path
    for c in cs:
        exe,network,case,out,*_=c["command"]
        assert sha(exe)==r["binary_sha256"] and sha(network)==r["network_export_sha256"] and sha(case)==c["case_sha256"]
        for name,expected_hash in c["hashes"].items(): assert sha(pathlib.Path(out)/name)==expected_hash,(c["case"],name)
        if c["packets"]:
            with open(pathlib.Path(out)/"packets.tsv") as f:
                rows=list(csv.DictReader(f,delimiter="\t"))
            assert len(rows)==2
            for row in rows:
                a={k:float(v) for k,v in row.items()}; assert a["native_number_per_h"]+a["com_number_per_h"]==0 and a["native_energy_j_per_h"]+a["com_energy_j_per_h"]==0 and a["atom_energy_j_per_h"]==0
receipt={"research_id":"R118-C2B-REC-NATIVE-ANGULAR-REDISTRIBUTION-BRIDGE-01","status":"IMPLEMENTATION_VERIFIED_SCOPED","positivity_status":"COUNTEREXAMPLE_VERIFIED_FOR_FINITE_BAND","science_promotion":False,"source_fixture_pass":len(good)-len(bb),"bass_pass":len(bb),"counterexamples":len(bad),"rust_tests":262,"example_tests":3,"metrics_max":metrics,"run_max":runs,"bass_max":bm,"packet_receipts":[dict(case=c["case"],source_updated_rel=c["metrics"]["source_updated_rel"],unresolved_j_per_h=c["metrics"]["packet_unresolved_energy_j_per_h"]) for c in pp],"kernel_sign_audit":r["kernel_sign_audit"],"counterexample_actions":[dict(floor=c["adversarial"]["floor"],target_action_s_inv=c["metrics"]["negative_gain_target"]) for c in bad],"next_id":"R118-C2C-POSITIVE-SOURCE-EVENT-MEASURE-AND-BOUNDARY-COUPLING-01","provenance":s,"results_sha256":sha(d/"RESULTS.json"),"limitations":["fixed source scalar 35-state closure; no polarized kernel","finite harmonic band not quasi-positive for arbitrary angular occupations","atom force is negative photon-force ledger, not independent event measurement","collisionless Planck characteristic plus one frozen BE step, no coupled trajectory","boundary packets fixed; exterior not evolved","centroid energy closure, no mixed-spectrum feedback","no native delegation tool; serial fallback","historical byte-parity checks not rerun in this loop"]}
(d/"ACCEPTANCE.json").write_text(json.dumps(receipt,indent=2,allow_nan=False)+"\n")
print("VERIFIED",len(good),"scoped passes",len(bad),"counterexamples; tests 265; raw",args.raw)
