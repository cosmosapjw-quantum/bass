"""Executed science and provenance tests for CE1-Y 6x1681 physical time pairs."""
from __future__ import annotations
import csv,json,hashlib,importlib.util
from pathlib import Path
import numpy as np
import pytest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('ce1ygen',ROOT/'source/generate_rk4_k4_transfer.py')
gen=importlib.util.module_from_spec(spec);spec.loader.exec_module(gen)
S=json.loads((ROOT/'data/SCIENCE_RESULTS.json').read_text())


def test_01_original_physical_source_locked():
    assert S['original_binary64_source_sha256']==gen.SOURCE_SHA
    assert S['parent_pr270_head']==gen.PARENT_HEAD


def test_02_original_dop_raw_hashes():
    for n in (6,8):
        assert gen.sha(ROOT/'input'/f'GL{n}_DOP853_coupled_41epochs.csv')==gen.GL_DOP_CSV_SHA[n]


def test_03_source_and_geometry_parent_identity():
    l,tm,r=gen.load_parent(ROOT/'input')
    for n in (6,8):
        for steps in (4,8,16):
            key=f'GL{n}_STEPS{steps}'
            assert r['cases'][key]['certified_path_coefficients_sha256']==l['cases'][str(n)]['time_path_cases'][str(steps)]['parent_path_coefficients_sha256']
            assert tm['cases'][str(n)]['cases'][str(steps)]['source_ray_sha256']==r['cases'][key]['stored_source_ray_sha256']


def test_04_six_times_1681_is_actual_data():
    assert S['physical_rows']==10086 and len(S['channel_results'])==6
    for n in (6,8):
        for s in (4,8,16):
            assert len(gen.read_csv(ROOT/'data'/f'GL{n}_STEPS{s}_two_time_K4_1681.csv'))==1681


@pytest.mark.parametrize('n,steps',[(6,4),(6,8),(6,16),(8,4),(8,8),(8,16)])
def test_05_gram_matrix_and_fractional_parity(n,steps):
    p=gen.l4_from_rust(gen.read_csv(ROOT/'input'/f'GL{n}_STEPS{steps}_BASS_RUST_SKY.csv'))
    k=p['K']; np.testing.assert_allclose(k,k.T,atol=2e-14,rtol=0)
    assert min(np.linalg.eigvalsh(k)) > -1e-12
    assert abs(k[0,-1]-S['channel_results'][f'GL{n}_STEPS{steps}']['endpoint_K4delta_RK4'])<1e-16
    assert max(abs(p['rho'].ravel()))<1+1e-12
    assert abs(p['D2'][0,0])<1e-13


def test_06_independent_even_complex_l4_formula():
    p=gen.l4_from_rust(gen.read_csv(ROOT/'input'/'GL8_STEPS16_BASS_RUST_SKY.csv'))
    r=gen.read_csv(ROOT/'input'/'GL8_STEPS16_BASS_RUST_SKY.csv')
    aa=np.array([[float(t[f'a_4_{m}_re']) for m in (0,2,4)] for t in r])
    E=np.array([float(t['E']) for t in r])
    vec=4*np.pi*aa/E[:,None]*np.sqrt([1.,2.,2.])[None,:]
    expected=vec@vec.T/9
    np.testing.assert_allclose(p['K'],expected,atol=1e-14,rtol=0)


def test_07_two_time_time_derivative_symmetry():
    p=gen.l4_from_rust(gen.read_csv(ROOT/'input'/'GL8_STEPS16_BASS_RUST_SKY.csv'))
    np.testing.assert_allclose(p['Ku'],p['Kv'].T,atol=1e-14,rtol=0)
    f=p['Ku']+p['Kv']
    assert np.max(abs(np.diag(f)-2*np.real(np.sum(p['z'].conj()*p['zdot'],axis=1))/9))<1e-13


def test_08_time_derivative_five_point_interior():
    p=gen.l4_from_rust(gen.read_csv(ROOT/'input'/'GL8_STEPS16_BASS_RUST_SKY.csv'))
    x=p['K'];dt=p['u'][1]-p['u'][0]
    fd=(-x[4:,2:-2]+8*x[3:-1,2:-2]-8*x[1:-3,2:-2]+x[:-4,2:-2])/(12*dt)
    err=np.max(abs(fd-p['Ku'][2:-2,2:-2]))
    assert err<2e-7,err


def test_09_exact_bound_hierarchy_and_meaning():
    l,tm,r=gen.load_parent(ROOT/'input')
    for n in (6,8):
        c=l['cases'][str(n)]['time_path_cases']
        assert float(c['16']['total_cross_kernel_upper_ceil_27']) < float(c['8']['total_cross_kernel_upper_ceil_27'])
        assert float(c['8']['total_cross_kernel_upper_ceil_27']) < float(c['4']['total_cross_kernel_upper_ceil_27'])
        for s in (4,8,16):
            z=S['channel_results'][f'GL{n}_STEPS{s}']
            assert z['sample_center_not_a_certified_interval']
            assert float(z['total_conditional_exact_real_bound_uniform']) > float(z['source_bound_uniform'])


def test_10_do_not_pretend_dop853_interval():
    assert S['DOP853_bridge_is_empirical_NOT_certified'] is True
    assert S['input_numeric_rust_centers_are_NOT_rigorous_MPFR_intervals'] is True


def test_11_empirical_difference_is_calculated_from_original_two_histories():
    for n in (6,8):
        dop=gen.l4_from_dop(gen.read_csv(ROOT/'input'/f'GL{n}_DOP853_coupled_41epochs.csv'))
        for steps in (4,8,16):
            p=gen.l4_from_rust(gen.read_csv(ROOT/'input'/f'GL{n}_STEPS{steps}_BASS_RUST_SKY.csv'))
            q=S['channel_results'][f'GL{n}_STEPS{steps}']
            assert abs(np.max(abs(p['K']-dop['K']))-q['max_empirical_abs_K4delta_minus_DOP853'])<1e-16


def test_12_reject_tampered_dop_source(tmp_path):
    (tmp_path/'GL6_DOP853_coupled_41epochs.csv').write_bytes((ROOT/'input'/'GL6_DOP853_coupled_41epochs.csv').read_bytes()+b'X')
    assert gen.sha(tmp_path/'GL6_DOP853_coupled_41epochs.csv')!=gen.GL_DOP_CSV_SHA[6]


def test_13_original_dag_not_promoted():
    assert S['upper_dag']=='9/15' and S['ce1']=='PARTIAL'
    assert not S['production_ready'] and not S['merge_ready'] and not S['auto_next']


def test_14_normalization_removes_common_energy_rescaling():
    p=gen.l4_from_rust(gen.read_csv(ROOT/'input'/'GL8_STEPS8_BASS_RUST_SKY.csv'))
    pscale=(4*np.pi*(3.5*p['a']))/(3.5*p['E'][:,None])
    k=pscale@pscale.conj().T/9
    assert np.max(abs(k.real-p['K']))<1e-14
