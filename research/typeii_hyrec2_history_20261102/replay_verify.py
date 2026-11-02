#!/usr/bin/env python3
"""BASS HYREC2 native-source isolated normal/-O 6-program reproducibility and byte identity."""
import ast, hashlib, json, os, subprocess, sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
programs=[
 "run_native_hyrec2.py",
 "typeii_hyrec2_transport.py",
 "typeii_extended_window.py",
 "validate_extended_window.py",
 "model_sensitivity.py",
 "owner_electron_parity.py",
]
artifacts=[
 "HYREC2_FLRW_INPUT_20261102.dat",
 "HYREC2_FLRW_XE_TM_8000.dat",
 "HYREC2_NATIVE_SOURCE_REPORT.json",
 "HYREC2_TYPEII_THOMSON_RESULTS.json",
 "TYPEII_HYREC2_26RAY_DEPTH_401.csv",
 "TYPEII_HYREC2_ELECTRON_401.csv",
 "EXTENDED_RECOMB_WINDOW_RESULT.json",
 "EXTENDED_TYPEII_HYREC2_RAY_26.csv",
 "EXTENDED_WINDOW_VALIDATION.json",
 "MODEL_SENSITIVITY_RESULTS.json",
 "ORIGINAL_ELECTRON_OWNER_PARITY.json",
]
def check(ok,msg):
    if not bool(ok):raise RuntimeError(msg)
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
for file in programs:
    check((HERE/file).exists(),"RUNNER_MISSING_"+file)
    syntax=ast.parse((HERE/file).read_text(),filename=str(HERE/file))
    check(not any(isinstance(x,ast.Assert) for x in ast.walk(syntax)),
          "OPTIMIZED_VALIDATION_BYPASS_POSSIBLE_"+file)
before={file:digest(HERE/file) for file in artifacts}
# Hash all original HyRec source and rate tables from the previously READ original native distribution.
metadata=json.loads((HERE/"HYREC2_NATIVE_SOURCE_REPORT.json").read_text())
for name,expected in metadata["original_source_atomic_table_sha256"].items():
    actual=digest(Path(metadata["installed_source"])/name)
    check(actual==expected,"HYREC_ORIGINAL_C_AND_TABLE_DRIFT_"+name)
# Protect the original unmodified BASS source and previously source-validated ray input.
source_hash=json.loads((ROOT/"research/typeii_host_preflight_20261101/SOURCE_LOCK.json").read_text())["original_git_blobs_sha1"]
for rel,expected in source_hash.items():
    current=subprocess.check_output(["git","-C",str(ROOT),"hash-object",rel],text=True).strip()
    check(current==expected,"ORIGINAL_BASS_SOURCE_DRIFT_"+rel)
source_ray=digest(ROOT/"research/typeii_liouville_optdepth_20261101/PHOTON_RAYS_401X26.csv")
check(source_ray=="9f1400588d39ba3a61020542e14b0e372c8e9be1af130f8c64ed8829b23ad217",
      "ORIGINAL_BASS_401x26_RAY_DRIFT")
env=dict(os.environ)
env.update(PYTHONDONTWRITEBYTECODE="1",OPENBLAS_NUM_THREADS="1",OMP_NUM_THREADS="1")
results={}
for mode in ("normal","optimized"):
    for script in programs:
        command=[sys.executable]+(["-O"] if mode=="optimized" else [])+[str(HERE/script)]
        proc=subprocess.run(command,cwd=ROOT,env=env,text=True,
                            stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=180)
        key=mode+":"+script
        results[key]={"exit_code":proc.returncode,"stderr_tail":proc.stderr[-220:]}
        check(proc.returncode==0,"SOURCE_SCIENCE_PROGRAM_FAILED_"+key+":"+proc.stderr[-900:])
        for file,original in before.items():
            check(digest(HERE/file)==original,"SOURCE_SCIENCE_BYTE_DRIFT_"+key+":"+file)
print("VERIFIED_SCIENCE_EXECUTIONS",len(results),flush=True)
report={
 "schema":"bass.typeii.HyRec2_FLRW_HHe_source_and_extended_Bianchi_replay.v1",
 "native_C_source_and_rate_tables_checksum_verification":len(metadata["original_source_atomic_table_sha256"]),
 "original_BASS_9_source_blobs":len(source_hash),
 "original_BASS_401x26_rays_sha256":source_ray,
 "normal_and_optimized_source_sci_program_passes":len(results),
 "actual_program_receipts":results,
 "output_artifact_sha256":before,
 "validation_source_assert_nodes":0,
 "claim":"NATIVE_HYREC2_ORIGINAL_SOURCE_AND_BIANCHI_RAY_REPLAY_NORMAL_OPTIMIZED_BYTE_EXACT_PASS",
 "limitations":"does not certify self-consistent Bianchi atomic kinetics, full Boltzmann gain/polarization or CMB"
}
(HERE/"SOURCE_REPLAY_VALIDATION.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
print(json.dumps({k:report[k] for k in
 ["schema","native_C_source_and_rate_tables_checksum_verification","original_BASS_9_source_blobs",
 "normal_and_optimized_source_sci_program_passes","claim"]},indent=2))
