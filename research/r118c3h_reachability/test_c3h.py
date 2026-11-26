import unittest,numpy as np,json
from reachability import *
from native_candidates import controls
class T(unittest.TestCase):
 def test_gap(self):self.assertLess(check_gaps(),1e-12)
 def test_skew(self):
  x=np.arange(6.);np.testing.assert_array_equal(vector(skew(x,4)),x)
 def test_candidate(self):
  r=controls();self.assertAlmostEqual(r['orthogonal_fraction'],r['predicted_fraction'],places=9)
  Z=np.array(r['orthogonal']);np.testing.assert_allclose(Z.T@Z,np.eye(4),atol=1e-12)
 def test_axial(self):
  self.assertLess(gap_spectrum([0,1,0,0,0])[0],1e-12)
if __name__=='__main__':unittest.main()
