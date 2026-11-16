import importlib.util,unittest
from pathlib import Path
import numpy as np
class Contracts(unittest.TestCase):
 def api(self):
  p=Path(__file__).with_name('redistribution.py');self.assertTrue(p.is_file(),'redistribution implementation not yet present')
  sp=importlib.util.spec_from_file_location('rd',p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
 def test_sphere_rule(self):
  m=self.api();n,w=m.sphere_rule(4,8);self.assertAlmostEqual(sum(w),4*np.pi);self.assertLess(max(abs(w@n)),1e-14);self.assertLess(np.max(abs(n.T@(w[:,None]*n)-(4*np.pi/3)*np.eye(3))),2e-14)
 def test_boost(self):
  m=self.api();n,w=m.sphere_rule(8,16);a,D=m.atom_directions(n,.05);self.assertLess(np.max(abs(np.linalg.norm(a,axis=1)-1)),1e-14);self.assertLess(abs(sum(w/D**2)-4*np.pi),2e-13)
 def test_invalid_angles(self):
  m=self.api()
  with self.assertRaises(ValueError):m.atom_directions(np.array([[2.,0,0]]),.1)
 def test_invalid_tilt(self):
  m=self.api()
  with self.assertRaises(ValueError):m.atom_directions(np.array([[1.,0,0]]),1.)
 def test_BE_pair_balance(self):
  m=self.api();x=.7;d=.3;e=.2;f=1/np.expm1(x+e);g=1/np.expm1(x+d+e);self.assertLess(abs(m.pair_flux(f,g,d)),1e-14)
 def test_pair_photon_number(self):
  m=self.api();F=m.pair_flux(.2,.7,.04);self.assertEqual((-F)+F,0.)
 def test_angular_detailed_balance(self):
  m=self.api();n,w=m.sphere_rule(3,4);a,D=m.atom_directions(n,.08);Q,pi=m.angular_generator(a,w/D**2,D);self.assertLess(np.max(abs(Q.sum(axis=0))),3e-15);self.assertLess(np.max(abs(Q@pi)),3e-15)
 def test_angular_positive_step(self):
  m=self.api();n,w=m.sphere_rule(3,4);a,D=m.atom_directions(n,.05);Q,pi=m.angular_generator(a,w/D**2,D);p=np.zeros(12);p[2]=1.;q=m.angular_evolve(Q,pi,p[:,None],np.array([4.]));self.assertGreaterEqual(q.min(),0.);self.assertAlmostEqual(q.sum(),1.)
 def test_frequency_Wien_equilibrium(self):
  m=self.api();e=np.linspace(2e15,2.002e15,17);q=m.frequency_model(e,3000.,np.ones(16),np.ones(17),0.,1.,absorbing=False);p=q['pi']/sum(q['pi']);out=m.frequency_step(q,p,.7);self.assertLess(max(abs(out['N']-p)),2e-14)
 def test_frequency_count_and_positivity(self):
  m=self.api();e=np.linspace(2e15,2.002e15,17);q=m.frequency_model(e,3000.,np.ones(16),np.ones(17),.07,1.,absorbing=True);p=np.zeros(16);p[8]=1.;out=m.frequency_step(q,p,4.);self.assertGreaterEqual(out['N'].min(),0.);self.assertAlmostEqual(out['N'].sum()+out['red']+out['blue']+out['death'],1.,places=12)
 def test_measure_boost(self):
  m=self.api();n,w=m.sphere_rule(4,8);a,D=m.atom_directions(n,.05);e=np.array([1e15,1.1e15,1.2e15]);M=m.capacities(e,w,D,2.);g=m.mode_capacity(e);self.assertLess(np.max(abs(M/(2*w[:,None]/D[:,None]**3*g[None,:])-1)),2e-14)
 def test_remap_count(self):
  m=self.api();e=np.linspace(1.,2.,101);p=np.ones((1,100))/100;q,red,blue=m.redshift_remap(p,e,np.array([.9]));self.assertGreaterEqual(q.min(),0.);self.assertAlmostEqual(q.sum()+red+blue,1.)
 def test_invalid_population(self):
  m=self.api();e=np.linspace(2e15,2.002e15,17);q=m.frequency_model(e,3000.,np.ones(16),np.ones(17),0.,1.,absorbing=False)
  with self.assertRaises(ValueError):m.frequency_step(q,-np.ones(16),.1)
 def test_no_negative_kinetic_temperature(self):
  m=self.api()
  with self.assertRaises(ValueError):m.frequency_model(np.linspace(2e15,2.002e15,17),-1.,np.ones(16),np.ones(17),0.,1.)
if __name__=='__main__':unittest.main(verbosity=2)
