"""KM2K source-locked true frequency-resolved physical tests."""
import hashlib,math,os,json
from pathlib import Path
import numpy as np
import pytest
from research.dual_lane_km2k_20261031 import frequency_core as fc
from research.dual_lane_km2k_20261031 import escaping_lya as m


@pytest.fixture(scope="session")
def science(tmp_path_factory):
    p=os.environ.get("KM2K_SCIENCE_JSON")
    if p and Path(p).is_file():return json.loads(Path(p).read_text())
    return m.run_science(tmp_path_factory.mktemp("km2k")/"science.json")


def test_parent_git_blobs_and_source_owner():
    src=m.exact_parent_sources()
    key="research/dual_lane_km2j_20261031/coupled_chem_p8.py"
    assert src[key]==m.KM2J_CODE_BLOB
    assert m.KM2J_HEAD=="63147c01f1b1fd3f0cf698c919db25d9bd2ef80b"


def test_source_mutation_fail_closed(monkeypatch):
    monkeypatch.setattr(m,"KM2J_CODE_BLOB","0"*40)
    with pytest.raises(ValueError,match="IMMUTABLE_KM2J_SOURCE_CHANGED"):
        m.exact_parent_sources()


def test_exact_gl_partial_antiderivative_for_polynomials():
    for order in (4,8,12,16):
        x,w,P=fc.partial_gauss_integration(order)
        assert abs(w.sum()-2)<2e-14
        for power in range(order):
            ant=(x**(power+1)-(-1.)**(power+1))/(power+1)
            assert np.max(abs(P@x**power-ant))<1e-11


def test_static_frequency_green_bolometric_exact():
    h=.37;j0=2.5;u=.21
    x,w=np.polynomial.legendre.leggauss(80)
    t=u*(x+1)/2
    num=np.dot(w*u/2,j0*np.exp(-4*h*(u-t)))
    exact=fc.static_green_energy(h,j0,u)
    assert abs(num/exact-1)<2e-14
    # Integral (j/h) exp(4*y) over exact line support [-h*u,0].
    yl,yw=np.polynomial.legendre.leggauss(80)
    y=h*u*(yl-1)/2
    actual=np.dot(yw*h*u/2,(j0/h)*np.exp(4*y))
    assert abs(actual/exact-1)<2e-14


def test_gaussian_frequency_packet_energy_and_angular_moments():
    n=np.vstack([np.eye(3),-np.eye(3)])
    w=np.ones(6)*(4*np.pi/6)
    means=np.array([[-.015,-.04,-.015,-.06,-.05,-.12],
                    [-.016,-.039,-.023,-.052,-.053,-.109]])
    p=np.ones_like(means)*1.e-9
    sig=np.array([1.7e-5,2.0e-5])
    mom=fc.summarize_packets(means,sig,p,n,w)
    hist,gap=fc.gaussian_bin_histogram(means,sig,p,w,np.linspace(-.5,.5,1201))
    assert gap<2e-12
    assert abs(hist.sum()/mom["rho"]-1)<2e-12
    assert 0<mom["redwing_fraction"]<1
    assert mom["std_log_nu"]>0
    assert np.linalg.norm(mom["q"])<mom["rho"]
    assert np.all(np.isfinite(mom["quadrupole"]))


def test_histogram_hard_fail_if_source_outside_band():
    n=np.vstack([np.eye(3),-np.eye(3)])
    w=np.ones(6)
    with pytest.raises(ValueError,match="support excludes"):
        fc.gaussian_bin_histogram(np.ones((1,6))*.8,np.array([1e-5]),
                                 np.ones((1,6)),w,np.linspace(-.5,.5,1201))


def test_real_parent_joint_ivps_not_relabelled_postprocess(science):
    assert set(science["data"])=={"GL12","GL16"}
    assert science["new_solved_joint_Einstein_P8_chemistry_IVPs"]==2
    for key,c in science["data"].items():
        assert c["parent_joint_ivp_nfev"]>10
        assert c["rays"]==2*c["ntheta"]**2
        assert c["source_guard_count"]>=12
        assert c["characteristic_samples"]==320
        assert 0<c["final_x_e"]<.1
        assert c["initial_x_e"]>.3
        assert len(c["parent_original_j_sha256"])==64


def test_real_41_epoch_frequency_and_five_physical_spectra(science):
    for c in science["data"].values():
        assert set(c["scenarios"])=={"shear","H_only"}
        for mode in c["scenarios"].values():
            epochs=mode["epochs"];spectra=mode["spectra"]
            assert len(epochs)==41 and len(spectra)==5
            assert epochs[0]["rho"]==0
            for ep in epochs[1:]:
                assert 0<ep["rho"] and 0<ep["ratio_to_P8_rho"]<1
                assert -.5<ep["mean_log_nu"]<.5
                assert 0<ep["std_log_nu"]<.5
                assert 0<=ep["redwing_fraction"]<=1
                assert ep["quadrupole_frob"]>=0
            for z in spectra:
                assert len(z["spectrum_energy_bins"])==1200
                assert z["histogram_loss_relative"]<2e-11
                assert abs(sum(z["spectrum_energy_bins"])/z["rho"]-1)<2e-10


def test_sheared_photon_frequency_actual_physical_effect(science):
    for c in science["data"].values():
        physical=c["scenarios"]["shear"]["epochs"][-1]
        control=c["scenarios"]["H_only"]["epochs"][-1]
        assert abs(physical["mean_log_nu"]-control["mean_log_nu"])>1e-5
        assert abs(physical["rho"]-control["rho"])>1e-12
        assert c["comparison"][-1]["rho_shear_minus_H_only"]==physical["rho"]-control["rho"]
        assert 0<c["line_energy_fraction_range"][0]<1
        assert 0<c["line_energy_fraction_range"][1]<1
        assert c["min_expansion_through_frequency"]>0


def test_scoped_cross_angular_grid_agreement(science):
    assert science["cross_grid"]["xe_abs_diff"]<1e-7
    assert science["cross_grid"]["line_centroid_abs_diff"]<2e-3
    for c in science["data"].values():
        assert c["max_source_fourmoment_relative_gap"]<2e-12
        cons=c["conservation"]
        assert cons["max_Hamiltonian_norm"]<5e-8
        assert cons["max_momentum_norm"]<5e-8
        assert cons["hamiltonian_propagation_error"]<5e-8
        assert cons["momentum_integrated_error"]<5e-8


def test_actual_raw_packet_npz_sha_and_positive_energy(science):
    for c in science["data"].values():
        p=Path(m.HERE)/"results"/c["packet_npz"]
        assert p.exists()
        assert hashlib.sha256(p.read_bytes()).hexdigest()==c["packet_npz_sha256"]
        with np.load(p) as z:
            assert z["source_packets"].shape==(320,c["rays"])
            assert np.all(z["source_packets"]>0)
            assert len(z["doppler_sigma"])==320
            assert np.all(z["doppler_sigma"]>0)
            assert np.all(z["time_quadrature_weights"]>0)
            assert z["source_expected_fourforce"].shape==(320,4)


def test_dag_no_double_count_or_production_claim(science):
    assert science["upper_dag"]=="9/15"
    assert science["km2"]=="PARTIAL"
    assert science["new_completed_upper_nodes"]==0
    assert not science["production_ready"] and not science["merge_ready"] and not science["auto_next"]
    assert science["native_subagent"]=="NOT_RUN"
    assert "resonant Lya frequency diffusion" in science["not_implemented"]
