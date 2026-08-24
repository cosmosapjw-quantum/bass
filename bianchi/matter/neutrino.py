"""
PR-34 · 질량 중성미자 (Fermi-Dirac 정확 적분).

무충돌 종족의 특수화 (freestream 과 물리 공유) 이지만, 등방 배경에서의 ρ_ν, p_ν,
w_ν(a) 를 정확 FD 적분으로 준다.  질량은 오늘의 온도 T_ν0 = (4/11)^{1/3} T_γ0 에
대한 무차원 y = m/T_ν 로 들어간다.

극한 (설계 오라클):
  m -> 0    : ρ ∝ a^{-4}, w = 1/3      (상대론)
  m >> T    : ρ ∝ a^{-3}, w -> 0        (비상대론)
  Σm_ν = 0.06 eV -> Ω_ν h^2 = 6.4e-4    (비상대론 근사)

★ 자유흐름이면 이방 배경에서 π_ab 를 만든다 (matter.freestream).  여기서는 등방
  배경의 밀도/압력 진화 (열역사·거리 계산용).
"""
from __future__ import annotations

import numpy as np

from bianchi.physical import units as U
from bianchi.optional_dependencies import require_optional

integrate = require_optional("scipy.integrate", feature=__name__, dependency="scipy")

# FD 적분 상수:  단일 페르미온 (g=2, 입자+반입자는 계수로), 무차원 x = p/T.
#   n ∝ ∫ x^2 f dx ,  ρ ∝ ∫ x^2 √(x^2+y^2) f dx ,  P ∝ (1/3)∫ x^4/√(x^2+y^2) f dx
def _fd(x):
    return 1.0 / (np.exp(np.minimum(x, 700.0)) + 1.0)


def _rho_integral(y):
    """∫_0^∞ x^2 √(x^2+y^2) f_FD dx  (무차원, 종별 온도 단위)."""
    val, _ = integrate.quad(lambda x: x ** 2 * np.sqrt(x ** 2 + y ** 2) * _fd(x),
                            0, np.inf, limit=200)
    return val


def _p_integral(y):
    val, _ = integrate.quad(lambda x: x ** 4 / (3.0 * np.sqrt(x ** 2 + y ** 2)) * _fd(x),
                            0, np.inf, limit=200)
    return val


def _n_integral():
    val, _ = integrate.quad(lambda x: x ** 2 * _fd(x), 0, np.inf, limit=200)
    return val


_RHO0 = _rho_integral(0.0)          # 무질량 ρ 적분값 (7π^4/120 형)
_N0 = _n_integral()                 # 무질량 n 적분값 (3ζ(3)/2 형)


def neutrino_rho_p(a, m_eV, T_nu0_K=None, n_species=1.0):
    """등방 배경에서 한 종의 (ρ, p) 를 오늘 대비 무차원으로.

    반환: (rho/rho0_massless, p/rho0_massless, w).  a=1 이 오늘.
    T_nu 는 a 에 반비례: T_nu(a) = T_nu0/a, 따라서 y(a) = m/T_nu = (m/T_nu0) a.
    """
    a = np.atleast_1d(np.asarray(a, float))
    if T_nu0_K is None:
        T_nu0_K = U.T_NU_OVER_T_GAMMA * U.T_CMB_K
    y0 = m_eV / (U.KB_EV_K * T_nu0_K)        # m / T_nu0  (무차원)
    rho = np.empty_like(a); pr = np.empty_like(a)
    for i, ai in enumerate(a):
        # T_nu ∝ 1/a, 적분은 x=p/T 로 하므로 y = y0 * a, 그리고 (T/T0)^4 = a^-4 스케일
        y = y0 * ai
        rho[i] = _rho_integral(y) / ai ** 4      # ρ ∝ T^4 ∫... = a^-4 ∫(y)
        pr[i] = _p_integral(y) / ai ** 4
    rho *= n_species; pr *= n_species
    w = pr / rho
    if a.size == 1:
        return float(rho[0]), float(pr[0]), float(w[0])
    return rho, pr, w


def omega_nu_h2(sum_m_eV, T0_K=U.T_CMB_K):
    """비상대론 근사 Ω_ν h^2 = Σm_ν / 93.14 eV (정확 적분과 <1% 일치)."""
    return U.massive_neutrino_omega_h2(sum_m_eV)


def scaling_exponent(m_eV, a1=1.0, a2=0.5, T_nu0_K=None):
    """ρ ∝ a^{-n} 의 국소 지수 n = -d ln ρ/d ln a  (m→0: 4, m≫T: 3)."""
    r1 = neutrino_rho_p(a1, m_eV, T_nu0_K)[0]
    r2 = neutrino_rho_p(a2, m_eV, T_nu0_K)[0]
    return np.log(r2 / r1) / np.log(a1 / a2)
