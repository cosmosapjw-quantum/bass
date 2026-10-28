"""Exact conditional forcing-to-output bounds; no ODE or source estimator.

Caller supplies a valid whole-domain storage certificate, one common proper-time
clock and density, and nonduplicated L1 forcing records. Unknown is not zero.
"""
from dataclasses import dataclass
from fractions import Fraction as F


def rational(x):
    if isinstance(x, bool) or not isinstance(x, (int, str, F)):
        raise ValueError('explicit integer, decimal/rational string or Fraction required')
    try:
        return F(x)
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError('finite rational required') from exc


def pair(x, nonnegative=False):
    try:
        a, b = map(rational, x)
    except (TypeError, ValueError) as exc:
        raise ValueError('two rational endpoints required') from exc
    if a > b or (nonnegative and a < 0):
        raise ValueError('ordered interval of the stated sign required')
    return a, b


@dataclass(frozen=True)
class Envelope:
    D: object
    N: object
    Rmax: object
    gamma: object
    v: object
    w: object

    def __post_init__(self):
        for name in ('D', 'N', 'Rmax', 'gamma'):
            object.__setattr__(self, name, rational(getattr(self, name)))
        for name in ('v', 'w'):
            try:
                values = tuple(map(rational, getattr(self, name)))
            except TypeError as exc:
                raise ValueError('two state coordinates required') from exc
            if len(values) != 2:
                raise ValueError('two state coordinates required')
            object.__setattr__(self, name, values)
        if (min(self.D, self.N, self.Rmax, *self.v, *self.w) < 0
                or self.gamma <= 0 or self.w[1] > self.N
                or any(a > b for a, b in zip(self.v, self.w))):
            raise ValueError('invalid ordered nonnegative storage certificate')

    def coefficients(self, A, B, port):
        """Kernel bounds on [A,B]; supplied certificate validity is a premise."""
        A, B = rational(A), rational(B)
        if not 0 <= A <= B <= self.D or port not in ('f1', 'f2', 'shared_rate'):
            raise ValueError('invalid common-clock window or forcing port')
        i = 0 if port == 'f1' else 1
        tail = (1 + self.gamma * (self.D - B) / 8) ** -8
        lo = max(F(0), self.v[i] - max(self.v) * tail)
        hi = min(self.w[i], self.N * self.Rmax * (self.D - A))
        if lo > hi:
            raise ValueError('supplied certificate produces inconsistent envelopes')
        return (self.N - hi, self.N - lo) if port == 'shared_rate' else (lo, hi)

    def contribution(self, A, B, port, P, Q):
        """P,Q bound integrated positive/negative masses, not signed net mass."""
        coeff = self.coefficients(A, B, port)
        P, Q = pair(P, True), pair(Q, True)
        if rational(A) == rational(B) and max(*P, *Q) != 0:
            raise ValueError('an L1 forcing cannot have mass on a zero-length window')
        return mass_interval(coeff, P, Q)


def mass_interval(coeff, P, Q):
    L, U = pair(coeff, True)
    Pl, Pu = pair(P, True)
    Ql, Qu = pair(Q, True)
    return L * Pl - U * Qu, U * Pu - L * Ql


def split_net_tv(net, TV):
    net, TV = rational(net), rational(TV)
    if TV < abs(net):
        raise ValueError('total variation must be at least the absolute net mass')
    return (TV + net) / 2, (TV - net) / 2


def combine(base, terms, direct=(0, 0)):
    """Add each distinct forcing once; direct is the integrated g interval."""
    lo, hi = pair(base)
    for term in (*terms, direct):
        a, b = pair(term)
        lo, hi = lo + a, hi + b
    return lo, hi


def sign_budget(base, weights, budgets):
    """Joint sufficient sign bound, not an estimate of the actual errors."""
    lo, hi = pair(base)
    weights, budgets = tuple(map(rational, weights)), tuple(map(rational, budgets))
    if (hi >= 0 or not weights or len(weights) != len(budgets)
            or min(*weights, *budgets) < 0):
        raise ValueError('negative baseline and nonnegative matched budgets required')
    cost = sum((w * b for w, b in zip(weights, budgets)), F(0))
    return {'thresholds': tuple(-hi / w if w else None for w in weights),
            'cost': cost, 'upper': hi + cost,
            'strict_negative': hi + cost < 0}
