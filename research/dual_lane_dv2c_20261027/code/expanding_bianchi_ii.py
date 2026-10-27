"""DV2-C: coframe-compatible expanding Bianchi-II transport supplier.

Dimensionless u=t/T_star, spatial coordinates in c*T_star. Metric / (cT*)^2:
-du^2 + ax^2 dx^2 + ay^2 dy^2 + az^2(dz-k0*x*dy)^2.
log ai=hi*u+di*u^2/2; curvature=c*n_structure*T_star=k0 az/(ax ay).
No Einstein feedback, small-amplitude expansion, linear momentum map p=Aq,
angular renormalization, clipping or production Rust execution. Fixed z axis.
The unchanged memory interface uses mu=E/E_initial, w=w0*Jac, v=w*mu^4.
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
from curvature_streaming import curvature_matrix
ALPHA=3/(8*np.pi)

@dataclass(frozen=True)
class CoframeProfile:
    h: tuple=(.12,.45,.28)
    d: tuple=(.16,-.12,.08)
    k0: float=.9
    nu0: float=1.1
    nuamp: float=.2
    def __post_init__(self):
        for x in (self.h,self.d):
            a=np.asarray(x,float)
            if a.shape!=(3,) or not np.isfinite(a).all():raise ValueError('finite rate triples required')
        if not np.isfinite([self.k0,self.nu0,self.nuamp]).all() or self.nu0<abs(self.nuamp):
            raise ValueError('finite curvature and nonnegative opacity at all times required')
    def logs(self,t):return np.asarray(self.h)*t+.5*np.asarray(self.d)*t*t
    def scales(self,t):return np.exp(self.logs(t))
    def rates(self,t):return np.asarray(self.h)+np.asarray(self.d)*t
    def fields(self,t):
        r=self.rates(t);H=float(np.mean(r));return H,np.diag(r-H)
    def curvature(self,t):
        b=self.logs(t);return np.diag([0.,0.,self.k0*np.exp(b[2]-b[0]-b[1])])
    def curvature_rate(self,t):
        r=self.rates(t);return (r[2]-r[0]-r[1])*self.curvature(t)[2,2]
    def rate(self,t):return self.nu0+self.nuamp*np.cos(2*t)
    def kappa(self,t):
        """Compatibility API: integrated OPACITY, not the curvature rate k0."""
        return self.nu0*t+.5*self.nuamp*np.sin(2*t)


def cross_matrix(a):
    a=np.atleast_2d(np.asarray(a,float));o=np.zeros((len(a),3,3))
    o[:,0,1]=-a[:,2];o[:,0,2]=a[:,1];o[:,1,0]=a[:,2]
    o[:,1,2]=-a[:,0];o[:,2,0]=-a[:,1];o[:,2,1]=a[:,0]
    return o


def analytic_rates(n,E,H,S,N):
    """Direction, log energy, screen, log area; exact continuum unit n/screen."""
    sn=n@S.T;s=np.einsum('ni,ni->n',n,sn);vS=-sn+s[:,None]*n
    vn=np.cross(n@N.T,n);v=vS+vn
    omega=n@N.T-.5*np.trace(N)*n
    B=np.einsum('ni,nj->nij',vS,n)-np.einsum('ni,nj->nij',n,vS)+cross_matrix(omega)
    return v,-H-s,B@E,3*s


def _solve(rhs,y0,end,rtol,atol):
    if not np.isfinite(end) or not 0<end<=.6:raise ValueError('support 0<end<=.6')
    sol=solve_ivp(rhs,(0.,float(end)),np.asarray(y0).ravel(),method='DOP853',rtol=rtol,atol=atol,dense_output=True)
    if not sol.success:raise RuntimeError(sol.message)
    return sol


class ExpandingGeometry:
    """Characteristic/screen/area provider; no radiation, no P8 calls in RHS.

    Raw geometry dense output is not renormalized. Jac is integrated separately
    from redshift. An independent tangent-map validator checks its area meaning.
    """
    def __init__(self,grid,profile,end,rtol=2e-12,atol=2e-14):
        self.grid,self.profile,self.end=grid,profile,float(end);self.n=len(grid.w)
        self.screen0=np.stack([grid.bt,grid.bp],axis=2);self._cache={}
        y=np.zeros((self.n,11));y[:,:3]=grid.n;y[:,4:10]=self.screen0.reshape(self.n,6)
        def rhs(t,yy):
            z=yy.reshape(self.n,11);H,S=profile.fields(t);N=profile.curvature(t)
            v,lr,dE,lj=analytic_rates(z[:,:3],z[:,4:10].reshape(self.n,3,2),H,S,N)
            return np.column_stack([v,lr,dE.reshape(self.n,6),lj]).ravel()
        self.solution=_solve(rhs,y,end,rtol,atol)
    def _time(self,t):
        t=float(t)
        if not np.isfinite(t) or t<0 or t>self.end+1e-14:raise ValueError('time outside provider support')
        return min(t,self.end)
    def at(self,t):
        t=self._time(t)
        if t not in self._cache:
            z=self.solution.sol(t).reshape(self.n,11);n=z[:,:3];E=z[:,4:10].reshape(self.n,3,2)
            mu=np.exp(z[:,3]);jac=np.exp(z[:,10]);w=self.grid.w*jac
            self._cache[t]={'e':n,'screen':E,'mu':mu,'jacobian':jac,'w':w,'v':w*mu**4}
        return self._cache[t]
    def moment(self,t,J):return np.einsum('n,nij->ij',self.at(t)['w'],J)
    def free_state(self,t,J0):
        X=np.einsum('nia,nij,njb->nab',self.screen0,J0,self.screen0)
        z=self.at(t);return z['mu'][:,None,None]**4*np.einsum('nia,nab,njb->nij',z['screen'],X,z['screen'])


class CoordinateRays:
    """Independent canonical Hamilton equations in the explicit coordinate metric.

    Spatial x,y,z in c*T_star; canonical momenta in an arbitrary common p_star.
    H_null=sqrt((Px/ax)^2+((Py+k0*x*Pz)/ay)^2+(Pz/az)^2).
    Py and Pz are Killing constants. No tetrad direction RHS or P8 invocation.
    """
    def __init__(self,n0,profile,end,rtol=2e-12,atol=2e-14):
        self.profile,self.end=profile,float(end);n0=np.asarray(n0,float);self.n=len(n0)
        y=np.zeros((self.n,6));y[:,0]=.13;y[:,3:]=n0
        y[:,4]-=profile.k0*y[:,0]*n0[:,2]
        self.initial=y.copy()
        def rhs(t,yy):
            z=yy.reshape(self.n,6);a=profile.scales(t);k=profile.k0
            px=z[:,3]/a[0];py=(z[:,4]+k*z[:,0]*z[:,5])/a[1];pz=z[:,5]/a[2]
            r=np.sqrt(px*px+py*py+pz*pz);out=np.zeros_like(z)
            out[:,0]=px/(a[0]*r);out[:,1]=py/(a[1]*r)
            out[:,2]=k*z[:,0]*out[:,1]+pz/(a[2]*r)
            out[:,3]=-k*z[:,5]*py/(a[1]*r)
            return out.ravel()
        self.solution=_solve(rhs,y,end,rtol,atol)
    def at(self,t):
        z=self.solution.sol(t).reshape(self.n,6);a=self.profile.scales(t)
        p=np.stack([z[:,3]/a[0],(z[:,4]+self.profile.k0*z[:,0]*z[:,5])/a[1],z[:,5]/a[2]],axis=1)
        r=np.linalg.norm(p,axis=1);return p/r[:,None],r


class TangentGeometry:
    """Sphere flow derivative: evolve two tangents, not the area ODE."""
    def __init__(self,grid,profile,end,rtol=2e-12,atol=2e-14):
        self.n=len(grid.w);E0=np.stack([grid.bt,grid.bp],axis=2)
        y=np.column_stack([grid.n,E0.reshape(self.n,6)])
        def rhs(t,yy):
            z=yy.reshape(self.n,9);n=z[:,:3];Q=z[:,3:].reshape(self.n,3,2)
            H,S=profile.fields(t);N=profile.curvature(t);sn=n@S.T;s=np.einsum('ni,ni->n',n,sn)
            v=-sn+s[:,None]*n+np.cross(n@N.T,n)
            D=-S[None]+s[:,None,None]*np.eye(3)+2*np.einsum('ni,nj->nij',n,sn)-cross_matrix(n)@N+cross_matrix(n@N.T)
            return np.column_stack([v,(D@Q).reshape(self.n,6)]).ravel()
        self.solution=_solve(rhs,y,end,rtol,atol)
    def area(self,t):
        z=self.solution.sol(t).reshape(self.n,9);Q=z[:,3:].reshape(self.n,3,2)
        return np.einsum('ni,ni->n',z[:,:3],np.cross(Q[:,:,0],Q[:,:,1]))


class ExpandingDirect:
    """Physical Cartesian carrier ODE calling pinned P8, not a pullback solver."""
    def __init__(self,geo,J0,rtol=2e-12,atol=2e-14):
        self.geo=geo;J0=np.asarray(J0,float)
        if J0.shape!=(geo.n,3,3) or not np.isfinite(J0).all():raise ValueError('finite initial carrier/grid required')
        def rhs(t,y):
            z=geo.at(t);e=z['e'];J=y.reshape(geo.n,3,3);H,S=geo.profile.fields(t);N=geo.profile.curvature(t)
            s=np.einsum('ni,ij,nj->n',e,S,e);P=np.eye(3)-np.einsum('ni,nj->nij',e,e)
            M=np.einsum('n,nij->ij',z['w'],J)
            gain=ALPHA*np.einsum('nia,ab,nbj->nij',P,M,P,optimize=True)
            return (-4*(H+s)[:,None,None]*J+P8.tensor_rate(J,e,H,S,np.zeros(3),N,np.zeros(3))+geo.profile.rate(t)*(gain-J)).ravel()
        self.solution=_solve(rhs,J0,geo.end,rtol,atol)
    def state(self,t):return self.solution.sol(self.geo._time(t)).reshape(self.geo.n,3,3)
    def moment(self,t):return self.geo.moment(t,self.state(t))


class ExpandingHarmonic(HarmonicHistory):
    """Existing shear + curvature generators, explicit finite-L Galerkin IVP.

    Analytic matrices are reused; no angular quadrature or direct source enters.
    Only time-dependent curvature amplitude is added to inherited normal-clock
    shear/collision RHS. The code support remains 2<=L<=8, end<=.6.
    """
    def __init__(self,profile,initial,L,end,rtol=2e-12,atol=2e-14):
        self.C0=curvature_matrix(0,L,L,np.diag([0.,0.,1.])).real
        self.C2=curvature_matrix(2,L,L,np.diag([0.,0.,1.]))
        super().__init__(profile,initial,L,end,rtol,atol)
    def rhs(self,t,y):
        out=super().rhs(t,y);n0,n2=self.n0,self.n2;k=self.profile.curvature(t)[2,2]
        dp=self.C2@(y[2*n0:2*n0+n2]+1j*y[2*n0+n2:])
        return out+k*np.r_[self.C0@y[:n0],self.C0@y[n0:2*n0],dp.real,dp.imag]
