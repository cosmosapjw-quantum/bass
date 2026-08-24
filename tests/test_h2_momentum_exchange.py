"""
H'2 · **성분간 운동량 교환** — n-프레임 순수 운동량 모형 (63차).

측정·게이트:
  · 기호 항등 2건 (audit/h2): δdq̂ ≡ R (닫힌식 검산 — G₋+2(γ−1)V²=G₊ 소거),
    Σ_c R_c ≡ 0 (κ 대칭 ⇒ 쌍별 반대칭).
  · 두 경로: 닫힌식 ≡ (Ω,q̂) 야코비안 선형해 (유도의 독립 재현).
  · κ=0 ≡ H'1 (교환 무): rhs 정확 일치.
  · ★ 총량 κ-불변: 같은 상태에서 d(q̂_tot)/dτ 가 κ 의존 없음 (JVP 실측) —
    δdΩ=0 이라 dΩ·기하는 자명 불변, 실질은 q̂_tot 율.
  · Gauss 전파 닫힘이 κ>0 에서도 유지 (δdΩ=0 의 실측 귀결).
  · ★ 끌림 평형화: 상대속도 지수감쇠 — 소-v 해석율과 궤적 적합 대조 ≤3%.
  · κ 검증: 비대칭/비영대각 명시 거부.
"""
import numpy as np
import pytest

import jax

jax.config.update("jax_enable_x64", True)

import jax.numpy as jnp  # noqa: E402

from bianchi.charts import class_a_tilted_multi as M  # noqa: E402
from bianchi.matter import exchange as EX  # noqa: E402


def _rand_state(nc, seed, scale=0.25):
    rng = np.random.default_rng(seed)
    S5 = scale * rng.standard_normal(5)
    N3 = np.array([0.9, -0.4, 0.3]) + 0.2 * rng.standard_normal(3)
    Om = 0.2 + 0.5 * rng.random(nc)
    V = 0.3 * rng.standard_normal((nc, 3))
    return M.StateATM.of(S5, N3, Om, V)


def _kappa(nc, seed=5):
    rng = np.random.default_rng(seed)
    k = 0.5 * rng.random((nc, nc))
    k = k + k.T
    np.fill_diagonal(k, 0.0)
    return k


def test_symbolic_identities():
    """★★ 기호 박제: δdq̂ ≡ R + Σ R ≡ 0 (sympy)."""
    from audit.h2_exchange_derivation import (delta_dq_is_R_symbolic,
                                              total_R_vanishes_symbolic)
    assert delta_dq_is_R_symbolic()
    assert total_R_vanishes_symbolic()


def test_two_exchange_routes_agree():
    """★ 닫힌식 ≡ 야코비안 선형해 — NC=2,3."""
    for nc, seed in ((2, 1), (3, 2)):
        y = _rand_state(nc, seed)
        gam = np.array([4.0/3.0, 1.0, 1.7][:nc])
        R = EX.exchange_R(y.Om, y.V, _kappa(nc))
        d1 = EX.delta_dv_closed(gam, y.Om, y.V, R)
        d2 = EX.delta_dv_linsolve(gam, y.Om, y.V, R)
        assert float(jnp.abs(d1 - d2).max()) <= 1e-13


def test_full_rhs_two_routes_with_kappa():
    """★ 차트 배선: rhs (닫힌식) ≡ rhs_via_general (선형해) — κ 켠 채."""
    y = _rand_state(2, seed=3)
    args = dict(gammas=np.array([4.0/3.0, 1.2]), kappa=_kappa(2))
    d1 = M.rhs(0.0, y, args).as_array()
    d2 = M.rhs_via_general(0.0, y, args).as_array()
    assert float(jnp.abs(d1 - d2).max()) <= 1e-13


def test_kappa_zero_reduces_to_h1():
    """κ=0 ≡ 교환 무 — 정확 일치."""
    y = _rand_state(2, seed=4)
    args0 = dict(gammas=np.array([4.0/3.0, 1.2]))
    argsk = dict(args0, kappa=np.zeros((2, 2)))
    d0 = M.rhs(0.0, y, args0).as_array()
    dk = M.rhs(0.0, y, argsk).as_array()
    assert float(jnp.abs(d0 - dk).max()) == 0.0


def test_total_momentum_rate_is_kappa_invariant():
    """★★ 보존의 실측: d(q̂_tot)/dτ 가 κ 무관 (JVP) — δdΩ=0 도 함께."""
    y = _rand_state(3, seed=6)
    gam = np.array([4.0/3.0, 1.0, 1.7])
    args0 = dict(gammas=gam)
    argsk = dict(gammas=gam, kappa=_kappa(3))

    def qtot_of(arr):
        return M.aux(M.StateATM.from_array(arr), args0)["q_tot"]

    arr = y.as_array()
    r0 = M.rhs(0.0, y, args0)
    rk = M.rhs(0.0, y, argsk)
    assert float(jnp.abs(rk.Om - r0.Om).max()) == 0.0          # δdΩ = 0
    assert float(jnp.abs(rk.Sigma5 - r0.Sigma5).max()) == 0.0  # 기하 무변
    _, dq0 = jax.jvp(qtot_of, (arr,), (r0.as_array(),))
    _, dqk = jax.jvp(qtot_of, (arr,), (rk.as_array(),))
    assert float(jnp.abs(dqk - dq0).max()) <= 1e-13


def test_gauss_closure_survives_exchange():
    """★ Gauss 전파 닫힘 — κ>0 에서도 (δdΩ=0 의 귀결, 실측)."""
    y = _rand_state(2, seed=21)
    a = M.aux(y, dict(gammas=np.ones(2)))
    target = 1.0 - a["Sigma2"] - a["K"]
    y = M.StateATM.of(y.Sigma5, y.N3, y.Om * target / jnp.sum(y.Om), y.V)
    args = dict(gammas=np.array([4.0/3.0, 1.0]), kappa=_kappa(2))

    def gauss_of(arr):
        return M.aux(M.StateATM.from_array(arr), args)["gauss"]

    arr = y.as_array()
    darr = M.rhs(0.0, M.StateATM.from_array(arr), args).as_array()
    _, dg = jax.jvp(gauss_of, (arr,), (darr,))
    assert abs(float(dg)) <= 1e-13


def test_drag_equilibrates_relative_velocity():
    """★ 끌림 평형화: 소-v 상대속도 지수감쇠 — 해석율
    λ = κ(Ω₂/γ₁ + Ω₁/γ₂)/3 (소-v: G₊→1; **1/3 은 q̂=3γΩv 의 3** — 첫 판이
    이걸 빠뜨려 ×3 반증됨) 과 궤적 적합 대조 ≤3%.  γ 둘 다 4/3 로 배경
    T-항 (3γ−4) 을 정확 소거 — 순수 교환 감쇠만 잰다."""
    gam = np.array([4.0/3.0, 4.0/3.0])
    Om = np.array([0.5, 0.3])
    kap = np.zeros((2, 2))
    kap[0, 1] = kap[1, 0] = 30.0                       # 교환 지배 영역
    y = M.StateATM.of(np.zeros(5), [1e-6, -2e-6, 3e-6], Om,
                      np.array([[0.02, 0.0, 0.0], [-0.02, 0.0, 0.0]]))
    args = dict(gammas=gam, kappa=kap)
    arr = y.as_array()

    def f(a):
        return M.rhs(0.0, M.StateATM.from_array(a), args).as_array()

    h, nstep = 2e-4, 400                               # τ ∈ [0, 0.08]
    rels = []
    for _ in range(nstep):
        k1 = f(arr)
        k2 = f(arr + 0.5*h*k1)
        k3 = f(arr + 0.5*h*k2)
        k4 = f(arr + h*k3)
        arr = arr + (h/6.0)*(k1 + 2.0*k2 + 2.0*k3 + k4)
        yv = M.StateATM.from_array(arr)
        rels.append(float(jnp.abs(yv.V[0, 0] - yv.V[1, 0])))
    rels = np.array(rels)
    assert rels[-1] < rels[0]                          # 감쇠
    lam_fit = -np.polyfit(h*np.arange(1, nstep + 1), np.log(rels), 1)[0]
    lam = kap[0, 1] * (Om[1]/gam[0] + Om[0]/gam[1]) / 3.0
    assert abs(lam_fit - lam) / lam <= 0.03, (lam_fit, lam)


def test_kappa_validation_rejects_bad_matrices():
    """★ 비대칭·비영대각 κ 명시 거부 (총 보존 위반 예방)."""
    y = _rand_state(2, seed=9)
    bad = np.array([[0.0, 1.0], [0.5, 0.0]])
    with pytest.raises(ValueError, match="대칭"):
        M.rhs(0.0, y, dict(gammas=np.array([1.0, 1.5]), kappa=bad))
    bad2 = np.array([[0.1, 0.3], [0.3, 0.0]])
    with pytest.raises(ValueError, match="대각"):
        M.rhs(0.0, y, dict(gammas=np.array([1.0, 1.5]), kappa=bad2))
