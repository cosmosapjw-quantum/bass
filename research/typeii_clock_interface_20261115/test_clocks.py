import unittest,importlib.util
from pathlib import Path
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.integrate import solve_ivp,quad
class Contract(unittest.TestCase):
 def module(self):
  p=Path(__file__).with_name('clocks.py');self.assertTrue(p.exists(),'pure clock/radiation interface not yet implemented')
  s=importlib.util.spec_from_file_location('clocks',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
 def test_zero_tilt(self):
  m=self.module();k=m.kinematics(2.,0.,.3)
  self.assertEqual(k['Gamma'],1.);self.assertEqual(k['theta'],6.);self.assertEqual(m.reaction_rhs(7.,k),3.5)
  self.assertEqual(m.thermal_rhs(10.,12.,3.,0.,k),-17.)
 def test_invalid_inputs(self):
  m=self.module()
  for h,b,bp in [(0.,0.,0.),(-1.,0.,0.),(1.,1.,0.),(1.,-1.,0.),(1.,np.nan,0.),(1.,.1,np.inf)]:
   with self.assertRaises(ValueError):m.kinematics(h,b,bp)
  with self.assertRaises(ValueError):m.directional_temperature(2.,.1,1.01)
 def test_number_continuity(self):
  m=self.module();t=np.linspace(0.,1.,31);b=.2*np.exp(-.3*t);bp=-.3*b
  k=m.kinematics(np.ones_like(t)*2,b,bp)
  derivative=-3-k['L'];self.assertLess(np.max(abs(-k['Gamma']*2*derivative-k['theta'])),2e-14)
 def test_proper_decay(self):
  m=self.module();beta=.4;h=2.;lam=.7;k=m.kinematics(h,beta,0.)
  s=solve_ivp(lambda t,x:m.reaction_rhs(-lam*x,k),(0,2),[1.],rtol=1e-11,atol=1e-13)
  self.assertAlmostEqual(s.y[0,-1],np.exp(-lam*2*np.sqrt(1-beta**2)/h),places=10)
 def test_exact_adiabatic(self):
  m=self.module();beta=lambda t:.3*np.exp(-.2*t)
  s=solve_ivp(lambda t,y:m.thermal_rhs(y,0.,0.,0.,m.kinematics(1.,beta(t),-.2*beta(t))),(0,1),[100.],rtol=2e-11,atol=1e-12)
  g=lambda t:1/np.sqrt(1-beta(t)**2)
  self.assertAlmostEqual(s.y[0,-1],100*np.exp(-2)*(g(1)/g(0))**(-2/3),places=8)
 def test_tracking_not_equilibrium(self):
  m=self.module();k=m.kinematics(2.,.2,-.03);T=m.tracking_temperature(100.,20.,0.,k)
  self.assertAlmostEqual(m.thermal_rhs(T,100.,20.,0.,k),-T,places=12)
 def test_implicit_and_parity(self):
  m=self.module();k=m.kinematics(1.,.1,-.02);rev=m.kinematics(1.,-.1,.02)
  self.assertEqual(k,rev);dt=.01;old=100.;new=m.implicit_temperature(old,90.,4.,0.,k,dt)
  self.assertAlmostEqual((new-old)/dt,m.thermal_rhs(new,90.,4.,0.,k),places=10)
 def test_radiation_moments(self):
  m=self.module();mu,w=leggauss(128)
  for beta in (0.,.05,-.05,.4,-.6):
   v=m.directional_temperature(1.,beta,mu);moms=m.radiation_moments(beta)
   self.assertAlmostEqual(float(np.dot(w,v**3)/2),moms['number_ratio'],places=12)
   self.assertAlmostEqual(float(np.dot(w,v**4)/2),moms['energy_ratio'],places=12)
   self.assertAlmostEqual(float(np.dot(w,mu*v**4)/2),moms['flux_ratio'],places=12)
 def test_lorentz_tensor(self):
  m=self.module();beta=.3;g=1/np.sqrt(1-beta**2);B=np.eye(4);B[0,0]=B[1,1]=g;B[0,1]=B[1,0]=-g*beta
  R=B@np.diag([1.,1/3,1/3,1/3])@B.T;a=m.radiation_moments(beta)
  self.assertAlmostEqual(R[0,0],a['energy_ratio']);self.assertAlmostEqual(R[0,1],a['flux_ratio']);self.assertAlmostEqual(R[1,1],a['parallel_pressure_ratio'])
 def test_no_scalar_blackbody_replacement(self):
  m=self.module();a=m.radiation_moments(.2)
  self.assertGreater(abs(a['energy_ratio']**.75-a['number_ratio']),1e-3)
if __name__=='__main__':unittest.main(verbosity=2)
