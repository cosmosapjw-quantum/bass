"""
PR-38 · 무충돌(자유흐름) 종족 — Vlasov 특성곡선 + 구적.

균질 시공간의 Vlasov 방정식은 k-모드가 없다: 불변기저 운동량이 특성곡선을 따라
보존되므로 분포함수 f(t, p_α) 로부터 모멘트가 **고정영역 구적**으로 나온다
(설계 D4; audit/d_kinetic.py 로 검증).

Bianchi I 정확식 (공변 성분 p_i = a_i P^i = const):
    ρ    = (1/V) ∫ d³p_i  E f0(p_i)
    p    = (1/V) ∫ d³p_i (|P|²/3E) f0
    π_ab = (1/V) ∫ d³p_i (P_a P_b - |P|²δ_ab/3)/E f0
    V = a1 a2 a3 ,  P^i = p_i/a_i ,  E = √(m² + Σ(p_i/a_i)²)

검증 오라클 (audit/d_kinetic.py):
  * 등방 극한 π_ab = 0 (2.6e-13)
  * 무질량 w=1/3, ρ∝ℓ⁻⁴;  비상대론 ρ∝ℓ⁻³
  * ∇^aT_ab = 0:  ρ̇ + 3H(ρ+p) + σ_ab π^ab = 0  (3.9e-10)
  * 급작응답 π_ab = -(8/15)ρ δ(ln a)_⟨ab⟩  (Misner 중성미자 점성의 기원)

★ 광자(m=0) 널 측지선(PR-43)과 같은 특성곡선을 쓴다.  π_ab≠0 이므로 이 종족이
  들어오면 대각 shear 가정이 깨진다 → 일반차트(charts.general) 기본 (설계 §6-7).
"""
from __future__ import annotations

import numpy as np

# ------------------------------------------------------- 구적 격자 (모듈 캐시)
_NR, _NANG = 96, 24


def _build_grid(NR=_NR, NANG=_NANG, L=3.0):
    xr, wr = np.polynomial.legendre.leggauss(NR)
    xc, wc = np.polynomial.legendre.leggauss(NANG)
    phi = 2 * np.pi * (np.arange(NANG) + 0.5) / NANG
    wphi = np.full(NANG, 2 * np.pi / NANG)
    q = L * (1 + xr) / (1 - xr)                 # 지름 (0, ∞) 사상
    dq = wr * 2 * L / (1 - xr) ** 2
    st = np.sqrt(1 - xc ** 2)
    NHAT = np.stack([np.outer(st, np.cos(phi)).ravel(),
                     np.outer(st, np.sin(phi)).ravel(),
                     np.outer(xc, np.ones_like(phi)).ravel()], axis=-1)
    WANG = np.outer(wc, wphi).ravel()
    return q, dq, NHAT, WANG


_Q, _DQ, _NHAT, _WANG = _build_grid()


def f_fermi_dirac(q):
    """상대론적 페르미-디랙 (T=1).  중성미자 기본."""
    return 1.0 / (np.exp(np.minimum(q, 700.0)) + 1.0)


def f_bose_einstein(q):
    return 1.0 / (np.expm1(np.minimum(q, 700.0)))


def moments(a_vec, mass, f0=f_fermi_dirac):
    """자유흐름 종족의 (ρ, p, π_ab).  a_vec: 방향 스케일인자 (3,), mass ≥ 0."""
    a_vec = np.asarray(a_vec, float)
    V = float(np.prod(a_vec))
    P = (_Q[:, None, None] * _NHAT[None, :, :]) / a_vec[None, None, :]   # P^i = p_i/a_i
    P2 = np.einsum("rai,rai->ra", P, P)
    E = np.sqrt(mass ** 2 + P2)
    w = (_DQ[:, None] * _Q[:, None] ** 2) * _WANG[None, :] * f0(_Q)[:, None] / V
    rho = float((w * E).sum())
    pr = float((w * P2 / (3 * E)).sum())
    pi = (np.einsum("ra,rai,raj->ij", w / E, P, P)
          - np.eye(3) * (w * P2 / (3 * E)).sum())
    return rho, pr, pi


class FreeStreamingSpecies:
    """자유흐름 종족 (Bianchi I 정확; 일반형은 특성곡선 표본).

    상태: 방향 스케일인자 a_vec (또는 lna).  분포는 초기 f0 로 고정.
    """
    def __init__(self, mass=0.0, f0=f_fermi_dirac, a_vec=(1.0, 1.0, 1.0), norm=1.0):
        self.mass = float(mass)
        self.f0 = (lambda q: norm * f0(q))
        self.a_vec = np.asarray(a_vec, float)

    def at(self, a_vec):
        return FreeStreamingSpecies(self.mass, self.f0, a_vec)

    def rho_p_pi(self):
        return moments(self.a_vec, self.mass, self.f0)

    def rho(self):
        return self.rho_p_pi()[0]

    def pressure(self):
        return self.rho_p_pi()[1]

    def anisotropic_stress(self):
        """π_ab (trace-free).  대각 shear 가정을 깨는 성분."""
        return self.rho_p_pi()[2]

    def w_eos(self):
        r, p, _ = self.rho_p_pi()
        return p / r


def emt_conservation_residual(fs, H, sigma_diag):
    """ρ̇ + 3H(ρ+p) + σ_ab π^ab = 0 의 잔차 (수치 미분).

    자유흐름 종족을 H, σ 대각 배경에서 한 스텝 흘려 ρ̇ 를 유한차분으로 얻고 검증.
    """
    a = fs.a_vec
    rho, pr, pi = fs.rho_p_pi()
    sig = np.asarray(sigma_diag, float)
    h = 1e-6
    a_p = a * np.exp(h * (H + sig)); a_m = a * np.exp(-h * (H + sig))
    rp = moments(a_p, fs.mass, fs.f0)[0]; rm = moments(a_m, fs.mass, fs.f0)[0]
    drho = (rp - rm) / (2 * h)
    return drho + 3 * H * (rho + pr) + float(np.einsum("ij,ij->", np.diag(sig), pi))


def sudden_response_coefficient(delta=0.002, mass=0.0, f0=f_fermi_dirac):
    """등방 분포를 부피보존 변형 δ(ln a) 로 순간 찌그러뜨렸을 때 π_11/(ρ δ).

    초상대론적 극한에서 정확히 -8/15 (Misner 점성).  질량 기체는 0 으로 소멸.
    """
    lna = np.array([2 * delta, -delta, -delta])
    rho, _, pi = moments(np.exp(lna), mass, f0)
    return float(pi[0, 0] / (rho * lna[0]))
