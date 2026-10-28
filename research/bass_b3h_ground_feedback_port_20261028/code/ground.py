"""Exact arithmetic for a declared isolated ground-denominator feedback port.

The source adapter must verify all whole-interval reference conditions. This is
not a full atomic-conservation closure or an empirical physical error estimate.
"""
from fractions import Fraction as F


def rational(value):
    if isinstance(value,(float,bool)) or value is None:
        raise ValueError('explicit rational required')
    try:return F(value)
    except (TypeError,ValueError,ZeroDivisionError,OverflowError) as exc:
        raise ValueError('finite rational required') from exc


def port(C,g,q,phat2,f):
    """Vary loss and incoming consistently; q can have either sign here."""
    c,g,q,p,f=map(rational,(C,g,q,phat2,f))
    if c<0 or g<=0 or g+q<=0 or p<0 or f<0:
        raise ValueError('positive ground denominator and nonnegative source required')
    rb=c/g;rh=c/(g+q)
    return dict(R=rb,Rhat=rh,incoming=3*c*f,s=(rh-rb)*p)


def envelope(*,n0,Rhi,gamma,gmin,Pbound,X,p_initial,nominal,D,reference_valid):
    """Return one-sided bounds for the explicitly supplied selected model.

    reference_valid records a separately checked b>=0, cooperative A with
    nonnegative column sums, and a valid nominal contraction/output certificate.
    A boolean cannot authenticate these mathematical input obligations.
    """
    supplied=locals().copy()
    missing=[k for k,v in supplied.items() if v is None]
    if missing:return dict(status='INPUT_REQUIRED',missing=missing,interval=None,physical_admitted=False)
    if reference_valid is not True:raise ValueError('verified reference conditions required')
    n,R,ga,g,P,d=map(rational,(n0,Rhi,gamma,gmin,Pbound,D))
    if n<=0 or R<0 or ga<=0 or g<=0 or P<0 or d<0 or R>ga:
        raise ValueError('nonnegative bounds, positive domain and Rhi/gamma<=1 required')
    if len(X)!=2 or any(len(row)!=2 for row in X) or len(p_initial)!=2 or len(nominal)!=2:
        raise ValueError('two state components and ordered intervals required')
    X=[tuple(map(rational,row)) for row in X];p=list(map(rational,p_initial));lo,hi=map(rational,nominal)
    if any(a>b or b>0 for a,b in X) or any(v<0 for v in p) or any(p[i]+X[i][0]<0 for i in range(2)):
        raise ValueError('nonpositive reset and nonnegative compared initial state required')
    if sum(p)>P:raise ValueError('Pbound must bound the initial one-norm')
    if lo>hi or hi>0:raise ValueError('ordered nonpositive nominal count interval required')
    Z=sum(-a for a,b in X)
    if Z>=g:raise ValueError('strict initial mass-deficit ground gap required')
    G=R/ga;B=G*Z
    if (d==0 or B==0) and (lo!=0 or hi!=0):
        raise ValueError('zero duration or zero nominal response requires zero nominal interval')
    k=R*P/(g-B);E=n*k*B*d
    interval=(lo,min(F(0),hi+E))
    status='NEGATIVE_CONDITIONAL_GROUND_PORT' if interval[1]<0 else 'NONPOSITIVE_CONDITIONAL_GROUND_PORT'
    return dict(status=status,interval=interval,Z=Z,G=G,B=B,kR=k,kA=F(0),
                added_upper=E,ground_gap_initial=g-Z,ground_gap_refined=g-B,
                rate_ratio_upper=g/(g-B),relative_ground_change_upper=B/g,
                loop_exposure=k*d,denominator_nonexit=True,physical_admitted=False)
