"""
P8 · **P 층 ↔ Q 층 합성** + P9b **부스트** + P9c **Mode B** 게이트 (84–85차).

★★ 박제하는 것
  1. 자유흐름에서 I 채널이 스칼라 Q 경로와 **비트 동일** (11유형 대표 4종).
  2. 무편광은 무편광으로 남는다 — 곡률이 있어도, **각 해상도와 무관하게**.
  3. 충돌 차는 P4 의 닫힌형 ΔI 다.
  4. (P9b) 부스트 하 스크린 회전 ψ = 0, 배율 1 ⇒ 편광×부스트가 세 단계로 끝난다.
  5. (P9c) Mode B 편광 Rust ≡ Python, 반경 슬라이스 = Mode A.
"""
import numpy as np
import pytest

from audit import p9_boost_screen as A9
from audit.p3_polarized_thomson import grid
from bianchi.q import contract as C
from bianchi.q import coupled as QC
from bianchi.q import polarization as PL
from bianchi.q import polstate as PS
from bianchi.q import sphere as S

SIG = np.diag([0.2, -0.1, -0.1])
CASES = [("I", np.zeros((3, 3)), np.zeros(3)),
         ("IX", np.diag([0.3, 0.3, 0.3]), np.zeros(3)),
         ("VIII", np.diag([0.4, -0.3, 0.1]), np.zeros(3)),
         ("V", np.zeros((3, 3)), np.array([0.4, 0.0, 0.0]))]


def _mk(sph, N, A):
    K, _ = QC.QState(sph, SIG, N, A).curvature()
    return QC.on_gauss_surface(sph, SIG, N, A,
                               1 - float(np.trace(SIG @ SIG) / 6) - K,
                               aniso=lambda e: 1.0 + 0.5 * e[2] ** 2)


def _pw(st):
    _, e, _, lw = st.geometry()
    w = np.exp(lw - lw.max())
    return e, w * (4 * np.pi / w.sum())


def _p2(e, w, f):
    u = e @ e.T
    return (5.0 / (4 * np.pi)) * ((1.5 * u ** 2 - 0.5) @ (w * f))


# ─────────────────────────────────────────────────────────── P8
@pytest.mark.parametrize("name,N,A", CASES)
def test_p8_freestream_intensity_is_bitwise_scalar_path(name, N, A):
    """★★ P4 의 나머지 절반: 지표 수송이 tr(dJ)=0 이라 진폭을 손대지 않는다."""
    sph = S.sphere(16, 32)
    a, b = _mk(sph, N, A), PS.PolQState(_mk(sph, N, A))
    h = -0.5 / 50
    for _ in range(50):
        a.residual_step(0.5 * h); a.rk4_step(h); a.residual_step(0.5 * h)
        b.residual_step(0.5 * h); b.rk4_step(h); b.residual_step(0.5 * h)
    assert float(np.abs(a.lG - b.st.lG).max()) == 0.0, name


@pytest.mark.parametrize("name,N,A", CASES)
def test_p8_freestream_generates_no_polarization(name, N, A):
    """★★ 각 해상도와 **무관하게** 무편광이 유지된다 (무편광 부분을 해석 분리)."""
    tol = C.budget("P8", "freestream_polarization")
    vals = []
    for nt in (16, 32):
        b = PS.PolQState(_mk(S.sphere(nt, 2 * nt), N, A))
        h = -0.5 / 50
        for _ in range(50):
            b.residual_step(0.5 * h); b.rk4_step(h); b.residual_step(0.5 * h)
        vals.append(float(b.polarization_fraction().max()))
        assert b.screen_leak() <= C.budget("P8", "screen_leak"), name
        assert b.trace_error() <= C.budget("P8", "trace"), name
    assert max(vals) <= tol, (name, vals)
    assert abs(vals[0] - vals[1]) / max(vals) <= 0.05, (name, vals)


def test_p8_freestream_polarization_converges_in_dtau():
    sph = S.sphere(16, 32)
    errs = []
    for ns in (25, 50, 100):
        b = PS.PolQState(_mk(sph, np.diag([0.4, -0.3, 0.1]), np.zeros(3)))
        h = -0.5 / ns
        for _ in range(ns):
            b.residual_step(0.5 * h); b.rk4_step(h); b.residual_step(0.5 * h)
        errs.append(float(b.polarization_fraction().max()))
    ords = [float(np.log2(errs[i] / errs[i + 1])) for i in range(2)]
    assert min(ords) >= 2.5, (ords, errs)


def test_p8_collision_difference_matches_closed_form():
    """★★ 충돌 차 = P4 닫힌형 ΔI (합성 경로 위에서 재현)."""
    sph = S.sphere(24, 48)
    tol = C.budget("P8", "collide_closed_form")
    N = np.diag([0.4, -0.3, 0.1])
    for x in (0.05, 0.2, 1.0):
        a, b = _mk(sph, N, np.zeros(3)), PS.PolQState(_mk(sph, N, np.zeros(3)))
        e, w = _pw(a)
        ref = a.lG.max()
        I0 = np.exp(a.lG - ref)
        a.collide(x); b.collide(x)
        got = np.exp(b.st.lG - ref) - np.exp(a.lG - ref)
        want = PL.unpolarized_delta_closed(x, _p2(e, w, I0))
        assert float(np.abs(got - want).max()) <= tol, x


def test_p8_number_conserved_and_strang_runs():
    b = PS.PolQState(_mk(S.sphere(16, 32), np.diag([0.4, -0.3, 0.1]), np.zeros(3)))
    _, w = _pw(b.st)
    ref = b.st.lG.max()
    n0 = float((w * np.exp(b.st.lG - ref)).sum())
    b.collide(2.0)
    assert abs(float((w * np.exp(b.st.lG - ref)).sum()) - n0) / n0 <= \
        C.budget("P8", "number")
    PS.evolve(b, -0.01, 10, nu=1.0)
    assert np.isfinite(b.st.lG).all() and np.isfinite(b.Jhat).all()


# ─────────────────────────────────────────────────────── P9a/P9b
def test_p9a_boost_screen_map_has_no_extra_rotation():
    """★★ D7: 계획의 예상 ('광행차가 스크린을 돌린다') 이 **기각**된다."""
    r = A9.run(n=200, seed=11, vmax=0.6)
    assert r["psi"] <= C.budget("P9", "psi_boost"), r
    assert r["scale"] <= C.budget("P9", "boost_scale"), r
    assert r["aniso"] <= 1e-13 and r["leak"] <= 1e-13
    assert r["roundtrip"] <= C.budget("P9", "boost_roundtrip"), r


def test_p9a_boost_preserves_unpolarized_and_trace():
    rng = np.random.default_rng(5)
    w = [0.0, 0.0]
    for _ in range(100):
        v = rng.standard_normal(3); v *= rng.uniform(0.01, 0.5) / np.linalg.norm(v)
        e = rng.standard_normal(3); e /= np.linalg.norm(e)
        Pi = np.eye(3) - np.outer(e, e)
        Jp, ep = A9.tensor_boost(0.5 * Pi, v, e)
        w[0] = max(w[0], float(np.abs(Jp - 0.5 * (np.eye(3) - np.outer(ep, ep))).max()))
        J = rng.standard_normal((3, 3)); J = Pi @ (0.5 * (J + J.T)) @ Pi
        Jb, _ = A9.tensor_boost(J, v, e)
        w[1] = max(w[1], abs(float(np.trace(Jb)) - float(np.trace(J))))
    assert w[0] <= 1e-13 and w[1] <= 1e-13, w


def test_p9b_boosted_collision_runs_and_reduces_to_rest_frame():
    """★ v→0 에서 정지계 결과로 **1차**로 수렴한다 (도플러가 O(v))."""
    sph = S.sphere(16, 32)
    base = PS.PolQState(_mk(sph, np.zeros((3, 3)), np.zeros(3)))
    base.collide(1.0)
    errs = []
    for v in (1e-3, 1e-4, 1e-5):
        c = PS.PolQState(_mk(sph, np.zeros((3, 3)), np.zeros(3)))
        c.collide(1.0, v_b=np.array([v, 0.0, 0.0]))
        assert c.screen_leak() <= C.budget("P8", "screen_leak")
        assert c.trace_error() <= C.budget("P8", "trace")
        errs.append(float(np.abs(c.st.lG - base.st.lG).max()))
    p, tol = C.budget("P9", "v_to_zero_order")
    ords = [float(np.log10(errs[i] / errs[i + 1])) for i in range(2)]
    assert all(abs(o - p) <= tol for o in ords), (ords, errs)


def test_p9b_boost_with_zero_velocity_is_the_rest_frame_path():
    sph = S.sphere(16, 32)
    a = PS.PolQState(_mk(sph, np.zeros((3, 3)), np.zeros(3))); a.collide(1.0)
    b = PS.PolQState(_mk(sph, np.zeros((3, 3)), np.zeros(3)))
    b.collide(1.0, v_b=np.zeros(3))
    assert float(np.abs(a.st.lG - b.st.lG).max()) == 0.0
    assert float(np.abs(a.Jhat - b.Jhat).max()) == 0.0


# ────────────────────────────────────────────────────────── P9c
def test_p9c_modeb_rust_matches_python_and_mode_a():
    """★ Mode B 편광: Rust ≡ Python, 그리고 반경 슬라이스 = Mode A (핵이 에너지 무관)."""
    e, w = grid(16, 32)
    n_p = 12
    rng = np.random.default_rng(2)
    J = PL.project_screen(e, rng.standard_normal((len(w), 3, 3)))
    Jb = np.repeat(J[:, None], n_p, axis=1) * (1.0 + 0.1 * np.arange(n_p))[None, :, None, None]
    a = PS.collide_modeb(e, w, Jb, n_p, 1.7, backend="python")
    b = PS.collide_modeb(e, w, Jb, n_p, 1.7, backend="rust")
    rel = float(np.abs(a - b).max() / max(np.abs(a).max(), 1e-300))
    assert rel <= C.budget("P9", "modeb_rust_vs_python"), rel
    for jj in (0, n_p // 2, n_p - 1):
        want = PL.collide(e, w, Jb[:, jj], 1.7)
        assert float(np.abs(b[:, jj] - want).max()) <= \
            C.budget("P9", "modeb_slice_identity"), jj


def test_p9c_modeb_zero_x_is_identity_and_rejects_negative():
    e, w = grid(12, 24)
    n_p = 4
    J = np.repeat(PL.project_screen(e, np.ones((len(w), 3, 3)))[:, None], n_p, axis=1)
    # x=0 은 커널에서 항등이지만 pack9/unpack9 왕복에 반올림이 남는다 (비트 아님)
    assert float(np.abs(PS.collide_modeb(e, w, J, n_p, 0.0) - J).max()) <= 1e-15
    import bianchi_rustcore as R
    with pytest.raises(ValueError):
        R.qp_collide_modeb(np.ascontiguousarray(e.ravel()),
                           np.ascontiguousarray(w),
                           np.ascontiguousarray(PL.pack9(J.reshape(-1, 3, 3)).ravel()),
                           n_p, -0.1)
