"""Behavioral tests for the exact shared-rate two-state witness."""
from pathlib import Path
from fractions import Fraction as F
import sys, unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'code'))
from dual import least_witness, corner_slacks, signed_bound
A=[[3,-1],[-2,4]]
ENDS=[A,A]
W=(F(5,4),F(15,8))
class DualTests(unittest.TestCase):
    def test_exact_fixture(self):
        self.assertEqual(least_witness(ENDS,5,2),W)
    def test_zero_reward(self):
        self.assertEqual(least_witness(ENDS,5,0),(F(0),F(0)))
    def test_diagonal_system(self):
        self.assertEqual(least_witness([[[3,0],[0,4]]]*2,5,2),(F(0),F(5,3)))
    def test_mixed_signed_interval(self):
        self.assertEqual(signed_bound(W,[(F(-2),F(-1)),(F(3),F(4))]),(F(-5,2),F(15,2)))
    def test_negative_box_preserves_sign(self):
        self.assertEqual(signed_bound(W,[(-2,-1),(-4,-3)]),(F(-10),F(0)))
    def test_four_corners_are_checked(self):
        sl=corner_slacks(ENDS,5,2,W)
        self.assertEqual(len(sl),4)
        self.assertTrue(all(v>=0 for pair in sl for v in pair))
        self.assertEqual(sl[1][1],0)
    def test_source_scaling(self):
        self.assertEqual(least_witness(ENDS,10,2),tuple(2*x for x in W))
    def test_time_unit_scaling(self):
        b=[[[7*x for x in row] for row in a] for a in ENDS]
        self.assertEqual(least_witness(b,5,14),W)
    def test_endpoint_order(self):
        b=[[[3,-1],[-2,4]],[[6,-2],[-3,6]]]
        w=least_witness(b,5,2)
        self.assertEqual(w,W)
        self.assertEqual(least_witness(b[::-1],5,2),w)
    def test_invalid_shape_and_sign(self):
        for b in [[],[A],[[[3,-1],[-2,4,8]],A],[[[3,1],[-2,4]],A],[[[0,-1],[-2,4]],A]]:
            with self.subTest(b=b), self.assertRaises(ValueError): least_witness(b,5,2)
    def test_unavailable_positive_slack(self):
        with self.assertRaises(ValueError): least_witness([[[1,-2],[-2,1]]]*2,5,2)
    def test_float_boolean_and_negative_input(self):
        for n,r in [(5.,2),(True,2),(5,False),(-1,2),(5,-1)]:
            with self.subTest(n=n,r=r), self.assertRaises(ValueError): least_witness(ENDS,n,r)
    def test_interval_and_weight_validation(self):
        for w,b in [(W,[(2,1),(0,1)]),(W,[(0,1)]),((-1,1),[(0,1),(0,1)]),(W,[(0.,1),(0,1)])]:
            with self.subTest(w=w,b=b), self.assertRaises(ValueError): signed_bound(w,b)
    def test_wrong_transpose_is_detected(self):
        wrong=(F(10,17),F(30,17))
        self.assertTrue(any(v<0 for pair in corner_slacks(ENDS,5,2,wrong) for v in pair))
if __name__=='__main__': unittest.main(verbosity=2)
