import unittest,numpy as np
from radial import windows,finite_check,solve
from fisher import vectors,fisher
from optimize import construct,evaluate
class T(unittest.TestCase):
 def test_partition(self):
  w=windows(np.linspace(0,60,100),5);np.testing.assert_allclose(w.sum(axis=0),1,atol=1e-15);self.assertGreaterEqual(w.min(),0)
 def test_fd(self):self.assertLess(finite_check()['0.0001'],1e-7)
 def test_fisher(self):
  r=fisher(*vectors(),32);self.assertLess(abs(r['results']['full']['cosine']+.00108134508822),1e-9);self.assertTrue(all(x['condition']>=1 for x in r['results'].values()))
 def test_bound(self):
  M=np.array([[0.,2.,0.,0.],[-2.,0.,0.,0.],[0.,0.,0.,.3],[0.,0.,-.3,0.]])
  A,_=construct(M);v=evaluate(M,A);self.assertLess(v['projected'],1e-12);self.assertAlmostEqual(v['norm'],np.sqrt(5)*.3,places=12)
if __name__=='__main__':unittest.main()
