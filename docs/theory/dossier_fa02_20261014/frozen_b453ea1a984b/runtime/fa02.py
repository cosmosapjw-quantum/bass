"""FA-02: total rapidity/pointing derivatives in a fixed physical observer cap.
Only new observer dependence is evaluated. Parent FA-01 data/closures are unchanged.
Jet coefficients are (value, d_chi, d_psi, d_chichi/2, d_chipsi, d_psipsi/2).
No finite differences are used to obtain the jet. Right generators use transpose:
coefficients are real for real parameters; this also defines the holomorphic extension.
"""
from __future__ import annotations
import argparse, json, math, time
from pathlib import Path
import numpy as np
from numpy.polynomial.legendre import leggauss

ROOT=Path(__file__).resolve().parents[1]
TERMS=((0,0),(1,0),(0,1),(2,0),(1,1),(0,2))
PAIRS=[[(i,j) for i,a in enumerate(TERMS) for j,b in enumerate(TERMS)
        if (a[0]+b[0],a[1]+b[1])==k] for k in TERMS]
P3=np.zeros((3,3),complex);P3[1:,1:]=[[.7,.1+.05j],[.1-.05j,.3]]
K3=np.diag([.4,.4,.8]);J2=np.array([[0.,-1.],[1.,0.]])
M3=1.0004;M4=1.000800032

class Jet:
    __array_priority__=1000
    def __init__(self,c): self.c=np.asarray(c)
    @classmethod
    def const(cls,x):
        x=np.asarray(x); c=np.zeros((6,)+x.shape,dtype=np.result_type(x,float)); c[0]=x
        return cls(c)
    @classmethod
    def variable(cls,x,axis):
        z=cls.const(x);z.c[1+axis]=1;return z
    @staticmethod
    def cast(x):return x if isinstance(x,Jet) else Jet.const(x)
    def __getitem__(self,key):
        if not isinstance(key,tuple):key=(key,)
        return Jet(self.c[(slice(None),)+key])
    def __add__(self,o):
        o=Jet.cast(o);n=max(self.c.ndim,o.c.ndim)
        a=self.c.reshape((6,)+(1,)*(n-self.c.ndim)+self.c.shape[1:])
        b=o.c.reshape((6,)+(1,)*(n-o.c.ndim)+o.c.shape[1:])
        return Jet(a+b)
    __radd__=__add__
    def __neg__(self):return Jet(-self.c)
    def __sub__(self,o):return self+-Jet.cast(o)
    def __rsub__(self,o):return Jet.cast(o)+-self
    def __mul__(self,o):
        o=Jet.cast(o)
        return Jet(np.stack([sum(self.c[i]*o.c[j] for i,j in pairs) for pairs in PAIRS]))
    __rmul__=__mul__
    def __matmul__(self,o):
        o=Jet.cast(o)
        return Jet(np.stack([sum(self.c[i]@o.c[j] for i,j in pairs) for pairs in PAIRS]))
    def __rmatmul__(self,o):return Jet.cast(o)@self
    def reciprocal(self):return compose(self,lambda x:1/x,lambda x:-1/x**2,lambda x:2/x**3)
    def __truediv__(self,o):return self*Jet.cast(o).reciprocal()
    def __rtruediv__(self,o):return Jet.cast(o)*self.reciprocal()
    def T(self):return Jet(self.c.swapaxes(-1,-2))

def compose(a,f,df,ddf):
    x=a.c[0];d=a-Jet.const(x)
    return Jet.const(f(x))+Jet.const(df(x))*d+.5*Jet.const(ddf(x))*d*d

def sqrt(x):
    if not isinstance(x,Jet):return np.sqrt(x)
    return compose(x,np.sqrt,lambda z:.5/np.sqrt(z),lambda z:-.25/z**1.5)
def sin(x):return compose(x,np.sin,np.cos,lambda z:-np.sin(z)) if isinstance(x,Jet) else np.sin(x)
def cos(x):return compose(x,np.cos,lambda z:-np.sin(z),lambda z:-np.cos(z)) if isinstance(x,Jet) else np.cos(x)
def sinh(x):return compose(x,np.sinh,np.cosh,np.sinh) if isinstance(x,Jet) else np.sinh(x)
def cosh(x):return compose(x,np.cosh,np.sinh,np.cosh) if isinstance(x,Jet) else np.cosh(x)
def stack(v,axis=-1):
    if any(isinstance(x,Jet) for x in v):return Jet(np.stack([Jet.cast(x).c for x in v],axis=axis))
    return np.stack(v,axis=axis)
def transpose(x):return x.T() if isinstance(x,Jet) else x.swapaxes(-1,-2)
def cross(a,b):return stack([a[...,1]*b[...,2]-a[...,2]*b[...,1],a[...,2]*b[...,0]-a[...,0]*b[...,2],a[...,0]*b[...,1]-a[...,1]*b[...,0]])

def cap_nodes(delta,nr=6,nphi=16):
    if not 0<delta<=.02:raise ValueError('0 < delta <= 0.02 required')
    t,w=leggauss(nr);r=2*np.arcsin(np.sqrt((t+1)/2)*np.sin(delta/2))
    phi=np.arange(nphi)*2*np.pi/nphi
    rr,pp=np.meshgrid(r,phi,indexing='ij')
    ell=np.stack([np.cos(rr),np.sin(rr)*np.cos(pp),np.sin(rr)*np.sin(pp)],axis=-1).reshape(-1,3)
    return ell,np.repeat(w/(2*nphi),nphi)

def setup(ell,chi,psi,jets=False,freeze_analyzer=False,freeze_energy=False):
    N=len(ell)
    if jets:
        chi=Jet.variable(np.full(N,chi),0);psi=Jet.variable(np.full(N,psi),1)
    co,si=cos(psi),sin(psi)
    m=stack([co*ell[:,0]-si*ell[:,1],si*ell[:,0]+co*ell[:,1],ell[:,2]+0*co])
    ch,sh=cosh(chi),sinh(chi)
    L=ch+sh*m[...,0]
    n=stack([(sh+ch*m[...,0])/L,m[...,1]/L,m[...,2]/L])
    dm=sqrt(1-m[...,1]*m[...,1])
    aw=stack([-m[...,0]*m[...,1]/dm,dm,-m[...,1]*m[...,2]/dm])
    bw=stack([-m[...,2]/dm,0*dm,m[...,0]/dm])
    A=stack([aw,bw],axis=-1)
    # inverse Lorentz boost followed by subtraction of time component times n
    Avec=stack([ch[...,None]*A[...,0,:],A[...,1,:],A[...,2,:]],axis=-2)
    At=Avec-(sh[...,None,None] if isinstance(sh,Jet) else np.asarray(sh)[...,None,None])*n[..., :,None]*A[...,0,None,:]
    # constant horizontal Sachs basis and exact parallel-transport coordinate map
    hh=sqrt(n[...,0]*n[...,0]+n[...,1]*n[...,1])
    kk=stack([-n[...,1]/hh,n[...,0]/hh,0*hh])
    B0=stack([kk,cross(n,kk)],axis=-1)
    C=transpose(B0)@At
    if jets and freeze_analyzer:C=Jet.const(C.c[0])
    if jets and freeze_energy:L=Jet.const(L.c[0])
    return n,kk,C,L,m,At

def coefficients(x,data):
    n,kk,C,L,_,_=data
    v=sqrt(1-(1-x*x)*n[...,2]*n[...,2]);q=x**(-2/3)*v
    e=stack([n[...,0]/v,n[...,1]/v,x*n[...,2]/v])
    B=stack([kk,cross(e,kk)],axis=-1)
    S=B@C
    Ps=transpose(S)@P3@S
    G=.5*(transpose(S)@K3@S)+.3*e[...,0,None,None]*J2
    weight=M3+.1*M4*L*q
    return weight[...,None,None]*Ps,G

def _rhs(x,F,data):
    B,G=coefficients(x,data)
    return B-G@F-F@transpose(G)

def solve_cap(chi,psi,delta=.02,nr=6,nphi=16,steps=256,jets=False,**kw):
    if abs(chi)>.02+1e-15 or abs(psi)>.02+1e-15:
        raise ValueError('real physical family |chi|,|psi| <=0.02')
    ell,w=cap_nodes(delta,nr,nphi);data=setup(ell,chi,psi,jets=jets,**kw)
    F=Jet.const(np.zeros((len(ell),2,2),complex)) if jets else np.zeros((len(ell),2,2),complex)
    h=.5/steps
    for k in range(steps):
        x=.5+k*h
        k1=_rhs(x,F,data);k2=_rhs(x+h/2,F+h*k1/2,data)
        k3=_rhs(x+h/2,F+h*k2/2,data);k4=_rhs(x+h,F+h*k3,data)
        F=F+h*(k1+2*k2+2*k3+k4)/6
    return np.einsum('n,knij->kij',w,F.c) if jets else np.einsum('n,nij->ij',w,F)

def stokes(F):
    return np.array([np.trace(F).real,(F[0,0]-F[1,1]).real,2*F[0,1].real,-2*F[0,1].imag])
def trnorm(F):return float(np.linalg.svd(F,compute_uv=False).sum())
def taylor(c,h):
    a,b=h;return c[0]+a*c[1]+b*c[2]+a*a*c[3]+a*b*c[4]+b*b*c[5]
def serialise(c):
    return {'base':stokes(c[0]).tolist(),'d_chi':stokes(c[1]).tolist(),'d_psi':stokes(c[2]).tolist(),
            'd_chichi':stokes(2*c[3]).tolist(),'d_chipsi':stokes(c[4]).tolist(),'d_psipsi':stokes(2*c[5]).tolist(),
            'coefficients_real':c.real.tolist(),'coefficients_imag':c.imag.tolist()}

def main():
    p=argparse.ArgumentParser();p.add_argument('--mode',choices=['jet0','jetoff','finite','controls'],default='jet0');p.add_argument('--steps',type=int,default=256);p.add_argument('--nr',type=int,default=6);p.add_argument('--nphi',type=int,default=16);a=p.parse_args()
    t=time.time();out=ROOT/'runtime';out.mkdir(exist_ok=True)
    if a.mode in ('jet0','jetoff'):
        base=[0.,0.] if a.mode=='jet0' else [.008,.01]
        c=solve_cap(*base,jets=True,steps=a.steps,nr=a.nr,nphi=a.nphi)
        r={'mode':a.mode,'parameters':base,'delta':.02,'steps':a.steps,'nr':a.nr,'nphi':a.nphi,**serialise(c)}
    elif a.mode=='finite':
        cfile=json.loads((out/'jetoff.json').read_text());c=np.array(cfile['coefficients_real'])+1j*np.array(cfile['coefficients_imag']);base=np.array(cfile['parameters']);r={'cases':[]}
        for h in [.008,.004,.002]:
            change=np.array([h,-h/2]);param=base+change
            F=solve_cap(*param,steps=a.steps,nr=a.nr,nphi=a.nphi);pred=taylor(c,change)
            first=c[0]+change[0]*c[1]+change[1]*c[2]
            r['cases'].append({'parameters':param.tolist(),'change':change.tolist(),'stokes':stokes(F).tolist(),'first_prediction':stokes(first).tolist(),'second_prediction':stokes(pred).tolist(),'first_remainder':trnorm(F-first),'second_remainder':trnorm(F-pred),'uniform_first_bound':125*max(abs(change))**2,'uniform_second_bound':1250*max(abs(change))**3})
    else:
        base=[.008,.01];c=solve_cap(*base,jets=True,steps=a.steps,nr=a.nr,nphi=a.nphi)
        bad=solve_cap(*base,jets=True,freeze_energy=True,steps=a.steps,nr=a.nr,nphi=a.nphi)
        r={'omitted_energy_dchi_error':trnorm(c[1]-bad[1])}
    r['elapsed_seconds']=time.time()-t;r['empirical_provider_error']=None
    name=a.mode+'.json';(out/name).write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
if __name__=='__main__':main()
