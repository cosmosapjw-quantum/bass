"""CI evidence-only regression, deliberately does NOT claim native CLASS/HYREC rebuild.

The native rebuild is documented in source-complete 17MB archived files with
original upstream user ZIPs. This test only checks frozen physical comparisons.
"""
from pathlib import Path
import json,hashlib
import numpy as np
import pytest

HERE=Path(__file__).resolve().parent
DATA=HERE/'source_data'

def j():return json.loads((DATA/'flrw_regression_evidence.json').read_text())
def rows():return np.genfromtxt(DATA/'flrw_recombination_regression_1to1600.csv',delimiter=',',names=True)

def test_evidence_is_flrw_not_bianchi():
    d=j();assert d['scope'].startswith('FLRW_ONLY')
    assert d['KM2']=='PARTIAL' and d['frozen_BASS_upper_DAG']=='9/15'
    assert d['HyRec2020_CLASS_HYREC2_shared_atomic_source']
    assert not d['production_ready'] and not d['auto_next'] and not d['merge_ready']

def test_expected_raw_source_SHA_is_recorded():
    d=j();o=d['sources_sha256']
    assert o['HYREC_2_uploaded_source_zip_sha256']=='f0b8bba1547ae9da83a0e663f57056884c689683396e1cf9a58bee1904040ac0'
    assert o['CLASS_uploaded_source_zip_sha256']=='d1b2e1ce2b49de472e2cca9a327dc51c351e75bc0a2ad37d2e6538df76b289b7'
    assert o['HYREC_native_output_sha256']=='1ac2ddad6aa0e3c4080883c71479e2e398669468e4813075ec61bca86b7afc40'

def test_1600_nonnegative_native_physical_rows():
    d=j();x=rows()
    assert len(x)==1600 and d['flrw_table_rows']==1600
    assert np.array_equal(x['z'],np.arange(1.,1601.))
    for k in ['xe_hyrec_per_H','xe_class_per_H','Tm_hyrec_K','Tb_class_K','n_e_hyrec_per_m3','Gamma_T_hyrec_per_s','tau_class']:
        assert np.isfinite(x[k]).all() and np.min(x[k])>0

def test_atomic_source_crosscheck_is_scoped():
    d=j();x=rows()
    m=(x['z']>=800)&(x['z']<=1500)
    assert np.max(abs(x['xe_hyrec_per_H'][m]/x['xe_class_per_H'][m]-1))<3e-4
    assert np.max(abs(x['Tm_hyrec_K'][m]-x['Tb_class_K'][m]))<.8
    assert abs(d['xe_relative_diff_z1100']+3.054115378686717e-5)<2e-11

def test_class_native_peak_vs_unit_grid_separated():
    d=j()
    assert abs(d['CLASS_z_rec_from_native_stdout']-1088.66913)<1e-6
    assert d['HYREC_CLASS_H_HYBRID_visibility_peak_grid_z_resolution_1']==1089.
    assert d['HYREC_CLASS_H_HYBRID_z_star']-d['CLASS_z_star_from_native_stdout']<.1

def test_observed_optical_depth_is_monotone_and_z1_anchor_fixed():
    x=rows();assert abs(x['tau_class'][0]-x['tau_hybrid_class_H_z1_anchor'][0])<1e-13
    assert np.all(np.diff(x['tau_class'])>0)
    assert np.all(np.diff(x['tau_hybrid_class_H_z1_anchor'])>0)

def test_physical_Mpc_vs_SI_collision_rate():
    x=rows();s=6.6524587051e-29;M=3.0856775814913673e22;c=299792458.
    m=(x['z']>=300)&(x['z']<=1500)
    conformal=x['n_e_hyrec_per_m3'][m]*s*M/(1+x['z'][m])
    assert np.max(abs(conformal/x['kappa_prime_hyrec_Mpc_inverse'][m]-1))<1e-8
    assert np.max(abs(x['n_e_hyrec_per_m3'][m]*s*c/x['Gamma_T_hyrec_per_s'][m]-1))<1e-10

def test_baryon_density_and_thomson_to_Hubble():
    d=j();x=rows()
    assert .18<d['nH_today_from_CLASS_per_m3']<.2
    assert 10<x['Gamma_T_over_H_class'][1099]<20

def test_unchanged_numeric_sha_manifest_before_machine_claim():
    m=json.loads((DATA/'FLRW_FROZEN_MANIFEST.json').read_text())
    for name,digest in m['payload_sha256'].items():
        assert hashlib.sha256((DATA/name).read_bytes()).hexdigest()==digest
