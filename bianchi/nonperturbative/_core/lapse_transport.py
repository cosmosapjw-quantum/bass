"""Collisionless photons in a prescribed positive periodic static lapse.

Metric (-+++): ds^2=-N(x)^2 c^2 dt^2+L_star^2 d{x}^2.
Coordinates are dimensionless; u=t/T_star, cbar=c*T_star/L_star.
The static normal observer is accelerated. No Einstein solution is assumed.
State coordinates are lifted, not wrapped; metric coefficients are periodic.
No screen/state/measure renormalization or clipping is performed.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from scipy.integrate import solve_ivp, quad
from scipy.optimize import brentq

@dataclass(frozen=True)
class PeriodicLapse:
    epsilon: float
    cbar: float = 1.0
    offset: float = 0.0

    def __post_init__(self):
        if not np.isfinite([self.epsilon, self.cbar, self.offset]).all() or self.cbar <= 0:
            raise ValueError('Require finite epsilon,offset and cbar>0')
        if abs(self.epsilon) + abs(self.offset) > 300:
            raise ValueError('Lapse exponent outside bounded float64 implementation domain')

    def N(self, x):
        return np.exp(self.offset + self.epsilon * np.cos(x))

    def dN(self, x):
        return -self.epsilon * np.sin(x) * self.N(x)

    def ddN(self, x):
        return self.N(x) * (self.epsilon ** 2 * np.sin(x) ** 2 - self.epsilon * np.cos(x))

def screen_basis(n: np.ndarray) -> np.ndarray:
    n = np.atleast_2d(np.asarray(n, float))
    if n.shape[1] != 3 or not np.isfinite(n).all() or np.max(abs(np.sum(n * n, axis=1) - 1)) > 2e-10:
        raise ValueError('Require unit finite directions')
    axis = np.eye(3)[np.argmin(abs(n), axis=1)]
    e1 = np.cross(n, axis)
    e1 /= np.linalg.norm(e1, axis=1)[:, None]
    return np.stack((e1, np.cross(n, e1)), axis=2)

def checked_ray_data(x, n, screen0=None):
    x = np.atleast_2d(np.asarray(x, float))
    n = np.atleast_2d(np.asarray(n, float))
    if x.shape != n.shape or x.shape[1] != 3 or (not np.isfinite(x).all()):
        raise ValueError('x,n must have matching (ray,3) shape and be finite')
    if not np.isfinite(n).all() or np.max(abs(np.sum(n * n, axis=1) - 1)) > 2e-10:
        raise ValueError('n must be unit and finite; no normalization performed')
    E = screen_basis(n) if screen0 is None else np.asarray(screen0, float).copy()
    if E.shape != (len(n), 3, 2) or not np.isfinite(E).all():
        raise ValueError('screen must have shape (ray,3,2)')
    if np.max(abs(E.swapaxes(1, 2) @ E - np.eye(2))) > 2e-10 or np.max(abs(np.einsum('ni,nij->nj', n, E))) > 2e-10:
        raise ValueError('Initial screen must be orthonormal and transverse')
    return (x.copy(), n.copy(), E)

class DenseHistory:

    def _solve(self, y0, fun, t_end, rtol, atol):
        self.t_end = float(t_end)
        if not np.isfinite(self.t_end) or self.t_end == 0:
            raise ValueError('Nonzero finite time interval required')
        self.shape = y0.shape
        self.sol = solve_ivp(lambda t, y: fun(t, y.reshape(self.shape)).ravel(), (0.0, self.t_end), y0.ravel(), method='DOP853', dense_output=True, rtol=rtol, atol=atol)
        if not self.sol.success:
            raise RuntimeError(self.sol.message)
        self.nfev = self.sol.nfev

    def _raw(self, t):
        t = float(t)
        if not np.isfinite(t) or t < min(0.0, self.t_end) or t > max(0.0, self.t_end):
            raise ValueError('No extrapolation outside the solved interval')
        return self.sol.sol(t).reshape(self.shape)

class TetradHistory(DenseHistory):
    """Normal-frame direction, log-energy ratio and physical screen flow.

    Uses observer-acceleration equations, not canonical momenta/Christoffels.
    """

    def __init__(self, model, x0, n0, t_end, screen0=None, rtol=2e-12, atol=2e-14):
        self.model = model
        self.x0, self.n0, self.screen0 = checked_ray_data(x0, n0, screen0)
        m = len(self.n0)
        y0 = np.concatenate((self.x0, self.n0, np.zeros((m, 1)), self.screen0.reshape(m, 6)), axis=1)

        def fun(t, y):
            x = y[:, :3]
            n = y[:, 3:6]
            E = y[:, 7:].reshape(m, 3, 2)
            N = model.N(x[:, 0])
            grad = np.zeros_like(n)
            grad[:, 0] = model.dN(x[:, 0])
            gdot = np.sum(grad * n, axis=1)
            dn = model.cbar * (gdot[:, None] * n - grad)
            Omega = np.einsum('ni,nj->nij', dn, n) - np.einsum('ni,nj->nij', n, dn)
            dE = Omega @ E
            return np.concatenate((model.cbar * N[:, None] * n, dn, -model.cbar * gdot[:, None], dE.reshape(m, 6)), axis=1)
        self._solve(y0, fun, t_end, rtol, atol)

    def at(self, t):
        y = self._raw(t)
        return {'x': y[:, :3], 'n': y[:, 3:6], 'r': np.exp(y[:, 6]), 'log_r': y[:, 6], 'screen': y[:, 7:].reshape(-1, 3, 2)}

    def carrier(self, t, screen_carrier):
        """Propagate real P8 S+A encoding, or complex physical screen coherency.

        Carrier is bolometric: r^4, unlike the invariant occupation function.
        Signed inputs are allowed; positivity is checked on physical total states.
        """
        q = self.at(t)
        X = np.asarray(screen_carrier)
        if X.shape not in ((2, 2), (len(self.n0), 2, 2)) or not np.isfinite(X).all():
            raise ValueError('screen carrier must be finite (2,2) or (ray,2,2)')
        return q['r'][:, None, None] ** 4 * (q['screen'] @ X @ q['screen'].swapaxes(1, 2))

def radial_exact(model: PeriodicLapse, x0: float, sign: int, u: float):
    """Independent radial travel-time quadrature, not an ODE integration."""
    if sign not in (-1, 1) or not np.isfinite([x0, u]).all():
        raise ValueError('Require radial sign +/-1 and finite x0,u')
    if u == 0:
        return (float(x0), 1.0)
    span = abs(u) * model.cbar * np.exp(model.offset + abs(model.epsilon)) * 1.01 + 1e-12
    end = x0 + np.sign(sign * u) * span
    lo, hi = sorted((x0, end))

    def residual(x):
        travel = quad(lambda z: 1.0 / model.N(z), x0, x, epsabs=2e-13, epsrel=2e-13)[0]
        return travel - sign * model.cbar * u
    x = brentq(residual, lo, hi, xtol=2e-13, rtol=2e-14)
    return (float(x), float(model.N(x0) / model.N(x)))
