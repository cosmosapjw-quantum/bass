"""
K5b · **type V 결합 진화** — 프로젝트의 원래 목표: 운동론이 기하를 실제로 움직인다.

K4c 가 "type V 자유흐름은 법선틀 열유속 q₁ 을 스스로 만든다" 를 측정했고, K5a 가
계량에서 Friedmann·Codazzi·공간 Einstein 식을 확정했다.  여기서 둘을 **함께 굴린다**.
구속식은 진화에 **넣지 않는다** — 넣으면 게이트가 자기 자신을 검사하게 된다.

★ 이 파일이 고정하는 측정:
  · 순방향 Liouville 측도 규칙 `d ln W/dt = −2Ap¹/E` 가 K4b 역추적과 **1.4e−11**
    (규칙을 빼면 1.2e−01 — 배율 8.5e+09)
  · `accelerations` 왕복 잔차 **1.3e−15** (K5a 기호식 → 물질 → 되풀기)
  · ★★ 두 구속 잔차가 **RK4 4차로 수렴** (nsteps 2배당 16.1배) — 부과한 게 아니라
    **역학이 보존**한다는 뜻
  · ★★ **Codazzi 추적**: σ₁(0)=0 에서 출발해 자유흐름이 만든 q₁ 을 σ₁ 이 따라간다
    (`3σ₁A/a₁ = −q₁` 상대 1.0e−07)
  · A=0 에서 K1 의 **독립 적분기**와 궤적 5.5e−11 일치
  · 깨진 구속은 **번진다**: C/ρ≈1.4e−03 이 F/ρ 를 0 → 5.2e−04 로 단조하게 민다

★ 반증 기록 둘:
  (a) 무게에 1/V 까지 실어 −3H 를 RK4 로 굴렸더니 A=0 대조군이 0 이 아니라 1.7e−09.
      전량이 e^{−3Ht} 의 RK4 오차였다 (예측 n·z⁵/120 = 1.70e−09).  V 를 해석적으로
      빼내니 **비트-정확 0.0**.
  (b) "A=0 이면 σ₁ 도 0" 은 틀렸다.  A=0 에서 Codazzi 는 q₁=0 으로 퇴화해 σ₁ 을
      구속하지 않는다 — σ₁ 은 π₁₁ 이 끌고 간다 (2.1e−03 까지).
"""
import numpy as np
import pytest

from bianchi.matter import type_v_coupled as C


# ═══════════════════════════════ 1. 순방향 운동론 — 측도 규칙을 대조로 확정
def test_forward_liouville_matches_backward_characteristics():
    """★★ 순방향(노드+무게)이 K4b 역추적과 같은 모멘트를 준다.

    격자마저 다르다 — 역추적은 시각 t 의 고정 구면격자, 순방향은 t=0 격자를 실어
    나른 찌그러진 격자.  그래서 이 일치는 특성곡선·야코비안·구적을 한 번에 잡는다.
    """
    assert C.forward_vs_backward(nsteps=80) < 1e-8


def test_the_measure_rule_is_not_decoration():
    """★★ 대조군 — 야코비안 항을 빼면 잔차가 1.2e−01 로 무너진다 (배율 8.5e+09)."""
    r = C.measure_rule_is_needed(nsteps=80)
    assert r["without_rule"] > 1e-2, r
    assert r["ratio"] > 1e6, r


def test_volume_factor_belongs_outside_the_integrator():
    """★ **반증 기록**: 1/V 를 RK4 에 실었던 옛 판은 A=0 에서도 1.7e−09 를 냈다.

    그 값이 지수함수 RK4 오차 예측 n·z⁵/120 과 2% 이내로 맞는다 — 원인이 확정된다.
    V 를 해석적으로 빼낸 지금 판은 A=0 에서 **정확히 0**.
    """
    v = C.volume_factor_is_the_error_floor()
    assert 0.9 < v["old_scheme"] / v["predicted"] < 1.1, v
    assert v["new_scheme"] == 0.0, v


# ═══════════════════════════════ 2. 기하 — K5a 기호식과 왕복
def test_accelerations_inverts_the_symbolic_einstein_equations():
    """★★ K5a 의 G_{îî}(a,h,u,A) 에서 물질을 역산해 `accelerations` 로 u 를 되찾는다.

    두 경로가 만난다: sympy 기호 계량 → 수치 선형해.  잔차 1.3e−15.
    """
    from audit import k5_type_v_einstein as K5
    G = K5.spatial_einstein_numeric()
    rng = np.random.default_rng(7)
    worst = 0.0
    for _ in range(50):
        a = rng.uniform(0.5, 2.0, 3)
        h = rng.uniform(-1, 1, 3)
        u = rng.uniform(-2, 2, 3)
        Av = rng.uniform(-1.5, 1.5)
        g = np.array(G(a, h, u, Av))
        p = float(g.mean())                       # 무대각합 π 가 되도록
        back = C.accelerations(a, h * a, Av, p, np.diag(g - p))
        worst = max(worst, float(np.abs(back - u).max()))
    assert worst < 1e-12, worst


def test_all_three_directions_share_the_same_curvature_term():
    """★ 1 축이 특별한데도 세 공간식에 모두 **같은** A²/a₁² 가 붙는다 (K5a 측정)."""
    import sympy as sp
    from audit import k5_type_v_einstein as K5
    d = K5.spatial_einstein_symbols()
    for e in d["G"]:
        assert sp.simplify(sp.diff(e, K5.A) - 2 * K5.A / d["a"][0] ** 2) == 0, e


# ═══════════════════════════════ 3. ★★ 결합 진화 — 구속은 부과하지 않는다
def test_initial_data_satisfies_both_constraints_exactly():
    """★ 등방 f₀ 면 q=0 이라 **Codazzi 가 σ₁=0 을 강제**하고, H 는 Friedmann 이 정한다."""
    r = C.evolve_coupled(nsteps=2, t_end=1e-4)
    assert abs(r["friedmann"][0] / r["rho"][0]) < 1e-14, r["friedmann"][0]
    assert abs(r["codazzi"][0] / r["rho"][0]) < 1e-14, r["codazzi"][0]


def test_constraints_converge_at_fourth_order():
    """★★ **가장 결정적인 게이트** — 잔차가 RK4 4차로 사라진다 (nsteps 2배당 16.1배).

    구속을 진화식에 넣지 않았으므로, 이 수렴은 특성곡선·측도·모멘트·공간 Einstein
    식이 서로 **정합**해야만 나온다.  하나라도 틀리면 dt→0 에서 상수로 남는다.
    """
    lo = C.constraint_drift(nsteps=30, t_end=0.3)
    hi = C.constraint_drift(nsteps=60, t_end=0.3)
    assert 12.0 < lo["friedmann"] / hi["friedmann"] < 20.0, (lo, hi)
    assert 12.0 < lo["codazzi"] / hi["codazzi"] < 20.0, (lo, hi)
    assert hi["friedmann"] < 1e-6 and hi["codazzi"] < 1e-9, hi


def test_shear_tracks_the_spontaneously_generated_flux():
    """★★ **K5b 의 물리 결론**: σ₁(0)=0 에서 출발해 자유흐름이 만든 q₁ 을 따라간다.

    아무도 Codazzi 를 부과하지 않았는데 `3σ₁A/a₁ = −q₁` 이 진화 내내 성립한다
    (상대 1.0e−07).  K4c 가 발견한 "자발적 열유속" 이 기하에 **실제로 흡수된다**.
    """
    c = C.codazzi_tracking(nsteps=60, t_end=0.3)
    assert abs(c["sigma1"][0]) < 1e-14, c["sigma1"][0]
    assert abs(c["q1"][0]) < 1e-12, c["q1"][0]
    assert np.abs(c["q1"]).max() > 1e-3, c["q1"]
    assert np.abs(c["sigma1"]).max() > 1e-3, c["sigma1"]
    assert c["rel"] < 1e-5, c["rel"]


def test_flux_and_shear_have_opposite_signs():
    """★ 부호까지 맞다 — Codazzi 가 `3σ₁A/a₁ = −q₁` 이므로 q₁>0 이면 σ₁<0."""
    c = C.codazzi_tracking(nsteps=40, t_end=0.3)
    nz = np.abs(c["q1"]) > 1e-6
    assert np.all(c["q1"][nz] * c["sigma1"][nz] < 0), (c["q1"], c["sigma1"])


# ═══════════════════════════════ 4. 대조군
def test_bianchi_I_limit_matches_the_independent_K1_integrator():
    """★★ A=0 에서 K1 과 궤적이 만난다 — 공유하는 것이 거의 없는 두 경로.

    K1: H 를 구속에서 풀고 σ̇=−3Hσ+π (1계), 물질은 닫힌형 적색이동 구적.
    K5b: ä 를 공간 Einstein 에서 풀고 (2계), Friedmann 미사용, 물질은 특성곡선 노드.
    """
    r = C.bianchi_I_cross_check(nsteps=60)
    assert r["a"] < 1e-6, r
    assert r["sigma"] < 1e-8, r


def test_type_I_limit_kills_the_flux_but_not_the_shear():
    """★ **반증 기록**: A=0 이면 q₁ 은 정확히 0 이지만 **σ₁ 은 0 이 아니다**.

    A=0 에서 Codazzi 는 q₁=0 으로 퇴화해 σ₁ 을 구속하지 않는다 — σ₁ 은 π₁₁ 이 끈다.
    """
    r = C.type_I_limit(nsteps=40, t_end=0.3)
    assert r["q1_max"] < 1e-12, r
    assert r["sigma1_max"] > 1e-3, r


def test_a_violated_codazzi_leaks_into_friedmann():
    """★★ 구속 위반은 **번진다** — Bianchi 항등식이 두 잔차를 닫힌 선형계로 묶는다.

    σ₁(0)=0.05 로 일부러 깨면 F(0)=0 인데도 F 가 단조 증가해 5.2e−04 에 이른다.
    ⇒ §3 의 4차 수렴이 "구속을 부과해서" 나온 게 아님을 반대편에서 확인한다.
    """
    r = C.constraint_propagation(nsteps=60, t_end=0.3)
    assert abs(r["F0"]) < 1e-14, r["F0"]
    assert r["C_mean"] > 1e-4, r
    assert abs(r["F_end"]) > 1e-4, r
    assert r["monotone"], r


@pytest.mark.parametrize("s1", [0.02, 0.05])
def test_broken_initial_data_is_orders_of_magnitude_worse(s1):
    """★ 대조군의 세기: 정합 초기자료 대비 구속 잔차가 6자리 이상 크다."""
    good = C.constraint_drift(nsteps=30, t_end=0.3)
    bad = C.broken_initial_data(nsteps=30, t_end=0.3, sigma1=s1)
    assert bad["codazzi"] / good["codazzi"] > 1e5, (good, bad)
