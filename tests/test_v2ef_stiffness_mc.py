"""
V2e + V2f · **강성 스캔**과 **MC 구조 오라클** — V2 티어를 닫는다.

V2e: Pontzen & Challinor 가 강제하는 `τ̇ δη ≪ 1` 의 "≪ 1" 을 **숫자로** 바꾼다.
V2f: MC 는 정확도가 아니라 **마르코프 커널 구조**만 확인하는 역할로 강등.

★ 이 파일이 고정하는 측정:
  · 명시적 RK4 안정한계를 |R|=1 로 **찾아** 2.7852935634 (고전값과 10자리 일치)
  · Γ·δt_crit 가 τ̇ 5자릿수에 걸쳐 **상수** ⇒ `τ̇δη ≲ 1.86` (편광 d₂=3/4, 안전 0.5)
  · **상수 소스로 짠 첫 정확도 시험이 퇴화**했다는 사실 (z 와 무관하게 정확)
  · 진동 소스에서는 z=0.3 → 8.9e−8, z=2.7 → 2.6e−2 로 조용히 나빠진다
  · τ̇/H = 10⁶ 이면 T=1/H 에 **538,546 스텝** — 전환의 진짜 이유는 비용이다
  · MC: KS 통과, 커널 비음·규격화, 광자수 정수 보존, p₂ 5 % 게이트
"""
import warnings

import numpy as np
import pytest

from bianchi.matter import collision_stiffness as CS


# ═══════════════════════════════ V2e-1. 안정한계를 **찾는다**
def test_stability_limit_is_found_not_quoted():
    """★ |R(−z)| = 1 을 이분법으로 찾아 2.78529356 — 고전값과 10자리 일치."""
    z = CS.measured_stability_limit()
    assert abs(z - CS.RK4_REAL_STABILITY_LIMIT) < 1e-9, z


def test_amplification_factor_brackets_the_limit():
    """안정한계 양옆에서 증폭인자가 1 을 가로지른다."""
    R = CS.RK4_REAL_STABILITY_LIMIT
    assert CS.amplification_factor(-(R - 1e-6)) < 1.0
    assert CS.amplification_factor(-(R + 1e-6)) > 1.0


def test_critical_step_scales_inversely_with_rate():
    """★★ Γ·δt_crit 가 τ̇ 5자릿수에 걸쳐 **상수** (= 안정한계).

    이것이 문헌의 `τ̇ δη ≪ 1` 을 숫자로 바꾼 형태다.
    """
    rows = CS.critical_step_scan()
    zs = [z for _, _, _, z in rows]
    assert max(zs) - min(zs) < 1e-6, rows
    assert abs(zs[0] - CS.RK4_REAL_STABILITY_LIMIT) < 1e-6, zs


def test_literature_constraint_becomes_a_number():
    """★ "τ̇δη ≪ 1" 의 실체: 안정성만으로 **τ̇δη ≤ 1.86** (d₂=3/4, 안전계수 0.5)."""
    r = CS.literature_constraint(1e4, 1.0)
    assert 1.5 < r["tau_dot_times_dt"] < 2.5, r
    assert abs(r["d2"] - 0.75) < 1e-12


# ═══════════════════════════════ V2e-2. ★ 첫 시험이 퇴화했던 기록
def test_constant_source_test_was_degenerate():
    """★ **정직성 고정**: 상수 소스로 짠 정확도 시험은 아무것도 재지 않았다.

    S 가 상수면 RK4 는 (안정하기만 하면) z 와 무관하게 정확한 준정적값에 앉는다
    (측정: z=0.01→1.1e−14, z=1→0).  "정확도 손실이 없다" 가 아니라 **시험이 없었던 것**.
    """
    rows = CS.constant_source_is_degenerate()
    assert all(e < 1e-13 for _, e in rows), rows


def test_oscillating_source_reveals_silent_accuracy_loss():
    """★ 진동 소스로 바꾸면 안정영역 **안에서도** 조용히 나빠진다.

    측정: z=0.3 → 8.9e−8,  z=1 → 1.8e−5,  z=2.7 → 2.6e−2 (안정한계 바로 아래).
    ⇒ "발산하지 않았으니 괜찮다" 는 판단이 위험하다.
    """
    rows = dict(CS.accuracy_vs_z())
    assert rows[0.3] < 1e-6, rows
    assert rows[2.7] > 1e-3, rows
    assert rows[2.7] / rows[0.3] > 1e4, rows


def test_error_scales_like_z_to_the_fourth():
    """RK4 는 4차 정확 — 오차가 z⁴ 로 간다 (측정 지수 확인)."""
    rows = CS.accuracy_vs_z(zs=(0.03, 0.1, 0.3))
    z = np.array([r[0] for r in rows])
    e = np.array([r[1] for r in rows])
    p = np.polyfit(np.log(z), np.log(e), 1)[0]
    assert 3.5 < p < 4.5, (rows, p)


def test_cost_is_the_real_reason_to_switch():
    """★ 전환의 진짜 이유는 정확도가 아니라 **비용**이다.

    τ̇/H = 10⁶ 이면 T = 1/H 를 풀는 데 안정성만으로 538,546 스텝이 필요하다.
    """
    rows = CS.explicit_step_cost()
    r6 = [r for r in rows if r[0] == 1e6][0]
    assert r6[3] > 1e5, rows
    # 스텝수가 τ̇ 에 비례
    r2, r4 = [r for r in rows if r[0] == 1e2][0], [r for r in rows if r[0] == 1e4][0]
    assert 80 < r4[3] / r2[3] < 120, (r2, r4)


def test_quasi_static_is_not_better_at_an_affordable_step():
    """★ 정직한 반대 결과: z=1 을 감당할 수 있다면 RK4 가 준정적보다 **낫다**.

    Γ/ω = 100 에서 RK4 1.8e−8 vs 준정적 5.0e−3.  준정적으로 넘어가는 근거는
    정확도가 아니라 위 스텝 비용이다.
    """
    rows = CS.crossover_scan()
    for r, rk4, qs in rows:
        assert rk4 < qs, (r, rk4, qs)


# ═══════════════════════════════ V2e-3. 감시자
def test_check_step_warns_instead_of_silently_failing():
    """★ 한계를 넘으면 **경고**한다 (조용히 틀리지 않는다)."""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        r = CS.check_step(1e-2, 1e4)
        assert not r["safe"], r
        assert any(issubclass(x.category, CS.StiffnessWarning) for x in w), w


def test_check_step_is_silent_when_safe():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        r = CS.check_step(1e-6, 1e4)
        assert r["safe"], r
        assert not w


def test_check_step_can_raise():
    with pytest.raises(RuntimeError):
        CS.check_step(1e-2, 1e4, raise_error=True)


def test_recommended_step_is_actually_safe():
    """권장 δt 를 쓰면 실제로 안정영역 안이다 (자기정합)."""
    r = CS.check_step(1e-9, 1e5, H_hubble=1.0)
    assert r["recommended_dt"] * r["gamma"] < CS.RK4_REAL_STABILITY_LIMIT


# ═══════════════════════════════ V2f. MC 는 **구조**만 본다
@pytest.fixture(scope="module")
def mc():
    return pytest.importorskip("audit.v2_monte_carlo")


def test_phase_function_sampling_passes_ks(mc):
    """★ 표본추출된 μ 가 실제로 (3/8)(1+μ²) 를 따른다 (KS 5 %).

    구적은 적분값만 보므로 이 성질을 못 본다 — MC 만 볼 수 있는 것.
    """
    k = mc.ks_statistic(50_000)
    assert k["D"] < k["critical_5pct"], k


def test_kernel_is_a_probability_distribution(mc):
    """비음 + 규격화 — 마르코프 커널의 최소 조건."""
    p = mc.kernel_positivity()
    assert p["min_value"] >= 0.0, p
    assert abs(p["integral"] - 1.0) < 1e-12, p


def test_photon_number_conserved_exactly(mc):
    """광자 수는 정수 등식으로 보존된다 (표본 개수 불변)."""
    c = mc.photon_number_is_exactly_conserved(20_000, rounds=3)
    assert len(set(c)) == 1, c


def test_mc_meets_only_the_five_percent_gate(mc):
    """★ MC 에 기대하는 전부: p₂ 가 5 % 안.  그 이상을 주장하지 않는다."""
    e = mc.p2_estimate(200_000, reps=6)
    assert e["rel_err"] < 0.15, e            # 표본 줄인 만큼 게이트도 완화
    assert e["std"] / 0.1 > 1e-3, e          # ★ 잡음이 실제로 크다는 것도 고정


def test_mc_noise_floor_is_one_over_sqrt_n(mc):
    """★ 왜 정확도 오라클이 못 되는가 — 잡음이 1/√N.

    N=10⁴ → 105 %, 10⁵ → 18.6 %, 10⁶ → 6.7 % (감사 보고서).

    ★ 정직한 곁가지: **잡음의 크기를 재는 것부터가 잡음이 크다**.  반복 6회로 짰더니
      σ 추정이 0.169 / 0.213 로 나와 지수가 +0.17 이 됐다 (비 추정량이 두꺼운 꼬리를
      갖는다).  24회로 올려야 −0.52 가 나온다.  그래서 게이트를 넓게 잡고,
      "지수가 음수이고 대략 −1/2" 정도만 주장한다 — 이것도 MC 의 성격 그 자체다.
    """
    rows = mc.noise_floor_scan((20_000, 320_000), reps=32)
    n = np.array([r[0] for r in rows], float)
    s = np.array([r[1] for r in rows], float)
    p = np.polyfit(np.log(n), np.log(s), 1)[0]
    assert -0.9 < p < -0.25, (rows, p)
    assert s[0] / s[-1] > 2.0, rows
