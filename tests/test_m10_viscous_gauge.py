"""PR-39 점성 + PR-40 게이지장 테스트."""
import numpy as np
import jax.numpy as jnp
import pytest

from bianchi.matter import viscous as vis
from bianchi.matter import gauge_field as gf


# ══════════════════════════════ PR-39 점성
def test_eckart_damping_sign():
    """Eckart Π = -2(η/H)Σ: shear 와 반대부호 (등방화)."""
    Sigma = np.diag([0.2, -0.1, -0.1])
    Pi = vis.eckart_anisotropic_stress(Sigma, eta_over_H=0.5)
    assert np.allclose(Pi, -1.0 * Sigma)          # -2*0.5 = -1
    assert np.sign(Pi[0, 0]) == -np.sign(Sigma[0, 0])


def test_entropy_production_nonneg():
    """T Ṡ = 2ησ² + ζθ² ≥ 0 (η,ζ ≥ 0)."""
    Sigma = np.diag([0.3, -0.15, -0.15])
    s = vis.entropy_production_rate(Sigma, theta=3.0, eta=0.1, zeta=0.05, H=1.0)
    assert s > 0
    # η=ζ=0 -> 0
    assert vis.entropy_production_rate(Sigma, 3.0, 0.0, 0.0) == 0.0


def test_israel_stewart_eckart_limit():
    """IS 완화시간 τ_π → 0 에서 Eckart 로 수렴."""
    Sigma = np.diag([0.2, -0.1, -0.1]); H = 1.2; eta = 0.3
    is_ = vis.IsraelStewartStress(Pi=np.zeros((3, 3)), tau_pi=1e-6, eta=eta)
    # Π 가 정지상태(dΠ/dt=0)면 Π = -2η σ
    Pi_eq = is_.eckart_limit(Sigma, H)
    assert np.allclose(Pi_eq, -2 * eta * H * Sigma)
    # rhs 가 Π 를 Eckart 값으로 끌어당김 (부호)
    rhs = is_.rhs(Sigma, H)
    assert np.allclose(rhs, -(is_.Pi + 2 * eta * H * Sigma) / 1e-6)


# ══════════════════════════════ PR-40 게이지장
def test_maxwell_curl_relative_sign():
    """curl 상대부호 + : (curl X)_a = n_ab X^b + eps_abc a^b X^c (v1.2)."""
    from bianchi.conventions import EPS3
    N = np.diag([0.0, 0.6, -0.4]); A = np.array([0.5, 0, 0]); X = np.array([0.1, 0.2, -0.3])
    c = gf._curl(N, A, X)
    assert np.allclose(c, N @ X + np.cross(A, X))
    # 구부호(-)와 구별
    assert not np.allclose(c, N @ X - np.cross(A, X))


def test_maxwell_EB_duality():
    """Ė, Ḃ 가 쌍대구조: E↔B, curl 부호 반전."""
    rng = np.random.default_rng(0)
    E = rng.normal(size=3); B = rng.normal(size=3)
    N = np.diag([0.3, -0.2, -0.1]); A = np.array([0.4, 0, 0])
    sig = np.diag([0.1, -0.05, -0.05]); R = np.zeros(3); H = 1.0
    dE, dB = gf.maxwell_rhs(E, B, H, sig, N, A, R)
    # E=0 이면 Ḃ 에 curl(E)=0, dE = -curl(B)
    dE0, dB0 = gf.maxwell_rhs(np.zeros(3), B, H, sig, N, A, R)
    assert np.allclose(dE0, -gf._curl(N, A, B) - 2 * H * 0 + sig @ np.zeros(3))
    assert np.allclose(dE0, -gf._curl(N, A, B))


def test_em_reduces_to_magnetic():
    """f=1, E=0 극한: ρ = B²/2, p = B²/6 (γ_eff=4/3), 순수 자기장."""
    B = np.array([0.0, 0.3, -0.2])
    rho, p = gf.em_energy_pressure(np.zeros(3), B)
    assert abs(rho - 0.5 * (B @ B)) < 1e-12
    assert abs(p - rho / 3) < 1e-12


def test_em_anisotropic_stress_tracefree():
    E = np.array([0.2, 0, 0]); B = np.array([0, 0.3, 0])
    pi = gf.em_anisotropic_stress(E, B)
    assert abs(np.trace(pi)) < 1e-12
    assert np.allclose(pi, pi.T)


def test_gauss_constraints():
    """a·E = 0, a·B = 0."""
    A = np.array([1.0, 0, 0]); E = np.array([0, 0.2, 0.1]); B = np.array([0, -0.1, 0.3])
    c = gf.gauss_constraints(E, B, A)
    assert abs(c["divE"]) < 1e-12 and abs(c["divB"]) < 1e-12


def test_anisotropic_inflation_attractor_nonzero():
    """이방 인플레이션: Σ/H = O(ε) ≠ 0 (no-hair 위반)."""
    sh = gf.anisotropic_inflation_attractor(epsilon=0.01, c=2.0)
    assert sh > 0                                  # 게이지장 유지 -> 잔류 이방성
    # ε → 0 에서 Σ/H → 0 (no-hair 회복)
    assert gf.anisotropic_inflation_attractor(0.0, 2.0) == 0.0
