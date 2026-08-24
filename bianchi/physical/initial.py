"""
PR-31 · 초기조건 빌더.  오늘의 Ω_i0 -> 과거로 역적분할 초기 상태.

솔버는 팽창정규화 τ 로 돈다.  관측은 오늘 (τ=0, ℓ=1) 의 밀도 파라미터 Ω_i0 로
주어지므로, 여기서 오늘 상태를 만들고 필요하면 과거로 역적분하는 헬퍼를 제공한다.

  Gauss (오늘):  Σ² + K + Σ_i Ω_i0 = 1     (Σ²=Σ_abΣ^ab/6, K=곡률 기여)
  각 종족의 τ-스케일링:  Ω_i ∝ ℓ^{-3γ_i + ...}  (일반 Bianchi 는 shear 결합 포함)

역적분은 physical.chart + 종족 진화로 수행 (여기선 초기 상태 구성만).
"""
from __future__ import annotations

import numpy as np

from bianchi.physical import units as U


def flrw_lcdm_today(h=0.674, Omega_m=0.315, Omega_b=0.049, T0_K=U.T_CMB_K,
                    N_eff=U.N_EFF_STANDARD, sum_m_nu_eV=0.06):
    """오늘의 ΛCDM 밀도 파라미터 묶음 (등방 극한, 회귀 기준).

    Ω_γ, Ω_ν(무질량+질량), Ω_c(CDM), Ω_b, Ω_Λ = 1 - 나머지 (평탄).
    """
    Og = U.photon_omega_h2(T0_K) / h ** 2
    Onu = U.neutrino_omega_h2_massless(N_eff, T0_K) / h ** 2
    Onu_m = U.massive_neutrino_omega_h2(sum_m_nu_eV) / h ** 2
    Or = Og + Onu                                   # 복사 (무질량 중성미자 포함)
    Oc = Omega_m - Omega_b - Onu_m
    OL = 1.0 - Omega_m - Or                         # 평탄
    return dict(h=h, Omega_gamma=Og, Omega_nu_massless=Onu, Omega_nu_massive=Onu_m,
                Omega_c=Oc, Omega_b=Omega_b, Omega_r=Or, Omega_m=Omega_m,
                Omega_Lambda=OL, Omega_total=Omega_m + Or + OL)


def matter_radiation_equality(Omega_m, Omega_r):
    """z_eq = Ω_m/Ω_r - 1  (등방)."""
    return Omega_m / Omega_r - 1.0


def age_gyr_lcdm(h=0.674, Omega_m=0.315, Omega_Lambda=None, nz=200000):
    """평탄 ΛCDM 우주 나이 [Gyr] = (1/H0)∫_0^1 da/(a E(a)),  E=√(Ω_m a^-3+Ω_Λ)."""
    if Omega_Lambda is None:
        Omega_Lambda = 1.0 - Omega_m
    a = np.linspace(1e-8, 1.0, nz)
    E = np.sqrt(Omega_m * a ** -3 + Omega_Lambda)
    integ = 1.0 / (a * E)
    t_over_tH = np.trapezoid(integ, a)
    return t_over_tH * U.hubble_time_gyr(100.0 * h)


def anisotropic_initial_state(Omega_i0, Sigma0, N0=None, A0=None):
    """오늘(τ=0) 의 이방 초기 상태를 Gauss 로 완결.

    Omega_i0: 종족별 오늘 밀도 파라미터 dict,
    Sigma0: (3,3) trace-free shear (Hubble 정규화),
    N0, A0: 곡률 (없으면 Bianchi I).
    반환: (Sigma0, N0, A0, Omega_total, gauss_residual).
    """
    Sigma0 = np.asarray(Sigma0, float)
    Sigma2 = np.trace(Sigma0 @ Sigma0) / 6.0
    N0 = np.zeros((3, 3)) if N0 is None else np.asarray(N0, float)
    A0 = np.zeros(3) if A0 is None else np.asarray(A0, float)
    # K = -^3R/(6H^2);  ^3R = -tr N^2 + (1/2)(tr N)^2 - 6 A.A
    R3 = -np.trace(N0 @ N0) + 0.5 * np.trace(N0) ** 2 - 6.0 * (A0 @ A0)
    K = -R3 / 6.0
    Om_tot = sum(Omega_i0.values())
    gauss = Sigma2 + K + Om_tot - 1.0             # 0 이어야 함
    return dict(Sigma0=Sigma0, N0=N0, A0=A0, Sigma2=Sigma2, K=K,
                Omega_total=Om_tot, gauss_residual=gauss)


def shear_from_gauss(Omega_i0, K=0.0):
    """오늘의 등가 shear Σ² = 1 - K - ΣΩ_i0 (Bianchi I 에서 Σ² ≥ 0 이어야 물리)."""
    Sigma2 = 1.0 - K - sum(Omega_i0.values())
    return Sigma2
