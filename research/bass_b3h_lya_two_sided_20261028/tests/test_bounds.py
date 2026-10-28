import sys, unittest
from pathlib import Path
from fractions import Fraction as F
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'code'))
from bounds import witnesses,response_box,signed_box
A=[[[2,-1],[-1,2]],[[2,-1],[-1,2]]]
class BoundTests(unittest.TestCase):
    def test_exact_witnesses(self):
        self.assertEqual(witnesses(A,1,1,2),((F(1,5),F(2,5)),(F(2,7),F(4,7)),F(1)))
    def test_lower_without_positive_rate_is_zero(self):
        v,w,g=witnesses(A,1,0,2)
        self.assertEqual(v,(0,0));self.assertEqual(w,(F(2,7),F(4,7)))
    def test_zero_output_rate(self):
        self.assertEqual(response_box(A,1,0,0,3)[:2],((0,0),(0,0)))
    def test_zero_duration_is_exact(self):
        self.assertEqual(response_box(A,1,1,2,0),((0,0),(0,0),F(1)))
    def test_short_time_upper_and_terminal(self):
        low,up,B=response_box(A,1,1,2,F(1,100))
        self.assertEqual(up,(F(1,50),F(1,50)))
        self.assertEqual(B,(1+F(1,800))**-8)
        self.assertEqual(low[0],0)
        self.assertEqual(low[1],F(2,5)*(1-B))
    def test_large_time_retains_nonzero_tail(self):
        low,up,B=response_box(A,1,1,2,10)
        self.assertGreater(B,0);self.assertLess(B,F(1,100))
        self.assertEqual(low,(F(1,5)-F(2,5)*B,F(2,5)*(1-B)))
        self.assertEqual(up,(F(2,7),F(4,7)))
    def test_density_scaling(self):
        lo,hi,B=response_box(A,1,1,2,2)
        L,H,B2=response_box(A,7,1,2,2)
        self.assertEqual(L,tuple(7*x for x in lo));self.assertEqual(H,tuple(7*x for x in hi));self.assertEqual(B,B2)
    def test_witness_corner_signs(self):
        v,w,g=witnesses(A,1,1,2)
        for R in (F(1),F(3,2),F(2)):
            self.assertLessEqual(2*v[0]-v[1],0)
            self.assertLessEqual(-v[0]+(2+R)*v[1],R)
            self.assertGreaterEqual(2*w[0]-w[1],0)
            self.assertGreaterEqual(-w[0]+(2+R)*w[1],R)
    def test_mixed_sign_initial_box(self):
        self.assertEqual(signed_box((1,2),(3,4),[(-2,-1),(1,2)]),(F(-4),F(7)))
    def test_negative_initial_box(self):
        self.assertEqual(signed_box((1,2),(3,4),[(-2,-1),(-3,-2)]),(F(-18),F(-5)))
    def test_invalid_rate_order_and_density(self):
        for args in ((-1,1,2),(1,-1,2),(1,3,2)):
            with self.subTest(args=args),self.assertRaises(ValueError):witnesses(A,*args)
    def test_explicit_rational_semantics(self):
        self.assertEqual(witnesses(A,'1','1','2')[0],(F(1,5),F(2,5)))
        for x in (1.0,True):
            with self.subTest(x=x),self.assertRaises(ValueError):witnesses(A,x,1,2)
    def test_invalid_coefficient_and_contraction(self):
        for a in ([[[0,-1],[-1,2]]]*2,[[[2,1],[-1,2]]]*2,[[[1,-1],[-1,1]]]*2):
            with self.subTest(a=a),self.assertRaises(ValueError):witnesses(a,1,0,2)
    def test_negative_duration_refused(self):
        with self.assertRaises(ValueError):response_box(A,1,1,2,-1)
    def test_bad_tail_order_refused(self):
        for m in (0,-1,True,F(3,2)):
            with self.subTest(m=m),self.assertRaises(ValueError):response_box(A,1,1,2,1,m)
    def test_tail_refinement_is_ordered(self):
        Bs=[response_box(A,1,1,2,1,m)[2] for m in (1,2,4,8)]
        self.assertTrue(all(a>b for a,b in zip(Bs,Bs[1:])))
    def test_reversed_boxes_refused(self):
        with self.assertRaises(ValueError):signed_box((2,0),(1,1),[(0,1),(0,1)])
        with self.assertRaises(ValueError):signed_box((0,0),(1,1),[(2,1),(0,1)])
    def test_zero_density(self):
        lo,hi,B=response_box(A,0,1,2,1)
        self.assertEqual((lo,hi),((0,0),(0,0)))
if __name__=='__main__':unittest.main(verbosity=2)
