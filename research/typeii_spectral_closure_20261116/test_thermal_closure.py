import unittest,importlib.util
from pathlib import Path
import numpy as np
class Thermal(unittest.TestCase):
 def mod(self):
  p=Path(__file__).with_name('thermal_closure.py');self.assertTrue(p.is_file(),'spectral thermal source not yet implemented')
  q=importlib.util.spec_from_file_location('tc',p);m=importlib.util.module_from_spec(q);q.loader.exec_module(m);return m
 def test_zero_radiation(self):
  m=self.mod();C,J,A,T=100.,2.,1.999,3000.
  self.assertEqual(m.tracking(C,J,A,T,-1),(C*T+J)/(C+A-1))
  self.assertEqual(m.rhs(2800,C,J,A,T),-A*2800+C*(T-2800)+J)
 def test_tracking_exponential(self):
  m=self.mod();C,A,r,T=35.,1.99,-.997,3000.
  state=m.tracking(C,0,A,T,r)
  self.assertAlmostEqual(m.rhs(state,C,0,A,T),r*state,delta=2e-11)
  self.assertGreater(abs(state-m.tracking(C,0,A,T,-1)),.1)
 def test_implicit_refinement(self):
  m=self.mod();C,A,T,X=2.,2.,5.,2.
  exact=C*T/(A+C)+(X-C*T/(A+C))*np.exp(-.1*(A+C))
  y=m.implicit(X,C,0,A,T,.1);z=m.implicit(m.implicit(X,C,0,A,T,.05),C,0,A,T,.05)
  self.assertLess(abs(z-exact),abs(y-exact))
 def test_energy_coefficient(self):
  m=self.mod();C,A,X,T,U=40.,2.,2500.,3000.,1.003
  self.assertAlmostEqual(m.rhs(X,C*U,0,A,T)-m.rhs(X,C,0,A,T),C*(U-1)*(T-X),places=9)
 def test_reject(self):
  m=self.mod()
  for args in ((-1.,0,2.,3000.,-1.),(1.,0,2.,-1.,-1.),(1.,0,2.,3000.,-4.)):
   with self.assertRaises(ValueError):m.tracking(*args)
  with self.assertRaises(ValueError):m.implicit(3.,2.,0,2.,5.,0.)
if __name__=='__main__':unittest.main(verbosity=2)
