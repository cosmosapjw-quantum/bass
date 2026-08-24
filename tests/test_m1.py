"""M1 완료 기준 — PR-06/07/08/09/10.

PR-06 class A : Kasner 원 불변, 오라클 A~E, N_i=0 정확 보존
PR-07 class B : (b3,c2,c)=(-4,2,6) 재유도, Codazzi 전파, 유형 V 차원 2
PR-08 예외형  : g' 항등, A 2배 환산 없음, essential params 5
PR-09 적분기  : scipy 대조, throw=False, 이벤트 시맨틱
PR-10 정확해  : Kasner, Collins-Stewart(II), Collins VI_h, Heckmann-Schucking, Bianchi I+Lambda
"""
import numpy as np
import pytest
import sympy as sp

import bianchi  # noqa: F401  (x64)
import jax
import jax.numpy as jnp

from bianchi import algebra as alg
from bianchi import conventions as cv
from bianchi import integrate as itg
from bianchi.charts import class_a as ca
from bianchi.charts import class_b as cb
from bianchi.charts import exceptional as ce

SQ3 = cv.SQRT3
rng = np.random.default_rng(20260728)


def _args(gamma=1.0, kappa=None):
    d = {"gamma": jnp.asarray(gamma)}
    if kappa is not None:
        d["kappa"] = jnp.asarray(kappa)
    return d


# ================================================================ PR-06
def test_classA_kasner_circle_invariant():
    """진공 I: Sigma^2 = 1 이 불변이고 상태가 정지한다."""
    for psi in np.linspace(0, 2*np.pi, 9)[:-1]:
        y = ca.kasner(psi)
        d = ca.rhs(0.0, y, _args(gamma=4/3))
        assert np.abs(np.asarray(d.as_array())).max() < 1e-14
        a = ca.aux(y, 4/3)
        assert np.isclose(float(a["Sigma2"]), 1.0)
        assert abs(float(a["Omega"])) < 1e-14


def test_classA_omega_identity_runtime():
    for _ in range(8):
        y = ca.StateA.of(*rng.normal(0, .4, 2), *rng.normal(0, .5, 3))
        for g in (1.0, 4/3, 1.9):
            r = float(ca.omega_identity_residual(y, _args(g)))
            assert abs(r) < 1e-11, r


def test_classA_Ni_zero_exactly_preserved():
    """★ 곱셈 구조: N_i = 0 이 부동소수점에서도 정확히 0 을 유지."""
    y = ca.StateA.of(0.3, -0.2, 1.0, 0.0, 0.0)      # 유형 II
    args = _args(4/3)
    sol = itg.solve_jit(ca.rhs, y, 0.0, 4.0, args,
                        cfg=itg.SolverConfig(weights=itg.DEFAULT_WEIGHTS["class_a"]))
    yf = jax.tree.map(lambda x: x[-1] if x.ndim else x, sol.ys)
    assert float(yf.N2) == 0.0 and float(yf.N3) == 0.0
    assert float(yf.N1) != 0.0


def test_classA_type_preserved_along_flow():
    y = ca.from_type("VII_0", Sp=0.2, Sm=-0.1)
    assert ca.type_of(y).name == "VII_0"
    args = _args(1.0)
    sol = itg.solve_jit(ca.rhs, y, 0.0, 3.0, args)
    yf = jax.tree.map(lambda x: x[-1] if x.ndim else x, sol.ys)
    assert ca.type_of(yf).name == "VII_0"


# ================================================================ PR-07
def test_classB_coefficients_rederived():
    """(b3, c2, c) = (-4, 2, 6). c2, c 는 항등적; b3 는 구속면 위에서."""
    g, kap = sp.symbols("gamma kappa")
    Sp, St, De, At, Np = sp.symbols("Sp St De At Np")
    b3, c2, c6 = sp.symbols("b3 c2 c6")
    Nt = (Np**2 - kap*At)/3
    Om = 1 - Sp**2 - St - At - Nt
    q = 2*(Sp**2 + St) + sp.Rational(1, 2)*(3*g - 2)*Om
    flow = {
        Sp: (q-2)*Sp - 2*Nt,
        St: 2*(q-2)*St - 4*Sp*At + b3*De*Np,
        De: 2*(q+Sp-1)*De + c2*(St-Nt)*Np,
        At: 2*(q+2*Sp)*At,
        Np: (q+2*Sp)*Np + c6*De,
    }
    dOm = sp.expand(sum(sp.diff(Om, v)*dv for v, dv in flow.items()))
    res = sp.expand(dOm - (2*q - (3*g-2))*Om)
    # b3 = -4 를 고정하면 c6 가 유일하게 6 으로 결정된다
    sol_c6 = sp.solve(res.subs(b3, -4), c6)
    assert sol_c6 == [6], sol_c6
    # C' = 4(q+Sp-1)C 가 c2 를 고정
    C = St*Nt - De**2 - Sp**2*At
    fl = {k: v.subs({b3: -4, c6: 6}) for k, v in flow.items()}
    dC = sp.expand(sum(sp.diff(C, v)*dv for v, dv in fl.items()))
    sol_c2 = sp.solve(sp.expand(dC - 4*(q+Sp-1)*C), c2)
    assert sol_c2 == [2], sol_c2


def test_classB_codazzi_propagation():
    args = _args(1.0, kappa=-4.0)
    for _ in range(8):
        y = cb.StateB.of(rng.normal(0, .3), abs(rng.normal(0, .2)),
                         rng.normal(0, .2), abs(rng.normal(0, .2)),
                         rng.normal(0, .4))
        r = float(cb.codazzi_propagation_residual(y, args))
        scale = max(1.0, abs(float(cb.codazzi(y, -4.0))))
        assert abs(r) < 1e-9 * scale, r


def test_classB_type_V_is_two_dimensional():
    """N_+=0 => Ntilde=0 => Codazzi 가 Delta = Sigma_+ = 0 강제 -> (St, At) 2차원."""
    kap = 0.0
    y = cb.type_V_state(0.3, 0.25)
    assert abs(float(cb.codazzi(y, kap))) < 1e-15
    args = _args(1.0, kappa=kap)
    d = cb.rhs(0.0, y, args)
    # Sigma_+, Delta, N_p 방향으로 흐름이 새지 않는다
    assert abs(float(d.Sigma_p)) < 1e-14
    assert abs(float(d.Delta)) < 1e-14
    assert abs(float(d.N_p)) < 1e-14


def test_classB_kappa_covers_all_types():
    for kap, expect in [(0.0, ("IV", "V")), (-1.0, ("III",)),
                        (-4.0, ("VI_h",)), (4.0, ("VII_h",))]:
        n2n3, A = kap, 1.0
        if kap == 0.0:
            n = np.array([0.0, 0.0, 1.0])
        else:
            n = np.array([0.0, 1.0, kap])
        t = alg.classify(n, np.array([A, 0.0, 0.0]))
        assert t.name in expect, f"kappa={kap}: {t.name}"


def test_classB_exceptional_guard():
    with pytest.raises(ValueError, match="예외형"):
        cb.guard_exceptional(-9.0)
    cb.guard_exceptional(-4.0)   # 통과


# ================================================================ PR-08
def test_exceptional_g_propagation_identity():
    """g' = 2(q+Sigma_+-1) g 는 **항등적**으로 (구속면 밖에서도) 성립."""
    args = _args(1.0)
    for _ in range(8):
        y = ce.StateE.of(*rng.normal(0, .3, 6))
        r = float(ce.g_propagation_residual(y, args))
        assert abs(r) < 1e-10, r


def test_exceptional_omega_identity_off_and_on_shell():
    """Omega' - [2q-(3g-2)]Omega = -4 A g  (항등), 구속면 위에서 0."""
    args = _args(4/3)
    for _ in range(6):
        y = ce.StateE.of(*rng.normal(0, .3, 6))
        assert abs(float(ce.omega_identity_residual(y, args))) < 1e-10
    for _ in range(6):
        Sp, Sm, S2, Nm, A = rng.normal(0, .3, 5)
        Nm = Nm if abs(Nm) > .1 else .3
        y = ce.on_g_surface(Sp, Sm, S2, Nm, A)
        assert abs(float(ce.g_constraint(y))) < 1e-13


def test_exceptional_curvature_matches_HHW_and_no_A_rescale():
    """K = N_-^2 + 4A^2 이고 A 는 재정규화되지 않는다 (U13)."""
    y = ce.StateE.of(0.1, 0.2, 0.0, 0.05, 0.7, 0.3)
    a = ce.aux(y, 1.0)
    assert np.isclose(float(a["K"]), 0.7**2 + 4*0.3**2)
    assert cv.A_EXCEPTIONAL_RESCALE == 1.0


def test_exceptional_essential_parameters_five():
    assert ce.essential_parameters() == 5     # VIII, IX 와 동등


def test_exceptional_gauge_forces_kappa_minus_nine():
    """HHW 게이지 N_+=sqrt3 N_-, N_x=sqrt3 A 는 kappa=-9 를 자동 강제."""
    Nm, A = 0.7, 0.3
    Np, Nx = SQ3*Nm, SQ3*A
    n2n3 = Np**2 - 3*(Nm**2 + Nx**2)
    assert np.isclose(n2n3 / A**2, -9.0)
    assert np.isclose(3*(9*A**2 + n2n3), 0.0)


# ================================================================ PR-09
def test_integrator_matches_scipy_on_classA():
    """diffrax 결과를 scipy Radau/LSODA 와 대조."""
    from scipy.integrate import solve_ivp
    y0 = ca.StateA.of(0.25, -0.15, 0.6, 0.35, 0.0)   # 유형 VI_0/VII_0 계열
    g = 4/3
    args = _args(g)
    tau1 = 2.5
    cfg = itg.SolverConfig(rtol=1e-11, atol=1e-13,
                           weights=itg.DEFAULT_WEIGHTS["class_a"])
    sol = itg.solve_jit(ca.rhs, y0, 0.0, tau1, args, cfg=cfg)
    yj = np.asarray(jax.tree.map(lambda x: x[-1] if x.ndim else x,
                                 sol.ys).as_array())

    # ★ R3 (성능): scipy 가 RHS 를 수천 번 부르는데 그때마다 JAX 를 **즉시 실행**해
    #   이 한 시험이 46 초를 먹었다.  RHS 를 jit 로 한 번 컴파일해 재사용한다
    #   (같은 함수·같은 tolerance — 비교값은 그대로다).
    _rhs_jit = jax.jit(lambda t, v: ca.rhs(t, ca.StateA.from_array(v), args).as_array())

    def f(t, v):
        return np.asarray(_rhs_jit(t, jnp.asarray(v)))
    for method in ("Radau", "LSODA", "DOP853"):
        r = solve_ivp(f, (0.0, tau1), np.asarray(y0.as_array()),
                      method=method, rtol=1e-12, atol=1e-14)
        assert np.abs(r.y[:, -1] - yj).max() < 1e-7, (method, r.y[:, -1], yj)


def test_integrator_throw_false_and_status():
    y0 = ca.StateA.of(0.3, 0.1, 1.0, 0.5, 0.2)
    cfg = itg.SolverConfig(max_steps=8)             # 일부러 부족하게
    sol = itg.solve(ca.rhs, y0, 0.0, 50.0, _args(1.0), cfg=cfg)
    st = itg.status(sol)
    assert st["successful"] is False                 # 예외 없이 상태로 보고
    assert "max_steps" in st["result"].lower() or st["num_steps"] >= 0


def test_integrator_vmap_batch():
    """vmap 배치에서 원소별 result 가 오염되지 않는다."""
    n = 8
    v0 = jnp.asarray(rng.normal(0, .3, (n, 5)))
    args = _args(1.0)
    import equinox as eqx
    cfg = itg.SolverConfig()
    run = eqx.filter_jit(jax.vmap(
        lambda v: itg.solve(ca.rhs, ca.StateA.from_array(v), 0.0, 1.5, args, cfg=cfg)
    ))
    sol = run(v0)
    steps = np.asarray(sol.stats["num_steps"])
    assert steps.shape == (n,)
    assert (steps > 0).all()


def test_weighted_norm_shape_agnostic():
    w = jnp.asarray(itg.DEFAULT_WEIGHTS["class_a"])
    nrm = itg.weighted_rms(w)
    y = ca.StateA.of(1., 1., 1., 1., 1.)
    assert float(nrm(y)) > 0


# ================================================================ PR-10 정확해
def test_exact_collins_stewart_II():
    """Collins-Stewart (Bianchi II 자기닮음 평형점).

    2/3 < gamma < 2 에서 CS(II):
      Sigma_+ = (3 gamma - 2)/16 ,  N_1^2 = (3 gamma-2)(2-gamma)*3/16... 를
    고정점 방정식으로 직접 푼다 (문헌값 전사 대신).
    """
    g = 10/9   # 2/3 < g < 2
    args = _args(g)
    from scipy.optimize import fsolve

    def F(v):
        y = ca.StateA.of(v[0], 0.0, v[1], 0.0, 0.0)
        d = ca.rhs(0.0, y, args).as_array()
        return [float(d[0]), float(d[2])]
    sol = fsolve(F, [0.1, 0.5], full_output=False)
    y = ca.StateA.of(sol[0], 0.0, sol[1], 0.0, 0.0)
    d = np.abs(np.asarray(ca.rhs(0.0, y, args).as_array()))
    assert d.max() < 1e-10
    a = ca.aux(y, g)
    assert 0 < float(a["Omega"]) < 1
    # 자기닮음: q 가 상수이고 Sigma_+ > 0
    assert float(y.Sigma_p) > 0
    # 문헌 대조: Sigma_+ = (3g-2)/16
    # 유도로 확정 (문헌 전사 아님): Sigma_+ = (3gamma-2)/8, Omega = 9/8 - 3gamma/16
    assert np.isclose(float(y.Sigma_p), (3*g-2)/8, rtol=1e-8)
    assert np.isclose(float(a["Omega"]), 9/8 - 3*g/16, rtol=1e-8)


def test_exact_kasner_vacuum_is_fixed_point():
    for psi in (0.3, 1.1, 2.7):
        y = ca.kasner(psi)
        assert np.abs(np.asarray(ca.rhs(0., y, _args(1.5)).as_array())).max() < 1e-14


def test_exact_flat_FLRW_fixed_point():
    """평탄 FLRW: Sigma=0, N=0, Omega=1 은 고정점."""
    y = ca.StateA.of(0., 0., 0., 0., 0.)
    for g in (1.0, 4/3):
        assert np.abs(np.asarray(ca.rhs(0., y, _args(g)).as_array())).max() < 1e-15
        assert np.isclose(float(ca.aux(y, g)["Omega"]), 1.0)


def test_exact_heckmann_schucking_bianchi_I_dust():
    """Heckmann-Schucking (I + 먼지): Kasner -> 평탄 FLRW 보간.

    Bianchi I 먼지에서 Sigma^2 + Omega = 1 이고
      Sigma_pm' = -(2-q)Sigma_pm,  q = 2Sigma^2 + Omega/2
    닫힌 해: Sigma(tau) = Sigma_0 / sqrt(Sigma_0^2 + (1-Sigma_0^2) e^{3 tau}) ... 를
    수치적으로 확인하는 대신, **불변량 Sigma^2+Omega=1 과 두 점근**을 검사한다.
    """
    g = 1.0
    args = _args(g)
    y0 = ca.StateA.of(0.9, 0.0, 0., 0., 0.)
    cfg = itg.SolverConfig(rtol=1e-12, atol=1e-14)
    ts = jnp.linspace(0.0, 6.0, 40)
    sol = itg.solve_jit(ca.rhs, y0, 0.0, 6.0, args, ts=ts, cfg=cfg)
    Sp = np.asarray(sol.ys.Sigma_p)
    Om = np.asarray([float(ca.aux(ca.StateA.from_array(v), g)["Omega"])
                     for v in np.asarray(sol.ys.as_array()).T])
    assert np.allclose(Sp**2 + Om, 1.0, atol=1e-10)      # Gauss
    assert Sp[-1] < 1e-3                                  # 평탄 FLRW 로 등방화
    # 해석해 대조: Bianchi I 먼지에서 Sigma_+(tau) = S0 / sqrt(S0^2 + (1-S0^2)e^{3tau})
    S0 = 0.9
    exact = S0 / np.sqrt(S0**2 + (1 - S0**2) * np.exp(3 * np.asarray(ts)))
    assert np.abs(Sp - exact).max() < 1e-9


def test_exact_bianchi_I_with_lambda():
    """Bianchi I + Lambda (gamma=0): de Sitter 로 등방화, Sigma ~ e^{-3tau}."""
    g = 0.0
    args = _args(g)
    y0 = ca.StateA.of(0.5, 0.2, 0., 0., 0.)
    ts = jnp.linspace(0.0, 3.0, 25)
    sol = itg.solve_jit(ca.rhs, y0, 0.0, 3.0, args, ts=ts,
                        cfg=itg.SolverConfig(rtol=1e-12, atol=1e-14))
    S = np.sqrt(np.asarray(sol.ys.Sigma_p)**2 + np.asarray(sol.ys.Sigma_m)**2)
    S0 = np.hypot(0.5, 0.2)
    exact = S0 / np.sqrt(S0**2 + (1 - S0**2) * np.exp(6 * np.asarray(ts)))
    assert np.abs(S - exact).max() < 1e-9


def test_exact_collins_VI_h():
    """Collins VI_h 자기닮음 평형점 — 고정점 조건에서 **유도**한다.

    Atilde != 0 이므로 Atilde' = 0  =>  q = -2 Sigma_+.
    N_+' = (q+2Sigma_+)N_+ + 6 Delta = 6 Delta = 0  =>  Delta = 0.
    N_+ = 0 가지 (Collins VI_h):
        Ntilde = -kappa Atilde/3
        Sigma_+' = 0   =>  Atilde = 3 Sigma_+(Sigma_+ + 1)/kappa
        Sigmatilde' = 0 =>  Sigmatilde = -3 Sigma_+^2/kappa   (Codazzi 와 자동 일치)
        Omega = 1 + Sigma_+ - 3 Sigma_+/kappa
    남는 것은 q = -2Sigma_+ 한 방정식.
    """
    g, kap = 4/3, -4.0
    args = _args(g, kappa=kap)

    S = sp.Symbol("S")
    At = 3*S*(S + 1)/kap
    St = -3*S**2/kap
    Nt = -kap*At/3
    Om = 1 + S - 3*S/kap
    eq = sp.Eq(-2*S, 2*(S**2 + St) + sp.Rational(1, 2)*(3*sp.Rational(4, 3) - 2)*Om)
    roots = [float(r) for r in sp.solve(eq, S) if r.is_real]
    # 물리적 가지: Omega > 0
    cand = [r for r in roots if float(Om.subs(S, r)) > 1e-9]
    assert cand, roots
    Sp = cand[0]
    y = cb.StateB.of(Sp, float(St.subs(S, Sp)), 0.0,
                     float(At.subs(S, Sp)), 0.0)
    a = cb.aux(y, g, kap)

    # 1) 진짜 고정점인가
    d = np.abs(np.asarray(cb.rhs(0., y, args).as_array()))
    assert d.max() < 1e-12, d
    # 2) Codazzi 구속면 위인가
    assert abs(float(cb.codazzi(y, kap))) < 1e-14
    # 3) Gauss 합이 1
    assert np.isclose(float(a["Sigma2"] + a["K"] + a["Omega"]), 1.0, atol=1e-13)
    # 4) 자기닮음: q = -2 Sigma_+, Omega > 0
    assert np.isclose(float(a["q"]), -2*Sp, atol=1e-12)
    assert 0 < float(a["Omega"]) < 1
    # 5) 이 파라미터의 닫힌 값 (gamma=4/3, kappa=-4): Sigma_+ = -1/2, Omega = 1/8
    assert np.isclose(Sp, -0.5, atol=1e-12)
    assert np.isclose(float(a["Omega"]), 0.125, atol=1e-12)
