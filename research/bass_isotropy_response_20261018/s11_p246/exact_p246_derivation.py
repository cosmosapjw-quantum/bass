"""Independent exact arithmetic checks for the new BASS P246 construction.

No project projector, scientific history, solver, or completed campaign is called.
The cubic-facet oracle is checked against independent exhaustive tetrahedron
barycentric coordinates on small fixed rational supports.
"""
from fractions import Fraction as F
from itertools import combinations
from math import factorial
from pathlib import Path
import hashlib
import json
import platform
import time


def add(a, b):
    c = [F(0)] * max(len(a), len(b))
    for i, x in enumerate(a):
        c[i] += x
    for i, x in enumerate(b):
        c[i] += x
    while len(c) > 1 and c[-1] == 0:
        c.pop()
    return c


def scale(a, k):
    return [x * k for x in a]


def mul(a, b):
    c = [F(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            c[i + j] += x * y
    return c


def exact_solve(a, b):
    """Independent rational Gaussian elimination with pivoting."""
    a = [list(row) + [rhs] for row, rhs in zip(a, b)]
    n = len(b)
    for j in range(n):
        pivot = next(i for i in range(j, n) if a[i][j])
        a[j], a[pivot] = a[pivot], a[j]
        divisor = a[j][j]
        a[j] = [x / divisor for x in a[j]]
        for i in range(n):
            if i != j:
                q = a[i][j]
                a[i] = [x - q * y for x, y in zip(a[i], a[j])]
    return [row[-1] for row in a]


def cubic_expectation(a, b, c):
    return F(1, 7) - (a + b + c) / 5 + (a*b + a*c + b*c) / 3 - a*b*c


def facets(zs):
    z = sorted(zs)
    return ([cubic_expectation(z[0], z[i], z[i+1])
             for i in range(1, len(z)-1)]
            + [-cubic_expectation(z[i], z[i+1], z[-1])
               for i in range(len(z)-2)])


def barycentric_oracle(zs):
    """All LP vertices have <=4 positive masses, independently of facet form."""
    covered = set()
    feasible = 0
    for idx in combinations(range(len(zs)), 4):
        z = [zs[i] for i in idx]
        w = exact_solve([[zz**k for zz in z] for k in range(4)],
                        [F(1, 2*k+1) for k in range(4)])
        if all(ww >= 0 for ww in w):
            feasible += 1
            covered.update(i for i, ww in zip(idx, w) if ww > 0)
    return {'feasible_tetrahedra': feasible,
            'covered_vertices': sorted(covered),
            'strict_interior': len(covered) == len(zs)}


def main():
    started = time.perf_counter()
    checks = []
    # Independent Legendre recurrence in mu followed by even-z conversion.
    polynomials = [[F(1)], [F(0), F(1)]]
    for n in range(1, 10):
        polynomials.append(scale(add(scale([F(0)] + polynomials[n], 2*n+1),
                                     scale(polynomials[n-1], -n)), F(1, n+1)))
    p_even = [polynomials[2*k][::2] for k in range(6)]
    r = [[F(1)]]
    for n in range(1, 6):
        c = [F(2**n, factorial(n)), F((-4)**n-2**n, factorial(n))]
        for k in range(1, n):
            c = add(c, scale(mul(r[k], r[n-k]), -1))
        r.append(scale(c, F(1, 2)))
    derivative_records = {}
    expected = {
        3: [F(-96,35), F(200,77), F(-43632,5005), F(-864,77), F(1728,143)],
        4: [F(-320,77), F(4528,143), F(10080,143), F(-116640,1309),
            F(-172800,2717), F(3265920,46189)]}
    for n in [3, 4]:
        derivative = scale(r[n+1], F(-factorial(n+1), 2))
        remainder = derivative[:]
        coefficients = [F(0)] * (n+2)
        for k in range(n+1, -1, -1):
            c = remainder[k] / p_even[k][k]
            coefficients[k] = c
            remainder = add(remainder, scale(p_even[k], -c))
            remainder += [F(0)] * (n+2-len(remainder))
        checks.append({'id': f'D{n}_legendre', 'pass': coefficients == expected[n]})
        checks.append({'id': f'D{n}_pole', 'pass': sum(derivative) == (-2)**n})
        checks.append({'id': f'D{n}_equator', 'pass': derivative[0] == F(-1, 2)})
        derivative_records[str(n)] = {
            'polynomial_z': list(map(str, derivative)),
            'legendre_P0_to_P2n2': list(map(str, coefficients))}

    # Divide G(d) by F(d) independently, using the exact recurrence F'=-2G.
    # Coefficients are vectors [constant, M8, M10], only linear moments occur
    # through d4 after imposing M2=M4=M6=0.
    g1, g2 = F(-8,5), F(8,7)
    f2, f3 = F(8,5), F(-16,21)
    a3 = [expected[3][0]/6 - g1*f2, expected[3][4]/6, F(0)]
    a4 = [expected[4][0]/24 - g2*f2 - g1*f3,
          expected[4][4]/24, expected[4][5]/24]
    checks.append({'id': 'normalized_A_d3', 'pass': a3 == [F(368,175),F(288,143),F(0)]})
    checks.append({'id': 'normalized_A_d4', 'pass': a4 == [F(-248,77),F(-7200,2717),F(136080,46189)]})

    exact_mu = [F(0), F(1,2), F(3,4), F(1)]
    exact_z = [m*m for m in exact_mu]
    exact_mass = [F(286,945),F(32,105),F(2048,6615),F(61,735)]
    checks.append({'id': 'dyadic_control_positive', 'pass': all(w>0 for w in exact_mass)})
    for k in range(4):
        value = sum(w*z**k for w,z in zip(exact_mass,exact_z))
        checks.append({'id':f'dyadic_control_moment_z{k}', 'pass': value == F(1,2*k+1)})

    # New mathematical controls, not physical source/history campaign points.
    fixed_supports = [list(c) for c in combinations([F(0),F(1,4),F(1,2),F(3,4),F(1)],4)]
    fixed_supports += [[F(0),F(1,4),F(1,2),F(3,4),F(1)],
                      [F(0),F(1,2),F(3,4),F(7,8)],
                      [F(0),F(1,8),F(1,4),F(1,2),F(3,4),F(1)],
                      [F(0),F(1,4),F(3,8),F(1,2),F(3,4),F(1)],
                      [F(0),F(1,4),F(1,2),F(5,8),F(3,4),F(1)],
                      [F(0),F(1,4),F(1,2),F(3,4),F(7,8),F(1)]]
    geometry_records = []
    for n,mus in enumerate(fixed_supports):
        zs=[m*m for m in mus]
        slacks=facets(zs)
        oracle=barycentric_oracle(zs)
        ok=all(s>0 for s in slacks)==oracle['strict_interior']
        checks.append({'id':f'facet_barycentric_control_{n}', 'pass':ok})
        geometry_records.append({'mu_nonnegative':list(map(str,mus)),
                                 'facet_slacks':list(map(str,slacks)), **oracle})
    negative_z=[F(0),F(1,16),F(1,4),F(1)]
    p24_lower=max((a+b)/3-a*b for a,b in zip(negative_z,negative_z[1:]))
    checks.append({'id':'P24_feasible_P246_infeasible_control',
                   'pass': F(1,5)-p24_lower==F(1,30)
                           and min(facets(negative_z))==F(-1,42)})
    output={'unit':'S11_P246_INDEPENDENT_THEORY',
            'status':'PASS_SCOPED' if all(c['pass'] for c in checks) else 'FAIL',
            'method':'Fraction polynomial recurrence and independent tetrahedron barycentric enumeration',
            'python':platform.python_version(),
            'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'elapsed_s':time.perf_counter()-started,
            'checks':checks,'checks_passed':sum(c['pass'] for c in checks),
            'checks_total':len(checks),'derivatives':derivative_records,
            'P246_A_d3':list(map(str,a3)),'P246_A_d4':list(map(str,a4)),
            'geometry_controls':geometry_records,
            'completed_project_campaigns_called':0,
            'scope':'Exact symbolic identities and finite-support geometry; not a continuum/native-history acceptance.'}
    target=Path(__file__).with_name('EXACT_DERIVATION_CHECKS.json')
    target.write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps({'status':output['status'],'checks':len(checks),
                      'elapsed_s':output['elapsed_s'],'output':str(target)}))
    if output['status']!='PASS_SCOPED':
        raise SystemExit(1)


if __name__=='__main__':
    main()
