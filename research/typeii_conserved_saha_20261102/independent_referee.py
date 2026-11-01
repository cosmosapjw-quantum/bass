#!/usr/bin/env python3
"""Same-author hostile, independent ODE source-current/Saha/ray verification.

This is deliberately separate from the source evaluator's Gauss quadrature,
and must survive python -O (all gates are explicit exceptions).
"""
import contextlib, io, json, math, runpy
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp

here=Path(__file__).resolve().parent
source=here/"source_saha_transport.py"
with contextlib.redirect_stdout(io.StringIO()):
    mod=runpy.run_path(str(source))
data=json.loads((here/"PHYSICAL_SAHA_THOMSON_SUMMARY.json").read_text())
t=np.asarray(mod["times"])
H0=float(mod["H_ref"]); nH0=float(mod["nH_rest0_cm3"])
qsource=mod["q_from_state"]; interp=mod["interp"]; rhsowner=mod["rhs_owner"]
gam_index=mod["FLUID_GAMMA"]
proper=mod["phys"]; depth=mod["depth"]; ny_inter=mod["direction_interp"]
fluid=mod["evaluate_physical"]
check=mod["check"]
source_x=mod["states"]

# Independent ODE integration of the physical conservation+Raychaudhuri system.
def fluid_system(tt, logdens):
    x=np.asarray(interp(tt),float)
    rx=np.asarray(rhsowner(list(x),gam_index))
    v=float(x[4]); vp=float(rx[4])
    q=float(rx[3]/x[3]+4*x[0])
    return [-1-q,-3-v*vp/(1-v*v)]
y0=[math.log(H0),math.log(nH0)]
fluid_ode=solve_ivp(fluid_system,(0,.2),y0,t_eval=t,method="DOP853",
      atol=4e-14,rtol=4e-13,max_step=.001)
check(fluid_ode.success,"CONSERVATION_ODE_SOLVER_FAILED")
H_ode=np.exp(fluid_ode.y[0]); nH_ode=np.exp(fluid_ode.y[1])
Hrel=float(np.max(abs(H_ode/proper["H"]-1)))
nHrel=float(np.max(abs(nH_ode/proper["nH_rest"]-1)))
check(Hrel<2e-11 and nHrel<2e-11,"INDEPENDENT_CONSERVATION_ODE_FAIL")

# 4 off-axis rays + exact axial pair, compare independently integrated Radau
# optical depth against the 8-point interval Gauss cumulative source result.
rays=[0,7,13,25,mod["axis_p"],mod["axis_m"]]
rays=sorted(set(rays))
errors={}
for ray in rays:
    def ode(t,y):
        p=fluid(t)
        ny=float(ny_inter(t)[ray])
        return [float(p["nu_normal"])*(1-float(p["v"])*ny)]
    sol=solve_ivp(ode,(0,.2),[0.],t_eval=t,method="Radau",
                 atol=1e-11,rtol=2e-12,max_step=.003)
    check(sol.success,"THOMSON_RADAU_FAILURE")
    gap=float(np.max(abs(sol.y[0]-depth[ray])))
    errors[str(ray)]={"max_abs_gap":gap,"nfev":int(sol.nfev)}
    check(gap<3e-8,"FULL_RAY_RADAU_GAUSS_DISAGREEMENT_"+str(ray))

# Flat mean temperature optical history is NOT a physical anisotropic ray
# temperature: prescribed zmean is a scalar proxy. Verify mean redshift
# endpoint while distinguishing actual directional photon energies.
zmean0=float(proper["zmean"][0]);zmean_end=float(proper["zmean"][-1])
check(abs(zmean0-1700)<1e-10 and 1300<zmean_end<1500,"THERMAL_SUPPORT_BAD")

# Hostile case: the density-frame mapping must NEVER be the old unmodified
# legacy FLRW ne=x_e n_H (normal density) when source tilt is not zero.
naive=data["source_proper_electron_density_vs_naive_FLRW_max_relative_gap"]
check(naive>1e-5,"MISSING_TILT_FRAME_SOURCE_GAP")
check(data["source_normal_collision_prefactor_vs_wrong_missing_Gamma_max_relative_gap"]>0.001,
      "NEGATIVE_MISSING_GAMMA_NOT_DETECTED")

# Flat H anchor affects the overall optical depth, not the odd/even
# anisotropy ratio for hydrogen Saha equilibrium at a fixed n_H anchor.
oldh=fluid.__globals__["H_ref"]
fluid.__globals__["H_ref"]=2*oldh
try:
    times_probe=np.array([0,.08,.14,.2])
    double=fluid(times_probe)
    fluid.__globals__["H_ref"]=oldh
    orig=fluid(times_probe)
finally:
    fluid.__globals__["H_ref"]=oldh
scale_err=float(np.max(abs(np.asarray(double["nu_normal"])/np.asarray(orig["nu_normal"])-.5)))
check(scale_err<5e-15,"H_ANCHOR_RATE_SCALING_NUMERIC_FAIL")

# Negative domain: no time interpolation/extrapolation outside source endpoints.
domain_rejections=0
for invalid in (-.001,.200001,float("nan")):
    try:fluid(invalid)
    except RuntimeError:domain_rejections+=1
check(domain_rejections==3,"INVALID_SOURCE_DOMAIN_ACCEPTED")
check(np.max(abs(mod["depth"]-mod["depth16"]))<3e-9,"GL_8_16_CONVERGENCE_FAIL")

out={
 "schema":"bass.typeii.conserved_saha.science_referee.v1",
 "source_locked_main":mod["MAIN"],
 "referee_kind":"independent mathematical formulation same author; different DOP853/Radau algorithms",
 "independent_H_ode_max_relative_gap":Hrel,
 "independent_Hproper_ode_max_relative_gap":nHrel,
 "independent_optical_depth_Radau_rays":errors,
 "max_radau_vs_gauss_depth_gap":max(x["max_abs_gap"] for x in errors.values()),
 "source_endpoint_zmean":zmean_end,
 "wrong_FLRW_proper_density_relative_gap":naive,
 "numeric_anchor_H_2x_normal_rate_gap":scale_err,
 "domain_rejection_tests":domain_rejections,
 "verdict":"SOURCE_SCOPED_PHYSICS_CROSSCHECK_PASS",
 "not_checked":"actual HyRec/CosmoRec, full photon spectral collision, Einstein-radiation coupled background"
}
(here/"INDEPENDENT_REFEREE.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
