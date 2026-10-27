"""Focused new controls. No old driver or old test suite is invoked."""
import sys,unittest,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'code'))
from reconstruct import *
class Controls(unittest.TestCase):
 def test_rk4_identity(self):
  # Independent coupled RK4 stages x'=v, v'=-x-.3v.
  z=np.array([.2,.7]);d=.03
  f=lambda a:np.array([a[1],-a[0]-.3*a[1]])
  a=f(z);b=f(z+d*a/2);c=f(z+d*b/2);dd=f(z+d*c);end=z+d*(a+2*b+2*c+dd)/6
  self.assertAlmostEqual(end[0],z[0]+d*(z[1]+end[1])/2+d*d*(a[1]-dd[1])/12,places=15)
 def inputs(self):
  read=lambda n:json.loads((OLD/'inputs/b3c/raw'/n).read_text())
  return read('ISO_N256_PATH.json')[0],read('ISO_N256_SOURCE_HISTORY.json')[0],read('VALIDATION.json')['fixtures'][0]
 def test_stage_refusal(self):
  ep,b,f=self.inputs();ep['h']=2
  with self.assertRaises(ValueError):midpoint(ep,b,f)
 def test_duration_and_stf(self):
  ep,b,f=self.inputs();m=midpoint(ep,b,f);b['interval_end_tau']+=1
  alt=midpoint(ep,b,f);np.testing.assert_array_equal(m['coordinates'],alt['coordinates'])
  self.assertEqual(m['analytic'][3],sum(m['analytic'][1:3]));self.assertEqual(sum(m['coordinates'][1:]),0)
 def test_q14_birth(self):
  finite,_=reused_modules();S=np.diag([.15,-.05,-.10]);v=finite.p.moments(S,np.eye(3),*q14())
  np.testing.assert_allclose(v['P'],np.eye(3)/3+2*S/15,rtol=0,atol=ROUND)
 def test_isotropic_scaling_and_dilution(self):
  finite,_=reused_modules();p=finite.p;T=p.moments(np.zeros((3,3)),.7*np.eye(3),*q14())['T']*.7**3
  self.assertAlmostEqual(T[0,0],.7**4);self.assertGreater(abs(T[0,0]-.7),.1)
 def test_beta_sign_detectable(self):
  finite,_=reused_modules();p=finite.p;beta=np.array([.1,-.04,-.06]);S=np.diag([.1,-.03,-.07])
  a=p.moments(S,np.diag(np.exp(-.2-beta)),*q14())['T'];b=p.moments(S,np.diag(np.exp(-.2+beta)),*q14())['T']
  self.assertGreater(np.linalg.norm(a-b),.01)
 def test_missing_physical(self):
  finite,_=reused_modules();self.assertEqual(finite.ball(np.zeros((3,3)),.8*np.eye(3),1,0)['status'],'INPUT_ERROR_UNSPECIFIED')
 def test_underflow_refused(self):
  with self.assertRaises(ValueError):diagonal_bound(np.full(3,1000.),np.zeros(3))
 def test_aniso_stf_reconstruction(self):
  read=lambda n:json.loads((OLD/'inputs/b3c/raw'/n).read_text())
  m=midpoint(read('ANISO_N256_PATH.json')[0],read('ANISO_N256_SOURCE_HISTORY.json')[0],read('VALIDATION.json')['fixtures'][1])
  self.assertGreater(abs(m['coordinates'][1]),0)
  self.assertEqual(sum(m['coordinates'][1:]),0)
 def test_near_cancellation_equation_scale(self):
  self.assertLess(abs(normalize_residual(2e-16,2.)),ROUND)
  np.testing.assert_array_equal(normalize_residual(np.zeros(3),0),np.zeros(3))
  with self.assertRaises(ArithmeticError):normalize_residual(1e-30,0)
if __name__=='__main__':unittest.main()
