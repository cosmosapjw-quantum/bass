"""BF3-E: source-only Volterra integration on a static periodic lapse.

Uses the SAME Fourier/Legendre collocation generator as lapse_field, not a
finite-time inverse interpolation identified with that generator. Units and
Y=N^4 W are inherited from BF3-D. Static nonnegative proper opacity only.
The scalar phase-space streaming/loss propagator contains no radiation source.
Angular source has nine real components per x. Full initial carrier is retained.
No clipping, normalization, native fallback, or claimed positivity theorem.
"""
from __future__ import annotations
import numpy as np
from scipy.linalg import expm, lu_factor, lu_solve
from .lapse_field import FieldGrid, _oracle


def exponential_weights(A, h: float, r: float = 1.):
    """U(rh), W_j=h*int_0^r exp(h*A*(r-v))*L_j(v)dv, j=0,1,2.

    A singular generator is allowed. An augmented exponential evaluates all
    polynomial moments without A^{-1} or cancellation-prone recurrences.
    L0=1-3v+2v^2, L1=4v-4v^2, L2=2v^2-v.
    """
    A=np.asarray(A,float)
    if A.ndim!=2 or A.shape[0]!=A.shape[1] or not np.isfinite(A).all():
        raise ValueError('Finite square real streaming/loss matrix required')
    if not np.isfinite(h) or h<=0 or not np.isfinite(r) or r<0 or r>1:
        raise ValueError('Require h>0 and 0<=r<=1')
    n=len(A)
    if r==0:return np.eye(n),np.zeros((3,n,n))
    block=np.zeros((4*n,4*n));block[:n,:n]=h*A
    for j in range(3):block[j*n:(j+1)*n,(j+1)*n:(j+2)*n]=np.eye(n)
    e=expm(r*block);a,b,c=e[:n,n:2*n],e[:n,2*n:3*n],e[:n,3*n:]
    W=h*np.stack((a-3*b+4*c,4*b-8*c,4*c-b))
    return e[:n,:n],W


class LapseMemory:
    """Bounded dense reference solver; explicit python_oracle backend required.

    No calls to LapseField.rhs/direct/split/gain or any radiation ODE. The phase
    matrix is nx*nmu; source stage solves are 18*nx. Azimuth and four real screen
    components share the scalar phase propagator. No angular modes are deleted.
    """
    def __init__(self,grid:FieldGrid,metric,nu_star,*,backend=None):
        _oracle(backend);self.grid,self.metric=grid,metric
        value=nu_star(grid.x) if callable(nu_star) else nu_star
        self.nu=np.broadcast_to(np.asarray(value,float),(grid.nx,)).copy()
        self.N=np.asarray(metric.N(grid.x),float)
        if self.N.shape!=(grid.nx,) or not np.isfinite(self.N).all() or np.any(self.N<=0):
            raise ValueError('Finite positive lapse required')
        if not np.isfinite(self.nu).all() or np.any(self.nu<0):
            raise ValueError('Finite nonnegative proper opacity required')
        self.rate=self.N*self.nu;self.nphase=grid.nx*grid.nmu
        if self.nphase>800:raise ValueError('Dense scoped reference supports nx*nmu<=800')
        Dx=grid.dx(np.eye(grid.nx))
        vx=metric.cbar*self.N[:,None]*grid.mu[None,:]
        vm=-metric.cbar*metric.dN(grid.x)[:,None]*(1-grid.mu[None,:]**2)
        self.A=(-vx.ravel()[:,None]*np.kron(Dx,np.eye(grid.nmu))
                -vm.ravel()[:,None]*np.kron(np.eye(grid.nx),grid.Dmu)
                -np.diag(np.repeat(self.rate,grid.nmu)))
        if not np.isfinite(self.A).all():raise ValueError('Nonfinite generator')
        E=grid.E.reshape(grid.nmu,grid.nphi,3,2)
        Z=np.einsum('ipak,jpck->ijpac',E,E,optimize=True)
        T=np.einsum('ijpac,ijpbd->ijabcd',Z,Z,optimize=True)
        self._angular=(3/(8*np.pi))*(2*np.pi/grid.nphi)*grid.wmu[:,None,None,None,None,None]*T
        self._angular=self._angular.reshape(grid.nmu,grid.nmu,9,9)
        self._cache={};self._exp_cache={0.:np.eye(self.nphase)}

    def apply_phase(self,P,y):
        g=self.grid
        return (P@np.asarray(y).reshape(self.nphase,-1)).reshape(g.shape)

    def scaled_source(self,y):
        g=self.grid;y=g.check(y,signed=True).reshape(g.nx,-1,2,2)
        cart=g.E[None]@y@g.E[None].swapaxes(-1,-2)
        return np.einsum('a,xaij->xij',g.w,cart,optimize=True)

    def source(self,y):
        return self.scaled_source(y)/self.N[:,None,None]**4

    def inject(self,S):
        """B S for scaled source S=N^4 M, including coordinate rate once."""
        g=self.grid;S=np.asarray(S,float)
        if S.shape!=(g.nx,3,3) or not np.isfinite(S).all():raise ValueError('Invalid scaled source')
        E=g.E[None]
        out=(3/(8*np.pi))*self.rate[:,None,None,None]*(E.swapaxes(-1,-2)@S[:,None]@E)
        return out.reshape(g.shape)

    def source_block(self,P):
        """Exact finite-grid L P B, assembled without materializing carrier RHS."""
        g=self.grid
        C=np.einsum('xiyj,ijab,y->xayb',P.reshape(g.nx,g.nmu,g.nx,g.nmu),
                    self._angular,self.rate,optimize=True)
        return C.reshape(9*g.nx,9*g.nx)

    def propagator(self,t):
        t=float(t)
        if not np.isfinite(t) or t<0:raise ValueError('Nonnegative lag required')
        if t not in self._exp_cache:self._exp_cache[t]=expm(t*self.A)
        return self._exp_cache[t]

    def kernel(self,lag):
        """Physical-source kernel M(t)=b+int K(lag) M(s) ds."""
        C=self.source_block(self.propagator(lag))
        n4=np.repeat(self.N**4,9)
        return C*n4[None,:]/n4[:,None]

    def _panel(self,h,r):
        key=(float(h),float(r))
        if key not in self._cache:self._cache[key]=exponential_weights(self.A,*key)
        return self._cache[key]

    def solve(self,y0,tend,panels,*,signed=False):
        y0=self.grid.check(y0,signed=signed).copy()
        if not np.isfinite(tend) or tend<0 or not isinstance(panels,(int,np.integer)) or isinstance(panels,bool) or panels<1:
            raise ValueError('Nonnegative finite end time and positive integer panels required')
        return SourceHistory(self,y0,float(tend),int(panels))


class SourceHistory:
    """Causal source collocation and full carrier reconstruction; no extrapolation."""
    def __init__(self,op,y0,tend,panels):
        self.op,self.initial_state,self.tend,self.panels=op,y0.copy(),tend,panels
        self.times=np.linspace(0,tend,panels+1);self.h=tend/panels
        self.values=[y0.copy()];self.stages=[];self.condition=1.;self.stage_residual=0.
        if tend==0:return
        U1,W1=op._panel(self.h,.5);U2,W2=op._panel(self.h,1.)
        C1=[op.source_block(W) for W in W1];C2=[op.source_block(W) for W in W2]
        I=np.eye(9*op.grid.nx)
        system=np.block([[I-C1[1],-C1[2]],[-C2[1],I-C2[2]]])
        self.condition=float(np.linalg.cond(system))
        if not np.isfinite(self.condition) or self.condition>1e12:
            raise ArithmeticError('Source panel is ill-conditioned; no silent correction')
        LU=lu_factor(system)
        for _ in range(panels):
            ya=self.values[-1];S0=op.scaled_source(ya)
            rhs=np.r_[op.scaled_source(op.apply_phase(U1,ya)).ravel()+C1[0]@S0.ravel(),
                      op.scaled_source(op.apply_phase(U2,ya)).ravel()+C2[0]@S0.ravel()]
            sol=lu_solve(LU,rhs);S1,S2=sol.reshape(2,op.grid.nx,3,3)
            stages=np.stack((S0,S1,S2));self.stages.append(stages.copy())
            yb=op.apply_phase(U2,ya)
            for W,S in zip(W2,stages):yb+=op.apply_phase(W,op.inject(S))
            self.stage_residual=max(self.stage_residual,float(np.max(abs(op.scaled_source(yb)-S2))))
            if not np.isfinite(yb).all():raise ArithmeticError('Nonfinite carrier')
            self.values.append(yb)

    def _location(self,t):
        t=float(t)
        if not np.isfinite(t) or t<0 or t>self.tend:raise ValueError('No extrapolation')
        if self.tend==0:return 0,0.
        j=min(int(t/self.h),self.panels-1);r=(t-self.times[j])/self.h
        return j,float(np.clip(r,0,1))  # Roundoff in time coordinates only, never in fields.

    def at(self,t):
        j,r=self._location(t)
        if self.tend==0:return self.initial_state.copy()
        if abs(r)<2e-14:return self.values[j].copy()
        if abs(r-1)<2e-14:return self.values[j+1].copy()
        U,W=self.op._panel(self.h,r);y=self.op.apply_phase(U,self.values[j])
        for w,S in zip(W,self.stages[j]):y+=self.op.apply_phase(w,self.op.inject(S))
        return y

    def moment(self,t):return self.op.source(self.at(t))

    def source_polynomial(self,t):
        j,r=self._location(t)
        if self.tend==0:return self.op.source(self.initial_state)
        c=np.array([1-3*r+2*r*r,4*r-4*r*r,2*r*r-r])
        S=np.einsum('a,axij->xij',c,self.stages[j])
        return S/self.op.N[:,None,None]**4

    def initial(self,t):
        self._location(t)
        return self.op.apply_phase(self.op.propagator(t),self.initial_state)

    def gain_history(self,t):return self.at(t)-self.initial(t)

    def global_reconstruction(self,t):
        j,r=self._location(t);y=self.initial(t)
        if self.tend==0:return y
        for k in range(j+1):
            frac=1. if k<j else r
            if frac==0:continue
            _,W=self.op._panel(self.h,frac)
            contribution=np.zeros_like(y)
            for w,S in zip(W,self.stages[k]):contribution+=self.op.apply_phase(w,self.op.inject(S))
            end=self.times[k]+frac*self.h
            y+=self.op.apply_phase(self.op.propagator(max(0.,t-end)),contribution)
        return y
