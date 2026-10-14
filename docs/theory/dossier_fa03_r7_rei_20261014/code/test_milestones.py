import unittest
from fractions import Fraction as F
from milestones import first_passage_band
class FirstPassageTests(unittest.TestCase):
 def test_supplied_continuous_envelope_bounds_linear_first_hit(self):
  r=first_passage_band([0,10],[0,1],F(1,2),F(1,10),envelope_kind='CONTINUOUS_ERROR_ENVELOPE',bound_authority='manufactured uniform bound')
  self.assertEqual((r['lower'],r['upper']),(F(4),F(6)))
if __name__=='__main__':unittest.main()

class EdgeCases(unittest.TestCase):
 def band(self,t,y,c,d):return first_passage_band(t,y,c,d,envelope_kind='CONTINUOUS_ERROR_ENVELOPE',bound_authority='synthetic proved envelope')
 def test_nonmonotone_first_event(self):
  r=self.band([0,1,2,3],[0,1,0,1],F(1,2),F(1,10));self.assertEqual((r['lower'],r['upper']),(F(2,5),F(3,5)))
 def test_missing_error_is_not_zero(self):
  r=first_passage_band([0,1],[0,1],F(1,2));self.assertIsNone(r['lower']);self.assertIsNone(r['upper']);self.assertIn('UNKNOWN',r['status'])
 def test_initial_envelope_overlap(self):
  r=self.band([0,1],[F(9,20),1],F(1,2),F(1,10));self.assertEqual(r['lower'],0);self.assertGreater(r['upper'],0)
 def test_flat_threshold_interval(self):
  r=self.band([0,1,2,3],[0,F(1,2),F(1,2),1],F(1,2),0);self.assertEqual(r['lower'],1);self.assertEqual(r['upper'],1)
 def test_flat_uncertain_endpoint(self):
  r=self.band([0,1],[F(49,100),F(49,100)],F(1,2),F(1,10));self.assertEqual(r['lower'],0);self.assertIsNone(r['upper'])
 def test_no_hit_under_bound(self):
  r=self.band([0,1],[0,F(1,4)],F(1,2),F(1,10));self.assertIsNone(r['lower']);self.assertIn('NO_HIT',r['status'])
 def test_possible_not_guaranteed(self):
  r=self.band([0,1],[0,F(49,100)],F(1,2),F(1,10));self.assertIsNotNone(r['lower']);self.assertIsNone(r['upper'])
 def test_initial_above_no_pre_history(self):
  r=self.band([0,1],[1,2],F(1,2),F(1,10));self.assertEqual(r['upper'],0);self.assertEqual(r['reference']['prehistory'],'UNKNOWN')
 def test_variable_radius(self):
  r=self.band([0,10],[0,1],F(1,2),[0,F(1,10)]);self.assertEqual(r['lower'],F(50,11));self.assertEqual(r['upper'],F(50,9))
 def test_large_origin_no_float_cancellation(self):
  n=10**25;r=self.band([n,n+10],[0,1],F(1,2),F(1,10));self.assertEqual(r['lower'],n+4);self.assertEqual(r['upper'],n+6)
 def test_node_only_error_rejected(self):
  with self.assertRaises(ValueError):first_passage_band([0,1],[0,1],'.5','.1',envelope_kind='NODE_ERROR',bound_authority='node proof')
 def test_no_authority_rejected(self):
  with self.assertRaises(ValueError):first_passage_band([0,1],[0,1],'.5','.1',envelope_kind='CONTINUOUS_ERROR_ENVELOPE')
 def test_duplicate_coordinate_rejected(self):
  with self.assertRaises(ValueError):self.band([0,0],[0,1],'.5','.1')
 def test_reverse_coordinate_rejected(self):
  with self.assertRaises(ValueError):self.band([1,0],[0,1],'.5','.1')
 def test_negative_error_rejected(self):
  with self.assertRaises(ValueError):self.band([0,1],[0,1],'.5','-.1')
 def test_nan_rejected(self):
  with self.assertRaises(ValueError):self.band([0,1],[0,float('nan')],'.5','.1')
 def test_vector_length_rejected(self):
  with self.assertRaises(ValueError):self.band([0,1],[0,1],'.5',[0])
 def test_uniform_slope_scaling(self):
  r=self.band([0,100],[0,1],'.5','.01');self.assertEqual(r['upper']-r['lower'],2)
 def test_single_point(self):
  r=self.band([3],[1],'.5','.1');self.assertEqual(r['lower'],3)
 def test_radius_widening(self):
  a=self.band([0,10],[0,1],'.5','.1');b=self.band([0,10],[0,1],'.5','.2');self.assertLess(b['lower'],a['lower']);self.assertGreater(b['upper'],a['upper'])
