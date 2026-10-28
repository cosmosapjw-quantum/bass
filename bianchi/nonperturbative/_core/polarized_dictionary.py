"""Source-matched P8 to all-m angular dictionary, isolated DL2 research adapter.

Real CS scalar basis Z_lm follows BASS canonical order m=-l,...,l.
Q+iU = sum (E_lm+i B_lm) Z_(+2,lm); this E/B is the negative of
an external convention defined by Q+iU=-sum(E_ext+i B_ext) Z_(+2,lm).
The P8 real matrix is S+A; physical Hermitian coherency is S+i A.
No spatial/metric evolution, moving-electron rates, or spectral closure here.
"""
from __future__ import annotations
from math import factorial, pi, sqrt
import numpy as np
from numpy.polynomial.legendre import leggauss
Coeff = dict[tuple[str, int, int], float]

class Grid:
    """Gauss-Legendre x periodic azimuth, with pole-avoiding theta/phi screen."""

    def __init__(self, nt: int, np_: int):
        if nt < 4 or np_ < 8:
            raise ValueError('Angular grid is too small for this adapter')
        mu, w = leggauss(nt)
        self.theta = np.repeat(np.arccos(mu), np_)
        self.phi = np.tile(2 * pi * np.arange(np_) / np_, nt)
        self.w = np.repeat(w, np_) * (2 * pi / np_)
        st, ct = (np.sin(self.theta), np.cos(self.theta))
        sp, cp = (np.sin(self.phi), np.cos(self.phi))
        self.n = np.stack([st * cp, st * sp, ct], axis=1)
        self.bt = np.stack([ct * cp, ct * sp, -st], axis=1)
        self.bp = np.stack([-sp, cp, np.zeros_like(sp)], axis=1)
        self.P = np.eye(3) - np.einsum('ni,nj->nij', self.n, self.n)
        self._cache = {}

    def y(self, s: int, l: int, m: int) -> np.ndarray:
        """(-1)^s sqrt((2l+1)/4pi) d^l_(m,-s)(theta) exp(i m phi)."""
        if l < abs(s) or abs(m) > l or l > 8:
            raise ValueError('Require |s|<=l<=8 and |m|<=l')
        key = (s, l, m)
        if key not in self._cache:
            q = -s
            ch = np.cos(self.theta / 2)
            sh = np.sin(self.theta / 2)
            pref = sqrt(factorial(l + q) * factorial(l - q) * factorial(l + m) * factorial(l - m))
            d = np.zeros_like(self.theta)
            for k in range(max(0, q - m), min(l + q, l - m) + 1):
                den = factorial(l + q - k) * factorial(k) * factorial(m - q + k) * factorial(l - m - k)
                d += (-1) ** (m - q + k) * pref / den * ch ** (2 * l + q - m - 2 * k) * sh ** (m - q + 2 * k)
            self._cache[key] = (-1) ** s * sqrt((2 * l + 1) / (4 * pi)) * d * np.exp(1j * m * self.phi)
        return self._cache[key]

    def z(self, s: int, l: int, m: int) -> np.ndarray:
        if m == 0:
            return self.y(s, l, 0)
        a = abs(m)
        if m > 0:
            return ((-1) ** a * self.y(s, l, a) + self.y(s, l, -a)) / sqrt(2)
        return ((-1) ** a * self.y(s, l, a) - self.y(s, l, -a)) / (1j * sqrt(2))

def _validate(c: Coeff) -> None:
    for (f, l, m), v in c.items():
        if f not in ('I', 'E', 'B', 'V') or abs(m) > l or l < 0 or (l > 8):
            raise ValueError('Invalid harmonic label')
        if f in ('E', 'B') and l < 2:
            raise ValueError('Spin-2 requires l>=2')
        if not np.isfinite(v):
            raise ValueError('Nonfinite coefficient')

def synthesize(g: Grid, c: Coeff) -> np.ndarray:
    """Synthesize real P8 S+A encoding. Signed operator bases need not be PSD."""
    _validate(c)
    I = np.zeros(len(g.w))
    V = I.copy()
    pol = np.zeros(len(g.w), complex)
    for (f, l, m), a in c.items():
        if f == 'I':
            I += a * g.z(0, l, m).real
        elif f == 'V':
            V += a * g.z(0, l, m).real
        else:
            pol += a * (1 if f == 'E' else 1j) * g.z(2, l, m)
    tt = np.einsum('ni,nj->nij', g.bt, g.bt)
    pp = np.einsum('ni,nj->nij', g.bp, g.bp)
    tp = np.einsum('ni,nj->nij', g.bt, g.bp)
    return 0.5 * (I[:, None, None] * g.P + pol.real[:, None, None] * (tt - pp) + pol.imag[:, None, None] * (tp + tp.transpose(0, 2, 1)) + V[:, None, None] * (tp.transpose(0, 2, 1) - tp))

def stokes(g: Grid, J: np.ndarray) -> tuple[np.ndarray, ...]:
    J = np.asarray(J, float)
    if J.shape != (len(g.w), 3, 3):
        raise ValueError('J shape does not match grid')
    a = np.einsum('ni,nij,nj->n', g.bt, J, g.bt)
    b = np.einsum('ni,nij,nj->n', g.bp, J, g.bp)
    c = np.einsum('ni,nij,nj->n', g.bt, J, g.bp)
    d = np.einsum('ni,nij,nj->n', g.bp, J, g.bt)
    return (a + b, a - b, c + d, d - c)

def analyze(g: Grid, J: np.ndarray, lmax: int=4) -> Coeff:
    I, Q, U, V = stokes(g, J)
    out = {}
    pol = Q + 1j * U
    for l in range(lmax + 1):
        for m in range(-l, l + 1):
            z = g.z(0, l, m).real
            out['I', l, m] = float(np.dot(g.w, I * z))
            out['V', l, m] = float(np.dot(g.w, V * z))
            if l >= 2:
                p = np.dot(g.w, pol * np.conj(g.z(2, l, m)))
                out['E', l, m] = float(p.real)
                out['B', l, m] = float(p.imag)
    return out

def stf_basis() -> np.ndarray:
    """Frobenius-orthonormal BASS U_2m, m=-2,-1,0,1,2."""
    u = np.zeros((5, 3, 3))
    u[0, 0, 1] = u[0, 1, 0] = 1 / sqrt(2)
    u[1, 1, 2] = u[1, 2, 1] = 1 / sqrt(2)
    u[2] = np.diag([-1, -1, 2]) / sqrt(6)
    u[3, 0, 2] = u[3, 2, 0] = 1 / sqrt(2)
    u[4] = np.diag([1, -1, 0]) / sqrt(2)
    return u

def source_matrix(c: Coeff) -> np.ndarray:
    """Exact continuum M=int J dOmega from gain-relevant angular harmonics.

    This 14->9 map is not an invertible dictionary for the full state.
    """
    _validate(c)
    M = sqrt(4 * pi) * c.get(('I', 0, 0), 0.0) * np.eye(3) / 3
    for m, u in zip(range(-2, 3), stf_basis()):
        M += -sqrt(2 * pi / 15) * (c.get(('I', 2, m), 0.0) - sqrt(6) * c.get(('E', 2, m), 0.0)) * u
    d = sqrt(4 * pi / 3) * np.array([c.get(('V', 1, 1), 0.0), c.get(('V', 1, -1), 0.0), c.get(('V', 1, 0), 0.0)])
    M -= 0.5 * np.array([[0, d[2], -d[1]], [-d[2], 0, d[0]], [d[1], -d[0], 0]])
    return M

def collision_coefficients(c: Coeff, chi: float) -> Coeff:
    """Exact static rest-electron Thomson semigroup in this angular convention."""
    _validate(c)
    if not np.isfinite(chi) or chi < 0:
        raise ValueError('Require finite chi>=0')
    em = np.exp(-chi)
    out = {k: em * v for k, v in c.items()}
    out['I', 0, 0] = c.get(('I', 0, 0), 0.0)
    fac = em * np.expm1(0.7 * chi) / 0.7 if 0.7 * chi < 1 else (np.exp(-0.3 * chi) - em) / 0.7
    K = np.array([[0.1, -sqrt(6) / 10], [-sqrt(6) / 10, 0.6]])
    for m in range(-2, 3):
        y = np.array([c.get(('I', 2, m), 0.0), c.get(('E', 2, m), 0.0)])
        a = em * y + fac * (K @ y)
        out['I', 2, m] = float(a[0])
        out['E', 2, m] = float(a[1])
    for m in range(-1, 2):
        out['V', 1, m] = np.exp(-0.5 * chi) * c.get(('V', 1, m), 0.0)
    return out

def hermitian(J: np.ndarray) -> np.ndarray:
    """Decode the real antisymmetric circular-polarization channel explicitly."""
    J = np.asarray(J, float)
    JT = J.swapaxes(-1, -2)
    return 0.5 * (J + JT) + 0.5j * (J - JT)
