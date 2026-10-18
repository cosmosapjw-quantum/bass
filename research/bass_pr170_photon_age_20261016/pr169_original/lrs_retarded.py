"""Source-formula FD96 linear Einstein--Vlasov causal retarded response.

Uses original BASS PR167 verified FD96 Gaussian q96 reconstruction; it is an
independent integrator, not a native REI H/He/Thomson matter callback.
SI Hubble times s^-1, x=ln(a/a_ref), dimensionless A,b, positive Sigma.
"""
from __future__ import annotations
from dataclasses import dataclass
import math
import numpy as np
from scipy.integrate import solve_ivp, cumulative_simpson

from reference_kinetic_equilibrium import FD96Equilibrium
from reference_kinetic_tangent import H0,OMEGA_M,OMEGA_B,OMEGA_R,OMEGA_L,AREF,XMAX


@dataclass(frozen=True)
class LinearCoefficients:
    x: float
    rho0: float
    pbar0: float
    alpha: float
    kappa: float
    hubble: float
    gamma: float


@dataclass(frozen=True)
class Response:
    x: np.ndarray
    b_per_A: np.ndarray
    s_per_href_per_A: np.ndarray
    b_without_feedback_per_A: np.ndarray
    picard_steps: int
    proven_q_bound: float
    posterior_discrete_bound: float
    discrete_residual: float


class FD96Retarded:
    def __init__(self, mass:float, fraction:float=.1):
        if not math.isfinite(fraction) or not 0 <= fraction <= (OMEGA_M-OMEGA_B)/OMEGA_M:
            raise ValueError('MASSIVE_MATTER_NONBARYONIC_BUDGET')
        self.fd=FD96Equilibrium(mass)
        self.mass=float(mass)
        self.fraction=float(fraction)
        self.cm=OMEGA_M*fraction/AREF**3
        self.K=H0**2*self.cm
        self.href=H0*math.sqrt(OMEGA_M/AREF**3+OMEGA_R/AREF**4+OMEGA_L)
        self.hdust=H0*math.sqrt(OMEGA_M*(1-fraction)/AREF**3)
        self.kappa0=self.coefficients(0.).kappa
        self.q_bound=(5./6.)*(fraction/(1-fraction))*self.kappa0*(1-math.exp(-XMAX))

    def coefficients(self,x:float)->LinearCoefficients:
        if not math.isfinite(x) or not 0. <= x <= XMAX+1e-11:
            raise ValueError('SOURCE_SCALE_DOMAIN')
        r=math.exp(-x); k=(r*self.fd.q)**2
        e0=np.hypot(self.mass,r*self.fd.q)
        w=self.fd.rw
        fac=r**3/self.fd.norm
        rho=fac*float(w@e0)
        j1=fac*float(w@(k/e0))
        j2=fac*float(w@(k*k/e0**3))
        pbar=j1/3.
        alpha=j1/5.
        kappa=2.*j1-(2./5.)*j2
        a=AREF*math.exp(x)
        h2=H0**2*(OMEGA_M*(1-self.fraction)/a**3 + OMEGA_R/a**4+OMEGA_L+self.cm*rho)
        if not (h2>0. and alpha>0. and kappa>0. and rho>0.):
            raise ArithmeticError('SOURCE_CONVEXITY_OR_FRIEDMANN_FAILURE')
        return LinearCoefficients(float(x),rho,pbar,alpha,kappa,math.sqrt(h2),kappa/alpha)

    def proven_contraction_bound(self, x_end:float=XMAX)->float:
        if not 0<=x_end<=XMAX+1e-12:raise ValueError('CONTRACTION_DOMAIN')
        return (5./6.)*(self.fraction/(1-self.fraction))*self.kappa0*(1-math.exp(-x_end))

    def proven_unforced_bound(self, x_end:float=XMAX)->float:
        """Uniform positive g(x) upper bound independent of m (linear response)."""
        if not 0<=x_end<=XMAX+1e-12:raise ValueError('UNFORCED_BOUND_DOMAIN')
        return (2./15.)*(self.fraction/(1.-self.fraction))*(
            x_end-(2./3.)*(-math.expm1(-1.5*x_end)))

    def tangent_ode(self, x_eval:np.ndarray|None=None, *, rtol:float=2e-12):
        if x_eval is None: x_eval=np.linspace(0.,XMAX,513)
        xs=np.asarray(x_eval,dtype=float)
        if xs.ndim!=1 or len(xs)<2 or xs[0]!=0. or xs[-1]>XMAX+1e-12 or np.any(np.diff(xs)<=0):
            raise ValueError('TANGENT_GRID')
        def rhs(x,y):
            c=self.coefficients(x)
            b,v=y
            return [self.href*v/c.hubble, -3*v+self.K/(self.href*c.hubble)*(c.alpha-c.kappa*b)]
        sol=solve_ivp(rhs,(0.,float(xs[-1])),(0.,0.),method='DOP853',rtol=rtol,atol=2e-15,
                      t_eval=xs,dense_output=True)
        if not sol.success:raise RuntimeError(sol.message)
        return sol

    def picard(self, x_eval:np.ndarray, *, iterations:int=25, tol:float=1e-14)->Response:
        xs=np.asarray(x_eval,dtype=float)
        if xs.ndim!=1 or len(xs)<5 or xs[0]!=0. or xs[-1]>XMAX+1e-12 or np.any(np.diff(xs)<=0):
            raise ValueError('PICARD_GRID')
        if iterations<1 or iterations>100 or not 0<tol<1e-4:raise ValueError('PICARD_PARAMS')
        c=[self.coefficients(float(x)) for x in xs]
        H=np.array([a.hubble for a in c]);al=np.array([a.alpha for a in c]);ka=np.array([a.kappa for a in c]);
        def propagate(force):
            # Integrate source in canonical shear p=e^(3x)*s, then b'=s/H.
            integral=cumulative_simpson(self.K*np.exp(3*xs)*force/H,x=xs,initial=0.)
            s=np.exp(-3*xs)*integral
            b=cumulative_simpson(s/H,x=xs,initial=0.)
            return b,s
        g,_=propagate(al)
        b=g.copy();delta=float('inf');steps=0
        for k in range(iterations):
            new=g-propagate(ka*b)[0]
            delta=float(np.max(np.abs(new-b)))
            b=new;steps=k+1
            if delta<tol:break
        _,s=propagate(al-ka*b)
        resid=float(np.max(np.abs(g-propagate(ka*b)[0]-b)))
        q=self.proven_contraction_bound(float(xs[-1]))
        posterior=q*delta/(1-q) if q<1 else math.inf
        return Response(xs,b,s/self.href,g,steps,q,posterior,resid)

    def direct_kernel(self,x:float,u:float)->float:
        """Positive retarded kernel using quadrature; slow independent spot-check."""
        if not 0<=u<=x<=XMAX+1e-12:raise ValueError('GREEN_DOMAIN')
        from scipy.integrate import quad
        if u==x:return 0.
        integral=quad(lambda v:math.exp(-3*v)/self.coefficients(v).hubble,u,x,
                     epsrel=1e-11)[0]
        return self.K*math.exp(3*u)*integral/self.coefficients(u).hubble

    def nonlinearity_remainder(self,A:float):
        """Compare true nonlinear source against its first-order tangent."""
        if A==0 or not -1<=A<=2:raise ValueError('NONLINEAR_A_DOMAIN')
        from reference_kinetic_tangent import EinsteinTangent
        m=EinsteinTangent(mass=self.mass,fraction=self.fraction,A=float(A),Sigma_ref=0,orientation=1)
        exact=m.endpoint(rtol=2e-12,atol=2e-14,n=51)
        tangent=self.tangent_ode(np.array([0.,XMAX])).y[:,-1]
        linear_signed=A*self.href*tangent[1]/self.coefficients(XMAX).hubble
        return {'A':A,'b_exact':exact['b'],
                'signed_s_over_H_exact':exact['signed_s_over_H'],
                'signed_s_over_H_linear':float(linear_signed),
                'signed_s_over_H_absolute_remainder':abs(exact['signed_s_over_H']-linear_signed),
                'b_linear':A*tangent[0],
                'b_absolute_remainder':abs(exact['b']-A*tangent[0]),
                'b_relative_linear_error':abs(exact['b']-A*tangent[0])/max(abs(exact['b']),1e-30),
                'b_A_PR164':exact['sensitivity_b_A'],'b_A_linear':float(tangent[0]),
                'nfev':exact['nfev']}
