"""Physics-first CE1-U tests, independent SciPy Ylm and exact rational invariants."""
from __future__ import annotations
import csv,json,math,sys
from fractions import Fraction as F
from pathlib import Path
import numpy as np
import pytest
from scipy.special import sph_harm_y
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'research'/'ce1u_20261030'/'source'))
sys.path.insert(0,str(ROOT/'research'/'ce1t_20261030'))
import ce1u_cert_source as C
import ce1u_physical_histories as H
from cellwise_gl_rust import make_cell_rays,frozen_source_identity
DATA=ROOT/'research'/'ce1u_20261030'/'data'

def read(n):
    with (DATA/f'GL{n}_coupled_41epochs.csv').open() as f:return [{k:float(v) for k,v in r.items()} for r in csv.DictReader(f)]

def cert(n):return json.loads((DATA/f'GL{n}_source_exact_bound.json').read_text())

def test_01_source_identity():
    assert frozen_source_identity()==C.SOURCE_SHA=='022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035'


def test_02_angular_moment_trace_symbolic():
    rows=[C.continuum_symbol(1,0,0),C.continuum_symbol(0,1,0),C.continuum_symbol(0,0,1)]
    sums=tuple(sum(row[k] for row in rows) for k in range(3))
    assert sums==(C.ENERGY,F(0),F(0))


def test_03_wolfram_cell_element():
    # mean cos² on phi=[0,pi/8] = 1/2 + sqrt(2)/pi,
    # mean(1-mu²) on mu=[0,1/2] = 11/12.
    phi=C.phi_avg_symbol(1,0,F(0),F(1,4))
    assert phi==(F(1,2),F(0),F(1))
    assert C.mu_avg(1,0,0,F(0),F(1,2))==F(11,12)


def test_04_pi_sqrt2_bounds():
    assert C.PI_L<C.PI_H and abs(C.PI_L-F('3.14159265358979323846264338327950288419716939937510'))<F(1,10**49)
    assert C.SQ_L*C.SQ_L<=2<=C.SQ_H*C.SQ_H


@pytest.mark.parametrize('n', [6,8])
def test_05_positivity_and_hash(n):
    ray,w=make_cell_rays(n)
    c=cert(n)
    import hashlib
    assert (c['stored_gl_hashes']['ray_sha256']==hashlib.sha256(ray.tobytes()).hexdigest())
    assert (c['stored_gl_hashes']['mass_sha256']==hashlib.sha256(w.tobytes()).hexdigest())
    assert w.min()>0 and abs(w.sum()-.9)<1e-13
    assert np.max(np.abs(np.sum(ray*ray,axis=1)-1))<1e-12


@pytest.mark.parametrize('n', [6,8])
def test_06_exact_rational_source_bound(n):
    c=cert(n)
    assert c['certificate']=='EXACT_RATIONAL_REAL_SOURCE_BOUND_NOT_FLOAT_RUNTIME_NOT_MPFR192'
    eps=F(c['maximum_epsilon_source_exact'])
    assert 0<eps<F(1,100000)
    assert 0<c['final_h_ell_bound']<1e-5
    assert c['meets_target']
    assert c['K']==12 and c['moment_count']==559
    assert c['stored_ray_nonunit_weighted_defect']<1e-12


@pytest.mark.parametrize('n',[6,8])
def test_07_physical_history_constraints(n):
    r=read(n)
    assert len(r)==41 and np.max(abs(np.diff([x['u'] for x in r])-.002))<2e-17
    assert max(abs(x['Hamiltonian_C']) for x in r)<1e-10
    assert max(x['trace_gap'] for x in r)<1e-12
    assert max(x['continuity_gap'] for x in r)<1e-12
    assert max(x['pressure_dot_gap'] for x in r)<1e-12
    assert min(x['h2'] for x in r)>0 and max(x['h1'] for x in r)<1


@pytest.mark.parametrize('n',[6,8])
def test_08_harmonics_vs_independent_scipy(n):
    rays,mass=make_cell_rays(n)
    for row in (read(n)[0],read(n)[20],read(n)[-1]):
        ell=np.array([row[f'ell{i}'] for i in (1,2,3)])
        Ht=np.array([row[f'h{i}'] for i in (1,2,3)])
        q=rays*np.exp(-ell)
        r=np.linalg.norm(q,axis=1)
        s=-q/r[:,None]
        ww=mass*np.exp(-ell.sum())*r/8
        allsky=np.concatenate([s*np.array([i,j,k]) for i in (-1.,1.) for j in (-1.,1.) for k in (-1.,1.)])
        w=np.tile(ww,8)
        th=np.arccos(np.clip(allsky[:,2],-1,1));ph=np.mod(np.arctan2(allsky[:,1],allsky[:,0]),2*np.pi)
        for l,m in ((2,0),(2,2),(4,0),(4,2),(4,4)):
            actual=np.dot(w,np.conjugate(sph_harm_y(l,m,th,ph)))
            assert abs(actual-row[f'a{l}{m}'])<1e-12


@pytest.mark.parametrize('n',[6,8])
def test_09_real_time_derivative(n):
    x=read(n);du=.002
    for i in (4,20,37):
        for key in ('C2','C4'):
            fd=(x[i-2][key]-8*x[i-1][key]+8*x[i+1][key]-x[i+2][key])/(12*du)
            assert abs(fd-x[i][key+'prime'])<1e-8


@pytest.mark.parametrize('n',[6,8])
def test_10_four_panel_rk4_diagnostic(n):
    data=json.loads((DATA/f'GL{n}_coupled_summary.json').read_text())
    assert data['rk4_endpoint_h_gaps']['4']<1e-5
    assert data['rk4_endpoint_h_gaps']['8']<data['rk4_endpoint_h_gaps']['4']/10
    assert data['GL_ODE_status']=='NUMERICAL_NOT_RIGOROUS_IVP_CERTIFICATE'


def test_11_four_panel_h_comparison_to_gl40_reference():
    # GL40 is a numerical, NOT a certified continuum enclosure.
    rows40=[]
    ref=ROOT/'research'/'ce1t_20261030'/'local_GL40_history_authority.csv'
    if not ref.exists(): ref=ROOT/'research'/'ce1q_20261030'/'parent_verified'/'data'/'continuum_GL40_history.csv'
    with ref.open() as f:
        rows40=[{k:float(v) for k,v in r.items()} for r in csv.DictReader(f)]
    for n in (6,8):
        x=read(n)
        gap=max(abs(a[f'h{i}']-b[f'h{i}']) for a,b in zip(x,rows40) for i in (1,2,3))
        assert gap<1e-8


def test_12_rational_gronwall_constants():
    # t=2/25, L=7 and e^(Lt) <=1/(1-Lt)=25/11.
    assert 7*F(2,25)==F(14,25)
    assert F(1)/(1-7*F(2,25))==F(25,11)
    assert F(2,25)/(1-7*F(2,25))==F(2,11)


@pytest.mark.parametrize('n',[6,8])
def test_13_true_mpfr192_directed_knot_values(n):
    data=json.loads((DATA/'MPFR192_source_knots.json').read_text())
    assert data['source_identity']==C.SOURCE_SHA
    vals=data['results'][f'GL{n}']
    assert [x['index'] for x in vals]==[0,10,20,30,40]
    for x in vals:
        assert x['precision_bits']==192
        for interval in [x['E_interval']]+x['P_intervals']:
            assert interval[0]<=interval[1] and 0<interval[0]<.95
            assert interval[1]-interval[0]<2e-13
        assert x['max_binary64_gap_from_mpfr_interval']<1e-12
