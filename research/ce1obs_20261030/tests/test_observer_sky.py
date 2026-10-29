from __future__ import annotations
import importlib.util
import json
import math
import os
import pathlib
import shutil
import sys
import numpy as np
import pytest

BASE=pathlib.Path(__file__).resolve().parents[1]
PARENT=pathlib.Path(os.environ.get('CE1P_PARENT_DIR', BASE.parent/'bass_ce1a_work/source_package'))
ARCHIVE=pathlib.Path(os.environ.get('CE1P_ARCHIVE_PATH', BASE.parent/'BASS_CE1P_PHYSICAL_HISTORY_20261029_FINAL.zip'))
spec=importlib.util.spec_from_file_location('observer_sky',BASE/'source/generate_observer_sky.py')
sky=importlib.util.module_from_spec(spec);sys.modules['observer_sky']=sky;spec.loader.exec_module(sky)

@pytest.fixture(scope='session')
def source():
    return sky.source_lock(PARENT,ARCHIVE)[0]

@pytest.fixture(scope='session')
def result():
    return json.loads((BASE/'data/results.json').read_text())


def test_original_source_manifest_binary_lock(source):
    assert source.ENERGY.shape==(2,3)
    assert sky.sha(ARCHIVE)==sky.PARENT_ZIP_SHA
    assert abs(source.ENERGY.sum()-.9)<1e-14
    assert [float(v).hex() for v in source.SHEAR]==[float(v).hex() for v in (.2,-.13,-.07)]


def test_gl_initial_measure_octant_solid_angle(source):
    for order in (24,40):
        x=sky.build_gl(source.MU,source.PHI,source.ENERGY,order)
        assert len(x['n'])==6*order**2
        assert abs(8*x['omega0_oct'].sum()-4*math.pi)<1e-12
        assert abs(x['mass'].sum()-.9)<1e-13
        assert np.max(abs(x['mass']-8*x['omega0_oct']*x['I0']))<3e-16


def test_inverse_tetrad_map_and_redshift(source):
    sam=sky.build_gl(source.MU,source.PHI,source.ENERGY,24)
    ell=np.array([.041,.013,.029])
    q=sky.ray_observer(ell,sam)
    inverse=q['e']*np.exp(ell)
    inverse/=np.linalg.norm(inverse,axis=1)[:,None]
    assert np.max(abs(inverse-sam['n']))<4e-16
    assert np.max(abs(q['r']-1/np.linalg.norm(q['e']*np.exp(ell),axis=1)))<8e-16
    assert np.all(q['r']>0)


def test_solid_angle_jacobian_numerical_area(source):
    sampler=sky.build_gl(source.MU,source.PHI,source.ENERGY,24)
    ell=np.array([.04,.01,.026])
    B=np.exp(-ell)
    def direction(mu,t):
        n=np.array([np.sqrt(1-mu**2)*np.cos(np.pi*t/2),
                    np.sqrt(1-mu**2)*np.sin(np.pi*t/2),mu])
        p=B*n
        return p/np.linalg.norm(p),n
    for mu,t in [(.2,.1),(.7,.55),(.95,.9),(.45,.85)]:
        h=1e-5
        e,n=direction(mu,t)
        dmu=(direction(mu+h,t)[0]-direction(mu-h,t)[0])/(2*h)
        dt=(direction(mu,t+h)[0]-direction(mu,t-h)[0])/(2*h)
        actual=np.linalg.norm(np.cross(dmu,dt))/(np.pi/2)
        r=np.linalg.norm(B*n)
        predicted=np.prod(B)/r**3
        assert abs(actual-predicted)/predicted<2e-8


def test_source_history_moment_reconstruction(result):
    assert len(result['channels'])==6
    for _,c in result['errors'].items():
        assert c['energy_positive']
        assert c['kinetic_energy']<1e-12
        assert c['kinetic_pressure']<1e-12
        assert c['a00']<1e-12
        assert c['a20']<1e-12
        assert c['a22']<1e-12
    for key in ('gl24','gl40'):
        assert result['errors'][key]['sky_energy']<1e-12
        assert result['errors'][key]['sky_pressure']<1e-12


def test_independent_scipy_parity_and_normalization(result):
    for d in result['independent_scipy_harmonic_checks'].values():
        assert d['max_polynomial_vs_scipy']<2e-13
        assert d['odd_l']<2e-13
        assert d['odd_m_or_imag']<2e-13
        assert d['conjugate_symmetry']<2e-13


def test_uniform_control_isotropic_scaling(source):
    w=np.outer(np.diff(source.MU),np.diff(source.PHI))*.9
    sam=sky.build_gl(source.MU,source.PHI,w,24)
    ell=np.array([.037,.037,.037])
    obs=sky.ray_observer(ell,sam)
    e,wobs=obs['e'],obs['atomic']
    E=wobs.sum();P=np.einsum('n,ni->i',wobs,e*e)
    H=sky.harmonics(e,wobs)
    assert abs(E-.9*np.exp(-4*.037))<1e-13
    assert np.max(abs(P-E/3))<1e-13
    assert max(abs(H[k]) for k in ('a20','a22','a40','a42','a44'))<2e-13
    I_obs=sam['I0']*obs['r']**4
    assert np.max(abs(I_obs-E/(4*math.pi)))<1e-14


def test_stored_rays_are_atomic_not_density(source):
    for n in (1,4,8,16):
        s=sky.build_stored(source.MU,source.PHI,source.ENERGY,n)
        assert s['type']=='atomic'
        assert 'I0' not in s
        assert len(s['n'])==6*n*n
        assert s['mass'].sum()==pytest.approx(.9,abs=5e-15)


def test_gl_cross_order_and_stored_refinement(result):
    conv=result['convergence']
    for key in ('a00','a20','a22','a40','a42','a44'):
        assert conv['gl24'][f'max_abs_{key}_vs_GL40']<1e-12
        seq=[conv[f'stored_ref{n}'][f'max_abs_{key}_vs_GL40'] for n in (1,4,8,16)]
        assert all(a>b>0 for a,b in zip(seq,seq[1:]))
    assert conv['stored_ref16']['max_abs_a40_vs_GL40']>1e-4


def test_generated_arrays_and_sky_measure():
    with (BASE/'data/gl40_observer_sky_positive_octant_u008.csv').open() as f:
        import csv
        r=list(csv.DictReader(f))
    assert len(r)==9600
    values={k:np.array([float(row[k]) for row in r]) for k in
       ('J_obs_dimless_per_sr','dOmegaObs_oct_node','energy_total8_node','jac_dOmegaObs_over_dOmega0','dOmega0_oct_node')}
    assert np.max(abs(8*values['J_obs_dimless_per_sr']*values['dOmegaObs_oct_node']-values['energy_total8_node']))<3e-16
    assert np.max(abs(values['dOmegaObs_oct_node']-values['dOmega0_oct_node']*values['jac_dOmegaObs_over_dOmega0']))<1e-16


def test_tamper_manifest_detected(tmp_path):
    p=tmp_path/'source_package'
    shutil.copytree(PARENT,p)
    with (p/'data/continuum_GL40_history.csv').open('a') as f:f.write('tamper\n')
    with pytest.raises(ValueError,match='manifest mismatch'):
        sky.source_lock(p,ARCHIVE)
