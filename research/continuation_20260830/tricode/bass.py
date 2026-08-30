"""R2 coherency candidates, NOT BASS native transport or Thomson scattering.

Screen matrices are 2x2 in declared bases. Validation proves algebraic
isometry, not that the caller supplied the correct spatial association.
All dynamical variables here are normalized manufactured variables. H/hbar
is an inverse normalized time, not a declaration of natural units.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import math
from typing import Callable
import numpy as np
from scipy.linalg import expm
TOL=2e-12
METHOD_CLAIMS={
 'full_generator':{'scope':'frozen 4x4 exponential','uniform_stiff_order2':False},
 'bloch_generator':{'scope':'invariant-separated frozen manufactured generator','uniform_stiff_order2':False},
 'strang_reference':{'scope':'R2 fixed-rate second-order reference','uniform_stiff_order2':False}}

def _array(x,dtype=float):
    a=np.array(x,dtype=dtype,copy=True,order='C')
    if not np.isfinite(a).all():raise ValueError('nonfinite data')
    return a

def _readonly(a):a.setflags(write=False);return a

def validate_coherency(j):
    a=_array(j,complex)
    if a.shape[-2:]!=(2,2):raise ValueError('2x2 screen matrices required')
    for m in a.reshape(-1,2,2):
        scale=np.max(abs(m))
        if scale==0:continue
        v=m/scale
        if np.max(abs(v-v.conj().T))>TOL:raise ValueError('not Hermitian')
        if np.linalg.eigvalsh(v).min()<-TOL:raise ValueError('not positive semidefinite')
    return a

@dataclass(frozen=True,init=False)
class RemapPlan:
    weights:np.ndarray
    source_measure:np.ndarray
    target_measure:np.ndarray
    transports:np.ndarray
    content_sha256:str
    def __init__(self,weights,source_measure,target_measure,transports=None):
        R=_array(weights);ws=_array(source_measure);wt=_array(target_measure)
        if R.ndim!=2 or min(R.shape)<1 or ws.shape!=(R.shape[1],) or wt.shape!=(R.shape[0],):raise ValueError('remap shape')
        if max(R.shape)>4096:raise ValueError('dense reference resource limit')
        if np.any(R<0) or np.any(ws<=0) or np.any(wt<=0):raise ValueError('nonnegative weights and positive measures required')
        if np.max(abs(R.sum(axis=1)-1))>TOL:raise ValueError('partition of unity')
        mass_scale=max(float(ws.max()),float(wt.max()))
        if np.max(abs((wt/mass_scale)@R-ws/mass_scale))>TOL:
            raise ValueError('weighted conservation violated')
        U=np.tile(np.eye(2,dtype=complex),(*R.shape,1,1)) if transports is None else _array(transports,complex)
        if U.shape!=(*R.shape,2,2):raise ValueError('screen transport shape')
        for i,j in zip(*np.nonzero(R)):
            if np.max(abs(U[i,j].conj().T@U[i,j]-np.eye(2)))>TOL:raise ValueError('non-isometric screen transport')
        h=sha256()
        for a in (R,ws,wt,U):h.update(str(a.shape).encode());h.update(a.astype(a.dtype.newbyteorder('<')).tobytes())
        for n,a in [('weights',R),('source_measure',ws),('target_measure',wt),('transports',U)]:object.__setattr__(self,n,_readonly(a))
        object.__setattr__(self,'content_sha256',h.hexdigest())
    def apply(self,j):
        a=validate_coherency(j)
        if a.shape!=(len(self.source_measure),2,2):raise ValueError('source count mismatch')
        out=np.zeros((len(self.target_measure),2,2),complex)
        for i,k in zip(*np.nonzero(self.weights)):
            U=self.transports[i,k];out[i]+=self.weights[i,k]*(U@a[k]@U.conj().T)
        validate_coherency(out)
        return out

def coherency_step(j,h:float,omega:float,rate:float,*,method='full_generator'):
    """Frozen dephasing/Hamiltonian flow; no extra Kato physical source.

    Full dense exponentiation and split are baselines. Bloch formulation
    evolves the invariant trace as an independent coordinate, not by clipping
    or post-hoc normalization. O(1) fixed-size computation.
    """
    y=validate_coherency(j)
    if y.shape!=(2,2):raise ValueError('one screen matrix required')
    if not all(math.isfinite(float(x)) for x in (h,omega,rate)) or h<0 or rate<0:raise ValueError('invalid step/rate')
    if method not in METHOD_CLAIMS:raise ValueError('unsupported method')
    if h==0:return y
    sy=np.array([[0,-1j],[1j,0]]);sz=np.diag([1.,-1.]);I=np.eye(2);H=omega*sy/2
    A=-1j*(np.kron(I,H)-np.kron(H.T,I));C=rate/2*(np.kron(sz.T,sz)-np.eye(4));flat=y.reshape(4,order='F')
    if method=='bloch_generator':
        tr=float(np.trace(y).real);bx=2*float(y[0,1].real);by=-2*float(y[0,1].imag);bz=float((y[0,0]-y[1,1]).real)
        if rate>=2*abs(omega):
            d=math.sqrt((rate-2*abs(omega))*(rate+2*abs(omega)))
            slow=-2*omega*omega/(rate+d) if rate+d else 0.;fast=-rate-slow
            es=math.exp(h*slow);ef=math.exp(h*fast);ratio=es*(-math.expm1(-h*d)/d) if d else h*es
            nx=(ef+slow*ratio)*bx+omega*ratio*bz;nz=-omega*ratio*bx+(es-slow*ratio)*bz
        else:
            frequency=math.sqrt((2*abs(omega)-rate)*(2*abs(omega)+rate))/2
            damp=math.exp(-rate*h/2);co=math.cos(frequency*h);si=h*np.sinc(frequency*h/np.pi)
            nx=damp*((co-rate*si/2)*bx+omega*si*bz);nz=damp*(-omega*si*bx+(co+rate*si/2)*bz)
        ny=math.exp(-rate*h)*by
        result=np.array([[(tr+nz)/2,(nx-1j*ny)/2],[(nx+1j*ny)/2,(tr-nz)/2]]).reshape(4,order='F')
    elif method=='full_generator':
        result=expm(h*(A+C))@flat
    else:
        result=flat
        for op in (expm(h*C/2),expm(h*A),expm(h*C/2)):
            result=op@result;validate_coherency(result.reshape(2,2,order='F'))
    out=result.reshape(2,2,order='F');validate_coherency(out)
    scale=max(float(np.max(abs(y))),np.finfo(float).tiny)
    if abs((np.trace(out)-np.trace(y))/scale)>TOL:raise ArithmeticError('trace defect exceeds research precision budget')
    return out

@dataclass(frozen=True)
class SplitStats:
    splits:int
    leaves:int
    max_depth:int
    rhs_evaluations:int
@dataclass(frozen=True)
class MidpointResult:
    value:np.ndarray
    stats:SplitStats

def midpoint_panels(y0,h,fn:Callable,*,panels=1,max_depth=8,iterations=12,atol=1e-10):
    """Executable telemetry model, NOT the pinned Rust donor instrumentation.

    Count actual recursive split events in successful transactions. Fixed-point
    convergence is not a truncation certificate; failure returns no result.
    """
    y=_array(y0)
    if y.ndim!=1 or not len(y):raise ValueError('nonempty vector required')
    for v,lo,hi in [(panels,1,4096),(max_depth,0,16),(iterations,1,4096)]:
        if type(v) is not int or not lo<=v<=hi:raise ValueError('invalid work budget')
    if not math.isfinite(h) or h<=0 or not math.isfinite(atol) or atol<=0:raise ValueError('invalid time/tolerance')
    def advance(v,dt,depth):
        guess=v.copy();calls=0
        for _ in range(iterations):
            d=_array(fn((v+guess)/2))
            if d.shape!=v.shape:raise ValueError('rhs shape')
            new=v+dt*d;calls+=1
            if not np.isfinite(new).all():raise ArithmeticError('nonfinite midpoint')
            if np.max(abs(new-guess))<=atol:return new,SplitStats(0,1,depth,calls)
            guess=new
        if depth>=max_depth:raise ArithmeticError('midpoint did not converge at maximum depth')
        left,a=advance(v,dt/2,depth+1);right,b=advance(left,dt/2,depth+1)
        return right,SplitStats(1+a.splits+b.splits,a.leaves+b.leaves,max(a.max_depth,b.max_depth),calls+a.rhs_evaluations+b.rhs_evaluations)
    total=SplitStats(0,0,0,0)
    for _ in range(panels):
        y,a=advance(y,h/panels,0)
        total=SplitStats(total.splits+a.splits,total.leaves+a.leaves,max(total.max_depth,a.max_depth),total.rhs_evaluations+a.rhs_evaluations)
    assert total.leaves==panels+total.splits
    return MidpointResult(_readonly(y),total)
