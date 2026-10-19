"""Targeted S8 derivative/guard checks; no main finite-difference campaign."""
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'
from dataclasses import replace
import json
import hashlib
import math
from pathlib import Path
import tempfile
import unittest
import numpy as np
import coupled_cohorts as cc
import s8_tangent as st
import s8_tangent_math as sm


def direct_kernels(d, mu):
    R = np.sqrt(np.exp(2*d)*(1-mu*mu)+np.exp(-4*d)*mu*mu)
    return R, (np.exp(-4*d)*mu*mu-np.exp(2*d)*(1-mu*mu)/2)/R


class LocalDerivatives(unittest.TestCase):
    def test_kernel_partials_against_independent_complex_step(self):
        mu = np.array([-0.93, -0.4, 0.2, 0.8]); step = 1e-25
        for d in (-0.3, 0.0, 0.4):
            _, _, Rd, Dd, Rmu, Dmu = sm.kernel_partials(d, mu)
            Rdc, Ddc = direct_kernels(d+1j*step, mu)
            Rmc, Dmc = direct_kernels(d, mu+1j*step)
            for actual, reference in ((Rd, Rdc.imag/step), (Dd, Ddc.imag/step),
                                      (Rmu, Rmc.imag/step), (Dmu, Dmc.imag/step)):
                self.assertLessEqual(float(np.max(abs(actual-reference))), 2e-13)

    def test_source_frame_and_prior_derivatives(self):
        b, n, step = 0.3, 16, 1e-25
        mu, prior = cc.lrs_rule(b, n)
        mu_b, score, _ = sm.source_frame_derivatives(mu, prior)
        m, w = np.polynomial.legendre.leggauss(n)
        bc = b+1j*step
        R = np.sqrt(np.exp(2*bc)*(1-m*m)+np.exp(-4*bc)*m*m)
        mc = m*np.exp(-2*bc)/R
        raw = w/R**3; qc = raw/np.sum(raw)
        self.assertLessEqual(float(np.max(abs(mu_b-mc.imag/step))), 5e-13)
        self.assertLessEqual(float(np.max(abs(prior*score-qc.imag/step))), 5e-13)

    def test_implicit_kl_derivative_local_symmetric_difference(self):
        b, step = 0.3, 1e-5
        rule = sm.birth_differential(b, 16, 'P24')
        _, plus = sm.primal_birth_rule(b+step, 16, 'P24')
        _, minus = sm.primal_birth_rule(b-step, 16, 'P24')
        self.assertLessEqual(float(np.max(abs(rule.alpha_b-(plus-minus)/(2*step)))), 1e-7)
        self.assertTrue(rule.diagnostics['exact_moment_certificate']['pass'])
        self.assertLessEqual(max(abs(v) for v in rule.diagnostics['moment_derivative_residual']), 1e-11)
        np.testing.assert_array_equal(rule.alpha_b, rule.alpha_b[::-1])
        np.testing.assert_array_equal(rule.mu_b, -rule.mu_b[::-1])

    def test_feature_span_prior_score_cancels_only_in_weight_derivative(self):
        rule = sm.birth_differential(0.3, 16, 'P24')
        mu, prior = cc.lrs_rule(0.3, 16)
        _, _, fb = sm.source_frame_derivatives(mu, prior)
        alternative, details = sm.implicit_kl_derivative(mu, rule.alpha, rule.diagnostics['multipliers'],
                                                        np.zeros_like(mu), fb)
        self.assertLessEqual(float(np.max(abs(alternative-rule.alpha_b))), 5e-13)
        shift = np.array(rule.diagnostics['lambda_b'])-np.array(details['lambda_b'])
        np.testing.assert_allclose(shift, [-6, 0], rtol=0, atol=5e-12)

    def test_rank_condition_failure_is_explicit(self):
        with self.assertRaisesRegex(sm.TangentDomainError, 'RANK_OR_CONDITION') as caught:
            sm.checked_covariance_solve(np.ones((2, 2)), np.ones(2))
        self.assertEqual(caught.exception.record['eigenvalues'][0], 0)
        self.assertIsNone(caught.exception.record['condition'])

    def test_full_cohort_parameter_derivative_by_complex_step(self):
        rule = sm.birth_differential(0.3, 16, 'P24')
        c = cc.Cohort.create(0.1, 0.3, 0.03, rule.mu, rule.alpha, 'new_isotropic_P24')
        bu_theta, b_theta = 0.2, 0.43
        entry = st.TangentCohort(c, np.array([bu_theta]), np.array([bu_theta]),
                                  rule.mu_b[None, :]*bu_theta, rule.alpha_b[None, :]*bu_theta)
        _, _, dE, dPi = entry.energy_pressure_tangent(0.5, 0.38, [b_theta])
        step = 1e-25
        dc = 0.38-0.3+1j*step*(b_theta-bu_theta)
        mc = c.mu+1j*step*entry.mu_theta[0]
        ac = c.alpha+1j*step*entry.alpha_theta[0]
        R, D = direct_kernels(dc, mc)
        factor = c.energy_birth*math.exp(-4*(0.5-c.u))
        self.assertAlmostEqual(dE[0], (factor*np.sum(ac*R)).imag/step, delta=2e-13)
        self.assertAlmostEqual(dPi[0], (factor*np.sum(ac*D)).imag/step, delta=2e-13)

    def test_old_physical_stock_has_transport_tangent_without_reweighting(self):
        c = cc.initial_bank(cc.Config()).cohorts[1]; old_digest = c.digest()
        zero = np.zeros((1, len(c.mu)))
        entry = st.TangentCohort(c, np.zeros(1), np.zeros(1), zero, zero)
        _, _, dE, dPi = entry.energy_pressure_tangent(0.5, 0.36, [0.4])
        self.assertGreater(abs(dE[0]), 1e-8)
        self.assertGreater(abs(dPi[0]), 1e-8)
        self.assertEqual(c.digest(), old_digest)

    def test_source_frame_gauge_zero_local_response(self):
        c = cc.initial_bank(cc.Config()).cohorts[1]
        zero = np.zeros((1, len(c.mu)))
        entry = st.TangentCohort(c, np.ones(1), np.ones(1), zero, zero)
        _, _, dE, dPi = entry.energy_pressure_tangent(0.5, 0.36, [1.0])
        self.assertEqual(dE[0], 0); self.assertEqual(dPi[0], 0)


class ShortDevelopmentIntegration(unittest.TestCase):
    def test_two_birth_analytic_smoke_and_linearized_conservation(self):
        cfg = replace(cc.Config(), K=2, n=16, mode='P24', birth_end=0.08, x_end=0.12)
        history = st.solve_tangent(cfg)
        diag = st.diagnostics(history, 13)
        self.assertTrue(all(diag['gate_results'].values()), diag['gate_results'])
        self.assertEqual(len(history.events), 2)
        self.assertTrue(history.bank.unchanged())


class PublicationGuards(unittest.TestCase):
    def test_changed_gate_does_not_match_preregistered_contract(self):
        from run_s8_tangent import campaign_definition, verify_preregistration
        plan = campaign_definition(); plan['gates']['fine_richardson_h_b_y_max_abs'] = 1
        with tempfile.TemporaryDirectory() as td:
            path = Path(td)/'plan.json'; path.write_text(json.dumps(plan))
            with self.assertRaisesRegex(ValueError, 'SOURCE_OR_CONTRACT_CHANGED'):
                verify_preregistration(path, '0'*40)

    def test_unverified_publication_receipt_rejected(self):
        from run_s8_tangent import campaign_definition, verify_preregistration
        with tempfile.TemporaryDirectory() as td:
            path, receipt = Path(td)/'plan.json', Path(td)/'receipt.json'
            path.write_text(json.dumps(campaign_definition())); receipt.write_text('{}')
            with self.assertRaisesRegex(ValueError, 'PUBLICATION_RECEIPT_MISMATCH'):
                verify_preregistration(path, '0'*40, receipt_path=receipt)

    def test_wrong_repository_or_path_receipt_rejected(self):
        import run_s8_tangent as runner
        with tempfile.TemporaryDirectory() as td:
            path, receipt = Path(td)/'plan.json', Path(td)/'receipt.json'
            raw = json.dumps(runner.campaign_definition()).encode(); path.write_bytes(raw)
            valid = {'schema': runner.PUBLICATION_SCHEMA, 'repo': runner.REPO,
                     'path': runner.PREREGISTRATION_PATH, 'commit': '0'*40,
                     'preregistration_sha256': hashlib.sha256(raw).hexdigest(),
                     'preregistration_git_blob_sha': hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest(),
                     'source_sha256': runner.source_hashes(), 'remote_readback_verified': True}
            receipt.write_text(json.dumps(valid))
            runner.verify_preregistration(path, '0'*40, receipt_path=receipt)
            for key, wrong in (('repo', 'different/repository'), ('path', 'different/PREREGISTRATION.json'),
                               ('schema', 'different.schema')):
                with self.subTest(key=key):
                    receipt.write_text(json.dumps({**valid, key: wrong}))
                    with self.assertRaisesRegex(ValueError, 'PUBLICATION_RECEIPT_MISMATCH'):
                        runner.verify_preregistration(path, '0'*40, receipt_path=receipt)


if __name__ == '__main__':
    unittest.main(verbosity=2)
