"""Exact norms between two explicitly represented piecewise-linear curves.

The coordinate knots are Fractions. A native adapter may lift binary64 ln(a)
knots exactly, but that is a named representation distinct from PL in a.
No source-pair admission, true-ODE error estimate, solver or DAG mutation occurs.
Reuse the owner's pair-bound source relation check before calling this module.
"""
from __future__ import annotations
from fractions import Fraction as Q
from bisect import bisect_left

def validate(curve):
    x,y=curve
    if len(x)<2 or len(x)!=len(y):raise ValueError('matching arrays with at least two nodes required')
    if any(not isinstance(t,Q) for t in (*x,*y)):raise TypeError('exact Fraction knots and values required')
    if any(v<=u for u,v in zip(x,x[1:])):raise ValueError('strictly increasing coordinate required')

def evaluate(curve,t):
    x,y=curve
    if t<x[0] or t>x[-1]:raise ValueError('no extrapolation')
    i=bisect_left(x,t)
    if x[i]==t:return y[i]
    s=(t-x[i-1])/(x[i]-x[i-1]);return (1-s)*y[i-1]+s*y[i]

def compare(a,b,*,coordinate_a='LN_A_BINARY64',coordinate_b='LN_A_BINARY64'):
    if coordinate_a!=coordinate_b:raise ValueError('interpolation coordinates differ')
    if coordinate_a not in ('LN_A_BINARY64','A_BINARY64','TIME_S_BINARY64','MANUFACTURED_EXACT'):
        raise ValueError('unknown declared coordinate')
    validate(a);validate(b)
    lo=max(a[0][0],b[0][0]);hi=min(a[0][-1],b[0][-1])
    if lo>=hi:raise ValueError('positive-length common interval required')
    # Each curve is ordered, so the merged knot set is O(n+m) before exact evaluations.
    knots=[];i=j=0;xa,xb=a[0],b[0]
    while i<len(xa) or j<len(xb):
        if j==len(xb) or i<len(xa) and xa[i]<=xb[j]:t=xa[i];i+=1
        else:t=xb[j];j+=1
        if lo<=t<=hi and (not knots or t!=knots[-1]):knots.append(t)
    if knots[0]!=lo:knots.insert(0,lo)
    if knots[-1]!=hi:knots.append(hi)
    d=[evaluate(a,t)-evaluate(b,t) for t in knots]
    peak=max(range(len(d)),key=lambda i:abs(d[i]));l1=Q(0);l2=Q(0)
    for i,h in enumerate(v-u for u,v in zip(knots,knots[1:])):
        u,v=d[i],d[i+1];l2+=h*(u*u+u*v+v*v)/3
        if u*v<0:l1+=h*(u*u+v*v)/(2*(abs(u)+abs(v)))
        else:l1+=h*(abs(u)+abs(v))/2
    return {'coordinate':coordinate_a,'interval':(lo,hi),'knot_count':len(knots),
            'sup_abs':abs(d[peak]),'peak_coordinate':knots[peak],'signed_at_peak':d[peak],
            'integral_abs':l1,'integral_squared':l2,
            'true_ode_error_bound':None,'scope':'exact norm of declared PL references only'}

def difference_supremum(a,b):return compare(a,b)['sup_abs']

def true_difference_ceiling(reference_sup,error_a,error_b):
    """Only for externally established uniform errors in the same coordinate."""
    if any(v is not None and v<0 for v in (reference_sup,error_a,error_b)):raise ValueError('negative bound')
    return None if error_a is None or error_b is None else reference_sup+error_a+error_b

def encode(x):
    if isinstance(x,Q):return {'num':x.numerator,'den':x.denominator,'approx':float(x)}
    if isinstance(x,dict):return {k:encode(v) for k,v in x.items()}
    if isinstance(x,(tuple,list)):return [encode(v) for v in x]
    return x
