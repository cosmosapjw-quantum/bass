import unittest,importlib.util
from pathlib import Path
import numpy as np
class Contracts(unittest.TestCase):
 def api(self):
  p=Path(__file__).with_name('line_transfer.py');self.assertTrue(p.exists(),'implementation not yet present')
  sp=importlib.util.spec_from_file_location('lt',p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
 def test_isotropic_drift(self):
  m=self.api();r=m.drift(np.zeros(5),np.zeros(5),np.array([[1.,0,0],[0,1.,0]]));np.testing.assert_allclose(r['kappa'],1.)
 def test_photon_clock_not_atom_clock(self):
  m=self.api();s=np.array([0.,0.,0.,0.,.1]);r=m.drift(s,np.zeros(5),np.array([[0.,1,0],[0,-1.,0]]));self.assertNotEqual(float(r['D'][0]),float(r['D'][1]))
 def test_sobolev_limits(self):
  m=self.api();self.assertAlmostEqual(m.sobolev(0.),1.);self.assertAlmostEqual(m.sobolev(1e8)*1e8,1.);self.assertAlmostEqual(m.sobolev(1.),1-np.exp(-1.))
 def test_profile_positive(self):
  m=self.api();e=np.linspace(-7,7,101);p=m.profile_masses(e,.001);self.assertTrue(np.all(p>0));self.assertLess(sum(p),1.)
 def test_planck_cellwise_balance(self):
  m=self.api();z=m.line_grid(3000.,halfwidth=30.,cells=100);n=m.planck(m.H*z['nu']/(m.KB*3000.));nl=1e8;nu=3*nl*np.exp(-z['E0']/(m.KB*3000.));r=m.collision(z,nl,nu,n,3000.);self.assertLess(r['balance_relative'],2e-12)
 def test_energy_exchange(self):
  m=self.api();z=m.line_grid(4000.,halfwidth=10.,cells=30);r=m.collision(z,1e8,1e-5,np.zeros(30),4000.);self.assertLess(abs(r['energy_residual'])/r['gross_energy'],2e-13)
 def test_photon_nucleus_exchange(self):
  m=self.api();z=m.line_grid(3000.,cells=24);r=m.collision(z,2e8,1e-5,np.zeros(24),3000.);self.assertAlmostEqual((r['dnu']+r['dnl']),0.);self.assertAlmostEqual(r['dnu']+sum(r['F']),0.)
 def test_singleflight_analytic(self):
  m=self.api();p=np.array([.2,.5,.3]);self.assertAlmostEqual(m.singleflight(p,20*p),m.sobolev(20.),places=14)
 def test_finite_band_not_normalized(self):
  m=self.api();p=np.array([.05,.1,.05]);self.assertAlmostEqual(m.singleflight(p,10*p),.2*m.sobolev(2.),places=14)
 def test_inversion_rejected(self):
  m=self.api();self.assertRaises(ValueError,m.sobolev,-1.)
 def test_invalid_geometry(self):
  m=self.api();self.assertRaises(ValueError,m.drift,np.zeros(5),np.zeros(5),np.array([[2.,0,0]]))
 def test_invalid_band(self):
  m=self.api();self.assertRaises(ValueError,m.line_grid,-1.);self.assertRaises(ValueError,m.profile_masses,np.array([0.,0.,1.]),.1)
if __name__=='__main__':unittest.main(verbosity=2)
