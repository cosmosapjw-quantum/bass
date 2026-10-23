"""Positive antipodal collisionless streams for an independent Bianchi-I test.

Each axis denotes a pair of opposite conserved covariant momenta, so flux=0.
The exact discrete-stream model has two massive/massless sectors. Its radial and
angular measure is intentionally distinct from the retained FD96 owner.

For a fixed physical momentum P_*, `mass` means m_phys*c/P_*, `momentum`
means conserved physical covariant momentum / P_*, and `number` means
kappa*L_*^2*c*P_* times the reference-volume number density of each pair.
Thus sqrt(mass^2+k^2) is E_phys/(c*P_*). The returned density and pressure
use exactly the fixed gravitational scaling in CONTRACT.md; c is not set to 1.
"""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np
from core import State, Source, rhs


@dataclass(frozen=True)
class AxisStreams:
    mass: float
    number: np.ndarray
    momentum: np.ndarray

    def __post_init__(self):
        if not np.isfinite(self.mass) or self.mass < 0:
            raise ValueError("mass must be finite and nonnegative")
        if np.shape(self.number) != (3,) or np.shape(self.momentum) != (3,):
            raise ValueError("three positive antipodal-axis pair weights required")
        if not np.all(np.isfinite(self.number)) or not np.all(np.asarray(self.number) >= 0):
            raise ValueError("nonnegative finite stream weights required")
        if not np.all(np.isfinite(self.momentum)) or not np.all(np.asarray(self.momentum) > 0):
            raise ValueError("positive finite canonical momentum required")

    def moments(self, alpha, beta):
        momentum = self.momentum * np.exp(-alpha-np.asarray(beta))
        energy = np.sqrt(self.mass*self.mass + momentum*momentum)
        volume_factor = np.exp(-3*alpha)
        density = volume_factor * np.sum(self.number*energy)
        diagonal_pressure = volume_factor * self.number*momentum*momentum/energy
        pressure = np.sum(diagonal_pressure)/3
        # Use the same independent STF coordinates as the Einstein operator.
        # Subtracting pressure three times loses relative trace accuracy near
        # isotropy, even though the underlying analytic tensor is trace-free.
        p1, p2 = diagonal_pressure[:2]-pressure
        pi = np.diag(np.array([p1, p2, -p1-p2]))
        return density, pressure, pi


def cancellation_model(sign=1.0, *, seed=0.3):
    if sign not in (-1.0, 0.0, 1.0):
        raise ValueError("sign must be -1, 0 or +1")
    mass = 3.0
    rho_m, rho_r, lam = 1.8, 0.9, 0.3
    k = np.ones(3)
    energy_m = np.sqrt(mass*mass+1)
    v2 = 1/(mass*mass+1)
    shape = sign*seed*np.array([1., -2/3, -1/3])
    massive_axis_density = rho_m*(1+shape)/3
    pi_massive = v2*(massive_axis_density-rho_m/3)
    radiation_axis_density = rho_r/3-pi_massive
    models = (AxisStreams(mass, massive_axis_density/energy_m, k),
              AxisStreams(0., radiation_axis_density, k))
    initial = State(1., np.zeros((3, 3)), np.zeros((3, 3)), np.zeros(3),
                    0., np.array([rho_m, rho_r]), np.zeros((2, 3))).pack()
    return models, np.r_[initial, 0., 0.], lam


def evaluate(models, alpha, beta):
    values = [s.moments(alpha, beta) for s in models]
    return (np.array([v[0] for v in values]),
            Source(np.array([v[1] for v in values]), np.array([v[2] for v in values])))


def extended_rhs(tau, extended, models, lam):
    packed = extended[:-2]
    y = State.unpack(packed)
    beta = np.r_[extended[-2:], -np.sum(extended[-2:])]
    _, source = evaluate(models, y.alpha, beta)
    dy = rhs(tau, packed, source, cosmological_constant=lam)
    return np.r_[dy, y.sigma[0, 0], y.sigma[1, 1]]


def eliminated_rhs(tau, z, models, lam):
    """Five-variable reference: densities from streams, H from constraint.

    This separate path is used only while expanding, h>0. The main free-evolution
    operator evolves h and both densities and also covers recollapse.
    """
    alpha, b1, b2, s1, s2 = z
    beta = np.array([b1, b2, -b1-b2])
    sigma = np.array([s1, s2, -s1-s2])
    rho, source = evaluate(models, alpha, beta)
    h = np.sqrt((np.sum(sigma*sigma)/2 + np.sum(rho)+lam)/3)
    ds = -3*h*sigma + np.diag(np.sum(source.pi, axis=0))
    return np.array([h, s1, s2, ds[0], ds[1]])
