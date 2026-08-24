"""
L3 · **유질량 tilted 정확도** — 계획이 "측정된 적이 없다" 고 적어둔 항목.

측정 → 진단 → 고침 순서로 진행했고, **중간에 자연스러운 기대 하나가 반증**됐다.

1) 측정: 유질량에서도 지배 오차는 **i-닫힘**이다 (l 은 이미 포화).
2) 구조: i-탑은 x=(λ′/E′)² 의 Hausdorff 모멘트열이라 비 r_i 가 **단조 증가**한다.
   기존 닫힘은 r 을 얼려서 구조적으로 과소평가한다.
3) ★ 반증: 그런데 **J 닫힘을 정확하게 만들어도 궤적은 좋아지지 않는다** —
   격자 밖 J 를 *정확 구적*으로 채워 넣어도 오히려 나빠졌다 (π 7배).
4) ★★ 진짜 원인: 격자 밖 **J̇** 만 버리고 있었다.  J 는 닫으면서 J̇ 은 0 이니
   **닫힘이 J 와 J̇ 사이에서 어긋나** 있었다.  같은 비로 J̇ 도 닫으면 무질량에서
   1차원 환원과 **비트 단위로 같은 답**이 나온다 (= 1차원 환원은 r=1 특수경우).
"""
import numpy as np
import pytest

from bianchi.matter import tilted_closure as TC
from bianchi.matter import tilted_integrate as TI


@pytest.fixture(scope="module")
def bg():
    return TI.Background()


# ═══════════════════════════════ 1. 구조: Hausdorff 모멘트열
@pytest.mark.parametrize("l", [0, 1, 2])
def test_massless_ratio_sequence_is_exactly_one(l):
    """무질량은 λ′=E′ 이라 x≡1 — 모든 비가 정확히 1 (축퇴)."""
    r = TC.exact_ratio_sequence(0.0, l=l, i_max=4)
    assert max(abs(x - 1.0) for x in r) < 1e-12, r


@pytest.mark.parametrize("mass,l", [(0.5, 0), (1.0, 0), (2.0, 1), (4.0, 2)])
def test_massive_ratio_sequence_increases_toward_one(mass, l):
    """★ r_i = J^(i+1)/J^(i) 가 **단조 증가**하고 1 을 넘지 않는다.

    x ∈ [0,1] 위의 모멘트열이므로 큰 i 일수록 x≈1 쪽이 지배한다.
    측정 (m=4, l=0): 0.4068 → 0.5269 → 0.5996 → 0.6487 → 0.6844.
    ⇒ **비를 얼리는 닫힘은 구조적으로 과소평가**한다.
    """
    r = TC.exact_ratio_sequence(mass, l=l, i_max=4)
    assert all(b > a - 1e-12 for a, b in zip(r, r[1:])), r
    assert all(0.0 < x <= 1.0 + 1e-12 for x in r), r
    assert r[-1] > r[0]


# ═══════════════════════════════ 2. 닫힘 자체의 예측오차 (ODE 없이)
@pytest.mark.parametrize("mass,l", [(0.5, 0), (1.0, 1), (2.0, 2), (4.0, 0)])
def test_ratio_closure_predicts_better_than_frozen(mass, l):
    """★ (1−r) 기하외삽이 얼린 비보다 **3–8배** 정확하다 (적분과 분리해서 측정)."""
    f = TC.closure_prediction_error(mass, l, 2, "frozen")
    r = TC.closure_prediction_error(mass, l, 2, "ratio")
    assert r["e1"] < f["e1"] / 2.0, (f, r)
    assert r["e2"] < f["e2"] / 2.0, (f, r)


def test_ratio_closure_is_exact_for_massless():
    """무질량은 r≡1 이라 어느 모드든 **정확**해야 한다 (축퇴 보존)."""
    for mode in ("frozen", "ratio", "ratio_scalar"):
        e = TC.closure_prediction_error(0.0, 0, 2, mode)
        assert e["e1"] < 1e-12 and e["e2"] < 1e-12, (mode, e)


def test_zero_mode_is_a_control_that_breaks_massless():
    """대조군: 0 절단은 무질량 축퇴를 통째로 깬다 (닫힘이 필요한 이유)."""
    e = TC.closure_prediction_error(0.0, 0, 2, "zero")
    assert e["e1"] > 0.1, e


# ═══════════════════════════════ 3. ★ 반증: J 를 정확히 채워도 소용없다
def test_exact_J_closure_does_not_help(bg):
    """★★ 자연스러운 기대의 **반증**.

    격자 밖 J 를 정확 구적으로 채우면 좋아질 것 같지만, 측정하면
    ρ 4.8e−5 → 8.1e−5, π 2.3e−4 → 1.6e−3 으로 **나빠진다**.
    방정식 안에서 J 항과 J̇ 항이 상당부분 상쇄하기 때문에, 한쪽만 정확하게 만들면
    균형이 깨진다 — **정확성보다 일관성**이 먼저다.
    """
    r = TI.oracle_closure_experiment(bg, mass=1.0, nsteps=10, l_max=2, i_max=2)
    assert r["exact_J"]["pi"] > 3.0 * r["baseline"]["pi"], r
    assert r["jdot"]["pi"] < r["baseline"]["pi"], r
    assert r["jdot"]["q"] < r["baseline"]["q"], r


# ═══════════════════════════════ 4. ★★ J̇ 닫힘 = 1차원 환원의 일반화
def test_jdot_closure_reproduces_the_1d_reduction_bit_for_bit(bg):
    """★★ 무질량에서 2차원 격자 + J̇ 닫힘(r=1) 이 1차원 환원과 **같은 답**.

    코드 경로가 전혀 다르다 (하나는 (l,i) 격자 + 질량행렬, 다른 하나는 J_l 로 접은
    축소계).  일치는 "1차원 환원 = J̇ 닫힘의 r=1 특수경우" 를 뜻한다.
    ★ **정정 (R3, 39차)**: 기본 설정에서 상대차가 오래 **정확히 0.0** 이었는데,
      `hierarchy.pstf` 를 고정 행렬로 굳히면서 그 동률이 깨졌다.  원인은 이분법으로
      확정했다 (pstf 만 바꾼 트리 1.21e−13, tilted_mass 만 바꾼 트리 0.0).

      비트-일치는 **수학적 항등식이 아니라 연산 순서가 같아서** 생긴 것이었다:
      옛 판은 l! 개 전치의 평균을 루프로 더한 뒤 lstsq 를 돌았고, 새 판은 같은
      직교사영을 행렬곱 한 번으로 한다 — 반올림이 다르다.

      물리 주장은 그대로다: 두 경로의 오차값이 **1.8e−18 절대**로 갈린다 (궤적량이
      O(1) 이라 배정밀도 eps 의 1/100 이다).  그래서 게이트를 "정확히 0" 대신
      **절대 1e−16** 으로 바꾼다 — 값을 느슨하게 한 게 아니라 척도를 맞춘 것이다.
    """
    r = TI.jdot_closure_reproduces_1d_reduction(bg, nsteps=10, l_max=2)
    assert r["gap"] < 1e-8, r
    exact = TI.jdot_closure_reproduces_1d_reduction(bg, nsteps=20, l_max=3)
    worst = max(abs(exact["reduction"][k] - exact["jdot"][k]) for k in exact["jdot"])
    assert worst < 1e-16, (worst, exact)


def test_massless_jdot_closure_is_orders_of_magnitude_better(bg):
    """무질량 궤적오차: ρ 5.3e−4 → 7.8e−8 (**6800배**)."""
    old = TI.trajectory_error(bg, 0.0, 0.2, 20, 3, 1, jdot_closure=False)
    new = TI.trajectory_error(bg, 0.0, 0.2, 20, 3, 1, jdot_closure=True)
    assert new["rho"] < old["rho"] / 1000.0, (old, new)
    assert new["q"] < old["q"] / 50.0, (old, new)
    assert new["pi"] < old["pi"] / 20.0, (old, new)


def test_massless_jdot_result_is_independent_of_i_max(bg):
    """★ r=1 이면 i 방향이 **완전히 축퇴**하므로 i_max 를 올려도 답이 같다.

    (기존 방식은 i_max 1→3 에서 27배 움직였다 — 그 움직임의 정체가 J̇ 절단이었다.)
    """
    a = TI.trajectory_error(bg, 0.0, 0.2, 10, 2, 1, jdot_closure=True)
    b = TI.trajectory_error(bg, 0.0, 0.2, 10, 2, 3, jdot_closure=True)
    for k in a:
        assert abs(a[k] - b[k]) <= 1e-12 * max(a[k], 1e-300), (k, a, b)


# ═══════════════════════════════ 5. 유질량 — 정직한 표
@pytest.mark.parametrize("mass", [0.5, 1.0, 4.0])
def test_massive_gain_at_i_max_3(bg, mass):
    """유질량 궤적오차 개선 (i_max=3, ratio+J̇):
        m=0.5  1.86e−5 → 8.4e−7 (22배)
        m=1    1.18e−5 → 2.6e−6 (4.6배)
        m=4    3.2e−6  → 1.8e−6 (1.8배)
    """
    old = TI.trajectory_error(bg, mass, 0.2, 20, 3, 3, mode="frozen",
                              jdot_closure=False)
    new = TI.trajectory_error(bg, mass, 0.2, 20, 3, 3, mode="ratio",
                              jdot_closure=True)
    assert new["rho"] < old["rho"], (old, new)
    assert new["pi"] < old["pi"], (old, new)


def test_m2_rho_gets_worse_and_we_say_so(bg):
    """★ **정직성 고정**: m=2 의 ρ 는 기존 값이 부호상쇄로 우연히 좋았다.

    옛 6.8e−7 → 새 3.9e−6.  i_max=2 에서는 2.9e−5 이고 i_max=4 에서 4.8e−7 이므로
    i_max=3 의 6.8e−7 은 **수렴열의 일부가 아니라 영점 통과**다.
    개선을 주장하면서 이런 칸을 감추지 않는다.
    """
    old = TI.trajectory_error(bg, 2.0, 0.2, 20, 3, 3, mode="frozen",
                              jdot_closure=False)
    new = TI.trajectory_error(bg, 2.0, 0.2, 20, 3, 3, mode="ratio",
                              jdot_closure=True)
    assert old["rho"] < new["rho"]                      # 실제로 나빠진다
    assert new["pi"] < old["pi"] / 2.0                  # 그래도 π 는 좋아진다


def test_jdot_closure_alone_is_not_enough_for_heavy_mass(bg):
    """★ 무거우면 얼린 비가 나빠서 J̇ 닫힘만으로는 부족하다 (i_max=1 에서 역효과).

    m=2, i_max=1: 6.3e−4 → 8.9e−4.  비 r 자체를 고쳐야(ratio) 이득이 난다.
    ⇒ 두 고침은 **함께**라야 한다.
    """
    old = TI.trajectory_error(bg, 2.0, 0.2, 20, 3, 1, mode="frozen",
                              jdot_closure=False)
    bad = TI.trajectory_error(bg, 2.0, 0.2, 20, 3, 1, mode="frozen",
                              jdot_closure=True)
    good = TI.trajectory_error(bg, 2.0, 0.2, 20, 3, 3, mode="ratio",
                               jdot_closure=True)
    assert bad["rho"] > old["rho"]
    assert good["rho"] < old["rho"] / 10.0, (old, good)


# ═══════════════════════════════ 6. V4 — 성분별 비 vs 스칼라 비
def test_scalar_ratio_variant_is_available_and_comparable():
    """V4: `close_i` 의 성분별 비가 '거의 0 인 성분' 에서 무의미해지는 문제.

    노름 기반 스칼라 비를 대안으로 두고 **비교 가능하게** 만들었다.
    측정: l=0 (스칼라) 에서는 둘이 같고, 텐서 성분에서는 성분별이 더 낫다.
    """
    e_c = TC.closure_prediction_error(1.0, 0, 2, "ratio")
    e_s = TC.closure_prediction_error(1.0, 0, 2, "ratio_scalar")
    assert abs(e_c["e1"] - e_s["e1"]) < 1e-12          # l=0 은 동일
    t_c = TC.closure_prediction_error(1.0, 2, 2, "ratio")
    t_s = TC.closure_prediction_error(1.0, 2, 2, "ratio_scalar")
    assert t_c["e1"] <= t_s["e1"] * 1.5, (t_c, t_s)


def test_unknown_mode_raises():
    """오타를 조용히 넘기지 않는다."""
    J = {(0, 0): 1.0, (0, 1): 0.9, (0, 2): 0.85}
    with pytest.raises(ValueError):
        TC.predict(J, 0, 2, "geometrik")


# ═══════════════════════════════ 7. 회귀 — 질량행렬이 여전히 J̇ 에 선형
def test_mass_matrix_stays_linear_with_i_ratio():
    """★ i_ratio 는 **현재 상태에서 온 상수 계수**다 — M 은 여전히 J̇ 에 선형.

    선형성이 깨지면 `dense` 의 단위벡터 조립이 조용히 틀린다.
    """
    from bianchi.matter import tilted_mass as TMass
    from bianchi.matter import tilted_terms as TT
    geo = TT.geometry((1.0, 0.9, 1.2), (0.35, 0.28, 0.42),
                      (0.08, -0.05, 0.12), (0.015, 0.01, -0.02))
    ir = {0: np.array(0.8), 1: np.full((3,), 0.85), 2: np.full((3, 3), 0.9)}
    M = TMass.dense(geo, 2, 1, None, ir)
    n = M.shape[0]
    rng = np.random.default_rng(0)
    x, y = rng.normal(size=n), rng.normal(size=n)
    lhs = TMass.pack(TMass.matvec(TMass.unpack(2.0 * x - 3.0 * y, 2, 1), geo,
                                  2, 1, None, ir), 2, 1)
    assert np.abs(lhs - (2.0 * (M @ x) - 3.0 * (M @ y))).max() < 1e-12


def test_i_ratio_none_reproduces_the_old_mass_matrix():
    """i_ratio 를 안 주면 **옛 M 과 정확히 같다** (기본 경로 불변 확인)."""
    from bianchi.matter import tilted_mass as TMass
    from bianchi.matter import tilted_terms as TT
    geo = TT.geometry((1.0, 0.9, 1.2), (0.35, 0.28, 0.42),
                      (0.08, -0.05, 0.12), (0.015, 0.01, -0.02))
    A = TMass.dense(geo, 3, 2, None, None)
    B = TMass.dense(geo, 3, 2)
    assert np.abs(A - B).max() == 0.0
