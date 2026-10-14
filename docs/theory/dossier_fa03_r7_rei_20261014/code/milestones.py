"""Exact-rational first-passage diagnostics for continuous piecewise-linear references.

An optional radius must bound the entire continuous curve, not just saved nodes.
The module neither establishes that premise nor promotes scientific admission.
Coordinate values are increasing elapsed proper time or a declared increasing
expansion coordinate; temperature must not be sorted into an evolution clock.
"""
from __future__ import annotations
from fractions import Fraction
from numbers import Real
from typing import Sequence
import math

Number = int | float | str | Fraction

def rational(x: Number) -> Fraction:
    if isinstance(x,bool):raise ValueError('boolean is not a physical scalar')
    if isinstance(x,float):
        if not math.isfinite(x):raise ValueError('nonfinite scalar')
        return Fraction.from_float(x)
    return Fraction(x)

def _inputs(coordinate: Sequence[Number], values: Sequence[Number]):
    if len(coordinate)!=len(values) or len(coordinate)==0:raise ValueError('equal nonempty vectors required')
    t=[rational(x) for x in coordinate];y=[rational(x) for x in values]
    if any(t[i]>=t[i+1] for i in range(len(t)-1)):raise ValueError('strictly increasing coordinate required')
    return t,y

def first_ge(coordinate: Sequence[Number], values: Sequence[Number], target: Number) -> dict:
    """First hit of {y >= target} in the represented interval; no extrapolation."""
    t,y=_inputs(coordinate,values);c=rational(target)
    if y[0]>=c:
        return {'coordinate':t[0],'left':0,'right':0,'theta':Fraction(0),
                'kind':'INITIAL_EXACT' if y[0]==c else 'INITIAL_ABOVE','prehistory':'UNKNOWN'}
    for i in range(len(t)-1):
        if y[i]<c<=y[i+1]:
            theta=(c-y[i])/(y[i+1]-y[i])
            return {'coordinate':t[i]+theta*(t[i+1]-t[i]),'left':i,'right':i+1,'theta':theta,'kind':'UPWARD_BRACKET'}
    return {'coordinate':None,'left':None,'right':None,'theta':None,'kind':'NOT_REACHED'}

def first_passage_band(coordinate: Sequence[Number], values: Sequence[Number], target: Number,
                       radius: Number | Sequence[Number] | None=None, *,
                       envelope_kind: str | None=None, bound_authority: str | None=None) -> dict:
    """Enclose the first hit conditional on a supplied continuous error envelope.

    Radius vector defines a nonnegative PL envelope on this coordinate. Uniform
    scalar radius is also supported. For every point, not merely nodes, the
    caller must establish |y_true-y_reference| <= radius. Upper/lower envelope
    first hits give lower/upper first-passage bounds without a derivative lower
    bound or a monotonicity assumption on either curve.
    """
    t,y=_inputs(coordinate,values);c=rational(target);ref=first_ge(t,y,c)
    out={'reference':ref,'lower':None,'upper':None,'event_guaranteed':None,
         'bound_authority':bound_authority,'scientific_admission':'NOT_ISSUED',
         'scope':'conditional on supplied whole-interval continuous error envelope'}
    if radius is None:
        return dict(out,status='REFERENCE_ONLY_ERROR_UNKNOWN')
    if envelope_kind!='CONTINUOUS_ERROR_ENVELOPE' or not isinstance(bound_authority,str) or not bound_authority.strip():
        raise ValueError('node-only errors or unbound radii cannot bound first passage')
    if isinstance(radius,(str,int,float,Fraction)):
        d=[rational(radius)]*len(t)
    else:
        if len(radius)!=len(t):raise ValueError('radius length mismatch')
        d=[rational(v) for v in radius]
    if min(d)<0:raise ValueError('negative error radius')
    possible=first_ge(t,[a+b for a,b in zip(y,d)],c)
    guaranteed=first_ge(t,[a-b for a,b in zip(y,d)],c)
    out.update(lower=possible['coordinate'],upper=guaranteed['coordinate'],
               possible_first=possible,guaranteed_first=guaranteed,
               event_guaranteed=guaranteed['coordinate'] is not None)
    if possible['coordinate'] is None:
        out['status']='NO_HIT_IN_REPRESENTED_INTERVAL_UNDER_ENVELOPE'
    elif guaranteed['coordinate'] is None:
        out['status']='POSSIBLE_HIT_NO_FINITE_UPPER_BOUND'
    else:
        if possible['coordinate']>guaranteed['coordinate']:raise AssertionError('envelope order violated')
        out['status']='CONDITIONAL_FIRST_PASSAGE_BRACKET'
    return out

def encode_result(value):
    """Lossless JSON representation, keeping short floats as display only."""
    if isinstance(value,Fraction):return {'numerator':str(value.numerator),'denominator':str(value.denominator),'display':float(value)}
    if isinstance(value,dict):return {k:encode_result(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [encode_result(v) for v in value]
    return value
