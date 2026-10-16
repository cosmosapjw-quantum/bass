from __future__ import annotations
import json, tempfile,unittest
from pathlib import Path
import numpy as np
from run_campaign import create

class CampaignTest(unittest.TestCase):
    def test_actual_campaign_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'r';doc=create(out)
            self.assertEqual(doc['rows'],99)
            self.assertEqual(len(doc['cases']),3)
            self.assertLess(doc['tests']['max_abs_picard_vs_ode'],3e-13)
            self.assertTrue(out.joinpath('SHA256SUMS.txt').exists())
    def test_nonlinear_remainder_is_small_at_A03(self):
        with tempfile.TemporaryDirectory() as tmp:
            doc=create(Path(tmp)/'r')
            for c in doc['cases']:
                for d in c['nonlinear_A']:
                    if abs(d['A'])<=.05:
                        self.assertLess(d['b_relative_linear_error'],2e-3)
    def test_high_order_time_convergence(self):
        with tempfile.TemporaryDirectory() as tmp:
            doc=create(Path(tmp)/'r')
            e=[c['time_refinement'] for c in doc['cases']][0]
            self.assertGreater(e[0]['endpoint_bA_error']/e[1]['endpoint_bA_error'],10.)
    def test_source_no_feedback_vs_actual(self):
        with tempfile.TemporaryDirectory() as tmp:
            doc=create(Path(tmp)/'r')
            for c in doc['cases']:
                self.assertGreater(c['feedback_fraction_final'],0.)
                self.assertLess(c['feedback_fraction_final'],.1)

    def test_causal_sign_and_absolute_positive_bound(self):
        from lrs_retarded import FD96Retarded,XMAX
        from reference_kinetic_tangent import XMAX
        import numpy as np
        for m in (3.,30.,300.):
            f=FD96Retarded(m)
            xs=np.linspace(0,XMAX,513)
            r=f.picard(xs)
            self.assertLess(f.proven_unforced_bound(),.1)
            self.assertLessEqual(np.max(r.b_without_feedback_per_A),f.proven_unforced_bound()+1e-14)
            self.assertTrue(np.all(r.b_per_A[1:]>0))
            self.assertTrue(np.all(r.s_per_href_per_A[1:]>0))
            self.assertTrue(np.all(r.b_per_A[1:]<=r.b_without_feedback_per_A[1:]+2e-13))
            self.assertTrue(np.all(r.b_per_A[1:]>=(1.-f.q_bound)*r.b_without_feedback_per_A[1:]-2e-13))

    def test_isotropic_mass_pressure_alpha_upper(self):
        import numpy as np,math
        from lrs_retarded import FD96Retarded,XMAX
        for m in (3.,30.,300.):
            f=FD96Retarded(m)
            for x in np.linspace(0.,XMAX,17):
                c=f.coefficients(float(x))
                self.assertLessEqual(c.alpha,math.exp(-3*x)/5*(1+1e-13))

if __name__=='__main__':unittest.main()
