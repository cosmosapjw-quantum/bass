"""
PR-28 · 물리 시간 차트.  τ <-> (H, t, ℓ).

핵심 (설계 D1, audit/d_transport.py 로 검증):
    ℓ ≡ (a1 a2 a3)^{1/3},   ℓ'/ℓ = 1   (정의상 정확; θ = 3H)
  ⟹  τ = ln(ℓ/ℓ0) 는 이미 "평균 스케일인자의 e-fold 수"다.  따로 적분기가
     필요 없고, 물리 차트는 τ 위의 부수량 묶음이다:

    H(τ)   = H0 exp(-∫_0^τ (1+q) dτ')        (H'/H = -(1+q))
    t(τ)   = t0 + ∫_0^τ dτ'/H
    ρ_i(τ) = 3 H(τ)^2 Ω_i(τ)
    T_γ(τ) : g_*s(T) T^3 ℓ^3 = const  ->  thermo.temperature (PR-33)

함정 (설계 §6):
  * H = 0 (Bianchi IX 재붕괴) 에서 이 차트가 깨진다.  IX 는 D-정규화 차트에서
    적분하고, 여기서는 dt = -dτ_-/D, H = D * H̄ 로 복원한다 (r5e 검증).
"""
from __future__ import annotations

import numpy as np

# ------------------------------------------------------------------ 기본 τ-차트
def hubble_of_tau(tau, q, H0=1.0):
    """H(τ) = H0 exp(-∫ (1+q) dτ).  사다리꼴 적분 (q 는 τ 격자 위 배열)."""
    tau = np.asarray(tau, float); q = np.asarray(q, float)
    integ = 1.0 + q
    cum = np.concatenate([[0.0], np.cumsum(0.5 * (integ[1:] + integ[:-1])
                                          * np.diff(tau))])
    return H0 * np.exp(-cum)


def cosmic_time_of_tau(tau, H, t0=0.0):
    """t(τ) = t0 + ∫ dτ / H."""
    tau = np.asarray(tau, float); H = np.asarray(H, float)
    inv = 1.0 / H
    return t0 + np.concatenate([[0.0], np.cumsum(0.5 * (inv[1:] + inv[:-1])
                                                * np.diff(tau))])


def mean_scale_factor(tau, l0=1.0):
    """ℓ = ℓ0 e^τ  (정의상; ℓ'/ℓ = 1)."""
    return l0 * np.exp(np.asarray(tau, float))


def energy_density(H, Omega):
    """ρ = 3 H^2 Ω  (법선 프레임)."""
    return 3.0 * np.asarray(H, float) ** 2 * np.asarray(Omega, float)


def reconstruct(tau, q, Omega=None, H0=1.0, t0=0.0, l0=1.0):
    """τ 격자 + q(τ) [+ Ω(τ)] -> 물리량 묶음 (H, t, ℓ, ρ)."""
    tau = np.asarray(tau, float)
    H = hubble_of_tau(tau, q, H0)
    t = cosmic_time_of_tau(tau, H, t0)
    out = dict(tau=tau, H=H, t=t, ell=mean_scale_factor(tau, l0), q=np.asarray(q, float))
    if Omega is not None:
        out["rho"] = energy_density(H, Omega)
    return out


# ------------------------------------------------------------ Bianchi IX D-차트 복원
def ix_physical_from_D(tau_minus, Hbar, D, t0=0.0):
    """IX D-정규화 해 (H̄, D)(τ_-) 로부터 물리량 복원 (r5e 검증).

    Heinzle-Uggla:  D = sqrt(H^2 + (1/6) Σ_{i<j} n_i n_j) > 0 항상,
                    dτ_-/dt = -D  (과거지향),   H = D * H̄.
    재붕괴는 H̄ 의 영점 통과 (H = 0) 로 검출한다 — H-정규화 차트엔 영점이 없다.

    입력은 τ_- 오름차순 격자 위의 배열.  물리 시간 t 는 감소 방향이므로
    t(τ_-) = t0 - ∫ dτ_- / D 로 적분한다.
    """
    tau_minus = np.asarray(tau_minus, float)
    Hbar = np.asarray(Hbar, float); D = np.asarray(D, float)
    H = D * Hbar
    invD = 1.0 / D
    # dt = -dτ_-/D  =>  t = t0 - ∫ dτ_-/D
    t = t0 - np.concatenate([[0.0], np.cumsum(0.5 * (invD[1:] + invD[:-1])
                                             * np.diff(tau_minus))])
    return dict(tau_minus=tau_minus, H=H, t=t, D=D, Hbar=Hbar)


def recollapse_indices(Hbar):
    """H̄ (또는 H) 의 부호 변화 위치 = 재붕괴/반등 시점."""
    Hbar = np.asarray(Hbar, float)
    s = np.sign(Hbar)
    return np.where(np.diff(s) != 0)[0]


# --------------------------------------------------------------------- 참조 극한
def de_sitter(tau, H0=1.0):
    """de Sitter 참조: q = -1  ->  H = const, ℓ = ℓ0 e^τ.  회귀 오라클용."""
    tau = np.asarray(tau, float)
    q = -np.ones_like(tau)
    return reconstruct(tau, q, H0=H0)


def flat_dust(tau, H0=1.0, t0=None):
    """평탄 먼지 FLRW 참조: q = 1/2 상수  ->  H = H0 e^{-(3/2)τ}, t = 2/(3H).

    회귀 오라클: cosmic_time_of_tau 가 t = 2/(3H) - 2/(3H0) + t0 를 재현.
    """
    tau = np.asarray(tau, float)
    q = 0.5 * np.ones_like(tau)
    H = hubble_of_tau(tau, q, H0)
    if t0 is None:
        t0 = 2.0 / (3.0 * H0)
    t = cosmic_time_of_tau(tau, H, t0)
    return dict(tau=tau, q=q, H=H, t=t, ell=mean_scale_factor(tau),
                t_exact=2.0 / (3.0 * H))
