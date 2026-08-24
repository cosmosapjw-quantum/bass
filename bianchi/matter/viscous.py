"""
PR-39 · 점성 유체.  Eckart (1차) 와 Israel-Stewart (인과 2차).

Eckart:  π_ab = -2 η σ_ab ,   p -> p - ζ θ    (전단·부피 점성)
  정규화:  Π_ab = -2 (η/H) Σ_ab      -> Σ 방정식의 순수 감쇠항 (등방화)
  ★ 함정: Eckart 은 비인과·불안정 (섭동에서).  배경에서는 감쇠항으로만 쓴다.

Israel-Stewart:  Π_ab 를 독립 변수로 승격, 완화시간 τ_π:
  τ_π Π̇_ab + Π_ab = -2 η σ_ab
  -> 인과적, 큰 σ 에서 Π 가 즉시 따라가지 않음.

엔트로피 생성 (열역학 2법칙):  T Ṡ = 2 η σ_ab σ^ab + ζ θ² ≥ 0  (η, ζ ≥ 0).
(audit/d_matter.py D21 로 확인.)
"""
from __future__ import annotations

import numpy as np


def eckart_anisotropic_stress(Sigma, eta_over_H):
    """Eckart Π_ab = -2 (η/H) Σ_ab  (Hubble 정규화; Σ RHS 소스)."""
    return -2.0 * eta_over_H * np.asarray(Sigma, float)


def eckart_bulk_pressure(theta, zeta):
    """부피 점성 압력 δp = -ζ θ."""
    return -zeta * theta


def entropy_production_rate(Sigma_ab, theta, eta, zeta, H=1.0):
    """T Ṡ = 2 η σ_ab σ^ab + ζ θ².  차원량 σ = H Σ.  ≥ 0 이어야."""
    sig = H * np.asarray(Sigma_ab, float)
    sig2 = float(np.einsum("ab,ab->", sig, sig))
    return 2.0 * eta * sig2 + zeta * theta ** 2


class IsraelStewartStress:
    """인과 점성: Π_ab 를 독립 상태로.  τ_π Π̇ + Π = -2η σ."""
    def __init__(self, Pi, tau_pi, eta):
        self.Pi = np.asarray(Pi, float)          # (3,3) trace-free
        self.tau_pi = float(tau_pi)
        self.eta = float(eta)

    def rhs(self, Sigma, H):
        """dΠ/dt = -(1/τ_π)(Π + 2 η σ),  σ = H Σ."""
        sig = H * np.asarray(Sigma, float)
        return -(self.Pi + 2.0 * self.eta * sig) / self.tau_pi

    def eckart_limit(self, Sigma, H):
        """τ_π → 0 에서 Eckart Π = -2 η σ 로 수렴."""
        return -2.0 * self.eta * H * np.asarray(Sigma, float)


def shear_damping_rate(eta_over_H, q):
    """자유 shear 방정식 Σ' = -(2-q)Σ + Π 에서 Π=-2(η/H)Σ 감쇠 기여율.

    유효 감쇠:  Σ' = -[(2-q) + 2 η/H] Σ  -> 점성이 등방화를 가속.
    """
    return (2.0) + 2.0 * eta_over_H       # (2-q) 의 곡률 부분은 별도; 점성 기여 2η/H
