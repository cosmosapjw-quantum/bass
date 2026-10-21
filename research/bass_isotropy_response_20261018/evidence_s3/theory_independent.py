#!/usr/bin/env python3
"""Independent S3 evidence: exact rational algebra and Decimal evaluation.

Uses only the Python standard library. It imports no BASS production or
projection code, and changes no runtime source. Write stdout to the adjacent
theory_independent.json to retain a reproducible result.
"""
from __future__ import annotations

from collections import Counter
from decimal import Decimal, localcontext
from fractions import Fraction as F
from itertools import combinations
from math import factorial
import hashlib
import json
from pathlib import Path
import platform


def padd(a, b):
    c = [F(0)] * max(len(a), len(b))
    for i, value in enumerate(a):
        c[i] += value
    for i, value in enumerate(b):
        c[i] += value
    while len(c) > 1 and c[-1] == 0:
        c.pop()
    return c


def pscale(a, factor):
    return [value * factor for value in a]


def pmul(a, b):
    c = [F(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            c[i + j] += x * y
    return c


def peval(poly, z):
    value = F(0)
    for coefficient in reversed(poly):
        value = value * z + coefficient
    return value


def polynomials():
    # R^2 = exp(2d)(1-z)+exp(-4d)z; exact d-series at d=0.
    squared = [[F(2**k, factorial(k)),
                F((-4)**k - 2**k, factorial(k))] for k in range(6)]
    r = [[F(1)]]
    for n in range(1, 6):
        cross = [F(0)]
        for k in range(1, n):
            cross = padd(cross, pmul(r[k], r[n-k]))
        r.append(pscale(padd(squared[n], pscale(cross, -1)), F(1, 2)))
    leg_mu = {0: [F(1)], 1: [F(0), F(1)]}
    for n in range(1, 10):
        leg_mu[n+1] = pscale(padd(
            pscale([F(0)] + leg_mu[n], 2*n+1),
            pscale(leg_mu[n-1], -n)), F(1, n+1))
    leg_z = {n: leg_mu[n][::2] for n in range(0, 11, 2)}
    deriv = [pscale(r[n+1], -F(factorial(n+1), 2)) for n in range(4)]
    coefficients = []
    for polynomial in deriv:
        remainder = polynomial[:]
        decomposition = {}
        for ell in reversed(range(0, 2*len(polynomial), 2)):
            value = remainder[-1] / leg_z[ell][-1]
            decomposition[ell] = value
            remainder = padd(remainder, pscale(leg_z[ell], -value))
        assert remainder == [0]
        coefficients.append(dict(sorted(decomposition.items())))
    expected = [
        {0: F(0), 2: F(1)},
        {0: F(-8, 5), 2: F(-10, 7), 4: F(36, 35)},
        {0: F(16, 7), 2: F(12, 7), 4: F(-216, 77), 6: F(216, 77)},
        {0: F(-96, 35), 2: F(200, 77), 4: F(-43632, 5005),
         6: F(-864, 77), 8: F(1728, 143)},
    ]
    assert coefficients == expected
    continuum = [sum((c / F(2*k+1) for k, c in enumerate(p)), F(0))
                 for p in deriv]
    assert continuum == [F(0), F(-8, 5), F(16, 7), F(-96, 35)]
    return r, leg_z, deriv, coefficients, continuum


def dec(fraction):
    return Decimal(fraction.numerator) / Decimal(fraction.denominator)


def kernel(d, z):
    a = (2*d).exp() * (1-z)
    b = (-4*d).exp() * z
    r = (a+b).sqrt()
    return r, (b-a/2)/r


def decimal_derivative_check(deriv):
    rows = []
    with localcontext() as ctx:
        ctx.prec = 80
        h = Decimal('1e-7')
        for zf in (F(0), F(1, 7), F(1, 3), F(1, 2), F(1)):
            z = dec(zf)
            data = {k: kernel(k*h, z) for k in (-2, -1, 0, 1, 2)}
            finite = [data[0][1],
                      (data[1][1]-data[-1][1])/(2*h),
                      (data[1][1]-2*data[0][1]+data[-1][1])/(h*h),
                      (data[2][1]-2*data[1][1]+2*data[-1][1]-data[-2][1])/(2*h**3)]
            errors = [abs(value-dec(peval(poly, zf)))
                      for value, poly in zip(finite, deriv)]
            # This gate bounds finite-difference truncation in this test only.
            assert max(errors) < Decimal('1e-9')
            conservation = abs((data[1][0]-data[-1][0])/(2*h)+2*data[0][1])
            assert conservation < Decimal('1e-11')
            rows.append({'z': str(zf), 'h': str(h),
                         'absolute_derivative_errors_0_to_3': list(map(str, errors)),
                         'central_R_prime_plus_2D_error': str(conservation)})
    return rows


def hull_status(nodes):
    z = sorted(set(nodes))
    t, v = F(1, 3), F(1, 5)
    if len(z) == 1:
        return 'INFEASIBLE_RANK0'
    if not z[0] < t < z[-1]:
        return 'INFEASIBLE_MEAN'
    upper = (z[0]+z[-1])*t-z[0]*z[-1]
    if len(z) == 2:
        return 'FEASIBLE_RELATIVE_INTERIOR_RANK1' if v == upper else 'INFEASIBLE_RANK1'
    lower = max((a+b)*t-a*b for a, b in zip(z, z[1:]))
    if v < lower:
        return 'INFEASIBLE_LOWER'
    if v > upper:
        return 'INFEASIBLE_UPPER'
    if v == lower or v == upper:
        return 'BOUNDARY_NONNEGATIVE_ONLY'
    return 'FEASIBLE_FULL_INTERIOR'


def independent_simplex_status(nodes):
    # Exhaustive exact 3-point barycentric solutions provide an independent
    # convex-hull check; averaging feasible solutions establishes all-positive
    # support iff every support point occurs positively in at least one.
    z = sorted(set(nodes))
    t, v = F(1, 3), F(1, 5)
    covered = set()
    feasible = False
    for i, j in combinations(range(len(z)), 2):
        a, b = z[i], z[j]
        if a < t < b and v == (a+b)*t-a*b:
            feasible = True
            covered.update((i, j))
    for ids in combinations(range(len(z)), 3):
        values = [z[index] for index in ids]
        weights = []
        for n in range(3):
            a = values[n]
            b, c = [values[k] for k in range(3) if k != n]
            weights.append((v-(b+c)*t+b*c)/((a-b)*(a-c)))
        if all(weight >= 0 for weight in weights):
            feasible = True
            assert sum(weights) == 1
            assert sum(w*x for w, x in zip(weights, values)) == t
            assert sum(w*x*x for w, x in zip(weights, values)) == v
            covered.update(index for index, w in zip(ids, weights) if w > 0)
    return feasible, len(covered) == len(z)


def feasibility_checks():
    grid = [F(k, 10) for k in range(11)]
    counts = Counter()
    for n in range(1, 6):
        for nodes in combinations(grid, n):
            status = hull_status(nodes)
            feasible, positive = independent_simplex_status(nodes)
            assert positive == status.startswith('FEASIBLE_')
            assert feasible == (positive or status == 'BOUNDARY_NONNEGATIVE_ONLY')
            counts[status] += 1
    cases = {
        'rank1_full_positive': [F(0), F(3, 5)],
        'lower_boundary': [F(0), F(3, 5), F(1)],
        'upper_boundary': [F(0), F(3, 10), F(3, 5)],
        'lower_outside': [F(0), F(7, 10), F(1)],
        'upper_outside': [F(0), F(1, 4), F(1, 2)],
    }
    return {'method': 'Fraction hull inequalities vs exhaustive exact barycentric simplex solutions',
            'support_grid': 'z=k/10, k=0..10; all subsets of cardinality1..5',
            'total_supports_checked': sum(counts.values()),
            'counts': dict(sorted(counts.items())),
            'cases': {name: {'z': list(map(str, z)), 'status': hull_status(z)}
                      for name, z in cases.items()}}


def response_examples(leg_z, deriv):
    examples = {
        'P2_only_four_rays': ([F(1, 6), F(1, 2)], [F(1, 2), F(1, 2)]),
        'P2P4_five_rays': ([F(0), F(1, 2), F(1)], [F(2, 5), F(8, 15), F(1, 15)]),
        'P2P4_rank1_three_rays': ([F(0), F(3, 5)], [F(4, 9), F(5, 9)]),
    }
    output = {}
    for name, (z, weights) in examples.items():
        assert all(w > 0 for w in weights) and sum(weights) == 1
        moments = {ell: sum(w*peval(poly, zz) for zz, w in zip(z, weights))
                   for ell, poly in leg_z.items() if ell <= 8}
        g = [sum(w*peval(poly, zz) for zz, w in zip(z, weights)) for poly in deriv]
        assert moments[2] == 0
        a = [g[0], g[1], g[2], g[3]+6*g[1]*g[1]]
        output[name] = {'z': list(map(str, z)), 'group_weights': list(map(str, weights)),
                        'moments': {str(k): str(v) for k, v in moments.items()},
                        'normalized_response_derivatives_0_to_3': list(map(str, a)),
                        'support_status': hull_status(z)}
    assert output['P2_only_four_rays']['moments']['4'] == '-77/288'
    assert output['P2_only_four_rays']['normalized_response_derivatives_0_to_3'][1] == '-15/8'
    assert output['P2P4_five_rays']['moments']['6'] == '-11/80'
    assert output['P2P4_five_rays']['normalized_response_derivatives_0_to_3'][2] == '19/10'
    assert output['P2P4_rank1_three_rays']['moments']['6'] == '-33/100'
    return output


def continuum_response_decimal(d):
    """Independent closed-form isotropic integral at small real d.

    J(k)=integral_0^1(1+k*mu^2)^(-1/2)dmu is evaluated by its absolutely
    convergent binomial series in k, not the d-series used for derivatives.
    """
    if d == 0:
        return Decimal(0)
    k = (-6*d).exp()-1
    assert abs(k) < Decimal('0.5')
    term, j = Decimal(1), Decimal(1)
    for n in range(1, 2000):
        term *= -k * Decimal(2*n-1) / Decimal(2*n)
        add = term / Decimal(2*n+1)
        j += add
        if abs(add) < Decimal('1e-76'):
            break
    else:
        raise AssertionError('CONTINUUM_BINOMIAL_SERIES_NOT_CONVERGED')
    root = (1+k).sqrt()
    f = d.exp()*(root+j)/2
    g = d.exp()*((2*k+3)*root-(4*k+3)*j)/(4*k)
    return g/f


def decimal_response_checks():
    rows = []
    with localcontext() as ctx:
        ctx.prec = 80
        gl = Decimal(30).sqrt()
        examples = {
            'P2_only_four_rays': ([dec(F(1, 6)), dec(F(1, 2))],
                                  [Decimal('0.5'), Decimal('0.5')], 1, F(-11, 40)),
            'P2P4_five_rays': ([Decimal(0), Decimal('0.5'), Decimal(1)],
                               [dec(F(2, 5)), dec(F(8, 15)), dec(F(1, 15))], 2, F(-27, 140)),
            'GL4_b0': ([(15-2*gl)/35, (15+2*gl)/35],
                       [(18+gl)/36, (18-gl)/36], 3, F(-144, 245)),
        }
        for name, (z, weights, order, expected) in examples.items():
            last = None
            for hs in ('0.001', '0.0005', '0.00025'):
                h = Decimal(hs)
                errors = []
                for d in (h, -h):
                    fg = [kernel(d, zz) for zz in z]
                    f = sum(w*pair[0] for w, pair in zip(weights, fg))
                    g = sum(w*pair[1] for w, pair in zip(weights, fg))
                    errors.append(g/f-continuum_response_decimal(d))
                # Symmetric parity removes the following Taylor order.
                coefficient = (errors[0]+(-1)**order*errors[1])/(2*h**order)
                absolute = abs(coefficient-dec(expected))
                if last is not None:
                    assert absolute < last/Decimal('3.9')
                last = absolute
                rows.append({'example': name, 'h': hs, 'leading_order': order,
                             'expected_coefficient': str(expected),
                             'measured_symmetric_coefficient': str(coefficient),
                             'absolute_coefficient_error': str(absolute),
                             'positive_d_response_error': str(errors[0]),
                             'negative_d_response_error': str(errors[1])})
            assert last < Decimal('1e-6')
    return rows


def main():
    r, leg, derivative, coefficients, continuum = polynomials()
    result = {
        'status': 'PASS_SCOPED_INDEPENDENT_THEORY_CHECK',
        'scope': 'fixed-birth positive axisymmetric angular quadrature; no native finite-bin claim',
        'runtime': 'PYTHON_PASS',
        'python_version': platform.python_version(),
        'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'methods': ['exact Fraction square-root recurrence and Legendre recurrence',
                    'independent 80-digit Decimal exp/sqrt central differences',
                    'exact Fraction moment-curve hull vs barycentric enumeration'],
        'D_derivatives_z_monomials': [[str(x) for x in p] for p in derivative],
        'D_derivatives_Legendre': [{str(k): str(v) for k, v in c.items()} for c in coefficients],
        'isotropic_G_derivatives_0_to_3': list(map(str, continuum)),
        'isotropic_A_derivatives_0_to_3': ['0', '-8/5', '16/7', '2208/175'],
        'decimal_derivative_checks': decimal_derivative_check(derivative),
        'decimal_response_checks': decimal_response_checks(),
        'feasibility': feasibility_checks(),
        'exact_response_examples': response_examples(leg, derivative),
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
