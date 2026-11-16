import unittest,importlib.util
from pathlib import Path
import numpy as np
from numpy.polynomial.legendre import leggauss
class Physics(unittest.TestCase):
 def m(self):
  p=Path(__file__).with_name('collisions.py');self.assertTrue(p.exists(),'spectral collision implementation absent')
  s=importlib.util.spec_from_file_location('collisions',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
 def test_invalid_inputs(self):
  m=self.m()
  for args in [(3000,1.),(-1,.05),(3000,float('nan'))]:
   with self.assertRaises(ValueError):m.photo_rate(*args,'HI')
  with self.assertRaises(ValueError):m.sigma_ev(100,'unknown')
 def test_zero_tilt_planck_balance(self):
  m=self.m();r=m.compton_moments(0.)
  self.assertAlmostEqual(r['Tc_over_Tn'],1.,delta=3e-10)
  self.assertAlmostEqual(r['energy_ratio'],1.,delta=3e-10)
 def test_bose_einstein_balance(self):
  m=self.m();self.assertAlmostEqual(m.compton_moments(0.,eta=.7)['Tc_over_Tn'],1.,delta=3e-10)
 def test_boost_energy_and_number(self):
  m=self.m();b=.05;r=m.compton_moments(b);g=1/np.sqrt(1-b*b)
  self.assertAlmostEqual(r['energy_ratio'],g*g*(1+b*b/3),delta=3e-10)
  self.assertAlmostEqual(r['number_ratio'],g,delta=3e-10)
 def test_small_beta_coefficient(self):
  m=self.m();b=.001;r=m.compton_moments(b)
  self.assertAlmostEqual((r['Tc_over_Tn']-1)/b**2,2*np.pi**2/9-7/6,delta=2e-5)
 def test_induced_angular_bilinear(self):
  m=self.m();mu,w=leggauss(24);f=np.exp(.3*mu)+.2*mu**4
  a=m.induced_multipoles(f,mu,w/2);b=m.induced_pair(f,mu,w/2)
  self.assertAlmostEqual(a,b,delta=3e-11*abs(b))
 def test_no_induced_fails_equilibrium(self):
  m=self.m();r=m.compton_moments(0.);self.assertGreater(abs(r['Tc_spontaneous_over_Tn']-1),.03)
 def test_sigma_threshold_and_positive(self):
  m=self.m()
  for s in ('HI','HeI','HeII'):
   e=m.PARAMS[s][0];self.assertEqual(float(m.sigma_ev(e-.001,s)),0.)
   self.assertGreater(float(m.sigma_ev(e*1.01,s)),0.)
 def test_frame_photoionization(self):
  m=self.m()
  for s in ('HI','HeI','HeII'):
   a=m.photo_rate(3000,.05,s);b=m.photo_rate_normal(3000,.05,s)
   self.assertLess(abs(np.expm1(a['log_rate_s']-b['log_rate_s'])),2e-7)
 def test_parity(self):
  m=self.m();a=m.photo_rate(3000,.05,'HI');b=m.photo_rate(3000,-.05,'HI')
  self.assertAlmostEqual(a['log_rate_s'],b['log_rate_s'],delta=2e-12)
  self.assertAlmostEqual(m.compton_moments(.05)['Tc_over_Tn'],m.compton_moments(-.05)['Tc_over_Tn'],delta=2e-12)
 def test_scalar_temperature_counterexample(self):
  m=self.m();r=m.compton_moments(.05);self.assertGreater(abs(r['Tc_over_Tn']-r['energy_ratio']**.25),.001)
 def test_quadrature_refinement(self):
  m=self.m();a=m.photo_rate(3000,.05,'HI',order=48);b=m.photo_rate(3000,.05,'HI',order=96)
  self.assertLess(abs(np.expm1(a['log_rate_s']-b['log_rate_s'])),2e-7)
  a=m.compton_moments(.05,order=20);b=m.compton_moments(.05,order=40)
  self.assertLess(abs(a['Tc_over_Tn']-b['Tc_over_Tn']),3e-10)
if __name__=='__main__':unittest.main(verbosity=2)
