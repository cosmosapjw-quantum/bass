"""Scoped independent MP70 and source normalization semantics."""
import unittest
from high_precision import compare
from lrs_retarded import FD96Retarded,XMAX

class PrecisionTest(unittest.TestCase):
    def test_mp70_fixed_source_9_cases(self):
        d=compare();self.assertEqual(len(d['states']),9)
        self.assertLess(d['max_relative_error'],3e-14)
    def test_signed_H_vs_Href_output_contract(self):
        f=FD96Retarded(3.)
        v=f.nonlinearity_remainder(.05)
        self.assertIn('signed_s_over_H_exact',v)
        self.assertIn('signed_s_over_H_linear',v)
        self.assertNotIn('v_exact',v)
        self.assertGreater(v['signed_s_over_H_linear'],0)
        self.assertLess(v['signed_s_over_H_absolute_remainder'],2e-7)
    def test_nonlinear_positive_negative_A_response(self):
        f=FD96Retarded(3.)
        for A in (-.05,.05):
            v=f.nonlinearity_remainder(A)
            self.assertGreater(A*v['signed_s_over_H_exact'],0)
            self.assertGreater(A*v['b_exact'],0)
            self.assertLess(v['b_relative_linear_error'],1e-3)

if __name__=='__main__':unittest.main()
