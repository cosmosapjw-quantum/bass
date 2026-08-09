"""
차등 테스트 하네스 — Rust 코어(`bianchi_rustcore`) 대 Python 오라클 비트-근접 대조.

계획 §5 의 핵심 안전망: Rust 커널은 교체 이전에 **동결된 Python 오라클과 성분별
rtol≤1e-10** 일치를 증명해야 한다.  두 층을 검증한다:
  (1) 규약 패리티 — rotation_matrix, tracefree_from_5, P_double  (순수 산술, ~1e-13)
  (2) 측지 광선추적 — trace_ray_diag 대 rays.geodesics.trace_ray_diag_bianchi

Rust Euler 산술은 Python 과 연산 순서를 맞췄으나 `H**2`(pow) vs `h*h` 등 미세
차이가 있어 **비트-정확이 아닌 rtol≤1e-10** 를 목표로 한다(안정 구간).
"""
import numpy as np
import pytest

rustcore = pytest.importorskip("bianchi_rustcore")

from bianchi import conventions as conv
from bianchi.rays import frame as rframe
from bianchi.rays import geodesics as geo


# ─────────────────────────────── (1) 규약 패리티
def test_rotation_matrix_parity():
    rng = np.random.default_rng(0)
    for _ in range(50):
        R = rng.normal(size=3)
        got = rustcore.rotation_matrix(R)
        exp = np.asarray(conv.rotation_matrix(R), float)
        np.testing.assert_allclose(got, exp, rtol=1e-13, atol=1e-15)


def test_tracefree_from_5_parity():
    rng = np.random.default_rng(1)
    for _ in range(50):
        s = rng.normal(size=5)
        got = rustcore.tracefree_from_5(*s)
        exp = np.asarray(conv.tracefree_from_5(*s), float)
        np.testing.assert_allclose(got, exp, rtol=1e-13, atol=1e-15)


def test_p_double_parity():
    rng = np.random.default_rng(2)
    for _ in range(50):
        N = rng.normal(size=(3, 3)); A = rng.normal(size=3); x = rng.normal(size=3)
        got = rustcore.p_double(N, A, x)
        exp = np.asarray(rframe.P_double(N, A, x), float)
        np.testing.assert_allclose(got, exp, rtol=1e-12, atol=1e-14)


# ─────────────────────────────── (2) 측지 광선추적 패리티
def _stable_model(rng):
    """안정 역적분(H>0 유지)용 무작위 대각 Bianchi 모형."""
    s = rng.normal(size=3); s -= s.mean(); s *= rng.uniform(0.02, 0.15) / (np.linalg.norm(s) + 1e-12)
    nhat = rng.normal(size=3)
    return dict(H0=1.0, Sigma0=s, Omega0=float(rng.uniform(0.1, 0.6)),
                gamma=float(rng.uniform(1.0, 1.6)), nhat=nhat)


def _py_hist_arrays(hist):
    return (np.array([h["t"] for h in hist]), np.array([h["z"] for h in hist]),
            np.array([h["H"] for h in hist]), np.array([h["nhat"] for h in hist]),
            np.array([h["lna"] for h in hist]))


@pytest.mark.parametrize("seed", range(8))
def test_geodesic_ray_parity(seed):
    rng = np.random.default_rng(100 + seed)
    m = _stable_model(rng)
    t0, t_end, nsteps = 0.0, -0.3, 600
    hist = geo.trace_ray_diag_bianchi(m, t0, t_end, nsteps=nsteps)
    t_py, z_py, H_py, nh_py, lna_py = _py_hist_arrays(hist)

    ts, zs, hs, nhs, lnas = rustcore.trace_ray_diag(
        m["H0"], np.asarray(m["Sigma0"], float), m["Omega0"], m["gamma"],
        np.asarray(m["nhat"], float), t0, t_end, nsteps)

    assert len(zs) == len(z_py), (len(zs), len(z_py))
    np.testing.assert_allclose(ts, t_py, rtol=1e-11, atol=1e-13)
    np.testing.assert_allclose(zs, z_py, rtol=1e-10, atol=1e-12)
    np.testing.assert_allclose(hs, H_py, rtol=1e-10, atol=1e-12)
    np.testing.assert_allclose(nhs, nh_py, rtol=1e-10, atol=1e-12)
    np.testing.assert_allclose(lnas, lna_py, rtol=1e-10, atol=1e-12)


def test_batch_final_z_parity():
    """배치 trace_rays_batch 의 방향별 마지막 z 가 Python 루프와 일치 (CMB z(n̂))."""
    rng = np.random.default_rng(7)
    m = _stable_model(rng)
    t0, t_end, nsteps = 0.0, -0.25, 500
    nhats = rng.normal(size=(64, 3))

    zs_rust = rustcore.trace_rays_batch(
        m["H0"], np.asarray(m["Sigma0"], float), m["Omega0"], m["gamma"],
        nhats, t0, t_end, nsteps)

    zs_py = np.empty(len(nhats))
    for i, nh in enumerate(nhats):
        mm = dict(m); mm["nhat"] = nh
        hist = geo.trace_ray_diag_bianchi(mm, t0, t_end, nsteps=nsteps)
        zs_py[i] = hist[-1]["z"]

    np.testing.assert_allclose(zs_rust, zs_py, rtol=1e-10, atol=1e-12)


# ─────────────────────────────── (3) Sachs 광학 d_A 패리티 (R1 완결 + R4)
@pytest.mark.parametrize("seed", range(6))
def test_optical_dA_parity(seed):
    """조석행렬 닫힌형(R4) + Jacobi 적분이 Python(sympy/JAX) 오라클과 일치."""
    from bianchi.rays import optical as opt
    rng = np.random.default_rng(200 + seed)
    m = _stable_model(rng)
    t0, t_end, nsteps = 0.0, -0.3, 500

    py = opt.trace_optical_diag_bianchi(m, t0, t_end, nsteps=nsteps)
    zs, das, lnas, zf, daf, ortho = rustcore.trace_optical_diag(
        m["H0"], np.asarray(m["Sigma0"], float), m["Omega0"], m["gamma"],
        np.asarray(m["nhat"], float), t0, t_end, nsteps)

    assert abs(zf - py["z_final"]) <= 1e-10 * abs(py["z_final"]) + 1e-12
    assert abs(daf - py["dA_final"]) <= 1e-10 * abs(py["dA_final"]) + 1e-12
    # 스크린 직교성: 4-벡터 평행이동이 유지되어야 (v1.4 부채; 공간성분만 옮기면 깨짐)
    assert ortho < 1e-12
    # 히스토리 배열 대조
    z_py = np.array([h["z"] for h in py["hist"]])
    dA_py = np.array([h["dA"] for h in py["hist"]])
    assert len(zs) == len(z_py)
    np.testing.assert_allclose(zs, z_py, rtol=1e-10, atol=1e-12)
    np.testing.assert_allclose(das, dA_py, rtol=1e-10, atol=1e-12)


def test_optical_batch_parity():
    """배치 광학(Rayon)이 방향별 단일 호출과 일치."""
    rng = np.random.default_rng(11)
    m = _stable_model(rng)
    t0, t_end, nsteps = 0.0, -0.25, 400
    nhats = rng.normal(size=(24, 3))

    zs_b, das_b = rustcore.trace_optical_batch(
        m["H0"], np.asarray(m["Sigma0"], float), m["Omega0"], m["gamma"],
        nhats, t0, t_end, nsteps)
    for i, nh in enumerate(nhats):
        _, _, _, zf, daf, _ = rustcore.trace_optical_diag(
            m["H0"], np.asarray(m["Sigma0"], float), m["Omega0"], m["gamma"],
            nh, t0, t_end, nsteps)
        assert abs(zs_b[i] - zf) < 1e-14
        assert abs(das_b[i] - daf) < 1e-14


def test_optical_eds_reference():
    """물리 오라클: EdS(Σ=0, Ω=1, γ=1) 에서 d_A = (2/H0)(1-(1+z)^{-1/2})/(1+z)."""
    m = dict(H0=1.0, Sigma0=np.zeros(3), Omega0=1.0, gamma=1.0, nhat=np.array([1.0, 0, 0]))
    _, _, _, zf, daf, _ = rustcore.trace_optical_diag(
        m["H0"], m["Sigma0"], m["Omega0"], m["gamma"], m["nhat"], 0.0, -0.35, 4000)
    exact = (2.0 / m["H0"]) * (1 - (1 + zf) ** -0.5) / (1 + zf)
    assert abs(daf - exact) / exact < 1e-6, (daf, exact, zf)


# ─────────────────────────────── (4) 배경 ODE (R2/R3)
def _py_rhs_a(v, gamma):
    import jax.numpy as jnp
    from bianchi.charts import class_a as ca
    return np.asarray(
        ca.rhs(0.0, ca.StateA.from_array(jnp.asarray(v)), {"gamma": gamma}).as_array())


def _py_rhs_b(v, gamma, kappa):
    import jax.numpy as jnp
    from bianchi.charts import class_b as cb
    return np.asarray(
        cb.rhs(0.0, cb.StateB.from_array(jnp.asarray(v)), {"gamma": gamma, "kappa": kappa}).as_array())


def test_chart_rhs_parity_class_a():
    """Class A RHS 가 Python 오라클과 비트-정확."""
    rng = np.random.default_rng(20)
    for _ in range(100):
        v = rng.normal(size=5) * 0.5
        g = float(rng.uniform(1.0, 1.9))
        np.testing.assert_allclose(rustcore.chart_rhs("class_a", v, g),
                                   _py_rhs_a(v, g), rtol=1e-13, atol=1e-15)


def test_chart_rhs_parity_class_b():
    """Class B RHS (κ 파라미터화) 가 Python 오라클과 비트-정확."""
    rng = np.random.default_rng(21)
    for _ in range(100):
        v = rng.normal(size=5) * 0.5
        g = float(rng.uniform(1.0, 1.9)); k = float(rng.uniform(-3, 3))
        np.testing.assert_allclose(rustcore.chart_rhs("class_b", v, g, k),
                                   _py_rhs_b(v, g, k), rtol=1e-13, atol=1e-15)


def test_chart_unknown_name_raises():
    with pytest.raises(ValueError):
        rustcore.chart_rhs("class_z", np.zeros(5), 1.0)


def test_multiplicative_structure_preserves_type():
    """N_i = 0 이 **정확히** 보존 (곱셈 구조) — 유형 안전성의 구조적 보장."""
    ts = np.linspace(0.0, 4.0, 21)
    ys, ok = rustcore.integrate_background("class_a", np.array([0.4, -0.2, 0.0, 0.0, 0.0]),
                                           ts, 4 / 3)
    assert ok
    assert np.all(ys[:, 2:] == 0.0)


def test_integrate_matches_diffrax():
    """diffsol BDF 궤적이 Python diffrax Kvaerno5 와 일치 (적분기 이산화 수준)."""
    import jax
    jax.config.update("jax_enable_x64", True)
    import jax.numpy as jnp
    from bianchi.charts import class_a as ca
    from bianchi import integrate as itg

    cfg = itg.SolverConfig(rtol=1e-12, atol=1e-14, max_steps=100000)
    rng = np.random.default_rng(22)
    for _ in range(4):
        v = np.array([rng.uniform(-.5, .5), rng.uniform(-.5, .5),
                      abs(rng.normal()) * .5, abs(rng.normal()) * .5, 0.0])
        g = float(rng.uniform(1.0, 1.7))
        ts = np.linspace(0.0, 3.0, 31)
        sol = itg.solve(lambda t, y, a: ca.rhs(t, y, a),
                        ca.StateA.from_array(jnp.asarray(v)),
                        0.0, 3.0, {"gamma": g}, ts=jnp.asarray(ts), cfg=cfg)
        py = np.asarray(jnp.stack([sol.ys.Sigma_p, sol.ys.Sigma_m,
                                   sol.ys.N1, sol.ys.N2, sol.ys.N3], axis=-1))
        ys, ok = rustcore.integrate_background("class_a", v, ts, g, 0.0, 1e-12, 1e-14)
        assert ok
        scale = max(1e-30, np.max(np.abs(py)))
        assert np.max(np.abs(ys - py)) / scale < 1e-8


def test_batch_matches_single():
    """배치(Rayon)가 단일 적분과 동일 — 낙오자 격리 확인."""
    rng = np.random.default_rng(23)
    y0s = np.column_stack([rng.uniform(-.4, .4, 16), rng.uniform(-.4, .4, 16),
                           abs(rng.normal(size=16)) * .3, abs(rng.normal(size=16)) * .3,
                           np.zeros(16)])
    ts = np.linspace(0.0, 2.0, 11)
    ys_b, ok = rustcore.integrate_batch("class_a", y0s, ts, 4 / 3)
    assert np.all(ok == 1.0)
    for i in range(len(y0s)):
        ys_s, ok_s = rustcore.integrate_background("class_a", y0s[i], ts, 4 / 3)
        assert ok_s
        np.testing.assert_allclose(ys_b[i], ys_s[-1], rtol=1e-12, atol=1e-14)


def test_omega_identity_along_trajectory():
    """물리 오라클: Ω = 1 - Σ² - K 가 궤적 위에서 유지 (Gauss 구속)."""
    ts = np.linspace(0.0, 3.0, 31)
    y0 = np.array([0.3, -0.2, 0.4, 0.2, 0.0])
    ys, ok = rustcore.integrate_background("class_a", y0, ts, 4 / 3)
    assert ok
    for row in ys:
        om, _ = rustcore.chart_aux("class_a", row, 4 / 3)
        s2 = row[0] ** 2 + row[1] ** 2
        K = (row[2] ** 2 + row[3] ** 2 + row[4] ** 2
             - 2 * (row[2] * row[3] + row[3] * row[4] + row[4] * row[2])) / 12.0
        assert abs(om - (1 - s2 - K)) < 1e-13


def test_codazzi_constraint_preserved_class_b():
    """Class B Codazzi C = Σ̃Ñ - Δ² - Σ₊²Ã 가 궤적 위에서 보존 (C'=4(q+Σ₊-1)C)."""
    ts = np.linspace(0.0, 1.5, 16)
    # C=0 인 초기조건 구성: Δ=0, Σ₊=0 → C = Σ̃Ñ,  Σ̃=0 이면 C=0
    y0 = np.array([0.0, 0.0, 0.0, 0.3, 0.4])
    g, k = 4 / 3, -1.0
    _, c0 = rustcore.chart_aux("class_b", y0, g, k)
    assert abs(c0) < 1e-14
    ys, ok = rustcore.integrate_background("class_b", y0, ts, g, k)
    assert ok
    for row in ys:
        _, c = rustcore.chart_aux("class_b", row, g, k)
        assert abs(c) < 1e-8, c


def test_report_max_error(capsys):
    """참고용: 실제 최대 상대오차를 출력 (rtol 여유 확인)."""
    rng = np.random.default_rng(999)
    worst = 0.0
    for _ in range(20):
        m = _stable_model(rng)
        hist = geo.trace_ray_diag_bianchi(m, 0.0, -0.3, nsteps=800)
        _, z_py, H_py, _, _ = _py_hist_arrays(hist)
        _, zs, hs, _, _ = rustcore.trace_ray_diag(
            m["H0"], np.asarray(m["Sigma0"], float), m["Omega0"], m["gamma"],
            np.asarray(m["nhat"], float), 0.0, -0.3, 800)
        worst = max(worst, float(np.max(np.abs(zs - z_py) / (np.abs(z_py) + 1e-30))))
    with capsys.disabled():
        print(f"\n[differential] 측지 z 최대 상대오차 = {worst:.2e}")
    assert worst < 1e-9
