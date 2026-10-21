"""S6 regression tests: finite-d certificate, rank-one certificate, spectral replica, cohorts."""
from __future__ import annotations
import cmath
import json
import math
from pathlib import Path
import unittest
import numpy as np
import finite_d_error as fde
import rank1_certificate as r1
import spectral_residual as sr
import run_spectral_refinement as rsr
from s6_io import write_json_once
from fractions import Fraction
import tempfile
import source_age as sa
from angular_balance import lrs_rule, project as project2
from angular_p24 import project as project24

HERE = Path(__file__).resolve().parent


def cert(c):
    return {'schema': r1.CERT_SCHEMA, 'z_quadratic': c}


class FiniteD(unittest.TestCase):
    def test_rho_closed_form_matches_branch_point(self):
        for d in (-0.7, -0.2, -0.01, 0.01, 0.2, 0.7):
            ms = cmath.sqrt(1/(1-math.exp(-6*d)))
            rho = max(abs(ms+cmath.sqrt(ms*ms-1)), abs(ms-cmath.sqrt(ms*ms-1)))
            self.assertAlmostEqual(fde.rho(d), rho, places=12)
            e2, e4 = math.exp(2*d), math.exp(-4*d)
            self.assertLess(abs(e2*(1-ms*ms)+e4*ms*ms), 1e-12)
        self.assertTrue(math.isinf(fde.rho(0.0)))

    def test_coefficients_obey_rigorous_bound_and_rate(self):
        for d in (0.2, -0.2):
            c = fde.kernel_coefficients(d, 60); a = float(c['reference']['A'])
            rp = fde.tail_bound(d, a, 60)['rho_prime']; C = fde.coefficient_bound(d, a, rp)
            for l in range(2, 61, 2):
                self.assertLessEqual(abs(float(c['k'][l])), C*math.sqrt(2*l+1)*rp**-l)
            scaled = [abs(float(c['k'][l]))*fde.rho(d)**l for l in range(20, 61, 2)]
            self.assertLess(max(scaled)/min(scaled), 1.5)

    def test_thirty_digit_coefficients_agree_with_forty(self):
        import mpmath as mp
        c30 = fde.kernel_coefficients(0.2, 100)
        old = fde.DPS
        try:
            fde.DPS = 40; c40 = fde.kernel_coefficients(0.2, 100)
        finally:
            fde.DPS = old
        diff = max(abs(c30['k'][l]-c40['k'][l]) for l in c30['k'])
        self.assertLess(float(diff), fde.ARITH_FLOOR*1e-3)

    def test_small_d_matches_s3_p4_slope(self):
        d = 1e-4; c = fde.kernel_coefficients(d, 8)
        self.assertAlmostEqual(float(c['k'][4])/d, 36/35, places=3)
        # D(0)=P2, so k_2(0)=1 and k_2'(0)=g_2'(0)=-10/7 (A r_2=O(d^2)).
        self.assertAlmostEqual((float(c['k'][2])-1)/d, -10/7, places=3)

    def test_identity_and_bound_on_positive_rule(self):
        mu, q = lrs_rule(0.3, 8); w = project2(mu, q).weights
        for d in (-0.2, 0.05):
            c = fde.kernel_coefficients(d, 80); m = fde.rule_moments(mu, w, 80)
            x = fde.certificate(d, mu, w, c, m)
            # truncation at L=80 is bounded by the rigorous tail, not by 30-digit noise
            self.assertLessEqual(abs(float(x['series']-x['direct'])), x['tail_bound']+fde.ARITH_FLOOR)
            self.assertLessEqual(abs(float(x['direct'])), x['bound'])

    def test_constraint_only_guarantee_decreases_by_about_rho_squared(self):
        d = 0.2; c = fde.kernel_coefficients(d, 100)
        g = [fde.constraint_only_guarantee(d, c, m) for m in (2, 3, 4, 5)]
        for a, b in zip(g, g[1:]):
            self.assertTrue(0.6*fde.rho(d)**2 < a/b < 1.6*fde.rho(d)**2)

    def test_domains(self):
        with self.assertRaises(ValueError):
            fde.kernel_coefficients(0.1, 1)
        with self.assertRaises(ValueError):
            fde.coefficient_bound(0.1, 0.0, fde.rho(0.1))
        with self.assertRaises(ValueError):
            fde.rho(math.nan)


class Rank1(unittest.TestCase):
    def test_gl4_certified_equals_gauss_weights(self):
        m, w = np.polynomial.legendre.leggauss(4)
        with self.assertRaises(ArithmeticError):
            project24(m, w)
        x = r1.project_rank1(m, w, cert([3, -30, 35]))
        self.assertLess(np.max(abs(x.weights-w/2)), 1e-15)
        self.assertLessEqual(max(abs(x.residuals)), 3e-15)
        self.assertEqual(x.float_status, 'FEASIBILITY_UNRESOLVED_RANK1')

    def test_zero_ray_support(self):
        m = np.array([-math.sqrt(.6), 0.0, math.sqrt(.6)])
        x = r1.project_rank1(m, np.ones(3), cert(['0', '-3', '5']))
        self.assertTrue(np.allclose(x.weights, [5/18, 4/9, 5/18], rtol=0, atol=2e-16))

    def test_prior_ratio_kept_within_group(self):
        m, w = np.polynomial.legendre.leggauss(4)
        q = np.array([1.0, 3.0, 3.0, 1.0])
        x = r1.project_rank1(m, q, cert([3, -30, 35]))
        self.assertLess(np.max(abs(x.weights-w/2)), 1e-15)

    def test_exact_rejections(self):
        m, w = np.polynomial.legendre.leggauss(4)
        cases = {
            'INFEASIBLE_P24_RANK1_EXACT': [1, -8, 12],         # z=1/6,1/2: M4!=0
            'INFEASIBLE_P24_MEAN_EXACT': [1, -12, 32],         # z=1/8,1/4
            'RANK1_CERT_NOT_TWO_DISTINCT_ROOTS': [1, -4, 4],
            'RANK1_CERT_ROOTS_OUTSIDE_UNIT': [3, -4, 1],       # z=1,3
            'RANK1_CERT_DEGREE': [1, 2, 0],
            'RANK1_CERT_INTEGER': [1.0, -30, 35],
        }
        for tag, c in cases.items():
            with self.subTest(tag=tag):
                with self.assertRaisesRegex(ValueError, tag):
                    r1.project_rank1(m, w, cert(c))
        with self.assertRaisesRegex(ValueError, 'RANK1_CERT_SCHEMA'):
            r1.project_rank1(m, w, {'schema': 'x', 'z_quadratic': [3, -30, 35]})
        with self.assertRaisesRegex(ValueError, 'RANK1_CERT_INTEGER'):
            r1.project_rank1(m, w, cert([True, -30, 35]))

    def test_binding_rejects_perturbed_rays(self):
        m, w = np.polynomial.legendre.leggauss(4)
        p = m.copy(); p[0] -= 1e-9; p[-1] += 1e-9
        with self.assertRaisesRegex(ValueError, 'RANK1_CERT_NOT_UNRESOLVED'):
            r1.project_rank1(p, w, cert([3, -30, 35]))
        # binding alone: 1e-13 in mu is outside the 2^-48 window in z
        with self.assertRaisesRegex(ValueError, 'RANK1_BINDING_NO_ROOT'):
            r1.bind_rays([m[0]-1e-13, m[1]], Fraction(6, 7), Fraction(3, 35))
        self.assertEqual(r1.bind_rays(m, Fraction(6, 7), Fraction(3, 35)), (1, 0, 0, 1))

    def test_rank_must_be_two(self):
        mu, q = lrs_rule(0.0, 8)
        with self.assertRaisesRegex(ValueError, 'RANK1_CERT_SUPPORT_RANK'):
            r1.project_rank1(mu, q, cert([3, -30, 35]))


class Rank1Guards(unittest.TestCase):
    def test_vertex_ambiguous_and_strict_integers(self):
        with self.assertRaisesRegex(ValueError, 'RANK1_BINDING_AMBIGUOUS'):
            r1.bind_rays([math.sqrt(3/7)], Fraction(6, 7), Fraction(3, 35))
        m, w = np.polynomial.legendre.leggauss(4)
        for bad in (' 3', '-3_0', '+3', '3.0'):
            with self.assertRaisesRegex(ValueError, 'RANK1_CERT_INTEGER'):
                r1.project_rank1(m, w, cert([bad, -30, 35]))

    def test_decided_float_status_is_not_rerouted(self):
        m = np.array([-0.9, -0.4, 0.4, 0.9])
        with self.assertRaisesRegex(ValueError, 'RANK1_CERT_NOT_UNRESOLVED'):
            r1.project_rank1(m, np.ones(4), cert([3, -30, 35]))


class Receipts(unittest.TestCase):
    def test_failed_serialization_leaves_no_file(self):
        with tempfile.TemporaryDirectory() as t:
            p = Path(t)/'r.json'
            with self.assertRaises(TypeError):
                write_json_once(p, {'x': object()})
            self.assertFalse(p.exists())


class SpectralValidator(unittest.TestCase):
    def _rows(self, prereg):
        pred = {p['cps']: p['probe_residual_predicted'] for p in prereg['predictions']}
        rows = []
        for block, n, ne, c, b in sorted(rsr.expected_grid(prereg)):
            rows.append({'schema': 'bass.angular.native.s6c.v1', 'block': block, 'mode': 'P2P4', 'n_mu': n,
                         'n_energy': ne, 'cells_per_segment': c, 'b_birth': b, 'inventory_n': 1.0, 'inventory_u': 1.0,
                         'ledger_n_residual': 0.0, 'ledger_u_residual': 0.0, 'photon_vs_source_relative': 0.0,
                         'energy_vs_source_moment_relative': pred[c], 'source_mean_ev': 30.0, 'weight_p2': 0.0,
                         'weight_p4': 0.0, 'energy_p2': 0.0, 'energy_p4': 0.0, 'derivative_central': -1.6,
                         'derivative_legendre': -1.6, 'derivative_h': 1e-5, 'min_weight': 0.01})
        return rows

    def _write(self, rows, t):
        p = Path(t)/'x.jsonl'
        done = {'schema': 'bass.angular.native.s6c.complete.v1', 'rows': len(rows),
                'owner_commit': rsr.REI_SHA, 'source_id': rsr.SOURCE_ID}
        p.write_text(''.join(json.dumps(r)+'\n' for r in rows+[done]))
        return p

    def test_grid_and_gates(self):
        prereg = json.loads(rsr.PREREG.read_text())
        rows = self._rows(prereg)
        with tempfile.TemporaryDirectory() as t:
            _, val = rsr.validate(self._write(rows, t), prereg)
            self.assertTrue(all(val['gates'].values()))
        with tempfile.TemporaryDirectory() as t:
            bad = [dict(r) for r in rows]; bad[0]['cells_per_segment'] = 128
            with self.assertRaises((ValueError, KeyError)):
                rsr.validate(self._write(bad, t), prereg)
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaisesRegex(ValueError, 'S6C_COMPLETION_IDENTITY'):
                rsr.validate(self._write(rows[1:], t), prereg)
        with tempfile.TemporaryDirectory() as t:
            bad = [dict(r) for r in rows]; bad[3]['energy_vs_source_moment_relative'] += 5e-15
            _, val = rsr.validate(self._write(bad, t), prereg)
            self.assertFalse(val['gates']['per_row'])


class Spectral(unittest.TestCase):
    def test_bitwise_native_run01_value(self):
        p = sr.predicted(16)
        self.assertEqual(p['probe_residual_predicted'], 5.369704680902032e-12)
        self.assertLess(abs(p['gl8_vs_exact']), 1e-16)
        self.assertLess(abs(p['simpson32_vs_exact']+p['probe_residual_predicted']), 1e-16)
        rows = [json.loads(l) for l in (HERE/'evidence_native_s3/run01/NATIVE_ADAPTER.jsonl').read_text().splitlines()]
        vals = {r['energy_vs_source_moment_relative'] for r in rows if 'mode' in r}
        self.assertEqual(vals, {5.369704680902032e-12, 5.369926725506957e-12})
        self.assertLessEqual(max(vals)-min(vals), 2.3e-16)

    def test_fourth_order_panel_scaling(self):
        a, b = sr.predicted(8)['probe_residual_predicted'], sr.predicted(16)['probe_residual_predicted']
        self.assertTrue(15 < a/b < 17)


class SourceAge(unittest.TestCase):
    def test_frozen_cohorts_satisfy_identity(self):
        u, w = sa.cohorts(8)
        rules = [sa.rule(sa.b_of_x(x), 8, 'P2') for x in u]
        res, U = sa.identity_residual(0.9, u, w, rules)
        self.assertLess(abs(res)/U, 1e-13)

    def test_reprojection_breaks_identity(self):
        """Negative control: re-weighting survivors with the observation-time rule."""
        u, w = sa.cohorts(8)
        def moment(x, j):
            mu, al = sa.rule(sa.b_of_x(x), 8, 'P24')
            return sum(wk*math.exp(-4*(x-uk))*math.fsum(al*sa._kernels(sa.b_of_x(x)-sa.b_of_x(uk), mu)[j])
                       for uk, wk in zip(u, w))
        x, h = 0.9, 1e-5
        dU = (moment(x+h, 0)-moment(x-h, 0))/(2*h)
        self.assertGreater(abs(dU+4*moment(x, 0)+2*sa.db_dx(x)*moment(x, 1))/moment(x, 0), 1e-6)

    def test_rule_modes(self):
        mu, al = sa.rule(0.1, 8, 'P24')
        self.assertLess(abs(math.fsum(al*(3*mu*mu-1)/2)), 3e-15)
        with self.assertRaises(ValueError):
            sa.rule(0.1, 8, 'P6')


if __name__ == '__main__':
    unittest.main()
