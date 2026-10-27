"""DV1-B finite-time full-polarized Galerkin reference, L<=8.

Uses the pinned DV1-A Wigner generator, not a quadrature fit to a direct RHS.
P_L L P_L is an EXPLICIT harmonic cutoff approximation. No amplitude expansion,
no direct/Volterra source callback, no positivity clipping or tail extrapolation.
Rates are in normal proper time, or all scaled by T_star for u=t/T_star.
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
from harmonic_streaming import collision_rhs


def coefficient_keys(L: int):
    return [(f,l,m) for f in ('I','V','E','B')
            for l,m in labels(2 if f in ('E','B') else 0,L)]


@lru_cache(maxsize=7)
def operators(L: int):
    n0,n2=len(labels(0,L)),len(labels(2,L));size=2*n0+2*n2
    si,sv,se,sb=slice(0,n0),slice(n0,2*n0),slice(2*n0,2*n0+n2),slice(2*n0+n2,size)
    shear=[]
    for U in stf_basis():
        a0=streaming_matrix(0,L,L,0.,U)
        a2=streaming_matrix(2,L,L,0.,U)
        if np.max(abs(a0.imag))>2e-12:raise ArithmeticError('spin0 reality failure')
        A=np.zeros((size,size));A[si,si]=a0.real;A[sv,sv]=a0.real
        A[se,se]=a2.real;A[se,sb]=-a2.imag;A[sb,se]=a2.imag;A[sb,sb]=a2.real
        shear.append(A)
    keys=coefficient_keys(L);index={k:i for i,k in enumerate(keys)}
    C=-np.eye(size);C[index['I',0,0],index['I',0,0]]=0.
    for m in range(-2,3):
        i,e=index['I',2,m],index['E',2,m]
        C[i,i]=-.9;C[i,e]=-np.sqrt(6)/10
        C[e,i]=-np.sqrt(6)/10;C[e,e]=-.4
    for m in range(-1,2):C[index['V',1,m],index['V',1,m]]=-.5
    O=np.stack(shear);O.setflags(write=False);C.setflags(write=False)
    return O,C


class GalerkinSystem:
    def __init__(self,L: int):
        if isinstance(L,bool) or int(L)!=L or not 2<=L<=8:
            raise ValueError('explicit supported angular cutoff: 2<=L<=8')
        self.L=int(L);self.keys=coefficient_keys(self.L);self.index={k:i for i,k in enumerate(self.keys)}
        self.shear,self.collision=operators(self.L)

    def pack(self,c):
        out=np.zeros(len(self.keys))
        for k,v in c.items():
            if k not in self.index:
                raise ValueError(f'initial mode {k} is outside the selected carrier; no silent truncation')
            if not np.isfinite(v) or not np.isreal(v):raise ValueError('finite real harmonic coefficients required')
            out[self.index[k]]=v
        return out

    def unpack(self,y):
        return dict(zip(self.keys,map(float,y)))

    def rhs(self,t,y,profile):
        H,S=profile.fields(float(t));nu=profile.rate(float(t));S=np.asarray(S,float)
        if (S.shape!=(3,3) or not np.isfinite(S).all() or not np.isfinite(H)
            or not np.isfinite(nu) or nu<0 or np.max(abs(S-S.T))>1e-13 or abs(np.trace(S))>1e-13):
            raise ValueError('invalid normal-frame H/shear/opacity')
        sk=np.einsum('kij,ij->k',stf_basis(),S)
        return -4*H*y+sk@(self.shear@y)+nu*(self.collision@y)


class HarmonicHistory:
    def __init__(self,profile,c0,L,end,rtol=2e-12,atol=2e-14):
        if not np.isfinite(end) or not 0<end<=.6:raise ValueError('bounded support 0<end<=.6')
        self.profile,self.end=profile,float(end);self.system=GalerkinSystem(L)
        self.initial=self.system.pack(c0)
        self.solution=solve_ivp(lambda t,y:self.system.rhs(t,y,profile),(0,self.end),self.initial,
             method='DOP853',rtol=rtol,atol=atol,dense_output=True)
        if not self.solution.success:raise RuntimeError(self.solution.message)

    def _time(self,t):
        t=float(t)
        if not np.isfinite(t) or not 0<=t<=self.end:raise ValueError('outside solved time support')
        return t

    def coefficients(self,t):
        return self.system.unpack(self.solution.sol(self._time(t)))

    def state(self,g,t):
        return synthesize(g,self.coefficients(t))

    def moment(self,t):
        """Continuum angular source of the truncated harmonic field, not raw M_h."""
        return source_matrix(self.coefficients(t))

    def moments(self,t):
        """Continuum intensity moments in the inherited carrier normalization."""
        c=self.coefficients(t)
        return {'rho':float(np.sqrt(4*np.pi)*c['I',0,0]),
                'q':np.sqrt(4*np.pi/3)*np.array([c['I',1,1],c['I',1,-1],c['I',1,0]]),
                'pi':np.sqrt(8*np.pi/15)*np.einsum('k,kij->ij',np.array([c['I',2,m] for m in range(-2,3)]),stf_basis())}


def point_grid(n,w=None):
    """Reuse pinned harmonics on supplied directions, matching the theta/phi screen.

    Sampling transform only. No direct data are supplied to the harmonic solver.
    Pole values need a limiting screen convention; this scoped adapter rejects
    exact poles, while Gauss-Legendre fixtures avoid them by construction.
    """
    n=np.asarray(n,float)
    if n.ndim!=2 or n.shape[1]!=3 or not np.isfinite(n).all():raise ValueError('finite Nx3 directions required')
    if np.max(abs(np.linalg.norm(n,axis=1)-1))>2e-10:raise ValueError('unit directions required')
    g=Grid.__new__(Grid);g.n=n.copy();g.theta=np.arccos(np.clip(n[:,2],-1,1));g.phi=np.arctan2(n[:,1],n[:,0])
    st,ct=np.sin(g.theta),np.cos(g.theta);sp,cp=np.sin(g.phi),np.cos(g.phi)
    if np.min(abs(st))<1e-12:raise ValueError('exact polar screen not supported')
    g.bt=np.stack([ct*cp,ct*sp,-st],axis=1);g.bp=np.stack([-sp,cp,np.zeros(len(n))],axis=1)
    g.P=np.eye(3)-np.einsum('ni,nj->nij',n,n);g._cache={}
    g.w=np.ones(len(n)) if w is None else np.asarray(w,float)
    if g.w.shape!=(len(n),) or not np.isfinite(g.w).all():raise ValueError('invalid weights')
    return g


def kinetic_moments(g,J):
    I=np.trace(J,axis1=-2,axis2=-1);rho=float(np.dot(g.w,I))
    q=np.einsum('n,n,ni->i',g.w,I,g.n)
    pi=np.einsum('n,n,ni,nj->ij',g.w,I,g.n,g.n)-rho*np.eye(3)/3
    return {'rho':rho,'q':q,'pi':pi}
