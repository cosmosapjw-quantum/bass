"""CE1-X: run original BASS Rust sky kinetic CLI on exact same MPFR paths.

BASS _rustcore/src/kinetic/comoving.rs Frame.apply/det/phys_dirs is imported
by inherited research/ce1r_20261030/sky_time_derivative.rs, NOT copied here.
Independent NumPy polynomial implementation checks full real l4 sky components.
These are binary64 diagnostics, not outward source/geometry certificates.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import subprocess

import numpy as np
from bianchi.nonperturbative.einstein_error_budget import rk4_path
from research.ce1u_20261030.certified_gl_source import sample_gl_source, SHEAR, sha
from research.ce1u_20261030.rust_parity import knots
from research.ce1t_20261030.cellwise_gl_rust import rust_payload


def _binpath(a)->str:
    v=np.asarray(a)
    h=hashlib.sha256()
    h.update(repr((v.shape,v.dtype.str)).encode("ascii"))
    h.update(v.tobytes(order="C"))
    return h.hexdigest()


def independent_harmonics(source,ell):
    ell=np.asarray(ell,dtype=float)
    with np.errstate(all="raise"):
        m=np.exp(-ell)
        p=np.asarray(source.n)*m[None,:]
        r=np.sqrt(np.sum(p*p,axis=1))
        t=p*p/(r*r)[:,None]
        weights=np.asarray(source.mass)*float(np.prod(m))*r
        E=float(np.sum(weights))
        z=t[:,2]
        Y40=3/(16*math.sqrt(math.pi))*(35*z*z-30*z+3)
        Y42=3/8*math.sqrt(5/(2*math.pi))*(t[:,0]-t[:,1])*(7*z-1)
        Y44=3/16*math.sqrt(35/(2*math.pi))*(t[:,0]**2-6*t[:,0]*t[:,1]+t[:,1]**2)
        a=np.array([float(np.dot(weights,Y40)),
                    float(np.dot(weights,Y42)),float(np.dot(weights,Y44))])
        return E,a


def _k4_normalized(aa,bb,Ea,Eb):
    alpha=4*math.pi*aa/Ea
    beta=4*math.pi*bb/Eb
    return float((alpha[0]*beta[0]+2*alpha[1]*beta[1]+2*alpha[2]*beta[2])/9)


def run(*,binary,time_certificate,source_certificate,output,raw_dir):
    program=Path(binary)
    if not program.is_file():raise FileNotFoundError(program)
    time=json.loads(Path(time_certificate).read_text())
    source_proof=json.loads(Path(source_certificate).read_text())
    raw=Path(raw_dir);raw.mkdir(parents=True,exist_ok=True)
    all_cases={}
    for order in (6,8):
        x=sample_gl_source(order)
        proof=source_proof["cases"][str(order)]
        if (proof["source_ray_sha256"]!=sha(np.asarray(x.n,dtype="<f8").tobytes())
            or proof["source_mass_sha256"]!=sha(np.asarray(x.mass,dtype="<f8").tobytes())):
            raise ValueError("Frozen GL rays are not source/MPFR certified")
        for steps in (4,8,16):
            cert=time["cases"][str(order)]["cases"][str(steps)]
            path=rk4_path(x,x.initial_state(tuple(SHEAR)),.08,steps,backend="python_oracle")
            if _binpath(path.coefficients)!=cert["path_sha256"]["coefficients"]:
                raise ValueError("Actual Rust numerical path differs from certified binary Hermite")
            history=knots(path,n=41)
            cp=subprocess.run([str(program)],input=rust_payload(x.n,x.mass,history),
                              capture_output=True,text=True,timeout=100)
            if cp.returncode:raise RuntimeError("BASS native Rust reject "+cp.stderr[-700:])
            rows=list(csv.DictReader(io.StringIO(cp.stdout)))
            if len(rows)!=41:raise ValueError("Missing 41 original proper-time BASS Rust observations")
            expected_a=[];observed_a=[];E_expected=[];E_rust=[]
            largest=0.0
            for row,h in zip(rows,history):
                E,a=independent_harmonics(x,[h[f"ell{i+1}"] for i in range(3)])
                Eout=float(row["E"])
                ar=np.array([float(row["a_4_0_re"]),float(row["a_4_2_re"]),
                             float(row["a_4_4_re"])])
                largest=max(largest,abs(E-Eout),float(np.max(np.abs(a-ar))))
                expected_a.append(a);observed_a.append(ar);E_expected.append(E);E_rust.append(Eout)
            if largest>=4e-11:raise AssertionError((order,steps,largest))
            a=np.asarray(observed_a)
            kr=_k4_normalized(a[0],a[-1],E_rust[0],E_rust[-1])
            ke=_k4_normalized(expected_a[0],expected_a[-1],E_expected[0],E_expected[-1])
            if abs(kr-ke)>=1e-10:raise AssertionError((order,steps,kr,ke))
            name=f"GL{order}_STEPS{steps}"
            (raw/f"{name}_BASS_RUST_SKY.csv").write_text(cp.stdout)
            all_cases[name]={
                "order":order,"steps":steps,"rays":len(x.mass),
                "epoch_count":41,
                "stored_source_ray_sha256":proof["source_ray_sha256"],
                "stored_source_mass_sha256":proof["source_mass_sha256"],
                "certified_path_coefficients_sha256":cert["path_sha256"]["coefficients"],
                "max_abs_native_Rust_vs_NumPy_l4":largest,
                "K4_delta_0_008_native":kr,
                "K4_delta_0_008_independent_NumPy":ke,
                "max_abs_cross_kernel_bound_ceil_27":
                    proof["time_path_cases"][str(steps)]["total_cross_kernel_upper_ceil_27"],
                "formal_MPFR_integral_from_Rust":"NOT_RUN",
            }
            print("CE1X_ORIGINAL_BASS_RUST_L4_PASS",name,kr,largest,flush=True)
    # Source+geometry theorem bound must cover both different-positive
    # quadratures against a common physical continuum K4 at u=0,u=.08.
    differences={}
    for steps in (4,8,16):
        a=all_cases[f"GL6_STEPS{steps}"]
        b=all_cases[f"GL8_STEPS{steps}"]
        empirical=abs(a["K4_delta_0_008_native"]-b["K4_delta_0_008_native"])
        upper=float(a["max_abs_cross_kernel_bound_ceil_27"])+float(b["max_abs_cross_kernel_bound_ceil_27"])
        if not (empirical<=upper and upper>0):
            raise AssertionError(("Cross-GL independent falsification",steps,empirical,upper))
        differences[str(steps)]={"empirical_GL6_vs_GL8_K4_delta":empirical,
                                  "sum_of_two_certified_continuum_upper":upper,
                                  "observed_bound_pass":True}
    result={"status":"SCOPED_BASS_NATIVE_RUST_L4_PARITY_AND_K4_CROSSCHECK_PASS",
            "source":"_rustcore/src/kinetic/comoving.rs Frame.apply/det/phys_dirs",
            "BASS_original_Rust_blob":"a29b12b5e7b0d529bddaf9eac53cfdb984ddaa84",
            "cases":all_cases,"GL6_GL8_intercase":differences,
            "upper_dag":"9/15","production_ready":False,
            "rust_binary64_is_not_MPFR_interval_proof":True}
    target=Path(output);target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(result,indent=2,allow_nan=False)+"\n")
    return result


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--binary",required=True)
    parser.add_argument("--time-certificate",required=True)
    parser.add_argument("--source-certificate",required=True)
    parser.add_argument("--output",required=True)
    parser.add_argument("--raw-dir",required=True)
    a=parser.parse_args()
    run(binary=a.binary,time_certificate=a.time_certificate,
        source_certificate=a.source_certificate,output=a.output,raw_dir=a.raw_dir)
