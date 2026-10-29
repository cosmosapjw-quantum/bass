"""CE1-F: positive cell-defined continuum radiation with outward stress bounds.

Each table entry is the TOTAL initial angular energy in eight reflected
solid-angle cells. Density is constant in (mu,phi) inside each original cell.
Exact subdivision preserves this physical function. Rays are only a numerical
quadrature; no physical harmonic/dynamical closure is introduced.

Certificates compare continuum integrals with the exact-real formula defined
by stored binary64 masses/rays. They exclude floating source evaluation and
ODE time-integration error. See research/ce1f_20261029/THEORY.md.
"""
from __future__ import annotations

import ctypes as C
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache

import numpy as np

from .einstein_error_budget import _oracle, _real
from .einstein_interval import (Interval, _iv_fraction, _lib, _P, D, U,
                                propagate_interval)

for _name in ('mpfr_sinpi', 'mpfr_cospi'):
    try:
        _fn = getattr(_lib, _name)
    except AttributeError as exc:
        raise ImportError('CE1-F requires MPFR sinpi/cospi; no float fallback') from exc
    _fn.argtypes = [_P, _P, C.c_int]
    _fn.restype = C.c_int
_lib.mpfr_const_pi.argtypes = [_P, C.c_int]
_lib.mpfr_const_pi.restype = C.c_int


def _q(x):
    return Fraction.from_float(float(x))


def _absmax(x):
    return max(abs(x.lower), abs(x.upper))


@lru_cache(maxsize=4096)
def _trig_pi(t, kind):
    """Outward sin(pi*t)/cos(pi*t), exact rational t in [0,1]."""
    if not 0 <= t <= 1:
        raise ValueError('Trigonometric fraction outside [0,1]')
    if kind == 'sin' and t in (0, Fraction(1, 2), 1):
        return Interval(1 if t == Fraction(1, 2) else 0)
    if kind == 'cos' and t in (0, Fraction(1, 2), 1):
        return Interval(1 if t == 0 else -1 if t == 1 else 0)
    x = _iv_fraction(t)
    f = getattr(_lib, 'mpfr_' + kind + 'pi')
    vals = []
    for endpoint in (x.a, x.b):
        z = Interval._empty()
        f(z.a.ptr(), endpoint.ptr(), D)
        f(z.b.ptr(), endpoint.ptr(), U)
        vals.append(z)
    lo = min(z.lower for z in vals)
    hi = max(z.upper for z in vals)
    # Sine is not monotone across 1/2. Its interior maximum is exact.
    if kind == 'sin' and x.lower <= .5 <= x.upper:
        hi = 1.
    return Interval.between(lo, hi)


@lru_cache(maxsize=1)
def _pi():
    z = Interval._empty()
    _lib.mpfr_const_pi(z.a.ptr(), D)
    _lib.mpfr_const_pi(z.b.ptr(), U)
    return z


def _unit_interval(x):
    """Intersect a proof enclosure with its analytically known [0,1] range.

    This tightens arithmetic bounds only; no source data or weights are clipped.
    """
    lo, hi = max(0., x.lower), min(1., x.upper)
    if lo > hi:
        raise ArithmeticError('Cell mean/range enclosure contradicts simplex')
    return Interval.between(lo, hi)


@lru_cache(maxsize=4096)
def _cell_geometry(ma, mb, ta, tb):
    # t=phi/(pi/2); sin(2phi)=sin(pi*t).
    mz = _iv_fraction((ma*ma + ma*mb + mb*mb) / 3)
    c = Interval(1)/2 + (_trig_pi(tb, 'sin') - _trig_pi(ta, 'sin')) / (
        2*_pi()*_iv_fraction(tb-ta))
    means = tuple(_unit_interval(x) for x in ((1-mz)*c, (1-mz)*(1-c), mz))
    ca = _unit_interval((1+_trig_pi(ta, 'cos'))/2)
    cb = _unit_interval((1+_trig_pi(tb, 'cos'))/2)
    a, b = _iv_fraction(ma*ma), _iv_fraction(mb*mb)
    lower = [(1-b)*cb, (1-b)*(1-ca), a]
    upper = [(1-a)*ca, (1-a)*(1-cb), b]
    ranges = tuple(Interval.between(max(0., l.lower), min(1., h.upper))
                   for l, h in zip(lower, upper))
    return means, ranges


@dataclass(frozen=True)
class _Cell:
    bounds: tuple[Fraction, Fraction, Fraction, Fraction]
    energy: Fraction
    means: tuple[Interval, Interval, Interval]
    ranges: tuple[Interval, Interval, Interval]


class TabulatedRadiation:
    """Nonnegative piecewise-constant continuum source, eight implicit reflections.

    mu_edges and phi_fraction_edges must strictly partition [0,1]. Exact binary
    table energies include all eight octants. Integer refinement subdivides
    each original cell uniformly in solid angle without changing its density.
    """
    def __init__(self, mu_edges, phi_fraction_edges, cell_energy, *,
                 refinement=1, backend=None):
        _oracle(backend)
        mu = _real(mu_edges)
        ph = _real(phi_fraction_edges)
        w = _real(cell_energy)
        for a in (mu, ph):
            if (a.ndim != 1 or len(a) < 2 or a[0] != 0 or a[-1] != 1
                    or np.any(np.diff(a) <= 0)):
                raise ValueError('Strict ordered edges must partition [0,1]')
        if w.shape != (len(mu)-1, len(ph)-1) or np.any(w < 0):
            raise ValueError('Nonnegative cell energy table with matching shape required')
        if (isinstance(refinement, (bool, np.bool_))
                or not isinstance(refinement, (int, np.integer))
                or not 1 <= refinement <= 32
                or w.size*int(refinement)**2 > 20000):
            raise ValueError('Integer refinement 1..32 and <=20000 cells required')
        f = int(refinement)
        muq, phq = tuple(map(_q, mu)), tuple(map(_q, ph))
        original = tuple(_q(t) for t in w.ravel())
        total = sum(original, Fraction())
        try:
            total_float = float(total)
        except OverflowError as exc:
            raise ValueError('Finite positive total energy required') from exc
        if total <= 0 or not np.isfinite(total_float):
            raise ValueError('Finite positive total energy required')
        cells, rays, masses = [], [], []
        for i in range(len(muq)-1):
            for j in range(len(phq)-1):
                energy = original[i*(len(phq)-1)+j] / (f*f)
                if energy == 0:
                    continue
                for k in range(f):
                    ma = muq[i] + (muq[i+1]-muq[i])*Fraction(k, f)
                    mb = muq[i] + (muq[i+1]-muq[i])*Fraction(k+1, f)
                    for l in range(f):
                        ta = phq[j] + (phq[j+1]-phq[j])*Fraction(l, f)
                        tb = phq[j] + (phq[j+1]-phq[j])*Fraction(l+1, f)
                        means, ranges = _cell_geometry(ma, mb, ta, tb)
                        ray = np.sqrt([m.lower/2 + m.upper/2 for m in means])
                        mass = float(energy)
                        if mass <= 0 or not np.isfinite(ray).all() or np.dot(ray, ray) <= 0:
                            raise ValueError('Positive stored mass and resolved ray norm required')
                        cells.append(_Cell((ma, mb, ta, tb), energy, means, ranges))
                        rays.append(ray)
                        masses.append(mass)
        self.cells = tuple(cells)
        self.n = np.asarray(rays, float)
        self.mass = np.asarray(masses, float)
        self.mu_edges, self.phi_fraction_edges = mu.copy(), ph.copy()
        self.cell_energy, self.refinement = w.copy(), f
        self.continuum_energy = total
        self.energy0 = self.moments(np.zeros(3))[0]
        if not np.isfinite(self.energy0) or self.energy0 <= 0:
            raise ValueError('Finite positive stored initial energy required')
        for a in (self.n, self.mass, self.mu_edges, self.phi_fraction_edges, self.cell_energy):
            a.setflags(write=False)
        # Physical measure is immutable. The exact-binary numerical ray/mass
        # arrays are intentionally *not* in this lock: their cardinality-safe
        # rebinding is an admitted a posteriori recertification path.
        self._physical_table_lock = (
            self.cells, self.continuum_energy, self.refinement,
            (self.mu_edges.shape, self.mu_edges.tobytes()),
            (self.phi_fraction_edges.shape, self.phi_fraction_edges.tobytes()),
            (self.cell_energy.shape, self.cell_energy.tobytes()),
        )

    def moments(self, ell):
        e = _real(ell, (3,))
        with np.errstate(over='raise', under='raise', invalid='raise', divide='raise'):
            b = np.exp(-2*e)
            x = self.n*self.n
            r = np.sqrt(x@b)
            v = np.exp(-e.sum())
            E = v*(self.mass@r)
            P = v*b*np.einsum('q,qi->i', self.mass/r, x)
        if not np.isfinite(E) or not np.isfinite(P).all() or E <= 0:
            raise FloatingPointError('Source outside supported binary64 range')
        return float(E), P

    def rhs(self, u, y):
        y = _real(y, (6,))
        h = y[3:]
        return np.r_[h, -h.sum()*h + self.moments(y[:3])[1]]

    def initial_state(self, shear=(.2, -.13, -.07)):
        s = _real(shear, (3,))
        scale = max(np.finfo(float).tiny, float(np.max(abs(s))))
        if abs(s.sum()) > 2e-12*scale:
            raise ValueError('Trace-free shear required')
        h = np.sqrt((self.energy0+.5*np.dot(s, s))/3)+s
        if not np.isfinite(h).all() or np.any(h < 0):
            raise ValueError('Nonnegative directional initial expansion required')
        return np.r_[np.zeros(3), h]


def _source(source):
    if not isinstance(source, TabulatedRadiation):
        raise TypeError('TabulatedRadiation required')
    # The continuum cells/edges/total are *physical* initial conditions, not
    # interchangeable numerical quadrature data. Silently changing one while
    # retaining the other invalidates the Hamiltonian root and Emax premise.
    lock = source._physical_table_lock
    if (source.cells is not lock[0] or source.continuum_energy != lock[1]
            or source.refinement != lock[2]):
        raise ValueError('Immutable physical cell/energy input contract violated')
    for array, expected in zip(
        (source.mu_edges, source.phi_fraction_edges, source.cell_energy), lock[3:]
    ):
        if (not isinstance(array, np.ndarray) or array.dtype != np.float64
                or (array.shape, array.tobytes()) != expected):
            raise ValueError('Immutable physical angular table/edge input contract violated')


def _stored_data(source):
    # One stored positive ray and mass per refined physical cell is required.
    # A zip-based pressure bound must never silently omit a mutated ray.
    ncell = len(source.cells)
    if np.shape(source.n) != (ncell, 3) or np.shape(source.mass) != (ncell,):
        raise ValueError("Stored ray/cell cardinality and shape contract violated")
    squared = [tuple(_q(x)**2 for x in row) for row in source.n]
    masses = tuple(map(_q, source.mass))
    if any(w <= 0 for w in masses) or any(sum(row) <= 0 for row in squared):
        raise ValueError('Positive stored masses and ray norms required')
    return squared, masses


def certified_tabulated_energy(source):
    """Separate continuum energy, exact-real quadrature energy and float result."""
    _source(source)
    squared, masses = _stored_data(source)
    exact = sum((_iv_fraction(w)*_iv_fraction(sum(x)).sqrt()
                 for w, x in zip(masses, squared)), Interval(0))
    continuum = _iv_fraction(source.continuum_energy)
    return {'continuum_lower': continuum.lower, 'continuum_upper': continuum.upper,
            'stored_real_lower': exact.lower, 'stored_real_upper': exact.upper,
            'continuum_vs_stored_real_upper': _absmax(continuum-exact),
            'stored_sum_roundoff_upper': _absmax(exact-Interval(source.energy0)),
            'continuum_vs_float_initial_upper': _absmax(continuum-Interval(source.energy0)),
            'energy_max_upper': max(continuum.upper, exact.upper)}


def certified_tabulated_pressure(source, upper):
    """Uniform bound on 0<=ell_i<=upper_i, including stored ray/mass rounding."""
    _source(source)
    hi = _real(upper, (3,))
    if np.any(hi < 0) or max(hi) > 2:
        raise ValueError('Require nonnegative expanding box with max ell<=2')
    L = Interval(float(max(hi)))
    d = Interval((1-(-2*L).exp()).upper)
    rmin = (-L).exp()
    squared, stored_masses = _stored_data(source)
    totals = [Interval(0) for _ in range(3)]
    bias_sum, ray_sum, mass_sum = Interval(0), Interval(0), Interval(0)
    for cell, X, stored_w in zip(source.cells, squared, stored_masses):
        widths = [Interval(r.upper)-Interval(r.lower) for r in cell.ranges]
        variances = [z*z/4 for z in widths]
        V = sum(variances, Interval(0))
        Q = 3*d*d*V/4
        eps = [Interval(_absmax(_iv_fraction(x)-m)) for x, m in zip(X, cell.means)]
        eps1 = sum(eps, Interval(0))
        norm2 = sum(X)
        r0 = ((-2*L).exp()*_iv_fraction(min(Fraction(1), norm2))).sqrt()
        w = _iv_fraction(cell.energy)
        mass_error = _iv_fraction(abs(cell.energy-stored_w))*_iv_fraction(norm2).sqrt()
        bc, rc = [], []
        for i in range(3):
            bias = (variances[i]*Q).sqrt()/(2*rmin**3) + (
                3*Interval(cell.ranges[i].upper)*Q/(8*rmin**5))
            M = max(cell.means[i].upper, _iv_fraction(X[i]).upper)
            ray = eps[i]/r0 + Interval(M)*eps1/(2*r0**3)
            totals[i] = totals[i]+w*(bias+ray)+mass_error
            bc.append(bias.upper)
            rc.append(ray.upper)
        bias_sum = bias_sum+w*Interval(max(bc))
        ray_sum = ray_sum+w*Interval(max(rc))
        mass_sum = mass_sum+mass_error
    bounds = [z.upper for z in totals]
    return {'status': 'MPFR_OUTWARD_TABULATED_PRESSURE_BOUND',
            'pressure_upper': bounds, 'bound_max': max(bounds),
            'parts_max_upper': {'cell_centered_taylor': bias_sum.upper,
                                'stored_ray': ray_sum.upper,
                                'stored_mass': mass_sum.upper},
            'geometry_box_upper': hi.tolist(), 'refined_cells': len(source.cells),
            'rounding': 'MPFR192_RNDD_RNDU_EXACT_BINARY_DATA',
            'physical_table_changed_by_refinement': False,
            'floating_source_evaluation_error_included': False,
            'production_ready': False}


def certified_tabulated_geometry(source, *, end=.08, shear=(.2, -.13, -.07)):
    """Continuum-vs-stored-source exact ODE comparison; time error excluded."""
    _source(source)
    T = float(end)
    if not np.isfinite(T) or not 0 < T <= .2:
        raise ValueError('Pilot end time must be in (0,.2]')
    s = _real(shear, (3,))
    stored = source.initial_state(s)[3:]
    sx, sy = _q(s[0]), _q(s[1])
    si = [_iv_fraction(sx), _iv_fraction(sy), _iv_fraction(-(sx+sy))]
    ec = certified_tabulated_energy(source)
    E = _iv_fraction(source.continuum_energy)
    hbar = ((E+sum((z*z for z in si), Interval(0))/2)/3).sqrt()
    hc = [hbar+z for z in si]
    if any(h.lower < 0 for h in hc):
        raise ValueError('Continuum directional expansion must be nonnegative')
    d0 = max(_absmax(h-Interval(float(v))) for h, v in zip(hc, stored))
    Emax = ec['energy_max_upper']
    box = [(Interval(max(h.upper, float(v)))*Interval(T)
            + Interval(Emax)*Interval(T)**2/2).upper for h, v in zip(hc, stored)]
    src = certified_tabulated_pressure(source, box)
    prop = propagate_interval([Interval(0), Interval(d0)], Interval(T),
                              Interval(Emax), Interval(0), Interval(src['bound_max']))
    return {'status': 'SCOPED_TABULATED_COUPLED_ENCLOSURE', 'u_end': T,
            'geometry_h_upper': prop[1].upper, 'geometry_ell_upper': prop[0].upper,
            'initial_h_error_upper': d0, 'energy_max_upper': Emax,
            'energy_certificate': ec, 'source_certificate': src,
            'source_pressure_upper': src['bound_max'], 'geometry_box_upper': box,
            'initial_shear_reference': 'EXACT_BINARY_SX_SY_TRACEFREE',
            'time_integration_error_included': False, 'production_ready': False}
