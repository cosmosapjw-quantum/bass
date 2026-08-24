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


# ─────────────────────────────── (5) C1 · 일반유형 조석 (codegen Riemann)
def _stf(M):
    S = 0.5 * (M + M.T)
    return S - np.trace(S) * np.eye(3) / 3


def _sym(M):
    return 0.5 * (M + M.T)


def _general_state(rng):
    """N, A, R 이 모두 0 이 아닌 일반유형 상태 (VII_h 등이 사는 영역)."""
    return dict(H=float(rng.uniform(0.5, 1.5)),
                N=_sym(rng.normal(size=(3, 3))),
                A=rng.normal(size=3),
                sigma=_stf(rng.normal(size=(3, 3))),
                R=rng.normal(size=3),
                Hd=float(rng.normal()),
                sigmad=_stf(rng.normal(size=(3, 3))))


def test_riemann_general_parity():
    """자동생성 Riemann 이 sympy 오라클과 일치 (일반유형 N,A,R≠0)."""
    from bianchi.rays.weyl import riemann_up, pack_state
    rng = np.random.default_rng(30)
    for _ in range(30):
        st = _general_state(rng)
        got = np.asarray(rustcore.riemann_up_general(pack_state(st))).reshape(4, 4, 4, 4)
        np.testing.assert_allclose(got, riemann_up(st), rtol=1e-11, atol=1e-13)


def test_tidal_general_parity():
    """일반유형 조석행렬 T_AB 가 `weyl.tidal_matrix` 와 일치."""
    from bianchi.rays.weyl import tidal_matrix, pack_state
    rng = np.random.default_rng(31)
    for _ in range(30):
        st = _general_state(rng)
        args = pack_state(st)
        nh = rng.normal(size=3); nh /= np.linalg.norm(nh)
        E = float(rng.uniform(0.5, 3.0))
        k = np.concatenate([[E], E * nh])
        sc = rng.normal(size=(2, 4))              # 임의 스크린 (E_A^0 ≠ 0 포함)
        np.testing.assert_allclose(rustcore.tidal_general(args, k, sc),
                                   tidal_matrix(k, sc, st), rtol=1e-10, atol=1e-12)


def test_tidal_general_ricci_focusing():
    """물리 오라클 D16: tr T = -R_mn k^m k^n (Ricci 집속)."""
    from bianchi.rays.weyl import pack_state
    rng = np.random.default_rng(32)
    worst = 0.0
    for _ in range(20):
        st = _general_state(rng)
        args = pack_state(st)
        nh = rng.normal(size=3); nh /= np.linalg.norm(nh)
        E = float(rng.uniform(0.5, 2.0))
        k = np.concatenate([[E], E * nh])
        tmp = np.array([1.0, 0, 0])
        if abs(nh @ tmp) > 0.9:
            tmp = np.array([0, 1.0, 0])
        e1 = np.cross(nh, tmp); e1 /= np.linalg.norm(e1); e2 = np.cross(nh, e1)
        sc = np.array([[0, *e1], [0, *e2]])
        T = rustcore.tidal_general(args, k, sc)
        worst = max(worst, abs(np.trace(T) + rustcore.ricci_kk(args, k)))
    assert worst < 1e-11, worst


def test_tidal_general_reduces_to_diagonal_closed_form():
    """대각 극한(N=A=R=0)에서 codegen 경로가 R4 손유도 닫힌형(=Python)과 일치."""
    from bianchi.rays.weyl import tidal_matrix, pack_state
    H = 1.0
    sig = np.array([0.1, -0.05, -0.05])
    st = dict(H=H, N=np.zeros((3, 3)), A=np.zeros(3), sigma=np.diag(sig),
              R=np.zeros(3), Hd=-1.2, sigmad=np.diag(-3 * H * sig))
    args = pack_state(st)
    k = np.array([1.0, 0.6, 0.8, 0.0]); k[1:] /= np.linalg.norm(k[1:])
    sc = np.array([[0, 0, 0, 1.0], [0, -0.8, 0.6, 0]])
    np.testing.assert_allclose(rustcore.tidal_general(args, k, sc),
                               tidal_matrix(k, sc, st), rtol=1e-12, atol=1e-14)


def test_tidal_general_rejects_bad_shapes():
    args = np.zeros(24)
    with pytest.raises(ValueError):
        rustcore.tidal_general(np.zeros(23), np.zeros(4), np.zeros((2, 4)))
    with pytest.raises(ValueError):
        rustcore.tidal_general(args, np.zeros(3), np.zeros((2, 4)))
    with pytest.raises(ValueError):
        rustcore.tidal_general(args, np.zeros(4), np.zeros((3, 4)))


# ─────────────────────────────── (6) B1 · 열역학 커널
def test_fd_rho_p_parity():
    """중성미자 FD (ρ,p,w) 가 scipy.quad 오라클과 일치 (GL 적분)."""
    from bianchi.matter import neutrino as nu
    from bianchi.physical import units as U
    T_nu0 = U.T_NU_OVER_T_GAMMA * U.T_CMB_K
    for m_eV in (0.02, 0.06, 0.2):
        y0 = m_eV / (U.KB_EV_K * T_nu0)
        for a in (1e-3, 1e-2, 0.1, 0.5, 1.0):
            py = nu.neutrino_rho_p(a, m_eV)
            ru = rustcore.fd_rho_p(a, y0, 1.0)
            for p, r in zip(py, ru):
                assert abs(p - r) <= 1e-10 * abs(p) + 1e-14, (m_eV, a, p, r)


def test_fd_batch_matches_single():
    a = np.linspace(1e-3, 1.0, 32)
    rho, p, w = rustcore.fd_rho_p_batch(a, 1.5, 1.0)
    for i, ai in enumerate(a):
        r1, p1, w1 = rustcore.fd_rho_p(ai, 1.5, 1.0)
        assert abs(rho[i] - r1) < 1e-15 and abs(p[i] - p1) < 1e-15 and abs(w[i] - w1) < 1e-15


def test_fd_physical_limits():
    """m→0: w=1/3;  m≫T: w→0."""
    assert abs(rustcore.fd_rho_p(1.0, 0.0, 1.0)[2] - 1 / 3) < 1e-10
    assert rustcore.fd_rho_p(1.0, 50.0, 1.0)[2] < 0.02


def test_gstar_table_shared_exactly():
    """g_*, g_*s 표가 Python 과 **비트-정확** (codegen 공유 → 표류 불가)."""
    from bianchi.thermo import dof
    for T in (1e4, 1e3, 1e2, 10.0, 1.0, 0.3, 0.214, 0.2, 0.15, 0.1, 1e-3, 1e-5, 1e-7):
        assert rustcore.g_star(T) == dof.g_star(T), T
        assert rustcore.g_star_s(T) == dof.g_star_s(T), T


# ─────────────────────────────── (7) H2 · 운동론 (구적 + 다극 계층)
def _kin_pyref(l, i, mass, a, eps):
    from bianchi.matter import hierarchy as HH
    from bianchi.matter import freestream as ffs
    f0 = ffs.f_fermi_dirac if eps == 0.0 else HH.f_dipole(eps, 2)
    # ★ R5c: J_moment 가 기본으로 Rust 를 타므로, 차등테스트의 참조는 **명시적으로**
    #   numpy 오라클에 못박는다 — 안 그러면 Rust 대 Rust 의 공허한 비교가 된다.
    return np.atleast_1d(np.asarray(HH.J_moment(a, mass, l, i, f0,
                                                backend="python"), float)).ravel()


@pytest.mark.parametrize("l", [0, 1, 2, 3, 4])
@pytest.mark.parametrize("eps", [0.0, 0.4])
def test_kin_j_moment_parity(l, eps):
    """구적 모멘트 J^(i)_{A_l} 가 Python 오라클과 일치 (l=0..4, 등방/쌍극).

    ★ 스케일 하한: 등방 홀수 l 은 항등적으로 0 (|J|~3e−15) 이므로 상대오차가
      무의미해진다 → **ρ 로 정규화**한다 (물리적 지표).
    """
    a = np.array([1.0, 0.9, 1.15])
    mass = 0.8
    rho = _kin_pyref(0, 0, mass, a, eps)[0]
    for i in (0, 1, 2):
        py = _kin_pyref(l, i, mass, a, eps)
        ru = np.asarray(rustcore.kin_j_moment(a, mass, l, i, eps, 2))
        assert ru.shape == py.shape
        assert np.abs(py - ru).max() / rho < 1e-12, (l, i, eps)


def test_kin_moments_matches_freestream():
    """Rust `kin_moments` 가 Python `freestream.moments` 와 일치 (ρ, p, π_ab)."""
    from bianchi.matter import freestream as ffs
    for a in (np.array([1.0, 1.0, 1.0]), np.array([1.0, 0.85, 1.2])):
        for mass in (0.0, 0.8, 3.0):
            rho, p, pi = ffs.moments(a, mass)
            r_rho, r_p, r_pi = rustcore.kin_moments(a, mass)
            assert abs(r_rho / rho - 1.0) < 1e-12
            assert abs(r_p / p - 1.0) < 1e-12
            assert np.abs(r_pi - pi).max() / rho < 1e-12


@pytest.mark.parametrize("l", [2, 3, 4])
def test_kin_pstf_parity(l):
    """Rust PSTF 사영이 Python 직교사영과 일치 + 대각합 제거."""
    from bianchi.matter import hierarchy as HH
    rng = np.random.default_rng(200 + l)
    T = rng.normal(size=(3,) * l)
    py = np.asarray(HH.pstf(T), float).ravel()
    ru = np.asarray(rustcore.kin_pstf(T.ravel(), l))
    scale = max(np.abs(py).max(), 1e-30)
    np.testing.assert_allclose(ru, py, rtol=1e-10, atol=1e-12 * scale)
    tr = np.abs(np.trace(ru.reshape((3,) * l), axis1=-2, axis2=-1)).max()
    assert tr < 1e-10 * scale


def test_kin_pstf_rejects_bad_length():
    with pytest.raises(ValueError):
        rustcore.kin_pstf(np.zeros(8), 2)          # 3^2 = 9 여야


def test_kin_integrate_trajectory_parity():
    """★ 계층 RK4 궤적이 Python 구현과 일치 (ρ(t), π_ab(t))."""
    from bianchi.matter import hierarchy as HH
    a0 = np.array([1.0, 1.0, 1.0])
    sig = np.array([0.06, -0.02, -0.04])
    t, rho_r, p_r, pi_r = rustcore.kin_integrate(a0, 0.0, 1.0, sig, 0.3, 40, 4, 2, 0.0)
    res = HH.integrate_hierarchy(a0, 0.0, 1.0, sig, 0.3, nsteps=40, l_max=4, i_max=2)
    py_rho = np.array([float(J[(0, 0)]) for J in res["J"]])
    py_pi = np.array([np.asarray(J[(2, 0)]).ravel() for J in res["J"]])
    assert np.abs(rho_r - py_rho).max() / np.abs(py_rho).max() < 1e-11
    assert np.abs(pi_r - py_pi).max() / np.abs(py_pi).max() < 1e-9


def test_kin_integrate_matches_exact_quadrature():
    """물리 게이트: Rust 계층 궤적이 **정확 구적**과 일치 (Python 경유 없이)."""
    a0 = np.array([1.0, 1.0, 1.0])
    sig = np.array([0.06, -0.02, -0.04])
    H_ = 1.0
    t, rho_r, p_r, pi_r = rustcore.kin_integrate(a0, 0.0, H_, sig, 0.3, 40, 4, 2, 0.0)
    a_end = a0 * np.exp((H_ + sig) * t[-1])
    rho_e, p_e, pi_e = rustcore.kin_moments(a_end, 0.0)
    assert abs(rho_r[-1] / rho_e - 1.0) < 1e-6
    assert np.abs(pi_r[-1].reshape(3, 3) - pi_e).max() / rho_e < 1e-6


# ─────────────────────────────── (8) H3 · Thomson 충돌 (두 경로를 각각 대조)
def test_kin_thomson_route_a_parity():
    """★ 경로 A (수치 위상함수) 가 Python 과 일치 — 두 언어의 GL 격자·Legendre 점화 대조.

    Rust 는 3항 점화, Python 은 `numpy.polynomial.legendre.legval` — **다른 구현**이므로
    이 대조는 단순 포팅 확인이 아니라 독립 검산이다.
    """
    from bianchi.matter import collision as CC
    for l in range(8):
        py = CC.thomson_eigenvalue_numeric(l)
        ru = rustcore.kin_thomson_eigenvalue_numeric(l)
        assert abs(py - ru) < 1e-13, (l, py, ru)


def test_kin_thomson_route_b_parity():
    """경로 B (해석 다극) 는 유리수라 **비트-정확** 이어야 한다."""
    from bianchi.matter import collision as CC
    for l in range(8):
        assert rustcore.kin_thomson_eigenvalue(l) == CC.thomson_eigenvalue(l), l


def test_kin_legendre_matches_numpy():
    """Rust 3항 점화 P_l(x) 대 numpy legval — 경로 A 의 내부 부품 검증."""
    from numpy.polynomial.legendre import legval
    rng = np.random.default_rng(303)
    for l in range(9):
        c = np.zeros(l + 1)
        c[l] = 1.0
        for x in np.concatenate([rng.uniform(-1, 1, 12), [-1.0, 0.0, 1.0]]):
            assert abs(rustcore.kin_legendre(l, x) - legval(x, c)) < 1e-13, (l, x)


def test_kin_two_routes_agree_in_rust():
    """★ Rust 내부에서도 두 경로가 λ₂ = 1/10 (감쇠 9/10) 을 독립 재생산."""
    worst = max(abs(rustcore.kin_thomson_eigenvalue_numeric(l)
                    - rustcore.kin_thomson_eigenvalue(l)) for l in range(7))
    assert worst < 1e-12, worst
    assert abs(rustcore.kin_thomson_eigenvalue_numeric(2) - 0.1) < 1e-12


@pytest.mark.parametrize("l,i", [(0, 0), (2, 0), (2, 1), (4, 0)])
@pytest.mark.parametrize("route", ["analytic", "numeric"])
def test_kin_collision_term_parity(l, i, route):
    """충돌항 C[J^(i)_{A_l}] 가 Python 과 일치 (두 route 옵션 각각)."""
    from bianchi.matter import collision as CC
    from bianchi.matter import hierarchy as HH
    a = np.array([1.0, 0.85, 1.18])
    mass, rate = 0.0, 2.5
    J = {(ll, ii): HH.J_moment(a, mass, ll, ii)
         for ll in range(5) for ii in range(5)}
    py = np.atleast_1d(np.asarray(CC.collision_term(J, l, i, rate, route), float)).ravel()
    ru = np.asarray(rustcore.kin_collision_term(a, mass, l, i, rate, route, 4, 2, 0.0))
    rho = float(J[(0, 0)])
    assert np.abs(py - ru).max() / rho < 1e-12, (l, i, route)


def test_kin_collision_term_rejects_bad_route():
    with pytest.raises(ValueError):
        rustcore.kin_collision_term(np.array([1.0, 0.9, 1.1]), 0.0, 2, 0, 1.0, "nope")


@pytest.mark.parametrize("rate", [0.0, 3.0, 50.0])
def test_kin_rhs_collisional_parity(rate):
    """충돌 RHS 가 Python 과 일치.  rate=0 은 무충돌 RHS 와 정확히 같아야 한다."""
    from bianchi.matter import collision as CC
    from bianchi.matter import hierarchy as HH
    a = np.array([1.0, 0.85, 1.18])
    sig = np.diag([0.05, -0.02, -0.03])
    mass = 0.0
    J = {(ll, ii): HH.J_moment(a, mass, ll, ii) for ll in range(5) for ii in range(5)}
    J = HH.close_i(J, 4, 2)
    rho = float(J[(0, 0)])
    for l in (0, 2):
        py = np.atleast_1d(np.asarray(
            CC.hierarchy_rhs_collisional(J, 1.0, sig, l, 0, rate), float)).ravel()
        ru = np.asarray(rustcore.kin_rhs_collisional(
            a, mass, 1.0, np.diag(sig).copy(), l, 0, rate, "analytic", 4, 2, 0.0))
        assert np.abs(py - ru).max() / rho < 1e-10, (l, rate)


def test_kin_free_streaming_residual_is_exactly_zero():
    """★ Rust 쪽에서도 n_eσ_T=0 잔차가 **정확히 0** (H1/H2 회귀 보호)."""
    r = rustcore.kin_free_streaming_residual(
        0.0, np.array([1.0, 0.85, 1.18]), 1.0, np.array([0.05, -0.02, -0.03]))
    assert r == 0.0, r


def test_kin_thomson_viscosity_parity():
    """유도 Thomson 점성이 Python 과 일치: 8/27 (9/10 포함) vs 4/15 (미포함)."""
    from bianchi.matter import collision as CC
    for flag, target in ((True, 8.0 / 27.0), (False, 4.0 / 15.0)):
        py = CC.thomson_viscosity(1.0, 1e4, 0.0, flag)
        eta, tau, damp, ratio = rustcore.kin_thomson_viscosity(1.0, 1e4, 0.0, flag)
        assert abs(eta - py["eta"]) < 1e-15
        assert abs(tau - py["tau_pi"]) < 1e-18
        assert abs(ratio - target) < 1e-12
    a, b = (rustcore.kin_thomson_viscosity(1.0, 1e4, 0.0, f)[3] for f in (True, False))
    assert abs(a / b - 10.0 / 9.0) < 1e-12          # 차이의 전부가 9/10 인자


@pytest.mark.parametrize("rate", [1e2, 1e3, 1e4])
def test_kin_tight_coupling_parity(rate):
    """긴밀결합 게이트가 Python 과 일치 + 1/rate 스케일링."""
    from bianchi.matter import collision as CC
    a = np.array([1.0, 0.85, 1.18])
    sg = np.array([0.05, -0.02, -0.03])
    py = CC.tight_coupling_residual(0.0, tuple(a), 1.0, tuple(sg), rate)
    pi_qs, damp, src = rustcore.kin_tight_coupling(0.0, a, 1.0, sg, rate, 4, 2)
    assert abs(pi_qs / py["pi_quasi_static_over_rho"] - 1.0) < 1e-10
    assert pi_qs * rate < 1.0


def test_kin_stiffness_flag():
    """RK4 강성 진단: n_eσ_T·dt·(1−λ₂) < 2.785 여야 안정."""
    assert rustcore.kin_stiffness_ratio(1.0, 0.01)[1]
    assert not rustcore.kin_stiffness_ratio(1e4, 0.01)[1]


def test_kin_integrate_collisional_reduces_to_free_at_zero_rate():
    """★ rate=0 충돌 적분이 무충돌 `kin_integrate` 와 **비트-정확** 일치."""
    a0 = np.array([1.0, 1.0, 1.0])
    sig = np.array([0.06, -0.02, -0.04])
    t0, r0, p0, pi0 = rustcore.kin_integrate(a0, 0.0, 1.0, sig, 0.3, 40, 4, 2, 0.0)
    t1, r1, p1, pi1 = rustcore.kin_integrate_collisional(
        a0, 0.0, 1.0, sig, 0.0, 0.3, 40, 4, 2, 0.0, "analytic")
    np.testing.assert_array_equal(r0, r1)
    np.testing.assert_array_equal(pi0, pi1)


def test_kin_integrate_collisional_damps_pi():
    """충돌을 켜면 π 가 무충돌보다 작아진다 (부호·크기 감각)."""
    a0 = np.array([1.0, 0.85, 1.18])
    sig = np.array([0.05, -0.02, -0.03])
    _, _, _, pi_f = rustcore.kin_integrate_collisional(
        a0, 0.0, 1.0, sig, 0.0, 0.2, 200, 4, 2, 0.0, "analytic")
    _, _, _, pi_c = rustcore.kin_integrate_collisional(
        a0, 0.0, 1.0, sig, 5.0, 0.2, 200, 4, 2, 0.0, "analytic")
    assert np.abs(pi_c[-1]).max() < np.abs(pi_f[-1]).max()


# ─────────────────────────────── (9) H4 · imperfect fluid 유도 (두 경로를 각각 대조)
@pytest.mark.parametrize("mass", [0.0, 0.5, 1.0, 4.0])
def test_kin_route_a_damping_parity(mass):
    """★ 경로 A (구적 유한차분) 감쇠율이 Python 과 일치 — 계층 수식 미사용 경로.

    ★ **허용오차가 왜 1e−7 인가 (정직하게)**: 구적 자체의 Rust↔Python 일치는
      |Δπ|/ρ ≈ 1.5e−14 다 (`test_kin_moments_matches_freestream` 가 1e−12 로 못박음).
      그런데 이 경로는 그 π 를 2·dt = 2e−5 로 나누고 다시 |π|/ρ ≈ 6.2e−3 으로 나눈다
      ⇒ 증폭계수 ≈ 1/(2·dt·|π|/ρ) ≈ 8e7.  즉 **1e−14 의 반올림이 8e−7 로 확대**된다.
      측정 7.7e−9 은 이 예측 범위 안이다.  이는 계수 오류가 아니라 **차분 조건수**이며,
      `test_kin_route_a_damping_is_roundoff_limited` 가 그 기제(1/dt 증가)를 못 박는다.
      진짜 정밀 대조는 구적 층에서 이미 1e−12 로 이뤄졌다.
    """
    from bianchi.matter import viscous_derived as vd
    a = np.array([1.0, 0.85, 1.18])
    py = vd.route_a_damping(mass, tuple(a), H_hubble=1.0)
    comp, mean, aniso = rustcore.kin_route_a_damping(mass, a, 1.0, 1e-5)
    np.testing.assert_allclose(comp, py["rate_per_component"], rtol=1e-7, atol=1e-9)
    assert abs(mean - py["rate_mean"]) < 1e-7
    assert abs(aniso - py["anisotropy"]) < 1e-7


def test_kin_route_a_damping_is_roundoff_limited():
    """★ 위 허용오차의 **근거를 시험으로 못 박는다**: 불일치가 1/dt 로 커진다.

    차분 조건수라면 dt↓ ⇒ 불일치↑ (반올림/dt).  계수 오류라면 dt 무관한 하한이 남는다.
    측정: dt=1e−3 → 1.1e−10,  1e−5 → 3.1e−8,  1e−7 → 2.7e−6  (약 1/dt).
    """
    from bianchi.matter import viscous_derived as vd
    a = np.array([1.0, 0.85, 1.18])
    errs = {}
    for dt in (1e-3, 1e-5, 1e-7):
        py = vd.route_a_damping(0.0, tuple(a), H_hubble=1.0, dt=dt)["rate_per_component"]
        ru = np.asarray(rustcore.kin_route_a_damping(0.0, a, 1.0, dt)[0])
        errs[dt] = float(np.abs(py - ru).max())
    assert errs[1e-3] < errs[1e-5] < errs[1e-7], errs      # 단조 증가 = 반올림 지배
    assert errs[1e-3] < 1e-8                                # 큰 dt 에서는 잔차 소멸
    # 계수 오류라면 dt 를 키워도 남을 텐데, 100배 키우면 100배 이상 줄어든다
    assert errs[1e-5] / errs[1e-3] > 30.0, errs


@pytest.mark.parametrize("mass", [0.0, 1.0, 4.0])
def test_kin_route_a_source_parity(mass):
    """경로 A 급작응답 소스 계수가 Python `freestream` 과 일치."""
    from bianchi.matter import viscous_derived as vd
    py = vd.route_a_source(mass)
    ru = rustcore.kin_route_a_source(mass, 0.002)
    assert abs(py - ru) < 1e-10, (mass, py, ru)


@pytest.mark.parametrize("mass", [0.0, 0.5, 1.0, 4.0])
def test_kin_route_b_damping_parity(mass):
    """★ 경로 B (PSTF 계층) 감쇠율이 Python 과 일치 — 구적 미분 미사용 경로."""
    from bianchi.matter import viscous_derived as vd
    a = np.array([1.0, 0.85, 1.18])
    py = vd.route_b_damping(mass, tuple(a), H_hubble=1.0)
    comp, mean, aniso = rustcore.kin_route_b_damping(mass, a, 1.0)
    np.testing.assert_allclose(comp, py["rate_per_component"], rtol=1e-10, atol=1e-12)
    assert abs(mean - py["rate_mean"]) < 1e-10


def test_kin_route_b_handset_is_exactly_minus_four():
    """★ 구적을 전혀 쓰지 않는 가장 순수한 경로 B — Rust 에서도 정확히 −4H."""
    comp, mean = rustcore.kin_route_b_damping_handset(1.0, np.array([0.1, -0.04, -0.06]))
    assert abs(mean + 4.0) < 1e-12, mean
    from bianchi.matter import viscous_derived as vd
    py = vd.route_b_damping_handset(1.0)
    np.testing.assert_allclose(comp, py["rate_per_component"], rtol=1e-12, atol=1e-14)


def test_kin_route_b_source_is_exactly_minus_8_over_15():
    """경로 B 소스 계수가 정확히 −8/15 (계수 유리수라 오차 없음) + Python 일치."""
    from bianchi.matter import viscous_derived as vd
    ru = rustcore.kin_route_b_source(0.0, None, 1.0, None)
    assert abs(ru + 8.0 / 15.0) < 1e-12, ru
    assert abs(ru - vd.route_b_source(0.0)) < 1e-12


def test_kin_route_b_rejects_isotropic_a_vec():
    """등방 a_vec 은 π_ab ≡ 0 → 조용히 넘기지 않고 예외 (Python 과 같은 계약).

    ★ 이 계약은 H4 에서 실제 버그를 잡았다: 기본 (1,1,1) 로 rescale 하면 m=1 에서
      23% 불일치가 났다.  Rust 포트도 같은 방어를 갖도록 못 박는다.
    """
    with pytest.raises(ValueError):
        rustcore.kin_route_b_damping(0.0, np.array([1.0, 1.0, 1.0]), 1.0)


@pytest.mark.parametrize("route", ["hierarchy", "quadrature"])
def test_kin_transport_coefficients_parity(route):
    """★ 유도값 τ_π = 1/(4H), η = ρ/(15H) 가 Rust·Python 양쪽에서 재생산."""
    from bianchi.matter import viscous_derived as vd
    a = np.array([1.0, 0.85, 1.18])
    py = vd.transport_coefficients(0.0, tuple(a), H_hubble=1.0, route=route)
    eta, tau, rho, damp, src, eta_rh = rustcore.kin_transport_coefficients(
        0.0, a, 1.0, route)
    assert abs(tau - 0.25) < 1e-6, tau
    assert abs(eta_rh - 1.0 / 15.0) < 5e-4, eta_rh
    # 계층 경로는 방정식 평가라 1e−9, 구적 경로는 차분 조건수 때문에 1e−7
    # (위 test_kin_route_a_damping_is_roundoff_limited 가 그 기제를 증명한다).
    tol = 1e-9 if route == "hierarchy" else 1e-7
    assert abs(tau / py["tau_pi"] - 1.0) < tol, (route, tau, py["tau_pi"])
    assert abs(eta / py["eta"] - 1.0) < tol, (route, eta, py["eta"])
    assert eta > 0                                   # 산일적 (2법칙)


def test_kin_transport_rejects_unknown_route():
    with pytest.raises(ValueError):
        rustcore.kin_transport_coefficients(0.0, np.array([1.0, 0.9, 1.1]), 1.0, "nope")


@pytest.mark.parametrize("mass", [0.0, 0.5, 1.0, 4.0])
def test_kin_cross_validate_parity(mass):
    """★ Rust 내부 두 경로 교차검증이 Python 과 같은 상대차를 준다."""
    from bianchi.matter import viscous_derived as vd
    py = vd.cross_validate(mass)
    d_rel, s_rel, ok = rustcore.kin_cross_validate(mass, None, 1.0, 2e-3, 5e-3)
    assert ok, (mass, d_rel, s_rel)
    assert d_rel < 1e-6, (mass, d_rel)
    assert abs(d_rel - py["damping_rel_diff"]) < 1e-8
    assert abs(s_rel - py["source_rel_diff"]) < 1e-9


def test_kin_eckart_and_relaxation_helpers():
    """유도 헬퍼 비트-정확 대조."""
    from bianchi.matter import viscous_derived as vd
    assert rustcore.kin_eckart_eta(3.0, 1.5) == vd.eckart_eta_from_hierarchy(3.0, 1.5)
    assert rustcore.kin_relaxation_time(2.0) == vd.relaxation_time_massless(2.0)


# ─────────────────────────────── (10) 수치 재현성 (비트 안정성)
def test_quadrature_is_bit_reproducible_under_load():
    """★ 같은 입력 → **같은 비트**.  동시 부하 아래에서도.

    ★ 이 시험이 생긴 이유 (실제 결함):  `quad::j_moment` 초기 판은 Rayon `reduce` 로
      부분합을 합쳤는데, reduce 는 작업훔치기에 따라 **축약 트리 모양이 실행마다
      달라져** 부동소수 합산 순서가 바뀐다.  동시 부하 아래 200회 호출에서 서로 다른
      비트패턴 2개가 관측됐고, 그 결과 "rate=0 이면 무충돌과 비트-정확" 시험이
      **간헐적으로 실패**했다 (전체 스위트에서만 재현 — 단독 실행은 통과).
      부분합을 노드 순서대로 수집한 뒤 순차 합산하도록 고쳤다.
    """
    import threading
    a = np.array([1.0, 0.9, 1.15])
    stop = threading.Event()

    def spin():
        x = np.random.default_rng(0).normal(size=(160, 160))
        while not stop.is_set():
            x @ x

    workers = [threading.Thread(target=spin, daemon=True) for _ in range(4)]
    for w in workers:
        w.start()
    try:
        for l, i, eps in ((2, 0, 0.0), (3, 1, 0.4)):
            pats = {np.asarray(rustcore.kin_j_moment(a, 0.8, l, i, eps, 2)).tobytes()
                    for _ in range(120)}
            assert len(pats) == 1, (l, i, len(pats))
    finally:
        stop.set()
        for w in workers:
            w.join(timeout=2.0)


def test_free_and_zero_rate_collisional_agree_bitwise_repeatedly():
    """★ rate=0 충돌 경로 = 무충돌 경로, **반복해도** 비트-정확.

    단발 비교는 우연히 통과할 수 있다 (위 결함이 정확히 그랬다) → 반복 확인.
    """
    a0 = np.array([1.0, 1.0, 1.0])
    sig = np.array([0.06, -0.02, -0.04])
    for _ in range(8):
        _, r0, _, pi0 = rustcore.kin_integrate(a0, 0.0, 1.0, sig, 0.3, 40, 4, 2, 0.0)
        _, r1, _, pi1 = rustcore.kin_integrate_collisional(
            a0, 0.0, 1.0, sig, 0.0, 0.3, 40, 4, 2, 0.0, "analytic")
        np.testing.assert_array_equal(r0, r1)
        np.testing.assert_array_equal(pi0, pi1)


# ─────────────────────────────── (11) H5-e · tilted (boosted) 구적
@pytest.mark.parametrize("mass", [0.0, 0.7, 3.0])
def test_kin_tilted_moment_parity(mass):
    """★ boosted 구적이 Python 오라클과 일치 (l=0..5, i=−1..2).

    L_MAX 를 5 로 올린 뒤이므로 l=5 까지 대조한다 (H5-d 잔차가 l+2=5 를 요구).
    """
    from bianchi.matter import tilted_moments as TM
    a = np.array([1.0, 0.9, 1.2])
    v = np.array([0.12, -0.08, 0.15])
    rho = TM.J_moment_tilted(a, v, mass, 0, 0, backend="python")
    for l in range(6):
        for i in (-1, 0, 1, 2):
            py = np.atleast_1d(np.asarray(          # ★ R5c: 오라클 명시 (공허 비교 방지)
                TM.J_moment_tilted(a, v, mass, l, i, backend="python"), float)).ravel()
            ru = np.asarray(rustcore.kin_j_moment_tilted(a, v, mass, l, i))
            assert ru.shape == py.shape
            assert np.abs(py - ru).max() / rho < 1e-12, (mass, l, i)


def test_kin_tilted_zero_v_is_bit_exact():
    """★ v=0 이면 `kin_j_moment` 와 **비트-정확** (피적분함수가 문자 그대로 동일)."""
    a = np.array([1.0, 0.9, 1.2])
    z = np.zeros(3)
    for l in range(6):
        for i in (0, 1):
            n = np.asarray(rustcore.kin_j_moment(a, 0.7, l, i, 0.0, 2))
            t = np.asarray(rustcore.kin_j_moment_tilted(a, z, 0.7, l, i))
            np.testing.assert_array_equal(n, t)


def test_kin_boost_shell_residual():
    """λ′² = E′² − m² 격자 전점 (Rust 자체 검증, 측정 1.1e−15)."""
    a = np.array([1.0, 0.9, 1.2])
    v = np.array([0.15, -0.1, 0.2])
    for mass in (0.0, 0.7, 3.0):
        assert rustcore.kin_boost_shell_residual(a, v, mass) < 1e-13


def test_kin_moments_tilted_parity():
    from bianchi.matter import tilted_moments as TM
    a = np.array([1.0, 0.9, 1.2])
    v = np.array([0.12, -0.08, 0.15])
    for mass in (0.0, 0.7):
        rho, p, q, pi = TM.moments_tilted(a, v, mass, backend="python")
        r_rho, r_p, r_q, r_pi = rustcore.kin_moments_tilted(a, v, mass)
        assert abs(r_rho / rho - 1.0) < 1e-12
        assert abs(r_p / p - 1.0) < 1e-12
        assert np.abs(r_q - q).max() / rho < 1e-12
        assert np.abs(r_pi - pi).max() / rho < 1e-12


def test_kin_tilted_rejects_superluminal():
    a = np.array([1.0, 0.9, 1.2])
    with pytest.raises(ValueError):
        rustcore.kin_j_moment_tilted(a, np.array([0.8, 0.8, 0.0]), 0.0, 0, 0)


def test_kin_rejects_rank_above_codegen_limit():
    """★ 기존 결함 수정: l > L_MAX 가 **panic** 이 아니라 ValueError 여야 한다.

    이전 판은 세 곳(`index_table` 범위, `pstf::basis` 매치, `symmetrize` 의
    `[0usize; 4]` 고정버퍼)에 l 한계가 흩어져 있었고 l=5 에서 Rust panic 이
    FFI 를 넘어왔다 (`kin_j_moment` 도 동일).  이제 경계에서 막고,
    codegen 한계와 스택버퍼 한계의 불일치는 **컴파일 시** 어서션으로 잡는다.
    """
    a = np.array([1.0, 0.9, 1.2])
    for fn in (lambda: rustcore.kin_j_moment(a, 0.7, 6, 0, 0.0, 2),
               lambda: rustcore.kin_j_moment_tilted(a, np.zeros(3), 0.7, 6, 0),
               lambda: rustcore.kin_pstf(np.zeros(3 ** 6), 6)):
        with pytest.raises(ValueError):
            fn()
    # l = 5 는 이제 지원된다 (codegen L_MAX 를 5 로 올렸다)
    assert np.asarray(rustcore.kin_j_moment(a, 0.7, 5, 0, 0.0, 2)).size == 3 ** 5
