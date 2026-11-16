import importlib.util,unittest
from pathlib import Path
import numpy as np
class Contracts(unittest.TestCase):
 def m(self):
  p=Path(__file__).with_name('cascade.py');self.assertTrue(p.is_file(),'cascade implementation absent')
  s=importlib.util.spec_from_file_location('cascade',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
 def test_E1_2p1s_radial(self):
  m=self.m();self.assertAlmostEqual(m.radial_exact((2,1),(1,0)),256/(81*np.sqrt(6)),places=12)
 def test_E1_selection(self):
  m=self.m();self.assertEqual(len(m.lines()),5)
  with self.assertRaises(ValueError):m.einstein_A((2,0),(1,0))
 def test_E1_thermal(self):
  m=self.m();a=m.line_rates((3,1),(2,0),3000,0)
  self.assertAlmostEqual(np.log(a['up']/a['down']),np.log(3)-a['gap_J']/(m.KB*3000),places=11)
 def test_two_photon_vacuum(self):
  m=self.m();d=m.two_photon(3000,0,vacuum=True);self.assertAlmostEqual(d['down'],8.2206,places=12);self.assertEqual(d['up'],0.)
 def test_two_photon_thermal(self):
  m=self.m();d=m.two_photon(3000,0);self.assertAlmostEqual(np.log(d['up']/d['down']),-d['gap_J']/(m.KB*3000),places=11)
 def test_pair_quadrupole(self):
  m=self.m();a=m.pair_average(.1*m.EV,.2*m.EV,3000,.05)
  b=m.pair_average(.1*m.EV,.2*m.EV,3000,.05,direct=True)
  self.assertLess(abs(a/b-1),2e-12)
 def test_beta_even(self):
  m=self.m();a=m.two_photon(3000,.05);b=m.two_photon(3000,-.05);self.assertLess(abs(a['up']/b['up']-1),1e-12)
 def test_generator_schur(self):
  m=self.m();n=m.network(3000,3000,.05,1e8);e=m.eliminate(n['Q']);s=e['S'];off=s.copy();np.fill_diagonal(off,0)
  self.assertGreaterEqual(off.min(),0);self.assertLess(max(abs(s.sum(axis=0)))/max(abs(s).flat),1e-12)
 def test_exit_probabilities(self):
  m=self.m();e=m.eliminate(m.network(3000,3000,.05,1e8)['Q']);self.assertLess(max(abs(e['P'].sum(axis=0)-1)),1e-12)
 def test_thermal_population(self):
  m=self.m();n=m.network(3000,3000,0,1e8);p=m.stationary(n['Q'],n['reference_weights']);self.assertLess(max(abs(p/n['reference_weights']-1)),1e-9)
 def test_reconstructed_stationary(self):
  m=self.m();n=m.network(3000,3000,.05,1e8);e=m.eliminate(n['Q']);full=m.stationary(n['Q'],n['reference_weights']);red=m.stationary(e['S'],n['reference_weights'][m.RETAINED]);lift=m.lift(e,red);lift/=sum(lift);self.assertLess(max(abs(lift/full-1)),1e-9)
 def test_energy_ledger(self):
  m=self.m();n=m.network(3000,3000,.05,1e8);p=np.arange(1,8,dtype=float);p/=sum(p);q=m.energy(n,p);self.assertLess(q['relative_residual'],1e-12)
 def test_BE_cycle_not_reversible(self):
  m=self.m();self.assertAlmostEqual(m.cycle_affinity(3000,0,eta=.3),.6,places=11)
 def test_invalid_inputs(self):
  m=self.m()
  for a in [(-1,3000,0,1e8),(3000,-1,0,1e8),(3000,3000,1,1e8),(3000,3000,0,-1)]:
   with self.assertRaises(ValueError):m.network(*a)
 def test_slow_column_conservation(self):
  m=self.m();q=m.network(3000,3000,.05,1e8)['Q'].copy();q[0,0]*=2
  with self.assertRaises(ValueError):m.eliminate(q)
 def test_stationary_weight_contract(self):
  m=self.m();q=m.network(3000,3000,.05,1e8)['Q']
  for w in (np.zeros(7),np.r_[np.nan,np.ones(6)],np.ones(6)):
   with self.assertRaises(ValueError):m.stationary(q,w)
if __name__=='__main__':unittest.main(verbosity=2)
