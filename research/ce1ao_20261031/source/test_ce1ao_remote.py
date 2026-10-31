"""CE1AO remote clean-checkout original sky physics and exact initial source gates."""
import csv,json,sys
from pathlib import Path
import pytest
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
sys.path.insert(0,str(HERE))
import ce1ao_remote as a
def data():
 with (ROOT/'data'/'CE1AO_REMOTE_SKY.csv').open(newline='') as f:return list(csv.DictReader(f))
def summary():return json.loads((ROOT/'data'/'CE1AO_REMOTE_RESULTS.json').read_text())
def entry(rows,g,e,u):
 return next(v for v in rows if int(v['GL'])==g and float(v['eps'])==e and float(v['u'])==u)
def test_source_owner_and_immutable_parent():
 assert a.src.validate_immutable()==a.SOURCE
 assert summary()['parent_head']=='61257246883df00ff478aeb5e8317d46e25702ce'
def test_true_original_ce1an_data_and_counts():
 r=data();s=summary()
 assert len(r)==8421 and s['new_sky_physical_rows']==8421
 assert s['reused_parent_IVPs']==24 and s['new_ivps']==0
 assert all(s['GL'][str(n)]['rows']==2807 for n in (8,16,24))
def test_exact_initial_low_l_dark_and_nonzero_l6():
 r=data()
 for g in (8,16,24):
  v=entry(r,g,0.,0.)
  for eps in (-.035,-.025,-.01,.01,.025,.035):
   w=entry(r,g,eps,0.)
   for k in ('C2','C4','alpha20','alpha22','alpha40','alpha42','alpha44'):
    assert abs(float(w[k])-float(v[k]))<2e-10,(g,eps,k)
   assert abs((float(w['alpha64'])-float(v['alpha64']))/eps+5.302758811735706)<3e-9
def test_physical_moment_3d_and_independent_harmonic_polynomial():
 for s in summary()['GL'].values():
  assert s['max_E_gap']<1e-10 and s['max_P_gap']<1e-10
  assert s['max_l6_cartesian_gap']<1e-10
def test_initial_l6_to_l4_source_transfer_first_jet():
 rows=data();h=.0002
 for g in (8,16,24):
  p=sorted([r for r in rows if int(r['GL'])==g and float(r['eps'])==.035],key=lambda r:float(r['u']))
  m=sorted([r for r in rows if int(r['GL'])==g and float(r['eps'])==-.035],key=lambda r:float(r['u']))
  F=lambda i:(float(p[i]['alpha44'])-float(m[i]['alpha44']))/.07
  first=2*(F(1)-F(0))/h-(F(2)-F(0))/(2*h)
  assert abs(first-.18834888978939164)<2e-6
def test_claim_limit_and_physical_positivity():
 s=summary()
 assert s['upper_DAG']=='9/15' and s['new_upper_nodes']==0
 assert not s['continuum_horizon_weyl_sign_proved'] and not s['CMB_likelihood']
 assert not s['production'] and not s['merge'] and not s['auto_next']
 assert all(float(r[k])>=0 for r in data() for k in ('C2','C4','C6','C8'))
