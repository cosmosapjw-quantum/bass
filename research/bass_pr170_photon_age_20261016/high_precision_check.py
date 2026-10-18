"""Independent MP70 closed-form photon angular optics and Einstein kernel audit."""
from __future__ import annotations
import math,json,pathlib,argparse
import numpy as np
import mpmath as mp
from scipy.integrate import solve_ivp
from born_photon_stress import angular_f_delta,XMAX
from coupled_lrs_gamma import gamma_contraction_bound
from coupled_lrs_gamma import FD96Retarded,H0,AREF,OMEGA_R


def analytic_F(d):
    """Exact elementary integral of sqrt(A+B mu²) on mu in [0,1]."""
    t=mp.mpf(str(d))
    if t==0:return mp.mpf(1)
    A=mp.exp(2*t)
    B=mp.exp(-4*t)-A
    R1=mp.exp(-2*t)
    if B>0:
        return (R1 + A*mp.asinh(mp.sqrt(B/A))/mp.sqrt(B))/2
    return (R1 + A*mp.asin(mp.sqrt(-B/A))/mp.sqrt(-B))/2


def analytic_D(d):
    """D=-F'/2 evaluated with independent arbitrary-precision differentiation."""
    t=mp.mpf(str(d))
    if t==0:return mp.mpf(0)
    return -mp.diff(analytic_F,t)/2


def estimate_gamma_operator_max(mass:float):
    """Compute positive T_gamma[1] from independent two-component ODE."""
    model=FD96Retarded(mass,.1)
    def rhs(x,y):
        c=model.coefficients(x)
        K=(8/5)*(OMEGA_R/AREF**4)*math.exp(-4*x)
        return [model.href*y[1]/c.hubble,
                -3*y[1]+H0**2*K/(model.href*c.hubble)]
    s=solve_ivp(rhs,(0.,XMAX),(0.,0.),method='DOP853',
        rtol=1e-12,atol=1e-15,dense_output=True)
    if not s.success:raise RuntimeError(s.message)
    return float(s.y[0,-1]),gamma_contraction_bound(1.,.1)


def run(output:pathlib.Path):
    if output.exists():raise FileExistsError('CREATE_ONLY_HIGH_PRECISION')
    output.parent.mkdir(parents=True,exist_ok=True)
    mp.mp.dps=70
    cases=[]
    for d in (-.6,-.32,-.07,-.01,-1e-15,1e-15,.01,.09,.31,.62):
        val=analytic_F(d);stress=analytic_D(d)
        F,D=angular_f_delta(d,128)
        absF=abs(float(val)-F);absD=abs(float(stress)-D)
        cases.append(dict(d=d,analytic_F=mp.nstr(val,35),analytic_D=mp.nstr(stress,35),
                     gl128_F=F,gl128_D=D,F_abs_error=absF,D_abs_error=absD))
    maxf=max(x['F_abs_error'] for x in cases)
    maxd=max(x['D_abs_error'] for x in cases)
    gamma=[]
    for m in (3.,30.,300.):
        actual,upper=estimate_gamma_operator_max(m)
        gamma.append(dict(mass=m,direct_ode_positive_Tgamma_1_endpoint=actual,
            conservative_qgamma_bound=upper,admission=actual>0 and actual<=upper))
    out={'schema':'bass.pr170.independent_mp70_gamma_bound.v1',
        'method':'MP70 elementary F integral and independent derivative for Delta vs source angular GL128; positive Einstein photon Green operator source-only ODE',
        'rows':cases,'max_F_abs_error':maxf,'max_D_abs_error':maxd,
        'gamma_kernel_upper_bound_check':gamma,
        'numerical_pass':maxf<5e-12 and maxd<5e-11 and all(g['admission'] for g in gamma),
        'scope':'Discrete quadrature vs independently evaluated closed angular integral; no continuum spectral/chemistry theorem'}
    output.write_text(json.dumps(out,indent=2)+'\n')
    if not out['numerical_pass']:raise ArithmeticError('MP70_CLOSED_FORM_PARITY_OR_GAMMA_BOUND')
    print(json.dumps({'maxF':maxf,'maxD':maxd,'gamma':gamma,'status':'PASS'},indent=2))
    return out
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=pathlib.Path,required=True)
    run(p.parse_args().out)
