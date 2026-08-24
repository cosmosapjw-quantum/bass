"""
통합 검증 — `bianchi.backend` 디스패치가 Rust/Python 두 경로에서 같은 답을 준다.

계획 §2 하이브리드의 인수 조건: 공개 API 는 백엔드에 무관해야 하고, Rust 가 없으면
조용히 오라클로 폴백해야 한다.
"""
import numpy as np
import pytest

from bianchi import backend


MODEL = dict(H0=1.0, Sigma0=np.array([0.05, -0.025, -0.025]), Omega0=0.3, gamma=4 / 3)


def test_backend_reports_state():
    assert backend.name() in ("rust", "python")
    info = backend.info()
    assert info["backend"] == backend.name()
    if backend.available():
        assert "integrate_batch" in info["functions"]


def test_ray_batch_paths_agree():
    nhats = np.random.default_rng(0).normal(size=(8, 3))
    a = backend.ray_final_z_batch(MODEL, nhats, 0.0, -0.25, 400)
    b = backend.ray_final_z_batch(MODEL, nhats, 0.0, -0.25, 400, force_python=True)
    np.testing.assert_allclose(a, b, rtol=1e-10, atol=1e-12)


def test_optical_paths_agree():
    nhats = np.random.default_rng(1).normal(size=(4, 3))
    za, da = backend.optical_batch(MODEL, nhats, 0.0, -0.25, 300)
    zb, db = backend.optical_batch(MODEL, nhats, 0.0, -0.25, 300, force_python=True)
    np.testing.assert_allclose(za, zb, rtol=1e-10, atol=1e-12)
    np.testing.assert_allclose(da, db, rtol=1e-10, atol=1e-12)


def test_chart_rhs_paths_agree():
    rng = np.random.default_rng(2)
    for _ in range(20):
        y = rng.normal(size=5) * 0.4
        g = float(rng.uniform(1.0, 1.8))
        np.testing.assert_allclose(backend.chart_rhs("class_a", y, g),
                                   backend.chart_rhs("class_a", y, g, force_python=True),
                                   rtol=1e-13, atol=1e-15)


def test_integrate_background_paths_agree():
    """diffsol BDF 와 diffrax Kvaerno5 — 서로 다른 적분기이므로 이산화 수준 일치."""
    ts = np.linspace(0.0, 2.5, 21)
    y0 = np.array([0.3, -0.15, 0.35, 0.2, 0.0])
    a, ok_a = backend.integrate_background("class_a", y0, ts, 4 / 3, rtol=1e-12, atol=1e-14)
    b, ok_b = backend.integrate_background("class_a", y0, ts, 4 / 3, rtol=1e-12, atol=1e-14,
                                           force_python=True)
    assert ok_a and ok_b
    assert np.max(np.abs(a - b)) / max(1e-30, np.max(np.abs(b))) < 1e-8


def test_integrate_batch_paths_agree():
    rng = np.random.default_rng(3)
    y0s = np.column_stack([rng.uniform(-.3, .3, 6), rng.uniform(-.3, .3, 6),
                           abs(rng.normal(size=6)) * .3, abs(rng.normal(size=6)) * .3,
                           np.zeros(6)])
    ts = np.linspace(0.0, 2.0, 11)
    ya, oka = backend.integrate_batch("class_a", y0s, ts, 4 / 3, rtol=1e-12, atol=1e-14)
    yb, okb = backend.integrate_batch("class_a", y0s, ts, 4 / 3, rtol=1e-12, atol=1e-14,
                                      force_python=True)
    assert np.array_equal(oka, okb)
    m = oka
    assert np.max(np.abs(ya[m] - yb[m])) / max(1e-30, np.max(np.abs(yb[m]))) < 1e-8


def test_batch_isolates_failures():
    """비물리(Ω<0) 초기조건이 섞여도 나머지 원소는 정상 완료 (낙오자 격리)."""
    ts = np.linspace(0.0, 3.0, 11)
    good = np.array([0.2, -0.1, 0.3, 0.2, 0.0])
    bad = np.array([0.99, 0.5, 0.9, 0.9, 0.0])      # Ω < 0
    y0s = np.vstack([good, bad, good, bad, good])
    ys, ok = backend.integrate_batch("class_a", y0s, ts, 4 / 3, rtol=1e-8, atol=1e-10)
    assert ok[0] and ok[2] and ok[4], "정상 원소가 낙오자에 오염됨"
    assert np.all(np.isfinite(ys[[0, 2, 4]]))


def test_legacy_dispatch_alias():
    """구 `rays._dispatch` API 가 backend 로 재노출되어 계속 동작."""
    from bianchi.rays import _dispatch as d
    assert d.backend() in ("rust", "python")
    nhats = np.random.default_rng(4).normal(size=(4, 3))
    np.testing.assert_allclose(
        d.ray_final_z_batch(MODEL, nhats, 0.0, -0.2, 300),
        backend.ray_final_z_batch(MODEL, nhats, 0.0, -0.2, 300), rtol=1e-14)


# ─────────────────────────────── 운동론 계층 디스패치 (H2/H3/H4)
# ★ 두 경로를 디스패치 층에서도 분리 유지하는지 확인 — Rust 전환으로 교차검증을 잃지 않기.
@pytest.mark.parametrize("l", [0, 2, 4])
def test_backend_j_moment_both_paths(l):
    """`j_moment` 가 Rust/Python 양쪽에서 같은 모멘트 (l=0 은 스칼라 반환)."""
    a = np.array([1.0, 0.85, 1.18])
    r = backend.j_moment(a, 0.5, l, 0)
    p = backend.j_moment(a, 0.5, l, 0, force_python=True)
    rho = float(backend.j_moment(a, 0.5, 0, 0, force_python=True))
    if l == 0:
        assert isinstance(r, float) and abs(r / p - 1.0) < 1e-12
    else:
        assert np.asarray(r).shape == (3,) * l
        assert np.abs(np.asarray(r) - np.asarray(p)).max() / rho < 1e-12


def test_backend_kinetic_moments_both_paths():
    rho_r, p_r, pi_r = backend.kinetic_moments([1.0, 0.85, 1.2], 0.8)
    rho_p, p_p, pi_p = backend.kinetic_moments([1.0, 0.85, 1.2], 0.8, force_python=True)
    assert abs(rho_r / rho_p - 1.0) < 1e-12
    assert abs(p_r / p_p - 1.0) < 1e-12
    assert np.abs(pi_r - pi_p).max() / rho_p < 1e-12


def test_backend_hierarchy_integrate_both_paths():
    """무충돌 궤적이 Rust/Python 양쪽에서 일치 (ρ, π_ab)."""
    kw = dict(nsteps=40, l_max=4, i_max=2)
    r = backend.hierarchy_integrate([1.0, 1.0, 1.0], 0.0, 1.0, [0.06, -0.02, -0.04],
                                    0.3, **kw)
    p = backend.hierarchy_integrate([1.0, 1.0, 1.0], 0.0, 1.0, [0.06, -0.02, -0.04],
                                    0.3, force_python=True, **kw)
    assert np.abs(r["rho"] - p["rho"]).max() / np.abs(p["rho"]).max() < 1e-11
    assert np.abs(r["pi"] - p["pi"]).max() / np.abs(p["pi"]).max() < 1e-9


def test_backend_collision_reduces_to_free_at_zero_rate():
    """★ n_eσ_T=0 이면 무충돌 경로와 **비트-정확** 동일 (회귀 보호)."""
    kw = dict(nsteps=40, l_max=4, i_max=2)
    a = backend.hierarchy_integrate([1.0, 1.0, 1.0], 0.0, 1.0, [0.06, -0.02, -0.04],
                                    0.3, n_e_sigma_T=0.0, **kw)
    b = backend.hierarchy_integrate([1.0, 1.0, 1.0], 0.0, 1.0, [0.06, -0.02, -0.04],
                                    0.3, **kw)
    np.testing.assert_array_equal(a["rho"], b["rho"])
    np.testing.assert_array_equal(a["pi"], b["pi"])


@pytest.mark.skipif(not backend.available(),
                    reason="충돌 궤적은 Rust 경로만 제공한다 (Python 폴백은 "
                           "NotImplementedError — backend.py 의 명시적 설계)")
def test_backend_collision_damps_pi():
    kw = dict(nsteps=200, l_max=4, i_max=2)
    f = backend.hierarchy_integrate([1.0, 0.85, 1.18], 0.0, 1.0, [0.05, -0.02, -0.03],
                                    0.2, n_e_sigma_T=0.0, **kw)
    c = backend.hierarchy_integrate([1.0, 0.85, 1.18], 0.0, 1.0, [0.05, -0.02, -0.03],
                                    0.2, n_e_sigma_T=5.0, **kw)
    assert np.abs(c["pi"][-1]).max() < np.abs(f["pi"][-1]).max()


def test_backend_collisional_python_fallback_is_explicit():
    """★ 충돌 궤적의 Python 폴백은 **없다** — 조용히 무충돌로 떨어지지 않고 예외."""
    with pytest.raises(NotImplementedError):
        backend.hierarchy_integrate([1.0, 1.0, 1.0], 0.0, 1.0, [0.06, -0.02, -0.04],
                                    0.3, n_e_sigma_T=1.0, force_python=True)


@pytest.mark.parametrize("route", ["analytic", "numeric"])
def test_backend_thomson_eigenvalue_both_routes_both_paths(route):
    """λ_l 이 (경로 A/B) × (Rust/Python) 네 조합에서 모두 일치."""
    for l in range(6):
        r = backend.thomson_eigenvalue(l, route)
        p = backend.thomson_eigenvalue(l, route, force_python=True)
        assert abs(r - p) < 1e-13, (l, route)
        assert abs(r - (1.0 if l == 0 else 0.1 if l == 2 else 0.0)) < 1e-12


def test_backend_thomson_viscosity_both_paths():
    for flag, target in ((True, 8.0 / 27.0), (False, 4.0 / 15.0)):
        r = backend.thomson_viscosity(1.0, 1e4, 0.0, flag)
        p = backend.thomson_viscosity(1.0, 1e4, 0.0, flag, force_python=True)
        assert abs(r["eta"] / p["eta"] - 1.0) < 1e-14
        assert abs(r["eta_times_nesigT_over_rho"] - target) < 1e-12


def test_backend_stiffness_both_paths():
    for rate, dt in ((1.0, 0.01), (1e4, 0.01), (100.0, 0.02)):
        r = backend.thomson_stiffness(rate, dt)
        p = backend.thomson_stiffness(rate, dt, force_python=True)
        assert abs(r[0] - p[0]) < 1e-14 and r[1] == p[1]


@pytest.mark.parametrize("route", ["hierarchy", "quadrature"])
def test_backend_transport_coefficients_both_routes(route):
    """★ 유도값 τ_π=1/(4H), η=ρ/(15H) 가 두 경로 × 두 백엔드에서 재생산."""
    r = backend.transport_coefficients(0.0, route=route)
    p = backend.transport_coefficients(0.0, route=route, force_python=True)
    tol = 1e-9 if route == "hierarchy" else 1e-7    # 경로 A 는 차분 조건수 제한
    assert abs(r["tau_pi"] / p["tau_pi"] - 1.0) < tol
    assert abs(r["tau_pi"] - 0.25) < 1e-6
    assert abs(r["eta_over_rho_H"] - 1.0 / 15.0) < 5e-4


@pytest.mark.parametrize("mass", [0.0, 1.0, 4.0])
def test_backend_viscous_cross_validate_both_paths(mass):
    r = backend.viscous_cross_validate(mass)
    p = backend.viscous_cross_validate(mass, force_python=True)
    assert r["agree"] and p["agree"]
    assert abs(r["damping_rel_diff"] - p["damping_rel_diff"]) < 1e-8


# ─────────────────────────────── tilted 구적 디스패치 (H5-e)
@pytest.mark.parametrize("l", [0, 1, 2, 4, 5])
def test_backend_tilted_moment_both_paths(l):
    a = np.array([1.0, 0.9, 1.2]); v = np.array([0.12, -0.08, 0.15])
    r = backend.j_moment_tilted(a, v, 0.7, l, 0)
    p = backend.j_moment_tilted(a, v, 0.7, l, 0, force_python=True)
    rho = float(backend.j_moment_tilted(a, v, 0.7, 0, 0, force_python=True))
    if l == 0:
        assert abs(r / p - 1.0) < 1e-12
    else:
        assert np.asarray(r).shape == (3,) * l
        assert np.abs(np.asarray(r) - np.asarray(p)).max() / rho < 1e-12


def test_backend_moments_tilted_both_paths():
    a = np.array([1.0, 0.9, 1.2]); v = np.array([0.12, -0.08, 0.15])
    rr, rp, rq, rpi = backend.moments_tilted(a, v, 0.7)
    pr, pp, pq, ppi = backend.moments_tilted(a, v, 0.7, force_python=True)
    assert abs(rr / pr - 1.0) < 1e-12 and abs(rp / pp - 1.0) < 1e-12
    assert np.abs(rq - pq).max() / pr < 1e-12
    assert np.abs(rpi - ppi).max() / pr < 1e-12


def test_backend_boost_shell_both_paths():
    a = np.array([1.0, 0.9, 1.2]); v = np.array([0.15, -0.1, 0.2])
    for mass in (0.0, 0.7):
        assert backend.boost_shell_residual(a, v, mass) < 1e-13
        assert backend.boost_shell_residual(a, v, mass, force_python=True) < 1e-13
