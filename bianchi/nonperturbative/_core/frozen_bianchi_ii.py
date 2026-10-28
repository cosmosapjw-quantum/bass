"""Frozen Bianchi-II characteristic provider and independent finite-time paths.

Normal time u=t/T_star. curvature=c*n_structure*T_star is NOT opacity.
H=sigma=0, A_struct=0, N=curvature*axis*axis.T constant; prescribed ultrastatic
geometry, not a solution of Einstein equations for the evolved radiation.
No Bianchi-I momentum matrix is used. Geometry has mu=1 and exact area Jacobian1.
P8 carrier is S+A, physical coherency S+iA; propagation-direction spin convention
is inherited unchanged. Native production/Rust/Strang paths are not invoked.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from scipy.integrate import solve_ivp
from scipy.linalg import expm
from bianchi.q import polarization as P8
from .polarized_dictionary import synthesize, stokes, source_matrix
from .harmonic_history import direction_view
from .harmonic_streaming import labels
from .curvature_streaming import curvature_matrix, rank_one
ALPHA = 3 / (8 * np.pi)

@dataclass(frozen=True)
class FrozenProfile:
    curvature: float = 0.9
    nu: float = 1.4
    axis: tuple = (0.0, 0.0, 1.0)
    variable: bool = False

    def __post_init__(self):
        a = np.asarray(self.axis, float)
        if a.shape != (3,) or not np.isfinite(a).all() or np.linalg.norm(a) == 0:
            raise ValueError('finite nonzero axis required')
        if not np.isfinite(self.curvature) or not np.isfinite(self.nu) or self.nu < 0:
            raise ValueError('finite curvature and nonnegative opacity required')
        if self.variable and self.nu < 0.3:
            raise ValueError('variable opacity must stay nonnegative')

    @property
    def a(self):
        a = np.asarray(self.axis, float)
        return a / np.linalg.norm(a)

    @property
    def N(self):
        return rank_one(self.curvature, self.a)

    def rate(self, t):
        return self.nu + (0.3 * np.cos(2 * t) if self.variable else 0.0)

    def optical_depth(self, t):
        return self.nu * t + (0.15 * np.sin(2 * t) if self.variable else 0.0)

    def kappa(self, t):
        """Compatibility name required by KM3: integrated OPACITY, not curvature."""
        return self.optical_depth(t)

def rotations(axis, angle):
    """Right-handed Rodrigues matrices, broadcast over axes/angles."""
    a = np.asarray(axis, float)
    a = np.broadcast_to(a, (np.size(angle), 3))
    q = np.asarray(angle, float).reshape(-1)
    K = np.zeros((len(q), 3, 3))
    K[:, 0, 1] = -a[:, 2]
    K[:, 0, 2] = a[:, 1]
    K[:, 1, 0] = a[:, 2]
    K[:, 1, 2] = -a[:, 0]
    K[:, 2, 0] = -a[:, 1]
    K[:, 2, 1] = a[:, 0]
    return np.cos(q)[:, None, None] * np.eye(3) + np.sin(q)[:, None, None] * K + (1 - np.cos(q))[:, None, None] * np.einsum('ni,nj->nij', a, a)

class FrozenGeometry:
    """Exact curved characteristic/screen/measure supplier, no geometry ODE.

    n(t)=R_axis(k mu0 t)n0;
    E(t)=R_axis(k mu0 t) R_n0(-k t/2) E0.
    The latter retains intrinsic screen rotation. mu0=axis dot n0 is not
    the radial-redshift mu field of KM1: that compatibility field is exactly1.
    """

    def __init__(self, grid, profile: FrozenProfile, end: float):
        if not np.isfinite(end) or not 0 < end <= 2.0:
            raise ValueError('require 0<end<=2')
        self.grid, self.profile, self.end = (grid, profile, float(end))
        self.n = len(grid.w)
        self.screen0 = np.stack([grid.bt, grid.bp], axis=2)
        self._cache = {}

    def _time(self, t):
        t = float(t)
        if not np.isfinite(t) or t < 0 or t > self.end + 1e-14:
            raise ValueError('time outside geometry support')
        return min(t, self.end)

    def at(self, t):
        t = self._time(t)
        if t not in self._cache:
            k = self.profile.curvature
            a = self.profile.a
            n0 = self.grid.n
            Ra = rotations(a, k * (n0 @ a) * t)
            Rn = rotations(n0, np.full(self.n, -k * t / 2))
            e = np.einsum('nij,nj->ni', Ra, n0)
            E = Ra @ Rn @ self.screen0
            self._cache[t] = {'e': e, 'screen': E, 'mu': np.ones(self.n), 'w': self.grid.w, 'v': self.grid.w, 'jacobian': np.ones(self.n)}
        return self._cache[t]

    def moment(self, t, J):
        return np.einsum('n,nij->ij', self.at(t)['w'], J)

    def free_state(self, t, J0):
        X = np.einsum('nia,nij,njb->nab', self.screen0, J0, self.screen0)
        E = self.at(t)['screen']
        return np.einsum('nia,nab,njb->nij', E, X, E)

class FrozenDirect:
    """Physical Cartesian carrier ODE, independently using pinned P8 connection."""

    def __init__(self, geo: FrozenGeometry, J0, rtol=2e-12, atol=2e-14):
        self.geo = geo
        J0 = np.asarray(J0, float)
        if J0.shape != (geo.n, 3, 3) or not np.isfinite(J0).all():
            raise ValueError('finite J0/grid required')
        Z = np.zeros((3, 3))
        zero = np.zeros(3)
        N = geo.profile.N

        def rhs(t, y):
            z = geo.at(t)
            e = z['e']
            J = y.reshape(geo.n, 3, 3)
            P = np.eye(3) - np.einsum('ni,nj->nij', e, e)
            M = np.einsum('n,nij->ij', z['w'], J)
            gain = ALPHA * np.einsum('nia,ab,nbj->nij', P, M, P, optimize=True)
            return (P8.tensor_rate(J, e, 0.0, Z, zero, N, zero) + geo.profile.rate(t) * (gain - J)).ravel()
        self.solution = solve_ivp(rhs, (0, geo.end), J0.ravel(), method='DOP853', rtol=rtol, atol=atol, dense_output=True)
        if not self.solution.success:
            raise RuntimeError(self.solution.message)

    def state(self, t):
        return self.solution.sol(self.geo._time(t)).reshape(self.geo.n, 3, 3)

    def moment(self, t):
        return self.geo.moment(t, self.state(t))

class FrozenHarmonic:
    """Independent analytic-curvature Galerkin IVP; explicit zero tail above L."""

    def __init__(self, profile: FrozenProfile, initial: dict, L: int, end: float, rtol=2e-12, atol=2e-14):
        if isinstance(L, bool) or int(L) != L or (not 2 <= L <= 8):
            raise ValueError('integer 2<=L<=8')
        if not np.isfinite(end) or not 0 < end <= 2:
            raise ValueError('0<end<=2')
        self.profile, self.L, self.end = (profile, int(L), float(end))
        self.l0, self.l2 = (labels(0, L), labels(2, L))
        self.n0, self.n2 = (len(self.l0), len(self.l2))
        self.keys = [(f, l, m) for f in ('I', 'V') for l, m in self.l0] + [(f, l, m) for f in ('E', 'B') for l, m in self.l2]
        self.index = {key: i for i, key in enumerate(self.keys)}
        if any((k not in self.index or not np.isfinite(v) for k, v in initial.items())):
            raise ValueError('invalid or excluded initial harmonic')
        self.A0 = curvature_matrix(0, L, L, profile.N).real
        self.A2 = curvature_matrix(2, L, L, profile.N)
        self.idx0 = {lm: i for i, lm in enumerate(self.l0)}
        self.idx2 = {lm: i for i, lm in enumerate(self.l2)}
        self.initial = np.array([initial.get(k, 0.0) for k in self.keys])
        self.solution = solve_ivp(self.rhs, (0, end), self.initial, method='DOP853', rtol=rtol, atol=atol, dense_output=True)
        if not self.solution.success:
            raise RuntimeError(self.solution.message)

    def rhs(self, t, y):
        nu = self.profile.rate(t)
        n0, n2 = (self.n0, self.n2)
        I = y[:n0]
        V = y[n0:2 * n0]
        p = y[2 * n0:2 * n0 + n2] + 1j * y[2 * n0 + n2:]
        dI = self.A0 @ I - nu * I
        dV = self.A0 @ V - nu * V
        dp = self.A2 @ p - nu * p
        dI[self.idx0[0, 0]] += nu * I[self.idx0[0, 0]]
        for m in range(-2, 3):
            i, j = (self.idx0[2, m], self.idx2[2, m])
            dI[i] += nu * (0.1 * I[i] - np.sqrt(6) / 10 * p[j].real)
            dp[j] += nu * (-np.sqrt(6) / 10 * I[i] + 0.6 * p[j].real)
        for m in range(-1, 2):
            dV[self.idx0[1, m]] += 0.5 * nu * V[self.idx0[1, m]]
        return np.r_[dI, dV, dp.real, dp.imag]

    def coefficients(self, t):
        t = float(t)
        if not np.isfinite(t) or t < 0 or t > self.end:
            raise ValueError('outside harmonic support')
        return {k: float(v) for k, v in zip(self.keys, self.solution.sol(t))}

    def moment(self, t):
        return source_matrix(self.coefficients(t))

    def state(self, t, view):
        return synthesize(view, self.coefficients(t))

def carrier_from_stokes(view, I, Q, U, V):
    a, b = (view.bt, view.bp)
    ab = np.einsum('ni,nj->nij', a, b)
    return 0.5 * (I[:, None, None] * view.P + Q[:, None, None] * (np.einsum('ni,nj->nij', a, a) - np.einsum('ni,nj->nij', b, b)) + U[:, None, None] * (ab + ab.transpose(0, 2, 1)) + V[:, None, None] * (ab.transpose(0, 2, 1) - ab))

def free_eulerian(directions, weights, initial, curvature, t):
    """Independent closed Eulerian formula for canonical z axis only.

    f_s(t,theta,phi)=exp(-is*k*t/2) f_si(theta,phi-k*cos(theta)*t).
    """
    now = direction_view(directions, weights)
    back = rotations([0, 0, 1], -curvature * now.n[:, 2] * t) @ now.n[:, :, None]
    old = direction_view(back[:, :, 0], weights)
    I, Q, U, V = stokes(old, synthesize(old, initial))
    p = (Q + 1j * U) * np.exp(-1j * curvature * t)
    return carrier_from_stokes(now, I, p.real, p.imag, V)

def m0_exact(y0, curvature, nu, t):
    """Exact all-time closed I20/E20/B20 block, constant rest opacity.

    This closure is exact for m=0,l=2 (plus unchanged I00), NOT general angular
    closure. Full source-null B20 is retained.
    """
    a = np.sqrt(6) * nu / 10
    B = np.array([[-0.9 * nu, -a, 0.0], [-a, -0.4 * nu, curvature], [0.0, -curvature, -nu]])
    return expm(t * B) @ np.asarray(y0, float)
