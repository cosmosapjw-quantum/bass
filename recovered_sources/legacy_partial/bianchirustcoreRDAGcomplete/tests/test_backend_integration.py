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
