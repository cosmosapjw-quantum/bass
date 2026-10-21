#!/usr/bin/env python3
"""Independent S7 Einstein/cohort checks; stdlib only, no BASS imports.

Exact sparse polynomial algebra checks the metric normalization and constraint.
80-digit Decimal checks the new donor split and closed-model reference limits.
This is a verification artifact, not an alternative native transport owner.
"""
from __future__ import annotations

from decimal import Decimal as D, getcontext
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json
import math
import platform
import resource
import sys
import time


class P:
    """Tiny exact commutative polynomial ring over Fraction."""

    def __init__(self, value=0):
        if isinstance(value, P):
            self.terms = dict(value.terms)
        elif isinstance(value, dict):
            self.terms = {m: F(c) for m, c in value.items() if c}
        else:
            self.terms = {(): F(value)} if value else {}

    @classmethod
    def var(cls, name):
        return cls({(name,): F(1)})

    def __add__(self, other):
        out = dict(self.terms)
        for m, c in P(other).terms.items():
            out[m] = out.get(m, F(0)) + c
        return P(out)

    __radd__ = __add__

    def __neg__(self):
        return P({m: -c for m, c in self.terms.items()})

    def __sub__(self, other):
        return self + (-P(other))

    def __rsub__(self, other):
        return P(other) + (-self)

    def __mul__(self, other):
        out = {}
        for a, ca in self.terms.items():
            for b, cb in P(other).terms.items():
                m = tuple(sorted(a + b))
                out[m] = out.get(m, F(0)) + ca * cb
        return P(out)

    __rmul__ = __mul__

    def __pow__(self, exponent):
        if type(exponent) is not int or exponent < 0:
            raise ValueError("nonnegative integer powers only")
        result = P(1)
        for _ in range(exponent):
            result = result * self
        return result

    def derivative(self, name):
        out = {}
        for m, c in self.terms.items():
            n = m.count(name)
            if n:
                reduced = list(m)
                reduced.remove(name)
                out[tuple(reduced)] = n * c
        return P(out)

    def substitute(self, substitutions):
        result = P(0)
        for m, c in self.terms.items():
            term = P(c)
            for name in m:
                term = term * substitutions.get(name, P.var(name))
            result += term
        return result

    def encoded(self):
        return {"*".join(m) or "1": str(c) for m, c in sorted(self.terms.items())}

    def __eq__(self, other):
        return self.terms == P(other).terms


def same(name, left, right, rows):
    defect = left - right
    passed = defect == 0
    rows.append({"name": name, "pass": passed,
                 "exact_defect": P(defect).encoded()})
    if not passed:
        raise AssertionError(rows[-1])


def algebra_checks():
    h, y, hd, yd, ed, er, pi, lam, q, w = (
        P.var(v) for v in ("h", "y", "hd", "yd", "Ed", "Er", "Pi", "L", "q", "w"))
    rows = []
    hs = [h - y, h - y, h + 2*y]
    hds = [hd - yd, hd - yd, hd + 2*yd]
    theta, theta_dot = sum(hs), sum(hds)
    sq = sum(v*v for v in hs)
    g00 = sum(hs[i]*hs[j] for i in range(3) for j in range(i+1, 3))
    gii = [dv + theta*v - theta_dot - F(1, 2)*(sq+theta*theta)
           for v, dv in zip(hs, hds)]
    same("mean_expansion", theta, 3*h, rows)
    same("shear_norm_sigma_squared", F(1, 2)*sum((v-h)**2 for v in hs), 3*y*y, rows)
    same("Hamiltonian_from_metric", g00, 3*(h*h-y*y), rows)
    same("directional_Einstein_shear_sign", gii[2]-gii[0], 3*yd+9*h*y, rows)
    same("mean_spatial_Einstein", sum(gii)*F(1, 3), -2*hd-3*h*h-3*y*y, rows)

    # General R00/Raychaudhuri, rather than substitution of the constraint.
    dh = -h*h-2*y*y-F(1, 2)*ed-er+lam
    dy = -3*h*y+pi
    ded = -3*h*ed-q
    der = -4*h*er-2*y*pi+q
    r00 = -theta_dot-sq
    same("Raychaudhuri_from_R00", r00.substitute({"hd": dh}),
         F(3, 2)*ed+3*er-3*lam, rows)
    same("total_energy_transfer_cancels", ded+der,
         -3*h*ed-4*h*er-2*y*pi, rows)
    constraint = h*h-y*y-ed-er-lam
    dot_constraint = 2*h*dh-2*y*dy-ded-der
    same("closed_constraint_dot_plus_2hC", dot_constraint+2*h*constraint, 0, rows)
    leaking_constraint = 2*h*dh-2*y*dy-(-3*h*ed)-der
    same("omitted_donor_identified_leak", leaking_constraint+2*h*constraint, -q, rows)
    event_constraint = constraint.substitute({"Ed": ed-w, "Er": er+w})
    same("impulsive_event_constraint_jump", event_constraint, constraint, rows)

    # Linear radiation limit and the similarity to Lee--Nungesser--Tod Eq. 35.
    matrix = [[F(-1), F(1)], [F(-8, 5), F(0)]]
    lit = [[F(-1), F(3)], [F(-8, 15), F(0)]]
    scale = [F(2), F(6)]  # q=2 Sigma_+, A=6 w_+ for axis 3 parallel.
    for i in range(2):
        for j in range(2):
            same(f"linear_literature_similarity_{i}{j}",
                 P(scale[i]*lit[i][j]/scale[j]), P(matrix[i][j]), rows)
            m2 = sum(matrix[i][k]*matrix[k][j] for k in range(2))
            same(f"linear_characteristic_{i}{j}",
                 P(m2+matrix[i][j]+(F(8, 5) if i == j else 0)), P(0), rows)

    # New S7 consequence of the reused S3 local kernel identity: a stress-
    # isotropic but finite angular rule changes the coupled linear frequency.
    v = P.var("mean_z_squared")
    m4 = (35*v-7)*F(1, 8)
    restoring = P(F(8, 5))-F(36, 35)*m4
    same("finite_rule_restoring_coefficient", restoring, F(5, 2)-F(9, 2)*v, rows)
    same("restoring_positive_support_lower_endpoint", restoring.substitute({"mean_z_squared": P(F(1, 3))}), 1, rows)
    same("restoring_positive_support_upper_endpoint", restoring.substitute({"mean_z_squared": P(F(1, 9))}), 2, rows)
    same("restoring_P24_continuum_value", restoring.substitute({"mean_z_squared": P(F(1, 5))}), F(8, 5), rows)
    # z=(1/6,1/2), weights=(1/2,1/2): S3 counterexample reused as an exact input.
    example_v = (F(1, 6)**2+F(1, 2)**2)/2
    same("restoring_P2_counterexample_value", restoring.substitute({"mean_z_squared": P(example_v)}), F(15, 8), rows)
    kappa = P.var("kappa")
    matrix_general = [[P(-1), P(1)], [-kappa, P(0)]]
    for i in range(2):
        for j in range(2):
            m2 = sum(matrix_general[i][k]*matrix_general[k][j] for k in range(2))
            same(f"finite_rule_characteristic_{i}{j}",
                 m2+matrix_general[i][j]+(kappa if i == j else 0), 0, rows)

    # A sampled exact identity only for the decomposition, not a dynamics test.
    pa, pb, ha, hb = F(7, 11), F(-2, 9), F(13, 10), F(17, 10)
    same("Duhamel_forcing_decomposition", P(pa/ha-pb/hb),
         P((pa-pb)/hb+pa*(1/ha-1/hb)), rows)
    return rows


def kernel(d, mu):
    z = mu*mu
    a = (2*d).exp()*(1-z)
    b = (-4*d).exp()*z
    r = (a+b).sqrt()
    return r, (b-a/2)/r


def cohort(x, b, birth_x, birth_b, birth_energy, mus, weights):
    factor = birth_energy * (-4*(x-birth_x)).exp()
    values = [kernel(b-birth_b, mu) for mu in mus]
    return (factor*sum(w*r for w, (r, _) in zip(weights, values)),
            factor*sum(w*g for w, (_, g) in zip(weights, values)))


def sincos(x):
    sin_term, cos_term = x, D(1)
    sine, cosine = sin_term, cos_term
    for n in range(1, 200):
        sin_term *= -x*x/D((2*n)*(2*n+1))
        cos_term *= -x*x/D((2*n-1)*(2*n))
        sine += sin_term
        cosine += cos_term
        if max(abs(sin_term), abs(cos_term)) < D("1e-85"):
            return sine, cosine
    raise ArithmeticError("Decimal trigonometric series did not converge")


def decimal_checks():
    getcontext().prec = 80
    rows = []
    x, b, h, y = D("0.7"), D("0.2"), D("0.9"), D("0.07")
    sqrt_half = (D(1)/2).sqrt()
    data = [
        # Preserved, physically anisotropic pre-existing axis beam pair.
        (D(0), D("-0.1"), D("0.12"), [D(-1), D(1)], [D(1)/2, D(1)/2]),
        # Manufactured new isotropic birth rule already derived in S3.
        (D("0.4"), D("0.05"), D("0.03"),
         [D(-1), -sqrt_half, D(0), sqrt_half, D(1)],
         [D(1)/30, D(4)/15, D(2)/5, D(4)/15, D(1)/30]),
    ]
    dt = D("1e-12")
    maximum_energy_defect = D(0)
    maximum_gauge_defect = D(0)
    for birth_x, birth_b, energy, mus, weights in data:
        def evaluate(xx, bb, shift=D(0)):
            return cohort(xx, bb+shift, birth_x, birth_b+shift, energy, mus, weights)
        u, p = evaluate(x, b)
        up, _ = evaluate(x+h*dt, b+y*dt)
        um, _ = evaluate(x-h*dt, b-y*dt)
        defect = (up-um)/(2*dt)+4*h*u+2*y*p
        maximum_energy_defect = max(maximum_energy_defect, abs(defect))
        shifted = evaluate(x, b, D("0.375"))
        maximum_gauge_defect = max(maximum_gauge_defect, abs(shifted[0]-u), abs(shifted[1]-p))
        assert all(w > 0 for w in weights)
        assert -D(1)/2 <= p/u <= 1
    assert maximum_energy_defect < D("1e-22")
    assert maximum_gauge_defect == 0
    rows.append({"name": "frozen_cohort_energy_with_anisotropic_old_stock", "pass": True,
                 "central_proper_time_step": str(dt), "absolute_gate": "1e-22",
                 "maximum_absolute_defect": str(maximum_energy_defect)})
    rows.append({"name": "birth_frame_constant_b_gauge", "pass": True,
                 "maximum_absolute_defect": str(maximum_gauge_defect)})

    # Midpoint split: exact continuous dust+isotropic radiation reference.
    end, decay, dust0, radiation0 = D("1.2"), D("0.4"), D("0.7"), D("0.2")
    reference = (-4*end).exp()*(radiation0+decay*dust0*
                 (((1-decay)*end).exp()-1)/(1-decay))
    errors, records = [], []
    for count in (8, 16, 32, 64, 128):
        step = end/count
        radiation = radiation0*(-4*end).exp()
        event_jump_defect = D(0)
        for k in range(count):
            u = (D(k)+D("0.5"))*step
            before = dust0*(-3*u-decay*k*step).exp()
            after = before*(-decay*step).exp()
            born = before-after
            assert before > after > 0 and born > 0
            event_jump_defect = max(event_jump_defect, abs(after+born-before))
            radiation += born*(-4*(end-u)).exp()
        error = radiation-reference
        errors.append(abs(error))
        expected_dust = dust0*(-(3+decay)*end).exp()
        split_dust = dust0*(-3*end-decay*count*step).exp()
        assert split_dust == expected_dust
        assert event_jump_defect < D("1e-75")
        records.append({"birth_count": count, "step": str(step),
                        "radiation_error": str(error),
                        "event_energy_jump_defect": str(event_jump_defect)})
    ratios = [errors[i]/errors[i+1] for i in range(len(errors)-1)]
    assert all(D("3.99") < r < D("4.01") for r in ratios)
    rows.append({"name": "closed_midpoint_birth_second_order_reference", "pass": True,
                 "continuous_reference": str(reference), "gate_error_ratios": ["3.99", "4.01"],
                 "error_ratios": [str(r) for r in ratios], "records": records})

    # A diagnostic trap: lambda=1/2 gives exact isotropic endpoint radiation.
    step, decay = D("0.15"), D("0.5")
    ratio = ((1-decay)/decay) * ((decay*step/2).exp()-(-decay*step/2).exp()) / (
        ((1-decay)*step/2).exp()-(-(1-decay)*step/2).exp())
    assert ratio == 1
    rows.append({"name": "lambda_half_endpoint_superconvergence_trap", "pass": True,
                 "exact_ratio": str(ratio)})

    # Direct residual of the analytic radiation-only linear closed solution.
    omega = 3*D(15).sqrt()/10
    q0, a0 = D("0.001"), D("-0.0002")
    def linear(v):
        ss, cc = sincos(omega*v)
        decay = (-v/2).exp()
        return (decay*(q0*cc+(a0-q0/2)/omega*ss),
                decay*(a0*cc+(a0/2-D(8)/5*q0)/omega*ss))
    step, maximum = D("1e-10"), D(0)
    for v in (D(0), D("0.2"), D("0.8"), D("1.6")):
        qv, av = linear(v)
        qp, ap = linear(v+step)
        qm, am = linear(v-step)
        maximum = max(maximum, abs((qp-qm)/(2*step)+qv-av),
                      abs((ap-am)/(2*step)+D(8)/5*qv))
    assert maximum < D("1e-22")
    rows.append({"name": "radiation_only_linear_analytic_solution", "pass": True,
                 "eigenvalue_real_part": "-1/2", "omega": str(omega),
                 "central_step": str(step), "absolute_gate": "1e-22",
                 "maximum_absolute_ODE_residual": str(maximum)})
    return rows


def main():
    started = time.perf_counter()
    algebra, decimal = algebra_checks(), decimal_checks()
    path = Path(__file__).resolve()
    result = {
        "schema": "bass.s7.independent_coupled_theory_review.v1",
        "status": "PASS_SCOPED",
        "review_scope": "new Einstein/donor/cohort coupled coding contract; no native transport execution",
        "method": "metric directional rates with exact Fraction polynomial algebra and 80-digit Decimal independent limits",
        "implementation_imports": "Python standard library only; no BASS kernel/projector/solver imported",
        "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "command": "python3 evidence_s7/theory_review/independent_coupled_review.py",
        "python": platform.python_version(),
        "decimal_precision": getcontext().prec,
        "exact_algebra_checks": algebra,
        "decimal_checks": decimal,
        "counts": {"exact": len(algebra), "decimal": len(decimal)},
        "wall_seconds": time.perf_counter()-started,
        "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "physical_assumptions": [
            "Non-tilted LRS Bianchi I, signature (-,+,+,+), a_perp=a exp(-b), a_parallel=a exp(2b)",
            "s=dot b; Sigma=sqrt(3)|s|/H, expanding H>0",
            "Pressureless positive donor transfers energy to collisionless new radiation with frozen positive birth weights",
            "Existing physically anisotropic stock is transported without angular reprojection",
            "Manufactured donor amplitude; no identification with MD14 energy budget or production admission",
        ],
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
