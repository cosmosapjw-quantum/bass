import sys,unittest
from pathlib import Path
from fractions import Fraction as F
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'code'))
from general import Context,response,combine,energy_rows,source_number
ZERO=(0,0)
def context(**kw):
 d=dict(B=((2,0),(0,3)),X=((1,1),(2,2)),Dlo=2,Dhi=2,gamma=2,alphaM=0,LM=0,theta=(0,0),Tlo=2,Rb=1,Rhi=2,alphaR=0,LR=0)
 d.update(kw);return Context(**d)
class Tests(unittest.TestCase):
 def test_constant_resolvent(self):self.assertEqual(response(context(),((2,3),(2,3),ZERO))['center_box'],(F(3),F(3)))
 def test_zero_time(self):self.assertEqual(response(context(Dlo=0,Dhi=0),((2,3),(2,3),ZERO))['interval'],(F(0),F(0)))
 def test_zero_state(self):self.assertEqual(response(context(X=((0,0),(0,0))),((2,3),(2,3),ZERO))['radius'],0)
 def test_zero_row(self):self.assertEqual(response(context(),(ZERO,ZERO,ZERO))['interval'],(F(0),F(0)))
 def test_signed_row(self):self.assertEqual(response(context(),((2,-3),(2,-3),ZERO))['center_box'],(F(-1),F(-1)))
 def test_mixed_box(self):self.assertEqual(response(context(X=((-1,2),(-2,3))),((2,-3),(2,-3),ZERO))['center_box'],(F(-4),F(4)))
 def test_negative_state_sign(self):self.assertLessEqual(response(context(X=((-2,-1),(-3,-2))),((1,2),(2,1),ZERO))['interval'][1],0)
 def test_row_reversal(self):
  c=context();a=response(c,((2,3),(2,3),ZERO));b=response(c,((-2,-3),(-2,-3),ZERO));self.assertEqual(b['interval'],(-a['interval'][1],-a['interval'][0]))
 def test_cancel_before_norm(self):self.assertEqual(combine([((2,3),(4,5),ZERO),((-2,-3),(-4,-5),ZERO)]),((F(0),F(0)),)*3)
 def test_energy_pairing(self):self.assertEqual(energy_rows((3,0),(5,0),1,4,1,1),((F(3),F(0)),(F(20),F(0)),(F(0),F(0))))
 def test_wrong_energy_product_detected(self):
  r=energy_rows((3,0),(5,0),1,4,1,1);correct=(r[0][0]+r[1][0])/2;self.assertEqual(correct,F(23,2));self.assertNotEqual(correct,F(5,2)*4)
 def test_binary64_semantics(self):self.assertEqual(source_number(.1),F.from_float(.1));self.assertNotEqual(source_number(.1),F(1,10))
 def test_bad_float(self):
  with self.assertRaises(ValueError):source_number(float('nan'))
 def test_bool(self):
  with self.assertRaises(ValueError):source_number(True)
 def test_singular(self):
  with self.assertRaises(ValueError):context(B=((1,-1),(-1,1)))
 def test_wrong_offdiag(self):
  with self.assertRaises(ValueError):context(B=((2,1),(0,3)))
 def test_bad_horizon(self):
  with self.assertRaises(ValueError):context(Dlo=3,Dhi=2)
 def test_bad_box(self):
  with self.assertRaises(ValueError):context(X=((2,1),(2,2)))
 def test_rate_outside_box(self):
  with self.assertRaises(ValueError):context(Rb=3)
 def test_derivative_not_omitted(self):self.assertGreater(response(context(LM=1),((2,3),(2,3),ZERO))['operator_error'],0)
 def test_row_variation_not_omitted(self):self.assertGreater(response(context(),((2,3),(4,5),ZERO))['row_error'],0)
 def test_finite_tail(self):self.assertGreater(response(context(),((2,3),(2,3),ZERO))['tail'],0)
if __name__=='__main__':unittest.main(verbosity=2)
