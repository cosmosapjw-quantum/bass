"""
H3 · Thomson 충돌항 시험 — 무충돌 계층을 진짜 Boltzmann 계층으로.

★ **두 경로를 분리**해 시험한다 (H4 와는 나누는 방식이 다르다):
    경로 A: Thomson 위상함수 K(μ)∝(1+μ²) 를 각격자에서 **직접 적분** → λ_l 측정
            (다극 대수 미사용)
    경로 B: Legendre 전개에서 λ_l = 4π k_l/(2l+1) **해석값** (적분 미사용)

★ 정직한 한계: `freestream.py` 정확 구적은 충돌항을 검증할 수 **없다** — 충돌이
  자유흐름 특성곡선을 깨뜨리므로.  그래서 H4 처럼 "구적 vs 계층" 으로 나눌 수 없다.
"""
import numpy as np
import pytest

from bianchi.matter import collision as C
from bianchi.matter import hierarchy as H


# ═══════════════════════════════ 경로 A — 수치 위상함수
@pytest.mark.parametrize("l,expected", [(0, 1.0), (1, 0.0), (2, 0.1), (3, 0.0), (4, 0.0)])
def test_route_a_numeric_eigenvalues(l, expected):
    """★ 경로 A: 위상함수 각적분이 λ_l 을 준다.  다극 대수를 쓰지 않은 측정."""
    lam = C.thomson_eigenvalue_numeric(l)
    assert abs(lam - expected) < 1e-12, (l, lam)


def test_route_a_l2_damping_is_9_over_10():
    """★ 경로 A 만으로 표준 Thomson 사중극 인자 **9/10** 이 나온다."""
    assert abs(C.thomson_damping_numeric(2) - 0.9) < 1e-12


def test_route_a_phase_function_is_normalised():
    """K̃(μ)=(3/8)(1+μ²) 의 적분이 1 (광자 수 보존의 전제)."""
    assert abs(C.thomson_eigenvalue_numeric(0) - 1.0) < 1e-12


# ═══════════════════════════════ 경로 B — 해석 다극
@pytest.mark.parametrize("l,expected", [(0, 1.0), (1, 0.0), (2, 0.1), (5, 0.0)])
def test_route_b_analytic_eigenvalues(l, expected):
    """경로 B: λ_l = 4π k_l/(2l+1) 해석값 (적분 미사용)."""
    assert C.thomson_eigenvalue(l) == expected


def test_route_b_damping_pattern():
    """감쇠 (1-λ_l): l=0 → 0 (수 보존), l=2 → 9/10, 나머지 → 1."""
    assert C.thomson_damping(0) == 0.0
    assert abs(C.thomson_damping(2) - 0.9) < 1e-15
    for l in (1, 3, 4, 6):
        assert C.thomson_damping(l) == 1.0


# ═══════════════════════════════ 교차검증
def test_two_routes_agree_on_eigenvalues():
    """★ 핵심: 수치 위상함수 적분과 해석 다극값이 일치 (측정 8.8e−15)."""
    worst = max(abs(C.thomson_eigenvalue_numeric(l) - C.thomson_eigenvalue(l))
                for l in range(7))
    assert worst < 1e-12, worst


def test_collision_term_route_consistency():
    """충돌항이 두 route 옵션에서 같은 값 (같은 λ_l 을 쓰므로)."""
    J = {(2, 0): np.diag([0.1, -0.04, -0.06])}
    a = C.collision_term(J, 2, 0, 1.5, route="analytic")
    b = C.collision_term(J, 2, 0, 1.5, route="numeric")
    assert np.abs(a - b).max() < 1e-12


# ═══════════════════════════════ 물리 게이트
def test_free_streaming_limit_is_exact():
    """★ n_e σ_T = 0 이면 무충돌 RHS 와 **정확히** 같다 (H1/H2 회귀 보호)."""
    assert C.free_streaming_limit_residual() == 0.0


def test_photon_number_conserved():
    """Thomson 은 광자 수를 보존 ⇒ l=0 충돌항이 정확히 0."""
    J = {(0, 0): 7.5}
    assert C.photon_number_is_conserved(J, n_e_sigma_T=3.0) == 0.0


def test_collision_damps_l2_and_higher():
    """l≥1 은 감쇠, l=0 은 불변 (부호와 크기)."""
    pi = np.diag([0.1, -0.04, -0.06])
    J = {(0, 0): 1.0, (2, 0): pi, (3, 0): np.ones((3, 3, 3)) * 0.01}
    c0 = C.collision_term(J, 0, 0, 2.0)
    c2 = C.collision_term(J, 2, 0, 2.0)
    c3 = C.collision_term(J, 3, 0, 2.0)
    assert np.abs(np.atleast_1d(c0)).max() == 0.0
    # π 와 반대부호 (감쇠), 크기 = n_eσ_T · 0.9 · |π|
    assert np.allclose(c2, -2.0 * 0.9 * pi)
    assert np.allclose(c3, -2.0 * 1.0 * J[(3, 0)])


@pytest.mark.parametrize("rate", [1e2, 1e3, 1e4])
def test_tight_coupling_drives_pi_to_zero(rate):
    """★ 긴밀결합 극한: π_ab 준정적값이 1/(n_eσ_T) 로 감소 (완전유체화)."""
    t = C.tight_coupling_residual(n_e_sigma_T=rate)
    assert t["pi_quasi_static_over_rho"] < 1e-3
    # 1/rate 스케일링 확인 (측정: 2.84e-4 → 2.95e-5 → 2.96e-6)
    assert t["pi_quasi_static_over_rho"] * rate < 1.0


def test_tight_coupling_scaling_is_inverse_rate():
    """π/ρ ∝ 1/(n_eσ_T) — 완전유체 극한의 정량 확인."""
    lo = C.tight_coupling_residual(n_e_sigma_T=1e3)["pi_quasi_static_over_rho"]
    hi = C.tight_coupling_residual(n_e_sigma_T=1e4)["pi_quasi_static_over_rho"]
    assert 8.0 < lo / hi < 12.0                # 10배 rate → 약 10배 감소


# ═══════════════════════════════ 유도: Thomson 점성
def test_thomson_viscosity_with_9_10_is_8_over_27():
    """9/10 포함 시 η·n_eσ_T/ρ = **8/27** (H4 매칭 + Thomson 사중극)."""
    r = C.thomson_viscosity(1.0, 1e4, 0.0, include_thomson_9_10=True)
    assert abs(r["eta_times_nesigT_over_rho"] - 8.0 / 27.0) < 1e-9


def test_thomson_viscosity_without_9_10_is_4_over_15():
    """9/10 미포함 시 **4/15** — 문헌에서 흔히 인용되는 값.

    두 값의 비가 정확히 10/9 이며, **차이의 전부가 9/10 인자**다.
    어느 쪽이 맞다고 단정하지 않고 플래그로 노출한다 (문헌 관례가 갈림).
    """
    r = C.thomson_viscosity(1.0, 1e4, 0.0, include_thomson_9_10=False)
    assert abs(r["eta_times_nesigT_over_rho"] - 4.0 / 15.0) < 1e-9
    with_910 = C.thomson_viscosity(1.0, 1e4, 0.0, True)["eta_times_nesigT_over_rho"]
    assert abs(with_910 / r["eta_times_nesigT_over_rho"] - 10.0 / 9.0) < 1e-9


def test_viscosity_reduces_to_collisionless_when_rate_zero():
    """n_eσ_T → 0 이면 H4 의 무충돌값 τ_π = 1/(4H), η = ρ/(15H) 로 환원."""
    r = C.thomson_viscosity(1.0, 0.0, 1.0, include_thomson_9_10=True)
    assert abs(r["tau_pi"] - 0.25) < 1e-12
    assert abs(r["eta"] - 1.0 / 15.0) < 1e-12


def test_collisional_rhs_matches_free_plus_collision():
    """충돌 RHS = 무충돌 RHS + 충돌항 (분해 가능성 확인)."""
    a = np.array([1.0, 0.85, 1.18])
    sig = np.diag([0.05, -0.02, -0.03])
    J = {(l, i): H.J_moment(a, 0.0, l, i) for l in (0, 2, 4) for i in (0, 1, 2, 3)}
    rate = 3.0
    tot = np.asarray(C.hierarchy_rhs_collisional(J, 1.0, sig, 2, 0, rate), float)
    free = np.asarray(H.hierarchy_rhs(J, 1.0, sig, 2, 0), float)
    coll = np.asarray(C.collision_term(J, 2, 0, rate), float)
    assert np.abs(tot - (free + coll)).max() < 1e-14
