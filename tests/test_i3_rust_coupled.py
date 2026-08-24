"""
I3 · **결합 루프 Rust 전면화** (69차) — R5b (루프째) + J3 표 + U-기저 캐리.

게이트: cp_rhs ≡ Python coupled_rhs (nc=0/1/2 × κ × N-항 on/off, 무작위 상태)
≤1e−14; 물리 IC 궤적 루프째 패리티 ≤1e−13 (실측 ~1e−16); keep-궤적 형상;
u-표 길이 가드; 속도 (실측 ×1000+; 게이트는 ×10 — 타이밍 플레이크 여유).
"""
import numpy as np
import pytest

from bianchi.matter import coupled_tilted as CT

pytest.importorskip("bianchi_rustcore")


def _phys_state(nc, lmax, seed=3):
    import jax.numpy as jnp

    from bianchi.charts import class_a_tilted_multi as MM
    rng = np.random.default_rng(seed)
    S5 = np.array([0.12, -0.07, 0.03, -0.02, 0.04])
    N3 = np.array([0.8, -0.5, 0.3])
    K = float(MM.aux(MM.StateATM.of(S5, N3, np.zeros(1), np.zeros((1, 3))),
                     dict(gammas=np.ones(1)))["K"])
    Jc = {(l, 0): 0.02*rng.standard_normal(2*l + 1) for l in range(lmax + 1)}
    Jc[(0, 0)] = np.array([1.2])
    Ok = 1.2/3.0
    rest = 1.0 - float(S5 @ S5) - K - Ok
    Om = np.full(nc, rest/nc) if nc else np.zeros(0)
    V = 0.05*rng.standard_normal((nc, 3)) if nc else np.zeros((0, 3))
    return CT.pack(S5, N3, 0.0, Om, V, Jc, lmax)


@pytest.mark.parametrize("nc,use_kappa,nterm", [
    (0, False, True), (1, False, True), (2, True, True), (2, True, False)])
def test_rhs_parity(nc, use_kappa, nterm):
    """★★ I3 의 심판 1: cp_rhs ≡ Python coupled_rhs — 전 구성."""
    lmax = 4
    gam = np.array([4.0/3.0, 1.1][:nc])
    kap = None
    if use_kappa:
        kap = np.zeros((nc, nc))
        kap[0, 1] = kap[1, 0] = 0.7
    for seed in (3, 7):
        y = _phys_state(nc, lmax, seed)
        a = CT.coupled_rhs(y, gam, lmax, kappa=kap, nterm_on=nterm)
        b = CT.coupled_rhs_rust(y, gam, lmax, kappa=kap, nterm_on=nterm)
        assert np.abs(a - b).max() <= 1e-14, (nc, seed)


def test_trajectory_parity_loop_whole():
    """★★ I3 의 심판 2: 루프째 궤적 — 물리 IC, τ=1.0/400 ≤1e−13 (실측 ~1e−16)."""
    lmax = 4
    gam = np.array([4.0/3.0])
    y = _phys_state(1, lmax)
    yp = CT.rk4_evolve(y, gam, lmax, 1.0, 400)
    yr = CT.rk4_evolve_rust(y, gam, lmax, 1.0, 400)
    assert np.isfinite(yr).all()
    assert np.abs(yp - yr).max() <= 1e-13


def test_keep_trajectory_shape_and_head():
    """★ keep: (nsteps+1, dim), 행0 = IC."""
    lmax = 3
    y = _phys_state(0, lmax)
    yT, traj = CT.rk4_evolve_rust(y, np.zeros(0), lmax, 0.3, 50, keep=True)
    assert traj.shape == (51, y.size)
    assert np.abs(traj[0] - y).max() == 0.0
    assert np.abs(traj[-1] - yT).max() == 0.0


def test_input_guards():
    """★ u-표/부호 길이 가드 (FFI 검증)."""
    import bianchi_rustcore as R
    y = _phys_state(0, 2)
    with pytest.raises(Exception, match="u1"):                # 74차: +nu_bgk
        R.cp_rhs(y, np.zeros(0), None, 2, True, np.zeros(5), np.zeros(45),
                 np.array([1.0, -1.0, -1.0]), 0.0)


def test_speed_at_least_10x():
    """★ 속도 (실측 ×1000+): 게이트 ×10 — 타이밍 플레이크 여유 (관례: 실패 시
    단독 재실행 판정)."""
    import time
    lmax = 4
    gam = np.array([4.0/3.0])
    y = _phys_state(1, lmax)
    t0 = time.perf_counter()
    CT.rk4_evolve(y, gam, lmax, 0.25, 100)
    tp = time.perf_counter() - t0
    t0 = time.perf_counter()
    CT.rk4_evolve_rust(y, gam, lmax, 0.25, 100)
    tr = time.perf_counter() - t0
    assert tp / tr > 10.0, (tp, tr)
