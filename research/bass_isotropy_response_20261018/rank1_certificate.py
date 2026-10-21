"""S6b: exact input certificate and execution path for rank-one P2/P4 supports.

A support with two distinct z=mu^2 values admits strictly positive P2=P4=0
weights iff z1<1/3<z2 and 15 z1 z2 - 5(z1+z2) + 3 = 0 (S3 Theorem, m=2). In
binary64, polynomial equality is decidable using exact dyadic arithmetic.
Rounded rays alone do not uniquely identify the intended algebraic support;
the floating-point classifier angular_p24 reports FEASIBILITY_UNRESOLVED_RANK1
for its ambiguous rank-one cases. Here the caller supplies that intended exact
support as an integer quadratic c2 z^2 + c1 z + c0. Fraction arithmetic verifies
the algebraic support and each sign-change isolation interval. Binding certifies
proximity to a unique exact root, not equality of the rounded ray to that root.
The final binary64 weights are separately checked with the unchanged 3e-15
direct floating-point moment gate. No tolerance is widened.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
import hashlib
import json
import math
import re
import mpmath as mp
import numpy as np
from angular_p24 import DEFAULT_ATOL, feasibility, legendre24

CERT_SCHEMA = 'bass.rank1_support_certificate.v1'
ALGORITHM_ID = 'BASS_LRS_SOURCE_P24_RANK1_CERTIFIED_V1'
# New acceptance width (about 16 ulp of z near 1, 3.55e-15 absolute) binding a
# binary64 ray to an exact root; the unchanged 3e-15 moment gate still applies.
BINDING_HALF_WIDTH = Fraction(1, 2**48)
_INT = re.compile(r'-?[0-9]+')
T, V = Fraction(1, 3), Fraction(1, 5)


@dataclass(frozen=True)
class Rank1Result:
    weights: np.ndarray
    residuals: np.ndarray
    group_weights: tuple
    roots: tuple
    assignment: tuple
    float_status: str
    certificate_sha256: str


def _int(x):
    if isinstance(x, bool) or not isinstance(x, (int, str)):
        raise ValueError('RANK1_CERT_INTEGER')
    if isinstance(x, str) and not _INT.fullmatch(x):
        raise ValueError('RANK1_CERT_INTEGER')
    v = int(x)
    if abs(v) > 10**60:
        raise ValueError('RANK1_CERT_INTEGER_RANGE')
    return v


def verify_support(cert: dict) -> dict:
    """Exact rational checks on the certified quadratic. Returns s=z1+z2, p=z1z2."""
    if not isinstance(cert, dict) or cert.get('schema') != CERT_SCHEMA:
        raise ValueError('RANK1_CERT_SCHEMA')
    coeff = cert.get('z_quadratic')
    if not isinstance(coeff, list) or len(coeff) != 3:
        raise ValueError('RANK1_CERT_SHAPE')
    c0, c1, c2 = (_int(x) for x in coeff)
    if c2 == 0:
        raise ValueError('RANK1_CERT_DEGREE')
    s, p = Fraction(-c1, c2), Fraction(c0, c2)
    disc = s*s-4*p
    if disc <= 0:
        raise ValueError('RANK1_CERT_NOT_TWO_DISTINCT_ROOTS')
    if not (s >= 0 and p >= 0 and 2-s >= 0 and 1-s+p >= 0):
        raise ValueError('RANK1_CERT_ROOTS_OUTSIDE_UNIT')
    if not T*T-s*T+p < 0:
        raise ValueError('INFEASIBLE_P24_MEAN_EXACT')
    if 15*p-5*s+3 != 0:
        raise ValueError('INFEASIBLE_P24_RANK1_EXACT')
    return {'s': s, 'p': p, 'disc': disc, 'coeff': (c0, c1, c2)}


def _poly(z, s, p):
    return z*z-s*z+p


def bind_rays(mu, s: Fraction, p: Fraction) -> tuple:
    """Assign each binary64 ray to the unique exact root within its z interval."""
    half = s/2  # vertex separates the two roots
    out = []
    for m in mu:
        z = Fraction(float(m))**2
        if _poly(z, s, p) == 0:
            out.append(0 if z < half else 1); continue
        lo, hi = z-BINDING_HALF_WIDTH, z+BINDING_HALF_WIDTH
        if lo <= half <= hi:
            raise ValueError('RANK1_BINDING_AMBIGUOUS')
        a, b = _poly(lo, s, p), _poly(hi, s, p)
        if a*b > 0:
            raise ValueError('RANK1_BINDING_NO_ROOT')
        out.append(0 if hi < half else 1)
    if set(out) != {0, 1}:
        raise ValueError('RANK1_BINDING_MISSING_ROOT')
    return tuple(out)


def certificate_sha256(cert: dict) -> str:
    return hashlib.sha256(json.dumps(cert, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def project_rank1(mu, prior, cert: dict, *, atol=DEFAULT_ATOL) -> Rank1Result:
    """Unique positive P2/P4 weights on a certified rank-one support.

    On a rank-one support the group totals are fixed by the moments; the KL
    minimizer keeps prior ratios inside each group (pair or z-group).
    """
    m = np.asarray(mu, dtype=float); q = np.asarray(prior, dtype=float)
    if (m.ndim != 1 or q.shape != m.shape or not 2 <= m.size <= 4096 or
            not np.isfinite(m).all() or not np.isfinite(q).all() or
            np.any(abs(m) > 1) or np.any(q <= 0) or np.any(np.diff(m) <= 0)):
        raise ValueError('ANGULAR_INPUT_DOMAIN')
    if not math.isfinite(atol) or not 1e-16 <= atol <= DEFAULT_ATOL:
        raise ValueError('ANGULAR_TOLERANCE_DOMAIN')
    q = q/q.max(); q = q/math.fsum(q)
    if np.max(abs(m+m[::-1])) > 5e-14 or np.max(abs(q-q[::-1])) > 5e-14:
        raise ValueError('REFLECTION_SOURCE_REQUIRED')
    fstat = feasibility(m)
    if fstat.distinct_z != 2:
        raise ValueError('RANK1_CERT_SUPPORT_RANK')
    if fstat.status != 'FEASIBILITY_UNRESOLVED_RANK1':
        # Only the binary64-undecidable case is routed here; decided cases keep
        # their angular_p24 status (incl. near-boundary and mean failures).
        raise ValueError('RANK1_CERT_NOT_UNRESOLVED:'+fstat.status)
    exact = verify_support(cert)
    assign = bind_rays(m, exact['s'], exact['p'])
    with mp.workdps(50):
        s = mp.mpf(exact['s'].numerator)/exact['s'].denominator
        root = mp.sqrt(mp.mpf(exact['disc'].numerator)/exact['disc'].denominator)
        z1, z2 = (s-root)/2, (s+root)/2
        t = mp.mpf(1)/3
        beta = ((z2-t)/(z2-z1), (t-z1)/(z2-z1))
        groups = [[i for i, k in enumerate(assign) if k == g] for g in (0, 1)]
        w = [mp.mpf(0)]*len(m)
        for g, idx in enumerate(groups):
            qs = mp.fsum(mp.mpf(float(q[i])) for i in idx)
            for i in idx:
                w[i] = beta[g]*mp.mpf(float(q[i]))/qs
        weights = np.array([float(x) for x in w])
    # Direct binary64 gates, identical to angular_p24.project finish().
    p2, p4 = legendre24(m)
    res = np.array([math.fsum(weights*p2), math.fsum(weights*p4)])
    if not np.isfinite(weights).all() or np.any(weights <= 0):
        raise ArithmeticError('NUMERIC_POSITIVE_SUPPORT_LOSS')
    if max(abs(res)) > atol or abs(math.fsum(weights)-1) > 5e-16:
        raise ArithmeticError('MOMENT_TOLERANCE')
    if np.max(abs(weights-weights[::-1])) > 5e-14:
        raise ArithmeticError('REFLECTION_RESULT')
    return Rank1Result(weights, res, (float(beta[0]), float(beta[1])), (float(z1), float(z2)),
                       assign, fstat.status, certificate_sha256(cert))
