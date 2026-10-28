import sys, unittest
from pathlib import Path
from fractions import Fraction as F
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'code'))
from anchored import source_number,anchored_gap,layer_mass,replace_layer,first_rate

A=[[F(2),F(-1)],[F(-1),F(3)]]
class AnchorTests(unittest.TestCase):
    def test_exact_source_float_semantics(self):
        self.assertEqual(source_number(.1),F.from_float(.1))
        self.assertNotEqual(source_number(.1),F('0.1'))
    def test_exact_decimal_and_integer(self):
        self.assertEqual(source_number('0.1'),F(1,10));self.assertEqual(source_number(3),3)
    def test_invalid_numeric_inputs(self):
        for x in [True,None,float('nan'),float('inf')]:
            with self.subTest(x=x),self.assertRaises(ValueError):source_number(x)
    def test_exact_anchor_match(self):
        self.assertEqual(anchored_gap(A,A,[[2,-1],[-1,4]],(0,0),(1,1)),0)
    def test_rate_interval_and_margin(self):
        self.assertEqual(anchored_gap(A,A,[[2,-1],[-1,4]],(0,0),(F(9,10),F(6,5)),F(1,100)),F(21,100))
    def test_induced_one_norm_is_column_sum(self):
        self.assertEqual(anchored_gap([[1,3],[2,4]],[[1,3],[2,4]],[[0,0],[0,0]],(0,0),(0,0)),7)
    def test_affine_clock_rectangle(self):
        self.assertEqual(anchored_gap([[2,0],[0,3]],[[4,0],[0,5]],[[3,0],[0,4]],(F(1,4),F(3,4)),(0,1)),F(3,2))
    def test_signed_matrix_corners(self):
        self.assertEqual(anchored_gap([[1,-2],[-3,4]],[[3,-1],[-2,5]],[[2,-1],[-2,5]],(0,1),(0,2)),2)
    def test_invalid_intervals_and_margin(self):
        for th,r,m in [((1,0),(0,1),0),((-1,0),(0,1),0),((0,2),(0,1),0),((0,1),(2,1),0),((0,1),(-1,1),0),((0,1),(0,1),-1)]:
            with self.subTest(th=th,r=r,m=m),self.assertRaises(ValueError):anchored_gap(A,A,A,th,r,m)
    def test_wrong_matrix_dimension(self):
        with self.assertRaises(ValueError):anchored_gap([[1]],A,A,(0,0),(0,0))
    def test_layer_preserves_temporal_term(self):
        self.assertEqual(layer_mass(1,2,10,0,3,10),F(3,4))
    def test_layer_initial_and_temporal_terms(self):
        self.assertEqual(layer_mass(2,2,10,3,4,100),5)
    def test_layer_short_interval(self):
        self.assertEqual(layer_mass(2,2,F(1,10),3,4,100),F(16,25))
    def test_global_bound_can_dominate(self):
        self.assertEqual(layer_mass(2,2,10,100,100,1),1)
    def test_zero_duration_and_zero_amplitude(self):
        self.assertEqual(layer_mass(3,2,0,1,1,1),0);self.assertEqual(layer_mass(0,2,1,1,1,1),0)
    def test_invalid_layer_inputs(self):
        vals=[1,2,3,4,5,6]
        for i in range(6):
            v=vals.copy();v[i]=-1
            with self.subTest(i=i),self.assertRaises(ValueError):layer_mass(*v)
        with self.assertRaises(ValueError):layer_mass(1,0,1,1,1,1)
    def test_same_case_complement(self):
        self.assertEqual(replace_layer(F(11),F(6),F(2),[F(1),F(1,2)]),8)
    def test_replacement_refuses_wider_or_inconsistent_bound(self):
        for args in [(11,6,2,[4]),(5,6,2,[1]),(11,6,-1,[1])]:
            with self.subTest(args=args),self.assertRaises(ValueError):replace_layer(*args)
    def test_first_rate_manufactured_exact_value(self):
        s={'clock':{'eta0':'0','NH_reference':'2000000','g0':'2'},'cosmology':{'omh2':4.0,'odeh2':0.0,'photon_omega_prefactor':0.0,'T0_K':1.0,'neutrino_factor':0.0,'Nnueff':0.0,'H_prefactor_s_inv':3.0,'LYA_FACT_cm3_inv':2.0}}
        lo,hi=first_rate(s,128).pair();self.assertLessEqual(lo,3);self.assertGreaterEqual(hi,3);self.assertLess(hi-lo,F(1,10**30))
    def test_invalid_first_rate_density(self):
        with self.assertRaises(ValueError):first_rate({'clock':{'NH_reference':'0','eta0':'0','g0':'1'},'cosmology':{}},128)
if __name__=='__main__':unittest.main(verbosity=2)
