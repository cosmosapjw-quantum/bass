"""Collisionless massive homogeneous LRS susceptibility and Einstein--Thomson ODE."""
import numpy as np
from functools import lru_cache
from numpy.polynomial.legendre import leggauss
from scipy.integrate import solve_ivp
from scipy.interpolate import PchipInterpolator
H0=67.4e3/3.0856775814913673e22
C=299792458.;G=6.67430e-11;SIG=6.6524587051e-29
OM=.315;OR=9.2e-5;OL=1-OM-OR
OG0=8*np.pi*G*(7.5657e-16*2.7255**4)/(3*C*C*H0**2)
ON0=OR-OG0;A0=1/21
TNU_EV=8.617333262145e-5*2.7255*(4/11)**(1/3)
@lru_cache(None)
def gl(n):
    x,w=leggauss(n);return x,w
class Species:
    def __init__(self,m,n):
        assert np.isfinite(m) and m>=0
        self.m=m
        x,w=gl(n);self.y=(x+1)*30;self.w=w*30/(np.exp(self.y)+1)
        self.norm=ON0/(self.w@self.y**3)
    def moments(self,a):
        y=self.y;x=a*self.m/TNU_EV;e=np.sqrt(y*y+x*x);v2=(y/e)**2
        den=self.norm*(self.w@(y*y*e))
        p=self.norm/3*(self.w@(y**4/e))
        chi=self.norm*2/15*(self.w@(y**4/e*(5-v2)))
        dchi=-self.norm*2/15*(self.w@(x*x*y**4/e**3*(5-3*v2)))
        # All four values are comoving a^4 densities in present critical-density units.
        return den,p,chi,dchi
def exact_stress(s,a,b):
    y=s.y[:,None];mu,w=gl(48);mu=mu[None,:]
    pz2=y*y*mu*mu*np.exp(-2*b);pt2=y*y*(1-mu*mu)*np.exp(b)
    e=np.sqrt(pz2+pt2+(a*s.m/TNU_EV)**2)
    return s.norm*(s.w@((y*y*(pz2-(pz2+pt2)/3)/e)@(w/2)))
class Background:
    h0=H0
    def __init__(self,m,n=128):
        self.s=Species(m,n);self.om=OM+ON0-self.s.moments(1.)[0];assert self.om>0
    def coeff(self,a):
        den,p,chi,dchi=self.s.moments(a)
        r=(OG0+den)/a**4;mat=self.om/a**3;total=r+mat+OL
        d=-(4*OG0/a**4+3*(den+p)/a**4+3*mat)/(2*total)
        return H0*np.sqrt(total),OG0/a**4/total,chi/a**4/total,d,dchi/OG0
def matrix(bg,a,k,mode):
    _,og,oc,d,_=bg.coeff(a)
    if mode not in ('all','photon','tracer'):raise ValueError('mode')
    return np.array([[-(3+d),.4*og if mode!='tracer' else 0.,0.,-3*oc if mode=='all' else 0.],
                     [-4.,-.9*k,-.4*k,0.],[0.,-.15*k,-.4*k,0.],[1.,0.,0.,0.]])
def energy(bg,a,v,mode):
    _,og,oc,_,_=bg.coeff(a);s,A,B,b=v
    return 10*s*s/og+A*A+8/3*B*B+(30*oc/og*b*b if mode=='all' else 0.)
def loss(bg,a,k,v,mode):
    _,og,_,_,dchi=bg.coeff(a);s,A,B,b=v
    return 20*s*s/og+k*(1.8*A*A+1.6*A*B+32/15*B*B)-(30*dchi*b*b if mode=='all' else 0.)
def solve(bg,u,ne,mode,rtol=2e-10,method='DOP853'):
    nf=PchipInterpolator(u,ne,extrapolate=False)
    def fun(t,y):
        a=A0*np.exp(t);k=C*SIG*float(nf(t))/bg.coeff(a)[0]
        assert k>=0
        return np.r_[matrix(bg,a,k,mode)@y[:4],loss(bg,a,k,y[:4],mode)]
    sol=solve_ivp(fun,(u[0],u[-1]),[1.,0.,0.,0.,0.],method=method,rtol=rtol,atol=rtol/100,max_step=.004,dense_output=True)
    assert sol.success,sol.message
    t=np.linspace(u[0],u[-1],2049);v=sol.sol(t)
    ll=np.array([energy(bg,A0*np.exp(x),y[:4],mode) for x,y in zip(t,v.T)])
    bal=abs(ll[-1]+v[-1,-1]-ll[0])/ll[0] if mode!='tracer' else None
    inc=float(np.max(np.diff(ll))/ll[0]) if mode!='tracer' else None
    if mode!='tracer':assert bal<3e-8 and inc<1e-11
    return dict(end=sol.y[:4,-1].tolist(),balance=bal,max_inc=inc,nfev=sol.nfev,L0=float(ll[0]),Lf=float(ll[-1]),series=np.vstack((t,v[:4],ll)))
