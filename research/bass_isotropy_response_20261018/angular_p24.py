"""Positive source-frame P2/P4 information projection, fixed support.

Only a newly born, declared locally isotropic source may use these weights.
The original P2-only implementation and all spectral/transport owners are separate.
See S3_THEORY_KO.md for exact feasibility and the nested scalar dual proof.
"""
from __future__ import annotations
from dataclasses import dataclass
import math
import numpy as np

ALGORITHM_ID = 'BASS_LRS_SOURCE_KL_P24_V1'
DEFAULT_ATOL = 3e-15
FEASIBILITY_ROUNDOFF_GUARD = 64 * np.finfo(float).eps


@dataclass(frozen=True)
class Feasibility:
    status: str
    distinct_z: int
    z_min: float
    z_max: float
    lower: float
    upper: float
    lower_slack: float
    upper_slack: float


@dataclass(frozen=True)
class Result:
    weights: np.ndarray
    multipliers: np.ndarray
    residuals: np.ndarray
    iterations: int
    evaluations: int
    before: np.ndarray
    kl: float
    feasibility: Feasibility


def legendre24(mu):
    z = np.asarray(mu, dtype=float)**2
    return (3*z-1)/2, (35*z*z-30*z+3)/8


def feasibility(mu) -> Feasibility:
    """Float diagnostic with an explicit uncertain band, not a proof by tolerance.

Exact full-positive rank-one supports exist. An almost-consistent f64 rank-one
input requires an exact support certificate and is returned UNRESOLVED here.
Boundary cases never pass via dropping rays or adjusting a target moment.
"""
    m = np.asarray(mu, dtype=float)
    if m.ndim != 1 or len(m) < 2 or not np.isfinite(m).all() or np.any(abs(m)>1):
        raise ValueError('ANGULAR_INPUT_DOMAIN')
    z = np.unique(m*m)
    t, v, guard = 1/3, 1/5, FEASIBILITY_ROUNDOFF_GUARD
    low, high = float(z[0]), float(z[-1])
    upper = (low+high)*t-low*high
    if len(z) >= 2:
        lower = max(float((a+b)*t-a*b) for a,b in zip(z[:-1],z[1:]))
    else:
        lower = float(z[0]**2)
    ls, us = v-lower, upper-v
    if len(z) == 1:
        status = 'INFEASIBLE_P24_SINGLE_Z'
    elif t < low-guard or t > high+guard:
        status = 'INFEASIBLE_P24_MEAN'
    elif t <= low+guard or t >= high-guard:
        status = 'FEASIBILITY_UNRESOLVED_NEAR_BOUNDARY'
    elif len(z) == 2:
        status = ('INFEASIBLE_P24_RANK1' if abs(upper-v)>guard
                  else 'FEASIBILITY_UNRESOLVED_RANK1')
    elif ls < -guard:
        status = 'INFEASIBLE_P24_LOWER'
    elif us < -guard:
        status = 'INFEASIBLE_P24_UPPER'
    elif ls <= guard or us <= guard:
        status = 'FEASIBILITY_UNRESOLVED_NEAR_BOUNDARY'
    else:
        status = 'STRICT_INTERIOR'
    return Feasibility(status,len(z),low,high,lower,upper,ls,us)


def project(mu, prior, *, atol=DEFAULT_ATOL) -> Result:
    """Nested monotone dual solves, with positivity checked on the final result.

At fixed lambda4 the inner root sets M2=0. Along that root, dM4/dlambda4
is the positive covariance Schur complement on full-dimensional supports.
The output tolerance is a dimensionless moment tolerance; no continuum bound.
"""
    m=np.asarray(mu,dtype=float);q=np.asarray(prior,dtype=float)
    if (m.ndim!=1 or q.shape!=m.shape or not 2<=m.size<=4096 or
        not np.isfinite(m).all() or not np.isfinite(q).all() or
        np.any(abs(m)>1) or np.any(q<=0) or np.any(np.diff(m)<=0)):
        raise ValueError('ANGULAR_INPUT_DOMAIN')
    if not math.isfinite(atol) or not 1e-16<=atol<=DEFAULT_ATOL:
        raise ValueError('ANGULAR_TOLERANCE_DOMAIN')
    q=q/q.max();q=q/math.fsum(q)
    if np.any(q<=0):
        raise ArithmeticError('NUMERIC_POSITIVE_SUPPORT_LOSS')
    if np.max(abs(m+m[::-1]))>5e-14 or np.max(abs(q-q[::-1]))>5e-14:
        raise ValueError('REFLECTION_SOURCE_REQUIRED')
    feasible=feasibility(m)
    if feasible.status.startswith('INFEASIBLE'):
        raise ValueError(feasible.status)
    if feasible.status!='STRICT_INTERIOR':
        raise ArithmeticError(feasible.status)
    p2,p4=legendre24(m);logq=np.log(q)
    before=np.array([math.fsum(q*p2),math.fsum(q*p4)])
    evaluations=0

    def evaluate(l2,l4):
        nonlocal evaluations
        evaluations+=1
        logs=logq+l2*p2+l4*p4
        if not np.isfinite(logs).all():
            raise ArithmeticError('NUMERIC_DUAL_RANGE')
        logs-=logs.max();weights=np.exp(logs);weights/=math.fsum(weights)
        return weights,np.array([math.fsum(weights*p2),math.fsum(weights*p4)])

    def inner(l4):
        w,res=evaluate(0.,l4)
        inner_tol=atol/8
        if abs(res[0])<=inner_tol:
            return w,res,0.
        lo,hi=-1.,1.
        for _ in range(60):
            if evaluate(lo,l4)[1][0]<=0:break
            lo*=2
        else:raise ArithmeticError('P2_LOWER_BRACKET')
        for _ in range(60):
            if evaluate(hi,l4)[1][0]>=0:break
            hi*=2
        else:raise ArithmeticError('P2_UPPER_BRACKET')
        for _ in range(200):
            mid=lo+(hi-lo)/2;w,res=evaluate(mid,l4)
            if abs(res[0])<=inner_tol:return w,res,mid
            if mid==lo or mid==hi:
                raise ArithmeticError('P2_INNER_RESOLUTION')
            if res[0]<0:lo=mid
            else:hi=mid
        raise ArithmeticError('P2_INNER_NOT_CONVERGED')

    def finish(w,res,l2,l4,n):
        if not np.isfinite(w).all() or np.any(w<=0):
            raise ArithmeticError('NUMERIC_POSITIVE_SUPPORT_LOSS')
        if max(abs(res))>atol or abs(math.fsum(w)-1)>5e-16:
            raise ArithmeticError('MOMENT_TOLERANCE')
        if np.max(abs(w-w[::-1]))>5e-14:
            raise ArithmeticError('REFLECTION_RESULT')
        return Result(w,np.array([l2,l4]),res,n,evaluations,before,
                      math.fsum(w*(np.log(w)-logq)),feasible)

    if max(abs(before))<=atol:
        return finish(q.copy(),before,0.,0.,0)
    w,res,l2=inner(0.)
    if abs(res[1])<=atol:return finish(w,res,l2,0.,0)
    lo,hi=-1.,1.
    for _ in range(60):
        if inner(lo)[1][1]<=0:break
        lo*=2
    else:raise ArithmeticError('P4_LOWER_BRACKET')
    for _ in range(60):
        if inner(hi)[1][1]>=0:break
        hi*=2
    else:raise ArithmeticError('P4_UPPER_BRACKET')
    for k in range(1,201):
        mid=lo+(hi-lo)/2;w,res,l2=inner(mid)
        if abs(res[1])<=atol:return finish(w,res,l2,mid,k)
        if mid==lo or mid==hi:raise ArithmeticError('P4_OUTER_RESOLUTION')
        if res[1]<0:lo=mid
        else:hi=mid
    raise ArithmeticError('P4_OUTER_NOT_CONVERGED')


def balance(mu,prior,*,atol=DEFAULT_ATOL):
    return project(mu,prior,atol=atol).weights
