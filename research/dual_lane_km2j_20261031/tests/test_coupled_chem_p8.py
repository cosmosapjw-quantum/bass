"""KM2J source-bound regression and scientific tests, normal + python -O."""
import hashlib
import json
import os
from pathlib import Path
import numpy as np
import pytest
from research.dual_lane_km2j_20261031 import coupled_chem_p8 as m
from research.dual_lane_km2h_20261030.external_opacity_bianchi import ExternalFLRWOpacityBianchi
from tilted_collision import radiation_tensor

HERE=Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def science(tmp_path_factory):
    pathname=os.environ.get("KM2J_SCIENCE_JSON")
    if pathname and Path(pathname).exists():
        return json.loads(Path(pathname).read_text())
    return m.run_science(tmp_path_factory.mktemp("km2j")/"science.json")


def test_all_original_physics_sha_source_guarded():
    src=m.guard_all()
    assert src["research/dual_lane_km2i_20261031/lya_peebles.py"]==m.PARENT_LYA_BLOB
    assert src["research/dual_lane_km2f_20261030/einstein_bianchi.py"]==m.PARENT_F_BLOB


def test_parent_tamper_fails_closed(monkeypatch):
    monkeypatch.setattr(m,"PARENT_LYA_BLOB","0"*40)
    with pytest.raises(ValueError,match="IMMUTABLE_PARENT_GIT_BLOB_CHANGED"):
        m.guard_all()


def test_angular_emission_four_moments_and_unpolarized_projection():
    n=np.vstack([np.eye(3),-np.eye(3)])
    w=np.full(6,4*np.pi/6)
    beta=np.array([.13,-.09,.17])
    J,F,gap,low,high=m.angular_grey_emission(n,w,beta,2.3e-5)
    assert J.shape==(6,3,3)
    assert np.max(np.abs(radiation_tensor(n,w,J)[0,:]-F))<1e-18
    assert gap<1e-12 and low>0 and high>0
    assert np.max(np.abs(np.einsum("nij,nj->ni",J,n)))<1e-20
    assert np.max(np.abs(J-J.transpose(0,2,1)))<1e-20
    assert abs(F[0]-2.3e-5/np.sqrt(1-beta@beta))<1e-18


def test_angular_zero_boost_no_polarization_false_claim():
    n=np.vstack([np.eye(3),-np.eye(3)])
    w=np.full(6,4*np.pi/6)
    J,F,gap,low,high=m.angular_grey_emission(n,w,np.zeros(3),1e-7)
    assert np.max(np.abs(F[1:]))<1e-20
    assert abs(F[0]-1e-7)<1e-20
    assert gap<1e-12 and low>0
    with pytest.raises(ValueError):
        m.angular_grey_emission(n,w,np.array([1.1,0,0]),1e-7)


def test_live_state_has_one_extra_x_and_original_initial_seed():
    obj=m.CoupledChemicalP8(ntheta=12)
    native=obj.parent
    init=obj.initial()
    assert init.shape==(native.total_size+1,)
    assert init[-1]==obj.x0
    assert np.array_equal(init[native.slice_J],native.initial()[native.slice_J])
    assert obj.initial_j_sha==hashlib.sha256(native.j0.tobytes()).hexdigest()
    assert 0<obj.eta<3e-8


def test_proper_time_reaction_and_opacity_exact_SI_at_initial():
    obj=m.CoupledChemicalP8(ntheta=12)
    d=obj.fields(0,obj.initial(),True)
    x=obj.x0
    direct=d["nH"]*x*m.SIGMA_T_M2*m.C_M_S*obj.parent.Tstar_seconds
    assert abs(d["nu"]/direct-1)<1e-13
    xproper=obj.parent.Tstar_seconds*d["C_factor"]*(
        d["betaB"]*(1-x)*np.exp(-m.E_ALPHA_EV*m.E_CHARGE/(m.K_B*d["Tgamma"]))
        -d["alphaB"]*d["nH"]*x*x)
    assert abs(obj.parent.gamma0*d["xprime"]-xproper)<1e-9
    assert d["chem_force"][0]>0
    assert d["M"]==obj.parent.M0
    assert d["xprime"]<0


def test_internal_binding_energy_four_force_not_double_counted():
    obj=m.CoupledChemicalP8(ntheta=12)
    d=obj.fields(0,obj.initial(),True)
    expected=-obj.parent.M0*obj.eta*d["zeta"]*d["xprime"]
    assert abs(d["chem_rest_source"]-expected)/abs(expected)<1e-13
    expected4=expected*np.r_[d["gamma"],d["p"]]
    assert np.max(abs(d["chem_force"]-expected4))<1e-18
    assert d["chem_discrete_gap"]<2e-12
    opaque=m.CoupledChemicalP8(ntheta=12,chem_energy=False)
    control=opaque.fields(0,opaque.initial(),True)
    assert np.all(control["chem_force"]==0)
    assert control["M"]==opaque.parent.M0


def test_two_original_grids_new_joint_ivps_not_saved_external_trajectory(science):
    assert science["parent_head"]==m.PARENT_HEAD
    assert set(science["cases"])=={"GL12","GL16"}
    for label,c in science["cases"].items():
        assert c["parent_original_Einstein_IVP_nfev"]>10
        assert c["N_original_P8_rays"]==2*c["n_theta"]**2
        assert c["parent_initial_J_sha256"]==c["cases"]["full"]["initial_j_sha256"]
        for mode,z in c["cases"].items():
            assert z["rhs_evals"]>10
            assert len(z["epochs"])==41
            assert len(z["source_snapshots"])==3
            assert z["depth"]["tau_ray_min"]>0
            assert len(z["depth"]["tau_rays"])==c["N_original_P8_rays"]


def test_physical_chemical_thomson_feedback_is_nontrivial(science):
    for c in science["cases"].values():
        new=c["comparison"]
        assert 0<new["chem_xe_end"]<.11
        assert new["chem_xe_end"]<new["old_hyrec_xe_end"]-.04
        assert new["full_tau_minus_parent_mean"]<-.5
        assert new["full_minus_parent_shear_matrix_frob"]>1e-8
        assert 3<new["hydrogen_binding_release_eV_per_H"]<5


def test_binding_energy_is_small_but_real_photon_coupling(science):
    for c in science["cases"].values():
        full=c["cases"]["full"];ctrl=c["cases"]["opacity_only"]
        assert abs(c["comparison"]["full_minus_opacity_only_photon_rho"])>1e-12
        assert full["epochs"][-1]["chemical_mass_ratio"]<1
        assert ctrl["epochs"][-1]["chemical_mass_ratio"]==1
        assert full["epochs"][-1]["chemical_rest_emission_per_u"]>0
        assert ctrl["epochs"][-1]["chemical_rest_emission_per_u"]==0
        assert full["depth"]["moment_weight_correction_min"]>0
        assert full["depth"]["moment_weight_correction_max"]>0


def test_scoped_constraints_and_fourforce_source_balance(science):
    for c in science["cases"].values():
        for z in c["cases"].values():
            con=z["conservation"]
            assert con["max_Hamiltonian_norm"]<5e-8
            assert con["max_momentum_norm"]<5e-8
            assert con["hamiltonian_propagation_error"]<5e-8
            assert con["momentum_integrated_error"]<5e-8
            assert con["max_chemical_fourforce_discrete_relative"]<2e-12
            assert all(0<row["x_e"]<1 for row in z["epochs"])
            assert all(row["charge_C_m3"]==0 for row in z["epochs"])


def test_angular_GL12_GL16_scoped_physics(science):
    x12=science["cases"]["GL12"]["comparison"]["chem_xe_end"]
    x16=science["cases"]["GL16"]["comparison"]["chem_xe_end"]
    assert abs(x12-x16)<1e-5
    tau12=science["cases"]["GL12"]["cases"]["full"]["depth"]["tau_ray_mean"]
    tau16=science["cases"]["GL16"]["cases"]["full"]["depth"]["tau_ray_mean"]
    assert abs(tau12-tau16)<1e-2


def test_scope_and_dag_no_production_or_spectral_claim(science):
    assert science["upper_dag"]=="9/15" and science["KM2"]=="PARTIAL"
    assert science["new_upper_nodes"]==0
    assert not science["production_ready"] and not science["merge_ready"] and not science["auto_next"]
    assert "frequency resolved Lyalpha and ionizing radiation" in science["not_implemented"]
    assert science["distinct_author_R6_C9"]=="NOT_RUN"
