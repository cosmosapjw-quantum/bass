#!/usr/bin/env python3
"""R7 source-locked local Type II Liouville/Thomson geometry, NO photon Boltzmann evolution."""
import json
import subprocess
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[2]
MAIN="9c6506e4e2087129a8b674ff10438e5db1a55c9d"
SOURCES=[
 "runtime/rust/typeii/typeii_polarized_liouville.rs",
 "runtime/rust/typeii/typeii_physical_guard.rs",
 "generated/rust/typeii/typeii_polarized.rs",
 "generated/rust/typeii/typeii_collision.rs",
 "bianchi/rays/geodesics.py",
 "bianchi/q/electron_rate.py",
 "compiler/validation/typeii_fixture_canonical.json"
]
def cmd(*a):
    return subprocess.check_output(["git","-C",str(ROOT),*a],text=True).strip()
for path in SOURCES:
    if cmd("hash-object",path)!=cmd("rev-parse",MAIN+":"+path):
        raise RuntimeError("ORIGINAL_SOURCE_IDENTITY_MISMATCH "+path)
rows=json.loads((ROOT/SOURCES[-1]).read_text())["trajectory"]["samples"]
if len(rows)!=401 or rows[0]["state"][4]!=0.05:
    raise RuntimeError("NOT_CANONICAL_401")

SQ3=np.sqrt(3.0)
def background(x):
    sp,sm,s13,n1,v=x
    sigma=np.array([[-2*sp,0,SQ3*s13],[0,sp+SQ3*sm,0],
                    [SQ3*s13,0,sp-SQ3*sm]],float)
    nmat=np.diag([n1,0,0])
    R=np.array([0,SQ3*s13,0.],float)
    return sigma,nmat,R
def coefficients(x,n):
    n=np.asarray(n,float)
    if abs(np.linalg.norm(n)-1)>1e-10:raise ValueError("nonunit direction")
    sigma,N,R=background(x)
    sn=sigma@n
    sig=float(n@sn)
    dvec=-sn+sig*n+np.cross(R,n)-np.cross(n,N@n)
    rate=-1-sig
    v=x[4]
    if not np.isfinite(v) or abs(v)>=1:raise ValueError("superluminal")
    gamma=1/np.sqrt(1-v*v)
    q=1-v*n[1]
    return dvec,rate,gamma*q,q,gamma
def bolometric_frame_derivative(x,dx,n,dn):
    v=x[4];vp=dx[4];ny=n[1];nyp=dn[1]
    return v*vp/(1-v*v)-(vp*ny+v*nyp)/(1-v*ny)
def fibonacci(n):
    idx=np.arange(n);h=1-2*(idx+.5)/n
    t=np.pi*(3-np.sqrt(5.0))*idx
    return np.stack([np.sqrt(1-h*h)*np.cos(t),h,np.sqrt(1-h*h)*np.sin(t)],axis=1)
dirs=fibonacci(26)
max_norm=0.;max_trace=0.;min_q=9.;min_D=9.;max_Gamma_minus1=0.; max_ang=0.
for sample in rows:
    x=np.asarray(sample["state"],float)
    sigma,N,R=background(x)
    max_trace=max(max_trace,abs(np.trace(sigma)))
    for n in dirs:
        dn,g,D,q,G=coefficients(x,n)
        max_norm=max(max_norm,abs(n@dn))
        max_ang=max(max_ang,np.linalg.norm(dn))
        min_q=min(min_q,q)
        min_D=min(min_D,D)
        max_Gamma_minus1=max(max_Gamma_minus1,G-1)
x=np.asarray(rows[0]["state"],float);dx=np.asarray(rows[0]["rhs"],float)
n=np.array([1.,1.,1.])/np.sqrt(3.)
dn,r,D,q,G=coefficients(x,n)
curv=np.cross(n,background(x)[1]@n)
h=1e-6
def dlnd(xx,nn):
    vv=float(xx[4]); nn=nn/np.linalg.norm(nn)
    return np.log((1-vv*nn[1])/np.sqrt(1-vv*vv))
finite_diff=(dlnd(x+h*dx,n+h*dn)-dlnd(x-h*dx,n-h*dn))/(2*h)
analytic=bolometric_frame_derivative(x,dx,n,dn)
err=abs(finite_diff-analytic)
bad_sign_gap=float(np.max(abs((-curv)-curv)))
bad_extra_q_gap=abs(D-D*q)
bad_omit_Gamma_gap=abs(D-q)
assert max_norm<1e-13 and max_trace<1e-14 and min_q>0 and min_D>0
assert bad_sign_gap>0.1 and bad_extra_q_gap>1e-2 and bad_omit_Gamma_gap>1e-4
assert err<2e-8
out={
 "schema":"bass.typeii.liouville_thomson.r7.v1",
 "source_main":MAIN,"original_source_git_blobs_verified":len(SOURCES),
 "canonical_rows":len(rows),"probe_directions":len(dirs),
 "max_direction_tangency_defect":max_norm,
 "max_shear_trace_defect":max_trace,
 "max_angular_rate":max_ang,
 "min_q":min_q,"min_D":min_D,
 "max_Gamma_minus_1":max_Gamma_minus1,
 "initial_source_velocity":float(x[4]),
 "initial_source_velocity_prime":float(dx[4]),
 "lnD_chain_finite_difference":finite_diff,
 "lnD_chain_exact":analytic,
 "lnD_chain_max_gap":err,
 "hostile_curvature_wrong_sign_gap":bad_sign_gap,
 "hostile_extra_q_abs_gap":bad_extra_q_gap,
 "hostile_missing_Gamma_abs_gap":bad_omit_Gamma_gap,
 "claim_scope":"local 401x26 coefficient diagnostics, not photon evolution, no Saha"
}
path=Path(__file__).with_name("R7_LOCAL_SOURCE_RESULTS.json")
path.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,sort_keys=True,indent=2))
