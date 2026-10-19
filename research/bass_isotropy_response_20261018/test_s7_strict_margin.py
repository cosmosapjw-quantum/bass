"""Two targeted R3 checks; no history integration before publication."""
from fractions import Fraction
import json
import math
from pathlib import Path
import unittest
import run_s7_strict_margin as r3
import coupled_cohorts as cc
import numpy as np


class StrictMarginTests(unittest.TestCase):
    def test_known_true_excess_repaired_with_same_nodes_and_positive_parity(self):
        path = Path(__file__).resolve().parent/'evidence_s7_coupled/EXACT_MOMENT_FAILURES_R2.json'
        witness = json.loads(path.read_text())['true_exact_failures'][0]['birth']
        old = cc.exact_birth_moment_certificate(witness['mu'], witness['alpha'], 'P24')
        self.assertFalse(old['pass'])
        original = cc.birth_rule
        with r3.strict_new_births() as counter:
            mu, alpha = cc.birth_rule(witness['b_birth'], 32, 'P24')
        self.assertIs(cc.birth_rule, original)
        self.assertEqual(counter['strict_projection_calls'], 1)
        np.testing.assert_array_equal(mu, witness['mu'])
        self.assertTrue(np.all(alpha > 0))
        np.testing.assert_array_equal(alpha, alpha[::-1])
        self.assertLessEqual(abs(math.fsum(alpha)-1), 3e-15)
        certificate = cc.exact_birth_moment_certificate(mu, alpha, 'P24')
        self.assertTrue(certificate['pass'])
        self.assertLessEqual(abs(Fraction(certificate['M4_exact'])), Fraction(3, 10**15))
        self.assertNotEqual(list(alpha), witness['alpha'])

    def test_exact_gate_still_rejects_a_true_excess(self):
        m = math.sqrt((1+1e-14)/3)
        certificate = cc.exact_birth_moment_certificate([-m, m], [0.5, 0.5], 'P2')
        self.assertEqual(certificate['gate_rational'], str(Fraction(3, 10**15)))
        self.assertGreater(abs(Fraction(certificate['M2_exact'])), Fraction(3, 10**15))
        self.assertFalse(certificate['pass'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
