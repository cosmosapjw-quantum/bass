"""
F2 · **정확해 매트릭스** — 평형점 지속성 + 동적 닫힌형(제1적분) 게이트.

측정 (이 증분, 54차):
  · 평형점 7종 (Kasner/F/CS(II)/Milne/Collins VI_h/plane wave κ=0,+4):
    Python 오라클 RHS ‖·‖∞ ≤ 1e−13, Rust BDF 3τ 지속 ‖y−y₀‖∞ ≤ 1e−7.
  · 진공 type II (Taub): L=(2−Σ₊)/Σ₋ 와 Φ(Σ₊)−τ 가 Rust 궤적 내내 보존.
  · 진공 type V: 로지스틱 닫힌형 Σ̃(τ)=Σ̃₀/(Σ̃₀+(1−Σ̃₀)e^{4τ}) 을 rtol 1e−7 추적.
  · ★ 발견 박제: plane wave 완전족 N₊²=(1+Σ₊)[κ(1+Σ₊)−3Σ₊] — Σ̃≥0 정의역이
    Σ₊∈(−1,0] 를 강제하고 N₊=0 가지는 κ=3Σ₊/(1+Σ₊)≤0 뿐이라
    **VII_h(κ>0) plane wave 는 N₊≠0 필수** (축소차트에서 처음엔 N₊=0 로 풀어
    κ≤0 가지만 얻었었다 — 완전족 재유도로 정정).
  · 두 경로 유도: sympy (audit/f2_exact_derivation.py) = Wolfram (54차 기록) 완전
    합치.  CS(II) 는 audit/d_tilted_II.py 의 문헌 하드코드와도 독립 일치.
"""
import numpy as np
import pytest

RC = pytest.importorskip("bianchi_rustcore")

from bianchi import exact as EX  # noqa: E402
from bianchi import routing as R  # noqa: E402


def _py_rhs(chart, y, gamma, kappa):
    """Python(JAX) 오라클 RHS — Rust 와 독립 경로.

    ★ F2b BLOCKER 정정: 초판은 비-class_a 를 전부 class_b 로 보냈고
      StateB.from_array 가 예외형 6-상태를 **침묵 절단**해 쓰레기 오라클을
      평가했다 (잔차 0.73).  차트 명시 분기 + 길이 가드."""
    import jax.numpy as jnp
    _n = {"class_a": 5, "class_b": 5, "exceptional": 6}[chart]
    if len(y) != _n:
        raise ValueError(f"{chart} 상태는 길이 {_n}, 받은 것 {len(y)}")
    if chart == "class_a":
        from bianchi.charts import class_a as C
        st = C.StateA.from_array(jnp.asarray(y))
        return np.asarray(C.rhs(0.0, st, {"gamma": gamma}).as_array(), float)
    if chart == "exceptional":
        from bianchi.charts import exceptional as C
        st = C.StateE.from_array(jnp.asarray(y))
        return np.asarray(C.rhs(0.0, st, {"gamma": gamma}).as_array(), float)
    from bianchi.charts import class_b as C
    st = C.StateB.from_array(jnp.asarray(y))
    return np.asarray(C.rhs(0.0, st, {"gamma": gamma, "kappa": kappa}).as_array(),
                      float)


# ---------------------------------------------------------------- 평형점
@pytest.mark.parametrize("name", sorted(EX.EQUILIBRIA))
def test_equilibria_have_zero_rhs(name):
    """★★ 오라클 게이트: 유도된 평형점에서 Python RHS 가 기계정밀 0.
    + Ω ≥ 0 (리뷰 MAJOR 2: RHS=0 만으로는 음의 에너지밀도 고정점을 못 거른다)."""
    chart, ctor, kappa = EX.EQUILIBRIA[name]
    y = ctor(1.3)
    assert np.abs(_py_rhs(chart, y, 1.3, kappa)).max() <= 1e-13, name
    if chart == "class_a":
        om = 1.0 - y[0]**2 - y[1]**2 - (
            (y[2:5]**2).sum() - 2.0 * (y[2]*y[3] + y[3]*y[4] + y[4]*y[2])) / 12.0
    elif chart == "exceptional":
        om = 1.0 - (y[:4]**2).sum() - y[4]**2 - 4.0 * y[5]**2
    else:
        nt = (y[4]**2 - kappa * y[3]) / 3.0
        om = 1.0 - y[0]**2 - y[1] - nt - y[3]
    assert om >= -1e-15, (name, om)


def test_collins_vih_existence_condition_is_enforced():
    """★ 리뷰 MAJOR 2 박제: κ=−4 는 γ≳1.44 에서 Ω<0 — 생성자가 거부해야 한다."""
    with pytest.raises(ValueError, match="존재조건"):
        EX.collins_VIh(1.5, -4.0)                     # Ω = −0.094 였던 사례
    y = EX.collins_VIh(1.5, -8.0)                     # κ < −5 면 존재
    assert np.abs(_py_rhs("class_b", y, 1.5, -8.0)).max() <= 1e-13


def test_jacobs_disc_is_equilibrium_only_at_stiff():
    """★ Jacobs 원판: γ=2 에서 q≡2 → RHS=0; γ=1.3 에서는 평형이 아니다."""
    y = EX.jacobs(0.3, 0.2)
    assert np.abs(_py_rhs("class_a", y, 2.0, 0.0)).max() <= 1e-13
    assert np.abs(_py_rhs("class_a", y, 1.3, 0.0)).max() > 1e-3


@pytest.mark.parametrize("name", sorted(EX.EQUILIBRIA))
def test_equilibria_persist_under_rust_integration(name):
    """★★ 지속성: Rust BDF 3τ 적분이 평형점을 1e−7 이내로 붙잡아 둔다."""
    chart, ctor, kappa = EX.EQUILIBRIA[name]
    y0 = ctor(1.3)
    ts = np.linspace(0.0, 3.0, 7)
    ys, ok = RC.integrate_background(chart, y0, ts, 1.3, kappa)
    assert ok, name
    assert np.abs(ys - y0[None, :]).max() <= 1e-7, name


def test_cs_ii_confirms_prior_audit_hardcode():
    """★ 교차확인: d_tilted_II.py 의 문헌 하드코드 = 이번 sympy/Wolfram 유도."""
    import importlib.util as u
    spec = u.spec_from_file_location("d_tilted_II", "audit/d_tilted_II.py")
    m = u.module_from_spec(spec)
    spec.loader.exec_module(m)
    g = 1.3
    _, _, _, om, sp, n1 = m.cs_state(g)
    y = EX.collins_stewart_II(g)
    assert abs(y[0] - sp) <= 1e-15 and abs(y[2] - n1) <= 1e-15
    assert abs(om - (18.0 - 3.0 * g) / 16.0) <= 1e-15


# ------------------------------------------------- 동적 닫힌형 (제1적분)
def test_taub_line_integral_conserved():
    """★★ 진공 type II: L=(2−Σ₊)/Σ₋ 보존 — 게이트는 **기계론적** (Ω 예산).

    ★ 반증 기록: 균일 게이트 |ΔL| ≤ 1e−6 은 τ=6 에서 7.2e−5 로 깨졌다.
      원인은 적분기 결함이 아니라 **구속 불안정성**: 진공면 Ω=0 은 미래방향
      반발적 (Ω′=Ω(2q−(3γ−2)), Kasner 에서 율 2.1) — atol 급 잡음이 e^{2.1τ}
      로 증폭되고 dL ≈ 5.7·Ω (실측 비 4.6–5.7).  게이트: |ΔL| ≤ 10·max|Ω|
      + Ω 성장률이 예측 율 2q−(3γ−2)=2.1 과 일치 (V15 전파법칙의 수치 관측)."""
    y0 = EX.taub_II_vacuum(-0.3, 0.4)
    ts = np.linspace(0.0, 6.0, 25)
    ys, ok = RC.integrate_background("class_a", y0, ts, 1.3, 0.0)
    assert ok
    om = 1.0 - ys[:, 0]**2 - ys[:, 1]**2 - ys[:, 2]**2 / 12.0
    L = EX.taub_line_integral(ys)
    dL = np.abs(L - L[0])
    assert np.abs(om).max() <= 3e-5                    # 잡음 예산 상한 (실측 ~1.4e-5)
    assert dL.max() <= 10.0 * np.abs(om).max() + 1e-9  # dL 은 Ω 누출이 전부
    # 해석 확인 (리뷰): dL/dτ = −(3γ−2)Ω/Σ₋ — Σ₋≈0.4 에서 비 ≈ 4.75
    tail = np.abs(om[-9:])                             # τ ∈ [4, 6] 성장률
    rate = np.polyfit(ts[-9:], np.log(tail), 1)[0]
    assert 1.8 <= rate <= 2.4, rate                    # 예측 2q−(3γ−2) = 2.1
    assert np.abs(ys[:, 3:5]).max() == 0.0             # N₂=N₃=0 정확 보존


def test_taub_time_integral_lrs():
    """★★ LRS 진공 type II: Φ(Σ₊)−τ 보존 (dΦ/dτ=1 — 기호 유도 확인)."""
    y0 = EX.taub_II_vacuum(-0.5)
    ts = np.linspace(0.0, 1.5, 16)
    ys, ok = RC.integrate_background("class_a", y0, ts, 1.3, 0.0)
    assert ok
    phi = EX.taub_time_integral(ys[:, 0], ts)
    assert np.abs(phi - phi[0]).max() <= 1e-6
    assert ys[-1, 0] > 0.9                            # Σ₊ → 1 (Kasner 향)


def test_typeV_logistic_tracks_rust():
    """★★ 진공 type V: 로지스틱 닫힌형을 척도-절대 1e−7·max|Σ̃| 로 추적
    (꼬리 Σ̃~8e−4 에서는 상대 ~9e−5 에 해당 — 게이트 문구를 게이트에 맞춤)."""
    y0 = EX.typeV_vacuum(0.7)
    ts = np.linspace(0.0, 2.0, 21)
    ys, ok = RC.integrate_background("class_b", y0, ts, 1.3, 0.0)
    assert ok
    ref = EX.typeV_logistic(0.7, ts)
    assert np.abs(ys[:, 1] - ref).max() <= 1e-7 * ref.max()
    assert np.abs(ys[:, 1] + ys[:, 3] - 1.0).max() <= 1e-9   # Ω=0 면 유지


# ---------------------------------------------------------------- 발견·정의역
def test_plane_wave_viih_requires_nonzero_np():
    """★ 발견 박제: κ>0 plane wave 는 N₊≠0 필수 — 서명도 정합."""
    y = EX.plane_wave(-0.4, 4.0)
    assert y[4] > 0.0
    assert R.signature_of_state("class_b", y, kappa=4.0) == "VII_h"
    assert R.signature_of_state("class_b", EX.plane_wave(-0.4, 0.0),
                                kappa=0.0) == "IV"
    with pytest.raises(ValueError, match="plane wave 없음"):
        EX.plane_wave(-0.4, -3.0)                     # N₊² < 0 인 (Σ₊,κ)


def test_domain_guards():
    with pytest.raises(ValueError, match="존재 구간"):
        EX.collins_stewart_II(2.5)
    with pytest.raises(ValueError, match="κ < 0"):
        EX.collins_VIh(1.3, +4.0)
    with pytest.raises(ValueError, match="정의역"):
        EX.plane_wave(+0.1, 4.0)
    with pytest.raises(ValueError, match="원판"):
        EX.jacobs(0.8, 0.7)
    with pytest.raises(ValueError, match="Σ²"):
        EX.taub_II_vacuum(0.9, 0.5)
    with pytest.raises(ValueError, match="Σ̃"):
        EX.typeV_vacuum(1.2)


def test_symbolic_first_integrals_are_exact():
    """★ 기호 게이트 (경로 1 재실행, 미분 항등만 — solve 류는 audit 리포트 몫)."""
    from audit import f2_exact_derivation as D
    t = D.taub_II_first_integrals()
    assert t["dL"] == 0 and t["dPhi_minus_1"] == 0
    v = D.typeV_vacuum_logistic()
    assert v["reduced_ok"] == 0 and v["ode_res"] == 0
    j = D.jacobs_disc()
    assert j["dSp"] == 0 and j["dSm"] == 0 and j["q"] == 2
