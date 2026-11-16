import importlib.util,unittest
from pathlib import Path
import numpy as np
class Contracts(unittest.TestCase):
 def api(self):
  p=Path(__file__).with_name('redistribution.py');self.assertTrue(p.exists(),'constructive implementation absent')
  s=importlib.util.spec_from_file_location('rd',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
 def test_bernoulli(self):
  m=self.api();self.assertAlmostEqual(m.bernoulli(0.),1.);self.assertAlmostEqual(m.bernoulli(-.3),np.exp(.3)*m.bernoulli(.3))
 def test_sphere_quadrature(self):
  m=self.api();n,w=m.sphere(6,12);self.assertAlmostEqual(sum(w),1.);np.testing.assert_allclose(np.einsum('i,ij,ik->jk',w,n,n),np.eye(3)/3,atol=1e-14)
 def test_boost_roundtrip(self):
  m=self.api();n,w=m.sphere(4,8);nn,D=m.to_normal(n,.1);ne,De=m.to_atom(nn,.1);np.testing.assert_allclose(ne,n,atol=1e-14);np.testing.assert_allclose(D,De,atol=1e-14)
 def test_frequency_BE(self):
  m=self.api();e=np.linspace(.1,6,50);f=1/np.expm1(e+.2);j=m.thermal_flux(f,np.diff(e),stimulated=True);self.assertLess(np.max(abs(j)),2e-14)
 def test_frequency_Wien(self):
  m=self.api();e=np.linspace(.1,6,50);f=np.exp(-e);j=m.thermal_flux(f,np.diff(e),stimulated=False);self.assertLess(np.max(abs(j)),1e-14)
 def test_angular_conservation(self):
  m=self.api();n,w=m.sphere(4,8);D=np.linspace(.96,1.04,len(w));Q,pi=m.angular_generator(n,w,D);self.assertLess(np.max(abs(Q.sum(axis=0))),1e-14);self.assertLess(np.max(abs(Q@pi)),1e-14)
 def test_angular_number(self):
  m=self.api();n,w=m.sphere(4,8);Q,pi=m.angular_generator(n,w,np.ones(len(w)));N=np.arange(1,len(w)*8+1,dtype=float).reshape(len(w),8);out=m.angular_step(N,Q,pi,np.linspace(0,1e4,8));np.testing.assert_allclose(out.sum(axis=0),N.sum(axis=0),rtol=2e-12);self.assertGreaterEqual(out.min(),-1e-10)
 def test_negative_input(self):
  m=self.api()
  with self.assertRaises(ValueError):m.thermal_flux(np.array([1.,-1.]),np.array([.1]))
 def test_superluminal(self):
  m=self.api();n,w=m.sphere(4,8)
  with self.assertRaises(ValueError):m.to_atom(n,1.01)
 def test_bad_sphere(self):
  m=self.api()
  with self.assertRaises(ValueError):m.sphere(1,3)
 def test_nonunit(self):
  m=self.api()
  with self.assertRaises(ValueError):m.to_normal(np.array([[2.,0,0]]),.1)
 def test_invalid_angular_weight(self):
  m=self.api();n,w=m.sphere(4,8);w[0]=-1
  with self.assertRaises(ValueError):m.angular_generator(n,w,np.ones(len(w)))
 def test_fractional_cells_rejected(self):
  m=self.api()
  with self.assertRaises(ValueError):m.fixed_grid(3000.,20.,160.5)
 def test_negative_count_rejected(self):
  m=self.api();N=np.ones((2,5));N[0,0]=-1e-14;z=np.zeros_like(N)
  with self.assertRaises(ValueError):m.backward_birth_death(N,z,z,z,1.)
if __name__=='__main__':unittest.main(verbosity=2)
