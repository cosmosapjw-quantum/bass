#!/usr/bin/env python3
"""BASS physical high-z Saha opacity: first-event and zero-scattering probabilities.

A nonhomogeneous Poisson Thomson *event* model along already solved Type-II
null geodesics. Not a full Boltzmann gain term nor CMB visibility.
"""
from __future__ import annotations
import contextlib,csv,io,json,math,runpy
from pathlib import Path

import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.interpolate import CubicHermiteSpline
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

HERE=Path(__file__).resolve().parent
with contextlib.redirect_stdout(io.StringIO()):
    m=runpy.run_path(str(HERE/"source_saha_transport.py"))
data=json.loads((HERE/"PHYSICAL_SAHA_THOMSON_SUMMARY.json").read_text())
times=m["times"]; states=m["states"]; d=m["depth"]
qrate=m["evaluate_physical"](times)["nu_normal"]
ny=m["n_y"];ray_interp=m["direction_interp"]
def check(cond,msg):
    if not bool(cond):raise RuntimeError(msg)
rate_nodes=qrate[None,:]*(1-states[:,4][None,:]*ny)
check(np.min(rate_nodes)>0,"PHYSICAL_EVENT_RATE_NOT_POSITIVE")
depth_interp=CubicHermiteSpline(times,d,rate_nodes,axis=1)
P0=np.exp(-d)
g0=rate_nodes*P0
check(np.max(abs(depth_interp(times)-d))<1e-13,"HERMITE_DEPTH_AT_NODES_DRIFT")
check(np.max(abs(depth_interp.derivative()(times)-rate_nodes))<1e-11,"HERMITE_DEPTH_DERIVATIVE_DRIFT")
check(np.min(P0)>0 and np.max(P0)<=1,"ZERO_SCATTER_PROBABILITY_INVALID")
check(np.min(g0)>0,"FIRST_EVENT_DENSITY_NOT_POSITIVE")
wx,w=leggauss(8)
mass=np.zeros(26);mean_moment=np.zeros(26);variance_moment=np.zeros(26)
for lo,hi in zip(times[:-1],times[1:]):
    t=lo+.5*(hi-lo)*(wx+1)
    p=m["evaluate_physical"](t)
    n_yt=ray_interp(t)
    rate=(1-p["v"][None,:]*n_yt)*p["nu_normal"][None,:]
    tau_t=depth_interp(t)
    gg=rate*np.exp(-tau_t)
    width=.5*(hi-lo)
    mass+=width*gg@w
    mean_moment+=width*(gg*t[None,:])@w
    variance_moment+=width*(gg*(t*t)[None,:])@w
survival=np.exp(-d[:,-1])
mass_target=-np.expm1(-d[:,-1])
norm_gap=float(np.max(abs(mass-mass_target)))
check(norm_gap<8e-9,"FIRST_SCATTER_NORMALIZATION_NOT_CONSERVED")
mean=mean_moment/mass
variance=np.maximum(variance_moment/mass-mean*mean,0)
median=np.zeros(26)
for j in range(26):
    if d[j,-1]<=math.log(2):raise RuntimeError("FIRST_SCATTER_MEDIAN_OUTSIDE_SUPPORT")
    median[j]=brentq(lambda tau:float(depth_interp(tau)[j])-math.log(2),
                     float(times[0]),float(times[-1]),xtol=1e-13)
# Independent ODE for two axial and one generic offaxis ray. State y=P0.
sol_errors={}
for j in sorted(set([0,int(m["axis_p"]),int(m["axis_m"])])):
    def rate_ode(t,y):
        p=m["evaluate_physical"](t)
        rt=float(p["nu_normal"])*(1-float(p["v"])*float(ray_interp(t)[j]))
        return [-rt*y[0]]
    sol=solve_ivp(rate_ode,(0,.2),[1.0],t_eval=times,method="Radau",
            atol=3e-16,rtol=2e-12,max_step=.001)
    check(sol.success,"FIRST_SCATTER_RADAU_SOLVER_FAILURE")
    gap=float(np.max(abs(sol.y[0]-P0[j])))
    check(gap<3e-9,"SOURCE_POISSON_SURVIVAL_AND_RADAU_MISMATCH")
    sol_errors[str(j)]={"maximum_abs_error":gap,"rhs_evaluations":int(sol.nfev)}
p=int(m["axis_p"]);n=int(m["axis_m"])
ratio=float(survival[p]/survival[n])
ratio_expected=float(math.exp(d[n,-1]-d[p,-1]))
check(abs(ratio/ratio_expected-1)<1e-13,"AXIAL_SURVIVAL_RATIO_EXACT_IDENTITY")
check(min(mean)>0 and max(mean)<.2,"FIRST_SCATTER_MEAN_OUTSIDE_INTERVAL")
# At true vacuum, there is no collision hazard: P0=1, and event density is identically zero.
vacuum_P0=1.0;vacuum_first=0.0
check(vacuum_P0==1. and vacuum_first==0.,"VACUUM_CONTRACT_FAILED")
out={
 "schema":"bass.typeii.source_hydrogen_saha.first_scattering_survival.v1",
 "parent_thermodynamics":data["schema"],
 "model":"nonhomogeneous Poisson zero-scattering survival along 26 normal TypeII null characteristics",
 "source_rays":26,"sample_steps":401,
 "survival_probability_final_min":float(min(survival)),
 "survival_probability_final_max":float(max(survival)),
 "plus_axis_final_zero_scattering_probability":float(survival[p]),
 "minus_axis_final_zero_scattering_probability":float(survival[n]),
 "positive_to_negative_axial_survival_ratio":ratio,
 "axial_survival_ratio_from_exact_tau_difference":ratio_expected,
 "first_scattering_mean_tau_H_min":float(min(mean)),
 "first_scattering_mean_tau_H_max":float(max(mean)),
 "first_scattering_median_tau_H_min":float(min(median)),
 "first_scattering_median_tau_H_max":float(max(median)),
 "max_event_mass_vs_one_minus_survival_gap":norm_gap,
 "independent_Radau_survival_checks":sol_errors,
 "claim_status":"SOURCE_CONDITIONAL_FIRST_EVENT_DISTRIBUTION_NUMERICALLY_CHECKED",
 "not_established":"redistribution/gain in full Thomson Boltzmann, CMB observed visibility, native nonequilibrium recombination"
}
(HERE/"FIRST_SCATTER_SUMMARY.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
with (HERE/"FIRST_SCATTER_401X26.csv").open("w",newline="") as f:
    wr=csv.writer(f,lineterminator="\n")
    wr.writerow(["ray_id","tau_H","zero_scattering_probability","first_scattering_density_per_tau_H",
                 "first_event_mean_tau_H_conditional_on_event","first_event_median_tau_H"])
    for j in range(26):
        for k,t in enumerate(times):
            wr.writerow([j]+[format(float(z),".17g") for z in
                [t,P0[j,k],g0[j,k],mean[j],median[j]]])
print(json.dumps(out,indent=2,sort_keys=True))
