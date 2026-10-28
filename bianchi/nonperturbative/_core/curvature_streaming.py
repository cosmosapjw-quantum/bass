"""Analytic instantaneous Bianchi-II curvature generator, normal time rates.

N = c*n_structure = kappa*a*a^T (a unit vector); A_struct=0. No small-N
expansion. For a=z, L_s=-kappa*cos(theta)*d_phi-i*s*kappa/2. The second
term includes intrinsic screen transport, not merely direction advection.
Analytic cos(theta) recurrence and representation rotations only; no angular
quadrature, direct P8 callback, finite-time closure or Einstein evolution.
DL2 convention Q+iU=sum(E+iB) spin+2 Z, photon propagation direction.
"""
from __future__ import annotations
from functools import lru_cache
import numpy as np
from scipy.linalg import expm
from .harmonic_streaming import labels, real_transform

def rank_one(kappa: float, axis) -> np.ndarray:
    a = np.asarray(axis, float)
    if a.shape != (3,) or not np.isfinite(a).all() or (not np.isfinite(kappa)) or (np.linalg.norm(a) == 0):
        raise ValueError('finite kappa and nonzero finite 3-vector required')
    a = a / np.linalg.norm(a)
    return float(kappa) * np.outer(a, a)

def axis_of(N):
    N = np.asarray(N, float)
    if N.shape != (3, 3) or not np.isfinite(N).all():
        raise ValueError('finite3x3 curvature rate required')
    scale = float(np.linalg.norm(N))
    if scale == 0:
        return (0.0, np.array([0.0, 0.0, 1.0]))
    if np.max(np.abs(N - N.T)) > 1e-12 * scale:
        raise ValueError('symmetric N required')
    vals, vec = np.linalg.eigh(N)
    idx = int(np.argmax(np.abs(vals)))
    k = float(vals[idx])
    a = vec[:, idx]
    if np.linalg.norm(N - k * np.outer(a, a)) > 1e-12 * scale:
        raise ValueError('this slice requires rank-one Bianchi-II N')
    if a[np.argmax(np.abs(a))] < 0:
        a = -a
    return (k, a)

@lru_cache(maxsize=None)
def rotation(l: int, theta: float, phi: float):
    """Active z->axis Rz(phi)Ry(theta), ordinary SO(3) spin-harmonic irrep."""
    m = np.arange(-l, l + 1)
    jp = np.zeros((2 * l + 1, 2 * l + 1), complex)
    for j, mm in enumerate(m[:-1]):
        jp[j + 1, j] = np.sqrt(l * (l + 1) - mm * (mm + 1))
    jy = (jp - jp.T) / 2j
    d = np.diag(np.exp(-1j * m * phi)) @ expm(-1j * theta * jy)
    d.setflags(write=False)
    return d

def cosine_coefficient(spin, l, m):
    if l <= 0:
        return 0.0
    return np.sqrt(max(0.0, (l * l - m * m) * (l * l - spin * spin) / (l * l * (4 * l * l - 1))))

def curvature_matrix(spin: int, lin: int, lout: int, N) -> np.ndarray:
    if spin not in (0, 2) or not abs(spin) <= lin <= lout <= 8:
        raise ValueError('Require spin0/2 and |spin|<=Lin<=Lout<=8')
    k, a = axis_of(N)
    theta = float(np.arccos(np.clip(a[2], -1, 1)))
    phi = float(np.arctan2(a[1], a[0]))
    out = np.zeros((len(labels(spin, lout)), len(labels(spin, lin))), complex)
    ro = 0
    for l in range(abs(spin), lout + 1):
        ci = 0
        for lp in range(abs(spin), lin + 1):
            if abs(l - lp) <= 1:
                block = np.zeros((2 * l + 1, 2 * lp + 1), complex)
                for m in range(-min(l, lp), min(l, lp) + 1):
                    if l == lp:
                        diag = spin / 2 - spin * m * m / (l * (l + 1)) if l else 0.0
                        block[l + m, lp + m] = -1j * k * diag
                    else:
                        block[l + m, lp + m] = -1j * k * m * cosine_coefficient(spin, max(l, lp), m)
                block = rotation(l, theta, phi) @ block @ rotation(lp, theta, phi).conj().T
                block = real_transform(l).conj() @ block @ real_transform(lp).T
                out[ro:ro + 2 * l + 1, ci:ci + 2 * lp + 1] = block
            ci += 2 * lp + 1
        ro += 2 * l + 1
    return out

def curvature_rhs(c: dict, N, lout: int | None=None) -> dict:
    for (f, l, m), v in c.items():
        if f not in ('I', 'E', 'B', 'V') or l < 0 or abs(m) > l or (l > 6) or (f in ('E', 'B') and l < 2) or (not np.isfinite(v)):
            raise ValueError('finite valid coefficient with ell<=6 required')
    lin = max([2] + [k[1] for k in c])
    lout = lin + 1 if lout is None else lout
    a0 = curvature_matrix(0, lin, lout, N)
    a2 = curvature_matrix(2, lin, lout, N)
    out = {}
    for f in ('I', 'V'):
        y = a0 @ np.array([c.get((f, l, m), 0.0) for l, m in labels(0, lin)])
        if np.max(abs(y.imag)) > 2e-11:
            raise ArithmeticError('scalar reality violation')
        out.update({(f, l, m): float(v.real) for (l, m), v in zip(labels(0, lout), y)})
    y = a2 @ np.array([c.get(('E', l, m), 0.0) + 1j * c.get(('B', l, m), 0.0) for l, m in labels(2, lin)])
    for (l, m), v in zip(labels(2, lout), y):
        out['E', l, m] = float(v.real)
        out['B', l, m] = float(v.imag)
    return out
