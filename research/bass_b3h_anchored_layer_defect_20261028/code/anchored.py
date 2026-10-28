"""Anchor-specific bounds for the same saved frozen-layer reconstruction.

Only first_rate evaluates a new elementary-function expression. It uses the
unchanged outward-dyadic dependency; no stationary solve or ODE is called.
"""
from __future__ import annotations
import math
from fractions import Fraction as F
from itertools import product
from enclosure import I


def source_number(value) -> F:
    """Preserve JSON binary64 values versus exact written decimal strings."""
    if isinstance(value,bool) or value is None:
        raise ValueError('numeric source literal required')
    if isinstance(value,float):
        if not math.isfinite(value):raise ValueError('finite binary64 required')
        return F.from_float(value)
    try:return F(value)
    except (ValueError,TypeError,ZeroDivisionError) as exc:
        raise ValueError('finite numeric source literal required') from exc


def _exact(x) -> F:
    if isinstance(x,(bool,float)):raise ValueError('explicit rational required')
    try:return F(x)
    except (ValueError,TypeError,ZeroDivisionError) as exc:raise ValueError('rational required') from exc


def _matrix(x):
    if len(x)!=2 or any(len(row)!=2 for row in x):raise ValueError('2x2 matrix required')
    return [[_exact(v) for v in row] for row in x]


def anchored_gap(A0,A1,B,theta,rate,margin=0) -> F:
    """Maximum induced one-norm on a containing anchor rectangle, plus margin.

    Convexity proves enclosure of the entire rectangle. The caller must supply
    intervals for the same source, anchor and clock as B, not nearby samples.
    """
    a0,a1,bb=map(_matrix,(A0,A1,B));th=tuple(map(_exact,theta));rr=tuple(map(_exact,rate));m=_exact(margin)
    if len(th)!=2 or len(rr)!=2 or not 0<=th[0]<=th[1]<=1 or not 0<=rr[0]<=rr[1] or m<0:
        raise ValueError('ordered physical anchor rectangle and nonnegative margin required')
    norms=[]
    for t,r in product(th,rr):
        E=[[a0[i][j]+t*(a1[i][j]-a0[i][j])+(r if i==j==1 else 0)-bb[i][j] for j in range(2)] for i in range(2)]
        norms.append(max(sum(abs(E[i][j]) for i in range(2)) for j in range(2)))
    return max(norms)+m


def layer_mass(Z,beta,duration,alpha,L,C) -> F:
    """Conditional joint L1 mass; temporal variation is never silently dropped."""
    z,b,d,a,l,c=map(_exact,(Z,beta,duration,alpha,L,C))
    if min(z,d,a,l,c)<0 or b<=0:raise ValueError('positive decay and nonnegative bounds required')
    phi=min(d,1/b);psi=min(d*d/2,1/(b*b))
    return z*min(c*phi,a*phi+l*psi)


def replace_layer(count,old_layer,K,new_masses) -> F:
    """Replace one additive ledger port, preserving its unchanged complement."""
    total,old,k=map(_exact,(count,old_layer,K));masses=list(map(_exact,new_masses))
    if min([total,old,k,*masses])<0 or old>total:raise ValueError('nonnegative consistent ledger required')
    new=k*sum(masses,F(0))
    if new>old:raise ValueError('this tightening interface refuses a wider layer bound')
    return total-old+new


def first_rate(source:dict,bits:int) -> I:
    """Enclose R(u=0) for the source-literal flat background; no QSS solve.

    Density conversion 1e6 and the frozen common-volume g0 convention are part
    of the pinned source law, not new universal atomic constants.
    """
    clock=source['clock'];nh=source_number(clock['NH_reference']);g=source_number(clock['g0'])
    if nh<=0 or g<=0:raise ValueError('positive reference density and ground fraction required')
    co=source['cosmology']; cv=lambda key:I.point(source_number(co[key]),bits)
    eta=I.point(source_number(clock['eta0']),bits)
    rad=cv('photon_omega_prefactor')*cv('T0_K')**4*(1+cv('neutrino_factor')*cv('Nnueff'))
    H=cv('H_prefactor_s_inv')*(cv('omh2')*(-3*eta).exp()+cv('odeh2')+rad*(-4*eta).exp()).sqrt()
    return cv('LYA_FACT_cm3_inv')/(I.point(nh,bits)/10**6)*H/I.point(g,bits)
