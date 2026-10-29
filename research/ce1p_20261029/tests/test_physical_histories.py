"""Scientific checks on saved CE1-P model histories, not a production solver gate."""
import csv,json,math,os
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'
O=json.loads((DATA/'results.json').read_text())

def csvrow(name):
    with (DATA/name).open() as f:return [{k:(v if k=='channel' else float(v)) for k,v in row.items() if v!=''} for row in csv.DictReader(f)]

def test_frozen_identity():
    assert O['source_git_blobs']['einstein_tabulated_source.py']=='fdeb83a65cd424786ba6bb8ddadbcb2b2e2d45bf'
    assert O['source_git_blobs']['einstein_interval.py']=='abbab0990fdefaf535ccbf5191ae3e060cb19214'
    assert O['source_input_binary64_sha256']=='022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035'
    assert O['upper_dag']=='9/15' and not O['production_ready']

def test_ensemble_and_trace():
    names=['stored_ref1','stored_ref4','stored_ref8','stored_ref16','continuum_GL24','continuum_GL40']
    for name in names:
        vals=csvrow(name+'_history.csv')
        assert len(vals)==41
        assert all(abs(v['trace_E_minus_P'])<1e-13 for v in vals)
        assert all(v['E']>0 and v['h1']>0 and v['h2']>0 and v['h3']>0 for v in vals)
        assert all(0<v['energy_ratio_min']<=v['energy_ratio_max']<=1+1e-14 for v in vals)
        assert max(abs(v['H_constraint_C']) for v in vals)<1e-11
        assert all(abs(v['pi1']+v['pi2']+v['pi3'])<1e-13 for v in vals)

def test_exact_initial_cell_pressure():
    mu=[0,.5,1];pf=[0,.25,.75,1];W=[[.1,.25,.05],[.2,.15,.15]]
    pressure=[0.,0.,0.]
    for i in range(2):
      ma,mb=mu[i:i+2]
      mz=(ma*ma+ma*mb+mb*mb)/3
      for j in range(3):
        ta,tb=pf[j:j+2]
        c=.5+(math.sin(math.pi*tb)-math.sin(math.pi*ta))/(2*math.pi*(tb-ta))
        w=W[i][j]
        for k,v in enumerate([(1-mz)*c,(1-mz)*(1-c),mz]):pressure[k]+=w*v
    first=csvrow('continuum_GL40_history.csv')[0]
    assert max(abs(first['P'+str(i+1)]-pressure[i]) for i in range(3))<2e-14
    assert abs(sum(pressure)-.9)<3e-15

def test_source_grid_convergence_and_refinement():
    x={a['channel']:a for a in O['summary']}
    e1=x['stored_ref1']['max_source_h_gap_vs_GL_reference'];e4=x['stored_ref4']['max_source_h_gap_vs_GL_reference']
    e8=x['stored_ref8']['max_source_h_gap_vs_GL_reference'];e16=x['stored_ref16']['max_source_h_gap_vs_GL_reference']
    assert e1>e4>e8>e16>0
    assert 3.5 < e4/e8 <4.5 and 3.5<e8/e16<4.5
    assert e8<1e-5 and e16<1e-5
    assert x['gl24']['max_source_h_gap_vs_GL_reference']<5e-13

def test_source_continuity_and_shear():
    for name in ['continuum_GL24','continuum_GL40']:
      arr=csvrow(name+'_history.csv')
      assert max(abs(x['continuity_residual']) for x in arr)<8e-14
      assert any(abs(x['pi1'])>1e-3 for x in arr)
      assert abs(arr[-1]['sigma1']+arr[-1]['sigma2']+arr[-1]['sigma3'])<2e-15
    # Independent finite differencing of the saved state (not analytic RHS reuse)
    arr=csvrow('continuum_GL40_history.csv')
    for j in range(2,len(arr)-2):
      mid=arr[j];dt=arr[j+1]['u']-arr[j]['u']
      # 4th-order five-point independent finite-difference: 2nd-order with
      # delta-u=0.002 has a ~2e-5 discretization defect and is not a physics error.
      e_der=(-arr[j+2]['E']+8*arr[j+1]['E']-8*arr[j-1]['E']+arr[j-2]['E'])/(12*dt)
      analytic=-mid['theta']*mid['E']-sum(mid['h'+str(i)]*mid['P'+str(i)] for i in range(1,4))
      assert abs(e_der-analytic)<3e-6

def test_independent_time_integrator_order():
    rk=O['rk4_ref8']
    e32=rk['32']['max_h_error_vs_DOP853'];e64=rk['64']['max_h_error_vs_DOP853']
    assert 12<e32/e64<23
    assert rk['128']['max_h_error_vs_DOP853']<2e-14

def test_no_false_observation_or_certificate_claim():
    assert O['simulation_not_observation'] is True
    assert 'not mathematically certified' in O['continuum_quadrature_reference']
    assert 'not claimed for DOP853' in O['geometry_certificate_scope']