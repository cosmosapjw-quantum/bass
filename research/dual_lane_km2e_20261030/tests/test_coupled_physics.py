"""KM2E regression: source-locked matter-photon momentum backreaction."""
from __future__ import annotations
import json
import os
from pathlib import Path

import numpy as np
import pytest
from research.dual_lane_km2e_20261030 import coupled_electron_photon as m


@pytest.fixture(scope="module")
def science(tmp_path_factory):
    path=os.environ.get("KM2E_RESULT")
    if path:
        return json.loads(Path(path).read_text())
    return m.actual_science(tmp_path_factory.mktemp("km2e")/"physical.json",quick=True)


def test_original_km2c_d_original_bass_source_unchanged(science):
    a=m.source_guards()
    assert a[str((m.PREV/"accelerating_tilt.py").relative_to(m.ROOT))]==m.PARENT_KM2D_BLOB
    assert a[str((m.OLD/"code/curved_tilt.py").relative_to(m.ROOT))]==m.KM2C_BLOB
    assert a[str((m.OLD/"vendor/tilted_collision.py").relative_to(m.ROOT))]==m.KM2A_BLOB
    assert science["parent_head"]==m.PARENT_HEAD


def test_actual_full_photon_plus_matter_ivp_and_two_representations(science):
    assert science["upper_dag"]=="9/15" and science["km2"]=="PARTIAL"
    assert not science["production_ready"] and not science["merge_ready"]
    assert science["new_upper_completed"]==0
    for g in science["cases"].values():
        assert g["IVP_direct_photons_and_electron_p"]
        assert g["IVP_independent_electron_beta_representation"]
        err=g["p_vs_beta_same_physical_solutions"]
        assert err["max_J_abs"]<1e-8
        assert err["max_beta_abs"]<1e-8
        assert err["max_zeta_abs"]<1e-10
        assert len(g["physical_5epoch_records"])==5
        assert all(len(x["original_source_electron_M"])==3
                   for x in g["physical_5epoch_records"])


def test_backreaction_changes_actual_electron_velocity_and_mass_shell(science):
    for g in science["cases"].values():
        assert g["feedback_enabled_vs_nonconservative_control_beta_final_norm"]>1e-5
        for r in g["physical_5epoch_records"]:
            assert r["velocity_subluminal"]
            assert r["physical_mass_shell_residual"]<2e-12
            assert r["rest_density_ratio"]>0
            assert r["nu_rest_Tstar"]>0
            assert r["zeta_lab_number_ratio"]>0
            assert r["normal_screen_leak"]<2e-9


def test_actual_total_stress_energy_balance_includes_raw_angular_defect(science):
    for g in science["cases"].values():
        w=g["normal_time_work"]
        assert w["E_closure_abs"]<2e-8
        assert w["Q_closure_max_abs"]<2e-8
        assert w["max_covariant_force_orthogonality_residual"]<1e-10
        assert w["max_screen_leak"]<2e-9
        assert len(w["time_rows"])==24
        assert np.isfinite(w["E_raw_force_gap_integral"])
        assert len(w["Q_raw_force_gap_integral"])==3
        for r in g["physical_5epoch_records"]:
            ep=np.asarray(r["P_electron"])
            beta=np.asarray(r["beta"])
            rho=r["rho_electron_normal"]
            assert np.max(abs(ep-rho*np.outer(beta,beta)))<1e-11
            assert abs(r["nu_rest_Tstar"]-
                       1.3*r["zeta_lab_number_ratio"]*g["physical_5epoch_records"][0]["gamma"]/r["gamma"])<1e-12


def test_flat_limit_is_actual_total_energy_momentum_exchange(science):
    assert science["flat_spacetime_total_E_abs_delta"]<2e-8
    assert science["flat_spacetime_total_Q_max_abs_delta"]<2e-8


def test_zero_opacity_has_zero_photon_collisions(science):
    x=science["vacuum_final"]
    assert x["nu_rest_Tstar"]==0
    assert np.max(abs(np.asarray(x["photon_raw_P8_force"])))==0
    assert np.max(abs(np.asarray(x["covariant_photon_force"])))==0
    assert x["rest_density_ratio"]>0


def test_covariant_matter_specific_momentum_geodesic_and_recoil_form():
    x=m.CoupledColdElectronPhoton(n=6,end=.12,nu0=1.3)
    t=0.
    y=x.init("p")
    J,p,beta,gamma,zeta=x.parse(y,"p")
    d=x.at(t,J,beta,gamma,zeta)
    got=x.rhs(t,y,mode="p")
    pdot=got[x.J0.size:x.J0.size+3]
    expected=-d["B"]@p-d["covariant_force"][1:]/(x.M0*zeta)
    assert np.max(abs(pdot-expected))<1e-13
    assert abs(got[-1]+3*d["H"]*zeta)<1e-13
    assert abs(d["covariant_force"][0]-beta@d["covariant_force"][1:])<1e-11


def test_independent_beta_variable_is_exact_mass_shell_transform():
    x=m.CoupledColdElectronPhoton(n=6,end=.12)
    yp=x.init("p")
    yb=x.init("beta")
    dp=x.rhs(0.,yp,mode="p")[x.J0.size:x.J0.size+3]
    db=x.rhs(0.,yb,mode="beta")[x.J0.size:x.J0.size+3]
    p=x.p0;gamma=x.gamma0
    Jacob=(np.eye(3)-np.outer(x.beta0,x.beta0))/gamma
    assert np.max(abs(db-Jacob@dp))<3e-13


def test_matter_energy_and_momentum_balance_from_different_variables():
    x=m.CoupledColdElectronPhoton(n=6,end=.12)
    y=x.init("p"); J,p,beta,gamma,zeta=x.parse(y,"p")
    d=x.at(0.,J,beta,gamma,zeta)
    dr=x.rhs(0.,y,mode="p")
    pdot=dr[x.J0.size:x.J0.size+3]
    zdot=dr[-1]
    R=x.M0*zeta*gamma
    Rp=x.M0*(zdot*gamma+zeta*(p@pdot)/gamma)
    Qp=x.M0*(zdot*p+zeta*pdot)
    pressure=R*np.outer(beta,beta)
    source=d["covariant_force"]
    expectedE=-3*d["H"]*R-np.sum(d["B"]*pressure)-source[0]
    expectedQ=-(4*d["H"]*np.eye(3)+d["sigma"])@(x.M0*zeta*p)-source[1:]
    assert abs(Rp-expectedE)<4e-12
    assert np.max(abs(Qp-expectedQ))<4e-12


def test_source_mutation_rejected(monkeypatch):
    monkeypatch.setitem(m.SOURCE_BLOBS,m.OLD/"code/curved_tilt.py","0"*40)
    with pytest.raises(ValueError,match="Original photon and geometry source SHA changed"):
        m.source_guards()


def test_invalid_matter_inputs_and_stored_rates_fail_closed():
    for args in ({"inertia_ratio":0.},{"nu0":-1.},{"beta0":(1.,0.,0.)}):
        with pytest.raises(ValueError):
            m.CoupledColdElectronPhoton(n=6,end=.1,**args)
    x=m.CoupledColdElectronPhoton(n=6,end=.12)
    y=x.init("p"); y[-1]=0
    with pytest.raises(ValueError,match="not positive"):
        x.rhs(0.,y)


def test_no_new_unearned_physics_claims(science):
    assert science["Einstein_feedback"]=="NOT_RUN"
    assert science["electron_temperature_or_pressure"]=="NOT_RUN"
    assert science["spectral_domain"]=="NOT_CERTIFIED"
    assert science["distinct_author_R6_C9"]=="NOT_RUN"
    assert science["numerical_continuum_angular_certificate"]=="NOT_RUN"
