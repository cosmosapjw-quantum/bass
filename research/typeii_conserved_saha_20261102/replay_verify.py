#!/usr/bin/env python3
"""Evidence-grade normal/-O immutable-source and data-replay audit for this scoped model."""
import ast,hashlib,json,os,subprocess,sys
from pathlib import Path
here=Path(__file__).resolve().parent
root=here.parents[1]
scripts=["source_saha_transport.py","independent_referee.py","first_scattering.py",
         "test_owner_density_rate.py","model_sensitivity.py","hostile_science.py"]
outputs=[
 "HYDROGEN_SAHA_HISTORY_401.csv","SAHA_THOMSON_RAYS_401X26.csv",
 "PHYSICAL_SAHA_THOMSON_SUMMARY.json","INDEPENDENT_REFEREE.json",
 "FIRST_SCATTER_401X26.csv","FIRST_SCATTER_SUMMARY.json",
 "OWNER_ELECTRON_RATE_PARITY.json","MODEL_SENSITIVITY.json","MODEL_SENSITIVITY_26.csv",
 "HOSTILE_SCIENCE.json",
]
def check(ok,msg):
    if not bool(ok):raise RuntimeError(msg)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
before={x:digest(here/x) for x in outputs}
for p in here.glob("*.py"):
    mod=ast.parse(p.read_text(),filename=str(p))
    if any(isinstance(n,ast.Assert) for n in ast.walk(mod)):
        raise RuntimeError("OPTIMIZED_GATES_BYPASSABLE_"+p.name)
for p in scripts:
    check((here/p).exists(),"SCIENTIFIC_PROGRAM_NOT_FOUND_"+p)
env=dict(os.environ)
env.update(PYTHONDONTWRITEBYTECODE="1",OPENBLAS_NUM_THREADS="1",OMP_NUM_THREADS="1")
log={}
for mode in ("normal","optimized"):
    for script in scripts:
        cmd=[sys.executable]+(["-O"] if mode=="optimized" else [])+[str(here/script)]
        proc=subprocess.run(cmd,cwd=str(root),env=env,stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,text=True,timeout=180)
        key=mode+":"+script
        log[key]={"exit":proc.returncode,"last_stderr":proc.stderr[-300:]}
        check(proc.returncode==0,"RUNTIME_TEST_FAILED_"+key+":"+proc.stderr[-700:])
        for name,old in before.items():
            check(digest(here/name)==old,"SCIENTIFIC_BYTE_REPLAY_DRIFT_"+key+":"+name)
print("SCIENTIFIC_TESTS_FINISHED",len(log))
source_lock=json.loads((root/"research/typeii_host_preflight_20261101/SOURCE_LOCK.json").read_text())["original_git_blobs_sha1"]
for p,sha in source_lock.items():
    now=subprocess.check_output(["git","-C",str(root),"hash-object",p],text=True).strip()
    check(now==sha,"ORIGINAL_9_SOURCE_DRIFT_"+p)
expected_parent="9f1400588d39ba3a61020542e14b0e372c8e9be1af130f8c64ed8829b23ad217"
check(digest(root/"research/typeii_liouville_optdepth_20261101/PHOTON_RAYS_401X26.csv")==expected_parent,
      "PARENT_RAY_BYTE_IDENTITY_DRIFT")
report={
 "schema":"bass.typeii.conserved_highz_saha.replay_verify.v1",
 "committed_parent":"97359596c3d640d5ad306e2285b248a5105cf40e",
 "original_9_source_blobs":len(source_lock),
 "normal_and_optimized_program_passes":len(log),
 "cases":log,
 "tracked_science_artifact_sha256":before,
 "python_source_assert_nodes":0,
 "parent_401x26_csv_sha256":expected_parent,
 "verdict":"REPLAY_NORMAL_OPTIMIZED_AND_BYTE_IDENTITY_PASS"
}
(here/"VALIDATION_RESULTS.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
print(json.dumps({k:report[k] for k in
  ("schema","original_9_source_blobs","normal_and_optimized_program_passes",
   "python_source_assert_nodes","verdict")},indent=2))
