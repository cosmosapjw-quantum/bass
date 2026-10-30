"""C9 hostile checks for physical KM2G charge-neutral e+p Coulomb lock model."""
from __future__ import annotations
import hashlib,json,os
from pathlib import Path
import numpy as np
import pytest
from research.dual_lane_km2g_20261030 import neutral_baryons as m


@pytest.fixture(scope='module')
def science(tmp_path_factory):
    if os.environ.get('BASS_KM2G_RESULT'):
        return json.loads(Path(os.environ['BASS_KM2G_RESULT']).read_text())
    return m.physics_run(tmp_path_factory.mktemp('km2g')/'science.json',orders=(12,16),
                         time_scales=(10_000_000.,57_883_065.06488644))


def test_parent_and_original_photon_source_binary_sha_exact(science):
    live=m.verify_unchanged_physics()
    assert science['source_base_pr278']==m.SRC_PARENT
    assert live[str(m.PARENT.relative_to(m.ROOT))]==m.KM2F_BLOB
    assert science['original_source_git_blobs']==live


def test_codata_2022_mass_and_thomson_input_unit_dimensionalization(science):
    assert abs(m.M_P_KG/m.M_E_KG-1836.152673426)<2e-7
    x=m.NeutralHydrogenEinstein(ntheta=12,Tstar_years=10e6)
    T=x.Tstar_seconds
    assert abs(x.energy_unit_J_m3 - x.kappa*m.C_M_S**2/(8*np.pi*m.G_SI*T*T))<1e-15
    assert np.isclose(x.n_rest_initial_m3, x.Re0*x.energy_unit_J_m3/(x.mass_baryon*m.C_M_S**2*x.gamma0**2),rtol=1e-14)
    assert np.isclose(x.nu0,x.n_rest_initial_m3*m.SIGMA_T_M2*m.C_M_S*T,rtol=1e-14)
    assert np.isclose(x.nu0,7.52479845843524,rtol=2e-11)
    assert x.electron_fraction<0.001 and x.proton_fraction>0.999


def test_charge_neutrality_and_separate_species_stress_algebra(science):
    for run in science['cases'].values():
        for q in run['physics_epochs']:
            assert q['charge_density_C_m3']==0
            assert np.max(abs(np.asarray(q['electric_current_Am2'])))==0
            assert q['proper_n_electron_m3']==q['proper_n_proton_m3']>0
            assert abs(q['rho_electron_species']+q['rho_proton_species']-q['rho_electron'])<2e-12
            assert np.max(abs(np.asarray(q['q_electron_species'])+np.asarray(q['q_proton_species'])-np.asarray(q['q_electron'])))<2e-12
            assert np.max(abs(np.asarray(q['P_electron_species'])+np.asarray(q['P_proton_species'])-np.asarray(q['P_electron'])))<2e-12
            assert abs(q['electron_share_of_recoil']+q['proton_share_of_recoil']-1)<1e-15


def test_internal_coulomb_drag_exactly_redistributes_photon_force(science):
    for case in science['cases'].values():
        for q in case['physics_epochs']:
            fg=np.asarray(q['photon_covariant_force'])
            ce=np.asarray(q['Coulomb_force_on_electron'])
            cp=np.asarray(q['Coulomb_force_on_proton'])
            ne=np.asarray(q['net_force_on_electron'])
            np_=np.asarray(q['net_force_on_proton'])
            eg=np.asarray(q['photon_force_on_electron'])
            assert np.max(abs(ce+cp))<1e-15
            assert np.max(abs(eg+fg))<1e-15
            # Binary64 non-associative summation: bound by the input force's own ULP,
            # not an arbitrary absolute 1e-13 threshold on O(10^3) terms.
            tol=8*np.finfo(float).eps*max(1.,np.max(abs(fg)))
            assert np.max(abs(ne+np_+fg))<tol
            assert np.max(abs(ne+q['electron_share_of_recoil']*fg))<tol
            assert np.max(abs(np_+q['proton_share_of_recoil']*fg))<tol
            beta=np.asarray(q['beta_electron'])
            # Orthogonality is inherited from covariant force computed as
            # cancellation of O(nu*rho_gamma) stress-energy terms, not from
            # the (possibly much smaller) final F components. Test against
            # that actual input operation scale rather than F-only ULPs.
            force_scale=max(1.,q['nu_rest_tstar']*q['rho_photon'],np.max(abs(fg)))
            orthog_roundoff=64*np.finfo(float).eps*force_scale
            assert abs(ne[0]-beta@ne[1:])<orthog_roundoff
            assert abs(np_[0]-beta@np_[1:])<orthog_roundoff


def test_live_dynamical_Einstein_constraints_survive_stronger_Thomson(science):
    assert science['upper_dag']=='9/15' and science['km2']=='PARTIAL'
    for k,case in science['cases'].items():
        assert case['max_normalized_Hamiltonian']<1e-7
        assert case['max_normalized_momentum']<1e-7
        assert case['constraint_integrals']['Hamiltonian_source_balance_abs']<2e-8
        assert case['constraint_integrals']['momentum_constraint_balance_max_abs']<2e-8
        assert case['final_sourced_shear_norm']>1e-4
        assert case['optical_depth_min']>0
        assert case['optical_depth_min']<=case['optical_depth_max']
        for q in case['physics_epochs']:
            assert abs(q['electron_number_vs_tetrad_detA_error'])<1e-9
            assert q['nu_rest_tstar']>0
            assert np.linalg.norm(q['beta_electron'])<1
            assert q['photon_screen_transversality']<2e-8
            assert q['screen_unit_gram_residual']<1e-8
            assert q['rho_total']>0


def test_original_KM2F_reference_recovered_at_matched_dimensional_opacity(science):
    for n in (12,16):
        key=f'GL{n}_TstarYears57883065'
        if key not in science['cases']:continue
        x=science['cases'][key]
        assert abs(x['nu0_physical_derived']-1.3)<1e-12
        ref=0.3472821545020744 if n==12 else 0.3472821545497598
        assert abs(x['actual_H_end']-ref)<3e-11


def test_derived_opacity_changes_real_photon_and_Einstein_physics(science):
    a=science['cases']['GL16_TstarYears10000000']
    b=science['cases']['GL16_TstarYears57883065']
    assert a['nu0_physical_derived']>b['nu0_physical_derived']*5
    assert a['optical_depth_min']>b['optical_depth_max']*4
    assert abs(a['actual_rho_gamma_end']-b['actual_rho_gamma_end'])>.01
    assert abs(a['actual_H_end']-b['actual_H_end'])>5e-5
    assert abs(a['final_sourced_shear_norm']-b['final_sourced_shear_norm'])>1e-5


def test_angular_grid_refinement_reduces_measured_not_certified_constraint_error(science):
    for time in (10000000,57883065):
        a=science['cases'][f'GL12_TstarYears{time}'];b=science['cases'][f'GL16_TstarYears{time}']
        assert b['max_normalized_Hamiltonian']<a['max_normalized_Hamiltonian']/100
        assert b['max_normalized_momentum']<a['max_normalized_momentum']/100
        assert abs(a['actual_H_end']-b['actual_H_end'])<1e-7
        assert abs(a['actual_rho_gamma_end']-b['actual_rho_gamma_end'])<1e-5


def test_wrong_electron_only_inertia_recoil_rejected_by_physical_mass_ratio():
    x=m.NeutralHydrogenEinstein(ntheta=12,Tstar_years=10e6)
    y=x.initial();z=x.fields(0.,y)
    F=np.array(z['cf'][1:]);M_b=x.M0
    correct=-F/M_b
    wrong=-F/(M_b*x.electron_fraction)
    assert np.linalg.norm(F)>1e-4
    assert np.isclose(np.linalg.norm(wrong)/np.linalg.norm(correct),1/x.electron_fraction,rtol=1e-13)
    assert 1800<1/x.electron_fraction<1900


def test_zero_thomson_control_does_not_change_number_neutrality_or_source():
    x=m.NeutralHydrogenEinstein(ntheta=8,Tstar_years=10e6,scattering_switch=0.0,end=.08)
    sol=x.solve();q=x.measure_species(.08,sol.sol(.08))
    assert x.nu0==0
    assert q['nu_rest_tstar']==0
    assert np.max(abs(np.asarray(q['photon_covariant_force'])))==0
    assert np.max(abs(np.asarray(q['Coulomb_force_on_electron'])))==0
    assert np.max(abs(np.asarray(q['electric_current_Am2'])))==0
    assert q['rho_electron_species']>0 and q['rho_proton_species']>0
    assert np.max(abs(x.optical_depth(sol)))==0


def test_invalid_physical_inputs_fail_closed():
    for bad in ({'Tstar_years':0},{'Tstar_years':float('nan')},
                {'inertia_ratio':.01},{'scattering_switch':-1},
                {'scattering_switch':1.2},{'kappa':0}):
        with pytest.raises(ValueError):m.NeutralHydrogenEinstein(ntheta=8,**bad)


def test_parent_source_tamper_rejected(monkeypatch):
    monkeypatch.setattr(m,'KM2F_BLOB','0'*40)
    with pytest.raises(ValueError,match='FROZEN_KM2F_PHOTON_EINSTEIN_BLOB_MISMATCH'):
        m.verify_unchanged_physics()


def test_no_observational_or_full_plasma_claims(science):
    assert science['photon_blackbody_and_ionization_history']=='NOT_AVAILABLE_NOT_CLAIMED'
    assert science['finite_Coulomb_rate_Maxwell']=='NOT_RUN'
    assert science['Einstein_full_formal_verification']=='NOT_RUN'
    assert science['distinct_author_R6_C9']=='NOT_RUN'
    assert science['new_upper_completed']==0
    assert not science['production_ready'] and not science['merge_ready'] and not science['auto_next']


def test_direct_species_conservation_against_full_photon_einstein_rhs():
    # Independently differentiate R_s=M_s zeta gamma and Q_s=M_s zeta p,
    # without using the species-source convenience expressions as a definition.
    x=m.NeutralHydrogenEinstein(ntheta=12,Tstar_years=10e6,end=.12)
    sol=x.solve()
    for t in (0.,.06,.12):
        state=sol.sol(t)
        ydot=x.rhs(t,state)
        A,E,J,p,zeta,H,sigma,gamma,beta=x.decode(state)
        pdot=ydot[x.slice_p]
        zeta_dot=ydot[x.idx_zeta]
        q=x.measure_species(t,state)
        Rb=x.M0*zeta*gamma
        Rb_dot=x.M0*(zeta_dot*gamma+zeta*(p@pdot)/gamma)
        Qb_dot=x.M0*(zeta_dot*p+zeta*pdot)
        for label,fraction in [('electron',x.electron_fraction),('proton',x.proton_fraction)]:
            analytic_energy=fraction*Rb_dot
            analytic_momentum=fraction*Qb_dot
            source_energy=q[f'{label}_energy_source']
            source_momentum=np.asarray(q[f'{label}_momentum_source'])
            assert abs(analytic_energy-source_energy)<2e-12
            assert np.max(abs(analytic_momentum-source_momentum))<2e-12
        assert abs(q['electron_energy_source']+q['proton_energy_source']-Rb_dot)<2e-12


def test_original_photon_initial_source_exact_byte_identity_across_opacity():
    from research.dual_lane_km2f_20261030.einstein_bianchi import EinsteinCoupledBianchi
    for n in (12,16):
        reference=EinsteinCoupledBianchi(ntheta=n,end=.25,nu0=1.3)
        physical=m.NeutralHydrogenEinstein(ntheta=n,end=.25,Tstar_years=3e6)
        for name in ('j0','n0','w0','screen0'):
            assert getattr(reference,name).dtype==getattr(physical,name).dtype
            assert getattr(reference,name).tobytes()==getattr(physical,name).tobytes()
        assert reference.H0==physical.H0
        assert reference.ratio==physical.ratio
        assert np.array_equal(reference.sigma0,physical.sigma0)
