"""Optional first-order BASS LRS Einstein matter + old free-stream radiation shear.

This is a DIFFERENT first-order background diagnostic from injected photon
cohorts.  It reallocates a fraction f_gamma of the already counted isotropic
Omega_r reference energy into initially-isotropic free-streaming photons,
without adding their rho a second time to H^2.  S(x)=0 in this coupling.
There is no native REI chemistry, new photons, opacity or momentum Q^a.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import math,sys
import numpy as np
from scipy.integrate import solve_ivp
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/'pr169_original'))
from lrs_retarded import FD96Retarded
from reference_kinetic_tangent import H0,AREF,OMEGA_R,OMEGA_M,XMAX

@dataclass(frozen=True)
class FeedbackResult:
    x:np.ndarray
    b_per_A:np.ndarray
    signed_s_over_H_per_A:np.ndarray
    b_shear_from_matter_only:np.ndarray
    mass:float
    f_gamma:float
    universal_q_bound:float
    gamma_q_bound:float
    source_owner_note:str


def gamma_contraction_bound(f_gamma:float,f_m:float,x_end:float=XMAX):
    if not (math.isfinite(f_gamma) and 0<=f_gamma<=1 and
            math.isfinite(f_m) and 0<=f_m<1 and 0<=x_end<=XMAX+1e-12):
        raise ValueError('PHOTON_ENERGY_ALLOCATION_DOMAIN')
    # Conservative dust-lower-bound inequality for Hbar^2.
    return (16/15)*f_gamma*OMEGA_R/(OMEGA_M*(1-f_m)*AREF)*(1-math.exp(-x_end))


def integrate(mass:float,f_gamma:float,x_eval:np.ndarray|None=None)->FeedbackResult:
    if not math.isfinite(f_gamma) or not 0<=f_gamma<=1:
        raise ValueError('PHOTON_ENERGY_ALLOCATION_DOMAIN')
    model=FD96Retarded(mass,.1)
    if x_eval is None: x_eval=np.linspace(0.,XMAX,129)
    xs=np.asarray(x_eval,dtype=float)
    if xs.ndim!=1 or len(xs)<2 or xs[0]!=0 or xs[-1]>XMAX+1e-12 or np.any(np.diff(xs)<=0):
        raise ValueError('GAMMA_GRID_DOMAIN')
    def rhs(x,y):
        c=model.coefficients(x)
        b,v=y
        photon0=(OMEGA_R/AREF**4)*f_gamma*math.exp(-4*x)
        gamma_pressure_diff_per_A=-(8/5)*photon0*b
        total_pressure_diff_per_A=model.cm*(c.alpha-c.kappa*b)+gamma_pressure_diff_per_A
        return [model.href*v/c.hubble,
                -3*v+H0**2*total_pressure_diff_per_A/(model.href*c.hubble)]
    sol=solve_ivp(rhs,(0.,float(xs[-1])),(0.,0.),method='DOP853',
             rtol=2e-12,atol=2e-15,t_eval=xs,dense_output=True)
    if not sol.success:raise RuntimeError(sol.message)
    matter=model.tangent_ode(xs,rtol=2e-12)
    hs=np.array([model.coefficients(float(x)).hubble for x in xs])
    gamma_bound=gamma_contraction_bound(f_gamma,model.fraction,float(xs[-1]))
    return FeedbackResult(xs,sol.y[0],sol.y[1]*model.href/hs,
                          matter.y[0],float(mass),float(f_gamma),
                          model.proven_contraction_bound(float(xs[-1]))+gamma_bound,
                          gamma_bound,
                          'f_gamma share of pre-existing Omega_r, initial photons only; no extra energy-density stock, no new emission/reactions')
