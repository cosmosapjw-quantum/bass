import sys,unittest
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal,localcontext
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'code'))
from enclosure import exp_bounds,sqrt_bounds,solve_2x2
class BasicTests(unittest.TestCase):
    def contains(self,I,v):self.assertLessEqual(I[0],v);self.assertGreaterEqual(I[1],v)
    def test_exp_zero(self):self.assertEqual(exp_bounds(F(0),128),(F(1),F(1)))
    def test_sqrt_exact(self):self.assertEqual(sqrt_bounds(F(4),128),(F(2),F(2)))
    def test_sqrt_irrational_squared(self):
        l,h=sqrt_bounds(F(2),128);self.assertGreater(l,0);self.assertLessEqual(l*l,2);self.assertGreaterEqual(h*h,2)
    def test_exp_signed_reference(self):
        with localcontext() as ctx:
            ctx.prec=180
            for x in (F(1,1000),F(-1,1000),F(40),F(-40)):
                I=exp_bounds(x,128);v=F((Decimal(x.numerator)/Decimal(x.denominator)).exp())
                self.contains(I,v)
    def test_exact_2state(self):
        q=solve_2x2([[F(3),F(-1)],[F(-2),F(4)]],[F(1),F(2)],128)
        self.contains(q[0],F(3,5));self.contains(q[1],F(4,5))
    def test_singular_refused(self):
        with self.assertRaises(ValueError):solve_2x2([[1,-1],[-1,1]],[1,1],128)
    def test_wrong_sign_refused(self):
        with self.assertRaises(ValueError):solve_2x2([[2,1],[-1,2]],[1,1],128)
    def test_negative_sqrt_refused(self):
        with self.assertRaises(ValueError):sqrt_bounds(F(-1),128)
if __name__=='__main__':unittest.main(verbosity=2)
