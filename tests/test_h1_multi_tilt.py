"""
H'1 · **다성분 tilted class A** — 상태 설계 + 총량 결합 (62차).

측정·게이트:
  · 두 경로 (성분별 전개 ≡ general+fluid 합성) — NC=2,3 무작위 ≤1e−13.
  · NC=1 환원: F3 단일유체 rhs 와 dΣ·dN·dv **성분 동일** (Ω 는 다성분만 진화).
  · 등분할 축퇴: 같은 (γ, v) 2성분의 Ω 분할 ≡ 단일유체 — 기하 동일,
    dΩ₁+dΩ₂ = dΩ_단일.
  · ★ Gauss 전파 닫힘: Ω 비소거 설계의 심판 — on-shell 에서 d(Gauss)/dτ ≈ 0
    (JVP 실측).  D2 유도·실측 이중의 실측 반.
  · ★ Codazzi 는 **총**만 구속: 성분별 q_c ≠ 0 이면서 q_tot = 0 인 상태에서
    총 잔차 ~0, 성분별 잔차 O(1) — "성분별 자유, 합이 구속" 박제.
  · 성분별 편타면 (V16): γ_c<2 성분은 G₋ ≥ 2−γ_c (발화 불가), γ=2 성분만
    면 근접 — 같은 상태에서 성분별 gap 이 서로 다른 곳.
  · RK4 궤적: on-shell IC 에서 Gauss·Codazzi 표류 유계 + N 부호 보존.
"""
import numpy as np
import pytest

import jax

jax.config.update("jax_enable_x64", True)

import jax.numpy as jnp  # noqa: E402

from bianchi.charts import class_a_tilted as AT  # noqa: E402
from bianchi.charts import class_a_tilted_multi as M  # noqa: E402
from bianchi.matter.fluid import G_plus  # noqa: E402


def _rand_state(nc, seed, scale=0.25):
    rng = np.random.default_rng(seed)
    S5 = scale * rng.standard_normal(5)
    N3 = np.array([0.9, -0.4, 0.3]) + 0.2 * rng.standard_normal(3)
    Om = 0.2 + 0.5 * rng.random(nc)
    V = 0.3 * rng.standard_normal((nc, 3))
    return M.StateATM.of(S5, N3, Om, V)


def _gammas(nc):
    return np.array([4.0/3.0, 1.0, 2.0, 1.2][:nc])


def test_two_routes_agree_nc2_nc3():
    """★★ H'1 의 심판: 성분별 전개 ≡ general+fluid 합성."""
    for nc in (2, 3):
        for seed in (1, 2, 3):
            y = _rand_state(nc, seed)
            args = dict(gammas=_gammas(nc))
            d1 = M.rhs(0.0, y, args).as_array()
            d2 = M.rhs_via_general(0.0, y, args).as_array()
            assert float(jnp.abs(d1 - d2).max()) <= 1e-13, (nc, seed)


def test_nc1_reduces_to_f3_single_fluid():
    """★ 환원: NC=1 은 F3 class_a_tilted 와 dΣ·dN·dv 성분 동일 (Ω 명시 주입)."""
    y = _rand_state(1, seed=7)
    g = 1.4
    d_m = M.rhs(0.0, y, dict(gammas=[g]))
    y_f3 = AT.StateAT.of(*[float(y.Sigma5[k]) for k in range(5)],
                         *[float(y.N3[k]) for k in range(3)],
                         *[float(y.V[0, k]) for k in range(3)])
    d_f3 = AT.rhs(0.0, y_f3, dict(gamma=g, Omega=float(y.Om[0])))
    got = np.concatenate([np.asarray(d_m.Sigma5), np.asarray(d_m.N3),
                          np.asarray(d_m.V[0])])
    want = np.asarray(d_f3.as_array())
    want = np.concatenate([want[:8], want[8:11]])
    assert np.abs(got - want).max() <= 1e-14


def test_equal_split_degeneracy():
    """★ 같은 (γ,v) 2성분의 Ω 분할 ≡ 단일: 기하 rhs 동일 + dΩ 합 보존."""
    y1 = _rand_state(1, seed=11)
    g = 1.3
    for alpha in (0.3, 0.7):
        y2 = M.StateATM.of(y1.Sigma5, y1.N3,
                           jnp.array([alpha, 1.0 - alpha]) * y1.Om[0],
                           jnp.stack([y1.V[0], y1.V[0]]))
        d1 = M.rhs(0.0, y1, dict(gammas=[g]))
        d2 = M.rhs(0.0, y2, dict(gammas=[g, g]))
        assert float(jnp.abs(d1.Sigma5 - d2.Sigma5).max()) <= 1e-15
        assert float(jnp.abs(d1.N3 - d2.N3).max()) <= 1e-15
        assert float(jnp.abs(d1.V[0] - d2.V[0]).max()) <= 1e-15
        assert float(jnp.abs(d1.V[0] - d2.V[1]).max()) <= 1e-15
        assert abs(float(jnp.sum(d2.Om) - d1.Om[0])) <= 1e-15


def _on_gauss(y):
    """Ω 를 균일 재척도해 Gauss 잔차 0 으로."""
    a = M.aux(y, dict(gammas=np.ones(y.nc)))           # gauss 는 γ 무관
    target = 1.0 - a["Sigma2"] - a["K"]
    return M.StateATM.of(y.Sigma5, y.N3,
                         y.Om * target / jnp.sum(y.Om), y.V)


def test_gauss_propagation_closes():
    """★★ Ω 비소거 설계의 심판: on-shell 에서 d(Gauss)/dτ ≈ 0 (JVP 실측)."""
    for nc, seed in ((2, 21), (3, 22)):
        y = _on_gauss(_rand_state(nc, seed))
        args = dict(gammas=_gammas(nc))

        def gauss_of(arr):
            return M.aux(M.StateATM.from_array(arr), args)["gauss"]

        arr = y.as_array()
        darr = M.rhs(0.0, M.StateATM.from_array(arr), args).as_array()
        _, dg = jax.jvp(gauss_of, (arr,), (darr,))
        assert abs(float(dg)) <= 1e-13, (nc, float(dg))


def test_codazzi_constrains_total_only():
    """★ 성분별 자유·합 구속 박제: q₁ = −q₂ ≠ 0 (대각 Σ ⇒ 기하부 정확 0)."""
    from bianchi.conventions import codazzi_residual
    S5 = np.array([0.2, -0.1, 0.0, 0.0, 0.0])         # 대각 Σ
    N3 = np.array([0.8, -0.5, 0.3])
    g1, g2 = 4.0/3.0, 1.4
    Om = np.array([0.4, 0.3])
    v1 = np.array([0.2, -0.1, 0.15])
    q1 = 3.0*g1*Om[0]*v1 / float(G_plus(g1, v1 @ v1))
    v2 = -q1 * 0.1                                     # 반복 수렴: q₂ → −q₁
    for _ in range(60):
        v2 = -q1 * float(G_plus(g2, v2 @ v2)) / (3.0*g2*Om[1])
    y = M.StateATM.of(S5, N3, Om, np.stack([v1, v2]))
    a = M.aux(y, dict(gammas=[g1, g2]))
    tot = M.constraints(y, dict(gammas=[g1, g2]))["codazzi"]
    assert float(jnp.abs(tot).max()) <= 1e-12          # 총: 구속 만족
    S, N = a["S"], jnp.diag(y.N3)
    c1 = codazzi_residual(S, N, jnp.zeros(3), q1)
    assert float(jnp.abs(c1).max()) > 1e-2             # 성분별: 크게 위반


def test_component_whiplash_surfaces_differ():
    """★ V16 이행: 성분별 G₋_c — γ<2 는 발화 불가 하한, γ=2 만 면 근접."""
    gam = np.array([4.0/3.0, 2.0])
    y = M.StateATM.of(np.zeros(5), [0.5, -0.3, 0.2], [0.3, 0.3],
                      np.array([[0.9, 0.0, 0.0], [0.9, 0.0, 0.0]]))
    gaps = np.asarray(M.whiplash_gaps(y, gam))
    assert gaps[0] >= 2.0 - gam[0] - 1e-15             # 원리적 하한 (γ=4/3: ≥2/3)
    assert gaps[1] < 0.25                              # γ=2: 같은 V 로 면 근접
    assert abs(gaps[0] - gaps[1]) > 0.4                # 같은 상태, 다른 면


def test_rk4_trajectory_preserves_constraints_and_n_signs():
    """★ 궤적: on-shell IC — Gauss·총 Codazzi 표류 유계, N 부호·0 보존."""
    S5 = np.array([0.15, -0.08, 0.0, 0.0, 0.0])
    N3 = np.array([0.7, -0.4, 0.0])                    # N₃=0 보존도 본다
    gam = np.array([4.0/3.0, 1.0])
    Om0 = np.array([0.5, 0.5])
    y = _on_gauss(M.StateATM.of(S5, N3, Om0, np.zeros((2, 3))))
    # 대각 Σ + q_tot=0 (v=0) ⇒ 총 Codazzi 정확 0 에서 출발
    args = dict(gammas=gam)
    arr = y.as_array()

    def f(a):
        return M.rhs(0.0, M.StateATM.from_array(a), args).as_array()

    h, nstep = 0.005, 200                              # τ ∈ [0, 1]
    for _ in range(nstep):
        k1 = f(arr)
        k2 = f(arr + 0.5*h*k1)
        k3 = f(arr + 0.5*h*k2)
        k4 = f(arr + h*k3)
        arr = arr + (h/6.0)*(k1 + 2.0*k2 + 2.0*k3 + k4)
    yT = M.StateATM.from_array(arr)
    c = M.constraints(yT, args)
    assert abs(float(c["gauss"])) <= 1e-8
    assert float(jnp.abs(c["codazzi"]).max()) <= 1e-8
    assert float(yT.N3[0]) > 0.0 and float(yT.N3[1]) < 0.0
    assert float(jnp.abs(yT.N3[2])) == 0.0             # N=0 곱셈 구조 정확 보존


def test_state_array_roundtrip():
    """상태 팩킹 왕복 — NC=1,2,4."""
    for nc, seed in ((1, 31), (2, 32), (4, 33)):
        y = _rand_state(nc, seed)
        arr = y.as_array()
        assert arr.shape == (8 + 4*nc,)
        y2 = M.StateATM.from_array(arr)
        assert float(jnp.abs(y2.as_array() - arr).max()) == 0.0
