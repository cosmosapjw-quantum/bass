"""KM2N: source-locked real Einstein/P8/Peebles one-scatter photon tests."""
import hashlib, json, math, os
from pathlib import Path
import numpy as np
import pytest
from scipy.integrate import quad
from research.dual_lane_km2n_20261031 import once_scattered as m

@pytest.fixture(scope="session")
def science(tmp_path_factory):
    s=os.getenv("KM2N_SCIENCE_JSON")
    if s and Path(s).is_file():return json.loads(Path(s).read_text())
    return m.run_science(tmp_path_factory.mktemp("km2n")/"science.json",grids=(12,))

def test_source_git_byte_guards_reused_not_modified():
    sources=m.source_guards()
    assert len(sources)>=17
    assert sources["research/dual_lane_km2m_20261031/first_gain.py"]==m.KM2M_BLOB

def test_modified_source_lock_fails_closed(monkeypatch):
    monkeypatch.setattr(m,"KM2M_BLOB","0"*40)
    with pytest.raises(ValueError,match="FROZEN_SOURCE_KM2M_CHANGED"):
        m.source_guards()

def test_exact_analytic_poisson_single_scattering_pulse():
    h=.3;nu=7.1;t=.15;A=1.3
    actual=m.analytic_one_scatter_pulse(h,nu,A,t)
    independently=quad(lambda s:A*math.exp(-(4*h+nu)*s)*nu*
                       math.exp(-(4*h+nu)*(t-s)),0,t,epsabs=1e-14)[0]
    assert abs(actual/independently-1)<4e-14
    assert abs(m.analytic_one_scatter_pulse(0.,nu,A,t)/
               (A*(nu*t)*math.exp(-nu*t))-1)<2e-14
    assert m.analytic_one_scatter_pulse(.4,0.,1.,t)==0.

def test_exact_constant_emissivity_one_scatter_analytic():
    h=.31;nu=6.9;t=.2;j=2.5;a=4*h+nu
    exact=m.analytic_one_scatter_constant_emissivity(h,nu,j,t)
    ref=quad(lambda s:nu*j*(-math.expm1(-a*s))/a*math.exp(-a*(t-s)),
             0,t,epsabs=1e-14)[0]
    assert abs(ref/exact-1)<4e-14
    assert m.analytic_one_scatter_constant_emissivity(h,0.,j,t)==0.

def test_analytic_invalid_inputs_are_rejected():
    with pytest.raises(ValueError):m.analytic_one_scatter_pulse(-1,1,2,.2)
    with pytest.raises(ValueError):m.analytic_one_scatter_constant_emissivity(.2,-1,2,.2)
    with pytest.raises(ValueError):m.analytic_one_scatter_pulse(.2,1,2,-.2)

def test_exact_positive_frequency_matrix_remap_conserves_energy():
    n=4;r=np.zeros((n,m.NBINS,2,2))
    r[:,540:560,0,0]=2.e-9;r[:,540:560,1,1]=1.e-9;r[:,540:560,0,1]=2e-10
    r[:,540:560,1,0]=2e-10
    x,gap=m.remap_logfreq_source_tensor(r,np.array([-.01,0.,.01,.02]))
    assert x.shape==r.shape and gap<3e-13
    assert abs(x.trace(axis1=2,axis2=3).sum()/r.trace(axis1=2,axis2=3).sum()-1)<3e-13

def test_out_of_band_nonzero_scattered_source_rejected():
    x=np.zeros((1,m.NBINS,2,2));x[0,0,0,0]=1.
    with pytest.raises(ArithmeticError,match="frequency support"):
        m.remap_logfreq_source_tensor(x,np.array([-.02]))

def test_original_einstein_Bianchi_polarized_P8_chemistry_live(science):
    assert set(science["cases"]).issubset({"GL12","GL16"})
    for case in science["cases"].values():
        assert len(case["snapshots"])==5
        assert case["original_P8_ray_count"]==2*case["grid"]**2
        assert min(case["fresh_original_joint_IVP_RHS"])>10
        assert case["original_Einstein_conservation"]["max_Hamiltonian_norm"]<5e-8
        assert case["original_Einstein_conservation"]["max_momentum_norm"]<5e-8
        assert case["max_source_p8_gain_parity_relative"]<4e-10

def test_five_real_observations_are_retarded_and_positive(science):
    for case in science["cases"].values():
        for i,e in enumerate(case["snapshots"],1):
            assert abs(e["u"]-.05*i)<2e-14
            assert 0<e["rho_exactly_one"]
            assert 0<e["original_KM2L_ballistic_rho"]
            assert e["new_once_scattered_to_ballistic_energy_ratio"]>0
            assert len(e["source_rates_per_event_u"])==8*i
            assert e["screen_eigen_min"]>-1e-18
            assert 0<=e["mean_linear_polarization"]<=1
            assert 0<=e["max_linear_polarization"]<=1+2e-9

def test_true_frequency_field_and_fourmom_consistency(science):
    assert science["frequency_bins_per_snapshot"]==1200
    for case in science["cases"].values():
        for row in case["snapshots"]:
            assert len(row["spectral_energy_bins"])==1200
            assert abs(sum(row["spectral_energy_bins"])/row["rho_exactly_one"]-1)<2e-11
            assert np.all(np.asarray(row["spectral_energy_bins"])>=0)
            assert np.linalg.norm(row["q_exactly_one"])<row["rho_exactly_one"]
            assert row["frequency_bolometric_relative_gap"]<2e-11
            assert row["max_remap_relative_gap"]<5e-12

def test_live_original_source_ledger_and_final_full_matrix_sha(science):
    for case in science["cases"].values():
        a=m.HERE/"results"/case["first_source_ledger_file"]
        assert hashlib.sha256(a.read_bytes()).hexdigest()==case["first_source_ledger_sha256"]
        with np.load(a,allow_pickle=False) as z:
            assert z["Me"].shape==(41,1200,3,3)
            assert z["F"].shape==(41,2*case["grid"]**2,3,2)
            assert np.all(np.diff(z["tau"],axis=0)>0)
        final=case["snapshots"][-1]
        p=m.HERE/"results"/final["factorized_field_file"]
        assert hashlib.sha256(p.read_bytes()).hexdigest()==final["factorized_field_sha256"]
        with np.load(p,allow_pickle=False) as z:
            X=z["screen_spectral_first_one"]
            assert X.shape==(2*case["grid"]**2,1200,2,2)
            assert np.linalg.eigvalsh(X.sum(axis=1)).min()>-1e-17

def test_GL_angular_grid_response_is_bounded_not_continuum_claim(science):
    if not {"GL12","GL16"}.issubset(science["cases"]):pytest.skip("single grid fixture")
    a=science["cases"]["GL12"]["snapshots"][-1]
    b=science["cases"]["GL16"]["snapshots"][-1]
    assert abs(a["rho_exactly_one"]/b["rho_exactly_one"]-1)<1e-5
    assert abs(a["mean_linear_polarization"]-b["mean_linear_polarization"])<2e-4
    assert abs(a["mean_logfreq"]-b["mean_logfreq"])<3e-4

def test_no_double_count_and_no_false_DAG_promotion(science):
    assert science["upper_dag"]=="9/15" and science["KM2"]=="PARTIAL"
    assert science["new_upper_completed"]==0
    assert not science["production_ready"] and not science["merge_ready"] and not science["auto_next"]
    assert science["native_subagent"]=="NOT_RUN"
    assert "second and higher Thomson scattering gain" in science["not_implemented"]
