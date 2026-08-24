"""M8 (PR-28/29/30) 물리 차트 기반 테스트."""
import numpy as np
import jax.numpy as jnp
import pytest

from bianchi.physical import chart as pc
from bianchi.physical import frame_transport as ft
from bianchi.matter import species as sp


# ══════════════════════════════ PR-28 physical/chart
def test_de_sitter_H_constant():
    """de Sitter (q=-1): H = const, ℓ = e^τ."""
    tau = np.linspace(0, 5, 400)
    r = pc.de_sitter(tau, H0=1.3)
    assert np.allclose(r["H"], 1.3, atol=1e-10)
    assert np.allclose(r["ell"], np.exp(tau), atol=1e-10)


def test_flat_dust_cosmic_time():
    """평탄 먼지 FLRW (q=1/2): t = 2/(3H) (적분과 해석식 일치)."""
    tau = np.linspace(0, 4, 2000)
    r = pc.flat_dust(tau, H0=1.0)
    # H = H0 e^{-(3/2)τ}
    assert np.allclose(r["H"], np.exp(-1.5 * tau), atol=1e-9)
    # 적분한 t 와 해석식 t = 2/(3H) 가 일치 (t0 = 2/(3H0) 로 맞춤)
    assert np.allclose(r["t"], r["t_exact"], atol=1e-6)


def test_hubble_reconstruction_identity():
    """H'/H = -(1+q) 를 사다리꼴로 적분한 값이 정의와 일치."""
    tau = np.linspace(0, 3, 1000)
    q = 0.3 + 0.5 * np.sin(tau)          # 임의 q(τ)
    H = pc.hubble_of_tau(tau, q, H0=2.0)
    # d ln H / dτ ≈ -(1+q)
    dlnH = np.gradient(np.log(H), tau)
    assert np.allclose(dlnH[5:-5], -(1 + q)[5:-5], atol=1e-3)


def test_ix_D_chart_recollapse_detection():
    """IX D-차트: H̄ 영점통과 = 재붕괴.  H = D H̄, t 는 감소방향."""
    tau_m = np.linspace(0, 6, 500)
    Hbar = np.cos(0.6 * tau_m)           # 부호가 바뀌는 모의 H̄
    D = 1.0 + 0.1 * np.sin(tau_m)
    r = pc.ix_physical_from_D(tau_m, Hbar, D, t0=0.0)
    assert np.allclose(r["H"], D * Hbar)
    idx = pc.recollapse_indices(Hbar)
    assert len(idx) >= 1                 # 최소 한 번의 재붕괴/반등
    # H-정규화라면 영점이 없다: H̄ 가 실제로 0 을 지나는지
    assert np.min(Hbar) < 0 < np.max(Hbar)


# ══════════════════════════════ PR-29 frame_transport
def test_trace_identity_gives_e3tau():
    """tr(I+Σ+Ω) = 3  =>  det E = e^{3τ}."""
    rng = np.random.default_rng(0)
    for _ in range(20):
        S = rng.normal(size=(3, 3)); S = 0.5 * (S + S.T); S -= np.trace(S) * np.eye(3) / 3
        R = rng.normal(size=3)
        assert abs(ft.trace_identity_residual(jnp.asarray(S), jnp.asarray(R))) < 1e-12


def test_det_triad_is_e3tau_constant_state():
    """상수 (Σ,R) 전송에서 det E(τ) = e^{3τ} (부피 = ℓ^3)."""
    S = np.diag([0.3, -0.1, -0.2])
    R = np.array([0.2, -0.15, 0.1])
    taus = np.linspace(0, 2, 400)
    E, detE = ft.integrate_triad(taus, lambda i: S, lambda i: R)
    assert np.allclose(detE, np.exp(3 * taus), rtol=1e-6)


def test_rotation_preserves_volume_and_is_gauge():
    """순수 회전 (Σ=0): det E = e^{3τ} 그대로, 즉 회전은 부피에 무영향."""
    R = np.array([0.5, -0.3, 0.2])
    taus = np.linspace(0, 1.5, 300)
    E, detE = ft.integrate_triad(taus, lambda i: np.zeros((3, 3)), lambda i: R)
    assert np.allclose(detE, np.exp(3 * taus), rtol=1e-6)
    # E(τ) E(τ)^T 의 대각합(부피형)이 e^{2τ}·(회전이므로 등방적으로)
    assert np.allclose(np.linalg.det(E[-1]), np.exp(3 * taus[-1]), rtol=1e-6)


def test_frame_transport_matches_legacy_directional():
    """대각 게이지 방향 스케일인자가 legacy directional_scale_factors 와 일치."""
    from bianchi.physical import directional_scale_factors as legacy
    taus = np.linspace(0, 2, 500)
    Sdiag = np.stack([0.2 * np.ones_like(taus), -0.05 * np.ones_like(taus),
                      -0.15 * np.ones_like(taus)], axis=-1)
    a_new = ft.directional_scale_factors_diag(taus, Sdiag)
    a_leg = legacy(taus, Sdiag)
    assert np.allclose(a_new, a_leg, rtol=1e-10)


def test_transport_sign_is_plus_Omega():
    """전송 생성자의 반대칭 부분이 +Ω = +eps R (부호 확정, d_transport)."""
    from bianchi.conventions import EPS3
    R = np.array([0.4, -0.2, 0.3])
    M = np.asarray(ft.transport_generator(np.zeros((3, 3)), jnp.asarray(R)))
    anti = 0.5 * (M - M.T)
    Omega = np.einsum('abc,c->ab', EPS3, R)      # +eps R
    assert np.allclose(anti, Omega, atol=1e-12)


# ══════════════════════════════ PR-30 matter/species
def test_species_adapters_reproduce_legacy_sources():
    """FluidSpecies/ScalarSpecies/MagneticSpecies 가 legacy 값을 재현."""
    rng = np.random.default_rng(1)
    Sigma = rng.normal(size=(3, 3)); Sigma = 0.5 * (Sigma + Sigma.T)
    Sigma -= np.trace(Sigma) * np.eye(3) / 3
    N = rng.normal(size=(3, 3)); N = 0.5 * (N + N.T)
    A = rng.normal(size=3); R = rng.normal(size=3)
    ctx = sp.Ctx.of(Sigma, N, A, R)

    v = np.array([0.2, -0.1, 0.05])
    fs = sp.FluidSpecies.of(1.3, 0.4, v)
    from bianchi.matter.fluid import sources as legacy_src
    leg = legacy_src(fs.fluid, jnp.asarray(Sigma), jnp.asarray(A))
    assert np.isclose(float(fs.omega(ctx)), float(leg["Omega"]))
    assert np.allclose(np.asarray(fs.pi(ctx)), np.asarray(leg["Pi"]))
    assert np.allclose(np.asarray(fs.q_flux(ctx)), np.asarray(leg["q_flux"]))

    sc = sp.ScalarSpecies.of(0.3, 0.5, 1.0)
    assert np.isclose(float(sc.omega(ctx)), 0.3**2 + 0.5**2)
    assert np.allclose(np.asarray(sc.pi(ctx)), 0.0)

    mg = sp.MagneticSpecies.of(np.array([0.0, 0.2, -0.1]))
    assert np.isclose(float(mg.omega(ctx)), (0.2**2 + 0.1**2) / 6.0)


def test_species_mix_deceleration_matches_sum():
    """SpeciesMix.deceleration = 2Σ² + Σ_i q_source_i (복사+먼지+Λ 예)."""
    Sigma = np.diag([0.1, -0.05, -0.05])
    ctx = sp.Ctx.of(Sigma, np.zeros((3, 3)), np.zeros(3))
    rad = sp.FluidSpecies.of(4.0 / 3.0, 0.5, np.zeros(3))    # 복사
    dust = sp.FluidSpecies.of(1.0, 0.3, np.zeros(3))         # 먼지
    lam = sp.FluidSpecies.of(1e-9, 0.2, np.zeros(3))         # ~Λ (γ→0)
    mix = sp.SpeciesMix.of(rad, dust, lam)
    Sigma2 = np.trace(Sigma @ Sigma) / 6.0
    expect = 2 * Sigma2 + sum(float(m.q_source(ctx)) for m in (rad, dust, lam))
    assert np.isclose(float(mix.deceleration(ctx)), expect)


def test_species_exchange_conservation_enforced():
    """비상호작용 혼합은 ΣQ=0; 상호작용 켜면 짝을 맞춰야 통과."""
    Sigma = np.zeros((3, 3))
    ctx = sp.Ctx.of(Sigma, np.zeros((3, 3)), np.zeros(3))
    # 비상호작용
    a = sp.FluidSpecies.of(1.0, 0.3, np.zeros(3))
    b = sp.FluidSpecies.of(4.0 / 3.0, 0.5, np.zeros(3))
    assert sp.SpeciesMix.of(a, b).check_exchange_conservation(ctx)
    # 짝이 안 맞는 상호작용 -> 실패
    a2 = sp.FluidSpecies.of(1.0, 0.3, np.zeros(3), Q_energy=0.1)
    assert not sp.SpeciesMix.of(a2, b).check_exchange_conservation(ctx)
    # 짝을 맞추면 통과
    b2 = sp.FluidSpecies.of(4.0 / 3.0, 0.5, np.zeros(3), Q_energy=-0.1)
    assert sp.SpeciesMix.of(a2, b2).check_exchange_conservation(ctx)
