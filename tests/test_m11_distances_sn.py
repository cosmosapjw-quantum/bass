"""PR-47 거리·이방 BAO + PR-48 SNIa Hubble diagram 테스트."""
import numpy as np
import pytest

from bianchi.observables import distances as dist
from bianchi.observables import sn


# ═══════════════════════════════════════════ PR-47 거리·BAO
def test_sound_horizon_planck():
    """r_s(z_drag) ≈ 147 Mpc (Planck)."""
    rs = dist.sound_horizon(H0=67.4, Om=0.315, Ob_h2=0.0224)
    assert 143.0 < rs < 151.0


def test_hubble_distance():
    """D_H(z) = c/H(z);  z=0 이면 c/H0."""
    DH0 = dist.hubble_distance(1e-6, H0=67.4)
    assert abs(DH0 - 299792.458 / 67.4) < 1.0


def test_bao_observables_structure():
    b = dist.bao_observables(0.5, H0=67.4, Om=0.315)
    assert b["DM_over_rs"] > 0 and b["DH_over_rs"] > 0 and b["DV_over_rs"] > 0
    # F_AP = D_M/D_H, 그리고 D_V 는 D_M,D_H 사이 스케일
    assert abs(b["F_AP"] - b["DM_over_rs"] / b["DH_over_rs"]) < 1e-9
    assert b["DM_over_rs"] > b["DH_over_rs"] * 0.1


def test_anisotropic_bao_isotropic_limit():
    """Σ=0 → 방향 무관, anisotropy=0."""
    r = dist.anisotropic_bao(0.5, np.zeros((3, 3)))
    assert r["anisotropy"] < 1e-12
    assert np.allclose(r["DH_over_rs"], r["DH_over_rs"][0])


def test_anisotropic_bao_shear_signal():
    """Σ≠0 → 방향별 D_H 갈라짐 (이방 BAO 신호)."""
    Sig = np.diag([0.1, -0.05, -0.05])
    r = dist.anisotropic_bao(0.5, Sig,
                             nhats=np.array([[1., 0, 0], [0, 1., 0], [0, 0, 1.]]))
    assert r["anisotropy"] > 1e-3
    # x 방향(Σ_xx>0) 팽창 빠름 → D_H=c/H_∥ 작음
    assert r["DH_over_rs"][0] < r["DH_over_rs"][1]


def test_ap_quadrupole_scales_with_shear():
    """AP 사중극 C₂: Σ=0→0, 그리고 2Σ 가 Σ 보다 큼."""
    c0 = dist.alcock_paczynski_quadrupole(0.5, np.zeros((3, 3)))
    Sig = np.diag([0.08, -0.04, -0.04])
    c1 = dist.alcock_paczynski_quadrupole(0.5, Sig)
    c2 = dist.alcock_paczynski_quadrupole(0.5, 2 * Sig)
    assert c0 < 1e-14
    assert c2 > c1 > 1e-12


def test_directional_hubble_eigendirection():
    """H_∥ = H(1+Σ_nn);  대각 Σ 의 고유방향에서 성분값."""
    H = 70.0; Sig = np.diag([0.1, -0.1, 0.0])
    assert abs(dist.directional_hubble(H, Sig, [1, 0, 0]) - 70 * 1.1) < 1e-9
    assert abs(dist.directional_hubble(H, Sig, [0, 1, 0]) - 70 * 0.9) < 1e-9


# ═══════════════════════════════════════════ PR-48 SNIa
def test_distance_modulus_anchor():
    """d_L=10 pc → μ=0;  d_L=10 Mpc → μ=30."""
    assert abs(sn.distance_modulus(1e-5)) < 1e-9        # 10 pc = 1e-5 Mpc
    assert abs(sn.distance_modulus(10.0) - 30.0) < 1e-9


def test_mu_directional_reduces_to_iso():
    """Σ=0 → μ(z,n̂) = μ_iso(z)."""
    z = 0.1
    mu_iso = sn.distance_modulus(sn.luminosity_distance_iso(z))
    for n in ([1, 0, 0], [0, 1, 0], [0, 0, 1]):
        assert abs(sn.mu_directional(z, n, np.zeros((3, 3))) - mu_iso) < 1e-9


def test_peculiar_velocity_dipole_sign():
    """관측자가 n̂ 방향으로 이동(β·n̂>0) → δμ<0 (가까워 보임)."""
    v = np.array([1e-3, 0, 0])
    assert sn.peculiar_velocity_residual(0.02, v, [1, 0, 0]) < 0
    assert sn.peculiar_velocity_residual(0.02, v, [-1, 0, 0]) > 0
    # ∝ 1/z: 저-z 에서 더 큼
    r_lo = abs(sn.peculiar_velocity_residual(0.01, v, [1, 0, 0]))
    r_hi = abs(sn.peculiar_velocity_residual(0.05, v, [1, 0, 0]))
    assert r_lo > r_hi


def test_decompose_isotropic_null():
    """Σ=0, v=0 → C₁≈C₂≈0."""
    d = sn.decompose_dipole_quadrupole(0.1, np.zeros((3, 3)), v=None)
    assert d["C1"] < 1e-12 and d["C2"] < 1e-12


def test_decompose_shear_is_quadrupole():
    """Σ≠0, v=0 → 사중극 C₂ 지배 (C₂ >> C₁)."""
    Sig = np.diag([0.05, -0.025, -0.025])
    d = sn.decompose_dipole_quadrupole(0.1, Sig, v=None)
    assert d["C2"] > 1e-10
    assert d["C2"] > 100 * d["C1"]


def test_decompose_velocity_is_dipole():
    """v≠0, Σ=0 → 쌍극 C₁ 지배 (C₁ >> C₂)."""
    d = sn.decompose_dipole_quadrupole(0.05, np.zeros((3, 3)), v=np.array([2e-3, 0, 0]))
    assert d["C1"] > 1e-10
    assert d["C1"] > 100 * d["C2"]


def test_pantheon_format_fields():
    """Pantheon+ 유사 레코드 구조."""
    zs = [0.02, 0.1, 0.3]; ras = [10., 120., 250.]; decs = [-30., 5., 60.]
    rec = sn.to_pantheon_format(zs, ras, decs, np.diag([0.03, -0.015, -0.015]),
                                v=np.array([1e-3, 0, 0]))
    assert rec.shape == (3,)
    assert set(rec.dtype.names) == {"zHD", "MU", "MU_ERR", "RA", "DEC"}
    assert np.all(rec["MU"] > 0) and np.all(np.isfinite(rec["MU"]))
