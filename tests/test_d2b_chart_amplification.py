"""
D2b · **일반 Bianchi 차트의 구속 증폭** — 0.0 을 돌려주던 자리를 메운다.

D2 는 type V 를 물리 단위에서 계량으로 유도했다.  여기서 프로덕션 차트
(`charts/general`, 확장정규화) 로 올린다.  방법은 손대수가 아니라 **자동미분**이다:
Ċ = J f 이고 계가 닫혔다면 구속면 위에서 ∂(Jf)/∂y = M·J 이므로, M 을 최소제곱으로
풀고 **그 잔차를 닫힘 검사로 쓴다**.

★ 이 파일이 고정하는 측정:
  · ★★ `trace` 구속의 기울기가 **항등적으로 0** — `tracefree_from_5` 로 상태를 짜서
    애초에 위반될 수 없다.  rank(J) = 7 ≠ 8.  감시해도 정보가 없다.
  · ★★ `gauss` 는 args 에 Ω 를 안 주면 **항등적으로 0** (aux 가 Gauss 로 Ω 를 소거).
  · ★★ 물질을 얼린 채로는 닫히지 않는다 (잔차 6.3e−01 ~ 1.0e+00)
  · ★★ 닫히게 하는 물질 법칙을 **적합으로 결정** (잔차 1e−15):
        Q̇^a = (2q−2)Q^a − Σ^a_bQ^b + 3Π^{ab}A_b + ε^{abc}N_bd Π^d_c
        Ω̇   = (2q−2)Ω + (2/3)A·Q − (1/3)Σ·Π
    후보 `NQ`, `εAQ` 는 계수가 **정확히 0**.
  · ★★ type V 배위의 Codazzi 증폭률 = **2(q + Σ₊ − 1)** (차 2.2e−16) — D2 가 계량에서
    얻은 값.  `constraints.py` 인용식 4(q+Σ₊−1) 은 2차 잔차라 두 배.
  · ★ 대조군: Jacobi (N·A = 0) 를 깨면 같은 계수로도 잔차가 1.4e−01 ~ 3.8e−01 로 튄다.

★★ 그리고 운동론 쪽 확인 하나 — 닫힘이 요구하는 물질 법칙을 **K5b 의 해가 실제로
  만족한다**: q̇₁ = −(4H+σ₁)q₁ − 3(A/a₁)π₁₁ 를 6.3e−12 로 만족하고, a·π 항을 빼면
  100% 틀린다 (t=0 에서 참값 1.6e−01 인데 0 을 준다).  Liouville 수송에 넣은 적이 없다.

★ 반증 기록: 처음 적합은 계수가 1~15% 어긋나고 (`NQ`=+0.126 처럼) 잔차가 1e−1 에서
  멈췄다.  무작위 배위가 **Jacobi 를 위반**하고 있었다 — 구속면 위가 아니었으니
  "구속면 위에서 미분한다" 는 전제가 통째로 무너져 있었다.  N 의 A-방향 행·열을
  0 으로 두자 계수가 정확한 정수·분수로 떨어졌다.
"""
import numpy as np
import pytest

from bianchi.constraint_rates import CLOSURE_COEFFS, general_amplification_rate


# ═══════════════════════════════ 1. 공허한 감시자
def test_trace_constraint_can_never_be_violated():
    """★★ `trace` 기울기가 항등적으로 0 — 상태가 애초에 trace-free 로 짜여 있다."""
    from audit import d2b_chart_amplification as D
    d = D.degenerate_constraints()
    assert d["trace_row"] == 0.0, d
    assert d["rank"] == 7, d
    assert (np.delete(d["row_norms"], 1) > 1e-3).all(), d


def test_gauss_is_vacuous_when_omega_is_eliminated():
    """★★ args 에 Ω 가 없으면 `aux` 가 Gauss 로 Ω 를 소거 — 잔차·기울기 모두 0."""
    from audit import d2b_chart_amplification as D
    v = D.gauss_is_vacuous_without_omega()
    assert v["without_omega"] == 0.0, v
    assert v["gradient_norm"] == 0.0, v


# ═══════════════════════════════ 2. ★★ 얼린 물질로는 닫히지 않는다
def test_frozen_matter_breaks_closure():
    """★★ 차트의 현재 동작 — Ω, Q, Π 가 args 로 얼어 있으면 잔차가 O(1)."""
    from audit import d2b_chart_amplification as D
    rows = D.closure_table(freeze_matter=True)
    assert min(rows) > 1e-2, rows


def test_the_fitted_laws_close_the_system():
    """★★ 적합한 물질 법칙을 넣으면 잔차가 **기계정밀도**로 떨어진다."""
    from audit import d2b_chart_amplification as D
    rows = D.closure_table()
    assert max(rows) < 1e-12, rows


# ═══════════════════════════════ 3. ★★ 법칙의 계수를 적합으로 결정
def test_closure_determines_the_matter_evolution_laws():
    """★★ 계수가 정확한 정수·분수로 떨어진다 (인용이 아니라 적합)."""
    from audit import d2b_chart_amplification as D
    c, sol = D.closure_coefficients()
    assert np.abs(np.asarray(sol) - CLOSURE_COEFFS).max() < 1e-6, c


def test_the_spurious_candidates_come_out_exactly_zero():
    """★ 넣어 본 `N Q` 와 `ε A Q` 는 계수가 0 — 기저가 축퇴하지 않았다는 확인."""
    from audit import d2b_chart_amplification as D
    c, _ = D.closure_coefficients()
    assert abs(c["NQ"]) < 1e-8, c
    assert abs(c["epsAQ"]) < 1e-8, c


def test_violating_jacobi_breaks_the_whole_argument():
    """★★ **반증 기록** — 구속면 위가 아니면 같은 계수로도 잔차가 1e−1 로 튄다.

    처음 적합이 어긋난 원인이 이것이었다 (무작위 N 이 N^{ab}A_b ≠ 0 였다).
    """
    from audit import d2b_chart_amplification as D
    rows = D.closure_table(jacobi=False)
    assert min(rows) > 1e-2, rows


# ═══════════════════════════════ 4. ★★ D2 와 만나는 지점
def test_chart_codazzi_rate_equals_the_metric_derivation():
    """★★ type V 배위의 Codazzi 증폭률 = 2(q + Σ₊ − 1) — D2 가 계량에서 얻은 값.

    확장정규화 차트(JAX)와 물리 단위 sympy 유도가 여기서 만난다.
    """
    from audit import d2b_chart_amplification as D
    r = D.type_v_rate()
    assert r["gap"] < 1e-12, r
    assert r["residual"] < 1e-12, r


def test_amplification_rate_no_longer_returns_a_silent_zero():
    """★★ `constraints.amplification_rate` 가 general 차트에서 실제 수를 낸다."""
    import jax.numpy as jnp
    from bianchi import constraints as CS
    from bianchi.charts import general as G
    Sig = np.diag([0.12, -0.05, -0.07])
    Av = np.array([0.6, 0.0, 0.0])
    S2 = float(np.trace(Sig @ Sig)) / 6.0
    K = float(G.curvature(jnp.zeros((3, 3)), jnp.asarray(Av))[0])
    args = {"gamma": 4 / 3, "Omega": 1 - S2 - K,
            "q_flux": np.array([3 * 0.6 * 0.12, 0.0, 0.0]),
            "Pi": np.zeros((3, 3))}
    y = G.StateG.of(Sig, np.zeros((3, 3)), Av)
    rate = float(CS.amplification_rate(G, y, args))
    r = general_amplification_rate(y, args)
    assert r["closure"] < 1e-12, r["closure"]
    assert abs(rate - r["rate"]) < 1e-12
    assert rate != 0.0
    assert np.isclose(np.min(r["spectrum"].real), 2 * (
        float(G.aux(y, args)["q"]) - Sig[0, 0] / 2 - 1.0), atol=1e-10)


# ═══════════════════════════════ 5. ★★ 운동론 해가 그 법칙을 만족한다
def test_the_kinetic_solver_obeys_the_momentum_law_it_was_never_told():
    """★★ q̇₁ = −(4H+σ₁)q₁ − 3(A/a₁)π₁₁ 를 6.3e−12 로 만족한다.

    D2b 가 차트에서 요구한 `3Π^{ab}A_b` 항이 물리 단위에서 바로 이 항이다.
    """
    from bianchi.matter import type_v_constraints as D2
    r = D2.momentum_law_residual(nsteps=40, t_end=0.3)
    assert r["reduced"] < 1e-9, r["reduced"]


def test_dropping_the_a_pi_term_is_not_a_small_correction():
    """★★ a·π 항을 빼면 **100% 틀린다** — t=0 에서 참값 1.6e−01 인데 0 을 준다."""
    from bianchi.matter import type_v_constraints as D2
    r = D2.momentum_law_residual(nsteps=40, t_end=0.3)
    assert r["naive_err"] > 0.5, r["naive_err"]
    assert abs(r["naive"][0]) < 1e-10 < abs(r["node"][0]), (r["naive"][0], r["node"][0])
