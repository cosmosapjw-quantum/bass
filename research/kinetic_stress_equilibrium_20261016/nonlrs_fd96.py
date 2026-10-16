"""Source-locked diagonal Bianchi-I FD96 moments; source-only research evaluator.

The canonical momentum grid and Fermi-Dirac radial source follow
``bianchi.matter.freestream``.  The density is divided by the same reference
FD96 energy integral used by PR164/PR167.  A reflection-odd angular modifier
may be inspected, but cannot be admitted as a diagonal Einstein source.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
import pathlib
import sys
from typing import Callable

import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.optimize import root

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from bianchi.matter import freestream


XMAX = math.log(21.0 / 5.0)
B = np.array([[1.0, 0.0], [0.0, 1.0], [-1.0, -1.0]])
AngularModifier = Callable[[np.ndarray], np.ndarray]


@dataclass(frozen=True)
class TensorMoments:
    rho: float
    pressure: np.ndarray
    pi: np.ndarray
    hessian3: np.ndarray
    hessian2: np.ndarray
    energy_gradient2: np.ndarray
    parity_defect: float
    offdiagonal_max: float
    quadrature_weight_min: float

    @property
    def pbar(self) -> float:
        return float(np.trace(self.pressure) / 3.0)


class FD96Diagonal:
    """Fixed-source two-anisotropy chart beta=(u,v,-u-v), |beta_i|<=1."""

    def __init__(self, mass: float, A: float, radial: int = 96,
                 polar: int = 24, azimuth: int = 24,
                 permutation: tuple[int, int, int] = (0, 1, 2),
                 triaxial_C: float = 0.0):
        if not (math.isfinite(mass) and 3.0 <= mass <= 1e5):
            raise ValueError("FD96_MASS_DOMAIN")
        if not (math.isfinite(A) and -1.0 <= A <= 2.0):
            raise ValueError("FD96_POSITIVE_ANGULAR_SOURCE")
        if not math.isfinite(triaxial_C) or abs(triaxial_C) > .4:
            raise ValueError("FD96_TRIAXIAL_EXTENSION_DOMAIN")
        if min(1.0 + A, 1.0 - A/2.0 + triaxial_C,
               1.0 - A/2.0 - triaxial_C) < 0.0:
            raise ValueError("FD96_NONPOSITIVE_CONTINUOUS_ANGULAR_SOURCE")
        if not (32 <= radial <= 192 and 8 <= polar <= 128 and
                8 <= azimuth <= 128 and azimuth % 4 == 0):
            raise ValueError("FD96_QUADRATURE_DOMAIN")
        if tuple(sorted(permutation)) != (0, 1, 2):
            raise ValueError("FD96_AXIS_PERMUTATION")
        self.mass, self.A, self.triaxial_C = float(mass), float(A), float(triaxial_C)
        self.resolution = (radial, polar, azimuth)
        self.permutation = tuple(permutation)
        if (radial, polar, azimuth) == (96, 24, 24):
            q, dq = freestream._Q.copy(), freestream._DQ.copy()
            nhat, wang = freestream._NHAT.copy(), freestream._WANG.copy()
        else:
            xr, wr = leggauss(radial)
            mu, wm = leggauss(polar)
            phi = 2.0 * np.pi * (np.arange(azimuth) + .5) / azimuth
            q = 3.0 * (1.0 + xr) / (1.0 - xr)
            dq = wr * 6.0 / (1.0 - xr) ** 2
            st = np.sqrt(1.0 - mu**2)
            nhat = np.stack((np.outer(st, np.cos(phi)).ravel(),
                             np.outer(st, np.sin(phi)).ravel(),
                             np.outer(mu, np.ones_like(phi)).ravel()), axis=-1)
            wang = np.outer(wm, np.full(azimuth, 2.0 * np.pi / azimuth)).ravel()
        self.q, self.dq = q, dq
        self.nhat = nhat[:, self.permutation]
        self.wang = wang
        self.axis = self.permutation.index(2)
        self.transverse_x = self.permutation.index(0)
        self.transverse_y = self.permutation.index(1)
        self.radial_weight = dq * q**2 * freestream.f_fermi_dirac(q)
        self.norm = float(self.radial_weight @ np.hypot(self.mass, q))
        if not (self.norm > 0 and np.min(self.radial_weight) > 0 and
                abs(sum(wang) / (4.0 * np.pi) - 1.0) < 3e-14):
            raise ArithmeticError("FD96_SOURCE_NORMALIZATION")

    def _weights(self, modifier: AngularModifier | None):
        n = self.nhat
        p2 = .5 * (3.0 * n[:, self.axis] ** 2 - 1.0)
        # C=0 is the exact parent axisymmetric angular source.  C!=0 is an
        # explicitly separate, reflection-even positive FD96 radial extension.
        base = (1.0 + self.A * p2 + self.triaxial_C *
                (n[:, self.transverse_x]**2 - n[:, self.transverse_y]**2))
        if modifier is None:
            factor = np.ones(len(n))
            parity = 0.0
        else:
            factor = np.asarray(modifier(n), dtype=float)
            if factor.shape != (len(n),):
                raise ValueError("FD96_ANGULAR_MODIFIER_SHAPE")
            if not np.all(np.isfinite(factor)) or np.min(factor) < 0.0:
                raise ValueError("FD96_NONPOSITIVE_PHASE_SPACE_WEIGHT")
            parity = 0.0
            for i in range(3):
                reflected = n.copy()
                reflected[:, i] *= -1.0
                counterpart = np.asarray(modifier(reflected), dtype=float)
                if counterpart.shape != factor.shape:
                    raise ValueError("FD96_ANGULAR_MODIFIER_SHAPE")
                if not np.all(np.isfinite(counterpart)) or np.min(counterpart) < 0.0:
                    raise ValueError("FD96_NONPOSITIVE_PHASE_SPACE_WEIGHT")
                parity = max(parity, float(np.max(np.abs(factor - counterpart))))
        aw = self.wang * base * factor
        with np.errstate(over="ignore"):
            total = np.sum(aw)
        if (not np.all(np.isfinite(aw)) or np.min(aw) < 0.0 or
                not np.isfinite(total) or total <= 0.0):
            raise ValueError("FD96_NONPOSITIVE_PHASE_SPACE_WEIGHT")
        return aw, parity

    def moments(self, x: float, beta2: tuple[float, float] | np.ndarray,
                *, modifier: AngularModifier | None = None,
                diagonal_only: bool = True) -> TensorMoments:
        u = np.asarray(beta2, dtype=float)
        if u.shape != (2,) or not np.all(np.isfinite(u)) or not math.isfinite(x):
            raise ValueError("FD96_NONFINITE_STATE")
        beta = B @ u
        if not (0.0 <= x <= XMAX + 1e-9 and np.max(np.abs(beta)) <= 1.0):
            raise ValueError("FD96_CHART")
        aw, parity = self._weights(modifier)
        if diagonal_only and parity > 1e-12:
            raise ValueError("FD96_OFFDIAGONAL_SOURCE_PARITY")
        r = math.exp(-x)
        p = (r * self.q[:, None, None]) * self.nhat[None, :, :] * np.exp(-beta)[None, None, :]
        w = p * p
        E = np.sqrt(self.mass**2 + np.sum(w, axis=2))
        weight = self.radial_weight[:, None] * aw[None, :] * (r**3 / (4.0 * np.pi * self.norm))
        with np.errstate(over="ignore", invalid="ignore"):
            rho = float(np.sum(weight * E))
            pressure = np.einsum("ra,rai,raj->ij", weight / E, p, p)
        pbar = float(np.trace(pressure) / 3.0)
        pi = pressure - np.eye(3) * pbar
        with np.errstate(over="ignore", invalid="ignore"):
            diag = np.einsum("ra,rai->i", 2.0 * weight / E, w)
            cross = np.einsum("ra,rai,raj->ij", weight / E**3, w, w)
            h3 = np.diag(diag) - cross
            h2 = B.T @ h3 @ B
        if not (np.isfinite(rho) and rho > 0.0 and
                np.all(np.isfinite(pressure)) and np.all(np.isfinite(h3)) and
                np.all(np.isfinite(h2))):
            raise ValueError("FD96_NONFINITE_TENSOR_RESULT")
        offdiag = float(np.max(np.abs(pressure - np.diag(np.diag(pressure)))))
        if diagonal_only and offdiag > 2e-12 * rho:
            raise ValueError("FD96_OFFDIAGONAL_STRESS")
        return TensorMoments(rho, pressure, pi, h3, h2,
                             -B.T @ np.diag(pressure), parity, offdiag,
                             float(np.min(weight)))

    def neutral_root(self, x: float, start: tuple[float, float] = (0.0, 0.0)):
        def gradient(u):
            return self.moments(x, u).energy_gradient2
        sol = root(gradient, np.asarray(start, dtype=float), jac=lambda u: self.moments(x, u).hessian2,
                   method="hybr", tol=1e-11)
        if not sol.success and np.linalg.norm(sol.fun, ord=np.inf) > 5e-13:
            raise ArithmeticError("FD96_NEUTRAL_ROOT_NOT_CONVERGED")
        m = self.moments(x, sol.x)
        residual = float(np.linalg.norm(m.energy_gradient2, ord=np.inf))
        if residual > 5e-13 * m.rho or np.linalg.eigvalsh(m.hessian2)[0] <= 0:
            raise ArithmeticError("FD96_NEUTRAL_ROOT_INVALID")
        return np.asarray(sol.x), m, residual


def source_einstein_residual(source: FD96Diagonal, x: float, u: np.ndarray,
                             beta_prime2: np.ndarray, h: float = 2e-5):
    """Pointwise finite-difference work and Raychaudhuri identity, 8piG=1.

    beta_prime is signed sigma_i/H.  H is supplied by the Hamiltonian
    constraint; the local Raychaudhuri expression is returned, not a claim
    about a separately solved cosmological history.
    """
    beta_prime = B @ np.asarray(beta_prime2, dtype=float)
    m = source.moments(x, u)
    d = (source.moments(x+h, u+h*beta_prime2).rho -
         source.moments(x-h, u-h*beta_prime2).rho) / (2*h)
    rhs = -3.0 * (m.rho + m.pbar) - float(beta_prime @ np.diag(m.pi))
    shear_fraction = float(beta_prime @ beta_prime / 2.0)
    H = math.sqrt(m.rho / (3.0 - shear_fraction))
    sigma2 = H * H * shear_fraction
    hamiltonian = 3.0*H*H - m.rho - sigma2
    ray_hx = (-.5*(m.rho + m.pbar) - sigma2) / H
    return dict(energy_work_raw=d-rhs, energy_work_denominator=abs(rhs),
                hamiltonian_raw=hamiltonian,
                hamiltonian_denominator=3.0*H*H,
                raychaudhuri_hx=ray_hx, H=H,
                signed_shear_over_H=beta_prime.tolist(),
                Sigma=math.sqrt(shear_fraction))
