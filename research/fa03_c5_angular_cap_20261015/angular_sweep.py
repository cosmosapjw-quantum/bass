#!/usr/bin/env python3
"""Executable FA03 fixed-detector versus angular-resolution study.

This is a C5 implementation and exploratory angular convergence study, NOT a
rigorous continuous-cap quadrature enclosure. Original FA03 R7 numerical
certificate applies only to unchanged GL3x12 nodes, and remains immutable.

References fa02.py/fa03.py are byte-identical source copies from R7 archive.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
from numpy.polynomial.legendre import leggauss

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "reference"))
import fa02  # noqa: E402
import fa03  # noqa: E402

SOURCE_LOCKS = {
    "fa02.py": "1e89e75f7a08d2eec1851a58e602c2683b1888a37b3e1fe10b1be4234756eee5",
    "fa03.py": "ad865127da7c2f9ea613541571f9b842f9da7630af9bb951a3df5968ad44ecf7",
}
CERTIFIED_R7 = ROOT / "reference" / "R7_MAIN_CERTIFICATE.json"
CERTIFIED_R7_SHA256 = "cac2515682821deebe7eb30770a27b30dc7576522c3a1f6101ef0e70e2486adc"

def verify_source_lock() -> dict[str, str]:
    checks = {}
    for filename, expected in SOURCE_LOCKS.items():
        actual = hashlib.sha256((ROOT / "reference" / filename).read_bytes()).hexdigest()
        if actual != expected:
            raise RuntimeError(f"SOURCE_IDENTITY_MISMATCH:{filename}")
        checks[filename] = actual
    return checks


def cap_nodes(nr: int, nphi: int, phase: float = 0.0, delta: float = 0.02):
    if not isinstance(nr, int) or not isinstance(nphi, int) or nr < 2 or nphi < 8:
        raise ValueError("nr>=2 and nphi>=8 required for diagnostic")
    if not (np.isfinite(phase) and 0 < delta <= .02):
        raise ValueError("real finite cap phase, 0<delta<=0.02")
    t, w = leggauss(nr)
    # cos(r) is affine in t; exact normalized area measure.
    r = 2 * np.arcsin(np.sqrt((t + 1) / 2) * np.sin(delta / 2))
    phi = np.arange(nphi) * 2 * np.pi / nphi + phase * (2 * np.pi / nphi)
    rr, pp = np.meshgrid(r, phi, indexing="ij")
    ell = np.stack([np.cos(rr), np.sin(rr)*np.cos(pp), np.sin(rr)*np.sin(pp)], axis=-1).reshape(-1, 3)
    weights = np.repeat(w / (2 * nphi), nphi)
    assert len(weights) == len(ell)
    return ell, weights


def solve_six_at_nodes(ell: np.ndarray, w: np.ndarray, steps: int, chi=.008, psi=.01):
    if not isinstance(steps, int) or steps < 2:
        raise ValueError("at least 2 RK4 steps")
    if not np.isfinite([chi, psi]).all() or max(abs(chi),abs(psi))>.02:
        raise ValueError("source family observer bound")
    data = fa02.setup(ell, chi, psi)
    ys = [np.zeros((len(ell), 2, 2), complex) for _ in range(6)]
    h = .5 / steps
    def advance(a, b, fac):
        return [v + fac * dv for v, dv in zip(a, b)]
    for i in range(steps):
        x = .5 + h*i
        a = fa03._rhs(x, ys, data)
        b = fa03._rhs(x + h/2, advance(ys, a, h/2), data)
        c = fa03._rhs(x + h/2, advance(ys, b, h/2), data)
        d = fa03._rhs(x + h, advance(ys, c, h), data)
        ys = [v + h*(av+2*bv+2*cv+dv)/6 for v,av,bv,cv,dv in zip(ys,a,b,c,d)]
    return np.stack([np.einsum("n,nij->ij",w,y) for y in ys])


def stokes(mat):
    return np.array([np.trace(mat).real,
                     (mat[0,0] - mat[1,1]).real,
                     2*mat[0,1].real, -2*mat[0,1].imag])

def trnorm(mat):
    return float(np.linalg.svd(mat, compute_uv=False).sum())


def polynomial(ys, eps):
    return ys[0] + eps * ys[3] + .5 * eps * eps * ys[5]


def energy_solve_at_nodes(ell, w, eps, steps, ne):
    if abs(eps) > .1 or ne < 2:
        raise ValueError("finite epsilon range or insufficient energy quadrature")
    en, we = leggauss(ne)
    en, we = 1+.02*en, we/2
    data=fa02.setup(ell,.008,.01)
    F=np.zeros((len(ell), ne, 2,2),complex)
    h=.5/steps
    def rhs(x, F):
        P,H,G,k=fa03.fields(x,data)
        B=(en[None,:]**3*(1+.1*en[None,:]*k[:,None]))[...,None,None]*P[:,None]
        Ge=G[:,None]+eps*(en[None,:]*k[:,None]-1)[...,None,None]*H[:,None]
        return B-Ge@F-F@Ge.swapaxes(-1,-2)
    for j in range(steps):
        x=.5+j*h
        a=rhs(x,F)
        b=rhs(x+h/2,F+h*a/2)
        c=rhs(x+h/2,F+h*b/2)
        d=rhs(x+h,F+h*c)
        F=F+h*(a+2*b+2*c+d)/6
    return np.einsum("n,e,neij->ij",w,we,F)


def geometric_checks(ell, weights, delta=.02):
    mu=ell[:,0]
    c=math.cos(delta)
    checks={"sum_weights":float(sum(weights)),
        "cos_theta_first_moment":float(weights@mu),
        "cos_theta_first_exact":(1+c)/2,
        "cos_theta_second_moment":float(weights@(mu*mu)),
        "cos_theta_second_exact":(1+c+c*c)/3,
        "min_sqrt_1_minus_m_y_squared":None}
    data=fa02.setup(ell,.008,.01)
    m=data[4]
    checks["min_sqrt_1_minus_m_y_squared"]=float(np.sqrt(np.maximum(0,1-m[:,1]**2)).min())
    checks["max_weight"]=float(weights.max())
    checks["min_weight"]=float(weights.min())
    return checks


def r7_fixed_reference() -> dict:
    if hashlib.sha256(CERTIFIED_R7.read_bytes()).hexdigest() != CERTIFIED_R7_SHA256:
        raise RuntimeError("R7_CERTIFICATE_IDENTITY_MISMATCH")
    record=json.loads(CERTIFIED_R7.read_text())
    if record.get("rays") != 36 or record.get("cells_per_ray") != 64:
        raise RuntimeError("R7_CERTIFICATE_SCOPE_MISMATCH")
    return record


def run_study(steps=128, grids=((2,8),(3,12),(4,16),(6,24),(10,48),(14,64)), energy_ne=(8,16)):
    verify_source_lock()
    if steps < 64 or steps % 2:
        raise ValueError("steps must be even and >=64")
    if len(energy_ne) != 2 or energy_ne[0]<2 or energy_ne[1]<energy_ne[0]:
        raise ValueError("energy orders must be >=2 and increasing")
    start=time.monotonic()
    ref=r7_fixed_reference()
    records=[]
    results={}
    for nr,nphi in grids:
        ell,w=cap_nodes(nr,nphi)
        checked=geometric_checks(ell,w)
        begin=time.monotonic()
        state=solve_six_at_nodes(ell,w,steps)
        row={"nr":nr,"nphi":nphi,"ray_count":len(w),"steps":steps,
             "source_span_at_x_point7":None,
             "area_checks":checked,
             "states_stokes":[stokes(x).tolist() for x in state],
             "seconds":time.monotonic()-begin}
        P,_,_,_=fa03.fields(.7,fa02.setup(ell,.008,.01))
        row["source_span_at_x_point7"]=float(np.ptp(P[:,0,0].real))
        records.append(row)
        results[(nr,nphi)]=state
    base=results[(3,12)]
    assert (3,12) in grids
    for row in records:
        state=results[(row["nr"],row["nphi"])]
        row["delta_to_gl3x12_trace_norm"]=[trnorm(a-b) for a,b in zip(state,base)]
        row["stokes_I_relative_diff"]=(stokes(state[0])[0]-stokes(base[0])[0])/stokes(base[0])[0]
        row["numerical_angular_error_certified"]=False
    # Reevaluate exact archived 64-step reference rather than claiming
    # the 128-step result is bit-identical to its 64-step certificate.
    ell,w=cap_nodes(3,12)
    ys64=solve_six_at_nodes(ell,w,64)
    old=np.array(ref["reference_stokes_display"],float)
    original_deviation=max(float(np.max(abs(stokes(x)-y))) for x,y in zip(ys64,old))
    time_deviation=[trnorm(x-y) for x,y in zip(base,ys64)]
    rotated_ell,rotated_w=cap_nodes(3,12,phase=.37)
    rotated=solve_six_at_nodes(rotated_ell,rotated_w,steps)
    energies=[]
    energy_grids = [(3,12)]
    high_grid = (10,48) if (10,48) in results else grids[-1]
    if high_grid != (3,12):
        energy_grids.append(high_grid)
    for nr,nphi in energy_grids:
        ell,w=cap_nodes(nr,nphi)
        for eps in [-.1,0,.1]:
            p2=polynomial(results[(nr,nphi)],eps)
            candidates={n:energy_solve_at_nodes(ell,w,eps,steps,n) for n in energy_ne}
            energy_val=candidates[energy_ne[-1]]
            eig=np.linalg.eigvalsh(.5*(energy_val+energy_val.conj().T))
            energies.append({"nr":nr,"nphi":nphi,"eps":eps,"energy_orders":list(energy_ne),
                             "actual_energy_stokes":stokes(energy_val).tolist(),
                             "polynomial_stokes":stokes(p2).tolist(),
                             "finite_epsilon_polynomial_deviation_trace_norm":trnorm(energy_val-p2),
                             "energy_order_difference_trace_norm":trnorm(candidates[energy_ne[0]]-energy_val),
                             "min_coherency_eigenvalue":float(eig.min()),
                             "certified_total_finite_error":None})
    out={"schema":"bass.fa03.c5.angular_cap_empirical.v1",
         "stage":"C5_IMPLEMENTATION_WITH_SCOPED_EXECUTION",
         "source_sha256":SOURCE_LOCKS,
         "fixed_detector":{"nr":3,"nphi":12,"chi":.008,"psi":.01,"delta":.02,
                           "finite_quadrature_certificate":"R7/R8 fixed 36-ray only",
                           "R8_trace_norm_bound":"<4.75e-7 for |epsilon|<=0.1",
                           "rigorous_continuum_angular_error":None},
         "not_scientifically_certified":["continuous angular cap truncation error",
                                       "time Richardson extrapolation",
                                       "energy Gauss order truncation error",
                                       "real atomic opacity or EoR chemistry"],
         "baseline_reference_64steps_max_abs_stokes_deviation":original_deviation,
         "baseline_64_to_current_step_trace_norm":time_deviation,
         "phi_phase_0_vs_point37_radians_trace_norm":[trnorm(x-y) for x,y in zip(base,rotated)],
         "grid_records":records,
         "finite_epsilon_records":energies,
         "runtime_seconds":time.monotonic()-start}
    return out


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--steps",type=int,default=128)
    parser.add_argument("--out",type=Path,default=ROOT/"evidence"/"ANGULAR_STUDY.json")
    a=parser.parse_args()
    result=run_study(steps=a.steps)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    if a.out.exists():
        raise FileExistsError("immutable study output exists; use a new output path")
    a.out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps({"saved":str(a.out),"elapsed_s":result["runtime_seconds"],
        "max_angular_variance":max(max(r["delta_to_gl3x12_trace_norm"]) for r in result["grid_records"]),
        "max_energy_order_difference":max(r["energy_order_difference_trace_norm"] for r in result["finite_epsilon_records"]),
        "max_64_vs_128_temporal_difference":max(result["baseline_64_to_current_step_trace_norm"]),
        "source_identity":result["source_sha256"],
        "angular_certificate":None},indent=2))


if __name__=="__main__":main()
