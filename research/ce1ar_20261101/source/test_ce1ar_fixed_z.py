"""Source-limited CE1AR physical data and exact redshift screen contracts."""
from pathlib import Path
import csv
import json
import math
import os
import sys

import numpy as np
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parent))
import ce1ar_fixed_z as q

HERE=Path(__file__).resolve().parent
RESEARCH=HERE.parents[1]
PACKAGE=HERE.parent
LOCAL=PACKAGE if (PACKAGE/'ancestor/CE1AP_DIRECTIONAL_GEODESIC.csv').exists() else Path('/mnt/data/bass_ce1ar_workspace/CE1AQ')
INPUT=Path(os.environ['CE1AR_GEOMETRY_INPUT']) if 'CE1AR_GEOMETRY_INPUT' in os.environ else (
  LOCAL/'ancestor/CE1AP_DIRECTIONAL_GEODESIC.csv' if (LOCAL/'ancestor/CE1AP_DIRECTIONAL_GEODESIC.csv').exists() else RESEARCH/'ce1ap_20261031/data/CE1AP_DIRECTIONAL_GEODESIC.csv')
META=Path(os.environ['CE1AR_GEOMETRY_META']) if 'CE1AR_GEOMETRY_META' in os.environ else (
  LOCAL/'ancestor/ANCESTOR_LOCK.json' if (LOCAL/'ancestor/ANCESTOR_LOCK.json').exists() else RESEARCH/'ce1ap_20261031/data/CE1AP_REMOTE_RESULTS.json')
OUT=Path(os.environ.get('CE1AR_OUTPUT_DIR',str(HERE.parent/'data')))

@pytest.fixture(scope='session')
def original():
 return q.load_original(INPUT,META,strict_sha=(INPUT == LOCAL/'ancestor/CE1AP_DIRECTIONAL_GEODESIC.csv'))[0]

def read_csv(name):
 with (OUT/name).open(newline='') as f:return list(csv.DictReader(f))

def test_source_lock_and_owner(original):
 assert set(original)=={(gl,ep) for gl in q.ORDERS for ep in q.EPS}
 assert len(q.directions())==103
 assert len(q.SHELLS)==6
 assert q.sha256(INPUT)==q.S2_ANCESTOR_INPUT_SHA if INPUT==LOCAL/'ancestor/CE1AP_DIRECTIONAL_GEODESIC.csv' else INPUT.is_file()

def test_root_observed_redshift_exact_and_monotonic(original):
 for gl in q.ORDERS:
  for ep in q.EPS:
   model=original[(gl,ep)]
   for _,direction in q.directions()[::8]:
    vals=[q.log_redshift(model,tt,direction) for tt in model.u]
    assert np.all(np.diff(vals)<0)
    for z in (q.SHELLS[0],q.SHELLS[-1]):
     ue,res=q.solve_emitter(model,z,direction)
     assert 0<ue<q.OBS_U and res<3e-13

def test_out_of_horizon_extrapolation_rejected(original):
 model=original[(24,0.)]
 with pytest.raises(ValueError,match='outside owner physical horizon'):
  q.solve_emitter(model,0.4,(0,1,0))
 with pytest.raises(ValueError,match='positive observed redshift'):
  q.solve_emitter(model,-.01,(1,0,0))

def test_source_metadata_tamper_fails(tmp_path):
 m=json.loads(META.read_text());m['source_sha256']='0'*64
 path=tmp_path/'bad.json';path.write_text(json.dumps(m))
 with pytest.raises(ArithmeticError,match='source SHA'):
  q.load_original(INPUT,path)

def test_known_flrw_analytic_fixed_z():
 u=np.linspace(0,.08,401); H=.46
 ell=np.tile((H*u)[:,None],(1,3)); hh=np.full_like(ell,H)
 model=q.Geometry(u,ell,hh,24,0.)
 for z in (.005,.01,.02,.03):
  expected_u=.08-math.log1p(z)/H
  expected_DA=z/((1+z)*H)
  for n in ((1,0,0),(0,1,0),(1,1,1)):
   ue,_=q.solve_emitter(model,z,n)
   o=q.optical_at_emitter(model,ue,n)
   iso=q.isotropic_equal_volume_proxy(model,z)
   assert abs(ue-expected_u)<2e-12
   assert abs(o['DA']-expected_DA)<3e-12
   assert abs(iso-expected_DA)<3e-12
   assert abs(o['DA']-iso)<2e-12
   assert abs(o['ellipticity'])<2e-12

def test_minkowski_null_beam():
 t=np.linspace(0,.08,401); ell=np.zeros((401,3)); h=np.zeros((401,3))
 # No z>0 emitter in Minkowski; geometry h>0 is specifically a positive-redshift source prerequisite.
 with pytest.raises(ValueError,match='nonexpanding'):
  q.Geometry(t,ell,h,24,0.)

def test_original_endpoint_axis_and_jacobi_saunders(original):
 for gl in q.ORDERS:
  for ep in q.EPS:
   model=original[(gl,ep)]
   for z in (.01,.025,.03):
    for n in ((1,0,0),(0,1,0),(0,0,1),(1,1,1)):
     ue,_=q.solve_emitter(model,z,n)
     o=q.optical_at_emitter(model,ue,n)
     assert abs(o['gap'])<5e-12
     assert 0<=o['ellipticity']<1 and o['det']>0

def test_integration_panel_self_convergence(original):
 m=original[(24,0.)]
 for z in (.01,.03):
  for n in ((1,0,0),(0,1,0),(0,0,1),(1,1,1)):
   ue,_=q.solve_emitter(m,z,n)
   ds=[q.optical_at_emitter(m,ue,n,panels=p)['DA'] for p in (129,257,513)]
   assert max(abs(ds[0]-ds[1]),abs(ds[1]-ds[2]))<2e-10

def test_new_real_physics_counts_and_claim_ceiling():
 out=json.loads((OUT/'CE1AR_RESULTS.json').read_text())
 full=read_csv('CE1AR_FIXED_Z_BEAMS.csv')
 resp=read_csv('CE1AR_FIXED_Z_RESPONSE.csv')
 assert len(full)==5562 and len(resp)==1854
 assert out['new_fixed_z_observable_records']==7416 and out['new_Einstein_IVPs']==0
 assert out['reused_original_Einstein_IVPs']==9 and not out['OB1_full_accepted']
 assert out['new_upper_completed']==0 and not out['production_ready'] and not out['merge_ready']
 assert out['source_SHA256']==q.SOURCE_SHA
 assert not out['matched_REI_IGM_source'] and not out['Planck_or_measured_sky_likelihood']
 assert len(set((row['GL'],row['eps'],row['z_target'],row['direction']) for row in full))==5562

def test_every_scientific_row_fixed_z_and_positive():
 for row in read_csv('CE1AR_FIXED_Z_BEAMS.csv'):
  assert float(row['redshift_abs_residual'])<5e-13
  assert abs(float(row['reconstructed_z'])-float(row['z_target']))<5e-13
  assert float(row['D_A_over_cTstar'])>0
  assert float(row['equal_volume_isotropic_D_A'])>0
  assert float(row['screen_det'])>0
  assert abs(float(row['D_A_jacobi_saunders_rel_gap']))<5e-12

def test_implicit_response_identity_all_real_rows():
 rr=read_csv('CE1AR_FIXED_Z_RESPONSE.csv')
 for row in rr:
  total=float(row['central_secant_D_A_at_fixed_z'])
  pred=float(row['implicit_total_source_response'])
  direct=float(row['direct_D_A_secant_at_fixed_emission_clock'])
  clock=float(row['emitter_clock_response_term'])
  assert abs(direct+clock-pred)<2e-19
  assert abs(total-pred)<2e-11

def test_observer_condition_effect_from_original_physics():
 rows=read_csv('CE1AR_FIXED_Z_RESPONSE.csv')
 p={(int(r['GL']),float(r['z_target']),r['direction']):r for r in rows}
 for name,sign in [('x',-1),('y',+1),('z',+1)]:
  r=p[(24,.02,name)]
  total=float(r['central_secant_D_A_at_fixed_z'])
  direct=float(r['direct_D_A_secant_at_fixed_emission_clock'])
  clock=float(r['emitter_clock_response_term'])
  assert total*sign>0
  assert abs(clock)>5*abs(direct)

def test_independent_gl24_v_gl16_physical_finite_grid():
 rows=read_csv('CE1AR_FIXED_Z_BEAMS.csv')
 p={(int(r['GL']),float(r['eps']),float(r['z_target']),r['direction']):float(r['D_A_over_cTstar']) for r in rows}
 for ep in q.EPS:
  for z in q.SHELLS:
   for direction in ('x','y','z','xyz'):
    assert abs(p[(24,ep,z,direction)]-p[(16,ep,z,direction)])<4e-10
