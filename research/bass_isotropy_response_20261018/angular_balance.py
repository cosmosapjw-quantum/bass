"""Opt-in positive P2 quadrature for *new isotropic* LRS source only.

No old radiation stock, physical anisotropic source, spectrum, or native default
is modified. This is standard KL information projection on a finite ray set.
"""
from __future__ import annotations
from dataclasses import dataclass
import math
import numpy as np

ALGORITHM_ID='BASS_LRS_SOURCE_KL_P2_V1'
DEFAULT_ATOL=3e-15

@dataclass(frozen=True)
class Result:
    weights:np.ndarray
    multiplier:float
    iterations:int
    before:float
    after:float
    variance:float
    kl:float

def project(mu,prior,*,atol=DEFAULT_ATOL)->Result:
    """Full-positive KL minimizer with normalized sum and zero P2 moment.

    Requires sorted reflection-paired rays and an even source prior. Feasibility
    is checked independently of normalization; impossible supports are rejected.
    Tolerance is dimensionless absolute mean P2, NOT a full angular error bound.
    """
    m=np.asarray(mu,dtype=float);q=np.asarray(prior,dtype=float)
    if (m.ndim!=1 or q.shape!=m.shape or not 2<=m.size<=4096 or
        not np.isfinite(m).all() or not np.isfinite(q).all() or
        np.any(np.abs(m)>1) or np.any(q<=0) or np.any(np.diff(m)<=0)):
        raise ValueError('ANGULAR_INPUT_DOMAIN')
    if not math.isfinite(atol) or not 1e-16<=atol<=1e-10:
        raise ValueError('ANGULAR_TOLERANCE_DOMAIN')
    # Scale before summation to avoid overflowing a legal positive prior.
    q=q/q.max();q=q/math.fsum(q)
    if np.max(np.abs(m+m[::-1]))>5e-14 or np.max(np.abs(q-q[::-1]))>5e-14:
        raise ValueError('REFLECTION_SOURCE_REQUIRED')
    p=(3*m*m-1)/2
    if not np.all(p==0) and not (p.min()<0<p.max()):
        raise ValueError('INFEASIBLE_ANGULAR_SUPPORT')
    logq=np.log(q)
    def ev(lam):
        l=logq+lam*p;l-=l.max()
        w=np.exp(l);w/=math.fsum(w)
        mean=math.fsum(w*p)
        return w,mean,math.fsum(w*(p-mean)**2)
    before=math.fsum(q*p)
    def result(w,lam,n,res,var):
        if np.any(w<=0) or not np.isfinite(w).all():
            raise ArithmeticError('NUMERIC_POSITIVE_SUPPORT_LOSS')
        if abs(res)>atol:raise ArithmeticError('MOMENT_TOLERANCE')
        return Result(w,lam,n,before,res,var,math.fsum(w*(np.log(w)-logq)))
    if abs(before)<=atol:
        return result(q.copy(),0.,0,before,math.fsum(q*(p-before)**2))
    lo,hi=-1.,1.
    for _ in range(60):
        if ev(lo)[1]<=0:break
        lo*=2
    else:raise ArithmeticError('LOWER_BRACKET')
    for _ in range(60):
        if ev(hi)[1]>=0:break
        hi*=2
    else:raise ArithmeticError('UPPER_BRACKET')
    for n in range(1,161):
        lam=lo+(hi-lo)/2;w,res,var=ev(lam)
        if abs(res)<=atol:return result(w,lam,n,res,var)
        if res<0:lo=lam
        else:hi=lam
    raise ArithmeticError('MOMENT_NOT_CONVERGED')

def balance(mu,prior,*,atol=DEFAULT_ATOL):
    return project(mu,prior,atol=atol).weights

def lrs_rule(b:float,n:int):
    """New research mesh; the unchanged native PR172 supports only 8/16/32."""
    if (not math.isfinite(b) or abs(b)>2 or isinstance(n,bool) or
        not isinstance(n,int) or not 4<=n<=512 or n%2):
        raise ValueError('LRS_GRID_DOMAIN')
    m,w=np.polynomial.legendre.leggauss(n)
    R=np.sqrt(math.exp(2*b)*(1-m*m)+math.exp(-4*b)*m*m)
    q=w/R**3;q/=math.fsum(q)
    return m*math.exp(-2*b)/R,q

def support_interval(n:int):
    if isinstance(n,bool) or not isinstance(n,int) or n%2 or not 4<=n<=512:
        raise ValueError('LRS_GRID_DOMAIN')
    m,_=np.polynomial.legendre.leggauss(n);z=m*m
    return (math.log(2*z.min()/(1-z.min()))/6,
            math.log(2*z.max()/(1-z.max()))/6)
