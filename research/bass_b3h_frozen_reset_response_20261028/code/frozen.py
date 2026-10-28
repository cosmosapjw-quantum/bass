"""Exact-rational frozen-response enclosure for a declared positive linear law.

Inputs are conditional bounds, not measured physical uncertainties. No ODE or
stationary-population solver is called. The finite terminal tail is retained.
"""
from __future__ import annotations
from fractions import Fraction as F
import math


def source_number(value) -> F:
    """Interpret JSON floats as exact binary64 and strings as written rationals."""
    if isinstance(value,bool) or value is None:
        raise ValueError('finite source number required')
    if isinstance(value,float):
        if not math.isfinite(value):raise ValueError('finite binary64 required')
        return F.from_float(value)
    try:return F(value)
    except (TypeError,ValueError,ZeroDivisionError) as exc:
        raise ValueError('finite source number required') from exc


def _q(value) -> F:
    if isinstance(value,(float,bool)) or value is None:
        raise ValueError('explicit rational required')
    return source_number(value)


def _matrix(B):
    if len(B)!=2 or any(len(row)!=2 for row in B):raise ValueError('2x2 B required')
    B=[[ _q(v) for v in row] for row in B]
    a,b=B[0];c,d=B[1]
    beta=min(a+c,b+d)
    if a<=0 or d<=0 or b>0 or c>0 or beta<=0:
        raise ValueError('positive column gap and nonpositive offdiagonals required')
    if a*d-b*c<=0:raise ValueError('nonsingular inverse-positive B required')
    return B,beta


def response_row(B,n0,Rb):
    """Return n0*Rb*e2^T B^-1 exactly, not a stationary population."""
    B,_=_matrix(B);n,r=map(_q,(n0,Rb))
    if n<0 or r<0:raise ValueError('nonnegative density and frozen rate required')
    a,b=B[0];c,d=B[1];det=a*d-b*c
    return [-n*r*c/det,n*r*a/det]


def _box(X):
    if len(X)!=2 or any(len(row)!=2 for row in X):raise ValueError('two ordered intervals required')
    X=[tuple(map(_q,row)) for row in X]
    if any(lo>hi for lo,hi in X):raise ValueError('ordered initial box required')
    return X


def box_linear(w,X):
    """Exact image of an independent component box under a linear functional."""
    if len(w)!=2:raise ValueError('two response entries required')
    w=list(map(_q,w));X=_box(X)
    terms=[(min(a*lo,a*hi),max(a*lo,a*hi)) for a,(lo,hi) in zip(w,X)]
    return tuple(sum(v[i] for v in terms) for i in range(2))


def assemble(*,B,n0,Rb,X,Dlo,Dhi,K,Rhi,alphaA,LA,alphaR,LR):
    """Enclose the same-law finite-horizon output using supplied whole-time bounds.

    Requires the proven adjoint bound 0<=h_i<=K<=n0. The caller, not this
    arithmetic routine, supplies source/clock/derivative validity.
    """
    B,beta=_matrix(B);X=_box(X)
    n,r,dl,dh,k,rhi,aa,la,ar,lr=map(_q,(n0,Rb,Dlo,Dhi,K,Rhi,alphaA,LA,alphaR,LR))
    if min(n,r,dl,dh,k,rhi,aa,la,ar,lr)<0 or dl>dh or k>n:
        raise ValueError('ordered nonnegative bounds and K<=n0 required')
    w=response_row(B,n,r);center=box_linear(w,X)
    Z=sum(max(abs(lo),abs(hi)) for lo,hi in X)
    phi=min(dh,1/beta);psi=min(dh*dh/2,1/(beta*beta))
    tail_factor=(1+beta*dl/8)**(-8)
    ea=Z*k*(aa*phi+la*psi)
    er=Z*n*(ar*phi+lr*psi)
    tail=max(w)*Z*tail_factor
    radius=ea+er+tail
    raw=(center[0]-radius,center[1]+radius)
    gross=n*rhi*dh*Z
    lo=max(raw[0],-gross);hi=min(raw[1],gross)
    if all(a>=0 for a,b in X):lo=max(lo,F(0))
    if all(b<=0 for a,b in X):hi=min(hi,F(0))
    if lo>hi:raise ValueError('inconsistent output enclosures')
    return dict(w=w,beta=beta,Z=Z,phi=phi,psi=psi,tail_factor=tail_factor,
                variation_A=ea,variation_R=er,variation=ea+er,tail=tail,
                radius=radius,center_box=center,raw_interval=raw,
                interval=(lo,hi),gross_bound=gross)
