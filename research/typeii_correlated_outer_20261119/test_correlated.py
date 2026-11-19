import unittest, numpy as np
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
class Contracts(unittest.TestCase):
 def setUp(self):
  import correlated as c
  self.c=c
 def test_angular_weights(self):
  n,w=self.c.sphere14()
  self.assertEqual(n.shape,(14,3));self.assertAlmostEqual(sum(w),1.,places=14)
  self.assertLess(max(abs(n@n.T-1).diagonal()),1e-12)
 def test_conditional_mass(self):
  p=self.c.conditional_bins(1.5,0.,0.005,np.array([-80.,0.,80.]))
  self.assertLess(abs(sum(p)-1),1e-8)
 def test_angle_frequency_correlation(self):
  x=2.
  a=self.c.conditional_bins(x,0.,.001,np.linspace(-20,20,81))
  b=self.c.conditional_bins(x,-1.,.001,np.linspace(-20,20,81))
  centers=np.linspace(-19.75,19.75,80)
  self.assertGreater(sum(centers*a)-sum(centers*b),2.0)
 def test_joint_flux_lte(self):
  g=self.c.small_generator(z=1100.,xouter=20.,angle_order=6)
  self.assertLess(g['column_defect'],1e-10)
  self.assertLess(g['wien_detailed_balance_defect'],1e-10)
 def test_factorized_not_same(self):
  g=self.c.small_generator(z=1100.,xouter=20.,angle_order=6)
  self.assertGreater(g['factorization_gap'],1e-5)
 def test_outer_reentry(self):
  g=self.c.small_generator(z=1100.,xouter=40.,angle_order=6)
  self.assertGreater(g['core_outward_rate'],0)
  self.assertGreater(g['core_return_rate'],0)
 def test_bad_inputs(self):
  with self.assertRaises(ValueError):self.c.conditional_bins(0.,2.,.1,np.array([-1.,1.]))
  with self.assertRaises(ValueError):self.c.conditional_bins(0.,0.,-.1,np.array([-1.,1.]))
  with self.assertRaises(ValueError):self.c.sphere14(invalid=True)
if __name__=='__main__':unittest.main(verbosity=2)
