"""
V2b+V2c · **움직이는 전자**의 Thomson 충돌항 — 부채 두 개를 함께 갚는다.

1. `collision.py` docstring 이 약속만 하고 **구현이 없던** `dipole_source`
   (광자–바리온 항력).  계수 4/3 을 **인용하지 않고 측정**했다.
2. V2a 가 전자 정지틀만 검증했다는 한계 (tilted 배경에서는 전자가 움직인다).

★ 구성: Thomson 이 **전자 정지틀에서 탄성**이라는 사실만 쓰고, 나머지는 boost 다.
  새 물리 입력이 없으므로 V2a 의 위상함수를 그대로 재사용해도 순환이 아니다.

★ 이 파일이 고정하는 측정:
  · boost 왕복 4e−16, v=0 에서 V2a 로 환원 4e−16
  · 정지틀 등방 분포는 산란으로 불변 (8.9e−16)  ← 그리고 이 게이트가 **무엇에**
    민감한지도 함께 고정한다 (규격화에 둔감, boost 에 민감)
  · 쌍극 원천 계수 c = 4/3 (편차 ∝ v_e²)
  · 광자수 보존 3e−13, 에너지는 보존되지 않음 (Doppler) — **구별해서** 잰다
  · l=2 감쇠는 v_e 1차에서 안 변한다 (편차 ∝ v_e²)
"""
import numpy as np
import pytest

from bianchi.matter import collision as C
from bianchi.matter import collision_moving as CM


# ═══════════════════════════════ 0. boost 자기검증
def test_boost_selfcheck():
    """|n̂′| = 1, 역boost 왕복, λ′ > 0 (4e−16)."""
    r = CM.boost_selfcheck()
    assert r["unit"] < 1e-14, r
    assert r["roundtrip_lam"] < 1e-14, r
    assert r["roundtrip_dir"] < 1e-14, r
    assert r["lam_positive"]


def test_superluminal_velocity_is_rejected():
    with pytest.raises(ValueError):
        CM.boost_photon(np.ones(3), np.eye(3), (0.9, 0.9, 0.0))


# ═══════════════════════════════ 1. ★ v=0 환원
def test_static_limit_reduces_to_v2a():
    """★ 전자가 정지하면 V2a 의 순수 각산란과 **같아진다** (4e−16).

    두 코드 경로가 전혀 다르다 (boost 조립 vs 격자 행렬) — 일치가 의미 있다.
    """
    assert CM.static_limit_residual() < 1e-13


# ═══════════════════════════════ 2. ★★ 평형 오라클과 그 민감도
def test_rest_frame_isotropic_distribution_is_unchanged():
    """★★ 정지틀 등방 분포는 Thomson 산란의 **정확한 평형해** (8.9e−16)."""
    assert CM.equilibrium_residual()["residual"] < 1e-13


def test_the_equilibrium_gate_is_insensitive_to_overall_normalisation():
    """★ **정직성 고정**: 첫 대조군은 아무것도 잡지 못했다.

    위상함수에 0.1 % 상수배를 걸어도 잔차가 8.95e−16 로 그대로다 —
    같은 상수로 나눈 행합으로 규격화하므로 상쇄된다.
    이 둔감성을 시험으로 남겨 "게이트가 살아 있다" 고 오인하지 않게 한다.
    (전체 규격화는 V2a 의 `phase_norm` 이 따로 잰다.)
    """
    assert CM.normalisation_control_is_vacuous() < 1e-13


def test_the_equilibrium_gate_does_bite_on_the_boost():
    """★ 실제로 무는 대조군: 되돌리는 boost 를 0.1 % 어긋내면 1.5e7 배 나빠진다."""
    r = CM.boost_control_residual()
    assert r["good"] < 1e-13, r
    assert r["broken"] > 1e-10, r
    assert r["ratio"] > 1e5, r


def test_phase_normalisation_is_direction_independent():
    """규격화가 입사방향과 무관 (격자 밖 n̂′ 200개에서 스프레드 1.7e−16).

    `collision_rate_density` 가 격자행 평균으로 규격화하므로 필요한 성질이다.
    """
    r = CM.phase_norm_is_direction_independent()
    assert r["spread"] < 1e-14, r
    assert r["offset"] < 1e-14, r


# ═══════════════════════════════ 3. ★★ V2b — 쌍극 원천 계수를 측정한다
def test_dipole_source_coefficient_is_four_thirds():
    """★★ q̇_a = −τ̇[q_a − c ρ v_{e,a}] 의 **c = 4/3** (측정, 인용 아님).

    |v_e| = 1e−4 에서 1.333333354 — 4/3 과의 차이가 2.1e−8 ≈ 2v_e².
    """
    r = CM.dipole_source_coefficient(1e-4)
    assert abs(r["c"] - 4.0 / 3.0) < 1e-6, r


def test_dipole_source_is_linear_in_ve():
    """★ 편차가 v_e² 로 간다 — 원천이 v_e **1차**임을 뜻한다."""
    rows = CM.linearity_in_ve()
    dev = [(m, abs(c - 4.0 / 3.0)) for m, c in rows]
    # v 를 30배 키우면 편차가 ~900배
    r0, r1 = dev[0], dev[-1]
    ratio = (r1[1] / r0[1]) / (r1[0] / r0[0]) ** 2
    assert 0.5 < ratio < 2.0, (dev, ratio)


def test_collision_module_now_has_the_promised_dipole_source():
    """★ H3 docstring 이 약속만 하고 없던 `dipole_source` 가 실제로 있다."""
    assert hasattr(C, "dipole_source")
    q = C.dipole_source(3.0, (0.0, 0.0, 0.1), 2.0)
    assert abs(q[2] - 2.0 * (4.0 / 3.0) * 3.0 * 0.1) < 1e-14


def test_collision_term_adds_the_source_only_at_l_equals_one():
    """v_e 를 줘도 l ≠ 1 은 옛 거동 그대로 (회귀)."""
    J = {(0, 0): 2.0, (1, 0): np.array([0.1, 0.0, 0.0]),
         (2, 0): np.eye(3) * 0.05}
    ve = (0.0, 0.0, 0.02)
    for l in (0, 2):
        a = np.asarray(C.collision_term(J, l, 0, 1.0), float)
        b = np.asarray(C.collision_term(J, l, 0, 1.0, v_e=ve), float)
        assert np.abs(a - b).max() == 0.0
    a = np.asarray(C.collision_term(J, 1, 0, 1.0), float)
    b = np.asarray(C.collision_term(J, 1, 0, 1.0, v_e=ve), float)
    assert abs((b - a)[2] - (4.0 / 3.0) * 2.0 * 0.02) < 1e-14


# ═══════════════════════════════ 4. 보존량 — 광자수와 에너지를 구별한다
def test_photon_number_conserved_but_energy_is_not():
    """★ Thomson 은 **광자 수**를 보존한다 (3e−13).  에너지는 Doppler 로 바뀐다.

    둘을 뭉뚱그리면 '보존이 깨졌다' 고 오독하게 된다 — 구별해서 잰다.
    """
    r = CM.photon_number_rate()
    assert abs(r["ndot_over_n"]) < 1e-10, r
    assert abs(r["rhodot_over_rho"]) > 1e-5, r          # 실제로 변한다


def test_static_electrons_conserve_both():
    """전자가 정지하면 에너지도 보존된다 (탄성)."""
    r = CM.photon_number_rate(v=(0.0, 0.0, 0.0))
    assert abs(r["ndot_over_n"]) < 1e-14, r
    assert abs(r["rhodot_over_rho"]) < 1e-14, r


# ═══════════════════════════════ 5. V2c — tilted 프레임에서 l=2
def test_quadrupole_damping_has_no_first_order_ve_correction():
    """★ l=2 감쇠 9/10 은 전자속도의 **1차에서 변하지 않는다** (편차 ∝ v_e²).

    측정: v_e=0 → −0.900000000000,  1e−3 → −0.900008,  1e−2 → −0.900831.
    ⇒ 계층이 π 감쇠에 v_e 보정을 넣지 않는 것이 1차까지 정당하다.
    """
    rows = CM.quadrupole_damping_vs_ve()
    assert abs(rows[0][1] + 0.9) < 1e-12, rows
    dev = [(v, abs(d + 0.9)) for v, d in rows[1:]]
    ratio = (dev[-1][1] / dev[0][1]) / (dev[-1][0] / dev[0][0]) ** 2
    assert 0.5 < ratio < 2.0, (dev, ratio)
