from pathlib import Path
import sys, unittest, math
from fractions import Fraction as F
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'code'))
from frozen import source_number,response_row,box_linear,assemble

def args(**changes):
 p=dict(B=[[3,-1],[-1,2]],n0=5,Rb=1,X=[[-1,-1],[-2,-2]],Dlo=2,Dhi=2,K=3,Rhi=1,alphaA=F(1,10),LA=F(1,20),alphaR=F(1,30),LR=F(1,40))
 p.update(changes);return p
class Tests(unittest.TestCase):
 def test_response_row_exact(self):self.assertEqual(response_row([[3,-1],[-1,2]],5,1),[F(1),F(3)])
 def test_row_inverse_identity(self):
  w=response_row([[5,-2],[-1,4]],7,2)
  self.assertEqual([5*w[0]-w[1],-2*w[0]+4*w[1]],[0,14])
 def test_binary64_source(self):self.assertEqual(source_number(.1),F.from_float(.1))
 def test_decimal_source(self):self.assertEqual(source_number('0.1'),F(1,10))
 def test_nonfinite_bool_source_refused(self):
  for x in [True,None,float('inf'),float('nan')]:
   with self.subTest(x=x),self.assertRaises(ValueError):source_number(x)
 def test_wrong_matrix_shape(self):
  with self.assertRaises(ValueError):response_row([[1]],1,1)
 def test_wrong_offdiagonal(self):
  with self.assertRaises(ValueError):response_row([[3,1],[-1,2]],1,1)
 def test_nonpositive_column_gap(self):
  with self.assertRaises(ValueError):response_row([[1,-1],[-1,1]],1,1)
 def test_negative_density_rate(self):
  for n,r in [(-1,1),(1,-1)]:
   with self.subTest(n=n,r=r),self.assertRaises(ValueError):response_row([[3,-1],[-1,2]],n,r)
 def test_signed_linear_box(self):self.assertEqual(box_linear([-1,2],[[1,2],[3,4]]),(F(4),F(7)))
 def test_reversed_box_refused(self):
  with self.assertRaises(ValueError):box_linear([1,2],[[2,1],[3,4]])
 def test_zero_duration(self):self.assertEqual(assemble(**args(Dlo=0,Dhi=0))['interval'],(F(0),F(0)))
 def test_zero_population(self):
  r=assemble(**args(X=[[0,0],[0,0]]));self.assertEqual((r['interval'],r['variation'],r['tail']),((F(0),F(0)),0,0))
 def test_frozen_law_has_tail(self):
  r=assemble(**args(alphaA=0,LA=0,alphaR=0,LR=0));self.assertEqual(r['variation'],0);self.assertGreater(r['tail'],0);self.assertEqual(r['center_box'],(-7,-7))
 def test_variation_components(self):
  r=assemble(**args());self.assertEqual(r['variation_A'],F(27,20));self.assertEqual(r['variation_R'],F(7,8));self.assertEqual(r['variation'],F(89,40))
 def test_derivative_not_discarded(self):
  r=assemble(**args(alphaA=0,alphaR=0));self.assertGreater(r['variation'],0)
 def test_invalid_bounds_refused(self):
  for k in ['Dlo','Dhi','K','Rhi','alphaA','LA','alphaR','LR']:
   with self.subTest(k=k),self.assertRaises(ValueError):assemble(**args(**{k:-1}))
 def test_invalid_time_order(self):
  with self.assertRaises(ValueError):assemble(**args(Dlo=3,Dhi=2))
 def test_shared_kernel_domain(self):
  with self.assertRaises(ValueError):assemble(**args(K=6))
 def test_zero_actual_output(self):self.assertEqual(assemble(**args(Rb=0,Rhi=0))['interval'],(F(0),F(0)))
if __name__=='__main__':unittest.main(verbosity=2)
