#!/usr/bin/env python3
"""Bounded scientific re-execution of original HYREC2 external-H and TypeII H+nH work.

One normal plus one optimized Python (-O) run of each of seven real science
programs. Verify source identities, complete code execution, and byte-identical
scientific data. This is NOT an independent author's referee or production CI.
"""
import ast,hashlib,json,os,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PARENT="9f10e1145c8582f71f7d81dcebfd3c125c70c04c"
programs=[
 "verify_native_external_api.py",
 "generate_typeii_H_grid.py",
 "run_native_typeii_atomic_H.py",
 "run_native_typeii_proper_current.py",
 "transport_native_atomic_photons.py",
 "verify_atomic_rays.py",
 "native_atomic_homotopy.py",
 "hostile_physics.py",
]
data_files=[
 "R2_NATIVE_FLRW_CALLBACK_CONTROL.json",
 "NATIVE_HYREC_FLRW_H_GRID.dat",
 "NATIVE_HYREC_FLRW_H_EXTERNAL_CONTROL_8000.dat",
 "R3_TYPEII_HUBBLE_GRID.json",
 "TYPEII_H_COMPARE_FLRW_GRID.csv",
 "NATIVE_TYPEII_H_ARRAY_2248.dat",
 "R3_NATIVE_TYPEII_ATOMIC_H_ONLY.json",
 "NATIVE_TYPEII_HUBBLE_HHE_ATOMIC_XE_TM_8000.dat",
 "PROPER_HYDROGEN_REPLACEMENT_PATCH.diff",
 "TYPEII_PROPER_NH_FACTOR_2248.dat",
 "R4_NATIVE_TYPEII_H_AND_PROPER_NH_RESULTS.json",
 "NATIVE_FLRW_H_AND_TYPEII_PROPER_NH_XE_TM_8000.dat",
 "NATIVE_TYPEII_H_AND_PROPER_NH_XE_TM_8000.dat",
 "R5_SOURCE_ATOMIC_TYPEII_PHOTON_RESULTS.json",
 "TYPEII_ATOMIC_THOMSON_EXTENDED_26RAY.csv",
 "R6_ATOMIC_PHOTON_NUMERIC_VALIDATION.json",
 "R7_ATOMIC_H_NH_HOMOTOPY.json",
 "ATOMIC_TYPEII_H_NH_HOMOTOPY_300_TO1700.csv",
 "R9_HOSTILE_PHYSICS.json"
]
def check(ok,msg):
    if not bool(ok):raise RuntimeError(msg)
def checksum(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
baseline={f:checksum(HERE/f) for f in data_files}
for f in programs:
    src=HERE/f
    check(src.exists(),"MISSING_SOURCE_SCIENCE_PROGRAM_"+f)
    tree=ast.parse(src.read_text(),filename=str(src))
    check(not any(isinstance(t,ast.Assert) for t in ast.walk(tree)),
          "PYTHON_OPTIMIZED_VALIDATION_GATES_UNSAFE_"+f)
git=lambda *a:subprocess.check_output(["git","-C",str(ROOT),*a],text=True).strip()
check(git("rev-parse",PARENT)==PARENT,"PARENT_IMMUTABLE_SOURCE_NOT_FOUND")
orig=json.loads((ROOT/"research/typeii_host_preflight_20261101/SOURCE_LOCK.json").read_text())["original_git_blobs_sha1"]
for name,sha in orig.items():
    check(git("hash-object",name)==sha,"ORIGINAL_BASS_SOURCE_DRIFT_"+name)
hyrec=json.loads((ROOT/"research/typeii_hyrec2_history_20261102/HYREC2_NATIVE_SOURCE_REPORT.json").read_text())
native_root=Path(hyrec["installed_source"])
for name,sha in hyrec["original_source_atomic_table_sha256"].items():
    check(checksum(native_root/name)==sha,"NATIVE_HYREC_SOURCE_IDENTITY_DRIFT_"+name)
env=dict(os.environ)
env.update(PYTHONDONTWRITEBYTECODE="1",OPENBLAS_NUM_THREADS="1",OMP_NUM_THREADS="1")
receipts={}
for mode in ("normal","optimized"):
    for program in programs:
        command=[sys.executable]+(["-O"] if mode=="optimized" else [])+[str(HERE/program)]
        result=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                              cwd=str(ROOT),env=env,text=True,timeout=140)
        key=mode+":"+program
        receipts[key]={"exit_code":result.returncode,"stderr_last":result.stderr[-190:]}
        check(result.returncode==0,"SCIENTIFIC_PROGRAM_FAILED_"+key+" "+result.stderr[-700:])
        for name,sha in baseline.items():
            check(checksum(HERE/name)==sha,"REPRODUCIBLE_SOURCE_DATA_BYTE_DRIFT_"+key+" "+name)
    print("REPLAY_PHASE",mode,len(programs),"ALL_SCIENCE_FILES_SHA256_STABLE",flush=True)
report={
 "schema":"bass.typeii.original_native_HyRec2_atomic_H_properH_14_case_replay.v1",
 "source_parent":PARENT,
 "original_BASS_source_Git_blobs_exact":len(orig),
 "original_HyRec2_source_C_headers_atomic_rate_SHA256_exact":
      len(hyrec["original_source_atomic_table_sha256"]),
 "programs":programs,
 "total_normal_plus_optimized_science_executions":len(receipts),
 "actual_case_exits":receipts,
 "scientific_data_files_SHA256":baseline,
 "bypassable_Python_assert_validation_nodes":0,
 "status":"NATIVE_HYREC2_BASS_TYPEII_ATOMIC_H_NH_PHOTON_FULL_REPLAY_BYTE_EXACT_PASS",
 "caveat":"source-conditional physics; no independent different-author referee and no new production dispatcher"
}
(HERE/"R8_SOURCE_REPLAY_RESULTS.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
print(json.dumps({"status":report["status"],
 "executed":len(receipts),"source_original":len(orig),
 "hyrec_native_c_files":len(hyrec["original_source_atomic_table_sha256"]),
 "science_byte_identity_count":len(baseline)},indent=2))
