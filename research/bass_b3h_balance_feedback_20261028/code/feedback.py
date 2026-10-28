"""Exact-rational finite-time envelope for declared count-dependent feedback.

The theorem requires whole-domain source bounds. This module does not estimate
physical gains, reconstruct a native trajectory, or authenticate those bounds.
"""
from __future__ import annotations
from fractions import Fraction as F


def _q(x) -> F:
    if isinstance(x,(bool,float)) or x is None:
        raise ValueError('explicit finite rational required; unknown is not zero')
    try:return F(x)
    except (ValueError,TypeError,ZeroDivisionError,OverflowError) as exc:
        raise ValueError('explicit finite rational required') from exc


def _ceil(q: F) -> int:
    return -((-q.numerator)//q.denominator)


def exp_interval(x, bits: int=80) -> tuple[F,F]:
    """Outward dyadic enclosure of exp(x), 0<=x<=8, absolute width<=2^-bits.

    Positive Taylor tail, rational scaling, and integer outward squaring are
    the inclusion argument. The asserted width is a verified arithmetic bound.
    """
    x=_q(x)
    if not 0<=x<=8 or type(bits) is not int or not 16<=bits<=256:
        raise ValueError('requires 0<=x<=8 and integer precision16..256')
    if x==0:return F(1),F(1)
    y=x;s=0
    while y>F(1,8):y/=2;s+=1
    work=bits+32;scale=2**work
    term=total=F(1);n=0
    while True:
        omitted=term*y/(n+1)
        tail=omitted/(1-y/F(n+2))
        if tail<=F(1,2**(work+2*s)):
            break
        n+=1;term=omitted;total+=term
        if n>512:raise ArithmeticError('Taylor iteration ceiling reached')
    lower=(total*scale).numerator//(total*scale).denominator
    upper=_ceil((total+tail)*scale)
    for _ in range(s):
        lower=lower*lower//scale
        upper=(upper*upper+scale-1)//scale
    lo,hi=F(lower,scale),F(upper,scale)
    if hi-lo>F(1,2**bits):raise ArithmeticError('fixed enclosure width not met')
    return lo,hi


def threshold_bracket(margin, amplitude, bits: int=40) -> tuple[F,F]:
    """Enclose log(1+margin/amplitude) in [0,8] with width<=2^-bits.

    This is a sign-budget boundary, not a measured gain. Use its lower endpoint
    with a strict inequality for a conservative admission.
    """
    m,c=map(_q,(margin,amplitude))
    if m<0 or c<=0 or type(bits) is not int or not 16<=bits<=60:
        raise ValueError('nonnegative margin, positive amplitude, bits16..60')
    if m==0:return F(0),F(0)
    target=1+m/c;left=F(0);right=F(8)
    if exp_interval(right)[0]<=target:
        raise ValueError('threshold not strictly bracketed inside0..8')
    tolerance=F(1,2**bits)
    while right-left>tolerance:
        mid=(left+right)/2;lo,hi=exp_interval(mid)
        if hi<target:left=mid
        elif lo>target:right=mid
        else:
            # exp'(x)>=1 on the entire nonnegative search interval.
            left=max(left,mid-(hi-target))
            right=min(right,mid+(target-lo))
            if right-left>tolerance:
                raise ArithmeticError('fixed exponential precision insufficient')
    return left,right


def envelope(*,n0,G,Z,D,nominal,kA,kR,q_limit) -> dict:
    """Conditional gain/tube/sign result. Missing gains or tube give no interval.

    q_limit is a certified domain radius supplied by the caller, not inferred
    from this result. A failed tube check leaves the hypothesized interval in
    conditional_interval only, never in the admitted interval field.
    """
    n,g,z,d=map(_q,(n0,G,Z,D))
    if n<=0 or not 0<=g<=1 or z<0 or d<0:
        raise ValueError('n0>0,0<=G<=1,Z>=0,D>=0 required')
    if len(nominal)!=2:raise ValueError('two nominal endpoints required')
    lo,hi=map(_q,nominal)
    if lo>hi:raise ValueError('nominal endpoints must be ordered')
    if (d==0 or g*z==0) and (lo!=0 or hi!=0):
        raise ValueError('zero horizon/prefix amplitude needs exact zero nominal interval')
    missing=[name for name,x in [('kA',kA),('kR',kR),('q_limit',q_limit)] if x is None]
    if missing:return dict(status='INPUT_REQUIRED',missing=missing,admitted=False,interval=None,conditional_interval=None,radius=None,xi=None,q_upper=None)
    ka,kr,tube=map(_q,(kA,kR,q_limit))
    if ka<0 or kr<0 or tube<=0:raise ValueError('nonnegative gains and positive tube radius required')
    a=g*ka+kr;xi=a*d;el,eu=exp_interval(xi)
    b=g*z;radius=n*b*(eu-1);q_upper=b*eu
    interval=(lo-radius,hi+radius)
    valid_tube=q_upper<tube
    status=('TUBE_NOT_CERTIFIED' if not valid_tube else
            'NEGATIVE_CERTIFIED_CONDITIONAL' if interval[1]<0 else 'SIGN_UNRESOLVED')
    return dict(status=status,admitted=valid_tube and interval[1]<0,
                interval=interval if valid_tube else None,
                conditional_interval=interval,radius=radius,xi=xi,
                exp_interval=(el,eu),B=b,a=a,q_upper=q_upper,
                tube_strictly_certified=valid_tube,physical_gain_inferred=False)
