"""DV2-D: exact instantaneous spin0/spin2 class-B Bianchi-V generator.

A=c*a_struct is a physical normal-time rate, NOT fluid acceleration and NOT
Hubble-normalized A/H. Numerical rates multiply T_star when time=u=t/T_star.
N=0; photon propagation direction; pinned DL2 Q+iU=sum(E+iB) spin+2 Z.
L_A=grad_S2(A.n).D_s, no Doppler/amplitude factor and no extra intrinsic twist.
Wigner construction uses no angular quadrature or direct RHS. Finite input
support Lin generates Lin+1 output; a smaller output is an explicit projection.
This is not a finite-time hierarchy, a general class-B solver or an EFE solution.
"""
from __future__ import annotations
from functools import lru_cache
from math import pi, sqrt
import numpy as np
from sympy.physics.wigner import wigner_3j
from .harmonic_streaming import labels, real_transform, coefficient_rhs as shear_rhs

def _vector(A):
    A = np.asarray(A, float)
    if A.shape != (3,) or not np.isfinite(A).all():
        raise ValueError('finite physical structure-rate three-vector required')
    return A

@lru_cache(maxsize=None)
def dipole_gaunt(spin: int, l: int, lp: int) -> np.ndarray:
    """Integral conj(sY_lm) Y_1M sY_lpmp, not fitted to quadrature."""
    out = np.zeros((2 * l + 1, 2 * lp + 1, 3))
    if abs(l - lp) <= 1 and l + lp >= 1:
        pref = sqrt((2 * l + 1) * 3 * (2 * lp + 1) / (4 * pi)) * float(wigner_3j(l, 1, lp, spin, 0, -spin))
        if pref:
            for m in range(-l, l + 1):
                for mp in range(max(-lp, m - 1), min(lp, m + 1) + 1):
                    out[m + l, mp + lp, m - mp + 1] = (-1) ** (m + spin) * pref * float(wigner_3j(l, 1, lp, -m, m - mp, mp))
    out.setflags(write=False)
    return out

def _matrix(spin, lin, lout, A, gradient):
    if spin not in (0, 2) or not abs(spin) <= lin <= lout <= 8:
        raise ValueError('Require spin0/2, |spin|<=Lin<=Lout<=8')
    A = _vector(A)
    ar = sqrt(4 * pi / 3) * A[[1, 2, 0]]
    ac = real_transform(1).T @ ar
    out = np.zeros((len(labels(spin, lout)), len(labels(spin, lin))), complex)
    ro = 0
    for l in range(abs(spin), lout + 1):
        ci = 0
        for lp in range(abs(spin), lin + 1):
            if abs(l - lp) <= 1:
                gc = np.einsum('ijm,m->ij', dipole_gaunt(spin, l, lp), ac)
                block = real_transform(l).conj() @ gc @ real_transform(lp).T
                pref = (lp * (lp + 1) - l * (l + 1) + 2) / 2 if gradient else 1.0
                out[ro:ro + 2 * l + 1, ci:ci + 2 * lp + 1] = pref * block
            ci += 2 * lp + 1
        ro += 2 * l + 1
    return out

def classb_matrix(spin: int, lin: int, lout: int, A) -> np.ndarray:
    """Analytic grad(alpha).D matrix; caller owns any finite-L truncation."""
    return _matrix(spin, lin, lout, A, True)

def multiplication_matrix(spin: int, lin: int, lout: int, A) -> np.ndarray:
    """Multiplication by alpha=A.n. B+B^dagger=2 alpha on a fixed band."""
    return _matrix(spin, lin, lout, A, False)

def coefficient_rhs(c: dict, A, H: float=0.0, S=None, nu: float=0.0, lout: int | None=None) -> dict:
    """Class-B drift plus inherited shear/dilution/full-polarized rest Thomson."""
    A = _vector(A)
    for (f, l, m), v in c.items():
        if f not in ('I', 'E', 'B', 'V') or not isinstance(l, int) or (not isinstance(m, int)) or (l < 0) or (l > 6) or (abs(m) > l) or (f in ('E', 'B') and l < 2) or (not np.isfinite(v)):
            raise ValueError('valid finite real harmonic coefficients with ell<=6 required')
    S = np.zeros((3, 3)) if S is None else np.asarray(S, float)
    lin = max([2] + [k[1] for k in c])
    lout = lin + (2 if np.any(S) else 1) if lout is None else lout
    out = shear_rhs(c, H, S, nu, lout)
    a0 = classb_matrix(0, lin, lout, A)
    a2 = classb_matrix(2, lin, lout, A)
    for f in ('I', 'V'):
        y = a0 @ np.array([c.get((f, l, m), 0.0) for l, m in labels(0, lin)])
        if np.max(abs(y.imag)) > 2e-12:
            raise ArithmeticError('scalar reality violation')
        for (l, m), v in zip(labels(0, lout), y):
            out[f, l, m] = out.get((f, l, m), 0.0) + float(v.real)
    p = a2 @ np.array([c.get(('E', l, m), 0.0) + 1j * c.get(('B', l, m), 0.0) for l, m in labels(2, lin)])
    for (l, m), v in zip(labels(2, lout), p):
        out['E', l, m] = out.get(('E', l, m), 0.0) + float(v.real)
        out['B', l, m] = out.get(('B', l, m), 0.0) + float(v.imag)
    return out

def frozen_map(n0, A, t: float):
    """Analytic direction/solid-angle map ONLY for frozen H=S=N=0.

    A is an inverse-time vector. Photon energy ratio is one, NOT the Lorentz
    Doppler factor suggested by the identical angular Mobius map. Bounded
    |A|*|t|<=10 avoids untested near-caustic floating-point conditioning.
    """
    A = _vector(A)
    n0 = np.asarray(n0, float)
    if n0.ndim != 2 or n0.shape[1] != 3 or (not np.isfinite(n0).all()) or (np.max(abs(np.linalg.norm(n0, axis=1) - 1)) > 2e-12) or (not np.isfinite(t)):
        raise ValueError('finite unit direction rows and finite time required')
    a = float(np.linalg.norm(A))
    x = a * t
    if abs(x) > 10:
        raise ValueError('frozen map accuracy domain |A|*|t|<=10')
    if a == 0:
        return (n0.copy(), np.ones(len(n0)))
    axis = A / a
    mu = n0 @ axis
    den = np.cosh(x) - mu * np.sinh(x)
    mup = (mu * np.cosh(x) - np.sinh(x)) / den
    n = (n0 - mu[:, None] * axis) / den[:, None] + mup[:, None] * axis
    return (n, den ** (-2))
