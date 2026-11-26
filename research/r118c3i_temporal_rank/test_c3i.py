import unittest,numpy as np
from numpy.polynomial.legendre import leggauss
from linear_response import coeff,radial_check,solve,parity
class T(unittest.TestCase):
 def test_radial(self):self.assertLess(radial_check(),1e-8)
 def test_massless(self):
  y,w=leggauss(96);y=30*(1+y);w=30*w
  r,p,A,D=coeff(y,w,0.,.1);self.assertAlmostEqual(p/r,1.,places=13);self.assertAlmostEqual(D/r,8/15,places=13);self.assertAlmostEqual(A/r,8/15,places=11)
 def test_degenerate(self):
  q,u,s,h=solve([.006,.006,.006],48,64);np.testing.assert_allclose(s[:,1],s[:,2],rtol=0,atol=1e-15);self.assertLess(q['ratio'],1e-13)
 def test_parity(self):self.assertTrue(all(x['orthogonal_fraction']>.99 for x in parity().values()))
if __name__=='__main__':unittest.main()
