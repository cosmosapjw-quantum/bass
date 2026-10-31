"""KM2M first polarized Thomson frequency source, normal scientific tests."""
import hashlib
import json
import math
import os
from pathlib import Path

import numpy as np
import pytest

from research.dual_lane_km2m_20261031 import first_gain as m

@pytest.fixture(scope="session")
def science(tmp_path_factory):
    p=os.environ.get("KM2M_SCIENCE_JSON")
    if p and Path(p).is_file():
        return json.loads(Path(p).read_text())
    return m.run_science(tmp_path_factory.mktemp("km2m")/"physics.json",orders=(12,))

def test_source_locked_original_KM2J_KM2K_KM2L():
    sources=m.source_guards()
    assert sources["research/dual_lane_km2l_20261031/thomson_lya.py"]==m.KM2L_BLOB
    assert len(sources)>=16

def test_tampered_original_fails_closed(monkeypatch):
    monkeypatch.setattr(m,"KM2L_BLOB","0"*40)
    with pytest.raises(ValueError,match="IMMUTABLE_KM2L_SOURCE_CHANGED"):
        m.source_guards()

def test_positive_gaussian_exact_CDF_energy_source():
    N=6
    p=np.ones((3,N))*2.e-9
    center=np.array([[-.1]*N,[-.12]*N,[-.15]*N])
    sig=np.array([2e-5,2e-5,2e-5])
    D=np.ones(N)
    spec,gap=m.electron_frame_gaussian_histogram(p,center,sig,D)
    assert spec.shape==(N,1200)
    assert gap<1e-12
    assert abs(spec.sum()/p.sum()-1)<1e-12

def test_out_of_band_nonzero_photons_fail_closed():
    N=6
    p=np.ones((1,N))*1.e-9
    with pytest.raises(ValueError,match="truncates real packets"):
        m.electron_frame_gaussian_histogram(p,np.full((1,N),.62),
                                            np.array([2e-5]),np.ones(N))

def test_bulk_Doppler_normal_bin_remap_conserves_source():
    N=6
    x=np.zeros((N,1200))
    x[:,570:640]=1.e-9
    D=np.array([.98,.99,1.,1.01,1.02,1.03])
    w=np.ones(N)
    out,gap=m.normal_frequency_spectrum(x,D,w)
    assert gap<1e-13 and np.min(out)>=0
    assert abs(out.sum()/x.sum()-1)<1e-13

def test_exact_unpolarized_thomson_differential_cross_section():
    # Three incident and outgoing ray directions, beta=0, original P8.
    from tilted_collision import TiltedThomson
    n=np.vstack([np.eye(3),-np.eye(3)])
    w=np.ones(6)*(4*np.pi/6)
    o=TiltedThomson(n,w,np.zeros(3))
    J=np.zeros((6,3,3))
    J[0]=.5*(np.eye(3)-np.outer(n[0],n[0]))
    ge=o.gain(J)
    measured=np.trace(ge,axis1=1,axis2=2)
    expected=(3/(16*np.pi))*w[0]*(1+(n@n[0])**2)
    assert np.max(abs(measured-expected))<2e-14

def test_real_physical_gain_new_epochs_and_original_IVPs(science):
    assert science["upper_dag"]=="9/15"
    assert len(science["snapshots"])>=1
    for case in science["snapshots"].values():
        assert case["actual_original_joint_IVP_reintegrations"]==3
        assert len(case["measurements"])==5
        assert min(case["original_joint_IVP_RHS_evals"])>10
        assert case["parent_Einstein_conservation"]["max_Hamiltonian_norm"]<5e-8
        assert case["parent_Einstein_conservation"]["max_momentum_norm"]<5e-8

def test_first_collision_gain_reproduces_exact_original_P8(science):
    for case in science["snapshots"].values():
        for x in case["measurements"]:
            assert 0<x["incoming_ballistic_tagged_rho"]
            assert x["normal_first_gain_energy_rate"]>0
            assert x["incoming_first_event_energy_rate"]>0
            assert x["P8_gain_bolometric_parity_relative_error"]<3e-10
            assert x["original_KM2L_first_rate_relative_error"]<4e-10

def test_rest_frame_thomson_energy_and_transverse_polarization(science):
    for case in science["snapshots"].values():
        for x in case["measurements"]:
            assert x["electron_rest_source_gain_relative_error"]<5e-6
            assert 0<=x["linear_polarization_mean"]<=1
            assert 0<=x["linear_polarization_rms"]<=1
            assert 0<=x["linear_polarization_max"]<=1+1e-9
            assert x["frequency_packet_CDF_error"]<5e-12
            assert x["normal_frequency_remap_energy_error"]<5e-13

def test_frequency_snapshots_have_exact_bins_and_positive_source(science):
    for case in science["snapshots"].values():
        for x in case["measurements"]:
            for key in ("incoming_electron_frame_spectrum",
                        "gained_electron_frame_spectrum",
                        "gained_normal_frame_spectrum"):
                v=np.asarray(x[key])
                assert v.shape==(1200,)
                assert np.min(v)>=0
                assert np.sum(v)>0
            assert np.isfinite(x["normal_scattered_logfrequency_centroid"])
            assert np.isfinite(x["electron_rest_scattered_logfrequency_centroid"])

def test_original_factorized_first_P8_polarized_source_replay(science):
    for case in science["snapshots"].values():
        x=case["measurements"][-1]
        p=m.HERE/"results"/x["factorized_source_file"]
        assert p.is_file()
        assert hashlib.sha256(p.read_bytes()).hexdigest()==x["factorized_source_sha256"]
        with np.load(p) as a:
            N=case["n_theta"]**2*2
            assert a["M_e_frequency"].shape==(1200,3,3)
            assert a["S"].shape==(N,3,3)
            assert a["first_gain_normal_bolometric_tensor"].shape==(N,3,3)
            assert a["incoming_rest_frequency_bin"].shape==(N,1200)

def test_KM2M_scope_not_promoted_to_full_spectrum(science):
    assert science["KM2"]=="PARTIAL"
    assert science["new_completed_upper_nodes"]==0
    assert not science["merge_ready"] and not science["production_ready"]
    assert not science["auto_next"]
    assert science["native_subagent"]=="NOT_RUN"
    assert "time propagation of first-scattered radiation" in science["not_implemented"]
