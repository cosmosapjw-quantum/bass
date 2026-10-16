import unittest
from einstein_stress_lag import evaluate

class TestEinsteinStressLag(unittest.TestCase):
    def test_exact_zero_source(self):
        rows,diag=evaluate(3.,0.,21)
        for r in rows:
            self.assertEqual(r['b'],0.)
            self.assertEqual(r['delta'],0.)
            self.assertEqual(r['Sigma'],0.)
    def test_signed_anisotropic_response_far_from_bstar(self):
        for A in (-.5,.5,2.):
            rows,_=evaluate(3.,A,21)
            e=rows[-1]
            self.assertGreater(e['b']*A,0.)
            self.assertGreater(e['signed_s_per_H']*A,0.)
            self.assertLess(e['ratio_abs_b_over_b_neutral'],.05)
    def test_mass_suppression(self):
        a,_=evaluate(3.,.5,21)
        b,_=evaluate(300.,.5,21)
        self.assertGreater(a[-1]['Sigma']/b[-1]['Sigma'],1000.)
    def test_kinetic_conservation(self):
        for m in (3.,30.,300.):
            _,check=evaluate(m,.5,21)
            self.assertLess(check['max_norm_energy_work'],2e-9)
            self.assertLess(check['max_norm_raychaudhuri'],2e-9)
    def test_integrator_output_density_independence(self):
        a,_=evaluate(3.,.5,21)
        b,_=evaluate(3.,.5,81)
        for key in ('b','Sigma','delta','b_neutral'):
            self.assertLess(abs(a[-1][key]-b[-1][key]),2e-9)

if __name__=="__main__":unittest.main()
