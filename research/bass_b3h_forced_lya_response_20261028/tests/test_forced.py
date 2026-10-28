from pathlib import Path
import sys,unittest
from fractions import Fraction as F
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'code'))
from forced import Envelope,mass_interval,split_net_tv,combine,sign_budget

class ForcingTests(unittest.TestCase):
    def env(self,D=2):
        # Scalar channel2: lambda=d+R=2, r=10, with decoupled first state.
        return Envelope(D,10,1,2,(0,5),(0,5))
    def test_positive_mass(self):
        self.assertEqual(mass_interval((2,3),(4,5),(0,0)),(8,15))
    def test_negative_mass(self):
        self.assertEqual(mass_interval((2,3),(0,0),(4,5)),(-15,-8))
    def test_mixed_mass(self):
        self.assertEqual(mass_interval((2,3),(1,2),(3,4)),(-10,0))
    def test_net_zero_is_not_zero_variation(self):
        self.assertEqual(split_net_tv(0,2),(1,1))
        self.assertEqual(mass_interval((2,3),(1,1),(1,1)),(-1,1))
    def test_negative_net(self):
        self.assertEqual(split_net_tv(-1,3),(1,2))
    def test_invalid_variation(self):
        with self.assertRaises(ValueError):split_net_tv(3,2)
    def test_unknown_mass_is_not_zero(self):
        with self.assertRaises(ValueError):mass_interval((2,3),(0,None),(0,0))
    def test_exact_source_semantics(self):
        with self.assertRaises(ValueError):split_net_tv(.1,1)
        with self.assertRaises(ValueError):self.env(True)
    def test_shared_complement_not_sum(self):
        e=self.env();h=e.coefficients(0,1,'f2');k=e.coefficients(0,1,'shared_rate')
        self.assertEqual(k,(10-h[1],10-h[0]));self.assertGreater(k[0],0)
    def test_whole_window_includes_final_zero_response(self):
        self.assertEqual(self.env().coefficients(0,2,'f2'),(0,5))
        self.assertEqual(self.env().coefficients(0,2,'shared_rate'),(5,10))
    def test_early_window_positive_lower(self):
        self.assertGreater(self.env().coefficients(0,1,'f2')[0],0)
    def test_late_window_small_population_response(self):
        self.assertEqual(self.env().coefficients(F(199,100),2,'f2'),(0,F(1,10)))
    def test_window_restriction_nesting(self):
        e=self.env();whole=e.coefficients(0,2,'f2');early=e.coefficients(0,1,'f2')
        self.assertGreater(early[0],whole[0]);self.assertLessEqual(early[1],whole[1])
    def test_invalid_window_and_port(self):
        for a,b,port in [(-1,1,'f1'),(1,0,'f1'),(0,3,'f1'),(0,1,'rate')]:
            with self.subTest((a,b,port)):
                with self.assertRaises(ValueError):self.env().coefficients(a,b,port)
    def test_zero_window_mass_rejected(self):
        self.assertEqual(self.env().contribution(1,1,'f2',(0,0),(0,0)),(0,0))
        with self.assertRaises(ValueError):self.env().contribution(1,1,'f2',(1,1),(0,0))
    def test_zero_horizon(self):
        e=self.env(0);self.assertEqual(e.coefficients(0,0,'f2'),(0,0))
        self.assertEqual(e.coefficients(0,0,'shared_rate'),(10,10))
    def test_zero_rate(self):
        e=Envelope(2,10,0,2,(0,0),(0,0))
        self.assertEqual(e.coefficients(0,2,'shared_rate'),(10,10))
    def test_invalid_certificate(self):
        for args in [(2,10,1,0,(0,5),(0,5)),(2,10,1,2,(0,5),(0,11)),(2,10,1,2,(0,6),(0,5))]:
            with self.subTest(args):
                with self.assertRaises(ValueError):Envelope(*args)
    def test_direct_output_and_no_change(self):
        self.assertEqual(combine((-3,-2),[]),(-3,-2))
        self.assertEqual(combine((-3,-2),[(1,2)],(4,5)),(2,5))
    def test_sign_threshold_boundary_and_joint_spending(self):
        base=(-3,-2);w=(2,4)
        r=sign_budget(base,w,(F(1,2),0));self.assertTrue(r['strict_negative'])
        self.assertEqual(r['thresholds'],(1,F(1,2)))
        self.assertFalse(sign_budget(base,w,(1,0))['strict_negative'])
        self.assertEqual(sign_budget(base,w,(1,0))['upper'],0)
        self.assertGreater(sign_budget(base,w,(1,F(1,2)))['upper'],0)
    def test_invalid_interval_and_budget(self):
        with self.assertRaises(ValueError):mass_interval((3,2),(1,1),(0,0))
        with self.assertRaises(ValueError):sign_budget((-3,-2),(2,),(None,))

if __name__=='__main__':unittest.main(verbosity=2)
