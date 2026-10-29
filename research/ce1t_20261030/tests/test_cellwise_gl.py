"""CE1-T same six-cell physical source; independent tests of Rust GL sky convergence."""
import json,math,os
from pathlib import Path
import numpy as np
import pytest
from scipy.special import sph_harm_y
from research.ce1t_20261030.cellwise_gl_rust import (make_cell_rays,read_history,
    c_and_cprime,run_rust,frozen_source_identity,CELL_E,DEFAULT_ORDERS)
DATA=Path(os.environ.get('BASS_CE1T_RESULTS','research/ce1t_20261030/data/results.json'))
HISTORY=Path(os.environ.get('BASS_CE1T_HISTORY','research/ce1q_20261030/parent_verified/data/continuum_GL40_history.csv'))
BIN=Path(os.environ.get('BASS_CE1T_RUST','research/ce1r_20261030/sky_time_derivative')).resolve()

def result():return json.loads(DATA.read_text())

def test_original_exact_cell_input_identity():
    assert frozen_source_identity()=='022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035'
    assert abs(float(CELL_E.sum())-.9)<1e-15

@pytest.mark.parametrize('n',[1,2,3,4,6,8,12])
def test_gauss_positive_unit_rays_and_8_octant_energy(n):
    rays,w=make_cell_rays(n)
    assert rays.shape==(6*n*n,3) and w.shape==(6*n*n,)
    assert (w>0).all() and np.isfinite(rays).all()
    np.testing.assert_allclose((rays*rays).sum(axis=1),1.,atol=3e-14,rtol=0)
    assert abs(float(w.sum())-.9)<2e-13

@pytest.mark.parametrize('bad',[True,0,-1,65,2.0])
def test_illegal_quadrature_order_fails_closed(bad):
    with pytest.raises(ValueError):make_cell_rays(bad)

@pytest.mark.parametrize('n',[2,3,4,6])
def test_exact_even_polynomial_moment_in_each_cell(n):
    rays,w=make_cell_rays(n)
    # For a constant density in each original cell GL n>=2 integrates mu^2 exactly.
    from research.ce1t_20261030.cellwise_gl_rust import MU,PHI
    offset=0
    for i in range(2):
        for j in range(3):
            sl=slice(offset,offset+n*n)
            target=float(CELL_E[i,j])*(MU[i]**2+MU[i]*MU[i+1]+MU[i+1]**2)/3
            assert abs(float((w[sl]*rays[sl,2]**2).sum())-target)<1e-14
            offset+=n*n

def test_41_epoch_observed_convergence_and_frozen_reference():
    d=result();assert d['record_count']==41 and d['upper_dag']=='9/15'
    assert d['empirical_minimum_uniform_order']==6
    stats=d['results'];assert set(map(int,stats))==set(DEFAULT_ORDERS)
    assert stats['6']['rays']==216 and stats['8']['rays']==384
    assert stats['4']['max_abs_delta_C4prime_vs_GL40']>1e-9
    assert stats['6']['max_abs_delta_C4prime_vs_GL40']<2e-12
    assert stats['6']['max_abs_delta_C4_vs_GL40']<1e-12
    assert stats['8']['max_abs_delta_C4prime_vs_GL40']<3e-15
    assert abs(stats['40']['stats'][-1]['C4prime']+0.00014789130274602826)<2e-12
    assert abs(stats['40']['stats'][-1]['E']-0.7584190590089329)<2e-11
    assert len(read_history(HISTORY))==41

def _scipy_c4(rays,w,ell):
    mm=np.exp(-np.asarray(ell));q=rays*mm
    radius=np.linalg.norm(q,axis=1);base=-q/radius[:,None]
    ww=w*np.prod(mm)*radius/8
    dirs=[]
    for sx in (-1,1):
        for sy in (-1,1):
            for sz in (-1,1):dirs.append(base*np.array([sx,sy,sz]))
    n=np.concatenate(dirs)
    weight=np.tile(ww,8)
    theta=np.arccos(np.clip(n[:,2],-1,1));phi=np.mod(np.arctan2(n[:,1],n[:,0]),2*np.pi)
    a=[np.dot(weight,np.conjugate(sph_harm_y(4,m,theta,phi))) for m in range(-4,5)]
    return sum(abs(z)**2 for z in a)/9

def test_216_ray_native_rust_vs_independent_scipy_sky_derivative():
    hist=read_history(HISTORY)
    rays,w=make_cell_rays(6)
    rows,_=run_rust(BIN,rays,w,[hist[-1]])
    C4,C4prime=rows[-1]['C4'],rows[-1]['C4prime']
    ell=np.array([hist[-1][f'ell{i}'] for i in (1,2,3)])
    h=np.array([hist[-1][f'h{i}'] for i in (1,2,3)])
    eps=1e-5
    Cplus=_scipy_c4(rays,w,ell+eps*h)
    Cminus=_scipy_c4(rays,w,ell-eps*h)
    assert abs(C4-_scipy_c4(rays,w,ell))<5e-13
    assert abs(C4prime-(Cplus-Cminus)/(2*eps))<2e-9
