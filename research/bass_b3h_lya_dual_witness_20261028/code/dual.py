"""Exact constant positive dual storage for a shared-rate two-state family.

M(theta,R) = [[a,-beta],[-chi,d+R]], r=N*R*e2.
The two supplied matrices exclude R. Their convex segment and 0<=R<=Rmax
are the admitted family. This module supplies no physical input uncertainty.
"""
from fractions import Fraction
from typing import Sequence


def _rational(value) -> Fraction:
    if isinstance(value, bool) or not isinstance(value, (int, str, Fraction)):
        raise ValueError('choose exact int/string/Fraction input semantics')
    try:
        return Fraction(value)
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError('finite rational required') from exc


def _family(endpoints, N, Rmax):
    try:
        if len(endpoints) != 2 or any(len(m) != 2 or any(len(row) != 2 for row in m) for m in endpoints):
            raise ValueError('exactly two 2x2 endpoint matrices required')
        matrices = tuple(tuple(tuple(_rational(x) for x in row) for row in m) for m in endpoints)
    except TypeError as exc:
        raise ValueError('two matrix endpoints required') from exc
    for m in matrices:
        if m[0][0] <= 0 or m[1][1] <= 0 or m[0][1] > 0 or m[1][0] > 0:
            raise ValueError('positive diagonals and nonpositive off-diagonals required')
    n, r = _rational(N), _rational(Rmax)
    if n < 0 or r < 0:
        raise ValueError('nonnegative density and rate required')
    return matrices, n, r


def least_witness(endpoints, N, Rmax) -> tuple[Fraction, Fraction]:
    """Return the componentwise least constant nonnegative storage vector.

    Raises ValueError when the declared sufficient slack s>0 is unavailable.
    Such refusal is not a theorem that no other certificate exists.
    """
    matrices, n, r = _family(endpoints, N, Rmax)
    k = max(-m[1][0] / m[0][0] for m in matrices)
    s = min(m[1][1] + m[0][1] * k for m in matrices)
    if s <= 0:
        raise ValueError('positive robust slack unavailable in this construction')
    w2 = n * r / (s + r)
    return k * w2, w2


def corner_slacks(endpoints, N, Rmax, w) -> list[tuple[Fraction, Fraction]]:
    """Return M^T w-r at all four endpoint/rate corners, retaining negatives."""
    matrices, n, rmax = _family(endpoints, N, Rmax)
    if len(w) != 2:
        raise ValueError('two storage weights required')
    w1, w2 = map(_rational, w)
    if min(w1, w2) < 0:
        raise ValueError('nonnegative storage required')
    return [(m[0][0]*w1 + m[1][0]*w2,
             m[0][1]*w1 + (m[1][1]+r)*w2 - n*r)
            for m in matrices for r in (Fraction(0), rmax)]


def signed_bound(w, intervals) -> tuple[Fraction, Fraction]:
    """Enclose the signed accumulated output for an initial component box.

    Assumes w was certified against the *same future law*. No cancellation
    sharper than positive/negative-part decomposition is asserted.
    """
    try:
        if len(w) != 2 or len(intervals) != 2 or any(len(row) != 2 for row in intervals):
            raise ValueError('two weights and two ordered intervals required')
        weights = tuple(map(_rational, w))
        box = tuple(tuple(map(_rational, row)) for row in intervals)
    except TypeError as exc:
        raise ValueError('two weights and two ordered intervals required') from exc
    if min(weights) < 0 or any(lo > hi for lo, hi in box):
        raise ValueError('nonnegative weights and ordered bounds required')
    lo = -sum(v * max(-a, 0) for v, (a, b) in zip(weights, box))
    hi = sum(v * max(b, 0) for v, (a, b) in zip(weights, box))
    return lo, hi
