"""Independent exact classical Hummer RII source regression."""
import unittest,numpy as np
from scipy.integrate import quad
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
class Hummer(unittest.TestCase):
 def setUp(self):
  import hummer_rii as r
  self.r=r
 def test_voigt(self):
  self.assertGreater(self.r.phi(0.,.0008),0.)
  self.assertLess(self.r.phi(100.,.0008),1e-6)
 def test_symmetric(self):
  r=self.r
  for mu in (-.8,0.,.7):
   a=r.joint(1.8,-2.3,mu,.0008)
   self.assertAlmostEqual(a,r.joint(-2.3,1.8,mu,.0008),places=12)
 def test_marginal(self):
  r=self.r
  for mu in (-.6,0.,.7):
   val=quad(lambda y:r.joint(2.,y,mu,.001),-40,40,epsabs=3e-11)[0]
   self.assertLess(abs(val/r.phi(2.,.001)-1),2e-4)
 def test_direct_conditional(self):
  r=self.r;edges=np.linspace(-12,12,49)
  p=r.conditional_bins(2.,0.,.001,edges)
  self.assertGreater(sum(p),.9999)
  import correlated
  old=correlated.conditional_bins(2.,0.,.001,edges)
  self.assertLess(max(abs(p-old)),2e-4)
 def test_wing_and_limit(self):
  r=self.r;edges=np.array([-200.,-100.,-60.,-20.,0.,20.,60.,100.,200.])
  p=r.conditional_bins(80.,0.,.001,edges)
  self.assertGreater(sum(p),.999)
  self.assertTrue(np.isfinite(p).all())
  self.assertLess(sum(r.conditional_bins(80.,0.,.001,np.array([-20.,20.]))),.1)
  self.assertAlmostEqual(sum(r.conditional_bins(2.,1.,.001,np.array([-10.,0.,10.]))),1.,places=14)
 def test_model_scope(self):
  r=self.r
  self.assertEqual(r.MODEL_SCOPE,"COHERENT_NO_RECOIL_EXACT_HUMMER_II")
  with self.assertRaises(ValueError):r.joint(0.,0.,1.001,.001)
if __name__=='__main__':unittest.main(verbosity=2)
