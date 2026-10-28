"""KM1 source-memory construction on prescribed Bianchi I.

No Volterra marching solver is implemented. evaluate_with_source inserts an
independently evolved direct source to check the exact Duhamel identity.
Time u=t/T_star, H and sigma below are rates multiplied by T_star, nu is
T_star*n_e_star*sigma_T*c. P8 physical carrier convention S+iA is inherited.
No angular harmonic truncation, no continuum renormalization of deformed weights.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import sys
import numpy as np
from scipy.integrate import solve_ivp
from numpy.polynomial.legendre import leggauss

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'vendor'))
import polarization as P8
from polarized_dictionary import Grid
ALPHA=3/(8*np.pi)

@dataclass(frozen=True)
class Profile:
    """Smooth prescribed fields on 0<=u<=0.6, not an Einstein solution."""
    kind: str='noncommuting'

    def __post_init__(self):
        if self.kind not in ('static','lrs','noncommuting','free'):
            raise ValueError('unknown prescribed profile')

    def fields(self,t: float):
        if self.kind=='static': return 0.,np.zeros((3,3))
        if self.kind=='lrs': return .3,np.diag([-.2,-.2,.4])
        d=np.diag([-.18,.03,.15])
        o=np.array([[0.,.22,.09],[.22,0.,-.12],[.09,-.12,0.]])
        return .4+.05*np.sin(2*t),d+np.sin(3*t+.2)*o

    def rate(self,t: float) -> float:
        return 0. if self.kind=='free' else 1.2+.5*np.cos(3*t)

    def kappa(self,t: float) -> float:
        return 0. if self.kind=='free' else 1.2*t+(.5/3)*np.sin(3*t)

class Geometry:
    """Integrate momentum A and a horizontal orthonormal screen, no intensity.

    q is the initial direction; p=A q, mu=|A q|. A'=-[H I+sigma]A.
    Screen E has two columns and E'=Omega E, Omega=e' e^T-e e'^T.
    Dense output errors are kept distinct from the analytic identities.
    """
    def __init__(self,g: Grid,profile: Profile,end: float,rtol=2e-12,atol=2e-14):
        if not 0<end<=.6: raise ValueError('bounded geometry requires 0<end<=0.6')
        self.grid,self.profile,self.end=g,profile,float(end)
        self.n=len(g.w); self.screen0=np.stack([g.bt,g.bp],axis=2)
        y0=np.r_[np.eye(3).ravel(),self.screen0.ravel()]
        def rhs(t,y):
            A=y[:9].reshape(3,3); E=y[9:].reshape(self.n,3,2)
            H,S=profile.fields(t); B=H*np.eye(3)+S
            p=g.n@A.T; mu=np.linalg.norm(p,axis=1); e=p/mu[:,None]
            en=e@B.T; ee=np.einsum('ni,ni->n',e,en)
            de=-en+ee[:,None]*e
            omega=np.einsum('ni,nj->nij',de,e)-np.einsum('ni,nj->nij',e,de)
            return np.r_[(-B@A).ravel(),np.einsum('nij,nja->nia',omega,E).ravel()]
        self.solution=solve_ivp(rhs,(0,self.end),y0,method='DOP853',rtol=rtol,atol=atol,dense_output=True)
        if not self.solution.success: raise RuntimeError(self.solution.message)
        self._cache={}

    def _time(self,t):
        t=float(t)
        if not np.isfinite(t) or t<0 or t>self.end+1e-14: raise ValueError('time outside prescribed support')
        return min(t,self.end)

    def at(self,t):
        t=self._time(t)
        if t not in self._cache:
            y=self.solution.sol(t); A=y[:9].reshape(3,3); screen=y[9:].reshape(self.n,3,2)
            det=float(np.linalg.det(A))
            if det<=0: raise ValueError('nonpositive momentum determinant')
            p=self.grid.n@A.T; mu=np.linalg.norm(p,axis=1); e=p/mu[:,None]
            self._cache[t]={'A':A,'det':det,'mu':mu,'e':e,'screen':screen,
                           'w':self.grid.w*det/mu**3,'v':self.grid.w*det*mu}
        return self._cache[t]

    def screen_rate(self,t,z=None):
        z=self.at(t) if z is None else z
        H,S=self.profile.fields(t); B=H*np.eye(3)+S; e=z['e']; en=e@B.T
        de=-en+np.einsum('ni,ni->n',e,en)[:,None]*e
        om=np.einsum('ni,nj->nij',de,e)-np.einsum('ni,nj->nij',e,de)
        return np.einsum('nij,nja->nia',om,z['screen'])

    def moment(self,t,J):
        return np.einsum('n,nij->ij',self.at(t)['w'],np.asarray(J,float))

class DirectHistory:
    """Independent physical-carrier ODE with the pinned P8 tensor-rate function.

    J'=-4(H+sigma:ee)J + P8.tensor_rate(J) + nu(alpha P M P-J).
    It shares prescribed geometry/quadrature with the kernel, not the pullback
    formula. It is NOT the production Rust/Strang/QState integrator.
    """
    def __init__(self,geo: Geometry,J0,rtol=2e-12,atol=2e-14):
        self.geo=geo; self.J0=np.asarray(J0,float).copy()
        if self.J0.shape!=(geo.n,3,3): raise ValueError('J0/grid shape mismatch')
        Z=np.zeros((3,3)); z=np.zeros(3)
        def rhs(t,y):
            d=geo.at(t);e=d['e'];J=y.reshape(geo.n,3,3);H,S=geo.profile.fields(t)
            es=np.einsum('ni,ij,nj->n',e,S,e)
            P=np.eye(3)-np.einsum('ni,nj->nij',e,e)
            M=np.einsum('n,nij->ij',d['w'],J)
            gain=ALPHA*np.einsum('nia,ab,nbj->nij',P,M,P)
            return (-4*(H+es)[:,None,None]*J+P8.tensor_rate(J,e,H,S,z,Z,z)
                    +geo.profile.rate(t)*(gain-J)).ravel()
        self.solution=solve_ivp(rhs,(0,geo.end),self.J0.ravel(),method='DOP853',
                                rtol=rtol,atol=atol,dense_output=True)
        if not self.solution.success: raise RuntimeError(self.solution.message)

    def state(self,t):
        t=self.geo._time(t);return self.solution.sol(t).reshape(self.geo.n,3,3)

    def moment(self,t): return self.geo.moment(t,self.state(t))

class SourceMemory:
    """9-component source kernel, including full initial angular state.

    K(t,s)[M] = nu(s)e^(-Delta kappa) alpha det A(t)
      * sum_q w0 mu(t)/mu(s)^4 Z(t,s) M Z(t,s)^T,
    Z=E(t) E(s)^T. This is exact for the continuous characteristics, and for
    any fixed angular quadrature applied consistently to both representations.
    """
    def __init__(self,geo: Geometry,J0):
        self.geo=geo;J0=np.asarray(J0,float)
        if J0.shape!=(geo.n,3,3): raise ValueError('J0/grid shape mismatch')
        E=geo.screen0
        self.X0=np.einsum('nia,nij,njb->nab',E,J0,E)

    def initial_term(self,t):
        d=self.geo.at(t); E=d['screen']
        return np.exp(-self.geo.profile.kappa(t))*np.einsum('n,nia,nab,njb->ij',d['v'],E,self.X0,E)

    def kernel(self,t,s):
        t=self.geo._time(t);s=self.geo._time(s)
        if s>t: raise ValueError('retarded kernel requires s<=t')
        a,b=self.geo.at(t),self.geo.at(s)
        Z=np.einsum('nia,nja->nij',a['screen'],b['screen'])
        wt=a['v']/b['mu']**4
        pref=ALPHA*self.geo.profile.rate(s)*np.exp(-(self.geo.profile.kappa(t)-self.geo.profile.kappa(s)))
        return pref*np.einsum('n,nia,njb->ijab',wt,Z,Z,optimize=True).reshape(9,9)

    def evaluate_with_source(self,t,source,order=24):
        """Duhamel residual diagnostic; source is provided, not solved for here."""
        t=self.geo._time(t)
        if order<2: raise ValueError('quadrature order must be >=2')
        val=self.initial_term(t)
        x,w=leggauss(int(order))
        for s,ws in zip(t*(x+1)/2,t*w/2):
            val=val+ws*(self.kernel(t,s)@np.asarray(source(s)).ravel()).reshape(3,3)
        return val

    def reconstruct_with_source(self,t,source,order=24):
        """Full carrier reconstruction with supplied source, not a source solver."""
        t=self.geo._time(t); d=self.geo.at(t)
        X=np.exp(-self.geo.profile.kappa(t))*self.X0
        x,w=leggauss(int(order))
        for s,ws in zip(t*(x+1)/2,t*w/2):
            ds=self.geo.at(s); E=ds['screen']
            gain=ALPHA/ds['mu'][:,None,None]**4*np.einsum('nia,ij,njb->nab',E,source(s),E)
            X=X+ws*self.geo.profile.rate(s)*np.exp(-(self.geo.profile.kappa(t)-self.geo.profile.kappa(s)))*gain
        E=d['screen']
        return d['mu'][:,None,None]**4*np.einsum('nia,nab,njb->nij',E,X,E)

    def kernel_bound(self,t,s):
        """Frobenius operator-norm bound for exact orthonormal screens (dimension 1/time)."""
        a,b=self.geo.at(t),self.geo.at(s)
        if s>t: raise ValueError('retarded kernel requires s<=t')
        pref=ALPHA*self.geo.profile.rate(s)*np.exp(-(self.geo.profile.kappa(t)-self.geo.profile.kappa(s)))
        return pref*float(np.sum(a['v']/b['mu']**4))
