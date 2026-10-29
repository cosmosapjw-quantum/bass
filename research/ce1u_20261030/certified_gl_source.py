"""CE1-U: MPFR192 enclosure for the ORIGINAL six-cell source vs binary64 GL nodes.

Two *distinct* errors: (1) ideal tensor Gauss-Legendre quadrature of analytic
angular pressure within each original physical cell, and (2) ideal algebraic GL
nodes/weights and trigonometric rays vs the actually stored binary64 source.

This is a standalone proof-scoped certificate, not a replacement for CE1-F's
midpoint-centered source certificate. It assumes the frozen original 6-cell
positive massless collisionless expanding diagonal Bianchi-I pilot geometry.
"""
from __future__ import annotations
import ctypes as C
from fractions import Fraction as Q
from functools import lru_cache
from math import nextafter, inf
import hashlib
import numpy as np

from bianchi.nonperturbative.einstein_interval import Interval as I, _iv_fraction as iv, _lib, _P, D, U
from bianchi.nonperturbative.einstein_tabulated_source import TabulatedRadiation, _source, _stored_data
from research.ce1t_20261030.cellwise_gl_rust import (MU, PHI, CELL_E, SHEAR,
                                                     frozen_source_identity, make_cell_rays, sha)

B = Q(7, 100)  # rigorously dominated by pilot h0<=4/5, Emax<=1, T<=2/25
RHO = Q(6)
PI_UP = Q(22, 7)  # strict classical rational upper bound on mathematical pi
NORM_MIN = Q(99, 100)
X_MAX = Q(101, 100)
SOURCE_SHA = '022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035'

_lib.mpfr_sinpi.argtypes = [_P, _P, C.c_int]
_lib.mpfr_sinpi.restype = C.c_int


def absmax(x: I) -> float:
    if not (np.isfinite(x.lower) and np.isfinite(x.upper)):
        raise ArithmeticError('Nonfinite interval in certified GL source')
    return max(abs(x.lower), abs(x.upper))


def bracket(lo: Q, hi: Q) -> I:
    return I.between(iv(lo).lower, iv(hi).upper)


def _poly_coeffs(n: int):
    a, b = (Q(1),), (Q(0), Q(1))
    if n == 0:
        return a
    if n == 1:
        return b
    for k in range(2, n + 1):
        x = [Q(0)] * (k + 1)
        for j, v in enumerate(b):
            x[j + 1] += Q(2 * k - 1, k) * v
        for j, v in enumerate(a):
            x[j] -= Q(k - 1, k) * v
        a, b = b, tuple(x)
    return b


def _eval_horner(coefs, x):
    s = Q(0)
    for c in reversed(coefs):
        s = s * x + c
    return s


def _ratmul(a, b):
    p = [a[0] * b[0], a[0] * b[1], a[1] * b[0], a[1] * b[1]]
    return min(p), max(p)


def _ratadd(a, b):
    return a[0] + b[0], a[1] + b[1]


def _ratpoly(coefs, lo, hi):
    s = (Q(0), Q(0))
    for c in reversed(coefs):
        s = _ratadd(_ratmul(s, (lo, hi)), (c, c))
    return s


@lru_cache(maxsize=8)
def exact_gl_brackets(order: int):
    """Certified exact rational root isolation + GL weight intervals.

    Each bracket has opposite exact Legendre polynomial signs. Since all n
    brackets are disjoint and P_n has degree n, they exhaust the n simple roots.
    Weights use exact algebraic formula 2/[(1-x²) P'_n(x)²].
    """
    if isinstance(order, bool) or not isinstance(order, int) or not 1 <= order <= 16:
        raise ValueError('Only integer GL order 1..16 with exact root isolation')
    roots, _ = np.polynomial.legendre.leggauss(order)
    polynomial = _poly_coeffs(order)
    dpoly = tuple(k * c for k, c in enumerate(polynomial))[1:]
    result = []
    for approx in roots:
        low, high = float(approx), float(approx)
        for _ in range(32):
            low = nextafter(low, -inf)
            high = nextafter(high, inf)
            lo, hi = Q.from_float(low), Q.from_float(high)
            pl, ph = _eval_horner(polynomial, lo), _eval_horner(polynomial, hi)
            if pl * ph < 0:
                break
        else:
            raise ArithmeticError('Could not isolate exact Legendre root')
        d0, d1 = _ratpoly(dpoly, lo, hi)
        if d0 <= 0 <= d1:
            raise ArithmeticError('Unresolved GL derivative sign in root bracket')
        # 1-r² >=0 within [-1,1]. Naive exact interval rational multiplication.
        r2lo, r2hi = _ratmul((lo, hi), (lo, hi))
        tlo, thi = Q(1)-r2hi, Q(1)-r2lo
        v0, v1 = _ratmul((d0, d1), (d0, d1))
        z0, z1 = _ratmul((tlo, thi), (v0, v1))
        if not 0 < z0 <= z1:
            raise ArithmeticError('GL weight denominator not provably positive')
        wlo, whi = Q(2)/z1, Q(2)/z0
        result.append(((lo, hi), (wlo, whi)))
    if any(result[i][0][1] >= result[i+1][0][0] for i in range(len(result)-1)):
        raise ArithmeticError('Exact GL root intervals overlap')
    return tuple(result)


def _sinpi_monotone(x: I) -> I:
    """sin(pi*x) increasing over proven 0<=x<=1/2."""
    if not 0 <= x.lower <= x.upper <= .5:
        raise ValueError('sinpi monotonic domain violated')
    y = I._empty()
    _lib.mpfr_sinpi(y.a.ptr(), x.a.ptr(), D)
    _lib.mpfr_sinpi(y.b.ptr(), x.b.ptr(), U)
    return y


def ideal_squared_rays(mu_bracket, phi_bracket):
    mu = bracket(*mu_bracket)
    ph = bracket(*phi_bracket)
    z = mu*mu
    one_minus_z = I(1) - z
    if one_minus_z.lower < 0:
        raise ArithmeticError('Ideal GL unit-angle geometry escaped the first octant')
    sn = _sinpi_monotone(ph/I(2))
    cs = _sinpi_monotone((I(1)-ph)/I(2))
    return ((one_minus_z*cs*cs), (one_minus_z*sn*sn), z)


def sample_gl_source(order: int) -> TabulatedRadiation:
    frozen_source_identity()
    ray, mass = make_cell_rays(order)
    src = TabulatedRadiation(MU, PHI, CELL_E, refinement=order, backend='python_oracle')
    assert ray.shape == src.n.shape and mass.shape == src.mass.shape
    src.n = ray
    src.mass = mass
    # Critical: cached midpoint initial energy MUST NOT initialize new GL ODE.
    src.energy0 = src.moments(np.zeros(3))[0]
    _source(src)
    _stored_data(src)
    if not 0 < src.energy0 < 1:
        raise ValueError('Source outside E0<=1 bounding premise')
    return src


def _geometry_analytic_majorant(order: int):
    # For mu/t complex Bernstein ellipses separately: no product ellipse needed.
    # |Z-1| <= D (1+2 U_mu^2) on the mu ellipse (t real), and
    # |Z-1| <= D cosh(pi*r_t) on the t ellipse (mu real).
    d = I(1) - (-2*iv(B)).exp()
    u = iv(Q(3,4)) + iv(Q(1,4)) * (iv(RHO)+iv(1/RHO))/2
    radius_t = iv(Q(1,4))*(iv(RHO)-iv(1/RHO))/2
    ct = (iv(PI_UP)*radius_t).cosh()
    qmu = d*(I(1)+2*u*u)
    qt = d*ct
    if qmu.upper >= 1 or qt.upper >= 1:
        raise ArithmeticError('Complex ellipse crosses uncertified sqrt branch')
    mmu = (I(1)+u*u)/(I(1)-qmu).sqrt()
    mt = ct/(I(1)-qt).sqrt()
    total_exact = sum((Q.from_float(float(a)) for a in CELL_E.ravel()), Q())
    # Chebyshev tail of degree (2n-1), positive normalized GL and integral.
    per_unit = I(4)*(mmu+mt)/(iv(RHO-1) * I(int(RHO)**(2*order-1)))
    res = iv(total_exact) * per_unit
    return {'qmu_upper': qmu.upper, 'qphi_upper': qt.upper,
            'Mmu_upper': mmu.upper, 'Mphi_upper': mt.upper,
            'ideal_gl_pressure_error_upper': res.upper,
            'analytic_assumptions': 'real expanding box 0<=ell_i<=0.07, separate ellipses rho=6; exact binary six-cell continuum'}


def certify_gl_source(order: int, source: TabulatedRadiation | None = None):
    """MPFR192 bound on exact continuum pressure minus exact binary GL source.

    The first part is analytical ideal Gauss quadrature; the second accounts for
    ALL binary GL root, Legendre weight, trig direction, stored mass roundoff.
    """
    if order not in (4, 6, 8):
        raise ValueError('Only validated original-cell GL4/GL6/GL8 in CE1-U')
    source = sample_gl_source(order) if source is None else source
    _source(source)
    _stored_data(source)
    # A self-consistent *different* physical table must not borrow the six-cell
    # analytic error theorem even if its numerical rays are copied from this one.
    if (source.refinement != order or not np.array_equal(source.mu_edges, MU)
            or not np.array_equal(source.phi_fraction_edges, PHI)
            or not np.array_equal(source.cell_energy, CELL_E)):
        raise ValueError('Immutable original six-cell physical input mismatch')
    expected = sample_gl_source(order)
    if not (np.array_equal(source.n, expected.n) and np.array_equal(source.mass, expected.mass)):
        raise ValueError('Frozen GL ray/mass binary identity mismatch')
    if source.energy0 != expected.energy0:
        raise ValueError('Frozen GL initial mass energy cache mismatch')
    analytic = _geometry_analytic_majorant(order)
    roots = exact_gl_brackets(order)
    # For both stored and ideal unit sphere nodes, finite stored norm2>=0.99.
    for n in source.n:
        norm2 = sum((Q.from_float(float(z))**2 for z in n), Q())
        if not (NORM_MIN < norm2 < X_MAX):
            raise ValueError('Stored GL unit-ray premise violated')
    rmin = (-iv(B)).exp() * iv(NORM_MIN).sqrt()
    invr = I(1)/rmin
    k = invr + iv(X_MAX)/(2*rmin*rmin*rmin)
    binary_sum = I(0)
    rayerrmax = 0.0
    for ci in range(2):
        for cj in range(3):
            em = Q.from_float(float(CELL_E[ci,cj]))
            mu_center = Q.from_float(float((MU[ci]+MU[ci+1])/2))
            mu_half = Q.from_float(float((MU[ci+1]-MU[ci])/2))
            ph_center = Q.from_float(float((PHI[cj]+PHI[cj+1])/2))
            ph_half = Q.from_float(float((PHI[cj+1]-PHI[cj])/2))
            for a, (roota, wa) in enumerate(roots):
                ma = (mu_center+mu_half*roota[0],mu_center+mu_half*roota[1])
                for b, (rootb, wb) in enumerate(roots):
                    t = (ph_center+ph_half*rootb[0],ph_center+ph_half*rootb[1])
                    xi = ideal_squared_rays(ma,t)
                    lam = iv(em)*bracket(*wa)*bracket(*wb)/4
                    idx = (ci*3+cj)*order*order+a*order+b
                    stored_mass = float(source.mass[idx])
                    mass_gap = absmax(lam-I(stored_mass))
                    eps = [absmax(xi[j]-iv(Q.from_float(float(source.n[idx,j]))**2)) for j in range(3)]
                    rayerrmax = max(rayerrmax, max(eps))
                    # ||d g_i / d x||_{infty} <= 1/rmin + x_max/(2*rmin^3).
                    # |lam*g_ideal - w*g_stored| <= |lam-w|/rmin + w*k*sum|delta x_j|.
                    binary_sum = binary_sum + I(mass_gap)*invr + I(stored_mass)*k*sum((I(z) for z in eps),I(0))
    combined = I(analytic['ideal_gl_pressure_error_upper']) + binary_sum
    out={'schema':'bass.ce1u.gl_cellwise_source_certificate.v1',
         'order':order, 'rays':len(source.n), 'physical_table_sha256':SOURCE_SHA,
         'stored_ray_sha256':sha(np.asarray(source.n,dtype='<f8').tobytes()),
         'stored_mass_sha256':sha(np.asarray(source.mass,dtype='<f8').tobytes()),
         'geometry_upper':float(B), 'rho':6, 'mpfr_precision_bits':192,
         **analytic, 'exact_root_brackets':len(roots),
         'max_component_ideal_vs_binary_squared_ray_upper':rayerrmax,
         'binary_input_pressure_error_upper':binary_sum.upper,
         'total_pressure_error_upper':combined.upper,
         'output_usage':'positive six-cell continuum vs exact-real stored binary GL source only; no time error',
         'production_ready':False,'upper_dag':'9/15'}
    assert out['total_pressure_error_upper'] > 0
    return out


if __name__=='__main__':
    import json,sys
    for n in map(int,sys.argv[1:] or (6,8)):
        print(json.dumps(certify_gl_source(n),indent=2,sort_keys=True))
