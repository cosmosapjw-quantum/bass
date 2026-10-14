import unittest
from fractions import Fraction as Q
import pl_metrics as p
class TestPL(unittest.TestCase):
 def test_interior_breakpoint_must_not_be_ignored(self):
  a=((Q(0),Q(1,2),Q(1)),(Q(0),Q(1),Q(0)))
  b=((Q(0),Q(1)),(Q(0),Q(0)))
  self.assertEqual(p.difference_supremum(a,b),1)

class Additional(unittest.TestCase):
 def setUp(self):
  self.z=((Q(0),Q(1)),(Q(0),Q(0)))
 def test_tent_integrals(self):
  a=((Q(0),Q(1,2),Q(1)),(Q(0),Q(1),Q(0)))
  r=p.compare(a,self.z);self.assertEqual(r['integral_abs'],Q(1,2));self.assertEqual(r['integral_squared'],Q(1,3))
 def test_opposite_sign_integral(self):
  r=p.compare(((Q(0),Q(1)),(Q(-1),Q(1))),self.z)
  self.assertEqual(r['integral_abs'],Q(1,2));self.assertEqual(r['integral_squared'],Q(1,3))
 def test_nonmatching_knots(self):
  a=((Q(0),Q(1,3),Q(1)),(Q(0),Q(1,3),Q(1)))
  b=((Q(0),Q(1,4),Q(3,4),Q(1)),(Q(0),Q(1,4),Q(3,4),Q(1)))
  self.assertEqual(p.compare(a,b)['sup_abs'],0)
 def test_coordinates_not_interchangeable(self):
  with self.assertRaises(ValueError):p.compare(self.z,self.z,coordinate_b='A_BINARY64')
 def test_no_extrapolation(self):
  with self.assertRaises(ValueError):p.evaluate(self.z,Q(2))
 def test_unknown_not_zero(self):self.assertIsNone(p.true_difference_ceiling(Q(0),None,Q(0)))
 def test_known_uniform(self):self.assertEqual(p.true_difference_ceiling(Q(1),Q(2),Q(3)),6)
 def test_nan_float_disallowed(self):
  with self.assertRaises(TypeError):p.compare(((Q(0),Q(1)),(Q(0),float('nan'))),self.z)
 def test_duplicate_knots(self):
  with self.assertRaises(ValueError):p.compare(((Q(0),Q(0)),(Q(0),Q(1))),self.z)
 def test_empty_overlap(self):
  with self.assertRaises(ValueError):p.compare(((Q(1),Q(2)),(Q(0),Q(1))),self.z)
 def test_sampled_grid_misses_narrow_tent(self):
  a=((Q(0),Q(2001,4000),Q(1001,2000),Q(2003,4000),Q(1)),(Q(0),Q(0),Q(1),Q(0),Q(0)))
  self.assertEqual(max(abs(p.evaluate(a,Q(i,1000))) for i in range(1001)),0)
  self.assertEqual(p.compare(a,self.z)['sup_abs'],1)
 def test_swap_sign_norm_invariant(self):
  a=((Q(0),Q(1)),(Q(2),Q(3)))
  r=p.compare(a,self.z);s=p.compare(self.z,a)
  self.assertEqual(r['sup_abs'],s['sup_abs']);self.assertEqual(r['signed_at_peak'],-s['signed_at_peak'])
 def test_partial_overlap_only(self):
  a=((Q(1,2),Q(3,2)),(Q(1),Q(3)))
  r=p.compare(a,self.z);self.assertEqual(r['interval'],(Q(1,2),Q(1)));self.assertEqual(r['sup_abs'],2)
 def test_negative_envelope_refused(self):
  with self.assertRaises(ValueError):p.true_difference_ceiling(Q(0),Q(-1),Q(1))
