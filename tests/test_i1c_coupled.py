"""
I1c · **Einstein-Boltzmann 결합 (untilted class A, 대각 절편)** (67차).

게이트 (PLAN-I1-coupled §1/§2 그대로):
  ① 유체극한: l_max=1 절단 ≡ class_a 차트 (γ=4/3) — 실측 ~1e−10.
  ② freestream: 결합 J(τ) ≡ 특성곡선 역추적 구적 오라클 (I1a back_trace;
     무질량 λ⁻⁴ 축약) — type I (Kasner) 와 **type II (N-항 부호의 심판)**.
  ③ Gauss h⁴: 잔차 수렴 차수 3.8–4.2.
  ④ N on/off: xyz-팔중극이 N 에서만 성장; ρ 는 무감각 (T4 의 동역학 판);
     대각 절편 감시 잔차 (q, π-비대각) 소량 유지.
  ⑤ 팩킹 왕복 + 무질량 별칭·절단 계약.
"""
import numpy as np
import pytest

from bianchi.matter import class_a_char as CH
from bianchi.matter import coupled_class_a as CP
from bianchi.matter import pstf_coeff as PC


def test_fluid_limit_matches_class_a_chart():
    """★★ 게이트 ①: l_max=1 ≡ class_a (γ=4/3), 같은 RK4 격자."""
    import jax
    jax.config.update("jax_enable_x64", True)
    from bianchi.charts import class_a as CA
    chart0 = np.array([0.15, -0.1, 0.4, -0.3, 0.2])
    y0 = CP.isotropic_ic(chart0, 0.0, l_max=1)
    tau, ns = 1.0, 400
    yT = CP.rk4_evolve(y0, 1, tau, ns)
    h = tau / ns
    args = dict(gamma=4.0 / 3.0)

    def f(v):
        return np.asarray(CA.rhs(0.0, CA.StateA.from_array(v), args).as_array())

    v = np.asarray(CA.StateA.of(*chart0).as_array())
    for _ in range(ns):
        k1 = f(v)
        k2 = f(v + 0.5 * h * k1)
        k3 = f(v + 0.5 * h * k2)
        k4 = f(v + h * k3)
        v = v + (h / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
    c5, lnH, Jc = CP.unpack(yT, 1)
    assert np.abs(c5 - v).max() <= 1e-8
    a = CA.aux(CA.StateA.from_array(v), 4.0 / 3.0)
    Om_k = CP.sources_from_J(Jc, lnH, 1)[0]
    assert abs(Om_k - float(a["Omega"])) <= 1e-8


def _interp_bg(traj, tau, l_max):
    """결합 궤적 → (H=1, Σ_we, R=0, N_we)(τ) 선형보간 배경 (τ-정규화 단위)."""
    ns = traj.shape[0] - 1
    ts = np.linspace(0.0, tau, ns + 1)
    c5s = traj[:, :5]

    def bg(t):
        t = min(max(t, 0.0), tau)
        k = min(int(t / tau * ns), ns - 1)
        w = (t - ts[k]) / (ts[k + 1] - ts[k])
        c5 = (1 - w) * c5s[k] + w * c5s[k + 1]
        Sp, Sm = c5[0], c5[1]
        S = np.diag([-2*Sp, Sp + np.sqrt(3)*Sm, Sp - np.sqrt(3)*Sm])
        return 1.0, S, np.zeros(3), c5[2:5]

    return bg


def _oracle_J(traj, tau, l, nq=14):
    """freestream 오라클: 단위방향 역추적 λ(e) — J(l,0)(τ) ∝ ∫dΩ e^l λ⁻⁴."""
    from bianchi.matter.hierarchy_nterm import _grid
    pts, wts = _grid(nq)
    bg = _interp_bg(traj, tau, None)
    P0 = CH.back_trace(pts, bg, 0.0, tau, nsteps=600)
    lam = np.sqrt(np.sum(P0 * P0, axis=1))
    w = wts * lam ** (-4.0)
    if l == 0:
        T = np.array(float(np.sum(w)))
    else:
        T = np.zeros((3,) * l)
        for k in range(len(pts)):
            outer = w[k]
            t = np.array(outer)
            for _ in range(l):
                t = np.multiply.outer(t, pts[k])
            T = T + t
    return PC.to_ccoef(np.asarray(T, float), l)


@pytest.mark.parametrize("name,N0", [("I", [0.0, 0.0, 0.0]),
                                     ("II", [0.6, 0.0, 0.0])])
def test_freestream_vs_characteristics_oracle(name, N0):
    """★★ 게이트 ②: 시험장 극한 (Ω~1e−12) — 결합 계층 ≡ 역추적 구적.
    type II 가 N-항 부호·계수의 **심판** (I1a 커널과 독립 경로 대조)."""
    chart0 = np.array([0.2, -0.12, *N0])
    lmax, tau, ns = 4, 0.8, 400
    rho0 = 4.0 * np.pi
    y0 = CP.isotropic_ic(chart0, 0.0, lmax, rho=rho0 * 1e-12)
    yT, traj = CP.rk4_evolve(y0, lmax, tau, ns, keep=True)
    _, _, Jc = CP.unpack(yT, lmax)
    worst = 0.0
    for l in (0, 2, 3):
        got = np.asarray(Jc[(l, 0)]) / 1e-12
        want = _oracle_J(traj, tau, l)
        worst = max(worst, float(np.abs(got - want).max()))
    assert worst <= 2e-4, (name, worst)


def test_gauss_residual_h4_convergence():
    """★ 게이트 ③: on-shell IC — Gauss 잔차의 h⁴ 수렴 (차수 3.5–4.5)."""
    chart0 = np.array([0.18, -0.09, 0.5, -0.25, 0.15])
    y0 = CP.isotropic_ic(chart0, 0.0, l_max=3)
    tau = 0.8
    res = []
    for ns in (50, 100, 200, 400):
        yT = CP.rk4_evolve(y0, 3, tau, ns)
        res.append(abs(CP.gauss_residual(yT, 3)))
    orders = [np.log2(res[k] / res[k + 1]) for k in range(3)]
    assert res[0] > res[-1]
    assert all(3.5 <= o <= 4.5 for o in orders[:2]), (res, orders)


def test_n_term_effect_selective():
    """★ 게이트 ④: II 배경 — xyz-팔중극은 N 에서만 성장, ρ 는 무감각;
    대각 절편 감시 잔차 소량."""
    chart0 = np.array([0.2, -0.12, 0.6, 0.0, 0.0])
    lmax, tau, ns = 4, 0.8, 300
    y0 = CP.isotropic_ic(chart0, 0.0, lmax)
    y_on = CP.rk4_evolve(y0, lmax, tau, ns, nterm_on=True)
    y_off = CP.rk4_evolve(y0, lmax, tau, ns, nterm_on=False)
    _, lnH_on, J_on = CP.unpack(y_on, lmax)
    _, lnH_off, J_off = CP.unpack(y_off, lmax)
    oct_on = float(np.abs(J_on[(3, 0)]).max())
    oct_off = float(np.abs(J_off[(3, 0)]).max())
    assert oct_on > 1e-4 and oct_off <= 1e-15          # 팔중극 = N 전용
    rho_on = float(J_on[(0, 0)][0])
    rho_off = float(J_off[(0, 0)][0])
    assert abs(rho_on - rho_off) / rho_off <= 2e-3     # ρ 무감각 (2차 되먹임뿐)
    m = CP.monitors(y_on, lmax)
    assert m["q_resid"] <= 1e-12 and m["pi_offdiag"] <= 1e-10


def test_pack_roundtrip_and_truncation_contract():
    """★ 게이트 ⑤: 팩킹 왕복 + 별칭 (l>l_max → 0, (l,i≥1) → i=0 층)."""
    rng = np.random.default_rng(3)
    chart5 = rng.standard_normal(5)
    Jc = {(l, 0): rng.standard_normal(2*l + 1) for l in range(4)}
    y = CP.pack(chart5, 0.3, Jc, 3)
    c5, lnH, J2 = CP.unpack(y, 3)
    assert np.abs(c5 - chart5).max() == 0.0 and lnH == 0.3
    for l in range(4):
        assert np.abs(J2[(l, 0)] - Jc[(l, 0)]).max() == 0.0
    A = CP._AliasJ(J2, 3)
    assert np.abs(A[(2, 5)] - J2[(2, 0)]).max() == 0.0
    assert np.abs(A[(5, 0)]).max() == 0.0
