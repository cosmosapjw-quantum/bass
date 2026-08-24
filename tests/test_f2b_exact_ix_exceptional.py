"""
F2b · **예외형 VI*_{-1/9} 정확해 + Taub(진공 LRS IX)** — F-티어 정확해 매트릭스 완결.

측정 (이 증분, 56차):
  · 예외형 평형 가족 4종 (sympy=Wolfram=수치전수 4000-시드 3중 합치):
    진공 호(Sx=−Nm 부호 필수) / Collins(F2 κ=−9 축약 정확 일치, Ω=(5−3γ)/3) /
    S₂-진공점(γ-무관) / ★ Wainwright γ=10/9 **평형점 선분** S₂²=2A²−4/27 —
    γ≠10/9 강제식 (6A²−1)(9γ−10)=0 (분기값 10/9 의 구조적 출현).
  · 반증 박제: 손축약 CF 라디칼 가지는 S₂²<0 실정의역 공허 (Nm≠0 유체 평형
    부재 — 수치 전수 확인); 진공 호 (+w,+w) 는 잔차 12√·(Σ₊+1).
  · Taub: 축약계 (Σ₊,u) 항등 (u'=−6Σ₊u, Σ₊' 닫힌형, 진공 Gauss n²u(u−4)=12(1−Σ₊²))
    이 Rust 궤적 위에서 성립; LRS(N₂=N₃ 비트동일)·Σ₋=0 정확 보존; H→D 차트
    사상의 점별 두-경로 게이트; **재붕괴 실측** (type_ix_d_future 에서 H̄ 부호전환).
  · ★ 명시 빈칸: Taub 궤도 제1적분의 초등 닫힌형 — sympy dsolve 240s 타임아웃,
    Wolfram DSolve 게이트웨이 오류 2회.  축약 ODE·구속 게이트로 대체 (기록).
"""
import numpy as np
import pytest

RC = pytest.importorskip("bianchi_rustcore")

import jax  # noqa: E402

jax.config.update("jax_enable_x64", True)
import jax.numpy as jnp  # noqa: E402

from bianchi import exact as EX  # noqa: E402


def _py_rhs_exc(y, gamma):
    from bianchi.charts import exceptional as E
    st = E.StateE.from_array(jnp.asarray(y))
    return np.asarray(E.rhs(0.0, st, {"gamma": gamma}).as_array(), float)


# ---------------------------------------------------------------- 예외형 가족
@pytest.mark.parametrize("name", ["exc_collins", "exc_s2_vacuum", "exc_vacuum_arc"])
def test_exceptional_equilibria_zero_rhs_and_persist(name):
    """★★ 오라클 RHS ≤ 1e−13 + Rust 3τ 지속 ≤ 1e−7 + g-구속면 위."""
    chart, ctor, _ = EX.EQUILIBRIA[name]
    y0 = ctor(1.3)
    assert np.abs(_py_rhs_exc(y0, 1.3)).max() <= 1e-13, name
    from bianchi.charts import exceptional as E
    assert abs(float(E.g_constraint(E.StateE.from_array(jnp.asarray(y0))))) <= 1e-15
    ts = np.linspace(0.0, 3.0, 7)
    ys, ok = RC.integrate_background("exceptional", y0, ts, 1.3)
    assert ok, name
    assert np.abs(ys - y0[None, :]).max() <= 1e-7, name


def test_exc_collins_matches_f2_collins_at_kappa_minus_nine():
    """★ 독립 게이지 재유도 합치: exceptional Collins = class_b Collins(κ=−9)."""
    g = 1.3
    ye = EX.exc_collins(g)                              # (Σ₊,Σ₋,S₂,Sx,Nm,A)
    yb = EX.collins_VIh(g, -9.0)                        # (Σ₊,Σ̃,Δ,Ã,N₊)
    assert abs(ye[0] - yb[0]) <= 1e-15                  # Σ₊ 동일
    assert abs(ye[1]**2 - yb[1]) <= 1e-15               # Σ₋² = Σ̃ (S₂=Sx=0)
    assert abs(ye[5]**2 - yb[3]) <= 1e-15               # A² = Ã
    om = 1.0 - ye[:4] @ ye[:4] - ye[4]**2 - 4.0*ye[5]**2
    assert abs((5.0 - 3.0*g)/3.0 - om) <= 1e-15


def test_wainwright_line_is_gamma_ten_ninths_only():
    """★★ 분기 구조: γ=10/9 에서 선분 전체 평형; γ=1.3 에서는 A²=1/6 만."""
    for a2 in (2.0/27.0, 0.1, 1.0/6.0):
        y = EX.exc_wainwright(a2)
        assert np.abs(_py_rhs_exc(y, 10.0/9.0)).max() <= 1e-13, a2
    y_mid = EX.exc_wainwright(0.1)                      # A² = 0.1 ≠ 1/6
    r = np.abs(_py_rhs_exc(y_mid, 1.3)).max()
    assert r > 1e-3                                     # 강제식이 죽인다
    # 강제식의 생존점 A²=1/6 은 γ=1.3 에서도 평형 (= S₂-진공점)
    assert np.abs(_py_rhs_exc(EX.exc_wainwright(1.0/6.0), 1.3)).max() <= 1e-13


def test_wainwright_endpoints_are_collins_and_s2vacuum():
    """★ 선분 끝점 접합: A²=2/27 → Collins(γ=10/9), A²=1/6 → S₂-진공점."""
    g = 10.0/9.0
    lo = EX.exc_wainwright(2.0/27.0)
    assert np.abs(lo - EX.exc_collins(g)).max() <= 1e-15
    hi = EX.exc_wainwright(1.0/6.0)
    assert np.abs(hi - EX.exc_s2_vacuum()).max() <= 1e-15


def test_vacuum_arc_sign_structure_is_enforced():
    """★ 반증 박제: Sx=−Nm 필수 — 뒤집으면 Nm-식 잔차 12(Σ₊+1)w,
    Sx-식 잔차 16(Σ₊+1)w (리뷰가 초판 기록 6→12 계수 오류를 정정)."""
    y = EX.exc_vacuum_arc(-0.85)
    assert y[3] == -y[4] and y[4] > 0.0
    bad = y.copy()
    bad[3] = +bad[4]
    r = np.abs(_py_rhs_exc(bad, 1.3))
    w = np.sqrt(-(y[0]+1.0)*(4.0*y[0]+3.0))
    assert abs(r[4] - 12.0*(y[0]+1.0)*w) <= 1e-12       # Nm-식 예측 잔차
    assert abs(r[3] - 16.0*(y[0]+1.0)*w) <= 1e-12       # Sx-식 예측 잔차


def test_vacuum_arc_matches_f2_plane_wave_at_kappa_minus_nine():
    """★ 리뷰 MINOR 7b: 진공 호 = F2 plane_wave(Σ₊, κ=−9) 의 HHW 게이지 사상
    (Σ̃=Σ₋²+Sx², Ã=A², N₊²=3Nm² [게이지 N₊=√3N₋]) — 4번째 가족의 교차게이지."""
    for sp_v in (-0.99, -0.85, -0.76):
        ye = EX.exc_vacuum_arc(sp_v)
        yb = EX.plane_wave(sp_v, -9.0)                  # (Σ₊,Σ̃,Δ,Ã,N₊)
        assert abs(ye[1]**2 + ye[3]**2 - yb[1]) <= 1e-14
        assert abs(ye[5]**2 - yb[3]) <= 1e-14
        assert abs(3.0*ye[4]**2 - yb[4]**2) <= 1e-14


def test_numeric_census_finds_only_the_known_families():
    """★★ 리뷰 MAJOR 2: 경로 3 을 저장소에 박제 — 시드 고정 fsolve 전수에서
    미분류 평형점 0 (완전성 심판; 전체 4000-시드는 __main__ 리포트)."""
    from audit.f2b_exact_derivation import numeric_census
    hits, unknown = numeric_census(n_seeds=400, gamma=1.5, seed=0)
    assert unknown == []                                # 알려진 가족 밖 없음
    assert hits["vacuum_arc"] > 0 and hits["collins"] > 0
    assert hits["s2_vacuum"] > 0


def test_spurious_cf_branch_has_no_real_domain():
    """★ 반증 박제: CF 라디칼 가지 S₂²=Σ₊(1−2Σ₊)/6 < 0 — 표본 + 전창 기호."""
    from audit.f2b_exact_derivation import spurious_cf_is_empty
    out = spurious_cf_is_empty()
    assert out["whole_window"]                          # Σ₊<0 전창 기호 증명
    for sp_val, s2sq in out["samples"]:
        assert float(s2sq) < 0.0, sp_val


def test_exceptional_domain_guards():
    with pytest.raises(ValueError, match="5/3"):
        EX.exc_collins(1.7)
    with pytest.raises(ValueError, match="Σ₊"):
        EX.exc_vacuum_arc(-0.5)
    with pytest.raises(ValueError, match="2/27"):
        EX.exc_wainwright(0.01)


def test_symbolic_derivation_gates():
    """★ 경로 1 재실행 (미분·대입 항등만): 세 가족 잔차 0 + 강제식 인수분해."""
    from audit import f2b_exact_derivation as D
    arc = D.vacuum_arc_residuals()
    assert all(r == 0 for r in arc["residuals"]) and arc["Omega"] == 0
    assert arc["wrong_sign_Nm_eq"] != 0
    col = D.collins_residuals()
    assert all(r == 0 for r in col["residuals"])
    wl = D.wainwright_line_residuals()
    assert all(r == 0 for r in wl["on_line"] + wl["s2_vacuum"])
    import sympy as sp
    aa = sp.Symbol("aa", positive=True)
    gam = sp.Symbol("gamma", positive=True)
    assert sp.simplify(wl["forcing"]*18 - (6*aa**2 - 1)*(9*gam - 10)) == 0
    tr = D.taub_reduction()
    assert tr["dSp_match"] == 0 and tr["du_match"] == 0 and tr["K_check"] == 0


# ---------------------------------------------------------------- Taub (IX)
def test_taub_h_chart_hits_recollapse_singularity_in_finite_tau():
    """★★ 반증→실측 승격: 진공 IX 는 K=1−Σ² 로 **구속 고정**이라 모든 궤도가
    재붕괴 근방이고, 재붕괴는 H-시간으로도 **유한 τ** — H-차트는 거기서
    좌표 특이 (N̄=n/H 발산).  τ=3 시험 초안이 ok=False 로 반증됐다 (리뷰
    이분법 고정: τ* ∈ (0.3, 0.5]).  type_ix_d LIMITATIONS 를 Rust 실측 고정."""
    y0 = EX.taub_lrs_ix(-0.3, 6.0)
    ys, ok = RC.integrate_background("class_a", y0, np.linspace(0, 0.5, 5), 1.3)
    assert not ok                                       # 유한-τ 붕괴 (침묵 금지)
    ys, ok = RC.integrate_background("class_a", y0, np.linspace(0, 0.3, 5), 1.3)
    assert ok                                           # 리뷰 이분: τ* ∈ (0.3, 0.5]


def test_taub_lrs_and_vacuum_are_exactly_preserved():
    """★★ LRS(N₂=N₃ 비트동일)·Σ₋=0·진공 Gauss 보존 (단지평 — 위 시험 참조)."""
    y0 = EX.taub_lrs_ix(-0.3, 6.0)
    ts = np.linspace(0.0, 0.08, 13)
    ys, ok = RC.integrate_background("class_a", y0, ts, 1.3)
    assert ok
    assert (ys[:, 3] == ys[:, 4]).all()                 # N₂ ≡ N₃ (비트 동일)
    # ★ 실측 정정: Σ₋ 는 RHS 로는 정확 0 보존이지만 BDF Newton 의 FD-야코비
    #   보정이 불변부분공간 밖으로 1.7e−29 를 주입한다 (N₂≡N₃ 는 대칭 보정이라
    #   비트 생존).  "정확 0" 기대를 반증 기록으로 남기고 1e−25 게이트.
    assert np.abs(ys[:, 1]).max() <= 1e-25
    u = ys[:, 2] / ys[:, 3]
    gauss = ys[:, 3]**2 * u * (u - 4.0) - 12.0*(1.0 - ys[:, 0]**2)
    assert np.abs(gauss).max() <= 1e-7                  # 진공면 유지 (Ω 누출 예산)


def test_taub_reduced_system_holds_along_rust_trajectory():
    """★★ 축약 닫힌형 (Σ₊',u') 이 Rust 궤적 위 chart_rhs 와 일치 (Ω 예산 내)."""
    y0 = EX.taub_lrs_ix(-0.3, 6.0)
    ts = np.linspace(0.0, 0.08, 9)
    ys, ok = RC.integrate_background("class_a", y0, ts, 1.3)
    assert ok
    for i in range(len(ys)):
        y = ys[i]
        u = y[2] / y[3]
        r = np.asarray(RC.chart_rhs("class_a", y, 1.3))
        dsp_ref, du_ref = EX.taub_reduced_rates(y[0], u)
        du_traj = r[2]/y[3] - y[2]*r[3]/y[3]**2         # (N₁/n)'
        assert abs(r[0] - dsp_ref) <= 5e-8
        assert abs(du_traj - du_ref) <= 5e-7


def test_h_to_d_chart_map_is_pointwise_consistent():
    """★★ 두-경로 점별 게이트: J_map·rhs_H = rhs_D_future(map)/H̄ (재매개 D/H)."""
    from bianchi.charts import class_a as CA
    from bianchi.charts import type_ix_d as XD
    y0 = jnp.asarray(EX.taub_lrs_ix(-0.3, 6.0))
    f_map = lambda v: XD.from_H_chart(CA.StateA.from_array(v), 1.3).as_array()
    J = np.asarray(jax.jacfwd(f_map)(y0))
    rhs_h = np.asarray(CA.rhs(0.0, CA.StateA.from_array(y0), {"gamma": 1.3}
                              ).as_array())
    yd = XD.from_H_chart(CA.StateA.from_array(y0), 1.3)
    rhs_d = np.asarray(XD.rhs_future(0.0, yd, {"gamma": 1.3}).as_array())
    hbar = float(yd.H)
    assert 0.0 < hbar < 1.0
    lhs = J @ rhs_h
    assert np.abs(lhs - rhs_d / hbar).max() <= 1e-12


def test_taub_recollapses_in_d_chart():
    """★★ 재붕괴 실측: D-차트(미래방향)에서 H̄ 가 유한 τ_D 에 부호 전환 —
    H-차트는 원리적으로 못 잡는다 (ln H 유계 논증, type_ix_d LIMITATIONS)."""
    from bianchi.charts import class_a as CA
    from bianchi.charts import type_ix_d as XD
    yh = EX.taub_lrs_ix(-0.3, 6.0)
    yd = np.asarray(XD.from_H_chart(CA.StateA.from_array(jnp.asarray(yh)), 1.3
                                    ).as_array(), float)
    ts = np.linspace(0.0, 40.0, 401)
    ys, ok = RC.integrate_background("type_ix_d_future", yd, ts, 1.3)
    assert ok
    h = ys[:, 0]
    assert h[0] > 0.0
    cross = np.nonzero(h < 0.0)[0]
    assert cross.size > 0                               # 재붕괴 도달
    i = cross[0]
    assert h[i-1] > 0.0 > h[i]                          # 하향 교차 국소화
    # LRS 는 D-차트에서도 보존 (S₂=S₃, N₂=N₃)
    assert np.abs(ys[:i, 2] - ys[:i, 3]).max() <= 1e-9
    assert np.abs(ys[:i, 5] - ys[:i, 6]).max() <= 1e-9
    # ★ 리뷰 MINOR 4: 교차가 병리로 조작되지 않게 구속 3종을 교차점까지 감시
    #   (정의식 G, trace ΣS̄ₐ, 진공 Ω — 실측 1.2e−9 / 2.4e−15 / 3.1e−9)
    defn = ys[:i+1, 0]**2 + (ys[:i+1, 4]*ys[:i+1, 5] + ys[:i+1, 4]*ys[:i+1, 6]
                             + ys[:i+1, 5]*ys[:i+1, 6]) / 6.0 - 1.0
    trace = ys[:i+1, 1] + ys[:i+1, 2] + ys[:i+1, 3]
    om = 1.0 - (ys[:i+1, 1:4]**2).sum(1)/6.0 - (ys[:i+1, 4:7]**2).sum(1)/12.0
    assert np.abs(defn).max() <= 1e-8
    assert np.abs(trace).max() <= 1e-12
    assert np.abs(om).max() <= 1e-8


def test_first_integral_closed_form_is_an_explicit_blank():
    """★ 빈칸 명시 (F2 원칙: 못 채우는 칸은 조용히 건너뛰지 않는다):
    Taub 궤도 제1적분의 초등 닫힌형은 미확보 — sympy dsolve 240s 타임아웃,
    Wolfram DSolve 게이트웨이 오류 2회 (56차 기록).  축약 ODE 항등·구속
    보존·재붕괴 게이트가 대체 감시.  닫히면 이 시험을 교체할 것."""
    from audit.f2b_exact_derivation import taub_reduction
    assert taub_reduction()["dSp_match"] == 0           # 대체 게이트의 전제
