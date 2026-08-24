"""
F3 · **tilted class A 차트** (n-대각 게이지) + 편타(whiplash) 문턱 이벤트.

측정 (이 증분, 55차):
  · 두 경로 유도: 성분 전개 rhs ≡ general+fluid 합성, 무작위 24점 ≤ 4.4e−16
    (첫 조립에서 [W,Σ]₁₃ 교차항 부호 2곳이 틀렸었다 — 경로 2 가 즉시 적발, 반증 기록).
  · 게이지 소거: n-대각 유지 회전 W_ij = √3Σ_ij(N_i+N_j)/(N_i−N_j) 로 일반 프레임
    dN 비대각 ≲1e−15 (환경 의존 라운드오프).  LRS 축퇴 (N_i=N_j, Σ_ij≠0) 는 게이지 불능 — 절벽 박제.
  · v=0 축약: class_a 와 5성분 일치 5.6e−17, 비대각/틸트 rate 정확히 0 (불변 부분공간).
  · N 곱셈 구조가 tilt 에서도 생존: Nᵢ' = (q+2σᵢ)Nᵢ — 0/부호 정확 보존.
  · CS(II) tilt 고윳값 교차검증: 차트 야코비안의 v-이중항 = thresholds 의
    dv_general 선형화 3(7γ−10)/8 (독립 두 경로).
  · ★ 편타 2단 반증 기록: 계획 v5 §2 "G₋ 영교차 이벤트" → 1차 정정 "γ≤2 영교차
    불가, γ=2 점근 접근" → 리뷰가 1차 정정도 반증: **γ=2 는 (1−V²) 가 1/G₋ 와
    대수 소거되어 V²=1 을 유한 τ 에 관통** (on-shell 실측 τ≈2.15, V²→10¹⁶).
    최종: γ<2 는 G₋≥2−γ 로 발화 불가, γ=2 는 문턱 통과(G₋<ε)가 유일한 유효
    종료 신호 + 무감시 적분은 초광속 가드(V²>1 → ok=false)가 차단.
"""
import numpy as np
import pytest

RC = pytest.importorskip("bianchi_rustcore")

import jax  # noqa: E402

jax.config.update("jax_enable_x64", True)
import jax.numpy as jnp  # noqa: E402

from bianchi.charts import class_a_tilted as AT  # noqa: E402
from bianchi import routing as R  # noqa: E402


def _rand_states(n, seed=7):
    rng = np.random.default_rng(seed)
    return [np.r_[rng.uniform(-0.3, 0.3, 5), rng.uniform(-0.8, 0.8, 3),
                  rng.uniform(-0.4, 0.4, 3)] for _ in range(n)]


# ---------------------------------------------------------------- 유도 게이트
def test_two_route_derivation_agrees():
    """★★ 경로 1 (성분 전개) ≡ 경로 2 (general+fluid 합성) ≤ 1e−13."""
    from audit.f3_class_a_tilted_gauge import gauge_cancellation, route_agreement
    assert route_agreement() <= 1e-13
    assert gauge_cancellation() <= 1e-13


def test_v0_reduces_to_class_a_exactly():
    """★★ v=0, Σ_offdiag=0 → class_a RHS 와 일치 + 불변 부분공간 rate 정확 0."""
    from bianchi.charts import class_a as CA
    yA = CA.StateA.of(0.2, -0.1, 0.7, 0.4, -0.3)
    yT = AT.StateAT.from_array(jnp.asarray(
        [0.2, -0.1, 0, 0, 0, 0.7, 0.4, -0.3, 0, 0, 0]))
    rA = np.asarray(CA.rhs(0.0, yA, {"gamma": 1.3}).as_array())
    rT = np.asarray(AT.rhs(0.0, yT, {"gamma": 1.3}).as_array())
    assert np.abs(rA - rT[[0, 1, 5, 6, 7]]).max() <= 1e-15
    assert np.abs(rT[[2, 3, 4, 8, 9, 10]]).max() == 0.0


def test_rust_mirrors_python_rhs():
    """★★ Rust ClassATilted = Python 경로 1, 무작위 12점 ≤ 1e−15."""
    for y in _rand_states(12):
        rp = np.asarray(AT.rhs(0.0, AT.StateAT.from_array(jnp.asarray(y)),
                               {"gamma": 1.3}).as_array())
        ru = np.asarray(RC.chart_rhs("class_a_tilted", y, 1.3))
        assert np.abs(rp - ru).max() <= 1e-15


def test_rust_aux_matches():
    """Ω·Codazzi(C¹) 도 Rust=Python."""
    y = _rand_states(1, seed=11)[0]
    yT = AT.StateAT.from_array(jnp.asarray(y))
    a = AT.aux(yT, {"gamma": 1.3})
    om_r, c_r = RC.chart_aux("class_a_tilted", y, 1.3)
    assert abs(float(a["Omega"]) - om_r) <= 1e-14
    c_py = np.asarray(AT.constraints(yT, {"gamma": 1.3})["codazzi"])
    assert abs(np.abs(c_py).max() - c_r) <= 1e-13      # Rust 는 max|C_a| (3성분)


def test_n_multiplicative_structure_survives_tilt():
    """★ Nᵢ=0 이 tilt 진화에서도 정확히 0 (Rust 적분)."""
    y0 = np.array([0.1, -0.05, 0.0, 0.0, 0.0, 0.7, 0.0, 0.0, 0.2, 0.1, 0.0])
    ts = np.linspace(0.0, 2.0, 9)
    ys, ok = RC.integrate_background("class_a_tilted", y0, ts, 1.2)
    assert ok
    assert np.abs(ys[:, 6]).max() == 0.0 and np.abs(ys[:, 7]).max() == 0.0
    assert ys[-1, 5] != 0.0                            # N₁ 은 살아 있다


def test_cs_ii_tilt_eigenvalue_cross_check():
    """★★ CS(II) v-이중항 고윳값: 차트 야코비안 = thresholds (독립 경로) = 3(7γ−10)/8."""
    from bianchi import thresholds as TH
    g = 1.3
    sp = (3.0*g - 2.0) / 8.0
    n1 = np.sqrt(9.0*(2.0 - g)*(3.0*g - 2.0)/16.0)
    y = jnp.asarray([sp, 0.0, 0, 0, 0, n1, 0, 0, 0, 0, 0])
    f = lambda v: AT.rhs(0.0, AT.StateAT.from_array(v), {"gamma": g}).as_array()
    J = np.asarray(jax.jacfwd(f)(y))
    lam_23 = J[9, 9], J[10, 10]                        # v₂, v₃ 대각 (이중항)
    analytic = 3.0*(7.0*g - 10.0)/8.0
    for lam in lam_23:
        assert abs(lam - analytic) <= 1e-12
    assert J[9, 10] == 0.0 and J[10, 9] == 0.0         # 이중항 비대각 (해석 0)
    assert abs(float(TH.stability_of_CS_II(g)) - analytic) <= 1e-10


def test_codazzi_stays_small_on_shell():
    """★★ 진짜 on-shell 보존 게이트 (리뷰 MAJOR 2 정정).

    1차 시도는 공허했다: CS(II)+v₂ 를 Σ₁₃=0 으로 놓으면 C²=−0.17 로 애초에
    off-shell 인데, 감시하던 C¹ 은 그 부분공간에서 **항등 0** — 아무것도 안
    쟀다.  tilted II 구속은 v₂ 를 Σ₁₃ 에 묶는다: C² = √3Σ₁₃(N₃−N₁) − q₂ = 0
    → Σ₁₃ = −√3γΩv₂/(3N₁G₊) 꼴 (Ω 가 Σ₁₃ 에 의존 — 고정점 반복으로 푼다)."""
    g, v2t = 1.3, 0.05
    sp, n1 = 0.2375, 0.865
    s13 = 0.0
    for _ in range(60):                                # 고정점 (수 회면 수렴)
        y = jnp.asarray([sp, 0, 0, s13, 0, n1, 0, 0, 0, v2t, 0])
        a = AT.aux(AT.StateAT.from_array(y), {"gamma": g})
        s13 = float(-np.sqrt(3.0)*g*a["Omega"]*v2t / (n1*float(a["Gp"])))
    y0 = np.array([sp, 0, 0, s13, 0, n1, 0, 0, 0, v2t, 0])
    c0 = np.asarray(AT.constraints(AT.StateAT.from_array(jnp.asarray(y0)),
                                   {"gamma": g})["codazzi"])
    assert np.abs(c0).max() <= 1e-12                   # 시작이 진짜 on-shell
    ts = np.linspace(0.0, 3.0, 13)
    ys, ok = RC.integrate_background("class_a_tilted", y0, ts, g)
    assert ok
    cmax = max(np.abs(np.asarray(AT.constraints(
        AT.StateAT.from_array(jnp.asarray(ys[i])), {"gamma": g})["codazzi"]
    )).max() for i in range(len(ys)))
    assert cmax <= 1e-7                                # 전 성분 보존 (실측 ~1e-9)
    # Rust 대표 구속(max|C_a|)도 같은 궤적에서 일치 감시
    assert RC.chart_aux("class_a_tilted", ys[-1], g)[1] <= 1e-7


# ---------------------------------------------------------------- 편타 이벤트
def test_whiplash_threshold_event_fires_and_truncates():
    """★★ γ=2: G₋=1−V² 문턱(0.1) 통과 — 중단·절단·문턱 이전 보증.
    (IC 는 의도적 off-shell — 역학·이벤트 시험 전용; v₁-tilt 는 II 구속 금지.)"""
    y0 = np.array([0.1, -0.05, 0, 0, 0, 0.5, 0, 0, 0.6, 0.0, 0.0])
    ts = np.linspace(0.0, 10.0, 41)
    ys, ok, hit, tau = RC.integrate_background_whiplash(
        "class_a_tilted", y0, ts, 2.0, 0.0, 0.1)
    assert ok and hit and 0.0 < tau < 10.0
    assert len(ys) < len(ts)
    v2 = (ys[:, 8:11]**2).sum(axis=1)
    assert (1.0 - (2.0 - 1.0)*v2 > 0.1).all()          # 반환점 전부 문턱 위


def test_unwatched_gamma2_run_is_stopped_superluminal():
    """★★ 리뷰 MAJOR 1 박제: γ=2 는 (1−V²) 가 1/G₋ 와 소거되어 V²=1 을
    **유한 τ 에 관통**한다 ("점근 접근" 1차 주장의 반증).  무감시 적분은
    초광속 가드가 ok=false 로 차단해야 한다 — 침묵 통과 금지."""
    y0 = np.array([0.1, -0.05, 0, 0, 0, 0.5, 0, 0, 0.6, 0.0, 0.0])
    ts = np.linspace(0.0, 10.0, 41)
    ys, ok = RC.integrate_background("class_a_tilted", y0, ts, 2.0)
    assert not ok                                      # V²>1 침묵 통과 금지
    assert len(ys) < len(ts)                           # 관통 전 구간까지만
    v2 = (ys[:, 8:11]**2).sum(axis=1)
    assert (v2 <= 1.0 + 1e-9).all()


def test_whiplash_no_zero_crossing_for_subcritical_gamma():
    """★ 반증 박제: γ=1.3 에서 G₋ ≥ 1−0.3·V² ≥ 0.7 — 문턱 1e−3 은 영원히 안 맞는다."""
    y0 = np.array([0.1, -0.05, 0, 0, 0, 0.5, 0, 0, 0.6, 0.0, 0.0])
    ts = np.linspace(0.0, 6.0, 25)
    ys, ok, hit, tau = RC.integrate_background_whiplash(
        "class_a_tilted", y0, ts, 1.3, 0.0, 1e-3)
    assert ok and not hit and np.isnan(tau)
    assert len(ys) == len(ts)


def test_whiplash_rejects_nontilt_charts():
    with pytest.raises(ValueError, match="tilt"):
        RC.integrate_background_whiplash("class_a", np.zeros(5),
                                         np.linspace(0, 1, 5), 1.3)


def test_whiplash_immediate_if_already_inside():
    """초기상태가 이미 절벽 안이면 한 발도 딛지 않는다 (ys 비어 있음)."""
    y0 = np.array([0.1, 0, 0, 0, 0, 0.5, 0, 0, 0.99, 0.0, 0.0])   # V²=0.9801
    ys, ok, hit, tau = RC.integrate_background_whiplash(
        "class_a_tilted", y0, np.linspace(0, 1, 5), 2.0, 0.0, 0.1)
    assert ok and hit and tau == 0.0 and len(ys) == 0


# ---------------------------------------------------------------- 라우팅 접합
def test_routing_opens_class_a_tilt():
    """★ F1 의 F3 예약 해제: class A tilt → class_a_tilted 라우팅 + 서명."""
    r = R.chart_for("IX", tilt=True)
    assert r["chart"] == "class_a_tilted" and r["params"] == {}
    y = np.array([0.1, 0.0, 0, 0, 0, 0.3, 0.2, 0.1, 0.05, 0, 0])
    assert R.signature_of_state("class_a_tilted", y) == "IX"
    y2 = np.array([0.1, 0.0, 0, 0, 0, 0.3, 0.0, 0.0, 0.05, 0, 0])
    assert R.signature_of_state("class_a_tilted", y2) == "II"


def test_lrs_cliff_is_measured_and_documented():
    """★ LRS 축퇴 절벽 박제: ΔN→0 에서 |W₁₂| ∝ 1/ΔN, 클리핑 후 ~1e12·Σ₁₂."""
    from audit.f3_class_a_tilted_gauge import lrs_cliff
    rows = lrs_cliff(s12=0.05)
    w_by_dn = dict(rows)
    assert abs(w_by_dn[1e-2]) < 1e2
    assert abs(w_by_dn[1e-8]) > 1e5                    # 발산 진행
    assert abs(w_by_dn[0.0]) >= 1e10                   # _safe 클리핑 극한
    assert "LRS" in AT.LIMITATIONS
