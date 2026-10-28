"""Exact-rational finite-horizon bounds for the declared two-state rate box.

These are same-law output bounds, not a physical-input uncertainty certificate.
All rates are inverse seconds, duration seconds, and N count per reference volume.
"""
from fractions import Fraction as F


def rational(value):
    """Retain explicit real-number meaning; do not silently decimalize floats."""
    if isinstance(value,bool) or not isinstance(value,(int,str,F)):
        raise ValueError('supply integers, rational/decimal strings, or Fraction')
    try:
        return F(value)
    except (ValueError,ZeroDivisionError) as exc:
        raise ValueError('finite rational value required') from exc


def witnesses(endpoints,N,rmin,rmax):
    """Return greatest lower v, least upper w, and a uniform column-sum gap."""
    N,rmin,rmax=map(rational,(N,rmin,rmax))
    if N<0 or rmin<0 or rmax<rmin:
        raise ValueError('nonnegative density and ordered rates required')
    if len(endpoints)!=2 or any(len(A)!=2 or any(len(row)!=2 for row in A) for A in endpoints):
        raise ValueError('two 2x2 non-Lyalpha endpoint matrices required')
    coeff=[]
    for A in endpoints:
        a,b,c,d=(rational(A[0][0]),-rational(A[0][1]),-rational(A[1][0]),rational(A[1][1]))
        if a<=0 or d<=0 or b<0 or c<0:
            raise ValueError('positive diagonal and nonpositive off-diagonal required')
        coeff.append((a,b,c,d))
    km=min(c/a for a,b,c,d in coeff);kp=max(c/a for a,b,c,d in coeff)
    sp=max(d-b*km for a,b,c,d in coeff);sm=min(d-b*kp for a,b,c,d in coeff)
    gamma=min(min(a-c,d-b+rmin) for a,b,c,d in coeff)
    if min(sp,sm,gamma)<=0:
        raise ValueError('positive storage denominators and contraction gap required')
    v2=N*rmin/(sp+rmin);w2=N*rmax/(sm+rmax)
    return (km*v2,v2),(kp*w2,w2),gamma


def response_box(endpoints,N,rmin,rmax,duration,tail_order=8):
    """Bound each integrated response coefficient, retaining terminal storage."""
    D=rational(duration)
    if D<0 or type(tail_order) is not int or tail_order<1:
        raise ValueError('nonnegative duration and positive integer tail order required')
    v,w,gamma=witnesses(endpoints,N,rmin,rmax)
    B=(1+gamma*D/tail_order)**(-tail_order)
    lower=tuple(max(F(0),vi-max(v)*B) for vi in v)
    upper=tuple(min(wi,rational(N)*rational(rmax)*D) for wi in w)
    return lower,upper,B


def signed_box(lower,upper,initial):
    """Enclose the signed bilinear output over two componentwise input boxes."""
    if len(lower)!=2 or len(upper)!=2 or len(initial)!=2 or any(len(x)!=2 for x in initial):
        raise ValueError('two response and initial-state components required')
    lo=hi=F(0)
    for L,U,box in zip(lower,upper,initial):
        L,U,a,b=map(rational,(L,U,*box))
        if L<0 or U<L or b<a:
            raise ValueError('ordered nonnegative response and ordered initial boxes required')
        products=(L*a,L*b,U*a,U*b)
        lo+=min(products);hi+=max(products)
    return lo,hi
