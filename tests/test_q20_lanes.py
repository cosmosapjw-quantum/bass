"""Q20 · **H 앵커 lane 분리** 게이트 (87차, 외부 리뷰 C5).

★★ 왜 필요한가.  모델 H 와 ΛCDM H 규약이 최대 33.8 % 차이 나고 자기일관 앵커가
외부 앵커의 0.389 배다.  이걸 "사용자 선택사항" 으로만 남기면 나중에 재결합
이동을 봤을 때 그것이 **anisotropic recombination physics** 인지 그냥
**H normalization 을 다르게 준 것** 인지 섞인다.  그래서 lane 을 강제한다.
"""
import numpy as np
import pytest

from bianchi.q import contract as C
from bianchi.q import rate as RT
from bianchi.q.model import Collision, Grid, Model, run
from bianchi.thermo import history_api as HA


@pytest.fixture(scope="module")
def hist():
    return HA.SahaHistory()


def test_q20_lane_is_required(hist):
    """★ 기본값이 없다 — 둘 중 하나를 **명시**해야 한다."""
    assert C.budget("Q20", "lane_required") is True
    with pytest.raises(ValueError, match="lane 은 필수"):
        RT.RateSchedule(hist, RT.Cosmology(z0=600.0), mode="lcdm")
    with pytest.raises(ValueError, match="lane 은 필수"):
        RT.RateSchedule(hist, RT.Cosmology(z0=600.0), lane="hybrid")


def test_q20_internal_lane_rejects_external_anchor(hist):
    """★ internal lane 은 Gauss 구속이 정하는 앵커만 쓴다 (조용한 혼합 금지)."""
    assert C.budget("Q20", "internal_rejects_external") is True
    with pytest.raises(ValueError, match="internal"):
        RT.RateSchedule(hist, RT.Cosmology(z0=600.0), lane="internal",
                        H_anchor=1e-14, Omega0=0.99)
    with pytest.raises(ValueError, match="Omega0"):
        RT.RateSchedule(hist, RT.Cosmology(z0=600.0), lane="internal")
    s = RT.RateSchedule(hist, RT.Cosmology(z0=600.0), lane="internal", Omega0=0.99)
    assert s.anchor_source.startswith("gauss")
    # 정의상 rho_r = 3 H^2 Omega_0 을 만족한다
    rho = s.cosmo.rho_rad(600.0)
    assert abs(3.0 * s.H_anchor ** 2 * 0.99 / rho - 1.0) <= 1e-12


def test_q20_phenomenology_lane_raises_on_omega_mismatch(hist):
    """★ 경고가 아니라 **예외**다 — 정합하지 않는 초기자료로 시작하면 멈춘다."""
    tol = C.budget("Q20", "anchor_consistency")
    with pytest.raises(ValueError, match="어긋난다"):
        RT.RateSchedule(hist, RT.Cosmology(z0=600.0), lane="phenomenology",
                        Omega0=0.99)
    # 앵커와 정합하는 Omega_0 는 통과하고, 정합도를 기록한다
    cos = RT.Cosmology(z0=600.0)
    Ha = float(cos.H_lcdm(600.0))
    om_ok = float(cos.rho_rad(600.0) / (3.0 * Ha ** 2))
    s = RT.RateSchedule(hist, cos, lane="phenomenology", Omega0=om_ok)
    assert s.anchor_consistency <= tol


def test_q20_two_lanes_give_measurably_different_rates(hist):
    """★ 두 lane 의 차이를 **실측해 기록**한다 (숨기지 않는다)."""
    cos = RT.Cosmology(z0=600.0)
    a = RT.RateSchedule(hist, cos, lane="internal", Omega0=0.99)
    b = RT.RateSchedule(hist, cos, lane="phenomenology")
    ratio = a.H_anchor / b.H_anchor
    assert 0.2 <= ratio <= 0.6, ratio          # 실측 0.3885
    # nu 는 앵커에 반비례하므로 lane 을 바꾸면 nu 가 1/ratio 배 달라진다
    rel = abs(a.nu(0.0, 0.0) / b.nu(0.0, 0.0) - 1.0)
    assert rel >= C.budget("Q20", "lane_gap_recorded"), rel


def test_q20_lane_is_printed_in_summary_and_describe(hist):
    """★ 산출물에 lane 이 각인된다 — 나중에 어느 lane 이었는지 묻지 않아도 된다."""
    m = Model(type="I", grid=Grid(12, 24), tau_span=(0.0, -0.5), nsteps=100,
              collision=Collision.thomson(hist, rate_mode="lcdm"),
              cosmology=RT.Cosmology(z0=600.0), lane="phenomenology")
    assert "lane=phenomenology" in m.schedule().describe()
    assert "lane=phenomenology" in m.summary()


def test_q20_internal_lane_runs_end_to_end(hist):
    """internal lane 이 Gauss 면 Omega_0 를 스스로 읽어 진화한다."""
    m = Model(type="I", grid=Grid(12, 24), tau_span=(0.0, -0.5), nsteps=100,
              collision=Collision.thomson(hist, rate_mode="model"),
              cosmology=RT.Cosmology(z0=600.0), lane="internal")
    s = m.schedule()
    assert s.anchor_source.startswith("gauss")
    st, _, _ = run(m, fast=True)
    assert np.isfinite(st.lG).all()
