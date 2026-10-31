"""CE1AN source-owned scientific tests. Execute after data regeneration, no tolerance relaxation."""
import csv, json, sys
from pathlib import Path
import numpy as np
import pytest
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
sys.path.insert(0,str(HERE))
import ce1an_remote as c

def results():
 return json.loads((ROOT/'data'/'CE1AN_REMOTE_RESULTS.json').read_text())
def records(name):
 with (ROOT/'data'/name).open(newline='') as f: return list(csv.DictReader(f))

def test_original_six_cell_source_lock_and_parent_head():
 assert c.source_check()==c.SOURCE
 assert results()['immutable_parent']==c.PARENT

def test_original_dark_initial_hidden_pressure_and_quartic():
 for gl in c.ORDERS:
  rays,m=c.src.make_cell_rays(gl); r2=rays*rays
  dm=c.src.ray_source_basis(gl,m)[-1]
  assert abs(float(np.sum(dm)))<3e-13
  assert max(abs(float(v)) for v in dm@r2)<3e-12
  assert max(abs(float(v)) for v in np.einsum('a,ai,aj->ij',dm,r2,r2,optimize=True).ravel())<3e-12

def test_source_tamper_rejected(monkeypatch):
 monkeypatch.setattr(c.src,'validate_immutable',lambda:'mismatch')
 with pytest.raises(RuntimeError): c.source_check()

def test_actual_24_independent_ivps_rows_and_nonzero_families():
 x=results()
 assert x['new_IVPs']==24 and x['nonlinear_rows']==8421 and x['nonzero_amp_rows']==7218
 assert x['tangent_rows']==1203 and x['secant_diagnostic_rows']==3609
 assert len(records('CE1AN_FINITE_SOURCE_PHYSICS.csv'))==8421
 assert len(records('CE1AN_TANGENT_PHYSICS.csv'))==1203
 assert len(records('CE1AN_SECANT_RESPONSE.csv'))==3609

def test_positive_original_source_and_einstein_constraint():
 for gl in ('8','16','24'):
  r=results()['results'][gl]
  assert r['nonlinear_IVPs']==7 and r['tangent_IVPs']==1 and r['max_constraint']<1e-10
 for row in records('CE1AN_FINITE_SOURCE_PHYSICS.csv'):
  assert float(row['E'])>0 and float(row['mass_min'])>0
  assert abs(float(row['constraint']))<1e-10

def test_weyl_ricci_decomposition_and_dossier_first_law():
 for gl in ('8','16','24'):
  r=results()['results'][gl]
  assert r['max_Weyl_identity']<1e-10
  assert r['max_integrated_energy_work']<1e-10
 for row in records('CE1AN_FINITE_SOURCE_PHYSICS.csv'):
  assert abs(float(row['Weyl_identity_gap']))<1e-10
  assert abs(float(row['logbalance']))<1e-10
  assert float(row['WeylSq'])>=0

def test_initial_dark_null_and_positive_mass_family():
 rows=records('CE1AN_FINITE_SOURCE_PHYSICS.csv')
 for gl in ('8','16','24'):
  initial=[v for v in rows if v['GL']==gl and float(v['u'])==0]
  assert len(initial)==7
  for key in ('E','P1','P2','P3','h1','h2','h3'):
   z=[float(r[key]) for r in initial]
   assert max(z)-min(z)<2e-12

def test_original_finite_source_weyl_response_and_tangent():
 x=results()
 for gl in ('8','16','24'):
  p=x['results'][gl]
  assert abs(p['end_dWeyl_tangent']-(-8.41283600394e-6))<1e-8
  for a in ('0.01','0.025','0.035'):
   y=p['eps'][a]
   assert y['all_400_positive_u_sampled_secants_negative']
   assert y['delta_weyl_eps_positive']<0<y['delta_weyl_eps_negative']
   assert y['max_abs_secant_minus_tangent_weyl']<1e-8

def test_claim_limit_upper_dag_and_no_promotion():
 x=results()
 assert x['upper_DAG']=='9/15' and x['CE1']=='PARTIAL'
 assert x['new_upper_completed_nodes']==0
 assert not x['full_continuum_sign_proof'] and not x['Planck_likelihood']
 assert not x['production'] and not x['merge'] and not x['auto_next']
