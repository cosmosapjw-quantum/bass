"""CE1-AE scoped falsification, provenance, numerical physical and exact-rational checks."""
from __future__ import annotations
import csv,hashlib,json,math,sys
from fractions import Fraction as F
from pathlib import Path
import numpy as np
import pytest
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'source'))
sys.path.insert(0,str(BASE/'input'))
from cellwise_gl_rust import frozen_source_identity,make_cell_rays
from spectral_gap_certificate import main as certify_physical, A,L,PARENT
from certify_dyadic_integral_surrogate import certify
from continuous_kernel_physics import angular,hermite_41_gram,COEFF
SRC='022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035'

def read():return json.loads((BASE/'data'/'CONTINUOUS_TIME_INTEGRATED_PHYSICS.json').read_text())

def record(gl):
    with (BASE/'data'/'COUPLED_SIXCELL_DENSE_TIME_SKY.csv').open() as f:
        return [r for r in csv.DictReader(f) if int(r['GL'])==gl]

def test_original_source():
    assert frozen_source_identity()==SRC
    for n in (6,8,16,64):
        ray,mass=make_cell_rays(n)
        assert len(mass)==6*n*n and (mass>0).all()
        assert abs(float(mass.sum())-.9)<1e-13

def test_original_saved_identity_and_new_source_evolution():
    data=read()
    for n in (6,8):
        assert data['data'][str(n)]['original_saved_max_state_delta']<5e-13
    assert len(data['data'])==4
    for n in (6,8,16,64):assert data['data'][str(n)]['nfev']==47

def test_integral_gap_rational():
    d=certify_physical()
    assert F(d['strict_uniform_du_integral_Gram_lambda3_lower_rational'])>F(1,10**23)
    assert d['numerical_spectrum_not_used_in_inequality']

def test_negative_sample_gate_control():
    assert 41*A*A<F(3,10**12)
    assert not 41*A*A<F(1,10**12)

def test_derivative_constants_dimensionless():
    # Upper bound for all normalized 3 component l4 harmonics in [0,1] simplex.
    assert F(56,3)**2 +F(155,4)**2 + F(21)**2 <50**2
    assert F(27,10)*50<L

def test_dense_data_and_physical_trace():
    for n in (6,8,16,64):
        rows=record(n)
        assert len(rows)==401
        assert abs(float(rows[-1]['u'])-.08)<1e-15
        for row in rows:
            E=float(row['E']);P=np.array([float(row[f'P{i}']) for i in (1,2,3)])
            assert E>0 and np.all(P>0)
            assert abs(sum(P)-E)<2e-13
            assert abs(float(row['Hamiltonian_C']))<3e-11
            X=np.array([float(row[k]) for k in ('X40','X42','X44')])
            assert abs(float(row['C4_fractional'])-float(X@X))<2e-15
            assert abs(float(row['C4_raw_energy'])-(E/(4*math.pi))**2*float(X@X))<2e-15

def test_growth_of_fractional_vs_decay_raw():
    data=read()['data']
    for n in ('6','8','16','64'):
        d=data[n]
        assert d['terminal_C4_fractional']>d['initial_C4_fractional']
        assert d['terminal_C4_raw_energy']<d['initial_C4_raw_energy']
        assert d['time_avg_C4_fractional']>0
        assert d['time_avg_C4_raw_energy']>0

def test_integrated_matrix_and_svd_consistency():
    for n in ('6','8','16','64'):
        d=read()['data'][n]
        G=np.array(d['time_Gram_G'])
        np.testing.assert_allclose(G,G.T,atol=1e-14,rtol=0)
        s=np.linalg.svd(G,compute_uv=False)
        e=np.array(d['time_Gram_eigenvalues_numeric'])
        np.testing.assert_allclose(s,e,rtol=1e-5,atol=2e-17)
        assert np.min(e)>0

def test_high_resolution_real_source_time_comparison():
    for n in ('6','8'):
        d=read()['data'][n]
        assert d['max_relative_dense_vs_fine_eigen_difference']<5e-4
        herm=np.array(d['Hermite_from_original_41']['time_Gram_eigenvalues_numeric'])
        num=np.array(d['fine_time_Gram_eigenvalues_numeric'])
        assert np.max(abs(herm-num)/num)<1e-5

def test_GL16_GL64_converge_in_physical_time_eigen():
    a=read()['data']['16'];b=read()['data']['64']
    ea=np.array(a['time_Gram_eigenvalues_numeric']);eb=np.array(b['time_Gram_eigenvalues_numeric'])
    assert np.max(abs(ea-eb)/eb)<1e-7

def test_independent_positive_dyadic_Simpson_surrogate_and_scope():
    r=certify(8)
    assert r['all_three_sylvester_minors_strict_positive']
    assert r['physical_continuous_time_operator_certified_by_this_Simpson_witness'] is False

def test_off_source_negative_mutation():
    ray,mass=make_cell_rays(6)
    fake=mass.copy();fake[0]=0
    E,P,X=angular(ray*ray,fake,[0,0,0])
    assert E<.9 and not np.array_equal(mass,fake)

@pytest.mark.parametrize('n',[6,8,16,64])
def test_integrated_physical_spectrum_positive_and_total_power(n):
    d=read()['data'][str(n)]
    eig=d['time_Gram_eigenvalues_numeric']
    assert eig[0]>eig[1]>eig[2]>0
    assert abs(sum(eig)-.08*d['time_avg_C4_fractional'])<1e-12
    assert eig[2] > 1e-14
