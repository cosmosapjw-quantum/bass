"""M9 (PR-31/32/33) 단위·초기조건·열역사 테스트."""
import numpy as np
import pytest

from bianchi.physical import units as U
from bianchi.physical import initial as ini
from bianchi.thermo import dof, temperature as temp


# ══════════════════════════════ PR-31 units / initial
def test_lcdm_age_and_equality():
    """ΛCDM 나이 ≈ 13.8 Gyr, z_eq ≈ 3400 (관측 근사)."""
    lc = ini.flrw_lcdm_today(h=0.674, Omega_m=0.315)
    age = ini.age_gyr_lcdm(h=0.674, Omega_m=0.315)
    assert 13.6 < age < 14.0, age
    zeq = ini.matter_radiation_equality(lc["Omega_m"], lc["Omega_r"])
    assert 3000 < zeq < 3600, zeq


def test_photon_neutrino_omega():
    """Ω_γ h^2 ≈ 2.47e-5, T_ν/T_γ = (4/11)^{1/3}."""
    assert abs(U.photon_omega_h2() - 2.4728e-5) < 1e-7
    assert abs(U.T_NU_OVER_T_GAMMA - (4 / 11) ** (1 / 3)) < 1e-12
    assert abs(U.massive_neutrino_omega_h2(0.06) - 0.06 / 93.14) < 1e-9


def test_hubble_time_distance():
    """H0=67.4 -> 1/H0 ≈ 14.5 Gyr, c/H0 ≈ 4450 Mpc."""
    assert abs(U.hubble_time_gyr(67.4) - 14.5) < 0.2
    assert abs(U.hubble_distance_mpc(67.4) - 4448) < 20


def test_anisotropic_initial_gauss_closure():
    """이방 초기상태가 Gauss 를 만족하도록 shear 를 맞추면 잔차 0."""
    Om = dict(r=0.3, m=0.2, L=0.4)                # 합 0.9
    # Bianchi I: Σ² = 1 - ΣΩ = 0.1
    Sig2 = ini.shear_from_gauss(Om, K=0.0)
    assert abs(Sig2 - 0.1) < 1e-12
    s = np.sqrt(6 * Sig2 / 6)                     # diag Σ = (s,-s/2,-s/2) 근사
    Sigma0 = np.diag([2 * np.sqrt(Sig2 / 1), 0, 0]) * 0  # 구성만
    # 정확히 Σ²=0.1 인 대각 shear 구성
    a = np.sqrt(0.1)                              # Σ² = (1/6)(4a²+a²+a²)= a²
    Sigma0 = np.diag([-2 * a, a, a]) / np.sqrt(6) * np.sqrt(6)
    Sigma0 = np.diag([-2 * a, a, a])
    r = ini.anisotropic_initial_state(Om, Sigma0)
    assert abs(r["Sigma2"] - 0.1) < 1e-9
    assert abs(r["gauss_residual"]) < 1e-9


# ══════════════════════════════ PR-32 dof
def test_gstar_limits():
    """g_*(T>>m_t)=106.75 (10 TeV 점근), (g_*,g_*s)(T<<m_e)=(3.36,3.91).

    ★ v3.0 (A1): 이전 판은 T=1 TeV 에서 106.75 를 요구했으나, 이는 구(舊) 골격표의
      **근사**였다.  격자QCD 반영 표(Husdal 2016)의 참값은 1 TeV 에서 106.72 이고,
      106.75 는 10 TeV 점근값이다.  테스트가 근사를 박제하고 있던 사례.
    """
    assert abs(dof.g_star(1e4) - 106.75) < 1e-6          # 10 TeV 점근
    assert abs(dof.g_star_s(1e4) - 106.75) < 1e-6
    assert abs(dof.g_star(1e3) - 106.72) < 1e-6          # 1 TeV (복사보정)
    assert abs(dof.g_star(1e-5) - 3.36) < 0.01
    assert abs(dof.g_star_s(1e-5) - 3.91) < 0.01


def test_gstar_qcd_region_regression():
    """QCD 전이 구간 회귀 가드 — 구표의 실제 오류를 박제.

    구표: T=1 GeV → 106.75 (참 76.34, 40% 과대);  T=200 keV → 3.909 (참 7.66).
    이 두 점은 WIMP 동결(x_f ~ m/20)과 e± 소멸이 놓이는 구간이라 결과에 직접 영향.
    """
    assert abs(dof.g_star(1.0) - 76.34) < 0.05           # 구표는 106.75 였다
    assert abs(dof.g_star(0.1) - 18.00) < 0.05
    assert abs(dof.g_star(2e-4) - 7.66) < 0.05           # 구표는 3.909 였다
    # QCD 전이에서 단조 감소 (온도 낮아지면 자유도 감소)
    Ts = [10.0, 1.0, 0.3, 0.2, 0.15, 0.1, 0.01]
    gs = [dof.g_star(T) for T in Ts]
    assert all(gs[i] > gs[i + 1] for i in range(len(gs) - 1)), gs


def test_gstar_monotone():
    """g_* 는 T 증가에 대해 비감소 (단조 보간)."""
    T = np.logspace(-5, 3, 200)
    g = dof.g_star(T)
    assert np.all(np.diff(g) >= -1e-9)


# ══════════════════════════════ PR-33 temperature
def test_neutrino_temperature_ratio():
    """T_ν/T_γ = (4/11)^{1/3} ≈ 0.7138."""
    Tg = 1.0
    assert abs(temp.neutrino_temperature(Tg) - 0.71377) < 1e-4


def test_entropy_conservation_T_of_ell():
    """엔트로피 보존: g_*s T^3 ℓ^3 = const.  T(ℓ) 를 풀어 s ℓ^3 불변 확인."""
    T0 = 1e-3                                     # 1 MeV
    ells = np.array([1.0, 2.0, 5.0, 10.0])
    Ts = temp.temperature_of_ell(ells, T0, ell0=1.0)
    # s ℓ^3 = g_*s T^3 ℓ^3 이 모두 같아야
    s_ell3 = dof.g_star_s(Ts) * Ts ** 3 * ells ** 3
    assert np.allclose(s_ell3, s_ell3[0], rtol=1e-6)


def test_temperature_scales_inverse_ell_in_constant_gstar():
    """g_*s 상수 구간에서는 T ∝ 1/ℓ (재결합 이후)."""
    T0 = 1e-9                                     # 저온, g_*s 상수
    ells = np.array([1.0, 2.0, 4.0])
    Ts = temp.temperature_of_ell(ells, T0)
    assert np.allclose(Ts * ells, Ts[0] * ells[0], rtol=1e-6)
