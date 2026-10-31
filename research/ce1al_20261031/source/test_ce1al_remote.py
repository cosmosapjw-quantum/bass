"""CE1AL: actual six-cell Weyl-curvature source transfer and hostile tests."""
import csv,json,math,sys
from pathlib import Path
import numpy as np
import pytest
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
sys.path.insert(0,str(HERE))
import ce1al_curvature_remote as c

def data(n):
 with (ROOT/'data'/n).open(newline='') as f:return list(csv.DictReader(f))

def test_original_source_exact_sha_and_nonthermal():
 assert c.certificate()['source_sha256']==c.SOURCE_SHA
 assert c.src.validate_immutable()==c.SOURCE_SHA

def test_strict_original_continuum_kappa_negative():
 cert=c.certificate();lo,hi=cert['kappa_floats']
 assert -.002252<lo<-.00216<hi<-.002079
 assert not cert['production_ready'] and cert['full_horizon_sign']=='NOT_CERTIFIED_CONTINUUM'

def test_exact_sixth_tensor_trace():
 x=c.certificate()
 from fractions import Fraction as F
 a=[F(v) for v in x['A_over_pi']]
 assert sum(a)==0
 assert max(abs(v) for v in a)>0

def test_nonlinear_positive_family_and_source_tamper(monkeypatch):
 rays,mass=c.src.make_cell_rays(6)
 for sign in (-1,1):
  m=c.src.positive_reweighted_mass(6,mass,'DARK_L2L4',sign*1e-3)
  assert np.all(m>0) and abs(m.sum()-mass.sum())<1e-12
 monkeypatch.setattr(c.src,'frozen_source_identity',lambda:'bad')
 with pytest.raises(RuntimeError):c.certificate()

def test_electric_weyl_is_traceless_and_FLRW_limit():
 h=np.array([.5,.5,.5]);p=np.array([.25,.25,.25]);E=.75
 w,w2,k,ric,ratio,r,trace=c.curv(h,p,E)
 assert max(abs(w))<1e-14 and w2<1e-14 and abs(trace)<1e-14
 assert abs(k-2*ric-w2)<1e-13

def test_weyl_and_riemann_tangent_identity_independently():
 h=np.array([.79,.54,.39]);E=h[0]*h[1]+h[0]*h[2]+h[1]*h[2]
 p=np.array([.25,.31,E-.56])
 dh=np.array([.009,-.011,.006]);dE=float((sum(h)-h)@dh)
 dp=np.array([.02,-.04,dE+.02])
 assert abs(dp.sum()-dE)<1e-14
 _,_,_,_,_,r,t=c.curv(h,p,E)
 _,_,_,_,_,dr,dt=c.dcurv(h,p,E,dh,dp,dE)
 assert abs(r)<1e-13 and abs(dr)<1e-13
 assert abs(t)<1e-12 and abs(dt)<1e-12

def test_actual_2406_tangent_and_4812_nonlinear_source_ivs():
 a=data('CE1AL_WEYL_CURVATURE_TANGENT.csv')
 b=data('CE1AL_NONLINEAR_SOURCE_CURVATURE.csv')
 assert len(a)==2406 and len(b)==4812
 assert {x['GL'] for x in a}=={'6','8','16'}
 assert {x['window'] for x in a}=={'short_curvature','original_horizon'}
 assert len([x for x in b if int(x['sign'])==1])==2406
 assert len([x for x in b if int(x['sign'])==-1])==2406
 assert all(math.isfinite(float(r['dWeylSq'])) for r in a)

def test_actual_Einstein_constraint_curvature_identity_and_tangent():
 rows=data('CE1AL_WEYL_CURVATURE_TANGENT.csv')
 for x in rows:
  for key,limit in [('einstein_constraint',1e-10),('curvature_identity_residual',1e-10),
                    ('dcurvature_identity_residual',1e-10),('dtangent_constraint',1e-10),
                    ('weyl_trace',1e-10),('dweyl_trace',1e-10)]:
   assert abs(float(x[key]))<limit,(key,x['GL'],x['u'],x[key])
  assert float(x['E'])>0 and float(x['WeylSq'])>=0

def test_initial_dark_c2_vanishes():
 for x in data('CE1AL_WEYL_CURVATURE_TANGENT.csv'):
  if float(x['u'])==0:
   for key in ['dE','dP1','dP2','dP3','dWeylSq','dElectricWeyl1','dElectricWeyl2','dElectricWeyl3']:
    assert abs(float(x[key]))<2e-11,(x['GL'],key,x[key])

def test_finite_source_nonlinear_ivp_agrees_with_tangent():
 r=json.loads((ROOT/'data'/'CE1AL_REMOTE_CURVATURE_RESULTS.json').read_text())
 assert r['row_counts']=={'tangent':2406,'nonlinear':4812,'total':7218}
 for o in ('6','8','16'):
  for w in ('short_curvature','original_horizon'):
   v=r['results'][o][w]
   assert v['epochs']==401 and v['physical_rows']==1203
   assert v['max_constraint']<1e-10
   assert v['max_identity']<1e-10
   assert v['max_didentity']<1e-10
   assert v['max_FD_error_WeylSq']<1e-8

def test_original_horizon_numerical_reproduction_scoped():
 r=json.loads((ROOT/'data'/'CE1AL_REMOTE_CURVATURE_RESULTS.json').read_text())
 x=r['results']['16']['original_horizon']
 assert abs(x['end_dWeylSq']-(-8.41283600394e-6))<1e-8
 assert r['DAG']=='9/15' and r['CE1']=='PARTIAL' and not r['production_ready'] and not r['merge_ready']

def test_strict_jet_negative_only_asymptotic():
 vals=[]
 for r in data('CE1AL_WEYL_CURVATURE_TANGENT.csv'):
  if r['GL']=='16' and r['window']=='short_curvature' and float(r['u'])>0:vals.append(float(r['dWeylSq']))
 assert vals[0]<0 and vals[-1]<0
 # Does not certify any continuum sign beyond the local initial Taylor theorem.
