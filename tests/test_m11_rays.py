"""M11 (PR-43 geodesics) 광선 추적 테스트."""
import numpy as np
import jax.numpy as jnp
import pytest

from bianchi.rays import geodesics as gd
from bianchi.rays.frame import P_double, frame_connection


# ══════════════════════════════ PR-43 널 측지선
def test_flrw_redshift_1_plus_z_equals_1_over_a():
    """평탄 먼지 FLRW: 1+z = 1/a = e^{-lna}."""
    hist = gd.trace_ray_diag_bianchi(
        dict(H0=1.0, Sigma0=[0, 0, 0], Omega0=1.0, gamma=1.0, nhat=[0, 0, 1]),
        t0=2.0 / 3.0, t_end=0.2 * 2.0 / 3.0, nsteps=8000)
    z = np.array([h["z"] for h in hist])
    lna = np.array([h["lna"][0] for h in hist])
    ok = z > 0.01
    assert np.allclose(np.exp(-lna[ok]), 1 + z[ok], rtol=1e-4)
    assert np.all(np.diff(z) >= -1e-9)          # z 단조 증가 (과거로)


def test_norm_preserved_along_ray():
    """|n̂| = 1 이 적분 내내 보존."""
    hist = gd.trace_ray_diag_bianchi(
        dict(H0=1.0, Sigma0=[0.25, -0.1, -0.15], Omega0=0.7, gamma=1.0,
             nhat=[0.4, -0.3, 0.87]), t0=1.0, t_end=0.5, nsteps=6000)
    for h in hist:
        assert abs(np.linalg.norm(h["nhat"]) - 1.0) < 1e-8


def test_photon_rhs_matches_verified_closed_form():
    """photon_rhs 가 D13 검증식과 일치 (부호 +(R×...) 포함)."""
    from bianchi.conventions import EPS3
    rng = np.random.default_rng(0)
    for _ in range(50):
        N = rng.normal(size=(3, 3)); N = 0.5 * (N + N.T)
        w, V = np.linalg.eigh(N); k = int(np.argmin(abs(w))); w[k] = 0
        N = V @ np.diag(w) @ V.T; A = float(rng.normal()) * V[:, k]
        S = rng.normal(size=(3, 3)); S = 0.5 * (S + S.T); S -= np.trace(S) * np.eye(3) / 3
        R = rng.normal(size=3); H = float(rng.uniform(0.5, 2))
        nh = rng.normal(size=3); nh /= np.linalg.norm(nh)
        E = float(rng.uniform(0.3, 3))
        dE, dn = gd.photon_rhs(E, nh, H, S, N, A, R)
        # closed form
        Sn = S @ nh; nSn = nh @ Sn
        P = np.asarray(P_double(N, A, nh))
        dE_ref = -E * (H + nSn)
        dn_ref = -(Sn - nSn * nh) + np.cross(R, nh) - (P - (nh @ P) * nh)
        assert abs(dE - dE_ref) < 1e-12
        assert np.allclose(dn, dn_ref, atol=1e-12)
        # n̂·dn̂ = 0 (노름 보존의 미분형)
        assert abs(nh @ dn) < 1e-12


def test_kasner_redshift():
    """진공 Kasner (Σ 상수, Ω=0): 방향별 적색이동이 방향에 의존.

    Kasner Σ_i = 상수, N=A=0.  세 축 방향 광선의 z 가 서로 다르다.
    """
    zs = {}
    for lbl, nhat in (('x', [1, 0, 0]), ('y', [0, 1, 0]), ('z', [0, 0, 1])):
        hist = gd.trace_ray_diag_bianchi(
            dict(H0=1.0, Sigma0=[0.6, -0.3, -0.3], Omega0=0.0, gamma=1.0, nhat=nhat),
            t0=1.0, t_end=0.6, nsteps=6000)
        # 같은 적분 끝점에서의 z
        zs[lbl] = hist[-1]["z"]
    # x 축(Σ=+0.6)과 y/z 축(Σ=-0.3)의 z 가 유의하게 다르다
    assert abs(zs['x'] - zs['y']) > 1e-3
    assert np.isclose(zs['y'], zs['z'], rtol=1e-6)   # y,z 대칭


def test_frame_connection_blocks():
    """프레임 접속 블록이 검증값과 일치: Γ^0_ab = Γ^a_0b = Hδ+σ, Γ^a_b0 = -εR."""
    from bianchi.conventions import EPS3
    rng = np.random.default_rng(2)
    N = rng.normal(size=(3, 3)); N = 0.5 * (N + N.T); A = rng.normal(size=3)
    S = rng.normal(size=(3, 3)); S = 0.5 * (S + S.T); S -= np.trace(S) * np.eye(3) / 3
    R = rng.normal(size=3); H = 1.3
    G = np.asarray(frame_connection(H, S, N, A, R))
    K = H * np.eye(3) + S
    assert np.allclose(G[0, 1:, 1:], K, atol=1e-12)
    assert np.allclose(G[1:, 0, 1:], K, atol=1e-12)
    assert np.allclose(G[1:, 1:, 0], -np.einsum('abc,c->ab', EPS3, R), atol=1e-12)
    assert abs(G[0, 0, 0]) < 1e-15


# ══════════════════════════════ PR-45 Weyl / tidal matrix
def _screen(nh):
    from bianchi.rays.optical import screen_basis
    return screen_basis(nh)


def test_tidal_matrix_D16_oracle():
    """tr T = -Ric_ab k^a k^b (Ricci 집속), T 대칭 — 일반 class B."""
    from bianchi.rays import weyl
    rng = np.random.default_rng(0)
    es = ef = 0.0
    for _ in range(20):
        N = rng.normal(size=(3, 3)); N = 0.5 * (N + N.T)
        w, V = np.linalg.eigh(N); k = int(np.argmin(abs(w))); w[k] = 0
        N = V @ np.diag(w) @ V.T; A = float(rng.normal()) * V[:, k]
        s = rng.normal(size=(3, 3)); s = 0.5 * (s + s.T); s -= np.trace(s) * np.eye(3) / 3
        H = float(rng.uniform(0.5, 2))
        state = dict(H=H, N=N, A=A, sigma=s, R=np.zeros(3))
        nh = rng.normal(size=3); nh /= np.linalg.norm(nh)
        kk = np.concatenate([[1.0], nh]); sc = _screen(nh)
        T = weyl.tidal_matrix(kk, sc, state)
        Ric = np.einsum('abad->bd', weyl.riemann_up(state))
        focus = -np.einsum('bd,b,d->', Ric, kk, kk)
        es = max(es, abs(T[0, 1] - T[1, 0]))
        ef = max(ef, abs(T.trace() - focus))
    assert es < 1e-12 and ef < 1e-10


# ══════════════════════════════ PR-44 Sachs optics
def test_eds_angular_diameter_distance():
    """EdS 기준해 d_A = (2/H0)(1-(1+z)^{-1/2})/(1+z) (RK4, 4-벡터 스크린)."""
    from bianchi.rays import optical as op
    H0 = 1.0; t0 = 2 / (3 * H0)
    r = op.trace_optical_diag_bianchi(
        dict(H0=H0, Sigma0=[0, 0, 0], Omega0=1.0, gamma=1.0, nhat=[0, 0, 1]),
        t0, 0.7 * t0, nsteps=2000)
    z = np.array([h["z"] for h in r["hist"]]); dA = np.array([h["dA"] for h in r["hist"]])
    ok = (z > 0.05) & (z < 1.2) & np.isfinite(dA)
    pred = (2 / H0) * (1 - 1 / np.sqrt(1 + z[ok])) / (1 + z[ok])
    assert np.max(np.abs(dA[ok] / pred - 1)) < 1e-6
    assert r["screen_ortho"] < 1e-12          # 4-벡터 스크린: k·E_A = 0 유지


def test_anisotropic_dA_direction_dependence():
    """이방 배경(Bianchi I)에서 d_A 가 방향에 유의하게 의존."""
    from bianchi.rays import optical as op
    H0 = 1.0; t0 = 2 / (3 * H0)
    dAs = {}
    for lbl, nhat in (('x', [1, 0, 0]), ('y', [0, 1, 0]), ('z', [0, 0, 1])):
        r = op.trace_optical_diag_bianchi(
            dict(H0=H0, Sigma0=[0.25, -0.1, -0.15], Omega0=0.9, gamma=1.0, nhat=nhat),
            t0, 0.6 * t0, nsteps=1500)
        h = r["hist"]; zz = np.array([x["z"] for x in h]); dd = np.array([x["dA"] for x in h])
        i = int(np.argmin(np.abs(zz - 0.3)))
        dAs[lbl] = dd[i]
    spread = (max(dAs.values()) - min(dAs.values())) / np.mean(list(dAs.values()))
    assert spread > 0.05                       # 방향 의존 실재 (>5%)


def test_etherington_via_flrw_reciprocity():
    """FLRW 극한에서 광자수 보존의 귀결로 d_A 가 표준 EdS 값과 일치 (Etherington 정합).

    d_L = (1+z)^2 d_A 를 *정의*하지 않고, d_A 를 Sachs 로 독립 적분해 EdS 와 대조한다.
    """
    from bianchi.rays import optical as op
    H0 = 1.0; t0 = 2 / (3 * H0)
    r = op.trace_optical_diag_bianchi(
        dict(H0=H0, Sigma0=[0, 0, 0], Omega0=1.0, gamma=1.0, nhat=[1, 0, 0]),
        t0, 0.6 * t0, nsteps=2000)
    z = r["z_final"]; dA = r["dA_final"]
    dL = (1 + z) ** 2 * dA                      # Etherington (검증용, 정의 아님)
    dL_eds = (2 / H0) * (1 + z) * (1 - 1 / np.sqrt(1 + z))   # EdS 광도거리
    assert abs(dL / dL_eds - 1) < 1e-6
