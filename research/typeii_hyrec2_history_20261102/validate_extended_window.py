#!/usr/bin/env python3
"""Independent correctness tests for the new Type-II-native geometry to zmean=300."""
import contextlib,io,json,math,runpy
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import CubicHermiteSpline
from scipy.optimize import minimize_scalar

HERE=Path(__file__).resolve().parent
with contextlib.redirect_stdout(io.StringIO()):
    m=runpy.run_path(str(HERE/"typeii_extended_window.py"))
def check(test,reason):
    if not bool(test):raise RuntimeError(reason)
time=m["time"]; depth=m["depth"];future=m["future"]; gammafluid=1.3
sol=m["sol"];X=m["X"];rayfield=m["nn"]
sp,sm,s13,n1,v=(X[:,i] for i in range(5))
omega=1-np.sum(X[:,[0,1,2]]**2,axis=1)-n1*n1/12
gp=1+(gammafluid-1)*v*v
codazzi=-math.sqrt(3)*n1*s13-3*gammafluid*omega*v/gp
codazzi_error=float(np.max(abs(codazzi)))
check(codazzi_error<6e-13,"EXTENDED_SOURCE_CODAZZI_VIOLATION")
check(np.min(omega)>0 and np.min(n1)>0 and np.max(abs(v))<1,
      "TYPEII_PHYSICAL_CHART_NOT_CLOSED")
# Direct numerical independent Radau integration of physical optical depths,
# on exact source dense-output geometry, not source Gauss quadrature.
checks={}
for j in sorted(set([0,7,m["axp"],m["axm"],25])):
    def f(t,y):
        W,q,*_=m["geometry"](t)
        return [float(W*q[j])]
    res=solve_ivp(f,(0,float(time[-1])),[0.],t_eval=time,
                  method="Radau",atol=3e-10,rtol=2e-11,max_step=.006)
    check(res.success,"RADUA_SOURCE_OPACITY_SOLVER_FAILED")
    gap=float(np.max(abs(res.y[0]-depth[j])))
    check(gap<2e-7,"SOURCE_GAUSS_VS_INDEPENDENT_RADAU_DISAGREE")
    checks[str(j)]={"maximum_depth_abs_gap":gap,"rhs_evaluations":int(res.nfev)}
max_radau=max(v["maximum_depth_abs_gap"] for v in checks.values())

# Evaluate the same original Type-II geodesics and HYREC source on a distinct
# smaller timestep quadrature grid, not simply increasing Gauss order.
previous=m["attenuation"]
g=previous.__globals__
origtime=g["time"]
refined=np.unique(np.r_[time,np.arange(0,float(time[-1]),.001)])
try:
    g["time"]=refined
    refined_depth,refined_even,refined_odd=previous(8)
finally:g["time"]=origtime
refine_end_gap=float(np.max(abs(refined_depth[:,-1]-depth[:,-1])))
check(refine_end_gap<3e-8,"GLOBAL_TIME_STEP_REFINEMENT_FAIL")
refine_axis=float(abs((refined_depth[m["axm"],-1]-refined_depth[m["axp"],-1])/
                      (refined_depth[m["axm"],-1]+refined_depth[m["axp"],-1])-
                    (depth[m["axm"],-1]-depth[m["axp"],-1])/(depth[m["axm"],-1]+depth[m["axp"],-1])))
check(refine_axis<2e-10,"OPACITY_ASYMMETRY_REFINEMENT_FAIL")

# Continuous conditional finite-window last-event peak vs discretized peak.
Wt,qt,*_=m["geometry"](time)
hazard=Wt[None,:]*qt
depth_continuous=CubicHermiteSpline(time,depth,hazard,axis=1)
peak_list=[]
raw_peaks=m["peaks"]
for ray in range(26):
    def first_source(t):
        W,q,*_=m["geometry"](t)
        tt=float(depth_continuous(t)[ray])
        return float(W*q[ray]*np.exp(-depth[ray,-1]+tt))
    optimum=minimize_scalar(lambda t:-first_source(t),
                bounds=(.25,.85),method="bounded",
                options={"xatol":3e-11,"maxiter":140})
    check(optimum.success,"LAST_EVENT_CONTINUOUS_PEAK_OPTIMIZATION_FAIL")
    outz=1701*np.exp(-optimum.x)-1
    peak_list.append(outz)
peak_z=np.array(peak_list)
peak_sampling_gap=float(np.max(abs(peak_z-raw_peaks)))
check(peak_sampling_gap<4.5,"DISCRETE_CONDITIONAL_LAST_EVENT_PEAK_NOT_CONVERGED")
# Abelian check: for actual axis rates, odd/even optical depth identities
# remain exact on continuous trajectories with independently sampled q.
ax_p,ax_m=m["axp"],m["axm"]
exact_axiserr=float(max(np.max(abs(depth[ax_p]-(m["even"]-m["odd"]))),
                        np.max(abs(depth[ax_m]-(m["even"]+m["odd"])))))
check(exact_axiserr<2e-11,"ODD_EVEN_AXIS_THEOREM_FAIL")
report={
 "schema":"bass.typeii.original_HyRec2_HHe_extended_geodesic_adversarial_validation.v1",
 "time_steps":len(time),"refined_time_steps":len(refined),
 "max_Codazzi_constraint_abs_residual":codazzi_error,
 "independent_Radau_5_photon_rays":checks,
 "max_Radau_vs_Gauss_abs_gap":max_radau,
 "max_refined_timestep_endpoint_depth_abs_gap":refine_end_gap,
 "refined_timestep_axis_asymmetry_abs_gap":refine_axis,
 "continuous_peak_mean_z_min":float(np.min(peak_z)),
 "continuous_peak_mean_z_max":float(np.max(peak_z)),
 "continuous_peak_plus_axis":float(peak_z[ax_p]),
 "continuous_peak_minus_axis":float(peak_z[ax_m]),
 "discrete_vs_continuous_peak_mean_z_max_abs_gap":peak_sampling_gap,
 "original_extended_axis_odd_even_max_abs_gap":exact_axiserr,
 "conclusion":"SOURCE_TYPEII_GAUSS_CODAZZI_AND_GENUINE_NATIVE_HYREC_WEIGHTING_NUMERICALLY_CHECKED",
 "caveat":"g_last along fixed-source photon ray to finite observer zmean=300; not coupled gain or today CMB visibility"
}
(HERE/"EXTENDED_WINDOW_VALIDATION.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
print(json.dumps(report,indent=2,sort_keys=True))
