"""Independent source-only oracle for pinned REI PR150 SourceLedger.

No opacity or chemistry. x=ln(a/a_ref), b anisotropy, s signed shear [s^-1].
N, U are photons/H and eV/H; proper density uses n_H0/a^3 exactly once.
This predicts the native discrete operator, NOT its continuum accuracy.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from functools import lru_cache
from pathlib import Path
import hashlib, math, sys
import numpy as np
from numpy.polynomial.legendre import leggauss
sys.path.insert(0,str(Path(__file__).resolve().parent/'reference'))
from pr171 import native_emission_rate, SOURCE_ID, _X8, _W8
AREF=1/21
XMAX=math.log(21/5)
KT=(1.380649e-16/1.602176634e-12)*50000
EDGES=(13.6,24.59,54.42,100.)
REI_SHA='0e25846433170d0f420c4cda44a0bedbf02cd177'
PINS={'axbi_sources.rs':'606e3c2ec367dd9951ebbf2f53486f2232b49c0218896d66d8dc13dd5ee83bfe',
      'axbi_covariant_transport.rs':'9d2d97881ca7b9b58d68dbeffad937e16ca8af237b3d9ba01de0fb5e00b67aa7',
      'axbi_driver.rs':'41c969a5308070c0a27708cf7443a96f83bdb2a7685edd5ee8819c46a8e96414'}

@dataclass(frozen=True)
class Case:
    id:str
    x:float
    b:float
    H:float
    s:float
    dt:float
    nh0:float=1.9e-7
    fesc:float=.2
    nseg:int=16
    nmu:int=8
    nenergy:int=128
    qmin:float=13.6
    qmax:float=512.
    def validate(self):
        if not self.id or any(ch.isspace() for ch in self.id):raise ValueError('CASE_ID')
        vals=(self.x,self.b,self.H,self.s,self.dt,self.nh0,self.fesc,self.qmin,self.qmax)
        if not all(math.isfinite(v) for v in vals):raise ValueError('NONFINITE_CASE')
        if not (0<=self.x<=XMAX and abs(self.b)<=.4 and self.H>0 and self.dt>=0 and self.nh0>=sys.float_info.min and 0<self.fesc<=1):raise ValueError('CASE_DOMAIN')
        for n in (self.nseg,self.nmu,self.nenergy):
            if not isinstance(n,int) or isinstance(n,bool):raise ValueError('INTEGER_RESOLUTION')
        if not (1<=self.nseg<=1024 and self.nmu in (8,16,32) and 1<=self.nenergy<=1024 and 0<self.qmin<self.qmax<=50000):raise ValueError('GRID_DOMAIN')
    @property
    def a(self):return AREF*math.exp(self.x)
    @property
    def z(self):return 1/self.a-1

@lru_cache(maxsize=12)
def gl(n):
    m,w=leggauss(n)
    m.setflags(write=False);w.setflags(write=False)
    return m,w/2

def rays(x:float,b:float,nmu:int):
    if not all(math.isfinite(z) for z in (x,b)) or abs(b)>.4 or not 0<=x<=XMAX or not isinstance(nmu,int) or isinstance(nmu,bool) or nmu<4 or nmu>512:raise ValueError('RAY_DOMAIN')
    mu0,w=gl(nmu)
    R=np.sqrt(math.exp(2*b)*(1-mu0*mu0)+math.exp(-4*b)*mu0*mu0)
    J=R**-3
    norm=float(np.dot(w,J))
    return math.exp(-x)*R,math.exp(-2*b)*mu0/R,w*J/norm,norm

def shape(E):
    E=np.asarray(E,dtype=float)
    return E*E/np.expm1(E/KT)

def moments(lo,hi):
    """Vectorized literal GL8 number and energy moments on physical intervals."""
    lo,hi=np.broadcast_arrays(lo,hi)
    half=np.maximum(hi-lo,0)/2
    E=(lo+hi)[...,None]/2+half[...,None]*np.array(_X8)
    wt=half[...,None]*np.array(_W8)
    y=shape(E)*wt
    return np.sum(y,axis=-1),np.sum(y*E,axis=-1)

@lru_cache(maxsize=16)
def spectral(nseg):
    pieces=[]
    for lo,hi in zip(EDGES[:-1],EDGES[1:]):
        for j in range(nseg):
            L=lo if j==0 else lo*(hi/lo)**(j/nseg)
            U=hi if j+1==nseg else lo*(hi/lo)**((j+1)/nseg)
            e=L+(U-L)*np.arange(33)/32
            w=np.ones(33);w[1:-1:2]=4;w[2:-1:2]=2
            n=float(np.dot(w,shape(e))*(U-L)/96)
            pieces.append((L,U,n))
    arr=np.array(pieces);arr[:,2]/=np.sum(arr[:,2]);arr.setflags(write=False)
    return arr

def predict(c:Case):
    c.validate()
    scales,mu,aw,jnorm=rays(c.x,c.b,c.nmu)
    cells=spectral(c.nseg)
    qe=c.qmin*np.exp(math.log(c.qmax/c.qmin)*np.arange(c.nenergy+1)/c.nenergy)
    qe[0]=c.qmin;qe[-1]=c.qmax
    if np.any(cells[0,0]/scales<qe[0]) or np.any(cells[-1,1]/scales>qe[-1]):raise ValueError('SOURCE_OUTSIDE_GRID')
    # Entire support admitted before any assignment. N,U remain positive.
    ns,us=moments(cells[:,0],cells[:,1])
    _,_,rate=native_emission_rate(c.z,c.nh0,c.fesc)
    amount=rate*c.dt
    nr=[];ur=[]
    for h,w in zip(scales,aw):
        lo=np.maximum(cells[:,0,None],qe[None,:-1]*h)
        hi=np.minimum(cells[:,1,None],qe[None,1:]*h)
        valid=hi>lo
        # Avoid evaluating BB at large invalid midpoint energies.
        n,u=moments(np.where(valid,lo,13.6),np.where(valid,hi,13.6))
        amp=amount*w*cells[:,2]/ns
        nr.append(float(np.sum(n*amp[:,None])))
        ur.append(float(np.sum(u*amp[:,None])))
    n=float(math.fsum(nr));u=float(math.fsum(ur))
    d=float(np.dot(ur,(3*mu*mu-1)/2));dip=float(np.dot(ur,mu))
    energy_rate=rate*float(np.sum(cells[:,2]*us/ns))
    proper_nh=c.nh0/c.a**3
    S=proper_nh*energy_rate/c.H
    return dict(id=c.id,n=n,u=u,inventory_n=n,inventory_u=u,
       delta=d,dipole=dip,min_stock=0.,source_amount=amount,
       source_mean_energy=float(np.sum(cells[:,2]*us/ns)),
       energy_rate_per_h=energy_rate,proper_nh=proper_nh,
       S_ev_cm3_per_x=S,raw_jacobian_norm=jnorm,
       angular_p2=float(np.dot(aw,(3*mu*mu-1)/2)),
       angular_p1=float(np.dot(aw,mu)),
       n_relative_source_error=(n/amount-1 if amount>0 else 0),
       u_relative_source_error=(u/(energy_rate*c.dt)-1 if c.dt>0 else 0),
       scope='predicted_discrete_injection_not_observed_Rust')

def verify_source_files():
    root=Path(__file__).resolve().parent/'reference'
    for p,sha in PINS.items():
        if hashlib.sha256((root/p).read_bytes()).hexdigest()!=sha:raise ValueError('SOURCE_HASH:'+p)
    return PINS.copy()
