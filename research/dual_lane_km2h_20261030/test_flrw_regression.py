"""Fresh hostile source and physical regression tests for original-user FLRW.

No Einstein-Bianchi I equation is invoked; no independent microphysics claimed.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pytest
import run_flrw_regression as regression

ROOT=Path(__file__).parent
ORIG=ROOT.parent
PHYS=ROOT/'evidence/flrw_regression_evidence.json'
CSV=ROOT/'evidence/flrw_recombination_regression_1to1600.csv'

@pytest.fixture(scope='module')
def evidence():
    return json.loads(PHYS.read_text())

@pytest.fixture(scope='module')
def table():
    return np.genfromtxt(CSV,delimiter=',',names=True)


def test_original_unmodified_uploaded_zip_source_bytes(evidence):
    assert regression.sha(ORIG/'HYREC-2-master.zip')==regression.EXPECTED['HYREC-2-master.zip']
    assert regression.sha(ORIG/'class_public-master.zip')==regression.EXPECTED['class_public-master.zip']


def test_real_native_HYREC_two_paths_byte_identical(evidence):
    p=ROOT/'hyrec_run/output_xe.dat'
    assert p.read_bytes()==(ORIG/'BASS_KM2H_20261030/upstream/HYREC-2-master/output_xe.dat').read_bytes()
    assert regression.sha(p)==regression.EXPECTED['HYREC_native']


def test_real_native_CLASS_background_and_thermodynamics_byte_identical(evidence):
    for name,original in [('thermodynamics','CLASS_thermo'),('background','CLASS_background')]:
        p=ROOT/'class_run'/('flrw_regression_00_'+name+'.dat')
        q=ORIG/'BASS_KM2H_20261030'/('class_same_parameters_00_'+name+'.dat')
        assert p.read_bytes()==q.read_bytes()
        assert regression.sha(p)==regression.EXPECTED[original]


def test_matched_cosmological_input_and_no_reionization(evidence):
    inp=(ROOT/'hyrec_run/input.dat').read_text().split('=====================================================================')[0]
    cl=(ROOT/'class_run/flrw_regression.ini').read_text()
    vals=[float(x.strip()) for x in inp.splitlines()[0:5]]
    assert vals==pytest.approx([.6735837,2.7255,.0494142797907188,.31242079216478097,0.],abs=1e-14)
    assert 'h = 0.6735837' in cl and 'YHe = 0.245' in cl
    assert 'Omega_cdm = 0.2630065123740622' in cl
    assert 'reio_parametrization = reio_none' in cl
    assert 'reio' in evidence['cosmological_input']['reionization'] or evidence['cosmological_input']['reionization']=='none'


def test_original_8000_native_rows_and_independent_1600_comparison_grid(evidence,table):
    assert evidence['HYREC_native_rows']==8000
    assert len(table)==1600
    assert np.array_equal(table['z'],np.arange(1,1601,dtype=float))
    assert np.isfinite(table['xe_hyrec_per_H']).all()
    assert np.all(table['xe_hyrec_per_H']>0)
    assert np.all(table['Tb_class_K']>0)
    assert np.all(table['Gamma_T_hyrec_per_s']>0)


def test_helium_ionization_is_not_falsely_clipped_to_one():
    h=np.loadtxt(ROOT/'hyrec_run/output_xe.dat')
    assert h[0,0]==8000 and h[-1,0]==1
    assert h[0,1]>1.0


def test_native_class_visibility_is_exact_collision_output_identity(evidence):
    assert evidence['CLASS_native_visibility_identity_max']<1e-9


def test_dimensionally_correct_opacity_in_Mpc_and_SI(evidence,table):
    sel=(table['z']>=300)&(table['z']<=1500)
    z=table['z'][sel]
    predicted=table['n_e_hyrec_per_m3'][sel]*regression.SIGMA_T*regression.MPC_M/(1+z)
    rel=np.max(abs(predicted/table['kappa_prime_hyrec_Mpc_inverse'][sel]-1))
    assert rel<1e-8
    predicted_gamma=table['n_e_hyrec_per_m3'][sel]*regression.SIGMA_T*regression.LIGHT_C
    assert np.max(abs(predicted_gamma/table['Gamma_T_hyrec_per_s'][sel]-1))<1e-10
    assert abs(evidence['nH_today_from_CLASS_per_m3']-.18998243579319968)<3e-8


def test_hydrogen_number_density_independent_background_formula(evidence):
    G=6.67430e-11
    h=evidence['cosmological_input']['h']
    H0=100000*h/regression.MPC_M
    mH=1.6735575e-27
    nH_approx=(1-evidence['cosmological_input']['YHe'])*evidence['cosmological_input']['Omega_b']*(3*H0**2/(8*np.pi*G))/mH
    assert abs(nH_approx/evidence['nH_today_from_CLASS_per_m3']-1)<1e-4


def test_FlRW_recombination_xe_and_Tm_source_scoped_limits(evidence,table):
    m=(table['z']>=800)&(table['z']<=1500)
    assert np.max(abs(table['xe_hyrec_per_H'][m]/table['xe_class_per_H'][m]-1))<3e-4
    assert np.max(abs(table['Tm_hyrec_K'][m]-table['Tb_class_K'][m]))<.8
    assert abs(evidence['xe_relative_diff_z1100']+3.054115378686717e-5)<2e-11


def test_HyRec_class_optical_depth_unity_and_correct_z1_anchor(evidence,table):
    assert abs(evidence['CLASS_z_star_from_native_stdout']-1089.753288)<1e-7
    assert abs(evidence['HYREC_CLASS_H_HYBRID_z_star']-evidence['CLASS_z_star_from_native_stdout'])<0.1
    assert abs(table['tau_hybrid_class_H_z1_anchor'][0]-table['tau_class'][0])<1e-14
    assert np.all(np.diff(table['tau_hybrid_class_H_z1_anchor'])>0)
    assert np.all(np.diff(table['tau_class'])>0)


def test_native_class_zrec_not_confused_with_integer_grid_peak(evidence):
    assert abs(evidence['CLASS_z_rec_from_native_stdout']-1088.669130)<1e-6
    assert evidence['HYREC_CLASS_H_HYBRID_visibility_peak_grid_z_resolution_1']==1089.
    assert abs(evidence['CLASS_z_rec_from_native_stdout']-1089)>0.3


def test_Thomson_rate_against_expansion_is_nontrivial(table):
    assert 10<table['Gamma_T_over_H_class'][1099]<20
    assert table['Gamma_T_over_H_class'][799]<1


def test_fail_closed_on_byte_mutation(tmp_path):
    fake=tmp_path/'source.dat';fake.write_bytes(b'mutation')
    with pytest.raises(ValueError,match='ORIGINAL_SOURCE_BYTE_LOCK_FAILED'):
        regression.check_hash(fake,regression.EXPECTED['HYREC_native'],'HYREC native output')


def test_no_Bianchi_claim_and_DAG_protected(evidence):
    assert evidence['scope'].startswith('FLRW_ONLY')
    assert evidence['HyRec2020_CLASS_HYREC2_shared_atomic_source']
    assert evidence['frozen_BASS_upper_DAG']=='9/15'
    assert evidence['KM2']=='PARTIAL'
    assert not evidence['production_ready'] and not evidence['merge_ready'] and not evidence['auto_next']
