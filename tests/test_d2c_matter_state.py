"""
D2c · **물질을 차트의 상태변수로 승격** — 구속계가 닫힌 채로 굴러간다.

D2b 는 "물질(Ω, Q, Π)이 args 로 얼려 있으면 구속계가 닫히지 않는다 (잔차 ~1)" 를
**한 점에서** 보였고, 닫히게 하는 법칙을 적합으로 결정했다.  D2c 는 그 법칙을
`charts/general_matter` 의 **진화식**으로 넣고, 결과를 궤적 위에서 잰다.

    Q̇^a = (2q−2)Q^a − Σ^a_b Q^b + 3Π^{ab}A_b + ε^{abc}N_bd Π^d_c
    Ω̇   = (2q−2)Ω + (2/3)A·Q − (1/3)Σ·Π

기하는 `charts/general.rhs` 를 **그대로** 쓴다 (두 판이 갈라지면 어느 쪽이 맞는지
알 수 없게 된다) — 환원 게이트가 그걸 **정확히 0** 으로 고정한다.

★ 이 파일이 고정하는 측정:
  · ★★ 구속 표류, 같은 초기자료 (τ = 0 → 3):
        상태(D2c)  1.4e−17 → 7.5e−14 → 6.4e−13 → 3.7e−12 → 2.7e−14
        얼림(기존) 1.4e−17 → 3.2e−01 → 9.3e−01 → 2.3e+01 → **NaN**
  · ★★ 닫힘 잔차가 **궤적 내내** 기계정밀도 (1.3e−15 ~ 2.3e−13),
    증폭률(max Re λ) 이 1.620 → 0.570 으로 잘 정의된다 (NaN 없음)
  · ★ 구속 잔차가 적분 tolerance 를 따라간다 (1.9e−10 / 2.8e−12 / 2.3e−14)
    — 구조적 표류가 아니라 **적분오차**라는 뜻
  · ★★ 환원 게이트: Q=0, Π=0 이면 기하 RHS 가 `charts.general` 과 **0.0** 으로 동일
  · ★★ 닫힌 계에서는 투영이 거의 무동작 (2.2e−14 → 2.8e−17) — D2 의 교훈 그대로
  · 깨진 자료는 확장 상태 위에서 되돌아온다 (4.0e−03 → 2.2e−16)

★ **정직한 한계**: Π 는 여전히 처방 입력이다.  구속계는 어떤 Π 에서도 닫히지만
  (D2b 적합이 Π 방향 잔차까지 0 으로 만들었다), 물질 모형 자체는 무모순이 아니다 —
  처방 Π 가 Ω 를 음수(−1.5e−03)로 끌 수 있다.  물리적 Π 는 운동론 계층의 몫이다.
"""
import numpy as np
import pytest


# ═══════════════════════════════ 1. ★★ 구속이 진화 내내 유지된다
def test_matter_as_state_keeps_the_constraints_frozen_matter_does_not():
    """★★ **D2c 의 핵심** — 같은 초기자료가 한쪽은 1e−12, 다른 쪽은 NaN 이 된다."""
    from audit import d2c_matter_state as D
    r = D.drift_comparison()
    assert r["state"].max() < 1e-10, r["state"]
    fr = r["frozen"]
    assert np.nanmax(fr) > 1e-1 or not np.all(np.isfinite(fr)), fr
    assert r["state"][-1] < 1e-10 < np.nan_to_num(fr[-1], nan=np.inf)


def test_constraint_residual_tracks_the_integration_tolerance():
    """★ 잔차가 rtol 을 따라 내려간다 — **구조적 표류가 아니다**."""
    from audit import d2c_matter_state as D
    rows = D.tolerance_convergence()
    ws = [w for _, w in rows]
    assert ws[0] > ws[1] > ws[2], rows
    assert ws[0] / ws[2] > 1e3, rows


# ═══════════════════════════════ 2. ★★ 닫힘이 궤적 위에서 유지된다
def test_closure_holds_all_along_the_trajectory():
    """★★ D2b 는 **한 점**에서 닫힘을 봤다 — 여기서는 궤적 위 여러 점에서."""
    from audit import d2c_matter_state as D
    rows = D.closure_along_trajectory()
    assert max(r[1] for r in rows) < 1e-11, rows
    assert all(np.isfinite(r[2]) for r in rows), rows


def test_amplification_rate_is_finite_not_nan():
    """★★ 얼린 차트에서는 닫힘이 깨져 NaN 이었다 — 여기서는 실제 수가 나온다."""
    from bianchi import constraints as con
    from bianchi.charts import general_matter as GM
    from audit import d2c_matter_state as D
    y0, args = D.configuration()
    rate = float(con.amplification_rate(GM, y0, args))
    assert np.isfinite(rate), rate
    r = GM.amplification_rate(y0, args)
    assert r["closure"] < 1e-12, r
    assert abs(rate - r["rate"]) < 1e-12


# ═══════════════════════════════ 3. ★★ 환원 게이트
def test_geometry_reduces_exactly_to_the_general_chart():
    """★★ Q = 0, Π = 0 이면 기하 RHS 가 `charts.general` 과 **비트-정확** 같다.

    기하를 다시 쓰지 않고 `general.rhs` 를 그대로 호출하므로 당연해야 하고,
    당연한 것을 **시험으로 고정**한다 (나중에 갈라지면 여기서 걸린다).
    """
    from audit import d2c_matter_state as D
    assert D.reduces_to_the_geometry_chart() == 0.0


def test_the_trace_constraint_is_not_monitored():
    """★ D2b 가 잰 대로 tr Σ 는 구조상 위반 불가 — 감시 목록에서 뺐다."""
    from bianchi.charts import general_matter as GM
    from audit import d2c_matter_state as D
    y0, args = D.configuration()
    assert set(GM.constraint_residuals(y0, args)) == {"gauss", "codazzi", "jacobi"}


def test_initial_data_satisfies_all_three_constraints():
    """★ `on_constraint_surface` 가 Gauss·Codazzi·Jacobi 를 동시에 0 으로 둔다."""
    from bianchi.charts import general_matter as GM
    from audit import d2c_matter_state as D
    y0, args = D.configuration()
    c = GM.constraint_residuals(y0, args)
    for k, v in c.items():
        assert float(np.abs(np.asarray(v)).max()) < 1e-14, (k, v)


# ═══════════════════════════════ 4. 투영 — 확장 상태 위에서
def test_projection_restores_broken_extended_data():
    """★ Q 와 Ω 를 흔들어도 확장 상태 투영이 되돌린다 (4.0e−03 → 2.2e−16)."""
    from audit import d2c_matter_state as D
    r = D.projection_restores_broken_data()
    assert r["before"] > 1e-4, r
    assert r["after"] < 1e-14, r
    assert r["correction"] > 1e-4, r


def test_projection_is_nearly_a_noop_on_a_closed_system():
    """★★ D2 의 교훈 그대로 — 닫힌 계에서는 투영이 할 일이 거의 없다."""
    from audit import d2c_matter_state as D
    r = D.projection_is_nearly_a_noop()
    assert r["off"] < 1e-10, r
    assert r["on"] <= r["off"], r


def test_the_projector_registry_no_longer_falls_through():
    """★ `make_projector` 가 이 차트를 **명시적으로** 안다 (조용한 항등 투영 금지)."""
    from bianchi import constraints as con
    from bianchi.charts import general_matter as GM
    assert callable(con.make_projector(GM))


# ═══════════════════════════════ 5. ★ 정직한 한계
def test_prescribed_Pi_is_not_a_consistent_matter_model():
    """★ **한계를 숫자로** — 처방 Π 는 Ω 를 음수로 끌 수 있다 (−1.5e−03).

    구속계가 닫혀 있다는 D2c 의 주장은 그대로다 (잔차 3.7e−12).  닫힘과 물질
    모형의 무모순성은 **다른 이야기**이고, 물리적 Π 는 운동론 계층의 몫이다.
    """
    from audit import d2c_matter_state as D
    r = D.prescribed_Pi_can_drain_omega()
    assert r["went_negative"] is True, r
    assert r["constraint_worst"] < 1e-10, r
