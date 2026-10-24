"""Fixed-scale, proper-time homogeneous Einstein operator.

See CONTRACT.md and THEORY_KO.md for physical units and source ownership.
No step divides by H. This module needs NumPy, not JAX or a native extension.
It is an opt-in research operator; the existing production dispatch is unchanged.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
import numpy as np

C_SI = 299_792_458.0
G_SI = 6.67430e-11


@dataclass(frozen=True)
class FixedScale:
    """The fixed length unit L; mu and pressure are both SI J m^-3."""

    length_m: float
    c: float = C_SI
    G: float = G_SI

    def __post_init__(self):
        if not all(math.isfinite(x) and x > 0 for x in
                   (self.length_m, self.c, self.G)):
            raise ValueError("length, c and G must be finite positive constants")

    @property
    def time_s(self):
        return self.length_m / self.c

    @property
    def density_factor(self):
        return 8.0 * math.pi * self.G * self.length_m**2 / self.c**4

    def density_from_si(self, energy_density):
        return np.asarray(energy_density) * self.density_factor

    def flux_from_si(self, energy_flux):
        return np.asarray(energy_flux) * self.density_factor / self.c


def stf(v):
    """Five independent entries: xx, yy, xy, xz, yz."""
    x, y, xy, xz, yz = v
    return np.array([[x, xy, xz], [xy, y, yz], [xz, yz, -x-y]])


def sym(v):
    x, y, z, xy, xz, yz = v
    return np.array([[x, xy, xz], [xy, y, yz], [xz, yz, z]])


def five(m):
    return np.asarray(m)[(0, 1, 0, 0, 1), (0, 1, 1, 2, 2)]


def six(m):
    return np.asarray(m)[(0, 1, 2, 0, 0, 1), (0, 1, 2, 1, 2, 2)]


def cross(v):
    x, y, z = v
    return np.array([[0*v[0], -z, y], [z, 0*v[0], -x], [-y, x, 0*v[0]]])


def epsilon_product(n, tensor):
    """epsilon_ijk n_jl tensor_lk; uses the antisymmetric part of n@tensor."""
    m = n @ tensor
    return np.array([m[1, 2]-m[2, 1], m[2, 0]-m[0, 2], m[0, 1]-m[1, 0]])


def curvature(n, a):
    """Closed spatial Ricci scalar and STF part, in fixed L units."""
    b = 2.0 * (n @ n) - np.trace(n) * n
    r = -6.0 * (a @ a) - np.trace(b) / 2.0
    ax = cross(a)
    s = b - np.trace(b) * np.eye(3) / 3.0 + ax @ n - n @ ax
    return r, s


@dataclass
class State:
    h: float
    sigma: np.ndarray
    n: np.ndarray
    a: np.ndarray
    alpha: float
    rho: np.ndarray
    flux: np.ndarray

    @classmethod
    def unpack(cls, y, sectors=None):
        y = np.asarray(y)
        if y.ndim != 1 or (y.size - 16) % 4 or y.size < 20:
            raise ValueError("state must have length 16+4*n_sector, n_sector>=1")
        ns = (y.size - 16) // 4
        if sectors is not None and ns != sectors:
            raise ValueError("state/source sector count mismatch")
        return cls(y[0], stf(y[1:6]), sym(y[6:12]), y[12:15], y[15],
                   y[16:16+ns], y[16+ns:].reshape(ns, 3))

    def pack(self):
        return np.concatenate(([self.h], five(self.sigma), six(self.n), self.a,
                               [self.alpha], self.rho, np.ravel(self.flux)))

    def validate(self):
        """Validate the tensor representation, without projecting or clipping."""
        if self.sigma.shape != (3, 3) or self.n.shape != (3, 3):
            raise ValueError("geometry tensors must be 3x3")
        if self.a.shape != (3,) or self.rho.ndim != 1 or len(self.rho) < 1:
            raise ValueError("invalid geometry/sector shape")
        if self.flux.shape != (len(self.rho), 3):
            raise ValueError("flux must have one 3-vector per sector")
        if not np.all(np.isfinite(self.pack())):
            raise ValueError("nonfinite state")
        _symmetric(self.n, "n")
        _symmetric(self.sigma, "sigma", tracefree=True)


def _symmetric(a, label, tracefree=False):
    if not np.all(np.isfinite(a)):
        raise ValueError(f"nonfinite {label}")
    tol = 128 * np.finfo(float).eps * max(float(np.max(np.abs(a))), 1e-300)
    if np.max(np.abs(a-a.T)) > tol:
        raise ValueError(f"{label} must be symmetric")
    if tracefree and abs(np.trace(a)) > 3 * tol:
        raise ValueError(f"{label} must be trace-free")


@dataclass
class Source:
    pressure: np.ndarray
    pi: np.ndarray
    energy_transfer: np.ndarray | None = None
    momentum_transfer: np.ndarray | None = None

    def arrays(self, ns, *, balanced=True):
        p = np.asarray(self.pressure)
        pi = np.asarray(self.pi)
        u = np.zeros(ns) if self.energy_transfer is None else np.asarray(self.energy_transfer)
        j = np.zeros((ns, 3)) if self.momentum_transfer is None else np.asarray(self.momentum_transfer)
        if p.shape != (ns,) or pi.shape != (ns, 3, 3) or u.shape != (ns,) or j.shape != (ns, 3):
            raise ValueError("invalid source/sector shape")
        if not all(np.all(np.isfinite(x)) for x in (p, pi, u, j)):
            raise ValueError("nonfinite source")
        for x in pi:
            _symmetric(x, "pi", tracefree=True)
        if balanced:
            for x in (u, j):
                # Scale each component before summation: finite large transfers
                # must not overflow both the residual and its tolerance to inf.
                scale = np.max(np.abs(x), axis=0)
                normalized = x / np.where(scale > 0, scale, 1.0)
                magnitude = np.sum(np.abs(normalized), axis=0)
                if np.any(np.abs(np.sum(normalized, axis=0)) > 128*np.finfo(float).eps*magnitude):
                    raise ValueError("total energy and momentum transfers must balance")
        return p, pi, u, j


def rhs(tau, packed, source: Source, *, cosmological_constant=0.0,
        rotation=(0.0, 0.0, 0.0), enforce_balanced=True):
    """Polynomial Einstein+sector conservation derivative in fixed-scale time.

    `source` is evaluated by the material owner at the current state. It is not
    an additional stress to add to an already sourced prescribed geometry.
    `enforce_balanced=False` is only for explicit constraint-forcing diagnostics.
    """
    y = State.unpack(packed)
    y.validate()
    p, pi, transfer, momentum = source.arrays(len(y.rho), balanced=enforce_balanced)
    rot = np.asarray(rotation)
    if rot.shape != (3,) or not np.all(np.isfinite(rot)) or not np.isfinite(cosmological_constant):
        raise ValueError("invalid rotation or cosmological constant")
    h, s, n, a = y.h, y.sigma, y.n, y.a
    w = cross(rot)
    _, spatial_stf = curvature(n, a)
    dh = -h*h - np.sum(s*s)/3 - (np.sum(y.rho)+3*np.sum(p))/6 + cosmological_constant/3
    ds = -3*h*s - spatial_stf + np.sum(pi, axis=0) + w@s-s@w
    dn = -h*n + s@n+n@s + w@n-n@w
    da = -h*a - s@a + w@a
    drho = -3*h*(y.rho+p) + 2*y.flux@a - np.einsum("ab,iab->i", s, pi) + transfer
    dflux = (-4*h*y.flux - y.flux@s.T + 3*np.einsum("iab,b->ia", pi, a)
             + np.stack([epsilon_product(n, x) for x in pi]) + y.flux@w.T + momentum)
    return State(dh, ds, dn, da, h, drho, dflux).pack()


def constraints(packed, cosmological_constant=0.0):
    y = State.unpack(packed)
    r, _ = curvature(y.n, y.a)
    c = 3*y.h*y.h - np.sum(y.sigma*y.sigma)/2 + r/2 - np.sum(y.rho) - cosmological_constant
    m = np.sum(y.flux, axis=0) - 3*y.sigma@y.a - epsilon_product(y.n, y.sigma)
    return np.concatenate(([c], m, y.n@y.a))


def constraint_derivative(packed, *, cosmological_constant=0.0, rotation=(0., 0., 0.),
                          energy_transfer=0.0, momentum_transfer=(0., 0., 0.)):
    """Analytic off-surface defect propagation; not a projected constraint."""
    y = State.unpack(packed)
    c, m, j = constraints(packed, cosmological_constant)[0], constraints(packed, cosmological_constant)[1:4], constraints(packed, cosmological_constant)[4:7]
    w = cross(np.asarray(rotation))
    dc = -2*y.h*c - 2*y.a@m - energy_transfer
    dm = (-4*y.h*np.eye(3)-y.sigma+w)@m + (3*y.n-np.trace(y.n)*np.eye(3)+3*cross(y.a))@j + np.asarray(momentum_transfer)
    dj = (-2*y.h*np.eye(3)+y.sigma+w)@j
    return np.concatenate(([dc], dm, dj))


def relative_constraint(packed, cosmological_constant=0.0):
    y = State.unpack(packed)
    scale = (3*y.h*y.h + np.sum(y.sigma*y.sigma)/2 + np.sum(y.n*y.n)
             + 6*(y.a@y.a) + np.sum(np.abs(y.rho)) + abs(cosmological_constant))
    return np.max(np.abs(constraints(packed, cosmological_constant))) / max(scale, np.finfo(float).tiny)


def barotropic_source(packed, w):
    y = State.unpack(packed)
    w = np.asarray(w)
    if w.shape != y.rho.shape:
        raise ValueError("one equation-of-state coefficient required per sector")
    return Source(w*y.rho, np.zeros((len(w), 3, 3)))


def hubble_view(packed):
    """Explicit adapter; the proper-time operator itself is regular at h=0."""
    y = State.unpack(packed)
    if y.h == 0:
        raise ValueError("Hubble-normalized variables are singular at h=0")
    return dict(Sigma=y.sigma/y.h, N=y.n/y.h, A=y.a/y.h,
                Omega=y.rho/(3*y.h*y.h), Q=y.flux/(y.h*y.h))


def rotate_state(packed, rotation_matrix):
    """Proper SO(3) rotation only; n is a pseudotensor under improper rotations."""
    o = np.asarray(rotation_matrix)
    if o.shape != (3, 3) or not np.all(np.isfinite(o)) or not np.allclose(o@o.T, np.eye(3), rtol=0, atol=2e-13) or abs(np.linalg.det(o)-1) > 2e-13:
        raise ValueError("proper orthogonal rotation required")
    y = State.unpack(packed)
    return State(y.h, o@y.sigma@o.T, o@y.n@o.T, o@y.a, y.alpha,
                 y.rho.copy(), y.flux@o.T).pack()
