"""CE1AP original-source remote clean GitHub checkout physics and parent witness tests."""
import csv,json,sys
from pathlib import Path
import numpy as np
import pytest
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(HERE))
import ce1ap_remote as p
def rows(name):
 with (ROOT/'data'/name).open(newline='') as f:return list(csv.DictReader(f))
def result():return json.loads((ROOT/'data'/'CE1AP_REMOTE_RESULTS.json').read_text())
def endpoint(rows_,gl,eps,direction):
 for v in rows_:
  if int(v['GL'])==gl and float(v['eps'])==eps and float(v['u'])==.08 and v['dir']==direction:return v
 raise RuntimeError('missing endpoint')
def test_source_and_parent():
 assert p.src.validate_immutable()==p.LOCK and result()['parent_head']==p.PARENT
def test_claim_and_counts():
 r=result()
 assert r['new_IVPs']==9 and r['tangent_IVPs']==3 and r['finite_IVPs']==6
 assert r['directional_rows']==16842 and r['tangent_rows']==1203 and r['directional_RMS_rows']==2406
 assert len(rows('CE1AP_DIRECTIONAL_GEODESIC.csv'))==16842
 assert len(rows('CE1AP_EINSTEIN_TANGENT_METRIC.csv'))==1203
 assert len(rows('CE1AP_DIRECTIONAL_SKY_RMS.csv'))==2406
def test_traceless_source_and_exact_initial_dark():
 A=p.A_exact();assert abs(sum(A))<1e-16
 for gl in p.ORDERS:
  rays,m=p.src.make_cell_rays(gl);r2=rays*rays;dm=p.src.ray_source_basis(gl,m)[-1]
  assert abs(sum(dm))<3e-13 and max(abs(dm@r2))<3e-12
def test_all_nine_original_einstein_constraint_and_tangent():
 r=result()
 for gl in ('8','16','24'):
  assert r['GL'][gl]['max_constraint']<1e-10
  assert r['GL'][gl]['max_finite_constraint']<1e-10
  assert r['GL'][gl]['max_tangent_constraint']<1e-10
def test_true_original_parent_gl24_endpoint_witness():
 w=json.loads((ROOT/'ancestor'/'CE1AP_PARENT_GL24_ENDPOINTS.json').read_text())
 assert w['source_sha256']==p.LOCK
 data=rows('CE1AP_DIRECTIONAL_GEODESIC.csv')
 for eps in p.EPS:
  for key,axis in [('x',0),('y',1),('z',2)]:
   entry=endpoint(data,24,eps,key)
   base=w['GL24']['0.0'];other=w['GL24'][str(eps)]
   assert abs(float(entry['ln_R_base'])+base['ell'][axis])<8e-13
   assert abs(float(entry['delta_ln_R'])+(other['ell'][axis]-base['ell'][axis]))<8e-13
   assert abs(float(entry['delta_drift'])+(other['h'][axis]-base['h'][axis]))<8e-13
def test_exact_initial_fourth_jet_numerical_limit():
 A=p.A_exact();data=rows('CE1AP_EINSTEIN_TANGENT_METRIC.csv')
 for gl in p.ORDERS:
  t=next(x for x in data if int(x['GL'])==gl and abs(float(x['u'])-.0004)<1e-14)
  for i in range(3):
   v=float(t[f'dell{i+1}'])/(.0004**4*A[i]/8)
   assert abs(v-1)<.015
def test_axis_signature_and_numerical_replay():
 data=rows('CE1AP_DIRECTIONAL_GEODESIC.csv')
 for gl in p.ORDERS:
  for key in p.DIR:
   plus=endpoint(data,gl,.035,key);minus=endpoint(data,gl,-.035,key)
   k=(float(plus['delta_ln_R'])-float(minus['delta_ln_R']))/.07
   assert abs(k-float(plus['tangent_delta_ln_R']))<7e-12
def test_negative_scientific_axis_control():
 data=rows('CE1AP_DIRECTIONAL_GEODESIC.csv')
 x=endpoint(data,24,.035,'x');z=endpoint(data,24,.035,'z')
 assert abs(float(x['delta_ln_R'])-float(z['delta_ln_R']))>1e-11
def test_bounded_scoped_dag_and_production_hold():
 r=result()
 assert r['upper_DAG']=='9/15' and r['new_upper_nodes']==0
 assert r['full_continuum_weyl_sign'] is False and r['CMB_likelihood'] is False
 assert not r['production'] and not r['merge'] and not r['auto_next']
