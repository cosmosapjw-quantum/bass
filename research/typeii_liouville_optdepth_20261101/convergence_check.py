#!/usr/bin/env python3
"""C8 source-conditioned Type II 401-state physical ray RK4 convergence against DOP853/Radau."""
import contextlib
import io
import json
import runpy
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp

HERE=Path(__file__).resolve().parent
with contextlib.redirect_stdout(io.StringIO()):
    globals_original=runpy.run_path(str(HERE/"physical_rays.py"))
system=globals_original["system"]
initial=globals_original["initial"]
directions=globals_original["directions"]
tau=globals_original["tau"]
check_ids=(0,7,13,25)
endpoints={}
def rk4(y0,nsteps):
    h=float(tau[-1]-tau[0])/nsteps
    t=float(tau[0])
    y=y0.copy()
    for k in range(nsteps):
        z1=system(t,y)
        z2=system(t+.5*h,y+.5*h*z1)
        z3=system(t+.5*h,y+.5*h*z2)
        z4=system(t+h,y+h*z3)
        y=y+(h/6.)*(z1+2*z2+2*z3+z4)
        t=float(tau[0])+(k+1)*h
    return y
for k in check_ids:
    y0=initial(directions[k])
    D=solve_ivp(system,(float(tau[0]),float(tau[-1])),y0,method="DOP853",
                rtol=7e-13,atol=2e-14,max_step=.0025)
    R=solve_ivp(system,(float(tau[0]),float(tau[-1])),y0,method="Radau",
                rtol=2e-11,atol=2e-13,max_step=.005)
    if not D.success or not R.success:raise RuntimeError("COMPARISON_INTEGRATOR_FAILURE")
    endpoints[k]={"d":D.y[:,-1],"r":R.y[:,-1],"d_calls":D.nfev,"r_calls":R.nfev}
ns=(4,8,16,32,64,128)
errors={}
for n in ns:
    e=0.0
    for idx in check_ids:
        y0=initial(directions[idx])
        y=rk4(y0,n)
        e=max(e,float(np.max(abs(y-endpoints[idx]["d"]))))
    errors[n]=e
r4order=[float(np.log2(errors[ns[i]]/errors[ns[i+1]]))
         for i in range(len(ns)-1) if errors[ns[i+1]]>0]
radau_max=max(float(np.max(abs(endpoints[i]["r"]-endpoints[i]["d"]))) for i in check_ids)
if not all(np.isfinite(x) for x in list(errors.values())+[radau_max]):
    raise ArithmeticError("NONFINITE_CONVERGENCE")
if not (errors[8]<errors[4] and errors[16]<errors[8] and errors[32]<errors[16]):
    raise ArithmeticError(f"EARLY_RK4_NONCONVERGENCE {errors}")
if not (errors[128]<5e-9 and radau_max<3e-9):
    raise ArithmeticError(f"REFERENCE_PRECISION_MISMATCH {errors} Radau={radau_max}")
if not (min(r4order[:3])>3.3):
    raise ArithmeticError(f"RK4_OBSERVED_ORDER_NOT_FOUR {r4order}")
out={
 "schema":"bass.typeii.source_liouville.r8.convergence.v1",
 "exact_original_sources":"physical_rays.py imports original-locked Type II geometry, electron D, Rust source, parent",
 "reference_DOP853":"rtol=7e-13 atol=2e-14 max_step=.0025",
 "independent_Radau":"rtol=2e-11 atol=2e-13 max_step=.005",
 "source_rays":list(check_ids),
 "evolution_tau_H":[float(tau[0]),float(tau[-1])],
 "RK4_steps":list(ns),
 "RK4_max_endpoint_abs_errors":[errors[n] for n in ns],
 "RK4_observed_orders":r4order,
 "maximum_Radau_vs_DOP853_endpoint_abs_gap":radau_max,
 "DOP853_rhs_counts":[int(endpoints[i]["d_calls"]) for i in check_ids],
 "Radau_rhs_counts":[int(endpoints[i]["r_calls"]) for i in check_ids],
 "verdict":"SOURCE_CONDITIONAL_RAY_NUMERICAL_CONVERGENCE_PASS",
 "physical_limits":"no native electron density, no CMB and no radiation-fluid feedback",
}
(HERE/"C8_CONVERGENCE.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
