#!/usr/bin/env python3
"""Native FLRW HYREC-2 H/He x_e(z) conditionally mapped onto original BASS Type-II 401x26 rays.

No native HYREC H(z)->Bianchi H(z) self-consistency claim. The time-varying
ionization fraction is an external scalar lookup on the declared mean z label.
"""
from __future__ import annotations
import csv
import hashlib
import json
import math
from pathlib import Path
import subprocess
import numpy as np
from scipy.interpolate import PchipInterpolator, CubicHermiteSpline, CubicSpline
from numpy.polynomial.legendre import leggauss
from scipy.integrate import quad, solve_ivp

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PARENT_SHA="0bee79382753d95c610f5e86431f9e7c318c27d5"
ORIGINAL_MAIN="9c6506e4e2087129a8b674ff10438e5db1a55c9d"
REFERENCE_RAY_SHA="9f1400588d39ba3a61020542e14b0e372c8e9be1af130f8c64ed8829b23ad217"
def check(ok,name):
    if not bool(ok):raise RuntimeError(name)
def git(*args):
    return subprocess.check_output(["git","-C",str(ROOT),*args],text=True).strip()
def hsh(path):return hashlib.sha256(path.read_bytes()).hexdigest()

locks=json.loads((ROOT/"research/typeii_host_preflight_20261101/SOURCE_LOCK.json").read_text())["original_git_blobs_sha1"]
for path,sha in locks.items():
    check(git("hash-object",path)==sha,"ORIGINAL_SOURCE_BLOB_MISMATCH_"+path)
parent_paths=["research/typeii_conserved_saha_20261102/HYDROGEN_SAHA_HISTORY_401.csv",
              "research/typeii_conserved_saha_20261102/PHYSICAL_SAHA_THOMSON_SUMMARY.json",
              "research/typeii_conserved_saha_20261102/SAHA_THOMSON_RAYS_401X26.csv",
              "compiler/validation/typeii_fixture_canonical.json"]
for rel in parent_paths:
    check(git("hash-object",rel)==git("rev-parse",PARENT_SHA+":"+rel),
          "PARENT_CALIBRATED_SOURCE_CHANGED_"+rel)
ray_path=ROOT/"research/typeii_liouville_optdepth_20261101/PHOTON_RAYS_401X26.csv"
check(hsh(ray_path)==REFERENCE_RAY_SHA,"ORIGINAL_10426_RAYS_SHA_MISMATCH")
hyrec_report=json.loads((HERE/"HYREC2_NATIVE_SOURCE_REPORT.json").read_text())
native_path=HERE/"HYREC2_FLRW_XE_TM_8000.dat"
check(hsh(native_path)==hyrec_report["published_output_sha256"],
      "NATIVE_HYREC_OUTPUT_CONTENT_DRIFT")
check(hsh(HERE/"HYREC2_FLRW_INPUT_20261102.dat")==hyrec_report["calibrated_input_sha256"],
      "NATIVE_HYREC_COSMOLOGY_INPUT_DRIFT")
hyrec=np.loadtxt(native_path)
check(hyrec.shape==(8000,3) and np.isfinite(hyrec).all(),"HYREC_WRONG_OR_NONFINITE_ROWS")
z0=1700.0
dt=.0005
fixture=json.loads((ROOT/"compiler/validation/typeii_fixture_canonical.json").read_text())
samples=fixture["trajectory"]["samples"]
times=np.asarray([x["tau"] for x in samples],float)
states=np.asarray([x["state"] for x in samples],float)
rhs=np.asarray([x["rhs"] for x in samples],float)
check(states.shape==rhs.shape==(401,5) and max(abs(np.diff(times)-dt))<1e-13,"TYPEII_BACKGROUND_IDENTITY_INVALID")
v2=states[:,4]
V=CubicHermiteSpline(times,v2,rhs[:,4])
with (ROOT/parent_paths[0]).open(newline="") as f:legacy_rows=list(csv.DictReader(f))
check(len(legacy_rows)==401,"PARENT_SAHA_ROWS_INVALID")
def old(name):return np.array([float(r[name]) for r in legacy_rows])
hubble_data=old("H_s_inv")
check(np.all(hubble_data>0),"INVALID_HUBBLE_SOURCE")
H_spline=CubicSpline(times,np.log(hubble_data))
zmean_knots=old("z_mean_not_observed")
zmean_check=(1+z0)*np.exp(-times)-1
check(max(abs(zmean_knots-zmean_check))<3e-11,"MEAN_Z_INPUT_SOURCE_DRIFT")
pchip=PchipInterpolator(np.log1p(hyrec[::-1,0]),hyrec[::-1,1],extrapolate=False)
tmchip=PchipInterpolator(np.log1p(hyrec[::-1,0]),hyrec[::-1,2],extrapolate=False)
# Not correct to use nH0=Saha coefficient (YHe=.24) for native HYREC-2 YHe=.245.
omega_bh2=hyrec_report["input_cosmology"]["Omega_b_h2"]
YHe=hyrec_report["input_cosmology"]["YHe"]
nH0_HyRec=11.223846333047e-6*omega_bh2*(1-YHe) # cm-3, HYREC-2 history.c
gamma_init=1/math.sqrt(1-v2[0]**2)
N_H0=nH0_HyRec*(1+z0)**3*gamma_init
c_cgs=2.99792458e10
sigma_cm2=6.6524587e-25

def physical(t):
    t=np.asarray(t,float)
    check(np.isfinite(t).all() and np.all(t>=times[0]) and np.all(t<=times[-1]),
          "TIME_OUTSIDE_PRESCRIBED_TYPEII_HISTORY")
    v=V(t)
    check(np.isfinite(v).all() and np.all(abs(v)<1),"UNPHYSICAL_TILTED_BACKGROUND")
    gamma=1/np.sqrt(1-v*v)
    z=(1+z0)*np.exp(-t)-1
    check(np.all(z>=hyrec[:,0].min()) and np.all(z<=hyrec[:,0].max()),
          "HYREC_OUTPUT_REDSHIFT_SUPPORT_EXCEEDED")
    xe=pchip(np.log1p(z)); Tm=tmchip(np.log1p(z))
    fHe=YHe/(1-YHe)/3.97153
    check(np.isfinite(xe).all() and np.all((xe>=0)&(xe<=1+2*fHe+1e-8)),
          "HYREC_FREE_ELECTRON_FRACTION_INVALID")
    check(np.isfinite(Tm).all() and np.all(Tm>0),"HYREC_T_MATTER_UNPHYSICAL")
    nHnormal=N_H0*np.exp(-3*t)
    nHrest=nHnormal/gamma
    neRest=xe*nHrest
    H=np.exp(H_spline(t))
    nuNormal= sigma_cm2*c_cgs*xe*nHnormal/H
    nuRest=sigma_cm2*c_cgs*neRest/H
    check(np.max(abs(nuRest*gamma/nuNormal-1))<2e-14,
          "NUMBER_CURRENT_GAMMA_CANCELLATION_MISMATCH")
    return dict(t=t,v=v,gamma=gamma,z=z,xe=xe,Tm=Tm,H=H,
        nHnormal=nHnormal,nHrest=nHrest,neRest=neRest,
        nuRest=nuRest,nuNormal=nuNormal)
phy=physical(times)

# Frozen source photon rays and exact source shear+Type-II spatial curvature direction derivatives.
rays=np.zeros((26,401,3));seen=np.zeros((26,401),bool)
with ray_path.open(newline="") as f:
 for row in csv.DictReader(f):
    j=int(row["ray_id"]); k=round(float(row["tau_H"])/dt)
    check(0<=j<26 and 0<=k<401 and not seen[j,k],"RAY_RECORD_INDEX_INVALID")
    rays[j,k]=[float(row["n_x"]),float(row["n_y"]),float(row["n_z"])]
    seen[j,k]=True
check(np.all(seen),"MISSING_PHOTON_RAY")
nx,ny,nz=(rays[:,:,i] for i in range(3))
sqrt3=math.sqrt(3)
sp,sm,s13,n1=(states[:,i][None,:] for i in (0,1,2,3))
sig_nn=-2*sp*nx*nx+(sp+sqrt3*sm)*ny*ny+(sp-sqrt3*sm)*nz*nz+2*sqrt3*s13*nx*nz
nydot=(sig_nn-(sp+sqrt3*sm))*ny-n1*nx*nz
NY=CubicHermiteSpline(times,ny,nydot,axis=1)
axis_plus=next(j for j in range(26) if np.max(abs(rays[j,0]-[0,1,0]))<1e-14)
axis_minus=next(j for j in range(26) if np.max(abs(rays[j,0]-[0,-1,0]))<1e-14)
check(np.max(abs(nydot[[axis_plus,axis_minus]]))<3e-14,"AXIAL_DIRECTION_DRIFT")
def integrate(order):
    xi,wi=leggauss(order)
    depth=np.zeros((26,401));even=np.zeros(401);odd=np.zeros(401)
    for k,(a,b) in enumerate(zip(times[:-1],times[1:])):
        u=a+(b-a)*(xi+1)/2
        x=physical(u)
        W=x["nuNormal"];ray_ny=NY(u)
        factor=1-x["v"][None,:]*ray_ny
        check(np.min(factor)>0,"THOMSON_RELATIVE_FLUX_NOT_POSITIVE")
        integrand=W[None,:]*factor
        depth[:,k+1]=depth[:,k]+(b-a)/2*(integrand@wi)
        even[k+1]=even[k]+(b-a)/2*np.dot(wi,W)
        odd[k+1]=odd[k]+(b-a)/2*np.dot(wi,W*x["v"])
    return depth,even,odd
depth,even,odd=integrate(8)
depth16,even16,odd16=integrate(16)
gauss_gap=float(max(abs(depth-depth16).flat))
check(gauss_gap<5e-8,"QUADRATURE_REFINEMENT_NOT_CONVERGED")
check(np.min(np.diff(depth,axis=1))>=0,"UNPHYSICAL_NEGATIVE_OPTICAL_DEPTH_INCREMENT")
axis_gap=float(max(np.max(abs(depth[axis_plus]-(even-odd))),
                  np.max(abs(depth[axis_minus]-(even+odd)))))
check(axis_gap<1e-10,"AXIAL_ODD_EVEN_IDENTITIES_FAIL")
asym=float((depth[axis_minus,-1]-depth[axis_plus,-1])/(depth[axis_minus,-1]+depth[axis_plus,-1]))
weighted=float(odd[-1]/even[-1])
check(abs(asym-weighted)<3e-13,"WEIGHTED_TILT_DISCREPANCY")

# Compare to exact parent Saha (hydrogen only, distinct helium normalization).
prior_summary=json.loads((ROOT/parent_paths[1]).read_text())
prior_plus=prior_summary["Thomson_depth_plus_ey"]
prior_minus=prior_summary["Thomson_depth_minus_ey"]
old_nH0=(old("n_H_normal_cm_minus3")[0]) / gamma_init/(1+z0)**3
nH_scale=nH0_HyRec/old_nH0
old_saha_xe=old("x_e_H_only_source_Saha")
xe_relative=np.max(abs(phy["xe"]/old_saha_xe-1))
source_HyRec_nH0_factor=nH_scale

# Independent ODE for three rays and axes in same fixed conditional model.
radau={}
for j in sorted(set([0,7,axis_plus,axis_minus])):
    def f(t,y):
        ph=physical(float(t))
        return [float(ph["nuNormal"])*(1-float(ph["v"])*float(NY(float(t))[j]))]
    sol=solve_ivp(f,(0,.2),[0.],t_eval=times,method="Radau",
          rtol=3e-11,atol=3e-12,max_step=.004)
    check(sol.success,"INDEPENDENT_RADAU_ODE_FAILED")
    e=float(np.max(abs(sol.y[0]-depth[j])))
    check(e<5e-8,"RADAU_VS_GAUSS_DISAGREEMENT")
    radau[str(j)]={"max_abs_gap":e,"rhs_evaluations":int(sol.nfev)}

# Endpoint tests for source xe/Tm, no extrapolation outside FLRW native grid.
for z,s in [(1700.,hyrec_report["x_e_at_1700"]),(1392.,hyrec_report["x_e_at_1392"])]:
    check(abs(float(pchip(np.log1p(z)))-s)<4e-12,"HYREC_INTERPOLANT_NODE_FIDELITY")

# CSVs, fully source-conditioned.
with (HERE/"TYPEII_HYREC2_ELECTRON_401.csv").open("w",newline="") as f:
    wr=csv.writer(f,lineterminator="\n")
    wr.writerow(["tau_H","z_mean_not_observed","source_HyRec2_xe_HHe","source_HyRec2_Tm_K",
                 "n_H_normal_cm_minus3","n_H_rest_cm_minus3","n_e_rest_cm_minus3",
                 "TypeII_H_s_inv","tilt_v2","electron_Gamma","Thomson_scalar_prefactor_per_tau",
                 "axis_depth_even","axis_depth_odd"])
    for k,t in enumerate(times):
        wr.writerow([format(float(y),".17g") for y in
             [t,phy["z"][k],phy["xe"][k],phy["Tm"][k],phy["nHnormal"][k],phy["nHrest"][k],
              phy["neRest"][k],phy["H"][k],v2[k],phy["gamma"][k],phy["nuNormal"][k],
              even[k],odd[k]]])
with (HERE/"TYPEII_HYREC2_26RAY_DEPTH_401.csv").open("w",newline="") as f:
    wr=csv.writer(f,lineterminator="\n")
    wr.writerow(["ray_id","tau_H","n_y_normal","relative_flux_q_one_factor",
                 "hazard_per_tau_H","cumulative_Thomson_depth"])
    for j in range(26):
        for k,t in enumerate(times):
            flux=1-v2[k]*ny[j,k]
            wr.writerow([j]+[format(float(y),".17g") for y in
                 [t,ny[j,k],flux,phy["nuNormal"][k]*flux,depth[j,k]]])
output={
 "schema":"bass.typeii.original_HyRec2_FLRW_HHe_source_reweighted_401x26.v1",
 "source_HyRec2_output_SHA256":hsh(native_path),
 "source_HyRec2_input_SHA256":hyrec_report["calibrated_input_sha256"],
 "parent_typeii_sha":PARENT_SHA,
 "parent_401x26_ray_sha256":REFERENCE_RAY_SHA,
 "physical_inference":"conditional FLRW H/He recombination history on fixed original Type II source and conserved hydrogen current; not native Bianchi recombination",
 "tau_domain":[float(times[0]),float(times[-1])],
 "mean_z0":z0,"mean_z_final":float(phy["z"][-1]),
 "source_HyRec_nH0_cm3":nH0_HyRec,
 "nH_source_ratio_to_previous_Saha":source_HyRec_nH0_factor,
 "electron_xe_initial":float(phy["xe"][0]),
 "electron_xe_final":float(phy["xe"][-1]),
 "electron_n_rest_initial_cm_minus3":float(phy["neRest"][0]),
 "electron_n_rest_final_cm_minus3":float(phy["neRest"][-1]),
 "HyRec_matter_T_initial_K":float(phy["Tm"][0]),
 "HyRec_matter_T_final_K":float(phy["Tm"][-1]),
 "prior_Saha_xe_initial":float(old_saha_xe[0]),
 "prior_Saha_xe_final":float(old_saha_xe[-1]),
 "max_relative_HyRec_vs_old_Saha_ionization_fraction":float(xe_relative),
 "BASS_H0_anchor_s_inv":float(phy["H"][0]),
 "BASS_Hfinal_s_inv":float(phy["H"][-1]),
 "Thomson_depth_plus_ey":float(depth[axis_plus,-1]),
 "Thomson_depth_minus_ey":float(depth[axis_minus,-1]),
 "Thomson_depth_26_min":float(np.min(depth[:,-1])),
 "Thomson_depth_26_max":float(np.max(depth[:,-1])),
 "Thomson_depth_odd_integral":float(odd[-1]),
 "Thomson_depth_even_integral":float(even[-1]),
 "Thomson_depth_asymmetry":asym,
 "Thomson_depth_gamma_weighted_tilt":weighted,
 "prior_Saha_depth_plus_ey":float(prior_plus),
 "prior_Saha_depth_minus_ey":float(prior_minus),
 "difference_from_previous_Saha_plus_ey":float(depth[axis_plus,-1]-prior_plus),
 "difference_from_previous_Saha_minus_ey":float(depth[axis_minus,-1]-prior_minus),
 "8_vs_16_point_Gauss_max_absolute_gap":gauss_gap,
 "axial_odd_even_identity_max_absolute_gap":axis_gap,
 "independent_4_ray_Radau":radau,
 "original_HyRec_recombination_C_code_executed":True,
 "native_typeii_recombination_C_code_executed":False,
 "full_photon_Thomson_gain_or_pol_executed":False,
 "production_RustCore_dispach_modified":False,
 "claim":"IMPLEMENTATION_VERIFIED_ORIGINAL_HYREC2_FLRW_INPUT_CONDITIONALLY_COUPLED_TYPEII_RAYS"
}
(HERE/"HYREC2_TYPEII_THOMSON_RESULTS.json").write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
print(json.dumps(output,indent=2,sort_keys=True))
