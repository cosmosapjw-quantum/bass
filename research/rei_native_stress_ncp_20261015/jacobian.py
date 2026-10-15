"""Analytic massive kinetic susceptibility and partial BASS Einstein Jacobian.

Fixed x, photon/neutrino multipole state and signed s; derivative is with respect
to LRS b, not the full stiff H/He Jacobian nor a closure for stellar Q^a.
Units: rho, Delta dimensionless original FD96; H,s in SI inverse-seconds.
"""
from __future__ import annotations
import math
import sys
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[1]/"research/rei_sigma_kinetic_gamma_nu_20261015"))
from joint_kinetic import KineticGammaNuMassive
from stable_moments import StableMassiveMoments

def kinetic_susceptibility(m:StableMassiveMoments,x:float,b:float,A:float):
    if not all(math.isfinite(v) for v in (x,b,A)) or x<0 or abs(b)>1 or not -1<=A<=2:
        raise ValueError("physical finite x, b, A")
    r=math.exp(-x)
    k=(r*m.q[:,None])**2
    z=(m.mu[None,:])**2
    tp=math.expm1(2*b);tz=math.expm1(-4*b)
    dp=k*(1+tz)*z-k*(1+tp)*(1-z)/2
    E=np.sqrt(m.mass*m.mass+k*(1+tp*(1-z)+tz*z))
    dk_b=-4*k*(1+tz)*z-k*(1+tp)*(1-z)
    W=m.rw[:,None]*(m.w*(1+A*m.p2))[None,:]
    return float(r**3/m.norm*np.sum(W*(dk_b/E+2*dp*dp/(E**3))))

def massive_jacobian_at_state(model:KineticGammaNuMassive,x:float,y):
    if not model.stable_massive_pi:
        raise ValueError("needs explicitly stabilized kinetic mode")
    p=model.fields(x,y)
    _,_,_,delta=model.mass.evaluate_with_delta(x,p["b"],model.Am)
    susc=kinetic_susceptibility(model.mass,x,p["b"],model.Am)
    massnorm=model.mass_normalizer
    # d rho_massive_normalized/db = -2 massnorm DeltaP.
    h_b=-model.source.h0**2*massnorm*delta/p["H"]
    pi_total=p["pi_radiation_norm"]+p["pi_massive_norm"]
    pi_b=massnorm*susc/3
    rhs_shear_b=3*model.source.h0**2/model.source.href*(
        pi_b/p["H"] -pi_total*h_b/(p["H"]*p["H"]))
    return {
        "x":float(x),"H_per_s":p["H"],"DeltaP_unit_normalized":delta,
        "dDeltaP_db_unit_normalized":susc,
        "dH_db_per_s":h_b,
        "d_pi_massive_norm_db":pi_b,
        "d_rhs_signed_s_over_href_db":rhs_shear_b,
        "scope":"partial b derivative at fixed x, radiation multipoles and s; not full native chemistry Newton Jacobian"
    }
