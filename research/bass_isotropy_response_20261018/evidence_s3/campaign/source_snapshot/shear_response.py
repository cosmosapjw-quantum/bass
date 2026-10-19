"""Exact fixed-birth collisionless kernels in non-tilted LRS Bianchi I.

All inputs/outputs here are dimensionless. mu is the birth source-frame angle,
d=b(x)-b(u). The caller holds positive birth weights fixed during propagation.
"""
from __future__ import annotations
import math
import numpy as np


def kernels(d,mu):
    if not math.isfinite(d) or abs(d)>4:
        raise ValueError('RESEARCH_KERNEL_DOMAIN')
    mu=np.asarray(mu,dtype=float)
    if not np.isfinite(mu).all() or np.any(abs(mu)>1):
        raise ValueError('RESEARCH_ANGLE_DOMAIN')
    z=mu*mu;perp=math.exp(2*d)*(1-z);para=math.exp(-4*d)*z
    r=np.sqrt(perp+para);D=(para-perp/2)/r
    return r,D


def response(d,mu,weights):
    m=np.asarray(mu,dtype=float);w=np.asarray(weights,dtype=float)
    if (m.ndim!=1 or w.shape!=m.shape or not np.isfinite(w).all() or
        np.any(w<=0) or abs(math.fsum(w)-1)>3e-15):
        raise ValueError('RESEARCH_WEIGHT_DOMAIN')
    R,D=kernels(d,m)
    f,g=math.fsum(w*R),math.fsum(w*D)
    return {'F':f,'G':g,'A':g/f}


def moments(mu,weights):
    m=np.asarray(mu,dtype=float);w=np.asarray(weights,dtype=float)
    return {ell:math.fsum(w*np.polynomial.legendre.legval(m,[0]*ell+[1]))
            for ell in [2,4,6,8]}


def derivative_diagnostics(mu,weights):
    M=moments(mu,weights);m2,m4,m6=M[2],M[4],M[6]
    g1=-8/5-10/7*m2+36/35*m4
    g2=16/7+12/7*m2-216/77*m4+216/77*m6
    # F(0)=1, F'=-2G. A=G/F has a different denominator from G.
    return {'moments':M,'G_prime':g1,'G_second':g2,
            'A_prime':g1+2*m2*m2,
            'A_second':g2+6*m2*g1+8*m2**3}
