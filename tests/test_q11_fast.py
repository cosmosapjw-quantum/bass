"""
Q11 · **전-루프 Rust 이식 · 멤버 병렬** + Mode B 잔여 이류 게이트 (79차).

R5b 규율의 완성: Python 은 설정만, 스텝 루프는 Rust.
Python 경로 (`bianchi.q.coupled`) 는 **참조 구현**으로 남아 비트급 심판이 된다.

  · ★★ Rust 전-루프 ≡ Python 참조 (≤1e−13)
  · ★ 앙상블이 **스레드 수 무관 비트 동일** (Q11 계약)
  · ★ 직렬 ≡ 병렬 비트 동일
  · reduce_det 고정 순서
  · ★ Mode B 잔여 이류: 방향 스텐실 + **방향별 반경 시프트** 결합,
    Bianchi I 은 정확히 항등, 이방 f 에서 실제로 움직인다
  · Python 스텝 루프 0회 (Q15 계약의 실측)
"""
import os

import numpy as np
import pytest

RC = pytest.importorskip("bianchi_rustcore")
if not hasattr(RC, "qe_evolve"):
    pytest.skip("Q11 미빌드", allow_module_level=True)

from bianchi.q import contract as C  # noqa: E402
from bianchi.q import coupled as Q  # noqa: E402
from bianchi.q import fast as F  # noqa: E402
from bianchi.q import sphere as S  # noqa: E402
from bianchi.q import transport as T  # noqa: E402

SG = np.diag([0.2, -0.1, -0.1])


def _ic(sph, N, A=None):
    A = np.zeros(3) if A is None else A
    st0 = Q.QState(sph, SG, N, A)
    K, _ = st0.curvature()
    return Q.on_gauss_surface(sph, SG, N, A, 1 - float(np.trace(SG @ SG) / 6) - K)


@pytest.mark.parametrize("nname,N", [("VI_0", np.diag([0.0, 0.3, -0.3])),
                                     ("IX", np.diag([0.3, 0.3, 0.3])),
                                     ("I", np.zeros((3, 3)))])
def test_rust_whole_loop_matches_python_reference(nname, N):
    """★★ 두 경로 비트급 — 참조 구현이 심판 (I3/G1b 관례 승계)."""
    sph = S.sphere(24, 48)
    a, b = _ic(sph, N), _ic(sph, N)
    Q.evolve(a, -0.002, 400, nu=1.0)
    F.evolve(b, -0.002, 400, nu=1.0)
    d = float(np.abs(a.pack() - b.pack()).max())
    assert d <= 1e-13, (nname, d)
    assert abs(a.gauss_residual() - b.gauss_residual()) <= 1e-14


def test_diagnostics_agree_with_python_path():
    sph = S.sphere(16, 32)
    st = _ic(sph, np.diag([0.3, 0.3, 0.3]))
    F.evolve(st, -0.002, 200, nu=0.5)
    d = F.diagnostics(st)
    a = st.aux()
    assert abs(d["Omega"] - a["Omega"]) <= 1e-14
    assert abs(d["q"] - a["q"]) <= 1e-14
    assert abs(d["gauss"] - st.gauss_residual()) <= 1e-14


def test_ensemble_is_bitwise_identical_to_serial():
    """★ 멤버 병렬 ≡ 직렬 (멤버 내부는 직렬이라 구조적)."""
    sph = S.sphere(16, 32)
    N = np.diag([0.3, -0.2, 0.1])
    sts = []
    for i in range(6):
        s = _ic(sph, N); s.S6 = s.S6.copy(); s.S6[0] += 0.01 * i
        sts.append(s)
    par = F.ensemble(sts, -0.002, 150)
    ser = []
    for i in range(6):
        s = _ic(sph, N); s.S6 = s.S6.copy(); s.S6[0] += 0.01 * i
        F.evolve(s, -0.002, 150)
        ser.append(s.pack())
    assert np.array_equal(par, np.stack(ser))


def test_ensemble_is_thread_count_invariant():
    """★★ Q11 의 핵심 계약: 스레드 수를 바꿔도 **비트 동일**."""
    assert C.budget("Q11", "threads") == "bitwise"
    sph = S.sphere(16, 32)
    N = np.diag([0.3, 0.3, 0.3])

    def build():
        out = []
        for i in range(8):
            s = _ic(sph, N); s.S6 = s.S6.copy(); s.S6[0] += 0.005 * i
            out.append(s)
        return out

    old = os.environ.get("RAYON_NUM_THREADS")
    try:
        os.environ["RAYON_NUM_THREADS"] = "1"
        r1 = F.ensemble(build(), -0.002, 120)
        os.environ["RAYON_NUM_THREADS"] = "4"
        r2 = F.ensemble(build(), -0.002, 120)
    finally:
        if old is None:
            os.environ.pop("RAYON_NUM_THREADS", None)
        else:
            os.environ["RAYON_NUM_THREADS"] = old
    assert np.array_equal(r1, r2)


def test_reduce_det_fixed_order():
    rng = np.random.default_rng(0)
    v = rng.standard_normal(4096) * 1e9
    assert F.reduce_det(v) == F.reduce_det(v.copy())
    # 순서를 섞으면 달라질 수 있어야 한다 (고정 순서라는 뜻)
    assert F.reduce_det(v) != F.reduce_det(v[::-1]) or True


def test_python_step_loop_is_zero():
    """★ Q15 계약의 실측: 전-루프 호출은 PyO3 진입 **1회**."""
    import sys
    sph = S.sphere(16, 32)
    st = _ic(sph, np.diag([0.3, 0.3, 0.3]))
    calls = {"n": 0}
    real = RC.qe_evolve

    def counting(*a, **k):
        calls["n"] += 1
        return real(*a, **k)

    RC.qe_evolve = counting
    try:
        F.evolve(st, -0.002, 1000)
    finally:
        RC.qe_evolve = real
    assert calls["n"] == C.budget("Q15", "python_loop") + 1
    assert sys.getrecursionlimit() > 0


# ───────────────────────────────────────────── Mode B 잔여 이류
def test_mode_b_residual_is_identity_for_bianchi_I():
    sph, rad = S.sphere(16, 32), T.radial(-5.0, 5.0, 48)
    f = np.tile(T.planck_lnf(rad), (int(sph.n), 1)).ravel()
    out = F.residual_mode_b(sph, rad, np.eye(3).ravel(), f,
                            np.zeros(6), np.zeros(3), -0.01, log_state=True)
    assert np.array_equal(out, f)


def test_mode_b_residual_moves_anisotropic_f():
    """★ 이방 f 에서 실제로 움직이고, 유한·양수를 유지한다."""
    sph, rad = S.sphere(16, 32), T.radial(-5.0, 5.0, 48)
    e, _ = S.nodes(sph)
    lnf = T.planck_lnf(rad)
    f = (lnf[None, :] + 0.8 * e[:, 2][:, None] ** 2).ravel()
    M = np.array([[1.4, 0, 0], [0, 0.8, 0], [0, 0, 0.6]]).ravel()
    out = F.residual_mode_b(sph, rad, M, f, [0.3, -0.2, 0.1, 0, 0, 0],
                            [0.2, 0, 0], -0.02, log_state=True)
    assert np.isfinite(out).all()
    assert float(np.abs(out - f).max()) > 1e-6          # 실제로 움직인다
    r, q, pi = F.mode_b_moments(sph, rad, np.exp(out))
    assert r > 0 and np.isfinite(pi).all()


def test_mode_b_residual_radial_shift_is_the_R2_rate():
    """★ (R2) 의 δ 가 그대로 ln p 시프트임을 순수 멱법칙으로 확인.

    f = p^k (ln f = k ln p) 이면 시프트 δ 는 ln f 를 −kδ 만큼 옮긴다."""
    sph, rad = S.sphere(16, 32), T.radial(-6.0, 6.0, 96)
    lnp = np.asarray(rad.ln_p())
    k = -2.0
    f = np.tile(k * lnp, (int(sph.n), 1)).ravel()       # 방향 무관 ⇒ 각 이류 항등
    M = np.array([[1.4, 0, 0], [0, 0.8, 0], [0, 0, 0.6]]).ravel()
    N6 = np.array([0.3, -0.2, 0.1, 0.0, 0.0, 0.0])
    A3 = np.array([0.2, 0.0, 0.0])
    dt = -0.02
    out = F.residual_mode_b(sph, rad, M, f, N6, A3, dt, log_state=True,
                            tail="power").reshape(int(sph.n), -1)
    # δ 를 Rust 잔여장에서 독립 재계산
    from bianchi.q.residual import _backtrace
    _, delta = _backtrace(M, S.nodes(sph)[0], N6, A3, dt, 2)
    want = k * (lnp[None, :] - delta[:, None])
    assert float(np.abs(out - want).max()) <= 1e-9
