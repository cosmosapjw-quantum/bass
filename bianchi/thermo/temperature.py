"""
PR-33 · 온도-부피 관계 T(ℓ) 와 중성미자 온도.

엔트로피 보존 (설계 D6):  g_*s(T) T^3 (a1 a2 a3) = g_*s T^3 ℓ^3 = const.
  ⟹  T ∝ g_*s(T)^{-1/3} ℓ^{-1}.
★ 함정 (설계 §6-1): 온도는 **평균 스케일 ℓ** 만 따른다.  방향 의존은 광선의
  적색이동(PR-43)에서만 나온다 — 둘을 곱하면 이방성을 이중계산한다.
★ 함정 (§6-2): 엔트로피 보존은 국소 평형 + 비틸트 종족일 때만.  tilted 종족엔
  Γ 인자가 붙는다.

중성미자:  e± 소멸로 광자만 데워져  T_ν/T_γ = (4/11)^{1/3}.
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import brentq

from bianchi.thermo import dof
from bianchi.physical import units as U


def temperature_of_ell(ell, T0_GeV, ell0=1.0):
    """엔트로피 보존으로 T(ℓ) 를 푼다:  g_*s(T) T^3 ℓ^3 = g_*s(T0) T0^3 ℓ0^3.

    ℓ 배열에 대해 각 점에서 암시식을 brentq 로 푼다.
    """
    ell = np.atleast_1d(np.asarray(ell, float))
    S0 = dof.g_star_s(T0_GeV) * T0_GeV ** 3 * ell0 ** 3
    out = np.empty_like(ell)
    for i, L in enumerate(ell):
        target = S0 / L ** 3                       # = g_*s(T) T^3

        def f(logT):
            T = 10.0 ** logT
            return dof.g_star_s(T) * T ** 3 - target
        # T0 근방에서 브래킷
        lo, hi = np.log10(T0_GeV) - 8, np.log10(T0_GeV) + 8
        out[i] = 10.0 ** brentq(f, lo, hi, xtol=1e-10)
    return out if out.size > 1 else float(out[0])


def entropy_density_ratio_check(T1, T2):
    """s ℓ^3 = const 검증용:  g_*s(T1)T1^3 / (g_*s(T2)T2^3)."""
    return (dof.g_star_s(T1) * T1 ** 3) / (dof.g_star_s(T2) * T2 ** 3)


def neutrino_temperature(T_gamma):
    """T_ν = (4/11)^{1/3} T_γ  (순간 탈결합).  소멸 후 유효."""
    return U.T_NU_OVER_T_GAMMA * np.asarray(T_gamma, float)


def n_eff(delta_N=0.0):
    """유효 중성미자 수.  표준 3.044 (비순간 탈결합 보정) + ΔN."""
    return U.N_EFF_STANDARD + delta_N


def photon_temperature_today_K():
    return U.T_CMB_K


def temperature_redshift_isotropic(T0_K, z):
    """등방 극한 T(z) = T0 (1+z)  (g_*s 상수 구간; 재결합 이후)."""
    return T0_K * (1.0 + np.asarray(z, float))


def bbn_temperature_GeV():
    """BBN 시작 (중성자-양성자 동결 부근) ~ 1 MeV = 1e-3 GeV."""
    return 1.0e-3
