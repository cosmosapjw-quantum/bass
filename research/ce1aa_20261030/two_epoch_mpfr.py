"""CE1-AA: directed MPFR192 certificate for two-epoch continuum l=4 Gram minor.

Exact saved binary64 original six-cell GL ray/mass source, original RK4/Hermite
binary coefficients, mathematical pi via MPFR, and immutable PR270
continuum/source/time upper bound. Binary64 BASS Rust sky is a comparison only.
No new K12 moment proof or IVP error integration.
"""
from __future__ import annotations

import argparse
import ctypes as C
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from bianchi.nonperturbative.einstein_error_budget import rk4_path
from bianchi.nonperturbative.einstein_interval import Interval as I, _lib, _P, D, U, BITS
from research.ce1t_20261030.cellwise_gl_rust import (
    frozen_source_identity, SHEAR, sha,
)
from research.ce1u_20261030.certified_gl_source import sample_gl_source
from research.ce1x_20261030.rust_l4_parity import _binpath
from research.ce1x_20261030.certify_l4 import ceil_decimal
from research.ce1v_20261030.cross_certify import load_donor
from research.ce1w_20261030.time_panels import _certify_same_source
from research.ce1z_20261030.gram_spectrum import read_rows, sky_modes

ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / "research/ce1y_20261030/input"
PAIR = ROOT / "research/ce1y_20261030/data"
SOURCE_SHA = "022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035"
RUST_BLOB = "a29b12b5e7b0d529bddaf9eac53cfdb984ddaa84"
TIME_BLOB = "2408eb05b9413621145728bc8a7fb26107bcf419"
L4_BLOB = "a2a165e01b852680e19f6270054e65aff1b1ba40"
EXPECTED_RAW = {
    6: (
        "6f6e5d0797404521abd51cb8394a8b2beca3e96b392924b9ad30b2093098d957",
        "56cb2c5baabdcf10355cc7ddf2f1cf41ad8a131d890e285320e39bab52758199",
    ),
    8: (
        "90e29d100d35dc7ac31f9d75f7d6d4c2d423d90ad487ec0922246bc8f39891cb",
        "2c0b9ca7d1845458639217fae0a86b3339c32f57f9f71dd6c649c3408d319a79",
    ),
}


def require(test, reason):
    if not test:
        raise ValueError(reason)


def git_blob_hash(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def exact_pi():
    pi = I._empty()
    _lib.mpfr_const_pi.argtypes = [_P, C.c_int]
    _lib.mpfr_const_pi.restype = C.c_int
    _lib.mpfr_const_pi(pi.a.ptr(), D)
    _lib.mpfr_const_pi(pi.b.ptr(), U)
    require(3.14159265358979 < pi.lower <= pi.upper < 3.14159265358980,
            "MPFR192 pi could not be enclosed")
    return pi


def l4_endpoint(source, ell, pi):
    """Exact-real stored-ray GL bolometric harmonic, each op outward at 192 bits."""
    require(len(ell) == 3 and all(np.isfinite(z.lower) and np.isfinite(z.upper)
                                and z.lower >= 0 and z.upper < .08 for z in ell),
            "Invalid expanding Hermite endpoint interval")
    scale = [(-z).exp() for z in ell]
    vol = (-(ell[0]+ell[1]+ell[2])).exp()
    c40 = I(3)/(I(16)*pi.sqrt())
    c42 = I(3)/I(8)*(I(5)/(I(2)*pi)).sqrt()
    c44 = I(3)/I(16)*(I(35)/(I(2)*pi)).sqrt()
    E = I(0)
    a = [I(0), I(0), I(0)]
    for mass, nr in zip(source.mass, source.n):
        # Ray and mass values are EXACT dyadic inputs, never idealized GL nodes.
        p = [I(float(nr[i]))*scale[i] for i in range(3)]
        p2 = [v*v for v in p]
        r2 = sum(p2, I(0))
        require(r2.lower > 0, "Nonpositive original ray norm")
        t = [v/r2 for v in p2]
        z = t[2]
        w = I(float(mass))*vol*r2.sqrt()
        E = E+w
        Y = [
            c40*(I(35)*z*z-I(30)*z+I(3)),
            c42*(t[0]-t[1])*(I(7)*z-I(1)),
            c44*(t[0]*t[0]-I(6)*t[0]*t[1]+t[1]*t[1]),
        ]
        for j in range(3):
            a[j] = a[j] + w*Y[j]
    require(E.lower > .6, "Positive original energy/mass premise failed")
    alpha = [I(4)*pi*v/E for v in a]
    return E, a, alpha


def kernel(x, y):
    require(len(x)==3 and len(y)==3, "Three real reflection-even l4 harmonics required")
    return (x[0]*y[0] + I(2)*x[1]*y[1] + I(2)*x[2]*y[2])/I(9)


def endpoints_exact_binary_hermite(path):
    require(float(path.times[0]) == 0.0 and float(path.times[-1]) == .08,
            "Original time horizon/clock changed")
    # At v=0 and v=1 in original exact-real cubic from BINARY COEFFICIENTS.
    # Last path.states[-1] is not silently treated as exact Hermite endpoint.
    start = [I(float(path.coefficients[0, 0, i])) for i in range(3)]
    finish = [sum((I(float(path.coefficients[-1, j, i])) for j in range(4)), I(0))
              for i in range(3)]
    return start, finish


def source_and_time_locks():
    require(BITS == 192, "Changed original MPFR precision")
    frozen_source_identity()
    tpath = INPUT/"real_time_mpfr.json"
    lpath = INPUT/"l4_source_and_transfer.json"
    require(git_blob_hash(tpath)==TIME_BLOB and git_blob_hash(lpath)==L4_BLOB,
            "Original donor time/l4 data blob identity changed")
    t = json.loads(tpath.read_text())
    l4 = json.loads(lpath.read_text())
    require(t["source"].startswith("Original frozen six cell")
            and t["rust_source_blob"]==RUST_BLOB
            and t["parent_head"]=="2d5076ecb2307cea39c1b608396c34050021ebc3",
            "Original time source/parent changed")
    require(l4["source"]==SOURCE_SHA and l4["BASS_original_Rust_blob"]==RUST_BLOB,
            "Original exact-rational l4 proof source changed")
    previous = json.loads((PAIR/"SCIENCE_RESULTS.json").read_text())
    require(previous["original_binary64_source_sha256"]==SOURCE_SHA
            and previous["physical_rows"]==10086
            and previous["input_numeric_rust_centers_are_NOT_rigorous_MPFR_intervals"],
            "Old BASS sky records/proof semantics changed")
    return t,l4,previous


def certify_pair(order, steps, t, l4, prior):
    require(order in (6,8) and steps in (4,8,16), "Unsupported original BASS source/path")
    src=sample_gl_source(order)
    actual=(sha(np.asarray(src.n,dtype="<f8").tobytes()),
            sha(np.asarray(src.mass,dtype="<f8").tobytes()))
    require(actual == EXPECTED_RAW[order], "Original ray/mass dyadic identity changed")
    tm=t["cases"][str(order)]["cases"][str(steps)]
    lc=l4["cases"][str(order)]
    cert=lc["time_path_cases"][str(steps)]
    require((actual[0]==lc["source_ray_sha256"]==tm["source_ray_sha256"]
             and actual[1]==lc["source_mass_sha256"]==tm["source_mass_sha256"]
             and tm["physical_source_sha256"]==SOURCE_SHA
             and lc["original_physical_source_sha256"]==SOURCE_SHA),
            "Original exact source/geometry matching failed")
    require(tm["target_h"]==1e-5 and tm["target_met"]
            and tm["final_h_upper"]<1e-5 and tm["u_end"]==.08,
            "Original h gate not preserved")
    require(tm["subcells"]==1 and tm["steps"]==steps, "Time certificate changed")
    path=rk4_path(src,src.initial_state(tuple(SHEAR)),.08,steps,backend="python_oracle")
    path_sha=_binpath(path.coefficients)
    predecessor_sha=tm["path_sha256"]["coefficients"]
    require(predecessor_sha==cert["parent_path_coefficients_sha256"],
            "Original predecessor certified path SHA inconsistency")
    # This exact decimal certificate is an upward rounding of the historical
    # exact-rational source-only term + 246* the original binary64 outward
    # path ell bound. Recheck before using EITHER historical or fresh path.
    source_only=Fraction(lc["source_only_cross_kernel_error"])
    original_bound=source_only+246*Fraction.from_float(float(tm["final_ell_upper"]))
    require(ceil_decimal(original_bound)==cert["total_cross_kernel_upper_ceil_27"],
            "Invalid frozen PR270 exact-real positive l4 bound")
    # Different GitHub CPU runners can regenerate different exact-binary
    # Hermite coefficient arrays from the SAME deterministic physical inputs.
    # Never borrow the predecessor path proof for a distinct byte identity.
    # Re-run the original MPFR192 residual/Dini certificate only for the
    # newly produced path, then compose with the unchanged EXACT K12 source
    # fraction. This is a targeted constructive repair, not a waived guard.
    new_time=None
    if path_sha==predecessor_sha:
        epsilon_decimal=cert["total_cross_kernel_upper_ceil_27"]
        path_certification="DIRECT_BYTE_IDENTICAL_PREDECESSOR_REUSE"
        active_h_upper=tm["final_h_upper"]
    else:
        new_time=_certify_same_source(src,load_donor(order),order,steps,subcells=1)
        require(new_time["path_sha256"]["coefficients"]==path_sha
                and new_time["source_ray_sha256"]==actual[0]
                and new_time["source_mass_sha256"]==actual[1]
                and new_time["physical_source_sha256"]==SOURCE_SHA
                and new_time["steps"]==steps
                and new_time["target_h"]==1e-5 and new_time["target_met"],
                "Fresh runner path MPFR192 recertification binding failed")
        fresh_ell=Fraction.from_float(float(new_time["final_ell_upper"]))
        require(fresh_ell>0 and fresh_ell<Fraction(1,100000),
                "Fresh path ell envelope invalid")
        epsilon_decimal=ceil_decimal(source_only+246*fresh_ell)
        path_certification="NEW_BYTE_PATH_FRESH_WHOLE_PANEL_MPFR192_CERTIFIED"
        active_h_upper=new_time["final_h_upper"]
    ell0,ellT=endpoints_exact_binary_hermite(path)
    pi=exact_pi()
    E0,a0,x0=l4_endpoint(src,ell0,pi)
    ET,aT,xT=l4_endpoint(src,ellT,pi)
    k00,k0T,kTT=kernel(x0,x0),kernel(x0,xT),kernel(xT,xT)
    require(k00.lower>0 and k0T.lower>0 and kTT.lower>0,
            "Positive K4 Gram principal entries premise failed")
    eps=I.decimal(epsilon_decimal)
    require(eps.lower>0 and eps.upper<1e-3,
            "Invalid frozen PR270 exact-real positive l4 bound")
    require(cert["valid_for_both_epochs"].startswith("all u,v"),
            "Original exact-real bound domain changed")
    A=k00-eps
    B=kTT-eps
    C=k0T+eps
    require(A.lower>0 and B.lower>0 and C.lower>0,
            "Two-time positive diagonal/overlap condition failed")
    determinant_lower=(A*B-C*C).lower
    determinant_upper=((k00+eps)*(kTT+eps)-(k0T-eps)*(k0T-eps)).upper
    eigen2_lower=((A*B-C*C)/(k00+kTT+I(2)*eps)).lower if determinant_lower>0 else None
    # Diagnostic-only original Rust binary64 sky, not an interval input.
    name=f"GL{order}_STEPS{steps}"
    filename=f"{name}_BASS_RUST_SKY.csv"
    sky_path=INPUT/filename
    require(hashlib.sha256(sky_path.read_bytes()).hexdigest()
            ==prior["input_file_sha256"][filename],
            "Original Rust saved sky CSV changed")
    rows=read_rows(sky_path)
    _,_,_,numeric_K=sky_modes(rows)
    rust_centers=[float(numeric_K[0,0]),float(numeric_K[0,-1]),float(numeric_K[-1,-1])]
    exact_mpf_iv=[k00,k0T,kTT]
    diagnostics=[abs(z-(v.lower+v.upper)/2) for z,v in zip(rust_centers,exact_mpf_iv)]
    require(max(diagnostics)<2e-12, "Original Rust center vs MPFR exact-real sky discrepancy")
    return {
        "case":name,"source_rays":6*order*order,
        "path_coefficients_binary_git_sha256":path_sha,
        "predecessor_path_coefficients_sha256":predecessor_sha,
        "path_time_certificate_binding":path_certification,
        "active_path_h_certified_upper":active_h_upper,
        "fresh_runner_path_MPFR192_full_time_proof":new_time,
        "original_Rust_CSV_SHA256":hashlib.sha256(sky_path.read_bytes()).hexdigest(),
        "original_strict_h_target":1e-5,"old_h_certified_upper":tm["final_h_upper"],
        "MPFR_bits":BITS,"MPFR_pi":"directed_mpfr_const_pi",
        "stored_gl_source_semantics":"exact dyadic rays/masses; exact-real original binary Hermite cubic",
        "saved_rust_binary64_sky_role":"diagnostic ONLY",
        "rust_vs_exact_stored_MPFR_midpoint_max_abs":max(diagnostics),
        "E0_MPFR_lower":E0.lower,"ET_MPFR_lower":ET.lower,
        "stored_exact_real_K4_intervals":[
            {"lower":v.lower,"upper":v.upper} for v in exact_mpf_iv
        ],
        "PR270_source_plus_geometry_exact_upper_decimal":epsilon_decimal,
        "PR270_original_path_upper_decimal":cert["total_cross_kernel_upper_ceil_27"],
        "continuum_two_time_minor_lower_outward":determinant_lower,
        "continuum_two_time_minor_upper_outward":determinant_upper,
        "continuum_two_time_minor_strict_positive":bool(determinant_lower>0),
        "continuum_two_time_principal_lambda_min_lower_outward":eigen2_lower,
        "continuum_second_mode_rank_at_least_two_certified_if_parent_claim_valid":
            bool(determinant_lower>0),
        "ensemble_covariance":False,
        "whole_program_formal_correctness":"NOT_RUN",
    }


def run(output: Path, *, orders=(6,8), steps=(4,8,16)):
    t,l4,prior=source_and_time_locks()
    results={}
    for n in orders:
        for k in steps:
            row=certify_pair(n,k,t,l4,prior)
            results[row["case"]]=row
            print("CE1AA_ORIGINAL_BASS_MPFR192",
                  row["case"],"Dlower",f'{row["continuum_two_time_minor_lower_outward"]:.17g}',
                  "rank2",row["continuum_two_time_minor_strict_positive"],flush=True)
    for key in ("GL6_STEPS16","GL8_STEPS16"):
        if key in results:
            require(results[key]["continuum_two_time_minor_strict_positive"],
                    "New exact-real continuum non-collinearity gate NOT MET")
    record={
        "schema":"bass.ce1aa.two_epoch_original_sky_mpfr192.v1",
        "source_sha256":SOURCE_SHA,"original_BASS_Rust_blob":RUST_BLOB,
        "PR270_parent_head":"9141d6dcfc66e721fa30390d697f6cd982244eae",
        "PR272_parent_head":"cd597ace92dabafa71a59779242910c3cbcd21c7",
        "theorem":"For a symmetric PSD exact continuum K4(u,v), strict positive principal minor at 0,T implies rank>=2",
        "proof_dependency":"Source/geometry continuum-vs-exact stored path from PR270; MPFR192 directly encloses stored GL sky from immutable binary rays and cubic path",
        "result_scope":"Conditional rigorous numerical certificate for fixed original expanding collisionless Bianchi I physical continuum",
        "this_run_new_directed_MPFR192_stored_sky":True,
        "original_K12_source_rerun":False,
        "full_time_residual_when_regenerated_path_sha_differs":
            "TARGETED_SCOPED_MPFR192_RECERTIFICATION_ONLY_ON_BYTE_MISMATCH",
        "original_h_target_unchanged":1e-5,"unmerged":True,
        "upper_dag":"9/15","ce1":"PARTIAL","new_upper_nodes":0,
        "production_ready":False,"merge_ready":False,"auto_next":False,
        "native_subagent":"NOT_RUN","distinct_author_R6_C9":"NOT_RUN",
        "whole_python_rust_mpfr_formal_program_proof":"NOT_RUN",
        "cases":results,
    }
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(record,indent=2,sort_keys=True,allow_nan=False)+"\n")
    return record


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",type=Path,required=True)
    ns=ap.parse_args()
    run(ns.output)


if __name__=="__main__":
    main()
