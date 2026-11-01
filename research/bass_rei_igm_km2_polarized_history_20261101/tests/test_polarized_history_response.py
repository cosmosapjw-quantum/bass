"""Original-source tests, independent source readback, falsification and scope guards."""
import csv,gzip,io,json,math,sys,unittest
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import polarized_history_response as r
from restore_source import ORIGINAL_SHA,HEAD

class PhysicalTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.report=json.loads((ROOT/'results/KM2_REI_POLARIZED_PHOTON_HISTORY_RESULT.json').read_text())
  with gzip.open(ROOT/'results/KM2_REI_POLARIZED_PHOTON_HISTORY_SKY_RESPONSE.csv.gz','rt') as f:cls.sky=list(csv.DictReader(f))
  with gzip.open(ROOT/'results/KM2_REI_POLARIZED_PHOTON_HISTORY_RAY_RESPONSE.csv.gz','rt') as f:cls.rays=list(csv.DictReader(f))
 def test_original_authority(self):
  self.assertEqual(self.report['source_owner_head'],HEAD)
  self.assertEqual(self.report['source_lock']['files'],ORIGINAL_SHA)
  self.assertEqual(len(ORIGINAL_SHA),9)
 def test_source_byte_hash_integrity(self):
  for k,v in ORIGINAL_SHA.items():
   with self.subTest(file=k):self.assertEqual(r.sha(ROOT/'source_inputs'/k),v)
 def test_current_scope_hold(self):
  self.assertEqual(self.report['BASS_upper'],'9/15 scoped/source-mapped')
  self.assertEqual(self.report['REI_central'],'28/88 reported')
  self.assertFalse(self.report['REI_history_injected'])
  self.assertFalse(self.report['production_ready'])
  self.assertEqual(self.report['original_Einstein_P8_Peebles_IVPs_new'],0)
 def test_original_photon_energy_and_polarization(self):
  self.assertEqual(len(self.report['cases']),10)
  for case in self.report['cases']:
   self.assertLess(case['original_rho_relative_gap'],2e-12)
   self.assertLess(case['original_polarization_absolute_gap'],2e-12)
   if case['k']==40:self.assertLess(case['original_screen_relative_gap'],2e-12)
 def test_no_unphysical_history_rows(self):
  self.assertEqual(self.report['ray_response_rows'],96000)
  self.assertEqual(self.report['sky_response_rows'],240)
  self.assertEqual(len(self.sky),240)
  self.assertEqual(len(self.rays),96000)
  for x in self.sky:
   self.assertGreater(float(x['rho_first_one']),0)
   self.assertTrue(0<float(x['pol_fraction'])<1)
   self.assertLess(int(x['electron_panel']),int(x['observer_k']))
 def test_finite_difference_comparisons(self):
  self.assertEqual(len(self.report['finite_difference_controls']),8)
  for c in self.report['finite_difference_controls']:
   with self.subTest((c['gl'],c['mode'])):
    self.assertLess(max(abs(v) for v in c['abs_error'][1:]),2e-9)
    rho=next(t['original_sky_energy'] for t in self.report['cases'] if t['gl']==c['gl'] and t['k']==40)
    self.assertLess(abs(c['abs_error'][0])/rho,2e-9)
 def test_uniform_mode_sums_and_physical_chronology(self):
  for gl in (12,16):
   x=next(c for c in self.report['cases'] if c['gl']==gl and c['k']==40)
   a=[p for p in self.sky if int(p['observer_k'])==40 and p['GL']==f'GL{gl}']
   self.assertEqual(len(a),40)
   self.assertAlmostEqual(sum(float(z['dlogrho_dlnne_panel']) for z in a),x['sky_uniform_energy_elasticity'],places=12)
   self.assertAlmostEqual(sum(float(z['dpol_dlnne_panel']) for z in a),x['sky_uniform_polarization_derivative'],places=12)
   self.assertGreater(x['sky_uniform_mean_scatter_derivative'],0.)
   self.assertGreater(x['sky_uniform_mean_emit_derivative'],0.)
   self.assertLess(x['sky_uniform_energy_elasticity'],0.)
 def test_real_epoch_history_effects(self):
  gl16=[x for x in self.sky if x['GL']=='GL16' and x['observer_k']=='40']
  self.assertEqual(sum(float(z['drho_dlnne_panel'])>0 for z in gl16),2)
  self.assertEqual(sum(float(z['drho_dlnne_panel'])<0 for z in gl16),38)
  self.assertEqual(sum(float(z['dpol_dlnne_panel'])>0 for z in gl16),8)
  self.assertEqual(sum(float(z['dmean_scatter_dlnne_panel'])>0 for z in gl16),40)
 def test_P8_coherency_gauge_basis_invariant(self):
  B=np.array([[2.,.25],[.25,.5]])
  dB=np.array([[.4,-.02],[-.02,-.1]])
  s=0.7;R=np.array([[np.cos(s),-np.sin(s)],[np.sin(s),np.cos(s)]])
  Br=R.T@B@R;dBr=R.T@dB@R
  lin=lambda X:np.hypot(X[0,0]-X[1,1],X[0,1]+X[1,0])
  self.assertAlmostEqual(np.trace(B),np.trace(Br),places=13)
  self.assertAlmostEqual(lin(B),lin(Br),places=13)
  a=(B[0,0]-B[1,1])*(dB[0,0]-dB[1,1])+(B[0,1]+B[1,0])*(dB[0,1]+dB[1,0])
  b=(Br[0,0]-Br[1,1])*(dBr[0,0]-dBr[1,1])+(Br[0,1]+Br[1,0])*(dBr[0,1]+dBr[1,0])
  self.assertAlmostEqual(a/lin(B),b/lin(Br),places=13)
 def test_negative_survival_exponent_counterexample(self):
  tau=4.;x=1.3;nom=x*np.exp(-tau);fake=x*np.exp(+tau)
  self.assertGreater(fake/nom,2000.)
  self.assertLess(nom,x)
 def test_corrupted_source_identity_rejected(self):
  from unittest.mock import patch
  with patch.dict(r.ORIGINAL_SHA,{f'KM2K_PACKETS_GL12_GLT8.npz':'0'*64}):
   with self.assertRaises(AssertionError):r.original(12)
 def test_deterministic_gzip_header(self):
  for fn in ('KM2_REI_POLARIZED_PHOTON_HISTORY_SKY_RESPONSE.csv.gz','KM2_REI_POLARIZED_PHOTON_HISTORY_RAY_RESPONSE.csv.gz'):
   b=(ROOT/'results'/fn).read_bytes();self.assertEqual(b[:3],b'\x1f\x8b\x08');self.assertEqual(b[4:8],b'\0\0\0\0')

if __name__=='__main__':unittest.main()
