"""Independent analytic/microscopic contracts for spectral collision moments."""
import importlib.util,unittest
from pathlib import Path
import numpy as np
from scipy.integrate import quad
from scipy.special import zeta
class Contract(unittest.TestCase):
 def module(self):
  p=Path(__file__).with_name('spectral.py');self.assertTrue(p.is_file(),'spectral collision implementation not yet present')
  s=importlib.util.spec_from_file_location('spectral_test',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
 def test_monopole_exact(self):
  m=self.module();x=np.geomspace(.001,400,170)
  for b in (0.,1e-6,.05,-.05,.3):
   direct=m.multipoles(x,b,96)[:,0]
   np.testing.assert_allclose(m.monopole(x,b),direct,rtol=3e-10,atol=1e-140)
 def test_lorentz_moments(self):
  m=self.module()
  for b in (0.,.05,.3):
   g=1/np.sqrt(1-b*b)
   n=quad(lambda x:x*x*float(m.monopole(x,b)),0,150,epsabs=1e-10)[0]
   u=quad(lambda x:x**3*float(m.monopole(x,b)),0,150,epsabs=1e-10)[0]
   self.assertAlmostEqual(n/(2*zeta(3)),g,places=10)
   self.assertAlmostEqual(u/(np.pi**4/15),g*g*(1+b*b/3),places=10)
 def test_induced_pair_kernel(self):
  m=self.module()
  for b in (.05,.3):
   for x in (.1,1.,6.):
    bl=m.multipoles(np.array([x]),b,48)[0]
    leg=m.induced(bl)
    pair=m.direct_pair(x,b,24,40)
    self.assertAlmostEqual(pair/leg,1.,places=11)
    self.assertGreater(leg,0.)
 def test_no_monopole_squared_shortcut(self):
  m=self.module();bl=m.multipoles(np.array([1.]),.1,48)[0]
  self.assertGreater(abs(m.induced(bl)-bl[0]**2),1e-5)
 def test_planck_energy_equilibrium(self):
  m=self.module();r=m.compton(0.,64,220)
  self.assertAlmostEqual(r['Tc_ratio'],1.,places=12)
  self.assertAlmostEqual(r['spontaneous_Tc_ratio'],zeta(5)/zeta(4),places=12)
  self.assertLess(r['spontaneous_Tc_ratio'],.97)
  self.assertAlmostEqual(m.heating_per_electron(3000,3000,0.),0.,delta=1e-36)
  self.assertLess(m.heating_per_electron(6000,3000,0.),0.)
 def test_small_beta_and_parity(self):
  m=self.module();b=.001;r=m.compton(b,48,200)
  a=(r['Tc_ratio']-1)/b**2
  self.assertLess(abs(a-(2*np.pi**2/9-7/6)),3e-6)
  self.assertAlmostEqual(m.compton(.05)['Tc_ratio'],m.compton(-.05)['Tc_ratio'],places=13)
 def test_cross_section_domain(self):
  m=self.module()
  for sp in ('HI','HeI','HeII'):
   th=m.PARAMS[sp]['threshold_eV']
   self.assertEqual(m.cross_section(sp,th*.99),0.)
   self.assertGreater(m.cross_section(sp,th),0.)
   with self.assertRaises(ValueError):m.cross_section(sp,50001.)
  with self.assertRaises(ValueError):m.cross_section('n2_effective',3.4)
 def test_photo_reference_integral(self):
  m=self.module();T=3000.;sp='HI';chi=m.PARAMS[sp]['threshold_eV'];kt=m.KB*T/m.EV
  norm=8*np.pi*m.EV**3/(m.HPLANCK**3*m.C**2)
  direct=norm*quad(lambda E:E*E*float(m.cross_section(sp,E))*float(m.monopole(E/kt,.05)),chi,chi+30*kt,epsabs=1e-60,epsrel=1e-10)[0]
  a=m.photo_rate(sp,T,.05,96,80)
  self.assertLess(abs(a['rate_s']/direct-1),2e-9)
  self.assertGreater(a['heating_W'],0.)
 def test_wien_log_robustness(self):
  m=self.module();a=m.photo_rate('HeII',820.,.028)
  self.assertTrue(np.isfinite(a['log_rate_s']))
  self.assertGreater(a['mean_excess_eV'],0.)
 def test_zero_boost_and_energy_scalar(self):
  m=self.module();T=3000.;b=.05;U=m.compton(b)['energy_ratio']
  a=m.photo_rate('HI',T,b);q=m.photo_rate('HI',T*U**.25,0.)
  self.assertGreater(a['rate_s']/q['rate_s'],1.2)
  self.assertAlmostEqual(m.photo_rate('HI',T,b)['log_rate_s'],m.photo_rate('HI',T,-b)['log_rate_s'],places=10)
 def test_invalid_input(self):
  m=self.module()
  for b in (1.,-1.,np.nan):
   with self.assertRaises(ValueError):m.compton(b)
  with self.assertRaises(ValueError):m.photo_rate('HI',0,.05)
  with self.assertRaises(ValueError):m.monopole(-1.,.05)
if __name__=='__main__':unittest.main(verbosity=2)
