"""Source-formula reconstruction of BASS FD96 LRS stress equilibrium.

Physics scope: massive collisionless canonical q,mu kinetic distribution
W=1+A*P2(mu)>=0, metric (-,+,+,+), a_perp=a e^-b,
a_parallel=a e^2b. This standalone evaluator cannot evolve H/He or CMB.

Original source and prior BASS PRs:
 bianchi/matter/freestream.py original 96-point mapped GL FD source;
 PR162 stable DeltaP; PR163 analytic chi_b; PR164 mass-stress tangent.
Their byte identities are recorded in parent JSON. This implementation does
NOT claim byte equality with source: it reconstructs the physical formula.
"""
from __future__ import annotations
from dataclasses import dataclass
import math
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.optimize import brentq

XMAX=math.log(21.0 / 5.0)

@dataclass(frozen=True)
class Stress:
    rho:float
    pbar:float
    delta:float
    chi_b:float
    delta_A:float
    delta_x:float
    p_perp:float
    p_parallel:float

@dataclass(frozen=True)
class Root:
    x:float
    A:float
    m:float
    b_star:float
    db_dA:float
    db_dx:float
    chi_b:float
    rho_min:float
    residual_delta:float
    b_nonrel:float

class FD96Equilibrium:
    def __init__(self, mass:float, angular:int=32):
        if not math.isfinite(mass) or not 3.0<=mass<=1e5:
            raise ValueError('mass_outside_BASS_source_domain')
        if not isinstance(angular,int) or not 8<=angular<=256:
            raise ValueError('angular_nodes_outside_BASS_source_domain')
        self.mass=float(mass)
        t,wr=leggauss(96)
        self.q=3.0*(1.0+t)/(1.0-t)
        self.dq=wr*6.0/(1.0-t)**2
        self.rw=self.dq*self.q*self.q/(np.exp(np.minimum(self.q,700.0))+1.0)
        self.mu,wa=leggauss(angular)
        self.wa=wa/2.0
        self.z=self.mu**2
        self.p2=(3.0*self.z-1.0)/2.0
        self.norm=float(self.rw@np.hypot(self.mass,self.q))
        self.initial_v2=float(self.rw@(self.q**2/np.hypot(self.mass,self.q))/self.norm)
        if self.norm<=0 or not np.isclose(sum(self.wa),1.0,rtol=0,atol=4e-14):
            raise ArithmeticError('SOURCE_QUADRATURE_INVALID')

    def _validate(self,x:float,b:float,A:float):
        if not all(math.isfinite(float(t)) for t in (x,b,A)):
            raise ValueError('NONFINITE_SOURCE_STATE')
        if not (0<=x<=XMAX+1e-9 and abs(b)<=1 and -1<=A<=2):
            raise ValueError('BASS_SOURCE_CHART_OR_POSITIVITY')

    def stress(self,x:float,b:float,A:float)->Stress:
        self._validate(x,b,A)
        r=math.exp(-float(x));r3=r*r*r
        k=(r*self.q)[:,None]**2
        z=self.z[None,:]
        p2=self.p2[None,:]
        wa=self.wa[None,:]
        W=wa*(1+A*p2)
        tperp=math.expm1(2*b)
        tpara=math.expm1(-4*b)
        d=tperp*(1-z)+tpara*z
        e0=np.hypot(self.mass,r*self.q)[:,None]
        E=np.sqrt(e0*e0+k*d)
        ep=1+tperp;ez=1+tpara
        X=k*ep*(1-z);Z=k*ez*z
        L=Z-X*.5
        rw=self.rw[:,None]
        C=r3/self.norm
        rho=C*np.sum(rw*W*E)
        pbar=C*np.sum(rw*W*(X+Z)/(3*E))
        # PR162 cancellation-resistant pressure anisotropy.
        # Analytical exact GL integral of g/P2 polynomial in the 1/E0 term.
        g=p2+tpara*z-tperp*(1-z)*.5
        inv_diff=-k*d/(E*e0*(E+e0))
        poly=A/5+tpara*(1/3+2*A/15)-tperp*(1/3-A/15)
        tail=np.sum(W*g*inv_diff,axis=1)
        delta=C*np.sum(self.rw*(r*self.q)**2*(poly/e0[:,0]+tail))
        # Pointwise-positive Hessian: no cancellation of divergent signed terms.
        positive=self.mass*self.mass*(2*X+8*Z)
        positive+=X*X+14*X*Z+4*Z*Z
        chi_b=-.5*C*np.sum(rw*W*positive/(E**3))
        # A derivative from exact GL-integrated first term, remainder rationalized.
        poly_A=1/5+tpara*2/15+tperp/15
        tail_A=np.sum(wa*p2*g*inv_diff,axis=1)
        delta_A=C*np.sum(self.rw*(r*self.q)**2*(poly_A/e0[:,0]+tail_A))
        # Comoving-density redshift derivative, fixed b,A,q,mu.
        delta_x=-5*delta+C*np.sum(rw*W*L*(X+Z)/E**3)
        p_perp=pbar-delta/3
        p_parallel=pbar+2*delta/3
        result=Stress(*(float(v) for v in (rho,pbar,delta,chi_b,delta_A,delta_x,p_perp,p_parallel)))
        if not (result.rho>0 and result.p_perp>=0 and result.p_parallel>=0 and
                result.chi_b<0 and result.delta_A>0):
            raise ArithmeticError('NONPHYSICAL_KINETIC_SOURCE')
        return result

    def equilibrium(self,x:float,A:float,btol:float=2e-14)->Root:
        self._validate(x,0.0,A)
        if not math.isfinite(btol) or not 0<btol<=1e-7:
            raise ValueError('BOUND_TOLERANCE_INVALID')
        if A==0:
            root=0.0
        else:
            f=lambda b: self.stress(x,b,A).delta
            if f(-1.)<=0 or f(1.)>=0:
                raise ValueError('ROOT_OUTSIDE_BASS_BOUNDED_CHART')
            root=float(brentq(f,-1.,1.,xtol=btol,rtol=8.881784197001252e-16,maxiter=110))
        st=self.stress(x,root,A)
        return Root(x=float(x),A=float(A),m=self.mass,b_star=root,
            db_dA=-st.delta_A/st.chi_b,db_dx=-st.delta_x/st.chi_b,
            chi_b=st.chi_b,rho_min=st.rho,residual_delta=st.delta,
            b_nonrel=math.log((5+2*A)/(5-A))/6)

    def isotropic_slope(self,x:float):
        self._validate(x,0.,0.)
        r=math.exp(-x)
        k=(r*self.q)**2
        e0=np.hypot(self.mass,r*self.q)
        j1=float(self.rw@(k/e0));j2=float(self.rw@(k*k/e0**3))
        R=j2/j1
        return 1/(10-2*R),R

    def stress_direct(self,x:float,b:float,A:float):
        """Independent conventional positive-pressure difference, unsafe near zero."""
        self._validate(x,b,A)
        k=(math.exp(-x)*self.q)[:,None]**2
        z=self.z[None,:]
        X=k*math.exp(2*b)*(1-z)
        Z=k*math.exp(-4*b)*z
        E=np.sqrt(self.mass**2+X+Z)
        W=self.rw[:,None]*self.wa[None,:]*(1+A*self.p2[None,:])
        fac=math.exp(-3*x)/self.norm
        pperp=fac*np.sum(W*X/(2*E))
        ppara=fac*np.sum(W*Z/E)
        return float(ppara-pperp)
