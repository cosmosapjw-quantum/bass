"""Remote source-bound CE1AK science checks, not an independent-author R6/C9."""
import csv, math, sys, json
from pathlib import Path
from fractions import Fraction as F
import numpy as np
import pytest
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import ce1ak_reproduce as ce
ROOT=HERE.parent

def rows(file):
    with (ROOT/'data'/file).open(newline='') as h:return list(csv.DictReader(h))

def test_exact_source():
    c=ce.certificate()
    assert c['source_sha256']==ce.ORIGINAL_SHA
    assert F(c['T_xxy_over_pi'])==F(-27,1421)
    assert ce.p.validate_immutable()==ce.ORIGINAL_SHA

def test_exact_sixth_tensor():
    q=F(-27,1421)
    assert ce.TKEY['xxx']==-3 and ce.TKEY['xxz']==2 and ce.TKEY['xyz']==-2
    assert ce.TKEY['xxy']==1 and ce.TKEY['xzz']==0 and ce.TKEY['zzz']==0
    s=[F.from_float(float(v)) for v in ce.p.SHEAR]
    t=[[[q*ce.TKEY[''.join(sorted('xyz'[i]+'xyz'[j]+'xyz'[k]))]
          for k in range(3)] for j in range(3)] for i in range(3)]
    assert all(sum(t[i][j][k] for i in range(3))==0 for j in range(3) for k in range(3))
    A=[sum((s[j]*s[k]*t[i][j][k] for j in range(3) for k in range(3)),F(0)) for i in range(3)]
    assert sum(A)==0
    assert sum((s[i]*A[i] for i in range(3)),F(0))>0

def test_time_jet_energy_work_relation():
    c=ce.certificate()
    assert F(c['delta_W_second_over_pi'])==-F(c['delta_E_third_over_pi'])
    assert c['W_u2']>0 and c['E_u3']<0
    assert abs(c['E_u3']+c['W_u2']/3)<1e-16

def test_two_window_actual_nonlinear_IVPs():
    a=rows('CE1AK_STRESS_EINSTEIN.csv')
    b=rows('CE1AK_NONLINEAR_IVP.csv')
    assert len(a)==2406 and len(b)==4812
    assert set((x['GL'],x['window']) for x in a)=={(str(j),w) for j in [6,8,16] for w in ce.WINDOWS}
    assert set(x['sign'] for x in b)=={'-1','1'}
    assert all(x['eps']=='0.001' for x in b)

@pytest.mark.parametrize('gl',[6,8,16])
def test_original_source_sixth_moment_frozen(gl):
    aa=[x for x in rows('CE1AK_STRESS_EINSTEIN.csv') if x['GL']==str(gl) and x['window']=='jet_resolved']
    x=aa[0]
    q=float(x['T_xxy'])
    assert abs(q+27/(1421*math.pi))<2e-10
    assert abs(float(x['T_xxx'])+3*q)<2e-10
    assert abs(float(x['T_xxz'])-2*q)<2e-10
    assert abs(float(x['T_xyz'])+2*q)<2e-10

@pytest.mark.parametrize('gl',[6,8,16])
def test_numerical_full_horizon_validity(gl):
    r=json.loads((ROOT/'data'/'CE1AK_SUMMARY.json').read_text())['reports'][str(gl)]['original_horizon']
    assert r['endpoint_dW']>0 and r['endpoint_dE']<0
    assert abs(r['endpoint_dW']-2.54469126144e-6)<3e-10
    assert abs(r['endpoint_dE']+7.2733523e-8)<3e-10
    assert r['max_constraint']<1e-10
    assert r['max_tangent_constraint']<1e-10
    assert r['max_nonlinear_constraint']<1e-10

@pytest.mark.parametrize('gl',[6,8,16])
def test_jet_window_stress_work_delay(gl):
    a=[x for x in rows('CE1AK_STRESS_EINSTEIN.csv') if x['GL']==str(gl) and x['window']=='jet_resolved']
    mid=a[200]
    u=float(mid['u']); c=ce.certificate()
    assert abs((float(mid['dP1'])/u**2)/c['P_u2'][0]-1)<.05
    assert abs((float(mid['dW'])/u**2)/c['W_u2']-1)<.05
    assert abs((float(mid['dE'])/u**3)/c['E_u3']-1)<.06
    assert abs((float(mid['dh1'])/u**3)/c['h_u3'][0]-1)<.06

def test_trace_pressure_equals_energy_response():
    for r in rows('CE1AK_STRESS_EINSTEIN.csv'):
        assert abs(sum(float(r[k]) for k in ('dP1','dP2','dP3'))-float(r['dE']))<1e-10

def test_no_unearned_DAG_promotion():
    r=json.loads((ROOT/'data'/'CE1AK_SUMMARY.json').read_text())
    assert r['upper_DAG']=='9/15' and r['new_upper_nodes']==0
    assert r['continuum_horizon_sign']=='NOT_CERTIFIED'
    assert not r['production_ready'] and not r['merge_ready']

def test_bad_original_source_rejected(monkeypatch):
    monkeypatch.setattr(ce.p,'frozen_source_identity',lambda:'bad')
    with pytest.raises(RuntimeError):
        ce.certificate()
