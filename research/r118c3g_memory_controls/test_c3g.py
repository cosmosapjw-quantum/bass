import unittest, numpy as np
from memory_controls import principal_bound, initial_span
class MemoryControlsTest(unittest.TestCase):
 def test_axial(self):
  self.assertLess(principal_bound(np.eye(5)[:,[0,2,3,4]])['sigma_min'],1e-12)
 def test_triaxial(self):
  self.assertAlmostEqual(principal_bound(np.eye(5)[:,[1,2,3,4]])['sigma_min'],1/np.sqrt(5),places=12)
 def test_span_invariance(self):
  A=initial_span(.025,.1,.25,.2);M=np.array([[1.,.1,0,0],[0,2,0,.2],[0,0,1,0],[.2,0,0,1]])
  self.assertAlmostEqual(principal_bound(A)['sigma_min'],principal_bound(A@M)['sigma_min'],places=12)
 def test_axial_construction(self):
  self.assertLess(principal_bound(initial_span(.025,0,1/(3*np.sqrt(2)),0))['sigma_min'],1e-12)
 def test_bad_rank(self):
  with self.assertRaises(ValueError):principal_bound(np.ones((5,4)))
if __name__=='__main__':unittest.main()
