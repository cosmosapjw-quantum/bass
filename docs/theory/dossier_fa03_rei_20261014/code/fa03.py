"""FA03: exact finite band-moment derivatives at a grey base point.

The six states are S0,S1,S2,V0,V1,W0. Vj is the epsilon derivative,
W0 the second epsilon derivative, not the Taylor coefficient W0/2.
Physical absorption alone is scaled by 1+epsilon*(local_energy/E_star-1).
The independent energy-resolved solver is provided only as a bounded check.
"""
from __future__ import annotations
import sys
from pathlib import Path
from fractions import Fraction
import numpy as np
from numpy.polynomial.legendre import leggauss
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'reference'))
import fa02 as p

def moment(j: int) -> float:
    """Exact-rational moment rounded once to binary64."""
    if not isinstance(j,int) or j < 0: raise ValueError('nonnegative integer moment')
    lo,hi=Fraction(49,50),Fraction(51,50)
    return float((hi**(j+1)-lo**(j+1))/((j+1)*(hi-lo)))

def fields(x, data):
    n,kk,C,L,_,_=data
    v=p.sqrt(1-(1-x*x)*n[...,2]*n[...,2])
    q=x**(-2/3)*v
    ray=p.stack([n[...,0]/v,n[...,1]/v,x*n[...,2]/v])
    screen=p.stack([kk,p.cross(ray,kk)],axis=-1)@C
    P=p.transpose(screen)@p.P3@screen
    H=.5*(p.transpose(screen)@p.K3@screen)
    G=H+.3*ray[...,0,None,None]*p.J2
    return P,H,G,L*q

def _anti(H,F): return H@F+F@p.transpose(H)

def _rhs(x,Y,data):
    P,H,G,k=fields(x,data)
    GT=p.transpose(G)
    r=[-G@f-f@GT for f in Y]
    for j in range(3):
        r[j]=r[j]+(moment(j+3)+.1*moment(j+4)*k)[...,None,None]*P
    r[3]=r[3]-_anti(H,k[...,None,None]*Y[1]-Y[0])
    r[4]=r[4]-_anti(H,k[...,None,None]*Y[2]-Y[1])
    r[5]=r[5]-2*_anti(H,k[...,None,None]*Y[4]-Y[3])
    return r

def _validate(chi,psi,steps,nr,nphi):
    if not np.isfinite([chi,psi]).all() or max(abs(chi),abs(psi))>.02:
        raise ValueError('real family |chi|,|psi| <= .02')
    if any(not isinstance(v,int) or v<1 for v in (steps,nr,nphi)):
        raise ValueError('positive integer resolution required')

def solve_moments(chi,psi,*,steps=64,nr=3,nphi=12,jets=False):
    """Return six cap-averaged matrices, or their six observer-jet coefficients.

    With jets=True shape is (state, jet, 2, 2); observer coefficient order
    is value, chi, psi, chi^2, chi*psi, psi^2. Ordinary second derivatives
    require factors 2 on the two diagonal quadratic coefficients.
    """
    _validate(chi,psi,steps,nr,nphi)
    ell,w=p.cap_nodes(.02,nr,nphi)
    data=p.setup(ell,chi,psi,jets=jets)
    zero=np.zeros((len(ell),2,2),complex)
    Y=[p.Jet.const(zero.copy()) if jets else zero.copy() for _ in range(6)]
    h=.5/steps
    plus=lambda a,b,s:[f+s*g for f,g in zip(a,b)]
    for j in range(steps):
        x=.5+j*h
        k1=_rhs(x,Y,data)
        k2=_rhs(x+h/2,plus(Y,k1,h/2),data)
        k3=_rhs(x+h/2,plus(Y,k2,h/2),data)
        k4=_rhs(x+h,plus(Y,k3,h),data)
        Y=[f+h*(a+2*b+2*c+d)/6 for f,a,b,c,d in zip(Y,k1,k2,k3,k4)]
    if jets:return np.stack([np.einsum('n,knij->kij',w,y.c) for y in Y])
    return np.stack([np.einsum('n,nij->ij',w,y) for y in Y])

def solve_energy(chi,psi,epsilon,*,steps=64,nr=3,nphi=12,ne=8):
    """Independent finite-epsilon energy quadrature (not a finite-epsilon closure)."""
    _validate(chi,psi,steps,nr,nphi)
    if not np.isfinite(epsilon) or abs(epsilon)>.1:
        raise ValueError('|epsilon|<=.1')
    if not isinstance(ne,int) or ne<1:raise ValueError('positive energy order')
    ell,w=p.cap_nodes(.02,nr,nphi);data=p.setup(ell,chi,psi)
    en,we=leggauss(ne);en=1+.02*en;we=we/2
    F=np.zeros((len(ell),ne,2,2),complex)
    def rhs(x,F):
        P,H,G,k=fields(x,data)
        B=(en[None,:]**3*(1+.1*en[None,:]*k[:,None]))[...,None,None]*P[:,None]
        Ge=G[:,None]+epsilon*(en[None,:]*k[:,None]-1)[...,None,None]*H[:,None]
        return B-Ge@F-F@Ge.swapaxes(-1,-2)
    h=.5/steps
    for j in range(steps):
        x=.5+j*h
        a=rhs(x,F);b=rhs(x+h/2,F+h*a/2)
        c=rhs(x+h/2,F+h*b/2);d=rhs(x+h,F+h*c)
        F=F+h*(a+2*b+2*c+d)/6
    return np.einsum('n,e,neij->ij',w,we,F)

def full_quadratic(states,dx):
    """Total second-order polynomial about (chi0,psi0,epsilon=0)."""
    a,b,e=dx
    return (p.taylor(states[0],[a,b])+e*(states[3,0]+a*states[3,1]+b*states[3,2])
            +.5*e*e*states[5,0])
