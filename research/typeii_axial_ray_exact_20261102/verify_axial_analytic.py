#!/usr/bin/env python3
"""Exact Hermite-integrated axial Type II null-rays vs published BASS source-run.
The comparison uses independent analytic invariance of n = +/-e_y and
independent quadrature of the electron-rest opacity, not the source ODE RHS.
No production callbacks, electron-history inference, backreaction, or CMB claims.
"""
from __future__ import annotations
import csv, hashlib, json, subprocess
from pathlib import Path

import numpy as np
from scipy.integrate import quad
from scipy.interpolate import CubicHermiteSpline
from numpy.polynomial.legendre import leggauss

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
MAIN="9c6506e4e2087129a8b674ff10438e5db1a55c9d"
PARENT="a3bf54708db1388227b34a313ff3c8e6c250d7f5"
EXPECTED_CSV_SHA="9f1400588d39ba3a61020542e14b0e372c8e9be1af130f8c64ed8829b23ad217"
def git(*a):return subprocess.check_output(["git","-C",str(ROOT),*a],text=True).strip()

ssot=json.loads((ROOT/"research/typeii_host_preflight_20261101/SOURCE_LOCK.json").read_text())
originals=ssot["original_git_blobs_sha1"]
for rel,expected in originals.items():
    actual=git("hash-object",rel)
    if actual!=expected:raise RuntimeError(f"IMMUTABLE_SOURCE_MISMATCH {rel}")
csv_path=ROOT/"research/typeii_liouville_optdepth_20261101/PHOTON_RAYS_401X26.csv"
sha=hashlib.sha256(csv_path.read_bytes()).hexdigest()
if sha!=EXPECTED_CSV_SHA:raise RuntimeError(f"PARENT_RAY_DATA_DRIFT {sha}")
for rel in ["runtime/rust/typeii/typeii_polarized_liouville.rs","bianchi/q/electron_rate.py"]:
    if git("hash-object",rel)!=git("rev-parse",MAIN+":"+rel):
        raise RuntimeError(f"PHYSICS_SOURCE_DRIFT {rel}")
fixture=json.loads((ROOT/"compiler/validation/typeii_fixture_canonical.json").read_text())
samples=fixture["trajectory"]["samples"]
if len(samples)!=401 or fixture["trajectory"]["contract"]["gamma"]!=1.3:
    raise RuntimeError("FIXTURE_CONTRACT_MISMATCH")
times=np.array([s["tau"] for s in samples],float)
x=np.array([s["state"] for s in samples],float)
xp=np.array([s["rhs"] for s in samples],float)
if not (max(abs(np.diff(times) - 0.0005)) < 1e-13): raise AssertionError('PHYSICS_GATE_AT_verify_axial_analytic.py_LINE_41')
if not (x.shape == xp.shape == (401, 5)): raise AssertionError('PHYSICS_GATE_AT_verify_axial_analytic.py_LINE_42')

spline=CubicHermiteSpline(times,x,xp,axis=0)
dt=np.diff(times)
S=np.sqrt(3.0)
energy_growth=1+x[:,0]+S*x[:,1]
energy_growth_prime=xp[:,0]+S*xp[:,1]
# Exact integral of the piecewise cubic Hermite interpolant on each segment.
increments=dt*(energy_growth[:-1]+energy_growth[1:])/2 + dt**2*(energy_growth_prime[:-1]-energy_growth_prime[1:])/12
lnE=np.r_[0.,-np.cumsum(increments)]
lnI=4*lnE
# Independent 8-point positive Gauss-Legendre quadrature for each nonlinear Gamma(v).
abscissae,weights=leggauss(8)
gam_segments=[]; gamv_segments=[]
for t0,t1 in zip(times[:-1],times[1:]):
    quadrature_t=t0+(t1-t0)*(abscissae+1)*0.5
    v=np.asarray(spline(quadrature_t))[:,4]
    if not np.all(np.isfinite(v)) or np.any(abs(v)>=1):raise RuntimeError("NONPHYSICAL_TILT")
    gamma=1/np.sqrt(1-v*v)
    factor=(t1-t0)*0.5
    gam_segments.append(float(factor*np.dot(weights,gamma)))
    gamv_segments.append(float(factor*np.dot(weights,gamma*v)))
tg=np.r_[0.,np.cumsum(gam_segments)]
tv=np.r_[0.,np.cumsum(gamv_segments)]
tau_plus=tg-tv  # n=+ey, q=1-v
tau_minus=tg+tv # n=-ey, q=1+v
weighted_mean_v=float(tv[-1]/tg[-1])
weighted_mean_v_from_depth=float((tau_minus[-1]-tau_plus[-1])/(tau_minus[-1]+tau_plus[-1]))
if not (abs(weighted_mean_v - weighted_mean_v_from_depth) < 1e-14): raise AssertionError('PHYSICS_GATE_AT_verify_axial_analytic.py_LINE_70')

# Completely different numerical integral of the same physical rates, endpoint only.
def gammav(t):
    v=float(spline(t)[4])
    return 1/np.sqrt(1-v*v),v
radau_like_quad=[]
for sgn in (+1.,-1.):
    qresult=quad(lambda z: gammav(z)[0]*(1-sgn*gammav(z)[1]),times[0],times[-1],epsabs=3e-14,epsrel=3e-13,limit=500)[0]
    radau_like_quad.append(qresult)
if not (abs(radau_like_quad[0] - tau_plus[-1]) < 4e-12): raise AssertionError('PHYSICS_GATE_AT_verify_axial_analytic.py_LINE_80')
if not (abs(radau_like_quad[1] - tau_minus[-1]) < 4e-12): raise AssertionError('PHYSICS_GATE_AT_verify_axial_analytic.py_LINE_81')

with csv_path.open(newline="") as f:
    records=list(csv.DictReader(f))
if not (len(records) == 401 * 26): raise AssertionError('PHYSICS_GATE_AT_verify_axial_analytic.py_LINE_85')
by_id={}
for row in records:by_id.setdefault(int(row["ray_id"]),[]).append(row)
if not (len(by_id) == 26): raise AssertionError('PHYSICS_GATE_AT_verify_axial_analytic.py_LINE_88')
axial={}
for j,group in by_id.items():
    if len(group)!=401:raise RuntimeError("INCOMPLETE_RAY")
    first=np.array([float(group[0][z]) for z in ("n_x","n_y","n_z")])
    if np.max(abs(first-np.array([0.,1.,0.])))<1e-14:
        axial["+"]=j
    if np.max(abs(first-np.array([0.,-1.,0.])))<1e-14:
        axial["-"]=j
if not (set(axial) == {'+', '-'}): raise AssertionError(f'AXIS_RAYS_NOT_FOUND {axial}')

def compare(sign,expected_tau):
    j=axial[sign]; rows=by_id[j]
    values=lambda key:np.array([float(row[key]) for row in rows])
    actual_t=values("tau_H")
    if not (np.max(abs(actual_t - times)) < 2e-15): raise AssertionError('PHYSICS_GATE_AT_verify_axial_analytic.py_LINE_103')
    ny=1. if sign=="+" else -1.
    const_dir_error=max(float(max(abs(values("n_x")))),float(max(abs(values("n_z")))),float(max(abs(values("n_y")-ny))))
    doppler=(1-ny*x[:,4])/np.sqrt(1-x[:,4]**2)
    expected_logEe=lnE+np.log(doppler)
    errors={
        "direction_invariance":const_dir_error,
        "normal_log_energy":float(max(abs(values("ln_E_normal")-lnE))),
        "normal_log_bolometric":float(max(abs(values("ln_I_normal")-lnI))),
        "electron_rest_log_energy":float(max(abs(values("ln_E_electron")-expected_logEe))),
        "unit_proper_optical_depth":float(max(abs(values("optical_depth_unit_proper_rate")-expected_tau))),
    }
    if max(errors.values())>2e-11:raise ArithmeticError(f"AXIAL_ORACLE_FAIL {sign}: {errors}")
    return {"ray_id":j,"max_abs_errors":errors, "tau_endpoint":float(expected_tau[-1]),"E_normal_endpoint":float(np.exp(lnE[-1])),"E_electron_endpoint":float(np.exp(expected_logEe[-1]))}
plus=compare("+",tau_plus)
minus=compare("-",tau_minus)

# The original Type II gamma-law state stays v>0 on this interval.
if not (np.min(x[:, 4]) > 0 and tau_minus[-1] > tau_plus[-1] > 0): raise AssertionError('PHYSICS_GATE_AT_verify_axial_analytic.py_LINE_121')
# Negative controls: forgetting Gamma, and double-counting q, are measurably different.
wrong_plus_q_only=float(np.trapz(1-x[:,4],times)) if hasattr(np,"trapz") else float(np.trapezoid(1-x[:,4],times))
missing_gamma_gap=float(abs(tau_plus[-1]-wrong_plus_q_only))
# Independent 8-point Gauss integration of Gamma*(1-v)^2.
wrong_extra_q=0.
for t0,t1 in zip(times[:-1],times[1:]):
    qt=t0+(t1-t0)*0.5*(abscissae+1)
    v=spline(qt)[:,4];gamma=1/np.sqrt(1-v*v)
    wrong_extra_q+=(t1-t0)*0.5*float(np.dot(weights,gamma*(1-v)**2))
double_q_gap=float(abs(tau_plus[-1]-wrong_extra_q))
if not (missing_gamma_gap > 0.0001 and double_q_gap > 0.001): raise AssertionError('PHYSICS_GATE_AT_verify_axial_analytic.py_LINE_132')

out={
 "schema":"bass.typeii.analytic_axial_null_ray_and_thomson_asymmetry.v1",
 "original_main":MAIN,"parent_commit":PARENT,
 "source_blob_locks":len(originals),"parent_csv_sha256":sha,
 "time_domain_tau_H":[float(times[0]),float(times[-1])],"state_count":401,
 "analytic_method":"exact integration of source cubic Hermite Sigma22; 8-point Gauss-Legendre for nonlinear Gamma(v), cross-checked by adaptive quad",
 "positive_axis":plus, "negative_axis":minus,
 "integral_Gamma_dtau":float(tg[-1]),
 "integral_Gamma_v_dtau":float(tv[-1]),
 "weighted_mean_tilt":weighted_mean_v,
 "optical_depth_asymmetry_ratio":weighted_mean_v_from_depth,
 "depth_difference":float(tau_minus[-1]-tau_plus[-1]),
 "depth_sum":float(tau_minus[-1]+tau_plus[-1]),
 "energy_identical_between_axes":True,
 "independent_adaptive_quad_gap":float(max(abs(radau_like_quad[0]-tau_plus[-1]),abs(radau_like_quad[1]-tau_minus[-1]))),
 "negative_control_q_only_gap":missing_gamma_gap,
 "negative_control_double_q_gap":double_q_gap,
 "claim_status":"DERIVED_EXACT_AXIAL_IDENTITY_NUMERICALLY_CHECKED_SOURCE_CONDITIONAL",
 "limitations":"unit electron-rest opacity per Hubble time, prescribed TypeII background; no ionization history, no spectral/polarized Boltzmann feedback, no CMB",
}
(OUT/"AXIAL_ORACLE_RESULT.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
with (OUT/"AXIAL_ORACLE_401.csv").open("w",newline="") as f:
    wr=csv.writer(f,lineterminator="\n")
    wr.writerow(["tau_H","lnE_normal_exact","lnI_normal_exact","tau_unit_plus","tau_unit_minus","int_Gamma","int_Gamma_v","weighted_tilt"])
    for k,t in enumerate(times):
        wr.writerow([format(float(t),".17g"),format(float(lnE[k]),".17g"),format(float(lnI[k]),".17g"),
         format(float(tau_plus[k]),".17g"),format(float(tau_minus[k]),".17g"),
         format(float(tg[k]),".17g"),format(float(tv[k]),".17g"),
         format(float(tv[k]/tg[k]) if k else 0.,".17g")])
print(json.dumps(out,indent=2,sort_keys=True))
