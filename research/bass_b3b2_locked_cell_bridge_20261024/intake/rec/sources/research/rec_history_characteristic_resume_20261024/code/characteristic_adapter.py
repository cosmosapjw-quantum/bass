"""REC-HISTORY-02R constant-shear positive-rate characteristic leaf.

eta=ln(a), normal propagation n=p/|p|, ten coefficient angular field.
No trajectory solver; preserved HISTORY01 owns interpolation and local ledger.
"""
from __future__ import annotations
import math
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'vendor'))
import history_boundary as HB
EPS=np.finfo(float).eps


def finite(*v):
    if not all(np.all(np.isfinite(np.asarray(x,dtype=float))) for x in v):
        raise ValueError('NONFINITE_INPUT')


def vector(v,name):
    a=np.asarray(v,dtype=float)
    if a.shape!=(3,):raise ValueError(name+'_SHAPE')
    finite(a)
    return a


def geometry(n,b):
    n=vector(n,'DIRECTION');b=vector(b,'SHEAR')
    norm=math.hypot(*n)
    if abs(norm-1)>64*EPS:raise ValueError('DIRECTION_UNIT')
    if abs(float(sum(b)))>64*EPS*max(1,float(np.abs(b).sum())):raise ValueError('SHEAR_TRACE')
    a=1+b
    if min(a)<=0:raise ValueError('NONPOSITIVE_RATE')
    return n/norm,b,a


def lognorm(n,a,delta):
    finite(delta)
    logs=np.full(3,-math.inf)
    nz=n!=0
    logs[nz]=np.log(np.abs(n[nz]))+a[nz]*delta
    finite(logs[nz])
    shift=float(max(logs));weights=np.exp(logs-shift)
    norm=math.hypot(*weights)
    lnD=shift+math.log(norm)
    ns=np.sign(n)*weights/norm
    q=float(np.dot(a,ns*ns))
    finite(lnD,ns,q)
    return lnD,ns,q


def crossing(n,b,lam,eta_t=0.0):
    n,b,a=geometry(n,b);finite(lam,eta_t)
    if lam<0:raise ValueError('NEGATIVE_LOGRATIO')
    lo=lam/float(max(a));hi=lam/float(min(a));finite(lo,hi)
    nonzero=np.flatnonzero(n)
    if lam==0:delta=0.0;kind='lambda0'
    elif len(nonzero)==1:delta=lam/float(a[nonzero[0]]);kind='axis'
    elif np.all(a==1):delta=float(lam);kind='FLRW'
    else:
        delta=.5*lo+.5*hi;kind='bracketed_Newton_bisection'
        for iteration in range(256):
            value,ns,q=lognorm(n,a,delta);f=value-lam
            if f>0:hi=delta
            elif f<0:lo=delta
            else:break
            proposal=delta-f/q
            if not lo<proposal<hi:proposal=.5*lo+.5*hi
            if proposal==delta or hi-lo<=4*EPS*max(1,abs(delta)):
                delta=min([lo,delta,hi],key=lambda x:abs(lognorm(n,a,x)[0]-lam));break
            delta=proposal
        else:raise ValueError('ROOT_NOT_CONVERGED')
    lnD,ns,qs=lognorm(n,a,delta);eta_s=eta_t-delta;finite(eta_s)
    return dict(delta=float(delta),eta_s=float(eta_s),ns=ns,n=n,b=b,a=a,lnD=lnD,qs=qs,qt=float(np.dot(a,n*n)),residual=lnD-lam,lam=float(lam),root_kind=kind,bracket=[lam/float(max(a)),lam/float(min(a))])


def crossing_jvp(r,dn=(0,0,0),db=(0,0,0),dlam=0.,deta_t=0.):
    dn=vector(dn,'DIRECTION_TANGENT');db=vector(db,'SHEAR_TANGENT');finite(dlam,deta_t)
    if abs(float(np.dot(r['n'],dn)))>64*EPS*max(1,float(np.linalg.norm(dn))):raise ValueError('NONTANGENT_DIRECTION')
    if abs(float(sum(db)))>64*EPS*max(1,float(np.abs(db).sum())):raise ValueError('SHEAR_TANGENT_TRACE')
    # Nonzero tangent components can be unrepresentable even when n_i=0.
    term=np.zeros(3)
    for i in range(3):
        if dn[i]!=0:
            exponent=r['a'][i]*r['delta']-r['lnD']+math.log(abs(dn[i]))
            if exponent>math.log(np.finfo(float).max):raise ValueError('TANGENT_TRANSFORM_OVERFLOW')
            term[i]=math.copysign(math.exp(exponent),dn[i])
    dd=(dlam-float(np.dot(r['ns'],term))-r['delta']*float(np.dot(r['ns']**2,db)))/r['qs']
    v=term+r['ns']*(r['delta']*db+r['a']*dd)
    dns=v-r['ns']*float(np.dot(r['ns'],v))
    dqt=float(np.dot(r['n']**2,db)+2*np.dot(r['a']*r['n'],dn))
    deta_s=deta_t-dd
    finite(dd,dns,dqt,deta_s)
    return dict(ddelta=dd,deta_s=deta_s,dns=dns,dqt=dqt)


def wien_x(logx):
    if logx==-math.inf:return 0.0,1.0,0.0
    if not math.isfinite(logx):raise ValueError('NONFINITE_LOGX')
    if logx>math.log(np.finfo(float).max):return math.inf,0.,0.
    x=math.exp(logx)
    w=math.exp(-x)
    xw=math.exp(logx-x) if x else 0.
    return x,w,xw


def reference(xt,lam,delta,dlnxt=0.,dlam=0.,ddelta=0.):
    finite(xt,lam,delta,dlnxt,dlam,ddelta)
    if xt<0:raise ValueError('NEGATIVE_X')
    logxt=math.log(xt) if xt else -math.inf
    logxs=logxt+lam-delta if xt else -math.inf
    xs,ws,xws=wien_x(logxs);_,wt,xwt=wien_x(logxt)
    if xt==0 or lam==delta:offset=0.
    elif math.isinf(xs):offset=-wt
    else:
        # Difference of x values uses expm1 before exponential subtraction.
        shift=lam-delta
        dx=xt*math.expm1(shift) if abs(shift)<.5 else xs-xt
        if dx>=0:offset=wt*math.expm1(-dx)
        else:offset=-ws*math.expm1(dx)
    doffset=xwt*dlnxt-xws*(dlnxt+dlam-ddelta)
    finite(offset,doffset)
    return dict(xs=xs,logxs=logxs,ws=ws,wt=wt,offset=offset,doffset=doffset)


def strict_interpolation(eta0,h,values,iz,eta,deta=0.):
    finite(eta0,h,eta,deta)
    if not isinstance(iz,(int,np.integer)) or isinstance(iz,(bool,np.bool_)) or h<=0:raise ValueError('HISTORY_CLOCK_OR_INDEX')
    if eta<eta0 or iz<2 or eta>=eta0+h*(iz-1):raise ValueError('HISTORY_RETAINED_DOMAIN')
    st=HB.interpolation(eta0,h,values,iz,eta)
    if st['at_knot'] and deta!=0:raise ValueError('NONSMOOTH_QUERY')
    return st


def coeff_parts(c):
    c=np.asarray(c,dtype=float)
    if c.shape!=(10,):raise ValueError('COEFFICIENT_SHAPE')
    finite(c)
    Q=np.diag(c[4:7]);Q[0,1]=Q[1,0]=c[7];Q[0,2]=Q[2,0]=c[8];Q[1,2]=Q[2,1]=c[9]
    return c[0],c[1:4],Q


def angular(c,n):
    c0,v,Q=coeff_parts(c)
    return float(c0+v@n+n@Q@n),v+2*Q@n


def history_field(eta0,h,coeff,iz,eta,n,dcoeff=None,deta=0.,dn=(0,0,0)):
    coeff=np.asarray(coeff,dtype=float);finite(coeff)
    if coeff.ndim!=2 or coeff.shape[0]!=10 or coeff.shape[1]<iz:raise ValueError('COEFFICIENT_HISTORY_SHAPE')
    if dcoeff is None:dcoeff=np.zeros_like(coeff)
    dcoeff=np.asarray(dcoeff,dtype=float);finite(dcoeff)
    if dcoeff.shape!=coeff.shape:raise ValueError('COEFFICIENT_TANGENT_SHAPE')
    dn=vector(dn,'SOURCE_DIRECTION_TANGENT');n=vector(n,'SOURCE_DIRECTION')
    sts=[strict_interpolation(eta0,h,row,iz,eta,deta) for row in coeff]
    c=np.array([st['value'] for st in sts]);dc=np.array([HB.interpolation_jvp(st,dy,deta) for st,dy in zip(sts,dcoeff)])
    value,grad=angular(c,n);data_time,_=angular(dc,n)
    return dict(value=value,jvp=data_time+float(grad@dn),k=sts[0]['k'],alpha=sts[0]['alpha'])


def compose(n,b,lam,eta_t,xt,eta0,h,coeff,iz,*,xr_p,x1s,tau,nH_cm3,H_t,dn=(0,0,0),db=(0,0,0),dlam=0.,deta_t=0.,dlnxt=0.,dcoeff=None,dxr_p=0.,dx1s=0.,dtau=0.):
    r=crossing(n,b,lam,eta_t);j=crossing_jvp(r,dn,db,dlam,deta_t);ref=reference(xt,lam,r['delta'],dlnxt,dlam,j['ddelta'])
    field=history_field(eta0,h,coeff,iz,r['eta_s'],r['ns'],dcoeff,j['deta_s'],j['dns'])
    din=field['value']+ref['offset'];ddin=field['jvp']+ref['doffset']
    if field['value']+ref['ws']<0:raise ValueError('NEGATIVE_ABSOLUTE_OCCUPATION')
    out=HB.boundary(din,xr_p,x1s,tau,r['qt'],ref['wt'])
    dout=HB.boundary_jvp(din,xr_p,x1s,tau,r['qt'],ddin,dxr_p,dx1s,dtau,j['dqt'],ref['wt'])
    ledger=HB.line_ledger(din,xr_p,x1s,tau,nH_cm3,H_t,r['qt'],reference_occupation=ref['wt'])
    return dict(crossing=r,tangent=j,reference=ref,field=field,din=din,ddin=ddin,outgoing=out['outgoing'],dout=dout,boundary=out,ledger=ledger,absolute_in=field['value']+ref['ws'])


def error_envelope(*,e_H,K_eta,K_n,eps_F,e_arithmetic,a_min,a_max,qt,tau,H_t):
    if any(x is None for x in [e_H,K_eta,K_n,eps_F,e_arithmetic]):raise ValueError('MISSING_ERROR_INPUT')
    finite(e_H,K_eta,K_n,eps_F,e_arithmetic,a_min,a_max,qt,tau,H_t)
    if min(e_H,K_eta,K_n,eps_F,e_arithmetic)<0 or a_min<=0 or a_max<a_min or qt<=0 or tau<0 or H_t<=0:raise ValueError('ERROR_BOUND_DOMAIN')
    ed=eps_F/a_min;ein=e_H+(K_eta+K_n*(a_max-a_min)/2+1/math.e)*ed+e_arithmetic
    T=math.exp(-tau/qt);A=-math.expm1(-tau/qt);en=HB.G_NATIVE*H_t*qt*A*ein
    finite(ed,ein,en)
    return dict(e_delta=ed,e_in=ein,e_out=T*ein,e_number=en,e_energy=HB.E21*HB.EV_J*en,status='CONDITIONAL_SUPPLIED_TUBE_BOUNDS')
