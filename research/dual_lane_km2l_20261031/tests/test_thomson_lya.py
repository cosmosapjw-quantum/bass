"""KM2L bounded physical tests on original live Einstein-P8-Peebles sources."""
from __future__ import annotations
import hashlib,json,os
from pathlib import Path
import numpy as np
import pytest

from research.dual_lane_km2l_20261031 import thomson_lya as m


@pytest.fixture(scope="session")
def science(tmp_path_factory):
    p = os.getenv("KM2L_SCIENCE_JSON")
    if p and Path(p).is_file():
        return json.loads(Path(p).read_text())
    return m.run_science(tmp_path_factory.mktemp("km2l")/"physics.json")


def test_original_KM2K_and_KM2J_source_blobs():
    sources = m.original_source_guards()
    for f,digest in m.SOURCE_BLOBS.items():
        assert sources[f] == digest
    assert len(sources) >= 14


def test_immutable_KM2K_tamper_fails_closed(monkeypatch):
    monkeypatch.setitem(m.SOURCE_BLOBS,
                        "research/dual_lane_km2k_20261031/escaping_lya.py",
                        "0"*40)
    with pytest.raises(ValueError,match="FROZEN_KM2K_PHYSICAL_SOURCE_CHANGED"):
        m.original_source_guards()


def test_constant_medium_exact_thomson_green_integral():
    from numpy.polynomial.legendre import leggauss
    h,lam,emit,t = .37,8.6,2.4,.25
    x,w = leggauss(64)
    u=t*(x+1)/2
    actual = np.dot(t*w/2,emit*np.exp(-(4*h+lam)*(t-u)))
    exact = m.static_green(h,lam,emit,t)
    assert abs(actual/exact-1) < 1e-14
    assert 0<exact<m.static_green(h,0.,emit,t)


def test_Thomson_limits_and_invalid_sources_fail_closed():
    t=.25
    assert m.static_green(.4,0.,2.,t)>0
    assert abs(m.static_green(.4,0.,2.,t)/m.static_green(.4,1e-15,2.,t)-1)<2e-14
    assert m.static_green(.4,1.e6,2.,t)<1e-4
    assert m.static_green(.4,12.,2.,0)==0
    with pytest.raises(ValueError):
        m.static_green(-.1,1.,2.,.2)
    with pytest.raises(ValueError):
        m.static_green(.1,-1.,2.,.2)


def test_genuinely_reintegrated_original_Einstein_P8_Peebles_IVPs(science):
    assert set(science["cases"]) == {"GL12","GL16"}
    assert science["separate_Einstein_P8_Peebles_initial_value_problems"]==2
    assert science["reintegrations_each"]==2
    for key,case in science["cases"].items():
        assert case["original_ray_count"]==2*case["n_theta"]**2
        assert case["joint_original_KM2J_IVP_reintegrations"]==2
        assert min(case["joint_original_parent_rhs_calls"])>10
        assert case["max_SI_opacity_relative_error"]<3e-12
        assert len(case["inherited_initial_J_SHA256"])==64


def test_exact_original_packet_and_new_optical_source_SHA(science):
    for case in science["cases"].values():
        root = m.HERE/"results"
        for fname,key in ((case["KM2K_original_packets_file"],"KM2K_original_packets_sha256"),
                          (case["thomson_opacity_file"],"thomson_opacity_sha256")):
            f=root/fname
            assert f.is_file()
            assert hashlib.sha256(f.read_bytes()).hexdigest()==case[key]
        with np.load(root/case["thomson_opacity_file"]) as a:
            assert a["hazard_nodes"].shape==(320,case["original_ray_count"])
            assert a["tau_nodes"].shape==(320,case["original_ray_count"])
            assert a["tau_edges"].shape==(41,case["original_ray_count"])
            assert np.all(a["hazard_nodes"]>0)
            assert np.min(np.diff(a["tau_edges"],axis=0))>0
            assert np.all(a["tau_edges"][0]==0)


def test_246_physical_epochs_and_30_actual_frequency_spectra(science):
    assert science["new_spectral_epoch_count"]==246
    assert science["frequency_spectrum_snapshot_count"]==30
    assert science["frequency_bin_count"]==1200
    for case in science["cases"].values():
        assert len(case["comparisons"])==41
        assert set(case["scenarios"])=={"shear_thomson","shear_free","Honly_thomson"}
        for scenario in case["scenarios"].values():
            assert len(scenario["epochs"])==41
            assert len(scenario["spectra"])==5
            assert scenario["epochs"][0]["rho"]==0
            for s in scenario["spectra"]:
                assert len(s["spectrum_energy_bins"])==1200
                assert abs(sum(s["spectrum_energy_bins"])/s["rho"]-1)<2e-10


def test_no_scattering_exactly_recovers_original_KM2K(science):
    for case in science["cases"].values():
        free=case["scenarios"]["shear_free"]["epochs"]
        assert all(e["first_collision_energy_rate"]==0 for e in free)
        assert all(e["mean_packet_survival"]==1 for e in free)
        assert all(e["rho"]>0 for e in free[1:])


def test_real_thomson_first_collision_physics(science):
    for case in science["cases"].values():
        a=case["scenarios"]["shear_thomson"]["epochs"]
        b=case["scenarios"]["shear_free"]["epochs"]
        for u,v in zip(a[1:],b[1:]):
            assert 0<u["rho"]<v["rho"]
            assert 0<u["mean_packet_survival"]<1
            assert u["first_collision_energy_rate"]>0
            assert u["max_packet_thomson_tau"]>0
            assert 0<=u["redwing_fraction"]<=1
            assert abs(u["mean_log_nu"])<.5
        assert case["comparisons"][-1]["first_scattered_marked_fraction"]>0


def test_anisotropic_propagation_distinct_from_counterfactual(science):
    for case in science["cases"].values():
        m1=case["scenarios"]["shear_thomson"]["epochs"][-1]
        m2=case["scenarios"]["Honly_thomson"]["epochs"][-1]
        assert abs(m1["mean_log_nu"]-m2["mean_log_nu"])>1e-5
        assert abs(m1["rho"]/m2["rho"]-1)>1e-6


def test_angular_grid_consistency_and_original_hamiltonian(science):
    a=science["cases"]["GL12"]["comparisons"][-1]
    b=science["cases"]["GL16"]["comparisons"][-1]
    assert abs(a["unscattered_over_free_energy"]-b["unscattered_over_free_energy"])<.05
    for case in science["cases"].values():
        c=case["reintegrated_KM2J_conservation"]
        assert c["max_Hamiltonian_norm"]<5e-8
        assert c["max_momentum_norm"]<5e-8
        assert c["hamiltonian_propagation_error"]<5e-8
        assert c["momentum_integrated_error"]<5e-8


def test_scoped_only_no_false_full_collision_or_production(science):
    assert science["upper_dag"]=="9/15"
    assert science["new_completed_upper_nodes"]==0
    assert science["KM2"]=="PARTIAL"
    assert not science["merge_ready"] and not science["production_ready"] and not science["auto_next"]
    assert science["native_subagent"]=="NOT_RUN"
    assert "scattered photon angular gain and repeated Thomson scattering" in science["not_implemented"]
