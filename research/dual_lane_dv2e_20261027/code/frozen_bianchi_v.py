"""DV2-E: frozen prescribed Bianchi-V polarized finite-time benchmark.

Signature (-,+,+,+), photon propagation n, time u=t/T_star. A=c*a_structure
and nu=n_e*sigma_T*c are rates multiplied by T_star. H=sigma=N=0.
The angular Mobius map has energy ratio 1, NOT a boost Doppler weight.
Geometry screens use the normalized differential of the conformal sphere map.
SourceMemory/VolterraHistory are unchanged parents. This is not an Einstein
solution, a production runner, or a general finite-L closure.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import sys
import numpy as np
from scipy.integrate import solve_ivp
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'vendor'))
import polarization as P8
from polarized_dictionary import Grid, synthesize, stokes, source_matrix
from harmonic_streaming import labels
from harmonic_history import direction_view
from classb_streaming import classb_matrix
ALPHA=3/(8*np.pi)

@dataclass(frozen=True)
class FrozenV:
    A: tuple=(0.,0.,.7)
    nu: float=1.3
    modulation: float=0.

    def __post_init__(self):
        v=np.asarray(self.A,float)
        if v.shape!=(3,) or not np.isfinite(v).all():raise ValueError('finite A three-vector required')
        if not np.isfinite(self.nu) or not np.isfinite(self.modulation) or self.nu<abs(self.modulation):
            raise ValueError('nonnegative bounded opacity required')
        object.__setattr__(self,'A',tuple(float(x) for x in v))
    def fields(self,t):return 0.,np.zeros((3,3))
    def rate(self,t):return self.nu+self.modulation*np.cos(2*t)
    def kappa(self,t):return self.nu*t+.5*self.modulation*np.sin(2*t)

class Geometry:
    """Exact direction, physical screen, energy and RAW solid-angle supplier.

    D=cosh(a*t)-mu0*sinh(a*t), n=(n0+[(cosh-1)mu0-sinh]axis)/D.
    W(t)=W0+[(cosh-1)axis+sinh*n(t)](axis.W0). Its norm is unchanged.
    This is D times the tangent differential of n(n0), so Jac=D^-2.
    """
    def __init__(self,g:Grid,profile:FrozenV,end:float):
        if not np.isfinite(end) or not 0<end<=1 or np.linalg.norm(profile.A)*end>1.5:
            raise ValueError('bounded support: 0<end<=1 and |A|*end<=1.5')
        self.grid,self.profile,self.end=g,profile,float(end);self.n=len(g.w)
        self.screen0=np.stack([g.bt,g.bp],axis=2);self._cache={}
    def _time(self,t):
        t=float(t)
        if not np.isfinite(t) or t<0 or t>self.end+1e-14:raise ValueError('time outside support')
        return min(t,self.end)
    def flow(self,n0,E0,t):
        A=np.asarray(self.profile.A);a=float(np.linalg.norm(A));x=a*float(t)
        if not np.isfinite(x) or abs(x)>1.5:raise ValueError('flow support exceeded')
        if a==0:return n0.copy(),np.ones(len(n0)),E0.copy()
        axis=A/a;mu=n0@axis;ch,sh=np.cosh(x),np.sinh(x);D=ch-mu*sh
        n=(n0+((ch-1)*mu-sh)[:,None]*axis)/D[:,None]
        v=(ch-1)*axis+sh*n
        E=E0+v[:,:,None]*np.einsum('i,nia->na',axis,E0)[:,None,:]
        return n,D**-2,E
    def at(self,t):
        t=self._time(t)
        if t not in self._cache:
            n,jac,E=self.flow(self.grid.n,self.screen0,t);w=self.grid.w*jac
            self._cache[t]={'e':n,'screen':E,'mu':np.ones(self.n),'jac':jac,'w':w,'v':w}
        return self._cache[t]
    def screen_rate(self,t):
        z=self.at(t)
        return z['e'][:,:,None]*np.einsum('i,nia->na',self.profile.A,z['screen'])[:,None,:]
    def moment(self,t,J):return np.einsum('n,nij->ij',self.at(t)['w'],J)

class Direct:
    """Physical Cartesian-carrier ODE calling pinned P8, not source pullback."""
    def __init__(self,geo:Geometry,J0,rtol=2e-12,atol=2e-14):
        self.geo=geo;self.J0=np.asarray(J0,float).copy()
        if self.J0.shape!=(geo.n,3,3) or not np.isfinite(self.J0).all():raise ValueError('invalid carrier')
        def rhs(t,y):
            z=geo.at(t);e=z['e'];J=y.reshape(geo.n,3,3)
            P=np.eye(3)-np.einsum('ni,nj->nij',e,e)
            M=geo.moment(t,J);gain=ALPHA*np.einsum('nia,ab,nbj->nij',P,M,P,optimize=True)
            tr=P8.tensor_rate(J,e,0.,np.zeros((3,3)),np.zeros(3),np.zeros((3,3)),np.asarray(geo.profile.A))
            return (tr+geo.profile.rate(t)*(gain-J)).ravel()
        self.rhs=rhs
        self.solution=solve_ivp(rhs,(0,geo.end),self.J0.ravel(),method='DOP853',rtol=rtol,atol=atol,dense_output=True)
        if not self.solution.success:raise RuntimeError(self.solution.message)
    def state(self,t):return self.solution.sol(self.geo._time(t)).reshape(self.geo.n,3,3)
    def moment(self,t):return self.geo.moment(t,self.state(t))

class Harmonic:
    """Independent analytic full-polarized Galerkin IVP. L>cutoff is zero.

    No initial mode outside the declared cutoff is silently discarded.
    Fixed operator is constructed without any angular quadrature or direct RHS.
    """
    def __init__(self,profile:FrozenV,initial:dict,L:int,end:float,rtol=2e-12,atol=2e-14):
        if isinstance(L,bool) or not isinstance(L,int) or not 2<=L<=8:raise ValueError('2<=integer L<=8 required')
        if not np.isfinite(end) or not 0<end<=1:raise ValueError('bounded history end required')
        self.profile,self.L,self.end=profile,L,float(end)
        self.l0,self.l2=labels(0,L),labels(2,L);self.n0,self.n2=len(self.l0),len(self.l2)
        self.keys=[(f,l,m) for f in ('I','V') for l,m in self.l0]+[(f,l,m) for f in ('E','B') for l,m in self.l2]
        self.index={k:i for i,k in enumerate(self.keys)}
        if any(k not in self.index or not np.isfinite(v) for k,v in initial.items()):raise ValueError('invalid or excluded initial mode')
        self.y0=np.array([initial.get(k,0.) for k in self.keys]);self.idx0=dict(zip(self.l0,range(self.n0)));self.idx2=dict(zip(self.l2,range(self.n2)))
        a0=classb_matrix(0,L,L,profile.A)
        if np.max(abs(a0.imag))>2e-12:raise ArithmeticError('scalar reality violation')
        self.a0=a0.real;self.a2=classb_matrix(2,L,L,profile.A)
        self.solution=solve_ivp(self.rhs,(0,end),self.y0,method='DOP853',rtol=rtol,atol=atol,dense_output=True)
        if not self.solution.success:raise RuntimeError(self.solution.message)
    def rhs(self,t,y):
        n0,n2=self.n0,self.n2;nu=self.profile.rate(t)
        I=y[:n0];V=y[n0:2*n0];p=y[2*n0:2*n0+n2]+1j*y[2*n0+n2:]
        dI=self.a0@I-nu*I;dV=self.a0@V-nu*V;dp=self.a2@p-nu*p
        dI[self.idx0[0,0]]+=nu*I[self.idx0[0,0]]
        for m in range(-2,3):
            i,j=self.idx0[2,m],self.idx2[2,m]
            dI[i]+=nu*(.1*I[i]-np.sqrt(6)/10*p[j].real)
            dp[j]+=nu*(-np.sqrt(6)/10*I[i]+.6*p[j].real)
        for m in range(-1,2):dV[self.idx0[1,m]]+=.5*nu*V[self.idx0[1,m]]
        return np.r_[dI,dV,dp.real,dp.imag]
    def coefficients(self,t):
        if not np.isfinite(t) or not 0<=t<=self.end:raise ValueError('time outside support')
        return {k:float(v) for k,v in zip(self.keys,self.solution.sol(t))}
    def moment(self,t):return source_matrix(self.coefficients(t))
    def state(self,t,view):return synthesize(view,self.coefficients(t))


def exact_free(geo:Geometry,t:float,c:dict):
    """Independent canonical-axis formula: I,Q,U,V fixed along each meridian.

    Only z-axis A. Uses explicit theta/phi bases instead of the transported
    screen formula. Photon intensity has no D^4 multiplier.
    """
    A=np.asarray(geo.profile.A)
    if np.any(A[:2]):raise ValueError('canonical z-axis oracle only')
    t=geo._time(t);initial=synthesize(geo.grid,c);I,Q,U,V=stokes(geo.grid,initial)
    z=geo.at(t);v=direction_view(z['e'],z['w'])
    tt=np.einsum('ni,nj->nij',v.bt,v.bt);pp=np.einsum('ni,nj->nij',v.bp,v.bp);tp=np.einsum('ni,nj->nij',v.bt,v.bp)
    return .5*(I[:,None,None]*v.P+Q[:,None,None]*(tt-pp)+U[:,None,None]*(tp+tp.transpose(0,2,1))+V[:,None,None]*(tp.transpose(0,2,1)-tp))


def coordinate_reference(n0,a,end,rtol=2e-12,atol=2e-14):
    """Independent canonical Hamiltonian rays for e^-2az(dx2+dy2)+dz2.

    u=t/T_star and coordinates in c*T_star units. Initial energy is one.
    No calls to the tetrad, analytic flow or screen supplier.
    """
    n0=np.asarray(n0,float);N=len(n0);Px,Py=n0[:,0],n0[:,1]
    y0=np.stack([np.zeros(N),n0[:,2]],axis=1).ravel()
    def rhs(t,y):
        zz,pz=y.reshape(N,2).T;pp=np.exp(2*a*zz)*(Px**2+Py**2);E=np.sqrt(pp+pz*pz)
        return np.stack([pz/E,-a*pp/E],axis=1).ravel()
    sol=solve_ivp(rhs,(0,end),y0,method='DOP853',rtol=rtol,atol=atol)
    if not sol.success:raise RuntimeError(sol.message)
    zz,pz=sol.y[:,-1].reshape(N,2).T
    p=np.column_stack([np.exp(a*zz)*Px,np.exp(a*zz)*Py,pz]);E=np.linalg.norm(p,axis=1)
    return p/E[:,None],E


def free_dipole_moments(a,t,base=2.,eps=.3):
    """Exact continuum rho,q_z for I_i=base+eps*mu_i, no collisions.

    rho=4pi base+4pi eps(coth x-x csch^2 x),
    qz=4pi eps csch^2 x(x coth x-1), x=a*t.
    Series prevents cancellation at x=0. Units follow base and eps.
    """
    x=float(a*t)
    if abs(x)<.05:
        h=2*x/3-4*x**3/45+4*x**5/315-8*x**7/4725+4*x**9/18711
        g=1/3-2*x*x/15+2*x**4/63-4*x**6/675+2*x**8/2079
    else:
        cs=1/np.sinh(x)**2;ct=1/np.tanh(x);h=ct-x*cs;g=cs*(x*ct-1)
    return 4*np.pi*(base+eps*h),4*np.pi*eps*g
