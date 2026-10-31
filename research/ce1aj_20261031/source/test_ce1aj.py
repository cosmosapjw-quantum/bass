"""CE1AJ actual scientific data, exact bound and hostile original-source controls."""
import sys,csv,json,math
from pathlib import Path
from fractions import Fraction as F
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'source'))
import certify_finite_transfer as cert
import ce1aj_physics as p

def rows(name):
    with (ROOT/'data'/name).open(newline='') as f:return list(csv.DictReader(f))

def test_source_and_rational():
    assert p.p.validate_immutable()=='022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035'
    x=cert.certify()
    assert F(x['initial_jet_strict_upper_rational'])<-F(3,4)
    assert F(x['quadratic_remainder_coefficient'])==232225
    assert x['new_upper_nodes']==0 and not x['production_ready']

def test_source_tamper(monkeypatch):
    monkeypatch.setattr(p.p,'frozen_source_identity',lambda:'bad')
    with pytest.raises(RuntimeError,match='SHA256 drift'):
        cert.certify()

def test_actual_9624_rows():
    assert len(rows('CE1AJ_BASELINE_PHYSICAL.csv'))==2406
    assert len(rows('CE1AJ_DARK_TANGENT_PHYSICAL.csv'))==2406
    assert len(rows('CE1AJ_DARK_FINITE_IVP.csv'))==4812

@pytest.mark.parametrize('gl',[6,8,16])
@pytest.mark.parametrize('window',['micro_certified','full_numeric'])
def test_bounded_continuum_scope_and_true_tangent(gl,window):
    t=[r for r in rows('CE1AJ_DARK_TANGENT_PHYSICAL.csv')
       if int(r['GL'])==gl and r['window']==window]
    assert len(t)==401
    assert abs(float(t[-1]['dconstraint']))<1e-10
    if window=='micro_certified':
        assert float(t[-1]['u'])==1e-6
        assert all(float(r['dalpha42'])<-.5*float(r['u']) for r in t[1:])
        assert int(t[-1]['rigor_applies'])==1
    else:
        assert abs(float(t[-1]['u'])-.08)<1e-12
        assert float(t[-1]['dalpha42'])<-.05
        assert int(t[-1]['rigor_applies'])==0
        assert math.isnan(float(t[-1]['rigorous_upper_bound']))

@pytest.mark.parametrize('gl',[6,8,16])
@pytest.mark.parametrize('window',['micro_certified','full_numeric'])
def test_nonlinear_finite_difference_not_tangent_only(gl,window):
    f=[r for r in rows('CE1AJ_DARK_FINITE_IVP.csv') if int(r['GL'])==gl and r['window']==window]
    assert len(f)==802
    ends=[r for r in f if float(r['u'])==max(float(x['u']) for x in f)]
    assert len(ends)==2
    val={int(r['sign']):float(r['alpha42']) for r in ends}
    fd=(val[1]-val[-1])/(2*float(ends[0]['eps']))
    t=[r for r in rows('CE1AJ_DARK_TANGENT_PHYSICAL.csv') if int(r['GL'])==gl and r['window']==window]
    assert abs(fd-float(t[-1]['dalpha42']))<2e-9

def test_hamiltonian_and_response_energy():
    b=rows('CE1AJ_BASELINE_PHYSICAL.csv')
    d=rows('CE1AJ_DARK_TANGENT_PHYSICAL.csv')
    for x,y in zip(b,d):
        E,W,q=map(float,(x['E'],x['W'],x['q']))
        de,dw,dq=map(float,(y['dE'],y['dW'],y['dq']))
        assert abs(float(x['constraint']))<5e-11
        assert abs(float(y['dconstraint']))<1e-11
        assert abs(q-W/E)<1e-13
        assert abs(dq-(dw-q*de)/E)<1e-13

def test_finite_family_positive_and_constrained():
    for r in rows('CE1AJ_DARK_FINITE_IVP.csv'):
        assert float(r['E'])>0
        assert abs(float(r['constraint']))<5e-11

def test_no_false_global_certification():
    c=cert.certify()
    assert c['finite_time_full_horizon_rank_certified'] is False
    assert F(c['certified_u_range'][1])<F(2,25)

def test_prior_ce1ai_science_preserved():
    old=json.loads((ROOT.parent/'ce1ai_20261031'/'data'/'CE1AI_PHYSICAL_RESPONSE_RESULTS.json').read_text())
    for gl in ('6','8','16'):
        t=[r for r in rows('CE1AJ_DARK_TANGENT_PHYSICAL.csv') if r['GL']==gl and r['window']=='full_numeric']
        target=old['GL'][gl]['endpoint_response']['DARK_L2L4']
        assert abs(float(t[-1]['dC4'])-target['dC4'])<3e-10
        assert abs(float(t[-1]['dW'])-target['dW'])<3e-10
