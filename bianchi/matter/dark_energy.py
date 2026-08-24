"""
PR-35 · 암흑에너지.  Λ, CPL w(a)=w0+wa(1-a), 임의 테이블, 상호작용 Q.

정규화 밀도 진화 (등방):
    ρ_DE(a)/ρ_DE0 = exp[ 3 ∫_a^1 (1 + w(a')) da'/a' ]
  CPL:  = a^{-3(1+w0+wa)} exp[-3 wa (1-a)]
  Λ (w=-1): = 1 (상수)

Species 인터페이스 (PR-30 호환): omega, q_source(감속 기여), pi=0, rhs.
상호작용 Q 는 다른 종족과 짝을 맞춰 ΣQ=0 (matter.species).
"""
from __future__ import annotations

import numpy as np


def w_cpl(a, w0=-1.0, wa=0.0):
    """CPL: w(a) = w0 + wa (1 - a)."""
    return w0 + wa * (1.0 - np.asarray(a, float))


def rho_ratio_cpl(a, w0=-1.0, wa=0.0):
    """ρ_DE(a)/ρ_DE0 (CPL 닫힌형)."""
    a = np.asarray(a, float)
    return a ** (-3.0 * (1.0 + w0 + wa)) * np.exp(-3.0 * wa * (1.0 - a))


def rho_ratio_tabulated(a, a_tab, w_tab):
    """임의 w(a) 테이블에서 ρ_DE(a)/ρ_DE0 = exp[3 ∫_a^1 (1+w)/a' da'].

    a_tab 오름차순, a ≤ 1.
    """
    a = np.atleast_1d(np.asarray(a, float))
    a_tab = np.asarray(a_tab, float); w_tab = np.asarray(w_tab, float)
    # 조밀 격자에서 누적적분
    ag = np.linspace(min(a.min(), a_tab.min()), 1.0, 4000)
    wg = np.interp(ag, a_tab, w_tab)
    integrand = (1.0 + wg) / ag
    # ∫_a^1 = cumulative from 1 backward
    cum = np.concatenate([[0.0], np.cumsum(0.5 * (integrand[1:] + integrand[:-1])
                                          * np.diff(ag))])
    F = cum[-1] - np.interp(a, ag, cum)          # ∫_a^1
    out = np.exp(3.0 * F)
    return out if out.size > 1 else float(out[0])


class DarkEnergy:
    """암흑에너지 성분 (Species 호환).  등방 밀도진화 + 이방 소스 (π=0)."""
    def __init__(self, Omega0, w0=-1.0, wa=0.0, Q_energy=0.0):
        self.Omega0 = float(Omega0); self.w0 = float(w0); self.wa = float(wa)
        self.Q_energy = float(Q_energy)

    def w(self, a):
        return w_cpl(a, self.w0, self.wa)

    def omega_at(self, a, H_ratio):
        """Ω_DE(a) = Ω_DE0 (ρ_ratio) / (H/H0)^2  (등방)."""
        return self.Omega0 * rho_ratio_cpl(a, self.w0, self.wa) / H_ratio ** 2

    def q_source_isotropic(self, Omega_DE):
        """감속 기여 (1/2)(1+3w) Ω_DE = (1/2)(3γ-2)Ω 형, γ=1+w."""
        return 0.5 * (1.0 + 3.0 * self.w0) * Omega_DE      # w=w0 근사 (a=1)

    def anisotropic_stress(self):
        return np.zeros((3, 3))                  # 스칼라 암흑에너지: π=0

    def is_lambda(self):
        return abs(self.w0 + 1.0) < 1e-12 and abs(self.wa) < 1e-12


def lambda_rho_ratio(a):
    """Λ (w=-1): ρ 상수 -> 비율 1."""
    return np.ones_like(np.asarray(a, float))
