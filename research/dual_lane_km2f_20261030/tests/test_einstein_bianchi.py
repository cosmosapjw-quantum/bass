"""KM2F source-locked Einstein constraint and physical GR photon-dust controls."""
from __future__ import annotations
import json, os
from pathlib import Path
import numpy as np
import pytest
from research.dual_lane_km2f_20261030 import einstein_bianchi as z


@pytest.fixture(scope='module')
def science(tmp_path_factory):
    loc=os.environ.get('BASS_KM2F_RESULT')
    if loc:
        return json.loads(Path(loc).read_text())
    return z.run(tmp_path_factory.mktemp('km2f')/'physical.json',orders=(12,16))


def test_original_parent_immutable_sources():
    k=z.full_source_guard()
    assert k['research/dual_lane_km2e_20261030/coupled_electron_photon.py']==z.EXPECTED_GIT[z.KM2E/'coupled_electron_photon.py']
    assert k['research/dual_lane_km2c_20261028/vendor/tilted_collision.py']==z.EXPECTED_GIT[z.KM2C/'vendor/tilted_collision.py']


def test_BianchiI_momentum_and_Hamiltonian_constraints_at_initial_data():
    m=z.EinsteinCoupledBianchi(ntheta=12)
    a=m.measure(0.,m.initial())
    assert a['momentum_constraint_normalized']<1e-13
    assert a['hamiltonian_normalized']<1e-13
    assert np.linalg.norm(m.beta0)<1
    assert np.max(abs(m.Re0*m.beta0+m.q0))<2e-12
    assert abs(3*m.H0**2-m.kappa*(m.rho0+m.Re0)-m.sigma2_0)<1e-14
    assert abs(a['sigma2']-m.sigma2_0)<1e-14


def test_actual_Einstein_source_evolves_both_H_and_noncommuting_shear(science):
    assert science['upper_dag']=='9/15' and science['km2']=='PARTIAL'
    assert science['new_upper_nodes']==0
    for n in ('12','16'):
        r=science['cases'][n]; epochs=r['physics_epochs']; start=epochs[0]; final=epochs[-1]
        assert len(epochs)==5
        assert 0<final['H']<start['H']
        assert final['rho_total']<start['rho_total']
        assert abs(final['sigma2']-start['sigma2'])>1e-3
        assert final['noncommuting_shear_commutator_norm']>1e-4
        assert r['integrated_balances']['sourced_shear_difference_from_unsourced_dilution']>1e-3
        assert r['integrated_balances']['sourced_shear_integral_error']<1e-8
        assert r['max_abs_normalized_hamiltonian']<1e-8
        assert r['max_abs_normalized_momentum']<1e-8


def test_conservation_constraint_propagation_with_measured_raw_P8_gap(science):
    for n in ('12','16'):
        w=science['cases'][n]['integrated_balances']
        assert w['time_GL_nodes']==24
        assert w['Hamiltonian_source_balance_abs']<1e-8
        assert w['momentum_constraint_balance_max_abs']<1e-8
        assert w['max_normalized_source_force_gap']>=0
        assert len(w['force_gap_time_rows'])==24
        assert np.max(abs(np.asarray(w['sourced_shear_integral'])-
                             np.asarray(w['sourced_shear_observed'])))<1e-8
        for row in science['cases'][n]['physics_epochs']:
            assert abs(row['Ricci_trace_constraint']-4*row['hamiltonian_constraint'])<2e-12
            assert abs(row['electron_number_vs_tetrad_detA_error'])<1e-8
            assert row['screen_unit_gram_residual']<1e-8
            assert row['screen_normal_orthogonality']<1e-8
            assert row['photon_screen_transversality']<1e-8


def test_angular_refinement_reduces_constraint_residual(science):
    a=science['cases']['12'];b=science['cases']['16']
    assert b['max_abs_normalized_hamiltonian']<a['max_abs_normalized_hamiltonian']/100
    assert b['max_abs_normalized_momentum']<a['max_abs_normalized_momentum']/100
    assert abs(a['physics_epochs'][-1]['H']-b['physics_epochs'][-1]['H'])<1e-7
    assert abs(a['physics_epochs'][-1]['rho_total']-b['physics_epochs'][-1]['rho_total'])<1e-5
    assert np.max(abs(np.asarray(a['physics_epochs'][-1]['beta_electron'])-
                      np.asarray(b['physics_epochs'][-1]['beta_electron'])))<1e-7


def test_fully_independent_Einstein_beta_versus_p_photon_integrators(science):
    c=science['full_independent_beta_vs_p_dynamical_comparison']
    assert len(c)==3
    for r in c.values():
        assert r['max_electron_beta_abs']<2e-10
        assert r['Einstein_H_abs']<2e-10
        assert r['max_shear_abs']<2e-10
        assert r['full_photon_J_abs']<2e-10
        assert r['total_density_abs']<2e-10


def test_physical_Minkowski_Thomson_control_conserves_total_energy_and_momentum(science):
    c=science['Minkowski_no_Einstein_feedback_control']
    assert abs(c['normal_total_E_change'])<2e-8
    assert c['total_Q_max_change']<2e-8
    assert c['H_final']==0
    assert c['sigma2_final']==0
    assert c['trace_curvature_final']==0


def test_matter_mass_shell_number_and_spatial_metric_positive(science):
    for n in ('12','16'):
        for q in science['cases'][n]['physics_epochs']:
            assert q['gamma_electron']>=1
            assert np.linalg.norm(q['beta_electron'])<1
            assert q['electron_zeta']>0 and q['nu_rest_tstar']>0
            assert q['rho_electron']>0 and q['rho_photon']>0
            assert q['detA']>0
            g=np.asarray(q['metric_spatial_covariant']);ev=np.linalg.eigvalsh(g)
            assert np.min(ev)>0
            assert abs(np.sqrt(np.linalg.det(g))-q['metric_volume'])<1e-10
            assert abs(np.trace(np.asarray(q['sigma'])))<2e-14


def test_fail_closed_if_photon_source_original_byte_mutated(monkeypatch):
    key=z.KM2C/'vendor/tilted_collision.py'
    monkeypatch.setitem(z.EXPECTED_GIT,key,'0'*40)
    with pytest.raises(ValueError,match='IMMUTABLE_ORIGINAL_PHYSICS_BLOB_MISMATCH'):
        z.full_source_guard()


def test_infeasible_cold_matter_ratio_and_wrong_H_not_silently_fixed():
    with pytest.raises(ValueError,match='NO_FEASIBLE_SINGLE_COLD_ELECTRON_MOMENTUM_CONSTRAINT'):
        z.EinsteinCoupledBianchi(ntheta=8,inertia_ratio=.2)
    m=z.EinsteinCoupledBianchi(ntheta=8)
    y=m.initial(); y[m.idx_H]*=1.01
    a=m.measure(0.,y)
    assert a['hamiltonian_normalized']>1e-3


def test_zero_metric_tensor_sources_no_fake_nonzero_geometry():
    m=z.EinsteinCoupledBianchi(ntheta=8,kappa=0,sigma_initial_scale=0.)
    y=m.initial();d=m.rhs(0.,y)
    assert m.H0==0
    assert np.max(abs(d[m.slice_A]))==0
    assert d[m.idx_H]==0
    assert np.max(abs(d[m.slice_sigma]))==0


def test_claim_scope_and_upper_DAG_protected(science):
    assert science['angular_continuum_certificate']=='NOT_RUN'
    assert science['Einstein_full_formal_program_verification']=='NOT_RUN'
    assert not science['production_ready'] and not science['merge_ready'] and not science['auto_next']
    assert science['original_photon_seed_beta']==[.3,-.4,.2]
    assert science['electron_inertia_ratio']==3.
    assert science['Einstein_coupling_kappa']==.003
