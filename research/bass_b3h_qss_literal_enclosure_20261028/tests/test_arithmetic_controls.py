"""Additional tests-after controls; not labelled an extra RED/GREEN cycle."""
from fractions import Fraction as F
from pathlib import Path
import sys,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'code'))
from enclosure import I
class ArithmeticControls(unittest.TestCase):
    def test_signed_operations_exact_samples(self):
        for x in (F(-7,3),F(-1,9),F(1,11),F(13,7)):
            for y in (F(-2,5),F(1,13),F(8,3)):
                a=I.point(x,128);b=I.point(y,128)
                for v,z in ((a+b,x+y),(a-b,x-y),(a*b,x*y),(a/b,x/y)):
                    l,h=v.pair();self.assertLessEqual(l,z);self.assertGreaterEqual(h,z)
    def test_mixed_precision_refusal(self):
        with self.assertRaises(ValueError):I.point(1,128)+I.point(1,256)
    def test_zero_denominator_refusal(self):
        with self.assertRaises(ValueError):I(-1,1,128).reciprocal()
    def test_literal_source_semantics(self):
        b=I.point(F.from_float(.13),128);d=I.point('0.13',128)
        self.assertLess(d.hi,b.lo)
        with self.assertRaises(ValueError):I.point(.13,128)
    def test_exponential_domain_refusal(self):
        with self.assertRaises(ValueError):I.point(129,128).exp()
    def test_abs_crossing_and_empty_refusal(self):
        self.assertEqual(I(-7,3,128).abs(),I(0,7,128))
        with self.assertRaises(ValueError):I(3,2,128)
if __name__=='__main__':unittest.main(verbosity=2)
