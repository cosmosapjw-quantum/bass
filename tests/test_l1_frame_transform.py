"""
L1 · **프레임 변환식과 삼각절단의 홀짝 불변성** — 문헌의 미검증 예측을 시험한다.

원논문은 절단조건 `J = 0 for l+2i > n_*` 가 **n_* 홀수에서만** 프레임 불변이라고
적는다.  계획서가 "아직 시험하지 않았다 — 다음 증분의 1순위" 로 남겨둔 항목이다.

★ 이 파일이 고정하는 측정:
  1. 논문의 변환식 계수 −(3+2i)/3, −(1−2i)/3 가 **정확 구적에서 재현**된다.
  2. ★ 그러나 그 두 항만으로는 **6–8 % 어긋난다** — Bianchi 배경에서는 π_ab 가 0차라
     l=2 항 두 개가 같은 차수로 살아난다.  계수 −2i 와 (2i−1) 을 **측정**했다.
  3. ★★ 홀짝 예측이 **정확히** 확인된다: 누출이 홀수 n_* 에서 0.000e+00,
     짝수에서 1.33 / 1.60 / 1.82.
  4. ★ 그런데 **궤적오차에는 홀짝 계단이 없다** — 순진한 기대의 반증.
     대신 v=0 에서 짝·홀이 **비트 단위로 같고**, tilt 를 켜야 홀수가 낫다.
"""
import numpy as np
import pytest

from bianchi.matter import frame_transform as FT
from bianchi.matter import tilted_integrate as TI
from bianchi.matter import tilted_mass as TMass


# ═══════════════════════════════ 1. 변환식 계수 — 측정으로 확인
@pytest.mark.parametrize("i", [0, 1, 2])
def test_coefficients_refit_matches_hardcoded(i):
    """★ 하드코딩된 계수가 **분포족 최소제곱 재적합**과 일치 (잔차 ~1e−12)."""
    r = FT.fit_coefficients(i)
    t = FT.transform_coefficients(i)
    assert r["residual"] < 1e-9, r
    for k in ("J0_lo", "J0_hi", "J2_lo", "J2_hi"):
        assert abs(r["coef"][k] - t[k]) < 1e-6, (k, r["coef"][k], t[k])


def test_control_sources_are_zero():
    """★ 대조군: 가중 n±3 소스의 계수가 0 (기저가 과적합이 아님)."""
    r = FT.fit_coefficients(2)
    assert abs(r["control"]["J0_n_minus_3"]) < 1e-6, r
    assert abs(r["control"]["J2_n_plus_3"]) < 1e-6, r


def test_paper_coefficients_are_reproduced():
    """★ 논문의 두 계수 −(3+2i)/3, −(1−2i)/3 이 그대로 나온다 (논문이 맞다)."""
    for i in range(4):
        c = FT.transform_coefficients(i)
        assert abs(c["J0_lo"] + (3 + 2 * i) / 3.0) < 1e-15
        assert abs(c["J0_hi"] + (1 - 2 * i) / 3.0) < 1e-15


def test_i_zero_is_the_well_known_result():
    """i=0 은 잘 알려진 q̃ = q − (ρ+p)v − π·v 다 (J^(1) = 3p 이므로)."""
    c = FT.transform_coefficients(0)
    assert abs(c["J0_lo"] + 1.0) < 1e-15          # −3J^(0)/3 = −ρ
    assert abs(c["J0_hi"] + 1.0 / 3.0) < 1e-15    # −J^(1)/3 = −p
    assert abs(c["J2_lo"]) < 1e-15                # l=2 저가중 항 없음
    assert abs(c["J2_hi"] + 1.0) < 1e-15          # −π·v


# ═══════════════════════════════ 2. ★ 두 경로 대조
@pytest.mark.parametrize("mass,i", [(0.0, 0), (1.0, 1), (2.0, 2)])
def test_full_formula_matches_exact_quadrature(mass, i):
    """★★ 측정된 4항 변환식이 boosted 정확 구적과 1e−9 이내로 일치."""
    r = FT.transform_residual(mass=mass, i=i)
    assert r["residual"] < 1e-8, r


@pytest.mark.parametrize("mass,i", [(0.0, 0), (1.0, 1), (2.0, 2)])
def test_paper_two_terms_alone_are_insufficient_here(mass, i):
    """★★ **논문 두 항만** 쓰면 6–8 % 어긋난다 — l=2 항이 필요한 이유를 정량화.

    논문이 틀린 게 아니다: 선형섭동론에서는 π_ab 가 1차라 π·v 가 2차로 떨어진다.
    Bianchi 배경에서는 π_ab 가 **0차**라 같은 차수로 살아난다.
    """
    r = FT.paper_only_residual(mass=mass, i=i)
    assert r["residual"] > 1e-2, r


def test_isotropic_background_restores_the_paper_formula():
    """★ 등방 a_vec 이면 π = 0 이므로 논문 두 항으로 **충분**하다 (경계 확인)."""
    r = FT.paper_only_residual(a_vec=(1.0, 1.0, 1.0), mass=1.0, i=1)
    assert r["residual"] < 1e-8, r


# ═══════════════════════════════ 3. ★★ 홀짝 프레임 불변성
@pytest.mark.parametrize("n_star", [3, 5, 7])
def test_odd_n_star_leaks_nothing(n_star):
    """★★ 홀수 n_* 에서 누출이 **정확히 0** — 문헌 예측 확인."""
    r = FT.truncation_leakage(n_star)
    assert r["leak"] == 0.0, r
    assert r["retained_sources"] == [], r


@pytest.mark.parametrize("n_star", [2, 4, 6])
def test_even_n_star_leaks_order_one(n_star):
    """★★ 짝수 n_* 에서 누출이 O(1) (측정 1.33 / 1.60 / 1.82)."""
    r = FT.truncation_leakage(n_star)
    assert r["leak"] > 1.0, r
    assert r["retained_sources"], r


def test_parity_table_alternates():
    """★ 표 전체가 홀짝으로 갈린다 (우연이 아님)."""
    rows = FT.parity_table()
    for n, leak in rows:
        if n % 2:
            assert leak == 0.0, (n, leak)
        else:
            assert leak > 1.0, (n, leak)


def test_leakage_mechanism_is_the_retained_source():
    """★ 짝수에서 새는 이유가 **가중 n_* 소스가 남아 있어서**임을 확인."""
    r = FT.truncation_leakage(4)
    i, kept = r["retained_sources"][0]
    assert 1 + 2 * i == 5, r                     # 절단을 넘는 최소 l=1 가중
    assert set(kept) == {"J0_lo", "J2_lo"}, r    # 가중 4 = n_* 인 두 소스


# ═══════════════════════════════ 4. 삼각 절단 구현
def test_triangular_layout_filters_by_total_weight():
    keys, _, n = TMass.layout(4, 3, n_star=4)
    assert all(l + 2 * i <= 4 for l, i in keys), keys
    assert (0, 2) in keys and (2, 1) in keys
    assert (1, 2) not in keys and (3, 1) not in keys


def test_rectangular_path_is_unchanged():
    """★ 회귀: n_star=None 이면 옛 배치·행렬과 **정확히** 같다."""
    from bianchi.matter import tilted_terms as TT
    a, b, c = TMass.layout(3, 2), TMass.layout(3, 2, None), TMass.layout(3, 2, 99)
    assert a[0] == b[0] == c[0]
    geo = TT.geometry((1.0, 0.9, 1.2), (0.35, 0.28, 0.42), (0.08, -0.05, 0.12),
                      (0.015, 0.01, -0.02))
    assert np.abs(TMass.dense(geo, 3, 2) - TMass.dense(geo, 3, 2, None, None, None)).max() == 0.0


def test_triangular_integration_converges_in_n_star():
    """삼각 절단 궤적오차가 n_* 로 수렴한다 (2→6 에서 20배)."""
    bg = TI.Background()
    e2 = max(TI.trajectory_error(bg, 1.0, 0.2, 20, 2, 1, n_star=2).values())
    e6 = max(TI.trajectory_error(bg, 1.0, 0.2, 20, 4, 3, n_star=6).values())
    assert e6 < e2 / 10.0, (e2, e6)


# ═══════════════════════════════ 5. ★ 궤적에서의 홀짝 — 순진한 기대의 반증
def test_zero_tilt_makes_even_and_odd_identical():
    """★★ v = 0 에서 n_*=4 와 5 가 **비트 단위로 같다** (상대차 0.000e+00).

    법선틀에서는 홀수 l 이 항등적으로 0 이라 가중 n_*+1 상태가 아무것도 안 한다.
    ⇒ 홀짝 차이는 **오직 tilt 를 켤 때만** 나타난다 — 그게 '프레임' 불변성이니 당연하다.
    """
    r = FT.zero_tilt_parity_degeneracy(4)
    assert r["gap"] == 0.0, r


def test_naive_staircase_in_trajectory_error_is_falsified():
    """★ **반증 기록**: 궤적오차만 보면 홀짝 계단이 없고 n_* 수렴만 보인다.

    측정 (m=1, T=0.2, tilt 기본):
        n_* = 2,3,4,5,6,7 → 1.4e−2, 1.5e−2, 3.0e−3, 2.5e−3, 6.9e−4, 5.4e−4
    n_*=2→3 에서는 오히려 나빠지는 성분도 있다.  "홀수가 뚜렷이 정확할 것" 이라는
    계획서의 기대는 **이 형태로는 틀렸다**.
    """
    bg = TI.Background()
    e2 = max(TI.trajectory_error(bg, 1.0, 0.2, 20, 2, 1, n_star=2).values())
    e3 = max(TI.trajectory_error(bg, 1.0, 0.2, 20, 3, 1, n_star=3).values())
    assert e3 > 0.5 * e2, (e2, e3)          # 계단이라면 훨씬 작아야 했다


def test_odd_is_better_only_once_the_frame_is_tilted():
    """★★ 올바른 형태의 확인: **tilt 를 켜면** 홀수가 인접 짝수보다 낫다.

    측정 (v=0.15): n_*=4 → 3.87e−3 vs n_*=5 → 2.61e−3 (1.5배),
                   오염비 +0.34 (짝) vs −0.10 (홀).
    """
    rows = dict((n, (e0, ev, c)) for n, e0, ev, c in
                FT.parity_trajectory_table((4, 5), mass=1.0, v_mag=0.15))
    assert abs(rows[4][0] - rows[5][0]) < 1e-14 * rows[4][0]   # v=0 은 동일
    assert rows[5][1] < rows[4][1], rows                        # tilt 에서 홀수가 낫다
    assert rows[4][2] > rows[5][2], rows                        # 오염비도 짝수가 크다
