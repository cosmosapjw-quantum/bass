"""Separate Decimal/owner-lift reference, no production tau_row imports.

Reads immutable source-model inventory and reproduces original full62 electron
formula before compact/reduced projection. This is not independent-author review.
"""
from decimal import Decimal, localcontext
from pathlib import Path
import hashlib, json, math

P=Path(__file__).resolve().parents[1]
Q21=(0,0,1,0,1,0,1,0,1,2,0,1,2,0,1,2,3,0,1,2,3)
GROUPS={'n':(0,), 'H1':(1,2),'D':(3,4),'T':(5,6),'He3':(7,8,9),'He4':(10,11,12),'Li6':(13,14,15,16),'Li7':(17,18,19,20)}
A=(1,1,1,2,2,3,3,3,3,3,4,4,4,6,6,6,6,7,7,7,7)


def f(x):
    from fractions import Fraction
    if isinstance(x,float):return Decimal.from_float(x)
    q=Fraction(x);return Decimal(q.numerator)/Decimal(q.denominator)


def owner_scales():
    b=(P/'input/atomic_model.json').read_bytes()
    if hashlib.sha256(b).hexdigest()!='9cc399e9e33ece544109f442f50b00c463cde96e406965e796240eaabd49c614':
        raise ValueError('owner model byte mismatch')
    model=json.loads(b)
    r=model['inventory_number_ratios_to_H1']
    s=math.fsum(A[idx[0]]*r[name] for name,idx in GROUPS.items())
    return {name:r[name]/s for name in GROUPS}


def source_full_electrons(z,nb):
    """Independent full21 representation with nine source representative fractions."""
    with localcontext() as ctx:
        ctx.prec=85
        scales=owner_scales();v=[f(x) for x in z];nb=f(nb)
        if len(v)!=6:raise ValueError('six charged')
        h=[f(1)-v[0],v[0]]
        he=[f(1)-v[1]-v[2],v[1],v[2]]
        li=[f(1)-v[3]-v[4]-v[5],v[3],v[4],v[5]]
        arr={ 'n':[f(0)],'H1':h,'D':h,'T':[f(0),f(0)],'He3':he,'He4':he,'Li6':li,'Li7':li }
        # 21 full atomic coordinate values have the same representative fractions on each isotope.
        ne=f(0)
        for name,idx in GROUPS.items():
            for q,pos in zip((Q21[i] for i in idx),arr[name]):
                ne+=f(scales[name])*f(q)*pos
        return nb*ne


def full_projected_row(z,fields,nb,K):
    """Compute full62 analytic tau Jacobian and manually reduce by exact lift."""
    with localcontext() as ctx:
        ctx.prec=85
        H=f(fields['H']);K=f(K);nb=f(nb)
        ne=source_full_electrons(z,nb)
        h0=f(fields['h0']);href=f(fields['href']);aa=f(fields['a'])
        gp={1:-3*h0*h0*f(fields['Pi_m_norm'])/H/H,
            2:href*href*f(fields['y2'])/H/H,
            4:h0*h0*f(fields['omega_gamma'])/(2*H*H*aa**4),
            22:h0*h0*f(fields['omega_nu'])/(2*H*H*aa**4)}
        compact_geom=(0,1,2,4,6,8,10,12,13,15,17,19,21,22,24,26,28,30,31,33,35,37,39)
        out=[f(0)]*30
        for native,val in gp.items():out[compact_geom.index(native)]=-K*ne/H*val
        s=owner_scales()
        grp=(f(s['H1'])+f(s['D']),f(s['He3'])+f(s['He4']),f(s['Li6'])+f(s['Li7']))
        weights=(grp[0],grp[1],2*grp[1],grp[2],2*grp[2],3*grp[2])
        for j,w in enumerate(weights):out[23+j]=K*nb/H*f(w)
        return out


def direct_local_fd(z,fields,nb,K,j,step):
    """Independent source-consistent local H² affine/quadratic geometry fixture.

    This is a local tangent diagnostic, not the actual full geometry RHS.
    """
    with localcontext() as ctx:
        ctx.prec=85
        H=f(fields['H']);h0=f(fields['h0']);hr=f(fields['href']);aa=f(fields['a']);hh=f(step)
        def opt(delta):
            if j==1: hh2=H*H-6*h0*h0*f(fields['Pi_m_norm'])*delta
            elif j==2: hh2=H*H+hr*hr*(2*f(fields['y2'])*delta+delta*delta)
            elif j==3: hh2=H*H+h0*h0*f(fields['omega_gamma'])*delta/aa**4
            elif j==13: hh2=H*H+h0*h0*f(fields['omega_nu'])*delta/aa**4
            else:raise ValueError('geo column required')
            return f(K)*source_full_electrons(z,nb)/hh2.sqrt()
        return (opt(hh)-opt(-hh))/(2*hh)
