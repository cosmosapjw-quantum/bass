"""Invariant photon event rates, distinct from kinetic density quadrature.

r=c*p is in joules; dR has units m^-3 s^-1 per invariant proper four-volume/c.
Rates are unchanged on boosts. K(u) uses the observer-dependent denominator.
"""
from dataclasses import dataclass
from itertools import product
import math
import numpy as np

C = 299792458.0
G = 6.67430e-11


def real_array(value, name, shape=None):
    def boolean(x):
        if isinstance(x, (bool, np.bool_)):
            return True
        if isinstance(x, (list, tuple)):
            return any(boolean(a) for a in x)
        if isinstance(x, np.ndarray):
            return x.dtype.kind == 'b' or (x.dtype.kind == 'O' and any(boolean(a) for a in x.flat))
        return False
    raw = np.asarray(value)
    if boolean(value) or raw.dtype.kind not in 'iuf' or not np.all(np.isfinite(raw)):
        raise ValueError(f'{name} must be finite, real and non-boolean')
    a = np.array(raw, dtype=float, copy=True)
    if shape is not None and a.shape != shape:
        raise ValueError(f'invalid {name} shape')
    a.setflags(write=False)
    return a


def positive(value, name):
    a = real_array(value, name, ())
    if a <= 0:
        raise ValueError(f'{name} must be positive')
    return float(a)


@dataclass(frozen=True)
class Identity:
    owner: str
    epoch: str
    frame: str
    clock: str
    provenance: str

    def __post_init__(self):
        if not all(isinstance(x, str) and x for x in self.__dict__.values()):
            raise ValueError('nonempty owner, epoch, frame, clock and provenance required')


@dataclass(frozen=True)
class PhotonEventMeasure:
    energy_J: np.ndarray
    directions: np.ndarray
    rates_m3_s: np.ndarray
    identity: Identity

    def __post_init__(self):
        e = real_array(self.energy_J, 'energy')
        w = real_array(self.rates_m3_s, 'gross event rate')
        n = real_array(self.directions, 'directions')
        if not isinstance(self.identity, Identity) or e.ndim != 1 or e.size == 0 or n.shape != (len(e), 3) or w.shape != e.shape:
            raise ValueError('invalid event representation')
        if np.any(e <= 0) or np.any(w < 0) or np.max(np.abs(np.sum(n*n,axis=1)-1)) > 5e-13:
            raise ValueError('positive energies, nonnegative gross rates and unit directions required')
        for name, value in [('energy_J',e),('directions',n),('rates_m3_s',w)]:
            object.__setattr__(self,name,value)

    @property
    def r(self):
        return np.column_stack((self.energy_J, self.energy_J[:,None]*self.directions))

    def boosted(self, beta, *, frame):
        if not isinstance(frame,str) or not frame:
            raise ValueError('explicit destination frame required')
        r = self.r @ boost_matrix(beta).T
        return PhotonEventMeasure(r[:,0], r[:,1:]/r[:,0,None], self.rates_m3_s,
                                  Identity(self.identity.owner,self.identity.epoch,frame,
                                           self.identity.clock,self.identity.provenance))


def boost_matrix(beta):
    v = real_array(beta, 'beta', (3,))
    b2 = float(v@v)
    if b2 >= 1:
        raise ValueError('beta squared must be below one')
    gamma = 1/math.sqrt(1-b2)
    L = np.eye(4)
    L[0,0] = gamma
    L[0,1:] = L[1:,0] = gamma*v
    L[1:,1:] += gamma**2/(gamma+1)*np.outer(v,v)
    return L


@dataclass(frozen=True)
class MomentResult:
    cQ_J_m3_s: np.ndarray
    K_J_m3_s: np.ndarray
    PiRate_J_m3_s: np.ndarray | None
    number_rate_m3_s: float
    identity: Identity
    observer: np.ndarray


def moments(events, *, observer=(1.,0.,0.,0.)):
    if not isinstance(events, PhotonEventMeasure):
        raise ValueError('PhotonEventMeasure required')
    u = real_array(observer,'observer',(4,))
    if u[0] <= 0 or abs(-u[0]**2+u[1:]@u[1:]+1) > 5e-12:
        raise ValueError('future unit timelike observer required')
    r = events.r
    denominator = u[0]*r[:,0]-r[:,1:]@u[1:]
    if np.any(denominator <= 0):
        raise ValueError('positive observer photon energy required')
    cq = events.rates_m3_s@r
    k = np.einsum('n,ni,nj->ij',events.rates_m3_s/denominator,r,r)
    # A generic observer's spatial subblock is not its physical 3D PSTF.
    # Return generic K(u), exposing PiRate3 only for the target-frame observer.
    pi = k[1:,1:]-np.eye(3)*np.trace(k[1:,1:])/3 if np.array_equal(u,[1.,0.,0.,0.]) else None
    for a in (cq,k) + (() if pi is None else (pi,)):
        if not np.all(np.isfinite(a)):
            raise ValueError('moments outside representable numeric domain')
    return MomentResult(cq,k,pi,float(np.sum(events.rates_m3_s)),events.identity,u)


@dataclass(frozen=True)
class GrossEventBundle:
    down: PhotonEventMeasure
    up: PhotonEventMeasure

    def __post_init__(self):
        if not isinstance(self.down,PhotonEventMeasure) or not isinstance(self.up,PhotonEventMeasure) or self.down.identity != self.up.identity:
            raise ValueError('two gross channels must share identity')

    def net_moments(self, *, observer=(1.,0.,0.,0.)):
        d,u = moments(self.down,observer=observer),moments(self.up,observer=observer)
        return MomentResult(d.cQ_J_m3_s-u.cQ_J_m3_s,d.K_J_m3_s-u.K_J_m3_s,
                            None if d.PiRate_J_m3_s is None else d.PiRate_J_m3_s-u.PiRate_J_m3_s,d.number_rate_m3_s-u.number_rate_m3_s,
                            d.identity,d.observer)

    def boosted(self,beta,*,frame):
        return GrossEventBundle(self.down.boosted(beta,frame=frame),self.up.boosted(beta,frame=frame))


def ab_fixture(which, identity=None):
    identity = identity or Identity('synthetic_AB','fixture','rest','proper_time','CONSTRUCTED_EXACT_AB')
    if which == 'A':
        n = np.concatenate((np.eye(3),-np.eye(3)))
    elif which == 'B':
        n = np.array(list(product((-1.,1.),repeat=3)))/math.sqrt(3)
    else:
        raise ValueError('A or B fixture required')
    return PhotonEventMeasure(np.ones(len(n)),n,np.full(len(n),1/len(n)),identity)


def exact_axis_pi_xx(which,beta):
    b = float(real_array(beta,'axis beta',()))
    if abs(b) >= 1:
        raise ValueError('axis beta outside domain')
    g = 1/math.sqrt(1-b*b)
    if which == 'A':
        return 2*g*b*b/3
    if which == 'B':
        return 2*g*b*b/3-2*b*b*math.sqrt(1-b*b)/(3*(3-b*b))
    raise ValueError('A or B fixture required')
