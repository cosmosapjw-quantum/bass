"""Positive homogeneous collisionless packets in fixed L,Pstar units.

Opt-in research closure. Weights represent proper-frame number density times
kappa L^2 c Pstar, not invariant d^3k/E weights. No collision or emission.
"""
from __future__ import annotations
import numpy as np
from vendor import core as bg


def _real(value, name):
    if np.iscomplexobj(value):
        raise ValueError(f'{name}: real values required')
    out = np.asarray(value, dtype=float)
    if not np.all(np.isfinite(out)):
        raise ValueError(f'{name}: finite values required')
    return out


def packet_arrays(k, w, mass):
    k, w, mass = (_real(k, 'k'), _real(w, 'weight'), _real(mass, 'mass'))
    if k.ndim != 2 or k.shape[1] != 3 or w.shape != (len(k),) or mass.shape != (len(k),):
        raise ValueError('expected k[N,3], w[N], mass[N]')
    if len(k) == 0 or np.any(w < 0) or np.any(mass < 0):
        raise ValueError('nonempty nonnegative packet measure required')
    e = np.hypot(mass, np.linalg.norm(k, axis=1))
    if np.any(e <= 0) or not np.all(np.isfinite(e)):
        raise ValueError('positive finite mass-shell energy required')
    return k, w, mass, e


def moments(k, w, mass):
    k, w, mass, e = packet_arrays(k, w, mass)
    rho = np.sum(w*e)
    flux = np.einsum('q,qi->i', w, k)
    pressure = np.einsum('q,qi,qj->ij', w/e, k, k)
    pbar = np.trace(pressure)/3
    pi = pressure-np.eye(3)*pbar
    # Encode the analytic STF representation, rather than impose a physical
    # positivity projection or renormalize the kinetic source.
    pi[2, 2] = -pi[0, 0]-pi[1, 1]
    if not all(np.all(np.isfinite(x)) for x in (rho,flux,pbar,pi)):
        raise ValueError('moment arithmetic overflow')
    return rho, flux, pbar, pi


def tensor(k, w, mass):
    k, w, mass, e = packet_arrays(k, w, mass)
    p4 = np.column_stack((e, k))
    return np.einsum('q,qa,qb->ab', w/e, p4, p4)


def flow(k, mass, h, sigma, n, a, rotation=(0.,0.,0.)):
    k, _, mass, e = packet_arrays(k, np.ones(len(k)), mass)
    sigma, n, a, rotation = (_real(sigma,'sigma'),_real(n,'n'),_real(a,'a'),_real(rotation,'rotation'))
    if sigma.shape!=(3,3) or n.shape!=(3,3) or a.shape!=(3,) or rotation.shape!=(3,) or not np.isfinite(h):
        raise ValueError('invalid geometry')
    bg._symmetric(sigma,'sigma',tracefree=True); bg._symmetric(n,'n')
    spatial = (k@a)[:,None]*k - np.sum(k*k,axis=1)[:,None]*a - np.cross(k,k@n.T)
    dk = -h*k-k@sigma.T+np.cross(rotation,k)+spatial/e[:,None]
    dlogw = -3*h+2*(k@a)/e
    if not np.all(np.isfinite(dk)) or not np.all(np.isfinite(dlogw)):
        raise ValueError('characteristic arithmetic overflow')
    return dk, dlogw


def boost_matrix(beta):
    beta=_real(beta,'beta')
    if beta.shape!=(3,):raise ValueError('beta must be a 3-vector')
    b2=beta@beta
    if b2>=1:raise ValueError('subluminal boost required')
    gamma=1/np.sqrt(1-b2)
    B=np.eye(4); B[0,0]=gamma; B[0,1:]=gamma*beta; B[1:,0]=gamma*beta
    B[1:,1:]+=gamma*gamma/(gamma+1)*np.outer(beta,beta)
    return B


def boost(k, w, mass, beta):
    """Active bulk-to-normal local initial-data boost, not a new background.

    d^3k/E is invariant: the proper-density quadrature weights acquire E'/E.
    Einstein/Codazzi initial constraints must still be checked by the caller.
    """
    k,w,mass,e=packet_arrays(k,w,mass)
    out=np.column_stack((e,k))@boost_matrix(beta).T
    kb,wb=out[:,1:],w*(out[:,0]/e)
    packet_arrays(kb,wb,mass)
    return kb,wb


def fd_packets(owner, mass, alpha=0., beta=(0.,0.,0.), A=0., C=0.):
    """Same finite nodes as pinned freestream, PR168 density normalization.

    Default m>=3 massive domain matches PR168; m=0 is an explicit separate
    massless FD source, not an empirical photon spectrum. No tail is dropped.
    A,C label an initial distribution only, not a constitutive EOS.
    """
    beta=_real(beta,'beta')
    if beta.shape!=(3,) or abs(np.sum(beta))>2e-14 or not np.isfinite(alpha):raise ValueError('tracefree beta required')
    if not all(np.isfinite(v) for v in (mass,A,C)) or not (mass==0 or 3<=mass<=1e5):
        raise ValueError('PR168 massive domain or explicitly massless source required')
    if not (-1<=A<=2 and abs(C)<=.4) or min(1+A,1-A/2+C,1-A/2-C)<0:
        raise ValueError('nonnegative source within donor angular domain required')
    if not (0<=alpha<=np.log(21/5)+1e-9 and np.max(np.abs(beta))<=1):
        raise ValueError('donor diagonal chart domain exceeded')
    q,dq,nhat,wa=owner._Q,owner._DQ,owner._NHAT,owner._WANG
    rw=dq*q*q*owner.f_fermi_dirac(q)
    norm=4*np.pi*np.sum(rw*np.hypot(mass,q))
    angular=1+A*(3*nhat[:,2]**2-1)/2+C*(nhat[:,0]**2-nhat[:,1]**2)
    k=(q[:,None,None]*nhat[None,:,:]*np.exp(-alpha-beta)[None,None,:]).reshape(-1,3)
    w=(rw[:,None]*(wa*angular)[None,:]*np.exp(-3*alpha)/norm).ravel()
    m=np.full(len(w),mass)
    packet_arrays(k,w,m)
    return k,w,m


class CoupledPackets:
    """Two-way Einstein/packet closure with independent rho/flux ledgers.

    State = existing core state + row-major k[N,3] + log(w)[N].
    Positive weights are represented logarithmically. Physical underflow and
    overflow are explicit failures, never silent removal of packets.
    """
    def __init__(self,mass,sectors,*,cosmological_constant=0.,rotation=(0.,0.,0.)):
        self.mass=_real(mass,'mass'); self.sectors=np.asarray(sectors)
        if self.mass.ndim!=1 or len(self.mass)==0 or np.any(self.mass<0) or self.sectors.shape!=self.mass.shape or self.sectors.dtype.kind not in 'iu':
            raise ValueError('invalid mass/sector arrays')
        if np.min(self.sectors)<0 or not np.array_equal(np.unique(self.sectors),np.arange(np.max(self.sectors)+1)):
            raise ValueError('sector IDs must be consecutive from zero')
        self.ns=int(np.max(self.sectors))+1; self.nb=16+4*self.ns
        self.lam=float(cosmological_constant); self.rotation=_real(rotation,'rotation')
        if not np.isfinite(self.lam) or self.rotation.shape!=(3,):raise ValueError('invalid constant geometry inputs')

    def decode(self,z):
        z=_real(z,'coupled state');N=len(self.mass)
        if z.shape!=(self.nb+4*N,):raise ValueError('invalid coupled state size')
        k=z[self.nb:self.nb+3*N].reshape(N,3)
        with np.errstate(over='ignore',under='ignore'): w=np.exp(z[self.nb+3*N:])
        if np.any(w<=0) or not np.all(np.isfinite(w)):raise ValueError('packet weight outside representable positive range')
        return bg.State.unpack(z[:self.nb],self.ns),k,w

    def moment_blocks(self,k,w):
        values=[moments(k[self.sectors==i],w[self.sectors==i],self.mass[self.sectors==i]) for i in range(self.ns)]
        rho=np.array([x[0] for x in values]);f=np.array([x[1] for x in values])
        src=bg.Source(np.array([x[2] for x in values]),np.array([x[3] for x in values]))
        return rho,f,src

    def initial(self,h,sigma,n,a,k,w,alpha=0.):
        packet_arrays(k,w,self.mass)
        if np.any(np.asarray(w)<=0):raise ValueError('log-weight evolution requires strictly positive packets')
        rho,f,_=self.moment_blocks(k,w)
        y=bg.State(h,np.asarray(sigma),np.asarray(n),np.asarray(a),alpha,rho,f)
        y.validate()
        return np.r_[y.pack(),np.ravel(k),np.log(w)]

    def rhs(self,t,z):
        y,k,w=self.decode(z);_,_,src=self.moment_blocks(k,w)
        dy=bg.rhs(t,z[:self.nb],src,cosmological_constant=self.lam,rotation=self.rotation)
        dk,dlw=flow(k,self.mass,y.h,y.sigma,y.n,y.a,self.rotation)
        return np.r_[dy,dk.ravel(),dlw]
