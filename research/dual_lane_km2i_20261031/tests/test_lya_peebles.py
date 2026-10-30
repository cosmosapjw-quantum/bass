"""KM2I real source-locked microphysics tests: no fictitious full spectral closure."""
import hashlib,json,os
from pathlib import Path
import numpy as np
import pytest
from research.dual_lane_km2i_20261031 import lya_peebles as m

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'results/KM2I_REAL_LYA_PEEBLES_2GRID.json'
@pytest.fixture(scope='session')
def evidence(tmp_path_factory):
    p=os.environ.get('KM2I_SCIENCE_JSON')
    if p:
        return json.loads(Path(p).read_text())
    return m.run_science(tmp_path_factory.mktemp('km2i')/'science.json')

def test_pinned_original_class_source_contract():
    src=m.source_guards()
    assert src[m.REF_SRC]==m.REF_BLOB
    assert src['source_data/wrap_recfast.c']==m.ORIGINAL_RECFAST_BLOBS['wrap_recfast.c']
    assert src['source_data/wrap_recfast.h']==m.ORIGINAL_RECFAST_BLOBS['wrap_recfast.h']

def test_source_tamper_fail_closed(monkeypatch):
    monkeypatch.setitem(m.ORIGINAL_RECFAST_BLOBS,'wrap_recfast.h','0'*64)
    with pytest.raises(ValueError,match='ORIGINAL_CLASS_RECFAST_BYTES_CHANGED'):
        m.source_guards()

def test_recfast_2022_atomic_coefficients_physically_dimensioned():
    assert 5.e-19<m.alpha_caseB(3000)<8.e-19
    assert 400<m.beta_caseB(3000)<650
    assert m.TWO_PHOTON==8.2245809
    assert m.H_PLANCK>0 and m.K_B>0
    with pytest.raises(ValueError):m.alpha_caseB(-1)

def test_sobolev_optically_thick_analytic_shear_quadrupole():
    from research.dual_lane_km2h_20261030.external_opacity_bianchi import ExternalFLRWOpacityBianchi
    s=ExternalFLRWOpacityBianchi(ntheta=16)
    x=.3
    a=m.sobolev_directional(s.H0,s.sigma0,s.n0,s.w0,s.nH_rest0,x,s.Tstar_seconds)
    assert a['tau_min']>1.e8
    assert abs(a['mean_s']/a['iso_s']-1)<1e-9
    assert np.max(abs(a['quadrupole']-a['quadrupole_thick_theory']))<2e-9
    assert np.linalg.norm(a['quadrupole'])>.05
    assert abs(np.trace(a['quadrupole']))<2e-9

def test_zero_shear_vacuum_optical_depth_limits():
    from research.dual_lane_km2h_20261030.external_opacity_bianchi import ExternalFLRWOpacityBianchi
    s=ExternalFLRWOpacityBianchi(ntheta=16)
    z=np.zeros((3,3))
    a=m.sobolev_directional(.4,z,s.n0,s.w0,s.nH_rest0,.3,s.Tstar_seconds)
    assert abs(a['mean_s']/a['iso_s']-1)<2e-12
    assert np.linalg.norm(a['quadrupole'])<2e-9
    thin=m.sobolev_directional(.4,z,s.n0,s.w0,1e-10,1e-6,s.Tstar_seconds)
    assert 1.-2e-7<thin['pesc_min']<=1
    with pytest.raises(ValueError,match='Negative directional expansion'):
        m.sobolev_directional(.001,s.sigma0,s.n0,s.w0,s.nH_rest0,.3,s.Tstar_seconds)

def test_six_charged_balanced_3level_physics_and_actual_ode(evidence):
    assert evidence['upper_dag']=='9/15' and evidence['km2']=='PARTIAL'
    assert set(evidence['cases'])=={'GL12','GL16'}
    for n,c in evidence['cases'].items():
        assert c['parent_ode_nfev']>0
        for mode,p in c['chemical_modes'].items():
            assert p['rhs_evals']>10 and len(p['epochs'])==41
            assert 0<p['xe_end']<.3221
            assert all(0<r['x']<1 and r['n_e_m3']==r['n_p_m3'] for r in p['epochs'])
            assert all(r['charge_source_C_m3']==0 for r in p['epochs'])
            assert p['ray_optical_depth_mean']>0
            assert p['ray_optical_depth_max']>p['ray_optical_depth_min']>0
            assert len(p['ray_optical_depths'])==c['rays']

def test_real_dynamic_xe_not_imported_hyrec(evidence):
    for c in evidence['cases'].values():
        p=c['chemical_modes']['angular']['epochs']
        assert abs(p[0]['x']-p[0]['xe_hyrec_prescribed'])<2e-13
        assert p[-1]['x']<p[-1]['xe_hyrec_prescribed']-.05
        assert p[-1]['x']<.1 and p[-1]['binding_energy_change_eV_per_H']>3
        assert all(p[i+1]['x']<p[i]['x'] for i in range(40))

def test_chemical_original_thomson_opacity_counterfactual_real_effect(evidence):
    for c in evidence['cases'].values():
        a=c['chemical_modes']['angular']
        assert 6.5<a['ray_optical_depth_mean']<8.0
        assert -6<a['ray_optical_depth_difference_from_parent']<-5
        assert a['parent_prescribed_ray_optical_depth_mean']>12
        last=a['epochs'][-1]
        assert last['missing_binding_to_photon_energy_ratio']>0
        assert last['missing_binding_to_photon_energy_ratio']<1e-7

def test_directional_lyalpha_numerical_first_order_vs_chemical_scalar_cancellation(evidence):
    for c in evidence['cases'].values():
        v=c['comparison']
        assert v['initial_lya_quad_F']>.08
        assert v['final_lya_quad_F']>.06
        assert v['max_xe_abs']<2e-10
        assert abs(v['lyalpha_angular_vs_isotropic_tau_mean'])<2e-9
        assert v['max_C_angular_vs_isotropic']<1e-10
    assert evidence['cases']['GL16']['chemical_modes']['angular']['max_line_quad_vs_analytic']<3e-9
    assert evidence['cases']['GL12']['chemical_modes']['angular']['max_line_quad_vs_analytic']<3e-8

def test_reconvergence_across_real_two_original_angular_grids(evidence):
    a=evidence['cases']['GL12'];b=evidence['cases']['GL16']
    assert abs(a['chemical_modes']['angular']['xe_end']-b['chemical_modes']['angular']['xe_end'])<3e-9
    assert abs(a['chemical_modes']['angular']['ray_optical_depth_mean']-b['chemical_modes']['angular']['ray_optical_depth_mean'])<5e-4
    assert abs(a['comparison']['initial_lya_quad_F']-b['comparison']['initial_lya_quad_F'])<3e-8

def test_no_false_claims_and_reference_evidence(evidence):
    assert evidence['new_upper_nodes']==0 and not evidence['production_ready']
    assert not evidence['merge_ready'] and not evidence['auto_next']
    assert 'NO_CHEMICAL_FEEDBACK' in evidence['scope']
    assert 'binding energy returned to Einstein stress' in evidence['not_implemented']
    assert evidence['distinct_author_R6_C9']=='NOT_RUN'
