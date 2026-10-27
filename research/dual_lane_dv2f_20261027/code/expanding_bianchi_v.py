"""DV2-F: coframe-compatible, diagonal prescribed expanding Bianchi V.

Signature (-,+,+,+); u=t/T_star, coordinates in c*T_star units; rates times
T_star. Metric/(cT*)^2=-du^2+ax^2 exp(-2a0*z)dx^2+
ay^2 exp(-2a0*z)dy^2+az^2 dz^2. A_z=a0/az; no independent A history.
Raw angular Jacobian evolves with 3 sigma_nn+2 A.n. Photon energy is not the
Doppler factor of the frozen Mobius map. No EFE, tilt, spectrum, normalization
or positivity projection. The two parent memory modules remain unchanged.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import sys
import numpy as np
from scipy.integrate import solve_ivp
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'vendor'))
import polarization as P8
from harmonic_history import HarmonicHistory
from classb_streaming import classb_matrix
ALPHA=3/(8*np.pi)

@dataclass(frozen=True)
class CoframeProfile:
    h: tuple=(.12,.45,.28)
    d: tuple=(.16,-.12,.08)
    a0: float=.7
    nu0: float=1.1
    nuamp: float=.2
    def __post_init__(self):
        for name in ('h','d'):
            a=np.asarray(getattr(self,name),float)
            if a.shape!=(3,) or not np.isfinite(a).all():raise ValueError('finite three directional rate coefficients required')
            object.__setattr__(self,name,tuple(float(x) for x in a))
        if not np.isfinite([self.a0,self.nu0,self.nuamp]).all() or self.nu0<abs(self.nuamp):
            raise ValueError('finite structural rate and nonnegative bounded opacity required')
    def logs(self,t):return np.asarray(self.h)*t+.5*np.asarray(self.d)*t*t
    def scales(self,t):
        a=np.exp(self.logs(t))
        if not np.isfinite(a).all() or np.min(a)<=0:raise ValueError('nonpositive or nonfinite scale factor')
        return a
    def rates(self,t):return np.asarray(self.h)+np.asarray(self.d)*t
    def fields(self,t):
        r=self.rates(t);H=float(np.mean(r));return H,np.diag(r-H)
    def structure(self,t):return np.array([0.,0.,self.a0/self.scales(t)[2]])
    def structure_rate(self,t):return -self.rates(t)[2]*self.structure(t)[2]
    def rate(self,t):return self.nu0+self.nuamp*np.cos(2*t)
    def kappa(self,t):
        """Compatibility name for integrated opacity, NOT a curvature parameter."""
        return self.nu0*t+.5*self.nuamp*np.sin(2*t)


def analytic_rates(n,E,H,S,A):
    """Direction, log energy, screen and log angular-area rates; no projection."""
    sn=n@S.T;s=np.einsum('ni,ni->n',n,sn);alpha=n@A
    v=-sn+(s+alpha)[:,None]*n-A
    B=np.einsum('ni,nj->nij',v,n)-np.einsum('ni,nj->nij',n,v)
    return v,-H-s,B@E,3*s+2*alpha


def _solve(rhs,y0,end,rtol,atol):
    if not np.isfinite(end) or not 0<end<=.6:raise ValueError('bounded support requires 0<end<=.6')
    if not (np.isfinite(rtol) and np.isfinite(atol) and rtol>0 and atol>0):raise ValueError('positive finite ODE tolerances required')
    sol=solve_ivp(rhs,(0.,float(end)),np.asarray(y0,float).ravel(),method='DOP853',rtol=rtol,atol=atol,dense_output=True)
    if not sol.success:raise RuntimeError(sol.message)
    return sol


class ExpandingGeometry:
    """Coupled ray/screen/redshift/angular-area supplier, no P8 or radiation RHS.

    The last variable eta_z=int A.n du equals a0*(z-z_initial). It is kept
    separately to test Jac*r^3*volume*exp(-2eta_z)=1. A coordinate Hamiltonian
    and tangent-map area provide genuinely distinct checks of this identity.
    """
    def __init__(self,grid,profile,end,rtol=2e-12,atol=2e-14):
        self.grid,self.profile,self.end=grid,profile,float(end);self.n=len(grid.w)
        self.screen0=np.stack([grid.bt,grid.bp],axis=2);self._cache={}
        y=np.zeros((self.n,12));y[:,:3]=grid.n;y[:,4:10]=self.screen0.reshape(self.n,6)
        def rhs(t,yy):
            z=yy.reshape(self.n,12);H,S=profile.fields(t);A=profile.structure(t)
            v,lr,dE,lj=analytic_rates(z[:,:3],z[:,4:10].reshape(self.n,3,2),H,S,A)
            return np.column_stack([v,lr,dE.reshape(self.n,6),lj,z[:,:3]@A]).ravel()
        self.rhs=rhs;self.solution=_solve(rhs,y,end,rtol,atol)
    def _time(self,t):
        t=float(t)
        if not np.isfinite(t) or t<0 or t>self.end+1e-14:raise ValueError('time outside geometry support')
        return min(t,self.end)
    def at(self,t):
        t=self._time(t)
        if t not in self._cache:
            z=self.solution.sol(t).reshape(self.n,12);r=np.exp(z[:,3]);jac=np.exp(z[:,10]);w=self.grid.w*jac
            if not np.isfinite(z).all() or np.min(r)<=0 or np.min(jac)<=0:raise ArithmeticError('invalid geometric carrier')
            self._cache[t]={'e':z[:,:3],'screen':z[:,4:10].reshape(self.n,3,2),
                'mu':r,'jac':jac,'eta_z':z[:,11],'w':w,'v':w*r**4}
        return self._cache[t]
    def moment(self,t,J):return np.einsum('n,nij->ij',self.at(t)['w'],np.asarray(J,float))
    def free_state(self,t,J0):
        X=np.einsum('nia,nij,njb->nab',self.screen0,J0,self.screen0)
        z=self.at(t)
        return z['mu'][:,None,None]**4*np.einsum('nia,nab,njb->nij',z['screen'],X,z['screen'])


class CoordinateRays:
    """Independent coordinate null Hamilton equations, not the tetrad flow.

    H_null=sqrt(exp(2a0 z)[(Px/ax)^2+(Py/ay)^2]+(Pz/az)^2).
    Px,Py are Killing constants; initial tetrad energy is one at z0=.13.
    No calls to structure(), fields(), P8 or the characteristic supplier.
    """
    def __init__(self,n0,profile,end,rtol=2e-12,atol=2e-14):
        n0=np.asarray(n0,float)
        if n0.ndim!=2 or n0.shape[1]!=3 or not np.isfinite(n0).all() or np.max(abs(np.linalg.norm(n0,axis=1)-1))>1e-10:raise ValueError('unit finite initial directions required')
        self.profile,self.end,self.n=profile,float(end),len(n0);self.z0=.13
        y=np.zeros((self.n,6));y[:,2]=self.z0;y[:,3:]=n0
        y[:,3:5]*=np.exp(-profile.a0*self.z0)
        def rhs(t,yy):
            y=yy.reshape(self.n,6);a=profile.scales(t);ez=np.exp(profile.a0*y[:,2])
            p=np.column_stack([ez*y[:,3]/a[0],ez*y[:,4]/a[1],y[:,5]/a[2]])
            r=np.linalg.norm(p,axis=1);out=np.zeros_like(y)
            out[:,0]=ez*p[:,0]/(a[0]*r);out[:,1]=ez*p[:,1]/(a[1]*r);out[:,2]=p[:,2]/(a[2]*r)
            out[:,5]=-profile.a0*(p[:,0]**2+p[:,1]**2)/r
            return out.ravel()
        self.solution=_solve(rhs,y,end,rtol,atol)
    def at(self,t):
        if not np.isfinite(t) or not 0<=t<=self.end:raise ValueError('time outside coordinate support')
        y=self.solution.sol(t).reshape(self.n,6);a=self.profile.scales(t);ez=np.exp(self.profile.a0*y[:,2])
        p=np.column_stack([ez*y[:,3]/a[0],ez*y[:,4]/a[1],y[:,5]/a[2]]);r=np.linalg.norm(p,axis=1)
        return p/r[:,None],r,y[:,2]


class TangentGeometry:
    """Differentiate the sphere flow, evolve two initial tangents, not logJac."""
    def __init__(self,grid,profile,end,rtol=2e-12,atol=2e-14):
        self.n=len(grid.w);self.end=float(end)
        y=np.column_stack([grid.n,np.stack([grid.bt,grid.bp],axis=2).reshape(self.n,6)])
        def rhs(t,yy):
            z=yy.reshape(self.n,9);n=z[:,:3];Q=z[:,3:].reshape(self.n,3,2)
            _,S=profile.fields(t);A=profile.structure(t);sn=n@S.T;s=np.einsum('ni,ni->n',n,sn);alpha=n@A
            v=-sn+(s+alpha)[:,None]*n-A
            D=-S[None]+(s+alpha)[:,None,None]*np.eye(3)+np.einsum('ni,nj->nij',n,2*sn+A)
            return np.column_stack([v,(D@Q).reshape(self.n,6)]).ravel()
        self.solution=_solve(rhs,y,end,rtol,atol)
    def area(self,t):
        if not np.isfinite(t) or not 0<=t<=self.end:raise ValueError('time outside tangent support')
        z=self.solution.sol(t).reshape(self.n,9);Q=z[:,3:].reshape(self.n,3,2)
        return np.einsum('ni,ni->n',z[:,:3],np.cross(Q[:,:,0],Q[:,:,1]))


class ExpandingDirect:
    """Cartesian physical J ODE calling pinned P8, not the memory pullback."""
    def __init__(self,geo,J0,rtol=2e-12,atol=2e-14):
        self.geo=geo;J0=np.asarray(J0,float)
        if J0.shape!=(geo.n,3,3) or not np.isfinite(J0).all():raise ValueError('finite initial carrier/grid required')
        def rhs(t,y):
            z=geo.at(t);e=z['e'];J=y.reshape(geo.n,3,3);H,S=geo.profile.fields(t);A=geo.profile.structure(t)
            s=np.einsum('ni,ij,nj->n',e,S,e);P=np.eye(3)-np.einsum('ni,nj->nij',e,e)
            M=np.einsum('n,nij->ij',z['w'],J);gain=ALPHA*np.einsum('nia,ab,nbj->nij',P,M,P,optimize=True)
            return (-4*(H+s)[:,None,None]*J+P8.tensor_rate(J,e,H,S,np.zeros(3),np.zeros((3,3)),A)
                    +geo.profile.rate(t)*(gain-J)).ravel()
        self.rhs=rhs;self.solution=_solve(rhs,J0,geo.end,rtol,atol)
    def state(self,t):return self.solution.sol(self.geo._time(t)).reshape(self.geo.n,3,3)
    def moment(self,t):return self.geo.moment(t,self.state(t))


class ExpandingHarmonic(HarmonicHistory):
    """Pinned analytic shear + class-B matrices; coefficients above L are zero.

    Fixed canonical structural axis, 2<=L<=8. No quadrature, P8, direct source
    or geometry-solution callbacks. The prescribed metric/rates alone are shared.
    """
    def __init__(self,profile,initial,L,end,rtol=2e-12,atol=2e-14):
        if isinstance(L,bool) or not isinstance(L,int) or not 2<=L<=8:raise ValueError('integer 2<=L<=8 required')
        b0=classb_matrix(0,L,L,[0,0,1])
        if np.max(abs(b0.imag))>2e-12:raise ArithmeticError('scalar reality violation')
        self.B0=b0.real;self.B2=classb_matrix(2,L,L,[0,0,1])
        super().__init__(profile,initial,L,end,rtol,atol)
    def rhs(self,t,y):
        out=super().rhs(t,y);n0,n2=self.n0,self.n2;a=self.profile.structure(t)[2]
        p=y[2*n0:2*n0+n2]+1j*y[2*n0+n2:];dp=self.B2@p
        return out+a*np.r_[self.B0@y[:n0],self.B0@y[n0:2*n0],dp.real,dp.imag]
