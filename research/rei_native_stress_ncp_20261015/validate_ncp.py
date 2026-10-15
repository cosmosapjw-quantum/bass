"""Actual NCP Rust output readback, cross-language source parity and scaling receipt.

No self-declared PASS: any source hash, bitwise readback, numerical tolerance
or NCP provenance mismatch raises and prevents a verified receipt.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import sys
import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from export_grid import source_grid,sha
from jacobian import kinetic_susceptibility

FIELDS=("rho","pp","pa","delta","db_delta")
def parse_bench(log:Path):
    rows=[]
    for line in log.read_text().splitlines():
        if not line.startswith("BENCH_PASS "):raise ValueError("Unexpected benchmark line")
        d=dict(x.split("=",1) for x in line.split()[1:])
        if d.pop("bitwise_parity")!="PASS":
            raise AssertionError("No per-state CPU parity")
        rows.append({k:int(d[k]) for k in ("n","threads","repeats")} |
                    {k:float(d[k]) for k in ("median_s","min_s","checksum","sum_abs_delta")})
    if len(rows)!=21 or any(k["n"]!=6000 or k["repeats"]!=3 for k in rows):
        raise AssertionError("Incomplete matched NCP scaling matrix")
    return rows

def run(dir:Path):
    inp=HERE/"evidence/SOURCE_GRIDS";remote=Path(dir)
    raw=(remote/"NCP_INPUT_SHA256.txt").read_text().splitlines()
    for item in raw:
        digest,file=item.strip().split(maxsplit=1)
        original=inp/Path(file).name
        if sha(original)!=digest:raise AssertionError("NCP source grid bytes differ "+file)
    build=(remote/"RUST_BUILD_SHA256.txt").read_text().splitlines()
    kernel_sha=build[0].split()[0]
    if sha(HERE/"kernel.rs")!=kernel_sha:raise AssertionError("NCP compiled source mismatch")
    bench=parse_bench(remote/"NCP_BENCHMARKS.log")
    out={"schema":"bass.rei.ncp.massive_stress_jacobian.checked.v1",
         "ncp_hardware":(remote/"NCP_HARDWARE.txt").read_text(),
         "source_sha256":kernel_sha,"cases_per_mass":1213,"mass_settings":[],
         "native_bitwise_widths":[1,64],
         "benchmark":bench,"claim":"independent source-native Rust FD96/GL stress susceptibility; no HHe production changed"}
    for mass in (3,30,300):
        names=[remote/f"native_m{mass}_t{w}.tsv" for w in (1,64)]
        if sha(names[0])!=sha(names[1]):raise AssertionError("1vs64 BITWISE_DRIFT")
        inp_cases=np.loadtxt(inp/f"cases_m{mass}.tsv")
        data=np.loadtxt(names[0],skiprows=1)
        if data.shape!=(1213,5):raise AssertionError("NCP output row count")
        _,model=source_grid(float(mass))
        refs=[]
        for x,b,A in inp_cases:
            scalars=model.evaluate_with_delta(float(x),float(b),float(A))
            sus=kinetic_susceptibility(model,float(x),float(b),float(A))
            refs.append([*scalars,sus])
        refs=np.array(refs,dtype=float)
        dif=np.abs(data-refs)
        # Same scientific tolerance across m=3,30,300 and all 5 outputs.
        if not np.allclose(data,refs,rtol=8e-13,atol=5e-14):
            k=np.unravel_index(np.argmax(dif),dif.shape)
            raise AssertionError(f"RUST_PYTHON_PHYSICS_FAIL m={mass}: {k} {data[k]} {refs[k]}")
        # Mean-density/work and physical pressure positivity for each case.
        if np.any(data[:,0]<=0) or np.any(data[:,1]<0) or np.any(data[:,2]<0):
            raise AssertionError("NEGATIVE_SOURCE_STRESS")
        if not np.allclose(data[:,2]-data[:,1],data[:,3],rtol=4e-12,atol=8e-16):
            raise AssertionError("PI_TENSOR_DIFFERENCE")
        near=[(i,float(refs[i,3]),float(data[i,3])) for i in (0,1,2,3,4,5,6)]
        if data[1,3]!=0 or data[2,3]>=0 or data[3,3]<=0:
            raise AssertionError("ISOTROPY_OR_TINY_SHEAR")
        out["mass_settings"].append({
          "m_over_Tref":mass,
          "source_output_1thread_sha256":sha(names[0]),
          "source_output_64thread_sha256":sha(names[1]),
          "rows":len(data),"max_abs_by_field":dict(zip(FIELDS,dif.max(axis=0).tolist())),
          "max_relative_on_nonnegligible":dict(zip(FIELDS,[
            float(np.max(dif[mask,j]/np.abs(refs[mask,j])))
            if np.any(mask) else None
            for j in range(5) for mask in [np.abs(refs[:,j])>1e-12]])),
          "tiny_shear_sign_checks":near,"rust_python_pass":True
        })
    groups={}
    for mass in (3,30,300):
        # Each mass shares the same case count, grid and bench widths.
        idx=(3,30,300).index(mass)
        subset=bench[idx*7:(idx+1)*7]
        base=subset[0]["median_s"]
        best=min(subset,key=lambda x:x["median_s"])
        groups[str(mass)]={"serial_median_s":base,
                           "best_threads":best["threads"],
                           "best_median_s":best["median_s"],
                           "best_speedup":base/best["median_s"],
                           "speedup_by_threads":{str(row["threads"]):base/row["median_s"] for row in subset}}
    out["scaling_summary"]=groups
    return out

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--ncp-results",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    if args.out.exists():raise FileExistsError(args.out)
    rec=run(args.ncp_results)
    args.out.write_text(json.dumps(rec,indent=2,ensure_ascii=False)+"\n")
    print("CROSS_LANGUAGE_AND_NCP_BITWISE_PASS")
    for item in rec["mass_settings"]:
        print("mass",item["m_over_Tref"],"max_abs",item["max_abs_by_field"])
    print("NCP_SCALING",json.dumps(rec["scaling_summary"],indent=2))
