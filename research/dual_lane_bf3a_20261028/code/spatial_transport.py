"""BF3-A: one periodic spatial coordinate, prescribed diagonal Bianchi I.

u=t/T_star; x is a dimensionless periodic coordinate with physical reference
length L_star. cbar=c*T_star/L_star is explicit (fixture cbar=1 chooses scales,
not a physical c=1 convention). Full bolometric P8 S+A carrier, beta=0.
No amplitude expansion. Spatial Fourier-Galerkin cutoff is explicit. Angular
quadrature, geometry dense output, time integration and spatial cutoff differ.
No production backend, Einstein/bath feedback, spatially varying metric or
independent spatial Volterra solver is supplied here.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import sys
import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import CubicHermiteSpline
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'vendor'))
import polarization as P8
from polarized_dictionary import Grid,synthesize,hermitian
from source_memory import Geometry,ALPHA


class FourierLine:
    """Odd grid on [0,2pi); scalar multiplication is exact truncated convolution.

    The excluded spatial modes are NOT set to physically zero: they are the
    declared numerical Galerkin tail. No circular convolution wrap is allowed.
    """
    def __init__(self,n:int):
        if not isinstance(n,int) or n<5 or n%2!=1:raise ValueError('Odd integer Nx>=5 required')
        self.n=n;self.K=n//2;self.x=2*np.pi*np.arange(n)/n
        self.k=np.fft.fftfreq(n,d=1/n)
    def _check(self,f):
        f=np.asarray(f)
        if f.shape[0]!=self.n or not np.isfinite(f).all():raise ValueError('Finite field on this spatial grid required')
        return f
    def derivative(self,f):
        f=self._check(f);mult=(1j*self.k).reshape((-1,)+(1,)*(f.ndim-1))
        return np.fft.ifft(mult*np.fft.fft(f,axis=0),axis=0).real
    def shift(self,f,delta):
        """Return f(x+delta[q],q,...) by exact finite-Fourier translation."""
        f=self._check(f);delta=np.asarray(delta,float)
        if f.ndim<2 or delta.shape!=(f.shape[1],) or not np.isfinite(delta).all():raise ValueError('One finite shift per ray required')
        phase=np.exp(1j*self.k[:,None]*delta[None]).reshape((self.n,len(delta))+(1,)*(f.ndim-2))
        return np.fft.ifft(np.fft.fft(f,axis=0)*phase,axis=0).real
    def multiply(self,f,coeff):
        """P_K[nu(x) f_K(x)] from finite analytic opacity coefficients."""
        f=self._check(f);a=np.fft.fftshift(np.fft.fft(f,axis=0)/self.n,axes=0)
        out=np.zeros_like(a)
        for m,c in coeff.items():
            if not isinstance(m,int) or abs(m)>self.K or not np.isfinite(c):raise ValueError('Opacity modes must lie inside the declared spatial cutoff')
            if m==0:out+=c*a
            elif m>0:out[m:]+=c*a[:-m]
            else:out[:m]+=c*a[-m:]
        return np.fft.ifft(np.fft.ifftshift(out,axes=0),axis=0).real*self.n
    def evaluate(self,f,x):
        f=self._check(f);x=np.atleast_1d(np.asarray(x,float))
        c=np.fft.fft(f,axis=0)/self.n
        return np.einsum('xk,k...->x...',np.exp(1j*x[:,None]*self.k[None]),c,optimize=True).real


@dataclass(frozen=True)
class Opacity:
    base:float=1.2
    contrast:float=.65
    second:float=.10
    modulation:float=.15
    def __post_init__(self):
        if not np.isfinite([self.base,self.contrast,self.second,self.modulation]).all() or self.base<0 or abs(self.contrast)+abs(self.second)>=1 or abs(self.modulation)>=1:
            raise ValueError('Require nonnegative finite base and certified positive bounded opacity shape/time factor')
    def scale(self,t):return self.base*(1+self.modulation*np.sin(2*t))
    def values(self,x,t):return self.scale(t)*(1+self.contrast*np.cos(x)+self.second*np.sin(2*x))
    def coefficients(self,t):
        b=self.scale(t)
        return {0:b,1:b*self.contrast/2,-1:b*self.contrast/2,2:-.5j*b*self.second,-2:.5j*b*self.second}


@dataclass(frozen=True)
class DiagonalProfile:
    kind:str='expanding'
    h:tuple=(.12,.45,.28)
    d:tuple=(.16,-.12,.08)
    mean_opacity:float=1.2
    rate_modulation:float=.15
    def __post_init__(self):
        if self.kind not in ('static','isotropic','expanding'):raise ValueError('Unknown geometry')
        if len(self.h)!=3 or len(self.d)!=3 or not np.isfinite(self.h+self.d).all():raise ValueError('Three finite scale-factor coefficients required')
    def scales(self,t):
        if self.kind=='static':return np.ones(3)
        if self.kind=='isotropic':return np.full(3,np.exp(.25*t))
        return np.exp(np.array(self.h)*t+.5*np.array(self.d)*t*t)
    def fields(self,t):
        hi=np.zeros(3) if self.kind=='static' else (np.full(3,.25) if self.kind=='isotropic' else np.array(self.h)+np.array(self.d)*t)
        H=float(hi.mean());return H,np.diag(hi-H)
    def rate(self,t):return self.mean_opacity*(1+self.rate_modulation*np.sin(2*t))
    def kappa(self,t):return self.mean_opacity*(t+.5*self.rate_modulation*(1-np.cos(2*t)))


def fixture(g,x):
    """Positive finite-amplitude common-frame initial carrier, spatial modes<=2.

    Angular fields through ell4. The background I40=.1 is not removed.
    """
    base={('I',0,0):2*np.sqrt(4*np.pi),('I',4,0):.1,('E',2,0):.05,('B',3,1):.025,('V',1,-1):.02}
    cosine={('I',0,0):.8*np.sqrt(4*np.pi),('I',2,0):.6,('E',2,1):.08}
    sine={('I',1,1):.2,('E',2,-1):.1,('B',2,2):.03}
    return (synthesize(g,base)[None]+np.cos(x)[:,None,None,None]*synthesize(g,cosine)[None]
            +np.sin(2*x)[:,None,None,None]*synthesize(g,sine)[None])


class Transport:
    def __init__(self,g:Grid,nx:int,profile:DiagonalProfile,end:float,opacity:Opacity,cbar=1.,rtol=2e-12,atol=2e-14):
        if not np.isfinite(cbar) or cbar<=0:raise ValueError('Explicit c*T_star/L_star must be positive')
        self.g,self.line,self.end,self.profile,self.opacity,self.cbar=g,FourierLine(nx),float(end),profile,opacity,float(cbar)
        self.geo=Geometry(g,profile,end,rtol=rtol,atol=atol)
        self.nq=len(g.w);self.shape=(nx,self.nq,3,3)
        def rhs(t,y):return self.velocity(t)
        self.ray=solve_ivp(rhs,(0,end),np.zeros(self.nq),method='DOP853',rtol=rtol,atol=atol,dense_output=True)
        if not self.ray.success:raise RuntimeError(self.ray.message)
    def velocity(self,t):return self.cbar*self.geo.at(t)['e'][:,0]/self.profile.scales(t)[0]
    def displacement(self,t):return self.ray.sol(self.geo._time(t))
    def check(self,J):
        J=np.asarray(J,float)
        if J.shape!=self.shape or not np.isfinite(J).all():raise ValueError('Finite (space,ray,3,3) physical carrier required')
        # Initial physical states only: never apply this guard to off-screen RK trial stages.
        scale=max(1.,float(np.max(abs(J))))
        right=np.einsum('xnij,nj->xni',J,self.g.n)
        left=np.einsum('ni,xnij->xnj',self.g.n,J)
        if max(float(np.max(abs(right))),float(np.max(abs(left))))>2e-11*scale:
            raise ValueError('Initial carrier must be transverse; no silent screen projection')
        return J
    def push(self,t,X):
        z=self.geo.at(t);E=z['screen']
        return z['mu'][None,:,None,None]**4*np.einsum('nia,xnab,njb->xnij',E,X,E,optimize=True)
    def pull(self,t,J):
        z=self.geo.at(t);E=z['screen']
        return np.einsum('nia,xnij,njb->xnab',E,J,E,optimize=True)/z['mu'][None,:,None,None]**4
    def source(self,t,J):return np.einsum('n,xnij->xij',self.geo.at(t)['w'],J,optimize=True)
    def collision_unit(self,t,J):
        z=self.geo.at(t);e=z['e'];P=np.eye(3)-np.einsum('ni,nj->nij',e,e)
        M=self.source(t,J)
        return ALPHA*np.einsum('nia,xab,nbj->xnij',P,M,P,optimize=True)-J
    def components(self,t,J):
        z=self.geo.at(t);e=z['e'];H,S=self.profile.fields(t)
        sn=np.einsum('ni,ij,nj->n',e,S,e)
        adv=-self.velocity(t)[None,:,None,None]*self.line.derivative(J)
        ev=np.broadcast_to(e,self.shape[:2]+(3,)).reshape(-1,3)
        geom=(-4*(H+sn)[None,:,None,None]*J+P8.tensor_rate(J.reshape(-1,3,3),ev,H,S,np.zeros(3),np.zeros((3,3)),np.zeros(3)).reshape(self.shape))
        coll=self.line.multiply(self.collision_unit(t,J),self.opacity.coefficients(t))
        return adv,geom,coll
    def physical_rhs(self,t,J):return sum(self.components(t,J))
    def pull_collision(self,t,X):
        z=self.geo.at(t);E=z['screen'];M=self.source(t,self.push(t,X))
        gain=ALPHA*np.einsum('nia,xij,njb->xnab',E,M,E,optimize=True)/z['mu'][None,:,None,None]**4
        return self.line.multiply(gain-X,self.opacity.coefficients(t))
    def characteristic_rhs(self,t,Y):
        shift=self.displacement(t)
        X=self.line.shift(Y,-shift)
        return self.line.shift(self.pull_collision(t,X),shift)
    def moments(self,t,J):
        z=self.geo.at(t);e,w=z['e'],z['w'];I=np.trace(J,axis1=-2,axis2=-1)
        rho=np.einsum('n,xn->x',w,I);q=np.einsum('n,xn,ni->xi',w,I,e)
        pi=np.einsum('n,xn,ni,nj->xij',w,I,e,e)-rho[:,None,None]*np.eye(3)/3
        return rho,q,pi
    def budgets(self,t,J):
        z=self.geo.at(t);e,w=z['e'],z['w'];H,S=self.profile.fields(t)
        sn=np.einsum('ni,ij,nj->n',e,S,e);adv,geom,coll=self.components(t,J)
        rho,q,pi=self.moments(t,J);dI=np.trace(adv+geom+coll,axis1=-2,axis2=-1);I=np.trace(J,axis1=-2,axis2=-1)
        rhodot=np.einsum('n,xn->x',w,dI+3*sn[None]*I)
        ce=np.einsum('n,xn->x',w,np.trace(coll,axis1=-2,axis2=-1))
        balance=rhodot+self.cbar/self.profile.scales(t)[0]*self.line.derivative(q[:,0])+4*H*rho+np.einsum('ij,xij->x',S,pi)
        mean=J.mean(axis=0);nu=self.opacity.values(self.line.x,t);nubar=nu.mean()
        opxi=self.collision_unit(t,J-mean[None]);corr=np.mean((nu-nubar)[:,None,None,None]*opxi,axis=0)
        baseline=nubar*self.collision_unit(t,mean[None])[0]
        return {'mean_streaming_abs':float(np.max(abs(adv.mean(axis=0)))),
          'mean_collision_identity_abs':float(np.max(abs(coll.mean(axis=0)-baseline-corr))),
          'covariance_source_norm':float(np.linalg.norm(np.einsum('n,nij->ij',w,corr))),
          'covariance_carrier_abs':float(np.max(abs(corr))),
          'local_energy_minus_collision_abs':float(np.max(abs(balance-ce))),
          'mean_energy_minus_collision_abs':float(abs(balance.mean()-ce.mean())),
          'raw_collision_energy_relative':float(np.max(abs(ce))/max(1.,np.max(nu)*np.max(abs(rho)))),
          'rho_mean':float(rho.mean()),'geometric_work_mean':float((-4*H*rho-np.einsum('ij,xij->x',S,pi)).mean()),
          'collision_energy_mean':float(ce.mean())}


class PhysicalHistory:
    """Semidiscrete spatial PDE, physical carrier, pinned P8 tensor-rate RHS."""
    def __init__(self,op:Transport,J0,rtol=2e-11,atol=2e-13):
        self.op=op;self.J0=op.check(J0).copy()
        def rhs(t,y):return op.physical_rhs(t,y.reshape(op.shape)).ravel()
        self.solution=solve_ivp(rhs,(0,op.end),self.J0.ravel(),method='DOP853',rtol=rtol,atol=atol,dense_output=True)
        if not self.solution.success:raise RuntimeError(self.solution.message)
    def state(self,t):return self.solution.sol(self.op.geo._time(t)).reshape(self.op.shape)


class CharacteristicHistory:
    """Independent RK4 of screen and spatial characteristic pullback.

    No physical-carrier/direct RHS is called. Both methods share prescribed
    geometry and quadrature, not radiation histories. A finite Fourier shift
    is exact for the retained spatial representation, not continuum-tail exact.
    """
    def __init__(self,op:Transport,J0,steps:int):
        if not isinstance(steps,int) or steps<1:raise ValueError('Positive integer step count required')
        self.op=op;J0=op.check(J0);Y=op.pull(0.,J0)
        self.times=np.linspace(0.,op.end,steps+1);self.values=[Y.copy()];rates=[]
        h=op.end/steps
        for t in self.times[:-1]:
            k1=op.characteristic_rhs(t,Y);rates.append(k1)
            k2=op.characteristic_rhs(t+h/2,Y+h*k1/2)
            k3=op.characteristic_rhs(t+h/2,Y+h*k2/2)
            k4=op.characteristic_rhs(min(t+h,op.end),Y+h*k3)
            Y=Y+h*(k1+2*k2+2*k3+k4)/6;self.values.append(Y.copy())
        rates.append(op.characteristic_rhs(op.end,Y))
        self.values=np.asarray(self.values)
        self.spline=CubicHermiteSpline(self.times,self.values,np.asarray(rates),axis=0)
    def state(self,t):
        t=self.op.geo._time(t)
        X=self.op.line.shift(self.spline(t),-self.op.displacement(t))
        return self.op.push(t,X)
