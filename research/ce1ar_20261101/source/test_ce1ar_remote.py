"""Source-conditional CE1AR remote CI checks, not a full continuum/observer likelihood."""
import csv,json,math
from pathlib import Path
import numpy as np
import pytest
from scipy.interpolate import PchipInterpolator
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ce1ar_remote as q

ROOT=Path(__file__).resolve().parent.parent

def read(name):
 with (ROOT/'data'/name).open(newline='') as f:return list(csv.DictReader(f))

def test_original_model_not_substituted():
 assert q.SOURCE=='022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035'
 assert q.parent.SOURCE==q.SOURCE
 hist,t=q.parent.metric()
 assert len(hist)==9 and len(t)==401 and abs(t[-1]-.08)<1e-14
 assert len(q.parent.directions())==103

def test_new_original_physics_generated():
 raw=read('CE1AR_FIXED_Z_REMOTE_BEAMS.csv');response=read('CE1AR_FIXED_Z_REMOTE_RESPONSE.csv')
 summary=json.loads((ROOT/'data/CE1AR_REMOTE_RESULTS.json').read_text())
 assert len(raw)==5562 and len(response)==1854
 assert summary['reused_owner_IVPs']==9 and summary['new_Einstein_IVPs']==0
 assert summary['new_upper_nodes']==0 and not summary['OB1_full_accepted']
 assert not summary['real_observation_likelihood'] and not summary['matched_REI_owner']
 assert not summary['production'] and not summary['merge']
 assert len(set((v['GL'],v['eps'],v['z'],v['direction']) for v in raw))==5562

def test_source_owned_fixed_z_roots_and_sauners_agreement():
 for r in read('CE1AR_FIXED_Z_REMOTE_BEAMS.csv'):
  assert abs(float(r['redshift_gap']))<5e-13
  assert abs(float(r['gap']))<5e-12
  assert float(r['D_A'])>0 and float(r['D_A_saunders'])>0
  assert float(r['isotropic_proxy_D_A'])>0

def test_observed_z_source_chain_rule():
 for r in read('CE1AR_FIXED_Z_REMOTE_RESPONSE.csv'):
  f=float(r['direct_fixed_time']);c=float(r['clock_term']);s=float(r['source_secant'])
  assert abs(s-(f+c))<2e-11

def test_flrw_analytic_emitter_and_DA():
 t=np.linspace(0,.08,401); H=.46
 ell=np.tile(H*t[:,None],(1,3));L=PchipInterpolator(t,ell,axis=0)
 for z in (.005,.01,.02,.03):
  u=q.emitter(L,z,q.nn([1,2,3]))[0]
  da,ds,_=q.screen(L,u,q.nn([1,2,3]))
  expect=z/(H*(1+z))
  assert abs(u-(.08-math.log1p(z)/H))<2e-12
  assert abs(da-expect)<3e-12 and abs(ds-expect)<3e-12
  assert abs(q.isotropic(L,z)-expect)<3e-12

def test_original_gl24_axis_prediction_anchor():
 raw=read('CE1AR_FIXED_Z_REMOTE_BEAMS.csv')
 res=read('CE1AR_FIXED_Z_REMOTE_RESPONSE.csv')
 def beam(axis):return next(r for r in raw if r['GL']=='24' and r['eps']=='0.0' and r['z']=='0.02' and r['direction']==axis)
 def response(axis):return next(r for r in res if r['GL']=='24' and r['z']=='0.02' and r['direction']==axis)
 known={'x':(.028044169626674734,-7.014856651903806e-9),
        'y':(.048605391588600874,1.6283706526033978e-9),
        'z':(.04260215256293194,1.1088997279941535e-8)}
 for axis,(distance,sec) in known.items():
  b=beam(axis);rr=response(axis)
  assert abs(float(b['D_A'])-distance)<2e-11
  assert abs(float(rr['source_secant'])-sec)<2e-11
  assert abs(float(rr['clock_term']))>5*abs(float(rr['direct_fixed_time']))
 assert abs(float(beam('x')['D_A'])-float(beam('y')['D_A']))>1e-2

def test_gl16_gl24_match_on_same_physical_input():
 beams=read('CE1AR_FIXED_Z_REMOTE_BEAMS.csv')
 idx={(r['GL'],r['eps'],r['z'],r['direction']):float(r['D_A']) for r in beams}
 for ep in (-.035,0.,.035):
  for z in q.ZS:
   for direction in ('x','y','z','xyz'):
    key=(str(ep),str(z),direction)
    assert abs(idx[('24',*key)]-idx[('16',*key)])<4e-10
