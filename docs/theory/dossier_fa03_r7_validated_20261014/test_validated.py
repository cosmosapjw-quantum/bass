import unittest
from fractions import Fraction as Q
import validated as v
class Tests(unittest.TestCase):
 def test_cauchy_tail_must_not_be_zero(self):
  self.assertEqual(v.tail_bound(Q(2),Q(1,16),3),Q(1,30720))

class Algebra(unittest.TestCase):
 def setUp(self):v.iv.dps=65
 def test_scalar_reciprocal_series(self):
  a=[v.iq(2),v.iq(3),v.iq(0),v.iq(0)]
  b=v.power(a,Q(-1))
  for x,y in zip(b,[Q(1,2),Q(-3,4),Q(9,8),Q(-27,16)]):
   lo,hi=v.ends(x);self.assertLessEqual(lo,y);self.assertLessEqual(y,hi)
 def test_sqrt_square(self):
  a=[v.iq(2),v.iq(3),v.iq(1),v.iq(0)]
  b=v.mul(v.power(a,Q(1,2)),v.power(a,Q(1,2)))
  for x,y in zip(b,[2,3,1,0]):
   lo,hi=v.ends(x);self.assertLessEqual(lo,y);self.assertLessEqual(y,hi)
 def test_domain_radius(self):
  for q in [-Q(1,8),Q(1),Q(2)]:
   with self.assertRaises(ValueError):v.tail_bound(Q(1),q,20)
 def test_exact_weights_and_directions(self):
  r=v.geometry();self.assertEqual(sum(a['weight'] for a in r),1)
  for a in r:
   lo,hi=v.ends(v.dot(a['n'],a['n']));self.assertLessEqual(lo,1);self.assertLessEqual(1,hi)
 def test_zero_initial_tail_nonzero(self):
  self.assertGreater(v.tail_bound(Q(3,4),Q(1,8),20),0)
 def test_linear_system_loss_components(self):
  import numpy as np
  from fractions import Fraction
  G=np.array([[.2,-.31],[.29,.4]]);F=np.array([[.4,.1+.05j],[.1-.05j,.2]])
  rhs=-G@F-F@G.T;x=[.4,.2,.1,.05];y=[0.]*4
  for i,j,a in v.loss_entries([[v.iv.mpf(G[0,0])],[v.iv.mpf(G[1,1])],[v.iv.mpf(G[0,1])],[v.iv.mpf(G[1,0])]]):
   y[i]+=float(a[0].mid)*x[j]
  np.testing.assert_allclose(y,[rhs[0,0].real,rhs[1,1].real,rhs[0,1].real,rhs[0,1].imag],atol=2e-16)

if __name__=='__main__':unittest.main()
