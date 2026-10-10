import unittest
from readback import HEADER, parse_cells, reference

H=','.join(HEADER)+'\n'

class IntakeTests(unittest.TestCase):
    def test_literal_header_erratum(self):
        self.assertEqual(len(parse_cells(b't0_s,t1_s,mean_z0,mean_z1,ne_eff_m3,delta_tau\n0,1,1,0,0,0\n',1)),1)
        with self.assertRaises(ValueError):
            parse_cells(b't0,t1,z0,z1,ne_eff,delta_tau\n0,1,1,0,0,0\n',1)
    def test_rejections(self):
        for body in ['0,1,1,0,-1,0','0,1,1,0,NaN,0','0,1,1,0,1',
                     '1,0,1,0,1,0','0,1,1,0,1,0\n2,3,0,0,1,0',
                     '1,2,1,0,1,0\n0,1,1,0,1,0']:
            with self.assertRaises(ValueError):
                parse_cells((H+body+'\n').encode(),len(body.splitlines()))
        with self.assertRaises(ValueError): parse_cells((H+'0,1,1,0,1,0\n').encode())
        with self.assertRaises(ValueError): parse_cells(b'wrong\n',0)

    def test_zero_exact(self):
        rows=parse_cells((H+'0,1,1,0,0,0\n1,2,0,0,0,0\n').encode(),2)
        ds,t,s,p,b,_,_=reference(rows)
        self.assertEqual(ds,[0,0]); self.assertEqual(t,[0,0,0])
        self.assertEqual(s,[1,1,1]); self.assertEqual(p,[0,0]); self.assertEqual(b,0)

if __name__=='__main__': unittest.main()
