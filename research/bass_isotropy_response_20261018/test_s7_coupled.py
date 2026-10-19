"""Independent conservation, limit and invalid-source tests for new S7 code."""
import math
import json
from pathlib import Path
import tempfile
import unittest
from dataclasses import replace
import numpy as np
from coupled_cohorts import (Config, Cohort, BirthRuleFailure, diagnostics, initial_bank,
                             solve_history, source_frame_gl)


class CoupledConservation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = Config(K=8, n=16, mode='P24')
        cls.history = solve_history(cls.config)
        cls.diag = diagnostics(cls.history, 61)

    def test_independently_evolved_hamiltonian(self):
        self.assertLessEqual(self.diag['max_hamiltonian_relative'], 1e-11)

    def test_each_cohort_complex_step_energy_identity(self):
        self.assertLessEqual(self.diag['max_cohort_energy_relative'], 1e-11)

    def test_positive_event_transfer_preserves_total_energy(self):
        for e in self.history.events:
            self.assertGreater(e['energy_birth'], 0)
            self.assertGreater(e['donor_after'], 0)
            self.assertAlmostEqual(e['donor_before']-e['donor_after'], e['energy_birth'], delta=1e-15)
            self.assertAlmostEqual(e['C_before'], e['C_after'], delta=1e-15)
        self.assertLessEqual(self.diag['max_event_energy_relative'], 1e-13)

    def test_physical_old_stock_is_frozen_and_anisotropic(self):
        originals = initial_bank(self.config)
        self.assertEqual(originals.birth_digests, self.history.bank.birth_digests[:2])
        self.assertTrue(self.history.bank.unchanged())
        E, Pi = self.history.bank.cohorts[1].energy_pressure(0, self.config.b0)
        self.assertAlmostEqual(Pi/E, self.config.eta/5, delta=2e-14)
        self.assertGreater(Pi, 0)

    def test_future_births_absent_from_initial_inventory(self):
        zero = self.history.observe(0)
        self.assertAlmostEqual(zero['E_radiation'], self.config.old_isotropic+self.config.old_anisotropic, delta=1e-15)
        self.assertAlmostEqual(zero['E_donor'], self.config.donor0, delta=1e-15)

    def test_positive_reflection_and_new_moment_gate(self):
        for label in ('positive_all_stock', 'reflection_all_stock', 'birth_moments'):
            self.assertTrue(self.diag['gate_results'][label])


class IndependentLimits(unittest.TestCase):
    def test_flrw_matter_radiation_lambda_no_birth(self):
        config = Config(K=0, mode='source_frame_GL', n=32, y0=0, eta=0, decay_lambda=0)
        history = solve_history(config)
        for x in np.linspace(0, config.x_end, 13):
            obs = history.observe(float(x))
            exact = math.sqrt(config.donor0*math.exp(-3*x)+(config.old_isotropic+config.old_anisotropic)*math.exp(-4*x)+config.cosmological_constant)
            self.assertAlmostEqual(obs['h'], exact, delta=2e-12)
            self.assertAlmostEqual(obs['b'], config.b0, delta=1e-13)
            self.assertAlmostEqual(obs['y'], 0, delta=1e-13)

    def test_isotropic_discrete_transfer_exact_background(self):
        config = Config(K=8, n=32, mode='source_frame_GL', y0=0, eta=0)
        history = solve_history(config)
        x = config.x_end
        du = config.birth_end/config.K
        comoving = config.old_isotropic+config.old_anisotropic
        for k, u in enumerate(history.births):
            w = config.donor0*math.exp(-3*u-config.decay_lambda*k*du)*(-math.expm1(-config.decay_lambda*du))
            comoving += w*math.exp(4*u)
        exact_E = math.exp(-4*x)*comoving
        exact_donor = config.donor0*math.exp(-3*x-config.decay_lambda*config.birth_end)
        obs = history.observe(x)
        self.assertAlmostEqual(obs['E_radiation'], exact_E, delta=2e-14)
        self.assertAlmostEqual(obs['h'], math.sqrt(exact_E+exact_donor+config.cosmological_constant), delta=2e-12)

    def test_wrong_source_without_donor_fails_hamiltonian(self):
        history = solve_history(Config(K=4, mode='source_frame_GL', n=16), donor_subtraction=False)
        self.assertGreater(diagnostics(history, 21)['max_hamiltonian_relative'], 1e-4)

    def test_infeasible_birth_records_support(self):
        with self.assertRaises(BirthRuleFailure) as caught:
            solve_history(Config(K=4, b0=0.9, n=8, mode='P24'))
        self.assertEqual(caught.exception.record['kind'], 'feasibility')
        self.assertIn('INFEASIBLE', caught.exception.record['error'])
        self.assertEqual(len(caught.exception.record['mu']), 8)

    def test_zero_source_makes_no_zero_weight_cohort(self):
        history = solve_history(Config(K=8, decay_lambda=0))
        self.assertEqual(len(history.bank.cohorts), 2)
        self.assertEqual(history.events, [])

    def test_invalid_signed_ray_is_rejected(self):
        mu, w = source_frame_gl(8)
        invalid = w.copy(); invalid[0] = -0.01
        with self.assertRaisesRegex(ValueError, 'POSITIVE_DOMAIN'):
            Cohort.create(0, 0, 1, mu, invalid, 'invalid')

    def test_configuration_rejects_missing_source_discretization(self):
        with self.assertRaisesRegex(ValueError, 'K0_REQUIRES_NO_SOURCE'):
            solve_history(Config(K=0))

    def test_nonfinite_birth_geometry_rejected(self):
        mu, alpha = source_frame_gl(8)
        for u, b in ((math.nan, 0), (0, math.inf)):
            with self.assertRaisesRegex(ValueError, 'POSITIVE_DOMAIN'):
                Cohort.create(u, b, 1, mu, alpha, 'invalid')


class PreregistrationGuards(unittest.TestCase):
    def test_gate_change_cannot_run_under_old_plan(self):
        from run_s7_coupled import campaign_definition, verify_preregistration
        plan = campaign_definition(); plan['gates']['moment_abs'] = 1e-10
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)/'plan.json'; p.write_text(json.dumps(plan))
            with self.assertRaisesRegex(ValueError, 'SOURCE_OR_GATE_CHANGED'):
                verify_preregistration(p, '0'*40)

    def test_unverified_local_receipt_not_admitted(self):
        from run_s7_coupled import campaign_definition, verify_preregistration
        with tempfile.TemporaryDirectory() as td:
            p, r = Path(td)/'plan.json', Path(td)/'receipt.json'
            p.write_text(json.dumps(campaign_definition())); r.write_text('{}')
            with self.assertRaisesRegex(ValueError, 'PUBLICATION_RECEIPT_MISMATCH'):
                verify_preregistration(p, '0'*40, r)


if __name__ == '__main__':
    unittest.main(verbosity=2)
