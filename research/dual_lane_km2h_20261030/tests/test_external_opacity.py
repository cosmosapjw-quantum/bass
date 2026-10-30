"""Hostile physics validations of source-locked conditional HYREC FLRW opacity in Bianchi-I.

All tests use original KM2A/C/F/G sources as pinned; external xe cannot be
mistaken for an anisotropic recombination solution or realistic baryon abundance.
"""
from __future__ import annotations
import os,json,hashlib
from pathlib import Path
import numpy as np
import pytest
from research.dual_lane_km2h_20261030 import external_opacity_bianchi as m

@pytest.fixture(scope='module')
def r(tmp_path_factory):
    p=os.environ.get('BASS_KM2H_EXTERNAL_RESULTS')
    if p: return json.loads(Path(p).read_text())
    return m.run_science(tmp_path_factory.mktemp('science')/'new.json')


def test_original_sources_and_flrw_user_zip_provenance(r):
    src=m.exact_source_guards()
    assert src['research/dual_lane_km2g_20261030/neutral_baryons.py']==m.PARENT_KM2G_BLOB
    assert src['research/dual_lane_km2h_20261030/source_data/flrw_recombination_regression_1to1600.csv']==m.FLRW_SHA
    assert r['parent_head']==m.PARENT_GIT_HEAD


def test_fail_closed_on_source_tamper(monkeypatch):
    monkeypatch.setattr(m,'FLRW_SHA','0'*64)
    with pytest.raises(ValueError,match='FLRW_NATIVE_SOURCE_TABLE_SHA_CHANGED'):
        m.SourceLockedFLRW()


def test_recombination_helium_scope_and_source_domain():
    flrw=m.SourceLockedFLRW()
    for z in (900,1100,1200):
        assert 0<flrw.xe(z,'hyrec')<1
        assert abs(flrw.xe(z,'class')-flrw.xe(z,'hyrec'))<3e-5
    assert flrw.xe(1000,'frozen_hyrec')==flrw.xe(1200,'hyrec')
    for z in (899,1200.000001):
        with pytest.raises(ValueError,match='SUPPORT_900_TO_1200'):
            flrw.xe(z,'hyrec')
    with pytest.raises(ValueError,match='Unknown'):
        flrw.xe(1100,'fictitious')


def test_class_conformal_vs_SI_Thomson_opacity():
    x=np.genfromtxt(m.TABLE,delimiter=',',names=True)
    for zz in (900,1000,1100,1200):
        row=x[zz-1]
        pred=row['n_e_hyrec_per_m3']*m.SIGMA_T_M2*m.MPC_M/(1+zz)
        assert abs(pred/row['kappa_prime_hyrec_Mpc_inverse']-1)<2e-8
        pred_s=row['n_e_hyrec_per_m3']*m.SIGMA_T_M2*m.C_M_S
        assert abs(pred_s/row['Gamma_T_hyrec_per_s']-1)<2e-12


def test_actual_six_full_polarized_einstein_runs(r):
    assert len(r['cases'])==6
    assert set(r['cases'])=={f'GL{n}_{mode}' for n in (12,16) for mode in m.OPACITY_MODES}
    for v in r['cases'].values():
        assert len(v['epochs'])==5 and len(v['dense_physical_curve_41epochs'])==41
        assert v['H0_CLASS_matched'] and v['n_fev']>0
        assert len(v['optical_depth_ray_list'])==v['n_theta']*2*v['n_theta']
        assert v['ray_optical_depth_min']>0 and v['ray_optical_depth_max']>v['ray_optical_depth_min']


def test_parent_exact_original_photon_initial_identity(r):
    originals={
     12:('e4693c77d24014000afe9a858bfbe39192d43fdb92fb783699cbec6669399037','7adfcf87c8eeaf775c07dde8f34a5791b1f972b9fe94a0efd3524f76ab39107f'),
     16:('e15a0fb2e7ed215e3ef8f6bf7eb71ed7b44f754f3f96a8f055419d5df58b08b4','8c06fdb0d2222c2f92bbc0832b44683d224d6cc6450f8ea6ea360392c5fb36df')}
    for c in r['cases'].values():
        j,ray=originals[c['n_theta']]
        assert c['parent_original_photon_J_hash']==j
        assert c['parent_original_photon_rays_hash']==ray


def test_einstein_momentum_hamiltonian_and_integral_constraint_propagation(r):
    for name,v in r['cases'].items():
        assert v['max_Hamiltonian_norm']<5e-8
        assert v['max_momentum_norm']<5e-8
        b=v['balances']
        assert b['time_GL_nodes']==24
        assert b['Hamiltonian_source_balance_abs']<5e-8
        assert b['momentum_constraint_balance_max_abs']<5e-8
        assert b['sourced_shear_integral_error']<5e-8
        assert len(b['force_gap_time_rows'])==24
        for t in v['epochs']:
            assert abs(t['electron_number_vs_tetrad_detA_error'])<2e-9
            assert t['screen_normal_orthogonality']<2e-9
            assert t['screen_unit_gram_residual']<2e-9
            assert t['photon_screen_transversality']<2e-9


def test_angular_refinement_really_reduces_finite_source_constraint(r):
    for mode in m.OPACITY_MODES:
        a=r['cases'][f'GL12_{mode}'];b=r['cases'][f'GL16_{mode}']
        assert b['max_Hamiltonian_norm']<a['max_Hamiltonian_norm']/100
        assert b['max_momentum_norm']<a['max_momentum_norm']/100
        assert abs(a['ray_optical_depth_mean']-b['ray_optical_depth_mean'])<2e-4
        assert abs(a['shear_source_norm']-b['shear_source_norm'])<3e-9


def test_charge_number_and_species_mass_fraction_without_hardcode(r):
    for c in r['cases'].values():
        for row in c['epochs']:
            assert abs(row['charge_C_m3'])==0
            assert np.max(np.abs(row['charged_e_p_current_A_m2']))==0
            assert row['np_free_rest_m3']==row['ne_free_rest_m3']
            assert row['mass_fraction_sum']==pytest.approx(1,abs=3e-15)
            assert sum(row['species_energy'].values())==pytest.approx(row['total_baryon_density'],abs=2e-12)
            assert np.max(abs(np.sum([np.asarray(x) for x in row['species_momentum'].values()],axis=0)-np.asarray(row['q_electron'])))<1e-12
            assert row['nH_rest_m3']>row['ne_free_rest_m3']>0


def test_proper_SI_Thomson_rate_equals_original_polarized_source(r):
    for c in r['cases'].values():
        for row in c['epochs']:
            assert abs(row['nu_rest_from_SI']/row['nu_rest_tstar']-1)<3e-12
            direct=row['ne_free_rest_m3']*m.SIGMA_T_M2*m.C_M_S*(c['Tstar_years']*m.JULIAN_YEAR_S)
            assert abs(direct/row['nu_rest_tstar']-1)<3e-12


def test_density_mismatch_is_falsifiable_not_class_universe(r):
    for c in r['cases'].values():
        assert 5.7<c['ratio_nH_BASS_to_CLASS_initial']<5.8
        assert abs(c['epochs'][0]['H_BASS_over_H_FLRW_zvol']-1)<1e-13
        assert abs(c['epochs'][-1]['H_BASS_over_H_FLRW_zvol']-1)>1e-3


def test_hyrec_ionization_decays_and_frozen_mode_is_genuine(r):
    g=r['cases']['GL16_hyrec'];f=r['cases']['GL16_frozen_hyrec']
    assert g['epochs'][-1]['xe_external_per_hydrogen']<g['epochs'][0]['xe_external_per_hydrogen']-.15
    assert all(abs(t['x_e']-f['flrw_xe_ref'])<1e-13 for t in f['dense_physical_curve_41epochs'])
    assert all(a['x_e']>=b['x_e'] for a,b in zip(g['dense_physical_curve_41epochs'][:-1],g['dense_physical_curve_41epochs'][1:]))
    assert g['epochs'][-1]['z_volume_proxy']<g['epochs'][0]['z_volume_proxy']


def test_time_varying_ionization_changes_actual_photon_anisotropy_and_shear(r):
    a=r['physical_differences_gl16']
    assert -6.0<a['HYREC_vs_frozen_tau_mean']<-5.
    assert a['HYREC_vs_frozen_shear_source_norm']>3e-5
    assert a['HYREC_vs_frozen_photon_pi_max_abs']>.02
    assert abs(a['HYREC_vs_CLASS_tau_mean'])<.001


def test_full_photon_p8_collision_is_original_kernel_with_variable_scalar_rate():
    from curved_tilt import linear_collision
    a=m.ExternalFLRWOpacityBianchi(ntheta=8,opacity_mode='hyrec')
    b=m.ExternalFLRWOpacityBianchi(ntheta=8,opacity_mode='frozen_hyrec')
    ya=a.initial();d=a.fields(0.,ya,True)
    assert np.max(abs(d['coll']-linear_collision(d['op'],d['J'],d['nu'])))==0
    z=b.fields(0.,b.initial(),True)
    assert abs(d['nu']-z['nu'])<1e-13
    assert np.max(abs(d['coll']-z['coll']))<1e-12
    assert np.max(abs(d['streaming']-z['streaming']))<1e-12
    assert np.max(abs(a.p0-b.p0))==0


def test_cold_species_with_ionization_are_not_falsely_separately_conserved(r):
    a=r['cases']['GL16_hyrec']
    x=a['epochs'][0]['charged_mass_fractions_and_neutral_mass_fractions']
    y=a['epochs'][-1]['charged_mass_fractions_and_neutral_mass_fractions']
    assert y['free_p']<x['free_p'] and y['H_neutral']>x['H_neutral']
    assert np.isclose(x['H_neutral']+x['He_neutral']+x['free_e']+x['free_p'],1.)
    assert 'no reaction-energy' in r['scope'] or 'no reaction-energy' in r['conditional_chemistry']


def test_t_star_and_external_z_support_reject_unphysical_change():
    a=m.ExternalFLRWOpacityBianchi(ntheta=8)
    assert a.matched_tstar_years>0
    assert abs(a.nu0-a.nH_rest0*a.xe_ref*m.SIGMA_T_M2*m.C_M_S*a.Tstar_seconds)<1e-12
    with pytest.raises(ValueError,match='SUPPORT_900_TO_1200'):
        a.external.xe(850,'hyrec')
    with pytest.raises(ValueError,match='Unsupported'):
        m.ExternalFLRWOpacityBianchi(ntheta=8,opacity_mode='invented')


def test_exact_vacuum_collision_limit_no_false_thomson():
    from numpy import zeros_like
    a=m.ExternalFLRWOpacityBianchi(ntheta=8)
    a.nu0=0.
    d=a.fields(0.,a.initial(),True)
    assert d['nu']==0.
    assert np.max(abs(d['coll']))==0
    assert np.max(abs(d['cf']))==0


def test_claim_boundaries_and_DAG(r):
    assert r['upper_dag']=='9/15' and r['km2']=='PARTIAL'
    assert r['new_upper_completed']==0
    assert r['full_Einstein_Boltzmann_recombination']=='NOT_RUN'
    assert r['angular_continuum_certificate']=='NOT_RUN'
    assert r['observer_CMB_prediction']=='NOT_CLAIMED'
    assert not r['production_ready'] and not r['merge_ready'] and not r['auto_next']
