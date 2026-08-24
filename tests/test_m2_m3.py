"""M2+M3 완료 기준 — PR-11/12/13/14/15/16/17."""
import numpy as np
import pytest
import jax
import jax.numpy as jnp

import bianchi  # noqa: F401
from bianchi import algebra as alg
from bianchi import constraints as con
from bianchi import conventions as cv
from bianchi import integrate as itg
from bianchi.charts import class_a as ca
from bianchi.charts import class_b as cb
from bianchi.charts import class_b_tilted as cbt
from bianchi.charts import exceptional as ce
from bianchi.charts import general as cg
from bianchi.matter import fluid as fl

rng = np.random.default_rng(7)
SQ3 = cv.SQRT3


def _args(gamma=1.0, **kw):
    d = {"gamma": jnp.asarray(gamma)}
    d.update({k: jnp.asarray(v) for k, v in kw.items()})
    return d


# ================================================================ PR-11
def test_general_curvature_matches_closed_form():
    for _ in range(6):
        N = rng.normal(0, .5, (3, 3)); N = 0.5*(N+N.T)
        A = rng.normal(0, .4, 3)
        Ric = np.asarray(cg.ricci3(jnp.asarray(N), jnp.asarray(A)))
        assert np.isclose(np.trace(Ric),
                          float(cg.R3_closed(jnp.asarray(N), jnp.asarray(A))))


def test_general_unit_three_sphere():
    N = jnp.eye(3) * 2.0
    Ric = cg.ricci3(N, jnp.zeros(3))
    assert np.allclose(np.asarray(Ric), 2*np.eye(3), atol=1e-13)


def test_general_reproduces_class_a_rhs():
    """★ Layer 0 <-> Layer 1 교차검증 (PR-13 의 핵심)."""
    for _ in range(8):
        yA = ca.StateA.of(*rng.normal(0, .4, 5))
        args = _args(4/3)
        dA = ca.rhs(0., yA, args)
        yG = cg.from_class_a(yA)
        dG = cg.rhs(0., yG, args)
        back = cg.to_class_a(dG)
        assert np.abs(np.asarray(back.as_array()) -
                      np.asarray(dA.as_array())).max() < 1e-12


def test_general_class_a_trajectory_agreement():
    yA = ca.StateA.of(0.2, -0.1, 0.5, 0.3, 0.0)
    args = _args(1.0)
    cfgA = itg.SolverConfig(rtol=1e-11, atol=1e-13)
    solA = itg.solve_jit(ca.rhs, yA, 0., 2.0, args, cfg=cfgA)
    yAf = jax.tree.map(lambda x: x[-1] if x.ndim else x, solA.ys)
    solG = itg.solve_jit(cg.rhs, cg.from_class_a(yA), 0., 2.0, args, cfg=cfgA)
    yGf = jax.tree.map(lambda x: x[-1] if x.ndim else x, solG.ys)
    assert np.abs(np.asarray(cg.to_class_a(yGf).as_array())
                  - np.asarray(yAf.as_array())).max() < 1e-8


def test_general_constraints_zero_on_class_a_data():
    yA = ca.StateA.of(0.3, 0.15, 0.7, -0.4, 0.2)
    yG = cg.from_class_a(yA)
    c = cg.constraint_vector(yG, _args(1.0))
    assert np.abs(np.asarray(c)).max() < 1e-13


def test_general_type_drift_diagnostics():
    n, a = alg.CANONICAL["VI_h"]
    d = alg.type_drift(np.diag(n), a, kappa0=alg.kappa_basis_independent(np.diag(n), a))
    assert d["jacobi_res"] < 1e-14
    assert d["kappa_rel_err"] < 1e-14


# ================================================================ PR-12
def test_projection_reduces_codazzi_violation():
    kap = -4.0
    args = _args(1.0, kappa=kap)
    y, _ = cb.on_codazzi_surface(0.2, 0.3, 0.25, 0.5, kap)
    # 일부러 구속을 깨뜨린다
    bad = cb.StateB.of(y.Sigma_p, y.Sigma_tilde, y.Delta + 0.05,
                       y.A_tilde, y.N_p)
    c0 = abs(float(cb.codazzi(bad, kap)))
    proj = con.make_projector(cb)
    fixed = proj(bad, args)
    c1 = abs(float(cb.codazzi(fixed, kap)))
    assert c0 > 1e-3 and c1 < 1e-12, (c0, c1)


def test_projection_suppresses_exponential_growth():
    """구속 오차의 지수 증폭이 투영으로 억제됨을 실증."""
    kap = -4.0
    args = _args(1.0, kappa=kap)
    y0, _ = cb.on_codazzi_surface(0.15, 0.25, 0.2, 0.4, kap)
    y0 = cb.StateB.of(y0.Sigma_p, y0.Sigma_tilde, y0.Delta + 1e-7,
                      y0.A_tilde, y0.N_p)
    cfg = itg.SolverConfig(rtol=1e-10, atol=1e-12)
    _, res_no = con.solve_with_projection(cb, cb.rhs, y0, 0., 6., args,
                                          n_chunks=12, cfg=cfg, project_every=False)
    _, res_yes = con.solve_with_projection(cb, cb.rhs, y0, 0., 6., args,
                                           n_chunks=12, cfg=cfg, project_every=True)
    assert float(res_yes[-1]) < float(res_no[-1])
    assert float(res_yes[-1]) < 1e-10


def test_amplification_rate_formula():
    kap = -4.0
    args = _args(1.0, kappa=kap)
    y = cb.StateB.of(0.2, 0.3, 0.1, 0.2, 0.4)
    a = cb.aux(y, 1.0, kap)
    assert np.isclose(float(con.amplification_rate(cb, y, args)),
                      4.0*(float(a["q"]) + 0.2 - 1.0))


# ================================================================ PR-14/15 tilt
def test_tilt_boundaries_invariant():
    """V=0, V=1 이 둘 다 불변 경계."""
    Sigma = jnp.asarray(rng.normal(0, .3, (3, 3)))
    Sigma = 0.5*(Sigma+Sigma.T); Sigma = Sigma - jnp.trace(Sigma)*jnp.eye(3)/3
    A = jnp.asarray(rng.normal(0, .3, 3))
    for g in (0.8, 4/3, 1.9):
        f0 = fl.TiltedFluid.of(g, 0.3, jnp.zeros(3))
        s0 = fl.sources(f0, Sigma, A)
        assert abs(float(fl.dV2(f0, s0))) < 1e-15
        c = jnp.asarray([1., 0., 0.])
        f1 = fl.TiltedFluid.of(g, 0.3, c)
        s1 = fl.sources(f1, Sigma, A)
        assert abs(float(fl.dV2(f1, s1))) < 1e-13


def test_tilt_isotropic_limit_gamma_four_thirds():
    """등방극한: (V^2)' 의 부호가 gamma = 4/3 에서 바뀐다."""
    Z3 = jnp.zeros((3, 3)); Z1 = jnp.zeros(3)
    for g, sign in [(1.2, -1), (4/3, 0), (1.6, +1)]:
        f = fl.TiltedFluid.of(g, 0.4, jnp.asarray([0.3, 0., 0.]))
        s = fl.sources(f, Z3, Z1)
        d = float(fl.dV2(f, s))
        if sign == 0:
            assert abs(d) < 1e-14
        else:
            assert np.sign(d) == sign, (g, d)


def test_omega_prime_uses_G_plus_not_G_minus():
    """★ U4: 분모가 G_+ 임을 코드가 실제로 쓰는지 확인."""
    g, Om = 1.5, 0.4
    v = jnp.asarray([0.3, 0.1, -0.2])
    Sigma = jnp.diag(jnp.asarray([0.2, -0.1, -0.1]))
    A = jnp.asarray([0.25, 0., 0.])
    f = fl.TiltedFluid.of(g, Om, v)
    s = fl.sources(f, Sigma, A)
    q = fl.deceleration(float(jnp.trace(Sigma@Sigma)/6), [(s, g)])
    got = float(fl.dOmega(f, s, q))
    V2 = float(v @ v)
    brace = (2*q - (3*g-2) + 2*g*float(s["Adv"])
             + (2*q*(g-1) - (2-g))*V2 - g*float(s["SV2"]))
    assert np.isclose(got, Om/fl.G_plus(g, V2)*brace)
    assert not np.isclose(got, Om/fl.G_minus(g, V2)*brace)


def test_q_at_extreme_tilt_is_gamma_independent():
    """q|_{V=1} = 2 Sigma^2 + Omega  (null fluid, gamma_eff = 4/3)."""
    Sigma = jnp.diag(jnp.asarray([0.3, -0.2, -0.1]))
    Sigma2 = float(jnp.trace(Sigma@Sigma)/6)
    A = jnp.zeros(3); Om = 0.35
    vals = []
    for g in (0.5, 1.0, 4/3, 1.9):
        f = fl.TiltedFluid.of(g, Om, jnp.asarray([1., 0., 0.]))
        s = fl.sources(f, Sigma, A)
        vals.append(fl.deceleration(Sigma2, [(s, g)]))
    assert np.allclose(vals, vals[0], atol=1e-12)
    assert np.isclose(vals[0], fl.q_at_extreme_tilt(Sigma2, Om))


def test_omega_nonzero_on_extreme_tilt_face():
    """★ U7: Omega 는 V=1 면에서 0 이 되지 않는다."""
    Sigma = jnp.diag(jnp.asarray([0.3, -0.2, -0.1]))
    A = jnp.asarray([0.2, 0., 0.]); Om = 0.35
    g = 1.4
    f = fl.TiltedFluid.of(g, Om, jnp.asarray([1., 0., 0.]))
    s = fl.sources(f, Sigma, A)
    q = fl.deceleration(float(jnp.trace(Sigma@Sigma)/6), [(s, g)])
    dOm = float(fl.dOmega(f, s, q))
    expect = fl.dOmega_at_extreme_tilt(Om, q, float(A[0]), float(Sigma[0, 0]))
    assert np.isclose(dOm, expect, rtol=1e-10)
    assert abs(dOm) > 0          # Omega' != 0 -> Omega 가 붙잡히지 않는다


def test_tilt_guards_report_degeneracies():
    r = fl.guard_report(2.0, 1.0)
    assert bool(r["stiff_extreme"])            # G_- = 0
    r2 = fl.guard_report(1e-9, 1.0)
    assert bool(r2["zero_gamma_extreme"])      # G_+ -> 0
    r3 = fl.guard_report(4/3, 0.2)
    assert not bool(r3["stiff_extreme"]) and not bool(r3["zero_gamma_extreme"])


# ================================================================ PR-16
def test_tilted_classB_codazzi_ratio_minus_three():
    """유도 Codazzi = -3 x Hervik (C_2,C_3,C_4). 3성분 전부."""
    args = _args(1.3)
    for _ in range(6):
        y = cbt.StateBT.of(*rng.normal(0, .25, 5), 0.4, 0.3, 0.35,
                           *rng.normal(0, .15, 3))
        c = cbt.constraints(y, args)
        d = np.asarray(cbt.codazzi_derived(y, args))
        lit = np.array([float(c["C2"]), float(c["C3"]), float(c["C4"])])
        nz = np.abs(lit) > 1e-9
        assert np.allclose(d[nz] / lit[nz], -3.0, rtol=1e-8), (d, lit)


def test_tilted_classB_gauge_rotations_all_three():
    y = cbt.StateBT.of(0.1, 0.2, 0.15, -0.1, 0.05, 0.4, 0.3, 0.35, .1, .05, -.05)
    R = np.asarray(cbt.gauge_rotations(y))
    assert R.shape == (3,) and np.abs(R).min() > 0
    # v1.1 부호 정정 (외부검토 R1): R_2 = -sqrt3 Sigma_13
    assert np.isclose(R[1], -SQ3 * float(y.Sigma_13))


def test_tilted_classB_sigma_p_has_rotation_term():
    """★ 함정 2: Sigma_+' 의 3(S12^2+S13^2) 항이 실제로 존재하는지."""
    base = dict(Sp=0.1, Sm=0.05, S23=0.02, N=0.4, lam=0.3, A=0.35)
    args = _args(1.0, Omega=0.2)
    y0 = cbt.StateBT.of(base["Sp"], base["Sm"], 0.0, 0.0, base["S23"],
                        base["N"], base["lam"], base["A"], 0., 0., 0.)
    y1 = cbt.StateBT.of(base["Sp"], base["Sm"], 0.3, 0.2, base["S23"],
                        base["N"], base["lam"], base["A"], 0., 0., 0.)
    d0 = float(cbt.rhs(0., y0, args).Sigma_p)
    d1 = float(cbt.rhs(0., y1, args).Sigma_p)
    # q 도 바뀌므로 정확한 3(S12^2+S13^2) 만 분리할 수는 없지만, 존재는 확인 가능
    assert d1 != d0
    a0, a1 = cbt.aux(y0, args), cbt.aux(y1, args)
    diff = d1 - d0 - (float(a1["q"]) - float(a0["q"])) * base["Sp"]
    assert np.isclose(diff, 3.0*(0.3**2 + 0.2**2), rtol=1e-8)


def test_tilted_classB_sigma23_coefficient_is_2sqrt3():
    """의심받았던 +2 sqrt3 lambda Sigma_-^2 항의 계수 확인."""
    args = _args(1.0, Omega=0.0)
    common = dict(Sp=0.0, S12=0.0, S13=0.0, S23=0.0, N=0.0, A=0.0)
    lam = 0.4
    for Sm in (0.2, 0.35):
        y = cbt.StateBT.of(common["Sp"], Sm, common["S12"], common["S13"],
                           common["S23"], common["N"], lam, common["A"], 0., 0., 0.)
        got = float(cbt.rhs(0., y, args).Sigma_23)
        assert np.isclose(got, 2*SQ3*lam*Sm**2, rtol=1e-10), (Sm, got)


def test_tilted_classB_lambda_and_A_evolution():
    args = _args(1.2, Omega=0.3)
    y = cbt.StateBT.of(0.1, 0.05, 0.0, 0.0, 0.12, 0.4, 0.3, 0.35, .1, 0., 0.)
    d = cbt.rhs(0., y, args)
    assert np.isclose(float(d.lam), 2*SQ3*0.12*(1-0.3**2), rtol=1e-12)
    a = cbt.aux(y, args)
    assert np.isclose(float(d.A), (float(a["q"]) + 2*0.1)*0.35, rtol=1e-12)


def test_tilted_classB_frame_dictionary():
    fd = cbt.frame_dictionary()
    assert fd["N_minus"] == 0.0
    assert "N_+/(sqrt3 * N_x)" in fd["lambda"]
    assert fd["K"] == "N^2 + A^2"


def test_tilted_classB_untilted_limit_matches_class_b_structure():
    """v=0 에서 tilt 항이 전부 사라지고 Gauss 가 일치."""
    args = _args(1.0)
    y = cbt.StateBT.of(0.1, 0.05, 0., 0., 0.12, 0.4, 0.3, 0.35, 0., 0., 0.)
    d = cbt.rhs(0., y, args)
    assert abs(float(d.v1)) < 1e-15
    assert abs(float(d.v2)) < 1e-15
    assert abs(float(d.v3)) < 1e-15
    a = cbt.aux(y, args)
    assert np.isclose(float(a["K"]), 0.4**2 + 0.35**2)


# ================================================================ PR-17 γ 임계값
def test_gamma_thresholds_catalog():
    """확정된 임계값만 코드에 들어있고, gamma=6/7 은 없어야 한다."""
    from bianchi import thresholds as th
    assert th.TILTED_II == (2/3, 10/7, 14/9)
    assert 6/5 in th.TILTED_VI0
    # ★ v1.1: 10/9 는 VI_0 이 아니라 예외형 VI*_{-1/9} 소속
    assert not any(np.isclose(x, 10/9) for x in th.TILTED_VI0)
    assert any(np.isclose(x, 10/9) for x in th.EXCEPTIONAL_VI)
    # 4/3, 3/2 는 불변 부분공간 전용 — 전체 상태공간 분기표에 없어야 한다
    assert not any(np.isclose(x, 4/3) for x in th.TILTED_VI0)
    assert set(map(float, th.TILTED_VI0_SUBSET)) >= {1.5, 4/3}
    # extreme tilt 개시는 유형 의존
    assert np.isclose(th.extreme_tilt_onset("VIII"), 1.0)
    assert np.isclose(th.extreme_tilt_onset("VII_0"), 4/3)
    assert np.isclose(th.extreme_tilt_onset("II"), 14/9)
    assert np.isclose(th.extreme_tilt_onset("IV", Sigma_p=0.0), 6/5)
    assert th.OPEN_QUESTIONS  # 미해결 지점을 값으로 채우지 않았는지
    assert not any(np.isclose(x, 6/7) for x in th.all_fixed_values())
    # IV/VII_h 는 Sigma_+ 의존 — 상수로 박으면 안 된다
    assert callable(th.tilted_IV_extreme_boundary)
    assert np.isclose(th.tilted_IV_extreme_boundary(0.0), 6/5)
    assert not np.isclose(th.tilted_IV_extreme_boundary(-0.2), 6/5)
    # VI_h 는 h 의존
    assert callable(th.tilted_VIh_boundary)
    assert np.isclose(th.tilted_VIh_boundary(-1.0), 2*(3+1)/(5+3))


def test_tilted_II_threshold_10_7_numerically():
    """tilted II: gamma > 10/7 에서 비틸트 CS(II) 가 tilt 에 불안정.

    ★ v1.3: 이전 버전의 stability_of_CS_II 는 (7g-10)/7 을 하드코딩한 가짜였고
      이 테스트는 그것을 세탁하는 동어반복이었다 (적대적 감사 결함 #1/#2).
      현재는 jax.jacfwd 로 dv_general 을 실제 선형화하며, 여기서는 그 결과를
      **독립 해석식** 3(7g-10)/8 과 대조한다 — 두 경로가 다르므로 진짜 판별력이
      있다 (dv_general 의 -Sigma.v 부호가 틀리면 즉시 실패).
    """
    from bianchi import thresholds as th
    for g in (0.9, 1.1, 1.3, 10/7, 1.5, 1.8):
        num = th.stability_of_CS_II(g)
        ana = th.cs_II_tilt_eigenvalue_analytic(g)
        assert abs(num - ana) < 1e-12, (g, num, ana)
    lo, hi = th.stability_of_CS_II(1.3), th.stability_of_CS_II(1.5)
    assert lo < 0 < hi, (lo, hi)          # 10/7 ≈ 1.4286 에서 부호 전환
    assert abs(th.stability_of_CS_II(10/7)) < 1e-12
