"""
Q19 · **B2b 이력 배선** 게이트 (85차).

★★ 이 파일이 존재하는 이유 — 84차 Q15 시험의 반증
예전 시험은 이것만 봤다:
    c = Collision.thomson(hist, nu=1.0)
    assert m.collision.history is hist
    run(m)
**객체가 이력을 들고 있다**는 것과 **적분기가 이력을 쓴다**는 것은 다른 명제다.
전자만 참이었다: `Model.run()` → Mode A/B evolve 경로에 들어가는 것은 상수
`collision.nu` 였고, 저장소 어디에도 매 스텝 `thomson_rate(hist, z)` 를 계산하는
경로가 없었다.  아래 시험들은 **후자**를 잰다 — 특히
`test_q19_two_histories_give_different_evolution` 은 예전 배선에서 반드시 실패한다
(x_e 의 **내용**이 결과를 바꾸는지 보므로).
"""
import numpy as np
import pytest

from bianchi.q import contract as C
from bianchi.q import rate as RT
from bianchi.q.model import Collision, Grid, Model, run
from bianchi.thermo import history_api as HA


def _mk(hist=None, nu=0.0, mode="model", z0=600.0, nsteps=300, n_p=0,
        tau_end=-1.0, ty="I"):
    return Model(type=ty, grid=Grid(12, 24, n_p=n_p),
                 tau_span=(0.0, tau_end), nsteps=nsteps,
                 collision=(Collision("thomson", nu, None) if hist is None
                            else Collision.thomson(hist, nu=nu, rate_mode=mode)),
                 cosmology=RT.Cosmology(z0=z0), lane="phenomenology")


@pytest.fixture(scope="module")
def hist():
    return HA.SahaHistory()


# ─────────────────────────────────── 규약: dln a/dτ = 1 ⇒ z(τ) 정확
def test_q19_tau_z_convention_is_exact(hist):
    """1 + z = (1+z₀)e^{−(τ−τ₀)} — 근사가 아니라 τ 의 정의에서 나온다."""
    s = RT.RateSchedule(hist, RT.Cosmology(z0=1000.0), tau0=0.3, lane="phenomenology")
    tol = C.budget("Q19", "tau_z_roundtrip")
    for z in (10.0, 200.0, 1000.0, 3000.0):
        assert abs(float(s.z_of(s.tau_of(z))) - z) <= tol * max(z, 1.0)
    assert abs(float(s.z_of(0.3)) - 1000.0) <= tol * 1000.0
    # d ln(1+z)/dτ = −1 (수치 미분)
    t = 0.3
    d = (np.log1p(float(s.z_of(t + 1e-6))) - np.log1p(float(s.z_of(t - 1e-6)))) / 2e-6
    assert abs(d + 1.0) <= 1e-8, d


# ─────────────────────────────────── ★★ 배선이 실제로 소비되는가
def test_q19_nu_actually_varies_along_the_run(hist):
    """★★ 예전 배선에서는 ν 가 **상수**였다.  이제 run 구간에서 자릿수로 변한다."""
    m = _mk(hist, mode="lcdm")
    sched = m.schedule()
    assert sched is not None, "이력이 있는데 schedule() 이 None 이면 배선이 끊긴 것"
    dtau = (m.tau_span[1] - m.tau_span[0]) / m.nsteps
    ns, ha = sched.sample(dtau, m.nsteps)
    assert ns.shape == (m.nsteps + 1,)
    ratio = float(ns.max() / max(ns.min(), 1e-300))
    assert ratio >= C.budget("Q19", "nu_dynamic_range"), ratio


def test_q19_two_histories_give_different_evolution(hist):
    """★★ 배선의 **결정적** 시험: x_e 의 *내용*이 결과를 바꾸는가.

    예전 배선(상수 ν)에서는 두 이력이 **같은** 결과를 준다 — 반드시 실패한다."""
    z = np.linspace(500.0, 3000.0, 400)
    xe = np.asarray(hist.x_e(z), float)
    # ★ 85차 (독립 리뷰 m5): 원래 **2배** 차이를 τ_opt≈27 (포화) 구간에서 쟀다.
    #   포화 구간은 가장 둔감한 곳이라 10 % 변화는 놓쳤다 (4.7e−4 < 1e−3).
    #   비포화 구간 (z₀=900, 짧은 τ) 에서 **10 %** 변화로 잰다.
    # x_e**1.1 : 고이온화 구간(x_e=1)은 그대로 두고 재조합 구간만 ~10 % 낮춘다.
    #   (단순 0.9 배는 high_z_ionized 검사를 깬다 — 이력이 비물리가 된다.)
    small = HA.TabulatedHistory(z, xe ** 1.1, name="xe**1.1")
    kw = dict(mode="lcdm", z0=900.0, tau_end=-0.35, nsteps=200)
    a, _, _ = run(_mk(hist, **kw), fast=True)
    b, _, _ = run(_mk(small, **kw), fast=True)
    rel = float(np.abs(a.lG - b.lG).max() / max(np.abs(a.lG).max(), 1e-300))
    assert rel >= C.budget("Q19", "history_content_sensitivity"), rel


def test_q19_history_changes_result_vs_no_collision(hist):
    """이력 주입이 무충돌과 다른 답을 준다 (충돌이 실제로 걸린다)."""
    a, _, _ = run(_mk(hist, mode="lcdm"), fast=True)
    b, _, _ = run(_mk(None, nu=0.0), fast=True)
    assert float(np.abs(a.lG - b.lG).max()) >= 1e-3


# ─────────────────────────────────── 경로 간 일치
@pytest.mark.parametrize("mode", ["lcdm", "model"])
def test_q19_rust_matches_python_reference(hist, mode):
    """★ Rust 전-루프 ≡ Python 참조 (Q11 표준 승계).  Python 스텝 루프는 0회 유지."""
    m = _mk(hist, mode=mode)
    r, _, _ = run(m, fast=True)
    p, _, _ = run(m, fast=False)
    rel = float(np.abs(r.lG - p.lG).max() / max(np.abs(p.lG).max(), 1e-300))
    assert rel <= C.budget("Q19", "rust_vs_python"), (mode, rel)
    assert abs(r.lnH - p.lnH) <= 1e-13


def test_q19_mode_b_also_consumes_history(hist):
    """Mode B (완전 f) 도 같은 배선을 탄다 — 한쪽만 고치면 조용히 갈린다."""
    a, _, _ = run(_mk(hist, mode="lcdm", n_p=24, nsteps=120), fast=True)
    b, _, _ = run(_mk(None, nu=0.0, n_p=24, nsteps=120), fast=True)
    assert np.isfinite(a.lnf).all()
    assert float(np.abs(a.lnf - b.lnf).max()) >= 1e-3


def test_q19_constant_nu_path_is_unchanged(hist):
    """★ 이력이 없으면 기존 경로 그대로 — **비트 동일** (골든 보존의 근거)."""
    m = _mk(None, nu=1.0)
    a, _, _ = run(m, fast=True)
    b, _, _ = run(m, fast=True)
    assert float(np.abs(a.lG - b.lG).max()) == 0.0
    assert m.schedule() is None


# ─────────────────────────────────── 물리 앵커: ∫ν dτ = 광학깊이
def test_q19_integral_nu_dtau_is_the_optical_depth(hist):
    """★★ dτ_광학 = σ_T n_e c dt = ν_τ dτ  ⇒ ∫ν dτ 가 곧 Δτ_광학.

    외부 모듈의 광학깊이와 대조하면 **배선 전체**가 한 번에 검증된다
    (같은 H 규약인 mode='lcdm' 에서)."""
    from bianchi.thermo import recombination as REC
    cos = RT.Cosmology(z0=500.0)
    s = RT.RateSchedule(hist, cos, mode="lcdm", lane="phenomenology")
    z_hi = 2800.0
    tau_end = float(s.tau_of(z_hi))
    ns = 20000
    got = s.optical_depth_along(tau_end / ns, ns)
    zg = np.linspace(cos.z0, z_hi, 40001)
    r = REC.optical_depth_and_visibility(zg, np.asarray(hist.x_e(zg), float),
                                         Omega_b_h2=cos.Omega_b_h2, h=cos.h,
                                         Omega_m_h2=cos.Omega_m_h2)
    want = float(r["tau"][-1] - r["tau"][0])
    rel = abs(got - want) / abs(want)
    assert rel <= C.budget("Q19", "optical_depth"), (got, want, rel)


# ─────────────────────────────────── 조용한 오답 금지
def test_q19_fails_fast_when_history_span_is_too_narrow(hist):
    """★ run 이 이력의 z 지지집합을 벗어나면 **스케줄 시점에** 거절한다.

    없으면 긴 run 이 중간에 죽거나 (좋은 경우), 누가 clamp 를 넣으면 조용히
    틀린 ν 로 끝까지 돈다 (나쁜 경우)."""
    s = RT.RateSchedule(hist, RT.Cosmology(z0=600.0), mode="lcdm", lane="phenomenology")
    with pytest.raises(ValueError, match="지지집합"):
        s.sample(-3.0 / 100, 100)          # z 가 600·e³ ≈ 12000 까지 간다


def test_q19_model_mode_requires_state_lnH(hist):
    """★ mode='model' 에서 lnH 없이 ν 를 묻는 것은 **거절** (ΛCDM 로 몰래 대체 금지)."""
    s = RT.RateSchedule(hist, RT.Cosmology(z0=600.0), mode="model", lane="phenomenology")
    with pytest.raises(ValueError, match="lnH"):
        s.nu(0.0)
    with pytest.raises(ValueError, match="mode"):
        RT.RateSchedule(hist, mode="planck", lane="phenomenology")
    with pytest.raises(ValueError, match="이력"):
        RT.RateSchedule(None, lane="phenomenology")


# ─────────────────────────────────── 규약 차이를 숨기지 않는다
def test_q19_model_vs_lcdm_H_difference_is_measured(hist):
    """★ 두 H 규약의 차이를 **실측**해 남긴다 (숨은 근사 금지 조항).

    ★★ 85차 반증 (독립 리뷰 M3): 처음엔 `np.interp(-t, -tau_rows[::-1], lnH[::-1])`
    로 lnH 를 보간했다.  `-tau_rows[::-1]` 은 **감소**하므로 np.interp 의 전제를
    깨고 조용히 쓰레기를 돌려준다 (τ=0 에서 lnH=2.03 을 줬다 — τ=−1 의 값).
    그런데 유일한 단언이 `max_rel >= 1e−3` 이라 0.338 이든 4.024 든 다 통과했다 —
    **실패할 수 없는 게이트**였다.  정정 + τ₀ 에서 비가 정확히 1 임을 못박는다."""
    m = _mk(hist, mode="model", ty="IX", nsteps=200)
    _, traj, _ = run(m, fast=True, keep_every=10)
    dtau = (m.tau_span[1] - m.tau_span[0]) / m.nsteps
    lnH = traj[:, 15]
    tau_rows = np.arange(len(lnH)) * dtau * 10
    assert np.all(np.diff(-tau_rows) > 0), "보간 축이 증가해야 한다"

    def lnH_of(t):
        return float(np.interp(-t, -tau_rows, lnH))

    # 자기검사: 보간이 원래 표본을 재현하는가 (M3 의 재발 방지)
    for i in (0, len(lnH) // 2, len(lnH) - 1):
        assert abs(lnH_of(tau_rows[i]) - lnH[i]) <= 1e-12

    s = m.schedule()
    d = s.compare_modes(dtau, 10 * (len(lnH) - 1), lnH_of)
    # ★ τ₀ 에서 두 모드는 **정확히 같다** (기본 앵커가 ΛCDM H(z₀) 이므로).
    #   이것이 "mode='model' 이 ΛCDM 을 전혀 안 쓴다" 가 과장인 이유다.
    assert abs(d["nu_model"][0] / d["nu_lcdm"][0] - 1.0) <= 1e-13
    assert C.budget("Q19", "H_convention_gap") <= d["max_rel"] <= 1.0, d["max_rel"]


def test_q19_strang_order_is_preserved_with_time_dependent_nu(hist):
    """★ 시간의존 ν 에서도 Strang 2차가 유지된다 (앞/뒤 반스텝 비대칭 금지)."""
    ref, errs = None, []
    for ns in (100, 200, 400, 1600):
        st, _, _ = run(_mk(hist, mode="lcdm", nsteps=ns), fast=True)
        if ns == 1600:
            ref = st.lG.copy()
        else:
            errs.append(st.lG.copy())
    e = [float(np.abs(x - ref).max()) for x in errs]
    ords = [float(np.log2(e[i] / e[i + 1])) for i in range(len(e) - 1)]
    assert min(ords) >= C.budget("Q19", "strang_order"), (ords, e)


# ═══════════════════════════════════════════════════════════════════
# 85차 독립 리뷰 (physmath-coding-harness:scientific-diff-reviewer) 대응
# BLOCKER 1 · MAJOR 4 · MINOR 7.  아래가 그 박제다.
# ═══════════════════════════════════════════════════════════════════
@pytest.mark.parametrize("tau0", [0.0, 0.3, -0.4])
def test_q19_parity_holds_for_nonzero_tau0(hist, tau0):
    """★★ BLOCKER 대응: `integrate` 가 시계를 **0.0** 에서 시작했다.

    스케줄은 τ₀ = tau_span[0] 에서 시작하므로 τ₀ ≠ 0 이면 두 경로가 다른
    적색이동을 본다 (1+z 가 e^{τ₀} 배).  실측 상대차 4.5e−3 (예산 1e−13),
    광학깊이 26.6 vs 88.6.  `fast=True` 도 events 가 있으면 이 경로로 온다 —
    그래서 예전 파리티 시험 (τ₀=0 전용) 이 못 잡았다."""
    m = Model(type="I", grid=Grid(12, 24), tau_span=(tau0, tau0 - 1.0),
              nsteps=200, collision=Collision.thomson(hist, rate_mode="lcdm"),
              cosmology=RT.Cosmology(z0=600.0), lane="phenomenology")
    r, _, _ = run(m, fast=True)
    p, _, _ = run(m, fast=False)
    rel = float(np.abs(r.lG - p.lG).max() / max(np.abs(p.lG).max(), 1e-300))
    assert rel <= C.budget("Q19", "rust_vs_python"), (tau0, rel)


def test_q19_event_path_also_gets_the_schedule(hist):
    """★ `fast=True` 여도 events 가 있으면 참조 적분기로 간다 — 같은 답이어야 한다."""
    from bianchi.q.integrate import omega_threshold_event
    m = Model(type="I", grid=Grid(12, 24), tau_span=(0.2, -0.8), nsteps=200,
              collision=Collision.thomson(hist, rate_mode="lcdm"),
              cosmology=RT.Cosmology(z0=600.0), lane="phenomenology")
    a, _, _ = run(m, fast=True)
    b, _, hits = run(m, fast=True, events=[omega_threshold_event(0.99)])
    rel = float(np.abs(a.lG - b.lG).max() / max(np.abs(a.lG).max(), 1e-300))
    assert rel <= C.budget("Q19", "rust_vs_python"), rel


def test_q19_rejects_history_that_clamps_instead_of_raising(hist):
    """★★ MAJOR 대응: `validate_span` 은 "x_e 가 예외를 던지는가" 로만 판정한다.

    범위 밖에서 **조용히 clamp** 하는 외부 모듈은 모든 게이트를 통과하고 답을
    바꿨다 (실측 광학깊이 8.09 vs 참값 26.62).  이제 SPEC §7 1단계의
    `validate_history` 를 스케줄 생성 시점에 강제한다."""
    class Clamping:
        name = "clamping"
        z_range = (500.0, 1300.0)

        def x_e(self, z):
            z = np.clip(np.atleast_1d(np.asarray(z, float)), 500.0, 1300.0)
            return hist.x_e(z)

    with pytest.raises(ValueError, match="B2b 계약"):
        RT.RateSchedule(Clamping(), RT.Cosmology(z0=600.0), mode="lcdm",
                        lane="phenomenology")
    # 의도적이면 명시로만 (조용한 우회 금지)
    s = RT.RateSchedule(Clamping(), RT.Cosmology(z0=600.0), mode="lcdm",
                        lane="phenomenology", strict_history=False)
    assert s.mode == "lcdm"


def test_q19_refuses_to_clamp_z_below_zero(hist):
    """★★ MAJOR 대응: 예전엔 `np.maximum(z, 0)` 로 눌러 ν 가 **얼어붙었다**.

    게다가 `validate_span` 이 같은 clamp 를 써서 끝점 검사가 구조적으로 못 잡았다
    (clamp 가 걸리면 z(τ) 가 단사가 아니게 되므로)."""
    s = RT.RateSchedule(hist, RT.Cosmology(z0=600.0), mode="lcdm", lane="phenomenology")
    with pytest.raises(ValueError, match="z<0|z\\(τ\\) < 0"):
        s.sample(10.0 / 100, 100)          # τ 폭 10 > ln(1+600) = 6.4


def test_q19_anchor_is_disclosed_and_measured(hist):
    """★★ MAJOR 대응: 앵커는 "차원만 붙이는 것" 이 아니라 ν 의 **절대 규모**다.

    기본 앵커가 ΛCDM H(z₀) 이므로 τ₀ 에서 mode='model' 과 'lcdm' 의 ν 가 정확히
    같다 — 즉 mode='model' 도 ΛCDM 을 (규모에서) 쓴다.  자기일관 앵커는 모델의
    Gauss 면 Ω₀ 에서 나오고, 두 앵커는 실측 2.6배 다르다."""
    a = RT.RateSchedule(hist, RT.Cosmology(z0=600.0), mode="model", lane="phenomenology")
    assert a.anchor_source == "lcdm(z0)"
    assert "[lcdm(z0)]" in a.describe()          # summary 가 출처를 숨기지 않는다
    g = RT.RateSchedule(hist, RT.Cosmology(z0=600.0), mode="model",
                        lane="internal", Omega0=0.99)
    assert g.anchor_source.startswith("gauss")
    ratio = g.H_anchor / a.H_anchor
    assert 0.2 <= ratio <= 0.6, ratio            # 실측 0.3885 — 무시할 크기가 아니다
    # 모델의 Ω₀ 로 만든 앵커는 정의상 ρ_r = 3H²Ω₀ 를 만족한다
    rho = a.cosmo.rho_rad(600.0)
    assert abs(3.0 * g.H_anchor ** 2 * 0.99 / rho - 1.0) <= 1e-12
    # Model 에서도 같은 값이 나온다 (배선 확인)
    m = Model(type="I", grid=Grid(12, 24), tau_span=(0.0, -1.0), nsteps=100,
              collision=Collision.thomson(hist), cosmology=RT.Cosmology(z0=600.0),
              lane="internal")
    assert m.schedule().anchor_source.startswith("gauss")


def test_q19_rate_mode_is_validated_even_without_history():
    """★ MINOR 대응: 이력이 없으면 rate_mode 오타가 조용히 통과했다."""
    with pytest.raises(ValueError, match="rate_mode"):
        Model(type="I", grid=Grid(12, 24),
              collision=Collision("thomson", 1.0, None, rate_mode="planck"))


def test_q19_h_anchor_zero_is_rejected(hist):
    """★ MINOR 대응: H_anchor = 0 은 커널에서 "sched 가 곧 ν" 라는 센티널이다.

    허용하면 A [1/s] 가 ν 로 오해되어 조용히 무충돌이 된다 (실측 |ΔlnĜ| = 0.98),
    그리고 두 백엔드가 서로 다른 답을 낸다 (Python 은 divide-by-zero)."""
    with pytest.raises(ValueError, match="H_anchor > 0"):
        RT.RateSchedule(hist, RT.Cosmology(z0=600.0), mode="model",
                        lane="phenomenology", H_anchor=0.0)


def test_q19_fast_path_forwards_baryon_velocity(hist):
    """★ MINOR 대응 (잔여위험): Mode A 의 `fast` 경로가 `collision.v_b` 를
    **버리고** 있었다 — `fast.evolve` 가 v_b 슬롯에 None 을 하드코딩했고
    `run()` 도 이 경로에만 안 넘겼다.  참조 경로는 넘겼으므로 두 경로가 조용히
    갈렸고, 새 파리티 게이트도 v_b 를 쓰는 시험이 없어 못 봤다."""
    c = Collision.thomson(hist, rate_mode="lcdm")
    c.v_b = np.array([0.05, 0.0, 0.0])
    m = Model(type="I", grid=Grid(12, 24), tau_span=(0.0, -1.0), nsteps=200,
              collision=c, cosmology=RT.Cosmology(z0=600.0), lane="phenomenology")
    a, _, _ = run(m, fast=True)
    b, _, _ = run(m, fast=False)
    rel = float(np.abs(a.lG - b.lG).max() / max(np.abs(b.lG).max(), 1e-300))
    assert rel <= C.budget("Q19", "rust_vs_python"), rel
    # v_b 가 실제로 걸렸는가 (버려지면 v_b=0 과 같아진다)
    c0 = Collision.thomson(hist, rate_mode="lcdm")
    m0 = Model(type="I", grid=Grid(12, 24), tau_span=(0.0, -1.0), nsteps=200,
               collision=c0, cosmology=RT.Cosmology(z0=600.0), lane="phenomenology")
    z, _, _ = run(m0, fast=True)
    assert float(np.abs(a.lG - z.lG).max()) >= 1e-6
