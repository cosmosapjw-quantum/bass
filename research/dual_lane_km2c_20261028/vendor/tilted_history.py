"""KM2B: fixed-beta normal-time polarized cold-Thomson evolution.

Normal t or u=t/T_star with nu0 multiplied by T_star. Constant beta and nu0.
The source-only Volterra march integrates the diagonal exponential exactly
against a quadratic source on each causal panel. It never calls DirectHistory
or TiltedThomson.rhs. Angular initial carrier/history is retained, not a
nine-variable Markov closure. No production caller, density boost, normalization,
positivity projection, recoil, or spectral-validity claim.
"""
from __future__ import annotations
from pathlib import Path
import sys
import numpy as np
from scipy.integrate import solve_ivp
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'vendor'))
from tilted_collision import TiltedThomson


def exponential_weights(z: np.ndarray, r: float=1.) -> np.ndarray:
    """W_j=integral_0^r z exp[-z(r-v)] L_j(v)dv; nodes 0,1/2,1.

    Stable power series at z*r<=1, exact recurrence otherwise. No division by
    zero or cancellation of nearly equal exponentials in the vacuum limit.
    """
    z=np.asarray(z,float)
    if z.ndim!=1 or not np.isfinite(z).all() or np.any(z<0) or not np.isfinite(r) or not 0<=r<=1:
        raise ValueError('finite nonnegative 1D z and r in [0,1] required')
    q=z*r; small=q<=1.; moments=[]
    for k in range(3):
        I=np.empty_like(z)
        term=np.full(np.count_nonzero(small),1./(k+1)); total=term.copy()
        for m in range(1,32):
            term *= -q[small]/(k+m+1)
            total += term
        I[small]=q[small]*r**k*total
        qs=q[~small]; e0=-np.expm1(-qs)
        if k==0:I[~small]=e0
        elif k==1:I[~small]=r*(1-e0/qs)
        else:I[~small]=r*r*(1-2/qs+2*e0/(qs*qs))
        moments.append(I)
    i0,i1,i2=moments
    return np.stack([i0-3*i1+2*i2,4*i1-4*i2,2*i2-i1],axis=1)


def _validate(op,J0,nu0,T):
    if not isinstance(op,TiltedThomson):raise TypeError('pinned TiltedThomson required')
    J0=op._carrier(J0).copy();nu0=float(nu0);T=float(T)
    if not np.isfinite(nu0) or nu0<0 or not np.isfinite(T) or T<=0:
        raise ValueError('finite nu0>=0 and T>0 required')
    return J0,nu0,T


def invariant(op,J):
    """gamma(rho-beta.q)=sum w_n D I_n=sum w_e I_e/D, NOT rho_e."""
    return float(np.einsum('n,n,n->',op.w,op.D,np.trace(J,axis1=1,axis2=2)))


def weighted_norm(op,J):
    """Weighted electron-carrier squared HS norm; real S+A has the same norm."""
    Y=op.to_electron(J)
    return float(np.einsum('n,nij,nij->',op.we/op.D,Y,Y))


class DirectHistory:
    """Reference normal-frame IVP invoking the unchanged KM2A physical RHS."""
    def __init__(self,op,J0,nu0,T,*,rtol=2e-12,atol=2e-14):
        self.op=op;self.J0,self.nu0,self.T=_validate(op,J0,nu0,T)
        shape=self.J0.shape
        self.rtol=float(rtol);self.atol=float(atol)
        self.sol=solve_ivp(lambda t,y:op.rhs(y.reshape(shape),self.nu0).ravel(),
                          (0,self.T),self.J0.ravel(),method='DOP853',dense_output=True,
                          rtol=rtol,atol=atol)
        if not self.sol.success:raise RuntimeError(self.sol.message)
    def carrier(self,t):
        if not np.isfinite(t) or not 0<=t<=self.T:raise ValueError('outside time support')
        return self.sol.sol(t).reshape(self.J0.shape)
    def moment(self,t):return self.op.source(self.carrier(t))


class VolterraHistory:
    """Unknown electron source M_e solved by an 18x18 causal system per panel.

    Endpoints preserve full angular memory. Midpanel polynomial values are not
    the same observable as reconstructed moments. Coarse steps are not asserted
    positivity preserving. Error acceptance is external and fixture scoped.
    """
    def __init__(self,op,J0,nu0,T,panels:int):
        self.op=op;self.J0,self.nu0,self.T=_validate(op,J0,nu0,T)
        if not isinstance(panels,(int,np.integer)) or isinstance(panels,bool) or panels<1:
            raise ValueError('positive integer panels required')
        self.panels=int(panels);self.h=self.T/self.panels
        self.d=self.nu0*op.D
        self.Y0=op.to_electron(self.J0)
        # R_n maps a flattened source to electron scattering gain at node n.
        self.R=(3/(8*np.pi))*np.einsum('nac,ndb->nabcd',op.Pe,op.Pe).reshape(-1,9,9)
        self.electron_endpoints=np.empty((self.panels+1,)+self.Y0.shape)
        self.electron_endpoints[0]=self.Y0
        self.stages=np.empty((self.panels,3,3,3))
        W=[exponential_weights(self.d*self.h,r) for r in (.5,1.)]
        B=[np.einsum('n,nj,nab->jab',op.we,w,self.R) for w in W]
        matrix=np.block([[np.eye(9)-B[0][1],-B[0][2]],[-B[1][1],np.eye(9)-B[1][2]]])
        self.stage_condition=float(np.linalg.cond(matrix))
        self.max_panel_loss_depth=float(np.max(self.d*self.h))
        if not np.isfinite(self.stage_condition) or self.stage_condition>1e12:
            raise ArithmeticError('ill-conditioned source collocation matrix')
        for k in range(self.panels):
            Y=self.electron_endpoints[k]
            M0=self._source_e(Y)
            rhs=[]
            for r,block in zip((.5,1.),B):
                free=self._source_e(np.exp(-self.d*self.h*r)[:,None,None]*Y)
                rhs.append(free.ravel()+block[0]@M0.ravel())
            unknown=np.linalg.solve(matrix,np.concatenate(rhs)).reshape(2,3,3)
            self.stages[k]=np.concatenate([M0[None],unknown],axis=0)
            self.electron_endpoints[k+1]=self._advance(Y,self.stages[k],W[1],1.)
    def _source_e(self,Y):return np.einsum('n,nij->ij',self.op.we,Y)
    def _advance(self,Y,stages,weights,r):
        gain=np.einsum('nab,jb->nja',self.R,stages.reshape(3,9))
        out=np.exp(-self.d*self.h*r)[:,None]*Y.reshape(-1,9)
        out+=np.einsum('nj,nja->na',weights,gain)
        return out.reshape(Y.shape)
    def _panel(self,t):
        if not np.isfinite(t) or not 0<=t<=self.T:raise ValueError('outside time support')
        k=min(int(t/self.h),self.panels-1)
        return k,min(1.,max(0.,(t-k*self.h)/self.h))
    def electron(self,t):
        k,r=self._panel(t)
        if t==0:return self.Y0.copy()
        if t==self.T:return self.electron_endpoints[-1].copy()
        return self._advance(self.electron_endpoints[k],self.stages[k],exponential_weights(self.d*self.h,r),r)
    @staticmethod
    def to_normal(op,Y):
        return np.einsum('nki,nkl,nlj->nij',op.S,Y,op.S)/op.D[:,None,None]**4
    def carrier(self,t):
        self._panel(t)
        if self.nu0==0 or t==0:return self.J0.copy()
        return self.to_normal(self.op,self.electron(t))
    def moment(self,t):return self._source_e(self.electron(t))
    def source_polynomial(self,t):
        k,r=self._panel(t)
        l=np.array([2*r*r-3*r+1,4*r-4*r*r,2*r*r-r])
        return np.einsum('j,jab->ab',l,self.stages[k])
    def initial_source(self,t):
        self._panel(t)
        return self._source_e(np.exp(-self.d*t)[:,None,None]*self.Y0)
    def gain_history(self,t):return self.moment(t)-self.initial_source(t)
