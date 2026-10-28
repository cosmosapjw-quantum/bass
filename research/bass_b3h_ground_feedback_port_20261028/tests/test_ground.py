import sys,unittest
from pathlib import Path
from fractions import Fraction as F
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'code'))
from ground import port,envelope

def args(**kw):
 d=dict(n0=2,Rhi=1,gamma=2,gmin=2,Pbound=1,X=[('-1/10','-1/10'),('-1/5','-1/5')],p_initial=['2/5','3/5'],nominal=('-1/5','-1/10'),D=1,reference_valid=True)
 d.update(kw);return d
class GroundTests(unittest.TestCase):
 def test_incoming_product_exact(self):self.assertEqual(port(2,3,'-1/2',4,'1/7')['incoming'],F(6,7))
 def test_signed_rate_feedback(self):
  p=port(2,3,'-1/2',4,0);self.assertEqual(p['Rhat'],F(4,5));self.assertEqual(p['s'],F(8,15))
 def test_zero_feedback(self):self.assertEqual(port(2,3,0,4,0)['s'],0)
 def test_positive_q_rate_sign(self):self.assertLess(port(2,3,1,4,0)['s'],0)
 def test_singular_denominator_refused(self):
  for q in [-3,-4]:
   with self.assertRaises(ValueError):port(2,3,q,4,0)
 def test_negative_phat_or_C_refused(self):
  with self.assertRaises(ValueError):port(-1,2,0,1,0)
  with self.assertRaises(ValueError):port(1,2,0,-1,0)
 def test_native_scalar_formula(self):
  r=envelope(**args());self.assertEqual(r['Z'],F(3,10));self.assertEqual(r['B'],F(3,20));self.assertEqual(r['kR'],F(20,37));self.assertEqual(r['added_upper'],F(6,37))
 def test_lower_endpoint_unchanged(self):self.assertEqual(envelope(**args())['interval'][0],F(-1,5))
 def test_upper_endpoint_respects_restoring_sign(self):self.assertEqual(envelope(**args())['interval'][1],0)
 def test_short_horizon_strict_negative(self):self.assertEqual(envelope(**args(D='1/100'))['status'],'NEGATIVE_CONDITIONAL_GROUND_PORT')
 def test_initial_positive_path_required(self):
  with self.assertRaises(ValueError):envelope(**args(p_initial=[0,1]))
 def test_mixed_sign_box_refused(self):
  with self.assertRaises(ValueError):envelope(**args(X=[('-1/10','1/10'),('-1/5','-1/5')]))
 def test_reversed_box_refused(self):
  with self.assertRaises(ValueError):envelope(**args(X=[(0,-1),(-1,0)]))
 def test_ground_gap_strict(self):
  for v in ['3/10','1/4']:
   with self.assertRaises(ValueError):envelope(**args(gmin=v))
 def test_missing_input_is_not_zero(self):
  for k in ['Pbound','gmin','reference_valid']:
   r=envelope(**args(**{k:None}));self.assertEqual(r['status'],'INPUT_REQUIRED');self.assertIsNone(r['interval'])
 def test_invalid_reference_not_admitted(self):
  with self.assertRaises(ValueError):envelope(**args(reference_valid=False))
 def test_G_above_one_refused(self):
  with self.assertRaises(ValueError):envelope(**args(Rhi=3))
 def test_zero_horizon(self):
  r=envelope(**args(D=0,nominal=(0,0)));self.assertEqual(r['interval'],(F(0),F(0)))
  with self.assertRaises(ValueError):envelope(**args(D=0))
 def test_zero_initial_reset(self):self.assertEqual(envelope(**args(X=[(0,0),(0,0)],nominal=(0,0)))['added_upper'],0)
 def test_zero_rate(self):self.assertEqual(envelope(**args(Rhi=0,nominal=(0,0)))['interval'],(F(0),F(0)))
 def test_invalid_scalar_refusal(self):
  for kw in [{'gamma':0},{'D':-1},{'Pbound':-1},{'Pbound':'1/2'},{'n0':0},{'Rhi':-1}]:
   with self.assertRaises(ValueError):envelope(**args(**kw))
 def test_float_bool_rejected(self):
  for kw in [{'D':1.0},{'gmin':True}]:
   with self.assertRaises(ValueError):envelope(**args(**kw))
 def test_density_scaling(self):
  a=envelope(**args(D='1/100'));b=envelope(**args(n0=20,nominal=(-2,-1),D='1/100'))
  self.assertEqual(b['added_upper'],10*a['added_upper']);self.assertEqual(b['interval'],tuple(10*x for x in a['interval']))
 def test_domain_and_physical_claim_separate(self):
  r=envelope(**args());self.assertTrue(r['denominator_nonexit']);self.assertFalse(r['physical_admitted'])
if __name__=='__main__':unittest.main(verbosity=2)
