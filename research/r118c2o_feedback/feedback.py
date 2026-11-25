"""Weak homogeneous Einstein--Thomson response. No feedback of O(s20^2) monopoles."""
import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import PchipInterpolator
H0=67.4e3/3.0856775814913673e22
C=299792458.;G=6.67430e-11;SIG=6.6524587051e-29
OM=.315;OR=9.2e-5;OL=1-OM-OR
OG0=8*np.pi*G*(7.5657e-16*2.7255**4)/(3*C*C*H0**2)
ON0=OR-OG0;A0=1/21
def coefficients(a):
    r=OR/a**4;m=OM/a**3;v=r+m+OL
    return H0*np.sqrt(v),OG0/a**4/v,ON0/a**4/v,-(4*r+3*m)/(2*v)
def mat(a,k,mode):
    _,og,on,d=coefficients(a)
    if mode not in ('all','photon','tracer'):raise ValueError('mode')
    return np.array([[-(3+d),.4*og if mode!='tracer' else 0.,0.,.4*on if mode=='all' else 0.],
                     [-4.,-.9*k,-.4*k,0.],[0.,-.15*k,-.4*k,0.],[-4.,0.,0.,0.]])
def lyapunov(a,v,mode):
    _,og,on,_=coefficients(a);s,x,b,n=v
    return 10*s*s/og+x*x+(8/3)*b*b+(on/og*n*n if mode=='all' else 0.)
def loss(a,k,v,mode):
    _,og,_,_=coefficients(a);s,x,b,n=v
    return 20*s*s/og+k*(1.8*x*x+1.6*x*b+32/15*b*b)
def integrate(u,k,mode,rtol=2e-11):
    interp=PchipInterpolator(u,k,extrapolate=False)
    def fun(t,y):
        a=A0*np.exp(t);rate=float(interp(t));assert rate>=-1e-14
        return np.r_[mat(a,max(0.,rate),mode)@y[:4],loss(a,max(0.,rate),y[:4],mode)]
    sol=solve_ivp(fun,(u[0],u[-1]),[1.,0.,0.,0.,0.],rtol=rtol,atol=rtol/100,method='DOP853',max_step=.002,dense_output=True)
    assert sol.success
    ts=np.linspace(u[0],u[-1],4097);v=sol.sol(ts);L=np.array([lyapunov(A0*np.exp(t),y[:4],mode) for t,y in zip(ts,v.T)])
    balance=abs(L[-1]+v[-1,-1]-L[0])/L[0] if mode!='tracer' else None
    inc=float(np.max(np.diff(L))/L[0]) if mode!='tracer' else None
    if mode!='tracer':assert balance<2e-8 and inc<2e-11
    return dict(end=sol.y[:4,-1].tolist(),nfev=sol.nfev,lyapunov_initial=float(L[0]),lyapunov_final=float(L[-1]),integrated_loss=float(v[-1,-1]),lyapunov_relative_balance=balance,lyapunov_max_increment=inc,series=np.vstack((ts,v[:4],L)))
def midpoint(u,k,mode,n):
    kf=PchipInterpolator(u,k);v=np.array([1.,0.,0.,0.]);dt=(u[-1]-u[0])/n;eye=np.eye(4)
    for t in u[0]+(np.arange(n)+.5)*dt:
        a=A0*np.exp(t);M=mat(a,float(kf(t)),mode)
        v=np.linalg.solve(eye-dt*M/2,(eye+dt*M/2)@v)
    return v
