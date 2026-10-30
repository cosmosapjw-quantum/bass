"""CE1-W genuinely BASS-native Rust differential at the SAME newly generated time paths.

This script invokes the compiled original BASS _rustcore/src/kinetic/comoving.rs
through the already-published CE1-R sky_time_derivative.rs CLI. It is binary64
physics parity, never the MPFR192 rigorous source or IVP certificate.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
from pathlib import Path
import subprocess
from time import perf_counter

import numpy as np

from bianchi.nonperturbative.einstein_error_budget import rk4_path
from research.ce1u_20261030.certified_gl_source import sample_gl_source, sha, SHEAR
from research.ce1u_20261030.rust_parity import knots
from research.ce1t_20261030.cellwise_gl_rust import rust_payload


def run(*,binary,certification_file,output):
    program=Path(binary).resolve()
    if not program.is_file():raise FileNotFoundError(str(program))
    original=json.loads(Path(certification_file).read_text())
    expected=original["cases"]
    checks={}
    for order in (6,8):
        source=sample_gl_source(order)
        ref=expected[str(order)]
        nsha=sha(np.asarray(source.n,dtype="<f8").tobytes())
        msha=sha(np.asarray(source.mass,dtype="<f8").tobytes())
        if nsha!=ref["source_ray_sha256"] or msha!=ref["source_mass_sha256"]:
            raise ValueError("Native Rust source ray/mass identity differs from MPFR case")
        for steps in (4,8,16):
            path=rk4_path(source,source.initial_state(tuple(SHEAR)),.08,steps,backend="python_oracle")
            history=knots(path,n=41)
            payload=rust_payload(source.n,source.mass,history)
            start=perf_counter()
            cp=subprocess.run([str(program)],input=payload,text=True,capture_output=True,timeout=90)
            if cp.returncode!=0:raise RuntimeError("Live BASS Rust failed: "+cp.stderr[-800:])
            rows=list(csv.DictReader(io.StringIO(cp.stdout)))
            if len(rows)!=41:raise ValueError("Original 41 proper-time samples not returned")
            maxima={k:0.0 for k in ("E","P","Eprime","trace","continuity")}
            for line,point in zip(rows,history):
                ell=np.array([point[f"ell{i+1}"] for i in range(3)])
                h=np.array([point[f"h{i+1}"] for i in range(3)])
                e,p=source.moments(ell)
                re=float(line["E"])
                rp=np.array([float(line[f"P{i+1}"]) for i in range(3)])
                redot=float(line["Eprime"])
                predot=-(float(np.sum(h))*e+float(np.dot(h,p)))
                maxima["E"]=max(maxima["E"],abs(re-e))
                maxima["P"]=max(maxima["P"],float(np.max(np.abs(rp-p))))
                maxima["Eprime"]=max(maxima["Eprime"],abs(redot-predot))
                maxima["trace"]=max(maxima["trace"],abs(float(np.sum(rp))-re))
                maxima["continuity"]=max(
                    maxima["continuity"],abs(redot+float(np.sum(h))*re+float(np.dot(h,rp))))
            if max(maxima.values())>=8e-12:raise AssertionError((order,steps,maxima))
            key=f"GL{order}_STEPS{steps}"
            checks[key]={"rays":len(source.mass),"time_samples":41,
                         "max_abs_gaps":maxima,
                         "native_elapsed_seconds":perf_counter()-start,
                         "binary_source_SHA_match":True}
            print("CE1W_ORIGINAL_BASS_RUST_E_P_EPRIME_PASS",key,max(maxima.values()),flush=True)
    result={"scope":"BASS original native Rust Frame.apply/det/phys_dirs, binary64 diagnostic",
            "git_rust_module":"_rustcore/src/kinetic/comoving.rs",
            "original_module_blob":"a29b12b5e7b0d529bddaf9eac53cfdb984ddaa84",
            "checks":checks,"production_ready":False,
            "native_b64_is_rigorous_mpfr":False,"upper_dag":"9/15"}
    dest=Path(output);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(result,indent=2,allow_nan=False)+"\n")
    return result


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--binary",required=True)
    parser.add_argument("--certificate",required=True)
    parser.add_argument("--output",required=True)
    args=parser.parse_args()
    run(binary=args.binary,certification_file=args.certificate,output=args.output)
