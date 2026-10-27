"""KM2C: fixed normal-tetrad beta on prescribed Bianchi-I geometry.

Normal proper time, or u=t/T_star with every rate multiplied by T_star.
Signature (-,+,+,+); beta=v_e/c; nu0=n_e_star sigma_T c, proper density.
The unchanged KM1 Geometry transports the normal screen and photon momentum.
Normal carrier J=r^4 E X E^T. Electron source uses F=S_beta E and
M_e=sum w_n r^4 D^2 F X F^T. Pullback X'=-nu0 D X+G_t[M_e].
No production runner, source injection, normalization, clipping, small-beta
expansion, spectral-validity certification, or matter/Einstein feedback.
"""
from __future__ import annotations
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
import sys
import numpy as np
from scipy.integrate import solve_ivp
from numpy.polynomial.legendre import leggauss
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'vendor'))
import polarization as P8
import polarized_dictionary as PD
from source_memory import Geometry,Profile,ALPHA
from tilted_collision import TiltedThomson,boost_map,radiation_tensor,expected_fourforce,_velocity
from km2b_fixtures import mixed_coefficients


@dataclass(frozen=True)
class FieldProfile:
    """Main fields are the unchanged KM1 noncommuting profile; bounded controls."""
    kind: str='main'
    nu0: float=1.3
    def __post_init__(self):
        if self.kind not in ('main','flat','isotropic','lrs') or not np.isfinite(self.nu0) or self.nu0<0:
            raise ValueError('declared kind and finite nu0>=0 required')
    def fields(self,t):
        if self.kind=='flat':return 0.,np.zeros((3,3))
        if self.kind=='isotropic':return .3,np.zeros((3,3))
        return Profile('noncommuting' if self.kind=='main' else 'lrs').fields(t)
    def rate(self,t):return self.nu0
    def kappa(self,t):return self.nu0*t  # only the legacy rest-electron limit


def make_fixture(n,profile,beta,end,coefficients=None,*,rtol=2e-12,atol=2e-14):
    """Electron GL initial field mapped to normal directions; raw solid angles."""
    beta,_=_velocity(beta);g=PD.Grid(n,2*n)
    S,nn,Dinv=boost_map(g.n,-beta)
    b=np.einsum('nij,nj->ni',S,g.bt);p=np.einsum('nij,nj->ni',S,g.bp)
    normal=SimpleNamespace(n=nn,w=g.w/Dinv**2,bt=b,bp=p)
    Je=PD.synthesize(g,mixed_coefficients() if coefficients is None else coefficients)
    J0=Dinv[:,None,None]**4*np.einsum('nik,nkl,njl->nij',S,Je,S)
    geo=Geometry(normal,profile,end,rtol=rtol,atol=atol)
    return geo,J0


class CurvedMemory:
    """Prescribed time-dependent source projection, gain, and ray attenuation.

    tau integration solves only prescribed scalar rate histories, not radiation.
    Projection L_t and gain G_t are 9x4 and 4x9 per angular node. The latter
    includes exactly one relative-flux factor nu0 D. No direct RHS is called.
    """
    def __init__(self,geo,J0,beta,nu0,*,loss_rtol=2e-12,loss_atol=2e-14):
        self.geo=geo;self.beta,self.gamma=_velocity(beta);self.beta=self.beta.copy()
        self.nu0=float(nu0)
        if not np.isfinite(self.nu0) or self.nu0<0:raise ValueError('finite nu0>=0 required')
        self.end=float(geo.end);self._cache=OrderedDict()
        z=self.at(0);self.J0=z['op']._carrier(J0).copy();E=z['screen']
        self.X0=np.einsum('nia,nij,njb->nab',E,self.J0,E)
        self.loss_rtol=loss_rtol;self.loss_atol=loss_atol
        self.loss=None
        if self.nu0:
            self.loss=solve_ivp(lambda t,y:self.at(t)['d'],(0,self.end),np.zeros(geo.n),
                                method='DOP853',rtol=loss_rtol,atol=loss_atol,dense_output=True)
            if not self.loss.success:raise RuntimeError(self.loss.message)
    def time(self,t):
        t=float(t)
        if not np.isfinite(t) or not 0<=t<=self.end:raise ValueError('outside prescribed support')
        return t
    def at(self,t):
        t=self.time(t)
        if t in self._cache:
            self._cache.move_to_end(t);return self._cache[t]
        a=self.geo.at(t);op=TiltedThomson(a['e'],a['w'],self.beta)
        F=np.einsum('nij,nja->nia',op.S,a['screen'])
        L=(a['v']*op.D**2)[:,None,None]*np.einsum('nia,njb->nijab',F,F).reshape(self.geo.n,9,4)
        G=(ALPHA*self.nu0/(a['mu']**4*op.D**3))[:,None,None]*np.einsum('nia,njb->nabij',F,F).reshape(self.geo.n,4,9)
        z={**a,'op':op,'F':F,'D':op.D,'d':self.nu0*op.D,'L':L,'G':G}
        self._cache[t]=z
        if len(self._cache)>128:self._cache.popitem(last=False)
        return z
    def tau(self,t):
        t=self.time(t)
        return np.zeros(self.geo.n) if self.loss is None else self.loss.sol(t)
    def attenuation(self,t,s):
        t=self.time(t);s=self.time(s)
        if s>t:raise ValueError('retarded attenuation requires s<=t')
        return np.exp(-(self.tau(t)-self.tau(s)))
    def project(self,t,X):
        return np.einsum('nab,nb->a',self.at(t)['L'],np.asarray(X).reshape(self.geo.n,4)).reshape(3,3)
    def carrier(self,t,X):
        z=self.at(t);E=z['screen']
        return z['mu'][:,None,None]**4*np.einsum('nia,nab,njb->nij',E,X,E)
    def initial_source(self,t):return self.project(t,self.attenuation(t,0)[:,None,None]*self.X0)
    def kernel(self,t,s):
        return np.einsum('n,nab,nbc->ac',self.attenuation(t,s),self.at(t)['L'],self.at(s)['G'],optimize=True)


def linear_collision(op,J,nu0):
    """Same physical RHS on transverse carriers; finite ambient RK extension."""
    J=np.asarray(J,float)
    if J.shape!=(len(op.n),3,3) or not np.isfinite(J).all():raise ValueError('finite RK carrier required')
    Y=op.D[:,None,None]**4*np.einsum('nik,nkl,njl->nij',op.S,J,op.S)
    M=np.einsum('n,nij->ij',op.we,Y)
    return nu0*op.D[:,None,None]*(op.gain_from_source(M)-J)


class DirectHistory:
    """Physical normal-carrier ODE with unchanged P8 and the KM2A linear algebra.

    RK trial stages need not satisfy the moving transverse subspace. Apply the
    ambient linear collision extension there, without state projection. Initial
    and output carriers use the unchanged strict KM2A admissibility test.
    """
    def __init__(self,memory:CurvedMemory,*,rtol=2e-12,atol=2e-14):
        self.memory=memory;self.rtol=rtol;self.atol=atol
        self.sol=solve_ivp(lambda t,y:self.rhs(t,y.reshape(memory.J0.shape)).ravel(),
                           (0,memory.end),memory.J0.ravel(),method='DOP853',
                           dense_output=True,rtol=rtol,atol=atol)
        if not self.sol.success:raise RuntimeError(self.sol.message)
    def rhs(self,t,J):
        m=self.memory;z=m.at(t);H,S=m.geo.profile.fields(t);e=z['e']
        s=np.einsum('ni,ij,nj->n',e,S,e);Z=np.zeros((3,3));zero=np.zeros(3)
        return -4*(H+s)[:,None,None]*J+P8.tensor_rate(J,e,H,S,zero,Z,zero)+linear_collision(z['op'],J,m.nu0)
    def carrier(self,t):return self.sol.sol(self.memory.time(t)).reshape(self.memory.J0.shape)
    def moment(self,t):return self.memory.at(t)['op'].source(self.carrier(t))


def lagrange(x):return np.array([2*x*x-3*x+1,4*x-4*x*x,2*x*x-x])


class VolterraHistory:
    """Causal unknown-source collocation using varying optical depth and boosts.

    History remains a full 2x2 carrier per ray. Three source nodes per panel,
    two unknown 3x3 stages:18x18 solve. Smooth kernel quadrature order separate
    from source interpolation. No frozen-rate exponential-weight substitution.
    """
    def __init__(self,memory:CurvedMemory,panels:int,*,order:int=4,end=None):
        if not isinstance(panels,(int,np.integer)) or isinstance(panels,bool) or panels<1:
            raise ValueError('positive integer panels required')
        if not isinstance(order,(int,np.integer)) or isinstance(order,bool) or not 2<=order<=16:
            raise ValueError('integer Gauss order in [2,16] required')
        self.memory=memory;self.end=memory.end if end is None else memory.time(end)
        if self.end<=0:raise ValueError('positive support required')
        self.times=np.linspace(0,self.end,int(panels)+1);self.gx,self.gw=leggauss(order)
        self.order=order;self.X=np.empty((panels+1,)+memory.X0.shape);self.X[0]=memory.X0
        self.stages=np.empty((panels,3,3,3));self.conditions=[];self.endpoint_defects=[]
        for i,(a,b) in enumerate(zip(self.times[:-1],self.times[1:])):
            left=memory.project(a,self.X[i]);blocks=[];rhs=[];weights=[]
            for t in ((a+b)/2,b):
                W=self.weights(t,a,b);weights.append(W)
                block=np.einsum('nab,njbc->jac',memory.at(t)['L'],W,optimize=True)
                blocks.append(block)
                free=memory.project(t,memory.attenuation(t,a)[:,None,None]*self.X[i])
                rhs.append(free.ravel()+block[0]@left.ravel())
            mat=np.block([[np.eye(9)-blocks[0][1],-blocks[0][2]],[-blocks[1][1],np.eye(9)-blocks[1][2]]])
            cond=float(np.linalg.cond(mat));self.conditions.append(cond)
            if not np.isfinite(cond) or cond>1e12:raise ArithmeticError('refine ill-conditioned panel')
            unknown=np.linalg.solve(mat,np.concatenate(rhs)).reshape(2,3,3)
            self.stages[i]=np.concatenate([left[None],unknown])
            self.X[i+1]=self.advance(b,a,self.X[i],self.stages[i],weights[1])
            self.endpoint_defects.append(float(np.max(abs(memory.project(b,self.X[i+1])-unknown[1]))))
    def weights(self,t,a,b):
        W=np.zeros((self.memory.geo.n,3,4,9))
        for s,w in zip(a+(t-a)*(self.gx+1)/2,(t-a)*self.gw/2):
            G=self.memory.at(float(s))['G'];att=self.memory.attenuation(t,float(s))
            W+=w*np.einsum('n,j,nab->njab',att,lagrange((s-a)/(b-a)),G)
        return W
    def advance(self,t,a,Xa,stages,W):
        out=self.memory.attenuation(t,a)[:,None]*Xa.reshape(-1,4)
        out+=np.einsum('njab,jb->na',W,stages.reshape(3,9),optimize=True)
        return out.reshape(Xa.shape)
    def locate(self,t):
        t=self.memory.time(t)
        if t>self.end:raise ValueError('outside solved support')
        i=min(max(0,np.searchsorted(self.times,t,side='right')-1),len(self.times)-2)
        return t,int(i)
    def pullback(self,t):
        t,i=self.locate(t);a,b=self.times[i:i+2]
        if t==a:return self.X[i].copy()
        if t==b:return self.X[i+1].copy()
        return self.advance(t,a,self.X[i],self.stages[i],self.weights(t,a,b))
    def carrier(self,t):return self.memory.carrier(t,self.pullback(t))
    def moment(self,t):return self.memory.project(t,self.pullback(t))
    def source_polynomial(self,t):
        t,i=self.locate(t);a,b=self.times[i:i+2]
        return np.einsum('j,jab->ab',lagrange((t-a)/(b-a)),self.stages[i])
    def global_reconstruction(self,t):
        t,_=self.locate(t);M=self.memory.initial_source(t).copy()
        for i,(a,b) in enumerate(zip(self.times[:-1],self.times[1:])):
            if a>=t:break
            top=min(b,t)
            for s,w in zip(a+(top-a)*(self.gx+1)/2,(top-a)*self.gw/2):
                Ms=np.einsum('j,jab->ab',lagrange((s-a)/(b-a)),self.stages[i])
                M+=w*(self.memory.kernel(t,float(s))@Ms.ravel()).reshape(3,3)
        return M


def balances(memory,t,J):
    """Local collision force, independent raw moment derivative, geometric work.

    The flat invariant C=gamma(rho-beta.q) is not a curved total invariant.
    Cdot_geom=-4H*C-gamma*sigma:pi+gamma*beta.sigma.q, in this homogeneous
    Bianchi-I Fermi normal tetrad with constant beta and reduced q=flux/c.
    """
    z=memory.at(t);op=z['op'];e=z['e'];w=z['w'];H,S=memory.geo.profile.fields(t)
    T=radiation_tensor(e,w,J);rho=T[0,0];q=T[0,1:];pi=T[1:,1:]-rho*np.eye(3)/3
    C=op.rhs(J,memory.nu0);Ic=np.trace(C,axis1=1,axis2=2)
    F=np.r_[np.dot(w,Ic),np.einsum('n,n,ni->i',w,Ic,e)]
    target=expected_fourforce(T,memory.beta,memory.nu0)
    I=np.trace(J,axis1=1,axis2=2);s=np.einsum('ni,ij,nj->n',e,S,e)
    de=-e@S.T+s[:,None]*e
    rho_dot=np.dot(w,(-4*H-s)*I+Ic)
    q_dot=np.einsum('n,n,ni->i',w,(-4*H-s)*I+Ic,e)+np.einsum('n,n,ni->i',w,I,de)
    rg=-4*H*rho-np.sum(S*pi);qg=-4*H*q-S@q
    invariant=memory.gamma*(rho-memory.beta@q)
    work=-4*H*invariant-memory.gamma*np.sum(S*pi)+memory.gamma*memory.beta@(S@q)
    scale=max(1.,(abs(H)+np.linalg.norm(S)+memory.nu0)*abs(rho))
    return {'rho':float(rho),'q':q.tolist(),'invariant':float(invariant),
            'geometric_invariant_rate':float(work),'force':F.tolist(),'expected_force':target.tolist(),
            'force_rel':float(np.max(abs(F-target))/max(1.,memory.nu0*abs(rho))),
            'elastic_rel':float(abs(F[0]-memory.beta@F[1:])/max(1.,memory.nu0*abs(rho))),
            'rho_dot':float(rho_dot),'q_dot':q_dot.tolist(),
            'energy_balance_rel':float(abs(rho_dot-rg-target[0])/scale),
            'flux_balance_rel':float(np.max(abs(q_dot-qg-target[1:]))/scale),
            'collision_invariant_rate':float(memory.gamma*(F[0]-memory.beta@F[1:]))}
