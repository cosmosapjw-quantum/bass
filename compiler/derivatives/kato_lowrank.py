from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class ScalarBoostedProjector:
    """
    Low-rank lowering of the continuum scalar bolometric finite-tilt Thomson
    equilibrium projector for a fixed angular quadrature.

    This is a *discretization-layer operator program*, not Continuum SymIR.
    """
    r: np.ndarray
    a: np.ndarray
    rv: np.ndarray
    av: np.ndarray
    denominator: float
    denominator_v: float

    def P(self, y: np.ndarray) -> np.ndarray:
        return self.r * (self.a @ y) / self.denominator

    def Pv(self, y: np.ndarray) -> np.ndarray:
        d = self.denominator
        dv = self.denominator_v
        ay = self.a @ y
        avy = self.av @ y
        return (
            self.rv * ay / d
            + self.r * avy / d
            - self.r * ay * dv / (d * d)
        )

    def Pdot(self, y: np.ndarray, vdot: float) -> np.ndarray:
        return vdot * self.Pv(y)

    def K(self, y: np.ndarray, vdot: float) -> np.ndarray:
        # [Pdot, P] y, evaluated matrix-free.
        Py = self.P(y)
        return self.Pdot(Py, vdot) - self.P(self.Pdot(y, vdot))


def scalar_boosted_projector(
    directions: np.ndarray,
    weights: np.ndarray,
    v: float,
    axis: int = 1,
) -> ScalarBoostedProjector:
    e = np.asarray(directions, dtype=float)
    w = np.asarray(weights, dtype=float)
    mu = e[:, axis]
    gamma = 1.0 / np.sqrt(1.0 - v * v)
    q = 1.0 - v * mu
    D = gamma * q

    r = D ** -4
    a = w * q / (4.0 * np.pi)
    rv = 4.0 * r * (mu / q - gamma * gamma * v)
    av = -w * mu / (4.0 * np.pi)
    den = float(a @ r)
    denv = float(av @ r + a @ rv)

    return ScalarBoostedProjector(r, a, rv, av, den, denv)


def directional_parameter_jvp(
    op: ScalarBoostedProjector,
    y: np.ndarray,
    y_direction: np.ndarray,
    v_direction: float,
) -> np.ndarray:
    """
    JVP of P(v)y in direction (delta y, delta v):
        P(v) delta y + delta v * dP/dv y.
    """
    return op.P(y_direction) + v_direction * op.Pv(y)
