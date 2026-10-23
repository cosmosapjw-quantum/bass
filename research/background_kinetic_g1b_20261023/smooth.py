"""Positive quadratures for fixed smooth initial sources, not a collision model.

q=cp/(k_B T_ref). Massive FD is momentum-decoupled, not equilibrium in E.
All resolutions use the same continuum normalizer. No density fitting per grid.
"""
from __future__ import annotations
from pathlib import Path
from functools import lru_cache
import json, math
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.special import zeta
from vendor import kinetic as kn

_LOCK=json.loads((Path(__file__).with_name('NORMALIZERS.json')).read_text())


def _kind(kind: str) -> str:
    if kind not in ('FD','Planck'): raise ValueError('statistics must be FD or Planck')
    return kind


def _real(value,name):
    if np.iscomplexobj(value): raise ValueError(f'{name}: real input required')
    x=np.asarray(value,dtype=float)
    if not np.all(np.isfinite(x)): raise ValueError(f'{name}: finite input required')
    return x


def occupation(q,kind: str):
    """Stable continuous function at positive q; no artificial high-q floor."""
    _kind(kind);q=_real(q,'q')
    if np.any(q<0) or (kind=='Planck' and np.any(q==0)):
        raise ValueError('Planck occupation needs q>0; FD needs q>=0')
    e=np.exp(-q)
    return e/(1+e) if kind=='FD' else e/(-np.expm1(-q))


def radial_density(q,kind: str):
    """q^2 f(q), continued by zero at q=0 for BOTH admitted spectra."""
    _kind(kind);q=_real(q,'q')
    if np.any(q<0):raise ValueError('nonnegative radial coordinate required')
    safe=np.where(q>0,q,1.)
    return np.where(q>0,q*q*occupation(safe,kind),0.)


def radial_moments(kind: str):
    _kind(kind)
    # Integrals of q^p f(q), with the Gamma factor included, p=2,3,4.
    return tuple(math.factorial(p)*float(zeta(p+1,1))*(1-2.**(-p) if kind=='FD' else 1.) for p in (2,3,4))


def normalizer(kind: str,mass: float):
    _kind(kind)
    if not np.isfinite(mass):raise ValueError('finite mass required')
    if kind=='Planck':
        if mass!=0:raise ValueError('Planck source admitted only for massless photons')
        return float(_LOCK['Planck_I3'])
    if mass not in (0.,3.,30.):raise ValueError('this source lock admits only FD masses 0,3,30')
    return float(_LOCK['FD_Z_m'][str(int(mass))])


def radial_rule(order: int,Q: float=48.):
    """Composite positive GL on [0,4,12,24,Q], keeping valid inner breaks."""
    if not isinstance(order,(int,np.integer)) or order<1 or order>128:
        raise ValueError('integer subinterval order 1..128 required')
    if not np.isfinite(Q) or Q<=0:raise ValueError('positive finite cutoff required')
    breaks=[0.]+[x for x in (4.,12.,24.) if x<Q]+[float(Q)]
    u,v=leggauss(order);qs=[];ws=[]
    for lo,hi in zip(breaks[:-1],breaks[1:]):
        qs.append(lo+(hi-lo)*(u+1)/2);ws.append((hi-lo)*v/2)
    return np.concatenate(qs),np.concatenate(ws)


def angular_rule(nmu: int):
    if not isinstance(nmu,(int,np.integer)) or nmu<4 or nmu>128:
        raise ValueError('integer angular order 4..128 required')
    mu,wm=leggauss(nmu);nphi=2*nmu
    phi=2*np.pi*(np.arange(nphi)+.5)/nphi
    st=np.sqrt(1-mu*mu)
    n=np.stack([np.outer(st,np.cos(phi)).ravel(),np.outer(st,np.sin(phi)).ravel(),np.repeat(mu,nphi)],axis=1)
    w=np.repeat(wm,nphi)*(2*np.pi/nphi)
    return n,w


def default_anisotropy():
    axis=np.array([1.,2.,3.])/np.sqrt(14.)
    return .6*(1.5*np.outer(axis,axis)-.5*np.eye(3))


def angular_factor(n,A=None):
    if A is None:return np.ones(len(n))
    A=_real(A,'angular shape')
    if A.shape!=(3,3) or np.max(np.abs(A-A.T))>1e-13 or abs(np.trace(A))>1e-13:
        raise ValueError('angular shape must be symmetric tracefree')
    if 1+np.linalg.eigvalsh(A)[0]<=0:
        raise ValueError('strictly positive continuous angular source required')
    return 1+np.einsum('qi,ij,qj->q',n,A,n)


def packets(kind: str,mass: float,order: int,nmu: int,*,Q: float=48.,amplitude: float=1.,A=None):
    Z=normalizer(kind,mass)
    if not np.isfinite(amplitude) or amplitude<=0:raise ValueError('positive finite amplitude required')
    q,dq=radial_rule(order,Q);n,wa=angular_rule(nmu);g=angular_factor(n,A)
    k=(q[:,None,None]*n[None,:,:]).reshape(-1,3)
    w=(dq[:,None]*radial_density(q,kind)[:,None]*(wa*g)[None,:]*(amplitude/(4*np.pi*Z))).ravel()
    m=np.full(len(w),mass)
    if np.any(w<=0) or not np.all(np.isfinite(w)):
        raise ValueError('quadrature weights outside positive floating-point domain')
    return k,w,m


def photon_packets(kind: str,nmu: int,*,amplitude: float=1.,A=None):
    """Exact N^a/T^ab radial reduction for separable massless collisionless data.

    A representative qbar=I3/I2 preserves two moments, not the spectrum.
    Frequency-dependent operators must use the original spectrum instead.
    """
    Z=normalizer(kind,0.)
    if not np.isfinite(amplitude) or amplitude<=0:raise ValueError('positive finite amplitude required')
    I2,I3,_=radial_moments(kind);n,wa=angular_rule(nmu)
    return n*(I3/I2),wa*angular_factor(n,A)*(amplitude*I2/(4*np.pi*Z)),np.zeros(len(n))


def radial_tail(power: int,Q: float,kind: str):
    """Analytic upper bound evaluated in binary64, not interval arithmetic."""
    _kind(kind)
    if not isinstance(power,(int,np.integer)) or power<0 or power>12 or not np.isfinite(Q) or Q<=0:
        raise ValueError('power 0..12 and positive finite cutoff required')
    gamma=math.factorial(power)*math.exp(-Q)*sum(Q**j/math.factorial(j) for j in range(power+1))
    return gamma if kind=='FD' else gamma/(-math.expm1(-Q))


def energy_tail_bound(kind: str,mass: float,Q: float,K: float=1.,J: float=1.,amplitude: float=1.):
    """Same-prescribed-field omitted initial-q energy bound, not trajectory error.

    |k(t)|<=K q, w(t)/w(0)<=J. Angular source is nonnegative with mean one.
    max(m I2,I3) is an analytic LOWER bound on the full continuum normalizer.
    """
    normalizer(kind,mass)
    if not all(np.isfinite(x) and x>0 for x in (K,J,amplitude)):
        raise ValueError('positive finite bound inputs required')
    I2,I3,_=radial_moments(kind)
    return amplitude*J*(mass*radial_tail(2,Q,kind)+K*radial_tail(3,Q,kind))/max(mass*I2,I3)


def deformed(data,alpha=0.,beta=(0.,0.,0.),boost=(0.,0.,0.)):
    beta=_real(beta,'beta')
    if beta.shape!=(3,) or abs(beta.sum())>1e-12 or not np.isfinite(alpha):raise ValueError('finite tracefree diagonal beta required')
    k,w,m=data;k=k*np.exp(-alpha-beta);w=w*np.exp(-3*alpha)
    if np.any(np.asarray(boost)!=0):k,w=kn.boost(k,w,m,boost)
    kn.packet_arrays(k,w,m)
    return k,w,m


def observables(data):
    k,w,m=data;e=np.hypot(m,np.linalg.norm(k,axis=1))
    return kn.tensor(k,w,m),np.r_[w.sum(),np.sum(w[:,None]*k/e[:,None],axis=0)]
