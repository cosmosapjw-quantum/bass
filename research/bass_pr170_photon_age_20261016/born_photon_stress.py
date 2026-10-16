"""Exact collisionless LRS Bianchi-I bolometric stress of born-isotropic photons.

BASS PR170 source-only research.  Each photon cohort starts isotropic in its own
orthonormal emission frame at x=u and free streams with conserved spatial
Killing momenta.  S(x) is physical energy density emitted per unit x=ln(a/aref).
No opacity, Thomson, gas or stellar momentum reaction, polarization or EoR.

The integrals use the birth-local direction mu, without a second Jacobian.
Units for all rho, Delta, U, M and S are caller's common energy-density unit;
b, x, mu, source shape dimensionless; Sigma = sqrt(3)|s|/H external.
"""
from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache
from typing import Callable
import math
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.integrate import solve_ivp

XMAX = math.log(21.0 / 5.0)

@lru_cache(None)
def _gl(n: int):
    if not isinstance(n,int) or n<8 or n>512:
        raise ValueError('QUADRATURE_ORDER_DOMAIN_8_TO_512')
    mu,w=leggauss(n)
    return mu,w*0.5


def angular_f_delta(d: float|np.ndarray, n_mu:int=48):
    """Return F(d), D(d), using expm1 and exact isotropic angular cancellation.

    At d=0 returns F=1,D=0 *exactly* with positive continuum measure.
    Avoid naive subtraction of positive transverse and parallel pressures.
    """
    mu,wa=_gl(n_mu)
    ds=np.asarray(d,dtype=float)
    if not np.all(np.isfinite(ds)) or np.any(np.abs(ds)>2):
        raise ValueError('BIRTH_GEOMETRY_DIFFERENCE_DOMAIN')
    shape=ds.shape
    dd=ds.reshape(-1,1)
    z=mu[None,:]**2
    tp=np.expm1(2*dd)
    tz=np.expm1(-4*dd)
    w=tp*(1-z)+tz*z
    R=np.sqrt(1+w)
    if not np.all(np.isfinite(R)) or np.any(R<=0):
        raise FloatingPointError('NULL_GEODESIC_ENERGY')
    p2=(3*z-1)/2
    q=p2+tz*z-tp*(1-z)/2
    inv_difference=-w/(R*(R+1))
    F=1+np.sum(wa[None,:]*(w/(R+1)),axis=1)
    D=(tz[:,0]-tp[:,0])/3+np.sum(wa[None,:]*q*inv_difference,axis=1)
    if not np.all(np.isfinite(F)) or not np.all(np.isfinite(D)) or np.any(F<=0):
        raise ArithmeticError('NONPOSITIVE_RADIATION_RESPONSE')
    if shape==():return float(F[0]),float(D[0])
    return F.reshape(shape),D.reshape(shape)


def angular_direct(d: float|np.ndarray,n_mu:int=128):
    """Independent naive quadrature oracle only for finite |d| away from zero."""
    mu,wa=_gl(n_mu)
    ds=np.asarray(d,dtype=float)
    shape=ds.shape;dd=ds.reshape(-1,1);z=mu[None,:]**2
    eperp=np.exp(2*dd);epara=np.exp(-4*dd)
    R=np.sqrt(eperp*(1-z)+epara*z)
    F=np.sum(wa[None,:]*R,axis=1)
    D=np.sum(wa[None,:]*(epara*z-0.5*eperp*(1-z))/R,axis=1)
    if shape==():return float(F[0]),float(D[0])
    return F.reshape(shape),D.reshape(shape)


def small_d_series(d:float):
    """Wolfram/SymPy verified Taylor truncation to second order in stress."""
    if not math.isfinite(d) or abs(d)>0.05:raise ValueError('SERIES_SMALL_D_DOMAIN')
    return 1+8/5*d*d-16/21*d**3, -8/5*d+8/7*d*d

@dataclass(frozen=True)
class PhotonMoments:
    x:float
    b:float
    rho:float
    delta:float
    isotropic_rho:float
    memory_b:float
    delta_linear:float
    source_per_x:float
    rho_quadratic:float
    delta_quadratic:float


class BornIsotropicRadiation:
    """A specified collisionless photon source from isotropic birth cohorts.

    ``b(x)`` and ``source(x)`` accept NumPy arrays of evaluation points.
    The source is a physically dimensionful or normalized bolometric energy
    injection per physical volume per unit x, not a comoving photon count.
    ``bprime(x)`` is provided for the independent exact energy work test.
    """
    def __init__(self,b:Callable,source:Callable,*,rho_old:float=1.,
                 x_end:float=XMAX,n_mu:int=48,n_birth:int=64,bprime:Callable|None=None):
        if not (math.isfinite(rho_old) and rho_old>=0 and 0<x_end<=XMAX+1e-12):
            raise ValueError('RADIATION_INITIAL_STOCK_DOMAIN')
        _gl(n_mu);_gl(n_birth)
        self.b=b;self.source=source;self.bprime=bprime
        self.rho_old=float(rho_old);self.x_end=float(x_end)
        self.n_mu=n_mu;self.n_birth=n_birth
        try:
            b0=float(np.asarray(b(np.array([0.])),dtype=float).reshape(-1)[0])
        except Exception as exc:
            raise ValueError('RADIATION_B_FUNCTION') from exc
        if not math.isfinite(b0) or abs(b0)>1.:
            raise ValueError('INITIAL_ANISOTROPY_DOMAIN')
        self.b0=b0

    def _evaluate(self,func,values,tag):
        raw=np.asarray(func(values),dtype=float)
        if raw.shape==():raw=np.full(values.shape,float(raw))
        if raw.shape!=values.shape or not np.all(np.isfinite(raw)):
            raise ValueError(tag)
        return raw

    def point(self,x:float)->PhotonMoments:
        if not math.isfinite(x) or not (0<=x<=self.x_end):
            raise ValueError('SOURCE_AGE_INTERVAL_DOMAIN')
        bx=float(self._evaluate(self.b,np.array([x]),'B_GEOMETRY_SHAPE')[0])
        if abs(bx)>1.:raise ValueError('B_CHART_DOMAIN')
        Sx=float(self._evaluate(self.source,np.array([x]),'SOURCE_SHAPE')[0])
        if Sx<0:raise ValueError('NEGATIVE_ISOTROPIC_BIRTH_SOURCE')
        wold=self.rho_old*math.exp(-4*x)
        Fold,Dold=angular_f_delta(bx-self.b0,self.n_mu)
        rho=wold*Fold;Delta=wold*Dold
        U=wold;M=wold*self.b0
        quadratic_rho=wold*(1+8/5*(bx-self.b0)**2)
        quadratic_delta=wold*(-8/5*(bx-self.b0)+8/7*(bx-self.b0)**2)
        if x:
            nodes,weights=_gl(self.n_birth)
            us=x*(nodes+1)*0.5
            src=self._evaluate(self.source,us,'SOURCE_SHAPE')
            if np.any(src<0):raise ValueError('NEGATIVE_ISOTROPIC_BIRTH_SOURCE')
            bus=self._evaluate(self.b,us,'B_GEOMETRY_SHAPE')
            if np.any(abs(bus)>1.):raise ValueError('B_CHART_DOMAIN')
            dd=bx-bus
            F,D=angular_f_delta(dd,self.n_mu)
            weights=x*weights*src*np.exp(-4*(x-us))
            rho+=float(weights@F);Delta+=float(weights@D)
            U+=float(weights.sum());M+=float(weights@bus)
            quadratic_rho+=float(weights@(1+8/5*dd**2))
            quadratic_delta+=float(weights@(-8/5*dd+8/7*dd**2))
        Delta_linear=-(8/5)*(U*bx-M)
        if (rho+8e-14<U or rho<-1e-14 or
                (x>0 and (self.rho_old>0 or Sx>0) and rho<=0)):
            raise ArithmeticError('POSITIVE_KINETIC_ENERGY_OR_CONVEXITY')
        return PhotonMoments(float(x),bx,float(rho),float(Delta),float(U),
                            float(M),float(Delta_linear),Sx,
                            float(quadratic_rho),float(quadratic_delta))

    def memory_ode(self,x_eval:np.ndarray, *,rtol:float=2e-12,atol:float=2e-14):
        xs=np.asarray(x_eval,dtype=float)
        if xs.ndim!=1 or len(xs)<2 or xs[0]!=0 or np.any(np.diff(xs)<=0) or xs[-1]>self.x_end:
            raise ValueError('MEMORY_ODE_GRID')
        def rhs(x,y):
            S=float(self._evaluate(self.source,np.array([x]),'SOURCE_SHAPE')[0])
            b=float(self._evaluate(self.b,np.array([x]),'B_GEOMETRY_SHAPE')[0])
            if S<0:raise ValueError('NEGATIVE_ISOTROPIC_BIRTH_SOURCE')
            return [-4*y[0]+S,-4*y[1]+S*b]
        sol=solve_ivp(rhs,(0.,float(xs[-1])),[self.rho_old,self.rho_old*self.b0],
                      method='DOP853',rtol=rtol,atol=atol,t_eval=xs,dense_output=True)
        if not sol.success:raise RuntimeError(sol.message)
        return sol

    def energy_rhs(self,x:float)->float:
        if self.bprime is None:raise ValueError('MISSING_SHEAR_DERIVATIVE')
        p=self.point(x)
        bp=float(self._evaluate(self.bprime,np.array([x]),'BPRIME_SHAPE')[0])
        return -4*p.rho+p.source_per_x-2*bp*p.delta

    def ledger(self,x_end:float,n_time:int=80):
        """Direct physical-volume energy balance: rho +int(4rho+2b'Δ)=rho0+int S."""
        if self.bprime is None:raise ValueError('MISSING_SHEAR_DERIVATIVE')
        if x_end<=0 or x_end>self.x_end:raise ValueError('LEDGER_DOMAIN')
        t,wt=_gl(n_time)
        ts=x_end*(t+1)*0.5;wt=x_end*wt
        p=[self.point(float(u)) for u in ts]
        bdot=self._evaluate(self.bprime,ts,'BPRIME_SHAPE')
        dilation=float(np.dot(wt,[4*z.rho for z in p]))
        shear_work=float(np.dot(wt,[2*bp*z.delta for bp,z in zip(bdot,p)]))
        emission=float(np.dot(wt,[z.source_per_x for z in p]))
        end=self.point(x_end)
        residual=end.rho+dilation+shear_work-self.rho_old-emission
        return {'energy_residual':float(residual),'rho_endpoint':end.rho,
                'isotropic_initial_energy':self.rho_old,'emission_integral':emission,
                'dilution_integral':dilation,'shear_work_integral':shear_work,
                'unit':'same physical energy density unit as input source/rho_old'}
