"""
K4c · **type V boosted 모멘트** — tilt 를 켠 자유흐름 오라클.

K4a/b 가 type V 자유흐름 모멘트를 세웠다.  여기서 tilt 를 켠다.  H5-d 가 type I 에
한 것과 구조는 같고 **딱 한 군데가 다르다**: 격자에서 f 값을 얻을 때 type I 은
f₀(q) 를 바로 읽지만 type V 는 **역방향 특성곡선**으로 t=0 까지 거슬러야 한다.

★ 이 파일이 고정하는 측정:
  · v = 0 에서 K4b 와 **비트-정확** (0.000e+00)
  · A → 0 에서 H5-d 의 type I boosted 구적과 **2.17e−16** — 두 오라클이 만난다
  · ★★ T^{μν} 프레임 무관성 **1.9e−15** (계층을 전혀 안 쓰는 가장 결정적 게이트)

★★ 그리고 물리 결과 하나: **type V 자유흐름은 법선틀 열유속을 스스로 만든다.**
  등방 f₀(|p|) 로 출발해도 특성곡선이 p₁ 의 홀짝 대칭을 깬다.
      t = 0, 0.1, 0.2, 0.35, 0.5  →  |q|/ρ = 0, 1.5e−3, 3.3e−3, 6.3e−3, 9.5e−3
      A = 0 이면 정확히 0 (2.7e−17) 이고, A 에 대해 거의 선형
  ⇒ K2b 가 "type V 는 tilt 를 담을 수 있다" 고 한 자리가 **실제로 채워진다**.

★ 이 발견은 **게이트 실패에서 나왔다**: 처음에 `tilted_moments.project_stress_to_tilted`
  를 그대로 썼다가 프레임 게이트가 1e−3 에서 멈췄다.  그 함수는 법선틀 q = 0 을
  가정한다 (type I 등방 f₀ 에서는 홀수 l 이 항등적으로 0 이라 옳다).  진단 필드
  `normal_flux = 6.3e−3` 이 원인을 가리켰다.
"""
import numpy as np
import pytest

from bianchi.matter import type_v as TV


# ═══════════════════════════════ 1. 환원 게이트
def test_zero_tilt_is_bit_exact():
    """★ v = 0 이면 K4b 와 **비트-정확** (E′=E, P′=P 이라 피적분함수가 문자 그대로 동일)."""
    assert TV.tilted_v_zero_residual() == 0.0


@pytest.mark.parametrize("mass", [0.0, 0.6, 2.0])
def test_A_zero_matches_type_I_boosted_quadrature(mass):
    """★★ A → 0 에서 H5-d 의 type I boosted 구적과 일치 (2.2e−16).

    두 독립 오라클(역방향 특성곡선 vs 닫힌형 1/a 적색이동)이 만나는 지점.
    """
    assert TV.type_I_boosted_residual(mass=mass) < 1e-13


# ═══════════════════════════════ 2. ★★ 프레임 무관성
@pytest.mark.parametrize("v", [(0.15, -0.1, 0.2), (0.0, 0.0, 0.3), (-0.2, 0.05, 0.1)])
def test_stress_tensor_is_frame_independent(v):
    """★★ **가장 결정적인 게이트** — 계층을 전혀 쓰지 않는다.

    법선틀 (ρ, q, p, π) 로 T^{μν} 를 세워 tilted 사틀로 사영한 값이 boosted 구적이
    직접 준 값과 1.9e−15 로 일치.  특성곡선·측도·boost 를 한 번에 검증한다.
    """
    r = TV.frame_independence_residual_type_V(v=v)
    assert max(r["rho"], r["p"], r["q"], r["pi"]) < 1e-12, r


def test_the_flux_term_is_required_in_the_projection():
    """★ **게이트 실패에서 배운 것**: 법선틀 q 를 빼면 프레임 게이트가 깨진다.

    `tilted_moments.project_stress_to_tilted` 는 q = 0 을 가정하므로 type V 에는
    쓸 수 없다 (그걸로 재면 잔차가 1e−3 에서 멈춘다).
    """
    from bianchi.matter import tilted_moments as TM
    bg = TV.Background(A=0.7)
    n = TV.moments_type_V(bg, 0.6, 0.35, 2, 1)
    rho, p = float(n[(0, 0)]), float(n[(0, 1)]) / 3.0
    pi = np.asarray(n[(2, 0)], float)
    q = np.asarray(n[(1, 0)], float)
    v = (0.15, -0.1, 0.2)
    good = TV.project_stress_with_flux(rho, p, q, pi, v)
    bad = TM.project_stress_to_tilted(rho, p, pi, v)          # q 를 빠뜨린 판
    assert np.abs(np.asarray(good[2]) - np.asarray(bad[2])).max() / rho > 1e-4


# ═══════════════════════════════ 3. ★★ 자발적 열유속 (물리 결과)
def test_flux_is_zero_at_t_zero():
    """★ t = 0 은 등방 f₀ 라 q = 0 (2.7e−17) — 유속이 **자유흐름으로 생긴다**."""
    assert TV.flux_vanishes_at_t_zero() < 1e-14


def test_flux_grows_with_time():
    """★★ |q|/ρ 가 0 → 1.5e−3 → 3.3e−3 → 6.3e−3 → 9.5e−3 으로 자란다."""
    rows = TV.flux_growth()
    assert rows[0][1] < 1e-14, rows
    assert all(b[1] > a[1] for a, b in zip(rows, rows[1:])), rows
    assert rows[-1][1] > 5e-3, rows


def test_flux_vanishes_when_A_is_zero():
    """★ 대조군: A = 0 (type I) 이면 유속이 **정확히** 0 — 원인이 A 임을 확정."""
    rows = [(m, A, q) for m, A, q in TV.spontaneous_flux() if A == 0.0]
    assert all(q < 1e-14 for _, _, q in rows), rows


def test_flux_is_essentially_linear_in_A():
    """★ |q|/ρ 가 A 에 거의 선형 (A = 0.2/0.4/0.7 → 1.95/3.88/6.67 e−3)."""
    rows = [(A, q) for m, A, q in TV.spontaneous_flux(masses=(0.0,)) if A > 0]
    A = np.array([r[0] for r in rows], float)
    q = np.array([r[1] for r in rows], float)
    p = np.polyfit(np.log(A), np.log(q), 1)[0]
    assert 0.9 < p < 1.05, (rows, p)


def test_heavier_matter_makes_less_flux():
    """유질량일수록 유속이 작다 (m=0 → 6.67e−3, m=2 → 4.39e−3)."""
    at07 = {m: q for m, A, q in TV.spontaneous_flux(As=(0.7,))}
    assert at07[0.0] > at07[0.6] > at07[2.0], at07


# ═══════════════════════════════ 4. K2b 가 연 자리에 물질을 넣는다
#
# ★ 정정 (K5a, 34차): 여기 있던 두 시험은 `self_consistent_A` (확장정규화 판) 를
#   썼는데, 그 함수의 규격화 인자(q/3H² 등)가 불확실해 "넣은 A 와 20배 차이" 라는
#   과장된 수를 냈다.  K5a 가 계량에서 Codazzi 를 확정했으므로
#   **물리 단위** 판(`self_consistent_a_physical`)으로 교체한다.  물리 단위로는
#   차이가 O(1) 이다 — 물리가 아니라 정규화가 문제였다.
def test_codazzi_can_absorb_the_spontaneous_flux():
    """★★ 자발적 q 를 담는 a₁ 이 존재하고, 크기가 배경과 **같은 자릿수**다.

    K2b 는 임의로 준 q 로 구성적 해를 보였는데, 이번엔 **실제 물질에서 나온** q 다.
    """
    r = TV.self_consistent_a_physical()
    assert abs(r["q1"]) > 1e-3, r
    assert 0.2 < abs(r["ratio"]) < 5.0, r


def test_prescribed_background_is_not_yet_an_einstein_solution():
    """★ **정직한 한계**: 필요한 a₁ 과 배경이 준 a₁ 의 **부호가 다르다**.

    크기는 O(1) 이라 물리적으로 가깝지만, σ₁ 의 부호가 정합 여부를 정한다.
    자기정합 해를 얻으려면 고정점을 풀어야 한다 (K5a 의 `solve_self_consistent_shear`).
    """
    r = TV.self_consistent_a_physical(t=0.35)
    assert r["ratio"] < 0, r
    assert r["a1_actual"] < 0 < r["a1_needed"], r
