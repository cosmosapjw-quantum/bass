"""Bounded research utilities derived from the VigilODE transfer study.

Linear diagnostics only: no nonlinear, PDE, physical-domain, or global-error
certificate. Distinct diagonal blocks are allowed (SDIRK/full-half generally do
NOT have one common W). Matrices are immutable snapshots, factors reused only
when exact matrix bytes and dimensions match. O(s*n^3) worst-case setup,
O(s^2*n^2) action/solve; n<=128, s<=32 for this dense reference backend.
"""
from dataclasses import dataclass
import warnings
import numpy as np
from scipy.linalg import lu_factor,lu_solve,LinAlgWarning


def array(value,shape=None):
    out=np.array(value,dtype=float,copy=True,order='C')
    if shape is not None and out.shape!=shape:raise ValueError('shape mismatch')
    if not np.isfinite(out).all():raise ValueError('nonfinite input')
    return out


@dataclass(frozen=True)
class LinearResult:
    value:np.ndarray
    residual:np.ndarray
    relative_backward_error:float
    factorization_count:int
    solve_count:int
    claim:str='LINEAR_DIAGNOSTIC_NOT_UNIFORM_NONLINEAR_CERTIFICATE'


class CausalSystem:
    def __init__(self,diagonal,lower):
        d=array(diagonal)
        if d.ndim!=3 or d.shape[1]!=d.shape[2] or not 1<=d.shape[0]<=32 or not 1<=d.shape[1]<=128:
            raise ValueError('square blocks required within dense reference limits')
        self.s,self.n=d.shape[:2];l=array(lower,(self.s,self.s,self.n,self.n))
        for i in range(self.s):
            for j in range(i,self.s):
                if np.any(l[i,j]!=0):raise ValueError('lower coupling must be EXACTLY strictly lower')
        self.diagonal=d;self.lower=l;self.diagonal.setflags(write=False);self.lower.setflags(write=False)
        cache={};self.factors=[]
        for block in d:
            key=(block.shape,block.tobytes())
            if key not in cache:
                with warnings.catch_warnings():
                    warnings.simplefilter('error',LinAlgWarning)
                    try:fac=lu_factor(block,check_finite=True)
                    except (LinAlgWarning,ValueError) as exc:raise ValueError('singular block') from exc
                if np.any(np.diag(fac[0])==0):raise ValueError('singular block')
                cache[key]=fac
            self.factors.append(cache[key])
        self.factorization_count=len(cache)

    def apply(self,value,transpose=False):
        x=array(value,(self.s,self.n));out=np.empty_like(x)
        for i in range(self.s):
            if transpose:
                out[i]=self.diagonal[i].T@x[i]
                for j in range(i+1,self.s):out[i]+=self.lower[j,i].T@x[j]
            else:
                out[i]=self.diagonal[i]@x[i]
                for j in range(i):out[i]+=self.lower[i,j]@x[j]
        if not np.isfinite(out).all():raise ArithmeticError('operator overflow')
        return out

    def dense(self):
        out=np.zeros((self.s*self.n,self.s*self.n))
        for i in range(self.s):
            for j in range(i+1):
                out[i*self.n:(i+1)*self.n,j*self.n:(j+1)*self.n]=self.diagonal[i] if i==j else self.lower[i,j]
        return out

    def solve(self,rhs,transpose=False):
        b=array(rhs,(self.s,self.n));x=np.zeros_like(b)
        indices=range(self.s-1,-1,-1) if transpose else range(self.s)
        for i in indices:
            r=b[i].copy()
            if transpose:
                for j in range(i+1,self.s):r-=self.lower[j,i].T@x[j]
            else:
                for j in range(i):r-=self.lower[i,j]@x[j]
            x[i]=lu_solve(self.factors[i],r,trans=int(bool(transpose)),check_finite=True)
            if not np.isfinite(x[i]).all():raise ArithmeticError('solve overflow')
        residual=b-self.apply(x,transpose=transpose)
        A=self.dense();A=A.T if transpose else A
        scale=np.linalg.norm(A,np.inf)*np.linalg.norm(x.ravel(),np.inf)+np.linalg.norm(b.ravel(),np.inf)
        if not np.isfinite(scale):raise ArithmeticError('backward-error scaling overflow')
        backward=float(np.linalg.norm(residual.ravel(),np.inf)/scale) if scale else 0.0
        x.setflags(write=False);residual.setflags(write=False)
        return LinearResult(x,residual,backward,self.factorization_count,self.s)


def original_residual_bridge(A_original,b_original,A_proposal,b_proposal,z):
    """Returns original residual, not an automatic admissibility decision."""
    z=array(z)
    if z.ndim!=1:raise ValueError('vector correction required')
    n=len(z);Ao=array(A_original,(n,n));Ap=array(A_proposal,(n,n));bo=array(b_original,(n,));bp=array(b_proposal,(n,))
    rp=Ap@z-bp
    bridge=rp+(Ao-Ap)@z-(bo-bp)
    direct=Ao@z-bo
    if not np.isfinite(bridge).all() or not np.isfinite(direct).all():raise ArithmeticError('residual overflow')
    return {'proposal_residual':rp,'original_residual':direct,'bridge_residual':bridge,
            'bridge_difference':float(np.linalg.norm(bridge-direct,np.inf)),
            'claim':'NO_FORWARD_OR_NONLINEAR_CERTIFICATE'}


def linear_goal_error(system,rhs,approximate,goal):
    """g^T(error)=lambda^T(b-A*xhat) for a frozen LINEAR system."""
    b=array(rhs,(system.s,system.n));x=array(approximate,b.shape);g=array(goal,b.shape)
    adjoint=system.solve(g,transpose=True);r=b-system.apply(x)
    return float(np.vdot(adjoint.value,r)),adjoint
