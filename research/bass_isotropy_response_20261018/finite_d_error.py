"""S6a: finite-d angular error of frozen positive birth rules (theory + certificate).

Dimensionless, non-tilted LRS Bianchi I. mu is the birth source-frame angle,
d=b(x)-b(u). For K(d,mu)=D(d,mu)-A_iso(d)R(d,mu) and any positive normalized
rule alpha, the exact identity

    A_alpha(d)-A_iso(d) = <K>_alpha / F_alpha = sum_{l>=2 even} k_l(d) M_l / F_alpha

separates the rule (moments M_l) from the physics kernel (k_l). See S6_THEORY_KO.md.
Nothing here re-optimizes weights or touches native/spectral owners.
"""
from __future__ import annotations
from functools import lru_cache
import math
import mpmath as mp

ALGORITHM_ID = 'BASS_S6A_FINITE_D_CERTIFICATE_V1'
DPS = 30
# Non-interval 30-digit evaluation of k_l, M_l, F: absolute allowance added to
# every bound; test_s6 cross-checks k_l against 40 digits far below this.
ARITH_FLOOR = 1e-25


def rho(d: float) -> float:
    """Bernstein-ellipse parameter of the nearest kernel branch point in mu.

    R^2=e^{2d}+(e^{-4d}-e^{2d})mu^2 vanishes at mu_s^2=1/(1-e^{-6d}); for both
    signs of d this lies on E_rho with rho=sqrt(coth(3|d|/2)). d=0 is entire.
    """
    if not math.isfinite(d):
        raise ValueError('S6A_D_DOMAIN')
    if d == 0:
        return math.inf
    return math.sqrt(1/math.tanh(1.5*abs(d)))


def rho_star(b: float, d: float) -> float:
    """Analyticity parameter for the GL-mapped LRS rule born at b, read at b+d.

    The LRS source rule is the exact pushforward dmu=dm/R(b,m)^3 of uniform GL
    nodes m; by the cocycle R(d,mu(m))R(b,m)=R(b+d,m) the integrand singularities
    in m are those of R(b,.) and R(b+d,.).
    """
    return min(rho(b), rho(b+d))


def _ctx(d):
    d = mp.mpf(d)
    e2, e4 = mp.e**(2*d), mp.e**(-4*d)
    def R(mu):
        return mp.sqrt(e2*(1-mu*mu)+e4*mu*mu)
    def D(mu):
        return (e4*mu*mu-e2*(1-mu*mu)/2)/R(mu)
    return d, e2, e4, R, D


def iso_reference(d: float) -> dict:
    """Continuum F, G, A at DPS digits (even integrands, branch point off [-1,1])."""
    with mp.workdps(DPS):
        _, _, _, R, D = _ctx(d)
        F = mp.quad(R, [0, 0.5, 1]); G = mp.quad(D, [0, 0.5, 1])
        return {'F': F, 'G': G, 'A': G/F}


def kernel_coefficients(d: float, lmax: int) -> dict:
    """Legendre coefficients (even l<=lmax) of R, D and K=D-A_iso R in mu.

    c_l=(2l+1)/2 int_{-1}^1 f P_l = (2l+1) int_0^1 f P_l for even f. k_0=0 exactly.
    """
    if isinstance(lmax, bool) or not isinstance(lmax, int) or not 2 <= lmax <= 400:
        raise ValueError('S6A_LMAX_DOMAIN')
    with mp.workdps(DPS):
        ref = iso_reference(d)
        _, _, _, R, D = _ctx(d)
        r, g, k = {}, {}, {}
        for l in range(0, lmax+1, 2):
            pts = [0, 0.25, 0.5, 0.75, 1] if l > 20 else [0, 0.5, 1]
            r[l] = (2*l+1)*mp.quad(lambda m: R(m)*mp.legendre(l, m), pts)
            g[l] = (2*l+1)*mp.quad(lambda m: D(m)*mp.legendre(l, m), pts)
            k[l] = g[l]-ref['A']*r[l]
        return {'d': d, 'reference': ref, 'r': r, 'g': g, 'k': k}


def coefficient_bound(d: float, a_iso: float, rho_p: float) -> float:
    """Constant C with |k_n|<=C sqrt(2n+1) rho'^{-n} on E_rho', 1<rho'<rho(d).

    |R^2|>=|c|(a_d-a')^2 by the confocal-ellipse distance a_d-a' (elliptic
    coordinates: |dmu|>=sinh(xi)dxi), |mu|<=a'. Chebyshev |c_k|<=2M rho'^{-k}
    and int|P_n|<=2/sqrt(2n+1) give C=2M/(1-1/rho').
    """
    rd = rho(d)
    if d == 0 or not 1 < rho_p < rd:
        raise ValueError('S6A_ELLIPSE_DOMAIN')
    e2, e4 = math.exp(2*d), math.exp(-4*d)
    c = abs(e4-e2)
    ad, ap = (rd+1/rd)/2, (rho_p+1/rho_p)/2
    r2min = c*(ad-ap)**2
    r2max = e2+c*ap*ap
    nmax = e2/2+(e4+e2/2)*ap*ap
    M = nmax/math.sqrt(r2min)+abs(a_iso)*math.sqrt(r2max)
    # upward margin for the binary64 evaluation of M
    M *= 1+1e-12
    return 2*M/(1-1/rho_p)


@lru_cache(maxsize=256)
def tail_bound(d: float, a_iso: float, lcut: int) -> dict:
    """Rigorous bound on sum_{even n>lcut}|k_n| (parity: odd n vanish exactly)."""
    if d == 0:
        return {'tail': 0.0, 'rho_prime': None}
    rd = rho(d); best = None
    for s in [0.05*i for i in range(1, 20)]:
        rp = 1+(rd-1)*s
        C = coefficient_bound(d, a_iso, rp)
        total, n = 0.0, lcut+2 if lcut % 2 == 0 else lcut+1
        while True:
            term = C*math.sqrt(2*n+1)*rp**(-n)
            total += term
            if term < 1e-40*max(total, 1e-300) or n > 200000:
                break
            n += 2
        # remaining even terms: successive ratio <= q, a geometric majorant
        q = math.sqrt((2*n+5)/(2*n+1))*rp**-2
        if q >= 1:
            continue
        total += term*q/(1-q)
        total *= 1+1e-12
        if best is None or total < best['tail']:
            best = {'tail': total, 'rho_prime': rp}
    if best is None:
        raise ArithmeticError('S6A_TAIL_BOUND')
    return best


def rule_moments(mu, w, lmax: int) -> dict:
    """DPS-digit Legendre moments of the stored binary64 rule (exact inputs)."""
    with mp.workdps(DPS):
        mus = [mp.mpf(float(x)) for x in mu]; ws = [mp.mpf(float(x)) for x in w]
        total = mp.fsum(ws)
        out = {0: mp.mpf(1)}
        pm = [mp.mpf(1)]*len(mus); p = list(mus)
        for l in range(2, lmax+1):
            nxt = [((2*l-1)*m*a-(l-1)*b)/l for m, a, b in zip(mus, p, pm)]
            pm, p = p, nxt
            if l % 2 == 0:
                out[l] = mp.fsum(wi*pi for wi, pi in zip(ws, p))/total
        return out


def rule_F(d: float, mu, w):
    with mp.workdps(DPS):
        _, _, _, R, _ = _ctx(d)
        ws = [mp.mpf(float(x)) for x in w]
        return mp.fsum(wi*R(mp.mpf(float(m))) for wi, m in zip(ws, mu))/mp.fsum(ws)


def certificate(d: float, mu, w, coeffs: dict, moments: dict) -> dict:
    """Series value, direct value and bounds of A_alpha(d)-A_iso(d), all in mp.

    bound: |series| + tail/F + floor (uses the rule's own series; consistency only).
    abs_bound: sum_l |k_l||M_l|/F + tail/F + floor (no sign cancellation).
    low_abs[m]: sum_{2<=l<=2m}|k_l||M_l|, used with constraint_only_guarantee
    to test (S6.4) on constrained rules without their high moments.
    """
    with mp.workdps(DPS):
        lcut = max(coeffs['k'])
        ref = coeffs['reference']
        F = rule_F(d, mu, w)
        _, _, _, R, D = _ctx(d)
        ws = [mp.mpf(float(x)) for x in w]; tot = mp.fsum(ws)
        direct = mp.fsum(wi*(D(mp.mpf(float(m)))-ref['A']*R(mp.mpf(float(m))))
                         for wi, m in zip(ws, mu))/tot/F
        terms = {l: coeffs['k'][l]*moments[l]/F for l in coeffs['k'] if l >= 2}
        series = mp.fsum(terms.values())
        tail = mp.mpf(tail_bound(d, float(ref['A']), lcut)['tail'])
        Fmin = min(math.exp(d), math.exp(-2*d))  # min_mu R
        floor = mp.mpf(ARITH_FLOOR)
        abs_sum = mp.fsum(abs(coeffs['k'][l]*moments[l]) for l in coeffs['k'] if l >= 2)
        low_abs = {m: mp.fsum(abs(coeffs['k'][l]*moments[l]) for l in coeffs['k'] if 2 <= l <= 2*m)
                   for m in (1, 2)}
        return {'direct': direct, 'series': series, 'terms': terms,
                'tail_bound': tail/F, 'tail_bound_rule_free': tail/Fmin,
                'bound': abs(series)+tail/F+floor,
                'abs_bound': (abs_sum+tail)/F+floor,
                'low_abs': low_abs, 'F': F, 'Fmin': Fmin}


def constraint_only_guarantee(d: float, coeffs: dict, m: int) -> float:
    """Worst case over positive rules with M_2=...=M_2m=0 and unknown |M_l|<=1.

    sum_{l>2m}|k_l|/min R. This is all that moment constraints alone guarantee.
    """
    if d == 0:
        return 0.0
    lcut = max(coeffs['k'])
    s = sum(abs(float(coeffs['k'][l])) for l in coeffs['k'] if 2*m < l)
    s += tail_bound(d, float(coeffs['reference']['A']), lcut)['tail']+ARITH_FLOOR
    return s/min(math.exp(d), math.exp(-2*d))


def required_constraint_order(d: float, eps: float, coeffs: dict) -> int | None:
    """Smallest m such that M_2..M_2m=0 alone guarantee |A_alpha-A_iso|<=eps."""
    for m in range(1, max(coeffs['k'])//2):
        if constraint_only_guarantee(d, coeffs, m) <= eps:
            return m
    return None


def predicted_refinement_n(b: float, d: float, eps: float, c: float = 1.0) -> float:
    """A-priori rays for E~c rho*^{-2n}<=eps (rate derived, prefactor c fitted)."""
    rs = rho_star(b, d)
    if math.isinf(rs):
        return 0.0
    return math.log(c/eps)/(2*math.log(rs))
