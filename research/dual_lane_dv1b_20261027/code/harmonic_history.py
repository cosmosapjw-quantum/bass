"""DV1-B finite-time Galerkin I/E/B/V evolution, 2<=L<=8.

Reuses the pinned DV1-A analytic spin generator. No direct/Volterra callbacks,
angular quadrature, source fitting, positivity projection or closure switching
are used in the harmonic IVP. Outside-L coefficients are set to zero explicitly;
this is an approximation controlled only by the declared cutoff study.
All rates use u=t/T_star (physical rates times T_star); coefficients carry the
common reference bolometric intensity normalization. P8 carrier S+A and
Q+iU=sum(E+iB) spin+2 Z are inherited without an observer-sky conversion.
"""
from __future__ import annotations
from functools import lru_cache
from pathlib import Path
import sys
import numpy as np
from scipy.integrate import solve_ivp
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'vendor'))
from harmonic_streaming import streaming_matrix,labels
from polarized_dictionary import Grid,stf_basis,synthesize,source_matrix


@lru_cache(maxsize=7)
def shear_blocks(L: int):
    """Five exact analytic STF generator matrices per spin, reused at each RHS."""
    u=stf_basis()
    a0=np.stack([streaming_matrix(0,L,L,0.,S) for S in u])
    if np.max(np.abs(a0.imag))>2e-12:raise ArithmeticError('scalar matrix not real')
    a2=np.stack([streaming_matrix(2,L,L,0.,S) for S in u])
    a0=a0.real.copy();a0.setflags(write=False);a2.setflags(write=False)
    return a0,a2


def direction_view(directions,weights):
    """Use DL2 spin harmonics on specified physical directions and raw weights.

    Reconstruct the same theta/phi screen; do not compare Q/U from different
    local screens. This is an evaluation view, not a new quadrature rule.
    """
    n=np.asarray(directions,float);w=np.asarray(weights,float)
    if n.ndim!=2 or n.shape[1]!=3 or w.shape!=(len(n),) or not np.isfinite(n).all() or not np.isfinite(w).all():
        raise ValueError('finite directions and matching weights required')
    if np.max(np.abs(np.linalg.norm(n,axis=1)-1))>2e-10:raise ValueError('unit directions required')
    g=Grid.__new__(Grid);g.theta=np.arccos(np.clip(n[:,2],-1,1));g.phi=np.arctan2(n[:,1],n[:,0]);g.w=w.copy()
    st,ct=np.sin(g.theta),np.cos(g.theta);sp,cp=np.sin(g.phi),np.cos(g.phi)
    g.n=n.copy();g.bt=np.stack([ct*cp,ct*sp,-st],axis=1);g.bp=np.stack([-sp,cp,np.zeros_like(sp)],axis=1)
    g.P=np.eye(3)-np.einsum('ni,nj->nij',n,n);g._cache={}
    return g


def intensity_moments(c):
    """Continuum reduced rho, flux q and pi from I00/I1m/I2m; no angular cutoff fit."""
    rho=np.sqrt(4*np.pi)*c.get(('I',0,0),0.)
    q=np.sqrt(4*np.pi/3)*np.array([c.get(('I',1,1),0.),c.get(('I',1,-1),0.),c.get(('I',1,0),0.)])
    pi=np.sqrt(8*np.pi/15)*np.einsum('m,mij->ij',[c.get(('I',2,m),0.) for m in range(-2,3)],stf_basis())
    return float(rho),q,pi


class HarmonicHistory:
    """Independent finite-time, full-polarized Galerkin IVP on a fixed L.

    `suppress_eb` is an explicit negative-control switch, never a default method.
    No initial mode is silently dropped when it lies outside the requested L.
    """
    def __init__(self,profile,initial:dict,L:int,end:float,rtol=2e-12,atol=2e-14,suppress_eb=False):
        if isinstance(L,bool) or int(L)!=L or not 2<=L<=8:raise ValueError('integer cutoff 2<=L<=8 required')
        if not np.isfinite(end) or not 0<end<=.6:raise ValueError('support requires 0<end<=0.6')
        self.profile,self.L,self.end=profile,int(L),float(end)
        self.l0,self.l2=labels(0,L),labels(2,L);self.n0,self.n2=len(self.l0),len(self.l2)
        self.keys=[(f,l,m) for f in ('I','V') for l,m in self.l0]+[(f,l,m) for f in ('E','B') for l,m in self.l2]
        self.index={k:i for i,k in enumerate(self.keys)}
        if any(k not in self.index or not np.isfinite(v) for k,v in initial.items()):raise ValueError('invalid or excluded initial harmonic mode')
        self.initial_vector=np.array([initial.get(k,0.) for k in self.keys],float)
        self.blocks0,self.blocks2=shear_blocks(L);self.suppress_eb=bool(suppress_eb)
        self.idx0={lm:i for i,lm in enumerate(self.l0)};self.idx2={lm:i for i,lm in enumerate(self.l2)}
        self.solution=solve_ivp(self.rhs,(0.,self.end),self.initial_vector,method='DOP853',rtol=rtol,atol=atol,dense_output=True)
        if not self.solution.success:raise RuntimeError(self.solution.message)

    def rhs(self,t,y):
        H,S=self.profile.fields(t);nu=float(self.profile.rate(t));S=np.asarray(S,float)
        if not np.isfinite(H) or not np.isfinite(nu) or nu<0 or S.shape!=(3,3) or not np.isfinite(S).all():raise ValueError('invalid prescribed rate')
        if abs(np.trace(S))>1e-13 or np.max(np.abs(S-S.T))>1e-13:raise ValueError('non-STF shear')
        ss=np.einsum('mij,ij->m',stf_basis(),S)
        A0=np.tensordot(ss,self.blocks0,axes=1);A2=np.tensordot(ss,self.blocks2,axes=1)
        if self.suppress_eb:A2=A2.real
        n0,n2=self.n0,self.n2
        I=y[:n0];V=y[n0:2*n0];p=y[2*n0:2*n0+n2]+1j*y[2*n0+n2:]
        dI=A0@I-(4*H+nu)*I;dV=A0@V-(4*H+nu)*V;dp=A2@p-(4*H+nu)*p
        dI[self.idx0[0,0]]+=nu*I[self.idx0[0,0]]
        for m in range(-2,3):
            i,j=self.idx0[2,m],self.idx2[2,m]
            dI[i]+=nu*(.1*I[i]-np.sqrt(6)/10*p[j].real)
            dp[j]+=nu*(-np.sqrt(6)/10*I[i]+.6*p[j].real)
        for m in range(-1,2):dV[self.idx0[1,m]]+=.5*nu*V[self.idx0[1,m]]
        return np.r_[dI,dV,dp.real,dp.imag]

    def unpack(self,y):return {k:float(v) for k,v in zip(self.keys,y)}

    def coefficients(self,t):
        t=float(t)
        if not np.isfinite(t) or t<0 or t>self.end:raise ValueError('time outside solved support')
        return self.unpack(self.solution.sol(t))

    def moment(self,t):return source_matrix(self.coefficients(t))

    def state(self,t,view:Grid):return synthesize(view,self.coefficients(t))
