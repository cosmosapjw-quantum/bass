"""Read-only code and certificate verifier; writes new local evidence only on request."""
from __future__ import annotations
import argparse
import hashlib
import json
import platform
import subprocess
import sys
import datetime
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SOURCE_LOCKS={
  "fa02.py":"1e89e75f7a08d2eec1851a58e602c2683b1888a37b3e1fe10b1be4234756eee5",
  "fa03.py":"ad865127da7c2f9ea613541571f9b842f9da7630af9bb951a3df5968ad44ecf7",
}

def sha(p:Path)->str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def inspect_artifacts():
    src=ROOT/"research/fa03_c5_angular_cap_20261015/reference"
    for name,expected in SOURCE_LOCKS.items():
        if sha(src/name)!=expected:
            raise RuntimeError("PARENT_FA03_SOURCE_LOCK_FAIL:"+name)
    p=HERE/"evidence/BENCHMARK_STOKES_64.json"
    j=json.loads(p.read_text())
    if len(j["results"])!=3 or [row["rays"] for row in j["results"]]!=[36,144,480]:
        raise RuntimeError("MATCHED_BENCHMARK_INCOMPLETE")
    for row in j["results"]:
        if row["steps"]!=64 or row["repetitions"]!=3:
            raise RuntimeError("BENCHMARK_INPUT_CHANGED")
        q=row["timing"]["real_vector_Stokes"]
        if q["max_matrix_trace_norm_vs_original"] is None or q["max_matrix_trace_norm_vs_original"]>3e-12:
            raise RuntimeError("NUMERICAL_IDENTITY_FAILED")
        if row["state_bytes_real"]*2!=row["state_bytes_complex"]:
            raise RuntimeError("REAL_STOKES_STATE_MEMORY_RELATION_FAILED")
    xc=json.loads((HERE/"evidence/XACT_C7.json").read_text())
    if not (xc.get("all_zero") and len(xc.get("checks",{}))==7 and all(x=="0" for x in xc["checks"].values())):
        raise RuntimeError("C7_XACT_NOT_SEVEN_ZEROS")
    return {"source_sha256":dict(SOURCE_LOCKS),
            "benchmark_sha256":sha(p),
            "xact_sha256":sha(HERE/"evidence/XACT_C7.json"),
            "xact_groups_pass":7,
            "ray_cases": [36,144,480],
            "measured_speedups":{str(row["rays"]):row["optimization"]["real_vs_original_speedup"] for row in j["results"]},
            "physical_comparisons_pass":True,
            "fully_certified_continuum_cap_error":None}

SUITES=[
  ("C7_physics",HERE,"test_c7.py",19),
  ("C7_real_stokes",HERE,"test_stokes.py",15),
  ("C6_inherited",ROOT/"research/fa03_c6_angular_audit_20261015","test_c6.py",18),
  ("C5_inherited",ROOT/"research/fa03_c5_angular_cap_20261015","test_angular_sweep.py",15),
]

def verify(output:Path):
    checks=inspect_artifacts()
    if output.exists():raise FileExistsError(str(output))
    output.parent.mkdir(parents=True,exist_ok=True)
    records=[]
    total=0
    for name,path,pattern,expected in SUITES:
        args=[sys.executable,"-m","unittest","discover","-s",str(path),"-p",pattern,"-v"]
        result=subprocess.run(args, cwd=ROOT, capture_output=True,text=True)
        log=HERE/"evidence"/f"VERIFY_{name}.log"
        if log.exists():raise FileExistsError(str(log))
        log.write_text("command: "+" ".join(args)+"\n\nstdout:\n"+result.stdout.rstrip("\n")+"\n\nstderr:\n"+result.stderr.rstrip("\n")+"\n")
        passed=(result.returncode==0 and f"Ran {expected} tests" in (result.stderr+result.stdout))
        records.append({"name":name,"expected_tests":expected,"passed":passed,
                       "exit_code":result.returncode,"log_file":str(log.relative_to(HERE)),
                       "log_sha256":sha(log)})
        if not passed:raise RuntimeError(f"REGRESSION_FAILED:{name}:{result.returncode}")
        total+=expected
    import numpy as np
    payload={"schema":"bass.fa03.c7.release_verification.v1",
             "verified_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
             "source_parent_commit":"76cfa950a6504a219365b31e9358dec9e4c05f66",
             "selected_stage":"C7",
             "python":platform.python_version(),"numpy":np.__version__,
             "tests":records,"total_passed":total,"artifact_checks":checks,
             "native_subagents":"NOT_RUN_UNAVAILABLE",
             "local_codex":"NOT_USED",
             "rei_owner_files_mutated":0,
             "rei_solver_jobs_launched":0,
             "science_status":"PASS_SCOPED_FIXED_FA03_NON_GREY_POLARIZED_TRANSPORT_ONLY",
             "next_stage":"C8_READY_NOT_RUN"}
    output.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+"\n")
    return payload

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    got=verify(args.out)
    print(json.dumps({"saved":str(args.out),"total":got["total_passed"],"passed":all(x["passed"] for x in got["tests"]),
       "speedups":got["artifact_checks"]["measured_speedups"]},indent=2))
