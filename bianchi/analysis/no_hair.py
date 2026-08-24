"""
PR-41 · Wald 우주 no-hair 정리의 수치 검증 + 반례.

Wald (1983): Λ>0 이고 물질이 지배·강 에너지조건을 만족하면, Bianchi IX 를 제외한
모든 초기 팽창 Bianchi 모형은 미래에 de Sitter 로 점근한다.  전단(shear)은 사라진다.

  정확한 진술 (Bianchi I + Λ, 임의 물질 없이):
    σ_ab ∝ a⁻³        (Bianchi I 는 곡률원 없음)
    H² = σ²/3 + Λ/3   (Friedmann)
    ⇒ H → H_dS = √(Λ/3),   θ = 3H → √(3Λ)  (아래로 단조)
    ⇒ σ ∝ e^{-3Ht} = e^{-3τ},   Σ = σ/H → 0   (τ = ∫H dt)

  ★ **Wald 감쇠 지수** d ln Σ/dτ → **-3**.  이 -3 을 수치로 재현하는 것이 핵심 오라클.

반례 (PR-40 이방 인플레이션, Watanabe-Kanno-Soda 2009):
  결합 f(φ)²F² 가 게이지장 에너지를 인플레이션 동안 유지하면 이방 응력 Π 가 사라지지
  않고, 정규화 전단이 **Σ/H → O(ε) ≠ 0** 끌개로 간다.  이때 d ln Σ/dτ → **0**.
  Wald 의 에너지조건 가정이 깨지므로 정리와 모순이 아니라 **가정의 필요성**을 보인다.

de Sitter 극한은 정확해 (Bianchi I) 로, 반례는 소스항이 있는 정규화 전단 ODE 로 준다.
둘 다 τ (= ln ℓ) 시간으로 적분하여 후기 국소 지수를 측정한다.
"""
from __future__ import annotations

import numpy as np

from bianchi.matter.gauge_field import anisotropic_inflation_attractor

#: Wald 정리가 예측하는 전단의 정규화 감쇠 지수 (Σ ∝ e^{WALD_EXPONENT·τ}).
WALD_EXPONENT = -3.0


def desitter_hubble(Lambda):
    """de Sitter Hubble H_dS = √(Λ/3)  (자연단위 8πG=1)."""
    return float(np.sqrt(Lambda / 3.0))


def desitter_expansion(Lambda):
    """de Sitter 팽창률 θ_dS = 3 H_dS = √(3Λ)  (Wald 하한)."""
    return float(np.sqrt(3.0 * Lambda))


# ---------------------------------------------------------------- 정확해: Bianchi I + Λ
def bianchi_I_lambda_rhs(t, y, Lambda):
    """우주시간 t 에서 (H, σ²) 의 정확한 Bianchi I + Λ RHS.

        Ḣ  = -σ²                      (Friedmann 미분 + shear 진화)
        σ̇² = -6 H σ²                  (σ_ab ∝ a⁻³ ⇒ σ² ∝ a⁻⁶)
    구속: H² = σ²/3 + Λ/3  (적분 내내 보존).
    """
    H, sig2 = y
    return np.array([-sig2, -6.0 * H * sig2])


def integrate_bianchi_I_lambda(Lambda=1.0, Sigma0=0.8, tau_max=8.0, n=1600):
    """Bianchi I + Λ 를 τ (= ln ℓ) 시간으로 적분.

    초기 Σ0 = σ0/H0 (정규화 전단) 로 시작.  구속 H0² = σ0²/3 + Λ/3 에서
    σ0 = H0 Σ0, 즉 H0² = H0²Σ0²/3 + Λ/3 ⇒ H0 = √(Λ/3 / (1 - Σ0²/3)).

    반환: dict(tau, H, sigma, Sigma, theta, sigma2, q).
    """
    if not (0.0 <= Sigma0 < np.sqrt(3.0)):
        raise ValueError("Σ0 must satisfy 0 ≤ Σ0 < √3 (constraint positivity).")
    H0 = np.sqrt((Lambda / 3.0) / (1.0 - Sigma0 ** 2 / 3.0))
    sig0 = H0 * Sigma0
    y = np.array([H0, sig0 ** 2], float)

    taus = np.linspace(0.0, tau_max, n)
    H = np.empty(n); sig2 = np.empty(n)
    H[0], sig2[0] = y
    for i in range(n - 1):
        dtau = taus[i + 1] - taus[i]
        # dτ = H dt ⇒ dt = dτ/H;  RK4 in t with local step dt = dτ/H (H>0 monotone)
        def f(yv):
            Hh = yv[0]
            dt = dtau / Hh
            return bianchi_I_lambda_rhs(0.0, yv, Lambda) * dt
        k1 = f(y)
        k2 = f(y + 0.5 * k1)
        k3 = f(y + 0.5 * k2)
        k4 = f(y + k3)
        y = y + (k1 + 2 * k2 + 2 * k3 + k4) / 6.0
        H[i + 1], sig2[i + 1] = y

    sigma = np.sqrt(np.clip(sig2, 0.0, None))
    Sigma = sigma / H
    theta = 3.0 * H
    # 감속 q = -1 - Ḣ/H² = -1 + σ²/H²  (de Sitter 로 갈수록 q → -1)
    q = -1.0 + sig2 / H ** 2
    return dict(tau=taus, H=H, sigma=sigma, Sigma=Sigma, theta=theta,
                sigma2=sig2, q=q, Lambda=Lambda, H_dS=desitter_hubble(Lambda))


def measure_decay_exponent(tau, Sigma, tail_frac=0.4):
    """후기 구간에서 d ln Σ/dτ 의 평균 국소 지수를 최소자승으로 측정.

    tail_frac: 뒤쪽 몫만 사용 (초기 과도 배제).  Σ>0 인 점만.
    """
    tau = np.asarray(tau, float); Sigma = np.asarray(Sigma, float)
    i0 = int((1.0 - tail_frac) * len(tau))
    m = Sigma[i0:] > 0
    x = tau[i0:][m]; y = np.log(Sigma[i0:][m])
    if x.size < 3:
        return float("nan")
    A = np.vstack([x, np.ones_like(x)]).T
    slope, _ = np.linalg.lstsq(A, y, rcond=None)[0]
    return float(slope)


def verify_no_hair(Lambda=1.0, Sigma0=0.8, tau_max=10.0):
    """Wald no-hair 검증.  반환 dict:
        decay_exponent  : 측정된 d ln Σ/dτ  (오라클 ≈ -3)
        Sigma_final     : 최종 Σ (→ 0)
        H_final, H_dS   : H → √(Λ/3) 확인
        theta_monotone  : θ 가 단조 감소하는가 (Wald 하한 접근)
        constraint_max  : |H² - σ²/3 - Λ/3| 최대 (보존)
    """
    s = integrate_bianchi_I_lambda(Lambda, Sigma0, tau_max)
    exp_ = measure_decay_exponent(s["tau"], s["Sigma"])
    constraint = np.abs(s["H"] ** 2 - s["sigma2"] / 3.0 - Lambda / 3.0)
    dtheta = np.diff(s["theta"])
    return dict(
        decay_exponent=exp_,
        wald_exponent=WALD_EXPONENT,
        Sigma_final=float(s["Sigma"][-1]),
        H_final=float(s["H"][-1]),
        H_dS=s["H_dS"],
        theta_final=float(s["theta"][-1]),
        theta_dS=desitter_expansion(Lambda),
        theta_monotone_decreasing=bool(np.all(dtheta <= 1e-10)),
        constraint_max=float(constraint.max()),
    )


# ---------------------------------------------------------------- 반례: 이방 인플레이션
def anisotropic_inflation_shear_rhs(tau, Sigma, Pi_source, q=-1.0):
    """정규화 전단 진화 (de Sitter 배경, 단일 자유도):
        dΣ/dτ = -(2 - q) Σ + Π          (Π = 게이지장 이방응력, 유지됨)
    소스 없으면(Π=0) q→-1 에서 dΣ/dτ = -3Σ  → **Wald 지수 -3** 재현.
    """
    return -(2.0 - q) * Sigma + Pi_source


def integrate_anisotropic_inflation(epsilon=0.02, c=2.0, Sigma0=0.5,
                                     tau_max=12.0, n=1600, q=-1.0):
    """게이지장이 유지하는 이방 응력으로 Σ 가 0 이 아닌 끌개로 가는 반례.

    끌개 Σ* = anisotropic_inflation_attractor(ε, c)  (PR-40).
    소스 Π = (2-q) Σ*  로 두면 고정점이 정확히 Σ* → d ln Σ/dτ → 0.
    """
    Sigma_star = anisotropic_inflation_attractor(epsilon, c)
    Pi = (2.0 - q) * Sigma_star            # 고정점이 Σ* 가 되도록
    taus = np.linspace(0.0, tau_max, n)
    S = np.empty(n); S[0] = Sigma0
    y = Sigma0
    for i in range(n - 1):
        h = taus[i + 1] - taus[i]
        def f(s):
            return anisotropic_inflation_shear_rhs(0.0, s, Pi, q)
        k1 = f(y); k2 = f(y + 0.5 * h * k1)
        k3 = f(y + 0.5 * h * k2); k4 = f(y + h * k3)
        y = y + h / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)
        S[i + 1] = y
    return dict(tau=taus, Sigma=S, Sigma_star=float(Sigma_star), Pi=float(Pi))


def anisotropic_inflation_counterexample(epsilon=0.02, c=2.0, Sigma0=0.5, tau_max=14.0):
    """반례 요약: 게이지 소스 유지 시 d ln Σ/dτ → 0 (no-hair 위반).

    반환 dict(decay_exponent≈0, Sigma_final≈Σ*, violates_no_hair=True).
    """
    s = integrate_anisotropic_inflation(epsilon, c, Sigma0, tau_max)
    exp_ = measure_decay_exponent(s["tau"], s["Sigma"], tail_frac=0.3)
    return dict(
        decay_exponent=exp_,
        Sigma_final=float(s["Sigma"][-1]),
        Sigma_star=s["Sigma_star"],
        violates_no_hair=bool(abs(exp_) < 0.5 and s["Sigma_star"] > 1e-6),
    )


def wald_theorem_summary():
    """정리·가정·반례의 한 줄 요약 (보고서/검증 로그용)."""
    return (
        "Wald(1983): Λ>0 + (강·지배 에너지조건) ⇒ Bianchi(≠IX) → de Sitter, "
        "Σ ∝ e^{-3τ}. 반례: f(φ)²F² 결합 게이지장은 에너지조건을 우회하여 "
        "Σ/H → O(ε) ≠ 0 (Watanabe-Kanno-Soda 2009)."
    )
