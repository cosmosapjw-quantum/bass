"""New behavior tests; original scientific campaigns are not imported."""
from pathlib import Path
import sys,unittest
from fractions import Fraction as F
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'code'))
from defect import exact,norm1,column_gap,duration_interval,tail,moments,layer_mass,gap_bound,output_bound,knot_mass
class DefectTests(unittest.TestCase):
    def test_decimal_semantics(self): self.assertEqual(exact('0.1'),F(1,10))
    def test_implicit_float_and_missing_rejected(self):
        for x in (0.1,True,None):
            with self.subTest(x=x),self.assertRaises(ValueError): exact(x)
    def test_induced_one_norm_not_row_norm(self): self.assertEqual(norm1([[1,-7],[2,3]]),10)
    def test_column_contraction(self): self.assertEqual(column_gap([[5,-1],[-2,4]]),3)
    def test_nonmetzler_or_nongap_rejected(self):
        for m in ([[1,1],[0,1]],[[1,-2],[-1,1]]):
            with self.subTest(m=m),self.assertRaises(ValueError):column_gap(m)
    def test_duration_enclosure(self): self.assertEqual(duration_interval(2,'0.1'),(F(19,10),F(21,10)))
    def test_zero_duration(self):
        self.assertEqual(moments(2,0),(0,0));self.assertEqual(tail(2,0),1)
    def test_invalid_durations(self):
        for d,e in ((-1,0),(1,-1),(1,2)):
            with self.subTest(d=d,e=e),self.assertRaises(ValueError):duration_interval(d,e)
    def test_positive_moment_envelopes(self):
        self.assertEqual(moments(2,1),(F(1,2),F(1,4)))
        self.assertEqual(moments(2,F(1,10)),(F(1,10),F(1,200)))
    def test_rational_tail(self):self.assertEqual(tail(2,4),F(1,256))
    def test_invalid_decay_domain(self):
        for beta,d,n in ((0,1,8),(1,-1,8),(1,1,0),(1,1,True)):
            with self.subTest(beta=beta,d=d,n=n),self.assertRaises(ValueError):tail(beta,d,n)
    def test_local_layer_integral(self):self.assertEqual(layer_mass(3,4,0,1,2,1),F(3,4))
    def test_global_gap_can_be_tighter(self):self.assertEqual(layer_mass(3,1,3,4,2,1),F(3,2))
    def test_zero_layer_is_zero(self):self.assertEqual(layer_mass(0,1,3,4,2,1),0)
    def test_negative_bound_refused(self):
        for args in ((-1,1,1,1,2,1),(1,-1,1,1,2,1),(1,1,-1,1,2,1)):
            with self.subTest(args=args),self.assertRaises(ValueError):layer_mass(*args)
    def test_convex_matrix_gap(self):
        a=[[3,-1],[-1,4]];b=[[4,-2],[-1,4]]
        self.assertEqual(gap_bound(a,b,a,(0,1),(0,2),'0.1'),F(31,10))
    def test_gap_identity(self):
        a=[[3,-1],[-1,4]]
        self.assertEqual(gap_bound(a,a,a,(0,0),(0,0)),0)
    def test_joint_mass_charged_once(self):self.assertEqual(output_bound(6,2,3,1,[2,3],[4]),40)
    def test_nonpositive_output_gap_rejected(self):
        with self.assertRaises(ValueError):output_bound(1,1,0,0,[1],[])
    def test_knot_endpoint_errors_and_tail(self):
        self.assertEqual(knot_mass([1,2],[1,3],'0.1','0.2',2,2,4),F(13,10)+F(1,128))
    def test_zero_output_rate(self):self.assertEqual(output_bound(6,0,3,1,[2],[4]),0)
if __name__=='__main__':unittest.main(verbosity=2)
