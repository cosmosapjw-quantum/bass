"""
PR-40 · 게이지장 (전기+자기) 과 이방 인플레이션 f(φ)²F².

프레임 Maxwell 전체 (audit/d_matter.py D19; 좌표검산 1.7e-16):
    Ė_a = -2H E_a + σ_ab E^b + (R×E)_a - (n_ab B^b + eps_abc a^b B^c)
    Ḃ_a = -2H B_a + σ_ab B^b + (R×B)_a + (n_ab E^b + eps_abc a^b E^c)
  curl 상대부호 **+** (v1.2 정정; E,B 동시 풀이의 쌍대구조).
  구속:  a·E = 0, a·B = 0.

이방 인플레이션 (Watanabe-Kanno-Soda):  스칼라장 φ + 게이지장, 결합 f(φ)²F².
  결합함수 f(φ) = exp(2cφ/M_Pl) 형으로 게이지장 에너지가 인플레이션 중 유지되어
  **우주 no-hair 정리의 반례** — Σ/H 가 0 이 아닌 끌개로 간다 (Σ/H ∝ ε, slow-roll).

f=1 극한에서 순수 자기장(components.MagneticField) 재현.
"""
from __future__ import annotations

import numpy as np

from bianchi.conventions import EPS3


def _curl(n, a, X):
    """(curl X)_a = n_ab X^b + eps_abc a^b X^c  (상대부호 +; v1.2)."""
    n = np.asarray(n, float); a = np.asarray(a, float); X = np.asarray(X, float)
    return n @ X + np.einsum("abc,b,c->a", EPS3, a, X)


def maxwell_rhs(E, B, H, sigma, N, A, R):
    """(Ė, Ḃ) 차원량 프레임 Maxwell (E, B 동시)."""
    E = np.asarray(E, float); B = np.asarray(B, float); sigma = np.asarray(sigma, float)
    dE = -2 * H * E + sigma @ E + np.cross(R, E) - _curl(N, A, B)
    dB = -2 * H * B + sigma @ B + np.cross(R, B) + _curl(N, A, E)
    return dE, dB


def em_energy_pressure(E, B):
    """전자기 에너지밀도·압력 (프레임):  ρ = (E²+B²)/2, p = ρ/3 (γ_eff=4/3)."""
    E = np.asarray(E, float); B = np.asarray(B, float)
    rho = 0.5 * (E @ E + B @ B)
    return rho, rho / 3.0


def em_anisotropic_stress(E, B):
    """π_ab = -(E_a E_b + B_a B_b) + (1/3)(E²+B²) δ_ab  (Maxwell 응력, trace-free)."""
    E = np.asarray(E, float); B = np.asarray(B, float)
    T = -(np.outer(E, E) + np.outer(B, B))
    tr = np.trace(T)
    return T - tr * np.eye(3) / 3.0


def gauss_constraints(E, B, A):
    """a·E = 0, a·B = 0."""
    A = np.asarray(A, float)
    return dict(divE=float(A @ np.asarray(E)), divB=float(A @ np.asarray(B)))


def coupling_f(phi, c=1.0, M_pl=1.0):
    """f(φ) = exp(2 c φ / M_Pl)  (Kanno-Soda 결합)."""
    return np.exp(2.0 * c * np.asarray(phi, float) / M_pl)


def anisotropic_inflation_attractor(epsilon, c=2.0):
    """이방 인플레이션 끌개의 Σ/H (slow-roll):  Σ/H ≈ (1/3)(c-1)/c · ε · (...).

    Watanabe-Kanno-Soda 2009: 게이지장이 유지되면 Σ/H = O(ε) ≠ 0 (no-hair 위반).
    간단화된 스케일링 (ε = slow-roll):  Σ/H ∝ ε.
    """
    return (1.0 / 3.0) * (c - 1.0) / c * epsilon * 2.0


def reduces_to_magnetic(B):
    """f=1, E=0 극한에서 순수 자기장식과 일치 확인용 (components.MagneticField)."""
    return em_energy_pressure(np.zeros(3), B)
