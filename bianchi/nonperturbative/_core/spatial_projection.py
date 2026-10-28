"""BF1 fixed-gauge spatial projection of physical carriers.

Spatial axis is first. All trailing momentum labels and tensor components must
already refer to one observer and one common coframe/screen. No angular cutoff,
small-amplitude expansion, metric constraint solve, collision closure or time
integration is implemented. A projector is linear for its FIXED measure; when
that measure is metric-dependent the joint (metric, carrier) map is nonlinear.
"""
from __future__ import annotations
import numpy as np

class SpatialProjector:
    """Normalized positive spatial quadrature and its prescribed log rate.

    density contains actual positive cell-volume weights, not angular weights.
    log_rate = d(log cell_volume)/dt in the caller's explicit time unit.
    For synchronous zero-shift proper volume this is theta=-c K.
    """

    def __init__(self, density, log_rate=None):
        w = np.asarray(density, dtype=float)
        if w.ndim != 1 or len(w) == 0 or (not np.isfinite(w).all()) or np.any(w <= 0):
            raise ValueError('Strictly positive finite spatial weights required')
        scaled = w / w.max()
        p = scaled / scaled.sum()
        if np.any(p <= 0):
            raise ValueError('Spatial measure underflows; use a bounded fixture')
        rate = np.zeros_like(p) if log_rate is None else np.asarray(log_rate, float)
        if rate.shape != p.shape or not np.isfinite(rate).all():
            raise ValueError('Finite logarithmic volume rate must match weights')
        self.p = p.copy()
        self.rate = rate.copy()
        self.weight_rate = self.p * (self.rate - np.dot(self.p, self.rate))
        for a in (self.p, self.rate, self.weight_rate):
            a.setflags(write=False)

    @classmethod
    def from_log_volume(cls, log_volume, log_rate=None):
        lv = np.asarray(log_volume, float)
        if lv.ndim != 1 or len(lv) == 0 or (not np.isfinite(lv).all()):
            raise ValueError('Finite one-dimensional log volume required')
        return cls(np.exp(lv - lv.max()), log_rate)

    def _field(self, field):
        f = np.asarray(field)
        if f.ndim < 1 or f.shape[0] != len(self.p) or (not np.isfinite(f).all()):
            raise ValueError('Finite field with matching leading spatial axis required')
        return f

    def mean(self, field):
        f = self._field(field)
        return np.tensordot(self.p, f, axes=(0, 0))

    def project(self, field):
        f = self._field(field)
        return np.broadcast_to(self.mean(f), f.shape).copy()

    def mean_pdot(self, field):
        """Partial time derivative of the measure map at fixed common-frame field."""
        f = self._field(field)
        return np.tensordot(self.weight_rate, f - self.mean(f), axes=(0, 0))

    def pdot(self, field):
        f = self._field(field)
        return np.broadcast_to(self.mean_pdot(f), f.shape).copy()

    def split(self, field):
        f = self._field(field)
        bg = self.project(f)
        return (bg, f - bg)

    def mean_rate(self, field, rhs):
        f = self._field(field)
        r = self._field(rhs)
        if r.shape != f.shape:
            raise ValueError('Field and rate shapes differ')
        return self.mean(r) + self.mean_pdot(f)

    def split_rhs(self, field, rhs):
        """Exact algebraic projection of the FULL supplied nonlinear RHS."""
        f = self._field(field)
        r = self._field(rhs)
        if r.shape != f.shape:
            raise ValueError('Field and RHS shapes differ')
        db = np.broadcast_to(self.mean_rate(f, r), f.shape).copy()
        return (db, r - db)

def _rotations(R, count):
    R = np.asarray(R, float)
    if R.shape != (count, 3, 3) or not np.isfinite(R).all():
        raise ValueError('One finite rotation per spatial cell required')
    gram = R @ R.transpose(0, 2, 1)
    if np.max(abs(gram - np.eye(3))) > 2e-11 or np.max(abs(np.linalg.det(R) - 1)) > 2e-11:
        raise ValueError('Frame maps must be proper orthogonal rotations')
    return R

def _carrier(local):
    f = np.asarray(local, float)
    if f.ndim != 4 or f.shape[-2:] != (3, 3) or (not np.isfinite(f).all()):
        raise ValueError('Finite P8 carrier (space, direction,3,3) required')
    return f

def align_carrier(local, R, local_directions, reference_directions):
    """Map paired physical rays from local triads to the common triad.

    R maps local vector components to common components. This is not angular
    interpolation: local_directions MUST map to the supplied reference rays.
    No Lorentz boosts or frequency remapping are silently performed here.
    """
    f = _carrier(local)
    R = _rotations(R, len(f))
    nl = np.asarray(local_directions, float)
    nr = np.asarray(reference_directions, float)
    if nl.shape != f.shape[:2] + (3,) or nr.shape != (f.shape[1], 3):
        raise ValueError('Direction label shapes do not match carrier')
    if not np.isfinite(nl).all() or not np.isfinite(nr).all():
        raise ValueError('Finite directions required')
    mapped = np.einsum('xai,xni->xna', R, nl)
    if np.max(abs(np.linalg.norm(nr, axis=1) - 1)) > 2e-11 or np.max(abs(mapped - nr[None])) > 2e-11:
        raise ValueError('Rays are not aligned; a separate remapping adapter is required')
    return np.einsum('xai,xnij,xbj->xnab', R, f, R)

def align_rate(local, local_rate, R, Rdot):
    """Derivative of R J R^T at fixed paired reference rays.

    Both the tensor rotation derivative and any moving angular-argument term
    must be accounted for. The latter is assumed included in local_rate by the
    caller's paired-ray construction; this routine does not infer it.
    """
    f = _carrier(local)
    df = _carrier(local_rate)
    if df.shape != f.shape:
        raise ValueError('Carrier and derivative shapes differ')
    R = _rotations(R, len(f))
    dR = np.asarray(Rdot, float)
    if dR.shape != R.shape or not np.isfinite(dR).all():
        raise ValueError('Finite Rdot required')
    omega = dR @ R.transpose(0, 2, 1)
    if np.max(abs(omega + omega.transpose(0, 2, 1))) > 2e-11:
        raise ValueError('Rdot must be tangent to SO(3)')
    return np.einsum('xai,xnij,xbj->xnab', R, df, R) + np.einsum('xai,xnij,xbj->xnab', dR, f, R) + np.einsum('xai,xnij,xbj->xnab', R, f, dR)

def physical_from_log_shape(logG, shape):
    """Recover the full carrier before spatial averaging; never average logG.

    This bounded float64 adapter refuses overflow AND exponential underflow;
    a production dynamic-range/log-sum-exp adapter is a separate obligation.
    Signed fluctuations should be formed after this operation, not clipped.
    """
    f = _carrier(shape)
    lg = np.asarray(logG, float)
    if lg.shape != f.shape[:2] or not np.isfinite(lg).all():
        raise ValueError('logG shape/values invalid')
    with np.errstate(over='raise', under='raise', invalid='raise'):
        out = np.exp(lg)[..., None, None] * f
    return out

def rotation_z(angles, rates=None):
    a = np.atleast_1d(np.asarray(angles, float))
    if a.ndim != 1 or not np.isfinite(a).all():
        raise ValueError('Finite angles required')
    w = np.zeros_like(a) if rates is None else np.broadcast_to(np.asarray(rates, float), a.shape)
    if not np.isfinite(w).all():
        raise ValueError('Finite angular rates required')
    c, s = (np.cos(a), np.sin(a))
    R = np.zeros((len(a), 3, 3))
    dR = np.zeros_like(R)
    R[:, 0, 0] = R[:, 1, 1] = c
    R[:, 0, 1] = -s
    R[:, 1, 0] = s
    R[:, 2, 2] = 1
    dR[:, 0, 0] = dR[:, 1, 1] = -w * s
    dR[:, 0, 1] = -w * c
    dR[:, 1, 0] = w * c
    return (R, dR)

def flat_torus_constraints(K, energy_source, length):
    """Restricted ADM diagnostic: gamma=I, x-only periodic fields, Lambda=j=0.

    K=-1/(2c) d_t gamma has units 1/length. energy_source is 16*pi*G*epsilon/c^4
    in inverse-length squared. The momentum residual is d_j(K_ij-delta_ij K).
    This is not a general metric/curvature constraint implementation.
    """
    K = np.asarray(K, float)
    s = np.asarray(energy_source, float)
    if K.ndim != 3 or K.shape[1:] != (3, 3) or len(K) < 4 or (s.shape != (len(K),)):
        raise ValueError('K shape (Nx,3,3) and energy source (Nx,) required')
    if not np.isfinite(K).all() or not np.isfinite(s).all() or (not np.isfinite(length)) or (length <= 0):
        raise ValueError('Finite fields and positive torus length required')
    if np.max(abs(K - K.transpose(0, 2, 1))) > 2e-11:
        raise ValueError('Symmetric K required')
    tr = np.trace(K, axis1=1, axis2=2)
    ham = tr ** 2 - np.einsum('xij,xij->x', K, K) - s
    flux = K[:, :, 0].copy()
    flux[:, 0] -= tr
    k = 2 * np.pi * np.fft.fftfreq(len(K), d=length / len(K))
    mom = np.fft.ifft(1j * k[:, None] * np.fft.fft(flux, axis=0), axis=0).real
    return (ham, mom)
