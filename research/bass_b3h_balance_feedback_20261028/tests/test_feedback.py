import sys, unittest
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal, localcontext
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'code'))
from feedback import exp_interval, envelope, threshold_bracket

def dec(x): return Decimal(x.numerator)/Decimal(x.denominator)
def args(**changes):
    a=dict(n0=1,G='1/2',Z=1,D=1,nominal=('-2/5','-2/5'),kA=0,kR=0,q_limit=10)
    a.update(changes);return a

class FeedbackTests(unittest.TestCase):
    def test_exp_zero_exact(self): self.assertEqual(exp_interval(0),(F(1),F(1)))
    def test_exp_positive_contains_reference(self):
        with localcontext() as c:
            c.prec=70
            for x in ('1/10000','1/8','1/2','1','4','8'):
                lo,hi=exp_interval(x);ref=dec(F(x)).exp()
                self.assertLessEqual(dec(lo),ref);self.assertGreaterEqual(dec(hi),ref)
    def test_exp_width_contract(self):
        for x in ('1/10','3','8'):
            lo,hi=exp_interval(x);self.assertGreater(hi-lo,0);self.assertLessEqual(hi-lo,F(1,2**80))
    def test_exp_domain_refusal(self):
        for x in (-1,9):
            with self.assertRaises(ValueError):exp_interval(x)
    def test_exp_float_bool_and_bits_refusal(self):
        for x in (0.5,True):
            with self.assertRaises(ValueError):exp_interval(x)
        with self.assertRaises(ValueError):exp_interval(1,bits=0)
    def test_known_zero_feedback_preserves_nominal(self):
        r=envelope(**args());self.assertEqual(r['radius'],0);self.assertEqual(r['interval'],(F(-2,5),F(-2,5)))
    def test_positive_source_feedback_has_nonzero_radius(self):
        r=envelope(**args(kA=1));self.assertGreater(r['radius'],F(3,10));self.assertLess(r['radius'],F(33,100))
    def test_shared_rate_weight_not_double_counted(self):
        r=envelope(**args(kA=2,kR='1/4'));self.assertEqual(r['xi'],F(5,4))
    def test_missing_inputs_are_not_zero(self):
        for key in ('kA','kR','q_limit'):
            r=envelope(**args(**{key:None}));self.assertEqual(r['status'],'INPUT_REQUIRED');self.assertIsNone(r['interval']);self.assertFalse(r['admitted'])
    def test_tube_failure_blocks_negative_admission(self):
        r=envelope(**args(kR='1/100',q_limit='1/4'))
        self.assertEqual(r['status'],'TUBE_NOT_CERTIFIED');self.assertFalse(r['admitted'])
    def test_tube_equality_is_not_strict(self):
        self.assertEqual(envelope(**args(q_limit='1/2'))['status'],'TUBE_NOT_CERTIFIED')
    def test_sign_loss_is_inconclusive(self):
        r=envelope(**args(kR=1));self.assertEqual(r['status'],'SIGN_UNRESOLVED');self.assertFalse(r['admitted'])
    def test_gain_zero_and_one_supported(self):
        self.assertEqual(envelope(**args(G=0,nominal=(0,0)))['interval'],(F(0),F(0)))
        self.assertGreater(envelope(**args(G=1,kA='1/10'))['radius'],0)
    def test_gain_above_one_refused(self):
        with self.assertRaises(ValueError):envelope(**args(G=2))
    def test_bad_domain_inputs_refused(self):
        for changes in ({'D':-1},{'n0':0},{'Z':-1},{'kA':-1},{'kR':-1},{'q_limit':0},{'G':-1}):
            with self.assertRaises(ValueError):envelope(**args(**changes))
    def test_new_bounds_reject_float_and_bool(self):
        for changes in ({'kA':0.1},{'G':True}):
            with self.assertRaises(ValueError):envelope(**args(**changes))
    def test_zero_duration_has_exact_zero_output(self):
        r=envelope(**args(D=0,nominal=(0,0),kA=3,kR=4));self.assertEqual(r['interval'],(F(0),F(0)))
        with self.assertRaises(ValueError):envelope(**args(D=0))
    def test_zero_initial_state_stays_zero(self):
        r=envelope(**args(Z=0,nominal=(0,0),kA=2,kR=3));self.assertEqual(r['radius'],0)
    def test_nominal_interval_order_required(self):
        with self.assertRaises(ValueError):envelope(**args(nominal=(2,1)))
    def test_root_encloses_log2(self):
        lo,hi=threshold_bracket(1,1)
        with localcontext() as c:
            c.prec=70;r=Decimal(2).ln()
            self.assertLessEqual(dec(lo),r);self.assertGreaterEqual(dec(hi),r)
        self.assertLessEqual(hi-lo,F(1,2**40))
    def test_zero_margin_has_zero_threshold(self):self.assertEqual(threshold_bracket(0,1),(F(0),F(0)))
    def test_root_outside_implemented_domain_refused(self):
        with self.assertRaises(ValueError):threshold_bracket(10000,1)
    def test_density_scaling(self):
        a=envelope(**args(kA='1/3'));b=envelope(**args(n0=10,nominal=(-4,-4),kA='1/3'))
        self.assertEqual(b['radius'],10*a['radius']);self.assertEqual(b['interval'],tuple(10*x for x in a['interval']))
    def test_no_artificial_small_gain_failure(self):
        r=envelope(**args(kR=2));self.assertEqual(r['xi'],2);self.assertGreater(r['radius'],3);self.assertEqual(r['status'],'SIGN_UNRESOLVED')

if __name__=='__main__':unittest.main(verbosity=2)
