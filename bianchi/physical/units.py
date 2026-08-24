"""
PR-31 · 단위계와 물리 상수 (경계 변환 일원화).

내부는 자연단위 (8πG = c = 1) + 무차원 τ.  관측 단위(km/s/Mpc, K, eV, Gyr, Mpc)
와의 변환은 여기 한 곳에서만.  설계 D7: ShearScalar 처럼 섞이면 조용히 틀리는
양들을 한 모듈에 가둔다.
"""
from __future__ import annotations

import numpy as np

# ---------------------------------------------------------------- CODATA / 천문 상수
# Exact SI definitions and CODATA 2022 recommended electron rest energy.
# Keep public cross-domain constants here; physics modules may retain aliases
# for compatibility but must not copy private recombination constants.
CODATA_RELEASE = "2022"
C_LIGHT_M_S = 299_792_458.0        # m/s, exact
C_LIGHT_KM_S = C_LIGHT_M_S / 1_000.0
BOLTZMANN_CONSTANT_J_K = 1.380_649e-23  # J/K, exact
ELECTRON_REST_ENERGY_J = 8.187_105_7880e-14  # J, CODATA 2022
ELECTRON_REST_ENERGY_EV = 510_998.950_69     # eV, CODATA 2022
MPC_KM = 3.0856775814913673e19     # 1 Mpc in km
GYR_S = 3.1556952e16               # 1 Gyr in s  (Julian)
KB_EV_K = 8.617333262e-5           # Boltzmann k_B in eV/K
T_CMB_K = 2.7255                   # 광자 온도 (Fixsen 2009)
HBAR_EV_S = 6.582119569e-16
G_NEWTON = 6.67430e-11             # m^3 kg^-1 s^-2

#: 임계밀도 계수: rho_crit = (3 H0^2)/(8πG);  Omega_i = rho_i/rho_crit
#: h = H0/(100 km/s/Mpc).  rho_crit,0 = 1.87834e-26 h^2 kg/m^3
RHO_CRIT_H2_KG_M3 = 1.8783e-26

#: 중성미자 온도비 (순간 탈결합):  T_nu/T_gamma = (4/11)^{1/3}
T_NU_OVER_T_GAMMA = (4.0 / 11.0) ** (1.0 / 3.0)
N_EFF_STANDARD = 3.044             # 비순간 탈결합 보정 포함


def hubble_time_gyr(H0_km_s_mpc):
    """1/H0 를 Gyr 로.  H0 [km/s/Mpc] -> t_H [Gyr]."""
    inv_H0_s = MPC_KM / H0_km_s_mpc          # (Mpc/km)*(s) = s
    return inv_H0_s / GYR_S


def hubble_distance_mpc(H0_km_s_mpc):
    """Hubble 거리 c/H0 [Mpc]."""
    return C_LIGHT_KM_S / H0_km_s_mpc


def redshift_to_scale_factor(z):
    return 1.0 / (1.0 + np.asarray(z, float))


def photon_omega_h2(T0_K=T_CMB_K):
    """광자 Ω_γ h^2 (흑체).  ≈ 2.47e-5 (T0=2.7255 K)."""
    # Omega_gamma h^2 = 2.4728e-5 * (T0/2.7255)^4
    return 2.4728e-5 * (T0_K / 2.7255) ** 4


def neutrino_omega_h2_massless(N_eff=N_EFF_STANDARD, T0_K=T_CMB_K):
    """무질량 중성미자 Ω_ν h^2 = (7/8)(4/11)^{4/3} N_eff Ω_γ h^2."""
    return (7.0 / 8.0) * (4.0 / 11.0) ** (4.0 / 3.0) * N_eff * photon_omega_h2(T0_K)


def massive_neutrino_omega_h2(sum_m_eV):
    """질량 중성미자 (비상대론적 근사) Ω_ν h^2 = Σm_ν / 93.14 eV."""
    return np.asarray(sum_m_eV, float) / 93.14


def to_dimensionful(H, Sigma, N, A, H0_km_s_mpc=None):
    """Hubble 정규화 (Σ, N, A) -> 차원량 (σ, n, a) = H*(...).  단위는 H 의 단위."""
    return dict(sigma=H * np.asarray(Sigma), n=H * np.asarray(N), a=H * np.asarray(A))
