#!/usr/bin/env python3
"""Original Type II 401-state, 26-ray normal Liouville and conditional Thomson optical depth.
No production mutation; source-locked original Rust Liouville comparator, no Saha claim.
"""
import csv
import importlib.util
import io
import json
import os
import subprocess
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import CubicHermiteSpline

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
ORIGINAL_MAIN="9c6506e4e2087129a8b674ff10438e5db1a55c9d"
SOURCE_LOCK=ROOT/"research/typeii_host_preflight_20261101/SOURCE_LOCK.json"
SRC_FIX=ROOT/"compiler/validation/typeii_fixture_canonical.json"
COMPARATOR=ROOT/"research/typeii_aem2_compare_20261101/source/replay_from_original_fixture.py"
EXTRA_ORIGINAL=[
 "runtime/rust/typeii/typeii_polarized_liouville.rs",
 "runtime/rust/typeii/typeii_physical_guard.rs",
 "generated/rust/typeii/typeii_polarized.rs",
 "generated/rust/typeii/typeii_collision.rs",
 "bianchi/q/electron_rate.py",
 "bianchi/rays/geodesics.py",
]
def git(*args):
    return subprocess.check_output(["git","-C",str(ROOT),*args],text=True).strip()
lock=json.loads(SOURCE_LOCK.read_text())["original_git_blobs_sha1"]
for path,expect in lock.items():
    actual=git("hash-object",path)
    if actual!=expect:raise RuntimeError(f"ORIGINAL_9_BLOB_DRIFT {path}")
for path in EXTRA_ORIGINAL:
    if git("hash-object",path)!=git("rev-parse",ORIGINAL_MAIN+":"+path):
        raise RuntimeError(f"ORIGINAL_EXTRA_BLOB_DRIFT {path}")
if git("hash-object",str(COMPARATOR.relative_to(ROOT)))!=git(
    "rev-parse","b5a64ff1be8038beb5ef339715ecd9af03a428c2:"+str(COMPARATOR.relative_to(ROOT))
):
    raise RuntimeError("PARENT_324_GRID_SOURCE_DRIFT")

source=json.loads(SRC_FIX.read_text())
rows=source["trajectory"]["samples"]
assert len(rows)==401 and source["trajectory"]["contract"]["gamma"]==1.3
tau=np.array([r["tau"] for r in rows],float)
states=np.array([r["state"] for r in rows],float)
derivs=np.array([r["rhs"] for r in rows],float)
assert np.max(abs(np.diff(tau)-.0005))<1e-14
state_interp=CubicHermiteSpline(tau,states,derivs,axis=0)
state_prime=state_interp.derivative()

spec=importlib.util.spec_from_file_location("parent_source_grid",COMPARATOR)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
directions,weights=m.grid("lebedev26")
assert len(directions)==26 and abs(weights.sum()-4*np.pi)<1e-14
SQ3=np.sqrt(3.)
anchors=np.asarray(source["opacity_model"]["anchors"],float)
proxy_coeff=np.polyfit(anchors[:,0],np.log(anchors[:,1]),2)
def proxy(t):
    return float(np.exp(np.polyval(proxy_coeff,t)))

def original_source_equiv_coeff(state,direction):
    x=np.asarray(state,float)
    n=np.asarray(direction,float)
    n=n/np.linalg.norm(n)
    sp,sm,s13,N1,v=x
    Sigma=np.array([[-2*sp,0,SQ3*s13],
                    [0,sp+SQ3*sm,0],
                    [SQ3*s13,0,sp-SQ3*sm]])
    N=np.diag([N1,0.,0.])
    R=np.array([0.,SQ3*s13,0.])
    Sn=Sigma@n
    snn=float(n@Sn)
    ndot=-Sn+snn*n+np.cross(R,n)-np.cross(n,N@n)
    logE=-1-snn
    gam=1/np.sqrt(1-v*v)
    q=1-v*n[1]
    D=gam*q
    return ndot,logE,gam,q,D

def dlogD(v,vp,ny,nyp):
    return v*vp/(1-v*v)-(vp*ny+v*nyp)/(1-v*ny)

def system(t,y,curvature_sign=-1.0):
    x=state_interp(t)
    n=y[:3]/np.linalg.norm(y[:3])
    ndot,logE,gam,q,D=original_source_equiv_coeff(x,n)
    if curvature_sign!= -1.0:
        N=np.diag([x[3],0.,0.])
        ndot=ndot+(curvature_sign+1.0)*np.cross(n,N@n)
    vp=float(state_prime(t)[4])
    rest_logE=logE+dlogD(float(x[4]),vp,float(n[1]),float(ndot[1]))
    return np.array([*ndot,logE,4*logE,rest_logE,D,proxy(t)*D,q],float)

def initial(n):
    v=float(states[0,4]);D=(1-v*n[1])/np.sqrt(1-v*v)
    return np.array([*n,0.,0.,np.log(D),0.,0.,0.])
def integrate(n,rtol=3e-11,atol=3e-13,max_step=.005,curvature_sign=-1.0):
    sol=solve_ivp(
       lambda t,y:system(t,y,curvature_sign),
       (float(tau[0]),float(tau[-1])),initial(n),
       t_eval=tau,method="DOP853",rtol=rtol,atol=atol,max_step=max_step,
    )
    if not sol.success or sol.y.shape!=(9,len(tau)):
        raise RuntimeError("PHOTON_IVP_FAILURE "+sol.message)
    return sol.y.T,sol.nfev

data=[];nfevs=[]
for direction in directions:
    y,nfev=integrate(direction)
    data.append(y);nfevs.append(nfev)
data=np.stack(data) # [26,401,9]
n=data[:,:,0:3]
norm=np.linalg.norm(n,axis=2)
logE=data[:,:,3];logI=data[:,:,4];logEe=data[:,:,5]
unit_tau=data[:,:,6];conditional_proxy_tau=data[:,:,7];q_only_tau=data[:,:,8]
state_v=states[:,4][None,:]
D_analytic=(1-state_v*n[:,:,1])/np.sqrt(1-state_v*state_v)
rest_chain_defect=float(np.max(abs(logEe-logE-np.log(D_analytic))))
bolometric_defect=float(np.max(abs(logI-4*logE)))
norm_defect=float(np.max(abs(norm-1.0)))
assert norm_defect<2e-10
assert rest_chain_defect<2e-9
assert bolometric_defect<2e-10
assert np.min(unit_tau)>-1e-13
assert np.min(conditional_proxy_tau)>-1e-12

# Compiled actual original Type-II Rust Liouville coefficient source on all 401x26 evolved rays.
sourcelines=[]
pythoncoeff=[]
for k,row in enumerate(rows):
    x=np.asarray(row["state"],float)
    for j in range(len(directions)):
        v=n[j,k,:]
        sourcelines.append(",".join(format(float(z),".17g") for z in list(x)+list(v)))
        nd,lg,gam,q,D=original_source_equiv_coeff(x,v)
        pythoncoeff.append([*nd,lg,4*lg,gam,q,D])
blob="\n".join(sourcelines)+"\n"
environment=dict(os.environ)
environment["CARGO_TARGET_DIR"]="/tmp/bass_typeii_fullcore_target"
environment["CARGO_BUILD_JOBS"]="4"
cmd=["cargo","run","--locked","--offline","--quiet","--example","typeii_photon_sweep"]
cp=subprocess.run(cmd,cwd=str(ROOT/"_rustcore"),input=blob,text=True,
                  stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=environment,timeout=180)
if cp.returncode:
    raise RuntimeError(f"COMPILED_SOURCE_ORACLE_EXIT_{cp.returncode} {cp.stderr[-2000:]}")
original=np.loadtxt(io.StringIO(cp.stdout),delimiter=",")
pythoncoeff=np.array(pythoncoeff)
if original.shape != pythoncoeff.shape or original.shape!=(401*26,8):
    raise RuntimeError(f"RUST_SOURCE_ORACLE_BAD_SHAPE {original.shape}")
col_errors=np.max(abs(original-pythoncoeff),axis=0)
max_source_gap=float(col_errors.max())
assert max_source_gap<2e-12,max_source_gap

# Fail-closed negative examples, comparing physical source-owned choices.
probe=next((j for j,a in enumerate(directions) if abs(a[0])>.1 and abs(a[1])>.1),None)
assert probe is not None
wrong,_=integrate(directions[probe],curvature_sign=+1.0)
wrong_curvature_final=float(np.max(abs(wrong[-1,:3]-data[probe,-1,:3])))
assert wrong_curvature_final>1e-3
missing_gamma_final=float(np.max(abs(unit_tau[:,-1]-q_only_tau[:,-1])))
assert missing_gamma_final>1e-4

endnormal_E=np.exp(logE[:,-1])
endbolometric=np.exp(logI[:,-1])
endrest_E=np.exp(logEe[:,-1])
out={
 "schema":"bass.original_typeii.normal_liouville_optical_depth.401x26.v1",
 "source_main":ORIGINAL_MAIN,
 "parent_head":"b5a64ff1be8038beb5ef339715ecd9af03a428c2",
 "source_locked_original_9":9,
 "source_locked_extra_original":len(EXTRA_ORIGINAL),
 "characteristics":len(directions),"background_samples":len(tau),
 "flow_time":"tau_H; d tau_H=H dt_normal; 0..0.2; forward normal photon ray",
 "method":"DOP853 CubicHermiteSpline original state and original RHS",
 "normal_rate":"unit electron-rest proper opacity per Hubble time, D=Gamma q; not native n_e",
 "proxy_rate":"3-anchor receipt-conditioned opacity assumed rest-frame scalar only for sensitivity, NOT native SahaHistory",
 "rust_source_oracle_evaluations":int(original.shape[0]),
 "rust_source_max_column_abs_gaps":col_errors.tolist(),
 "rust_source_max_abs_gap":max_source_gap,
 "direction_unit_norm_max_defect":norm_defect,
 "normal_bolometric_log_identity_max_defect":bolometric_defect,
 "electron_doppler_log_chain_max_defect":rest_chain_defect,
 "endpoint_E_normal_min":float(endnormal_E.min()),
 "endpoint_E_normal_max":float(endnormal_E.max()),
 "endpoint_I_normal_min":float(endbolometric.min()),
 "endpoint_I_normal_max":float(endbolometric.max()),
 "endpoint_E_electron_min":float(endrest_E.min()),
 "endpoint_E_electron_max":float(endrest_E.max()),
 "unit_proper_optical_depth_min":float(unit_tau[:,-1].min()),
 "unit_proper_optical_depth_max":float(unit_tau[:,-1].max()),
 "conditional_proxy_optical_depth_min":float(conditional_proxy_tau[:,-1].min()),
 "conditional_proxy_optical_depth_max":float(conditional_proxy_tau[:,-1].max()),
 "negative_wrong_curvature_sign_endpoint_direction_gap":wrong_curvature_final,
 "negative_missing_gamma_endpoint_optical_depth_gap":missing_gamma_final,
 "nfev_min":min(nfevs),"nfev_max":max(nfevs),
 "claim_gate":"SOURCE_CONDITIONAL_CHARACTERS_NUMERICALLY_CHECKED; no production runtime dispatcher or real electron n_e history",
}
outpath=HERE/"PHOTON_RAYS_RESULT.json"
outpath.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")

with (HERE/"PHOTON_RAYS_401X26.csv").open("w",newline="") as f:
    writer=csv.writer(f, lineterminator="\n")
    writer.writerow(["ray_id","tau_H","n_x","n_y","n_z","ln_E_normal","ln_I_normal",
                     "ln_E_electron","optical_depth_unit_proper_rate","optical_depth_proxy_if_proper",
                     "optical_depth_q_only_wrong"])
    for j in range(len(directions)):
        for k,t in enumerate(tau):
            y=data[j,k]
            writer.writerow([j,format(float(t),".17g")]+
                            [format(float(a),".17g") for a in y])
print(json.dumps(out,indent=2,sort_keys=True))
