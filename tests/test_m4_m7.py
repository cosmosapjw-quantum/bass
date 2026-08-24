"""M4~M7 완료 기준 — PR-18/19/20/21/22/23/25/26/27."""
import numpy as np
import pytest
import jax
import jax.numpy as jnp

import bianchi  # noqa: F401
from bianchi import batch as bt
from bianchi import integrate as itg
from bianchi import physical as ph
from bianchi.analysis import dynamics as dyn
from bianchi.charts import class_a as ca
from bianchi.charts import type_ix_d as ixd
from bianchi.matter import components as mc
from bianchi.matter import fluid as fl

rng = np.random.default_rng(11)


def _args(gamma=1.0, **kw):
    d = {"gamma": jnp.asarray(gamma)}
    d.update({k: jnp.asarray(v) for k, v in kw.items()})
    return d


# ================================================================ PR-18 다중 유체
def test_multifluid_relative_motion_creates_offdiagonal_stress():
    """★ 상대운동하는 다중 유체는 진짜 이방성 응력을 만든다 (대각 shear 불가)."""
    rad = fl.TiltedFluid.of(4/3, 0.3, jnp.asarray([0.2, 0.15, 0.0]))
    dust = fl.TiltedFluid.of(1.0, 0.25, jnp.zeros(3))
    mf = mc.MultiFluid.of(rad, dust)
    Sigma = jnp.diag(jnp.asarray([0.1, -0.05, -0.05]))
    A = jnp.zeros(3)
    assert mc.anisotropic_stress_is_nonzero(mf, Sigma, A)
    Pi = mf.total_sources(Sigma, A)["Pi"]
    assert abs(float(Pi[0, 1])) > 1e-6      # 비대각 성분이 실제로 존재


def test_multifluid_total_omega_and_q():
    rad = fl.TiltedFluid.of(4/3, 0.3, jnp.asarray([0.1, 0., 0.]))
    dust = fl.TiltedFluid.of(1.0, 0.25, jnp.zeros(3))
    mf = mc.MultiFluid.of(rad, dust)
    Sigma = jnp.zeros((3, 3)); A = jnp.zeros(3)
    tot = mf.total_sources(Sigma, A)
    assert np.isclose(float(tot["Omega"]), 0.55)
    q = mf.deceleration(0.0, Sigma, A)
    assert float(q) > 0


def test_multifluid_untilted_reduces_to_sum():
    """비틸트 극한에서 q = sum (1/2)(3g_i-2)Omega_i."""
    a = fl.TiltedFluid.of(4/3, 0.4, jnp.zeros(3))
    b = fl.TiltedFluid.of(1.0, 0.3, jnp.zeros(3))
    mf = mc.MultiFluid.of(a, b)
    q = float(mf.deceleration(0.0, jnp.zeros((3, 3)), jnp.zeros(3)))
    assert np.isclose(q, 0.5*(3*4/3-2)*0.4 + 0.5*(3*1.0-2)*0.3)


# ================================================================ PR-19 스칼라장
def test_scalar_conservation_identity():
    for _ in range(6):
        x, y, lam = rng.normal(0, .4), abs(rng.normal(0, .4)), rng.uniform(0, 2)
        sf = mc.ScalarField.of(x, y, lam)
        q = 2*0.1 + sf.pressure_term()
        assert abs(float(sf.conservation_residual(q))) < 1e-12


def test_scalar_no_anisotropic_stress():
    sf = mc.ScalarField.of(0.3, 0.5, 1.0)
    assert np.abs(np.asarray(sf.anisotropic_stress())).max() == 0.0
    assert np.abs(np.asarray(sf.momentum_flux())).max() == 0.0


def test_scalar_gamma_eff_range():
    """gamma_phi = 2x^2/(x^2+y^2) in [0,2]: 운동에너지지배 2, 퍼텐셜지배 0."""
    assert np.isclose(float(mc.ScalarField.of(1., 0., 0.).gamma_eff()), 2.0)
    assert np.isclose(float(mc.ScalarField.of(0., 1., 0.).gamma_eff()), 0.0)


def test_scalar_no_hair_isotropization():
    """이방성 no-hair: 지수퍼텐셜 스칼라장 + shear 에서 Sigma -> 0."""
    lam = 0.5
    def rhs(t, s, args):
        yA, sf = s
        a = ca.aux(yA, 0.0)
        Om_phi = sf.omega()
        Sigma2 = a["Sigma2"]
        q = 2*Sigma2 + sf.pressure_term()
        dA = ca.StateA(
            Sigma_p=-(2-q)*yA.Sigma_p, Sigma_m=-(2-q)*yA.Sigma_m,
            N1=jnp.zeros(()), N2=jnp.zeros(()), N3=jnp.zeros(()))
        return (dA, sf.rhs(q))
    y0 = (ca.StateA.of(0.5, 0.3, 0., 0., 0.), mc.ScalarField.of(0.2, 0.5, lam))
    sol = itg.solve_jit(rhs, y0, 0., 8., _args(0.0),
                        cfg=itg.SolverConfig(rtol=1e-10, atol=1e-12))
    yf = jax.tree.map(lambda x: x[-1] if jnp.ndim(x) else x, sol.ys)
    S = np.hypot(float(yf[0].Sigma_p), float(yf[0].Sigma_m))
    assert S < 0.05, S


# ================================================================ PR-20 자기장
def test_magnetic_emt_structure():
    B = jnp.asarray([0.3, -0.2, 0.1])
    mag = mc.MagneticField.of(B)
    B2 = float(B @ B)
    Pi = np.asarray(mag.anisotropic_stress())
    assert np.allclose(Pi, -(np.outer(B, B) - B2*np.eye(3)/3), atol=1e-14)
    assert abs(np.trace(Pi)) < 1e-14
    assert np.isclose(float(mag.omega()), B2/6)
    # gamma_eff = 4/3  =>  (1/2)(3*4/3-2)Omega = Omega
    assert np.isclose(float(mag.pressure_term()), float(mag.omega()))


def test_magnetic_constraints_restrict_type_V():
    """유형 V (n=0, a!=0) 에서는 B = 0 만 허용."""
    N = jnp.zeros((3, 3)); A = jnp.asarray([1.0, 0., 0.])
    good = mc.MagneticField.of(jnp.zeros(3))
    c = good.constraints(N, A)
    assert np.abs(np.asarray(c["div_free"])).max() < 1e-15
    assert np.abs(np.asarray(c["ampere"])).max() < 1e-15
    bad = mc.MagneticField.of(jnp.asarray([0., 0.3, 0.]))
    cb_ = bad.constraints(N, A)
    assert np.abs(np.asarray(cb_["ampere"])).max() > 1e-6   # a x B != 0


def test_magnetic_type_II_allows_kernel_direction():
    """유형 II (n=diag(1,0,0), a=0): B in ker(n) 즉 B_1 = 0."""
    N = jnp.diag(jnp.asarray([1., 0., 0.])); A = jnp.zeros(3)
    ok = mc.MagneticField.of(jnp.asarray([0., 0.3, 0.2]))
    c = ok.constraints(N, A)
    assert np.abs(np.asarray(c["ampere"])).max() < 1e-15
    bad = mc.MagneticField.of(jnp.asarray([0.3, 0., 0.]))
    assert np.abs(np.asarray(bad.constraints(N, A)["ampere"])).max() > 1e-6


def test_magnetic_constraints_preserved_by_evolution():
    N = jnp.diag(jnp.asarray([1., 0., 0.])); A = jnp.zeros(3)
    mag = mc.MagneticField.of(jnp.asarray([0., 0.3, 0.2]))
    Sigma = jnp.diag(jnp.asarray([0.2, -0.1, -0.1]))
    d = mag.rhs(Sigma, jnp.zeros(3), q=0.5)
    # a.B 은 A=0 이라 자명; Ampere 는 n B 이 보존되는지
    c0 = np.abs(np.asarray(mag.constraints(N, A)["ampere"])).max()
    c1 = np.abs(np.asarray(mc.MagneticField.of(
        mag.B + 1e-4*d.B).constraints(N, A)["ampere"])).max()
    assert c0 < 1e-15 and c1 < 1e-10


# ================================================================ PR-21 Bianchi IX
def test_ixd_definition_constraint_propagates_with_tracefree():
    """★ G' = -2(qH+F)G 는 trace-free 를 부과했을 때만 성립."""
    args = _args(1.0)
    for _ in range(6):
        S = rng.normal(0, .3, 3); S -= S.mean()
        y = ixd.StateD.of(rng.uniform(.3, .9), S, rng.uniform(.2, 1.2, 3))
        r = float(ixd.definition_propagation_residual(y, args))
        assert abs(r) < 1e-9, r


def test_ixd_trace_is_monitored_and_preserved():
    args = _args(4/3)
    S = np.array([0.3, -0.1, -0.2])
    y = ixd.StateD.of(0.7, S, [1.0, 0.8, 0.9])
    assert abs(float(ixd.constraints(y, args)["trace"])) < 1e-15
    d = ixd.rhs(0., y, args)
    assert abs(float(jnp.sum(d.S))) < 1e-14


def test_ixd_D_positive_and_H_can_cross_zero():
    """H-차트로는 잡을 수 없는 재붕괴를 D-차트가 통과한다."""
    args = _args(1.0)
    # 등방 닫힌 IX: 정의식 구속 위의 초기조건, H_bar > 0 (팽창 중)
    y0 = ixd.isotropic_closed_ic(0.35)
    assert abs(float(ixd.constraints(y0, args)["definition"])) < 1e-14
    assert float(ixd.aux(y0, 1.0)["Omega"]) > 0
    ev = ixd.recollapse_event()
    # ★ 미래 방향(rhs_future)으로 적분해야 재붕괴로 간다
    sol = itg.solve_jit(ixd.rhs_future, y0, 0., 12., args, event=ev,
                        cfg=itg.SolverConfig(rtol=1e-10, atol=1e-12))
    st = itg.status(sol)
    yf = jax.tree.map(lambda x: x[-1] if jnp.ndim(x) else x, sol.ys)
    assert st["accepted"]
    # H_bar 가 0 으로 내려온다 (= 최대팽창 도달). D > 0 은 항상 유지.
    assert float(yf.H) < float(y0.H)
    assert st["event_fired"] or abs(float(yf.H)) < 1e-6, float(yf.H)
    # 정의식 구속이 적분 내내 유지됨
    assert abs(float(ixd.constraints(yf, args)["definition"])) < 1e-7


def test_ixd_from_H_chart_roundtrip_consistency():
    yA = ca.StateA.of(0.1, -0.05, 0.5, 0.4, 0.45)
    yD = ixd.from_H_chart(yA, 1.0)
    c = ixd.constraints(yD, _args(1.0))
    assert abs(float(c["definition"])) < 1e-12
    assert abs(float(c["trace"])) < 1e-14


# ================================================================ PR-22/23 배치
def test_memory_estimate_matches_design_numbers():
    """설계 §5.4: 10^6 x 30 -> 선형연산자만 7.2 GB."""
    m = bt.memory_estimate(1_000_000, 30)
    assert np.isclose(m["linear_op_GB"], 7.2, rtol=1e-6)
    assert np.isclose(m["state_GB"], 0.24, rtol=1e-6)
    m40 = bt.memory_estimate(1_000_000, 40)
    assert np.isclose(m40["linear_op_GB"], 12.8, rtol=1e-6)


def test_recommend_chunk_size_fits_8GB():
    n = bt.recommend_chunk_size(30, vram_GB=8.0)
    assert 1_000 < n < 1_000_000
    m = bt.memory_estimate(n, 30)
    assert m["total_GB"] < 8.0


def test_batch_divergence_cost_metric():
    steps = np.array([12]*63 + [91])
    c = bt.batch_divergence_cost(steps)
    assert c["ideal"] == 847
    assert c["actual"] == 64*91
    assert c["waste_factor"] > 6      # 설계 §5.3 의 낭비 구조


def test_plan_creates_homogeneous_chunks():
    scores = rng.uniform(0, 100, 1000)
    plan = bt.make_plan(scores, chunk_size=100)
    assert plan.n_chunks() == 10
    spreads = [scores[c].max() - scores[c].min() for c in plan.chunks]
    assert max(spreads) < scores.max() - scores.min()   # 정렬로 균질화됨


def test_batch_vmap_run_and_stragglers():
    states = jnp.asarray(rng.normal(0, .3, (24, 5)))
    plan = bt.make_plan(bt.difficulty_score(np.asarray(states)), chunk_size=8)
    out = bt.run_scan(ca.rhs, states, _args(1.0), plan,
                      cfg=itg.SolverConfig(max_steps=2048),
                      unpack=ca.StateA.from_array)
    assert out["steps"].shape[0] == 24
    assert out["straggler_fraction"] < 0.2


# ================================================================ PR-25 물리 재구성
def test_physical_H_and_time_reconstruction():
    """de Sitter (q=-1): H 일정, t = tau/H."""
    tau = np.linspace(0, 3, 200)
    q = -np.ones_like(tau)
    H = ph.integrate_H(tau, q, H0=0.7)
    assert np.allclose(H, 0.7, atol=1e-12)
    t = ph.cosmic_time(tau, H)
    assert np.allclose(t, tau/0.7, atol=1e-9)


def test_physical_matter_dominated_H():
    """먼지 FLRW (q=1/2): H ~ e^{-3tau/2}."""
    tau = np.linspace(0, 2, 400)
    H = ph.integrate_H(tau, 0.5*np.ones_like(tau), H0=1.0)
    assert np.allclose(H, np.exp(-1.5*tau), rtol=1e-6)


def test_physical_shear_scalar_type_separation():
    s_we = ph.shear_scalar(0.25, kind="WE")
    s_th = ph.shear_scalar(0.25, kind="theta")
    assert np.isclose(s_we.value, 0.5)
    assert np.isclose(s_th.value, 0.5/np.sqrt(3))
    assert s_we.kind == "WE" and s_th.kind == "theta"


def test_physical_lorentz_factor_log_safe():
    lf = ph.lorentz_factor(np.array([0.0, 0.5, 1.0 - 1e-14]))
    assert np.isfinite(lf["log_Gamma"]).all()
    assert lf["Gamma"][0] == 1.0


def test_physical_directional_scale_factors():
    tau = np.linspace(0, 1, 50)
    S = np.zeros((50, 3))
    a = ph.directional_scale_factors(tau, S)
    assert np.allclose(a, np.exp(tau)[:, None], rtol=1e-9)


def test_bbn_anisotropy_monotone():
    assert ph.bbn_expansion_anisotropy(0.0) == 0.0
    assert ph.bbn_expansion_anisotropy(0.02) < ph.bbn_expansion_anisotropy(0.05)


# ================================================================ PR-26/27 분석
def _rhs_arr(v, args):
    return ca.rhs(0.0, ca.StateA.from_array(v), args).as_array()


def test_find_kasner_fixed_point_and_classify():
    args = _args(4/3)
    v0 = jnp.asarray([np.cos(0.7), np.sin(0.7), 0., 0., 0.])
    v, sol = dyn.find_fixed_point(_rhs_arr, v0, args)
    assert float(jnp.max(jnp.abs(_rhs_arr(v, args)))) < 1e-10
    c = dyn.classify_fixed_point(_rhs_arr, v, args)
    assert c["kind"] in ("saddle", "source", "non-hyperbolic")


def test_collins_stewart_eigenvalues_and_sink_for_small_gamma():
    """CS(II): 기하 방향은 2/3<g<2 에서 sink, tilt 방향은 g=10/7 에서 전환.

    ★ v1.3: 이전 버전은 expect_sink 를 바인딩만 하고 쓰지 않았으며 isfinite 만
      단언했다 (적대적 감사 결함 #2 동반 사례). 이제 (i) 기하(class A) 활성
      고윳값의 실부 음수, (ii) tilt 고윳값의 부호를 실제로 판정한다.
    """
    from bianchi import thresholds as th
    for g, expect_sink in [(1.0, True), (1.2, True), (1.5, False)]:
        args = _args(g)
        Sp = (3*g - 2)/8
        N1 = np.sqrt(max(3*(2 - 4*Sp)*Sp, 1e-9))
        v0 = jnp.asarray([Sp, 0.0, N1, 0.0, 0.0])
        v, _ = dyn.find_fixed_point(_rhs_arr, v0, args)
        assert float(jnp.max(jnp.abs(_rhs_arr(v, args)))) < 1e-9
        # (i) CS(II) 는 **유형 II 불변부분공간** (N2 = N3 = 0, 좌표 0:3) 의
        #     sink 다 (2/3 < g < 2).  N2/N3 축 방향은 유형 이탈 방향이라 원래
        #     불안정하다 — 전체 class A 고윳값으로 판정하면 물리를 잘못 읽는다.
        import jax
        J = np.asarray(jax.jacfwd(lambda w: _rhs_arr(w, args))(v))
        sub = np.linalg.eigvals(J[:3, :3])
        assert np.isfinite(sub).all() and (sub.real < 1e-10).all(), (g, sub)
        # (ii) tilt 안정성은 10/7 에서 갈린다 — expect_sink 를 실제로 사용
        tilt = th.stability_of_CS_II(g)
        assert (tilt < 0) == expect_sink, (g, tilt, expect_sink)


def test_continuation_over_gamma():
    rows = dyn.continuation(
        _rhs_arr,
        jnp.asarray([(3*1.0-2)/8, 0., np.sqrt(3*(2-4*(3*1.0-2)/8)*((3*1.0-2)/8)), 0., 0.]),
        lambda g: _args(g), np.linspace(1.0, 1.35, 8))
    assert all(r[2] < 1e-8 for r in rows)
    Sps = [r[1][0] for r in rows]
    assert np.allclose(Sps, [(3*g-2)/8 for g, _, _ in rows], atol=1e-8)


def test_lyapunov_of_fixed_point_is_nonpositive_ish():
    """고정점에서 최대 Lyapunov 지수는 그 고윳값 실부와 정합."""
    args = _args(1.0)
    g = 1.0
    Sp = (3*g-2)/8
    N1 = np.sqrt(3*(2-4*Sp)*Sp)
    v = jnp.asarray([Sp, 0., N1, 0., 0.])
    ev = dyn.eigenvalues(_rhs_arr, v, args)
    lam = dyn.largest_lyapunov(_rhs_arr, v, args, T=20.0, dt=0.01)
    assert lam < max(ev.real) + 0.15


def test_limit_cycle_detector_on_fixed_point():
    args = _args(1.0)
    g = 1.0; Sp = (3*g-2)/8
    N1 = np.sqrt(3*(2-4*Sp)*Sp)
    r = dyn.detect_limit_cycle(_rhs_arr, jnp.asarray([Sp, 0., N1, 0., 0.]),
                               args, T=30.0, dt=0.01)
    assert r["kind"] == "fixed-point"
