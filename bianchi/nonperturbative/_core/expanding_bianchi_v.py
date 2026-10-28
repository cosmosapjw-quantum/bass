"""DV2-F: coframe-compatible expanding Bianchi-V polarized transport.

Signature (-,+,+,+), u=t/T_star, coordinates in c*T_star. Metric/(cT*)^2:
-du^2+ax^2 exp(-2*a0*z)dx^2+ay^2 exp(-2*a0*z)dy^2+az^2 dz^2.
A=c*a_structure*T_star=(0,0,a0/az), NOT acceleration or A/H.
Positive diagonal scale factors are prescribed, not solved from Einstein eqs.
Class-B raw angular measure is independent of redshift; no normalization,
positivity projection, small-amplitude expansion, or production Rust path.
The parent source-memory/Volterra files are reused unchanged.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from scipy.integrate import solve_ivp
from bianchi.q import polarization as P8
from .harmonic_history import HarmonicHistory
from .classb_streaming import classb_matrix
from .frozen_bianchi_v import Geometry as FrozenGeometry, FrozenV, free_dipole_moments
ALPHA = 3 / (8 * np.pi)

@dataclass(frozen=True)
class CoframeProfile:
    h: tuple = (0.12, 0.45, 0.28)
    d: tuple = (0.16, -0.12, 0.08)
    a0: float = 0.7
    nu0: float = 1.1
    nuamp: float = 0.2

    def __post_init__(self):
        for name in ('h', 'd'):
            a = np.asarray(getattr(self, name), float)
            if a.shape != (3,) or not np.isfinite(a).all():
                raise ValueError('finite scale-rate triples required')
            object.__setattr__(self, name, tuple((float(x) for x in a)))
        if not np.isfinite([self.a0, self.nu0, self.nuamp]).all() or self.nu0 < abs(self.nuamp):
            raise ValueError('finite structure and nonnegative prescribed opacity required')

    def logs(self, u):
        return np.asarray(self.h) * u + 0.5 * np.asarray(self.d) * u * u

    def scales(self, u):
        return np.exp(self.logs(u))

    def rates(self, u):
        return np.asarray(self.h) + np.asarray(self.d) * u

    def fields(self, u):
        r = self.rates(u)
        H = float(np.mean(r))
        return (H, np.diag(r - H))

    def structure(self, u):
        return np.array([0.0, 0.0, self.a0 * np.exp(-self.logs(u)[2])])

    def structure_rate(self, u):
        return -self.rates(u)[2] * self.structure(u)

    def rate(self, u):
        return float(self.nu0 + self.nuamp * np.cos(2 * u))

    def kappa(self, u):
        """Parent compatibility name: integrated optical depth, NOT curvature."""
        return float(self.nu0 * u + 0.5 * self.nuamp * np.sin(2 * u))

def analytic_rates(n, E, H, S, A):
    """Direction, log photon energy, screen, log angular area on unit sphere."""
    sn = n @ S.T
    s = np.einsum('ni,ni->n', n, sn)
    alpha = n @ A
    v = -sn + (s + alpha)[:, None] * n - A
    B = np.einsum('ni,nj->nij', v, n) - np.einsum('ni,nj->nij', n, v)
    return (v, -H - s, B @ E, 3 * s + 2 * alpha)

def _solve(rhs, y0, end, rtol, atol):
    if not np.isfinite(end) or not 0 < end <= 0.6:
        raise ValueError('support 0<end<=.6 required')
    if not np.isfinite([rtol, atol]).all() or min(rtol, atol) <= 0:
        raise ValueError('positive finite tolerances required')
    sol = solve_ivp(rhs, (0.0, float(end)), np.asarray(y0, float).ravel(), method='DOP853', rtol=rtol, atol=atol, dense_output=True)
    if not sol.success:
        raise RuntimeError(sol.message)
    return sol

class ExpandingGeometry:
    """Direction/screen/redshift/area supplier independent of P8 and radiation.

    Jac and r are separate ODE variables. z_ray records coordinate displacement
    only for diagnostic identities, not a metric feedback. No reprojection of
    dense-output n, screen or quadrature weights is made.
    """

    def __init__(self, grid, profile, end, rtol=2e-12, atol=2e-14):
        self.grid, self.profile, self.end = (grid, profile, float(end))
        self.n = len(grid.w)
        if not np.isfinite(end) or not 0 < end <= 0.6:
            raise ValueError('bounded provider support required')
        if np.max(abs(profile.logs(end))) > 5:
            raise ValueError('bounded validation requires |log ai|<=5')
        self.screen0 = np.stack([grid.bt, grid.bp], axis=2)
        self._cache = {}
        y = np.zeros((self.n, 12))
        y[:, :3] = grid.n
        y[:, 4:10] = self.screen0.reshape(self.n, 6)

        def rhs(u, yy):
            z = yy.reshape(self.n, 12)
            H, S = profile.fields(u)
            A = profile.structure(u)
            v, lr, dE, lj = analytic_rates(z[:, :3], z[:, 4:10].reshape(self.n, 3, 2), H, S, A)
            return np.column_stack([v, lr, dE.reshape(self.n, 6), lj, z[:, 2] / profile.scales(u)[2]]).ravel()
        self.solution = _solve(rhs, y, end, rtol, atol)

    def _time(self, u):
        u = float(u)
        if not np.isfinite(u) or u < 0 or u > self.end + 1e-14:
            raise ValueError('time outside provider support')
        return min(u, self.end)

    def at(self, u):
        u = self._time(u)
        if u not in self._cache:
            z = self.solution.sol(u).reshape(self.n, 12)
            r = np.exp(z[:, 3])
            jac = np.exp(z[:, 10])
            w = self.grid.w * jac
            self._cache[u] = {'e': z[:, :3], 'screen': z[:, 4:10].reshape(self.n, 3, 2), 'mu': r, 'jac': jac, 'w': w, 'v': w * r ** 4, 'z_ray': z[:, 11]}
        return self._cache[u]

    def moment(self, u, J):
        return np.einsum('n,nij->ij', self.at(u)['w'], J)

    def free_state(self, u, J0):
        X = np.einsum('nia,nij,njb->nab', self.screen0, J0, self.screen0)
        z = self.at(u)
        return z['mu'][:, None, None] ** 4 * np.einsum('nia,nab,njb->nij', z['screen'], X, z['screen'])

class CoordinateRays:
    """Independent Hamiltonian rays for the explicit coordinate metric.

    E=sqrt(exp(2a0*z)[Px^2/ax^2+Py^2/ay^2]+Pz^2/az^2).
    Px,Py are Killing constants. Initial z0=.13 avoids conflating coordinate
    and tetrad momenta. No tetrad RHS, screen formula or P8 calls.
    """

    def __init__(self, n0, profile, end, rtol=2e-12, atol=2e-14):
        n0 = np.asarray(n0, float)
        if n0.ndim != 2 or n0.shape[1] != 3 or (not np.isfinite(n0).all()) or (np.max(abs(np.linalg.norm(n0, axis=1) - 1)) > 1e-10):
            raise ValueError('finite unit initial directions required')
        self.profile, self.end, self.n = (profile, float(end), len(n0))
        self.z0 = 0.13
        self.Px = n0[:, 0] * np.exp(-profile.a0 * self.z0)
        self.Py = n0[:, 1] * np.exp(-profile.a0 * self.z0)
        y = np.column_stack([np.full(self.n, self.z0), n0[:, 2]])

        def rhs(u, yy):
            zz, pz = yy.reshape(self.n, 2).T
            a = profile.scales(u)
            transverse = np.exp(2 * profile.a0 * zz) * (self.Px ** 2 / a[0] ** 2 + self.Py ** 2 / a[1] ** 2)
            energy = np.sqrt(transverse + pz * pz / a[2] ** 2)
            return np.column_stack([pz / (a[2] ** 2 * energy), -profile.a0 * transverse / energy]).ravel()
        self.solution = _solve(rhs, y, end, rtol, atol)

    def at(self, u):
        if not np.isfinite(u) or not 0 <= u <= self.end:
            raise ValueError('coordinate time outside support')
        zz, pz = self.solution.sol(u).reshape(self.n, 2).T
        a = self.profile.scales(u)
        p = np.column_stack([np.exp(self.profile.a0 * zz) * self.Px / a[0], np.exp(self.profile.a0 * zz) * self.Py / a[1], pz / a[2]])
        r = np.linalg.norm(p, axis=1)
        return (p / r[:, None], r, zz)

class TangentGeometry:
    """Differentiate the sphere flow, rather than integrating log Jac."""

    def __init__(self, grid, profile, end, rtol=2e-12, atol=2e-14):
        self.n, self.end = (len(grid.w), float(end))
        Q0 = np.stack([grid.bt, grid.bp], axis=2)
        y = np.column_stack([grid.n, Q0.reshape(self.n, 6)])

        def rhs(u, yy):
            z = yy.reshape(self.n, 9)
            n = z[:, :3]
            Q = z[:, 3:].reshape(self.n, 3, 2)
            _, S = profile.fields(u)
            A = profile.structure(u)
            sn = n @ S.T
            s = np.einsum('ni,ni->n', n, sn)
            alpha = n @ A
            v = -sn + (s + alpha)[:, None] * n - A
            D = -S[None] + (s + alpha)[:, None, None] * np.eye(3) + 2 * np.einsum('ni,nj->nij', n, sn) + np.einsum('ni,j->nij', n, A)
            return np.column_stack([v, (D @ Q).reshape(self.n, 6)]).ravel()
        self.solution = _solve(rhs, y, end, rtol, atol)

    def area(self, u):
        if not np.isfinite(u) or not 0 <= u <= self.end:
            raise ValueError('tangent time outside support')
        z = self.solution.sol(u).reshape(self.n, 9)
        Q = z[:, 3:].reshape(self.n, 3, 2)
        return np.einsum('ni,ni->n', z[:, :3], np.cross(Q[:, :, 0], Q[:, :, 1]))

class ExpandingDirect:
    """Physical Cartesian P8 ODE; shares geometry, not source/pullback history."""

    def __init__(self, geo, J0, rtol=2e-12, atol=2e-14):
        self.geo = geo
        J0 = np.asarray(J0, float)
        if J0.shape != (geo.n, 3, 3) or not np.isfinite(J0).all():
            raise ValueError('finite carrier with matching grid required')

        def rhs(u, y):
            z = geo.at(u)
            e = z['e']
            J = y.reshape(geo.n, 3, 3)
            H, S = geo.profile.fields(u)
            A = geo.profile.structure(u)
            sn = np.einsum('ni,ij,nj->n', e, S, e)
            P = np.eye(3) - np.einsum('ni,nj->nij', e, e)
            M = geo.moment(u, J)
            gain = ALPHA * np.einsum('nia,ab,nbj->nij', P, M, P, optimize=True)
            return (-4 * (H + sn)[:, None, None] * J + P8.tensor_rate(J, e, H, S, np.zeros(3), np.zeros((3, 3)), A) + geo.profile.rate(u) * (gain - J)).ravel()
        self.rhs = rhs
        self.solution = _solve(rhs, J0, geo.end, rtol, atol)

    def state(self, u):
        return self.solution.sol(self.geo._time(u)).reshape(self.geo.n, 3, 3)

    def moment(self, u):
        return self.geo.moment(u, self.state(u))

class ExpandingHarmonic(HarmonicHistory):
    """Pinned analytic shear plus class-B dipole matrix, finite-L Galerkin.

    Geometry and collision coefficients depend only on the prescribed coframe.
    No angular fitting, direct reference or Volterra callback.
    """

    def __init__(self, profile, initial, L, end, rtol=2e-12, atol=2e-14):
        self.G0 = classb_matrix(0, L, L, np.array([0.0, 0.0, 1.0])).real
        self.G2 = classb_matrix(2, L, L, np.array([0.0, 0.0, 1.0]))
        super().__init__(profile, initial, L, end, rtol, atol)

    def rhs(self, u, y):
        out = super().rhs(u, y)
        n0, n2 = (self.n0, self.n2)
        a = self.profile.structure(u)[2]
        dp = self.G2 @ (y[2 * n0:2 * n0 + n2] + 1j * y[2 * n0 + n2:])
        return out + a * np.r_[self.G0 @ y[:n0], self.G0 @ y[n0:2 * n0], dp.real, dp.imag]

def _conformal(profile, u):
    if not np.isfinite(u) or u < 0 or np.ptp(profile.h) > 1e-15 or np.any(np.asarray(profile.d) != 0):
        raise ValueError('constant isotropic scale rate required for this exact oracle')
    h = profile.h[0]
    eta = float(u if h == 0 else -np.expm1(-h * u) / h)
    a = float(np.exp(h * u))
    return (a, eta)

def conformal_exact_geometry(grid, profile, u):
    """Conformal-ultrastatic geometry oracle, NOT spatially-flat FLRW."""
    a, eta = _conformal(profile, u)
    f = FrozenGeometry(grid, FrozenV(A=(0.0, 0.0, profile.a0)), max(eta, 1e-12))
    z = f.at(eta)
    return {'e': z['e'], 'screen': z['screen'], 'jac': z['jac'], 'mu': np.full(len(grid.w), 1 / a)}

def conformal_dipole(profile, u, base=2.0, eps=0.3):
    """Exact collisionless rho,qz for isotropic exponential expansion.

    a^4*rho and a^4*qz equal frozen dipole moments at conformal eta.
    Thus rho_dot+4H*rho=2 A_z qz, no local-density renormalization.
    """
    if profile.nu0 != 0 or profile.nuamp != 0:
        raise ValueError('collisionless oracle requires zero opacity')
    a, eta = _conformal(profile, u)
    rho, qz = free_dipole_moments(profile.a0, eta, base, eps)
    return (rho / a ** 4, qz / a ** 4)
