"""Opt-in BF3-D field reconstruction on a prescribed static periodic lapse.

Metric(-+++): ds²=-N(x)² c²dt²+Lstar² dx_i². u=t/Tstar,cbar=cTstar/Lstar.
The field variable Y=N^4 times the real P8 screen coherency is well-balanced
for I proportional to N^-4. Coordinate collision rate is N*nu_star, with
nu_star=n_e_star*sigma_T*c*Tstar. x is periodic, mu=n_x, phi is about x.
This research route does not replace Q/native defaults or solve Einstein equations.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.integrate import solve_ivp
from ._core.lapse_transport import PeriodicLapse, TetradHistory
from bianchi.q import polarization as P8


def _oracle(backend):
    if backend != 'python_oracle':
        raise ValueError("This scoped field route requires backend='python_oracle'; no native fallback")


def from_stokes(I,Q,U,V):
    I,Q,U,V=np.broadcast_arrays(I,Q,U,V)
    z=np.empty(I.shape+(2,2),float)
    z[...,0,0]=(I+Q)/2; z[...,1,1]=(I-Q)/2
    z[...,0,1]=(U-V)/2; z[...,1,0]=(U+V)/2
    return z


def stokes(y):
    return (y[...,0,0]+y[...,1,1], y[...,0,0]-y[...,1,1],
            y[...,0,1]+y[...,1,0], y[...,1,0]-y[...,0,1])


def physical_screen(y):
    t=np.swapaxes(y,-1,-2)
    return np.linalg.eigvalsh(.5*(y+t)+.5j*(y-t))


class FieldGrid:
    """Uniform odd Fourier grid and unmodified GL(mu) x periodic phi weights."""
    def __init__(self,nx:int,nmu:int,nphi:int):
        if any(not isinstance(n,(int,np.integer)) or isinstance(n,bool) for n in (nx,nmu,nphi)):
            raise ValueError('Integer sizes required')
        if nx<5 or nx%2!=1 or nmu<4 or nphi<8 or nphi%2:
            raise ValueError('Require odd nx>=5,nmu>=4,even nphi>=8')
        self.nx,self.nmu,self.nphi=nx,nmu,nphi
        self.x=2*np.pi*np.arange(nx)/nx
        self.mu,wm=leggauss(nmu);self.phi=2*np.pi*np.arange(nphi)/nphi
        self.k=np.fft.fftfreq(nx,1/nx)
        mm,pp=np.meshgrid(self.mu,self.phi,indexing='ij');ss=np.sqrt(1-mm*mm)
        self.n=np.stack((mm,ss*np.cos(pp),ss*np.sin(pp)),axis=-1).reshape(-1,3)
        bt=np.stack((-ss,mm*np.cos(pp),mm*np.sin(pp)),axis=-1)
        bp=np.stack((np.zeros_like(pp),-np.sin(pp),np.cos(pp)),axis=-1)
        self.E=np.stack((bt,bp),axis=-1).reshape(-1,3,2)
        self.w=np.repeat(wm,nphi)*(2*np.pi/nphi)
        self.wmu=wm
        self.bw=np.array([1/np.prod(self.mu[j]-np.delete(self.mu,j)) for j in range(nmu)])
        self.bw/=np.max(abs(self.bw))
        diff=self.mu[:,None]-self.mu[None,:]
        np.fill_diagonal(diff,1.)
        self.Dmu=(self.bw[None,:]/self.bw[:,None])/diff
        np.fill_diagonal(self.Dmu,0.)
        np.fill_diagonal(self.Dmu,-self.Dmu.sum(axis=1))
        self.shape=(nx,nmu,nphi,2,2)

    def check(self,y,*,signed=False):
        if np.iscomplexobj(y): raise ValueError('Use real P8 S+A storage')
        y=np.asarray(y,float)
        if y.shape!=self.shape or not np.isfinite(y).all():
            raise ValueError(f'Finite field of shape{self.shape} required')
        if not signed and physical_screen(y).min() < -2e-10*max(1.,np.max(abs(y))):
            raise ValueError('Initial physical screen is not positive semidefinite')
        return y

    def dx(self,y):
        shape=(self.nx,)+(1,)*(y.ndim-1)
        return np.fft.ifft(1j*self.k.reshape(shape)*np.fft.fft(y,axis=0),axis=0).real

    def dmu(self,y):
        return np.einsum('ij,xj...->xi...',self.Dmu,y,optimize=True)


def stationary(g:FieldGrid,intensity:float=2.):
    return np.broadcast_to(np.eye(2)*(intensity/2),g.shape).copy()


def smooth_initial(x,mu,phi):
    x,mu,phi=np.broadcast_arrays(x,mu,phi)
    I=2+.2*np.cos(x)+.12*mu*np.sin(2*x)+.1*(3*mu**2-1)/2*np.cos(x)
    Q=.08*(1-mu**2)*np.cos(x)
    U=.06*(1-mu**2)*np.sin(2*x)
    V=.04*mu*np.cos(x)
    return from_stokes(I,Q,U,V)


def _barycentric(g,md):
    diff=md[...,None]-g.mu
    hit=abs(diff)<4*np.finfo(float).eps
    safe=np.where(hit,1.,diff)
    b=g.bw/safe
    b/=b.sum(axis=-1,keepdims=True)
    if hit.any():
        rows=hit.any(axis=-1);b[rows]=hit[rows].astype(float)
    return b


def interpolate(g:FieldGrid,y,xd,md):
    """Evaluate current trigonometric/polynomial interpolant at inverse rays.

    No phase-volume determinant multiplies a local field. This operation is not
    a positivity-preserving interpolation and not an exact finite spectral flow.
    """
    y=g.check(y,signed=True)
    xd,md=np.asarray(xd,float),np.asarray(md,float)
    if xd.shape!=(g.nx,g.nmu) or md.shape!=xd.shape or not np.isfinite(xd).all() or not np.isfinite(md).all():
        raise ValueError('Departure x and mu must be finite (nx,nmu)')
    if np.max(abs(md))>1+2e-10:raise ValueError('Departure direction outside sphere')
    phase=np.exp(1j*xd[...,None]*g.k)
    coeff=np.fft.fft(y,axis=0)/g.nx
    fourier=np.einsum('xmk,klpij->xmlpij',phase,coeff,optimize=True)
    out=np.einsum('xml,xmlpij->xmpij',_barycentric(g,md),fourier,optimize=True)
    if np.max(abs(out.imag))>2e-10*max(1.,np.max(abs(out.real))):
        raise ArithmeticError('Fourier reconstruction acquired imaginary carrier')
    return out.real


class InverseMap:
    """Reuse integrated BF3-C rays, starting at each final local angle, backward.

    The lapse depends on x only: azimuth is fixed and all azimuths share the
    same x/mu map and screen rotation. No angular or spatial Jacobian is used
    when evaluating a field at final x. Negative time is used only internally.
    """
    def __init__(self,g:FieldGrid,metric:PeriodicLapse,dt:float,*,backend=None,rtol=2e-12,atol=2e-14):
        _oracle(backend)
        if not np.isfinite(dt) or dt<=0:raise ValueError('Positive finite map duration required')
        self.grid,self.metric,self.dt=g,metric,float(dt)
        x,mu=np.meshgrid(g.x,g.mu,indexing='ij');ss=np.sqrt(1-mu*mu)
        self.final_x=x.ravel()
        self.final_n=np.stack((mu,ss,np.zeros_like(mu)),axis=-1).reshape(-1,3)
        xf=np.zeros_like(self.final_n);xf[:,0]=self.final_x
        bt=np.stack((-ss,mu,np.zeros_like(mu)),axis=-1).reshape(-1,3)
        bp=np.tile([0.,0.,1.],(len(bt),1));Ef=np.stack((bt,bp),axis=-1)
        self.rays=TetradHistory(metric,xf,self.final_n,-dt,screen0=Ef,rtol=rtol,atol=atol)
        d=self.rays.at(-dt);self.departure=d
        self.xd=d['x'][:,0].reshape(x.shape);self.md=d['n'][:,0].reshape(x.shape)
        # Canonical meridional departure basis, no normalization of solved screen.
        sd=np.sqrt(1-self.md**2)
        btd=np.stack((-sd,self.md,np.zeros_like(sd)),axis=-1).reshape(-1,3)
        Ed=np.stack((btd,bp),axis=-1)
        self.R=(Ed.swapaxes(1,2)@d['screen']).reshape(g.nx,g.nmu,2,2)
        self.killing_error=float(np.max(abs(metric.N(self.xd)*d['r'].reshape(x.shape)/metric.N(x)-1)))
        self.meridional_error=float(np.max(abs(self.R-np.eye(2))))

    def apply(self,y):
        z=interpolate(self.grid,y,self.xd,self.md)
        R=self.R[:,:,None,:,:]
        return np.swapaxes(R,-1,-2)@z@R

    def analytic(self,initial):
        """Evaluate analytic initial Y at departures, avoiding field interpolation."""
        g=self.grid
        z=np.asarray(initial(self.xd[:,:,None],self.md[:,:,None],g.phi[None,None,:]),float)
        z=np.broadcast_to(z,g.shape).copy();g.check(z,signed=True)
        R=self.R[:,:,None,:,:]
        return np.swapaxes(R,-1,-2)@z@R


@dataclass
class SampledHistory:
    times:np.ndarray
    values:list
    def at(self,t):
        idx=np.flatnonzero(np.isclose(self.times,t,rtol=0,atol=5e-14))
        if len(idx)!=1:raise ValueError('Only stored time nodes, no implicit interpolation')
        return self.values[int(idx[0])].copy()


class DirectHistory:
    def __init__(self,solver,y,tend,rtol,atol):
        self.shape=y.shape;self.tend=tend
        self.sol=solve_ivp(lambda t,z:solver.rhs(t,z.reshape(self.shape)).ravel(),(0,tend),y.ravel(),
                           method='DOP853',dense_output=True,rtol=rtol,atol=atol)
        if not self.sol.success:raise RuntimeError(self.sol.message)
        self.nfev=self.sol.nfev
    def at(self,t):
        if not np.isfinite(t) or t<0 or t>self.tend:raise ValueError('No extrapolation')
        return self.sol.sol(t).reshape(self.shape)


class LapseField:
    """Local-source collisional field on the static lapse. Explicit Python only."""
    def __init__(self,g:FieldGrid,metric:PeriodicLapse,nu_star,*,backend=None):
        _oracle(backend)
        self.grid,self.metric=g,metric
        value=nu_star(g.x) if callable(nu_star) else nu_star
        self.nu=np.broadcast_to(np.asarray(value,float),(g.nx,)).copy()
        if not np.isfinite(self.nu).all() or np.any(self.nu<0):raise ValueError('Finite nonnegative proper opacity required')
        self.N=metric.N(g.x);self.rate=self.N*self.nu
        self._maps={}

    def screen_to_cartesian(self,y):
        g=self.grid;y=g.check(y,signed=True).reshape(g.nx,-1,2,2)
        return g.E[None]@y@g.E[None].swapaxes(-1,-2)

    def carrier(self,y):
        return self.screen_to_cartesian(y)/self.N[:,None,None,None]**4

    def source(self,y):
        return np.einsum('a,xaij->xij',self.grid.w,self.carrier(y),optimize=True)

    def gain(self,y):
        g=self.grid;J=self.screen_to_cartesian(y)
        M=np.einsum('a,xaij->xij',g.w,J,optimize=True)
        out=(3/(8*np.pi))*(g.E[None].swapaxes(-1,-2)@M[:,None]@g.E[None])
        return out.reshape(g.shape)

    def collision_rhs(self,y):
        return self.rate[:,None,None,None,None]*(self.gain(y)-y)

    def collision(self,y,dt):
        g=self.grid;y=g.check(y,signed=True)
        if not np.isfinite(dt) or dt<0:raise ValueError('Nonnegative finite collision time')
        J=self.screen_to_cartesian(y)
        out=np.stack([P8.collide(g.n,g.w,J[i],dt*self.rate[i]) for i in range(g.nx)])
        return (g.E[None].swapaxes(-1,-2)@out@g.E[None]).reshape(g.shape)

    def rhs(self,t,y):
        g=self.grid;y=g.check(y,signed=True)
        vx=self.metric.cbar*self.N[:,None]*g.mu[None,:]
        vm=-self.metric.cbar*self.metric.dN(g.x)[:,None]*(1-g.mu[None,:]**2)
        return -vx[:,:,None,None,None]*g.dx(y)-vm[:,:,None,None,None]*g.dmu(y)+self.collision_rhs(y)

    def direct(self,y,tend,*,rtol=2e-11,atol=2e-13,signed=False):
        y=self.grid.check(y,signed=signed).copy()
        if not np.isfinite(tend) or tend<=0:raise ValueError('Positive finite history time required')
        return DirectHistory(self,y,float(tend),rtol,atol)

    def split(self,y,tend,steps,*,signed=False,clock_scale=1.):
        g=self.grid;y=g.check(y,signed=signed).copy()
        if not np.isfinite(tend) or tend<0 or not isinstance(steps,(int,np.integer)) or isinstance(steps,bool) or steps<1:
            raise ValueError('Nonnegative finite time and positive integer steps required')
        if clock_scale!=1.:raise ValueError('Clock modification is not part of the public solver')
        if tend==0:return SampledHistory(np.array([0.]),[y])
        h=float(tend)/steps
        if h not in self._maps:self._maps[h]=InverseMap(g,self.metric,h,backend='python_oracle')
        move=self._maps[h];times=np.linspace(0,tend,steps+1);values=[y.copy()]
        for _ in range(steps):
            y=self.collision(y,h/2);y=move.apply(y);y=self.collision(y,h/2)
            values.append(y.copy())
        return SampledHistory(times,values)

    def moments(self,y):
        J=self.carrier(y);I=np.trace(J,axis1=-2,axis2=-1);g=self.grid
        rho=I@g.w;q=np.einsum('a,xa,ai->xi',g.w,I,g.n,optimize=True)
        return rho,q

    def killing_energy(self,y):
        rho,_=self.moments(y)
        return float(2*np.pi*np.mean(self.N*rho))

    def balance(self,y,dy):
        rho,q=self.moments(y);drho,_=self.moments(dy);g=self.grid
        residual=self.N*drho+self.metric.cbar*g.dx(self.N**2*q[:,0])
        crho,_=self.moments(self.collision_rhs(y))
        return {'local_max':float(np.max(abs(residual))),
                'Killing_derivative':float(2*np.pi*np.mean(self.N*drho)),
                'collision_energy_max':float(np.max(abs(crho)))}
