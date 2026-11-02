#!/usr/bin/env python3
"""Independent TypeII native HYREC H+proper nucleus photon-transport numerical gates.

Integrates a different method (Radau) and refined photon time steps, checks full
401x26 original BASS electron frame owner and source Codazzi constraint. No new
physical model introduced or acceptance widened after seeing discrepancies.
"""
import contextlib,io,json,runpy,math,sys
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
with contextlib.redirect_stdout(io.StringIO()):
    m=runpy.run_path(str(HERE/"transport_native_atomic_photons.py"))
def check(ok,msg):
    if not bool(ok):raise RuntimeError(msg)
times=np.asarray(m["times"],float)
depth=m["depth"][m["target"]]
sol=m["bg"]
source_bg=sol.sol(times).T
sp,sm,s13,N1,v=(source_bg[:,i] for i in range(5))
gamma_fluid=1.3
Omega=1-sp*sp-sm*sm-s13*s13-N1*N1/12
Gp=1+(gamma_fluid-1)*v*v
Codazzi=-math.sqrt(3)*N1*s13-3*gamma_fluid*Omega*v/Gp
constraint=float(max(abs(Codazzi)))
check(constraint<5e-13 and np.min(Omega)>0 and np.min(N1)>0 and np.max(abs(v))<1,
      "ORIGINAL_BASS_GRAVITY_CODAZZI_OR_DOMAIN_FAIL")
# Independent physical ODE (Radau) against source interval Gauss sums.
radau={}
for j in sorted(set([0,7,15,25,m["axis_plus"],m["axis_minus"]])):
    def rhs(t,y):
        z,vt,G,W,nrest=m["phys"](float(t))
        xe=float(m["curves"][m["target"]](np.log1p(z)))
        ny=float(m["NY"](float(t))[j])
        return [float(W*xe*(1-vt*ny))]
    r=solve_ivp(rhs,(0,float(times[-1])),[0.],t_eval=times,method="Radau",
                atol=3e-11,rtol=3e-11,max_step=.005)
    check(r.success,"INDEPENDENT_RADAU_ATOMIC_RAY_FAILED")
    gap=float(max(abs(r.y[0]-depth[j])))
    check(gap<1.2e-7,"NATIVE_ATOMIC_SOURCE_GAUSS_VS_RADAU_FAIL_"+str(j))
    radau[str(j)]={"max_abs_gap":gap,"nfev":r.nfev}
# Full n_Hrest Class-A conservation checked independently from published source.
x_e=m["curves"][m["target"]](np.log1p(1701*np.exp(-times)-1))
g=1/np.sqrt(1-v*v)
nH_rest=m["N_H0"]*np.exp(-3*times)/g
conserve=float(max(abs(nH_rest*g*np.exp(3*times)/m["N_H0"]-1)))
check(conserve<5e-15,"BASS_TYPEII_PROPER_N_H_CURRENT_NOT_CONSERVED")
# 1167 point Gaussian integration vs finer source photon quadrature grid.
oldtimes=m["integrate"].__globals__["times"]
oldN=m["integrate"].__globals__["N"]
refined=np.unique(np.r_[times,np.arange(0,float(times[-1]),.001)])
try:
    m["integrate"].__globals__["times"]=refined
    m["integrate"].__globals__["N"]=len(refined)
    refine,even,odd=m["integrate"](8)
finally:
    m["integrate"].__globals__["times"]=oldtimes
    m["integrate"].__globals__["N"]=oldN
refined_gap=float(np.max(abs(refine[m["target"]][:,-1]-depth[:,-1])))
check(refined_gap<1.5e-8,"BASS_ATOMIC_PHOTON_TIME_REFINEMENT_FAIL")
# BASS source original electron comoving owner parity for ALL 401x26 fixture
# directions, not just five selected target/source points.
sys.path.insert(0,str(ROOT))
from bianchi.q.electron import ColdElectronTestField,transform_photon
fixture=json.load((ROOT/"compiler/validation/typeii_fixture_canonical.json").open())["trajectory"]["samples"]
R=m["ray_x"][:,[int(np.argmin(abs(times-f["tau"]))) for f in fixture],:]
zmean=np.array([1701*np.exp(-f["tau"])-1 for f in fixture])
tinput=np.array([f["tau"] for f in fixture])
check(R.shape==(26,401,3),"ORIGINAL_TYPEII_401X26_RAY_MISSING")
maxD=maxRate=0.
for k,t in enumerate(tinput):
    zz,vv,GG,W,nrest=m["phys"](float(t))
    native_xe=float(m["curves"][m["target"]](np.log1p(zz)))
    field=ColdElectronTestField.comoving(float(nrest*native_xe*1e6),(0.,float(vv),0.))
    _,_,D=transform_photon(1.,R[:,k,:],np.zeros(3),np.array([0.,float(vv),0.]))
    Dphys=float(GG)*(1-vv*R[:,k,1])
    maxD=max(maxD,float(max(abs(D-Dphys))))
    H=float(m["np"].exp(m["logHs"](t)))
    from_source=field.n_e_free*6.6524587e-29*299792458*D/H
    from_rate=float(W*native_xe)*(1-vv*R[:,k,1])
    maxRate=max(maxRate,float(max(abs(from_source/from_rate-1))))
check(maxD<4e-15 and maxRate<5e-15,"OWNER_ELECTRON_SOURCE_N_H_Q_MISMATCH")
# Adversarial limitation: two native histories Honly and H+nH must not collapse
# accidentally to one identity, as source gamma current effect was actually applied.
model=m["depth"]
nH_effect=float(max(abs(model["TypeII_H_only"][:,-1]-model[m["target"]][:,-1])))
check(nH_effect>2e-4,"PROPER_NH_SOURCE_KINETICS_NOT_SEEN_IN_PHOTON_DATA")
result={
 "schema":"bass.typeii.native_HyRec2_TypeII_H_proper_Hn_independent_photon_validation.v1",
 "original_typeii_gamma13_Codazzi_max_abs_residual":constraint,
 "original_typeii_classA_hydrogen_number_conservation_max_relative_defect":conserve,
 "original_TypeII_401x26_owner_electron_D_max_abs_error":maxD,
 "original_TypeII_401x26_owner_electron_SI_CGS_rate_max_relative_error":maxRate,
 "independent_6_rays_Radau_vs_original_Gauss":radau,
 "max_independent_Radau_vs_source_Gauss_abs_gap":max(x["max_abs_gap"] for x in radau.values()),
 "refined_time_points":int(len(refined)),
 "max_refined_global_timestep_endpoint_depth_abs_gap":refined_gap,
 "source_atomic_proper_H_effect_on_photon_depth":nH_effect,
 "claim":"BASS_TYPEII_SOURCE_ATOMIC_H_AND_PROPER_HN_PHOTON_NUMERICALLY_CHECKED",
 "limits":"FLRW-calibrated SWIFT fit, external blackbody thermal radiation, no metric/electron self-consistent backreaction"
}
(HERE/"R6_ATOMIC_PHOTON_NUMERIC_VALIDATION.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
print(json.dumps(result,indent=2,sort_keys=True))
