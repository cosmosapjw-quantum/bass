"""Source-locked CE1AQ exact Bianchi null screen tests; no surrogate data."""
import csv,json,math,sys
from pathlib import Path
import numpy as np
import pytest
from scipy.integrate import simpson
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(HERE))
import ce1aq_remote as q
def read(name):
  with (ROOT/'data'/name).open(newline='') as f:return list(csv.DictReader(f))
def outcome():return json.loads((ROOT/'data'/'CE1AQ_REMOTE_RESULTS.json').read_text())
def test_source_parent_identity():
  assert q.SOURCE=='022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035'
  assert outcome()['parent_head']=='baef3a4b5a556703f2e2feb93b57da6b364d29fd'
  hist,t=q.metric()
  assert len(hist)==9 and abs(t[-1]-.08)<1e-14
def test_actual_original_data_counts():
  assert len(read('CE1AQ_BEAM_PHYSICAL.csv'))==7416
  assert len(read('CE1AQ_SOURCE_BEAM_RESPONSE.csv'))==2472
  assert outcome()['new_Einstein_IVPs']==0 and outcome()['reused_parent_IVPs']==9
def test_exact_saunders_jacobi_against_original_geometries():
  for row in read('CE1AQ_BEAM_PHYSICAL.csv'):
    assert abs(float(row['D_A_Jacobi_relative_gap']))<5e-13
    assert float(row['D_A_over_cTstar'])>0
    assert float(row['screen_det'])>0
def test_flrw_and_minkowski():
  t=np.linspace(0,.08,401)
  for H in (0.,.47):
    ell=np.tile((H*t)[:,None],(1,3))
    for j in (0,40,200):
      z=q.optical(ell,t,(1,2,3),j)
      exact=(t[-1]-t[j]) if H==0 else -np.expm1(-H*(t[-1]-t[j]))/H
      assert abs(z[1]-exact)<1e-11
      assert abs(z[6])<1e-12
def test_exact_axis_scalar_quadrature():
  hist,t=q.metric();ell=hist[(24,.035)]
  a=np.exp(ell-ell[-1])
  for i in range(3):
    nn=np.eye(3)[i];val=q.optical(ell,t,nn,0)
    r=[a[0,j]*simpson(a[:,i]/a[:,j]**2,x=t) for j in range(3) if j!=i]
    assert abs(val[1]-math.sqrt(r[0]*r[1]))<4e-13
def test_real_hidden_sixth_source_changes_axis_distance():
  rows=read('CE1AQ_SOURCE_BEAM_RESPONSE.csv')
  axis={v['direction']:v for v in rows if v['GL']=='24' and v['u_emit']=='0.0' and v['direction'] in ('x','y','z')}
  assert float(axis['x']['dD_A_plus'])< -1e-12
  assert float(axis['z']['dD_A_plus'])> 1e-12
  assert float(axis['x']['D_A_base'])>0
def test_ellipticity_and_observer_direction_nonzero():
  rows=[v for v in read('CE1AQ_BEAM_PHYSICAL.csv') if v['GL']=='24' and v['eps']=='0.0' and v['u_emit']=='0.0']
  vals=[float(r['beam_ellipticity']) for r in rows]
  assert len(rows)==103 and max(vals)>1e-5 and min(vals)>=0
def test_no_unlicensed_upper_dag_or_observational_claim():
  r=outcome()
  assert r['BASS_CE1_upper']=='9/15' and r['new_upper_nodes']==0
  assert not r['full_continuum_Weyl_sign'] and not r['Planck_CMB_likelihood']
  assert not r['production'] and not r['merge'] and not r['auto_next']
