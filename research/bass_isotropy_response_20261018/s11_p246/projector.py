"""S11 positive fixed-support birth projection and exact binary64 certificate.

This independent standard-library reference uses Decimal dual optimization and
Fraction certificates. It never imports or changes the historical P24 solver.
Only a newly declared isotropic birth can call project_birth; the returned tuple
is new data. Existing radiation stock and all spectral owners are outside this API.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal as D, localcontext
from fractions import Fraction as Q
import hashlib
import math
import struct

EXACT_GATE = Q(3, 10**15)
ALGORITHM_ID = "BASS_LRS_NEW_BIRTH_KL_P246_DECIMAL_V1"


class ProjectionError(ValueError):
    def __init__(self, status, details=None):
        super().__init__(status)
        self.status, self.details = status, details


def array_digest(values):
    return hashlib.sha256(b"".join(struct.pack("<d", x) for x in values)).hexdigest()


def validate_input(mu, prior, order, declared_isotropic_birth):
    if declared_isotropic_birth is not True:
        raise ProjectionError("NOT_ISOTROPIC_BIRTH")
    m, q = tuple(map(float, mu)), tuple(map(float, prior))
    if type(order) is not int or order not in (4, 6):
        raise ProjectionError("ORDER_DOMAIN")
    if not 2 <= len(m) <= 4096 or len(q) != len(m):
        raise ProjectionError("ANGULAR_INPUT_SHAPE")
    if any(not math.isfinite(x) or abs(x) > 1 for x in m):
        raise ProjectionError("ANGULAR_INPUT_DOMAIN")
    if any(not math.isfinite(x) or x <= 0 for x in q):
        raise ProjectionError("PRIOR_POSITIVITY_DOMAIN")
    if any(a >= b for a, b in zip(m, m[1:])):
        raise ProjectionError("ANGULAR_ORDER_DOMAIN")
    if any(x != -y for x, y in zip(m, m[::-1])):
        raise ProjectionError("REFLECTION_SOURCE_REQUIRED")
    if q != q[::-1]:
        raise ProjectionError("REFLECTION_PRIOR_REQUIRED")
    return m, q


def legendre(x, ell):
    """Recurrence works independently in Fraction and Decimal arithmetic."""
    a, b = x * 0 + 1, x
    if ell == 0:
        return a
    for n in range(1, ell):
        a, b = b, ((2*n + 1)*x*b - n*a)/(n + 1)
    return b


def solve_linear(matrix, rhs):
    """Small pivoted elimination; supports exact Fraction and Decimal scalars."""
    n = len(rhs)
    aug = [list(row) + [rhs[i]] for i, row in enumerate(matrix)]
    for col in range(n):
        p = max(range(col, n), key=lambda j: abs(aug[j][col]))
        if not aug[p][col]:
            raise ProjectionError("SINGULAR_COVARIANCE")
        aug[col], aug[p] = aug[p], aug[col]
        scale = aug[col][col]
        aug[col] = [v/scale for v in aug[col]]
        for row in range(n):
            if row != col:
                factor = aug[row][col]
                aug[row] = [v - factor*w for v, w in zip(aug[row], aug[col])]
    return [row[-1] for row in aug]


def _qrec(x):
    return {"exact": str(x), "value": float(x)}


def support_feasibility(mu, order=6):
    """Exact moment-curve facets, on exact real values of the supplied floats.

    Squaring Fraction(mu) is deliberate: Fraction(mu*mu) has different semantics.
    This predicate does not use the final numerical moment tolerance.
    """
    if type(order) is not int or order not in (4, 6):
        raise ProjectionError("ORDER_DOMAIN")
    if not mu or any(not math.isfinite(float(x)) or abs(float(x)) > 1 for x in mu):
        raise ProjectionError("ANGULAR_INPUT_DOMAIN")
    z = sorted({Q(float(x))**2 for x in mu})
    degree, n = order//2, len(z)
    target = [Q(1, 2*k + 1) for k in range(degree + 1)]
    facets = []
    rec = {"order": order, "distinct_z": n, "z_min": _qrec(z[0]),
           "z_max": _qrec(z[-1]), "semantics": "Fraction(binary64_mu)**2"}
    if n <= degree:
        mass = solve_linear([[x**k for x in z] for k in range(n)], target[:n])
        mismatch = [sum((w*x**k for w, x in zip(mass, z)), Q(0))-target[k]
                    for k in range(n, degree + 1)]
        if any(mismatch):
            status = "INFEASIBLE_AFFINE_SUPPORT"
        elif any(w < 0 for w in mass):
            status = "INFEASIBLE_SUPPORT"
        elif any(w == 0 for w in mass):
            status = "BOUNDARY_ONLY"
        else:
            status = "POSITIVE_RELATIVE_INTERIOR"
        rec.update(status=status, masses=[_qrec(w) for w in mass],
                   compatibility_residuals=[_qrec(x) for x in mismatch])
        return rec
    if order == 4:
        t, v = target[1:]
        for i, (a, b) in enumerate(zip(z, z[1:])):
            facets.append(("lower", [i, i+1], v-(a+b)*t+a*b))
        facets.append(("upper", [0, n-1], (z[0]+z[-1])*t-z[0]*z[-1]-v))
    else:
        def j(a, b, c):
            return target[3]-(a+b+c)*target[2]+(a*b+a*c+b*c)*target[1]-a*b*c
        for i in range(1, n-1):
            facets.append(("lower", [0, i, i+1], j(z[0], z[i], z[i+1])))
        for i in range(n-2):
            facets.append(("upper", [i, i+1, n-1], -j(z[i], z[i+1], z[-1])))
    slack = min(f[2] for f in facets)
    status = "STRICT_INTERIOR" if slack > 0 else ("BOUNDARY_ONLY" if slack == 0 else "INFEASIBLE_SUPPORT")
    rec.update(status=status, minimum_slack=_qrec(slack), facets=[
        {"kind": name, "indices": indices, "slack": _qrec(value)}
        for name, indices, value in facets])
    return rec


def exact_certificate(mu, weights, order=6):
    """Certify stored binary64 outputs, without renormalizing their weights."""
    if type(order) is not int or order not in (4, 6):
        raise ProjectionError("ORDER_DOMAIN")
    m, w = tuple(map(float, mu)), tuple(map(float, weights))
    if len(m) != len(w) or not 2 <= len(m) <= 4096:
        raise ProjectionError("CERTIFICATE_SHAPE")
    if any(not math.isfinite(x) for x in (*m, *w)):
        raise ProjectionError("CERTIFICATE_NONFINITE")
    if any(abs(x) > 1 for x in m):
        raise ProjectionError("ANGULAR_INPUT_DOMAIN")
    if any(a >= b for a, b in zip(m, m[1:])):
        raise ProjectionError("ANGULAR_ORDER_DOMAIN")
    norm = sum(map(Q, w), Q(0))-1
    moments = {str(l): sum((Q(a)*legendre(Q(x), l) for x, a in zip(m, w)), Q(0))
               for l in range(2, order + 1, 2)}
    residuals = [norm, *moments.values()]
    positive = all(a > 0 for a in w)
    parity = all(x == -y for x, y in zip(m, m[::-1])) and w == w[::-1]
    accepted = positive and parity and all(abs(r) <= EXACT_GATE for r in residuals)
    return {"status": "PASS_SCOPED" if accepted else "FAIL", "gate_exact": str(EXACT_GATE),
            "normalization": _qrec(norm), "moments": {k: _qrec(v) for k, v in moments.items()},
            "max_abs_residual": float(max(map(abs, residuals))),
            "strict_positive": positive, "reflection_exact": parity,
            "minimum_weight": min(w), "mu_sha256": array_digest(m),
            "weight_sha256": array_digest(w)}


@dataclass(frozen=True)
class Projected:
    weights: tuple[float, ...]
    multipliers: tuple[str, ...]
    iterations: int
    decimal_residual: str
    certificate: dict
    support: dict
    kl: str
    prior_sha256: str


def project_birth(mu, prior, *, order=6, declared_isotropic_birth=False, precision=80):
    m, q = validate_input(mu, prior, order, declared_isotropic_birth)
    if not isinstance(precision, int) or not 60 <= precision <= 160:
        raise ProjectionError("DECIMAL_PRECISION_DOMAIN")
    support = support_feasibility(m, order)
    if support["status"] != "STRICT_INTERIOR":
        raise ProjectionError(support["status"], support)
    dim = order//2
    with localcontext() as ctx:
        ctx.prec = precision
        features = [[legendre(D.from_float(x), l) for l in range(2, order+1, 2)] for x in m]
        qd = list(map(D.from_float, q))
        qt = sum(qd)
        logs_q = [(v/qt).ln() for v in qd]
        lam = [D(0)]*dim

        def evaluate(v):
            logs = [logq + sum(a*b for a, b in zip(v, phi)) for logq, phi in zip(logs_q, features)]
            maximum = max(logs)
            e = [(x-maximum).exp() for x in logs]
            total = sum(e)
            weights = [x/total for x in e]
            mean = [sum(w*phi[j] for w, phi in zip(weights, features)) for j in range(dim)]
            return weights, mean, maximum + total.ln()

        target = D(10)**(-(precision//2))
        trace = []
        for iteration in range(101):
            weights, mean, objective = evaluate(lam)
            residual = max(map(abs, mean))
            trace.append(str(residual))
            if residual < target:
                output = tuple(map(float, weights))
                cert = exact_certificate(m, output, order)
                if cert["status"] != "PASS_SCOPED":
                    raise ProjectionError("FINAL_EXACT_CERTIFICATE_FAILED", cert)
                kl = sum(w*(w.ln()-lq) for w, lq in zip(weights, logs_q))
                return Projected(output, tuple(map(str, lam)), iteration, str(residual),
                                 cert, support, str(kl), array_digest(q))
            covariance = [[sum(w*(phi[i]-mean[i])*(phi[j]-mean[j])
                               for w, phi in zip(weights, features))
                           for j in range(dim)] for i in range(dim)]
            direction = solve_linear(covariance, [-r for r in mean])
            slope = sum(a*b for a, b in zip(mean, direction))
            if slope >= 0:
                raise ProjectionError("NON_DESCENT_NEWTON_DIRECTION", {"trace": trace})
            step = D(1)
            for _ in range(100):
                candidate = [a+step*b for a, b in zip(lam, direction)]
                _, trial_mean, trial_objective = evaluate(candidate)
                if (trial_objective <= objective + D("0.0001")*step*slope
                        or (residual < D("1e-20") and max(map(abs, trial_mean)) < residual/2)):
                    lam = candidate
                    break
                step /= 2
            else:
                raise ProjectionError("DECIMAL_LINESEARCH_LIMIT", {"trace": trace})
        raise ProjectionError("DECIMAL_ITERATION_LIMIT", {"trace": trace})


def decimal_ray_response(mu, weights, d, precision=80):
    with localcontext() as ctx:
        ctx.prec = precision
        d = D(str(d))
        ep, ea = (2*d).exp(), (-4*d).exp()
        f, g = D(0), D(0)
        for x, w in zip(mu, weights):
            z, w = D.from_float(float(x))**2, D.from_float(float(w))
            a, b = ep*(1-z), ea*z
            r = (a+b).sqrt()
            f += w*r
            g += w*(b-a/2)/r
        return {"F": str(f), "G": str(g), "A": str(g/f)}


def _decimal_atan(x):
    """Convergent atan with repeated half angle reduction, for real finite x."""
    factor = 1
    while abs(x) > D("0.2"):
        x = x/(1+(1+x*x).sqrt())
        factor *= 2
    xx, term, total = -x*x, x, x
    for k in range(1, 10000):
        term *= xx
        updated = total + term/(2*k+1)
        if updated == total:
            return factor*total
        total = updated
    raise ProjectionError("REFERENCE_ATAN_LIMIT")


def decimal_continuum_response(d, precision=80):
    """Independent exact integral form from S3, evaluated with Decimal arithmetic.

    F=e^d(sqrt(1+kappa)+J)/2, J=asinh(sqrt(kappa))/sqrt(kappa)
    or asin(sqrt(-kappa))/sqrt(-kappa), kappa=e^(-6d)-1.
    This is an angular reference for factorized collisionless radiation only.
    """
    with localcontext() as ctx:
        ctx.prec = precision
        d = D(str(d))
        if not d.is_finite() or abs(d) > 5:
            raise ProjectionError("REFERENCE_STRAIN_DOMAIN")
        if d == 0:
            return {"F": "1", "G": "0", "A": "0"}
        k = (-6*d).exp()-1
        r = (1+k).sqrt()
        if k > 0:
            s = k.sqrt()
            j = (s+r).ln()/s
        else:
            s = (-k).sqrt()
            j = _decimal_atan(s/r)/s
        f = d.exp()*(r+j)/2
        k2 = (r-j)/(2*k)
        g = d.exp()*(-j/2+(D("1.5")+k)*k2)
        return {"F": str(f), "G": str(g), "A": str(g/f)}


def response_taylor(mu, weights, max_power=4):
    """Exact Taylor coefficients of normalized G/F for actual stored float data.

    Includes accepted nonzero lower moments. It uses polynomial-series division,
    not any asymptotic P246 formula or numerical finite difference.
    """
    f = [Q(0)]*(max_power+2)
    for x, w in zip(mu, weights):
        z, w = Q(float(x))**2, Q(float(w))
        r = [Q(1)]
        for n in range(1, max_power+2):
            sn = (Q(2**n)*(1-z)+Q((-4)**n)*z)/math.factorial(n)
            r.append((sn-sum((r[k]*r[n-k] for k in range(1, n)), Q(0)))/2)
        for n, value in enumerate(r):
            f[n] += w*value
    g = [-Q(n+1, 2)*f[n+1] for n in range(max_power+1)]
    response = []
    for n in range(max_power+1):
        response.append((g[n]-sum((f[k]*response[n-k] for k in range(1, n+1)), Q(0)))/f[0])
    return response
