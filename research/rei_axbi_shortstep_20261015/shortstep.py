"""AX03 source-locked cancellation-resistant proper-time and Killing increments.

Selected C8 numerical/reproducibility research lane, actual Bianchi I AX03
source fields and original physical q cases. This module does NOT change the
live REI Rust solver and does NOT certify full Einstein/atomic feedback.

Numeric APIs:
- Gauss4/8 physical integrals of 1/H and s/H over the actual binary64 endpoints,
  using local log1p(a2-a1)/a1 and a1*exp(fraction*dx). No subtraction of
  accumulated 1e16-second timestamps.
- 501-node source-derived cubic Hermite interpolation with physical endpoint
  derivatives. Stable factored single/multi-cell increments, monotonicity gates.
- Differential photon energy/direction Jacobian computed using log1p/expm1.
"""
from __future__ import annotations
from bisect import bisect_right
from functools import lru_cache
from pathlib import Path
from typing import Optional
import hashlib,math,sys
import numpy as np
from numpy.polynomial.legendre import leggauss

HERE=Path(__file__).resolve().parent
SOURCE_CANDIDATES=(
    HERE.parent/"rei_axbi_background_supplier_20261015",  # BASS research sibling
    HERE.parent/"bass_20261015",                           # REI supplier sibling
)
PARENT=next((p for p in SOURCE_CANDIDATES if (p/"axbi_provider.py").is_file()),None)
if PARENT is None:
    raise FileNotFoundError("FROZEN_AX03_SUPPLIER_SOURCE_NOT_ADJACENT")
sys.path.insert(0,str(PARENT))
from axbi_provider import Background,Family,LOCK_SHA,_read_lock

class ResolutionError(ValueError):
    """A requested interval is unrepresentable in binary64 endpoint coordinates."""

def _native_ray(a):
    return np.asarray(a,dtype=np.float64)

def _validate_pair(bg:Background,a0:float,a1:float):
    a0=float(a0);a1=float(a1)
    if not math.isfinite(a0) or not math.isfinite(a1):
        raise ValueError("nonfinite scale coordinate")
    if not(bg.aref<=a0<=a1<=bg.aend):
        raise ValueError("AX03 source domain or ordering invalid")
    return a0,a1

def stable_dx(a0:float,a1:float)->float:
    """Logarithmic increment from already rounded actual binary64 endpoints."""
    a0=float(a0);a1=float(a1)
    if not(0<a0<=a1) or not math.isfinite(a0) or not math.isfinite(a1):
        raise ValueError("ordered positive finite")
    return math.log1p((a1-a0)/a0)

@lru_cache(maxsize=5)
def _gauss_rule(order:int):
    nodes,weights=leggauss(order)
    nodes.flags.writeable=False
    weights.flags.writeable=False
    return nodes,weights

def gauss_increment(bg:Background,a0:float,a1:float,*,order:int=4,
                    max_step_x:float=0.0028)->tuple[float,float]:
    """Return (delta proper seconds, delta b) by physical rate quadrature."""
    a0,a1=_validate_pair(bg,a0,a1)
    if a0==a1:return (0.0,0.0)
    if not isinstance(order,int) or isinstance(order,bool) or order not in (2,4,6,8,12):
        raise ValueError("supported normalized Gauss quadrature order")
    if not(math.isfinite(max_step_x) and max_step_x>0):
        raise ValueError("positive finite interval cap")
    dx=stable_dx(a0,a1)
    panels=max(1,math.ceil(dx/max_step_x))
    if panels>2048:raise ValueError("too many local Gauss panels")
    nodes,weights=_gauss_rule(order)
    lam=(np.arange(panels)[:,None]+(1+nodes[None,:])/2)/panels
    w=weights[None,:]/(2*panels)
    # Evaluates the source from a0 exp(lam*dx) directly; no subtraction
    # of two huge elapsed proper times.
    scales=a0*np.exp(lam*dx)
    H=np.asarray(bg.mean_hubble(scales),dtype=float)
    s=np.asarray(bg.shear(scales),dtype=float)
    dt=dx*math.fsum(float(x) for x in (w/H).ravel())
    db=dx*math.fsum(float(x) for x in (w*s/H).ravel())
    if not(math.isfinite(dt) and math.isfinite(db) and dt>0):
        raise ArithmeticError("unstable/negative physical clock increment")
    if bg.case.q_ref==0.0 and db!=0.0:
        raise ArithmeticError("source shear zero mode violated")
    return dt,db

def gauss_batch(bg:Background,a0_array,a1_array,*,order:int=4,
                max_step_x:float=0.0028):
    """Vectorize exact same local Gauss integrands over multiple intervals.

    Independent of time-table values, uses only source H(a) and s(a).
    Groups intervals by bounded panels. This reduces Python overhead but
    does not furnish a certified all-domain quadrature-error bound.
    """
    a0=np.asarray(a0_array,dtype=np.float64)
    a1=np.asarray(a1_array,dtype=np.float64)
    if a0.shape!=a1.shape or a0.ndim!=1 or not a0.size:
        raise ValueError("equal-length nonempty 1D endpoint arrays required")
    if not np.isfinite(a0).all() or not np.isfinite(a1).all():
        raise ValueError("nonfinite batch endpoints")
    if np.any(a0<bg.aref) or np.any(a1>bg.aend) or np.any(a1<a0):
        raise ValueError("source domain/order violated")
    if not isinstance(order,int) or isinstance(order,bool) or order not in (2,4,6,8,12):
        raise ValueError("invalid Gauss rule order")
    if not(math.isfinite(max_step_x) and max_step_x>0):
        raise ValueError("invalid maximum panel x")
    dx=np.log1p((a1-a0)/a0)
    count=np.maximum(1,np.ceil(dx/max_step_x).astype(np.int64))
    if np.any(count>2048):raise ValueError("too many Gauss panels")
    nodes,weights=_gauss_rule(order)
    result_dt=np.zeros_like(a0)
    result_db=np.zeros_like(a0)
    for n in np.unique(count):
        indices=np.flatnonzero((count==n)&(dx>0))
        if not len(indices):continue
        # [interval, panel, node] arrays, no source loops over each interval.
        panels=np.arange(int(n),dtype=float)
        theta=(panels[:,None]+(nodes[None,:]+1)/2)/n
        x=dx[indices,None,None]*theta[None,:,:]
        a=a0[indices,None,None]*np.exp(x)
        H=np.asarray(bg.mean_hubble(a),dtype=np.float64)
        s=np.asarray(bg.shear(a),dtype=np.float64)
        ww=weights[None,None,:]/(2*n)
        result_dt[indices]=dx[indices]*np.sum(ww/H,axis=(1,2))
        result_db[indices]=dx[indices]*np.sum(ww*s/H,axis=(1,2))
    if np.any(result_dt[dx>0]<=0) or not np.isfinite(result_dt).all() or not np.isfinite(result_db).all():
        raise ArithmeticError("invalid batched positive proper time")
    return result_dt,result_db

def _hermite_coeff(y0,y1,d0,d1,h):
    """Power coefficients at normalized cell coordinate u in [0,1]."""
    c0=float(y0)
    c1=h*float(d0)
    diff=float(y1)-float(y0)
    c2=3*diff-h*(2*float(d0)+float(d1))
    c3=-2*diff+h*(float(d0)+float(d1))
    return (c0,c1,c2,c3)

def _min_derivative(c):
    """Quadratic minimum of dp/du, including its interior vertex if any."""
    _,p1,p2,p3=c
    candidates=[p1,p1+2*p2+3*p3]
    if p3>0:
        u=-p2/(3*p3)
        if 0<u<1:candidates.append(p1+2*p2*u+3*p3*u*u)
    return min(candidates)

def _poly_increment(c,u,du):
    """Factored cubic difference, never subtract two huge cubic values."""
    if du==0:return 0.0
    _,p1,p2,p3=c
    return du*(p1+(2*u+du)*p2+(3*u*u+3*u*du+du*du)*p3)

class HermiteClock:
    """Source-bound 501-node physical-endpoint Hermite clock and anisotropy."""
    def __init__(self,bg:Background,n:int=501):
        if not isinstance(n,int) or isinstance(n,bool) or n<3 or n>32769:
            raise ValueError("number of intervals 2..32768")
        self.bg=bg
        self.nodes=np.linspace(0,bg.xmax,n)
        self.h=float(self.nodes[1]-self.nodes[0])
        self.anodes=bg.aref*np.exp(self.nodes)
        self.anodes[0]=bg.aref;self.anodes[-1]=bg.aend
        table=bg.table(n)
        T=np.asarray(table["proper_elapsed_s"])
        B=np.asarray(table["b"])
        dt_dx=np.asarray(table["dt_dln_a_s"])
        db_dx=np.asarray(table["db_dln_a"])
        self.ct=np.array([_hermite_coeff(T[j],T[j+1],dt_dx[j],dt_dx[j+1],
                          float(self.nodes[j+1]-self.nodes[j])) for j in range(n-1)])
        self.cb=np.array([_hermite_coeff(B[j],B[j+1],db_dx[j],db_dx[j+1],
                          float(self.nodes[j+1]-self.nodes[j])) for j in range(n-1)])
        if any(_min_derivative(c)<=0 for c in self.ct):
            raise ArithmeticError("nonmonotone or nonphysical Hermite proper clock")
        # Physical signed shear implies b monotonic in same sign; zero shear b identically zero.
        if bg.case.q_ref==0:
            if np.any(self.cb!=0):raise ArithmeticError("zero shear b not preserved")
        else:
            sign=math.copysign(1,bg.case.q_ref)
            for c in self.cb:
                if _min_derivative(sign*c)<=0:
                    raise ArithmeticError("Hermite b violates signed physical shear")
        self.source_lock_sha=LOCK_SHA
    def _cell(self,a):
        a=float(a)
        if not math.isfinite(a) or a<self.bg.aref or a>self.bg.aend:
            raise ValueError("outside mean scale source chart")
        i=max(0,min(len(self.nodes)-2,bisect_right(self.anodes,a)-1))
        # Use log1p near cell knot to preserve local u.
        u=math.log1p((a-float(self.anodes[i]))/float(self.anodes[i]))/(self.nodes[i+1]-self.nodes[i])
        return i,u
    def point(self,a):
        i,u=self._cell(a)
        def poly(v):return v[0]+u*(v[1]+u*(v[2]+u*v[3]))
        return poly(self.ct[i]),poly(self.cb[i])
    def increment(self,a0,a1):
        a0,a1=_validate_pair(self.bg,a0,a1)
        if a0==a1:return 0.0,0.0
        ti=bi=0.
        left=a0
        for _ in range(len(self.nodes)+1):
            if left>=a1:break
            j,u=self._cell(left)
            right=min(a1,float(self.anodes[j+1]))
            if right<=left:raise ArithmeticError("non-progress Hermite segment")
            local_dx=stable_dx(left,right)
            du=local_dx/float(self.nodes[j+1]-self.nodes[j])
            ti+=_poly_increment(self.ct[j],u,du)
            bi+=_poly_increment(self.cb[j],u,du)
            left=right
        else:
            raise ArithmeticError("unbounded interval segmentation")
        if not ti>0:raise ArithmeticError("nonpositive proper increment")
        return ti,bi
    def derivative(self,a):
        j,u=self._cell(a)
        delta=float(self.nodes[j+1]-self.nodes[j])
        return ((self.ct[j,1]+u*(2*self.ct[j,2]+3*u*self.ct[j,3]))/delta,
                (self.cb[j,1]+u*(2*self.cb[j,2]+3*u*self.cb[j,3]))/delta)

def photon_short_logmap(bg:Background,a_early,a_late,mu_face,*,order=4):
    """Cancellation-resistant source-fixed photon Killing characteristics."""
    dt,db=gauss_increment(bg,a_early,a_late,order=order)
    dx=stable_dx(a_early,a_late)
    mu=np.asarray(mu_face,dtype=np.float64)
    if not np.isfinite(mu).all() or np.any(abs(mu)>1):
        raise ValueError("orthonormal direction mu_face must be in [-1,1]")
    # B = b_early - b_late = -db; no difference between two accumulated b.
    dd=-db
    rminus1=(1-mu**2)*np.expm1(2*dd)+(mu**2)*np.expm1(-4*dd)
    logR=0.5*np.log1p(rminus1)
    log_energy=dx+logR
    mu_early=mu*np.exp(-2*dd-logR)
    jac_log=-3*logR
    return {"proper_elapsed_s":dt,"delta_b":db,"delta_ln_a":dx,
            "log_energy_early_over_late":log_energy,
            "mu_early":mu_early,
            "log_jacobian_early_over_late":jac_log,
            "number_phase_volume_log_residual":3*log_energy+jac_log-3*dx}

if __name__=="__main__":
    import json
    q=.01
    bg=Background(Family(q))
    clock=HermiteClock(bg)
    at=.1
    a2=np.nextafter(at,math.inf)
    answer={"case_q":q,"endpoints":[at,a2],
        "gauss4":gauss_increment(bg,at,a2),
        "gauss8":gauss_increment(bg,at,a2,order=8),
        "hermite":clock.increment(at,a2),
        "accumulated_t_subtraction":bg.at_a(a2)["proper_elapsed_s"]-bg.at_a(at)["proper_elapsed_s"]}
    print(json.dumps(answer,indent=2))
