#!/usr/bin/env python3
"""Independent S8 algebra and positive-KL derivative checks.

Standard-library Fraction/Decimal only; no BASS, NumPy, SciPy, Rust or ODE import.
This is a bounded derivative verification, not a rerun of an S7 campaign.
"""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal as D, localcontext
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import resource
import time


def dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def solve(matrix, vector):
    a = [list(row)+[v] for row, v in zip(matrix, vector)]
    n = len(a)
    for i in range(n):
        pivot = next(j for j in range(i, n) if a[j][i] != 0)
        a[i], a[pivot] = a[pivot], a[i]
        scale = a[i][i]
        a[i] = [v/scale for v in a[i]]
        for j in range(n):
            if j != i:
                scale = a[j][i]
                a[j] = [x-scale*y for x, y in zip(a[j], a[i])]
    return [row[-1] for row in a]


def feature(mu):
    return [(3*mu**2-1)/2, (35*mu**4-30*mu**2+3)/8]


def feature_b(mu):
    mu_b = -3*mu*(1-mu**2)
    return [3*mu*mu_b, (35*mu**3-15*mu)*mu_b/2]


def three_group_masses(nodes):
    return solve([[Q(1) for _ in nodes], [m*m for m in nodes],
                  [m**4 for m in nodes]], [Q(1), Q(1, 3), Q(1, 5)])


def rational_fixture():
    # Convex mixture of two exact positive three-group rules produces eight
    # strictly positive rays and a nontrivial KL degree of freedom.
    masses = {Q(1, 4): Q(0), Q(1, 2): Q(0), Q(3, 4): Q(0), Q(1): Q(0)}
    for nodes in ([Q(1, 4), Q(1, 2), Q(1)],
                  [Q(1, 4), Q(3, 4), Q(1)]):
        group = three_group_masses(nodes)
        assert all(v > 0 for v in group)
        for mu, w in zip(nodes, group):
            masses[mu] += w/2
    mus = sorted([-m for m in masses]+list(masses))
    alpha = [masses[abs(m)]/2 for m in mus]
    return mus, alpha, [Q(2, 5), Q(-3, 7)]


def implicit_weight_derivative(mu, alpha, lam, include_prior=True,
                               include_moving_target=True):
    f = [feature(m) for m in mu]
    fb = [feature_b(m) for m in mu]
    mean = [dot(alpha, [v[j] for v in f]) for j in range(2)]
    centered = [[v[j]-mean[j] for j in range(2)] for v in f]
    score = [(6*v[0] if include_prior else Q(0))+dot(lam, vb)
             for v, vb in zip(f, fb)]
    sbar = dot(alpha, score)
    covariance = [[dot(alpha, [v[j]*v[k] for v in centered])
                   for k in range(2)] for j in range(2)]
    rhs = [-dot(alpha, [v[j]*(s-sbar) for v, s in zip(centered, score)])
           -(dot(alpha, [v[j] for v in fb]) if include_moving_target else Q(0))
           for j in range(2)]
    dual_b = solve(covariance, rhs)
    alpha_b = [w*(s-sbar+dot(v, dual_b))
               for w, s, v in zip(alpha, score, centered)]
    return alpha_b, dual_b, covariance


def dec(value):
    if isinstance(value, Q):
        return D(value.numerator)/D(value.denominator)
    return D(value)


def kernel(d, mu):
    e, z = (2*d).exp(), (-4*d).exp()
    r = (e*(1-mu*mu)+z*mu*mu).sqrt()
    return r, (z*mu*mu-e*(1-mu*mu)/2)/r


def partials(d, mu):
    e, z = (2*d).exp(), (-4*d).exp()
    w, v = e*(1-mu*mu), z*mu*mu
    r, stress = kernel(d, mu)
    return [-2*stress, -(w*w+14*w*v+4*v*v)/(2*r**3),
            mu*(z-e)/r,
            mu*(e+2*z)/r-stress*mu*(z-e)/r**2]


def positive_kl_at_b(b, mu0, alpha0, lam0):
    # Define a smooth positive prior for which the rational fixture is exactly
    # the KL optimum at b=0. Moving-ray Jacobian is the actual R^-3 family.
    mus, logqs = [], []
    for m, a in zip(mu0, alpha0):
        r, _ = kernel(b, m)
        mus.append(m*(-2*b).exp()/r)
        logqs.append(a.ln()-dot(lam0, feature(m))-3*r.ln())
    f = [feature(m) for m in mus]
    lam = list(lam0)
    for iteration in range(100):
        logs = [q+dot(lam, v) for q, v in zip(logqs, f)]
        shift = max(logs)
        weights = [(v-shift).exp() for v in logs]
        norm = sum(weights)
        alpha = [w/norm for w in weights]
        means = [dot(alpha, [v[j] for v in f]) for j in range(2)]
        if max(map(abs, means)) < D('1e-75'):
            return alpha, mus, lam, iteration, means
        centered = [[v[j]-means[j] for j in range(2)] for v in f]
        covariance = [[dot(alpha, [v[j]*v[k] for v in centered])
                       for k in range(2)] for j in range(2)]
        step = solve(covariance, [-v for v in means])
        lam = [x+y for x, y in zip(lam, step)]
    raise AssertionError('INDEPENDENT_DECIMAL_KL_NOT_CONVERGED')


def main():
    started = time.monotonic()
    exact, numerical = [], []

    def check(name, condition, extra=None):
        if not condition:
            raise AssertionError(name)
        exact.append({'name': name, 'pass': True, **(extra or {})})

    def ncheck(name, error, gate, extra=None):
        if not (error <= gate):
            raise AssertionError(f'{name}: {error} > {gate}')
        numerical.append({'name': name, 'pass': True, 'max_abs_error': str(error),
                          'gate': str(gate), **(extra or {})})

    mu, alpha, lam = rational_fixture()
    f, fb = [feature(m) for m in mu], [feature_b(m) for m in mu]
    ab, lb, cov = implicit_weight_derivative(mu, alpha, lam)
    check('positive_reflection_even_eight_ray_fixture',
          all(w > 0 for w in alpha) and alpha == alpha[::-1])
    check('exact_fixture_normalization', sum(alpha) == 1)
    for j, name in enumerate(['P2', 'P4']):
        check('exact_fixture_'+name, dot(alpha, [v[j] for v in f]) == 0)
    check('covariance_strict_positive_definite',
          cov[0][0] > 0 and cov[0][0]*cov[1][1]-cov[0][1]**2 > 0)
    check('derivative_normalization', sum(ab) == 0)
    check('derivative_reflection_parity', ab == ab[::-1])
    for j, name in enumerate(['P2', 'P4']):
        check('moving_constraint_derivative_'+name,
              dot(ab, [v[j] for v in f])+dot(alpha, [v[j] for v in fb]) == 0)
    no_prior_ab, no_prior_lb, _ = implicit_weight_derivative(mu, alpha, lam, False)
    check('LRS_prior_score_in_constraint_span_cancels_in_alpha_b', ab == no_prior_ab)
    check('LRS_prior_score_only_shifts_dual2_b',
          lb[0] == no_prior_lb[0]-6 and lb[1] == no_prior_lb[1])
    bad_ab, _, _ = implicit_weight_derivative(mu, alpha, lam,
                                              include_moving_target=False)
    defects = [dot(bad_ab, [v[j] for v in f])+dot(alpha, [v[j] for v in fb])
               for j in range(2)]
    check('negative_control_missing_mean_f_b_rejected', any(v != 0 for v in defects),
          {'exact_constraint_defects': [str(v) for v in defects]})

    # Kernel derivative identity after multiplying by R^3, no radical or CAS.
    for w, v in [(Q(3, 2), Q(2, 7)), (Q(0), Q(5, 3)), (Q(9, 5), Q(0))]:
        radicand, numerator = w+v, v-w/2
        chain = (-w-4*v)*radicand+2*numerator*numerator
        stable = -(w*w+14*w*v+4*v*v)/2
        check(f'D_d_rational_identity_W{w}_V{v}', chain == stable)
        check(f'D_d_strict_negative_W{w}_V{v}', stable < 0)

    h, y, ed, er, cosm, stress = Q(6, 5), Q(1, 7), Q(2, 5), Q(3, 8), Q(1, 10), Q(1, 9)
    dh, dy, der, dstress = Q(2, 11), Q(3, 13), Q(5, 17), Q(7, 19)
    hp = (-h*h-2*y*y-ed/2-er+cosm)/h
    yp = -3*y+stress/h
    dhp = (-2-hp/h)*dh-4*y*dy/h-der/h
    dyp = -3*dy+dstress/h-stress*dh/h**2
    derp = -4*der-2*((dy*stress+y*dstress)/h-y*stress*dh/h**2)
    dc = 2*h*dh-2*y*dy-der
    dcp = 2*hp*dh+2*h*dhp-2*yp*dy-2*y*dyp-derp
    check('independent_Raychaudhuri_tangent_constraint_transport', dcp+2*dc == 0)
    check('initial_y0_parameter_constraint_tangent', 2*h*(y/h)-2*y == 0)
    check('birth_event_energy_tangent_zero', sum(ab) == 0)
    check('birth_event_stress_tangent_zero',
          dot(ab, [v[0] for v in f])+dot(alpha, [v[0] for v in fb]) == 0)
    dw = Q(0)
    check('fixed_donor_schedule_event_constraint_jump_zero', -(-dw)-dw == 0)
    check('signed_weight_derivative_is_not_a_negative_physical_weight',
          min(ab) < 0 < max(ab) and min(alpha) > 0)

    with localcontext() as context:
        context.prec = 90
        mud, ad, ld = list(map(dec, mu)), list(map(dec, alpha)), list(map(dec, lam))
        abd = list(map(dec, ab))
        hfd = D('1e-24')
        for d0, m0 in [(D('.2'), D('.31')), (D('-.35'), D('-.73')), (D('.4'), D(0))]:
            pp = partials(d0, m0)
            rplus, dplus = kernel(d0+hfd, m0)
            rminus, dminus = kernel(d0-hfd, m0)
            rmplus, dmplus = kernel(d0, m0+hfd)
            rmminus, dmminus = kernel(d0, m0-hfd)
            fd = [(rplus-rminus)/(2*hfd), (dplus-dminus)/(2*hfd),
                  (rmplus-rmminus)/(2*hfd), (dmplus-dmminus)/(2*hfd)]
            ncheck(f'kernel_partials_d{d0}_mu{m0}', max(abs(a-b) for a, b in zip(pp, fd)),
                   D('1e-43'))
        aw0, moved0, _, _, _ = positive_kl_at_b(D(0), mud, ad, ld)
        ncheck('independent_KL_rational_base_recovery', max(abs(a-b) for a, b in zip(aw0, ad)),
               D('1e-75'))
        rows = []
        for step in [D('.001'), D('.0005'), D('.00025'), D('1e-8')]:
            plus = positive_kl_at_b(step, mud, ad, ld)
            minus = positive_kl_at_b(-step, mud, ad, ld)
            derivative = [(a-b)/(2*step) for a, b in zip(plus[0], minus[0])]
            error = max(abs(a-b) for a, b in zip(derivative, abd))
            rows.append({'step': str(step), 'max_alpha_b_error': str(error),
                         'positive': min(plus[0]+minus[0]) > 0,
                         'max_iterations': max(plus[3], minus[3]),
                         'moment_residual': str(max(map(abs, plus[4]+minus[4])))})
        errors = [D(row['max_alpha_b_error']) for row in rows]
        ratios = [errors[i]/errors[i+1] for i in range(2)]
        ncheck('independent_moving_KL_finite_difference_alpha_b', errors[-1], D('1e-12'),
               {'rows': rows, 'coarse_error_ratios': list(map(str, ratios))})
        ncheck('moving_KL_derivative_second_order_FD', max(abs(r-4) for r in ratios), D('.02'))
        # Existing photons have fixed birth parameters but varying current
        # geometry. Their derivative cannot be set to zero just because stock
        # arrays remain unchanged.
        old_energy_derivative = sum(w*partials(D('.2'), m)[0] for w, m in zip(ad, mud))*D('.1')
        if old_energy_derivative == 0:
            raise AssertionError('OLD_STOCK_CURRENT_GEOMETRY_RESPONSE_MISSING')
        numerical.append({'name': 'old_stock_fixed_distribution_has_current_geometry_response',
                          'pass': True, 'nonzero_derivative': str(old_energy_derivative)})

    record = {
        'schema': 'bass.s8.independent_tangent_checks.v1',
        'utc': datetime.now(timezone.utc).isoformat(), 'status': 'PASS_SCOPED_DERIVATIVE_CHECKS',
        'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'independence': 'Separate standard-library Fraction/90-digit Decimal implementation; no BASS modules, ODE, native transport or S7 test imports.',
        'scientific_scope': 'Kernel and smooth finite positive-KL branch derivatives; manufactured donor sensitivity identities. Does not verify campaign trajectories or native refinement accuracy.',
        'exact_checks': exact, 'decimal_checks': numerical,
        'exact_checks_passed': len(exact), 'decimal_checks_passed': len(numerical),
        'rational_fixture': {'mu': list(map(str, mu)), 'alpha': list(map(str, alpha)),
                             'lambda': list(map(str, lam)), 'alpha_b': list(map(str, ab)),
                             'lambda_b': list(map(str, lb))},
        'wall_seconds': time.monotonic()-started,
        'maxrss_kib_linux': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        'threads': 1, 'old_campaigns_repeated': 0,
        'remaining': ['S8 full tangent finite-difference/conservation/omitted-term campaign',
                      'native extended angular-support implementation and accuracy campaign',
                      'no universal full-input conditioning or continuum/production admission']}
    print(json.dumps(record, indent=2))


if __name__ == '__main__':
    main()
