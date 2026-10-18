"""Additional independent MP70 and positive Green-bound controls."""
import unittest
import mpmath as mp
from born_photon_stress import angular_f_delta
from high_precision_check import analytic_F,analytic_D,estimate_gamma_operator_max
from coupled_lrs_gamma import gamma_contraction_bound_tight,gamma_contraction_bound

class HighPrecisionTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):mp.mp.dps=70
 def test_elementary_angular_energy_formula(self):
  for d in (-.62,-.31,-.008,.008,.31,.62):
   self.assertLess(abs(float(analytic_F(d))-angular_f_delta(d,128)[0]),2e-13)
 def test_independent_derivative_pressure(self):
  for d in (-.6,-.2,-.000000000001,.000000000001,.2,.62):
   true=float(analytic_D(d));computed=angular_f_delta(d,128)[1]
   self.assertLess(abs(true-computed),5e-12)
 def test_radiation_positive_operator_numerically_bounded(self):
  for mass in (3.,30.,300.):
   actual,upper=estimate_gamma_operator_max(mass)
   self.assertGreater(actual,0.)
   self.assertLess(actual,upper)
 def test_tight_green_bound_independent_of_mass(self):
  for x in (.001,.25,.7,1.435):
   self.assertGreaterEqual(gamma_contraction_bound_tight(1.,.1,x),0.)
   self.assertLess(gamma_contraction_bound_tight(1.,.1,x),gamma_contraction_bound(1.,.1,x))
  for m in (3.,30.,300.):
   actual,_=estimate_gamma_operator_max(m)
   self.assertLess(actual,gamma_contraction_bound_tight(1.,.1))
 def test_analytic_massless_quadratic_taylor(self):
  for d in (-.0001,.0001):
   mpF=analytic_F(d)
   self.assertLess(abs(mpF-(1+mp.mpf('1.6')*mp.mpf(str(d))**2)),mp.mpf('3')*abs(d)**3)

if __name__=='__main__':unittest.main()
