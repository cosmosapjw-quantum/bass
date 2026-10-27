"""KM2B fixed-beta, flat normal-time polarized Thomson histories.

Normal-time nu0=n_e_star*sigma_T*c, beta=v_e/c. Code rates may be multiplied
by T_star for dimensionless t/T_star. No frequency validity, material feedback,
positivity projection, weight renormalization, or production-runner promotion.
The Volterra solver never calls a direct history or its RHS. It retains the
complete initial carrier and angle-dependent attenuated history.
"""
from __future__ import annotations
from pathlib import Path
import sys
import numpy as np
from scipy.integrate import solve_ivp
from scipy.linalg import lu_factor,lu_solve
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'vendor'))
from tilted_collision import TiltedThomson


def _parameters(op,J0,nu0,T):
    if not isinstance(op,TiltedThomson):raise TypeError('Require pinned TiltedThomson')
    J0=op._carrier(J0).copy();nu0=float(nu0);T=float(T)
    if not np.isfinite(nu0) or nu0<0:raise ValueError('finite nu0>=0 required')
    if not np.isfinite(T) or T<=0:raise ValueError('finite T>0 required')
    return J0,nu0,T


def conserved(op,J):
    """Normal-slice gamma(rho-beta.q)=int dOmega_e tr(Y)/D, fixed beta."""
    return float(np.einsum('n,n,n->',op.w,op.D,np.trace(J,axis1=1,axis2=2)))


def from_electron(op,Y):
    return np.einsum('nki,nkl,nlj->nij',op.S,Y,op.S)/op.D[:,None,None]**4


def stationary_carrier(op,J0):
    """Continuum stationary state set by the normal-slice invariant.

    No finite-grid normalization is substituted for 4*pi*gamma.
    Raw non-exact quadrature need not make this an exact discrete equilibrium.
    """
    amplitude=conserved(op,J0)/(4*np.pi*op.gamma)
    return amplitude*(np.eye(3)-np.einsum('ni,nj->nij',op.n,op.n))/(2*op.D[:,None,None]**4)


def weighted_norm(op,J):
    """Hermitian Hilbert-Schmidt norm in electron variables, weight1/D.

    P8's real S+A representation has the same Frobenius norm as physical S+iA.
    """
    Y=op.to_electron(J)
    return float(np.sqrt(max(0.,np.einsum('n,nij,nij->',op.we/op.D,Y,Y))))


def exponential_weights(z,r):
    """Exact integrals z*int_0^r exp[-z(r-x)] l_j(x) dx, j=0,mid,1.

    z=nu0*D*h>=0; r is the fraction of the CURRENT full panel. Series avoid
    cancellation for small z*r; no angular or temporal renormalization.
    Negative cardinal weights can occur; no general positivity assertion.
    """
    z=np.asarray(z,float);r=float(r)
    if z.ndim!=1 or not np.isfinite(z).all() or np.any(z<0) or not np.isfinite(r) or not 0<=r<=1:
        raise ValueError('Require finite vector z>=0 and 0<=r<=1')
    x=z*r;I=np.zeros((len(z),3));small=x<.75
    for k in range(3):
        xx=x[small];term=xx/(k+1);acc=term.copy()
        for m in range(1,32):
            term*=(-xx)/(m+k+1);acc+=term
        I[small,k]=r**k*acc
    if np.any(~small):
        xx=x[~small];a=-np.expm1(-xx)
        I[~small,0]=a
        I[~small,1]=r*(1-a/xx)
        I[~small,2]=r*r*(1-2/xx+2*a/xx**2)
    return np.stack([I[:,0]-3*I[:,1]+2*I[:,2],4*I[:,1]-4*I[:,2],-I[:,1]+2*I[:,2]],axis=1)


class TiltedDirect:
    """Normal-frame carrier ODE invoking the exact pinned KM2A generator."""
    def __init__(self,op,J0,nu0,T,rtol=2e-11,atol=2e-13):
        self.J0,self.nu0,self.T=_parameters(op,J0,nu0,T);self.op=op
        self.sol=None
        if self.nu0:
            shape=self.J0.shape
            self.sol=solve_ivp(lambda t,y:op.rhs(y.reshape(shape),self.nu0).ravel(),(0.,self.T),self.J0.ravel(),method='DOP853',rtol=rtol,atol=atol,dense_output=True)
            if not self.sol.success:raise RuntimeError(self.sol.message)
        self.nfev=0 if self.sol is None else self.sol.nfev

    def carrier(self,t):
        t=float(t)
        if not np.isfinite(t) or not 0<=t<=self.T:raise ValueError('No extrapolation')
        return self.J0.copy() if self.sol is None or t==0 else self.sol.sol(t).reshape(self.J0.shape)

    def moment(self,t):return self.op.source(self.carrier(t))


class TiltedVolterra:
    """Independent 18x18 causal source solve with exact exponential weights.

    In electron angular coordinates, Ydot=d_i*(B_i M-Y), M=sum w_e Y.
    Complete Y at panel boundaries is an attenuated-history accumulator, not
    a 9-state Markov closure. Unknown mid/end sources are solved together.
    Stored boundary fields permit arbitrary-time carrier reconstruction.
    """
    def __init__(self,op,J0,nu0,T,panels):
        self.J0,self.nu0,self.T=_parameters(op,J0,nu0,T);self.op=op
        if not isinstance(panels,(int,np.integer)) or isinstance(panels,(bool,np.bool_)) or panels<1:
            raise ValueError('positive integer panels required')
        self.N=int(panels);self.h=self.T/self.N;self.d=self.nu0*op.D
        self.Y0=op.to_electron(self.J0);self.w=op.we
        self.B=(3/(8*np.pi))*np.einsum('nik,njl->nijkl',op.Pe,op.Pe).reshape(len(self.w),9,9)
        self.Y_edges=[self.Y0.copy()];self.stages=[]
        self.max_linear_residual=0.;self.condition=1.
        if not self.nu0:
            m=self._moment(self.Y0)
            self.stages=[np.stack([m,m,m]) for _ in range(self.N)]
            self.Y_edges=[self.Y0.copy() for _ in range(self.N+1)]
            return
        wmid=exponential_weights(self.d*self.h,.5);wend=exponential_weights(self.d*self.h,1.)
        blocks=[np.einsum('n,nj,nab->jab',self.w,w,self.B) for w in [wmid,wend]]
        p,q=blocks
        A=np.block([[np.eye(9)-p[1],-p[2]],[-q[1],np.eye(9)-q[2]]])
        self.condition=float(np.linalg.cond(A))
        if not np.isfinite(self.condition) or self.condition>1e12:raise ArithmeticError('Ill-conditioned collocation panel; refine explicitly')
        lu=lu_factor(A)
        decay=[np.exp(-self.d*self.h*r) for r in [.5,1.]]
        for _ in range(self.N):
            Y=self.Y_edges[-1];M0=self._moment(Y).ravel()
            rhs=np.r_[self._moment(decay[0][:,None,None]*Y).ravel()+p[0]@M0,
                      self._moment(decay[1][:,None,None]*Y).ravel()+q[0]@M0]
            sol=lu_solve(lu,rhs)
            self.max_linear_residual=max(self.max_linear_residual,float(np.max(abs(A@sol-rhs))))
            stage=np.stack([M0,sol[:9],sol[9:]]).reshape(3,3,3)
            self.stages.append(stage)
            self.Y_edges.append(decay[1][:,None,None]*Y+self._gain_sum(wend,stage))

    def _moment(self,Y):return np.einsum('n,nij->ij',self.w,Y)

    def _gain_sum(self,weights,stage):
        return np.einsum('nj,nab,jb->na',weights,self.B,stage.reshape(3,9)).reshape(self.Y0.shape)

    def _where(self,t):
        t=float(t)
        if not np.isfinite(t) or not 0<=t<=self.T:raise ValueError('No extrapolation')
        if t==self.T:return self.N-1,1.
        j=min(int(t/self.h),self.N-1)
        return j,float((t-j*self.h)/self.h)

    def electron_carrier(self,t):
        j,r=self._where(t)
        if not self.nu0:return self.Y0.copy()
        if t==0:return self.Y0.copy()
        if r==1.:return self.Y_edges[j+1].copy()
        if r==0.:return self.Y_edges[j].copy()
        W=exponential_weights(self.d*self.h,r)
        return np.exp(-self.d*self.h*r)[:,None,None]*self.Y_edges[j]+self._gain_sum(W,self.stages[j])

    def carrier(self,t):
        self._where(t)
        if not self.nu0 or t==0:return self.J0.copy()
        return from_electron(self.op,self.electron_carrier(t))

    def moment(self,t):return self._moment(self.electron_carrier(t))

    def source_polynomial(self,t):
        j,x=self._where(t)
        return np.einsum('j,jab->ab',np.array([1-3*x+2*x*x,4*x-4*x*x,-x+2*x*x]),self.stages[j])

    def initial_memory(self,t):
        self._where(t)
        return self._moment(np.exp(-self.d*float(t))[:,None,None]*self.Y0)

    def history_integral(self,t,order=10):
        """Independent all-past GL integration of the collocated source polynomial.

        This diagnostic does not march unknown sources or consume direct data.
        """
        self._where(t);x,w=np.polynomial.legendre.leggauss(order)
        out=self.initial_memory(t)
        for j in range(self.N):
            lo=j*self.h;hi=min((j+1)*self.h,float(t))
            if hi<=lo:break
            for s,weight in zip(lo+(x+1)*(hi-lo)/2,w*(hi-lo)/2):
                M=self.source_polynomial(s).ravel()
                Y=np.einsum('nab,b->na',self.B,M).reshape(self.Y0.shape)
                out+=weight*self._moment((self.d*np.exp(-self.d*(t-s)))[:,None,None]*Y)
        return out
