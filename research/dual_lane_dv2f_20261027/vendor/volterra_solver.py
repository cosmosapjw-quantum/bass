"""KM3: independent causal product integration of the BASS KM1 source equation.

Only prescribed geometry, rest-electron opacity, and the complete initial carrier
are inputs. No direct history/source callback or kinetic RHS integration is used.
Each panel interpolates M at {left, midpoint, right}; its two unknown 9-component
sources are solved together in an 18x18 linear system. Gauss-Legendre integration
applies to the kernel times each interpolation polynomial (product integration).

The default implementation uses the exactly factored angular history accumulator
X. This is algebraically the same discrete Volterra equation as the uncompressed
history sum, not a nine-state Markov closure. Initial and accumulated radiation
retain four real screen components per initial angular node. No positivity,
weight normalization, source projection, or harmonic closure is imposed.
"""
from __future__ import annotations
from pathlib import Path
import sys
import numpy as np
from numpy.polynomial.legendre import leggauss

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'vendor'))
from source_memory import SourceMemory, ALPHA


def lagrange3(x):
    """Quadratic cardinal basis at x=0,1/2,1. x may be an array."""
    x=np.asarray(x,float)
    return np.stack([2*(x-.5)*(x-1),4*x*(1-x),2*x*(x-.5)],axis=-1)


def _validate(memory,times,order):
    t=np.asarray(times,float)
    if t.ndim!=1 or len(t)<2 or not np.isfinite(t).all():
        raise ValueError('times must be a finite one-dimensional panel grid')
    if t[0]!=0. or np.any(np.diff(t)<=0) or t[-1]>memory.geo.end:
        raise ValueError('require t[0]=0, increasing times within prescribed support')
    if isinstance(order,bool) or int(order)!=order or order<2 or order>16:
        raise ValueError('Gauss product integration order must be an integer in [2,16]')
    if not np.isfinite(memory.X0).all(): raise ValueError('nonfinite initial carrier')
    return t.copy(),leggauss(int(order))


def panel_weights(memory,t,a,b,upper,gx,gw):
    """Three 9x9 product weights; t>=upper, cardinal coordinates use [a,b]."""
    out=np.zeros((3,9,9))
    for s,w in zip(a+(upper-a)*(gx+1)/2,(upper-a)*gw/2):
        if memory.geo.profile.rate(float(s))<0: raise ValueError('negative opacity')
        out+=w*lagrange3((s-a)/(b-a))[:,None,None]*memory.kernel(t,float(s))[None]
    return out


def _moment_of_X(geo,t,X):
    z=geo.at(t);E=z['screen']
    return np.einsum('n,nia,nab,njb->ij',z['v'],E,X,E,optimize=True)


def _advance_X(memory,t,a,b,Xa,source_nodes,gx,gw):
    """Integrate the factored history over a partial/full panel, never an ODE."""
    p=memory.geo.profile
    out=np.exp(-(p.kappa(t)-p.kappa(a)))*Xa
    for s,w in zip(a+(t-a)*(gx+1)/2,(t-a)*gw/2):
        s=float(s);z=memory.geo.at(s);E=z['screen']
        m=np.einsum('j,jab->ab',lagrange3((s-a)/(b-a)),source_nodes)
        gain=ALPHA/z['mu'][:,None,None]**4*np.einsum('nia,ij,njb->nab',E,m,E,optimize=True)
        out=out+w*p.rate(s)*np.exp(-(p.kappa(t)-p.kappa(s)))*gain
    return out


class VolterraHistory:
    """Quadratic causal source collocation with a factored angular memory buffer.

    Endpoint M and carrier are independently computed from the unknown source
    solution, not supplied from DirectHistory. Off-grid moment() reconstructs
    the integral carrier; source_polynomial() returns the within-panel source
    interpolant. Their difference is a collocation defect, not a global bound.
    """
    def __init__(self,memory: SourceMemory,times,order: int=4):
        self.memory=memory
        self.times,(self.gx,self.gw)=_validate(memory,times,order)
        self.order=int(order);geo=memory.geo;p=geo.profile
        self.moments=np.empty((len(self.times),3,3))
        self.panels=np.empty((len(self.times)-1,3,3,3))
        self.X_history=np.empty((len(self.times),*memory.X0.shape))
        self.X_history[0]=memory.X0
        self.moments[0]=memory.initial_term(0.)
        self.block_residuals=[];self.block_conditions=[];self.endpoint_consistency=[]
        eye=np.eye(9)
        for i,(a,b) in enumerate(zip(self.times[:-1],self.times[1:])):
            mid=(a+b)/2;Ws=[];rhs=[];left=self.moments[i].ravel()
            for t in (mid,b):
                W=panel_weights(memory,t,a,b,t,self.gx,self.gw);Ws.append(W)
                free=np.exp(-(p.kappa(t)-p.kappa(a)))*_moment_of_X(geo,t,self.X_history[i])
                rhs.append(free.ravel()+W[0]@left)
            block=np.block([[eye-Ws[0][1],-Ws[0][2]],[-Ws[1][1],eye-Ws[1][2]]])
            cond=float(np.linalg.cond(block))
            if not np.isfinite(cond) or cond>1e12:
                raise ValueError('ill-conditioned within-panel source system; refine panel')
            rhs=np.concatenate(rhs);sol=np.linalg.solve(block,rhs)
            if not np.isfinite(sol).all(): raise ValueError('nonfinite source solution')
            self.block_conditions.append(cond)
            self.block_residuals.append(float(np.max(np.abs(block@sol-rhs))))
            self.panels[i]=np.stack([self.moments[i],sol[:9].reshape(3,3),sol[9:].reshape(3,3)])
            self.moments[i+1]=self.panels[i,2]
            self.X_history[i+1]=_advance_X(memory,b,a,b,self.X_history[i],self.panels[i],self.gx,self.gw)
            check=_moment_of_X(geo,b,self.X_history[i+1])
            self.endpoint_consistency.append(float(np.max(np.abs(check-self.moments[i+1]))))

    def _locate(self,t):
        t=float(t)
        if not np.isfinite(t) or t<0 or t>self.times[-1]:
            raise ValueError('time outside solved history support')
        i=min(int(np.searchsorted(self.times,t,side='right')-1),len(self.times)-2)
        return t,i

    def source_polynomial(self,t):
        t,i=self._locate(t);a,b=self.times[i:i+2]
        return np.einsum('j,jab->ab',lagrange3((t-a)/(b-a)),self.panels[i])

    def pullback(self,t):
        t,i=self._locate(t);a,b=self.times[i:i+2]
        if t==a: return self.X_history[i].copy()
        if t==b: return self.X_history[i+1].copy()
        return _advance_X(self.memory,t,a,b,self.X_history[i],self.panels[i],self.gx,self.gw)

    def state(self,t):
        t,_=self._locate(t);z=self.memory.geo.at(t);E=z['screen']
        return z['mu'][:,None,None]**4*np.einsum('nia,nab,njb->nij',E,self.pullback(t),E,optimize=True)

    def moment(self,t):
        t,_=self._locate(t)
        return _moment_of_X(self.memory.geo,t,self.pullback(t))

    def global_reconstruction(self,t,order=8):
        """Independent uncompressed retarded sum of the SOLVED source interpolant."""
        t,_=self._locate(t);gx,gw=leggauss(int(order));out=self.memory.initial_term(t)
        for i,(a,b) in enumerate(zip(self.times[:-1],self.times[1:])):
            if a>=t: break
            W=panel_weights(self.memory,t,a,b,min(t,b),gx,gw)
            out+=np.einsum('jkl,jl->k',W,self.panels[i].reshape(3,9)).reshape(3,3)
        return out


def solve_global_history(memory: SourceMemory,times,order=4):
    """Small independent assembly oracle: sum every old kernel panel explicitly.

    Same product discretization, no angular history accumulator and no direct
    source. O(N^2) kernel quadratures; use only bounded comparison grids.
    """
    ts,(gx,gw)=_validate(memory,times,order)
    moments=np.empty((len(ts),3,3));moments[0]=memory.initial_term(0.)
    panels=np.empty((len(ts)-1,3,3,3));eye=np.eye(9)
    for i,(a,b) in enumerate(zip(ts[:-1],ts[1:])):
        Ws=[];rhs=[]
        for t in ((a+b)/2,b):
            history=memory.initial_term(t).ravel().copy()
            for j,(aa,bb) in enumerate(zip(ts[:i],ts[1:i+1])):
                old=panel_weights(memory,t,aa,bb,bb,gx,gw)
                history+=np.einsum('jkl,jl->k',old,panels[j].reshape(3,9))
            W=panel_weights(memory,t,a,b,t,gx,gw);Ws.append(W)
            rhs.append(history+W[0]@moments[i].ravel())
        block=np.block([[eye-Ws[0][1],-Ws[0][2]],[-Ws[1][1],eye-Ws[1][2]]])
        sol=np.linalg.solve(block,np.concatenate(rhs))
        panels[i]=np.stack([moments[i],sol[:9].reshape(3,3),sol[9:].reshape(3,3)])
        moments[i+1]=panels[i,2]
    return moments,panels
