#!/usr/bin/env python3
"""R7: BASS Type-II paired-grid amplitude geometry, read-only original source and 401 samples.
Exact source-conditional scalar bolometric scope; NOT a production CMB or Saha result.
"""
from __future__ import annotations
import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REF = ROOT / "research/typeii_aem2_compare_20261101/source/replay_from_original_fixture.py"
FIX = ROOT / "compiler/validation/typeii_fixture_canonical.json"
ORIGINAL_MAIN = "9c6506e4e2087129a8b674ff10438e5db1a55c9d"
EXPECTED_FIX_SHA = "dea22f0fce116b61314b13cea7d0bdd38efe48bc"

def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True).strip()

if git("hash-object", str(FIX.relative_to(ROOT))) != EXPECTED_FIX_SHA:
    raise RuntimeError("SOURCE_FIXTURE_GIT_BLOB_CHANGED")
for rel in ["generated/rust/typeii/typeii_collision.rs",
            "generated/rust/typeii/typeii_kato.rs",
            "generated/rust/typeii/typeii_background.rs"]:
    canonical = git("rev-parse", f"{ORIGINAL_MAIN}:{rel}")
    actual = git("hash-object", rel)
    if actual != canonical:
        raise RuntimeError(f"ORIGINAL_SOURCE_DRIFT_{rel}")
s = importlib.util.spec_from_file_location("original_bass_comparison", REF)
owner_module = importlib.util.module_from_spec(s)
s.loader.exec_module(owner_module)
m = owner_module
owner = m.Owner()
j = json.loads(FIX.read_text())
rows = j["trajectory"]["samples"]
assert len(rows) == 401
assert rows[0]["state"][4] == 0.05
PI = np.pi
TOL = 1e-11
out = {
    "schema": "bass.typeii.paired_kato.amplitude_theory.r7.v1",
    "source_main": ORIGINAL_MAIN,
    "fixture_git_blob": EXPECTED_FIX_SHA,
    "model": "prescribed 401-step Type-II gamma-law state, scalar finite-tilt Thomson, no backreaction",
    "tests": {},
    "grids": {},
}
v0 = float(rows[0]["state"][4])
vend = float(rows[-1]["state"][4])
amplitude_ratio = ((1.0-vend*vend)/(1.0-v0*v0))**2
out["v0"] = v0
out["vend"] = vend
out["tau_end"] = float(rows[-1]["tau"])
out["kato_amplitude_ratio_exact"] = amplitude_ratio
out["kato_amplitude_change_minus_one"] = amplitude_ratio-1.0

def paired_formula(e,w,v):
    mu = e[:,1]
    one = 1.0-v*v
    r = (1.0+v*mu)**4 / (one**2)
    a = (w/(4.0*PI)) * one**2 / (1.0+v*mu)**3
    return r,a

def derivs(e,w,v,vdot):
    mu = e[:,1]
    r,a = paired_formula(e,w,v)
    dr = r * (4.0*v/(1.0-v*v)+4.0*mu/(1.0+v*mu))*vdot
    da = a * (-4.0*v/(1.0-v*v)-3.0*mu/(1.0+v*mu))*vdot
    return dr, da

for gridname in ("axis6","lebedev26"):
    e,w = m.grid(gridname)
    assert abs(np.sum(w)/(4*PI)-1.0)<2e-15
    assert abs(np.dot(w,e[:,1]))<2e-15
    assert np.max(abs(np.einsum("i,ij,ik->jk",w,e,e) - (4*PI/3)*np.eye(3)))<5e-15
    maxima = {"r_exact_gap":0.0, "a_exact_gap":0.0, "s_minus_one":0.0,
              "Cr":0.0, "aC":0.0, "K_r":0.0,"H_r":0.0,
              "moment_H_random":0.0, "Pdot_complexstep_gap":0.0}
    for ix,row in enumerate(rows):
        v=float(row["state"][4])
        vdot=float(row["rhs"][4])
        C,P,_,_,r,a = m.cp(e,w,v,"paired")
        rf,af=paired_formula(e,w,v)
        dr,da=derivs(e,w,v,vdot)
        s=float(a@r)
        assert s>0.0
        pdot=(np.outer(dr,a)+np.outer(r,da))/s - P*((da@r+a@dr)/s)
        K=pdot@P-P@pdot
        lam=(a@dr)/s
        H=K+lam*P
        y=np.arange(1,len(r)+1,dtype=float)/(len(r)+2.0)
        now={"r_exact_gap":np.max(abs(r-rf)),
             "a_exact_gap":np.max(abs(a-af)),
             "s_minus_one":abs(s-1.0),
             "Cr":np.max(abs(C@r)),
             "aC":np.max(abs(a@C)),
             "K_r":np.max(abs(K@r-(dr-lam*r))),
             "H_r":np.max(abs(H@r-dr)),
             "moment_H_random":abs(da@y+a@(H@y))}
        if ix in (0,200,400):
            now["Pdot_complexstep_gap"]=np.max(abs(pdot-vdot*m.pv(e,w,v,"paired")))
        for k,value in now.items():
            maxima[k]=max(maxima[k],float(value))
    for field,value in maxima.items():
        if value>TOL: raise ArithmeticError(f"FAIL {gridname} {field} {value}")
    out["grids"][gridname]={"rows":len(rows),"maxima":maxima}
out["tests"]["all_401_source_paired_checks"] = "PASS"

# Independent integrator check at the original Type-II trajectory's variable opacity proxy.
e,w=m.grid("axis6")
def matrices(t):
    v=float(owner.trajectory(t)[4])
    vdot=float(owner.trajectory.derivative()(t)[4])
    C,P,_,_,r,a=m.cp(e,w,v,"paired")
    dr,da=derivs(e,w,v,vdot)
    denom=float(a@r)
    pdot=(np.outer(dr,a)+np.outer(r,da))/denom-P*((da@r+a@dr)/denom)
    K=pdot@P-P@pdot
    lam=float(a@dr)/denom
    return C,K,P,lam,r,a
def integrate(center):
    def fun(t,y):
        C,K,P,lam,*_=matrices(t)
        return (owner.rate(t)*C+K+(lam*P if center else 0.0))@y
    r0=matrices(0.0)[4]
    sol=solve_ivp(fun, (0.0,0.2),r0,method="DOP853",atol=2e-13,rtol=3e-11,max_step=0.005)
    if not sol.success:raise RuntimeError(sol.message)
    return sol.y[:,-1],int(sol.nfev)
for center in (False,True):
    y,nfev=integrate(center)
    *_,rend,aend=matrices(0.2)
    expected=rend * (1.0 if center else amplitude_ratio)
    maxgap=float(np.max(abs(y-expected)))
    invariant=float(aend@y)
    record={"rhs_evaluations":nfev,"final_state_max_gap":maxgap,
            "a_transpose_y_final":invariant,
            "expected_a_transpose_y_final":1.0 if center else amplitude_ratio}
    if maxgap>5e-9 or abs(invariant-record["expected_a_transpose_y_final"])>5e-9:
        raise ArithmeticError(f"IVP_MISMATCH {center} {record}")
    out["tests"]["center_calibrated" if center else "pure_kato"]=record
out["tests"]["non_symm_control"]="not part of eligible paired quadrature; no invalid normalization promoted"
print(json.dumps(out,indent=2,sort_keys=True))
(HERE/"R7_NUMERIC_RESULTS.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
