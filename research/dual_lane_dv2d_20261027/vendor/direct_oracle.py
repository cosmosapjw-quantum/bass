"""Independent Cartesian-tensor differentiation using byte-matched P8 transport.

Differentiates the Wigner finite-sum basis and Cartesian screen tensors,
then subtracts n-advection from the physical Lagrangian P8 RHS. Does not use
Wigner3j/Gaunt, the spectral coupling coefficient, or harmonic_streaming.
"""
from __future__ import annotations
from math import factorial,pi,sqrt
from pathlib import Path
import sys
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'vendor'))
import polarization as P8
from polarized_dictionary import Grid,analyze


def y_derivatives(g,s,l,m):
    q=-s;ch=np.cos(g.theta/2);sh=np.sin(g.theta/2)
    pref=sqrt(factorial(l+q)*factorial(l-q)*factorial(l+m)*factorial(l-m))
    value=np.zeros_like(ch);dt=value.copy()
    for k in range(max(0,q-m),min(l+q,l-m)+1):
        den=factorial(l+q-k)*factorial(k)*factorial(m-q+k)*factorial(l-m-k)
        coef=(-1)**(m-q+k)*pref/den;a=2*l+q-m-2*k;b=m-q+2*k
        value+=coef*ch**a*sh**b
        if a:dt-=coef*a/2*ch**(a-1)*sh**(b+1)
        if b:dt+=coef*b/2*ch**(a+1)*sh**(b-1)
    phase=(-1)**s*sqrt((2*l+1)/(4*pi))*np.exp(1j*m*g.phi)
    return phase*value,phase*dt,1j*m*phase*value


def z_derivatives(g,s,l,m):
    if m==0:return y_derivatives(g,s,l,0)
    a=abs(m);pos=y_derivatives(g,s,l,a);neg=y_derivatives(g,s,l,-a)
    if m>0:return tuple(((-1)**a*x+y)/sqrt(2) for x,y in zip(pos,neg))
    return tuple(((-1)**a*x-y)/(1j*sqrt(2)) for x,y in zip(pos,neg))


def components(g,c):
    out={f:[np.zeros(len(g.w),complex) for _ in range(3)] for f in ('I','P','V')}
    for (f,l,m),a in c.items():
        target=f if f in ('I','V') else 'P';s=0 if target!='P' else 2
        ds=z_derivatives(g,s,l,m);a=a*(1j if f=='B' else 1)
        for i in range(3):out[target][i]+=a*ds[i]
    return out


def _outer(a,b):return np.einsum('ni,nj->nij',a,b)


def carrier_with_derivatives(g,c):
    comp=components(g,c);n,t,p=g.n,g.bt,g.bp
    sn,cn=np.sin(g.theta),np.cos(g.theta)
    basis=[g.P,_outer(t,t)-_outer(p,p),_outer(t,p)+_outer(p,t),_outer(p,t)-_outer(t,p)]
    td=-n;pd=np.zeros_like(n)
    tf=cn[:,None]*p;pf=-sn[:,None]*n-cn[:,None]*t
    def change(dn,dt,dp):
        return [-_outer(dn,n)-_outer(n,dn),
                _outer(dt,t)+_outer(t,dt)-_outer(dp,p)-_outer(p,dp),
                _outer(dt,p)+_outer(t,dp)+_outer(dp,t)+_outer(p,dt),
                _outer(dp,t)+_outer(p,dt)-_outer(dt,p)-_outer(t,dp)]
    dbt=change(t,td,pd);dbp=change(sn[:,None]*p,tf,pf)
    vals=[[comp['I'][k].real,comp['P'][k].real,comp['P'][k].imag,comp['V'][k].real] for k in range(3)]
    J=sum(a[:,None,None]*b for a,b in zip(vals[0],basis))/2
    Jt=sum(a[:,None,None]*b+v[:,None,None]*db for a,v,b,db in zip(vals[1],vals[0],basis,dbt))/2
    Jp=sum(a[:,None,None]*b+v[:,None,None]*db for a,v,b,db in zip(vals[2],vals[0],basis,dbp))/2
    return J,Jt,Jp


def direct_rhs(g,c,H,S,nu=0.):
    J,Jt,Jp=carrier_with_derivatives(g,c);S=np.asarray(S,float)
    # Directions computed from pinned P8 connection, not the harmonic shear formula.
    zero=np.zeros(3);Z=np.zeros((3,3));V=P8.direction_rate(g.n,H,S,zero,Z,zero)
    vt=np.einsum('ni,ni->n',V,g.bt);vp=np.einsum('ni,ni->n',V,g.bp)/np.sin(g.theta)
    sig=np.einsum('ni,ij,nj->n',g.n,S,g.n)
    out=-4*(H+sig)[:,None,None]*J+P8.tensor_rate(J,g.n,H,S,zero,Z,zero)-vt[:,None,None]*Jt-vp[:,None,None]*Jp
    if nu:
        M=np.einsum('n,nij->ij',g.w,J)
        gain=3/(8*pi)*np.einsum('nia,ab,nbj->nij',g.P,M,g.P)
        out+=nu*(gain-J)
    return out


def projected_rhs(g,c,H,S,nu=0.,lout=6):return analyze(g,direct_rhs(g,c,H,S,nu),lout)


def spin_coordinate_rhs(g,c,H,S,connection=True):
    comp=components(g,c);s=np.einsum('ni,ij,nj->n',g.n,S,g.n)
    V=-g.n@np.asarray(S).T+s[:,None]*g.n
    vt=np.einsum('ni,ni->n',V,g.bt);vp=np.einsum('ni,ni->n',V,g.bp)/np.sin(g.theta)
    out={}
    for f,spin in [('I',0),('V',0),('P',2)]:
        x,dt,dp=comp[f]
        out[f]=-4*(H+s)*x-vt*dt-vp*dp
        if connection:out[f]-=1j*spin*np.cos(g.theta)*vp*x
    return out
