"""
I1d · **tilted 다성분 기하 × n-프레임 운동종 결합** (68차) — PLAN §1 마감.

★ 통찰 박제: 무충돌·무질량 운동종은 n-프레임 다중극이 완비 — 쌍극이 틸트를
나른다.  종-프레임 tilted 기계 (J2b/J2c) 는 B2b (충돌) 부터 필수.  질량행렬
불요 ⇒ 명시 dJ.

게이트: 운동종=0 ⇒ H'1 정확; 유체=0·대각·W=0 ⇒ I1c 정확; 회전항 부호 핀
(l=1 ≡ W@vec, 궤적 공변성); 총 Codazzi (운동 q 포함) 전파 닫힘 (JVP);
쌍극 유체극한; ★CS(II) 운동 고유값 −1/4 (γ=4/3, F3 해석값의 운동론 판);
F2 회귀 = 전체 스위트.
"""
import numpy as np
import pytest

import jax

jax.config.update("jax_enable_x64", True)

import jax.numpy as jnp  # noqa: E402

from bianchi.charts import class_a_tilted_multi as MM  # noqa: E402
from bianchi.matter import coupled_class_a as CP  # noqa: E402
from bianchi.matter import coupled_tilted as CT  # noqa: E402
from bianchi.matter import pstf_coeff as PC  # noqa: E402


def test_reduction_to_h1_multi_exact():
    """★ 운동종=0: 기하·유체 rhs ≡ class_a_tilted_multi (κ 포함)."""
    rng = np.random.default_rng(1)
    S5 = 0.2*rng.standard_normal(5)
    N3 = np.array([0.9, -0.4, 0.3])
    Om = np.array([0.4, 0.3])
    V = 0.25*rng.standard_normal((2, 3))
    gam = np.array([4.0/3.0, 1.1])
    kap = np.zeros((2, 2))
    kap[0, 1] = kap[1, 0] = 0.7
    Jc0 = {(l, 0): np.zeros(2*l + 1) for l in range(5)}
    y = CT.pack(S5, N3, 0.0, Om, V, Jc0, 4)
    d = CT.coupled_rhs(y, gam, 4, kappa=kap)
    dS5, dN3, _, dOm, dV, _ = CT.unpack(d, 2, 4)
    dm = MM.rhs(0.0, MM.StateATM.of(S5, N3, Om, V),
                dict(gammas=gam, kappa=kap))
    assert float(jnp.abs(jnp.asarray(dS5) - dm.Sigma5).max()) <= 1e-15
    assert float(jnp.abs(jnp.asarray(dN3) - dm.N3).max()) <= 1e-15
    assert float(jnp.abs(jnp.asarray(dOm) - dm.Om).max()) <= 1e-15
    assert float(jnp.abs(jnp.asarray(dV) - dm.V).max()) <= 1e-15


def test_reduction_to_i1c_exact():
    """★ 유체=0 + 대각 Σ (게이지 W=0): dJ·dlnH ≡ I1c coupled."""
    rng = np.random.default_rng(2)
    S5d = np.array([0.15, -0.08, 0.0, 0.0, 0.0])
    N3 = np.array([0.7, -0.4, 0.2])
    Jc = {(l, 0): 0.1*rng.standard_normal(2*l + 1) for l in range(5)}
    Jc[(0, 0)] = np.array([2.0])
    y = CT.pack(S5d, N3, 0.1, np.zeros(0), np.zeros((0, 3)), Jc, 4)
    d = CT.coupled_rhs(y, np.zeros(0), 4)
    _, _, dlnH, _, _, dJ = CT.unpack(d, 0, 4)
    yc = CP.pack(np.array([S5d[0], S5d[1], *N3]), 0.1, Jc, 4)
    dc = CP.coupled_rhs(yc, 4)
    _, dlnHc, dJc = CP.unpack(dc, 4)
    assert max(float(np.abs(dJ[(l, 0)] - dJc[(l, 0)]).max())
               for l in range(5)) == 0.0
    assert dlnH == dlnHc


def test_rotation_term_sign_pin():
    """★ 회전항 핀: l=1 에서 _rot_term ≡ W@vec (W=−ε·R) — 프레임 co-회전."""
    from bianchi.conventions import rotation_matrix
    rng = np.random.default_rng(3)
    R = np.array([0.3, -0.5, 0.2])
    W = np.asarray(rotation_matrix(jnp.asarray(R)))
    for _ in range(4):
        vec = rng.standard_normal(3)
        c1 = PC.vec_to_c3(vec)
        dc = CT._rot_term(c1, 1, R)
        dvec = np.asarray(PC.from_ccoef(dc, 1), float)
        assert np.abs(dvec - W @ vec).max() <= 1e-14


def test_rotation_covariance_of_hierarchy():
    """★ 궤적 공변성: 상수 R 순수회전 (Σ=N=0 동결) — J₂ 텐서가 O(τ) 로 회전."""
    from scipy.linalg import expm

    from bianchi.conventions import rotation_matrix
    R = np.array([0.25, -0.4, 0.15])
    W = np.asarray(rotation_matrix(jnp.asarray(R)))
    rng = np.random.default_rng(5)
    c2 = rng.standard_normal(5)
    lmax, tau, ns = 3, 0.7, 400
    Jc = {(l, 0): np.zeros(2*l + 1) for l in range(lmax + 1)}
    Jc[(2, 0)] = c2.copy()
    h = tau / ns
    J = {k: v.copy() for k, v in Jc.items()}

    def rhs(Jd):
        return {(l, 0): CT._rot_term(Jd[(l, 0)], l, R)
                for l in range(lmax + 1)}

    for _ in range(ns):
        k1 = rhs(J)
        st = lambda f, kk: {q: J[q] + f*h*kk[q] for q in J}
        k2 = rhs(st(0.5, k1))
        k3 = rhs(st(0.5, k2))
        k4 = rhs(st(1.0, k3))
        J = {q: J[q] + (h/6.0)*(k1[q] + 2*k2[q] + 2*k3[q] + k4[q]) for q in J}
    O = expm(W * tau)
    T0 = np.asarray(PC.from_ccoef(c2, 2), float)
    want = O @ T0 @ O.T
    got = np.asarray(PC.from_ccoef(J[(2, 0)], 2), float)
    assert np.abs(got - want).max() <= 1e-9


def test_total_codazzi_closure_with_kinetic_q():
    """★★ 총 Codazzi (운동 q 포함) 전파 닫힘 — on-shell JVP ≤1e−10.
    쌍극·비대각 π 가 살아 있는 상태에서 (I1c 대각 절편을 넘는 심판)."""
    rng = np.random.default_rng(7)
    S5 = np.array([0.12, -0.07, 0.03, -0.02, 0.04])
    N3 = np.array([0.8, -0.5, 0.3])
    gam = np.array([4.0/3.0])
    lmax = 3
    Jc = {(l, 0): 0.02*rng.standard_normal(2*l + 1) for l in range(lmax + 1)}
    Jc[(0, 0)] = np.array([1.5])
    # on-shell: Gauss 를 유체 Ω 로, Codazzi 를 운동 쌍극으로 맞춘다
    from bianchi.conventions import codazzi_residual
    S = np.asarray(MM.shear_matrix(jnp.asarray(S5)), float)
    geoC = np.asarray(codazzi_residual(jnp.asarray(S),
                                       jnp.diag(jnp.asarray(N3)),
                                       jnp.zeros(3), None), float)
    # q⃗_kin = geoC ⇒ J(1) = to_ccoef(geoC·H²), 유체 v=0 (q 유체 0)
    Jc[(1, 0)] = PC.to_ccoef(geoC * np.exp(0.0), 1)
    Ok = float(Jc[(0, 0)][0]) / 3.0
    K = float(MM.aux(MM.StateATM.of(S5, N3, np.zeros(1), np.zeros((1, 3))),
                     dict(gammas=np.ones(1)))["K"])
    Om_f = np.array([1.0 - float(S5 @ S5) - K - Ok])
    y = CT.pack(S5, N3, 0.0, Om_f, np.zeros((1, 3)), Jc, lmax)
    m0 = CT.monitors(y, gam, lmax)
    assert abs(m0["gauss"]) <= 1e-12
    assert np.abs(m0["codazzi"]).max() <= 1e-12
    # 전파: 수치 미분으로 d(residual)/dτ
    eps = 1e-6
    d = CT.coupled_rhs(y, gam, lmax)
    mp = CT.monitors(y + eps*d, gam, lmax)
    mm = CT.monitors(y - eps*d, gam, lmax)
    dg = (mp["gauss"] - mm["gauss"]) / (2*eps)
    dcod = (np.asarray(mp["codazzi"]) - np.asarray(mm["codazzi"])) / (2*eps)
    assert abs(dg) <= 1e-9, dg
    assert np.abs(dcod).max() <= 1e-9, dcod


def test_cs_ii_kinetic_eigenvalue():
    """★★ CS(II) 운동 고유값: γ=4/3 유체 해석값 3(7γ−10)/8 = −1/4 을
    운동 쌍극 (l_max=1 절단 = 유체극한) 이 재현 — v_eff 율 적합 ≤1e−3."""
    g = 4.0/3.0
    sp = (3.0*g - 2.0) / 8.0
    n1 = np.sqrt(9.0*(2.0 - g)*(3.0*g - 2.0)/16.0)
    S5 = np.array([sp, 0.0, 0.0, 0.0, 0.0])
    N3 = np.array([n1, 0.0, 0.0])
    lmax = 1
    K = float(MM.aux(MM.StateATM.of(S5, N3, np.zeros(1), np.zeros((1, 3))),
                     dict(gammas=np.ones(1)))["K"])
    rho = 3.0 * (1.0 - sp*sp - K)
    Jc = {(0, 0): np.array([rho]), (1, 0): np.zeros(3)}
    v0 = 1e-6
    Jc[(1, 0)] = PC.to_ccoef(np.array([0.0, v0*4.0/3.0*rho, 0.0]), 1)  # v₂ 방향
    y = CT.pack(S5, N3, 0.0, np.zeros(0), np.zeros((0, 3)), Jc, lmax)
    tau, ns = 0.4, 400
    yT, traj = CT.rk4_evolve(y, np.zeros(0), lmax, tau, ns, keep=True)
    # v_eff(τ) = 3 q̂ / (4 ρ̂)  (정규화 소거) — 성장률 적합
    ts = np.linspace(0, tau, ns + 1)
    vs = []
    for k in (0, ns):
        _, _, lnH, _, _, J = CT.unpack(traj[k], 0, lmax)
        qv = np.asarray(PC.from_ccoef(J[(1, 0)], 1), float)
        vs.append(3.0*qv[1] / (4.0*float(J[(0, 0)][0])))
    rate = np.log(vs[1] / vs[0]) / tau
    analytic = 3.0*(7.0*g - 10.0)/8.0                  # = −1/4
    assert abs(rate - analytic) <= 1e-3, (rate, analytic)


def test_kinetic_dipole_matches_tilted_fluid_smallv():
    """★ 쌍극 유체극한: l_max=1 운동종 vs H'1 단일 tilted 유체 (γ=4/3),
    소-v 궤적 — v_eff 대 v 상대오차 ≤ O(v)+절단."""
    rng = np.random.default_rng(11)
    S5 = np.array([0.1, -0.05, 0.0, 0.0, 0.0])
    N3 = np.array([0.6, -0.3, 0.2])
    lmax = 1
    K = float(MM.aux(MM.StateATM.of(S5, N3, np.zeros(1), np.zeros((1, 3))),
                     dict(gammas=np.ones(1)))["K"])
    Om0 = 1.0 - float(S5 @ S5) - K
    rho = 3.0 * Om0
    v0 = np.array([2e-4, -1e-4, 1.5e-4])
    Jc = {(0, 0): np.array([rho]),
          (1, 0): PC.to_ccoef(4.0/3.0*rho*v0, 1)}
    y = CT.pack(S5, N3, 0.0, np.zeros(0), np.zeros((0, 3)), Jc, lmax)
    tau, ns = 0.5, 300
    yT = CT.rk4_evolve(y, np.zeros(0), lmax, tau, ns)
    _, _, _, _, _, J = CT.unpack(yT, 0, lmax)
    v_kin = 3.0*np.asarray(PC.from_ccoef(J[(1, 0)], 1), float) \
        / (4.0*float(J[(0, 0)][0]))
    # 유체 경로 (H'1 다성분 차트, NC=1)
    ym = MM.StateATM.of(S5, N3, np.array([Om0]), v0[None, :])
    args = dict(gammas=np.array([4.0/3.0]))
    h = tau/ns
    yv = ym
    import jax.numpy as jnp2
    for _ in range(ns):
        k1 = MM.rhs(0.0, yv, args)
        def stp(a, f, k):
            return MM.StateATM(a.Sigma5 + f*h*k.Sigma5, a.N3 + f*h*k.N3,
                               a.Om + f*h*k.Om, a.V + f*h*k.V)
        k2 = MM.rhs(0.0, stp(yv, 0.5, k1), args)
        k3 = MM.rhs(0.0, stp(yv, 0.5, k2), args)
        k4 = MM.rhs(0.0, stp(yv, 1.0, k3), args)
        yv = MM.StateATM(
            yv.Sigma5 + (h/6)*(k1.Sigma5 + 2*k2.Sigma5 + 2*k3.Sigma5 + k4.Sigma5),
            yv.N3 + (h/6)*(k1.N3 + 2*k2.N3 + 2*k3.N3 + k4.N3),
            yv.Om + (h/6)*(k1.Om + 2*k2.Om + 2*k3.Om + k4.Om),
            yv.V + (h/6)*(k1.V + 2*k2.V + 2*k3.V + k4.V))
    v_fl = np.asarray(yv.V[0], float)
    denom = max(np.abs(v_fl).max(), 1e-12)
    assert np.abs(v_kin - v_fl).max() / denom <= 5e-3, (v_kin, v_fl)
