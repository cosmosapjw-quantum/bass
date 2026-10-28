"""KM-2A: instantaneous polarized cold-Thomson collision in normal time.

Signature (-,+,+,+), beta=v_e/c, nu0=n_e_star*sigma_T*c in s^-1.
P8 real carrier S+A encodes physical Hermitian coherency S+iA.
No density boost, weight renormalization, positivity projection, or small-beta
expansion. This is not a finite-time integrator or production Q/Rust wiring.
"""
from __future__ import annotations
import numpy as np

def _velocity(beta):
    beta = np.asarray(beta, dtype=float)
    if beta.shape != (3,) or not np.isfinite(beta).all():
        raise ValueError('beta must be a finite dimensionless 3-vector')
    b2 = float(beta @ beta)
    if b2 >= 1.0:
        raise ValueError('Require |beta|<1')
    return (beta, 1.0 / np.sqrt(1.0 - b2))

def _directions(n):
    n = np.asarray(n, dtype=float)
    if n.ndim != 2 or n.shape[1] != 3 or len(n) == 0 or (not np.isfinite(n).all()):
        raise ValueError('Require nonempty finite (N,3) directions')
    if np.max(np.abs(np.linalg.norm(n, axis=1) - 1.0)) > 1e-10:
        raise ValueError('Directions must be unit vectors; no silent normalization')
    return n

def boost_map(n, beta):
    """Normal -> moving frame: transverse isometry S, n_e, D=E_e/E_n.

    k=gamma^2/(gamma+1) avoids (gamma-1)/beta^2 cancellation near rest.
    S includes the normal screen projector; inverse on screens is S.T.
    """
    n = _directions(n)
    beta, gamma = _velocity(beta)
    bn = n @ beta
    D = gamma * (1.0 - bn)
    k = gamma * gamma / (gamma + 1.0)
    ne = (n + (k * bn - gamma)[:, None] * beta) / D[:, None]
    P = np.eye(3) - np.einsum('ni,nj->nij', n, n)
    W = np.eye(3) + np.einsum('ni,j->nij', k * beta + gamma * ne, beta)
    S = np.einsum('nik,nkj->nij', W, P)
    return (S, ne, D)

class TiltedThomson:
    """A fixed angular-grid generator using raw normal-frame solid-angle weights.

    Source is electron M_e=int J_e dOmega_e (nine real components).
    gain() excludes the ray rate; rhs() multiplies exactly nu0*D once.
    """

    def __init__(self, n, w, beta):
        self.n = _directions(n).copy()
        self.beta, self.gamma = _velocity(beta)
        self.beta = self.beta.copy()
        self.w = np.asarray(w, dtype=float).copy()
        if self.w.shape != (len(self.n),) or not np.isfinite(self.w).all() or np.any(self.w <= 0):
            raise ValueError('Require positive finite raw solid-angle weights')
        self.S, self.ne, self.D = boost_map(self.n, self.beta)
        self.we = self.w / self.D ** 2
        self.Pe = np.eye(3) - np.einsum('ni,nj->nij', self.ne, self.ne)

    def _carrier(self, J):
        J = np.asarray(J, dtype=float)
        if J.shape != (len(self.n), 3, 3) or not np.isfinite(J).all():
            raise ValueError('Require finite real carrier shaped (N,3,3)')
        scale = max(1.0, float(np.max(abs(J))))
        leak = max(float(np.max(abs(np.einsum('nij,nj->ni', J, self.n)))), float(np.max(abs(np.einsum('nji,nj->ni', J, self.n)))))
        if leak > 1e-09 * scale:
            raise ValueError('Carrier is not transverse; no implicit projection')
        return J

    def to_electron(self, J):
        J = self._carrier(J)
        return self.D[:, None, None] ** 4 * np.einsum('nik,nkl,njl->nij', self.S, J, self.S)

    def source(self, J):
        return np.einsum('n,nij->ij', self.we, self.to_electron(J))

    def gain_from_source(self, M):
        M = np.asarray(M, dtype=float)
        if M.shape != (3, 3) or not np.isfinite(M).all():
            raise ValueError('Require finite 3x3 source')
        ge = 3.0 / (8.0 * np.pi) * np.einsum('nik,kl,nlj->nij', self.Pe, M, self.Pe)
        return np.einsum('nki,nkl,nlj->nij', self.S, ge, self.S) / self.D[:, None, None] ** 4

    def gain(self, J):
        return self.gain_from_source(self.source(J))

    def rhs(self, J, nu0):
        J = self._carrier(J)
        nu0 = float(nu0)
        if not np.isfinite(nu0) or nu0 < 0:
            raise ValueError('nu0 must be finite nonnegative rest opacity')
        if nu0 == 0:
            return np.zeros_like(J)
        return nu0 * self.D[:, None, None] * (self.gain(J) - J)

def radiation_tensor(n, w, J):
    """T00=rho, T0i=q_i=energy_flux/c, Tij=pressure in common carrier units."""
    n = _directions(n)
    w = np.asarray(w, float)
    J = np.asarray(J, float)
    if w.shape != (len(n),) or J.shape != (len(n), 3, 3):
        raise ValueError('Shape mismatch')
    l = np.c_[np.ones(len(n)), n]
    return np.einsum('n,n,na,nb->ab', w, np.trace(J, axis1=1, axis2=2), l, l)

def expected_fourforce(T, beta, nu0):
    """c*Q^a=nu0 (delta^a_b+U^a U_b) T^{bc} U_c; U=u_e/c.

    Returned normal-frame moments are (rho_dot,q_dot), not T_dot transformed
    as a tensor: this collision-only update is on a normal-time slice.
    """
    beta, gamma = _velocity(beta)
    T = np.asarray(T, float)
    nu0 = float(nu0)
    if T.shape != (4, 4) or not np.isfinite(T).all() or (not np.isfinite(nu0)) or (nu0 < 0):
        raise ValueError('Invalid stress tensor or rest rate')
    U = gamma * np.r_[1.0, beta]
    Uc = U * np.array([-1.0, 1.0, 1.0, 1.0])
    return nu0 * (T @ Uc + U * (Uc @ T @ Uc))
