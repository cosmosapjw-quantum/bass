"""
H4 · imperfect fluid 유도 시험 — Eckart/IS 가 계층 l=2 절단의 귀결임을 확인.

★ **두 경로를 분리해 각각 시험하고, 마지막에 교차검증**한다:
    경로 A (freestream): 정확 구적의 유한차분 — 계층 수식 미사용
    경로 B (PSTF 계층) : 식 (12) l=2 방정식 평가 — (손세팅 판은) 구적 미사용
  한쪽의 실수를 다른 쪽이 잡는다.

유도값 (무질량 무충돌):  τ_π = 1/(4H),  η = ρ/(15H)
"""
import numpy as np
import pytest

from bianchi.matter import viscous_derived as vd
from bianchi.matter import viscous as vis


# ═══════════════════════════════ 경로 A — freestream (정확 구적)
def test_route_a_massless_damping_is_minus_four_H():
    """★ 경로 A: σ=0 에서 dπ/dt = −4H π (무질량).  계층 수식을 쓰지 않은 측정."""
    r = vd.route_a_damping(0.0, H_hubble=1.0)
    assert abs(r["rate_mean"] - (-4.0)) < 1e-6, r
    assert r["anisotropy"] < 1e-6            # 무질량은 성분 무관 (등방적 감쇠)


def test_route_a_source_is_minus_8_over_15():
    """경로 A: 급작응답 소스 계수 ≈ −8/15 (구적·차분 수준)."""
    c = vd.route_a_source(0.0)
    assert abs(c - vd.MASSLESS_SOURCE_COEFF) < 5e-3, c


@pytest.mark.parametrize("mass", [0.5, 1.0, 4.0])
def test_route_a_mass_increases_damping(mass):
    """유질량은 감쇠가 빨라진다 (J^(1)_ab ≠ π_ab).  측정: 4.01→4.04→4.34 H."""
    r0 = vd.route_a_damping(0.0)["rate_mean"]
    rm = vd.route_a_damping(mass)["rate_mean"]
    assert rm < r0                            # 더 음수 = 더 빠른 감쇠
    assert abs(rm) > 4.0


def test_route_a_massive_damping_is_anisotropic():
    """유질량은 τ_π 가 스칼라가 아니다 — 성분마다 감쇠율이 다르다 (정직한 한계)."""
    r = vd.route_a_damping(4.0)
    assert r["anisotropy"] > 1e-3, r


# ═══════════════════════════════ 경로 B — PSTF 계층
def test_route_b_handset_is_exactly_minus_four():
    """★ 가장 순수한 경로 B: J^(i)_ab 를 손으로 세팅 — **구적 전혀 미사용**.

    무질량은 i-무관이므로 J^(1)_ab = π_ab ⇒ π̇ = −H[5π − π] = −4Hπ 가 **정확**.
    """
    r = vd.route_b_damping_handset(H_hubble=1.0)
    assert abs(r["rate_mean"] - (-4.0)) < 1e-12, r


def test_route_b_source_is_exactly_minus_8_over_15():
    """경로 B: l=2 σ-소스 계수가 정확히 −8/15 (계수 유리수라 오차 없음)."""
    c = vd.route_b_source(0.0)
    assert abs(c - vd.MASSLESS_SOURCE_COEFF) < 1e-12, c


def test_route_b_requires_anisotropic_a_vec():
    """등방 a_vec 은 π_ab ≡ 0 이라 감쇠율이 정의되지 않는다 → 조용히 넘기지 않고 예외."""
    with pytest.raises(ValueError):
        vd.route_b_damping(0.0, a_vec=(1.0, 1.0, 1.0))


def test_route_b_sigma_zero_closes_exactly():
    """σ=0 이면 (A),(B),(C) 가 모두 사라져 l=2 방정식이 절단 없이 닫힌다.

    귀결: 감쇠율이 l_max 에 무관해야 한다 (l=4 를 넣든 빼든 같다).
    """
    from bianchi.matter import hierarchy as HH
    a = np.array([1.0, 0.85, 1.18])
    J_with = {(l, i): HH.J_moment(a, 0.0, l, i)
              for l in (0, 2, 4) for i in (0, 1, 2, 3)}
    J_without = dict(J_with)
    for i in (0, 1, 2, 3):
        J_without[(4, i)] = np.zeros((3,) * 4)
    d1 = np.asarray(HH.hierarchy_rhs(J_with, 1.0, np.zeros((3, 3)), 2, 0))
    d2 = np.asarray(HH.hierarchy_rhs(J_without, 1.0, np.zeros((3, 3)), 2, 0))
    assert np.abs(d1 - d2).max() < 1e-14


# ═══════════════════════════════ 교차검증 + 유도된 계수
@pytest.mark.parametrize("mass", [0.0, 0.5, 1.0, 4.0])
def test_two_routes_agree(mass):
    """★ 핵심: 서로 독립인 두 경로가 같은 (감쇠, 소스) 를 준다.

    측정 상대차: 감쇠 ~1e−9 (σ=0 에서 방정식이 정확하므로),
                 소스 ~1.5e−3 (구적 급작응답의 차분 한계).
    """
    cv = vd.cross_validate(mass)
    assert cv["agree"], cv
    assert cv["damping_rel_diff"] < 1e-6, cv
    assert cv["source_rel_diff"] < 5e-3, cv


@pytest.mark.parametrize("route", ["hierarchy", "quadrature"])
def test_derived_tau_pi_and_eta(route):
    """★ 유도값: τ_π = 1/(4H), η = ρ/(15H) — 자유 파라미터 없음."""
    tc = vd.transport_coefficients(0.0, H_hubble=1.0, route=route)
    assert abs(tc["tau_pi"] - 0.25) < 1e-6, tc
    assert abs(tc["eta_over_rho_H"] - 1.0 / 15.0) < 5e-4, tc
    assert tc["eta"] > 0                       # 산일적 (2법칙)


def test_eckart_limit_gives_same_eta():
    """Eckart 준정적 극한(π̇→0)이 IS 매칭과 **같은** η 를 준다.

    0 = −4Hπ − (8/15)ρσ ⇒ π = −(2/15)ρσ/H = −2ησ ⇒ η = ρ/(15H).
    """
    rho, Hub = 3.0, 1.5
    eta_eckart = vd.eckart_eta_from_hierarchy(rho, Hub)
    tc = vd.transport_coefficients(0.0, H_hubble=Hub, route="hierarchy")
    assert abs(eta_eckart / rho - tc["eta"] / tc["rho"]) < 1e-6


def test_derived_eta_reproduces_postulated_eckart_form():
    """유도된 η 를 `viscous.eckart_anisotropic_stress` 에 넣으면 계층 준정적해와 일치."""
    Hub = 1.0
    tc = vd.transport_coefficients(0.0, H_hubble=Hub, route="hierarchy")
    Sigma = np.diag([0.05, -0.02, -0.03])          # Hubble 정규화 shear
    # Eckart: Π = -2(η/H)Σ  (viscous.py 규약)
    Pi = vis.eckart_anisotropic_stress(Sigma, tc["eta"] / Hub)
    # 계층 준정적: π = -(2/15)ρ σ/H,  σ = H Σ  ⇒ π = -(2/15)ρΣ
    pi_hier = -(2.0 / 15.0) * tc["rho"] * Sigma
    assert np.abs(Pi - pi_hier).max() < 1e-6 * abs(tc["rho"])


def test_entropy_production_positive():
    """유도된 η > 0 ⇒ T Ṡ = 2η σ² ≥ 0 (열역학 2법칙)."""
    e = vd.entropy_production_is_positive(0.0)
    assert e["positive"]
    assert e["rate"] > 0


def test_relaxation_time_helper():
    assert abs(vd.relaxation_time_massless(2.0) - 1.0 / 8.0) < 1e-15


def test_transport_rejects_unknown_route():
    with pytest.raises(ValueError):
        vd.transport_coefficients(0.0, route="nope")
