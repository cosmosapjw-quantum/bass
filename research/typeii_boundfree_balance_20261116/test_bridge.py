import importlib.util,unittest
from pathlib import Path
import numpy as np
class Contracts(unittest.TestCase):
 def module(self):
  path=Path(__file__).with_name('boundfree.py');self.assertTrue(path.exists(),'level-resolved bridge not yet implemented')
  spec=importlib.util.spec_from_file_location('boundfree',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
 def test_source_states(self):
  m=self.module();self.assertEqual(len(m.LEVELS),55);self.assertEqual(m.LEVELS[2,1]['g'],3*m.LEVELS[2,0]['g'])
 def test_threshold(self):
  m=self.module();chi=m.LEVELS[2,0]['chi'];self.assertEqual(m.sigma(chi*.99,(2,0)),0.);self.assertGreater(m.sigma(chi,(2,0)),0.)
 def test_Milne_ratio(self):
  m=self.module();k=.3*m.EV;E=k+m.LEVELS[2,1]['chi'];expected=6*E*E/(2*m.ME*m.C*m.C*k)*m.sigma(E,(2,1));self.assertAlmostEqual(m.capture_sigma(k,(2,1))/expected,1.,places=13)
 def test_Planck_balance(self):
  m=self.module()
  for lev in [(1,0),(2,0),(2,1),(5,4),(10,9)]:
   r=m.rates(3000.,3000.,0.,lev);self.assertLess(abs(r['log_alpha']-r['log_photo']-m.log_saha(3000.,lev)),2e-10)
 def test_BE_chemical_balance(self):
  m=self.module();r=m.rates(3000.,3000.,0.,(5,0),eta=.7);self.assertLess(abs(r['log_alpha']-r['log_photo']-m.log_saha(3000.,(5,0))-.7),2e-10)
 def test_missing_stimulation_fails(self):
  m=self.module();r=m.rates(8000.,8000.,0.,(10,0));self.assertGreater(r['stimulated_fraction'],.05)
 def test_velocity_capture(self):
  m=self.module();r=m.rates(3000.,2800.,.05,(2,1));a=m.velocity_alpha(3000.,2800.,.05,(2,1));self.assertLess(abs(a/np.exp(r['log_alpha'])-1),2e-8)
 def test_degenerate_shell_ratio(self):
  m=self.module();a=m.rates(3000.,3000.,0.,(2,0));b=m.rates(3000.,3000.,0.,(2,1));ratio=np.exp(b['log_alpha']-b['log_photo']-a['log_alpha']+a['log_photo']);self.assertAlmostEqual(ratio,3.,places=10)
 def test_even_bulk_velocity(self):
  m=self.module();a=m.rates(3000.,2800.,.05,(2,0));b=m.rates(3000.,2800.,-.05,(2,0));self.assertAlmostEqual(a['log_alpha'],b['log_alpha'],places=12);self.assertAlmostEqual(a['log_photo'],b['log_photo'],places=12)
 def test_energy_ledger(self):
  m=self.module();r=m.rates(3000.,2800.,.05,(2,0));e=m.net_sources(r,2e5,3e7,3e7);scale=sum(abs(e[k]) for k in ('Q_photon','Q_kinetic','Q_ionization'));self.assertLess(abs(e['energy_residual'])/scale,1e-12);self.assertEqual(e['nucleus_residual'],0.)
 def test_zero_tilt_source_photon_integral(self):
  m=self.module();r=m.rates(3000.,3000.,0.,(1,0));self.assertGreater(np.exp(r['log_photo']),0.)
 def test_invalid(self):
  m=self.module()
  for args in [(0,3000,0,(2,0)),(3000,-1,0,(2,0)),(3000,3000,1.,(2,0)),(3000,3000,0,(2,2))]:
   with self.assertRaises(ValueError):m.rates(*args)
if __name__=='__main__':unittest.main(verbosity=2)
