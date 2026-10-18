"""Source-only native-grid oracle and independent birth-frame continuum reference.

x=ln(a/a_ref); number is photons/H-nucleus and energy eV/H-nucleus.
Multiplication by current proper n_H is required for physical-volume moments.
Reference-ray photon stocks do not dilute with a^3; their energies redshift.
No absorption, H/He, photon-energy reconstruction closure or Einstein feedback.
"""
from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache
from typing import Callable, Sequence
import math
import numpy as np
from scipy.integrate import quad
from source_oracle import Case, rays, spectral, moments, native_emission_rate, shape, AREF, XMAX

@dataclass
class CellState:
    number: np.ndarray
    energy_ref: np.ndarray
    def validate(self):
        if self.number.ndim!=2 or self.number.shape!=self.energy_ref.shape:
            raise ValueError('STOCK_SHAPE')
        if not all(np.isfinite(a).all() and (a>=0).all() for a in (self.number,self.energy_ref)):
            raise ValueError('NEGATIVE_OR_NONFINITE_STOCK')

@lru_cache(maxsize=32)
def source_grid(nseg: int, nenergy: int, qmin: float, qmax: float):
    cells=spectral(nseg)
    q=qmin*np.exp(math.log(qmax/qmin)*np.arange(nenergy+1)/nenergy)
    q[0]=qmin;q[-1]=qmax
    norm,_=moments(cells[:,0],cells[:,1])
    q.setflags(write=False);norm.setflags(write=False)
    return cells,q,norm

def deposit(case: Case) -> CellState:
    """Independent vectorized replica of the pinned discrete injection integral.

    It predicts actual native-grid stocks, not an observed native execution.
    Positive source panel intersections; one local solid-angle Jacobian only.
    """
    case.validate()
    scales,_,aw,_=rays(case.x,case.b,case.nmu)
    cells,q,norm=source_grid(case.nseg,case.nenergy,case.qmin,case.qmax)
    if np.any(cells[0,0]/scales<q[0]) or np.any(cells[-1,1]/scales>q[-1]):
        raise ValueError('SOURCE_OUTSIDE_GRID')
    _,_,rate=native_emission_rate(case.z,case.nh0,case.fesc)
    amount=rate*case.dt
    n=np.zeros((case.nmu,case.nenergy));u=np.zeros_like(n)
    for i,(h,w) in enumerate(zip(scales,aw)):
        lo=np.maximum(cells[:,0,None],q[None,:-1]*h)
        hi=np.minimum(cells[:,1,None],q[None,1:]*h)
        ok=hi>lo
        nn,uu=moments(np.where(ok,lo,13.6),np.where(ok,hi,13.6))
        coeff=(amount*w*cells[:,2]/norm)[:,None]
        n[i]=np.sum(coeff*nn,axis=0)
        u[i]=np.sum(coeff*uu,axis=0)/h
    state=CellState(n,u);state.validate()
    return state

def inventory(state: CellState, x: float, b: float) -> dict:
    state.validate()
    scales,mu,_,_=rays(x,b,state.number.shape[0])
    per_ray=state.energy_ref.sum(axis=1)*scales
    n=float(math.fsum(state.number.ravel()))
    u=float(math.fsum(per_ray));delta=float(per_ray@((3*mu*mu-1)/2))
    dip=float(per_ray@mu)
    return dict(inventory_n=n,inventory_u=u,delta=delta,dipole=dip,
                min_number=float(state.number.min()),
                pperp=(u-delta)/3,ppar=(u+2*delta)/3)

def simulate(cases: Sequence[Case], end_x: float, end_b: float) -> dict:
    """Sequential source-only deposition, free redshift and endpoint stress.

    Per-step work is the exact inventory difference at fixed canonical stock;
    that telescoping ledger is algebraic, not an independent quadrature error.
    """
    if not cases: raise ValueError('EMPTY_CASE')
    first=cases[0];first.validate()
    state=CellState(np.zeros((first.nmu,first.nenergy)),np.zeros((first.nmu,first.nenergy)))
    config=lambda c:(c.nmu,c.nenergy,c.nseg,c.qmin,c.qmax,c.nh0,c.fesc)
    nledger=uledger=work=0.0
    xold,bold=cases[0].x,cases[0].b
    for c in cases:
        c.validate()
        if config(c)!=config(first):raise ValueError('CHANGING_DISCRETE_SOURCE')
        if c.x<xold:raise ValueError('NONMONOTONE_TIME')
        before=inventory(state,xold,bold)['inventory_u']
        after=inventory(state,c.x,c.b)['inventory_u']
        work+=before-after
        new=deposit(c);added=inventory(new,c.x,c.b)
        nledger+=added['inventory_n'];uledger+=added['inventory_u']
        state.number+=new.number;state.energy_ref+=new.energy_ref
        xold,bold=c.x,c.b
    if end_x<xold:raise ValueError('END_BEFORE_BIRTH')
    work+=inventory(state,xold,bold)['inventory_u']-inventory(state,end_x,end_b)['inventory_u']
    result=inventory(state,end_x,end_b)
    result.update(id=first.id,births=len(cases),ledger_n=nledger,ledger_u=uledger,work=work,
                  number_residual=result['inventory_n']-nledger,
                  energy_residual=result['inventory_u']+work-uledger,
                  proper_nh=first.nh0/(AREF*math.exp(end_x))**3,
                  ray_number=state.number.sum(axis=1).tolist(),
                  ray_energy_ref=state.energy_ref.sum(axis=1).tolist(),
                  scope='PYTHON_DISCRETE_ORACLE_NOT_NATIVE_OBSERVATION')
    return result

def midpoint_cases(template: Case, geometry: Callable, x0: float, x1: float, steps: int):
    """Midpoint in log a; dt is independently integrated exact proper time.

    geometry(x) returns b,H,s. No equal-dt assumption or source-time freezing.
    """
    from dataclasses import replace
    if not (isinstance(steps,int) and not isinstance(steps,bool) and 1<=steps<=4096 and 0<=x0<x1<=XMAX):
        raise ValueError('TIME_GRID')
    cases=[]
    for left,right in zip(np.linspace(x0,x1,steps+1)[:-1],np.linspace(x0,x1,steps+1)[1:]):
        x=float((left+right)/2);b,H,s=geometry(x)
        dt=quad(lambda u:1/geometry(u)[1],float(left),float(right),epsabs=0.,epsrel=2e-12)[0]
        cases.append(replace(template,x=x,b=float(b),H=float(H),s=float(s),dt=float(dt)))
    return cases

@lru_cache(maxsize=4)
def mean_energy_quad() -> float:
    number=quad(lambda E:float(shape(E)),13.6,100.,epsabs=1e-11,epsrel=1e-12)[0]
    return quad(lambda E:E*float(shape(E)),13.6,100.,epsabs=1e-10,epsrel=1e-12)[0]/number

def continuum_reference(template: Case, geometry: Callable, x0: float, x1: float,
                        ntime: int=96, nangle: int=96) -> dict:
    """Independent physical birth-direction quadrature; no native cell bins.

    This integrates a continuous BB source and positive emission ages, with
    exact birth-to-observation null redshift. No old-frame J is used here.
    """
    if not (0<=x0<x1<=XMAX and 8<=ntime<=512 and 8<=nangle<=512):raise ValueError('REFERENCE_DOMAIN')
    template.validate()
    z,w=np.polynomial.legendre.leggauss(ntime);mu,wm=np.polynomial.legendre.leggauss(nangle)
    times=x0+(z+1)*(x1-x0)/2;w=w*(x1-x0)/2;wm=wm/2
    bend,_,_=geometry(x1);mean=mean_energy_quad();N=U=D=Eemit=0.
    for x,weight in zip(times,w):
        b,H,_=geometry(float(x));d=bend-b
        R=np.sqrt(math.exp(2*d)*(1-mu*mu)+math.exp(-4*d)*mu*mu)
        F=float(wm@R)
        # Small-d stable cancellation via the original analytic zero part.
        tp=math.expm1(2*d);tz=math.expm1(-4*d)
        g=(3*mu*mu-1)/2+tz*mu*mu-tp*(1-mu*mu)/2
        invdiff=-(tp*(1-mu*mu)+tz*mu*mu)/(R*(R+1))
        DD=(tz-tp)/3+float(wm@(g*invdiff))
        _,_,rate=native_emission_rate(1/(AREF*math.exp(x))-1,template.nh0,template.fesc)
        count=rate*weight/H
        N+=count;Eemit+=count*mean
        U+=count*mean*math.exp(x-x1)*F
        D+=count*mean*math.exp(x-x1)*DD
    return dict(inventory_n=N,inventory_u=U,delta=D,ledger_u=Eemit,work=Eemit-U,
                proper_nh=template.nh0/(AREF*math.exp(x1))**3,
                source_mean_ev=mean,scope='CONTINUOUS_BIRTH_FRAME_REFERENCE_NOT_NATIVE')

def gauss2_cases(template: Case, geometry: Callable, x0: float, x1: float, panels: int):
    """Two positive source impulses per log-scale panel, weighted by dt/dx.

    Fourth-order composite GL time integration for smooth source-only moments;
    not an assumed high-order integrator for nonlinear reacting gas.
    """
    from dataclasses import replace
    if not (isinstance(panels,int) and not isinstance(panels,bool) and 1<=panels<=2048 and 0<=x0<x1<=XMAX):
        raise ValueError('TIME_GRID')
    out=[]
    edges=np.linspace(x0,x1,panels+1)
    for left,right in zip(edges[:-1],edges[1:]):
        half=(right-left)/2;middle=(left+right)/2
        for node in (-1/math.sqrt(3),1/math.sqrt(3)):
            x=float(middle+half*node);b,H,s=geometry(x)
            c=replace(template,x=x,b=float(b),H=float(H),s=float(s),dt=float(half/H))
            c.validate();out.append(c)
    return out
