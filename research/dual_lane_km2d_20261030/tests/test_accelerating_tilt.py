"""KM-2D: original BASS causal physics with prescribed accelerating electron tilt.

One cached physical science campaign; tests read real output and independently
challenge fixed-beta, vacuum, normal-slice force, source-null, clock, tamper.
"""
from pathlib import Path
import sys
import numpy as np
import pytest
from research.dual_lane_km2d_20261030 import accelerating_tilt as x


@pytest.fixture(scope="module")
def science(tmp_path_factory):
    return x.run(tmp_path_factory.mktemp("km2d")/"science.json")


def test_scoped_physical_program_and_immutable_code(science):
    assert science["KM2"]=="PARTIAL" and science["upper_DAG"]=="9/15"
    assert science["new_upper_completed"]==0
    assert science["KM2C_original_blobs"][str(x.CODE/"curved_tilt.py")]==x.ORIGINAL_KM2C_SHA
    assert not science["production_ready"] and not science["auto_next"]


def test_increasing_time_refinement_at_fixed_physical_source(science):
    rows=science["cases"]
    assert list(sorted(rows,key=int))==["8","16","32"]
    errors=[rows[k]["max_source_error"] for k in ("8","16","32")]
    assert 0<errors[2]<errors[1]<errors[0]
    assert errors[2]<3e-9
    for z in rows.values():
        assert z["max_panel_condition"]<1e12
        assert z["max_source_self_consistency_error"]<2e-8
        assert len(z["source_rows"])==5
        assert all(np.isfinite(v["C_direct"]) for v in z["source_rows"])


def test_new_accelerating_physical_work_is_nonzero_and_balanced(science):
    w=science["independent_acceleration_work"]
    assert w["work_closure_absolute"]<1e-7
    assert abs(w["integrated_acceleration_work"])>1e-4
    assert w["would_omit_acceleration_work_error"]>1e-4
    assert w["max_product_rule_residual_relative"]<2e-11
    assert w["max_instantaneous_force_relative"]<5e-9


def test_source_null_initial_angular_memory_is_not_discarded(science):
    p=science["source_null_octupole"]
    assert p["initial_source_norm"]<2e-11
    assert p["final_source_norm"]>1e-5
    assert p["whole_initial_carrier_retained"]


def test_frozen_beta_limit_reproduces_original_KM2C_operator_and_history():
    law=x.ElectronVelocity((.3,-.4,.2),(0.,0.,0.),.12)
    geo,J=x.make_fixture(6,x.FieldProfile("main",1.3),law.beta(0),.12)
    m=x.MovingMemory(geo,J,law,1.3)
    old=x.CurvedMemory(geo,J,law.beta(0),1.3)
    for t in (0.,.06,.12):
        assert np.max(abs(m.at(t)["D"]-old.at(t)["D"]))<2e-15
        assert np.max(abs(m.at(t)["L"]-old.at(t)["L"]))<2e-13
        assert np.max(abs(m.at(t)["G"]-old.at(t)["G"]))<2e-13
        assert np.max(abs(m.tau(t)-old.tau(t)))<2e-12
    v=x.VolterraHistory(m,8);v0=x.VolterraHistory(old,8)
    assert np.max(abs(v.moment(.12)-v0.moment(.12)))<2e-11
    assert abs(x.moving_balance(m,0.,J)["acceleration_work_rate"])<1e-13


def test_full_normal_screen_collision_matches_original_instantaneous_source():
    m=x.make_moving(n=6,T=.12)
    for t in (0.,.06,.12):
        z=m.at(t);X=m.X0
        J=m.carrier(t,X);M=m.project(t,X)
        physical=z["op"].rhs(J,m.nu0)
        E=z["screen"];mu=z["mu"]
        pull=np.einsum("nia,nij,njb->nab",E,physical,E)/mu[:,None,None]**4
        predicted=-z["d"][:,None,None]*X+np.einsum(
            "nab,b->na",z["G"],M.ravel()).reshape(X.shape)
        assert np.max(abs(pull-predicted))<2e-10


def test_independent_optical_depth_vs_gauss_quadrature():
    m=x.make_moving(n=6,T=.12)
    gx,gw=x.leggauss(24)
    ref=sum(float(w)*m.at(float(s))["d"] for s,w in zip(.06*(gx+1),.06*gw))
    assert np.max(abs(ref-m.tau(.12)))<2e-11
    assert np.max(abs(m.tau(.12)-.12*m.at(0)["d"]))>1e-4


def test_vacuum_keeps_full_initial_carrier_and_has_zero_attentuation():
    m=x.make_moving(n=6,T=.12,nu0=0.0)
    v=x.VolterraHistory(m,5)
    assert np.max(abs(v.carrier(.12)-m.carrier(.12,m.X0)))<2e-12
    assert np.max(abs(m.tau(.12)))==0


def test_no_direct_ode_or_radiation_history_in_volterra(monkeypatch):
    m=x.make_moving(n=6,T=.12)
    def forbidden(*args,**kw):
        raise AssertionError("Volterra called a direct Boltzmann RHS")
    monkeypatch.setattr(x.TiltedThomson,"rhs",forbidden)
    v=x.VolterraHistory(m,6)
    assert np.isfinite(v.moment(.12)).all()


def test_velocity_entire_affine_support_is_subluminal_and_fail_closed():
    good=x.ElectronVelocity((.3,-.4,.2),(.2,-.1,.12),.25)
    assert np.linalg.norm(good.beta(.25))<1
    assert np.array_equal(good.derivative(0.),good.derivative(.25))
    with pytest.raises(ValueError):
        x.ElectronVelocity((.9,0,0),(.9,0,0),.25)
    with pytest.raises(ValueError):
        x.ElectronVelocity((0,0,0),(0,0,0),0)
    with pytest.raises(ValueError):
        good.beta(.251)


def test_source_tamper_fail_closed(monkeypatch):
    monkeypatch.setattr(x,"ORIGINAL_COLLISION_SHA","0"*40)
    with pytest.raises(ValueError,match="physical source Git blob identity"):
        x.check_origins()


def test_separate_spectral_and_matter_claim_boundaries(science):
    assert science["thermal_spectral_validity"]=="NOT_CERTIFIED"
    assert science["electron_Euler_or_continuity"]=="NOT_RUN"
    assert science["Einstein_feedback"]=="NOT_RUN"
    assert science["distinct_author_R6_C9"]=="NOT_RUN"
